---
title: 虚拟化大型列表以避免 DOM 过载
impact: HIGH
impactDescription: 渲染数千个列表项会产生过多 DOM 节点，导致渲染缓慢和内存占用过高
type: efficiency
tags: [vue3, performance, virtual-list, large-data, dom, optimization]
---

# 虚拟化大型列表以避免 DOM 过载

**影响等级：HIGH** - 渲染大型列表（数百或数千条）中的所有项会产生大量 DOM 节点。每个节点都会消耗内存、拖慢首次渲染，并使更新成本变高。列表虚拟化只渲染可见项，从而显著提升性能。

当处理的列表可能超过 50-100 项时，尤其是项的内容较为复杂时，请使用虚拟化库。

## 任务清单

- 识别渲染超过 50-100 项的列表
- 安装虚拟化库（vue-virtual-scroller、@tanstack/vue-virtual）
- 用虚拟化 component 替换标准的 `v-for`
- 确保列表项具有一致或可估算的高度
- 在开发阶段使用真实数据量进行测试

## 推荐库

| 库 | 适用场景 | 说明 |
|---------|----------|-------|
| `vue-virtual-scroller` | 通用场景，配置简单 | 最流行，默认值合理 |
| `@tanstack/vue-virtual` | 复杂布局，无头模式 | 框架无关，灵活 |
| `vue-virtual-scroll-grid` | 网格布局 | 二维虚拟化 |
| `vueuc/VVirtualList` | Naive UI 项目 | Naive UI 生态的一部分 |

**反面示例：**
```vue
<template>
  <!-- BAD: Renders ALL 10,000 items immediately -->
  <div class="user-list">
    <UserCard
      v-for="user in users"
      :key="user.id"
      :user="user"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import UserCard from './UserCard.vue'

const users = ref([])

onMounted(async () => {
  // 10,000 DOM nodes created, browser struggles
  users.value = await fetchAllUsers()
})
</script>
```

**正面示例：**
```vue
<template>
  <!-- GOOD: Only renders ~20 visible items at a time -->
  <RecycleScroller
    class="user-list"
    :items="users"
    :item-size="80"
    key-field="id"
    v-slot="{ item }"
  >
    <UserCard :user="item" />
  </RecycleScroller>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import UserCard from './UserCard.vue'

const users = ref([])

onMounted(async () => {
  // 10,000 items in memory, but only ~20 DOM nodes
  users.value = await fetchAllUsers()
})
</script>

<style scoped>
.user-list {
  height: 600px; /* Container must have fixed height */
}
</style>
```

## 使用 @tanstack/vue-virtual

```vue
<template>
  <div ref="parentRef" class="list-container">
    <div
      :style="{
        height: `${rowVirtualizer.getTotalSize()}px`,
        position: 'relative'
      }"
    >
      <div
        v-for="virtualRow in rowVirtualizer.getVirtualItems()"
        :key="virtualRow.key"
        :style="{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: `${virtualRow.size}px`,
          transform: `translateY(${virtualRow.start}px)`
        }"
      >
        <UserCard :user="users[virtualRow.index]" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useVirtualizer } from '@tanstack/vue-virtual'

const users = ref([/* 10,000 users */])
const parentRef = ref(null)

const rowVirtualizer = useVirtualizer({
  count: users.value.length,
  getScrollElement: () => parentRef.value,
  estimateSize: () => 80,  // Estimated row height
  overscan: 5  // Render 5 extra items above/below viewport
})
</script>

<style scoped>
.list-container {
  height: 600px;
  overflow: auto;
}
</style>
```

## 使用 vue-virtual-scroller 处理动态高度

```vue
<template>
  <!-- For variable height items, use DynamicScroller -->
  <DynamicScroller
    :items="messages"
    :min-item-size="54"
    key-field="id"
  >
    <template #default="{ item, index, active }">
      <DynamicScrollerItem
        :item="item"
        :active="active"
        :data-index="index"
      >
        <ChatMessage :message="item" />
      </DynamicScrollerItem>
    </template>
  </DynamicScroller>
</template>

<script setup>
import { DynamicScroller, DynamicScrollerItem } from 'vue-virtual-scroller'
</script>
```

## 性能对比

| 方案 | 100 项 | 1,000 项 | 10,000 项 |
|----------|-----------|-------------|--------------|
| 常规 v-for | ~100 个 DOM 节点 | ~1,000 个 DOM 节点 | ~10,000 个 DOM 节点 |
| 虚拟化 | ~20 个 DOM 节点 | ~20 个 DOM 节点 | ~20 个 DOM 节点 |
| 初始渲染 | 快 | 慢 | 非常慢 / 崩溃 |
| 虚拟化渲染 | 快 | 快 | 快 |

## 不应虚拟化的场景

- 项数少于 50 且内容简单的列表
- 所有项必须同时对屏幕阅读器可访问的列表
- 所有内容都必须渲染的打印布局
- 必须出现在初始 HTML 中的 SEO 关键内容
