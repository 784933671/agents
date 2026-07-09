---
name: element-plus-forms
description: Element Plus PC 端表单开发规范。用于 Vue 3 + JavaScript 项目中实现、修复或重构 el-form、el-form-item、rules、弹窗新增/编辑表单、查询表单、动态校验、异步校验、提交 loading、防重复提交和接口错误回填。
---

# Element Plus Forms

## 工作原则

- 优先复用项目已有表单组件、请求工具、字典工具和校验方法。
- 使用 Vue 3 Composition API，但代码按 JavaScript 项目编写，不加入类型标注。
- 表单状态、校验规则、提交状态、弹窗状态分开维护，避免把所有逻辑塞进模板。
- 所有提交类异步请求必须 `try/catch/finally`，失败时给出兜底提示并恢复 loading。

## 基础结构

- `el-form` 必须绑定 `ref`、`:model`、`:rules`。
- 每个需要校验的 `el-form-item` 必须设置 `prop`，且 `prop` 与 `model` 字段一致。
- `rules` 保持稳定，避免在模板内临时拼接复杂规则。
- 数字输入优先用 `v-model.number` 或提交前显式转换，避免字符串数字进入接口。
- 表单默认值集中定义，用工厂函数生成，避免新增/编辑互相污染。

```vue
<script setup>
import { reactive, ref, nextTick } from 'vue'

const formRef = ref()
const visible = ref(false)
const submitting = ref(false)

const createDefaultForm = () => ({
  name: '',
  status: '',
  sort: 0,
})

const form = reactive(createDefaultForm())

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

function assignForm(data = {}) {
  Object.assign(form, createDefaultForm(), data)
}
</script>
```

## 新增/编辑弹窗

- 新增：打开前写入默认值，`nextTick` 后清除历史校验。
- 编辑：先回填接口数据，再 `clearValidate()`，不要让旧错误跟随弹窗打开。
- 不要直接替换 `reactive` 表单对象；用 `Object.assign` 保持响应式引用稳定。
- 关闭弹窗时根据业务选择 `resetFields()` 或重新写入默认值，避免编辑数据残留。

```js
async function openCreate() {
  assignForm()
  visible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

async function openEdit(row) {
  assignForm(row)
  visible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}
```

## 提交流程

- 提交前先 `await formRef.value.validate()`。
- 校验失败不请求接口；接口失败不关闭弹窗。
- 使用 `submitting` 禁止重复提交。
- 提交成功后再关闭弹窗、刷新列表或回传事件。

```js
async function handleSubmit() {
  if (!formRef.value || submitting.value) return

  try {
    await formRef.value.validate()
    submitting.value = true
    await saveApi({ ...form })
    visible.value = false
    await loadList()
  } catch (error) {
    handleSubmitError(error)
  } finally {
    submitting.value = false
  }
}
```

## 动态和异步校验

- 字段联动后，用 `clearValidate(field)` 清掉已失效的错误。
- 只校验局部字段时使用 `validateField(field)`。
- 异步唯一性校验必须处理接口异常；异常时返回明确错误，不静默通过。
- 后端返回字段级错误时，优先映射到对应字段；无法映射时用全局消息提示。

## 查询表单

- 查询表单和编辑表单分开建模。
- 查询条件提交前清理空字符串、空数组和无效日期。
- 重置查询条件后立即回到第一页并重新请求列表。

## 完成检查

- 校验字段的 `prop` 与 `model` 完全匹配。
- 打开新增/编辑弹窗不会残留旧值或旧校验错误。
- 提交 loading、重复点击、接口失败、校验失败都有闭环。
- 所有异步请求都有异常捕获。
