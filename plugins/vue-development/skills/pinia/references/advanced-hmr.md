---
name: hot-module-replacement
description: 启用 HMR 以在开发时保留 store 状态
---

# 热模块替换（HMR）

Pinia 支持 HMR，允许在不刷新页面的情况下编辑 store，并保留现有 state。

## 配置

在每个 store 定义之后添加这段代码：

```js
import { defineStore, acceptHMRUpdate } from 'pinia'

export const useAuth = defineStore('auth', {
  // store 选项...
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuth, import.meta.hot))
}
```

## Setup Store 示例

```js
import { defineStore, acceptHMRUpdate } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const increment = () => count.value++
  return { count, increment }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useCounterStore, import.meta.hot))
}
```

## 构建工具支持

- **Vite：** 通过 `import.meta.hot` 官方支持
- **Webpack：** 使用 `import.meta.webpackHot`
- 任何实现了 `import.meta.hot` 规范的构建工具都应该可用

## Nuxt

使用 `@pinia/nuxt` 时，`acceptHMRUpdate` 会被自动导入，但仍需手动添加 HMR 代码片段。

## 收益

- 编辑 store 逻辑时不丢失 state
- 可即时增删 state、action 和 getter
- 加快开发迭代速度

<!--
Source references:
- https://pinia.vuejs.org/cookbook/hot-module-replacement.html
-->
