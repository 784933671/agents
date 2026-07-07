# 784933671-agents

A multi-category **subagent collection** for ZCode / Claude Code, packaged as a plugin marketplace. One-click install gives you categorized agent packs covering frontend, UI/UX craft, diagnostics, and engineering — all self-hosted in this repo.

## What's inside

Four vendored packs live in this marketplace, each a set of locally authored agents (originally from `~/.zcode/agents/`) served directly from `plugins/`:

<!-- AGENTS-TABLE:START -->
| Pack | Category | Agents |
|------|----------|--------|
| `web-frontend` | development | frontend-developer, javascript-pro, nextjs-developer, react-specialist, typescript-pro, vue-expert |
| `ui-ux-craft` | design | accessibility-tester, ui-designer, ui-fixer, ui-ux-tester |
| `diagnostics` | development | browser-debugger, performance-engineer |
| `engineering` | development | build-engineer, code-mapper, documentation-engineer, refactoring-specialist |

Total: **4 packs, 16 agents**.

<!-- AGENTS-TABLE:END -->

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
├── web-frontend/        ← React, Vue, Next.js, JS, TS specialists
├── ui-ux-craft/         ← UI design, fixing, UX testing, accessibility
├── diagnostics/         ← browser debugging + performance engineering
└── engineering/         ← build, code mapping, docs, refactoring
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

The agents table above (between the `AGENTS-TABLE` markers) is generated from `marketplace.json` and the resolved `agents/` directories — **don't hand-edit it**.

After any change to `marketplace.json` or a pack's `agents/`, refresh the table:

```bash
python scripts/sync_agents_table.py update
```

Other useful subcommands:

- `generate` — print the expected table to stdout (no files touched)
- `check` — verify the table matches what the packs declare; exits non-zero on mismatch

CI (`.github/workflows/verify-agents-table.yml`) runs `check` on changes to `marketplace.json`, `README.md`, or the script itself, and fails the build if the table drifts.

## License

MIT.
