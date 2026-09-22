"""No git write while a live RowWriter exists — as an executable gate.

WHY THIS EXISTS

"Never make a git write in a worktree with a live RowWriter" has been a standing rule
all campaign. A rebase wedges on the open rows file, and a plain commit races the
writer's own periodic commit and KILLS the worker. Until now it was a MEMO: I obeyed it
by hand, checking a process census before each commit. This campaign's clearest finding
is that gates transfer and memos do not, so e06 inherits it as a gate.

IT CONSUMES THE AUTHORITATIVE SIGNAL, NOT A PROXY

primordial/fabric/rows.py already publishes writer liveness: every RowWriter registers
`{pid, tag, exp_id, path, ts}` at `<git-dir>/pm-rowwriters/<pid>-<id>.json` on __init__,
unlinks it on close(), and re-registers cleanup via atexit. `rows.live_writers(repo)`
reads those markers and reaps any whose pid is dead. So this module calls that, rather
than inventing a psutil cmdline scan - which is the mistake CW01-D046 taught (the
walk-up already existed in localrun) and which would also re-create the
kill-script-matches-itself family of defects.

THREE OUTCOMES

  PASS          markers were read and none is live: a git write is safe
  FAIL          a live writer exists: refuse
  NOT_VERIFIED  liveness could not be determined (rows.py unimportable, path not in a
                git worktree). NEVER treated as safe - "I could not look" is not
                "nothing is there" (CW01-D034/D051 family).
"""
from __future__ import annotations

import pathlib
import sys


class LiveRowWriter(AssertionError):
    """Raised when a git write is attempted while a RowWriter holds the worktree."""


def _rows_module(repo):
    """Import primordial.fabric.rows relative to the discovered repo root."""
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from primordial.fabric import rows      # noqa: PLC0415
    return rows


def check(repo):
    """Is a git write safe in this worktree right now?"""
    repo = pathlib.Path(repo)
    try:
        rows = _rows_module(repo)
    except Exception as e:                                   # noqa: BLE001
        return {"outcome": "NOT_VERIFIED", "live": None, "repo": str(repo),
                "reason": "cannot import primordial.fabric.rows (%s); liveness unknown, "
                          "which is NOT the same as safe" % type(e).__name__}
    try:
        live = rows.live_writers(str(repo))
    except Exception as e:                                   # noqa: BLE001
        return {"outcome": "NOT_VERIFIED", "live": None, "repo": str(repo),
                "reason": "live_writers failed (%s: %s); liveness unknown"
                          % (type(e).__name__, str(e)[:80])}
    n = len(live)
    return {"outcome": "PASS" if n == 0 else "FAIL", "live": live, "repo": str(repo),
            "n_live": n,
            "reason": ("no live RowWriter markers; a git write is safe" if n == 0 else
                       "%d live RowWriter(s): %s" % (n, [w.get("exp_id") for w in live]))}


def require_quiet(repo):
    """Fail closed rather than race a live writer's own commit."""
    v = check(repo)
    if v["outcome"] != "PASS":
        raise LiveRowWriter("%s: %s" % (v["repo"], v["reason"]))
    return v


if __name__ == "__main__":
    import os

    here = pathlib.Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    import repopath as RP

    repo = RP.find_root(here)
    campaign = RP.find_campaign_root(here)
    ok = True

    def ck(label, cond, detail=""):
        global ok
        ok &= bool(cond)
        print("   %-46s %s %s" % (label, "PASS" if cond else "FAIL", detail))

    print("  -- gate proven against a REAL RowWriter --")
    os.environ.setdefault("PM_TAG", "m1-cw01e06g")
    rows = _rows_module(repo)

    baseline = check(repo)
    ck("quiet worktree admits a git write", baseline["outcome"] == "PASS", baseline["reason"][:44])

    probe = campaign / "experiments" / "cw01-e06" / "rows" / ".gate_probe.jsonl"
    w = rows.RowWriter(str(probe), "CW01-E06-GATE")     # writes NO rows -> close() cannot commit
    try:
        v = check(repo)
        ck("refuses while a RowWriter is live", v["outcome"] == "FAIL", v["reason"][:52])
        raised = False
        try:
            require_quiet(repo)
        except LiveRowWriter:
            raised = True
        ck("require_quiet fails closed", raised)
    finally:
        w.close()                                       # n == n_committed == 0 -> no commit
        probe.unlink(missing_ok=True)

    after = check(repo)
    ck("admits again once the writer closes", after["outcome"] == "PASS",
       "marker reaped, %s" % after["reason"][:32])

    bad = check(pathlib.Path(os.environ.get("TEMP", "/tmp")))
    ck("non-worktree path is NOT_VERIFIED, not PASS", bad["outcome"] == "NOT_VERIFIED",
       bad["reason"][:44])

    print("\n   %s" % ("writerlock proven by observed refusal" if ok else "FAILURES PRESENT"))
    sys.exit(0 if ok else 1)
