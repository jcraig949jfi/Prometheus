"""A SIMULATED host scheduler (C-013-T025). It is a harness, not an installation: it invokes the relaunch entry on a
timer in a subprocess, exactly the command line a Task Scheduler / systemd timer would run, and records every fire.
Nothing here (or anywhere in C-013-T025) registers an OS job; RELAUNCH.md only documents the install commands.

fire_test() is the packet's acceptance run: a job is started, then EVERYTHING is killed (supervisor and worker, mid
epoch) and no session acts any more; the simulated scheduler alone fires until the run completes. Criteria:
    nothing_running_after_kill  no supervisor, no live lease, heads frozen, before the first fire
    first_fire_launches         the first fire after the kill is LAUNCHED
    later_fires_are_noops       every fire while the job runs is RUNNING (>= 1 seen), none launches a second one
    one_supervisor_after_kill   exactly one SUPERVISOR_START after the kill, and at most one supervisor process live
    completed_by_scheduler      FINAL_ACCOUNT.json exists and every chain is COMPLETE
    fire_after_completion_noop  a fire after completion answers COMPLETE and launches nothing
    interrupted_accounted       the killed attempt is accounted as interrupted/wasted work
    digest_equals_control       run digest == the uninterrupted control's
"""
import json
import os
import subprocess
import sys
import time

import psutil

from rso.scale.runner import account as A
from rso.scale.runner import control as CTL
from rso.scale.runner import engine as E
from rso.scale.runner import fire_test as FT
from rso.scale.runner import lease as L
from rso.scale.runner import run as RUN
from rso.scale.runner import store as S
from rso.scale.runner import supervisor as SUP


def runner_procs(run_dir):
    """Live processes of this run (supervisor, workers, relaunch fires), by command line."""
    out = []
    for p in psutil.process_iter(["pid", "cmdline"]):
        cl = p.info["cmdline"] or []
        if "rso.scale.runner" in cl and any(os.path.abspath(a) == run_dir for a in cl[3:] if a):
            out.append(p.info["pid"])
    return out


class SimulatedScheduler:
    def __init__(self, run_dir, code_root=E.REPO, interval_s=60.0, python=sys.executable):
        self.run_dir, self.code_root, self.interval_s, self.python = os.path.abspath(run_dir), code_root, interval_s, python
        self.fires, self.peak_procs = [], 0
        self.log = os.path.join(self.run_dir, "scheduler_sim", "fires.jsonl")

    def fire(self):
        t0 = time.time()
        r = subprocess.run([self.python, "-m", "rso.scale.runner", "relaunch", self.run_dir], cwd=self.code_root,
                           capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        try:
            action = json.loads(r.stdout.strip().splitlines()[-1])["action"]
        except (ValueError, IndexError, KeyError):
            action = "NO_ANSWER"
        row = {"fire": len(self.fires) + 1, "rc": r.returncode, "action": action, "wall_s": round(time.time() - t0, 3),
               "at_utc": RUN.utc_now(), "stderr_tail": r.stderr.strip()[-300:] if r.returncode else ""}
        self.fires.append(row)
        S.append_jsonl(self.log, row)
        return row

    def run(self, done, timeout_s):
        """Fire every interval_s (the first fire at once) until done() or timeout_s; sample the process count."""
        start, next_fire = time.time(), 0.0
        while time.time() - start < timeout_s:
            if time.time() - start >= next_fire:
                self.fire()
                next_fire += self.interval_s
                if done():
                    return True
            self.peak_procs = max(self.peak_procs, len(runner_procs(self.run_dir)))
            time.sleep(0.2)
        return False


def _kill_everything(run_dir, m):
    cur = S.read_json(SUP._path(run_dir))
    victims = [cur["pid"]] + [h["pid"] for h in (L.live_holder(run_dir, c) for c in RUN.chain_ids(m)) if h]
    for pid in victims:
        FT.kill_pid(pid)
    time.sleep(1)
    return victims


def fire_test(run_dir, code_root=E.REPO, interval_s=5.0, timeout_s=900):
    run_dir = os.path.abspath(run_dir)
    m, _ = RUN.load_manifest(run_dir)
    SUP.launch_detached(run_dir, code_root=code_root)           # the job is started (by whoever); then it is killed
    FT.wait_mid_epoch(run_dir, m, min_epoch=2, timeout=120)
    victims = _kill_everything(run_dir, m)
    h0 = FT.heads(run_dir, m)
    time.sleep(2)
    down = FT.nothing_running(run_dir, m)
    frozen = h0 == FT.heads(run_dir, m)                         # nobody advanced a head while everything was down
    starts_before = sum(1 for r in S.read_jsonl(os.path.join(SUP.sdir(run_dir), "events.jsonl"))[0]
                        if r.get("kind") == "SUPERVISOR_START")
    sched = SimulatedScheduler(run_dir, code_root, interval_s)
    finished = sched.run(lambda: os.path.exists(os.path.join(run_dir, "FINAL_ACCOUNT.json")), timeout_s)
    after = sched.fire()                                        # one more fire, after completion
    rows, _ = S.read_jsonl(os.path.join(SUP.sdir(run_dir), "events.jsonl"))
    starts_after = sum(1 for r in rows if r.get("kind") == "SUPERVISOR_START") - starts_before
    acts = [f["action"] for f in sched.fires[:-1]]
    acct = A.final_account(run_dir)
    control = CTL.control(run_dir)
    crit = {
        "nothing_running_after_kill": (not down["supervisor_live"] and not down["live_leases"] and frozen),
        "first_fire_launches": acts[:1] == ["LAUNCHED"],
        "later_fires_are_noops": acts.count("LAUNCHED") == 1 and acts[1:].count("RUNNING") >= 1
                                 and set(acts[1:]) <= {"RUNNING", "COMPLETE"},
        "one_supervisor_after_kill": starts_after == 1,
        "completed_by_scheduler": finished and acct["state"] == "COMPLETE",
        "fire_after_completion_noop": after["action"] == "COMPLETE",
        "interrupted_accounted": acct["wasted"]["interrupted_attempts"] >= 1,
        "digest_equals_control": acct["run_digest"] == control["run_digest"],
    }
    result = {"criteria": crit, "failed": [k for k, v in crit.items() if not v], "killed_pids": victims,
              "down_check": down, "heads_at_kill": h0, "fires": sched.fires, "peak_runner_processes_sampled": sched.peak_procs,
              "supervisor_starts_after_kill": starts_after, "run_digest": acct["run_digest"],
              "control_digest": control["run_digest"], "interval_s": interval_s,
              "interrupted": acct["wasted"]["interrupted_attempts"]}
    S.atomic_write_json(os.path.join(run_dir, "scheduler_sim", "RESULT.json"), result)
    return result
