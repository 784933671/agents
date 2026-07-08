---
title: 为非进入/离开效果使用基于类的动画
impact: LOW
impactDescription: 对于保留在 DOM 中的元素，基于类的动画更简单、性能更好
type: best-practice
tags: [vue3, animation, css, class-binding, state]
---

# 为非进入/离开效果使用基于类的动画

**影响级别：LOW** - 对于并非正在进入或离开 DOM 的元素上的动画，应使用由 Vue 响应式状态触发的 CSS 基于类的动画。它比 `<Transition>` 更简单，也更适合用于抖动、脉冲或高亮等反馈类动画。

## 任务清单

- 对保留在 DOM 中的元素使用基于类的动画
- 只在进入/离开动画时使用 `<Transition>`
- 将 CSS 动画与 Vue 的类绑定（`:class`）结合使用
- 考虑用 `setTimeout` 自动移除动画类

**何时使用基于类的动画：**
- 用户反馈（出错时抖动、成功时脉冲）
- 引起注意的效果（高亮变化）
- 需要超出 CSS transition 能力的 hover/focus 状态
- 元素保持挂载状态的任何动画

**何时使用 Transition 组件：**
- 进入/离开 DOM 的元素（v-if/v-show）
- 路由切换
- 列表项的增删

## 基本模式

```vue
<template>
  <div :class="{ shake: showError }">
    <button @click="submitForm">Submit</button>
    <span v-if="showError">This feature is disabled!</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const showError = ref(false)

function submitForm() {
  if (!isValid()) {
    // 触发抖动动画
    showError.value = true

    // 动画结束后自动移除类
    setTimeout(() => {
      showError.value = false
    }, 820)  // 与动画时长匹配
  }
}
</script>

<style>
.shake {
  animation: shake 0.82s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
  transform: translate3d(0, 0, 0);  /* 启用 GPU 加速 */
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}
</style>
```

## 常见动画模式

### 成功时脉冲

```vue
<template>
  <button
    @click="save"
    :class="{ pulse: saved }"
  >
    {{ saved ? 'Saved!' : 'Save' }}
  </button>
</template>

<script setup>
import { ref } from 'vue'

const saved = ref(false)

async function save() {
  await saveData()
  saved.value = true
  setTimeout(() => saved.value = false, 1000)
}
</script>

<style>
.pulse {
  animation: pulse 0.5s ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
</style>
```

### 变化时高亮

```vue
<template>
  <div
    :class="{ highlight: justUpdated }"
  >
    Value: {{ value }}
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const value = ref(0)
const justUpdated = ref(false)

watch(value, () => {
  justUpdated.value = true
  setTimeout(() => justUpdated.value = false, 1000)
})
</script>

<style>
.highlight {
  animation: highlight 1s ease-out;
}

@keyframes highlight {
  0% { background-color: yellow; }
  100% { background-color: transparent; }
}
</style>
```

### 弹跳引起注意

```vue
<template>
  <div
    :class="{ bounce: needsAttention }"
    @animationend="needsAttention = false"
  >
    <BellIcon />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const needsAttention = ref(false)

function notifyUser() {
  needsAttention.value = true
  // 不需要 setTimeout —— 使用 animationend 事件
}
</script>

<style>
.bounce {
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
</style>
```

## 使用 animationend 事件

相比于 `setTimeout`，使用 `animationend` 事件能让代码更干净：

```vue
<template>
  <div
    :class="{ animate: isAnimating }"
    @animationend="isAnimating = false"
  >
    Content
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isAnimating = ref(false)

function triggerAnimation() {
  isAnimating.value = true
  // 动画结束时类会被自动移除
}
</script>
```

## 可复用动画的 Composable

```javascript
// composables/useAnimation.js
import { ref } from 'vue'

export function useAnimation(duration = 500) {
  const isAnimating = ref(false)

  function trigger() {
    isAnimating.value = true
    setTimeout(() => {
      isAnimating.value = false
    }, duration)
  }

  return {
    isAnimating,
    trigger
  }
}
```

```vue
<script setup>
import { useAnimation } from '@/composables/useAnimation'

const shake = useAnimation(820)
const pulse = useAnimation(500)
</script>

<template>
  <button
    :class="{ shake: shake.isAnimating.value }"
    @click="shake.trigger()"
  >
    Shake me
  </button>

  <button
    :class="{ pulse: pulse.isAnimating.value }"
    @click="pulse.trigger()"
  >
    Pulse me
  </button>
</template>
```
