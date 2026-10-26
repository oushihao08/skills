# 迁移细则

## Sass 分类

可以迁移到 Uno：

- 通用 flex、边框、背景、阴影。
- 通用文字颜色、字号、行高。
- 通用滚动、溢出、指针和 box-sizing。
- 通用 safe-area。

先保留在项目内：

- Element Plus/Dialog 深层 DOM 覆盖。
- 业务图片尺寸。
- 业务页面结构类。
- 编辑器、图表、上传组件等局部样式。

## 旧类映射

```text
f-1       -> f-1 或 flex-1
f-center  -> flex-center
f-between -> flex-between
f-wrap    -> flex flex-wrap
o-hidden  -> overflow-hidden
pointer   -> cursor-pointer
border-box -> box-border
scroll-y  -> overflow-y-auto
```

`hidden` 不映射为 `overflow-hidden`。它保留 Uno/Wind 的 `display: none` 语义；需要溢出隐藏使用 `o-hidden`。

## 迁移原则

1. 先搜索类的全部使用位置。
2. 确认目标规则与旧 Sass 的实际计算结果一致。
3. 先添加 Uno 兼容规则，再迁移页面。
4. 页面迁移完成后再删除旧 Sass 规则。
5. 一次只迁移一个职责组，不同时改变单位、主题和布局语义。
