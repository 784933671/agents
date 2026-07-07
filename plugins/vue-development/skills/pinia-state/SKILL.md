---
name: pinia-state
description: 掌握 Pinia 状态管理的实用模式：store 组织、setup vs options 风格、持久化、SSR 友好性与跨组件状态共享。适用于设计应用状态架构、拆分 store 或排查状态同步问题。
---

# Pinia 状态管理

Pinia 是 Vue 官方推荐的状态库。本技能聚焦实战组织、跨组件共享与常见陷阱，而非 API 罗列。

## 何时使用本技能

- 设计应用的整体状态架构
- 决定一块状态该放组件本地还是 store
- 拆分过大的"上帝 store"
- 处理持久化、SSR 或跨组件同步

## 何时用 store，何时用本地状态

```
组件本地状态      ← 表单输入、UI 折叠、临时 hover
  ↓ 多组件共享
Pinia store       ← 跨路由/跨组件的业务状态
  ↓ 来自服务端
请求缓存          ← 数据获取库（VueQuery/Pinia colada）或自管
```

判断标准：
- **只有本组件用** → `ref` / `reactive`
- **多个组件要读同一份** → store
- **来自服务端、需缓存失效** → 请求库（store 存客户端状态，请求库存服务端镜像）

## Store 定义：Setup vs Options

### Setup Store（推荐）

更灵活，可自由组合 composables：

```ts
export const useUserStore = defineStore('user', () => {
  // state
  const user = ref<User | null>(null)
  const token = ref<string>('')

  // getters
  const isLoggedIn = computed(() => !!user.value)

  // actions
  async function login(creds: Credentials) {
    const res = await api.login(creds)
    user.value = res.user
    token.value = res.token
  }

  function logout() {
    user.value = null
    token.value = ''
  }

  return { user, token, isLoggedIn, login, logout }
})
```

### Options Store

更接近 Vue 2 风格，适合简单场景：

```ts
export const useUserStore = defineStore('user', {
  state: () => ({ user: null as User | null, token: '' }),
  getters: { isLoggedIn: (s) => !!s.user },
  actions: {
    async login(creds) { /* ... */ },
    logout() { this.user = null; this.token = '' },
  },
})
```

新项目优先 Setup Store。

## Store 组织

### 按领域拆分

```
stores/
├── user.ts          ← 用户/鉴权
├── cart.ts          ← 购物车
├── products.ts      ← 商品列表
├── ui.ts            ← 全局 UI 状态（侧栏/主题）
└── index.ts         ← 注册（如有插件）
```

每个 store 职责单一，避免"上帝 store"。

### Store 间互相调用

```ts
// store A 调用 store B（在 action 内）
import { useCartStore } from './cart'
export const useOrderStore = defineStore('order', () => {
  async function checkout() {
    const cart = useCartStore()  // 在 action 内调用，不在 setup 顶层
    await api.order(cart.items)
    cart.clear()
  }
  return { checkout }
})
```

注意：在 action 内部调用其它 store，**不要**在 store 顶层直接调用（顺序与循环依赖问题）。

## 在组件中使用

```vue
<script setup>
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

const store = useUserStore()

// ✅ 解构响应式：用 storeToRefs
const { user, isLoggedIn } = storeToRefs(store)

// action 可以直接解构（函数不需要响应式）
const { login, logout } = store
</script>
```

陷阱：直接解构 store 会丢失响应式（类似 `reactive` 解构），必须用 `storeToRefs`。

## 持久化

### 选择性持久化

```ts
// 只持久化 token，不持久化敏感的 user 对象
import { useStorage } from '@vueuse/core'

export const useUserStore = defineStore('user', () => {
  const token = useStorage('app:token', '')  // 自动持久化到 localStorage
  const user = ref<User | null>(null)        // 仅内存
  return { token, user }
})
```

### 插件式持久化

`pinia-plugin-persistedstate` 提供声明式持久化：

```ts
defineStore('user', { /* ... */ }, {
  persist: {
    pick: ['token'],  // 只持久化 token
  },
})
```

## SSR 注意事项

- 服务端每次请求需要**新 store 实例**，避免跨请求状态污染
- 用 `pinia` 插件时，state 序列化后注入客户端水合
- 避免在 store 顶层访问 `window`/`localStorage`（SSR 报错）

```ts
// Nuxt 中 pinia 自动处理；自建 SSR 时手动：
const pinia = createPinia()
app.use(pinia)
// 渲染后：dehydrate
const state = pinia.state.value
// 客户端：hydrate
pinia.state.value = window.__PINIA_STATE__
```

## 请求与状态分层

```
服务端数据      ← 用请求库（VueQuery/Pinia colada），自动缓存失效
  +
客户端状态      ← Pinia store（用户偏好、UI 状态、本地编辑）
  +
组件本地状态    ← ref（临时输入、动画状态）
```

不要用 Pinia 手动管理服务端数据缓存（失效逻辑复杂且易错），交给专门的请求库。

## 原则

1. **按领域拆分**：一个 store 一个职责
2. **解构用 storeToRefs**：避免响应式丢失
3. **action 内互调**：不在 store 顶层依赖其它 store
4. **分层**：服务端数据用请求库，客户端状态用 store
5. **SSR 友好**：避免顶层副作用，每请求新实例
