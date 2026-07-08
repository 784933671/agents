---
title: Suspense 组件最佳实践
impact: MEDIUM
impactDescription: Suspense 协调异步依赖与回退界面；配置不当会导致缺失加载状态或令人困惑的用户体验
type: best-practice
tags: [vue3, suspense, async-components, async-setup, loading, fallback, router, transition, keepalive]
---

# Suspense 组件最佳实践

**影响：MEDIUM** - `<Suspense>` 协调异步依赖（异步组件或 async setup），并在它们解析时渲染回退内容。配置不当会导致缺失加载状态、空白渲染或细微的用户体验问题。

## 任务清单

- 将默认插槽和回退插槽的内容包裹在单个根节点中
- 当需要回退内容在回退时出现时使用 `timeout`
- 当需要 Suspense 重新触发时使用 `:key` 强制根节点替换
- 为嵌套的 Suspense 边界添加 `suspensible`（Vue 3.3+）
- 使用 `@pending`、`@resolve` 和 `@fallback` 实现编程式加载状态
- 按 `RouterView` -> `Transition` -> `KeepAlive` -> `Suspense` 的顺序嵌套
- 在生产环境中保持 Suspense 用法集中且有文档记录

## 默认插槽与回退插槽中的单个根节点

Suspense 在两个插槽中都只跟踪单个直接子节点。将多个元素包裹在单个元素或组件中。

**反面示例：**
```vue
<template>
  <Suspense>
    <AsyncHeader />
    <AsyncList />

    <template #fallback>
      <LoadingSpinner />
      <LoadingHint />
    </template>
  </Suspense>
</template>
```

**正面示例：**
```vue
<template>
  <Suspense>
    <div>
      <AsyncHeader />
      <AsyncList />
    </div>

    <template #fallback>
      <div>
        <LoadingSpinner />
        <LoadingHint />
      </div>
    </template>
  </Suspense>
</template>
```

## 回退时机的回退内容（`timeout`）

当 Suspense 已经解析完成并开始新的异步工作时，之前的内容会保持可见直到超时结束。使用 `timeout="0"` 实现立即回退，或使用短延迟以避免闪烁。

**反面示例：**
```vue
<template>
  <Suspense>
    <component :is="currentView" :key="viewKey" />

    <template #fallback>
      Loading...
    </template>
  </Suspense>
</template>
```

**正面示例：**
```vue
<template>
  <Suspense :timeout="200">
    <component :is="currentView" :key="viewKey" />

    <template #fallback>
      Loading...
    </template>
  </Suspense>
</template>
```

## 等待状态仅在根节点替换时重新触发

一旦解析完成，Suspense 只有在默认插槽的根节点变化时才会重新进入等待状态。如果异步工作发生在树更深层，不会出现回退内容。

**反面示例：**
```vue
<template>
  <Suspense>
    <TabContainer>
      <AsyncDashboard v-if="tab === 'dashboard'" />
      <AsyncSettings v-else />
    </TabContainer>

    <template #fallback>
      Loading...
    </template>
  </Suspense>
</template>
```

**正面示例：**
```vue
<template>
  <Suspense>
    <component :is="tabs[tab]" :key="tab" />

    <template #fallback>
      Loading...
    </template>
  </Suspense>
</template>
```

## 为嵌套 Suspense 使用 `suspensible`（Vue 3.3+）

嵌套的 Suspense 边界需要在内部边界上使用 `suspensible`，以便父级能协调加载状态。没有它，内部异步内容在解析前可能渲染为空节点。

**反面示例：**
```vue
<template>
  <Suspense>
    <LayoutShell>
      <Suspense>
        <AsyncWidget />
        <template #fallback>Loading widget...</template>
      </Suspense>
    </LayoutShell>

    <template #fallback>Loading layout...</template>
  </Suspense>
</template>
```

**正面示例：**
```vue
<template>
  <Suspense>
    <LayoutShell>
      <Suspense suspensible>
        <AsyncWidget />
        <template #fallback>Loading widget...</template>
      </Suspense>
    </LayoutShell>

    <template #fallback>Loading layout...</template>
  </Suspense>
</template>
```

## 使用 Suspense 事件跟踪加载状态

使用 `@pending`、`@resolve` 和 `@fallback` 进行数据分析、全局加载指示器，或协调 Suspense 边界外部的界面。

```vue
<script setup>
import { ref } from 'vue'

const isLoading = ref(false)

const onPending = () => {
  isLoading.value = true
}

const onResolve = () => {
  isLoading.value = false
}
</script>

<template>
  <LoadingBar v-if="isLoading" />

  <Suspense @pending="onPending" @resolve="onResolve">
    <AsyncPage />
    <template #fallback>
      <PageSkeleton />
    </template>
  </Suspense>
</template>
```

## 与 RouterView、Transition、KeepAlive 的推荐嵌套方式

组合这些组件时，嵌套顺序应为 `RouterView` -> `Transition` -> `KeepAlive` -> `Suspense`，以确保每个包裹器正常工作。

**反面示例：**
```vue
<template>
  <RouterView v-slot="{ Component }">
    <Suspense>
      <KeepAlive>
        <Transition mode="out-in">
          <component :is="Component" />
        </Transition>
      </KeepAlive>
    </Suspense>
  </RouterView>
</template>
```

**正面示例：**
```vue
<template>
  <RouterView v-slot="{ Component }">
    <Transition mode="out-in">
      <KeepAlive>
        <Suspense>
          <component :is="Component" />
          <template #fallback>Loading...</template>
        </Suspense>
      </KeepAlive>
    </Transition>
  </RouterView>
</template>
```

## 在生产环境中谨慎使用 Suspense

在生产代码中，保持 Suspense 边界最少，记录其使用位置，并准备好回退加载策略，以备将来需要替换或重构时使用。
