---
name: stores
description: 在 Pinia 中定义 store、state、getters 和 actions
---

# Pinia Store

Store 通过 `defineStore()` 定义，需要一个唯一名称。每个 store 有三个核心概念：**state**、**getters** 和 **actions**。

## 定义 Store

### Option Store

类似 Vue 的 Options API：

```js
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    name: 'Eduardo',
  }),
  getters: {
    doubleCount: (state) => state.count * 2,
  },
  actions: {
    increment() {
      this.count++
    },
  },
})
```

可以把 `state` 理解为 `data`，`getters` 理解为 `computed`，`actions` 理解为 `methods`。

### Setup Store（推荐）

使用 Composition API 语法，更灵活也更强大：

```js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const name = ref('Eduardo')
  const doubleCount = computed(() => count.value * 2)

  function increment() {
    count.value++
  }

  return { count, name, doubleCount, increment }
})
```

在 Setup Store 中：`ref()` → state，`computed()` → getters，`function()` → actions。

**重要：** 必须返回所有 state 属性，Pinia 才能追踪它们。

### 使用 Store

```vue
<script setup>
import { useCounterStore } from '@/stores/counter'

const store = useCounterStore()
// 访问：store.count, store.doubleCount, store.increment()
</script>
```

### 用 storeToRefs 解构

```vue
<script setup>
import { storeToRefs } from 'pinia'
import { useCounterStore } from '@/stores/counter'

const store = useCounterStore()

// ❌ 破坏响应式
const { name, doubleCount } = store

// ✅ 为 state/getters 保留响应式
const { name, doubleCount } = storeToRefs(store)

// ✅ Actions 可以直接解构
const { increment } = store
</script>
```

---

## State

State 定义为一个返回初始状态的函数。

### JavaScript

复杂 state 使用清晰的初始值表达结构：

```js
export const useUserStore = defineStore('user', {
  state: () => ({
    userList: [],
    user: null,
  }),
})
```

### 访问与修改

```js
const store = useStore()
store.count++
```

```vue
<input v-model="store.count" type="number" />
```

### 用 $patch 修改

一次性应用多个变更：

```js
// 对象语法
store.$patch({
  count: store.count + 1,
  name: 'DIO',
})

// 函数语法（用于复杂修改）
store.$patch((state) => {
  state.items.push({ name: 'shoes', quantity: 1 })
  state.hasChanged = true
})
```

### 重置 State

Option Store 内置 `$reset()`。Setup Store 需要自行实现：

```js
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)

  function $reset() {
    count.value = 0
  }

  return { count, $reset }
})
```

### 订阅 State 变化

```js
cartStore.$subscribe((mutation, state) => {
  mutation.type // 'direct' | 'patch object' | 'patch function'
  mutation.storeId // 'cart'
  mutation.payload // patch 对象（仅 'patch object' 时）

  localStorage.setItem('cart', JSON.stringify(state))
})

// 选项
cartStore.$subscribe(callback, { flush: 'sync' }) // 立即执行
cartStore.$subscribe(callback, { detached: true }) // 卸载后保留
```

---

## Getters

Getters 是计算值，等价于 Vue 的 `computed()`。

### 基础 Getter

```js
getters: {
  doubleCount: (state) => state.count * 2,
}
```

### 访问其他 Getter

使用 `this` 并显式声明返回类型：

```js
getters: {
  doubleCount: (state) => state.count * 2,
  doublePlusOne() {
    return this.doubleCount + 1
  },
},
```

### 带参数的 Getter

返回一个函数（注意：会丢失缓存）：

```js
getters: {
  getUserById: (state) => {
    return (userId) => state.users.find((user) => user.id === userId)
  },
},
```

在带参数的 getter 内部缓存：

```js
getters: {
  getActiveUserById(state) {
    const activeUsers = state.users.filter((user) => user.active)
    return (userId) => activeUsers.find((user) => user.id === userId)
  },
},
```

### 在 Getter 中访问其他 Store

```js
import { useOtherStore } from './other-store'

getters: {
  combined(state) {
    const otherStore = useOtherStore()
    return state.localData + otherStore.data
  },
},
```

---

## Actions

Actions 是用于业务逻辑的方法。与 getter 不同，它们可以是异步的。

### 定义 Action

```js
actions: {
  increment() {
    this.count++
  },
  randomizeCounter() {
    this.count = Math.round(100 * Math.random())
  },
},
```

### 异步 Action

```js
actions: {
  async registerUser(login, password) {
    try {
      this.userData = await api.post({ login, password })
    } catch (error) {
      return error
    }
  },
},
```

### 在 Action 中访问其他 Store

```js
import { useAuthStore } from './auth-store'

actions: {
  async fetchUserPreferences() {
    const auth = useAuthStore()
    if (auth.isAuthenticated) {
      this.preferences = await fetchPreferences()
    }
  },
},
```

**SSR：** 在任何 `await` 之前调用所有 `useStore()`：

```js
async orderCart() {
  // ✅ 在 await 之前调用 store
  const user = useUserStore()

  await apiOrderCart(user.token, this.items)
  // ❌ SSR 中不要在 await 之后调用 useStore()
}
```

### 订阅 Action

```js
const unsubscribe = someStore.$onAction(
  ({ name, store, args, after, onError }) => {
    const startTime = Date.now()
    console.log(`Start "${name}" with params [${args.join(', ')}]`)

    after((result) => {
      console.log(`Finished "${name}" after ${Date.now() - startTime}ms`)
    })

    onError((error) => {
      console.warn(`Failed "${name}": ${error}`)
    })
  }
)

unsubscribe() // 清理
```

组件卸载后保留订阅：

```js
someStore.$onAction(callback, true)
```

---

## Options API 辅助函数

```js
import { mapState, mapWritableState, mapActions } from 'pinia'
import { useCounterStore } from '../stores/counter'

export default {
  computed: {
    // 只读的 state/getter
    ...mapState(useCounterStore, ['count', 'doubleCount']),
    // 可写的 state
    ...mapWritableState(useCounterStore, ['count']),
  },
  methods: {
    ...mapActions(useCounterStore, ['increment']),
  },
}
```

---

## 在 Setup Store 中访问全局注入

```js
import { inject } from 'vue'
import { useRoute } from 'vue-router'
import { defineStore } from 'pinia'

export const useSearchFilters = defineStore('search-filters', () => {
  const route = useRoute()
  const appProvided = inject('appProvided')

  // 不要返回这些 —— 在组件中直接访问
  return { /* ... */ }
})
```

<!--
Source references:
- https://pinia.vuejs.org/core-concepts/
- https://pinia.vuejs.org/core-concepts/state.html
- https://pinia.vuejs.org/core-concepts/getters.html
- https://pinia.vuejs.org/core-concepts/actions.html
-->
