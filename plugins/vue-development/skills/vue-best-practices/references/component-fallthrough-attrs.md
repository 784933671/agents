---
title: 组件透传属性最佳实践
impact: MEDIUM
impactDescription: 错误的 $attrs 访问方式和响应式假设会导致值为 undefined 以及 watch 永不触发
type: best-practice
tags: [vue3, attrs, fallthrough-attributes, composition-api, reactivity]
---

# 组件透传属性最佳实践

**影响级别：MEDIUM** - 只要遵循 Vue 的约定，透传属性其实很简单：带连字符的名字使用方括号语法访问，监听器键名为 camelCase 形式的 `onX`，而 `useAttrs()` 可用但不是响应式的。

## 任务清单

- 用方括号语法访问带连字符的属性名（例如 `attrs['data-testid']`）
- 用 camelCase 的 `onX` 键访问事件监听器（例如 `attrs.onClick`）
- 不要对 `useAttrs()` 返回的值使用 `watch()`，这些 watcher 在属性变化时不会触发
- 用 `onUpdated()` 处理依赖属性的副作用
- 当需要响应式观察时，把频繁观察的属性提升为 props

## 正确访问属性和监听器的键

带连字符的属性名在 JavaScript 中会保留原始大小写，因此对包含 `-` 的键使用点语法是无效的。

**BAD：**
```vue
<script setup>
import { useAttrs } from 'vue'

const attrs = useAttrs()

console.log(attrs.data-testid)  // 语法错误
console.log(attrs.dataTestid)   // 对 data-testid 而言是 undefined
console.log(attrs['on-click'])  // undefined
console.log(attrs['@click'])    // undefined
</script>
```

**GOOD：**
```vue
<script setup>
import { useAttrs } from 'vue'

const attrs = useAttrs()

console.log(attrs['data-testid'])
console.log(attrs['aria-label'])
console.log(attrs['foo-bar'])

console.log(attrs.onClick)
console.log(attrs.onCustomEvent)
console.log(attrs.onMouseEnter)
</script>
```

### 命名参考

| 父组件用法 | `attrs` 中的访问方式 |
|--------------|-------------------|
| `class="foo"` | `attrs.class` |
| `data-id="123"` | `attrs['data-id']` |
| `aria-label="..."` | `attrs['aria-label']` |
| `foo-bar="baz"` | `attrs['foo-bar']` |
| `@click="fn"` | `attrs.onClick` |
| `@custom-event="fn"` | `attrs.onCustomEvent` |
| `@update:modelValue="fn"` | `attrs['onUpdate:modelValue']` |

## `useAttrs()` 不是响应式的

`useAttrs()` 始终返回最新值，但它有意不为 watcher 追踪而设计成响应式。

**BAD：**
```vue
<script setup>
import { watch, watchEffect, useAttrs } from 'vue'

const attrs = useAttrs()

watch(
  () => attrs.someAttr,
  (newValue) => {
    console.log('Changed:', newValue) // 属性变化时永远不会执行
  }
)

watchEffect(() => {
  console.log(attrs.class) // 只在 setup 时执行，属性更新时不执行
})
</script>
```

**GOOD：**
```vue
<script setup>
import { onUpdated, useAttrs } from 'vue'

const attrs = useAttrs()

onUpdated(() => {
  console.log('Latest attrs:', attrs)
})
</script>
```

**GOOD：**
```vue
<script setup>
import { watch } from 'vue'

const props = defineProps({
  someAttr: String
})

watch(
  () => props.someAttr,
  (newValue) => {
    console.log('Changed:', newValue)
  }
)
</script>
```

## 常见模式

### 安全地检查可选属性

```vue
<script setup>
import { computed, useAttrs } from 'vue'

const attrs = useAttrs()

const hasTestId = computed(() => 'data-testid' in attrs)
const ariaLabel = computed(() => attrs['aria-label'] ?? 'Default label')
</script>
```

### 在内部逻辑之后转发监听器

```vue
<script setup>
import { useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })

const attrs = useAttrs()

function handleClick(event) {
  console.log('Internal handling first')
  attrs.onClick?.(event)
}
</script>

<template>
  <button @click="handleClick">
    <slot />
  </button>
</template>
```

## JavaScript 注意事项

`useAttrs()` 返回透传属性对象。读取单个键时先判断是否存在，再按运行时值处理。

```vue
<script setup>
import { useAttrs } from 'vue'

const attrs = useAttrs()

const testId = typeof attrs['data-testid'] === 'string' ? attrs['data-testid'] : undefined
const onClick = typeof attrs.onClick === 'function' ? attrs.onClick : undefined
</script>
```
