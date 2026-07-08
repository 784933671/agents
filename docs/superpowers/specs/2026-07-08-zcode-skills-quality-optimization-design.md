# ZCode Skills 质量优化设计

**日期**: 2026-07-08

## 背景

当前仓库的 skills 分为两类:

- `ui-ux-craft`: `ui-fix-playbook`、`ux-test-design`、`wcag-essentials`
- `vue-development`: `vue`、`vue-best-practices`、`pinia`、`vue-router-best-practices`、`vite`

上一轮已经增强了 agent/command/skill 的基础结构校验，并给 README 增加了 agent 路由表。本轮聚焦 skills 本身的可维护性和使用清晰度。

## 目标

提升 skills 的可发现性、文档一致性和引用完整性。

## 非目标

- 不新增或删除 skill
- 不大规模改写生成型 Vue skills 的主体内容
- 不引入第三方依赖
- 不调整 marketplace 对外结构
- 不改变 agent 的职责边界

## 方案

### 1. 校验 skill 本地引用完整性

扩展 `scripts/verify.py`，检查 `plugins/*/skills/**/SKILL.md` 中引用的本地 Markdown 链接是否存在。

校验范围:

- `references/*.md`
- `reference/*.md`

校验规则:

- 只校验相对本 skill 目录内的本地 Markdown 链接
- 不校验外部 URL
- 不校验普通说明文本
- 失败时输出包含源文件和缺失链接的错误

成功时新增输出:

```text
ok: skill references are valid
```

### 2. README 增加 Choosing a skill

在 README 的 agent 路由表之后增加 skill 路由表，帮助用户理解小问题为什么更常走 skill。

覆盖:

- `vue`: Vue API / SFC / reactivity / script setup
- `vue-best-practices`: Vue 架构、组件拆分、实现规范
- `pinia`: store 设计、actions、getters、SSR/HMR
- `vue-router-best-practices`: 路由守卫、参数变化、重定向循环
- `vite`: Vite 配置、插件、构建、SSR
- `wcag-essentials`: WCAG A/AA、ARIA、键盘、对比度
- `ui-fix-playbook`: UI 缺陷定位、最小修复、回归验证
- `ux-test-design`: 用户流程测试、状态覆盖、缺陷报告

### 3. UI 修复手册去技术栈偏向

`ui-fix-playbook` 中的状态 bug 示例目前出现 `useEffect`，偏 React。将其改为更通用的“未清理监听器/副作用”，避免在 Vue 或框架无关任务中误导。

### 4. 生成型 Vue skills 维护说明

新增轻量维护说明文档，记录生成型 Vue skills 的来源和刷新原则:

- `vue`
- `pinia`
- `vite`
- `vue-best-practices`
- `vue-router-best-practices`

该文档只说明维护策略，不改生成型 skill 主体内容。

## 验证

本地执行:

```bash
python3 scripts/verify.py
git diff --check
```

预期:

```text
ok: json manifests are valid
ok: plugin content structure is valid
ok: skill references are valid
ok: README agent routing guide is in sync
ok: README agents table is in sync.
ok: repository verification passed
```

## 风险与边界

- Markdown 链接校验只覆盖本地 `reference(s)/*.md`，避免误伤外部链接和普通文本。
- README skill 路由表是维护说明，不参与自动调度。
- 生成型 Vue skills 内容仍以原来源为准，本轮只补维护策略，不做内容刷新。
