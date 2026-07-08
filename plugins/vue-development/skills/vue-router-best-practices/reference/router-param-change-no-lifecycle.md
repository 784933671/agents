---
title: 路由参数变化不会触发生命周期钩子
impact: HIGH
impactDescription: 在使用不同参数的路由间导航时会复用组件实例，跳过 created/mounted 钩子，导致显示陈旧数据
type: gotcha
tags: [vue3, vue-router, lifecycle, params, reactivity]
---

# 路由参数变化不会触发生命周期钩子

**Impact: HIGH** - 当在使用同一个组件的路由之间导航时（例如从 `/users/1` 到 `/users/2`），出于性能考虑，Vue Router 会复用已有的组件实例。这意味着 `onMounted`、`created` 等生命周期钩子并不会触发，从而让你看到上一个路由的陈旧数据。

## 任务清单

- [ ] 对路由参数使用 `watch` 来获取数据
- [ ] 或使用组件内守卫 `onBeforeRouteUpdate`
- [ ] 或使用 `:key="route.params.id"` 强制重新创建组件（效率较低）
- [ ] 永远不要仅依赖 `onMounted` 来加载依赖路由参数的数据

## 问题

```vue
<!-- UserProfile.vue - 用于 /users/:id -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const user = ref(null)

// BUG：仅在组件首次挂载时执行一次！
// 从 /users/1 导航到 /users/2 时不会触发这段代码
onMounted(async () => {
  user.value = await fetchUser(route.params.id)
})
</script>

<template>
  <div>
    <!-- 导航到 /users/2 时仍然显示 User 1 的数据！ -->
    <h1>{{ user?.name }}</h1>
  </div>
</template>
```

**场景：**
1. 访问 `/users/1` - 组件挂载，获取 User 1 的数据
2. 导航到 `/users/2` - 组件被复用，onMounted 不会执行
3. 界面仍然显示 User 1 的数据！

## 解决方案 1：监听路由参数（推荐）

```vue
<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const user = ref(null)
const loading = ref(false)

// 监听参数变化 - 同时处理初始加载和导航
watch(
  () => route.params.id,
  async (newId) => {
    loading.value = true
    user.value = await fetchUser(newId)
    loading.value = false
  },
  { immediate: true }  // 立即执行一次，用于初始加载
)
</script>
```

## 解决方案 2：使用 onBeforeRouteUpdate 守卫

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, onBeforeRouteUpdate } from 'vue-router'

const route = useRoute()
const user = ref(null)

async function loadUser(id) {
  user.value = await fetchUser(id)
}

// 初始加载
onMounted(() => loadUser(route.params.id))

// 处理同一路由内的参数变化
onBeforeRouteUpdate(async (to, from) => {
  if (to.params.id !== from.params.id) {
    await loadUser(to.params.id)
  }
})
</script>
```

## 解决方案 3：用 key 强制重新创建组件

```vue
<!-- App.vue 或父组件 -->
<template>
  <router-view :key="$route.fullPath" />
</template>
```

**权衡：**
- 简单但性能较差
- 每次参数变化都会销毁并重建组件
- 会丢失组件状态
- 仅在组件状态需要完全重置时使用

## 解决方案 4：用于路由响应式数据的 Composable

```javascript
// composables/useRouteData.js
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

export function useRouteData(paramName, fetcher) {
  const route = useRoute()
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)

  watch(
    () => route.params[paramName],
    async (id) => {
      if (!id) return

      loading.value = true
      error.value = null

      try {
        data.value = await fetcher(id)
      } catch (e) {
        error.value = e
      } finally {
        loading.value = false
      }
    },
    { immediate: true }
  )

  return { data, loading, error }
}
```

```vue
<!-- 在组件中使用 -->
<script setup>
import { useRouteData } from '@/composables/useRouteData'
import { fetchUser } from '@/api/users'

const { data: user, loading, error } = useRouteData('id', fetchUser)
</script>
```

## 会触发与不会触发的对照

| 导航类型 | 生命周期钩子 | beforeRouteUpdate | 对参数的 watch |
|----------------|-----------------|-------------------|-----------------|
| `/users/1` 到 `/posts/1` | 是 | 否 | 是 |
| `/users/1` 到 `/users/2` | 否 | 是 | 是 |
| `/users/1?tab=a` 到 `/users/1?tab=b` | 否 | 是 | 否（需用另一个 watch） |
| `/users/1` 到 `/users/1`（相同） | 否 | 否 | 否 |

## 要点

1. **同一路由、不同参数 = 同一个组件实例** - 这是一种性能优化
2. **生命周期钩子只触发一次** - 即组件首次挂载时
3. **使用 `watch` 配合 `immediate: true`** - 同时覆盖初始加载和更新
4. **`onBeforeRouteUpdate` 具备导航感知能力** - 适合必须在视图更新前加载的数据
5. **`:key="route.fullPath"` 是重型手段** - 仅在必要时使用

## 参考
- [Vue Router Dynamic Route Matching](https://router.vuejs.org/guide/essentials/dynamic-matching.html#reacting-to-params-changes)
- [Vue School: Reacting to Param Changes](https://vueschool.io/lessons/reacting-to-param-changes)
