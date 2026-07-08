#!/usr/bin/env python3
"""Keep README's plugin contents table in sync with marketplace.json.

Subcommands:
  check     build the expected table, compare to README, exit 1 on mismatch
  update    build the expected table, rewrite README's table block in place
  generate  build the expected table, print it to stdout

For each plugin in marketplace.json, resolves local agents and skills by source kind:
  git-subdir   -> GitHub Contents API at the pinned sha (set GITHUB_TOKEN
                  in CI to raise the rate limit)
  local path   -> read ./<path>/agents/ directly from this repo

No third-party dependencies (Python 3.7+ stdlib only).
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKETPLACE = os.path.join(REPO_ROOT, ".claude-plugin", "marketplace.json")
README = os.path.join(REPO_ROOT, "README.md")
CACHE_DIR = os.path.join(REPO_ROOT, ".cache", "agents-table")

START_MARKER = "<!-- AGENTS-TABLE:START -->"
END_MARKER = "<!-- AGENTS-TABLE:END -->"

API_BASE = "https://api.github.com"
# Cache TTL for successful GitHub API responses, in seconds.
CACHE_TTL = 6 * 60 * 60


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def load_marketplace():
    try:
        with open(MARKETPLACE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        die(f"marketplace.json not found at {MARKETPLACE}")
    except json.JSONDecodeError as e:
        die(f"marketplace.json is invalid JSON: {e}")


def parse_owner_repo(url):
    """https://github.com/wshobson/agents.git -> ('wshobson', 'agents')."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lstrip("/")
    if path.endswith(".git"):
        path = path[: -len(".git")]
    parts = path.split("/")
    if len(parts) != 2 or not all(parts):
        die(f"cannot parse owner/repo from source.url: {url}")
    return parts[0], parts[1]


def github_get(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sync-agents-table",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return e.code, body
    except urllib.error.URLError as e:
        die(f"network error hitting {url}: {e.reason}")


def agent_name_from_md(text, fallback):
    """Extract the `name:` field from a markdown agent file's frontmatter.

    Falls back to `fallback` (typically the filename stem) if there's no
    frontmatter or no name field. Strips surrounding quotes if present.
    """
    if not text.startswith("---"):
        return fallback
    end = text.find("\n---", 3)
    if end == -1:
        return fallback
    fm = text[3:end]
    match = re.search(r"^name:\s*\"?([^\"\n]+?)\"?\s*$", fm, re.MULTILINE)
    return match.group(1) if match else fallback


def skill_name_from_md(text, fallback):
    """Extract the `name:` field from a skill's SKILL.md frontmatter."""
    return agent_name_from_md(text, fallback)


def fetch_local_agents(rel_path):
    """Return a sorted list of agent names from a vendored (directory) pack.

    `rel_path` is resolved against REPO_ROOT so that `./plugins/foo` works.
    """
    abs_path = os.path.normpath(os.path.join(REPO_ROOT, rel_path))
    agents_dir = os.path.join(abs_path, "agents")
    if not os.path.isdir(agents_dir):
        skills_dir = os.path.join(abs_path, "skills")
        if os.path.isdir(skills_dir):
            return []
        die(
            f"vendored pack has no agents/ directory: {agents_dir}\n"
            f"  source was '{rel_path}'; does the directory exist, or is it a skills-only pack?"
        )
    names = []
    for fname in os.listdir(agents_dir):
        if not (fname.endswith(".md") and os.path.isfile(os.path.join(agents_dir, fname))):
            continue
        stem = os.path.splitext(fname)[0]
        try:
            with open(os.path.join(agents_dir, fname), encoding="utf-8") as f:
                text = f.read()
        except OSError:
            names.append(stem)
            continue
        names.append(agent_name_from_md(text, stem))
    return sorted(names)


def fetch_local_skills(rel_path):
    """Return a sorted list of skill names from a vendored pack."""
    abs_path = os.path.normpath(os.path.join(REPO_ROOT, rel_path))
    skills_dir = os.path.join(abs_path, "skills")
    if not os.path.isdir(skills_dir):
        return []

    names = []
    for skill_name in os.listdir(skills_dir):
        skill_file = os.path.join(skills_dir, skill_name, "SKILL.md")
        if not os.path.isfile(skill_file):
            continue
        try:
            with open(skill_file, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            names.append(skill_name)
            continue
        names.append(skill_name_from_md(text, skill_name))
    return sorted(names)


def cache_path_for(owner, repo, path, ref):
    key = f"{owner}/{repo}/{path}@{ref}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f"{digest}.json")


def cache_read(path):
    """Return cached agents list, or None if missing/stale/unreadable."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            entry = json.load(f)
        if not isinstance(entry, dict):
            return None
        if time.time() - entry.get("ts", 0) > CACHE_TTL:
            return None
        agents = entry.get("agents")
        if not isinstance(agents, list):
            return None
        return agents
    except (OSError, ValueError):
        return None


def cache_read_stale(path):
    """Return cached agents ignoring TTL, or None. Used as a fallback on API errors."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            entry = json.load(f)
        agents = entry.get("agents") if isinstance(entry, dict) else None
        return agents if isinstance(agents, list) else None
    except (OSError, ValueError):
        return None


def cache_write(path, agents):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "agents": agents}, f)
    except OSError:
        pass


