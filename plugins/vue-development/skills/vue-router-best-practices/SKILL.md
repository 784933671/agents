---
name: vue-router-best-practices
description: "Vue Router 4 模式、导航守卫、路由参数与路由组件生命周期交互。"
version: 1.0.0
license: MIT
author: github.com/vuejs-ai
---

Vue Router 最佳实践、常见陷阱与导航模式。

### 导航守卫
- 相同路由不同参数间导航 → 见 [router-beforeenter-no-param-trigger](reference/router-beforeenter-no-param-trigger.md)
- 在 beforeRouteEnter 守卫中访问组件实例 → 见 [router-beforerouteenter-no-this](reference/router-beforerouteenter-no-this.md)
- 导航守卫中发起 API 调用但未 await → 见 [router-guard-async-await-pattern](reference/router-guard-async-await-pattern.md)
- 用户陷入无限重定向循环 → 见 [router-navigation-guard-infinite-loop](reference/router-navigation-guard-infinite-loop.md)
- 导航守卫使用了已弃用的 next() 函数 → 见 [router-navigation-guard-next-deprecated](reference/router-navigation-guard-next-deprecated.md)

### 路由生命周期
- 相同路由间导航时数据过期 → 见 [router-param-change-no-lifecycle](reference/router-param-change-no-lifecycle.md)
- 组件卸载后事件监听器仍残留 → 见 [router-simple-routing-cleanup](reference/router-simple-routing-cleanup.md)

### 配置
- 构建生产环境单页应用 → 见 [router-use-vue-router-for-production](reference/router-use-vue-router-for-production.md)
