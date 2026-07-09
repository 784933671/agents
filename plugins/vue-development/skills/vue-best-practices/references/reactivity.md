---
title: 响应式核心模式（ref、reactive、shallowRef、computed、watch）
impact: MEDIUM
impactDescription: 清晰的响应式选择能让状态可预测，并减少 Vue 3 应用中不必要的更新
type: efficiency
tags: [vue3, reactivity, ref, reactive, shallowRef, computed, watch, watchEffect, external-state, best-practice]
---

# 响应式核心模式（ref、reactive、shallowRef、computed、watch）

**影响：MEDIUM** - 先选择正确的响应式基础类型，用 `computed` 派生，并把 watcher 仅用于副作用。

本参考涵盖了局部状态、外部数据、派生值和副作用相关的核心响应式决策。

## 任务清单

- 正确声明响应式状态
  - 对原始值始终使用 `shallowRef()` 而非 `ref()`
  - 为对象/数组/map/set 选择正确的响应式声明方式
- 遵循 `reactive` 的最佳实践
  - 避免直接从 `reactive()` 中解构
  - 对 `reactive` 正确使用 watch
- 遵循 `computed` 的最佳实践
  - 优先使用 `computed`，而非通过 watcher 赋值的派生 ref
  - 将过滤/排序的派生结果移出模板
  - 使用 `computed` 处理可复用的 class/style 逻辑
  - 保持 computed getter 纯净（无副作用），把副作用放到 watcher 中
- 遵循 watcher 的最佳实践
  - 使用 `immediate: true` 代替重复的初始调用
  - 清理 watcher 中的异步副作用

## 正确声明响应式状态

### 对原始值（string、number、boolean、null 等）始终使用 `shallowRef()` 而非 `ref()`，以获得更好的性能。

**反面示例：**
```js
import { ref } from 'vue'
const count = ref(0)
```

**正面示例：**
```js
import { shallowRef } from 'vue'
const count = shallowRef(0)
```

### 为对象/数组/map/set 选择正确的响应式声明方式

当你经常**替换整个值**（`state.value = newObj`）且仍希望其内部保持深层响应式时，使用 `ref()`，通常用于：

- 频繁重新赋值的状态（替换拉取到的对象/列表、重置为默认值、切换预设）。
- 更新主要通过 `.value` 重新赋值完成的 composable 返回值。

当你主要**修改属性**且很少整体替换时，使用 `reactive()`，通常用于：

- “单一状态对象”模式（store/表单）：`state.count++`、`state.items.push(...)`、`state.user.name = ...`。
- 希望避免 `.value` 并就地更新嵌套字段的场景。

```js
import { reactive } from 'vue'

const state = reactive({
  count: 0,
  user: { name: 'Alice', age: 30 }
})

state.count++ // ✅ reactive
state.user.age = 31 // ✅ reactive
// ❌ avoid replacing the reactive object reference:
// state = reactive({ count: 1 })
```

当值是**不透明的/不应被代理**的（类实例、外部库对象、非常大的嵌套数据），且你只希望在**替换** `state.value` 时才触发更新（不做深层追踪）时，使用 `shallowRef()`，通常用于：

- 存储 Vue 不代理其内部的外部实例/句柄（SDK 客户端、类实例）。
- 通过替换根引用来更新的庞大数据（不可变风格的更新）。

```js
import { shallowRef } from 'vue'

const user = shallowRef({ name: 'Alice', age: 30 })

user.value.age = 31 // ❌ not reactive
user.value = { name: 'Bob', age: 25 } // ✅ triggers update
```

当你希望**仅顶层属性**为响应式、嵌套对象保持原始状态时，使用 `shallowReactive()`，通常用于：

- 只有顶层键会变化、嵌套载荷应保持不被管理/不被代理的容器对象。
- Vue 追踪外层包装对象但不深入追踪嵌套或外来对象的混合结构。

```js
import { shallowReactive } from 'vue'

const state = shallowReactive({
  count: 0,
  user: { name: 'Alice', age: 30 }
})

state.count++ // ✅ reactive
state.user.age = 31 // ❌ not reactive
```

## `reactive` 的最佳实践

### 避免直接从 `reactive()` 中解构

**反面示例：**

```js
import { reactive } from 'vue'

const state = reactive({ count: 0 })
const { count } = state // ❌ disconnected from reactivity
```

### 对 reactive 正确使用 watch

**反面示例：**

向 `watch()` 传入一个非 getter 的值

