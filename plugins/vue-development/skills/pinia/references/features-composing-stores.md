---
name: composing-stores
description: store 之间的通信与避免循环依赖
---

# 组合 Store

Store 之间可以互相使用，共享 state 与逻辑。

## 原则：避免循环依赖

两个 store 不能在 setup 阶段直接读取彼此的 state：

```js
// ❌ 无限循环
const useX = defineStore('x', () => {
  const y = useY()
  y.name // 不要在这里读取！
  return { name: ref('X') }
})

const useY = defineStore('y', () => {
  const x = useX()
  x.name // 不要在这里读取！
  return { name: ref('Y') }
})
```

**解决方案：** 在 getter、computed 或 action 中读取：

```js
const useX = defineStore('x', () => {
  const y = useY()

  // ✅ 在 computed/action 中读取
  function doSomething() {
    const yName = y.name
  }

  return { name: ref('X'), doSomething }
})
```

## Setup Store：在顶层使用其它 Store

```js
import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const useCartStore = defineStore('cart', () => {
  const user = useUserStore()
  const list = ref([])

  const summary = computed(() => {
    return `Hi ${user.name}, you have ${list.value.length} items`
  })

  function purchase() {
    return apiPurchase(user.id, list.value)
  }

  return { list, summary, purchase }
})
```

## 共享 Getter

在 getter 内部调用 `useStore()`：

```js
import { useUserStore } from './user'

export const useCartStore = defineStore('cart', {
  getters: {
    summary(state) {
      const user = useUserStore()
      return `Hi ${user.name}, you have ${state.list.length} items`
    },
  },
})
```

## 共享 Action

在 action 内部调用 `useStore()`：

```js
import { useUserStore } from './user'
import { apiOrderCart } from './api'

export const useCartStore = defineStore('cart', {
  actions: {
    async orderCart() {
      const user = useUserStore()

      try {
        await apiOrderCart(user.token, this.items)
        this.emptyCart()
      } catch (err) {
        displayError(err)
      }
    },
  },
})
```

## SSR：在 await 之前调用 Store

在异步 action 中，所有 store 调用都要在任何 `await` 之前：

```js
actions: {
  async orderCart() {
    // ✅ 所有 useStore() 调用在 await 之前
    const user = useUserStore()
    const analytics = useAnalyticsStore()

    try {
      await apiOrderCart(user.token, this.items)
      // ❌ 不要在 await 之后调用 useStore()（SSR 问题）
      // const otherStore = useOtherStore()
    } catch (err) {
      displayError(err)
    }
  },
}
```

这能确保 SSR 时使用正确的 Pinia 实例。

<!--
Source references:
- https://pinia.vuejs.org/cookbook/composing-stores.html
-->
