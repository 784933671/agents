---
title: 生产环境应用应使用 Vue Router 库
impact: LOW
impactDescription: 简单哈希路由缺少生产环境 SPA 所需的关键特性；Vue Router 提供导航守卫、懒加载和完善的 history 管理
type: best-practice
tags: [vue3, vue-router, spa, production, architecture]
---

# 生产环境应用应使用 Vue Router 库

**Impact: LOW** - 虽然你可以用哈希变化和动态组件来实现基础路由，但任何生产环境的单页应用都应使用官方的 Vue Router 库。它提供了导航守卫、嵌套路由、懒加载以及完善的浏览器 history 集成等关键特性，而这些功能要手动实现既繁琐又容易出错。

## 任务清单

- [ ] 为生产环境 SPA 安装 Vue Router
- [ ] 仅在学习或小型原型中使用简单路由
- [ ] 善用内置特性：守卫、懒加载、meta 字段
- [ ] 考虑基于路由的状态和数据加载模式

## 简单路由可接受的场景

```vue
<!-- 仅适用于：学习、原型，或只有 2-3 个页面的微型应用 -->
<script setup>
import { ref, computed } from 'vue'
import Home from './Home.vue'
import About from './About.vue'

const routes = { '/': Home, '/about': About }
const currentPath = ref(window.location.hash.slice(1) || '/')

window.addEventListener('hashchange', () => {
  currentPath.value = window.location.hash.slice(1) || '/'
})

const currentView = computed(() => routes[currentPath.value])
</script>

<template>
  <nav>
    <a href="#/">Home</a>
    <a href="#/about">About</a>
  </nav>
  <component :is="currentView" />
</template>
```

## 为什么生产环境要用 Vue Router

### 你需要手动实现的功能

| 功能 | 简单路由 | Vue Router |
|---------|---------------|------------|
| 导航守卫 | 手动实现，易出错 | 内置，可组合 |
| 嵌套路由 | 实现复杂 | 原生支持 |
| 路由参数 | 手动解析 | 自动提取 |
| 懒加载 | 自行用动态 import 实现 | 内置代码分割 |
| History 模式（干净 URL） | 需服务器配置 + 手动处理 | 内置 |
| 滚动行为 | 手动处理 | 可配置 |
| 路由过渡 | 自行实现 | 与 Transition 集成 |
| 激活链接样式 | 手动切换 class | `router-link-active` class |
| 编程式导航 | `location.hash = ...` | `router.push()`、`router.replace()` |
| 路由 meta 字段 | 不适用 | 内置 |

## 使用 Vue Router 的生产环境配置

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),  // 懒加载
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue')
      }
    ]
  },
  {
    path: '/users/:id',
    name: 'UserProfile',
    component: () => import('@/views/UserProfile.vue'),
    props: true  // 将参数作为 props 传入
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

// 全局导航守卫
router.beforeEach((to, from) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
})

export default router
```

```javascript
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

createApp(App)
  .use(router)
  .mount('#app')
```

```vue
<!-- App.vue -->
<template>
  <nav>
    <router-link to="/">Home</router-link>
    <router-link to="/dashboard">Dashboard</router-link>
  </nav>

  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>
```

## 现代 Vue Router 特性（2025+）

```javascript
// 数据加载 API（Vue Router 4.2+）
const routes = [
  {
    path: '/users/:id',
    component: UserProfile,
    // 在路由层级加载数据
    loader: async (route) => {
      return { user: await fetchUser(route.params.id) }
    }
  }
]

// View Transitions API 集成
const router = createRouter({
  // 启用浏览器原生视图过渡
  // 需要浏览器支持（Chrome 111+）
})
```

## 要点

1. **任何超越原型的应用都应使用 Vue Router** - 这些特性都是必需的
2. **简单路由用于学习** - 先理解概念，再用库
3. **懒加载对打包体积至关重要** - Vue Router 让它变得轻而易举
4. **导航守卫能避免安全问题** - 手动实现很难做到正确
5. **History 模式离不开 Vue Router** - 干净的 URL 需要妥善处理
6. **新特性持续涌现** - Data Loading API、View Transitions

## 参考
- [Vue.js Routing Guide](https://vuejs.org/guide/scaling-up/routing.html)
- [Vue Router Documentation](https://router.vuejs.org/)
- [Vue Router Getting Started](https://router.vuejs.org/guide/)
