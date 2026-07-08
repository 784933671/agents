#!/usr/bin/env python3
"""Run repository checks before publishing plugin marketplace changes."""

import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = REPO_ROOT / "plugins"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_agents_table.py"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((reference(?:s)?/[^)#]+\.md)(?:#[^)]+)?\)")


def load_json(path: Path) -> object:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise RuntimeError(f"missing JSON manifest: {path.relative_to(REPO_ROOT)}")
    except json.JSONDecodeError as error:
        rel_path = path.relative_to(REPO_ROOT)
        raise RuntimeError(f"invalid JSON in {rel_path}: {error}") from error


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise RuntimeError(f"cannot read {path.relative_to(REPO_ROOT)}: {error}") from error


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


def parse_frontmatter(path: Path) -> dict:
    text = read_text(path)

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
        text = read_text(command)
        if "$ARGUMENTS" not in text:
            raise RuntimeError(f"{command.relative_to(REPO_ROOT)} must contain $ARGUMENTS")

    for skill in sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md")):
        fields = parse_frontmatter(skill)
        require_fields(skill, fields, ("name", "description"))

    print("ok: plugin content structure is valid")


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


def read_readme_table_names(heading: str, label: str) -> set[str]:
    readme = read_text(REPO_ROOT / "README.md")
    start = readme.find(heading)
    if start == -1:
        raise RuntimeError(f"README missing `{heading.removeprefix('## ')}` section")

    section = readme[start + len(heading) :]
    next_heading = section.find("\n## ")
    if next_heading != -1:
        section = section[:next_heading]

    names: set[str] = set()
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2 or cells[0] == label or set(cells[0]) <= {"-", ":"}:
            continue

        name = cells[0].strip("`")
        if name:
            names.add(name)

    if not names:
        raise RuntimeError(f"README `{heading.removeprefix('## ')}` table has no {label.lower()} rows")

    return names


def verify_agent_routing_guide() -> None:
    expected_names = {
        parse_frontmatter(agent).get("name", "")
        for agent in sorted(PLUGINS_DIR.glob("*/agents/*.md"))
    }
    expected_names.discard("")

    actual_names = read_readme_table_names("## Choosing an agent", "Agent")
    missing = sorted(expected_names - actual_names)
    unknown = sorted(actual_names - expected_names)

    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown: {', '.join(unknown)}")
        raise RuntimeError(f"README `Choosing an agent` table is out of sync ({'; '.join(details)})")

    print("ok: README agent routing guide is in sync")


def verify_skill_routing_guide() -> None:
    expected_names = {
        parse_frontmatter(skill).get("name", "")
        for skill in sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md"))
    }
    expected_names.discard("")

    actual_names = read_readme_table_names("## Choosing a skill", "Skill")
    missing = sorted(expected_names - actual_names)
    unknown = sorted(actual_names - expected_names)

    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown: {', '.join(unknown)}")
        raise RuntimeError(f"README `Choosing a skill` table is out of sync ({'; '.join(details)})")

    print("ok: README skill routing guide is in sync")


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
        verify_plugin_content()
        verify_skill_references()
        verify_agent_routing_guide()
        verify_skill_routing_guide()
        verify_agents_table()
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print("ok: repository verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
