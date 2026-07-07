# 784933671-agents

A curated multi-category **subagent collection** for ZCode / Claude Code, packaged as a plugin marketplace. One-click install gives you categorized agent packs — some sourced from high-quality community repos, some vendored from a local agent collection.

## What's inside

Two kinds of packs live side by side in this marketplace:

- **Upstream packs** — referenced from [`wshobson/agents`](https://github.com/wshobson/agents), pinned to commit `5cc2549a` (2026-06-25). Fetched on demand via `git-subdir`.
- **Vendored packs** — a set of locally authored agents (originally in `~/.zcode/agents/`), copied into `plugins/` and served from this repo directly.

<!-- AGENTS-TABLE:START -->
| Pack | Category | Agents |
|------|----------|--------|
| `frontend-mobile-development` | development | frontend-developer, mobile-developer |
| `backend-development` | development | backend-architect, event-sourcing-architect, graphql-architect, performance-engineer, security-auditor, tdd-orchestrator, temporal-python-pro, test-automator |
| `javascript-typescript` | development | javascript-pro, typescript-pro |
| `debugging-toolkit` | development | debugger, dx-optimizer |
| `code-refactoring` | development | code-reviewer, legacy-modernizer |
| `ui-design` | design | accessibility-expert, design-system-architect, ui-designer |
| `web-frontend` | development | web-frontend-frontend-developer, web-frontend-javascript-pro, web-frontend-nextjs-developer, web-frontend-react-specialist, web-frontend-typescript-pro, web-frontend-vue-expert |
| `ui-ux-craft` | design | ui-ux-craft-accessibility-tester, ui-ux-craft-ui-designer, ui-ux-craft-ui-fixer, ui-ux-craft-ui-ux-tester |
| `diagnostics` | development | diagnostics-browser-debugger, diagnostics-performance-engineer |
| `engineering` | development | engineering-build-engineer, engineering-code-mapper, engineering-documentation-engineer, engineering-refactoring-specialist |

Total: **10 packs, 35 agents**.

<!-- AGENTS-TABLE:END -->

## Install in ZCode / Claude Code

1. Open your client's plugin marketplace settings.
2. Add a marketplace with this repo's URL:
   ```
   https://github.com/784933671/agents.git
   ```
3. Browse the marketplace and install whichever pack(s) you want.

The client reads `.claude-plugin/marketplace.json` to discover the packs. Upstream packs are fetched on demand via `git-subdir` from the pinned commit; vendored packs are served directly from `plugins/`.

## How it's structured

```
.claude-plugin/
└── marketplace.json     ← declares all packs (upstream + vendored)
plugins/                 ← vendored packs live here
├── web-frontend/        ← React, Vue, Next.js, JS, TS specialists
├── ui-ux-craft/         ← UI design, fixing, UX testing, accessibility
├── diagnostics/         ← browser debugging + performance engineering
└── engineering/         ← build, code mapping, docs, refactoring
```

Each vendored pack has a minimal `.claude-plugin/plugin.json` (just `name` + `description`); its agents are auto-discovered from the `agents/*.md` directory convention.

## Updating the upstream pin

To pick up new agents from `wshobson/agents`:

1. Get the latest SHA of the source repo:
   ```bash
   curl -s https://api.github.com/repos/wshobson/agents/commits/main | python3 -c "import sys,json; print(json.load(sys.stdin)['sha'])"
   ```
2. Replace the `sha` field in `.claude-plugin/marketplace.json` (and `ref` if the branch changed).
3. Commit and push.

## Adding more packs

Add new entries to the `plugins` array in `marketplace.json`. Supported source types:

- `git-subdir` — pull a subdirectory from a git repo (used for wshobson packs)
- `directory` — serve a vendored pack from `./plugins/<name>` (used for local packs)
- `url` — pull an entire git repo as a plugin

Each entry needs `name`, `description`, `category`, and `source`. Upstream entries should also carry `homepage`.

## Keeping the table in sync

The agents table above (between the `AGENTS-TABLE` markers) is generated from `marketplace.json` and the resolved `agents/` directories — **don't hand-edit it**.

After any change to `marketplace.json` or a vendored pack's `agents/`, refresh the table:

```bash
python scripts/sync_agents_table.py update
```

Other useful subcommands:

- `generate` — print the expected table to stdout (no files touched)
- `check` — verify the table matches what the packs declare; exits non-zero on mismatch

## License

The manifests and vendored agents in this repo are MIT. The upstream packs retain their upstream licenses (see [wshobson/agents](https://github.com/wshobson/agents)).
