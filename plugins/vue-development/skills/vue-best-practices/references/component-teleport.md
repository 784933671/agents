---
title: Teleport 组件最佳实践
impact: MEDIUM
impactDescription: Teleport 将内容渲染到组件 DOM 位置之外，这对覆盖层至关重要，但会影响样式和布局
type: best-practice
tags: [vue3, teleport, modal, overlay, positioning, responsive]
---

# Teleport 组件最佳实践

**影响：MEDIUM** - `<Teleport>` 将组件模板的一部分渲染到 DOM 中的其他位置，同时保留 Vue 组件层级结构。用于覆盖层（模态框、提示框、工具提示）或任何需要脱离层叠上下文、溢出或固定定位限制的界面。

## 任务清单

- 将覆盖层 teleport 到 `body` 或应用根节点之外的专用容器
- 为同类界面保留共享目标（`#modals`、`#notifications`），并通过顺序或 z-index 控制分层
- 使用 `:disabled` 实现应在小屏幕上内联渲染的响应式布局
- 记住 props、emits 和 provide/inject 在 teleport 中仍然有效
- 避免依赖父级层叠上下文或 transform 来处理 teleported 的界面

## 将覆盖层 teleport 出 transform 容器

当祖先元素具有 `transform`、`filter` 或 `perspective` 时，固定定位的覆盖层可能表现为局部定位。Teleport 可以脱离该上下文。

**反面示例：**
```vue
<template>
  <div class="animated-container">
    <button @click="open = true">Open</button>

    <!-- Broken: fixed positioning is scoped to the transformed parent -->
    <div v-if="open" class="modal">Modal</div>
  </div>
</template>

<style>
.animated-container {
  transform: translateZ(0);
}

.modal {
  position: fixed;
  inset: 0;
  z-index: 9999;
}
</style>
```

**正面示例：**
```vue
<template>
  <div class="animated-container">
    <button @click="open = true">Open</button>

    <Teleport to="body">
      <div v-if="open" class="modal">Modal</div>
    </Teleport>
  </div>
</template>
```

## 使用 `disabled` 实现响应式布局

使用 `:disabled` 在移动端内联渲染，在更大屏幕上使用 teleport：

```vue
<script setup>
import { useMediaQuery } from '@vueuse/core'

const isMobile = useMediaQuery('(max-width: 768px)')
</script>

<template>
  <Teleport to="body" :disabled="isMobile">
    <nav class="sidebar">Navigation</nav>
  </Teleport>
</template>
```

## 逻辑层级结构被保留

Teleport 改变 DOM 位置，而不是 Vue 组件树。Props、emits、插槽和 provide/inject 仍然有效：

```vue
<template>
  <Teleport to="body">
    <ChildPanel :message="message" @close="open = false" />
  </Teleport>
</template>
```

## 多个 Teleport 指向同一目标

指向同一目标的 Teleport 按声明顺序追加：

```vue
<template>
  <Teleport to="#notifications">
    <div>First</div>
  </Teleport>

  <Teleport to="#notifications">
    <div>Second</div>
  </Teleport>
</template>
```

使用共享容器以保持堆叠可预测，仅在需要显式分层时应用 z-index。
