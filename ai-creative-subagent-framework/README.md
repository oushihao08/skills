# AI Creative Sub-Agent Framework / AI 创意影视制作子Agent调度框架

> **AI script breakdown → team dispatch → image/video generation**
> **AI 拆解脚本 → 调度创意团队 → 生图生视频**

A standardized sub-agent orchestration skill for AI-powered creative production. Contains 5 specialized roles (Director, Art Director, Director of Photography, Brand Director, AI Artist) and a 4-stage workflow.

符合 [agentskills.io](https://agentskills.io/specification) 开放标准，兼容主流 AI agent harness。

---

## 目录

- [角色介绍](#角色介绍)
- [快速开始](#快速开始)
- [安装指南](#安装指南)
  - [Claude Code](#claude-code)
  - [Claude Desktop](#claude-desktop)
  - [Codex CLI (OpenAI)](#codex-cli-openai)
  - [OpenClaw](#openclaw)
  - [Hermes (Nous Research)](#hermes-nous-research)
- [使用示例](#使用示例)
- [自定义指南](#自定义指南)
- [发布到平台](#发布到平台)
  - [GitHub Marketplace](#github-marketplace)
  - [RED Skill (小红书)](#red-skill-小红书)
  - [Coze (扣子)](#coze-扣子)
- [文件结构](#文件结构)
- [License](#license)

---

## 角色介绍

| 角色 | 职责 | 汇报对象 |
|------|------|---------|
| **导演** (Director) | 脚本分解、创意构思、分镜脚本 | 总导演（用户） |
| **美术指导** (Art Director) | 场景设计、影调方案、视觉参考 | 导演 |
| **摄影指导** (Director of Photography) | 运镜设计、构图、布光 | 导演 |
| **品牌总监** (Brand Director) | 品牌策略审核、合规检查、视觉审核 | 总导演（与导演平级）|
| **AI艺术家** (AI Artist) | 技术可行性评估、提示词优化、质量把控 | 总导演 |

### 标准工作流

```
总导演 → 导演 → (美术指导 ∥ 摄影指导) → (品牌总监 ∥ AI艺术家) → 总导演终审
```

---

## 快速开始

1. 按下方指南安装到你的 harness
2. 在对话中输入触发词如 "调用导演角色" 或 "开始一个创意项目"
3. 或手动调用：`/ai-creative-subagent-framework 帮我做脚本拆解`

---

## 安装指南

### Claude Code

```bash
# 方式 1：直接安装 .skill 包
claude skills install ./creative-subagent-framework.skill

# 方式 2：复制到技能目录
cp -r creative-subagent-framework ~/.claude/skills/

# 验证
ls ~/.claude/skills/ai-creative-subagent-framework/
```

### Claude Desktop

```bash
# 复制到技能目录
cp -r creative-subagent-framework ~/.claude/skills/

# 在对话中输入触发词激活
```

### Codex CLI (OpenAI)

```bash
# 复制到技能目录
cp -r creative-subagent-framework ~/.agents/skills/

# 验证 TOML 配置
cat ~/.agents/skills/ai-creative-subagent-framework/agents.toml

# 使用 Manager-Worker 模式：
codex "I need to create a creative project. Activate the creative-subagent-framework."
```

### OpenClaw

```bash
# 复制到技能目录
mkdir -p ~/.openclaw/skills/ai-creative-subagent-framework
cp -r creative-subagent-framework/* ~/.openclaw/skills/ai-creative-subagent-framework/

# 注册技能
openclaw skill register ai-creative-subagent-framework

# 使用：在对话中输入触发词
```

### Hermes (Nous Research)

```bash
# 复制到技能目录
cp -r creative-subagent-framework ~/.hermes/skills/

# 使用：在对话中输入触发词
# "开始创意项目调度，调用导演角色"
```

---

## 使用示例

### 完整的影视制作调用

```python
# 阶段 1：调用导演拆解脚本
Agent(
    description="导演角色",
    prompt=f"""从 references/director-agent.md 读取完整提示词

## 当前任务
分析以下脚本，输出完整分镜

## 项目上下文
- 项目名称：新产品发布会开场视频
- 项目类型：发布会开场视频
- 品牌：创新科技
- 行业：科技
- 时长：120秒
- 核心创意：科技突破，改变世界
- 叙事结构：三段式：困境→突破→未来

[粘贴脚本内容]""",
    subagent_type="claude"
)
```

### 快速调用子角色

```claude
/ai-creative-subagent-framework 调用美术指导，基于导演分镜设计视觉方案
```

---

## 自定义指南

### 替换占位符

所有提示词模板使用 `[PLACEHOLDER]` 系统，详见 `references/agent-templates.md`。

使用前将以下占位符替换为实际值：

```
[PROJECT_NAME]        → 项目名称
[BRAND_NAME]          → 品牌名称
[PRODUCT_NAME]        → 产品名称
[INDUSTRY_VERTICAL]   → 行业
[CREATIVE_METAPHOR]   → 核心创意隐喻
[IMAGE_GEN_TOOL]      → AI 生图工具
[BRAND_TONE]          → 品牌调性
```

### 添加新角色

1. 在 `references/` 下创建 `[role]-agent.md`
2. 遵循 `references/agent-templates.md` 中的模板结构
3. 在 `SKILL.md` 的角色层级图中添加

---

## 发布到平台

### GitHub Marketplace

1. 创建 GitHub 仓库：`ai-creative-subagent-framework`
2. 推送到主分支
3. 在仓库设置中启用 "Marketplace" 分类
4. 创建 Release 并打 tag

```bash
git init
git add .
git commit -m "Initial release v1.0.0"
git remote add origin https://github.com/birdilsss-byte/ai-creative-subagent-framework.git
git push -u origin main
git tag v1.0.0
git push origin v1.0.0
```

### RED Skill (小红书)

1. 在小红书创作者中心 → 技能创作
2. 上传 `creative-subagent-framework/` 文件夹
3. 分类选择：创意工具
4. 等待审核通过

### Coze (扣子)

本 skill 的纯 prompt 格式与 Coze 插件架构不完全兼容。请参考 `coze/README-coze.md` 在 Coze 工作台中手动搭建多 Agent 工作流。

---

## 文件结构

```
creative-subagent-framework/
├── SKILL.md                       # 主入口（agentskills.io 格式）
├── LICENSE                        # MIT License
├── README.md                      # 本文档
├── .gitignore
├── agents.toml                    # Codex CLI Manager-Worker 配置
├── plugin.json                    # GitHub Marketplace manifest
├── references/
│   ├── agent-templates.md         # 占位符系统 + 自定义角色指南
│   ├── workflow-patterns.md       # 标准工作流模式
│   ├── director-agent.md          # 导演子agent提示词模板
│   ├── art-director-agent.md      # 美术指导子agent提示词模板
│   ├── dop-agent.md               # 摄影指导子agent提示词模板
│   ├── brand-director-agent.md    # 品牌总监子agent提示词模板
│   └── ai-artist-agent.md         # AI艺术家子agent提示词模板
├── scripts/
│   └── install.sh                 # 跨 Harness 安装脚本
└── coze/
    └── README-coze.md             # Coze 适配指南
```

---

## License

MIT — 自由使用、修改、分发。
