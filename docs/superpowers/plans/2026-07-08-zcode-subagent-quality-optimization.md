# ZCode Subagent Quality Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve ZCode subagent routing clarity and repository validation without changing plugin behavior.

**Architecture:** Keep marketplace structure unchanged. Make one agent metadata-only update, extend the existing Python verifier with focused Markdown/frontmatter checks, and add a README routing guide that documents when to choose each current agent.

**Tech Stack:** Python 3 standard library, Markdown plugin conventions, existing `scripts/verify.py` and `scripts/sync_agents_table.py`.

## Global Constraints

- 不新增插件包
- 不新增或删除 agent、command、skill
- 不修改 agent 的核心工作模式和职责边界
- 不引入第三方依赖
- 不调整 marketplace 对外结构
- 不做大规模重构

---

## File Structure

- Modify `plugins/vue-development/agents/vue-expert.md`: update only frontmatter `description`.
- Modify `scripts/verify.py`: add lightweight plugin content structure validation.
- Modify `README.md`: add a `Choosing an agent` section.

---

### Task 1: Update Vue Expert Routing Description

**Files:**
- Modify: `plugins/vue-development/agents/vue-expert.md`

**Interfaces:**
- Consumes: current `vue-expert` frontmatter and body.
- Produces: `vue-expert` frontmatter `description` using the same "主动用于" routing style as UI agents.

- [ ] **Step 1: Update frontmatter description**

Change only the `description` line in `plugins/vue-development/agents/vue-expert.md` to:

```yaml
description: "Vue 开发专家。主动用于：Vue 3 组件实现、Composition API 与 <script setup>、响应式陷阱排查、组件架构设计、Pinia 状态管理、Vue Router 路由行为、Vite 构建配置、渲染性能优化。涉及 Vue、Pinia、Vue Router、Vite、SFC、响应式、组件通信等场景时使用。"
```

- [ ] **Step 2: Run verification**

Run:

```bash
python3 scripts/verify.py
git diff --check
```

Expected:

```text
ok: json manifests are valid
ok: README agents table is in sync.
ok: repository verification passed
```

`git diff --check` should print nothing and exit `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add plugins/vue-development/agents/vue-expert.md
git commit -m "docs: improve vue expert routing description"
```

---

### Task 2: Add Plugin Content Structure Verification

**Files:**
- Modify: `scripts/verify.py`

**Interfaces:**
- Consumes: `plugins/*/agents/*.md`, `plugins/*/commands/*.md`, `plugins/*/skills/*/SKILL.md`, `.claude-plugin/marketplace.json`
- Produces: `verify_plugin_content()` function called from `main()` before `verify_agents_table()`

- [ ] **Step 1: Add frontmatter parser and content checks**

Update `scripts/verify.py` to include these functions after `verify_json_manifests()`:

```python
def parse_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise RuntimeError(f"cannot read {path.relative_to(REPO_ROOT)}: {error}") from error

    if not text.startswith("---\n"):
        raise RuntimeError(f"missing frontmatter: {path.relative_to(REPO_ROOT)}")

    end = text.find("\n---", 4)
    if end == -1:
        raise RuntimeError(f"unterminated frontmatter: {path.relative_to(REPO_ROOT)}")

    fields = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")
    return fields


def require_fields(path: Path, fields: dict, required: tuple[str, ...]) -> None:
    missing = [field for field in required if not fields.get(field)]
    if missing:
        rel_path = path.relative_to(REPO_ROOT)
        raise RuntimeError(f"{rel_path} missing frontmatter field(s): {', '.join(missing)}")


def verify_plugin_content() -> None:
    marketplace = load_json(MARKETPLACE)
    plugins = marketplace.get("plugins", []) if isinstance(marketplace, dict) else []

    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        source = plugin.get("source")
        if isinstance(source, str) and source.startswith("./plugins/"):
            plugin_dir = (REPO_ROOT / source).resolve()
            if not plugin_dir.is_dir():
                raise RuntimeError(f"plugin source does not exist: {source}")

    for agent in sorted(PLUGINS_DIR.glob("*/agents/*.md")):
        fields = parse_frontmatter(agent)
        require_fields(agent, fields, ("name", "description", "model"))
        if fields["name"] != agent.stem:
            rel_path = agent.relative_to(REPO_ROOT)
            raise RuntimeError(f"{rel_path} frontmatter name must match filename stem")

    for command in sorted(PLUGINS_DIR.glob("*/commands/*.md")):
        text = command.read_text(encoding="utf-8")
        if "$ARGUMENTS" not in text:
            raise RuntimeError(f"{command.relative_to(REPO_ROOT)} must contain $ARGUMENTS")

    for skill in sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md")):
        fields = parse_frontmatter(skill)
        require_fields(skill, fields, ("name", "description"))

    print("ok: plugin content structure is valid")
```

Then update `main()` to call the new function:

```python
def main() -> int:
    try:
        verify_json_manifests()
        verify_plugin_content()
        verify_agents_table()
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("ok: repository verification passed")
    return 0
```

- [ ] **Step 2: Run verification**

Run:

```bash
python3 scripts/verify.py
git diff --check
```

Expected:

```text
ok: json manifests are valid
ok: plugin content structure is valid
ok: README agents table is in sync.
ok: repository verification passed
```

`git diff --check` should print nothing and exit `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add scripts/verify.py
git commit -m "chore: verify plugin content structure"
```

---

### Task 3: Add README Agent Routing Guide

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: current agent names and descriptions.
- Produces: `Choosing an agent` section in README.

- [ ] **Step 1: Add routing guide**

In `README.md`, add this section after the generated agents table and before `Install in ZCode / Claude Code`:

```markdown
## Choosing an agent

| Agent | Use when |
|-------|----------|
| `ui-designer` | You need UI design direction, layout decisions, interaction states, or design system alignment. |
| `ui-fixer` | You have a reproduced UI bug, layout issue, style regression, or responsive breakpoint problem. |
| `ui-ux-tester` | You need end-to-end UI/UX flow testing, state coverage, or a structured defect report. |
| `accessibility-tester` | You need keyboard, focus, ARIA, contrast, screen reader, or WCAG A/AA review. |
| `vue-expert` | You need Vue 3, Composition API, Pinia, Vue Router, Vite, SFC, reactivity, or component architecture help. |
```

- [ ] **Step 2: Run verification**

Run:

```bash
python3 scripts/verify.py
git diff --check
```

Expected:

```text
ok: json manifests are valid
ok: plugin content structure is valid
ok: README agents table is in sync.
ok: repository verification passed
```

`git diff --check` should print nothing and exit `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add README.md
git commit -m "docs: add agent routing guide"
```

---

## Final Verification

- [ ] Run:

```bash
python3 scripts/verify.py
git diff --check
git status --short
```

Expected:

```text
ok: json manifests are valid
ok: plugin content structure is valid
ok: README agents table is in sync.
ok: repository verification passed
```

`git diff --check` should print nothing and exit `0`; `git status --short` should be empty after all commits.

## Self-Review

- Spec coverage: Task 1 covers `vue-expert` routing text, Task 2 covers structure verification, Task 3 covers README agent choice guidance.
- Placeholder scan: no deferred-work wording remains.
- Type consistency: all tasks use the same command `python3 scripts/verify.py`; `verify_plugin_content()` is called by `main()` and has no external dependencies.
