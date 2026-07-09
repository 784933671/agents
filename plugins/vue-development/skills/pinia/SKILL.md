---
name: pinia
description: Pinia 是 Vue 官方状态管理库，适用于定义 store、使用 state/getters/actions，或在 Vue 应用中实现 JavaScript store 模式时。
metadata:
  author: Anthony Fu
  version: "2026.1.28"
  source: Generated from https://github.com/vuejs/pinia, scripts located at https://github.com/antfu/skills
---

# Pinia

Pinia 是 Vue 的官方状态管理库，设计直观。它同时支持 Options API 与 Composition API 两种风格，适合 JavaScript 项目和 devtools 调试。

> 本技能基于 Pinia v3.0.4，生成于 2026-01-28。

## 核心参考

| 主题 | 描述 | 参考 |
|------|------|------|
| Store | 定义 store、state、getters、actions、storeToRefs、订阅 | [core-stores](references/core-stores.md) |

## 进阶特性

### 可扩展性

| 主题 | 描述 | 参考 |
|------|------|------|
| 插件 | 通过自定义属性、state 和行为扩展 store | [features-plugins](references/features-plugins.md) |

### 组合性

| 主题 | 描述 | 参考 |
|------|------|------|
| Composables | 在 store 中使用 Vue composables（VueUse 等） | [features-composables](references/features-composables.md) |
| Store 间组合 | store 之间的通信，避免循环依赖 | [features-composing-stores](references/features-composing-stores.md) |

## 最佳实践

| 主题 | 描述 | 参考 |
|------|------|------|
| 测试 | 使用 @pinia/testing 进行单元测试、mock 与 stub | [best-practices-testing](references/best-practices-testing.md) |
| 组件外使用 | 在导航守卫、插件、中间件中使用 store | [best-practices-outside-component](references/best-practices-outside-component.md) |

## 高级

| 主题 | 描述 | 参考 |
|------|------|------|
| SSR | 服务端渲染、state 水合 | [advanced-ssr](references/advanced-ssr.md) |
| Nuxt | Nuxt 集成、自动导入、SSR 最佳实践 | [advanced-nuxt](references/advanced-nuxt.md) |
| HMR | 开发环境下的热模块替换 | [advanced-hmr](references/advanced-hmr.md) |

## 关键建议

- **复杂逻辑、composables 和 watchers 优先用 Setup Store**
- **解构 state/getters 时使用 `storeToRefs()`** 以保留响应式
- **Actions 可以直接解构** —— 它们已绑定到 store
- **在函数内部调用 store**，不要在模块作用域调用，SSR 场景尤其如此
- **为每个 store 添加 HMR 支持**，提升开发体验
- **组件测试使用 `@pinia/testing`** 来 mock store
