---
name: release
description: |
  发布工具 - 用于发布生产环境。自动执行：推代码 → 合并 UAT → Master → 创建 GitHub Release。
  
  触发词：
  - "发布"、"发布生产环境"、"发布正式环境"
  - "release"、"创建 release"
  - "打包发布"
  
  使用场景：
  - 用户想要发布生产环境
  - 用户想要创建新的 GitHub Release
  - 用户想要合并 UAT 到 Master 并发布
---

# 律小购发布工具

## 功能说明

自动执行以下发布流程：

1. 切换到 UAT 分支并拉取最新代码
2. 切换到 Master 分支并拉取最新代码
3. 合并 UAT 到 Master（冲突时选择 UAT 代码）
4. 推送到远程 Master 分支
5. 获取最新 tag 并计算新版本号（+0.0.1）
6. 创建新 tag 并推送
7. 创建 GitHub Release（自动生成 Release Notes）

## 命令位置

```bash
/Users/jack/Documents/codes/lvgou/scripts/release.mjs
```

## 使用方式

### 发布单个项目

```bash
node /Users/jack/Documents/codes/lvgou/scripts/release.mjs lvgou_app_c_vue
```

### 发布多个项目

```bash
node /Users/jack/Documents/codes/lvgou/scripts/release.mjs lvgou_app_b_vue,lvgou_app_c_vue
```

### 干跑模式（预览不执行）

```bash
node /Users/jack/Documents/codes/lvgou/scripts/release.mjs lvgou_app_c_vue --dry-run
```

### 仅推代码（不创建 Release）

```bash
node /Users/jack/Documents/codes/lvgou/scripts/release.mjs lvgou_app_c_vue --push-only
```

### 跳过合并（直接在 Master 上发布）

```bash
node /Users/jack/Documents/codes/lvgou/scripts/release.mjs lvgou_app_c_vue --no-merge
```

## 可用项目

| 项目 | 路径 | 说明 |
|------|------|------|
| lvgou_app_b_vue | `/Users/jack/Documents/codes/lvgou/lvgou_app_b_vue` | B 端 App |
| lvgou_app_c_vue | `/Users/jack/Documents/codes/lvgou/lvgou_app_c_vue` | C 端 App |

## 配置文件

每个项目根目录有 `release.config.json` 配置文件：

```json
{
  "name": "lvgou_app_c_vue",
  "description": "律小购 C 端 App",
  "branches": {
    "main": "master",
    "develop": "uat"
  }
}
```

## 版本规则

- 每次发布版本号 +0.0.1（如 1.0.0 → 1.0.1）
- 版本号从 GitHub tag 获取

## 执行流程

```
1. git checkout uat && git pull origin uat
2. git checkout master && git pull origin master
3. git merge uat -X theirs --no-edit
4. git push origin master
5. 获取最新 tag: git describe --tags --abbrev=0
6. 计算新版本号: bumpPatchVersion
7. git tag v1.0.x
8. git push origin v1.0.x
9. gh release create v1.0.x --title "v1.0.x" --notes-file ...
```

## 示例对话

**用户**: 帮我发布 C 端生产环境

**AI**: 好的，我来帮你发布 C 端生产环境。

```bash
node /Users/jack/Documents/codes/lvgou/scripts/release.mjs lvgou_app_c_vue
```

**用户**: 先预览一下 B 端的发布流程

**AI**: 好的，使用干跑模式预览：

```bash
node /Users/jack/Documents/codes/lvgou/scripts/release.mjs lvgou_app_b_vue --dry-run
```

## 注意事项

1. **冲突处理**：合并冲突时自动选择 UAT 分支的代码
2. **权限要求**：需要有 Git push 权限和 GitHub Release 创建权限
3. **网络要求**：需要能访问 GitHub
4. **环境要求**：需要安装 `gh` CLI 工具并登录

## 前置条件

检查 `gh` 是否已登录：

```bash
gh auth status
```

如果未登录，执行：

```bash
gh auth login
```
