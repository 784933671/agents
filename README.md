# 784933671-agents

一个面向 **ZCode / Claude Code** 的自托管 agents 与 skills 插件市场。安装后可按分类选择 UI/UX、Vue、JavaScript 和项目专用 API 能力包。

## What's inside

本市场的所有 pack 都内置在 `plugins/` 目录下，安装时直接从仓库读取：

<!-- AGENTS-TABLE:START -->
| Pack | Category | Agents | Skills |
|------|----------|--------|--------|
| `ui-ux-craft` | design | accessibility-tester, ui-designer, ui-fixer, ui-ux-tester | ui-fix-playbook, ux-test-design, wcag-essentials |
| `vue-development` | development | vue-expert | pinia, vite, vue, vue-best-practices, vue-router-best-practices |
| `javascript-development` | development | _(none)_ | javascript-pro |
| `xuegong-system` | development | xuegong-api-expert | _(none)_ |

Total: **4 packs, 6 agents, 9 skills**.

<!-- AGENTS-TABLE:END -->

## Choosing an agent

| Agent | Use when |
|-------|----------|
| `ui-designer` | You need UI design direction, layout decisions, interaction states, or design system alignment. |
| `ui-fixer` | You have a reproduced UI bug, layout issue, style regression, or responsive breakpoint problem. |
| `ui-ux-tester` | You need end-to-end UI/UX flow testing, state coverage, or a structured defect report. |
| `accessibility-tester` | You need keyboard, focus, ARIA, contrast, screen reader, or WCAG A/AA review. |
| `vue-expert` | You need Vue 3, Composition API, Pinia, Vue Router, Vite, SFC, reactivity, or component architecture help. |
| `xuegong-api-expert` | You need 学工系统 Apifox MCP 接口查询、参数确认、请求示例或响应结构说明. |

## Choosing a skill

Use skills for focused knowledge, API patterns, and lightweight guidance. Use agents when the task needs a larger audit, repair, or test workflow.

| Skill | Use when |
|-------|----------|
| `vue` | You need Vue API, SFC, reactivity, lifecycle, watcher, or `<script setup>` guidance. |
| `vue-best-practices` | You need Vue architecture, component boundaries, data flow, composables, or implementation standards. |
| `pinia` | You need store design, state/getters/actions, SSR, HMR, or testing guidance. |
| `vue-router-best-practices` | You need route guard, route params, redirect loop, or route lifecycle guidance. |
| `vite` | You need Vite config, plugin, build, SSR, environment, or Rolldown migration guidance. |
| `javascript-pro` | You need modern JavaScript, async/await, ESM/CJS modules, Node.js, browser APIs, or `.js/.mjs/.cjs` review guidance. |
| `wcag-essentials` | You need WCAG A/AA, ARIA, keyboard, focus, contrast, or accessible component guidance. |
| `ui-fix-playbook` | You need UI defect triage, root cause isolation, minimal repair, or regression verification guidance. |
| `ux-test-design` | You need user-flow test design, state coverage, test cases, or defect report structure. |

## Install in ZCode / Claude Code

1. Open your client's plugin marketplace settings.
2. Add a marketplace with this repo's URL:
   ```
   https://github.com/784933671/agents.git
   ```
3. Browse the marketplace and install whichever pack(s) you want.

The client reads `.claude-plugin/marketplace.json` to discover the packs; each pack is served directly from `plugins/<name>` in this repo.

## How it's structured

```
.claude-plugin/
└── marketplace.json     ← declares the packs
plugins/                 ← all packs live here
├── javascript-development/ ← JavaScript ES2023+ / async / ESM / Node.js / Browser API
├── ui-ux-craft/         ← UI design, fixing, UX testing, accessibility
└── vue-development/     ← Vue 3 / Composition API / Pinia / Vite
```

Each pack has a minimal `.claude-plugin/plugin.json` (just `name` + `description`); its agents, commands, and skills are auto-discovered from the `agents/*.md`, `commands/*.md`, and `skills/*/SKILL.md` directory conventions.

## Adding more packs

Add new entries to the `plugins` array in `marketplace.json`. Each entry needs `name`, `description`, `category`, and a `source` pointing at a vendored directory under `plugins/`:

```json
{
  "name": "your-pack",
  "description": "...",
  "category": "development",
  "source": "./plugins/your-pack"
}
```

## Keeping the table in sync

The contents table above (between the `AGENTS-TABLE` markers) is generated from `marketplace.json` and the resolved `agents/` / `skills/` directories — **don't hand-edit it**.

After any change to `marketplace.json` or a pack's `agents/` / `skills/`, refresh the table:

```bash
python scripts/sync_agents_table.py update
```

Other useful subcommands:

- `generate` — print the expected table to stdout (no files touched)
- `check` — verify the table matches what the packs declare; exits non-zero on mismatch

CI (`.github/workflows/verify.yml`) runs `python3 scripts/verify.py` on marketplace-related changes, and fails the build if the generated README table or manifests drift.

## Local verification

Before publishing marketplace changes, run the repository verifier:

```bash
python3 scripts/verify.py
```

It validates JSON manifests, plugin content structure, skill reference links, the README routing guides, and the generated README contents table.

## License

MIT.
