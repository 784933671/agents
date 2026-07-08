---
title: 路由级 beforeEnter 守卫会忽略参数/查询的变化
impact: MEDIUM
impactDescription: 路由级的 beforeEnter 守卫在仅有 params、query 或 hash 变化时不会触发，导致校验逻辑被意外绕过
type: gotcha
tags: [vue3, vue-router, navigation-guards, params, query]
---

# 路由级 beforeEnter 守卫会忽略参数/查询的变化

**Impact: MEDIUM** - 定义在路由配置中的 `beforeEnter` 守卫只有在从**不同的**路由进入时才会触发。在同一路由内修改 params、query 字符串或 hash **不会**触发 `beforeEnter`，这可能会绕过重要的校验逻辑。

## 任务清单

- [ ] 对参数/查询变化使用组件内 `onBeforeRouteUpdate`
- [ ] 或者使用全局 `beforeEach` 配合 route.params/query 检查
- [ ] 文档说明各个守卫分别覆盖哪些场景
- [ ] 测试同一路由下不同参数之间的导航

## 问题

```javascript
// router.js
const routes = [
  {
    path: '/orders/:id',
    component: OrderDetail,
    beforeEnter: async (to, from) => {
      // 从 /products 进入时会执行
      // 但从 /orders/1 导航到 /orders/2 时不会执行!
      const order = await checkOrderAccess(to.params.id)
      if (!order.canView) {
        return '/unauthorized'
      }
    }
  }
]
```

**场景：**
1. 用户从 `/products` 导航到 `/orders/1` —— beforeEnter 执行，访问权限被校验
2. 用户从 `/orders/1` 导航到 `/orders/2` —— beforeEnter **不执行**!
3. 用户可能访问到没有权限的订单!

## beforeEnter 触发与不触发的情况对比

| 导航 | beforeEnter 是否触发? |
|------------|-------------------|
| `/products` → `/orders/1` | 是 |
| `/orders/1` → `/orders/2` | 否 |
| `/orders/1` → `/orders/1?tab=details` | 否 |
| `/orders/1#section` → `/orders/1#other` | 否 |
| `/orders/1` → `/products` → `/orders/2` | 是（离开后重新进入） |

## 解决方案 1：添加组件内守卫

```vue
<!-- OrderDetail.vue -->
<script setup>
import { onBeforeRouteUpdate } from 'vue-router'

// 处理同一路由内的参数变化
onBeforeRouteUpdate(async (to, from) => {
  if (to.params.id !== from.params.id) {
    const order = await checkOrderAccess(to.params.id)
    if (!order.canView) {
      return '/unauthorized'
    }
  }
})
</script>
```

## 解决方案 2：改用全局 beforeEach

```javascript
// router.js
router.beforeEach(async (to, from) => {
  // 全局处理所有订单访问校验
  if (to.name === 'OrderDetail') {
    // 每次导航到该路由时都会执行,包括参数变化的情况
    const order = await checkOrderAccess(to.params.id)
    if (!order.canView) {
      return '/unauthorized'
    }
  }
})
```

## 解决方案 3：组合两种守卫

```javascript
// router.js - 处理从不同路由进入的情况
const routes = [
  {
    path: '/orders/:id',
    component: OrderDetail,
    beforeEnter: (to) => validateOrderAccess(to.params.id)
  }
]

// 组件内 - 处理同一路由内的参数变化
// OrderDetail.vue
onBeforeRouteUpdate((to) => validateOrderAccess(to.params.id))

// 共享的校验函数
async function validateOrderAccess(orderId) {
  const order = await checkOrderAccess(orderId)
  if (!order.canView) {
    return '/unauthorized'
  }
}
```

## 解决方案 4：使用 beforeEnter 配合守卫数组

```javascript
// guards/orderGuards.js
export const orderAccessGuard = async (to) => {
  const order = await checkOrderAccess(to.params.id)
  if (!order.canView) {
    return '/unauthorized'
  }
}

// router.js
const routes = [
  {
    path: '/orders/:id',
    component: OrderDetail,
    beforeEnter: [orderAccessGuard]  // 可以添加多个守卫
  }
]

// 参数变化时仍然需要组件内守卫!
```

## 完整的导航守卫执行顺序

理解每种守卫类型的触发时机：

```
1. beforeRouteLeave（组件内,即将离开的组件）
2. beforeEach（全局）
3. beforeEnter（路由级,仅在从不同路由进入时触发）
4. beforeRouteEnter（组件内,即将进入的组件）
5. beforeResolve（全局）
6. afterEach（全局,在导航确认之后）

对于同一路由上的 params/query 变化:
1. beforeRouteUpdate（组件内）- 只有这个会触发!
2. beforeEach（全局）
3. beforeResolve（全局）
4. afterEach（全局）
```

## 关键要点

1. **beforeEnter 仅用于路由进入** - 不适用于路由内部的变化
2. **使用 onBeforeRouteUpdate 处理参数变化** - 这就是组件内的解决方案
3. **全局 beforeEach 始终会运行** - 适合用于集中化的校验
4. **测试参数变化场景** - 开发过程中很容易遗漏
5. **考虑安全影响** - 基于参数的访问控制需要两种守卫配合

## 参考
- [Vue Router Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html)
- [Vue Router Per-Route Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html#per-route-guard)
