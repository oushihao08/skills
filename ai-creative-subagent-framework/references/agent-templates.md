# 占位符系统与自定义角色指南 (Agent Templates Reference)

## 占位符一览

本 Skill 所有提示词模板使用 `[PLACEHOLDER]` 系统参数化。使用前将占位符替换为实际值。

### 核心项目信息

| 占位符 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `[PROJECT_NAME]` | string | 项目名称 | 新品上市发布会 |
| `[BRAND_NAME]` | string | 品牌名称 | 品牌X |
| `[PRODUCT_NAME]` | string | 产品/服务名称 | 产品Y |
| `[PRODUCT_CATEGORY]` | string | 产品类别 | 抑制剂 / 新能源车 |
| `[INDUSTRY_VERTICAL]` | string | 行业/垂直领域 | 医药 / 汽车 / 快消 / 科技 |
| `[PROJECT_LEAD]` | string | 总导演/项目负责人 | 爵士 / PM |

### 创意参数

| 占位符 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `[PROJECT_TYPE]` | string | 项目类型 | 发布会开场视频 / 品牌TVC |
| `[VIDEO_DURATION]` | string | 视频时长 | 180秒 / 3分钟 |
| `[SHOT_COUNT]` | string | 镜头数量 | 20个镜头 |
| `[NARRATIVE_STRUCTURE]` | string | 叙事结构 | 三段式：困境→进化→领航 |
| `[CREATIVE_METAPHOR]` | string | 核心创意隐喻 | 赛车引擎隐喻药物发展 |
| `[OUTPUT_FORMAT]` | string | 输出格式 | 分镜表格 / 提示词列表 |

### 品牌与受众

| 占位符 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `[BRAND_TONE]` | string | 品牌调性集合 | 宏大、力量、大气、希望 |
| `[BRAND_TONE_1..4]` | string | 品牌调性（逐条） | 宏大 / 力量 / 大气 / 希望 |
| `[BRAND_MESSAGE_1..3]` | string | 核心品牌信息 | 双擎驱动 / 全面征服 |
| `[TARGET_AUDIENCES]` | string | 目标受众 | 医生、患者、投资者 |
| `[AUDIENCE_1..3]` | string | 受众（逐条） | 医生 / 患者 / 投资者 |

### 视觉与技术

| 占位符 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `[IMAGE_GEN_TOOL]` | string | 图像生成工具 | Seedream 4.0 / Midjourney |
| `[TECH_STACK]` | string | 技术栈 | 即梦MCP + Seedream |
| `[COLOR_PALETTE]` | string | 色彩方案描述 | 蓝橙双色能量体系 |
| `[PRIMARY_COLOR]` | string | 主色 | #1E90FF (道奇蓝) |
| `[SECONDARY_COLOR]` | string | 辅色 | #FF8C00 (暗橙) |
| `[ACCENT_COLOR]` | string | 强调色 | 蓝橙渐变 |
| `[STYLE_ADJECTIVE]` | string | 艺术风格形容词 | 科学 / CG / 手绘 |
| `[SPECIAL_STYLE]` | string | 特殊风格 | Need for Speed / 国风 |

### 行业与合规

| 占位符 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `[INDUSTRY_COMPLIANCE]` | string | 行业合规要求 | 医药广告法 / 食品广告法 |
| `[VISUAL_REFERENCE_KEYWORDS]` | string | 视觉参考搜索词 | CG赛车风格 / 分子结构 |
| `[ACTION_SCENE_TYPE]` | string | 动作场景类型 | 赛车追逐 / 城市奔跑 |
| `[SUBJECT_KEYWORDS]` | string | 主体描述关键词 | 赛车、引擎、分子结构 |
| `[ACTION_KEYWORDS]` | string | 动作关键词 | 加速、碰撞、突破 |
| `[ENVIRONMENT_KEYWORDS]` | string | 环境关键词 | 赛道、实验室、未来城市 |
| `[STYLE_SPECIFIC_PROMPT_ADDON]` | string | 风格专用提示词 | CG渲染参数 |
| `[VISUAL_STYLE_1..3]` | string | 视觉风格关键词 | 科技感/信任感/大气 |

---

## 使用流程

### 首次使用

1. 阅读 SKILL.md 了解整体框架
2. 打开对应的 reference 文件（如 `references/director-agent.md`）
3. 将文档中的所有 `[占位符]` 替换为实际项目值
4. 将替换后的完整提示词作为 `prompt` 参数传入 `Agent()` 工具调用

### 快速替换模板

```claude
Agent(
    description="[角色名称]",
    prompt=f"""从 references/[role]-agent.md 读取完整提示词

## 当前任务
[具体任务描述]""",
    subagent_type="claude"
)
```

---

## 自定义新角色指南

本框架设计为可扩展的。如需新增角色，请按以下步骤：

### 步骤 1：创建角色提示词文件

在 `references/` 目录下新建 `[role-name]-agent.md`，遵循以下结构：

```markdown
# [角色名]子agent提示词模板 ([English] Sub-Agent Prompt Template)

## Identity
- **职位**: [Title]
- **专长**: [Expertise areas]
- **工作风格**: [Style description]

## Core Duties
1. [Duty 1]
2. [Duty 2]
3. [Duty 3]

## Working Principles
- [Principle 1]
- [Principle 2]

## Expertise Areas
- [Expertise 1]
- [Expertise 2]

## Output Deliverables
1. [Deliverable 1]
2. [Deliverable 2]

## Permission Boundaries
- ✅ [Can do 1]
- ❌ [Cannot do 1]

## Reporting Hierarchy
- **直接上级**: [Superior role]
- **最终决策者**: [Decision maker]
- **协作同事**: [Colleagues]

## Workflow Next Steps
完成工作后：
1. [Step 1]
2. [Step 2]

## Usage Example
\```claude
Agent(
    description="[role-name]",
    prompt=f"""...
## 当前任务
[TASK_DESCRIPTION]""",
    subagent_type="claude"
)
\```
```

### 步骤 2：更新 SKILL.md

在 SKILL.md 的角色层级图和调用模板部分添加新角色的条目。

### 步骤 3：更新 workflow-patterns.md

在对应工作流模式中添加新角色的参与路径。

### 步骤 4：更新 metadata

在 SKILL.md 的 YAML frontmatter 中添加新角色的 trigger-keyword。
