---
name: vite-config
description: 使用 vite.config.js 的 Vite 配置模式
---

# Vite 配置

## 基础设置

```js
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  // 配置选项
})
```

Vite 会自动从项目根目录解析 `vite.config.js`。无论 `package.json` 的 `type` 是什么，都支持 ES modules 语法。

## 条件配置

导出一个函数以访问 command 和 mode：

```js
export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
  if (command === 'serve') {
    return { /* 开发配置 */ }
  } else {
    return { /* 构建配置 */ }
  }
})
```

- `command`：开发时为 `'serve'`，生产构建为 `'build'`
- `mode`：`'development'` 或 `'production'`（或通过 `--mode` 自定义）

## 异步配置

```js
export default defineConfig(async ({ command, mode }) => {
  const data = await fetchSomething()
  return { /* 配置 */ }
})
```

## 在配置中使用环境变量

`.env` 文件在配置解析**之后**加载。使用 `loadEnv` 在配置中访问它们：

```js
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  // 从 cwd 加载 env 文件，包含所有变量（空前缀）
  const env = loadEnv(mode, process.cwd(), '')

  return {
    define: {
      __APP_ENV__: JSON.stringify(env.APP_ENV),
    },
    server: {
      port: env.APP_PORT ? Number(env.APP_PORT) : 5173,
    },
  }
})
```

## 关键配置项

### resolve.alias

```js
export default defineConfig({
  resolve: {
    alias: {
      '@': '/src',
      '~': '/src',
    },
  },
})
```

### define（全局常量）

```js
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __API_URL__: 'window.__backend_api_url',
  },
})
```

值必须可被 JSON 序列化或是单个标识符。非字符串值会自动用 `JSON.stringify` 包装。

### plugins

```js
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})
```

plugins 数组会被扁平化；假值会被忽略。

### server.proxy

```js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

### build.target

默认：Baseline Widely Available 浏览器。自定义：

```js
export default defineConfig({
  build: {
    target: 'esnext', // 或 'es2020'、['chrome90', 'firefox88']
  },
})
```

## JavaScript 智能提示

对于纯 JS 配置文件：

```js
/** @type {import('vite').UserConfig} */
export default {
  // ...
}
```

<!--
Source references:
- https://vite.dev/config/
- https://vite.dev/guide/
-->
