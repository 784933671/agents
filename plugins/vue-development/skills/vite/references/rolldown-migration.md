---
name: vite-rolldown
description: Vite 8 Rolldown 打包器与 Oxc 转换器迁移
---

# Rolldown 迁移（Vite 8）

Vite 8 用 Rolldown（统一的基于 Rust 的打包器）替换了 esbuild+Rollup。

## 变更内容

| 迁移前（Vite 7） | 迁移后（Vite 8） |
|-----------------|-----------------|
| esbuild（开发转换） | Oxc Transformer |
| esbuild（依赖预打包） | Rolldown |
| Rollup（生产构建） | Rolldown |
| `rollupOptions` | `rolldownOptions` |
| `esbuild` 选项 | `oxc` 选项 |

## 性能影响

- 生产构建比 Rollup 快 10-30 倍
- 匹配 esbuild 的开发性能
- 开发与构建行为统一

## 配置迁移

### rollupOptions → rolldownOptions

```ts
// 迁移前（Vite 7）
export default defineConfig({
  build: {
    rollupOptions: {
      external: ['vue'],
      output: { globals: { vue: 'Vue' } },
    },
  },
})

// 迁移后（Vite 8）
export default defineConfig({
  build: {
    rolldownOptions: {
      external: ['vue'],
      output: { globals: { vue: 'Vue' } },
    },
  },
})
```

### esbuild → oxc

```ts
// 迁移前（Vite 7）
export default defineConfig({
  esbuild: {
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
  },
})

// 迁移后（Vite 8）
export default defineConfig({
  oxc: {
    jsx: {
      runtime: 'classic',
      pragma: 'h',
      pragmaFrag: 'Fragment',
    },
  },
})
```

### JSX 配置

```ts
export default defineConfig({
  oxc: {
    jsx: {
      runtime: 'automatic',  // 或 'classic'
      importSource: 'react', // 用于 automatic 运行时
    },
    jsxInject: `import React from 'react'`,  // 自动注入
  },
})
```

### 自定义转换目标

```ts
export default defineConfig({
  oxc: {
    include: ['**/*.ts', '**/*.tsx'],
    exclude: ['node_modules/**'],
  },
})
```

## 插件兼容性

大多数 Vite 插件无需改动即可工作。Rolldown 支持 Rollup 的插件 API。

如果插件只在构建时工作：

```ts
{
  ...rollupPlugin(),
  enforce: 'post',
  apply: 'build',
}
```

## 新能力

Rolldown 解锁了以前不可能的功能：

- 完整 bundle 模式（实验性）
- 模块级持久缓存
- 更灵活的代码块拆分
- Module Federation 支持

## 渐进式迁移

对于大型项目，先通过 `rolldown-vite` 迁移：

```bash
# 步骤 1：用 rolldown-vite 测试
pnpm add -D rolldown-vite

# 替换配置中的 vite 导入
import { defineConfig } from 'rolldown-vite'

# 步骤 2：稳定后升级到 Vite 8
pnpm add -D vite@8
```

## 在框架中覆盖 Vite

当框架依赖较旧的 Vite 时：

```json
{
  "pnpm": {
    "overrides": {
      "vite": "8.0.0"
    }
  }
}
```

<!--
Source references:
- https://vite.dev/blog/announcing-vite8-beta
- https://vite.dev/blog/announcing-vite7
- https://vite.dev/config/shared-options#oxc
-->
