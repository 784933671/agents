# 784933671-agents

A curated multi-category **subagent collection** for ZCode / Claude Code, packaged as a plugin marketplace. One-click install gives you categorized agent packs sourced from high-quality community repos.

## What's inside

Currently bundles agent packs from [`wshobson/agents`](https://github.com/wshobson/agents), pinned to commit `5cc2549a` (2026-06-25).

| Pack | Category | Agents |
|------|----------|--------|
| `frontend-mobile-development` | development | frontend-developer, mobile-developer |
| `backend-development` | development | backend-architect, event-sourcing-architect, graphql-architect, performance-engineer, security-auditor, tdd-orchestrator, temporal-python-pro, test-automator |
| `javascript-typescript` | development | javascript-pro, typescript-pro |
| `debugging-toolkit` | development | debugger, dx-optimizer |
| `code-refactoring` | development | code-reviewer, legacy-modernizer |
| `ui-design` | design | accessibility-expert, design-system-architect, ui-designer |

Total: **6 packs, 19 agents**.

## Install in ZCode / Claude Code

1. Open your client's plugin marketplace settings.
2. Add a marketplace with this repo's URL:
   ```
   https://github.com/784933671/agents.git
   ```
3. Browse the marketplace and install whichever pack(s) you want.

The client reads `.claude-plugin/marketplace.json` to discover the packs. Each pack is fetched on demand via `git-subdir` from the pinned commit — nothing is vendored here.

## How it's structured

```
.claude-plugin/
└── marketplace.json     ← declares the 6 packs (this is all you need)
plugins/                 ← reserved for any future self-hosted packs
```

This repo only ships the **manifest**. The actual agent `.md` files live in the source repos and are pulled by reference (`git-subdir` + `sha`). This keeps the repo tiny and lets upstream updates flow in by bumping the pinned commit.

## Updating the pin

To pick up new agents from upstream:

1. Get the latest SHA of the source repo:
   ```bash
   curl -s https://api.github.com/repos/wshobson/agents/commits/main | python3 -c "import sys,json; print(json.load(sys.stdin)['sha'])"
   ```
2. Replace the `sha` field in `.claude-plugin/marketplace.json` (and `ref` if the branch changed).
3. Commit and push.

## Adding more source repos

Add new entries to the `plugins` array in `marketplace.json`. Supported source types:

- `git-subdir` — pull a subdirectory from a git repo (used here)
- `url` — pull an entire git repo as a plugin
- local path — `./plugins/your-pack` if you vendor your own

Each entry needs `name`, `description`, `category`, `source`, and ideally `homepage`.

## License

The manifest in this repo is MIT. The bundled agents retain their upstream licenses (see [wshobson/agents](https://github.com/wshobson/agents)).
