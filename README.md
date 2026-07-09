# 784933671-agents

这是一个面向 **zCode** 的自托管插件市场，用来分发可安装的代理、技能、命令和 MCP 能力包。

这个仓库不是业务应用源码，也不是前端/后端项目模板。模型读取本仓库时，应把它理解为“zCode 插件市场”：维护 `.claude-plugin/marketplace.json`，并在 `plugins/` 下按能力包组织可安装能力。

说明：本项目使用 `.claude-plugin` 目录和 `SKILL.md` 结构作为 zCode 插件市场的兼容清单格式。文档中的 `.claude-plugin` 是技术目录约定，不表示本项目面向其他产品分发。

## 模型使用指南

当你在这个仓库工作时，先判断用户目标属于哪一类：

| 用户目标 | 应该怎么做 |
|----------|------------|
| 想给 zCode 增加一个可安装能力 | 新增或修改 `plugins/<pack-name>/`，并更新 `.claude-plugin/marketplace.json` |
| 想增加一个专门执行复杂任务的角色 | 新增 `plugins/<pack-name>/agents/<agent-name>.md` |
| 想增加一套可被模型按需调用的知识、流程或规范 | 新增 `plugins/<pack-name>/skills/<skill-name>/SKILL.md` |
| 想增加斜杠命令 | 新增 `plugins/<pack-name>/commands/<command-name>.md`，命令内容必须包含 `$ARGUMENTS` |
| 想接入外部服务或工具 | 在对应能力包中配置 MCP，例如 `.mcp.json` |
| 想修改市场展示或安装入口 | 修改 `.claude-plugin/marketplace.json` 和本 README |

处理请求时遵循这些原则：

- 优先复用现有能力包、代理、技能和脚本，不重复创建相同能力。
- 新能力应放在最贴近语义的能力包中；跨领域能力才新增能力包。
- 代理适合较重的流程、审查、修复、测试和跨步骤任务。
- 技能适合轻量知识、规范、API 模式、最佳实践和可复用执行流程。
- 不要手改 `AGENTS-TABLE` 标记之间的表格，用脚本生成。
- 修改可安装能力后，按语义化版本更新对应 `plugin.json` 的 `version`。
- 改完市场清单、代理或技能后，必须运行 markdownlint、单测和仓库校验。

## 市场内容

本市场的所有能力包都内置在 `plugins/` 目录下，安装时直接从仓库读取：

<!-- AGENTS-TABLE:START -->
| 能力包 | 分类 | 代理 | 技能 |
|--------|------|------|------|
| `ui-ux-craft` | 设计 | accessibility-tester, ui-designer, ui-fixer, ui-ux-tester | ui-fix-playbook, ux-test-design, wcag-essentials |
| `vue-development` | 开发 | vue-expert | pinia, vite, vue, vue-best-practices, vue-router-best-practices |
| `javascript-development` | 开发 | _(none)_ | javascript-pro |
| `xuegong-system` | 开发 | xuegong-api-expert | _(none)_ |

总计：**4 个能力包，6 个代理，9 个技能**。

<!-- AGENTS-TABLE:END -->

## 选择能力包

| 能力包 | 适用场景 |
|------|----------|
| `ui-ux-craft` | UI 设计、视觉修复、交互走查、可访问性审查、用户流程测试 |
| `vue-development` | Vue 3、Composition API、Pinia、Vue Router、Vite、SFC 和组件架构 |
| `javascript-development` | 现代 JavaScript、async/await、ESM/CJS、Node.js、浏览器 API、`.js/.mjs/.cjs` 审查 |
| `xuegong-system` | 学工系统接口查询、Apifox MCP 调用、接口参数和响应结构确认 |

## 选择代理

代理是更重的任务执行角色。任务需要审查、修复、测试、流程推进或外部工具协作时，优先选择代理。

| 代理 | 使用场景 |
|-------|----------|
| `ui-designer` | 需要 UI 设计方向、布局决策、交互状态、设计系统对齐或页面体验建议 |
| `ui-fixer` | 已复现 UI bug、布局异常、样式回归或响应式断点问题，需要最小范围修复 |
| `ui-ux-tester` | 需要端到端 UI/UX 流程测试、状态覆盖、缺陷报告或体验走查 |
| `accessibility-tester` | 需要键盘、焦点、ARIA、对比度、屏幕阅读器或 WCAG A/AA 审查 |
| `vue-expert` | 需要 Vue 3、Composition API、Pinia、Vue Router、Vite、SFC、响应式或组件架构支持 |
| `xuegong-api-expert` | 需要学工系统 Apifox MCP 接口查询、参数确认、请求示例或响应结构说明 |

## 选择技能

技能是按需加载的知识与流程。任务只需要规范、API 参考、最佳实践或轻量指导时，优先选择技能。

