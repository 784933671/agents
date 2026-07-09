---
name: vite-environment-api
description: Vite 6+ 用于多运行时环境的 Environment API
---

# Environment API（Vite 6+）

Environment API 将多个运行时环境形式化，超越传统的 client/SSR 划分。

## 概念

Vite 6 之前：两个隐式环境（`client` 和 `ssr`）。

Vite 6+：按需配置任意数量的环境（浏览器、node 服务器、边缘服务器等）。

## 基础配置

对于 SPA/MPA，无需改动——选项会应用到隐式的 `client` 环境：

```js
export default defineConfig({
  build: { sourcemap: false },
  optimizeDeps: { include: ['lib'] },
})
```

## 多环境

```js
export default defineConfig({
  build: { sourcemap: false },  // 被所有环境继承
  optimizeDeps: { include: ['lib'] },  // 仅 client
  environments: {
    // SSR 环境
    server: {},
    // 边缘运行时环境
    edge: {
      resolve: { noExternal: true },
    },
  },
})
```

环境继承顶层配置。某些选项（如 `optimizeDeps`）默认只应用于 `client`。

## 环境选项

环境选项按普通对象传入，根据运行环境设置 `define`、`resolve`、`optimizeDeps`、`consumer`、`dev` 和 `build` 等字段。

## 自定义环境实例

运行时提供方可定义自定义环境：

```js
import { customEnvironment } from 'vite-environment-provider'

export default defineConfig({
  environments: {
    ssr: customEnvironment({
      build: { outDir: '/dist/ssr' },
    }),
  },
})
```

示例：Cloudflare 的 Vite 插件在开发时于 `workerd` 运行时中运行代码。

## 向后兼容

- `server.moduleGraph` 返回混合的 client/SSR 视图
- `ssrLoadModule` 仍然可用
- 现有 SSR 应用无需改动

## 何时使用

- **终端用户**：通常无需配置——框架会处理
- **插件作者**：用于环境感知的转换
- **框架作者**：为其运行时需求创建自定义环境

## 插件中的环境访问

插件可在钩子中访问环境：

```js
{
  name: 'env-aware',
  transform(code, id, options) {
    if (options?.ssr) {
      // SSR 专属转换
    }
  },
}
```

<!--
Source references:
- https://vite.dev/guide/api-environment
- https://vite.dev/blog/announcing-vite6
-->
