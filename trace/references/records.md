# 记录结构 v1

按实际观察填写；下列ID和视频内容只演示结构，不是默认任务。无资料用null或空数组，不能照抄示例值。JSON文件不插入注释。

## 目录与事实源

```text
项目/执行观察/
  README.md                 项目任务索引、目录维护边界
  任务短ID/
    task.json               当前item/阶段、范围和恢复入口
    总览.md                 view.py生成，不手改
    attempts/A001.json      一次尝试；重试使用新ID
    observations/O001.json  问题、成果或经验；后续处理在updates中保留
    evidence/               按需建立；优先引用原产物，不复制无关正文
```

目录ID用字母数字、下划线、连字符；文件名与记录id一致。初始化只建本次需要的目录。业务项目指当前计划归属的项目，主项目/期次另在scope写清；不能把运行记录塞入skill或案件附件目录。

## task.json

```json
{
  "schema_version": 1,
  "id": "video-20261017",
  "title": "两镜头成片",
  "goal_ref": "当前会话或已有计划的路径/ID",
  "scope": "镜头03和04至上传；发布另按既有授权",
  "completion_criteria": ["本次用户确定的验收条件"],
  "items": [{
    "id": "shot03",
    "title": "镜头03",
    "plan_ref": "计划item-03",
    "stages": [{
      "id": "render",
      "title": "渲染",
      "state": "succeeded",
      "outcome": "仅抽帧通过，播放/听音待核",
      "attempt_id": "A003",
      "observed_at": "2026-10-17T13:00:00+08:00",
      "evidence": ["产物路径或证据ID"]
    }]
  }],
  "next_actions": ["核实原任务，不重复派发"],
  "updated_at": "2026-10-17T13:00:00+08:00"
}
```

stage.state：planned、queued、running、succeeded、failed、blocked、skipped、unknown、stale。blocked只表示这个阶段受阻，不改变/goal引擎状态。outcome写实际业务结论，如partial、repair、submitted、review_pending等；没有结论用null，不能用succeeded代替业务验收。

observed_at写本次确实核实的时间，带时区；状态过期不靠改时间伪装已核实。计划变更保留来源，不由Trace增加任务或验收门槛。

## attempts/<ID>.json

```json
{
  "id": "A003",
  "item_id": "shot03",
  "stage_id": "render",
  "previous_attempt_id": "A002",
  "status": "succeeded",
  "started_at": "2026-10-17T12:58:00+08:00",
  "finished_at": "2026-10-17T13:00:00+08:00",
  "inputs": [{"ref": "script.md", "version": "s1", "sha256": null}],
  "configuration": {"speed": 0.9},
  "changes_from_previous": ["修正音频路径"],
  "external_ids": {"call_id": "c3"},
  "environment": {"target": "local", "runtime_version": null},
  "artifacts": [{"ref": "shot03-v3.mp4", "sha256": null}],
  "verification": [{"kind": "frame_review", "result": "checked", "evidence": "三张抽帧"}],
  "error": null
}
```

只保存当前可取得的配置，区分请求值与实际生效值。不默认读取.env、凭证或全部环境。configuration允许领域字段；模型/提示词/素材/代码版本等凡影响复现且已知的条件均记录或引用。外部ID包括业务任务、attempt、request、call、操作、平台条目等；记录真实名称，未知用null。

终态succeeded/failed/skipped不是自动验收；晚到结果与输入不匹配，当前stage标stale，尝试保留实际执行结果。unknown的finished_at不能猜填。缺失历史不要重建为确定事实。

## error：失败或异常的结构

```json
{
  "kind": "process",
  "code": "E_AUDIO_MISSING",
  "message": "E_AUDIO_MISSING: narration.wav not found",
  "exit_code": 2,
  "http_status": null,
  "chain": [],
  "raw_error_ref": "evidence/A002-error.txt",
  "stderr_ref": "evidence/A002-error.txt",
  "stdout_ref": null,
  "stack_ref": null,
  "capture": "complete",
  "redactions": [],
  "impact": "镜头03未生成新产物",
  "confirmed_cause": null,
  "hypotheses": ["文件路径可能不正确，尚未确认"],
  "actions": []
}
```

capture：complete仅表示取得了工具返回的完整错误文本，不保证上游未截断；已知截断写truncated，遮蔽敏感字段写redacted，拿不到原文写unavailable。发生、环境、输入和关联ID从attempt读取，不在error重复维护。工具已只返回安全错误摘要时保留其原貌，注明上游未提供的信息，不收集受限私有正文。

## observations/<ID>.json

```json
{
  "id": "O001",
  "kind": "result",
  "status": "open",
  "title": "镜头03画面改善，声音尚未确认",
  "item_ids": ["shot03"],
  "attempt_ids": ["A001", "A003"],
  "facts": ["用户反馈A3画面优于A1；A3仅抽帧，未播放未听音"],
  "hypotheses": ["节奏变化可能与speed修改有关，因果未验证"],
  "evidence": ["对应用户反馈及产物位置"],
  "impact": "画面有正向反馈，不能宣布成片合格",
  "updates": [],
  "lesson": null,
  "created_at": "2026-10-17T13:01:00+08:00",
  "updated_at": "2026-10-17T13:01:00+08:00"
}
```

kind：issue、result、lesson。status：open、resolved、candidate、validated、rejected。issue解决时保留原facts，updates新增时间、动作、结果和证据；重复发生可新增关联attempt并更新发生次数，不逐次复制整份报错。

lesson对象仅用于经验候选，包含`conditions`、`reproduce`、`limitations`、`counterexamples`和`skill_ref`（未生成时null）。validated须有复现或独立核验的具体证据及适用范围；一次“效果好”、一次修复或指标相关不能直接推广。保存失败反例；用户要求提炼skill时再使用当前适用的skill创建流程。

## 更新顺序

先原子写尝试/观察，再更新task.json的当前引用，最后运行view.py。不同时手工维护JSON与Markdown两套状态。单一记录负责者写入；交接移交负责者并核实外部状态。脚本报关联缺失时先修复记录，不自动补造文件或业务结果。
