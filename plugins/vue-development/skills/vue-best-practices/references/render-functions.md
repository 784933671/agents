---
title: 渲染函数模式与性能
impact: MEDIUM
impactDescription: 渲染函数需要针对列表、事件、v-model 和性能采用明确的模式，才能保持正确性与可维护性
type: best-practice
tags: [vue3, render-function, h, v-model, directives, performance, jsx]
---

# 渲染函数模式与性能

**影响级别：MEDIUM** - 渲染函数功能强大，但会放弃模板编译器的优化。请有意识地使用它们，并应用以下关键模式，以保证输出正确且高性能。

## 任务清单

- 优先使用模板；仅当模板无法表达逻辑时才使用渲染函数
- 用 `h()`/JSX 渲染列表时始终添加稳定的 key
- 用 `withModifiers` / `withKeys` 处理事件修饰符
- 通过 `modelValue` + `onUpdate:modelValue` 实现 `v-model`
- 用 `withDirectives` 应用自定义指令
- 对无状态的展示型 UI 使用函数式组件

## 优先使用模板而非渲染函数

**BAD：**
```vue
<script setup>
import { h, ref } from 'vue'

const count = ref(0)
const render = () => h('div', `Count: ${count.value}`)
</script>
```

**GOOD：**
```vue
<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div>Count: {{ count }}</div>
</template>
```

## 渲染列表时始终添加 key

**BAD：**
```javascript
import { h, ref } from 'vue'

export default {
  setup() {
    const items = ref([{ id: 1, name: 'Apple' }])

    return () => h('ul',
      items.value.map(item => h('li', item.name))
    )
  }
}
```

**GOOD：**
```javascript
import { h, ref } from 'vue'

export default {
  setup() {
    const items = ref([{ id: 1, name: 'Apple' }])

    return () => h('ul',
      items.value.map(item => h('li', { key: item.id }, item.name))
    )
  }
}
```

## 用 `withModifiers` / `withKeys` 处理事件修饰符

**BAD：**
```javascript
import { h } from 'vue'

export default {
  setup() {
    const handleClick = (e) => {
      e.stopPropagation()
      e.preventDefault()
    }

    return () => h('button', { onClick: handleClick }, 'Click')
  }
}
```

**GOOD：**
```javascript
import { h, withModifiers, withKeys } from 'vue'

export default {
  setup() {
    const handleClick = () => {}
    const handleEnter = () => {}

    return () => h('div', [
      h('button', {
        onClick: withModifiers(handleClick, ['stop', 'prevent'])
      }, 'Click'),
      h('input', {
        onKeyup: withKeys(handleEnter, ['enter'])
      })
    ])
  }
}
```

## 显式实现 `v-model`

**BAD：**
```javascript
import { h, ref } from 'vue'
import CustomInput from './CustomInput.vue'

export default {
  setup() {
    const text = ref('')
    return () => h(CustomInput, { modelValue: text.value })
  }
}
```

**GOOD：**
```javascript
import { h, ref } from 'vue'
import CustomInput from './CustomInput.vue'

export default {
  setup() {
    const text = ref('')
    return () => h(CustomInput, {
      modelValue: text.value,
      'onUpdate:modelValue': (value) => { text.value = value }
    })
  }
}
```

## 用 `withDirectives` 应用自定义指令

**BAD：**
```javascript
import { h } from 'vue'

const vFocus = { mounted: (el) => el.focus() }

export default {
  setup() {
    return () => h('input', { 'v-focus': true })
  }
}
```

**GOOD：**
```javascript
import { h, withDirectives } from 'vue'

const vFocus = { mounted: (el) => el.focus() }

export default {
  setup() {
    return () => withDirectives(h('input'), [[vFocus]])
  }
}
```

## 无状态 UI 优先使用函数式组件

**BAD：**
```javascript
import { h } from 'vue'

export default {
  setup() {
    return () => h('span', { class: 'badge' }, 'New')
  }
}
```

**GOOD：**
```javascript
import { h } from 'vue'

function Badge(props, { slots }) {
  return h('span', { class: 'badge' }, slots.default?.())
}

Badge.props = ['variant']

export default Badge
```
