# AGENTS.md

## 项目定位

这是面向 zCode 的自托管插件市场，用于分发可安装的代理、技能、命令和 MCP 能力包。不要把它当作业务前端、后端或项目模板仓库。

## 维护原则

- 优先复用现有 `plugins/<pack-name>/`、代理、技能、命令和脚本，不重复创建同类能力。
- 新能力放入语义最接近的能力包；只有跨领域能力才新增能力包。
- 代理用于复杂任务、审查、修复、测试和跨步骤流程；技能用于轻量知识、规范、API 模式和可复用流程。
- 不要手改 README 中 `AGENTS-TABLE` 标记之间的表格，使用 `python3 scripts/sync_agents_table.py update` 生成。
- MCP 可以保留 `@latest` 版本策略，但禁止提交真实 token、密钥、密码或私有凭据。
- 修改可安装能力后，按语义化版本更新对应 `plugin.json` 的 `version`。

## 目录约定

- `.claude-plugin/marketplace.json`：市场入口，声明所有能力包。
- `plugins/<pack-name>/.claude-plugin/plugin.json`：能力包清单，`name` 必须与能力包目录名一致。
- `plugins/<pack-name>/agents/*.md`：子智能体，frontmatter 必须包含 `name`、`description`、`model`。
- `plugins/<pack-name>/skills/<skill-name>/SKILL.md`：技能入口，frontmatter 必须包含 `name`、`description`。
- `plugins/<pack-name>/commands/*.md`：斜杠命令，内容必须包含 `$ARGUMENTS`。
- `plugins/<pack-name>/.mcp.json`：可选 MCP 配置；如需 token，提交空字符串或环境变量占位，不提交真实值。

## 修改流程

1. 修改市场清单、代理、技能、命令或 MCP 配置。
2. 如能力包、代理或技能数量变化，运行 `python3 scripts/sync_agents_table.py update`。
3. 运行 `npx -y markdownlint-cli@0.43.0 '**/*.md'`。
4. 运行 `python3 -m unittest scripts/test_verify.py`。
5. 运行 `python3 scripts/verify.py`。
6. 修复所有失败后再交付。

## 校验边界

`scripts/verify.py` 会校验：

- JSON 清单有效且本地插件路径存在。
- marketplace 名称、插件目录名与 `plugin.json` 名称一致。
- `plugin.json` 版本号、展示名、作者、仓库、许可证、关键词等元数据完整。
- `mcpServers` 指向的 MCP 文件存在且不越出插件目录。
- MCP 中 `${user_config.xxx}` 引用能匹配 `plugin.json` 的 `userConfig` 字段。
- 代理、命令、技能基础结构符合约定。
- 技能参考链接存在且不越界。
- 代理正文中形如 `` `skill-name` 技能 `` 的引用能匹配同包技能。
- README 代理/技能路由表和自动生成表同步。
- 仓库中不存在已知格式的明文访问 token。
