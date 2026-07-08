---
title: 避免在 updated 钩子中执行昂贵操作
impact: MEDIUM
impactDescription: 在 updated 钩子中进行繁重计算会导致性能瓶颈和潜在的无限循环
type: capability
tags: [vue3, vue2, lifecycle, updated, performance, optimization, reactivity]
---

# 避免在 updated 钩子中执行昂贵操作

**影响等级：MEDIUM** - `updated` 钩子会在每次导致重渲染的响应式状态变更之后执行。在此处放置昂贵操作、API 调用或状态变更，会导致严重的性能退化、无限循环，以及帧率跌破 60fps 这一理想阈值。

应谨慎使用 `updated`/`onUpdated`，仅用于无法由 watcher 或 computed 处理的 DOM 更新后操作。对于大多数响应式数据处理，优先使用 watcher（`watch`/`watchEffect`），它们能更精确地控制什么会触发回调。

## 任务清单

- 永远不要在 updated 钩子中发起 API 调用
- 永远不要在 updated 中变更响应式状态（会导致无限循环）
- 在执行操作前使用条件判断确认更新是否相关
- 优先使用 `watch` 或 `watchEffect` 来响应特定的数据变化
- 如果 updated 中的操作较昂贵，应使用节流/防抖
- 将 updated 保留给底层的 DOM 同步任务

**反面示例：**
```javascript
// BAD: API call in updated - fires on every re-render
export default {
  data() {
    return { items: [], lastUpdate: null }
  },
  updated() {
    // This runs after every single state change!
    fetch('/api/sync', {
      method: 'POST',
      body: JSON.stringify(this.items)
    })
  }
}
```

```javascript
// BAD: State mutation in updated - infinite loop
export default {
  data() {
    return { renderCount: 0 }
  },
  updated() {
    // This causes another update, which triggers updated again!
    this.renderCount++ // Infinite loop
  }
}
```

```javascript
// BAD: Heavy computation on every update
export default {
  updated() {
    // Expensive operation runs on every keystroke, every state change
    this.processedData = this.heavyComputation(this.rawData)
    this.analytics = this.calculateMetrics(this.allData)
  }
}
```

**正面示例：**
```javascript
import debounce from 'lodash-es/debounce'

// GOOD: Use watcher for specific data changes
export default {
  data() {
    return { items: [] }
  },
  watch: {
    // Only fires when items actually changes
    items: {
      handler(newItems) {
        this.syncToServer(newItems)
      },
      deep: true
    }
  },
  methods: {
    syncToServer: debounce(function(items) {
      fetch('/api/sync', {
        method: 'POST',
        body: JSON.stringify(items)
      })
    }, 500)
  }
}
```

```vue
<!-- GOOD: Composition API with targeted watchers -->
<script setup>
import { ref, watch, onUpdated } from 'vue'
import { useDebounceFn } from '@vueuse/core'

const items = ref([])
const scrollContainer = ref(null)

// Watch specific data - not all updates
watch(items, (newItems) => {
  syncToServer(newItems)
}, { deep: true })

const syncToServer = useDebounceFn((items) => {
  fetch('/api/sync', { method: 'POST', body: JSON.stringify(items) })
}, 500)

// Only use onUpdated for DOM synchronization
onUpdated(() => {
  // Scroll to bottom only if content changed height
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
})
</script>
```

```javascript
// GOOD: Conditional check in updated hook
export default {
  data() {
    return {
      content: '',
      lastSyncedContent: ''
    }
  },
  updated() {
    // Only act if specific condition is met
    if (this.content !== this.lastSyncedContent) {
      this.syncContent()
      this.lastSyncedContent = this.content
    }
  },
  methods: {
    syncContent: debounce(function() {
      // Sync logic
    }, 300)
  }
}
```

## updated 钩子的合理使用场景

```javascript
// GOOD: Low-level DOM synchronization
export default {
  updated() {
    // Sync third-party library with Vue's DOM
    this.thirdPartyWidget.refresh()

    // Update scroll position after content change
    this.$nextTick(() => {
      this.maintainScrollPosition()
    })
  }
}
```

## 派生数据应优先使用 computed

```javascript
// BAD: Calculating derived data in updated
export default {
  data() {
    return { numbers: [1, 2, 3, 4, 5] }
  },
  updated() {
    this.sum = this.numbers.reduce((a, b) => a + b, 0) // Causes another update!
  }
}

// GOOD: Use computed property instead
export default {
  data() {
    return { numbers: [1, 2, 3, 4, 5] }
  },
  computed: {
    sum() {
      return this.numbers.reduce((a, b) => a + b, 0)
    }
  }
}
```
