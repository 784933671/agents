---
title: 组件数据流最佳实践
impact: HIGH
impactDescription: 清晰的组件间数据流可以避免状态 bug、过期的 UI 以及脆弱的耦合
type: best-practice
tags: [vue3, props, emits, v-model, provide-inject, data-flow, typescript]
---

# 组件数据流最佳实践

**影响：HIGH** - 当数据流显式且清晰时，Vue 组件才能保持可靠：props 向下传递，events 向上冒泡，`v-model` 处理双向绑定，provide/inject 支持跨树依赖。模糊这些边界会导致状态过期、隐藏的耦合以及难以调试的 UI。

Vue.js 中数据流的核心原则是 **Props Down / Events Up**。这是最具可维护性的默认方式，单向数据流也具备良好的扩展性。

## 任务清单

- 把 props 当作只读输入
- 组件通信使用 props/emit；把 ref 留给命令式操作
- 当确实需要 ref 来访问命令式 API 时，用模板 ref 为其标注类型
- 通过 emit 事件来通知变更，而非直接修改父级状态
- 在现代 Vue（3.4+）中使用 `defineModel` 实现 v-model
- 在子组件中有意识地处理 v-model 修饰符
- 使用 symbol 作为 provide/inject 的 key，以避免 props 透传（约超过 3 层时）
- 把变更集中在 provider 中，或暴露显式的 action
- 在 TypeScript 项目中，优先使用基于类型的 `defineProps`、`defineEmits` 和 `InjectionKey`

## Props：单向数据向下

props 是输入。不要在子组件中修改它们。

**反面示例：**
```vue
<script setup>
const props = defineProps({ count: Number })

function increment() {
  props.count++
}
</script>
```

**正面示例：**

如果状态需要变化，就 emit 一个事件、使用 `v-model`，或创建一个本地副本。

## 优先使用 props/emit 而非组件 ref

**反面示例：**
```vue
<script setup>
import { ref } from 'vue'
import UserForm from './UserForm.vue'

const formRef = ref(null)

function submitForm() {
  if (formRef.value.isValid) {
    formRef.value.submit()
  }
}
</script>

<template>
  <UserForm ref="formRef" />
  <button @click="submitForm">Submit</button>
</template>
```

**正面示例：**
```vue
<script setup>
import UserForm from './UserForm.vue'

function handleSubmit(formData) {
  api.submit(formData)
}
</script>

<template>
  <UserForm @submit="handleSubmit" />
</template>
```

## 当确实需要命令式访问时为组件 ref 标注类型

默认优先使用 props/emits。当父组件必须调用子组件暴露的方法时，显式地为 ref 标注类型，并用 `defineExpose` 仅暴露预期的 API。

**反面示例：**
```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DialogPanel from './DialogPanel.vue'

const panelRef = ref(null)

onMounted(() => {
  panelRef.value.open()
})
</script>

<template>
  <DialogPanel ref="panelRef" />
</template>
```

**正面示例：**
```vue
<!-- DialogPanel.vue -->
<script setup lang="ts">
function open() {}

defineExpose({ open })
</script>
```

```vue
<!-- Parent.vue -->
<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'
import DialogPanel from './DialogPanel.vue'

// Vue 3.5+ with useTemplateRef
const panelRef = useTemplateRef('panelRef')

// Before Vue 3.5 with manual typing and ref
// const panelRef = ref<InstanceType<typeof DialogPanel> | null>(null)

onMounted(() => {
  panelRef.value?.open()
})
</script>

<template>
  <DialogPanel ref="panelRef" />
</template>
```

## Emits：显式的事件向上

组件事件不会冒泡。如果父级需要知道某个事件，需要显式地重新 emit。

**反面示例：**
```vue
<!-- Parent expects "saved" from grandchild, but it won't bubble -->
<Child @saved="onSaved" />
```

**正面示例：**
```vue
<!-- Child.vue -->
<script setup>
const emit = defineEmits(['saved'])

function onGrandchildSaved(payload) {
  emit('saved', payload)
}
</script>

<template>
  <Grandchild @saved="onGrandchildSaved" />
</template>
```

**事件命名：** 在模板中使用 kebab-case，在 script 中使用 camelCase：
```vue
<script setup>
const emit = defineEmits(['updateUser'])
</script>

<template>
  <ProfileForm @update-user="emit('updateUser', $event)" />
</template>
```

## `v-model`：可预期的双向绑定

默认使用 `defineModel` 实现组件绑定，并在输入时 emit 更新。仅在 Vue < 3.4 时才使用 `modelValue` + `update:modelValue` 模式。

**反面示例：**
```vue
<script setup>
const props = defineProps({ value: String })
</script>

<template>
  <input :value="props.value" @input="$emit('input', $event.target.value)" />
</template>
```

**正面示例（Vue 3.4+）：**
```vue
<script setup>
const model = defineModel({ type: String })
</script>

<template>
  <input v-model="model" />
</template>
```

**正面示例（Vue < 3.4）：**
```vue
<script setup>
const props = defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <input
    :value="props.modelValue"
    @input="emit('update:modelValue', $event.target.value)"
  />
</template>
```

如果需要在变化后立即拿到最新值，可使用 input 事件的值，或在父组件中使用 `nextTick`。

## Provide/Inject：无需 props 透传的共享上下文

对跨树状态使用 provide/inject，但要把变更集中在 provider 中，并暴露显式的 action。

**反面示例：**
```vue
// Provider.vue
provide('theme', reactive({ dark: false }))

// Consumer.vue
const theme = inject('theme')
// Mutating shared state from any depth becomes hard to track
theme.dark = true
```

**正面示例：**
```vue
// Provider.vue
const theme = reactive({ dark: false })
const toggleTheme = () => { theme.dark = !theme.dark }

provide(themeKey, readonly(theme))
provide(themeActionsKey, { toggleTheme })

// Consumer.vue
const theme = inject(themeKey)
const { toggleTheme } = inject(themeActionsKey)
```

在大型应用中使用 symbol 作为 key 以避免冲突：
```ts
export const themeKey = Symbol('theme')
export const themeActionsKey = Symbol('theme-actions')
```

## 为组件公共 API 使用 TypeScript 契约

在 TypeScript 项目中，直接用 `defineProps`、`defineEmits` 和 `InjectionKey` 为组件边界标注类型，让无效的 payload 和不匹配的注入在编译期就报错。

**反面示例：**
```vue
<script setup lang="ts">
import { inject } from 'vue'

const props = defineProps({
  userId: String
})

const emit = defineEmits(['save'])
const settings = inject('settings')

// Payload shape is not checked here
emit('save', 123)

// Key is string-based and not type-safe
settings?.theme = 'dark'
</script>
```

**正面示例：**
```vue
<script setup lang="ts">
import { inject, provide } from 'vue'
import type { InjectionKey } from 'vue'

interface Props {
  userId: string
}

interface Emits {
  save: [payload: { id: string; draft: boolean }]
}

interface Settings {
  theme: 'light' | 'dark'
}

const settingsKey: InjectionKey<Settings> = Symbol('settings')

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

provide(settingsKey, { theme: 'light' })

const settings = inject(settingsKey)
if (settings) {
  emit('save', { id: props.userId, draft: false })
}
</script>
```