```js
import { reactive, watch } from 'vue'

const state = reactive({ count: 0 })

// ❌ watch expects a getter, ref, reactive object, or array of these
watch(state.count, () => { /* ... */ })
```

**正面示例：**

用 `toRefs()` 保留响应式，并为 `watch()` 使用 getter

```js
import { reactive, toRefs, watch } from 'vue'

const state = reactive({ count: 0 })
const { count } = toRefs(state) // ✅ count is a ref

watch(count, () => { /* ... */ }) // ✅
watch(() => state.count, () => { /* ... */ }) // ✅
```

## `computed` 的最佳实践

### 优先使用 `computed`，而非通过 watcher 赋值的派生 ref

**反面示例：**
```js
import { ref, watchEffect } from 'vue'

const items = ref([{ price: 10 }, { price: 20 }])
const total = ref(0)

watchEffect(() => {
  total.value = items.value.reduce((sum, item) => sum + item.price, 0)
})
```

**正面示例：**
```js
import { ref, computed } from 'vue'

const items = ref([{ price: 10 }, { price: 20 }])
const total = computed(() =>
  items.value.reduce((sum, item) => sum + item.price, 0)
)
```

### 将过滤/排序的派生结果移出模板

**反面示例：**
```vue
<template>
  <li v-for="item in items.filter(item => item.active)" :key="item.id">
    {{ item.name }}
  </li>

  <li v-for="item in getSortedItems()" :key="item.id">
    {{ item.name }}
  </li>
</template>

<script setup>
import { ref } from 'vue'

const items = ref([
  { id: 1, name: 'B', active: true },
  { id: 2, name: 'A', active: false }
])

function getSortedItems() {
  return [...items.value].sort((a, b) => a.name.localeCompare(b.name))
}
</script>
```

**正面示例：**
```vue
<script setup>
import { ref, computed } from 'vue'

const items = ref([
  { id: 1, name: 'B', active: true },
  { id: 2, name: 'A', active: false }
])

const visibleItems = computed(() =>
  items.value
    .filter(item => item.active)
    .sort((a, b) => a.name.localeCompare(b.name))
)
</script>

<template>
  <li v-for="item in visibleItems" :key="item.id">
    {{ item.name }}
  </li>
</template>
```

### 使用 `computed` 处理可复用的 class/style 逻辑

**反面示例：**
```vue
<template>
  <button :class="{ btn: true, 'btn-primary': type === 'primary' && !disabled, 'btn-disabled': disabled }">
    {{ label }}
  </button>
</template>
```

**正面示例：**
```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'primary' },
  disabled: Boolean,
  label: String
})

const buttonClasses = computed(() => ({
  btn: true,
  [`btn-${props.type}`]: !props.disabled,
  'btn-disabled': props.disabled
}))
</script>

<template>
  <button :class="buttonClasses">
    {{ label }}
  </button>
</template>
```

### 保持 computed getter 纯净（无副作用），把副作用放到 watcher 中

computed getter 应当只做值的派生。不要做变更、不要调用 API、不要写存储、不要触发事件。
([参考](https://vuejs.org/guide/essentials/computed.html#best-practices))

**反面示例：**

在 computed 中产生副作用

```js
const count = ref(0)

const doubled = computed(() => {
  // ❌ side effect
  if (count.value > 10) console.warn('Too big!')
  return count.value * 2
})
```

**正面示例：**

纯净的 computed + 用 `watch()` 处理副作用

```js
const count = ref(0)
const doubled = computed(() => count.value * 2)

watch(count, (value) => {
  if (value > 10) console.warn('Too big!')
})
```

## watcher 的最佳实践

### 使用 `immediate: true` 代替重复的初始调用

**反面示例：**
```js
import { ref, watch, onMounted } from 'vue'

const userId = ref(1)

function loadUser(id) {
  // ...
}

onMounted(() => loadUser(userId.value))
watch(userId, (id) => loadUser(id))
```

**正面示例：**
```js
import { ref, watch } from 'vue'

const userId = ref(1)

watch(
  userId,
  (id) => loadUser(id),
  { immediate: true }
)
```

### 清理 watcher 中的异步副作用

在响应快速变化（搜索框、筛选器）时，取消上一个请求。

**正面示例：**

```js
const query = ref('')
const results = ref([])

watch(query, async (q, _prev, onCleanup) => {
  const controller = new AbortController()
  onCleanup(() => controller.abort())

  const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`, {
    signal: controller.signal,
  })

  results.value = await res.json()
})
```
