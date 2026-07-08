---
title: KeepAlive 组件最佳实践
impact: HIGH
impactDescription: KeepAlive 会缓存组件实例；误用会导致数据过期、内存增长或意外的生命周期行为
type: best-practice
tags: [vue3, keepalive, cache, performance, router, dynamic-components]
---

# KeepAlive 组件最佳实践

**影响：HIGH** - `<KeepAlive>` 缓存组件实例而不是销毁它们。使用它来在切换时保留状态，但要显式管理缓存大小和新鲜度，以避免内存增长或界面过期。

## 任务清单

- 仅在状态保留能改善用户体验的地方使用 KeepAlive
- 设置合理的 `max` 以限制缓存大小
- 声明组件名称以供 include/exclude 匹配
- 使用 `onActivated`/`onDeactivated` 处理缓存感知逻辑
- 决定缓存视图如何以及何时刷新数据
- 避免缓存内存消耗大或安全敏感的视图

## 何时使用 KeepAlive

在切换需要保留状态的视图时使用 KeepAlive（标签页、多步表单、仪表盘）。当每次访问都应重新开始时避免使用。

**反面示例：**
```vue
<template>
  <!-- State resets on every switch -->
  <component :is="currentTab" />
</template>
```

**正面示例：**
```vue
<template>
  <!-- State preserved between switches -->
  <KeepAlive>
    <component :is="currentTab" />
  </KeepAlive>
</template>
```

## 何时不使用 KeepAlive

- 用户期望获取最新结果的搜索或筛选页面
- 内存消耗大的组件（地图、大型表格、媒体播放器）
- 退出时必须清除数据的敏感流程
- 无法暂停的、有大量后台活动的组件

## 限制和控制缓存

始终使用 `max` 限制缓存大小，并尽可能将缓存限制在特定组件。

```vue
<template>
  <KeepAlive :max="5" include="Dashboard,Settings">
    <component :is="currentView" />
  </KeepAlive>
</template>
```

## 确保组件名称与 include/exclude 匹配

`include` 和 `exclude` 匹配组件的 `name` 选项。显式设置名称以实现可靠的缓存。

```vue
<!-- TabA.vue -->
<script setup>
defineOptions({ name: 'TabA' })
</script>
```

```vue
<template>
  <KeepAlive include="TabA,TabB">
    <component :is="currentTab" />
  </KeepAlive>
</template>
```

## 缓存失效策略

Vue 3 没有直接移除特定缓存实例的 API。使用 key 或动态 include/exclude 来强制刷新。

```vue
<script setup>
import { ref, reactive } from 'vue'

const currentView = ref('Dashboard')
const viewKeys = reactive({ Dashboard: 0, Settings: 0 })

function invalidateCache(view) {
  viewKeys[view]++
}
</script>

<template>
  <KeepAlive>
    <component :is="currentView" :key="`${currentView}-${viewKeys[currentView]}`" />
  </KeepAlive>
</template>
```

## 缓存组件的生命周期钩子

缓存的组件在切换时不会被销毁。使用激活钩子进行刷新和清理。

```vue
<script setup>
import { onActivated, onDeactivated } from 'vue'

onActivated(() => {
  refreshData()
})

onDeactivated(() => {
  pauseTimers()
})
</script>
```

## 路由缓存与新鲜度

决定导航时应显示缓存状态还是全新视图。常见模式是在参数变化时按路由设置 key。

```vue
<template>
  <router-view v-slot="{ Component, route }">
    <KeepAlive>
      <component :is="Component" :key="route.fullPath" />
    </KeepAlive>
  </router-view>
</template>
```

如果想要复用缓存但获取最新数据，在 `onActivated` 中刷新，并在请求前比较 query/params。
