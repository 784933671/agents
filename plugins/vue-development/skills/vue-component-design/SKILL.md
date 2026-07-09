---
name: vue-component-design
description: Vue 3 + JavaScript 业务组件设计规范。用于拆分页面、设计 props/emits/slots、封装 Element Plus/Vant 业务组件、处理 v-model 契约、列表/详情/弹窗/筛选组件边界，并避免巨型 SFC。
---

# Vue Component Design

## 工作原则

- 优先复用项目已有组件、hooks/composables、样式规范和组件库封装。
- 使用 Vue 3 Composition API，但代码按 JavaScript 项目编写，不加入类型标注。
- 页面负责业务编排，组件负责单一 UI 或交互职责。
- 不为一次性小片段过度抽象；只在复用、复杂度或职责边界明确时拆分。

## 拆分判断

满足任一条件时考虑拆分组件：

- 单个 SFC 同时包含查询、列表、弹窗、表单、详情等多个区域。
- 模板超过一个清晰屏幕，且多个区域可以独立命名。
- 同一 UI 片段被复用或即将复用。
- 某块逻辑需要独立 loading、error、visible、selected 等状态。
- PC 和 H5 有不同展示，但共享同一业务语义。

## 推荐边界

- `views/xxx/index.vue`：路由页，负责拉数据、组合区域、处理路由。
- `components/xxx/SearchForm.vue`：查询条件和查询/重置事件。
- `components/xxx/DataTable.vue`：表格展示、分页、行操作事件。
- `components/xxx/EditDialog.vue`：PC 弹窗新增/编辑。
- `components/xxx/MobileForm.vue`：H5 表单页或表单块。
- `composables/useXxx.js`：可复用状态、副作用、请求编排。

## Props 设计

- props 只传组件需要的数据，不把整页状态对象塞进去。
- 对象和数组给默认工厂函数。
- 布尔值命名用正向语义，例如 `disabled`、`readonly`、`loading`。
- 组件内部不要直接修改 props；需要变更时 emit 事件。

```js
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({}),
  },
  loading: {
    type: Boolean,
    default: false,
  },
})
```

## Emits 设计

- 事件名表达业务意图，不只写 `change`。
- 表单提交用 `submit`，弹窗关闭用 `close`，行操作用 `edit`、`delete`、`view`。
- 双向绑定遵循 `modelValue` / `update:modelValue`。
- 子组件只发事件，不直接调用父级接口请求，除非它就是一个完整业务容器。

```js
const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

function updateField(key, value) {
  emit('update:modelValue', {
    ...props.modelValue,
    [key]: value,
  })
}
```

## Slots 设计

- 用 slot 让父级控制不稳定内容，例如表格操作列、卡片底部、弹窗 footer。
- slot 名称使用业务含义，如 `actions`、`footer`、`empty`。
- 不要为了一两个固定按钮引入复杂 slot，直接用 props 或事件即可。

## Element Plus 和 Vant 封装

- PC 端可以围绕 `el-table`、`el-dialog`、`el-form` 做业务封装。
- H5 端可以围绕 `van-list`、`van-form`、`van-popup` 做轻量封装。
- 封装组件保留原组件关键能力，避免把常用属性全部藏死。
- 跨 PC/H5 复用业务逻辑时，优先复用 composable，不强行复用 UI 组件。

## 完成检查

- 每个组件能用一句话说清职责。
- props、emits、slots 契约清晰，没有隐藏父子耦合。
- 页面层没有膨胀成巨型 SFC。
- PC/H5 差异留在展示层，共用逻辑沉到 composable。
