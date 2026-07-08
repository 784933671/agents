---
title: Vue 插件最佳实践
impact: MEDIUM
impactDescription: 错误的插件结构或 injection key 策略会导致安装失败、键名冲突以及不安全的 API
type: best-practice
tags: [vue3, plugins, provide-inject, typescript, dependency-injection]
---

# Vue 插件最佳实践

**影响等级：MEDIUM** - Vue 插件应遵循 `app.use()` 契约，显式地暴露能力，并使用防冲突的 injection key。这样可以让插件在大型应用中保持安装过程可预测、可组合。

## 任务清单

- 以带有 `install()` 的对象或 install 函数的形式导出插件
- 在 `install()` 中使用 `app` 实例注册 component/directive/provide
- 使用 `Plugin` 类型（必要时配合 options 元组类型）为插件 API 提供类型
- 在插件中为 `provide/inject` 使用 symbol key（优先使用 `InjectionKey<T>`）
- 为必需的注入提供一个小巧且带类型的 composable 包装，以便快速失败

## 为 `app.use()` 设计插件结构

Vue 插件必须是以下两种形式之一：
- 带有 `install(app, options?)` 的对象
- 具有相同签名的函数

**反面示例：**
```ts
const notAPlugin = {
  doSomething() {}
}

app.use(notAPlugin)
```

**正面示例：**
```ts
import type { App } from 'vue'

interface PluginOptions {
  prefix?: string
  debug?: boolean
}

const myPlugin = {
  install(app: App, options: PluginOptions = {}) {
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
```ts
import type { App } from 'vue'

function simplePlugin(app: App, options?: { message: string }) {
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
```ts
const uselessPlugin = {
  install(app, options) {
    const service = createService(options)
  }
}
```

**正面示例：**
```ts
const usefulPlugin = {
  install(app, options) {
    const service = createService(options)
    app.provide(serviceKey, service)
  }
}
```

## 为插件契约提供类型

使用 Vue 的 `Plugin` 类型，让 install 签名和 options 保持类型安全。

```ts
import type { App, Plugin } from 'vue'

interface MyOptions {
  apiKey: string
}

const myPlugin: Plugin<[MyOptions]> = {
  install(app: App, options: MyOptions) {
    app.provide(apiKeyKey, options.apiKey)
  }
}
```

## 在插件中使用 Symbol Injection Key

字符串 key 可能会冲突（如 `'http'`、`'config'`、`'i18n'`）。使用 `InjectionKey<T>` 包装的 symbol key，可以让注入既唯一又带类型。

**反面示例：**
```ts
export default {
  install(app) {
    app.provide('http', axios)
    app.provide('config', appConfig)
  }
}
```

**正面示例：**
```ts
import type { InjectionKey } from 'vue'
import type { AxiosInstance } from 'axios'

interface AppConfig {
  apiUrl: string
  timeout: number
}

export const httpKey: InjectionKey<AxiosInstance> = Symbol('http')
export const configKey: InjectionKey<AppConfig> = Symbol('appConfig')

export default {
  install(app) {
    app.provide(httpKey, axios)
    app.provide(configKey, { apiUrl: '/api', timeout: 5000 })
  }
}
```

## 提供必需注入的辅助方法

将必需的注入封装在 composable 中，并在缺少时抛出清晰的 setup 错误。

```ts
import { inject } from 'vue'
import { authKey, type AuthService } from '@/injection-keys'

export function useAuth(): AuthService {
  const auth = inject(authKey)
  if (!auth) {
    throw new Error('Auth plugin not installed. Did you forget app.use(authPlugin)?')
  }
  return auth
}
```
