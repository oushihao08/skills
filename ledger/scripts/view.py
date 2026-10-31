#!/usr/bin/env python3
"""Render a human task ledger from Trace v1 JSON; validate first, atomically replace 对账台.md. No business side effects."""
import argparse
import collections
from datetime import datetime
import importlib.util
import os
from pathlib import Path
import tempfile

TRACE = Path(__file__).resolve().parents[2] / 'trace/scripts/view.py'
if not TRACE.is_file():
    raise SystemExit('缺少依赖：~/.agents/skills/trace/scripts/view.py')
spec = importlib.util.spec_from_file_location('ledger_trace', TRACE)
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)
cell = trace.cell
LABELS = {'done': '已完成', 'review': '待验收', 'failed': '失败', 'unknown': '待核实',
          'blocked': '受阻', 'running': '运行', 'queued': '排队', 'pending': '待执行', 'skipped': '跳过'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp(value):
    try:
        return text(value) and datetime.fromisoformat(value).utcoffset() is not None
    except ValueError:
        return False


def strings(value):
    return isinstance(value, list) and all(text(v) for v in value)


def state(item):
    stages = [s for s in item['stages'] if s.get('required', True)]
    if not stages or all(s['state'] == 'skipped' for s in stages):
        return 'skipped'
    states = {s['state'] for s in stages}
    for status, result in [('unknown', 'unknown'), ('failed', 'failed'), ('blocked', 'blocked'),
                           ('stale', 'blocked'), ('running', 'running'), ('queued', 'queued')]:
        if status in states:
            return result
    if states != {'succeeded'}:
        return 'pending'
    return 'done' if item.get('acceptance', {}).get('state') == 'accepted' else 'review'


def load(root):
    task, attempts, observations = trace.load(root)
    require(isinstance(task.get('title'), str) and task['title'].strip(), '缺少任务名称')
    require(text(task.get('scope')) and text(task.get('goal_ref')), '缺少范围或目标引用')
    require(strings(task.get('completion_criteria')) and bool(task['completion_criteria']), '验收条件须为非空字符串数组')
    require(strings(task.get('next_actions')), 'next_actions须为字符串数组')
    require(isinstance(task.get('items'), list), 'items须为数组')
    require(timestamp(task.get('updated_at')), 'updated_at须为带时区的ISO时间')
    p = task.get('presentation', {})
    require(isinstance(p, dict), 'presentation须为对象')
    require(p.get('mode', 'auto') in {'auto', 'list', 'matrix', 'grouped'}, '未知展示模式')
    for k in ['columns', 'stage_order']:
        v = p.get(k, [])
        require(isinstance(v, list) and all(isinstance(x, str) for x in v) and len(set(v)) == len(v), f'{k}须为不重复字符串数组')
    for item in task['items']:
        require(bool(item.get('stages')), 'item必须至少有一个阶段')
        require(isinstance(item.get('details', {}), dict), 'details须为对象')
        require(isinstance(item.get('group', ''), str), 'group须为字符串')
        a = item.get('acceptance', {})
        require(isinstance(a, dict) and a.get('state', 'pending') in {'pending', 'accepted', 'rejected'}, '验收状态无效')
        require(strings(a.get('evidence', [])), '验收证据须为非空字符串组成的数组')
        for s in item['stages']:
            require(isinstance(s.get('required', True), bool), 'required须为布尔值')
            require(strings(s.get('evidence', [])), '阶段证据须为非空字符串组成的数组')
            require(s.get('observed_at') is None or timestamp(s['observed_at']), 'observed_at须为空或带时区的ISO时间')
            if s['state'] == 'succeeded':
                attempt = attempts.get(s.get('attempt_id'), {})
                artifacts = attempt.get('artifacts', [])
                verification = attempt.get('verification', [])
                has_artifact = isinstance(artifacts, list) and any(isinstance(v, dict) and text(v.get('ref')) for v in artifacts)
                has_verification = isinstance(verification, list) and any(
                    isinstance(v, dict) and text(v.get('kind')) and text(v.get('result')) and text(v.get('evidence')) for v in verification)
                require(bool(s.get('evidence')) or has_artifact or has_verification, '执行成功缺少证据或核验记录')
        if a.get('state') == 'accepted':
            required = [s for s in item['stages'] if s.get('required', True)]
            require(bool(required) and all(s['state'] == 'succeeded' for s in required), '未执行成功的必需阶段不能验收完成')
            require(any(isinstance(e, str) and e.strip() for e in a.get('evidence', [])), '验收完成缺少证据')
    return task, attempts, observations


def stage_cell(s):
    if s is None:
        return '不适用'
    result = trace.LABELS[s['state']]
    if s.get('required') is False:
        result += '（非必需）'
    if s.get('outcome'):
        result += ' · ' + cell(s['outcome'])
    return result


def table(items, p):
    order = list(p.get('stage_order', []))
    titles = {}
    for item in items:
        for s in item['stages']:
            titles.setdefault(s['id'], s.get('title', s['id']))
            if s['id'] not in order:
                order.append(s['id'])
    order = [k for k in order if k in titles]
    mode = p.get('mode', 'auto')
    if mode in {'auto', 'grouped'}:
        mode = 'matrix' if len(items) > 0 and len(items[0]['stages']) > 1 and all(
            {s['id'] for s in item['stages']} == {s['id'] for s in items[0]['stages']} for item in items) else 'list'
    columns = p.get('columns', [])
    headers = ['事项 / ID', '当前状态'] + ([titles[k] for k in order] if mode == 'matrix' else ['阶段进度 / 业务结论']) + columns
    lines = ['| ' + ' | '.join(cell(h) for h in headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |']
    for item in items:
        stages = {s['id']: s for s in item['stages']}
        values = [cell(item.get('title', item['id'])) + ' / ' + cell(item['id']), LABELS[state(item)]]
        if mode == 'matrix':
            values += [stage_cell(stages.get(k)) for k in order]
        else:
            values += ['<br>'.join(cell(s.get('title', s['id'])) + '：' + stage_cell(s) for s in item['stages'])]
        values += [cell(item.get('details', {}).get(k)) for k in columns]
        lines.append('| ' + ' | '.join(values) + ' |')
    return lines


def render(task, attempts, observations):
    items = task['items']
    counts = collections.Counter(state(i) for i in items)
    lines = ['# ' + cell(task['title']), '', '范围：' + cell(task['scope']), '',
             '目标/计划：' + cell(task.get('goal_ref')), '', '记录更新：' + cell(task.get('updated_at')), '',
             '**共 ' + str(len(items)) + ' 项**；' + ' · '.join(f'{label} {counts[k]}' for k, label in LABELS.items() if counts[k]), '',
             '口径：每项只归一类；执行成功≠验收通过。记录不是实时监听，恢复须核实外部状态。', '', '## 需关注', '']
    issues = 0
    for item in items:
        for s in item['stages']:
            if s['state'] in {'failed', 'blocked', 'unknown', 'stale'}:
                lines.append(f"- {cell(item.get('title', item['id']))} / {cell(s.get('title', s['id']))}：{stage_cell(s)}；最后核实 {cell(s.get('observed_at'))}")
                issues += 1
        if item.get('acceptance', {}).get('state') == 'rejected':
            lines.append(f"- {cell(item['id'])} 验收未通过：{cell(item['acceptance'].get('note'))}")
            issues += 1
    for key, obs in observations.items():
        if obs['status'] == 'open':
            lines.append(f"- [{key}](observations/{key}.json)：{cell(obs.get('title'))}；{cell(obs.get('impact'))}")
            issues += 1
    if not issues:
        lines.append('当前记录无异常；不代表未核实的外部状态正常。')
    lines += ['', '## 下一步', ''] + ['- ' + cell(v) for v in task.get('next_actions', [])]
    lines += ['', '## 任务对账', '']
    p = task.get('presentation', {})
    if p.get('mode') == 'grouped':
        groups = {}
        for item in items:
            groups.setdefault(item.get('group') or '未分组', []).append(item)
        for name, group in groups.items():
            lines += ['### ' + cell(name), ''] + table(group, p) + ['']
    else:
        lines += table(items, p)
    lines += ['', '## 阶段统计', '', '| 阶段 | 适用项 | 必需项 | 执行成功 | 排队 | 运行 | 失败 | 待核实 | 受阻/过期 | 跳过 | 待执行 |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    grouped = {}
    for item in items:
        for s in item['stages']:
            grouped.setdefault(s['id'], []).append(s)
    for key, stages in grouped.items():
        c = collections.Counter(s['state'] for s in stages)
        vals = [cell(stages[0].get('title', key)), len(stages), sum(s.get('required', True) for s in stages), c['succeeded'], c['queued'], c['running'], c['failed'], c['unknown'], c['blocked'] + c['stale'], c['skipped'], c['planned']]
        lines.append('| ' + ' | '.join(map(str, vals)) + ' |')
    lines += ['', '## 验收条件', ''] + ['- ' + cell(v) for v in task['completion_criteria']]
    lines += ['', '<details>', '<summary>状态证据与尝试历史</summary>', '']
    for item in items:
        lines += ['### ' + cell(item.get('title', item['id'])), '']
        for s in item['stages']:
            a = s.get('attempt_id')
            lines.append(f"- {cell(s.get('title', s['id']))}：{stage_cell(s)}；核实 {cell(s.get('observed_at'))}；尝试 " + (f'[{a}](attempts/{a}.json)' if a else '—') + '；证据 ' + cell(s.get('evidence')))
        lines.append('- 验收：' + cell(item.get('acceptance')))
    lines += ['', '| 尝试 | Item / 阶段 | 状态 | 前次 | 外部ID | 结果 / 错误 |', '| --- | --- | --- | --- | --- | --- |']
    for key, a in attempts.items():
        lines.append('| ' + ' | '.join([f'[{key}](attempts/{key}.json)', cell(a['item_id'] + '/' + a['stage_id']), trace.LABELS[a['status']], cell(a.get('previous_attempt_id')), cell(a.get('external_ids')), cell(a.get('artifacts') or a.get('error'))]) + ' |')
    lines += ['', '### 观察记录（全部状态）', '', '| 记录 | 类型 / 状态 | 摘要 | 影响 |', '| --- | --- | --- | --- |']
    for key, obs in observations.items():
        lines.append('| ' + ' | '.join([f'[{key}](observations/{key}.json)', cell(obs['kind'] + ' / ' + obs['status']), cell(obs.get('title')), cell(obs.get('impact'))]) + ' |')
    lines += ['', '</details>', '']
    return '\n'.join(lines)


def write_view(root):
    data = load(root)
    output = render(*data)
    dest = root / '对账台.md'
    require(not dest.is_symlink(), '拒绝覆盖符号链接')
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=root, prefix='.ledger-', delete=False) as f:
            temp = f.name
            f.write(output)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, dest)
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    try:
        task, attempts, _ = write_view(args.directory.resolve(strict=True))
        print(f"已生成对账台：{len(task['items'])} items / {len(attempts)} attempts")
    except (OSError, ValueError, TypeError, KeyError) as e:
        print('记录检查失败：' + str(e))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
