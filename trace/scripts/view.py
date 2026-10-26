#!/usr/bin/env python3
"""Validate Trace record links and atomically render 总览.md; never change source JSON or run business actions."""

import html
import json
import os
import re
import sys
import tempfile
from pathlib import Path


STATES = {"planned", "queued", "running", "succeeded", "failed", "blocked", "skipped", "unknown", "stale"}
LABELS = dict(zip(
    ["planned", "queued", "running", "succeeded", "failed", "blocked", "skipped", "unknown", "stale"],
    ["计划", "排队", "执行中", "执行成功", "执行失败", "受阻", "跳过", "未知", "已过期"],
))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]+", value) is not None


def read_object(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        # Do not echo JSON bodies or parser excerpts containing private data.
        raise ValueError(f"无法读取有效JSON对象：{path.name} ({type(exc).__name__})") from None
    require(isinstance(value, dict), f"必须为对象：{path.name}")
    return value


def records(root, directory):
    result = {}
    for path in sorted((root / directory).glob("*.json")):
        value = read_object(path)
        key = value.get("id")
        require(identifier(key) and key == path.stem, f"ID与文件名不符：{directory}/{path.name}")
        result[key] = value
    return result


def list_field(obj, field):
    value = obj.get(field, [])
    require(isinstance(value, list), f"{field}必须为数组")
    return value


def load(root):
    task = read_object(root / "task.json")
    require(task.get("schema_version") == 1 and identifier(task.get("id")), "task版本或ID无效")
    stages, item_ids = {}, set()
    for item in list_field(task, "items"):
        require(isinstance(item, dict) and identifier(item.get("id")), "item必须具有合法ID")
        item_id = item["id"]
        require(item_id not in item_ids, f"重复item：{item_id}")
        item_ids.add(item_id)
        for stage in list_field(item, "stages"):
            require(isinstance(stage, dict) and identifier(stage.get("id")), "stage必须具有合法ID")
            key = (item_id, stage["id"])
            require(key not in stages, f"重复stage：{item_id}/{stage['id']}")
            require(stage.get("state") in STATES, f"stage状态无效：{item_id}/{stage['id']}")
            stages[key] = stage
    attempts = records(root, "attempts")
    observations = records(root, "observations")
    for key, attempt in attempts.items():
        owner = (attempt.get("item_id"), attempt.get("stage_id"))
        require(owner in stages, f"尝试{key}关联不存在的item/stage")
        require(attempt.get("status") in STATES - {"stale"}, f"尝试{key}状态无效")
        require(attempt["status"] != "unknown" or attempt.get("finished_at") is None,
                f"未知尝试{key}不能填写完成时间")
        previous = attempt.get("previous_attempt_id")
        require(previous is None or previous in attempts, f"尝试{key}前次引用不存在")
        if previous:
            prev = attempts[previous]
            require((prev.get("item_id"), prev.get("stage_id")) == owner, f"尝试{key}前次引用跨item/stage")
        visited, cursor = set(), key
        while cursor:
            require(cursor not in visited, f"尝试{key}重试引用成环")
            visited.add(cursor)
            require(cursor in attempts, f"尝试{key}重试链引用不存在")
            cursor = attempts[cursor].get("previous_attempt_id")
        error = attempt.get("error")
        require(error is None or isinstance(error, dict), f"尝试{key}的error必须为对象或null")
        if error is not None:
            require(error.get("capture") in {"complete", "truncated", "redacted", "unavailable"},
                    f"尝试{key}须注明错误捕获范围")
    for (item_id, stage_id), stage in stages.items():
        current = stage.get("attempt_id")
        if current is None:
            require(stage["state"] not in {"queued", "running", "succeeded", "failed", "unknown"},
                    f"阶段{item_id}/{stage_id}缺少当前尝试引用")
        else:
            require(current in attempts, f"阶段{item_id}/{stage_id}当前尝试不存在")
            attempt = attempts[current]
            require((attempt.get("item_id"), attempt.get("stage_id")) == (item_id, stage_id),
                    f"阶段{item_id}/{stage_id}当前尝试归属错误")
            require(stage["state"] in {"stale", "blocked"} or stage["state"] == attempt["status"],
                    f"阶段{item_id}/{stage_id}与当前尝试状态不符")
    for key, obs in observations.items():
        require(obs.get("kind") in {"issue", "result", "lesson"}, f"观察{key}类型无效")
        require(obs.get("status") in {"open", "resolved", "candidate", "validated", "rejected"},
                f"观察{key}状态无效")
        ids = list_field(obs, "item_ids")
        refs = list_field(obs, "attempt_ids")
        require(all(i in item_ids for i in ids), f"观察{key}引用不存在的item")
        require(all(a in attempts for a in refs), f"观察{key}引用不存在的尝试")
        require(not ids or all(attempts[a]["item_id"] in ids for a in refs),
                f"观察{key}尝试与item归属不符")
    return task, attempts, observations


def cell(value):
    if value is None or value == "":
        return "—"
    if isinstance(value, list):
        return "<br>".join(cell(part) for part in value) or "—"
    if isinstance(value, dict):
        return "；".join(f"{cell(key)}={cell(part)}" for key, part in value.items()) or "—"
    value = re.sub(r"([\\`*_\[\]])", r"\\\1", html.escape(str(value)))
    return value.replace("|", "&#124;").replace("\r\n", "\n").replace("\n", "<br>")


def link(directory, key):
    # IDs validated above; arbitrary evidence remains text, never executable links.
    return f"[{key}]({directory}/{key}.json)"


def render(task, attempts, observations):
    lines = [f"# {cell(task.get('title', task['id']))}", "",
             "由JSON记录生成；执行成功不代表业务验收。恢复时须核实外部现状。", "",
             f"目标/计划：{cell(task.get('goal_ref'))}", "",
             f"范围：{cell(task.get('scope'))}", "",
             f"记录更新时间：{cell(task.get('updated_at'))}", "", "## 验收条件", ""]
    lines += [f"- {cell(v)}" for v in list_field(task, "completion_criteria")]
    lines += ["", "## 当前阶段", "",
              "| Item / 计划引用 | 阶段 | 执行状态 | 业务结果/待核 | 当前尝试 | 最后核实 | 证据 |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for item in task.get("items", []):
        for stage in item.get("stages", []):
            current = stage.get("attempt_id")
            values = [cell(item.get("title", item["id"])) + " / " + cell(item.get("plan_ref")),
                      cell(stage.get("title", stage["id"])), LABELS[stage["state"]], cell(stage.get("outcome")),
                      link("attempts", current) if current else "—", cell(stage.get("observed_at")),
                      cell(stage.get("evidence", []))]
            lines.append("| " + " | ".join(values) + " |")
    lines += ["", "## 尝试历史", "",
              "| 尝试 | Item / 阶段 | 前次 | 执行状态 | 开始 → 结束 | 外部标识 | 错误码/捕获范围 |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for key, attempt in attempts.items():
        error = attempt.get("error") or {}
        previous = attempt.get("previous_attempt_id")
        values = [link("attempts", key), cell(attempt["item_id"] + "/" + attempt["stage_id"]),
                  link("attempts", previous) if previous else "—", LABELS[attempt["status"]],
                  cell(attempt.get("started_at")) + " → " + cell(attempt.get("finished_at")),
                  cell(attempt.get("external_ids")), cell(error.get("code")) + "/" + cell(error.get("capture"))]
        lines.append("| " + " | ".join(values) + " |")
    lines += ["", "完整结构见各尝试JSON；以下列出复现与核验线索。"]
    for key, attempt in attempts.items():
        lines += ["", f"### 尝试 {key}", ""]
        for label, field in [("输入版本", "inputs"), ("配置", "configuration"), ("与前次差异", "changes_from_previous"),
                             ("环境", "environment"), ("产物", "artifacts"), ("核验", "verification"),
                             ("缺失信息", "missing_information")]:
            lines += [f"- {label}：{cell(attempt.get(field))}"]
        error = attempt.get("error")
        if error:
            lines += [f"- 错误结构/原文：{cell(error)}"]
    lines += ["",
              "## 问题、成果与经验", "",
              "| 记录 | 类型/状态 | 摘要 | Item | 尝试 | 影响 |",
              "| --- | --- | --- | --- | --- | --- |"]
    for key, obs in observations.items():
        values = [link("observations", key), cell(obs["kind"] + "/" + obs["status"]),
                  cell(obs.get("title")), cell(obs.get("item_ids")),
                  ", ".join(link("attempts", a) for a in obs.get("attempt_ids", [])) or "—", cell(obs.get("impact"))]
        lines.append("| " + " | ".join(values) + " |")
    for key, obs in observations.items():
        lines += ["", f"### {key}：{cell(obs.get('title'))}", ""]
        for label, field in [("事实", "facts"), ("假设（未确证）", "hypotheses"), ("证据", "evidence"),
                             ("后续处理", "updates"), ("经验条件/复现/限制", "lesson")]:
            lines += [f"- {label}：{cell(obs.get(field))}"]
    lines += ["", "## 下一步允许动作", ""]
    lines += [f"- {cell(v)}" for v in list_field(task, "next_actions")]
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) != 2:
        print("用法：view.py <任务目录>", file=sys.stderr)
        return 2
    try:
        root = Path(sys.argv[1]).resolve(strict=True)
        task, attempts, observations = load(root)
        output = render(task, attempts, observations)
        destination = root / "总览.md"
        require(not destination.is_symlink(), "拒绝覆盖符号链接总览")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=root,
                                             prefix=".trace-", suffix=".tmp", delete=False) as stream:
                temporary = stream.name
                stream.write(output)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
        print(f"已生成总览：{len(task.get('items', []))} items，{len(attempts)} attempts，{len(observations)} observations")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"记录检查失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
