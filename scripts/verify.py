#!/usr/bin/env python3
"""Run repository checks before publishing plugin marketplace changes."""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = REPO_ROOT / "plugins"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_agents_table.py"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((reference(?:s)?/[^)#]+\.md)(?:#[^)]+)?\)")
AGENT_SKILL_LINK_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`\s*技能")
SEMVER_RE = re.compile(
    r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z]+(?:\.[0-9A-Za-z]+)*)?(?:\+[0-9A-Za-z]+(?:\.[0-9A-Za-z]+)*)?$"
)
USER_CONFIG_REF_RE = re.compile(r"\$\{user_config\.([A-Za-z0-9_-]+)\}")
VUE_JS_ONLY_ENTRYPOINT_RE = re.compile(
    r"TypeScript|typescript|lang=[\"']ts[\"']|vue-tsc|vite\.config\.ts|defineProps<|defineEmits<|InjectionKey|import type"
)
SECRET_PATTERNS = (
    ("Apifox access token", re.compile(r"\bafxp_[A-Za-z0-9]{12,}\b")),
)
SKIPPED_SCAN_DIRS = {".git", ".cache", "node_modules"}


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


def verify_no_plaintext_secrets() -> None:
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or SKIPPED_SCAN_DIRS.intersection(path.relative_to(REPO_ROOT).parts):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError as error:
            raise RuntimeError(f"cannot scan {path.relative_to(REPO_ROOT)}: {error}") from error

        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                raise RuntimeError(f"{path.relative_to(REPO_ROOT)} contains plaintext secret: {label}")

    print("ok: no plaintext secrets detected")


def require_manifest_string(manifest: dict, field: str, manifest_path: Path) -> str:
    value = manifest.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(
            f"{manifest_path.relative_to(REPO_ROOT)} {field} must be a non-empty string"
        )
    return value


def verify_plugin_metadata(manifest: dict, manifest_path: Path) -> None:
    version = require_manifest_string(manifest, "version", manifest_path)
    if not SEMVER_RE.fullmatch(version):
        raise RuntimeError(
            f"{manifest_path.relative_to(REPO_ROOT)} version must be semver (MAJOR.MINOR.PATCH)"
        )

    for field in ("displayName", "description", "repository", "license"):
        require_manifest_string(manifest, field, manifest_path)

    author = manifest.get("author")
    if not isinstance(author, dict):
        raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} author must be an object")
    author_name = author.get("name")
    if not isinstance(author_name, str) or not author_name.strip():
        raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} author.name must be a non-empty string")
    author_url = author.get("url")
    if author_url is not None and (not isinstance(author_url, str) or not author_url.strip()):
        raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} author.url must be a non-empty string")

    keywords = manifest.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} keywords must be a non-empty array")
    if any(not isinstance(keyword, str) or not keyword.strip() for keyword in keywords):
        raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} keywords must contain only non-empty strings")

    user_config = manifest.get("userConfig")
    if user_config is None:
        return
    if not isinstance(user_config, dict):
        raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} userConfig must be an object")
    for key, config in user_config.items():
        if not isinstance(key, str) or not key.strip():
            raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} userConfig keys must be non-empty strings")
        if not isinstance(config, dict):
            raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} userConfig.{key} must be an object")
        config_type = config.get("type")
        if not isinstance(config_type, str) or not config_type.strip():
            raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} userConfig.{key}.type must be a non-empty string")
        description = config.get("description")
        if description is not None and (not isinstance(description, str) or not description.strip()):
            raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} userConfig.{key}.description must be a non-empty string")


def verify_plugin_manifest(plugin_dir: Path, expected_name: Optional[str] = None) -> dict:
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} must contain a JSON object")

    actual_name = manifest.get("name")
    if not isinstance(actual_name, str) or not actual_name:
        raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} missing plugin name")

    if actual_name != plugin_dir.name:
        raise RuntimeError(
            f"plugin manifest name mismatch: {plugin_dir.relative_to(REPO_ROOT)} declares `{actual_name}`"
        )
    if expected_name is not None and actual_name != expected_name:
        raise RuntimeError(
            f"plugin manifest name mismatch: marketplace declares `{expected_name}` but manifest declares `{actual_name}`"
        )

    verify_plugin_metadata(manifest, manifest_path)

    mcp_servers = manifest.get("mcpServers")
    if mcp_servers is not None:
        if not isinstance(mcp_servers, str) or not mcp_servers:
            raise RuntimeError(f"{manifest_path.relative_to(REPO_ROOT)} mcpServers must be a path string")

        mcp_path = (plugin_dir / mcp_servers).resolve()
        try:
            mcp_path.relative_to(plugin_dir)
        except ValueError as error:
            raise RuntimeError(
                f"{manifest_path.relative_to(REPO_ROOT)} mcpServers path escapes plugin directory"
            ) from error
        if not mcp_path.is_file():
            raise RuntimeError(f"mcpServers file does not exist: {mcp_path.relative_to(REPO_ROOT)}")

        user_config = manifest.get("userConfig", {})
        user_config_keys = set(user_config) if isinstance(user_config, dict) else set()
        for key in sorted(set(USER_CONFIG_REF_RE.findall(read_text(mcp_path)))):
            if key not in user_config_keys:
                raise RuntimeError(
                    f"{mcp_path.relative_to(REPO_ROOT)} references missing userConfig key: {key}"
                )

    return manifest


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

        plugin_name = plugin.get("name")
        if not isinstance(plugin_name, str) or not plugin_name:
            raise RuntimeError("each marketplace plugin entry must define a non-empty name")

        source = plugin.get("source")
        if not isinstance(source, str) or not source.startswith("./plugins/"):
            continue

        plugin_dir = (REPO_ROOT / source).resolve()
        try:
            plugin_dir.relative_to(REPO_ROOT)
        except ValueError as error:
            raise RuntimeError(f"plugin source escapes repository: {source}") from error

        verify_plugin_manifest(plugin_dir, plugin_name)

    for manifest in sorted(PLUGINS_DIR.glob("*/.claude-plugin/plugin.json")):
        verify_plugin_manifest(manifest.parents[1])

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


def verify_vue_development_entrypoints_are_js_only() -> None:
    vue_plugin_dir = PLUGINS_DIR / "vue-development"
    if not vue_plugin_dir.is_dir():
        return

    entrypoints = [
        *sorted(vue_plugin_dir.glob("skills/*/SKILL.md")),
        *sorted((vue_plugin_dir / "agents").glob("*.md")),
        *sorted((vue_plugin_dir / "commands").glob("*.md")),
    ]
    for entrypoint in entrypoints:
        match = VUE_JS_ONLY_ENTRYPOINT_RE.search(read_text(entrypoint))
        if match:
            raise RuntimeError(
                f"{entrypoint.relative_to(REPO_ROOT)} contains TypeScript-oriented entrypoint text: {match.group(0)}"
            )

    print("ok: vue-development entrypoints are JavaScript-oriented")


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


def local_skill_names(plugin_dir: Path) -> set[str]:
    return {
        parse_frontmatter(skill).get("name", "")
        for skill in sorted((plugin_dir / "skills").glob("*/SKILL.md"))
    } - {""}


def verify_agent_skill_links() -> None:
    for agent in sorted(PLUGINS_DIR.glob("*/agents/*.md")):
        plugin_dir = agent.parents[1]
        skill_names = local_skill_names(plugin_dir)
        text = read_text(agent)
        body_start = text.find("\n---", 4)
        body = text[body_start + 4 :] if body_start != -1 else text

        for skill_name in sorted(set(AGENT_SKILL_LINK_RE.findall(body))):
            if skill_name not in skill_names:
                raise RuntimeError(
                    f"{agent.relative_to(REPO_ROOT)} unknown skill reference: `{skill_name}`"
                )

    print("ok: agent skill links are valid")


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

    actual_names = read_readme_table_names("## 选择代理", "代理")
    missing = sorted(expected_names - actual_names)
    unknown = sorted(actual_names - expected_names)

    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown: {', '.join(unknown)}")
        raise RuntimeError(f"README `选择代理` table is out of sync ({'; '.join(details)})")

    print("ok: README agent routing guide is in sync")


def verify_skill_routing_guide() -> None:
    expected_names = {
        parse_frontmatter(skill).get("name", "")
        for skill in sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md"))
    }
    expected_names.discard("")

    actual_names = read_readme_table_names("## 选择技能", "技能")
    missing = sorted(expected_names - actual_names)
    unknown = sorted(actual_names - expected_names)

    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if unknown:
            details.append(f"unknown: {', '.join(unknown)}")
        raise RuntimeError(f"README `选择技能` table is out of sync ({'; '.join(details)})")

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
        verify_no_plaintext_secrets()
        verify_json_manifests()
        verify_plugin_content()
        verify_vue_development_entrypoints_are_js_only()
        verify_skill_references()
        verify_agent_skill_links()
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
