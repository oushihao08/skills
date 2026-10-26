---
name: lvgou-layout-style
description: Lvgou 项目的 Vue 3、UnoCSS、Row/Column 布局和主题样式规范。用于创建、修改、审查 Lvgou PC、Generate、Admin、H5、AI 官网页面，以及调整 uno.config.js、src/layout、uno/ 和 Sass 样式边界时。
---

# Lvgou Layout Style

这是 Lvgou 生态的布局与样式执行规范。它约束页面骨架、UnoCSS 规则来源、主题 token、第三方适配器和 Sass 使用边界，保证不同项目的页面写法一致。

## 核心顺序

按以下顺序处理样式任务：

1. 读取项目内的 `AGENTS.md`、`CLAUDE.md`、`uno.config.*`、`src/layout/` 和 Sass 入口。
2. 判断项目是 PC、后台、Generate、H5 还是 AI 官网，并确认 UnoCSS 版本。
3. 先设计 `Page → Row/Column → section → content` 的布局骨架。
4. 使用现有布局组件和 `presetWind` 原子规则。
5. 只有稳定高频的组合才新增 shortcut。
6. 最后才增加页面局部样式或第三方组件覆盖。

## 强制原则

- `presetWind` 是标准 UnoCSS 原子规则的基础来源。不要重复实现 `flex`、`justify-*`、`items-*`、`w-*`、`p-*` 等标准规则。
- `uno.config.js` 是项目 UnoCSS 入口；项目内的 `uno/` 按主题、规则、shortcut、safelist、preflight 和 adapter 拆分职责。
- 页面布局优先使用 `Row`、`Column`、`Grid`、`Page`。除非需要语义 HTML、第三方组件 DOM 或特殊定位，不用 `div + flex` 替代布局组件。
- `Row/Column` 默认不强制 `w-full h-full`。需要满尺寸时显式使用 `fill`、`size-full` 或 `Page`。
- `Flex.gap` 必须输出 CSS `gap`，不得用 `padding` 代替。
- PC 使用本地 px theme scale，不依赖 `@unocss/preset-rem-to-px`。
- H5 是否使用 `presetRemToPx` 必须由 H5 项目显式配置，不能由公共规则隐式开启。
- Element Plus、Varlet 等第三方规则只能放在 `uno/adapters/`，通过配置选择启用；基础主题不能绑定第三方 DOM 选择器。
- 旧 Sass 通用类迁移到 Uno 前先保留兼容映射；不要一次性删除业务 Sass。
- 不新增与原子类同名的 shortcut，不使用自引用 shortcut，不允许同名 shortcut 静默覆盖。
- `hidden` 保留 Uno/Wind 的隐藏语义；溢出隐藏使用 `o-hidden` 或 `overflow-hidden`，编辑器等组件使用自己的语义类名。
- 不把业务图片尺寸、业务页面特殊结构和组件库深层 DOM 覆盖塞入公共主题。

## 布局决策

使用 `Row` 处理横向主轴，使用 `Column` 处理纵向主轴：

```vue
<Page>
  <Column fill gap="16" class="min-h-0">
    <Row x="between" y="center">
      <span class="text-lg font-semibold">标题</span>
      <Row gap="8">操作</Row>
    </Row>
    <Column gap="12" class="scroll-region">
      内容
    </Column>
  </Column>
</Page>
```

组件职责：

- `Page`：页面高度、内容滚动、安全区。
- `Row`：横向排列、主轴 x 对齐、交叉轴 y 对齐。
- `Column`：纵向排列、主轴 y 对齐、交叉轴 x 对齐。
- `Grid`：二维等宽或自定义列布局。
- `Flex`：只有 Row/Column 无法表达时才直接使用。

避免：

```vue
<div class="box-border flex flex-row justify-between items-start h-full w-full">
```

优先写成：

```vue
<Row fill x="between" y="start">
```

## 主题和单位

- 优先使用 `theme.js` 中的语义色、字号、圆角、阴影和层级。
- PC 的数字尺寸由 `spacing/width/height/fontSize/lineHeight` px scale 提供，例如 `w-320` 生成 `320px`。
- 迁移固定尺寸时可使用显式后缀：`w-320px`、`p-10px`、`gap-12px`、`lh-20px`。
- 不用负 margin、绝对定位或全局 `!important` 修补布局问题，除非已确认是第三方组件边界。
- 文字必须有可读的字号和行高，禁止为了塞入一行而压缩文字或让内容重叠。

## 第三方适配器

检查项目配置中的 adapter 开关：

```js
const adapters = {
  elementPlus: true,
  varlet: false,
}
```

适配文件位于 `uno/adapters/`。只启用项目实际使用的组件库。基础 `theme.js` 和公共 rules 不直接写 Element Plus、Varlet 的内部选择器。

## 修改流程

1. 先读后改，确认现有布局组件和 Sass 是否已经提供同名能力。
2. 先解决布局骨架，再处理颜色、间距、文本和组件细节。
3. 优先复用 `presetWind` 和现有 shortcut；确有重复且稳定时才新增规则。
4. 修改 Uno 配置后检查动态类是否进入 `safelist`。
5. 修改第三方样式时放入对应 adapter，不改公共 core。
6. 检查 `hidden`、`o-hidden`、`overflow-hidden` 的语义是否混用。
7. 做静态语法检查、规则生成检查和 `git diff --check`；遵守项目指令，不主动运行禁止的测试、lint 或 dev server。
8. 最终报告说明：修改文件、适配器开关、单位策略、Sass 是否仍被依赖和剩余风险。

## 参考资料

- [unocss-and-layout.md](references/unocss-and-layout.md)：`presetWind`、Row/Column、safelist 和 shortcut 细则。
- [adapters-and-units.md](references/adapters-and-units.md)：第三方适配器与 PC/H5 单位策略。
- [migration.md](references/migration.md)：Sass、旧类和布局组件迁移规则。
