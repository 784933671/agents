---
title: 组件插槽最佳实践
impact: MEDIUM
impactDescription: 糟糕的插槽 API 设计会导致多余的 DOM 包装、薄弱的 TypeScript 安全、脆弱的默认内容以及不必要的组件开销
type: best-practice
tags: [vue3, slots, components, typescript, composables]
---

# 组件插槽最佳实践

**影响：MEDIUM** - 插槽是 Vue 中组件 API 的核心面。要有意识地组织它们，让模板保持可预期、有类型、且高性能。

## 任务清单

- 为具名插槽使用简写语法（用 `#` 代替 `v-slot:`）
- 仅在插槽有内容时才渲染可选的包装元素（通过 `$slots` 判断）
- 在 TypeScript 组件中用 `defineSlots` 为作用域插槽契约标注类型
- 为可选插槽提供后备内容
- 纯逻辑复用优先选择 composable，而非无渲染组件

## 具名插槽的简写语法

**反面示例：**
```vue
<MyComponent>
  <template v-slot:header> ... </template>
</MyComponent>
```

**正面示例：**
```vue
<MyComponent>
  <template #header> ... </template>
</MyComponent>
```

## 条件渲染可选的插槽包装元素

当包装元素会带来间距、边框或布局约束时，使用 `$slots` 判断来决定是否渲染。

**反面示例：**
```vue
<!-- Card.vue -->
<template>
  <article class="card">
    <header class="card-header">
      <slot name="header" />
    </header>

    <section class="card-body">
      <slot />
    </section>

    <footer class="card-footer">
      <slot name="footer" />
    </footer>
  </article>
</template>
```

**正面示例：**
```vue
<!-- Card.vue -->
<template>
  <article class="card">
    <header v-if="$slots.header" class="card-header">
      <slot name="header" />
    </header>

    <section v-if="$slots.default" class="card-body">
      <slot />
    </section>

    <footer v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </footer>
  </article>
</template>
```

## 用 defineSlots 为作用域插槽 props 标注类型

在 `<script setup lang="ts">` 中，使用 `defineSlots` 让插槽的消费方能获得自动补全和静态检查。

**反面示例：**
```vue
<!-- ProductList.vue -->
<script setup lang="ts">
interface Product {
  id: number
  name: string
}

defineProps<{ products: Product[] }>()
</script>

<template>
  <ul>
    <li v-for="(product, index) in products" :key="product.id">
      <slot :product="product" :index="index" />
    </li>
  </ul>
</template>
```

**正面示例：**
```vue
<!-- ProductList.vue -->
<script setup lang="ts">
interface Product {
  id: number
  name: string
}

defineProps<{ products: Product[] }>()

defineSlots<{
  default(props: { product: Product; index: number }): any
  empty(): any
}>()
</script>

<template>
  <ul v-if="products.length">
    <li v-for="(product, index) in products" :key="product.id">
      <slot :product="product" :index="index" />
    </li>
  </ul>
  <slot v-else name="empty" />
</template>
```

## 提供插槽后备内容

当父组件省略可选插槽时，后备内容能让组件保持健壮。

**反面示例：**
```vue
<!-- SubmitButton.vue -->
<template>
  <button type="submit" class="btn-primary">
    <slot />
  </button>
</template>
```

**正面示例：**
```vue
<!-- SubmitButton.vue -->
<template>
  <button type="submit" class="btn-primary">
    <slot>Submit</slot>
  </button>
</template>
```

## 纯逻辑复用优先使用 composable

无渲染组件在以插槽驱动的组合中仍然有用，但对于纯逻辑复用，composable 通常更简洁。

**反面示例：**
```vue
<!-- MouseTracker.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const x = ref(0)
const y = ref(0)

function onMove(event: MouseEvent) {
  x.value = event.pageX
  y.value = event.pageY
}

onMounted(() => window.addEventListener('mousemove', onMove))
onUnmounted(() => window.removeEventListener('mousemove', onMove))
</script>

<template>
  <slot :x="x" :y="y" />
</template>
```

**正面示例：**
```ts
// composables/useMouse.ts
import { ref, onMounted, onUnmounted } from 'vue'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  function onMove(event: MouseEvent) {
    x.value = event.pageX
    y.value = event.pageY
  }

  onMounted(() => window.addEventListener('mousemove', onMove))
  onUnmounted(() => window.removeEventListener('mousemove', onMove))

  return { x, y }
}
```

```vue
<!-- MousePosition.vue -->
<script setup lang="ts">
import { useMouse } from '@/composables/useMouse'

const { x, y } = useMouse()
</script>

<template>
  <p>{{ x }}, {{ y }}</p>
</template>
```
