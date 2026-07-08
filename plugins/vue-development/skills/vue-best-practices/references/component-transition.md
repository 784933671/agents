---
title: Transition 组件最佳实践
impact: MEDIUM
impactDescription: Transition 为单个元素或组件添加动画；结构或 key 不正确会阻止动画触发
type: best-practice
tags: [vue3, transition, animation, performance, keys]
---

# Transition 组件最佳实践

**影响：MEDIUM** - `<Transition>` 为单个元素或组件的进入/离开添加动画。它非常适合切换界面状态、交换视图或一次为一个组件添加动画。

## 任务清单

- 在 `<Transition>` 内包裹单个元素或组件
- 在相同元素类型之间切换时提供 `key`
- 当需要顺序交换时使用 `mode="out-in"`
- 优先使用 `transform` 和 `opacity` 以获得平滑动画

## 为单个根元素使用 Transition

`<Transition>` 仅支持一个直接子节点。将多个节点包裹在单个元素或组件中。

**反面示例：**
```vue
<template>
  <Transition name="fade">
    <h3>Title</h3>
    <p>Description</p>
  </Transition>
</template>
```

**正面示例：**
```vue
<template>
  <Transition name="fade">
    <div>
      <h3>Title</h3>
      <p>Description</p>
    </div>
  </Transition>
</template>
```

## 强制相同元素类型之间的过渡

当标签类型不变时，Vue 会复用相同的 DOM 元素。添加 `key` 让 Vue 将其视为新元素并触发进入/离开。

**反面示例：**
```vue
<template>
  <Transition name="fade">
    <p v-if="isActive">Active</p>
    <p v-else>Inactive</p>
  </Transition>
</template>
```

**正面示例：**
```vue
<template>
  <Transition name="fade" mode="out-in">
    <p v-if="isActive" key="active">Active</p>
    <p v-else key="inactive">Inactive</p>
  </Transition>
</template>
```

## 使用 `mode` 避免交换时的重叠

交换组件或视图时，使用 `mode="out-in"` 防止两者同时可见。

**反面示例：**
```vue
<template>
  <Transition name="fade">
    <component :is="currentView" />
  </Transition>
</template>
```

**正面示例：**
```vue
<template>
  <Transition name="fade" mode="out-in">
    <component :is="currentView" :key="currentView" />
  </Transition>
</template>
```

## 为性能使用 `transform` 和 `opacity` 动画

避免使用触发布局的属性，如 `height`、`margin` 或 `top`。使用 `transform` 和 `opacity` 实现平滑、对 GPU 友好的过渡。

**反面示例：**
```css
.slide-enter-active,
.slide-leave-active {
  transition: height 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  height: 0;
}
```

**正面示例：**
```css
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-12px);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(12px);
  opacity: 0;
}
```
