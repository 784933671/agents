---
name: script-setup-macros
description: Vue 3 script setup 语法与用于定义 props、emits、model 等的编译器宏
---

# Script Setup 与宏

`<script setup>` 是 Vue SFC 配合 Composition API 的推荐语法，提供更好的运行时性能与 IDE 类型推断。

## 基础语法

```vue
<script setup lang="ts">
// 顶层绑定会暴露给模板
import { ref } from 'vue'
import MyComponent from './MyComponent.vue'

const count = ref(0)
const increment = () => count.value++
</script>

<template>
  <button @click="increment">{{ count }}</button>
  <MyComponent />
</template>
```

## defineProps

声明组件 props，支持完整的 TypeScript 类型。

```ts
// 基于类型的声明（推荐）
const props = defineProps<{
  title: string
  count?: number
  items: string[]
}>()

// 带默认值（Vue 3.5+）
const { title, count = 0 } = defineProps<{
  title: string
  count?: number
}>()

// 带默认值（Vue 3.4 及以下）
const props = withDefaults(defineProps<{
  title: string
  items?: string[]
}>(), {
  items: () => []  // 数组/对象使用工厂函数
})
```

## defineEmits

声明带类型载荷的发射事件。

```ts
// 具名元组语法（推荐）
const emit = defineEmits<{
  update: [value: string]
  change: [id: number, name: string]
  close: []
}>()

emit('update', 'new value')
emit('change', 1, 'name')
emit('close')
```

## defineModel

通过 `v-model` 消费的双向绑定 prop。Vue 3.4+ 可用。

```ts
// 基础用法 —— 创建 "modelValue" prop
const model = defineModel<string>()
model.value = 'hello'  // 发射 "update:modelValue"

// 具名 model —— 通过 v-model:name 消费
const count = defineModel<number>('count', { default: 0 })

// 带修饰符
const [value, modifiers] = defineModel<string>()
if (modifiers.trim) {
  // 处理 trim 修饰符
}

// 带转换器
const [value, modifiers] = defineModel({
  get(val) { return val?.toLowerCase() },
  set(val) { return modifiers.trim ? val?.trim() : val }
})
```

父组件用法：
```vue
<Child v-model="name" />
<Child v-model:count="total" />
<Child v-model.trim="text" />
```

## defineExpose

通过模板 ref 显式暴露属性给父组件。组件默认是封闭的。

```ts
import { ref } from 'vue'

const count = ref(0)
const reset = () => { count.value = 0 }

defineExpose({
  count,
  reset
})
```

父组件访问：
```ts
const childRef = ref<{ count: number; reset: () => void }>()
childRef.value?.reset()
```

## defineOptions

无需单独的 `<script>` 块即可声明组件选项。Vue 3.3+ 可用。

```ts
defineOptions({
  inheritAttrs: false,
  name: 'CustomName'
})
```

## defineSlots

为插槽 props 提供类型提示。Vue 3.3+ 可用。

```ts
const slots = defineSlots<{
  default(props: { item: string; index: number }): any
  header(props: { title: string }): any
}>()
```

## 泛型组件

使用 `generic` 属性声明泛型类型参数。

```vue
<script setup lang="ts" generic="T extends string | number">
defineProps<{
  items: T[]
  selected: T
}>()
</script>
```

带约束的多泛型：
```vue
<script setup lang="ts" generic="T, U extends Record<string, T>">
import type { Item } from './types'
defineProps<{
  data: U
  key: keyof U
}>()
</script>
```

## 本地自定义指令

使用 `vNameOfDirective` 命名约定。

```ts
const vFocus = {
  mounted: (el: HTMLElement) => el.focus()
}

// 或导入后重命名
import { myDirective as vMyDirective } from './directives'
```

```vue
<template>
  <input v-focus />
</template>
```

## 顶层 await

在 `<script setup>` 中直接使用 `await`。组件会变为异步，必须配合 `<Suspense>` 使用。

```vue
<script setup lang="ts">
const data = await fetch('/api/data').then(r => r.json())
</script>
```

<!--
Source references:
- https://vuejs.org/api/sfc-script-setup.html
-->
