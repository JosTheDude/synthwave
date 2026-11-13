"""Startup update check: compares the installed commit with GitHub's main and offers to update."""
import json, os, re, subprocess, sys, urllib.request
from importlib import metadata

REPO = "JosTheDude/synthwave"
GIT = f"git+https://github.com/{REPO}"


def installed(prefix=sys.prefix):
    """(commit, update command) for a Homebrew, uv or pipx install from git, else None."""
    brew = re.search(r"/Cellar/synthwave/[^/]*-([0-9a-f]{7,40})/", prefix.replace("\\", "/") + "/")
    if brew:  # the formula's version ends in the commit it was built from
        return brew[1], ["brew", "upgrade", "synthwave"]
    try:
        dist = metadata.distribution("synthwave")
        commit = json.loads(dist.read_text("direct_url.json") or "{}").get("vcs_info", {}).get("commit_id")
    except (metadata.PackageNotFoundError, ValueError):
        return None
    if not commit:  # a clone, editable install or `python -m synthwave`: nothing to update from
        return None
    if (dist.read_text("INSTALLER") or "").strip() == "uv":
        return commit, ["uv", "tool", "install", "--reinstall", GIT]
    if "pipx" in prefix:
        return commit, ["pipx", "install", "--force", GIT]
    return None


def outdated(files):
    """True when the changed files touch the app itself, not just docs or the formula."""
    return any(f["filename"].startswith(("synthwave/", "pyproject.toml")) for f in files)


def newer(commit, timeout=2):
    url = f"https://api.github.com/repos/{REPO}/compare/{commit}...main"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "synthwave"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return outdated(json.load(r).get("files", []))


def check():
    """Offer to update before the TUI starts. Any network trouble just skips the check."""
    found = installed()
    if not found or not sys.stdin.isatty():
        return
    commit, cmd = found
    try:
        if not newer(commit):
            return
    except Exception:  # offline, rate limited, GitHub down: just play music
        return
    try:
        answer = input("  synthwave: an update is available. Update now? [Y/n] ").strip().lower()
    except EOFError:
        return
    except KeyboardInterrupt:
        sys.exit("")
    if answer not in ("", "y", "yes"):
        return
    print(f"  running {' '.join(cmd)}\n", flush=True)
    try:
        ok = subprocess.run(cmd).returncode == 0
    except OSError:  # brew, uv or pipx no longer on PATH
        ok = False
    if not ok:
        print("\n  synthwave: the update didn't finish; starting the version you have\n")
        return
    if os.name == "nt":  # Windows can't exec over itself
        sys.exit("\n  synthwave: updated. run synthwave again to tune in")
    print("\n  synthwave: updated. restarting…\n", flush=True)
    os.execv(sys.argv[0], sys.argv)
