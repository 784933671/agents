---
title: 简单哈希路由需要清理事件监听器
impact: MEDIUM
impactDescription: 在不使用 Vue Router 实现基础路由时，忘记移除 hashchange 监听器会导致内存泄漏和多次执行处理函数
type: gotcha
tags: [vue3, routing, events, memory-leak, cleanup]
---

# 简单哈希路由需要清理事件监听器

**Impact: MEDIUM** - 在不使用 Vue Router 实现基础客户端路由时（即使用基于 `hashchange` 事件的哈希路由），必须在组件卸载时清理事件监听器。否则会造成内存泄漏，并可能在组件重新创建后触发多个处理函数同时执行。

## 任务清单

- [ ] 保存事件监听器的引用以便清理
- [ ] 使用 onUnmounted 移除事件监听器
- [ ] 生产环境应用考虑改用 Vue Router
- [ ] 测试组件的挂载/卸载循环

## 问题

```vue
<script setup>
import { ref, computed } from 'vue'
import Home from './Home.vue'
import About from './About.vue'

const routes = {
  '/': Home,
  '/about': About
}

const currentPath = ref(window.location.hash)

// BUG：事件监听器从未被移除！
// 该组件每次挂载都会新增一个监听器
// 挂载 5 次后，就会有 5 个监听器同时在运行
window.addEventListener('hashchange', () => {
  currentPath.value = window.location.hash
})

const currentView = computed(() => {
  return routes[currentPath.value.slice(1) || '/']
})
</script>
```

**会发生什么：**
1. 组件挂载，添加监听器
2. 组件卸载（例如路由切换、v-if 切换）
3. 组件再次挂载，又添加了一个监听器
4. 现在每次哈希变化都会触发两个监听器
5. 最终导致性能问题和内存泄漏

## 解决方案：使用 onUnmounted 正确清理

```vue
<script setup>
import { ref, computed, onUnmounted } from 'vue'
import Home from './Home.vue'
import About from './About.vue'
import NotFound from './NotFound.vue'

const routes = {
  '/': Home,
  '/about': About
}

const currentPath = ref(window.location.hash)

// 保存处理函数引用以便清理
function handleHashChange() {
  currentPath.value = window.location.hash
}

// 添加监听器
window.addEventListener('hashchange', handleHashChange)

// 关键：卸载时移除监听器
onUnmounted(() => {
  window.removeEventListener('hashchange', handleHashChange)
})

const currentView = computed(() => {
  return routes[currentPath.value.slice(1) || '/'] || NotFound
})
</script>
```

## 解决方案：使用 Options API

```vue
<script>
import Home from './Home.vue'
import About from './About.vue'
import NotFound from './NotFound.vue'

const routes = {
  '/': Home,
  '/about': About
}

export default {
  data() {
    return {
      currentPath: window.location.hash
    }
  },

  computed: {
    currentView() {
      return routes[this.currentPath.slice(1) || '/'] || NotFound
    }
  },

  mounted() {
    // 保存绑定后的处理函数以便清理
    this.hashHandler = () => {
      this.currentPath = window.location.hash
    }
    window.addEventListener('hashchange', this.hashHandler)
  },

  beforeUnmount() {
    // 清理
    window.removeEventListener('hashchange', this.hashHandler)
  }
}
</script>
```

## 解决方案：用于可复用哈希路由的 Composable

```javascript
// composables/useHashRouter.js
import { ref, computed, onUnmounted } from 'vue'

export function useHashRouter(routes, notFoundComponent = null) {
  const currentPath = ref(window.location.hash)

  function handleHashChange() {
    currentPath.value = window.location.hash
  }

  // 初始化
  window.addEventListener('hashchange', handleHashChange)

  // 清理 - 组件卸载时自动处理
  onUnmounted(() => {
    window.removeEventListener('hashchange', handleHashChange)
  })

  const currentView = computed(() => {
    const path = currentPath.value.slice(1) || '/'
    return routes[path] || notFoundComponent
  })

  function navigate(path) {
    window.location.hash = path
  }

  return {
    currentPath,
    currentView,
    navigate
  }
}
```

```vue
<!-- 用法 -->
<script setup>
import { useHashRouter } from '@/composables/useHashRouter'
import Home from './Home.vue'
import About from './About.vue'
import NotFound from './NotFound.vue'

const { currentView } = useHashRouter({
  '/': Home,
  '/about': About
}, NotFound)
</script>

<template>
  <component :is="currentView" />
</template>
```

## 何时使用简单路由，何时使用 Vue Router

| 使用简单哈希路由 | 使用 Vue Router |
|------------------------|----------------|
| 学习/原型验证 | 生产环境应用 |
| 极简应用（2-3 个页面） | 需要嵌套路由 |
| 没有构建步骤 | 需要导航守卫 |
| 对打包体积要求苛刻 | 需要懒加载 |
| 仅静态托管 | 需要 history 模式（干净的 URL） |

## 要点

1. **务必清理事件监听器** - 使用 onUnmounted 或 beforeUnmount
2. **保存处理函数引用** - 匿名函数无法被移除
3. **真实应用考虑使用 Vue Router** - 它会自动处理清理工作
4. **测试卸载场景** - v-if 切换、热模块替换
5. **Composable 有助于封装清理逻辑** - 可复用且自动化

## 参考
- [Vue.js Routing Documentation](https://vuejs.org/guide/scaling-up/routing.html)
- [Vue Router Official Library](https://router.vuejs.org/)
