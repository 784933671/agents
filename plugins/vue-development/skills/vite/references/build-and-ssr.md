---
name: vite-build-ssr
description: Vite 库模式、多页应用、JavaScript API 与 SSR 指引
---

# 构建与 SSR

## 库模式

构建可分发的库：

```js
// vite.config.js
import { resolve } from 'node:path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    lib: {
      entry: resolve(import.meta.dirname, 'lib/main.js'),
      name: 'MyLib',
      fileName: 'my-lib',
    },
    rolldownOptions: {
      external: ['vue', 'react'],
      output: {
        globals: {
          vue: 'Vue',
          react: 'React',
        },
      },
    },
  },
})
```

### 多入口

```js
build: {
  lib: {
    entry: {
      'my-lib': resolve(import.meta.dirname, 'lib/main.js'),
      secondary: resolve(import.meta.dirname, 'lib/secondary.js'),
    },
    name: 'MyLib',
  },
}
```

### 输出格式

- 单入口：`es` 和 `umd`
- 多入口：`es` 和 `cjs`

### package.json 设置

```json
{
  "name": "my-lib",
  "type": "module",
  "files": ["dist"],
  "main": "./dist/my-lib.umd.cjs",
  "module": "./dist/my-lib.js",
  "exports": {
    ".": {
      "import": "./dist/my-lib.js",
      "require": "./dist/my-lib.umd.cjs"
    },
    "./style.css": "./dist/my-lib.css"
  }
}
```

## 多页应用

```js
export default defineConfig({
  build: {
    rolldownOptions: {
      input: {
        main: resolve(import.meta.dirname, 'index.html'),
        nested: resolve(import.meta.dirname, 'nested/index.html'),
      },
    },
  },
})
```

## SSR 开发

**注意：** Vite 的 SSR 支持是**底层**的，主要面向元框架作者，而非应用开发者。如果你的应用需要 SSR，请使用基于 Vite 的元框架：

- **Nuxt**（Vue）- https://nuxt.com
- **SvelteKit**（Svelte）- https://svelte.dev/docs/kit
- **SolidStart**（Solid）- https://start.solidjs.com
- **TanStack Start**（React）- https://tanstack.com/start

这些框架在 Vite 的 SSR 原语之上构建，你无需自己接线。

**需要服务器？** 考虑 [Nitro](https://nitro.build) —— 可以把它看作"服务器版 Vite"。Nitro 提供可移植的、框架无关的服务器层，支持基于文件的 API 路由、自动导入，以及数十个平台（Node.js、Deno、Bun、Cloudflare Workers、Vercel、Netlify 等）的部署预设。它与 Vite 自然集成，也是 Nuxt 服务器引擎的基础。详见 [Nitro 文档](https://nitro.build)。

## JavaScript API

### createServer

```js
import { createServer } from 'vite'

const server = await createServer({
  configFile: false,
  root: import.meta.dirname,
  server: { port: 1337 },
})

await server.listen()
server.printUrls()
```

### build

```js
import { build } from 'vite'

await build({
  root: './project',
  build: { outDir: 'dist' },
})
```

### preview

```js
import { preview } from 'vite'

const previewServer = await preview({
  preview: { port: 8080, open: true },
})
previewServer.printUrls()
```

### resolveConfig

```js
import { resolveConfig } from 'vite'

const config = await resolveConfig({}, 'build')
```

### loadEnv

```js
import { loadEnv } from 'vite'

const env = loadEnv('development', process.cwd(), '')
// 加载所有 env 变量（空前缀 = 不过滤）
```

<!--
Source references:
- https://vite.dev/guide/build
- https://vite.dev/guide/api-javascript
- https://nitro.build
-->
