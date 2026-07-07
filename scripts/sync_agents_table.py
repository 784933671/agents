#!/usr/bin/env python3
"""Keep README's agents table in sync with marketplace.json.

Subcommands:
  check     fetch upstream agents, compare to README, exit 1 on mismatch
  update    fetch upstream agents, rewrite README's table block in place
  generate  fetch upstream agents, print the expected table to stdout

No third-party dependencies (Python 3.7+ stdlib only). Talks to the GitHub
Contents API using the sha pinned in marketplace.json. Set GITHUB_TOKEN to
raise the rate limit (mostly relevant in CI).
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKETPLACE = os.path.join(REPO_ROOT, ".claude-plugin", "marketplace.json")
README = os.path.join(REPO_ROOT, "README.md")

START_MARKER = "<!-- AGENTS-TABLE:START -->"
END_MARKER = "<!-- AGENTS-TABLE:END -->"

API_BASE = "https://api.github.com"


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


def fetch_local_agents(rel_path):
    """Return a sorted list of agent names from a vendored (directory) pack.

    `rel_path` is resolved against REPO_ROOT so that `./plugins/foo` works.
    """
    abs_path = os.path.normpath(os.path.join(REPO_ROOT, rel_path))
    agents_dir = os.path.join(abs_path, "agents")
    if not os.path.isdir(agents_dir):
        die(
            f"vendored pack has no agents/ directory: {agents_dir}\n"
            f"  source.path was '{rel_path}'; does the directory exist?"
        )
    return sorted(
        os.path.splitext(name)[0]
        for name in os.listdir(agents_dir)
        if name.endswith(".md") and os.path.isfile(os.path.join(agents_dir, name))
    )


def fetch_agents(owner, repo, path, ref):
    """Return a sorted list of agent names (.md, no extension) for a pack."""
    api_path = f"{path}/agents"
    quoted_path = "/".join(urllib.parse.quote(seg, safe="") for seg in api_path.split("/"))
    url = (
        f"{API_BASE}/repos/{owner}/{repo}/contents/{quoted_path}"
        f"?ref={urllib.parse.quote(ref, safe='')}"
    )
    status, data = github_get(url)
    if status == 404:
        die(
            f"agents directory not found upstream: {owner}/{repo}/{api_path} @ {ref}\n"
            f"  was the pack renamed, moved, or does it lack an agents/ dir?"
        )
    if status == 403:
        die(
            f"GitHub API returned 403 (likely rate limited) for {url}\n"
            f"  set GITHUB_TOKEN to raise the limit. response: {data}"
        )
    if status != 200:
        die(f"GitHub API returned {status} for {url}: {data}")
    if not isinstance(data, list):
        die(f"expected a directory listing at {url}, got {type(data).__name__}")
    agents = sorted(
        os.path.splitext(item["name"])[0]
        for item in data
        if item.get("type") == "file" and item.get("name", "").endswith(".md")
    )
    return agents


def agents_for_pack(plugin):
    """Resolve a pack's agent list, dispatching by source kind.

    Supported source kinds:
      git-subdir  -> fetch from GitHub Contents API at the pinned ref
      directory   -> read vendored agents/ from a local path under the repo
    """
    source = plugin.get("source") or {}
    kind = source.get("source")
    if kind == "directory":
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
        f"  supported kinds: 'git-subdir', 'directory'"
    )


def pluralize(n, word):
    return f"{n} {word}{'s' if n != 1 else ''}"


def build_table(plugins):
    lines = ["| Pack | Category | Agents |", "|------|----------|--------|"]
    total_agents = 0
    for p in plugins:
        category = p.get("category", "")
        agents = agents_for_pack(p)
        if not agents:
            print(f"warning: pack {p['name']} has no agents", file=sys.stderr)
        total_agents += len(agents)
        agents_str = ", ".join(agents) if agents else "_(none)_"
        lines.append(f"| `{p['name']}` | {category} | {agents_str} |")
    lines.append("")
    lines.append(
        f"Total: **{pluralize(len(plugins), 'pack')}, {pluralize(total_agents, 'agent')}**."
    )
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
