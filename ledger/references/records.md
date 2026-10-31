# 记录与写入

事实格式复用 `~/.agents/skills/trace/references/records.md` 的v1；首次操作必须读取该文档。trace是已安装依赖，缺失时明确报告，不伪造关联或改用不校验的生成器。

目录最小为task.json、对账台.md；发生尝试后才建attempts，发生问题后才建observations。证据优先链接既有产物。task.json至少含schema_version、id、title、goal_ref、scope、completion_criteria、items、next_actions、updated_at。

title、goal_ref、scope为非空字符串；completion_criteria为非空字符串数组且至少一项；next_actions为字符串数组，可为空；items为数组。updated_at为带时区ISO时间；stage.observed_at未知可省略或null，填写时也须带时区。evidence数组中的每项须为非空字符串。成功阶段至少提供阶段evidence、带非空ref的artifact、或同时含非空kind/result/evidence的verification之一；生成器只校验凭证结构，不验证凭证真实性，也不把核验结论自动判为通过。

每个item至少一个阶段；单步事项也作为一个阶段。item可增加：

- `group`：本任务分组。
- `details`：自定义业务字段对象，如负责人、评分、飞书记录ID；不承担状态计算。
- `acceptance`：`{"state":"pending|accepted|rejected","evidence":[],"note":"验收结论"}`；缺省pending。accepted要求证据及所有必需阶段succeeded。若用户取消/缩减范围，保留原item并记观察，不删除原身份。

阶段可增加 `required:false` 表示明确不适用，默认必需。可选阶段失败仍在问题区展示，不能遮蔽；必需阶段skipped不算成功。阻塞、未知和执行状态按trace规则记录。

`presentation`为可选任务级展示配置：

```json
{"mode":"auto","columns":["负责人","评分"],"stage_order":["author","answer","score"]}
```

mode可为auto、list、matrix、grouped；columns从item.details取值；stage_order只调整排列，未列出的阶段仍展示。分组模式使用item.group。列表适合异构事项，矩阵适合同阶段批次；auto依实际阶段集合决定，不硬编码项目。

## 写入与恢复

使用本地原子替换：先写同目录临时文件，再rename；尝试/观察先写，task当前引用后写，最后生成展示。对已终态的尝试不改原事实，纠正通过新观察说明；同一在途尝试可补回执与核验。单一写入者是本工具前提，不承诺多进程合并或多文件事务；中断后生成器若拒绝关联，先核对并补齐原记录，不重跑业务来补日志。

总览快照的互斥item分类：全部跳过→跳过；必需阶段未知→待核实；失败→失败；受阻/过期→受阻；运行→运行；排队→排队；其余未成功→待执行；必需阶段均成功且验收accepted→已完成；均成功但验收未通过→待验收。失败优先于在途状态，因此每item只计一次；阶段矩阵保留完整并行情况。统计只表达记录，不是业务调度判断。

不必给每阶段赋权。必须展示总item数、状态和最近更新时间；有外部观察时展示observed_at。新增、删减范围说明前后数量及依据。生成对账台不会写业务API或修改JSON。
