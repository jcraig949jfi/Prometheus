"""Landing tripwire (batch 11 P0).

Batch 10 deviation D-1: rounds 06-09 reported carriers as "landed on main" when they were only on
LOCAL main and were not ancestors of origin/main. Nothing was lying; the claim was simply never
checked against the remote. This is the check.

    python -m techne.fossils.landed <sha> [<sha> ...]        exit 0 only if ALL are landed
    python -m techne.fossils.landed --no-fetch <sha>         skip the fetch (tests/offline)

LANDED means, and only means:

    the commit is an ancestor of the REMOTE-TRACKING ref (origin/main) AFTER a fetch

Not: HEAD contains it. Not: local main contains it. Not: git push printed something.
The distinction those rounds missed is exactly `main` vs `origin/main`, so both are reported.

This is a tripwire, not a workflow. It answers one question and exits.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

REMOTE_REF = "origin/main"
LOCAL_REF = "main"


def _git(*args, cwd=None):
    p = subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def _is_ancestor(commit: str, ref: str, cwd=None) -> bool:
    rc, _, _ = _git("merge-base", "--is-ancestor", commit, ref, cwd=cwd)
    return rc == 0


def status(commit: str, fetch: bool = True, cwd=None, remote_ref: str = REMOTE_REF,
           local_ref: str = LOCAL_REF) -> dict:
    """The one assertion. `landed` is true ONLY for an ancestor of the remote-tracking ref."""
    if fetch:
        _git("fetch", "--quiet", "origin", cwd=cwd)
    rc, resolved, _ = _git("rev-parse", "--verify", "%s^{commit}" % commit, cwd=cwd)
    if rc != 0:
        return {"commit": commit, "exists": False, "in_local_main": False, "landed": False,
                "reason": "not a commit in this repository"}
    has_remote = _git("rev-parse", "--verify", "%s^{commit}" % remote_ref, cwd=cwd)[0] == 0
    in_local = _is_ancestor(resolved, local_ref, cwd=cwd) if \
        _git("rev-parse", "--verify", "%s^{commit}" % local_ref, cwd=cwd)[0] == 0 else False
    landed = _is_ancestor(resolved, remote_ref, cwd=cwd) if has_remote else False
    out = {"commit": resolved[:12], "full": resolved, "exists": True,
           "in_local_main": bool(in_local), "landed": bool(landed),
           "remote_ref": remote_ref, "remote_ref_present": has_remote}
    if not has_remote:
        out["reason"] = "no %s remote-tracking ref; a landing claim CANNOT be supported" % remote_ref
    elif in_local and not landed:
        out["reason"] = ("THE BATCH-10 D-1 CASE: on local %s but NOT an ancestor of %s. "
                         "It has not landed." % (local_ref, remote_ref))
    elif not landed:
        out["reason"] = "not an ancestor of %s" % remote_ref
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("commits", nargs="+")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = [status(c, fetch=not a.no_fetch) for c in a.commits]
    if a.json:
        print(json.dumps(rows, indent=1))
    else:
        for r in rows:
            print("%-14s local_main=%-5s LANDED=%-5s %s" % (
                r["commit"], r["in_local_main"], r["landed"], r.get("reason", "")))
    ok = all(r["landed"] for r in rows)
    print("ALL LANDED" if ok else "NOT LANDED -- do not claim 'landed'/'on main'/'pushed'")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