def fetch_agents(owner, repo, path, ref):
    """Return a sorted list of agent names (.md, no extension) for a pack."""
    api_path = f"{path}/agents"
    quoted_path = "/".join(urllib.parse.quote(seg, safe="") for seg in api_path.split("/"))
    url = (
        f"{API_BASE}/repos/{owner}/{repo}/contents/{quoted_path}"
        f"?ref={urllib.parse.quote(ref, safe='')}"
    )
    cpath = cache_path_for(owner, repo, path, ref)
    cached = cache_read(cpath)
    if cached is not None:
        return cached

    status, data = github_get(url)
    if status == 200 and isinstance(data, list):
        agents = sorted(
            os.path.splitext(item["name"])[0]
            for item in data
            if item.get("type") == "file" and item.get("name", "").endswith(".md")
        )
        cache_write(cpath, agents)
        return agents

    # API failed. Try stale cache before giving up — a stale-but-correct
    # answer is better than failing the whole run when rate-limited locally.
    stale = cache_read_stale(cpath)
    if stale is not None:
        print(
            f"warning: GitHub API returned {status} for {owner}/{repo}/{api_path}; "
            f"using stale cache. Set GITHUB_TOKEN to avoid this.",
            file=sys.stderr,
        )
        return stale
    if status == 404:
        die(
            f"agents directory not found upstream: {owner}/{repo}/{api_path} @ {ref}\n"
            f"  was the pack renamed, moved, or does it lack an agents/ dir?"
        )
    if status == 403:
        die(
            f"GitHub API returned 403 (likely rate limited) for {url}\n"
            f"  set GITHUB_TOKEN to raise the limit, or re-run after a moment. "
            f"response: {data}"
        )
    die(f"GitHub API returned {status} for {url}: {data}")


def agents_for_pack(plugin):
    """Resolve a pack's agent list, dispatching by source kind.

    Supported `source` shapes (per Claude Code marketplace schema):
      "./plugins/foo" (string starting with ./)  -> read vendored agents/ locally
      {"source": "git-subdir", "url", "path", ...} -> fetch from GitHub Contents API
      {"source": "directory", "path": "./plugins/foo"} -> legacy, read locally
    """
    source = plugin.get("source")
    # Relative-path string, e.g. "./plugins/web-frontend"
    if isinstance(source, str):
        return fetch_local_agents(source)
    if not isinstance(source, dict):
        die(f"pack {plugin['name']} has malformed source: {source!r}")
    kind = source.get("source")
    if kind in ("directory", "local"):
        return fetch_local_agents(source["path"])
    if kind == "git-subdir":
        owner, repo = parse_owner_repo(source["url"])
        path = source["path"]
        ref = source.get("sha") or source.get("ref")
        if not ref:
            die(f"pack {plugin['name']} has neither sha nor ref in source")
        return fetch_agents(owner, repo, path, ref)
    die(
        f"pack {plugin['name']} has unsupported source kind: {kind!r}\n"
        f"  supported: './relative/path', {{'source':'git-subdir',...}}, "
        f"{{'source':'directory','path':...}}"
    )


