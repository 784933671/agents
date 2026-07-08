---
name: vite
description: Vite 构建工具的配置、插件 API、SSR 与 Vite 8 Rolldown 迁移。适用于开发 Vite 项目、编写 vite.config.ts、Vite 插件，或用 Vite 构建库/SSR 应用时。
metadata:
  author: Anthony Fu
  version: "2026.1.31"
  source: Generated from https://github.com/vitejs/vite, scripts located at https://github.com/antfu/skills
---

# Vite

> 基于 Vite 8 beta（Rolldown 驱动）。Vite 8 使用 Rolldown 打包器和 Oxc 转换器。

Vite 是新一代前端构建工具，拥有快速的开发服务器（原生 ESM + HMR）与优化的生产构建。

## 偏好

- 使用 TypeScript：优先用 `vite.config.ts`
- 始终使用 ESM，避免 CommonJS

## 核心参考

| 主题 | 描述 | 参考 |
|------|------|------|
| 配置 | `vite.config.ts`、`defineConfig`、条件配置、`loadEnv` | [core-config](references/core-config.md) |
| 特性 | `import.meta.glob`、资源查询（`?raw`、`?url`）、`import.meta.env`、HMR API | [core-features](references/core-features.md) |
| 插件 API | Vite 专属钩子、虚拟模块、插件顺序 | [core-plugin-api](references/core-plugin-api.md) |

## 构建与 SSR

| 主题 | 描述 | 参考 |
|------|------|------|
| 构建与 SSR | 库模式、SSR 中间件模式、`ssrLoadModule`、JavaScript API | [build-and-ssr](references/build-and-ssr.md) |

## 进阶

| 主题 | 描述 | 参考 |
|------|------|------|
| Environment API | Vite 6+ 多环境支持、自定义运行时 | [environment-api](references/environment-api.md) |
| Rolldown 迁移 | Vite 8 变更：Rolldown 打包器、Oxc 转换器、配置迁移 | [rolldown-migration](references/rolldown-migration.md) |

## 快速参考

### CLI 命令

```bash
vite              # 启动开发服务器
vite build        # 生产构建
vite preview      # 预览生产构建
vite build --ssr  # SSR 构建
```

### 常用配置

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [],
  resolve: { alias: { '@': '/src' } },
  server: { port: 3000, proxy: { '/api': 'http://localhost:8080' } },
  build: { target: 'esnext', outDir: 'dist' },
})
```

### 官方插件

- `@vitejs/plugin-vue` - Vue 3 SFC 支持
- `@vitejs/plugin-vue-jsx` - Vue 3 JSX
- `@vitejs/plugin-react` - React（Oxc/Babel）
- `@vitejs/plugin-react-swc` - React（SWC）
- `@vitejs/plugin-legacy` - 旧版浏览器支持
