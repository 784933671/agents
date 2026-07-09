---
title: 指令最佳实践
impact: MEDIUM
impactDescription: 自定义指令功能强大但容易误用；遵循这些模式可避免内存泄漏、无效用法和不清晰的抽象
type: best-practice
tags: [vue3, directives, custom-directives, composition, javascript]
---

# 指令最佳实践

**影响级别：MEDIUM** - 指令用于低层级 DOM 访问。请谨慎使用，保持副作用安全，并在需要带状态或可复用的 UI 行为时优先选择组件或 composable。

## 任务清单

- 仅在需要直接访问 DOM 时才使用指令
- 不要修改指令的参数或 binding 对象
- 在 `unmounted` 中清理定时器、监听器和 observer
- 在 `<script setup>` 中以 `v-` 前缀注册指令
- 在 JavaScript 项目中，为指令值标注类型，并扩展模板指令类型
- 对于复杂行为，优先使用组件或 composable

## 把指令参数当作只读对待

指令的 binding 并不是响应式存储。不要向其写入。

```js
const vFocus = {
  mounted(el, binding) {
    // binding.value 是只读的
    el.focus()
  }
}
```

## 避免在组件上使用指令

指令作用于 DOM 元素。当用在组件上时，它们会附加到根元素上，一旦根元素发生变化就可能失效。

**BAD：**
```vue
<MyInput v-focus />
```

**GOOD：**
```vue
<!-- MyInput.vue -->
<script setup>
const vFocus = (el) => el.focus()
</script>

<template>
  <input v-focus />
</template>
```

## 在 `unmounted` 中清理副作用

任何定时器、监听器或 observer 都必须被移除，以避免内存泄漏。

```js
const vResize = {
  mounted(el) {
    const observer = new ResizeObserver(() => {})
    observer.observe(el)
    el._observer = observer
  },
  unmounted(el) {
    el._observer?.disconnect()
  }
}
```

## 单钩子指令优先使用函数简写形式

如果只需要 `mounted`/`updated`，使用函数形式即可。

```js
const vAutofocus = (el) => el.focus()
```

## 使用 `v-` 前缀并在 Script Setup 中注册

```vue
<script setup>
const vFocus = (el) => el.focus()
</script>

<template>
  <input v-focus />
</template>
```

## 让自定义指令契约清晰

用运行时校验和清晰命名约束 `binding.value`，避免指令接收错误值时静默失败。

**BAD：**
```js
export const vHighlight = {
  mounted(el, binding) {
    el.style.backgroundColor = binding.value
  }
}
```

**GOOD：**
```js
export const vHighlight = {
  mounted(el, binding) {
    if (typeof binding.value !== 'string') return
    el.style.backgroundColor = binding.value
  }
}
```

## 用 `getSSRProps` 处理 SSR

`mounted` 和 `updated` 等指令钩子在 SSR 期间不会执行。如果某个指令会设置影响渲染 HTML 的属性/类，请通过 `getSSRProps` 提供 SSR 等价实现，以避免 hydration 不一致。

**BAD：**
```js
const vTooltip = {
  mounted(el, binding) {
    el.setAttribute('data-tooltip', binding.value)
    el.classList.add('has-tooltip')
  }
}
```

**GOOD：**
```js
const vTooltip = {
  mounted(el, binding) {
    el.setAttribute('data-tooltip', binding.value)
    el.classList.add('has-tooltip')
  },
  getSSRProps(binding) {
    return {
      'data-tooltip': binding.value,
      class: 'has-tooltip'
    }
  }
}
```

## 尽可能优先使用声明式模板

如果标准的属性或绑定就能满足需求，就用它，而不是使用指令。

## 在指令和组件之间做取舍

DOM 层面的行为用指令。当行为涉及结构、状态或渲染时，使用组件。
