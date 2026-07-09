---
name: core-new-apis
description: Vue 3 响应式系统、生命周期钩子与 composable 模式
---

# 响应式、生命周期与 Composable

## 响应式

### ref 与 shallowRef

```js
import { ref, shallowRef } from 'vue'

// ref —— 深层响应式（追踪嵌套变化）
const user = ref({ name: 'John', profile: { age: 30 } })
user.value.profile.age = 31  // 触发响应式

// shallowRef —— 只有 .value 赋值才触发响应式（性能更好）
const data = shallowRef({ items: [] })
data.value.items.push('new')  // 不触发响应式
data.value = { items: ['new'] }  // 触发响应式
```

对于大型数据结构或不需要深层响应式时，**优先用 `shallowRef`**。

### computed

```js
import { ref, computed } from 'vue'

const count = ref(0)

// 只读 computed
const doubled = computed(() => count.value * 2)

// 可写 computed
const plusOne = computed({
  get: () => count.value + 1,
  set: (val) => { count.value = val - 1 }
})
```

### reactive 与 readonly

```js
import { reactive, readonly } from 'vue'

const state = reactive({ count: 0, nested: { value: 1 } })
state.count++  // 响应式

const readonlyState = readonly(state)
readonlyState.count++  // 警告，修改被阻止
```

注意：`reactive()` 解构后会丢失响应式。使用 `ref()` 或 `toRefs()`。

## 侦听器

### watch

```js
import { ref, watch } from 'vue'

const count = ref(0)

// 侦听单个 ref
watch(count, (newVal, oldVal) => {
  console.log(`Changed from ${oldVal} to ${newVal}`)
})

// 侦听 getter
watch(
  () => props.id,
  (id) => fetchData(id),
  { immediate: true }
)

// 侦听多个源
watch([firstName, lastName], ([first, last]) => {
  fullName.value = `${first} ${last}`
})

// 限制深度的深度侦听（Vue 3.5+）
watch(state, callback, { deep: 2 })

// 只侦听一次（Vue 3.4+）
watch(source, callback, { once: true })
```

### watchEffect

立即执行并自动追踪依赖。

```js
import { ref, watchEffect, onWatcherCleanup } from 'vue'

const id = ref(1)

watchEffect(async () => {
  const controller = new AbortController()

  // 重新运行或卸载时清理（Vue 3.5+）
  onWatcherCleanup(() => controller.abort())

  const res = await fetch(`/api/${id.value}`, { signal: controller.signal })
  data.value = await res.json()
})

// 暂停/恢复（Vue 3.5+）
const { pause, resume, stop } = watchEffect(() => {})
pause()
resume()
stop()
```

### 刷新时机

```js
// 'pre'（默认）—— 组件更新前
// 'post' —— 组件更新后（可访问更新后的 DOM）
// 'sync' —— 立即执行，谨慎使用

watch(source, callback, { flush: 'post' })
watchPostEffect(() => {})  // flush: 'post' 的别名
```

## 生命周期钩子

```js
import {
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted,
  onErrorCaptured,
  onActivated,      // KeepAlive
  onDeactivated,    // KeepAlive
  onServerPrefetch  // 仅 SSR
} from 'vue'

onMounted(() => {
  console.log('DOM is ready')
})

onUnmounted(() => {
  // 清理定时器、监听器等
})

// 错误边界
onErrorCaptured((err, instance, info) => {
  console.error(err)
  return false  // 阻止传播
})
```

## Effect Scope

将响应式副作用分组以便批量销毁。

```js
import { effectScope, onScopeDispose } from 'vue'

const scope = effectScope()

scope.run(() => {
  const count = ref(0)
  const doubled = computed(() => count.value * 2)

  watch(count, () => console.log(count.value))

  // scope 停止时清理
  onScopeDispose(() => {
    console.log('Scope disposed')
  })
})

// 销毁所有副作用
scope.stop()
```

## Composable

Composable 是用 Composition API 封装有状态逻辑的函数。

### 命名约定

- 以 `use` 开头：`useMouse`、`useFetch`、`useCounter`

### 模式

```js
// composables/useMouse.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  const update = (e) => {
    x.value = e.pageX
    y.value = e.pageY
  }

  onMounted(() => window.addEventListener('mousemove', update))
  onUnmounted(() => window.removeEventListener('mousemove', update))

  return { x, y }
}
```

### 接受响应式输入

使用 `toValue()`（Vue 3.3+）规范化 ref、getter 或普通值。

```js
import { ref, watchEffect, toValue } from 'vue'

export function useFetch(url) {
  const data = ref(null)
  const error = ref(null)

  watchEffect(async () => {
    data.value = null
    error.value = null

    try {
      const res = await fetch(toValue(url))
      data.value = await res.json()
    } catch (e) {
      error.value = e
    }
  })

  return { data, error }
}

// 用法 —— 以下都可行：
useFetch('/api/users')
useFetch(urlRef)
useFetch(() => `/api/users/${props.id}`)
```

### 返回 ref（而非 reactive）

始终返回包含 ref 的普通对象，以保证解构兼容性。

```js
// 正确 —— 解构时保留响应式
return { x, y }

// 错误 —— 解构时丢失响应式
return reactive({ x, y })
```

<!--
Source references:
- https://vuejs.org/api/reactivity-core.html
- https://vuejs.org/api/reactivity-advanced.html
- https://vuejs.org/api/composition-api-lifecycle.html
- https://vuejs.org/guide/reusability/composables.html
-->
