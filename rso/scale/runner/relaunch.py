"""The idempotent host-relaunch entry (C-013-T025; roadmap P-3).

    python -m rso.scale.runner relaunch <run_dir>

Meant to be fired by a host timer (Task Scheduler / systemd; RELAUNCH.md has the install commands, which are
documented and NOT run) every few minutes, forever. Every fire is safe, cheap and decides alone, from the run
directory, with no session and no conversation:

    every chain COMPLETE                   COMPLETE   nothing to do
    any chain HALTED                       HALTED     a disagreement waits for a resolver; never relaunched
    a live supervisor holds the run        RUNNING    nothing to do (one supervisor per run)
    the last supervisor stopped BLOCKED
    or CAP_REFUSED (needs a human)         BLOCKED    an operator's explicit `launch` re-arms the run
    otherwise (killed, host rebooted)      LAUNCHED   a detached supervisor, which resumes from the verified head

The check and the launch happen under <run>/supervisor/.relaunch.lock, and a launch returns only once the new
supervisor is live, so two fires that overlap launch one supervisor; the supervisor lock (supervisor.py
acquire_supervisor) is the second guard. Every fire appends one row to <run>/supervisor/relaunch.jsonl.
"""
import os
import time

from rso.scale.runner import engine as E
from rso.scale.runner import run as RUN
from rso.scale.runner import store as S
from rso.scale.runner import supervisor as SUP

EXIT = {"COMPLETE": 0, "RUNNING": 0, "LAUNCHED": 0, "HALTED": 4, "BLOCKED": 5, "LAUNCH_FAILED": 1}
LIVE_WAIT_S = 60


def _supervisor_live(run_dir):
    p = SUP._path(run_dir)
    return SUP._live(S.read_json(p) if os.path.exists(p) else None)


def _blocked(run_dir):
    """The newest supervisor lifecycle row is an END that needs a human (an explicit launch writes a newer START)."""
    rows, _ = S.read_jsonl(os.path.join(SUP.sdir(run_dir), "events.jsonl"))
    life = [r for r in rows if r.get("kind") in ("SUPERVISOR_START", "SUPERVISOR_END")]
    last = life[-1] if life else None
    if last and last["kind"] == "SUPERVISOR_END" and last.get("state") in ("BLOCKED", "CAP_REFUSED"):
        return last
    return None


def _launch(run_dir, code_root):
    return SUP.launch_detached(run_dir, code_root=code_root)


def relaunch(run_dir, code_root=E.REPO, spawn=_launch):
    SUP.guard_code_root(code_root)                              # the same refusal as `launch`: never the canonical tree
    run_dir = os.path.abspath(run_dir)
    m, mid = RUN.load_manifest(run_dir)
    out = {"manifest_id": mid}
    with S.FileLock(os.path.join(SUP.sdir(run_dir), ".relaunch.lock"), timeout=LIVE_WAIT_S + 60):
        states = {c: RUN.head(run_dir, c)["state"] for c in RUN.chain_ids(m)}
        if set(states.values()) == {RUN.COMPLETE}:
            out["action"] = "COMPLETE"
        elif RUN.HALTED in states.values():
            out.update(action="HALTED", chains=[c for c, s in states.items() if s == RUN.HALTED])
        elif _supervisor_live(run_dir):
            out["action"] = "RUNNING"
        elif _blocked(run_dir):
            b = _blocked(run_dir)
            out.update(action="BLOCKED", state=b.get("state"), reason=b.get("reason"))
        else:
            out["launch"] = spawn(run_dir, code_root)
            deadline = time.time() + LIVE_WAIT_S
            while not _supervisor_live(run_dir) and time.time() < deadline:
                time.sleep(0.1)
            out["action"] = "LAUNCHED" if _supervisor_live(run_dir) else "LAUNCH_FAILED"
        S.append_jsonl(os.path.join(SUP.sdir(run_dir), "relaunch.jsonl"),
                       dict(out, host=S.HOST, pid=os.getpid(), at_utc=RUN.utc_now()))
    return out
