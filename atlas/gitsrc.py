"""Read-only git access for Atlas harvesters.

Every call reads the object database or the ref list of the shared
repository. Nothing here checks out, fetches, stashes, writes a ref or
touches another seat's worktree: a harvest must never disturb an engine
(charter R10). `fetch()` exists but is only called when the operator asks
for it (--fetch), and only updates refs/remotes.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
TIMEOUT = 300


def git(*args: str, timeout: int = TIMEOUT, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True,
                       timeout=timeout, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError("git {} failed: {}".format(" ".join(args[:3]), r.stderr.strip()[:400]))
    return r.stdout


def fetch() -> None:
    git("fetch", "-q", "origin", timeout=180)


def resolve(ref: str) -> Optional[str]:
    out = git("rev-parse", "--verify", "-q", ref + "^{commit}", check=False).strip()
    return out or None


def head_sha() -> str:
    return git("rev-parse", "HEAD").strip()


def refs(patterns: Tuple[str, ...] = ("refs/remotes/origin", "refs/heads")) -> List[Tuple[str, str, str]]:
    """(refname, sha, committer ISO date) for every ref under the patterns."""
    out = git("for-each-ref", "--format=%(refname)%09%(objectname)%09%(committerdate:iso-strict)", *patterns)
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and not parts[0].endswith("/HEAD"):
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def ls_tree(ref: str, prefix: str) -> List[Tuple[str, str, int]]:
    """(path, blob_sha, size) for every blob under prefix at ref."""
    out = git("ls-tree", "-r", "-l", "-z", ref, "--", prefix)
    rows = []
    for rec in out.split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        _mode, typ, sha, size = meta.split()
        if typ == "blob":
            rows.append((path, sha, int(size) if size != "-" else 0))
    return rows


def path_commits(ref: str, prefix: str) -> Tuple[Dict[str, Tuple[str, str]], Dict[str, Tuple[str, str]],
                                                 Dict[str, List[str]]]:
    """One log walk over prefix at ref. Returns
    (newest, oldest, touching): path -> (sha, ISO author date) of the newest
    and oldest commit touching it, and path -> every sha touching it."""
    out = git("log", "--format=%x1e%H%x1f%aI", "--name-only", ref, "--", prefix)
    newest: Dict[str, Tuple[str, str]] = {}
    oldest: Dict[str, Tuple[str, str]] = {}
    touching: Dict[str, List[str]] = {}
    for rec in out.split("\x1e"):
        if not rec.strip():
            continue
        head, _, names = rec.partition("\n")
        sha, date = head.split("\x1f")
        for p in names.splitlines():
            p = p.strip()
            if p:
                newest.setdefault(p, (sha, date))
                oldest[p] = (sha, date)  # the walk is newest-first, so the last write is the oldest
                touching.setdefault(p, []).append(sha)
    return newest, oldest, touching


class CatFile:
    """One `git cat-file --batch` process for many blob reads."""

    def __init__(self) -> None:
        self.p = subprocess.Popen(["git", "-C", str(REPO), "cat-file", "--batch"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def read(self, obj: str) -> Optional[bytes]:
        assert self.p.stdin and self.p.stdout
        self.p.stdin.write((obj + "\n").encode())
        self.p.stdin.flush()
        header = self.p.stdout.readline().decode().strip()
        if header.endswith("missing"):
            return None
        size = int(header.split()[2])
        data = self.p.stdout.read(size)
        self.p.stdout.read(1)
        return data

    def text(self, obj: str) -> Optional[str]:
        b = self.read(obj)
        return None if b is None else b.decode("utf-8", errors="replace")

    def json(self, obj: str):
        t = self.text(obj)
        if t is None:
            return None
        try:
            return json.loads(t)
        except ValueError:
            return None

    def jsonl(self, obj: str) -> Iterator[dict]:
        t = self.text(obj) or ""
        for line in t.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                v = json.loads(line)
            except ValueError:
                continue
            if isinstance(v, dict):
                yield v

    def close(self) -> None:
        if self.p.stdin:
            self.p.stdin.close()
        self.p.wait(timeout=30)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
