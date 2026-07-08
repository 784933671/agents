---
title: 使用 v-once 和 v-memo 跳过不必要的更新
impact: MEDIUM
impactDescription: v-once 跳过静态内容的所有后续更新；v-memo 按条件对子树进行记忆化
type: efficiency
tags: [vue3, performance, v-once, v-memo, optimization, directives]
---

# 使用 v-once 和 v-memo 跳过不必要的更新

**影响等级：MEDIUM** - Vue 会在每次响应式变更时重新求值模板。对于永不改变或很少改变的内容，`v-once` 和 `v-memo` 可以告知 Vue 跳过更新，从而减少渲染工作量。

对真正静态的内容使用 `v-once`，对列表中按条件静态的内容使用 `v-memo`。

## 任务清单

- 对使用了运行时数据但永远不需要更新的元素应用 `v-once`
- 对只应在特定条件变更时才更新的列表项应用 `v-memo`
- 验证被记忆化的内容确实不需要响应其他状态变更
- 使用 Vue DevTools 进行性能分析，确认更新被跳过

## v-once：渲染一次，永不更新

**反面示例：**
```vue
<template>
  <!-- BAD: Re-evaluated on every parent re-render -->
  <div class="terms-content">
    <h1>Terms of Service</h1>
    <p>Version: {{ termsVersion }}</p>
    <div v-html="termsContent"></div>
  </div>

  <!-- This content NEVER changes, but Vue checks it every render -->
  <footer>
    <p>Copyright {{ copyrightYear }} {{ companyName }}</p>
  </footer>
</template>
```

**正面示例：**
```vue
<template>
  <!-- GOOD: Rendered once, skipped on all future updates -->
  <div class="terms-content" v-once>
    <h1>Terms of Service</h1>
    <p>Version: {{ termsVersion }}</p>
    <div v-html="termsContent"></div>
  </div>

  <!-- v-once tells Vue this never needs to update -->
  <footer v-once>
    <p>Copyright {{ copyrightYear }} {{ companyName }}</p>
  </footer>
</template>

<script setup>
// These values are set once at component creation
const termsVersion = '2.1'
const termsContent = fetchedTermsHTML
const copyrightYear = 2024
const companyName = 'Acme Corp'
</script>
```

## v-memo：列表的条件记忆化

**反面示例：**
```vue
<template>
  <!-- BAD: All items re-render when selectedId changes -->
  <div v-for="item in list" :key="item.id">
    <div :class="{ selected: item.id === selectedId }">
      <ExpensiveComponent :data="item" />
    </div>
  </div>
</template>
```

**正面示例：**
```vue
<template>
  <!-- GOOD: Items only re-render when their selection state changes -->
  <div
    v-for="item in list"
    :key="item.id"
    v-memo="[item.id === selectedId]"
  >
    <div :class="{ selected: item.id === selectedId }">
      <ExpensiveComponent :data="item" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const list = ref([/* many items */])
const selectedId = ref(null)

// When selectedId changes:
// - Only the previously-selected item re-renders (selected: true -> false)
// - Only the newly-selected item re-renders (selected: false -> true)
// - All other items are SKIPPED (v-memo values unchanged)
</script>
```

## 带多个依赖的 v-memo

```vue
<template>
  <!-- Re-render only when item's selection OR editing state changes -->
  <div
    v-for="item in items"
    :key="item.id"
    v-memo="[item.id === selectedId, item.id === editingId]"
  >
    <ItemCard
      :item="item"
      :selected="item.id === selectedId"
      :editing="item.id === editingId"
    />
  </div>
</template>

<script setup>
const selectedId = ref(null)
const editingId = ref(null)
const items = ref([/* ... */])
</script>
```

## v-memo 使用空数组等价于 v-once

```vue
<template>
  <!-- v-memo="[]" is equivalent to v-once -->
  <div v-for="item in staticList" :key="item.id" v-memo="[]">
    {{ item.name }}
  </div>
</template>
```

## 不应使用这些指令的场景

```vue
<template>
  <!-- DON'T: Content that DOES need to update -->
  <div v-once>
    <span>Count: {{ count }}</span>  <!-- count won't update! -->
  </div>

  <!-- DON'T: When child components have their own reactive state -->
  <div v-memo="[selected]">
    <InputField v-model="item.name" />  <!-- v-model won't work properly -->
  </div>

  <!-- DON'T: When the memoization benefit is minimal -->
  <span v-once>{{ simpleText }}</span>  <!-- Overhead not worth it -->
</template>
```

## 性能对比

| 场景 | 不使用指令 | 使用 v-once/v-memo |
|----------|-------------------|-------------------|
| 静态头部，父组件重渲染 100 次 | 重新求值 100 次 | 仅求值 1 次 |
| 1000 项，选中状态变更 | 1000 项全部重渲染 | 仅 2 项重渲染 |
| 复杂子组件 | 完整重渲染 | 被记忆化时跳过 |

## 调试被记忆化的组件

```vue
<script setup>
import { onUpdated } from 'vue'

// This won't fire if v-memo prevents update
onUpdated(() => {
  console.log('Component updated')
})
</script>
```
