# 适配器与单位细则

## 第三方适配器

目录约定：

```text
uno/adapters/
├── index.js
├── elementPlus.js
└── varlet.js
```

`index.js` 根据配置选择 preflight：

```js
createThirdPartyPreflights({
  elementPlus: true,
  varlet: false,
})
```

适配器只能包含：

- 组件库主题变量。
- 组件库稳定的全局变量。
- 经确认的公共组件库覆盖。

适配器不能包含业务页面 class、业务图片尺寸或只在一个弹窗使用的深层选择器。

## PC 单位

PC 不加载 `@unocss/preset-rem-to-px`。本地 Uno theme 通过 px scale 维持数字类语义：

```text
w-320 -> 320px
h-540 -> 540px
p-10 -> 10px
text-46 -> 46px
```

固定尺寸迁移可以使用显式 px 类：

```text
w-320px
max-h-360px
p-10px
gap-12px
lh-20px
```

## H5 单位

H5 项目需要 rem 时，项目自己的 `uno.config.js` 显式加入：

```js
import presetRemToPx from '@unocss/preset-rem-to-px'

const enableRemToPx = true

presets: [
  presetWind(),
  ...(enableRemToPx ? [presetRemToPx({ baseFontSize: 4 })] : []),
]
```

公共 Uno 规则不能自动加载该转换器，也不能通过平台名称隐式改变单位。
