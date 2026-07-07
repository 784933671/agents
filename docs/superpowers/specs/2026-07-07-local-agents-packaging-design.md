# 本地子智能体打包上传设计

**日期**: 2026-07-07
**目标**: 将 `~/.zcode/agents/` 下的 16 个本地子智能体打包成 4 个插件包,加入现有 marketplace 仓库 `github.com/784933671/agents`,供后续通过插件市场安装。

## 背景

- 现有仓库 `agents` 已是一个插件市场,通过 `git-subdir` 引用 `wshobson/agents` 上游的 6 个 pack(共 19 个 agent)。
- 本地 16 个 agent 不是 git 仓库,无法用 `git-subdir` 引用,只能 vendor(复制)进插件仓库。
- 用户选择:**按领域分 4 个包** + **保留 wshobson 的 6 个包**。

## 分类方案

| 新包名 | category | agents | 数量 |
|--------|----------|--------|------|
| `web-frontend` | development | frontend-developer, react-specialist, vue-expert, nextjs-developer, javascript-pro, typescript-pro | 6 |
| `ui-ux-craft` | design | ui-designer, ui-fixer, ui-ux-tester, accessibility-tester | 4 |
| `diagnostics` | development | browser-debugger, performance-engineer | 2 |
| `engineering` | development | build-engineer, code-mapper, documentation-engineer, refactoring-specialist | 4 |

包名刻意避开 wshobson 已占用的名称(如 `frontend-mobile-development`、`ui-design`、`debugging-toolkit`),避免在同 marketplace 内冲突。

## 仓库结构

```
agents/
├── .claude-plugin/
│   └── marketplace.json                  ← 改造:支持 vendor 包 + git-subdir 包
├── plugins/                              ← 新增
│   ├── web-frontend/
│   │   ├── .claude-plugin/plugin.json
│   │   └── agents/*.md (6)
│   ├── ui-ux-craft/
│   │   ├── .claude-plugin/plugin.json
│   │   └── agents/*.md (4)
│   ├── diagnostics/
│   │   ├── .claude-plugin/plugin.json
│   │   └── agents/*.md (2)
│   └── engineering/
│       ├── .claude-plugin/plugin.json
│       └── agents/*.md (4)
├── scripts/sync_agents_table.py          ← 改造:支持 directory source
├── README.md                             ← 更新表格
└── .gitignore
```

## 关键设计

### Vendor 包的 source 写法

`marketplace.json` 中本地包使用 `directory` source(相对路径),与 wshobson 的 `git-subdir` 共存:

```json
{
  "name": "web-frontend",
  "source": { "source": "directory", "path": "./plugins/web-frontend" }
}
```

### plugin.json 最小清单

每个 vendor 包的 `.claude-plugin/plugin.json` 只写 `name` + `description`,agents 通过 `agents/*.md` 目录约定自动发现,无需显式声明 `agents` 字段。

### sync_agents_table.py 改造

按 source 类型分流:
- `git-subdir` → 调 GitHub Contents API(现有逻辑)
- `directory` → 直接读本地 `plugins/<name>/agents/*.md`

### Agent 文件原样 vendor

不修改任何 frontmatter,保留原始中文描述。

## 不做的事(YAGNI)

- 不改 wshobson 6 个包的 `sha`
- 不修改本地 agent 的 frontmatter
- 不新增 CI workflow
- 不在 vendor 包内单独加 LICENSE(README 已声明 MIT)

## 验证

1. `jq` 校验 `marketplace.json` 与各 `plugin.json` 为合法 JSON
2. `python scripts/sync_agents_table.py check` 验证 README 表格一致
3. `python scripts/sync_agents_table.py generate` 生成新表格供人工核对
4. 输出最终文件树确认

## 发布

打包完成后提示用户执行 `git add/commit/push`,不自动 push(对外发布需用户确认)。
