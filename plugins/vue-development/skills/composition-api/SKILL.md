---
name: composition-api
description: 掌握 Vue 3 Composition API 与响应式系统的实用模式：ref/reactive/computed/watch、组合式函数提取、生命周期与副作用管理。适用于设计组件逻辑、排查响应式陷阱或重构 Options API。
---

# Composition API 与响应式

Vue 3 Composition API 的实战指南，覆盖响应式 API、组合式函数提取与常见陷阱。核心：理解响应式的"边界"，才能写出正确的代码。

## 何时使用本技能

- 设计组件逻辑、拆分大型 `setup`
- 排查"数据不更新""computed 不触发""watch 读到旧值"
- 提取可复用的组合式函数（`useXxx`）
- 从 Options API 迁移到 Composition API

## 响应式 API 速查

| API | 用途 | 要点 |
|-----|------|------|
| `ref(v)` | 包装任意值为响应式 | `.value` 访问；模板自动解包 |
| `reactive(obj)` | 让对象响应式 | **不可解构**；不可整体替换 |
| `computed(getter)` | 派生缓存值 | 不放副作用；返回只读 ref |
| `watch(src, cb)` | 显式监听 | 可拿到新旧值；可深度/立即 |
| `watchEffect(cb)` | 自动追踪依赖 | 立即执行；返回清理函数 |
| `shallowRef(v)` | 只对 `.value` 替换响应 | 大对象性能优化 |
| `toRefs(obj)` | 把 reactive 属性转 ref | 用于解构保留响应式 |
| `readonly(proxy)` | 创建只读代理 | 防止意外修改 |

## 核心陷阱

### 1. reactive 解构丢失响应式

```js
const state = reactive({ count: 0 })
let { count } = state  // ❌ count 变成普通值，不再响应式
count++                 // 不触发更新

// ✅ 用 toRefs
const { count } = toRefs(state)
// ✅ 或直接 state.count
```

### 2. reactive 整体替换

```js
const state = reactive({ list: [] })
state = { list: [1, 2] }  // ❌ 重新赋值断开响应式

// ✅ 用 ref 替换
const state = ref({ list: [] })
state.value = { list: [1, 2] }
// ✅ 或改属性
state.list = [1, 2]
```

### 3. props 解构（Vue 3.5 前）

```vue
<script setup>
const props = defineProps<{ msg: string }>()
const { msg } = props  // ❌ 3.5 前丢失响应式

// ✅ 保持 props.msg，或用 toRefs
const { msg } = toRefs(props)
</script>
```

### 4. computed 中的副作用

```js
// ❌ 副作用污染缓存
const total = computed(() => {
  log('calculating')   // 每次依赖变化都执行，缓存读取时也可能重算
  return a.value + b.value
})

// ✅ 副作用放 watch
watch([a, b], () => log('changed'))
const total = computed(() => a.value + b.value)
```

### 5. watch 清理竞态

```js
watch(id, (newId, oldId, onCleanup) => {
  const controller = new AbortController()
  fetchData(newId, { signal: controller.signal }).then(setData)
  onCleanup(() => controller.abort())  // ✅ 快速切换时取消旧请求
})
```

## 组合式函数（Composables）

提取可复用逻辑为 `useXxx` 函数：

```ts
// useFetch.ts
export function useFetch<T>(url: Ref<string> | string) {
  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const loading = ref(false)

  async function load() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(unref(url))
      data.value = await res.json()
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  watch(() => unref(url), load, { immediate: true })
  return { data, error, loading, reload: load }
}
```

约定：
- 命名 `useXxx`
- 接受 `ref` 或裸值（内部 `unref`）
- 返回响应式引用（`ref`/`computed`）
- 在 `setup` 或其他 composable 内调用
- 副作用要在 `onUnmounted` 清理

## 常用模式

### 状态提升到 composable

```ts
// 多组件共享一块逻辑（非全局）
export function useCounter(initial = 0) {
  const count = ref(initial)
  const inc = () => count.value++
  return { count, inc }
}
// 每个组件调用得到独立实例
```

### 跨组件共享（单例）

```ts
// 模块级单例，所有调用方共享同一状态
const globalState = ref(0)
export function useGlobal() {
  return { state: readonly(globalState), inc: () => globalState.value++ }
}
```

### 模板 ref 与组件实例

```vue
<script setup>
const inputRef = ref<HTMLInputElement>()  // 与模板 ref 同名
onMounted(() => inputRef.value?.focus())
</script>
<template><input ref="inputRef" /></template>
```

## 原则

1. **理解响应式边界**：哪些操作断开响应式，哪些保留
2. **props 只读**：不直接改，用 `emit` 通知父组件
3. **composable 独立**：每个 `useXxx` 是独立逻辑单元，不互相耦合
4. **副作用清理**：定时器、监听、订阅在 `onUnmounted` 清理
5. **优先组合式**：新代码用 `<script setup>`，统一风格
