---
title: 异步组件最佳实践
impact: MEDIUM
impactDescription: 不当的异步组件策略会拖慢 SSR 应用的可交互时间，并造成加载 UI 闪烁
type: best-practice
tags: [vue3, async-components, ssr, hydration, performance, ux]
---

# 异步组件最佳实践

**影响级别：MEDIUM** - 异步组件应当在不损害感知性能的前提下降低 JavaScript 成本。重点关注 SSR 中的 hydration 时机以及稳定的加载态 UX。

## 任务清单

- 对非关键的 SSR 组件树使用懒 hydration 策略
- 只导入你实际用到的 hydration 辅助函数
- 除非有真实 UX 数据表明需要调整，否则让 `loadingComponent` 的 delay 保持在默认的 `200ms` 附近
- 同时配置 `delay` 和 `timeout`，以获得可预期的加载行为

## 在 SSR 中使用懒 hydration 策略

在 Vue 3.5+ 中，异步组件可以将 hydration 延迟到空闲时、可见时、媒体查询匹配时或用户交互时。

**BAD：**
```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

const AsyncComments = defineAsyncComponent({
  loader: () => import('./Comments.vue')
})
</script>
```

**GOOD：**
```vue
<script setup lang="ts">
import {
  defineAsyncComponent,
  hydrateOnVisible,
  hydrateOnIdle
} from 'vue'

const AsyncComments = defineAsyncComponent({
  loader: () => import('./Comments.vue'),
  hydrate: hydrateOnVisible({ rootMargin: '100px' })
})

const AsyncFooter = defineAsyncComponent({
  loader: () => import('./Footer.vue'),
  hydrate: hydrateOnIdle(5000)
})
</script>
```

## 避免加载动画闪烁

对于通常能很快加载完成的组件，不要立即显示加载 UI。

**BAD：**
```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'

const AsyncDashboard = defineAsyncComponent({
  loader: () => import('./Dashboard.vue'),
  loadingComponent: LoadingSpinner,
  delay: 0
})
</script>
```

**GOOD：**
```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'
import ErrorDisplay from './ErrorDisplay.vue'

const AsyncDashboard = defineAsyncComponent({
  loader: () => import('./Dashboard.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,
  timeout: 30000
})
</script>
```

## 延迟时长指南

| 场景 | 推荐延迟 |
|----------|-------------------|
| 小组件、网络快 | `200ms` |
| 已知重型组件 | `100ms` |
| 后台或非关键 UI | `300-500ms` |
