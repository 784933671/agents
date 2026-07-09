---
name: testing
description: 使用 @pinia/testing 对 store 和组件进行单元测试
---

# 测试 Store

## 单元测试 Store

为每个测试创建全新的 pinia 实例：

```js
import { setActivePinia, createPinia } from 'pinia'
import { useCounterStore } from '../src/stores/counter'

describe('Counter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('increments', () => {
    const counter = useCounterStore()
    expect(counter.n).toBe(0)
    counter.increment()
    expect(counter.n).toBe(1)
  })
})
```

### 带插件

```js
import { setActivePinia, createPinia } from 'pinia'
import { createApp } from 'vue'
import { somePlugin } from '../src/stores/plugin'

const app = createApp({})

beforeEach(() => {
  const pinia = createPinia().use(somePlugin)
  app.use(pinia)
  setActivePinia(pinia)
})
```

## 测试组件

安装 `@pinia/testing`：

```bash
npm i -D @pinia/testing
```

使用 `createTestingPinia()`：

```js
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { useSomeStore } from '@/stores/myStore'

const wrapper = mount(Counter, {
  global: {
    plugins: [createTestingPinia()],
  },
})

const store = useSomeStore()

// 直接修改 state
store.name = 'new name'
store.$patch({ name: 'new name' })

// action 默认被 stub
store.someAction()
expect(store.someAction).toHaveBeenCalledTimes(1)
```

## 初始 State

为测试设置初始 state：

```js
const wrapper = mount(Counter, {
  global: {
    plugins: [
      createTestingPinia({
        initialState: {
          counter: { n: 20 }, // store 名 → 初始 state
        },
      }),
    ],
  },
})
```

## Action Stub

### 执行真实 Action

```js
createTestingPinia({ stubActions: false })
```

### 选择性 Stub

```js
// 只 stub 特定 action
createTestingPinia({
  stubActions: ['increment', 'reset'],
})

// 或使用函数
createTestingPinia({
  stubActions: (actionName, store) => {
    if (actionName.startsWith('set')) return true
    return false
  },
})
```

### Mock Action 返回值

```js
import { Mock } from 'vitest'

// 获取 store 之后
store.someAction.mockResolvedValue('mocked value')
```

## Mock Getter

测试中 getter 是可写的：

```js
const pinia = createTestingPinia()
const counter = useCounterStore(pinia)

counter.double = 3 // 覆盖计算值

// 重置为默认行为
counter.double = undefined
counter.double // 现在正常计算
```

## 自定义 Spy 函数

如果使用的不是带 globals 的 Jest/Vitest：

```js
import { vi } from 'vitest'

createTestingPinia({
  createSpy: vi.fn,
})
```

配合 Sinon：

```js
import sinon from 'sinon'

createTestingPinia({
  createSpy: sinon.spy,
})
```

## 测试中的 Pinia 插件

把插件传给 `createTestingPinia()`：

```js
import { somePlugin } from '../src/stores/plugin'

createTestingPinia({
  stubActions: false,
  plugins: [somePlugin],
})
```

**不要使用** `testingPinia.use(MyPlugin)` —— 应在选项中传入插件。

## E2E 测试

无需特殊处理 —— Pinia 正常工作。

<!--
Source references:
- https://pinia.vuejs.org/cookbook/testing.html
-->
