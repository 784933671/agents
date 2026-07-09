---
name: vue-best-practices
description: 必须用于 Vue.js 任务。强烈推荐 Composition API 配合 script setup 作为标准方案。覆盖 Vue 3、SSR、SFC、组件边界、响应式和组合式函数。处理任何 Vue、.vue 文件、Vue Router、Pinia 或 Vite with Vue 工作时加载。除非项目明确要求 Options API，否则始终使用 Composition API。
license: MIT
metadata:
  author: github.com/vuejs-ai
  version: "18.0.0"
---

# Vue 最佳实践工作流

将本技能作为指令集使用。除非用户明确要求不同顺序，否则按顺序执行工作流。

## 核心原则
- **保持状态可预测：** 单一数据源，其余全部派生。
- **让数据流显式化：** 多数情况遵循 Props 向下、Events 向上。
- **偏好小型、聚焦的组件：** 更易测试、复用与维护。
- **避免不必要的重渲染：** 明智地使用 computed 与 watcher。
- **可读性至上：** 编写清晰、自解释的代码。

## 1) 编码前确认架构（必需）

- 默认技术栈：Vue 3 + Composition API + `<script setup>` + JavaScript。
- 若项目明确使用 Options API，在可用时加载 `vue-options-api-best-practices` 技能。
- 若项目明确使用 JSX，在可用时加载 `vue-jsx-best-practices` 技能。

### 1.1 必读核心参考（必需）

- 实现任何 Vue 任务前，确保阅读并应用这些核心参考：
  - `references/reactivity.md`
  - `references/sfc.md`
  - `references/component-data-flow.md`
  - `references/composables.md`
- 在整个任务期间保持这些参考处于活跃工作上下文中，而非仅在具体问题出现时才查阅。

### 1.2 编码前规划组件边界（必需）

对任何非简单功能，在实现前创建简要的组件映射图。

- 用一句话定义每个组件的单一职责。
- 默认将入口/根和路由级 view 组件保持为组合层面。
- 将功能 UI 与功能逻辑移出入口/根/view 组件，除非任务本身就是一个小型单文件演示。
- 在映射图中为每个子组件定义 props/emits 契约。
- 当新增多个组件时，优先采用按功能分目录的布局（`components/<feature>/...`、`composables/use<Feature>.js`）。

## 2) 应用必备 Vue 基础（必需）

这些是必备的、必须掌握的基础。在 `1.1` 已加载的核心参考基础上，在每个 Vue 任务中全部应用。

### 响应式

- `1.1` 必读参考：[reactivity](references/reactivity.md)
- 保持源状态最小化（`ref`/`reactive`），用 `computed` 尽可能派生其余内容。
- 需要时用 watcher 处理副作用。
- 避免在模板中重复计算昂贵逻辑。

### SFC 结构与模板安全

- `1.1` 必读参考：[sfc](references/sfc.md)
- SFC 各部分保持此顺序：`<script>` → `<template>` → `<style>`。
- 保持 SFC 职责聚焦；拆分过大的组件。
- 保持模板声明式；将分支/派生移到 script。
- 应用 Vue 模板安全规则（`v-html`、列表渲染、条件渲染选择）。

### 保持组件聚焦

当一个组件有**多个明确职责**时（如数据编排 + UI，或多个独立 UI 区域），拆分它。

- 偏好**更小的组件 + composables**，而非一个"巨型组件"
- 将 **UI 区域**移入子组件（props 进、events 出）。
- 将**状态/副作用**移入 composables（`useXxx()`）。

应用客观的拆分触发条件。当**任一**条件为真时拆分组件：

- 它同时拥有编排/状态与多个区域的大量展示性标记。
- 它有 3 个及以上独立 UI 区域（例如：表单、筛选器、列表、底部/状态栏）。
- 某个模板块被重复使用或可能变为可复用（条目行、卡片、列表项）。

入口/根与路由 view 规则：

- 保持入口/根与路由 view 组件精简：应用外壳/布局、provider 接线与功能组合。
- 当入口/根/view 组件中的功能包含独立部分时，不要在其中放置完整功能实现。
- 对于 CRUD/列表功能（待办、表格、目录、收件箱），至少拆分为：
  - 功能容器组件
  - 输入/表单组件
  - 列表（和/或条目）组件
  - 底部/操作或筛选/状态组件
