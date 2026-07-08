---
title: Vue Router 导航守卫 next() 函数已弃用
impact: HIGH
impactDescription: 错误使用已弃用的 next() 函数会导致导航卡死、无限循环或静默失败
type: gotcha
tags: [vue3, vue-router, navigation-guards, migration, async]
---

# Vue Router 导航守卫 next() 函数已弃用

**Impact: HIGH** - Vue Router 4 中导航守卫的第三个参数 `next()` 已被弃用。虽然为向后兼容仍提供支持，但错误使用它是引发 bug 的最常见原因之一：多次调用、忘记调用，或在缺少正确逻辑的情况下条件性调用。

## 任务清单

- [ ] 将守卫重构为基于返回值的写法，替代 next()
- [ ] 移除导航守卫中所有的 next() 调用
- [ ] 对异步检查使用 async/await 模式
- [ ] 返回 false 表示取消，返回路由对象表示重定向，不返回任何值表示继续

## 问题

```javascript
// 错误：使用了已弃用的 next() 函数
router.beforeEach((to, from, next) => {
  if (!isAuthenticated) {
    next('/login')  // 很容易忘记这一行调用
  }
  // BUG：已认证时没有调用 next()，导航会卡死！
})

// 错误：多次调用 next()
router.beforeEach((to, from, next) => {
  if (!isAuthenticated) {
    next('/login')
  }
  next()  // BUG：未认证时会被调用两次！
})

// 错误：在异步代码中使用 next() 而没有正确处理
router.beforeEach(async (to, from, next) => {
  const user = await fetchUser()
  if (!user) {
    next('/login')
  }
  next()  // 即使已重定向，这里仍然会被调用！
})
```

## 解决方案：使用基于返回值的守卫

```javascript
// 正确：基于返回值的写法（现代 Vue Router 4+）
router.beforeEach((to, from) => {
  if (!isAuthenticated) {
    return '/login'  // 重定向
  }
  // 不返回任何值（undefined）表示继续
})

// 正确：返回 false 取消导航
router.beforeEach((to, from) => {
  if (hasUnsavedChanges) {
    return false  // 取消导航
  }
})

// 正确：异步配合基于返回值的写法
router.beforeEach(async (to, from) => {
  const user = await fetchUser()
  if (!user) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
  // 继续导航
})
```

## 返回值说明

```javascript
router.beforeEach((to, from) => {
  // 不返回任何值/undefined - 允许导航
  return

  // 返回 false - 取消导航，停留在当前路由
  return false

  // 返回字符串路径 - 重定向到指定路径
  return '/login'

  // 返回路由对象 - 完全可控的重定向
  return { name: 'Login', query: { redirect: to.fullPath } }

  // 返回 Error - 取消导航并触发 router.onError()
  return new Error('Navigation cancelled')
})
```

## 如果必须使用 next()（遗留代码）

如果维护使用 `next()` 的遗留代码，请严格遵守以下规则：

```javascript
// 正确：每条代码路径只调用一次 next()
router.beforeEach((to, from, next) => {
  if (!isAuthenticated) {
    next('/login')
    return  // 关键：调用 next() 后立即退出
  }

  if (!hasPermission(to)) {
    next('/forbidden')
    return  // 关键：调用 next() 后立即退出
  }

  next()  // 仅在所有检查通过时才会执行到这里
})
```

## 错误处理模式

```javascript
router.beforeEach(async (to, from) => {
  try {
    await validateAccess(to)
    // 继续
  } catch (error) {
    if (error.status === 401) {
      return '/login'
    }
    if (error.status === 403) {
      return '/forbidden'
    }
    // 记录错误并仍然继续（也可以返回 false）
    console.error('Access validation failed:', error)
    return false
  }
})
```

## 要点

1. **优先使用基于返回值的写法** - 更简洁、更不易出错，是现代标准
2. **next() 必须恰好调用一次** - 如果使用旧写法，请确保每条路径只调用一次
3. **重定向后务必 return/退出** - 避免触发多次导航操作
4. **异步守卫自然支持** - 只需返回重定向路由或什么都不返回
5. **测试所有代码路径** - 每个分支都必须以 return 或 next() 结束

## 参考
- [Vue Router Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html)
- [RFC: Remove next() from Navigation Guards](https://github.com/vuejs/rfcs/discussions/302)
