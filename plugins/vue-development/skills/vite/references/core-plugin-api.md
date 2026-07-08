---
name: vite-plugin-api
description: 使用 Vite 专属钩子编写 Vite 插件
---

# Vite 插件 API

Vite 插件扩展了 Rolldown 的插件接口，增加了 Vite 专属钩子。

## 基础结构

```ts
function myPlugin(): Plugin {
  return {
    name: 'my-plugin',
    // 钩子...
  }
}
```

## Vite 专属钩子

### config

在解析前修改配置：

```ts
const plugin = () => ({
  name: 'add-alias',
  config: () => ({
    resolve: {
      alias: { foo: 'bar' },
    },
  }),
})
```

### configResolved

访问最终解析的配置：

```ts
const plugin = () => {
  let config: ResolvedConfig
  return {
    name: 'read-config',
    configResolved(resolvedConfig) {
      config = resolvedConfig
    },
    transform(code, id) {
      if (config.command === 'serve') { /* 开发 */ }
    },
  }
}
```

### configureServer

为开发服务器添加自定义中间件：

```ts
const plugin = () => ({
  name: 'custom-middleware',
  configureServer(server) {
    server.middlewares.use((req, res, next) => {
      // 处理请求
      next()
    })
  },
})
```

返回函数会在内部中间件**之后**运行：

```ts
configureServer(server) {
  return () => {
    server.middlewares.use((req, res, next) => {
      // 在 Vite 的中间件之后运行
    })
  }
}
```

### transformIndexHtml

转换 HTML 入口文件：

```ts
const plugin = () => ({
  name: 'html-transform',
  transformIndexHtml(html) {
    return html.replace(/<title>(.*?)<\/title>/, '<title>New Title</title>')
  },
})
```

注入标签：

```ts
transformIndexHtml() {
  return [
    { tag: 'script', attrs: { src: '/inject.js' }, injectTo: 'body' },
  ]
}
```

### handleHotUpdate

自定义 HMR 处理：

```ts
handleHotUpdate({ server, modules, timestamp }) {
  server.ws.send({ type: 'custom', event: 'special-update', data: {} })
  return [] // 空数组 = 跳过默认 HMR
}
```

## 虚拟模块

无需磁盘文件即可提供虚拟内容：

```ts
const plugin = () => {
  const virtualModuleId = 'virtual:my-module'
  const resolvedId = '\0' + virtualModuleId

  return {
    name: 'virtual-module',
    resolveId(id) {
      if (id === virtualModuleId) return resolvedId
    },
    load(id) {
      if (id === resolvedId) {
        return `export const msg = "from virtual module"`
      }
    },
  }
}
```

用法：

```ts
import { msg } from 'virtual:my-module'
```

约定：面向用户的路径加 `virtual:` 前缀，解析后的 id 加 `\0` 前缀。

## 插件顺序

用 `enforce` 控制执行顺序：

```ts
{
  name: 'pre-plugin',
  enforce: 'pre',  // 在核心插件之前运行
}

{
  name: 'post-plugin',
  enforce: 'post', // 在构建插件之后运行
}
```

顺序：Alias → `enforce: 'pre'` → 核心 → 用户（无 enforce）→ 构建 → `enforce: 'post'` → 构建后

## 条件应用

```ts
{
  name: 'build-only',
  apply: 'build',  // 或 'serve'
}

// 函数形式：
{
  apply(config, { command }) {
    return command === 'build' && !config.build.ssr
  }
}
```

## 通用钩子（来自 Rolldown）

这些在开发和构建中都能工作：

- `resolveId(id, importer)` - 解析导入路径
- `load(id)` - 加载模块内容
- `transform(code, id)` - 转换模块代码

```ts
transform(code, id) {
  if (id.endsWith('.custom')) {
    return { code: compile(code), map: null }
  }
}
```

## 客户端-服务端通信

服务端到客户端：

```ts
configureServer(server) {
  server.ws.send('my:event', { msg: 'hello' })
}
```

客户端：

```ts
if (import.meta.hot) {
  import.meta.hot.on('my:event', (data) => {
    console.log(data.msg)
  })
}
```

客户端到服务端：

```ts
// 客户端
import.meta.hot.send('my:from-client', { msg: 'Hey!' })

// 服务端
server.ws.on('my:from-client', (data, client) => {
  client.send('my:ack', { msg: 'Got it!' })
})
```

<!--
Source references:
- https://vite.dev/guide/api-plugin
-->