- 仅对非常小的一次性演示允许单文件实现；若选择此方式，明确说明为何无需拆分。

### 组件数据流

- `1.1` 必读参考：[component-data-flow](references/component-data-flow.md)
- 以 props 向下、events 向上作为主要模型。
- 仅在真正的双向组件契约时使用 `v-model`。
- 仅在深层树依赖或共享上下文时使用 provide/inject。
- 保持契约显式，按需使用 `defineProps`、`defineEmits` 和 provide/inject。

### Composables

- `1.1` 必读参考：[composables](references/composables.md)
- 当逻辑被复用、有状态或副作用较重时，提取为 composables。
- 保持 composable 的 API 小巧且可预测。
- 将功能逻辑与展示组件分离。

## 3) 仅在需求出现时考虑可选特性

### 3.1 标准可选特性

默认不要添加。仅在对应需求存在时加载匹配的参考。

- 插槽：父组件需要控制子组件内容/布局 -> [component-slots](references/component-slots.md)
- 透传属性：包装/基础组件需安全转发 attrs/events -> [component-fallthrough-attrs](references/component-fallthrough-attrs.md)
- 内置组件 `<KeepAlive>` 用于有状态视图缓存 -> [component-keep-alive](references/component-keep-alive.md)
- 内置组件 `<Teleport>` 用于覆盖层/门户 -> [component-teleport](references/component-teleport.md)
- 内置组件 `<Suspense>` 用于异步子树回退边界 -> [component-suspense](references/component-suspense.md)
- 动画相关特性：选择与所需运动行为匹配的最简方案。
  - 内置组件 `<Transition>` 用于进入/离开效果 -> [transition](references/component-transition.md)
  - 内置组件 `<TransitionGroup>` 用于列表变化的动画 -> [transition-group](references/component-transition-group.md)
  - 基于类的动画用于非进入/离开效果 -> [animation-class-based-technique](references/animation-class-based-technique.md)
  - 状态驱动的动画用于用户输入驱动的动画 -> [animation-state-driven-technique](references/animation-state-driven-technique.md)

### 3.2 较不常见的可选特性

仅在明确的产品或技术需求时使用。

- 指令：行为是 DOM 特定的，不适合 composable/组件 -> [directives](references/directives.md)
- 异步组件：重型/少用的 UI 应懒加载 -> [component-async](references/component-async.md)
- 仅在模板无法表达需求时使用渲染函数 -> [render-functions](references/render-functions.md)
- 当行为必须全应用范围安装时使用插件 -> [plugins](references/plugins.md)
- 状态管理模式：跨功能边界的应用级共享状态 -> [state-management](references/state-management.md)

## 4) 行为正确后再做性能优化

性能工作是功能完成后的后续步骤。不要在核心行为实现并验证前优化。

- 大列表渲染瓶颈 -> [perf-virtualize-large-lists](references/perf-virtualize-large-lists.md)
- 静态子树被不必要地重渲染 -> [perf-v-once-v-memo-directives](references/perf-v-once-v-memo-directives.md)
- 热列表路径中的过度抽象 -> [perf-avoid-component-abstraction-in-lists](references/perf-avoid-component-abstraction-in-lists.md)
- 昂贵更新触发过于频繁 -> [updated-hook-performance](references/updated-hook-performance.md)

## 5) 完成前的最终自检

- 核心行为可用且符合需求。
- 所有必读参考已阅读并应用。
- 响应式模型最小化且可预测。
- SFC 结构与模板规则已遵循。
- 组件聚焦且拆分合理，按需拆分。
- 入口/根与路由 view 组件保持为组合层面，除非有明确的小演示例外。
- 组件拆分决策显式且站得住脚（职责边界清晰）。
- 数据流契约显式且边界清晰。
- 在复用/复杂度合理处使用了 composables。
- 如适用，已将状态/副作用移入 composables。
- 可选特性仅在需求需要时使用。
- 性能变更仅在功能完成后应用。
