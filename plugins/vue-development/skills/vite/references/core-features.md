---
name: vite-features
description: Vite 专属的导入模式与运行时特性
---

# Vite 特性

## Glob 导入

导入匹配某个模式的多个模块：

```ts
const modules = import.meta.glob('./dir/*.ts')
// { './dir/foo.ts': () => import('./dir/foo.ts'), ... }

for (const path in modules) {
  modules[path]().then((mod) => {
    console.log(path, mod)
  })
}
```

### 同步加载

```ts
const modules = import.meta.glob('./dir/*.ts', { eager: true })
// 模块立即加载，无动态 import
```

### 具名导入

```ts
const modules = import.meta.glob('./dir/*.ts', { import: 'setup' })
// 只导入每个模块的 'setup' 导出

const defaults = import.meta.glob('./dir/*.ts', { import: 'default', eager: true })
```

### 多模式

```ts
const modules = import.meta.glob(['./dir/*.ts', './another/*.ts'])
```

### 负向模式

```ts
const modules = import.meta.glob(['./dir/*.ts', '!**/ignored.ts'])
```

### 自定义查询

```ts
const svgRaw = import.meta.glob('./icons/*.svg', { query: '?raw', import: 'default' })
const svgUrls = import.meta.glob('./icons/*.svg', { query: '?url', import: 'default' })
```

## 资源导入查询

### URL 导入

```ts
import imgUrl from './img.png'
// 返回解析后的 URL：'/src/img.png'（开发）或 '/assets/img.2d8efhg.png'（构建）
```

### 显式 URL

```ts
import workletUrl from './worklet.js?url'
```

### 原始字符串

```ts
import shaderCode from './shader.glsl?raw'
```

### 内联/不内联

```ts
import inlined from './small.png?inline'    // 强制 base64 内联
import notInlined from './large.png?no-inline'  // 强制单独文件
```

### Web Worker

```ts
import Worker from './worker.ts?worker'
const worker = new Worker()

// 或内联：
import InlineWorker from './worker.ts?worker&inline'
```

使用构造器的推荐模式：

```ts
const worker = new Worker(new URL('./worker.ts', import.meta.url), {
  type: 'module',
})
```

## 环境变量

### 内置常量

```ts
import.meta.env.MODE      // 'development' | 'production' | 自定义
import.meta.env.BASE_URL  // 来自配置的 Base URL
import.meta.env.PROD      // 生产环境为 true
import.meta.env.DEV       // 开发环境为 true
import.meta.env.SSR       // 服务端运行时为 true
```

### 自定义变量

只有 `VITE_` 前缀的变量会暴露给客户端：

```
# .env
VITE_API_URL=https://api.example.com
DB_PASSWORD=secret  # 不暴露给客户端
```

```ts
console.log(import.meta.env.VITE_API_URL) // 可用
console.log(import.meta.env.DB_PASSWORD)  // undefined
```

### 按 mode 区分的文件

```
.env                # 总是加载
.env.local          # 总是加载，gitignore
.env.[mode]         # 仅在指定 mode 下加载
.env.[mode].local   # 仅在指定 mode 下加载，gitignore
```

### TypeScript 支持

```ts
// vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

### HTML 替换

```html
<p>Running in %MODE%</p>
<script>window.API = "%VITE_API_URL%"</script>
```

## CSS Modules

任何 `.module.css` 文件都会被当作 CSS module：

```ts
import styles from './component.module.css'
element.className = styles.button
```

带 camelCase 转换：

```ts
// .my-class -> myClass（若配置了 css.modules.localsConvention）
import { myClass } from './component.module.css'
```

## JSON 导入

```ts
import pkg from './package.json'
import { version } from './package.json'  // 具名导入，支持 tree-shaking
```

## HMR API

```ts
if (import.meta.hot) {
  import.meta.hot.accept((newModule) => {
    // 处理更新
  })

  import.meta.hot.dispose((data) => {
    // 模块替换前清理
  })

  import.meta.hot.invalidate()  // 强制整页刷新
}
```

<!--
Source references:
- https://vite.dev/guide/features
- https://vite.dev/guide/env-and-mode
- https://vite.dev/guide/assets
- https://vite.dev/guide/api-hmr
-->
