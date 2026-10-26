# UnoCSS 与布局细则

## 规则来源

`presetWind` 提供标准原子规则：

- `flex`、`inline-flex`、`flex-row`、`flex-col`
- `justify-*`、`items-*`
- `w-*`、`h-*`、`p-*`、`m-*`、`gap-*`
- `text-*`、`leading-*`、`rounded-*`、`shadow-*`

不要在 `uno/rules/` 重复实现这些标准能力。项目自定义规则只解决 Lvgou 的历史兼容类、显式 px 后缀、安全区和语义差异。

## 动态类

`Flex.vue`、`Row.vue`、`Column.vue`、`Grid.vue` 会动态拼接类名，必须将所有可选值加入 `uno/safelist.js`：

```text
justify-start/center/end/between/around/evenly
items-start/center/end/stretch
flex-row/col/row-reverse/col-reverse
flex-wrap
justify-items-start/center/end/stretch
```

不要为了动态 class 使用字符串模板生成大量不可控规则；固定候选值使用 safelist。

## Row/Column 契约

`Row` 和 `Column` 的 props 约定：

- `x`：主轴或交叉轴的水平对齐。
- `y`：主轴或交叉轴的垂直对齐。
- `gap`：数字间距，最终写入 CSS `gap`。
- `wrap`：是否输出 `flex-wrap`。
- `fill`：是否输出 `w-full h-full`。
- `width`：固定宽度，并保留 `flex-shrink: 0`。
- `reverse`：是否反向排列。
- `inline`：是否输出 `inline-flex`。

不要在组件默认值中加入 `fill`，避免列表项和弹窗内部被强制拉满。

## Shortcut 判断

应该进入 shortcut：

- 多个页面重复出现。
- 组合有明确语义，例如 `scroll-region`、`surface-card`、`layout-row-between`。
- 组合不会因为页面类型变化而改变含义。

不应该进入 shortcut：

- 只是两个原子类的临时组合。
- 名称和现有原子类相同。
- 只在一个页面使用。
- 依赖第三方组件内部 DOM。
