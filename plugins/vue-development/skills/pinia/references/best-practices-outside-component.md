---
name: using-stores-outside-components
description: 在导航守卫、插件和其他非组件上下文中正确使用 store
---

# 在组件外使用 Store

Store 需要 `pinia` 实例，它在组件中会被自动注入。在组件之外，可能需要手动提供。

## 单页应用

在 pinia 安装**之后**调用 store：

```js
import { useUserStore } from '@/stores/user'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'

// ❌ 失败 —— pinia 尚未创建
const userStore = useUserStore()

const pinia = createPinia()
const app = createApp(App)
app.use(pinia)

// ✅ 可行 —— pinia 已激活
const userStore = useUserStore()
```

## 导航守卫

**错误：** 在模块层级调用

```js
import { createRouter } from 'vue-router'
const router = createRouter({ /* ... */ })

// ❌ 可能因导入顺序而失败
const store = useUserStore()

router.beforeEach((to) => {
  if (store.isLoggedIn) { /* ... */ }
})
```

**正确：** 在守卫内部调用

```js
router.beforeEach((to) => {
  // ✅ 在 pinia 安装之后调用
  const store = useUserStore()

  if (to.meta.requiresAuth && !store.isLoggedIn) {
    return '/login'
  }
})
```

## SSR 应用

始终把 `pinia` 实例传给 `useStore()`：

```js
const pinia = createPinia()
const app = createApp(App)
app.use(router)
app.use(pinia)

router.beforeEach((to) => {
  // ✅ 传入 pinia 实例
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

在 `<script setup>` 中正常工作：

```vue
<script setup>
const store = useStore()

onServerPrefetch(async () => {
  // ✅ 直接可用
  await store.fetchData()
})
</script>
```

## 关键要点

把 `useStore()` 调用推迟到 pinia 安装之后运行的函数中，而不是在模块作用域调用。

<!--
Source references:
- https://pinia.vuejs.org/core-concepts/outside-component-usage.html
-->
