---
title: 单文件组件结构、样式与模板模式
impact: MEDIUM
impactDescription: 一致的 SFC 结构和样式选择能提升可维护性、工具链支持以及渲染性能
type: best-practice
tags: [vue3, sfc, scoped-css, styles, build-tools, performance, template, v-html, v-for, computed, v-if, v-show]
---

# 单文件组件结构、样式与模板模式

**影响：MEDIUM** - 使用结构一致、样式高性能的 SFC，可以让组件更易维护，并避免不必要的渲染开销。

## 任务清单

- 使用 `.vue` SFC，而不是为组件单独拆分 `.js`/`.js` 与 `.css` 文件
- 默认将 template、script 和 styles 共置于同一个 SFC 中
- 在模板和文件名中为组件名使用 PascalCase
- 优先使用组件作用域样式
- 在 scoped CSS 中优先使用类选择器（而非元素选择器）以提升性能
- 在 Vue 3.5+ 中使用 `useTemplateRef()` 访问 DOM / 组件 ref
- 在 `:style` 绑定中使用 camelCase 键名，以保持一致并获得 IDE 支持
- 正确使用 `v-for` 和 `v-if`
- 永远不要对不可信/用户提供的内容使用 `v-html`
- 根据切换频率和初始渲染成本选择 `v-if` 还是 `v-show`

## 共置 template、script 和 styles

**反面示例：**
```
components/
├── UserCard.vue
├── UserCard.js
└── UserCard.css
```

**正面示例：**
```vue
<!-- components/UserCard.vue -->
<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: { type: Object, required: true }
})

const displayName = computed(() =>
  `${props.user.firstName} ${props.user.lastName}`
)
</script>

<template>
  <div class="user-card">
    <h3 class="name">{{ displayName }}</h3>
  </div>
</template>

<style scoped>
.user-card {
  padding: 1rem;
}

.name {
  margin: 0;
}
</style>
```

## 为组件名使用 PascalCase

**反面示例：**
```vue
<script setup>
import userProfile from './user-profile.vue'
</script>

<template>
  <user-profile :user="currentUser" />
</template>
```

**正面示例：**
```vue
<script setup>
import UserProfile from './UserProfile.vue'
</script>

<template>
  <UserProfile :user="currentUser" />
</template>
```

## SFC 中 `<style>` 块的最佳实践

### 优先使用组件作用域样式

- 属于某个组件的样式使用 `<style scoped>`。
- 将**全局 CSS** 放在专用文件中（例如 `src/assets/main.css`），用于 reset、排版、token 等。
- 谨慎使用 `:deep()`（仅限边缘场景）。

**反面示例：**

```vue
<style>
/* ❌ leaks everywhere */
button { border-radius: 999px; }
</style>
```

**正面示例：**

```vue
<style scoped>
.button { border-radius: 999px; }
</style>
```

**正面示例：**

```css
/* src/assets/main.css */
/* ✅ resets, tokens, typography, app-wide rules */
:root { --radius: 999px; }
```

### 在 scoped CSS 中使用类选择器

**反面示例：**
```vue
<template>
  <article>
    <h1>{{ title }}</h1>
    <p>{{ subtitle }}</p>
  </article>
</template>

<style scoped>
article { max-width: 800px; }
h1 { font-size: 2rem; }
p { line-height: 1.6; }
</style>
```

**正面示例：**
```vue
<template>
  <article class="article">
    <h1 class="article-title">{{ title }}</h1>
    <p class="article-subtitle">{{ subtitle }}</p>
  </article>
</template>

<style scoped>
.article { max-width: 800px; }
.article-title { font-size: 2rem; }
.article-subtitle { line-height: 1.6; }
</style>
```

## 使用 `useTemplateRef()` 访问 DOM / 组件 ref

对于 Vue 3.5+：使用 `useTemplateRef()` 访问模板 ref。

```vue
<script setup>
import { onMounted, useTemplateRef } from 'vue'

const inputRef = useTemplateRef<HTMLInputElement>('input')

onMounted(() => {
  inputRef.value?.focus()
})
</script>

<template>
  <input ref="input" />
</template>
```

## 在 `:style` 绑定中使用 camelCase

**反面示例：**
```vue
<template>
  <div :style="{ 'font-size': fontSize + 'px', 'background-color': bg }">
    Content
  </div>
</template>
```

**正面示例：**
```vue
<template>
  <div :style="{ fontSize: fontSize + 'px', backgroundColor: bg }">
    Content
  </div>
</template>
```

## 正确使用 `v-for` 和 `v-if`

### 始终提供稳定的 `:key`

- 优先使用原始值键（`string | number`）。
- 避免使用对象作为键。

**正面示例：**

```vue
<li v-for="item in items" :key="item.id">
  <input v-model="item.text" />
</li>
```

### 避免在同一元素上同时使用 `v-if` 和 `v-for`

这会导致意图不清晰并产生不必要的开销。
([参考](https://vuejs.org/guide/essentials/list.html#v-for-with-v-if))

**用于过滤列表项**
**反面示例：**

```vue
<li v-for="user in users" v-if="user.active" :key="user.id">
  {{ user.name }}
</li>
```

**正面示例：**

```vue
<script setup>
import { computed } from 'vue'

const activeUsers = computed(() => users.value.filter(u => u.active))
</script>

<template>
  <li v-for="user in activeUsers" :key="user.id">
    {{ user.name }}
  </li>
</template>
```

**用于条件显示/隐藏整个列表**
**正面示例：**

```vue
<ul v-if="shouldShowUsers">
  <li v-for="user in users" :key="user.id">
    {{ user.name }}
  </li>
</ul>
```

## 永远不要用 `v-html` 渲染不可信的 HTML

**反面示例：**
```vue
<template>
  <!-- DANGEROUS: untrusted input can inject scripts -->
  <article v-html="userProvidedContent"></article>
</template>
```

**正面示例：**
```vue
<script setup>
import { computed } from 'vue'
import DOMPurify from 'dompurify'

const props = defineProps({
  trustedHtml: {
    type: String,
    default: '',
  },
  plainText: {
    type: String,
    required: true,
  },
})

const safeHtml = computed(() => DOMPurify.sanitize(props.trustedHtml ?? ''))
</script>

<template>
  <!-- Preferred: escaped interpolation -->
  <p>{{ props.plainText }}</p>

  <!-- Only for trusted/sanitized HTML -->
  <article v-html="safeHtml"></article>
</template>
```

## 根据切换行为选择 `v-if` 还是 `v-show`

**反面示例：**
```vue
<template>
  <!-- Frequent toggles with v-if cause repeated mount/unmount -->
  <ComplexPanel v-if="isPanelOpen" />

  <!-- Rarely shown content with v-show pays initial render cost -->
  <AdminPanel v-show="isAdmin" />
</template>
```

**正面示例：**
```vue
<template>
  <!-- Frequent toggles: keep in DOM, toggle display -->
  <ComplexPanel v-show="isPanelOpen" />

  <!-- Rare condition: lazy render only when true -->
  <AdminPanel v-if="isAdmin" />
</template>
```
