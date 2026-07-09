---
name: server-side-rendering
description: SSR 配置、state 水合与避免跨请求 state 污染
---

# 服务端渲染（SSR）

当 store 在 `setup` 顶部、getter 或 action 中被调用时，Pinia 可与 SSR 配合工作。

> **使用 Nuxt？** 请参阅 [Nuxt 集成](advanced-nuxt.md)。

## 基本用法

```vue
<script setup>
// ✅ 可行 —— pinia 在 setup 中知道应用上下文
const main = useMainStore()
</script>
```

## 在 setup() 之外使用 Store

显式传入 `pinia` 实例：

```js
const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)

router.beforeEach((to) => {
  // ✅ 传入 pinia 以获得正确的 SSR 上下文
  const main = useMainStore(pinia)

  if (to.meta.requiresAuth && !main.isLoggedIn) {
    return '/login'
  }
})
```

## serverPrefetch()

通过 `this.$pinia` 访问 pinia：

```js
export default {
  serverPrefetch() {
    const store = useStore(this.$pinia)
    return store.fetchData()
  },
}
```

## onServerPrefetch()

正常工作：

```vue
<script setup>
const store = useStore()

onServerPrefetch(async () => {
  await store.fetchData()
})
</script>
```

## State 水合

在服务端序列化 state，在客户端水合。

### 服务端

使用 [devalue](https://github.com/Rich-Harris/devalue) 进行 XSS 安全的序列化：

```js
import devalue from 'devalue'
import { createPinia } from 'pinia'

const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)

// 渲染后，state 可用
const serializedState = devalue(pinia.state.value)
// 作为全局变量注入 HTML
```

### 客户端

在任何 `useStore()` 调用之前水合：

```js
const pinia = createPinia()
const app = createApp(App)
app.use(pinia)

// 从序列化 state 水合（例如从 window.__pinia）
if (typeof window !== 'undefined') {
  pinia.state.value = JSON.parse(window.__pinia)
}
```

## SSR 示例

- [Vitesse 模板](https://github.com/antfu/vitesse/blob/main/src/modules/pinia.js)
- [vite-plugin-ssr](https://vite-plugin-ssr.com/pinia)

## 关键要点

1. 在函数内部调用 store，不要在模块作用域
2. SSR 中在组件外使用 store 时传入 `pinia` 实例
3. 在任何 `useStore()` 调用之前水合 state
4. 使用 `devalue` 或类似工具进行安全序列化
5. 每个请求创建全新的 pinia，避免跨请求 state 污染

<!--
Source references:
- https://pinia.vuejs.org/ssr/
-->
