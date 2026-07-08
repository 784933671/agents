---
title: beforeRouteEnter 无法访问组件实例
impact: MEDIUM
impactDescription: beforeRouteEnter 守卫在组件创建之前执行,因此 this 是 undefined;使用 next 回调来访问组件实例
type: gotcha
tags: [vue3, vue-router, navigation-guards, lifecycle, this]
---

# beforeRouteEnter 无法访问组件实例

**Impact: MEDIUM** - `beforeRouteEnter` 组件内导航守卫在组件创建**之前**执行,意味着你无法访问 `this` 或任何组件实例属性。这是唯一一个支持在 `next()` 函数中使用回调、以便在导航完成后访问组件实例的导航守卫。

## 任务清单

- [ ] 使用 next(vm => ...) 回调来访问组件实例
- [ ] 或者使用具有不同模式的组合式 API 守卫
- [ ] 根据时机需求,合理地迁移数据获取逻辑
- [ ] 对于不需要访问组件的数据,考虑使用全局守卫

## 问题

```javascript
// Options API - 错误: this 是 undefined
export default {
  data() {
    return { user: null }
  },
  beforeRouteEnter(to, from, next) {
    // BUG: 这里 this 是 undefined - 组件还不存在!
    this.user = await fetchUser(to.params.id)  // ERROR!
    next()
  }
}
```

## 解决方案:使用 next() 回调（Options API）

```javascript
// Options API - 正确:使用回调访问 vm
export default {
  data() {
    return {
      user: null,
      loading: true
    }
  },

  beforeRouteEnter(to, from, next) {
    // 在组件存在之前获取数据
    fetchUser(to.params.id)
      .then(user => {
        // 向 next() 传入回调 - 接收组件实例作为 'vm'
        next(vm => {
          vm.user = user
          vm.loading = false
        })
      })
      .catch(error => {
        next(vm => {
          vm.error = error
          vm.loading = false
        })
      })
  }
}
```

## 解决方案:异步的 beforeRouteEnter（Options API）

```javascript
export default {
  data() {
    return { userData: null }
  },

  async beforeRouteEnter(to, from, next) {
    try {
      const user = await fetchUser(to.params.id)

      // 访问组件仍需通过回调
      next(vm => {
        vm.userData = user
      })
    } catch (error) {
      // 出错时重定向
      next('/error')
    }
  }
}
```

## 组合式 API 替代方案

在使用 `<script setup>` 的组合式 API 中,你无法直接使用 `beforeRouteEnter`,因为组件实例正在被建立。请改用其他模式：

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, onBeforeRouteUpdate } from 'vue-router'

const route = useRoute()
const user = ref(null)
const loading = ref(true)

// 选项 1:在 onMounted 中获取数据（组件存在之后）
onMounted(async () => {
  user.value = await fetchUser(route.params.id)
  loading.value = false
})

// 选项 2:处理后续的参数变化
onBeforeRouteUpdate(async (to, from) => {
  if (to.params.id !== from.params.id) {
    loading.value = true
    user.value = await fetchUser(to.params.id)
    loading.value = false
  }
})
</script>
```

## 路由级数据获取

对于需要在导航**之前**加载的数据,使用路由级守卫：

```javascript
// router.js
const routes = [
  {
    path: '/users/:id',
    component: () => import('./UserProfile.vue'),
    beforeEnter: async (to, from) => {
      try {
        // 存储数据供组件访问
        const user = await fetchUser(to.params.id)
        to.meta.user = user  // 附加到 route meta
      } catch (error) {
        return '/error'
      }
    }
  }
]
```

```vue
<!-- UserProfile.vue -->
<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
// 从 meta 中访问预先获取的数据
const user = route.meta.user
</script>
```

## 导航守卫对比

| 守卫 | 是否有 `this`/组件? | 能否延迟导航? | 用途 |
|-------|----------------------|----------------------|----------|
| beforeRouteEnter | 否（使用 next 回调） | 是 | 预获取、数据缺失时重定向 |
| beforeRouteUpdate | 是 | 是 | 响应参数变化 |
| beforeRouteLeave | 是 | 是 | 未保存改动警告 |
| Global beforeEach | 否 | 是 | 鉴权检查 |
| Route beforeEnter | 否 | 是 | 路由级校验 |

## 关键要点

1. **beforeRouteEnter 在组件创建之前运行** - 无法访问 `this`
2. **使用 next(vm => ...) 回调** - 这是访问组件实例的唯一方式
3. **组合式 API 存在限制** - 改用 onMounted 或全局守卫
4. **考虑用 route meta 承载预获取的数据** - 实现清晰的关注点分离
5. **beforeRouteUpdate 和 beforeRouteLeave 可以访问组件** - 它们运行时组件已存在

## 参考
- [Vue Router In-Component Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html#in-component-guards)
- [Vue Router Navigation Resolution Flow](https://router.vuejs.org/guide/advanced/navigation-guards.html#the-full-navigation-resolution-flow)
