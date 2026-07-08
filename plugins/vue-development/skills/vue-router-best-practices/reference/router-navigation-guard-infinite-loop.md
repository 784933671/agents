---
title: 导航守卫的无限重定向循环
impact: HIGH
impactDescription: 配置错误的导航守卫可能将用户困在无限重定向循环中,导致浏览器崩溃或应用无法使用
type: gotcha
tags: [vue3, vue-router, navigation-guards, redirect, debugging]
---

# 导航守卫的无限重定向循环

**Impact: HIGH** - 导航守卫中一个常见的错误是创建导致无限重定向的条件。Vue Router 会检测到这种情况并给出警告,但在生产环境中,它可能导致浏览器崩溃或造成破坏性的用户体验。

## 任务清单

- [ ] 在重定向之前始终检查是否已在目标路由上
- [ ] 用所有可能的导航场景测试守卫逻辑
- [ ] 使用路由 meta 控制哪些路由需要保护
- [ ] 使用 Vue Router devtools 调试重定向链

## 问题

```javascript
// 错误:无限循环 - 即使已经在 login 页也始终重定向到 login!
router.beforeEach((to, from) => {
  if (!isAuthenticated()) {
    return '/login'  // 重定向到 /login,这会再次触发守卫...
  }
})

// 错误:两个路由之间的循环重定向
router.beforeEach((to, from) => {
  if (to.path === '/dashboard' && !hasProfile()) {
    return '/profile'
  }
  if (to.path === '/profile' && !isVerified()) {
    return '/dashboard'  // 回到 dashboard,然后又跳到 profile...
  }
})
```

**你会看到的错误：**
```
[Vue Router warn]: Detected an infinite redirection in a navigation guard when going from "/" to "/login". Aborting to avoid a Stack Overflow.
```

## 解决方案 1：排除目标路由

```javascript
// 正确:如果已经在前往 login 的路上就不重定向
router.beforeEach((to, from) => {
  if (!isAuthenticated() && to.path !== '/login') {
    return '/login'
  }
})

// 正确:使用路由名称让检查更清晰
router.beforeEach((to, from) => {
  const publicPages = ['Login', 'Register', 'ForgotPassword']

  if (!isAuthenticated() && !publicPages.includes(to.name)) {
    return { name: 'Login' }
  }
})
```

## 解决方案 2：使用路由 Meta 字段

```javascript
// router.js
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/public',
    name: 'PublicPage',
    component: PublicPage,
    meta: { requiresAuth: false }
  }
]

// 守卫检查 meta 字段
router.beforeEach((to, from) => {
  // 仅在路由需要鉴权时才重定向
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
})
```

## 解决方案 3：谨慎处理重定向链

```javascript
// 正确:打破潜在的循环重定向
router.beforeEach((to, from) => {
  // 通过跟踪重定向深度来防止重定向循环
  const redirectCount = to.query._redirectCount || 0

  if (redirectCount > 3) {
    console.error('Too many redirects, stopping at:', to.path)
    return '/error'  // 逃生出口
  }

  if (needsRedirect(to)) {
    return {
      path: getRedirectTarget(to),
      query: { ...to.query, _redirectCount: redirectCount + 1 }
    }
  }
})
```

## 解决方案 4：集中式重定向逻辑

```javascript
// guards/auth.js
export function createAuthGuard(router) {
  const publicRoutes = new Set(['Login', 'Register', 'ForgotPassword', 'ResetPassword'])
  const guestOnlyRoutes = new Set(['Login', 'Register'])

  router.beforeEach((to, from) => {
    const isPublic = publicRoutes.has(to.name)
    const isGuestOnly = guestOnlyRoutes.has(to.name)
    const isLoggedIn = isAuthenticated()

    // 未登录,尝试访问受保护路由
    if (!isLoggedIn && !isPublic) {
      return { name: 'Login', query: { redirect: to.fullPath } }
    }

    // 已登录,尝试访问仅限游客的路由（如 login 页）
    if (isLoggedIn && isGuestOnly) {
      return { name: 'Dashboard' }
    }

    // 其他所有情况:放行
  })
}
```

## 调试重定向循环

```javascript
// 添加日志以理解重定向链
router.beforeEach((to, from) => {
  console.log(`Navigation: ${from.path} -> ${to.path}`)
  console.log('Auth state:', isAuthenticated())
  console.log('Route meta:', to.meta)

  // 你的守卫逻辑放在这里
})

// 或者使用 afterEach 追踪已确认的导航
router.afterEach((to, from) => {
  console.log(`Navigated: ${from.path} -> ${to.path}`)
})
```

## 常见重定向循环模式

| 模式 | 问题 | 修复方法 |
|---------|---------|-----|
| 鉴权检查未排除目标 | login 重定向到 login | 将 `/login` 排除在检查之外 |
| 基于角色的循环依赖 | Admin -> User -> Admin | 使用单一数据源定义角色要求 |
| 引导流程 | Step 1 -> Step 2 -> Step 1 | 正确跟踪完成状态 |
| 重定向 query 处理 | 读取重定向会创建新的重定向 | 仅处理一次重定向 |

## 关键要点

1. **始终排除目标路由** - 永远不要重定向到一个会触发相同重定向的路由
2. **使用路由 meta 字段** - 比路径字符串比较更清晰
3. **测试边界情况** - 直接 URL 访问、刷新、后退按钮
4. **开发期间添加日志** - 有助于追踪重定向链
5. **设置逃生出口** - 错误页或最大重定向次数

## 参考
- [Vue Router Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html)
- [Vue Router Route Meta Fields](https://router.vuejs.org/guide/advanced/meta.html)
