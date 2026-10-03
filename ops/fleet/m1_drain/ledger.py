"""M1 drain ledger (M1-DRAIN-2026-10-03): deterministic, read-only inventory of every checkout on this host.

For every git worktree registered with the canonical repo, and every directory under the worktrees root that is not a
registered worktree, record: path, seat (inferred from the directory name), branch, HEAD, upstream, tracked-dirty count,
untracked count, commits reachable from HEAD but from no remote ref (unpushed), ahead/behind origin/main, whether HEAD is
already contained in origin/main, the live processes whose cwd is inside it, and a mechanical disposition SUGGESTION.

The suggestion is never an action. MERGE/ARCHIVE/DISCARD decisions belong to the seat that owns the branch (directive s5).

Usage: python ops/fleet/m1_drain/ledger.py --repo F:/prometheus --root F:/Prometheus-worktrees --out <dir> [--jobs 8]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import subprocess


def git(cwd, *args, timeout=300):
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return r.returncode, r.stdout.strip()
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"


def worktrees(repo):
    rc, out = git(repo, "worktree", "list", "--porcelain")
    items, cur = [], {}
    for line in out.splitlines() + [""]:
        if not line:
            if cur:
                items.append(cur)
            cur = {}
            continue
        k, _, v = line.partition(" ")
        cur[k] = v or True
    return items


def seat_of(path):
    name = os.path.basename(path.rstrip("/\\"))
    m = re.match(r"([A-Za-z]+)", name)
    return (m.group(1).capitalize() if m else name) if name.lower() != "prometheus" else "CANONICAL"


def live_cwds():
    try:
        import psutil
    except ImportError:
        return {}
    out = {}
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cwd = p.cwd()
        except Exception:
            continue
        out.setdefault(os.path.normcase(os.path.normpath(cwd)), []).append(
            "%s:%s %s" % (p.info["pid"], p.info["name"], " ".join(p.info["cmdline"] or [])[:80]))
    return out


def inspect(path, branch_ref, procs):
    rec = {"path": path, "seat": seat_of(path)}
    rec["branch"] = branch_ref.replace("refs/heads/", "") if isinstance(branch_ref, str) else "(detached)"
    _, rec["head"] = git(path, "rev-parse", "--short=12", "HEAD")
    rc, up = git(path, "rev-parse", "--abbrev-ref", "@{upstream}")
    rec["upstream"] = up if rc == 0 else None
    rc, st = git(path, "status", "--porcelain=v1", "--untracked-files=normal", timeout=600)
    if rc != 0:
        rec["status_error"] = st[:200]
        rec["dirty"] = rec["untracked"] = None
    else:
        lines = [l for l in st.splitlines() if l]
        rec["untracked"] = sum(1 for l in lines if l.startswith("??"))
        rec["dirty"] = len(lines) - rec["untracked"]
        rec["dirty_sample"] = [l[3:] for l in lines[:6]]
    rc, n = git(path, "rev-list", "--count", "HEAD", "--not", "--remotes")
    rec["unpushed"] = int(n) if rc == 0 and n.isdigit() else None
    rc, ab = git(path, "rev-list", "--left-right", "--count", "origin/main...HEAD")
    if rc == 0 and ab:
        behind, ahead = ab.split()
        rec["behind_main"], rec["ahead_main"] = int(behind), int(ahead)
    rc, _ = git(path, "merge-base", "--is-ancestor", "HEAD", "origin/main")
    rec["in_main"] = rc == 0
    rec["live_processes"] = [v for k, vs in procs.items()
                             if k.startswith(os.path.normcase(os.path.normpath(path))) for v in vs]
    rec["suggestion"] = suggest(rec)
    return rec


EXCLUDED_SEATS = {"Cadmus", "Dionysus"}   # operator 2026-10-03: Cadmus (RSO builder, binding) and Dionysus (exempt for now)


def suggest(r):
    if r["seat"] in EXCLUDED_SEATS:
        return "EXCLUDED (operator: Phase 3 seat stays on M1; do not touch)"
    if r.get("status_error"):
        return "ARCHIVE/NEEDS_REVIEW (status unreadable)"
    clean = (r["dirty"] == 0 and r["untracked"] == 0)
    if r["live_processes"]:
        return "IN_USE (owner drains first)"
    if r["in_main"] and clean:
        return "RESOLVED (HEAD in origin/main; worktree removable)"
    if clean and r["unpushed"] == 0:
        return "PUSHED_NOT_MERGED (owner: MERGE or ARCHIVE)"
    if r["unpushed"]:
        return "UNPUSHED (owner must push, then MERGE or ARCHIVE)"
    return "DIRTY (owner must commit or explicitly DISCARD)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    git(a.repo, "fetch", "-q", "origin", timeout=900)
    procs = live_cwds()
    wts = worktrees(a.repo)
    registered = {os.path.normcase(os.path.normpath(w["worktree"])) for w in wts}
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        recs = list(ex.map(lambda w: inspect(w["worktree"], w.get("branch", True) if "detached" not in w else None,
                                             procs), wts))
    stray = []
    for d in sorted(os.listdir(a.root)):
        p = os.path.join(a.root, d)
        if os.path.isdir(p) and os.path.normcase(os.path.normpath(p)) not in registered:
            stray.append({"path": p, "seat": seat_of(p), "is_git": os.path.exists(os.path.join(p, ".git")),
                          "suggestion": "UNREGISTERED DIR (inspect: other repo, stale copy, or data)"})
    rc, br = git(a.repo, "for-each-ref", "--format=%(refname:short) %(objectname:short=12)", "refs/heads/")
    checked_out = {r["branch"] for r in recs}
    loose = []
    for line in br.splitlines():
        b, sha = line.split()
        if b in checked_out:
            continue
        rc1, _ = git(a.repo, "merge-base", "--is-ancestor", b, "origin/main")
        rc2, n = git(a.repo, "rev-list", "--count", b, "--not", "--remotes")
        loose.append({"branch": b, "head": sha, "in_main": rc1 == 0, "unpushed": int(n) if n.isdigit() else None})
    os.makedirs(a.out, exist_ok=True)
    doc = {"schema": "prometheus.m1_drain_ledger.v1", "order": "M1-DRAIN-2026-10-03", "host": os.environ.get("COMPUTERNAME"),
           "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "origin_main": git(a.repo, "rev-parse", "--short=12", "origin/main")[1],
           "worktrees": sorted(recs, key=lambda r: (r["seat"], r["path"])), "unregistered_dirs": stray,
           "branches_not_checked_out": loose}
    with open(os.path.join(a.out, "LEDGER.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
    print("worktrees", len(recs), "stray", len(stray), "loose branches", len(loose))


if __name__ == "__main__":
    main()
