"""M1 drain central cleanup (M1-DRAIN-2026-10-03, directive s7): remove RESOLVED worktrees and delete merged branches.

A worktree is removed only if, re-checked at removal time:
  * HEAD is an ancestor of origin/main (its commits are on main),
  * `git status --porcelain --untracked-files=normal` is empty (nothing uncommitted, nothing untracked),
  * no live process has its cwd inside it,
  * its seat is not excluded and not still draining.
Removal uses plain `git worktree remove` (never --force), so git itself refuses anything dirty.
Every action is appended to DISPOSITIONS.jsonl with path, branch, HEAD and result, so what was removed is provable
and recoverable (all content is on main).

Branches: a local branch is deleted only when its tip is an ancestor of origin/main and no worktree has it checked
out; with --remote, the same-named origin branch is deleted when its tip is an ancestor of origin/main.

Usage: python ops/fleet/m1_drain/dispose.py --repo F:/prometheus --ledger LEDGER.json --log DISPOSITIONS.jsonl
       --skip-seats Ananke,Tantalus,Aporia [--jobs 3] [--remote] [--dry-run]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import subprocess
import threading

EXCLUDED = {"Cadmus", "Dionysus", "CANONICAL",
            # Phase 3 seats are never subject to legacy cleanup (directive s12); added after the Enceladus restore
            "Enceladus", "Epimetheus", "Palamedes", "Argus", "Eupalamus", "Pallas"}
LOCK = threading.Lock()


def git(cwd, *args, timeout=1800):
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(path, rec):
    with LOCK:
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec) + "\n")


def live_cwds():
    import psutil
    out = []
    for p in psutil.process_iter(["pid"]):
        try:
            out.append(os.path.normcase(os.path.normpath(p.cwd())))
        except Exception:
            pass
    return out


def dispose_worktree(a, r, cwds):
    rec = {"utc": now(), "action": "worktree_remove", "seat": r["seat"], "path": r["path"], "branch": r["branch"],
           "head": r["head"]}
    p = os.path.normcase(os.path.normpath(r["path"]))
    if any(c.startswith(p) for c in cwds):
        rec["result"] = "SKIP_IN_USE"
    else:
        rc, _ = git(r["path"], "merge-base", "--is-ancestor", "HEAD", "origin/main")
        if rc != 0:
            rec["result"] = "SKIP_NOT_IN_MAIN"
        else:
            rc, st = git(r["path"], "status", "--porcelain", "--untracked-files=normal")
            if rc != 0 or st:
                rec["result"] = "SKIP_DIRTY" if rc == 0 else "SKIP_STATUS_ERROR"
                rec["detail"] = st[:300]
            elif a.dry_run:
                rec["result"] = "WOULD_REMOVE"
            else:
                rc, out = git(a.repo, "worktree", "remove", r["path"])
                rec["result"] = "REMOVED" if rc == 0 else "REMOVE_FAILED"
                if rc != 0:
                    rec["detail"] = out[:300]
    log(a.log, rec)
    print(rec["result"], r["path"], flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--skip-seats", default="")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--remote", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    skip = EXCLUDED | {s for s in a.skip_seats.split(",") if s}
    git(a.repo, "fetch", "-q", "origin")
    led = json.load(open(a.ledger, encoding="utf-8"))
    todo = [r for r in led["worktrees"] if r["suggestion"].startswith("RESOLVED") and r["seat"] not in skip]
    cwds = live_cwds()
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda r: dispose_worktree(a, r, cwds), todo))
    git(a.repo, "worktree", "prune")
    # branches: local, not checked out anywhere, tip in origin/main
    rc, wl = git(a.repo, "worktree", "list", "--porcelain")
    checked = {l.split(" ", 1)[1].replace("refs/heads/", "") for l in wl.splitlines() if l.startswith("branch ")}
    rc, br = git(a.repo, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads/")
    for line in br.splitlines():
        b, sha = line.split()
        seat = b.split("/")[0].capitalize()
        if b in checked or seat in skip or b in ("main",):
            continue
        rc, _ = git(a.repo, "merge-base", "--is-ancestor", sha, "origin/main")
        if rc != 0:
            continue
        rec = {"utc": now(), "action": "branch_delete_local", "branch": b, "head": sha}
        if a.dry_run:
            rec["result"] = "WOULD_DELETE"
        else:
            rc, out = git(a.repo, "branch", "-D", b)
            rec["result"] = "DELETED" if rc == 0 else "DELETE_FAILED"
        log(a.log, rec)
        if a.remote:
            rc, rsha = git(a.repo, "rev-parse", "-q", "--verify", "refs/remotes/origin/" + b)
            if rc == 0:
                rc2, _ = git(a.repo, "merge-base", "--is-ancestor", rsha, "origin/main")
                rrec = {"utc": now(), "action": "branch_delete_remote", "branch": b, "head": rsha}
                if rc2 != 0:
                    rrec["result"] = "SKIP_REMOTE_NOT_IN_MAIN"
                elif a.dry_run:
                    rrec["result"] = "WOULD_DELETE"
                else:
                    rc3, out = git(a.repo, "push", "origin", "--delete", b, timeout=300)
                    rrec["result"] = "DELETED" if rc3 == 0 else "DELETE_FAILED"
                    if rc3 != 0:
                        rrec["detail"] = out[-200:]
                log(a.log, rrec)
    c = {}
    for r in results:
        c[r["result"]] = c.get(r["result"], 0) + 1
    print("worktrees:", c)


if __name__ == "__main__":
    main()
