---
name: vite-build
description: 掌握 Vite 构建与优化的实用方法：配置、开发体验、分包策略、产物分析与部署优化。适用于配置 Vue 项目、排查构建问题或优化打包体积与启动速度。
---

# Vite 构建与优化

Vite 是 Vue 官方推荐的构建工具。本技能聚焦实战配置、性能优化与常见问题，而非完整文档搬运。

## 何时使用本技能

- 新建 Vue + Vite 项目，配置构建
- 排查构建错误、HMR 失效或产物异常
- 优化打包体积、首屏加载或冷启动速度
- 部署前的构建调优

## 开发服务器（dev）

### 基础配置

```js
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: { '@': '/src' },
  },
})
```

### 路径别名

配合 `tsconfig.json` 的 `paths`，让 IDE 与构建一致：

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  }
}
```

```js
// vite.config.ts
resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } }
```

### HMR 边界

HMR 失效常见原因：
- 改的文件不在组件依赖链上
- 状态在模块顶层（重载会丢）
- CSS 用了非 `<style>` 方式引入

`<script setup>` + `<style scoped>` 的 SFC 开箱即用 HMR。

## 构建优化（build）

### 分包策略

```js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vue')) return 'vue-vendor'
            if (id.includes('pinia')) return 'pinia-vendor'
            return 'vendor'
          }
        },
      },
    },
  },
})
```

原则：把不常变的依赖单独分包，利用浏览器长期缓存。

### 路由级懒加载

```ts
const routes = [
  { path: '/', component: () => import('./views/Home.vue') },
  { path: '/about', component: () => import('./views/About.vue') },
]
```

Vite 自动为动态 import 创建独立 chunk，首屏只加载所需。

### 资源内联阈值

```js
build: {
  assetsInlineLimit: 4096,  // 小于 4kb 的资源内联为 base64
}
```

小图内联减少请求数，大图单独文件便于缓存。

### CSS 代码分割

```js
build: { cssCodeSplit: true }  // 默认开启，每个 async chunk 单独 CSS
```

### 压缩

```js
build: {
  minify: 'esbuild',  // 默认，比 terser 快
  // 或用 terser 获得更小体积
}
```

## 产物分析

```bash
# 安装分析插件
npx vite-bundle-visualizer
```

```js
// vite.config.ts 集成
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    visualizer({ open: true, gzipSize: true }),
  ],
})
```

关注：
- 单 chunk 过大（>250kb 触发性能预算告警）
- 重复依赖（多个版本被打包）
- 意外引入的全量包（如 `lodash` 全量 vs `lodash-es` 按需）

## 常见问题排查

### 依赖预构建（optimizeDeps）

Vite dev 会预构建 CommonJS 依赖为 ESM。报错"xxx is not defined"时：

```js
export default defineConfig({
  optimizeDeps: {
    include: ['esm-dep'],  // 显式加入预构建
  },
})
```

清缓存重试：

```bash
rm -rf node_modules/.vite
npm run dev
```

### SSR / Node 内置模块

```js
// 报错: Module "fs" externalized for browser compatibility
// 客户端代码误用了 Node 内置模块，排查导入
```

### 静态资源路径

```js
// public/ 下的文件用绝对路径 /xxx.png（原样拷贝，不经过构建）
// src/ 下 import 的资源会经过构建处理（哈希、内联）
import imgUrl from './img.png'  // ✅ 得到处理后的 URL
```

### 环境变量

```bash
# .env
VITE_API_URL=https://api.example.com
```

```ts
// 代码中访问（只有 VITE_ 前缀的暴露给客户端）
const apiUrl = import.meta.env.VITE_API_URL
```

注意：客户端环境变量会打包进产物，敏感信息绝不能放这里。

## 部署优化

### Base 路径

```js
// 部署到子路径 /app/ 下
export default defineConfig({
  base: '/app/',
})
```

### 产物目录结构

```
dist/
├── assets/
│   ├── index-[hash].js     ← 入口 + 路由懒加载
│   ├── vue-vendor-[hash].js
│   └── index-[hash].css
└── index.html
```

用哈希文件名 + 长期缓存（`Cache-Control: max-age=31536000, immutable`）。

### 预加载关键资源

Vite 自动注入 `<link rel="modulepreload">` 预加载入口依赖，减少首屏等待。

## 原则

1. **dev 与 build 一致**：dev 能跑不等于 build 能过，CI 必跑 build
2. **按需引入**：用 ESM 友好的库（`lodash-es` 而非 `lodash`）
3. **分包缓存**：稳定依赖单独分包，利用长期缓存
4. **懒加载路由**：首屏只加载所需
5. **测了再优化**：用 visualizer 看实际产物，不盲改
