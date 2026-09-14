"""Commit-on-write rows (round 2 gate F4).

Round 1: a session died at 07:29 with a kill matrix's rows written but not
committed, and dev/tuning/aborted runs left no rows at all (0 of 86 files).
RowWriter appends one JSON line per evaluated thing, requires a status tag,
flushes every line, and commits the rows file by itself at most every
`commit_every_s` seconds and on close, exit, or SIGTERM/SIGBREAK. A TTL death
therefore strands at most one commit interval.

    from primordial.fabric.rows import RowWriter
    with RowWriter("primordial/ledger/rows/B/B8-x.jsonl", "B8-x") as w:
        w.write({"status": "dev", "cell": [3, 7], "fitness": 12.0, "bytes": 208})

Statuses: record, dev, aborted, timeout, cheat, control. Nothing is filtered
before commit (the failure landscape is kept).

Commits touch ONLY the rows file (`git commit --only`), retry on index.lock,
and do not push (pushing mid-run races the lane's own rebase). The lane pushes
as usual; the integration push carries these commits.

CLI (for rows written by other tools):
    python -m primordial.fabric.rows commit PATH --exp EXP_ID
"""
from __future__ import annotations

import argparse
import atexit
import json
import os
import pathlib
import signal
import subprocess
import sys
import time

STATUSES = ("record", "dev", "aborted", "timeout", "cheat", "control")


def _git(repo, *a, timeout=120):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=timeout)


def repo_root(path) -> pathlib.Path:
    p = pathlib.Path(path).resolve()
    q = _git(p.parent if p.suffix else p, "rev-parse", "--show-toplevel")
    if q.returncode != 0:
        raise RuntimeError(f"{path} is not inside a git worktree")
    return pathlib.Path(q.stdout.strip())


def commit_path(path, exp_id: str, note: str = "", repo=None, tries: int = 10) -> str | None:
    """Commit only `path`. -> new short sha, or None when there was nothing to commit."""
    path = pathlib.Path(path).resolve()
    repo = pathlib.Path(repo) if repo else repo_root(path)
    rel = path.relative_to(repo).as_posix()
    lane = os.environ.get("PM_LANE", "?")
    tag = os.environ.get("PM_TAG", "untagged")
    msg = f"{lane}[{tag}]: rows {exp_id}{(' ' + note) if note else ''}\n\nNestor-Instance: {lane} {tag}\n"
    delay = 0.5
    for _ in range(tries):
        add = _git(repo, "add", "--", rel)
        if add.returncode == 0:
            if _git(repo, "diff", "--cached", "--quiet", "--", rel).returncode == 0:
                return None
            c = _git(repo, "commit", "-q", "--only", "-m", msg, "--", rel)
            if c.returncode == 0:
                return _git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
            err = c.stderr + c.stdout
        else:
            err = add.stderr
        if "index.lock" not in err:
            raise RuntimeError(f"commit of {rel} failed: {err.strip()[:400]}")
        time.sleep(delay)
        delay = min(5.0, delay * 2)
    raise RuntimeError(f"commit of {rel} failed: index.lock held through {tries} tries")


class RowWriter:
    def __init__(self, path, exp_id: str, commit_every_s: float = 60.0, repo=None):
        self.path = pathlib.Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.exp_id = exp_id
        self.every = float(commit_every_s)
        self.repo = pathlib.Path(repo) if repo else repo_root(self.path)
        self.fh = open(self.path, "a", encoding="utf-8", newline="\n")
        self.n = self.n_committed = 0
        self.last_commit = time.monotonic()
        self.closed = False
        atexit.register(self.close)
        for sig in ("SIGTERM", "SIGBREAK"):
            if hasattr(signal, sig):
                try:
                    signal.signal(getattr(signal, sig), self._on_signal)
                except ValueError:            # not the main thread
                    pass

    def _on_signal(self, signum, frame):
        self.close(note="(signal)")
        sys.exit(128 + int(signum))

    def write(self, row: dict) -> None:
        if self.closed:
            raise RuntimeError("RowWriter is closed")
        if row.get("status") not in STATUSES:
            raise ValueError(f"row status must be one of {STATUSES}, got {row.get('status')!r}")
        rec = dict(row, exp_id=row.get("exp_id", self.exp_id), ts=row.get("ts", round(time.time(), 3)))
        self.fh.write(json.dumps(rec, sort_keys=True) + "\n")
        self.fh.flush()
        self.n += 1
        if time.monotonic() - self.last_commit >= self.every:
            self.commit()

    def commit(self, note: str = "") -> str | None:
        self.fh.flush()
        sha = commit_path(self.path, self.exp_id, note or f"(+{self.n - self.n_committed}, {self.n} total)", self.repo)
        self.n_committed = self.n
        self.last_commit = time.monotonic()
        return sha

    def close(self, note: str = "") -> None:
        if self.closed:
            return
        self.closed = True
        try:
            self.fh.flush()
            self.fh.close()
            if self.n > self.n_committed:
                commit_path(self.path, self.exp_id, note or f"(close, {self.n} total)", self.repo)
                self.n_committed = self.n
        finally:
            try:
                atexit.unregister(self.close)
            except Exception:                 # pragma: no cover
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close(note="(aborted)" if exc_type else "")
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("commit")
    c.add_argument("path")
    c.add_argument("--exp", required=True)
    a = ap.parse_args(argv)
    print(commit_path(a.path, a.exp) or "nothing to commit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
