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
