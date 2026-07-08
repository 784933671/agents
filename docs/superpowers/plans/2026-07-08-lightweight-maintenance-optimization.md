# Lightweight Maintenance Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a low-risk repository verification path and align documentation with the current two-pack plugin marketplace.

**Architecture:** Keep the existing marketplace and plugin package structure unchanged. Add one focused Python standard-library verification script, update docs to describe the current state, and wire the same verification script into GitHub Actions.

**Tech Stack:** Python 3 standard library, GitHub Actions, Markdown, existing `scripts/sync_agents_table.py`.

## Global Constraints

- Do not add plugin packs.
- Do not modify agent, command, or skill semantics.
- Do not adjust the marketplace public structure.
- Do not introduce third-party dependencies.
- Do not perform large directory restructuring.
- Keep outputs concise and actionable.

---

## File Structure

- Create `scripts/verify.py`: single repository verification entry point.
- Modify `README.md`: document current two-pack scope and local verification command.
- Modify `docs/superpowers/specs/2026-07-07-local-agents-packaging-design.md`: mark as historical and append current implementation status.
- Create `.github/workflows/verify.yml`: run local verification on push and pull request.
- Use existing `scripts/sync_agents_table.py`: no behavior changes required.

---

### Task 1: Add Repository Verification Script

**Files:**
- Create: `scripts/verify.py`

**Interfaces:**
- Consumes: `.claude-plugin/marketplace.json`, `plugins/*/.claude-plugin/plugin.json`, `scripts/sync_agents_table.py check`
- Produces: CLI command `python3 scripts/verify.py` returning `0` on success and non-zero on failure

- [ ] **Step 1: Write the script**

Create `scripts/verify.py` with:

```python
#!/usr/bin/env python3
"""Run repository checks before publishing plugin marketplace changes."""

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = REPO_ROOT / "plugins"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_agents_table.py"


def load_json(path: Path) -> object:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise RuntimeError(f"missing JSON manifest: {path.relative_to(REPO_ROOT)}")
    except json.JSONDecodeError as error:
        rel_path = path.relative_to(REPO_ROOT)
        raise RuntimeError(f"invalid JSON in {rel_path}: {error}") from error


def verify_json_manifests() -> None:
    marketplace = load_json(MARKETPLACE)
    if not isinstance(marketplace, dict):
        raise RuntimeError(".claude-plugin/marketplace.json must contain a JSON object")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise RuntimeError(".claude-plugin/marketplace.json must define a non-empty plugins array")

    for plugin in plugins:
        if not isinstance(plugin, dict):
            raise RuntimeError("each marketplace plugin entry must be a JSON object")

        source = plugin.get("source")
        if not isinstance(source, str) or not source.startswith("./plugins/"):
            continue

        plugin_dir = (REPO_ROOT / source).resolve()
        try:
            plugin_dir.relative_to(REPO_ROOT)
        except ValueError as error:
            raise RuntimeError(f"plugin source escapes repository: {source}") from error

        load_json(plugin_dir / ".claude-plugin" / "plugin.json")

    for manifest in sorted(PLUGINS_DIR.glob("*/.claude-plugin/plugin.json")):
        load_json(manifest)

    print("ok: json manifests are valid")


def verify_agents_table() -> None:
    result = subprocess.run(
        [sys.executable, str(SYNC_SCRIPT), "check"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        raise RuntimeError("README agents table check failed")


def main() -> int:
    try:
        verify_json_manifests()
        verify_agents_table()
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("ok: repository verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run verification**

Run:

```bash
python3 scripts/verify.py
```

Expected:

```text
ok: json manifests are valid
ok: README agents table is in sync.
ok: repository verification passed
```

- [ ] **Step 3: Commit**

Run:

```bash
git add scripts/verify.py
git commit -m "chore: add repository verification script"
```

---

### Task 2: Align Documentation With Current Marketplace

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-07-07-local-agents-packaging-design.md`