| 技能 | 使用场景 |
|-------|----------|
| `vue` | 需要 Vue API、SFC、响应式、生命周期、watcher 或 `<script setup>` 指导 |
| `vue-best-practices` | 需要 Vue 架构、组件边界、数据流、composables 或实现规范 |
| `pinia` | 需要 store 设计、state/getters/actions、SSR、HMR 或测试指导 |
| `vue-router-best-practices` | 需要路由守卫、路由参数、重定向循环或路由生命周期指导 |
| `vite` | 需要 Vite 配置、插件、构建、SSR、环境变量或 Rolldown 迁移指导 |
| `javascript-pro` | 需要现代 JavaScript、async/await、ESM/CJS、Node.js、浏览器 API 或 `.js/.mjs/.cjs` 审查指导 |
| `wcag-essentials` | 需要 WCAG A/AA、ARIA、键盘、焦点、对比度或无障碍组件指导 |
| `ui-fix-playbook` | 需要 UI 缺陷定位、根因隔离、最小修复或回归验证指导 |
| `ux-test-design` | 需要用户流程测试设计、状态覆盖、测试用例或缺陷报告结构 |

## 安装方式

在 zCode 的插件市场设置中添加本仓库：

```bash
https://github.com/784933671/agents.git
```

客户端会读取 `.claude-plugin/marketplace.json` 来发现可安装能力包。每个能力包都从 `plugins/<name>` 目录加载。

安装后，技能通常以命名空间方式调用，例如：

```text
/javascript-development:javascript-pro
```

## 目录结构

```text
.claude-plugin/
└── marketplace.json          # 插件市场入口，声明所有能力包
plugins/
├── javascript-development/   # JavaScript ES2023+ / async / ESM / Node.js / Browser API
├── ui-ux-craft/              # UI 设计、修复、UX 测试、可访问性
├── vue-development/          # Vue 3 / Composition API / Pinia / Vite
└── xuegong-system/           # 学工系统 Apifox MCP 接入
```

每个能力包至少包含：

```text
plugins/<pack-name>/
└── .claude-plugin/
    └── plugin.json
```

可选能力目录：

```text
agents/*.md                  # 子代理角色
commands/*.md                # 斜杠命令，必须包含 $ARGUMENTS
skills/*/SKILL.md            # 技能入口，可包含 references/scripts/assets
.mcp.json                    # MCP 配置
```

## 新增或修改能力

新增能力包：

1. 创建 `plugins/<pack-name>/.claude-plugin/plugin.json`。
2. 按需添加 `agents/`、`skills/`、`commands/` 或 MCP 配置。
3. 在 `.claude-plugin/marketplace.json` 的 `plugins` 数组中新增入口。
4. 运行 `python3 scripts/sync_agents_table.py update`。
5. 运行完整本地验证。

新增代理：

1. 创建 `plugins/<pack-name>/agents/<agent-name>.md`。
2. frontmatter 必须包含 `name`、`description`、`model`。
3. `name` 必须与文件名 stem 一致。
4. 更新 README 路由表中的 `选择代理`。

新增技能：

1. 创建 `plugins/<pack-name>/skills/<skill-name>/SKILL.md`。
2. frontmatter 必须包含 `name`、`description`。
3. 如需长文档，放到同级 `references/` 并在 `SKILL.md` 中链接。
4. 更新 README 路由表中的 `选择技能`。

新增命令：

1. 创建 `plugins/<pack-name>/commands/<command-name>.md`。
2. 文件内容必须包含 `$ARGUMENTS`。

## 升级测试

发布升级前按以下流程验证：

1. 根据变更范围更新 `plugins/<pack-name>/.claude-plugin/plugin.json` 的 `version`。
2. 运行完整本地验证。
3. 提交并推送到插件市场仓库。
4. 在 zCode 插件市场刷新仓库或重新安装目标能力包。
5. 新开会话验证目标技能、代理、斜杠命令或 MCP 是否加载为新版本。
6. 对 MCP 能力包，先填写插件配置，再运行对应自检命令，例如 `/xuegong-check`。

## 同步自动表格

`AGENTS-TABLE` 标记之间的内容由脚本生成，不要手动编辑。

当 `.claude-plugin/marketplace.json`、`agents/` 或 `skills/` 发生变化时，运行：

```bash
python3 scripts/sync_agents_table.py update
```

其他子命令：

- `generate`：输出期望表格，不修改文件
- `check`：检查 README 表格是否同步

## 本地验证

发布或提交前运行：

```bash
npx -y markdownlint-cli@0.43.0 '**/*.md'
python3 -m unittest scripts/test_verify.py
python3 scripts/verify.py
```

验证内容包括：

- Markdown 文档格式是否符合本仓库规则
- JSON 清单是否有效
- 市场中的本地能力包来源是否存在
- 市场入口、能力包目录与插件清单中的名称是否一致
- `plugin.json` 版本号、展示名、作者、仓库、许可证、关键词等元数据是否完整
- MCP 配置路径是否存在且不越出能力包目录
- MCP 中 `${user_config.xxx}` 引用是否能匹配 `plugin.json` 的 `userConfig` 字段
- 代理、命令、技能基本结构是否符合约定
- 技能参考链接是否存在且不越界
- 代理正文中引用的同包技能是否存在
- README 中代理/技能路由表是否完整
- README 自动生成表是否同步
- 仓库中是否存在已知格式的明文访问 token

## 维护边界

- 不要把业务项目代码放进这个仓库。
- 不要把临时说明、安装草稿、一次性文档放进技能目录。
- 不要为了一个普通技能新增代理，除非任务确实需要独立角色或长流程。
- 不要在不同能力包中复制相同技能，优先复用或移动到更通用的能力包。
- 引入第三方技能时，保留来源、许可和必要版权说明。

## 许可证

MIT.
