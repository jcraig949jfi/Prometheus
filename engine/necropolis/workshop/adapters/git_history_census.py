"""Git-history census and recovery of a path (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: none.  Wraps `git log --follow` and `git show
<sha>:<path>` so a deleted or rewritten instrument can be recovered to a
scratch directory WITHOUT `git checkout <ref> -- .` (which would write into
the live tree).  "A deleted tool is still a tool" (harvest charter I).

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_git_census.*

Reads: the repository object store.  Writes: only under the out_dir the caller
names (never the working tree).  Never runs checkout, reset, restore or stash.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Optional

_FORBIDDEN = ("checkout", "reset", "restore", "stash", "clean", "rm", "mv", "commit", "merge", "rebase", "pull", "push")


def _git(args, cwd) -> subprocess.CompletedProcess:
    if args and args[0] in _FORBIDDEN:
        raise PermissionError("git_history_census is read-only; refused: git " + " ".join(args))
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=300,
                          encoding="utf-8", errors="replace")


def history(path: str, repo: Path) -> dict:
    """Commits touching path (following renames) with first/last dates and whether HEAD still has it."""
    r = _git(["log", "--follow", "--diff-filter=ADMR", "--format=%H%x09%aI%x09%an%x09%s", "--name-status",
              "--", path], repo)
    commits, current = [], None
    for line in r.stdout.splitlines():
        head = line.split("\t")[0]
        if "\t" in line and len(head) == 40 and all(c in "0123456789abcdef" for c in head):
            sha, date, author, subject = line.split("\t", 3)
            current = {"sha": sha, "date": date, "author": author, "subject": subject[:120], "changes": []}
            commits.append(current)
        elif line.strip() and current is not None:
            current["changes"].append(line.strip())
    exists = _git(["cat-file", "-e", "HEAD:" + path], repo).returncode == 0
    deleted_in = [c["sha"] for c in commits if any(ch.startswith("D") for ch in c["changes"])]
    return {"path": path, "n_commits": len(commits), "in_head": exists,
            "first": commits[-1]["date"] if commits else None, "last": commits[0]["date"] if commits else None,
            "deleted_in": deleted_in, "commits": commits, "git_rc": r.returncode, "git_err": r.stderr[-200:]}


def recover(path: str, sha: str, repo: Path, out_dir: Path) -> dict:
    """git show <sha>:<path> into out_dir/<sha[:12]>/<basename>; returns sha256 of what was recovered."""
    out_dir = Path(out_dir)
    repo_r = Path(repo).resolve()
    out_r = out_dir.resolve()
    if out_r == repo_r or repo_r in out_r.parents:
        rel = out_r.relative_to(repo_r).as_posix()
        if not rel.startswith("engine/necropolis/workshop/fixtures"):
            raise PermissionError("recovery into the live tree is refused outside workshop/fixtures: " + rel)
    r = _git(["show", sha + ":" + path], repo)
    if r.returncode != 0:
        return {"ok": False, "sha": sha, "path": path, "err": r.stderr[-300:]}
    dest = out_dir / sha[:12] / Path(path).name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(r.stdout, encoding="utf-8", newline="\n")
    return {"ok": True, "sha": sha, "path": path, "recovered_to": str(dest),
            "sha256_lf": hashlib.sha256(r.stdout.encode("utf-8")).hexdigest(), "bytes": len(r.stdout)}


def deleted_python_files(repo: Path, since: Optional[str] = None, grep: Optional[str] = None,
                         limit: Optional[int] = None) -> list:
    """Every .py path deleted somewhere in history and absent at HEAD (candidate dead tools).

    limit stops after that many confirmed-absent paths (each costs one cat-file call)."""
    args = ["log", "--diff-filter=D", "--name-only", "--format=%H"]
    if since:
        args.append("--since=" + since)
    r = _git(args, repo)
    sha, out, seen = None, [], set()
    for line in r.stdout.splitlines():
        if len(line) == 40 and " " not in line:
            sha = line
        elif line.endswith(".py") and line not in seen and (grep is None or grep in line):
            seen.add(line)
            if _git(["cat-file", "-e", "HEAD:" + line], repo).returncode != 0:
                out.append({"path": line, "deleted_in": sha})
                if limit is not None and len(out) >= limit:
                    break
    return out
