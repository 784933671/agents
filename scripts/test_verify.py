#!/usr/bin/env python3
"""Focused tests for repository verification helpers."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify


class VerifyRepositoryChecksTest(unittest.TestCase):
    def make_repo(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name).resolve()
        (repo / ".claude-plugin").mkdir()
        (repo / "plugins" / "demo" / ".claude-plugin").mkdir(parents=True)
        (repo / "plugins" / "demo" / "agents").mkdir()
        (repo / "plugins" / "demo" / "skills" / "demo-skill").mkdir(parents=True)
        (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "demo",
                    "displayName": "Demo",
                    "version": "1.0.0",
                    "description": "Demo plugin.",
                    "author": {"name": "tester"},
                    "repository": "https://example.com/demo",
                    "license": "MIT",
                    "keywords": ["demo"],
                }
            ),
            encoding="utf-8",
        )
        (repo / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps(
                {
                    "plugins": [
                        {
                            "name": "demo",
                            "description": "Demo plugin.",
                            "category": "development",
                            "source": "./plugins/demo",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (repo / "plugins" / "demo" / "skills" / "demo-skill" / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Demo skill.\n---\n",
            encoding="utf-8",
        )
        (repo / "plugins" / "demo" / "agents" / "demo-agent.md").write_text(
            "---\nname: demo-agent\ndescription: Demo agent.\nmodel: inherit\n---\n\n"
            "需要时查阅 `demo-skill` 技能。\n",
            encoding="utf-8",
        )
        return repo

    def patch_repo(self, repo: Path):
        return patch.multiple(
            verify,
            REPO_ROOT=repo,
            MARKETPLACE=repo / ".claude-plugin" / "marketplace.json",
            PLUGINS_DIR=repo / "plugins",
            SYNC_SCRIPT=repo / "scripts" / "sync_agents_table.py",
        )

    def test_secret_scan_rejects_apifox_access_token(self) -> None:
        repo = self.make_repo()
        (repo / "plugins" / "demo" / ".mcp.json").write_text(
            '{"env":{"APIFOX_ACCESS_TOKEN":"' + "afxp_" + '1234567890abcdef"}}',
            encoding="utf-8",
        )

        with self.patch_repo(repo):
            with self.assertRaisesRegex(RuntimeError, "Apifox access token"):
                verify.verify_no_plaintext_secrets()

    def test_plugin_manifest_name_must_match_marketplace_entry(self) -> None:
        repo = self.make_repo()
        (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "wrong-name",
                    "displayName": "Demo",
                    "version": "1.0.0",
                    "description": "Demo plugin.",
                    "author": {"name": "tester"},
                    "repository": "https://example.com/demo",
                    "license": "MIT",
                    "keywords": ["demo"],
                }
            ),
            encoding="utf-8",
        )

        with self.patch_repo(repo):
            with self.assertRaisesRegex(RuntimeError, "plugin manifest name mismatch"):
                verify.verify_json_manifests()

    def test_mcp_servers_path_must_exist(self) -> None:
        repo = self.make_repo()
        (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "demo",
                    "displayName": "Demo",
                    "version": "1.0.0",
                    "description": "Demo plugin.",
                    "author": {"name": "tester"},
                    "repository": "https://example.com/demo",
                    "license": "MIT",
                    "keywords": ["demo"],
                    "mcpServers": "./missing.mcp.json",
                }
            ),
            encoding="utf-8",
        )

        with self.patch_repo(repo):
            with self.assertRaisesRegex(RuntimeError, "mcpServers file does not exist"):
                verify.verify_json_manifests()

    def test_plugin_manifest_version_must_be_semver(self) -> None:
        repo = self.make_repo()
        (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "demo",
                    "displayName": "Demo",
                    "description": "Demo plugin.",
                    "version": "latest",
                    "author": {"name": "tester"},
                    "repository": "https://example.com/demo",
                    "license": "MIT",
                    "keywords": ["demo"],
                }
            ),
            encoding="utf-8",
        )

        with self.patch_repo(repo):
            with self.assertRaisesRegex(RuntimeError, "version must be semver"):
                verify.verify_json_manifests()

    def test_plugin_manifest_metadata_shapes_are_validated(self) -> None:
        repo = self.make_repo()
        (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "demo",
                    "description": "Demo plugin.",
                    "version": "1.0.0",
                    "displayName": "",
                    "author": {"url": "https://example.com"},
                    "repository": "",
                    "license": "",
                    "keywords": ["demo", ""],
                }
            ),
            encoding="utf-8",
        )

        with self.patch_repo(repo):
            with self.assertRaisesRegex(RuntimeError, "displayName must be a non-empty string"):
                verify.verify_json_manifests()

    def test_mcp_user_config_references_must_exist_in_manifest(self) -> None:
        repo = self.make_repo()
        (repo / "plugins" / "demo" / ".mcp.json").write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "demo": {
                            "type": "stdio",
                            "command": "npx",
                            "args": ["demo@latest", "--project-id=${user_config.project_id}"],
                            "env": {"TOKEN": "${user_config.missing_token}"},
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "demo",
                    "displayName": "Demo",
                    "description": "Demo plugin.",
                    "version": "1.0.0",
                    "author": {"name": "tester"},
                    "repository": "https://example.com/demo",
                    "license": "MIT",
                    "keywords": ["demo"],
                    "mcpServers": "./.mcp.json",
                    "userConfig": {
                        "project_id": {
                            "type": "string",
                            "title": "Project ID",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

        with self.patch_repo(repo):
            with self.assertRaisesRegex(RuntimeError, "missing userConfig key"):
                verify.verify_json_manifests()

    def test_agent_skill_links_must_reference_existing_local_skill(self) -> None:
        repo = self.make_repo()
        (repo / "plugins" / "demo" / "agents" / "demo-agent.md").write_text(
            "---\nname: demo-agent\ndescription: Demo agent.\nmodel: inherit\n---\n\n"
            "需要时查阅 `missing-skill` 技能。\n",
            encoding="utf-8",
        )

        with self.patch_repo(repo):
            with self.assertRaisesRegex(RuntimeError, "unknown skill reference"):
                verify.verify_agent_skill_links()

    def test_vue_development_docs_must_stay_javascript_oriented(self) -> None:
        repo = self.make_repo()
        skill_dir = repo / "plugins" / "vue-development" / "skills" / "bad-skill"
        skill_dir.mkdir(parents=True)
        skill_dir.joinpath("SKILL.md").write_text(
            "---\nname: bad-skill\ndescription: Bad skill.\n---\n\n"
            "Use `<script setup lang=\"ts\">` for new components.\n",
            encoding="utf-8",
        )

        with self.patch_repo(repo):
            with self.assertRaisesRegex(RuntimeError, "TypeScript-oriented Vue documentation"):
                verify.verify_vue_development_docs_are_js_only()


if __name__ == "__main__":
    unittest.main()
