---
name: nuxt-integration
description: 在 Nuxt 中使用 Pinia —— 自动导入、SSR 与最佳实践
---

# Nuxt 集成

Pinia 可与 Nuxt 3/4 无缝协作，自动处理 SSR、序列化与 XSS 防护。

## 安装

```bash
npx nuxi@latest module add pinia
```

这会同时安装 `@pinia/nuxt` 和 `pinia`。如果 `pinia` 未安装，需手动添加。

> **npm 用户：** 如果出现 `ERESOLVE unable to resolve dependency tree`，在 `package.json` 中添加：
> ```json
> "overrides": { "vue": "latest" }
> ```

## 配置

```js
// nuxt.config.js
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
})
```

## 自动导入

以下内容会自动可用：
- `usePinia()` —— 获取 pinia 实例
- `defineStore()` —— 定义 store
- `storeToRefs()` —— 提取响应式 ref
- `acceptHMRUpdate()` —— HMR 支持

**`app/stores/`（Nuxt 4）或 `stores/` 下的所有 store 都会被自动导入。**

### 自定义 store 目录

```js
// nuxt.config.js
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
  pinia: {
    storesDirs: ['./stores/**', './custom-folder/stores/**'],
  },
})
```

## 在页面中获取数据

使用 `callOnce()` 进行 SSR 友好的数据获取：

```vue
<script setup>
const store = useStore()

// 只运行一次，数据在导航间持久化
await callOnce('user', () => store.fetchUser())
</script>
```

### 导航时重新获取

```vue
<script setup>
const store = useStore()

// 每次导航都重新获取（类似 useFetch）
await callOnce('user', () => store.fetchUser(), { mode: 'navigation' })
</script>
```

## 在组件外使用 Store

在导航守卫、中间件或其他 store 中，传入 `pinia` 实例：

```js
// middleware/auth.js
export default defineNuxtRouteMiddleware((to) => {
  const nuxtApp = useNuxtApp()
  const store = useStore(nuxtApp.$pinia)

  if (to.meta.requiresAuth && !store.isLoggedIn) {
    return navigateTo('/login')
  }
})
```

大多数情况下不需要这样做 —— 直接在组件或其他感知注入的上下文中使用 store 即可。

## 配合 Nuxt 的 Pinia 插件

创建一个 Nuxt 插件：

```js
// plugins/myPiniaPlugin.js
function MyPiniaPlugin({ store }) {
  store.$subscribe((mutation) => {
    console.log(`[🍍 ${mutation.storeId}]: ${mutation.type}`)
  })
  return { creationTime: new Date() }
}

export default defineNuxtPlugin(({ $pinia }) => {
  $pinia.use(MyPiniaPlugin)
})
```

<!--
Source references:
- https://pinia.vuejs.org/ssr/nuxt.html
-->
