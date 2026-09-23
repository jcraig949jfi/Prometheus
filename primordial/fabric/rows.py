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

O3 (round 3): a writer refuses to open, and commit_path refuses to commit,
without a real PM_TAG (unset, empty, or "untagged"). While open, a writer keeps
a live marker in its worktree's git dir (<git-dir>/pm-rowwriters/); markers of
dead processes are pruned on read. primordial.ops.push reads them and pushes
fast-forward only while any writer is live (a rebase under a live writer
wedges it: its commits land on the pre-rebase HEAD).

CLI (for rows written by other tools):
    python -m primordial.fabric.rows commit PATH --exp EXP_ID
    python -m primordial.fabric.rows live [REPO]
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


BAD_TAGS = ("", "untagged")


def require_tag() -> str:
    tag = os.environ.get("PM_TAG", "").strip()
    if tag in BAD_TAGS:
        raise RuntimeError("PM_TAG is not set: rows cannot be attributed (run `python -m comms instance` and export PM_TAG)")
    return tag


def pid_alive(pid: int) -> bool:
    import psutil                             # never os.kill(pid, 0): on Windows it terminates the process
    try:
        q = psutil.Process(int(pid))
        return q.is_running() and q.status() != psutil.STATUS_ZOMBIE
    except psutil.Error:
        return False


def writers_dir(repo) -> pathlib.Path:
    q = _git(repo, "rev-parse", "--absolute-git-dir")
    if q.returncode != 0:
        raise RuntimeError(f"{repo} is not inside a git worktree")
    return pathlib.Path(q.stdout.strip()) / "pm-rowwriters"


def live_writers(repo=".") -> list[dict]:
    """Live RowWriters of this worktree; markers of dead processes are removed."""
    d = writers_dir(repo)
    out = []
    for m in sorted(d.glob("*.json")) if d.exists() else []:
        try:
            rec = json.loads(m.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if pid_alive(rec.get("pid", -1)):
            out.append(rec)
        else:
            m.unlink(missing_ok=True)
    return out


def plain(p) -> pathlib.Path:
    """Drop Windows' extended-length prefix. Path.resolve() can return '\\\\?\\C:\\...' (seen in a
    worker thread under pytest, 09-14) while the repo is 'C:\\...', and relative_to then raises."""
    s = str(p)
    if s.startswith("\\\\?\\UNC\\"):
        s = "\\\\" + s[8:]
    elif s.startswith("\\\\?\\"):
        s = s[4:]
    return pathlib.Path(s)


def repo_root(path) -> pathlib.Path:
    p = plain(pathlib.Path(path).resolve())
    q = _git(p.parent if p.suffix else p, "rev-parse", "--show-toplevel")
    if q.returncode != 0:
        raise RuntimeError(f"{path} is not inside a git worktree")
    return plain(pathlib.Path(q.stdout.strip()))


def rel_to(path, repo) -> str:
    """POSIX path of `path` under `repo`, comparing prefix-free, case-normalized forms."""
    path, repo = plain(pathlib.Path(path).resolve()), plain(pathlib.Path(repo).resolve())
    try:
        rel = os.path.relpath(path, repo)
    except ValueError as e:                              # different drives
        raise ValueError(f"{path} is not inside {repo}") from e
    rel = pathlib.PurePath(rel).as_posix()
    if rel == ".." or rel.startswith("../") or os.path.isabs(rel):
        raise ValueError(f"{path} is not inside {repo}")
    return rel


def commit_path(path, exp_id: str, note: str = "", repo=None, tries: int = 10) -> str | None:
    """Commit only `path`. -> new short sha, or None when there was nothing to commit."""
    path = plain(pathlib.Path(path).resolve())
    repo = plain(pathlib.Path(repo).resolve()) if repo else repo_root(path)
    rel = rel_to(path, repo)
    lane = os.environ.get("PM_LANE", "?")
    tag = require_tag()
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
        self.tag = require_tag()
        self.path = plain(pathlib.Path(path).resolve())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.exp_id = exp_id
        self.every = float(commit_every_s)
        self.repo = plain(pathlib.Path(repo).resolve()) if repo else repo_root(self.path)
        self.fh = open(self.path, "a", encoding="utf-8", newline="\n")
        self.n = self.n_committed = 0
        self.last_commit = time.monotonic()
        self.closed = False
        d = writers_dir(self.repo)
        d.mkdir(parents=True, exist_ok=True)
        self.marker = d / f"{os.getpid()}-{id(self):x}.json"
        self.marker.write_text(json.dumps({"pid": os.getpid(), "tag": self.tag, "exp_id": exp_id,
                                           "path": str(self.path), "ts": round(time.time(), 3)}), encoding="utf-8")
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
            self.marker.unlink(missing_ok=True)
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
    lv = sub.add_parser("live")
    lv.add_argument("repo", nargs="?", default=".")
    a = ap.parse_args(argv)
    if a.cmd == "live":
        w = live_writers(a.repo)
        for rec in w:
            print(json.dumps(rec, sort_keys=True))
        print(f"{len(w)} live writer(s)")
        return 0
    print(commit_path(a.path, a.exp) or "nothing to commit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
