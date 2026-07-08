---
name: vue
description: Vue 3 Composition API、script setup 宏、响应式系统与内置组件。适用于编写 Vue SFC、使用 defineProps/defineEmits/defineModel、watchers，或使用 Transition/Teleport/Suspense/KeepAlive 时。
metadata:
  author: Anthony Fu
  version: "2026.1.31"
  source: Generated from https://github.com/vuejs/docs, scripts located at https://github.com/antfu/skills
---

# Vue

> 基于 Vue 3.5。始终使用 Composition API 配合 `<script setup lang="ts">`。

## 偏好

- 优先用 TypeScript 而非 JavaScript
- 优先用 `<script setup lang="ts">` 而非 `<script>`
- 性能上，若不需要深层响应式，优先用 `shallowRef` 而非 `ref`
- 始终使用 Composition API 而非 Options API
- 不鼓励使用 Reactive Props Destructure

## 核心参考

| 主题 | 描述 | 参考 |
|------|------|------|
| Script Setup 与宏 | `<script setup>`、defineProps、defineEmits、defineModel、defineExpose、defineOptions、defineSlots、泛型 | [script-setup-macros](references/script-setup-macros.md) |
| 响应式与生命周期 | ref、shallowRef、computed、watch、watchEffect、effectScope、生命周期钩子、composables | [core-new-apis](references/core-new-apis.md) |

## 进阶特性

| 主题 | 描述 | 参考 |
|------|------|------|
| 内置组件与指令 | Transition、Teleport、Suspense、KeepAlive、v-memo、自定义指令 | [advanced-patterns](references/advanced-patterns.md) |

## 快速参考

### 组件模板

```vue
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps<{
  title: string
  count?: number
}>()

const emit = defineEmits<{
  update: [value: string]
}>()

const model = defineModel<string>()

const doubled = computed(() => (props.count ?? 0) * 2)

watch(() => props.title, (newVal) => {
  console.log('Title changed:', newVal)
})

onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div>{{ title }} - {{ doubled }}</div>
</template>
```

### 关键导入

```ts
// 响应式
import { ref, shallowRef, computed, reactive, readonly, toRef, toRefs, toValue } from 'vue'

// 侦听器
import { watch, watchEffect, watchPostEffect, onWatcherCleanup } from 'vue'

// 生命周期
import { onMounted, onUpdated, onUnmounted, onBeforeMount, onBeforeUpdate, onBeforeUnmount } from 'vue'

// 工具
import { nextTick, defineComponent, defineAsyncComponent } from 'vue'
```
