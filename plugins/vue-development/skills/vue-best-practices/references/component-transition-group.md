---
title: TransitionGroup 组件最佳实践
impact: MEDIUM
impactDescription: TransitionGroup 为列表项添加动画；缺失 key 或误用会导致列表过渡失效
type: best-practice
tags: [vue3, transition-group, animation, lists, keys]
---

# TransitionGroup 组件最佳实践

**影响：MEDIUM** - `<TransitionGroup>` 为进入、离开和移动的列表项添加动画。用于 `v-for` 列表或随时间变化的动态集合。

## 任务清单

- 仅对列表和重复项使用 `<TransitionGroup>`
- 为每个直接子元素提供唯一且稳定的 key
- 当需要语义化或布局包裹器时使用 `tag`
- 避免 `mode` prop（不支持）
- 使用 JavaScript 钩子实现交错效果

## 为列表使用 TransitionGroup

`<TransitionGroup>` 专为列表项设计。需要时使用 `tag` 控制包裹元素。

**反面示例：**
```vue
<template>
  <TransitionGroup name="fade">
    <ComponentA />
    <ComponentB />
  </TransitionGroup>
</template>
```

**正面示例：**
```vue
<template>
  <TransitionGroup name="list" tag="ul">
    <li v-for="item in items" :key="item.id">
      {{ item.name }}
    </li>
  </TransitionGroup>
</template>
```

## 始终提供稳定的 key

key 是必需的。没有稳定的 key，Vue 无法跟踪项的位置，动画会失效。

**反面示例：**
```vue
<template>
  <TransitionGroup name="list" tag="ul">
    <li v-for="(item, index) in items" :key="index">
      {{ item.name }}
    </li>
  </TransitionGroup>
</template>
```

**正面示例：**
```vue
<template>
  <TransitionGroup name="list" tag="ul">
    <li v-for="item in items" :key="item.id">
      {{ item.name }}
    </li>
  </TransitionGroup>
</template>
```

## 不要在 TransitionGroup 上使用 `mode`

`mode` 仅适用于 `<Transition>`，因为它交换单个元素。如果需要进入/离开顺序控制，请使用 `<Transition>`。

**反面示例：**
```vue
<template>
  <TransitionGroup name="list" tag="div" mode="out-in">
    <div v-for="item in items" :key="item.id">{{ item.name }}</div>
  </TransitionGroup>
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

## 使用数据属性实现交错列表动画

对于级联列表动画，将索引传递给 JavaScript 钩子并为每个项计算延迟。

```vue
<template>
  <TransitionGroup
    tag="ul"
    :css="false"
    @before-enter="onBeforeEnter"
    @enter="onEnter"
  >
    <li v-for="(item, index) in items" :key="item.id" :data-index="index">
      {{ item.name }}
    </li>
  </TransitionGroup>
</template>

<script setup>
function onBeforeEnter(el) {
  el.style.opacity = 0
  el.style.transform = 'translateY(12px)'
}

function onEnter(el, done) {
  const delay = Number(el.dataset.index) * 80
  setTimeout(() => {
    el.style.transition = 'all 0.25s ease'
    el.style.opacity = 1
    el.style.transform = 'translateY(0)'
    setTimeout(done, 250)
  }, delay)
}
</script>
```
