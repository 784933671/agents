---
name: script-setup-macros
description: Vue 3 script setup 语法与用于定义 props、emits、model 等的编译器宏
---

# Script Setup 与宏

`<script setup>` 是 Vue SFC 配合 Composition API 的推荐语法，提供更好的运行时性能和更简洁的组件组织方式。

## 基础语法

```vue
<script setup>
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

声明组件 props，使用运行时类型和默认值。

```js
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  count: {
    type: Number,
    default: 0,
  },
  items: {
    type: Array,
    default: () => [],
  },
})
```

## defineEmits

集中声明可发射事件。

```js
const emit = defineEmits(['update', 'change', 'close'])

emit('update', 'new value')
emit('change', 1, 'name')
emit('close')
```

## defineModel

通过 `v-model` 消费的双向绑定 prop。Vue 3.4+ 可用。

```js
// 基础用法 —— 创建 "modelValue" prop
const model = defineModel()
model.value = 'hello'  // 发射 "update:modelValue"

// 具名 model —— 通过 v-model:name 消费
const count = defineModel('count', { type: Number, default: 0 })

// 带修饰符
const [value, modifiers] = defineModel()
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

```js
import { ref } from 'vue'

const count = ref(0)
const reset = () => { count.value = 0 }

defineExpose({
  count,
  reset
})
```

父组件访问：
```js
const childRef = ref()
childRef.value?.reset()
```

## defineOptions

无需单独的 `<script>` 块即可声明组件选项。Vue 3.3+ 可用。

```js
defineOptions({
  inheritAttrs: false,
  name: 'CustomName'
})
```

## defineSlots

JavaScript 项目通常通过清晰的 slot 命名和文档说明插槽契约。需要声明插槽时，保持名称稳定，并在组件示例中展示 slot props。

## 本地自定义指令

使用 `vNameOfDirective` 命名约定。

```js
const vFocus = {
  mounted: (el) => el.focus()
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
<script setup>
const data = await fetch('/api/data').then(r => r.json())
</script>
```

<!--
Source references:
- https://vuejs.org/api/sfc-script-setup.html
-->
