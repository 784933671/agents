---
name: vant-forms
description: Vant H5 表单开发规范。用于 Vue 3 + JavaScript 移动端项目中实现、修复或重构 van-form、van-field、rules、验证码、Picker/Calendar 联动、移动端输入体验、异步校验、提交 loading、防重复提交和失败兜底。
---

# Vant Forms

## 工作原则

- 优先复用项目已有 Vant 封装、请求工具、Toast 工具和业务校验方法。
- 使用 Vue 3 Composition API，但代码按 JavaScript 项目编写，不加入类型标注。
- 移动端表单优先保证输入效率、键盘类型、错误提示和提交反馈。
- 所有提交、验证码、异步校验请求必须 `try/catch/finally`。

## 基础结构

- `van-form` 使用 `@submit` 处理已通过校验的数据，使用 `@failed` 处理校验失败。
- 每个 `van-field` 设置 `name`，`name` 会成为提交 values 的字段名。
- 校验写在 `:rules`，支持 `required`、`pattern`、`validator`、异步 `validator`。
- 提交按钮使用 `native-type="submit"`，并绑定 loading。

```vue
<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'

const submitting = ref(false)
const mobile = ref('')
const code = ref('')

const mobileRules = [
  { required: true, message: '请输入手机号' },
  { pattern: /^1\d{10}$/, message: '手机号格式不正确' },
]

const codeRules = [{ required: true, message: '请输入验证码' }]

function onFailed(errorInfo) {
  const firstError = errorInfo?.errors?.[0]?.message
  if (firstError) showToast(firstError)
}
</script>

<template>
  <van-form @submit="onSubmit" @failed="onFailed">
    <van-cell-group inset>
      <van-field
        v-model="mobile"
        name="mobile"
        label="手机号"
        type="tel"
        maxlength="11"
        clearable
        :rules="mobileRules"
      />
      <van-field
        v-model="code"
        name="code"
        label="验证码"
        type="digit"
        maxlength="6"
        clearable
        :rules="codeRules"
      />
    </van-cell-group>
    <div class="form-actions">
      <van-button block round type="primary" native-type="submit" :loading="submitting">
        提交
      </van-button>
    </div>
  </van-form>
</template>
```

## 提交流程

- `onSubmit(values)` 中直接使用 Vant 校验后的 values。
- 提交中禁止重复点击。
- 接口失败保留当前输入，提示用户可继续修改。
- 成功后按业务跳转、返回或刷新页面。

```js
async function onSubmit(values) {
  if (submitting.value) return

  try {
    submitting.value = true
    await submitApi(values)
    showToast('提交成功')
  } catch (error) {
    showToast(error?.message || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
```

## 移动端输入体验

- 手机号用 `type="tel"`，验证码、纯数字编号用 `type="digit"`。
- 常用字段开启 `clearable`，长文本使用 `autosize`。
- 金额、编号等需要格式化时优先用 `formatter`，并明确 `format-trigger`。
- Picker、Calendar、DatetimePicker 用只读 `van-field` 触发弹层，选中后回填展示值和提交值。

## 验证码

- 发送验证码前先校验手机号字段。
- 发送中显示 loading，成功后进入倒计时。
- 倒计时期间禁用发送按钮。
- 接口失败恢复按钮状态，不启动倒计时。

## 动态和异步校验

- 异步 `validator` 返回 Promise，并捕获接口异常。
- 联动字段变化后清空下级字段，避免提交过期值。
- 不要在每次输入时发高频接口请求；唯一性校验优先放在 blur 或 submit 阶段。

## 完成检查

- 每个提交字段都有稳定 `name`。
- 键盘类型、maxlength、clearable、loading 状态符合移动端使用习惯。
- 校验失败、接口失败、重复提交、弹层联动都有闭环。