def skills_for_pack(plugin):
    """Resolve a pack's skill list for local vendored packs."""
    source = plugin.get("source")
    if isinstance(source, str):
        return fetch_local_skills(source)
    if not isinstance(source, dict):
        return []
    kind = source.get("source")
    if kind in ("directory", "local"):
        return fetch_local_skills(source["path"])
    return []


def pluralize(n, word):
    return f"{n} {word}{'s' if n != 1 else ''}"


def category_label(category):
    labels = {
        "design": "设计",
        "development": "开发",
    }
    return labels.get(category, category)


def build_table(plugins):
    lines = ["| 能力包 | 分类 | 代理 | 技能 |", "|--------|------|------|------|"]
    total_agents = 0
    total_skills = 0
    for p in plugins:
        category = category_label(p.get("category", ""))
        agents = agents_for_pack(p)
        skills = skills_for_pack(p)
        if not agents and not skills:
            print(f"warning: pack {p['name']} has no agents or skills", file=sys.stderr)
        total_agents += len(agents)
        total_skills += len(skills)
        agents_str = ", ".join(agents) if agents else "_(none)_"
        skills_str = ", ".join(skills) if skills else "_(none)_"
        lines.append(f"| `{p['name']}` | {category} | {agents_str} | {skills_str} |")
    lines.append("")
    lines.append(f"总计：**{len(plugins)} 个能力包，{total_agents} 个代理，{total_skills} 个技能**。")
    return "\n".join(lines)


def extract_block(text):
    """Split README into (before, inner, after) on the markers.

    `before` ends with START_MARKER, `after` starts with END_MARKER.
    Returns None if either marker is missing or out of order.
    """
    start_idx = text.find(START_MARKER)
    end_idx = text.find(END_MARKER)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        return None
    before = text[: start_idx + len(START_MARKER)]
    after = text[end_idx:]
    inner = text[start_idx + len(START_MARKER) : end_idx]
    return before, inner, after


def cmd_generate(plugins):
    print(build_table(plugins))


def cmd_check(plugins):
    try:
        with open(README, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        die(f"README not found at {README}")
    parts = extract_block(text)
    if parts is None:
        die(
            f"README is missing the marker block "
            f"({START_MARKER} ... {END_MARKER}).\n"
            f"  add the markers around the agents table, then re-run."
        )
    _, current_inner, _ = parts
    expected = build_table(plugins)
    if current_inner.strip() == expected.strip():
        print("ok: README agents table is in sync.")
        return
    print("FAIL: README agents table is out of sync with marketplace.json.", file=sys.stderr)
    print("", file=sys.stderr)
    print("----- expected -----", file=sys.stderr)
    print(expected, file=sys.stderr)
    print("----- current in README -----", file=sys.stderr)
    print(current_inner.strip(), file=sys.stderr)
    print("-----", file=sys.stderr)
    print("fix with: python scripts/sync_agents_table.py update", file=sys.stderr)
    sys.exit(1)


def cmd_update(plugins):
    try:
        with open(README, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        die(f"README not found at {README}")
    parts = extract_block(text)
    if parts is None:
        die(
            f"README is missing the marker block "
            f"({START_MARKER} ... {END_MARKER})."
        )
    before, _, after = parts
    expected = build_table(plugins)
    new_text = before + "\n" + expected + "\n\n" + after
    with open(README, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"updated: {README}")


def main(argv):
    if len(argv) != 2 or argv[1] not in ("check", "update", "generate"):
        print("usage: sync_agents_table.py {check|update|generate}", file=sys.stderr)
        return 2
    command = argv[1]
    marketplace = load_marketplace()
    plugins = marketplace.get("plugins")
    if not plugins:
        die("marketplace.json has no plugins array")
    if command == "generate":
        cmd_generate(plugins)
    elif command == "check":
        cmd_check(plugins)
    elif command == "update":
        cmd_update(plugins)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
