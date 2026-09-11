"""TECHNE-44: does MY budget wrapper actually reap a forking tree, and does the
mechanism it uses matter on this host?

    PYTHONPATH=<repo> <env>/python -m techne.acquisition.checks.probe_budget_cancellation

WHY THIS EXISTS. Vivarium's EXTERNAL_BACKEND_CONTRACT ruled that `taskkill /T`
is best-effort by documentation and that cancellation must be a kernel object.
They are right, and budget.py used taskkill. I have replaced it with a Windows
job object -- and a replacement I have not measured is a second claim of the
same kind as the one it replaced.

THREE ARMS, and the third is the one that discriminates.

  LIVE_JOB       the shipping path on a live tree: KILL_ON_JOB_CLOSE, armed at
                 spawn. The arm that must be clean, because it is what ships.
  LIVE_TASKKILL  the same workload, job helper stubbed to fail, so cancellation
                 falls to `taskkill /T /F`. Differs from LIVE_JOB in MECHANISM
                 only.
  ORPHAN_*       the case taskkill cannot serve even in principle: the direct
                 child spawns a grandchild and EXITS IMMEDIATELY. The grandchild
                 is reparented, and the recorded pid is gone -- so a parent/child
                 walk rooted at that pid has nothing left to walk. A job object
                 still holds the orphan, because membership is a property of the
                 process rather than of a relation re-derived at kill time.

WHAT A RESULT MEANS, DECIDED BEFORE RUNNING. On the LIVE pair, a clean taskkill
arm is NOT evidence the contract is wrong -- it is one host at one timing, and
the documented guarantee is still absent. A survivor is evidence of the defect;
no survivor is the absence of evidence. The ORPHAN pair is where the two
mechanisms are expected to part, and if they do not part there either, that is
reported as measured rather than argued away.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time

from .. import budget as _budget
from .. import receipt

#: forks a grandchild, then outlives any budget this probe sets.
CHILD = ("import subprocess, sys, time\n"
         "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
         "print(p.pid, flush=True)\n"
         "time.sleep(120)\n")

#: forks a grandchild and exits at once, orphaning it.
ORPHAN_CHILD = ("import subprocess, sys\n"
                "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
                "print(p.pid, flush=True)\n")

PROFILE = {"name": "probe_cancellation", "network": "FORBIDDEN",
           "max_wall_seconds": 4, "max_processes": 8,
           "max_download_bytes": 0, "max_rss_bytes": None, "max_disk_bytes": None}


def _descendants(pid: int) -> list:
    """Direct children of pid, via CIM. wmic is gone on this Windows build."""
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Process -Filter 'ParentProcessId=%d').ProcessId" % pid],
        capture_output=True, text=True).stdout
    return [x for x in out.split() if x.isdigit()]


def _alive(pid: str) -> bool:
    r = subprocess.run(["tasklist", "/FI", "PID eq %s" % pid],
                       capture_output=True, text=True).stdout
    return pid in r


def _one_trial(force_degraded: bool, orphan: bool = False) -> dict:
    real = _budget._win_job_for
    if force_degraded:
        _budget._win_job_for = lambda pid: (None, "FORCED for the comparison arm")
    try:
        with _budget.Budget(profile=dict(PROFILE)) as b:
            p = b.spawn([sys.executable, "-c", ORPHAN_CHILD if orphan else CHILD])
            if orphan:
                # read the grandchild's pid from stdout BEFORE the child exits: once
                # it has, the relation this arm is about no longer exists to query.
                line = (p.stdout.readline() or "").strip()
                kids = [line] if line.isdigit() else []
                p.wait(timeout=10)
                time.sleep(0.5)
            else:
                time.sleep(2.0)
                kids = _descendants(p.pid)
            t0 = time.monotonic()
            b._kill_one(p)
            time.sleep(1.5)
            parent_alive = p.poll() is None
            survivors = [g for g in kids if _alive(g)]
            rec = b.resource_receipt()["cancellation"]
    finally:
        _budget._win_job_for = real
    return {"parent_pid": p.pid, "grandchildren_seen": kids,
            "parent_alive_after_cancel": parent_alive, "survivors": survivors,
            "tree_reaped": not parent_alive and not survivors,
            "cancel_seconds": round(time.monotonic() - t0, 3),
            "mechanism_used": [k["mechanism"] for k in rec["kills_performed"]],
            "jobs_failed_to_arm": rec["jobs_failed_to_arm"]}


def _summarise(trials: list) -> dict:
    return {"trials": len(trials),
            "grandchildren_observed": sum(len(t["grandchildren_seen"]) for t in trials),
            "trees_reaped": sum(1 for t in trials if t["tree_reaped"]),
            "survivors_total": sum(len(t["survivors"]) for t in trials),
            "mechanisms": sorted({m for t in trials for m in t["mechanism_used"]})}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=5)
    a = ap.parse_args(argv)

    if sys.platform != "win32":                                  # pragma: no cover
        print("this probe is about a Windows job object; skipping on", sys.platform)
        return 0

    arms = {
        "LIVE_JOB": [_one_trial(False) for _ in range(a.trials)],
        "LIVE_TASKKILL": [_one_trial(True) for _ in range(a.trials)],
        "ORPHAN_JOB": [_one_trial(False, orphan=True) for _ in range(a.trials)],
        "ORPHAN_TASKKILL": [_one_trial(True, orphan=True) for _ in range(a.trials)],
    }
    summary = {k: _summarise(v) for k, v in arms.items()}

    lj, lt = summary["LIVE_JOB"], summary["LIVE_TASKKILL"]
    oj, ot = summary["ORPHAN_JOB"], summary["ORPHAN_TASKKILL"]

    rec = receipt.new("ADAPTER_QUALIFICATION", "techne_budget_wrapper")
    rec["check"] = "process_tree_cancellation_mechanism"
    rec["consumer"] = ("techne.acquisition.budget, which meters preparation-time work "
                       "(pip, git, cargo, the stitch binary)")
    rec["clears"] = "TECHNE-44"
    rec["observations"] = {
        "schema": "techne.tools.cancellation_probe/2",
        "clears": "TECHNE-44",
        "why": ("Vivarium's contract ruled taskkill /T insufficient. budget.py now uses a "
                "Windows job object with KILL_ON_JOB_CLOSE. This measures the replacement "
                "rather than documenting it."),
        "workloads": {
            "LIVE": "a child that forks a grandchild and then sleeps past the budget",
            "ORPHAN": "a child that forks a grandchild and exits at once, reparenting it"},
        "arms": arms,
        "summary": summary,
        "reference_probe": {
            "path": "vivarium/tools/probe_process_tree_kill.py",
            "result_on_this_host": "TREE REAPED",
            "note": "Vivarium's own probe, run unmodified. This one differs in that it "
                    "cancels THROUGH budget.py rather than through a hand-built job, and "
                    "adds the orphan case."},
        "what_a_clean_live_taskkill_arm_does_NOT_mean": (
            "that the contract is wrong. Absence of a survivor on one host at one timing is "
            "not a guarantee; taskkill walks a parent/child relation it reads at kill time "
            "and promises nothing about a process that forks between the read and the kill."),
    }
    checks = [
        {"claim": "the SHIPPING arm reaps every live tree it was given, grandchildren included",
         "pass": lj["trees_reaped"] == lj["trials"] and lj["survivors_total"] == 0},
        {"claim": "the shipping arm actually used the job object, never the degraded path",
         "pass": lj["mechanisms"] == ["job_object"]},
        {"claim": "the workload really did fork -- a probe that saw no grandchild would be "
                  "testing nothing",
         "pass": lj["grandchildren_observed"] >= lj["trials"]
                 and oj["grandchildren_observed"] >= oj["trials"]},
        {"claim": "the degraded LIVE arm was genuinely degraded, so LIVE_JOB and "
                  "LIVE_TASKKILL differ in MECHANISM and not in setup",
         "pass": lt["mechanisms"] == ["taskkill_tree_DEGRADED"]},
        {"claim": "in the ORPHAN arms the recorded pid is already dead, so the degraded path "
                  "has NOTHING TO KILL and records none_NO_JOB_AND_PID_DEAD -- which is the "
                  "mechanism of the defect rather than a gap in the probe",
         "pass": ot["mechanisms"] == ["none_NO_JOB_AND_PID_DEAD"]
                 and oj["mechanisms"] == ["job_object"]},
        {"claim": "the job object reaps ORPHANS -- the case a parent/child walk cannot reach",
         "pass": oj["survivors_total"] == 0},
    ]
    rec["checks"] = checks
    rec["all_passed"] = all(c["pass"] for c in checks)
    rec["verdict"] = (
        "LIVE: job %d/%d reaped (%d survivors), taskkill %d/%d (%d survivors). "
        "ORPHAN: job %d/%d reaped (%d survivors), taskkill %d/%d (%d survivors). %s"
        % (lj["trees_reaped"], lj["trials"], lj["survivors_total"],
           lt["trees_reaped"], lt["trials"], lt["survivors_total"],
           oj["trees_reaped"], oj["trials"], oj["survivors_total"],
           ot["trees_reaped"], ot["trials"], ot["survivors_total"],
           ("THE ORPHAN ARM SEPARATES THEM: taskkill left %d orphaned grandchildren alive "
            "and the job object left none. That is direct measured evidence for Vivarium's "
            "ruling rather than an appeal to documentation."
            % ot["survivors_total"]) if ot["survivors_total"] > oj["survivors_total"] else
           ("Neither mechanism left a survivor on this host, orphans included. The job "
            "object still ships, because it is a guarantee where taskkill is an "
            "observation -- but this probe did NOT reproduce the defect and says so.")))
    rec["does_not_establish"] = ["INSTALLATION", "FIRST_USEFUL_CHECK",
                                 "PAPER_REPRODUCTION", "LOCAL_SCIENTIFIC_BENEFIT"]
    rec["scope"] = ("This qualifies a PREPARATION-time metering wrapper. It does not make "
                    "budget.py an admitted in-run backend: Vivarium's contract admits a "
                    "backend, not a kill mechanism.")
    path = receipt.write(rec)
    print(json.dumps(summary, indent=1))
    print("VERDICT", rec["verdict"])
    print("receipt", path)
    return 0 if rec["all_passed"] else 1


if __name__ == "__main__":                                       # pragma: no cover
    raise SystemExit(main())
