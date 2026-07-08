# ZCode Skills Quality Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve ZCode skills discoverability and maintenance checks without changing plugin behavior.

**Architecture:** Extend the existing verifier with one local skill-reference check, add README guidance for when to use skills, make one framework-neutral wording fix in the UI playbook, and add a small maintenance note for generated Vue skills.

**Tech Stack:** Python 3 standard library, Markdown, existing plugin skill directory conventions.

## Global Constraints

- 不新增或删除 skill
- 不大规模改写生成型 Vue skills 的主体内容
- 不引入第三方依赖
- 不调整 marketplace 对外结构
- 不改变 agent 的职责边界
- 本轮实现后不要提交；只保留工作区改动并等待用户确认

---

## File Structure

- Modify `scripts/verify.py`: validate local Markdown references from skill `SKILL.md` files.
- Modify `README.md`: add `Choosing a skill` table and update local verification text.
- Modify `plugins/ui-ux-craft/skills/ui-fix-playbook/SKILL.md`: remove React-specific `useEffect` wording.
- Create `docs/skills-maintenance.md`: document generated Vue skill refresh policy.

---

### Task 1: Add Skill Reference Verification

**Files:**
- Modify: `scripts/verify.py`

**Interfaces:**
- Consumes: `plugins/*/skills/*/SKILL.md`
- Produces: `verify_skill_references()` called from `main()` after `verify_plugin_content()` and before README guide checks

- [ ] **Step 1: Add imports and regex**

Add this import near the existing imports:

```python
import re
```

Add this module constant after `SYNC_SCRIPT`:

```python
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((reference(?:s)?/[^)#]+\.md)(?:#[^)]+)?\)")
```

- [ ] **Step 2: Add verifier**

Add this function after `verify_plugin_content()`:

```python
def verify_skill_references() -> None:
    for skill in sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md")):
        text = read_text(skill)
        skill_dir = skill.parent
        for match in MARKDOWN_LINK_RE.finditer(text):
            link = match.group(1)
            target = (skill_dir / link).resolve()
            try:
                target.relative_to(skill_dir)
            except ValueError as error:
                rel_path = skill.relative_to(REPO_ROOT)
                raise RuntimeError(f"{rel_path} reference escapes skill directory: {link}") from error
            if not target.is_file():
                rel_path = skill.relative_to(REPO_ROOT)
                raise RuntimeError(f"{rel_path} missing skill reference: {link}")

    print("ok: skill references are valid")
```

- [ ] **Step 3: Wire into main**

Update `main()` to call `verify_skill_references()`:

```python
def main() -> int:
    try:
        verify_json_manifests()
        verify_plugin_content()
        verify_skill_references()
        verify_agent_routing_guide()
        verify_agents_table()
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("ok: repository verification passed")
    return 0
```

- [ ] **Step 4: Verify**

Run:

```bash
python3 scripts/verify.py
git diff --check
```

Expected:

```text
ok: json manifests are valid
ok: plugin content structure is valid
ok: skill references are valid
ok: README agent routing guide is in sync
ok: README skill routing guide is in sync
ok: README agents table is in sync.
ok: repository verification passed
```

`git diff --check` should print nothing and exit `0`.

---

### Task 2: Add README Skill Routing Guide

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: current skill names and categories.
- Produces: `Choosing a skill` section after `Choosing an agent`.

- [ ] **Step 1: Add README section**

Add this section after the `Choosing an agent` table and before `Install in ZCode / Claude Code`:

```markdown
## Choosing a skill

Use skills for focused knowledge, API patterns, and lightweight guidance. Use agents when the task needs a larger audit, repair, or test workflow.

| Skill | Use when |
|-------|----------|
| `vue` | You need Vue API, SFC, reactivity, lifecycle, watcher, or `<script setup>` guidance. |
| `vue-best-practices` | You need Vue architecture, component boundaries, data flow, composables, or implementation standards. |
| `pinia` | You need store design, state/getters/actions, SSR, HMR, or testing guidance. |
| `vue-router-best-practices` | You need route guard, route params, redirect loop, or route lifecycle guidance. |
| `vite` | You need Vite config, plugin, build, SSR, environment, or Rolldown migration guidance. |
| `wcag-essentials` | You need WCAG A/AA, ARIA, keyboard, focus, contrast, or accessible component guidance. |
| `ui-fix-playbook` | You need UI defect triage, root cause isolation, minimal repair, or regression verification guidance. |
| `ux-test-design` | You need user-flow test design, state coverage, test cases, or defect report structure. |
```

