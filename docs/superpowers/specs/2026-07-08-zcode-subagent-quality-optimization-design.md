# ZCode 子智能体质量优化设计

**日期**: 2026-07-08

## 背景

当前仓库维护两个 ZCode / Claude Code 插件包:

- `ui-ux-craft`: UI/UX 设计、修复、测试与无障碍审计
- `vue-development`: Vue 3 / Composition API / Pinia / Vue Router / Vite 开发辅助

上一轮已经补齐统一校验入口与 CI。本轮聚焦子智能体可用性: 让路由触发更稳定、让校验覆盖 agent/command/skill 的基础结构、让 README 能指导用户选择合适的 agent。

## 目标

低风险优化子智能体体验与维护质量。

## 非目标

- 不新增插件包
- 不新增或删除 agent、command、skill
- 不修改 agent 的核心工作模式和职责边界
- 不引入第三方依赖
- 不调整 marketplace 对外结构
- 不做大规模重构

## 方案

### 1. 统一 agent 路由描述

将 `vue-expert` 的 frontmatter `description` 调整为与 UI/UX agents 一致的“主动用于...”风格，并补充自动路由关键词:

- Vue 3
- Composition API
- `<script setup>`
- 响应式陷阱
- Pinia
- Vue Router
- Vite
- 组件架构
- 渲染性能

该调整只影响描述和触发精度，不改变正文工作模式。

### 2. 增强仓库校验

扩展 `scripts/verify.py`，在现有 JSON 与 README 表格校验基础上增加结构校验:

- 每个 `plugins/*/agents/*.md` 必须有 frontmatter
- agent frontmatter 必须包含 `name`、`description`、`model`
- agent 文件名 stem 必须等于 frontmatter `name`
- 每个 `plugins/*/commands/*.md` 必须包含 `$ARGUMENTS`
- 每个 `plugins/*/skills/*/SKILL.md` 必须有 frontmatter，并包含 `name`、`description`
- marketplace 中的本地 `./plugins/...` source 必须存在

校验仍只使用 Python 标准库。失败时输出可定位的错误信息并返回非 0。

### 3. 补 README 子智能体路由表

在 README 增加“Choosing an agent”说明，帮助用户按任务选择:

- `ui-designer`: 设计方案、布局、交互状态、设计系统一致性
- `ui-fixer`: 已复现 UI bug、布局错位、样式回归、响应式问题
- `ui-ux-tester`: 端到端流程测试、状态覆盖、缺陷报告
- `accessibility-tester`: 键盘可达、焦点、ARIA、对比度、WCAG
- `vue-expert`: Vue 3、Composition API、Pinia、Vue Router、Vite、组件架构

该表只作为用户选择指南，不改变 marketplace 内容。

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
ok: README agents table is in sync.
ok: repository verification passed
```

## 风险与边界

- `vue-expert` 描述变更可能影响客户端自动路由，但目标是提高触发精度，不改变能力边界。
- `$ARGUMENTS` 校验假设所有 command 都是参数化命令；当前仓库内 commands 均符合该模式。
- frontmatter 校验只做轻量字段检查，不实现完整 YAML 解析。