**Interfaces:**
- Consumes: current marketplace entries from `.claude-plugin/marketplace.json`
- Produces: documentation that describes the current two-pack marketplace and verification command

- [ ] **Step 1: Update README**

In `README.md`, keep the generated agents table unchanged and add a local verification section after "Keeping the table in sync":

````markdown
## Local verification

Before publishing marketplace changes, run the repository verifier:

```bash
python3 scripts/verify.py
```

It validates JSON manifests and checks that the generated README agents table matches the marketplace.
````

Also make the structure section explicitly list the two current packs:

```markdown
plugins/                 ← all current packs live here
├── ui-ux-craft/         ← UI design, fixing, UX testing, accessibility
└── vue-development/     ← Vue 3 / Composition API / Pinia / Vite
```

- [ ] **Step 2: Update historical design doc**

At the top of `docs/superpowers/specs/2026-07-07-local-agents-packaging-design.md`, add:

```markdown
> **历史设计说明**: 本文记录 2026-07-07 的初始打包方案。当前仓库已精简为 `ui-ux-craft` 与 `vue-development` 两个本地插件包，不再保留本文中的四包方案或上游包共存方案。
```

At the end of the same file, add:

```markdown
## 当前实现状态

截至 2026-07-08，仓库实际维护两个本地插件包:

- `ui-ux-craft`: UI/UX 设计、走查、修复与无障碍审计
- `vue-development`: Vue 3 / Composition API / Pinia / Vue Router / Vite 开发辅助

后续维护以 `.claude-plugin/marketplace.json` 和 README 中的 generated agents table 为准。
```

- [ ] **Step 3: Run verification**

Run:

```bash
python3 scripts/verify.py
```

Expected:

```text
ok: json manifests are valid
ok: README agents table is in sync.
ok: repository verification passed
```

- [ ] **Step 4: Commit**

Run:

```bash
git add README.md docs/superpowers/specs/2026-07-07-local-agents-packaging-design.md
git commit -m "docs: align marketplace maintenance docs"
```

---

### Task 3: Add CI Verification Workflow

**Files:**
- Create: `.github/workflows/verify.yml`

**Interfaces:**
- Consumes: `scripts/verify.py`
- Produces: GitHub Actions workflow named `Verify`

- [ ] **Step 1: Create workflow**

Create `.github/workflows/verify.yml` with:

```yaml
name: Verify

on:
  push:
    paths:
      - ".claude-plugin/**"
      - ".github/workflows/verify.yml"
      - "README.md"
      - "plugins/**"
      - "scripts/**"
  pull_request:
    paths:
      - ".claude-plugin/**"
      - ".github/workflows/verify.yml"
      - "README.md"
      - "plugins/**"
      - "scripts/**"

jobs:
  verify:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run repository verification
        run: python3 scripts/verify.py
```

- [ ] **Step 2: Run local verification**

Run:

```bash
python3 scripts/verify.py
```

Expected:

```text
ok: json manifests are valid
ok: README agents table is in sync.
ok: repository verification passed
```

- [ ] **Step 3: Inspect final diff**

Run:

```bash
git diff --stat
git diff --check
```

Expected:

```text
```

`git diff --check` should print nothing and exit `0`.

- [ ] **Step 4: Commit**

Run:

```bash
git add .github/workflows/verify.yml
git commit -m "ci: verify plugin marketplace"
```

---

## Final Verification

- [ ] Run:

```bash
python3 scripts/verify.py
git status --short
```

Expected:

```text
ok: json manifests are valid
ok: README agents table is in sync.
ok: repository verification passed
```

`git status --short` should be empty after all commits.

## Self-Review

- Spec coverage: Task 1 covers the unified verifier, Task 2 covers documentation consistency, Task 3 covers CI verification.
- Placeholder scan: no placeholder markers or deferred-work wording remains.
- Type consistency: the only produced command is `python3 scripts/verify.py`; the workflow and docs consume the same command.