- [ ] **Step 2: Update local verification sentence**

Replace the current local verification sentence with:

```markdown
It validates JSON manifests, plugin content structure, skill reference links, the README routing guides, and the generated README agents table.
```

- [ ] **Step 3: Verify**

Run:

```bash
python3 scripts/verify.py
git diff --check
```

Expected output includes:

```text
ok: skill references are valid
```

---

### Task 3: Make UI Fix Playbook Framework-Neutral

**Files:**
- Modify: `plugins/ui-ux-craft/skills/ui-fix-playbook/SKILL.md`

**Interfaces:**
- Consumes: existing state bug table.
- Produces: framework-neutral wording.

- [ ] **Step 1: Replace React-specific row**

Replace this row:

```markdown
| 切换后状态错乱 | 未清理上一次的副作用 | useEffect 清理 |
```

with:

```markdown
| 切换后状态错乱 | 未清理上一次的监听器、定时器或请求副作用 | 在状态切换或组件卸载时清理副作用 |
```

- [ ] **Step 2: Verify**

Run:

```bash
python3 scripts/verify.py
git diff --check
```

Expected output includes:

```text
ok: skill references are valid
```

---

### Task 4: Add Generated Skill Maintenance Note

**Files:**
- Create: `docs/skills-maintenance.md`

**Interfaces:**
- Consumes: current generated Vue skill metadata.
- Produces: maintenance policy documentation.

- [ ] **Step 1: Create maintenance note**

Create `docs/skills-maintenance.md` with:

```markdown
# Skills Maintenance

This repository contains hand-authored UI/UX skills and generated Vue ecosystem skills.

## Generated Vue Skills

The following skills are generated or derived from upstream documentation:

- `vue`
- `pinia`
- `vite`
- `vue-best-practices`
- `vue-router-best-practices`

Refresh these skills when:

- upstream Vue, Pinia, Vue Router, or Vite releases materially change APIs or best practices;
- a skill references beta behavior that has stabilized or changed;
- ZCode routing or skill-loading behavior changes;
- repository verification starts failing because referenced files move or disappear.

Keep generated skill refreshes separate from hand-authored content edits so review can distinguish source sync from local policy changes.

## Hand-authored UI/UX Skills

The following skills are maintained directly in this repository:

- `ui-fix-playbook`
- `ux-test-design`
- `wcag-essentials`

Keep these framework-neutral unless a skill explicitly scopes itself to a framework.
```

- [ ] **Step 2: Verify**

Run:

```bash
python3 scripts/verify.py
git diff --check
git status --short
```

Expected:

```text
ok: json manifests are valid
ok: plugin content structure is valid
ok: skill references are valid
ok: README agent routing guide is in sync
ok: README skill routing guide is in sync
ok: README agents table is in sync.
ok: repository verification passed
```

`git diff --check` should print nothing and exit `0`; `git status --short` should show the modified/untracked files only. Do not stage or commit.

---

## Final Verification

- [ ] Run:

```bash
python3 scripts/verify.py
git diff --check
git status --short --branch
```

Expected:

```text
ok: json manifests are valid
ok: plugin content structure is valid
ok: skill references are valid
ok: README agent routing guide is in sync
ok: README skill routing guide is in sync
ok: README agents table is in sync.
ok: repository verification passed
```

Worktree should contain only unstaged changes from this plan. No commit should be created until the user explicitly asks.

## Self-Review

- Spec coverage: Task 1 covers skill reference integrity, Task 2 covers README skill routing and verification wording, Task 3 removes framework-specific UI playbook wording, Task 4 adds generated skill maintenance guidance.
- Placeholder scan: no deferred-work wording remains.
- Type consistency: `verify_skill_references()` is called by `main()` and uses existing `read_text()` and `PLUGINS_DIR`.
