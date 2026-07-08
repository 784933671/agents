---
title: 异步导航守卫需要正确处理 Promise
impact: MEDIUM
impactDescription: 守卫中未 await 的 promise 会导致导航在异步检查完成前就结束,从而允许越权访问或携带不完整的数据
type: gotcha
tags: [vue3, vue-router, navigation-guards, async, promises]
---

# 异步导航守卫需要正确处理 Promise

**Impact: MEDIUM** - 执行异步操作（API 调用、鉴权检查）的导航守卫必须正确处理 promise。如果你不 await 异步操作或返回 promise,导航会在检查完成之前就结束,可能导致越权访问或带着不完整的数据进行导航。

## 任务清单

- [ ] 在导航守卫中使用 async/await
- [ ] 如果不使用 async/await,则返回 promise
- [ ] 为耗时的异步操作添加加载状态
- [ ] 为缓慢的 API 调用实现超时机制
- [ ] 处理错误以防止导航卡住

## 问题

```javascript
// 错误:没有 await - 导航立即继续
router.beforeEach((to, from) => {
  if (to.meta.requiresAuth) {
    checkAuth()  // 这会返回一个 Promise,但我们没有等待!
    // checkAuth 完成之前导航就已经继续了
  }
})

// 错误:异步函数但忘记 return
router.beforeEach(async (to, from) => {
  if (to.meta.requiresAuth) {
    const isValid = await checkAuth()
    if (!isValid) {
      // 这个重定向可能发生在导航已经完成之后!
      return '/login'
    }
  }
  // 缺少 return - 隐式返回 undefined,放行了导航
})
```

## 解决方案:正确的 async/await 模式

```javascript
// 正确:异步函数配合正确的 return
router.beforeEach(async (to, from) => {
  if (to.meta.requiresAuth) {
    try {
      const isAuthenticated = await checkAuth()

      if (!isAuthenticated) {
        return { name: 'Login', query: { redirect: to.fullPath } }
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      return { name: 'Error', params: { message: 'Authentication failed' } }
    }
  }
  // 显式不返回任何内容以放行导航
  return true
})
```

## 解决方案:基于 Promise 的模式（替代方案）

```javascript
// 正确:显式返回 promise
router.beforeEach((to, from) => {
  if (to.meta.requiresAuth) {
    return checkAuth()
      .then(isAuthenticated => {
        if (!isAuthenticated) {
          return { name: 'Login' }
        }
      })
      .catch(error => {
        console.error('Auth check failed:', error)
        return { name: 'Error' }
      })
  }
})
```

## 异步守卫期间的加载状态

```javascript
// app/composables/useNavigationLoading.js
import { ref } from 'vue'

const isNavigating = ref(false)

export function useNavigationLoading() {
  return { isNavigating }
}

export function setupNavigationLoading(router) {
  router.beforeEach(() => {
    isNavigating.value = true
  })

  router.afterEach(() => {
    isNavigating.value = false
  })

  router.onError(() => {
    isNavigating.value = false
  })
}
```

```vue
<!-- App.vue -->
<script setup>
import { useNavigationLoading } from '@/composables/useNavigationLoading'

const { isNavigating } = useNavigationLoading()
</script>

<template>
  <LoadingBar v-if="isNavigating" />
  <router-view />
</template>
```

## 针对缓慢 API 的超时模式

```javascript
// 正确:添加超时,防止无限等待
function withTimeout(promise, ms = 5000) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), ms)
    )
  ])
}

router.beforeEach(async (to, from) => {
  if (to.meta.requiresAuth) {
    try {
      const isValid = await withTimeout(checkAuth(), 5000)
      if (!isValid) {
        return '/login'
      }
    } catch (error) {
      if (error.message === 'Request timeout') {
        // 放行用户但显示警告
        console.warn('Auth check timed out')
      } else {
        return '/login'
      }
    }
  }
})
```

## 多个异步检查

```javascript
// 正确:并行执行独立的检查
router.beforeEach(async (to, from) => {
  if (to.meta.requiresAuth && to.meta.requiresSubscription) {
    try {
      const [isAuthenticated, hasSubscription] = await Promise.all([
        checkAuth(),
        checkSubscription()
      ])

      if (!isAuthenticated) {
        return '/login'
      }

      if (!hasSubscription) {
        return '/subscribe'
      }
    } catch (error) {
      return '/error'
    }
  }
})
```

## 错误处理的最佳实践

```javascript
router.beforeEach(async (to, from) => {
  try {
    // 你的异步逻辑放在这里
    await performChecks(to)
  } catch (error) {
    // 始终处理错误,防止导航卡住

    if (error.response?.status === 401) {
      return '/login'
    }

    if (error.response?.status === 403) {
      return '/forbidden'
    }

    if (error.code === 'NETWORK_ERROR') {
      // 离线 - 也许可以放行导航但显示警告
      return true
    }

    // 未知错误 - 重定向到错误页
    console.error('Navigation guard error:', error)
    return { name: 'Error', state: { error: error.message } }
  }
})
```

## 关键要点

1. **始终 await 异步操作** - 否则导航会立即继续
2. **返回值很重要** - 返回路由以重定向,返回 false 以取消,返回 true/undefined 以继续
3. **处理所有错误情况** - 未捕获的错误会使导航卡住
4. **添加超时** - 缓慢的 API 不应无限阻塞导航
5. **显示加载状态** - 异步检查期间用户需要反馈
6. **并行化独立的检查** - 使用 Promise.all 提升性能

## 参考
- [Vue Router Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html)
- [Vue Router Navigation Failures](https://router.vuejs.org/guide/advanced/navigation-failures.html)
