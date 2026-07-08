---
title: 状态管理策略
impact: HIGH
impactDescription: 选择错误的 store 模式会导致 SSR 请求间状态泄漏、脆弱的变更流程以及扩展性差
type: best-practice
tags: [vue3, state-management, pinia, composables, ssr, vueuse]
---

# 状态管理策略

**影响等级：HIGH** - 使用与应用架构匹配的最轻量状态方案。纯 SPA 应用可使用轻量的全局 composable，而 SSR/Nuxt 应用应默认使用 Pinia，以获得请求安全的状态隔离和可预测的工具链支持。

## 任务清单

- 优先保持状态局部化，仅在需要时才提升为共享/全局状态
- 仅在非 SSR 应用中使用单例 composable
- 将全局状态以 readonly 形式暴露，并通过显式 action 进行变更
- 在 SSR/Nuxt、大型应用以及需要高级调试/插件能力的场景中优先使用 Pinia
- 避免直接导出可变的模块级响应式状态

## 选择最轻量的 Store 方案

- **功能 composable：** 用于可复用逻辑和局部/功能级别状态的默认选择。
- **单例 composable 或 VueUse 的 `createGlobalState`：** 适用于需要共享应用状态的小型非 SSR 应用。
- **Pinia：** 适用于 SSR/Nuxt 应用、中大型应用，以及需要 DevTools、插件或 action 追踪的场景。

## 避免导出可变的模块状态

**反面示例：**
```ts
// store/cart.ts
import { reactive } from 'vue'

export const cart = reactive({
  items: [] as Array<{ id: string; qty: number }>
})
```

**正面示例：**
```ts
// composables/useCartStore.ts
import { reactive, readonly } from 'vue'

let _store: ReturnType<typeof createCartStore> | null = null

function createCartStore() {
  const state = reactive({
    items: [] as Array<{ id: string; qty: number }>
  })

  function addItem(id: string, qty = 1) {
    const existing = state.items.find((item) => item.id === id)
    if (existing) {
      existing.qty += qty
      return
    }
    state.items.push({ id, qty })
  }

  return {
    state: readonly(state),
    addItem
  }
}

export function useCartStore() {
  if (!_store) _store = createCartStore()
  return _store
}
```

## 在 SSR 中不要使用运行时单例

模块单例在整个运行时生命周期内存在。在 SSR 中这会导致请求间的状态泄漏。

**反面示例：**
```ts
// 跨请求复用的共享单例
const cartStore = useCartStore()

export function useServerCart() {
  return cartStore
}
```

**正面示例：**

> 需要 `pinia` 依赖。

```ts
// stores/cart.ts
import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [] as Array<{ id: string; qty: number }>
  }),
  actions: {
    addItem(id: string, qty = 1) {
      const existing = this.items.find((item) => item.id === id)
      if (existing) {
        existing.qty += qty
        return
      }
      this.items.push({ id, qty })
    }
  }
})
```

## 使用 `createGlobalState` 管理小型 SPA 全局状态

> 需要 `@vueuse/core` 依赖。

如果应用是非 SSR 且已经使用了 VueUse，`createGlobalState` 可以省去单例样板代码。

```ts
import { createGlobalState } from '@vueuse/core'
import { computed, ref } from 'vue'

export const useAuthState = createGlobalState(() => {
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => token.value !== null)

  function setToken(next: string | null) {
    token.value = next
  }

  return {
    token,
    isAuthenticated,
    setToken
  }
})
```
