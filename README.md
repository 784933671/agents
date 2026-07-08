# 784933671-agents

A **subagent collection** for ZCode / Claude Code, packaged as a plugin marketplace. One-click install gives you categorized agent packs covering UI/UX craft and Vue development — all self-hosted in this repo.

## What's inside

Two vendored packs live in this marketplace, each a set of locally authored agents served directly from `plugins/`:

<!-- AGENTS-TABLE:START -->
| Pack | Category | Agents |
|------|----------|--------|
| `ui-ux-craft` | design | accessibility-tester, ui-designer, ui-fixer, ui-ux-tester |
| `vue-development` | development | vue-expert |

Total: **2 packs, 5 agents**.

<!-- AGENTS-TABLE:END -->

## Choosing an agent

| Agent | Use when |
|-------|----------|
| `ui-designer` | You need UI design direction, layout decisions, interaction states, or design system alignment. |
| `ui-fixer` | You have a reproduced UI bug, layout issue, style regression, or responsive breakpoint problem. |
| `ui-ux-tester` | You need end-to-end UI/UX flow testing, state coverage, or a structured defect report. |
| `accessibility-tester` | You need keyboard, focus, ARIA, contrast, screen reader, or WCAG A/AA review. |
| `vue-expert` | You need Vue 3, Composition API, Pinia, Vue Router, Vite, SFC, reactivity, or component architecture help. |

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

The agents table above (between the `AGENTS-TABLE` markers) is generated from `marketplace.json` and the resolved `agents/` directories — **don't hand-edit it**.

After any change to `marketplace.json` or a pack's `agents/`, refresh the table:

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

It validates JSON manifests, plugin content structure, the README routing guide in `Choosing an agent`, and the generated README agents table.

## License

MIT.
