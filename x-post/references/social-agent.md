# social-agent 工具映射

根目录：当前工作区仓库根目录下的 `social-agent/`。从当前工作目录定位仓库，不依赖某台电脑的绝对路径。先读当前 README、适用规则与相关实现，版本变化后重新核对。不要输出 .env、密钥或 Cookies。

| 工作 | 已有入口 | 边界 |
| --- | --- | --- |
| 查询与平台执行 | `src/runtime/x_command.ts`：`XCommand.run(name, args, options)` | 复用命令限速与冷却；whoami、search、profile、tweets、timeline、post 使用当前适配器参数。 |
| 搜索参考 | `XCommand.run('search', {query, product, limit})` | 题材和时间窗取当前任务；支持排序才使用，不把搜索结果叫全站爆款。 |
| 参考账号与自有表现 | `XCommand.run('tweets', {username, limit})` | 区分原创、转发与回复；保留可见指标、采集时间，缺失不补零。 |
| 时间线线索 | `src/discovery/x/x_discoverer.ts`：`findHotPosts` | 生产模式实际读个人时间线，未做全站热榜或按 domains 筛选；非生产模式有模拟数据，不能作为事实或热度证据。需要完整指标时读运行层原始结果。 |
| 蓝 V 搜索 | `src/discovery/x/x_search.ts` | 专为关系筛选补字段；选题搜索不套互关、蓝 V 或粉丝条件。 |
| 审定图文发送 | `XCommand.run('post', {text, images}, {write:true})` | 复用现有 OpenCLI twitter/post；当前 images 是逗号分隔的本地路径字符串，最多 4 张 jpg/png/gif/webp；版本变化后查实际定义。核对完整正文与上传预览，提交一次，再核实平台正文与附件。 |
| 共享额度和历史 | `src/storage/db.ts`：`LocalDatabase` | 读取 getDailyCount、getCircuitBreaker，按当前配置 reserveAction 原子预留，核实成功后 recordAction；确认未提交才 releaseAction。 |

## 调用约束

- 在项目目录使用现有运行时加载上述模块，不另建采集或发布系统。发现命令与参数时读取 opencli-usage 并核对实时帮助；查询预算沿用 smart-search。必要直接 OpenCLI 只读查询保留来源记录；实际发送仍落实项目保护。
- XCommand 不自动提供账号互斥、最终内容去重或额度事务，调用方须落实这些条件；缺少保护时留草稿，不能只写“已检查”。
- `npm run x:post -- "主题"` 和 `x:post:cruise` 会再生成文案，不能代替发送 Skill 已审核的最终图文。不要擅自启动巡航。
- `src/executor/x/x_executor.ts` 的 post(content, mediaUrls?) 当前只传 text，没有转交图片；不能因为签名有图片参数就认定支持图文。
- 不使用模型故障后降级为预设话术的路径；不拿模拟数据替代失败采集。写入结果未知先核实，不盲重发。已确认成功不能被页面收尾异常覆盖。
- 使用后台浏览器核对，不打断用户。工具或保护缺失就报告具体缺口，不在自动发帖轮次改程序或配置。
