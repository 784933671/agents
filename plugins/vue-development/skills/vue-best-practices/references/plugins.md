---
title: Vue 插件最佳实践
impact: MEDIUM
impactDescription: 错误的插件结构或 injection key 策略会导致安装失败、键名冲突以及不安全的 API
type: best-practice
tags: [vue3, plugins, provide-inject, javascript, dependency-injection]
---

# Vue 插件最佳实践

**影响等级：MEDIUM** - Vue 插件应遵循 `app.use()` 契约，显式地暴露能力，并使用防冲突的 injection key。这样可以让插件在大型应用中保持安装过程可预测、可组合。

## 任务清单

- 以带有 `install()` 的对象或 install 函数的形式导出插件
- 在 `install()` 中使用 `app` 实例注册 component/directive/provide
- 使用稳定的 install 参数约定说明插件 API
- 在插件中为 `provide/inject` 使用 symbol key
- 为必需的注入提供一个小巧的 composable 包装，以便快速失败

## 为 `app.use()` 设计插件结构

Vue 插件必须是以下两种形式之一：
- 带有 `install(app, options?)` 的对象
- 具有相同签名的函数

**反面示例：**
```js
const notAPlugin = {
  doSomething() {}
}

app.use(notAPlugin)
```

**正面示例：**
```js
const myPlugin = {
  install(app, options = {}) {
    const { prefix = 'my', debug = false } = options

    if (debug) {
      console.log('Installing myPlugin with prefix:', prefix)
    }

    app.provide('myPlugin', { prefix })
  }
}

app.use(myPlugin, { prefix: 'custom', debug: true })
```

**正面示例：**
```js
function simplePlugin(app, options = {}) {
  app.config.globalProperties.$greet = () => options?.message ?? 'Hello!'
}

app.use(simplePlugin, { message: 'Welcome!' })
```

## 在 `install()` 中显式注册能力

在 `install()` 内部，通过 Vue 应用 API 来串联行为：
- 使用 `app.component()` 注册全局 component
- 使用 `app.directive()` 注册全局 directive
- 使用 `app.provide()` 注册可注入的服务与配置
- 使用 `app.config.globalProperties` 注册可选的全局辅助方法（谨慎使用）

**反面示例：**
```js
const uselessPlugin = {
  install(app, options) {
    const service = createService(options)
  }
}
```

**正面示例：**
```js
const usefulPlugin = {
  install(app, options) {
    const service = createService(options)
    app.provide(serviceKey, service)
  }
}
```

## 为插件契约提供清晰约定

在 install 入口校验必需参数，避免插件以半初始化状态运行。

```js
const myPlugin = {
  install(app, options = {}) {
    if (!options.apiKey) {
      throw new Error('apiKey is required')
    }
    app.provide(apiKeyKey, options.apiKey)
  }
}
```

## 在插件中使用 Symbol Injection Key

字符串 key 可能会冲突（如 `'http'`、`'config'`、`'i18n'`）。使用 symbol key 可以让注入 key 保持唯一。

**反面示例：**
```js
export default {
  install(app) {
    app.provide('http', axios)
    app.provide('config', appConfig)
  }
}
```

**正面示例：**
```js
export const httpKey = Symbol('http')
export const configKey = Symbol('appConfig')

export default {
  install(app) {
    app.provide(httpKey, axios)
    app.provide(configKey, { apiUrl: '/api', timeout: 5000 })
  }
}
```

## 提供必需注入的辅助方法

将必需的注入封装在 composable 中，并在缺少时抛出清晰的 setup 错误。

```js
import { inject } from 'vue'
import { authKey } from '@/injection-keys'

export function useAuth() {
  const auth = inject(authKey)
  if (!auth) {
    throw new Error('Auth plugin not installed. Did you forget app.use(authPlugin)?')
  }
  return auth
}
```
