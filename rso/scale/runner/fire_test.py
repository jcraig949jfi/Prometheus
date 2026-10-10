"""The fire test (C-013-T022 acceptance; architecture s4): kill the worker, the supervisor and the launching
session; resume from the last verified checkpoint in a DIFFERENT session; the final digest must equal an
uninterrupted control's, with the wasted work accounted.

Four phases, each a separate command, so each can run in a different session (the point: the job, not the
conversation, owns the state). Every phase appends to <run_dir>/FIRE_LOG.jsonl with its pid, parent pid and the
harness session id (CLAUDE_CODE_SESSION_ID), so which session did what is recorded, not asserted.

    python -m rso.scale.runner.fire_test start  --run-dir D   create the run (Aether kernel, 2 partitions), launch a
                                                               detached supervisor, see a worker computing, then
                                                               KILL ITS OWN PROCESS (no cleanup, no exit handlers)
    python -m rso.scale.runner.fire_test kill   --run-dir D   check the launcher and its session are gone and the job
                                                               kept computing; kill the worker mid-epoch; let the
                                                               supervisor replace it; kill the supervisor and the new
                                                               worker mid-epoch; check nothing is left running
    python -m rso.scale.runner.fire_test resume --run-dir D   (another session) check nothing is running, relaunch a
                                                               detached supervisor, see it resume, return
    python -m rso.scale.runner.fire_test verify --run-dir D   wait for FINAL_ACCOUNT.json, run the control, compare,
                                                               write FIRE_RESULT.json (PASS / FAIL per criterion)
    python -m rso.scale.runner.fire_test evidence --run-dir D --out <repo dir>   copy the small records into Git

Run it from a pinned worktree (WORKING_CONTRACT s6). Computation never exceeds two processes (supervisor + one
worker; the control runs only after the supervisor has exited); the phase driver itself only polls and sleeps.
"""
import argparse
import json
import os
import shutil
import signal
import sys
import time

import psutil

from rso.scale.runner import account as A
from rso.scale.runner import control as CTL
from rso.scale.runner import lease as L
from rso.scale.runner import run as RUN
from rso.scale.runner import store as S
from rso.scale.runner import supervisor as SUP

# B_balanced physics (Aether/observatory/aeth02_falsifiers.py:46-51, the values the AETH-02 trajectories ran);
# a 128x128 lattice so an epoch lasts seconds on one core and a kill can land inside one.
FIRE_SPEC = {
    "name": "fire",
    "runtime": {"name": "rso.runner.aether_kernel", "version": 1},
    "params": {"h": 128, "w": 128, "regime": "random_soup", "energy_mode": "uniform", "rng_seed": 0xA37E01,
               "seed": 0x5C011701, "write_cost": 1, "maintenance_cost": 1, "replenish_numer": 536870912,
               "replenish_amount": 8, "mut_numer": 429496730, "ticks_per_epoch": 240, "trace_every": 20},
    "partitions": [{"partition_id": "p0", "params": {}},
                   {"partition_id": "p1", "params": {"seed": 0x5C011702, "rng_seed": 0xA37E02}}],
    "epochs": 16,
    "replay_every": 4,
    "caps": {"cpu_core_s": 3600},
    "question_ref": "ops/campaigns/C-013/tasks/C-013-T022/TASK.json (engineering fire test; no scientific claim)",
}


def ident():
    return {"pid": os.getpid(), "ppid": os.getppid(), "host": S.HOST, "cpu_s": round(time.process_time(), 6),
            "create_time": psutil.Process(os.getpid()).create_time(),
            "harness_session": (os.environ.get("CLAUDE_CODE_SESSION_ID") or "")[:8] or None,
            "harness_pid": int(os.environ["CLAUDE_PID"]) if os.environ.get("CLAUDE_PID", "").isdigit() else None}


def log(run_dir, row):
    row = dict(row, at_utc=RUN.utc_now(), by=ident())
    S.append_jsonl(os.path.join(run_dir, "FIRE_LOG.jsonl"), row)
    print(json.dumps(row, sort_keys=True), flush=True)
    return row


def fire_rows(run_dir):
    return S.read_jsonl(os.path.join(run_dir, "FIRE_LOG.jsonl"))[0]


def alive(pid, create_time=None):
    return pid is not None and S.pid_alive(pid, create_time)


def launch_record(run_dir):
    return S.read_json(os.path.join(SUP.sdir(run_dir), "LAUNCH.json"))


def progress_rows(run_dir, m):
    out = []
    for c in RUN.chain_ids(m):
        rows, _ = S.read_jsonl(RUN.events_path(run_dir, c))
        out += [r for r in rows if r.get("kind") == "PROGRESS"]
    return out


def wait_mid_epoch(run_dir, m, *, min_epoch, exclude_pids=(), timeout=300):
    """The newest PROGRESS row of a live worker that is strictly inside an epoch >= min_epoch."""
    tpe = m["epoch_budget"]["ticks_per_epoch"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        for c in RUN.chain_ids(m):
            p = RUN.latest_progress(run_dir, c)
            if (p and p["epoch_index"] >= min_epoch and 0 < p["ticks_done"] < tpe - m["partitions"][0]["params"][
                    "trace_every"] and p["pid"] not in exclude_pids and alive(p["pid"])):
                return p
        time.sleep(0.05)
    raise TimeoutError("no live worker mid-epoch >= {} within {} s".format(min_epoch, timeout))


def kill_pid(pid):
    """Hard kill: TerminateProcess on Windows, SIGKILL on POSIX. No handler, no finally, no flush runs."""
    try:
        psutil.Process(pid).kill()
    except psutil.NoSuchProcess:
        return False
    psutil.wait_procs([psutil.Process(pid)] if psutil.pid_exists(pid) else [], timeout=15)
    return True


def heads(run_dir, m):
    return {c: RUN.head(run_dir, c) for c in RUN.chain_ids(m)}


def nothing_running(run_dir, m):
    p = os.path.join(SUP.sdir(run_dir), "SUPERVISOR.json")
    sup = S.read_json(p) if os.path.exists(p) else None
    return {"supervisor_live": SUP._live(sup), "live_leases": {c: L.live_holder(run_dir, c) for c in RUN.chain_ids(m)
                                                                 if L.live_holder(run_dir, c)}}


def rehearsal_spec():
    """A smaller lattice for rehearsing the phases; never the acceptance run."""
    spec = json.loads(json.dumps(FIRE_SPEC))
    spec["name"] = "rehearsal"
    spec["params"].update(h=64, w=64, ticks_per_epoch=200)
    spec["epochs"] = 6
    return spec


def phase_start(run_dir, rehearsal=False):
    if os.path.exists(run_dir):
        raise SystemExit("{} exists: a fire test starts from an empty run directory".format(run_dir))
    m = RUN.create_run(run_dir, **(rehearsal_spec() if rehearsal else FIRE_SPEC))
    _, mid = RUN.load_manifest(run_dir)
    log(run_dir, {"phase": "start", "event": "RUN_CREATED", "manifest_id": mid, "code_sha": m["engine"]["code_sha"],
                  "runner_paths_dirty": m["engine"]["runner_paths_dirty"]})
    rec = SUP.launch_detached(run_dir)
    log(run_dir, {"phase": "start", "event": "SUPERVISOR_LAUNCHED", "launch": rec})
    p = wait_mid_epoch(run_dir, m, min_epoch=1, timeout=120)
    log(run_dir, {"phase": "start", "event": "WORKER_COMPUTING", "progress": p})
    log(run_dir, {"phase": "start", "event": "LAUNCHER_SELF_KILL",
                  "note": "the launching process kills itself; its session then ends"})
    os.kill(os.getpid(), signal.SIGTERM if os.name == "nt" else signal.SIGKILL)


def phase_kill(run_dir, session_wait_s=180):
    m, _ = RUN.load_manifest(run_dir)
    start = next(r for r in fire_rows(run_dir) if r.get("event") == "LAUNCHER_SELF_KILL")
    launcher, session_pid = start["by"]["pid"], start["by"]["harness_pid"]
    deadline = time.time() + session_wait_s
    while time.time() < deadline and (alive(launcher, start["by"]["create_time"]) or alive(session_pid)):
        time.sleep(1)
    n_before = len(progress_rows(run_dir, m))
    time.sleep(3)
    n_after = len(progress_rows(run_dir, m))
    rec = launch_record(run_dir)
    log(run_dir, {"phase": "kill", "event": "LAUNCHER_AND_SESSION_GONE",
                  "launcher_pid": launcher, "launcher_alive": alive(launcher, start["by"]["create_time"]),
                  "launching_session": start["by"]["harness_session"], "launching_session_pid": session_pid,
                  "launching_session_alive": alive(session_pid),
                  "supervisor_pid": rec["supervisor_pid"], "supervisor_alive": alive(rec["supervisor_pid"]),
                  "progress_rows_in_3s_after": n_after - n_before, "heads": heads(run_dir, m)})
    p1 = wait_mid_epoch(run_dir, m, min_epoch=2)
    kill_pid(p1["pid"])
    log(run_dir, {"phase": "kill", "event": "KILLED_WORKER", "victim": p1, "victim_alive": alive(p1["pid"]),
                  "supervisor_alive": alive(rec["supervisor_pid"])})
    p2 = wait_mid_epoch(run_dir, m, min_epoch=2, exclude_pids=(p1["pid"],))
    kill_pid(rec["supervisor_pid"])
    kill_pid(p2["pid"])
    time.sleep(1)
    log(run_dir, {"phase": "kill", "event": "KILLED_SUPERVISOR_AND_WORKER", "supervisor_pid": rec["supervisor_pid"],
                  "victim": p2, "supervisor_alive": alive(rec["supervisor_pid"]), "worker_alive": alive(p2["pid"])})
    h0 = heads(run_dir, m)
    time.sleep(5)
    h1 = heads(run_dir, m)
    log(run_dir, {"phase": "kill", "event": "ALL_DOWN", "heads_unchanged_5s": h0 == h1, "heads": h1,
                  "running": nothing_running(run_dir, m)})


def phase_resume(run_dir):
    m, _ = RUN.load_manifest(run_dir)
    pre = nothing_running(run_dir, m)
    log(run_dir, {"phase": "resume", "event": "PRECONDITION", "running": pre, "heads": heads(run_dir, m)})
    if pre["supervisor_live"] or pre["live_leases"]:
        raise SystemExit("something is still running; the fire test resumes only a fully dead job")
    rec = SUP.launch_detached(run_dir)
    log(run_dir, {"phase": "resume", "event": "SUPERVISOR_RELAUNCHED", "launch": rec})
    killed = {r["victim"]["pid"] for r in fire_rows(run_dir) if r.get("victim")}
    p = wait_mid_epoch(run_dir, m, min_epoch=1, exclude_pids=tuple(killed), timeout=180)
    log(run_dir, {"phase": "resume", "event": "RESUMED_WORKER_COMPUTING", "progress": p})


def phase_verify(run_dir, timeout=540):
    m, mid = RUN.load_manifest(run_dir)
    fin = os.path.join(run_dir, "FINAL_ACCOUNT.json")
    deadline = time.time() + timeout
    while time.time() < deadline and not os.path.exists(fin):
        time.sleep(2)
    if not os.path.exists(fin):
        log(run_dir, {"phase": "verify", "event": "NOT_FINISHED", "heads": heads(run_dir, m)})
        return 3
    rec = launch_record(run_dir)
    while alive(rec["supervisor_pid"]):                          # the control starts only after the job's processes end
        time.sleep(0.5)
    acct = S.read_json(fin)
    ctl = CTL.control(run_dir)
    rows = fire_rows(run_dir)
    ev = {r["event"]: r for r in rows if "event" in r}
    resume_checks = []
    for c in RUN.chain_ids(m):
        rs, _ = S.read_jsonl(RUN.events_path(run_dir, c))
        resume_checks += [dict(r, chain_id=c) for r in rs if r.get("kind") == "RESUME_CHECK" and r["head_index"] > 0]
    pubs = {c: sorted(RUN.publications(run_dir, c)) for c in RUN.chain_ids(m)}
    resumed_heads = ev["PRECONDITION"]["heads"]
    relaunch_at = ev["SUPERVISOR_RELAUNCHED"]["at_utc"]
    # every chain that was mid-run when the job died resumed at its published head, verified, not at genesis
    resumed_from = {c: any(r["head_index"] == h["head_index"] and r["verdict"] == "VALID" and r["at_utc"] > relaunch_at
                           for r in resume_checks if r["chain_id"] == c)
                    for c, h in resumed_heads.items() if h["state"] == RUN.OPEN and h["head_index"] > 0}
    srows, _ = S.read_jsonl(os.path.join(SUP.sdir(run_dir), "events.jsonl"))
    sup_cpu = {}
    for r in srows:
        if "cpu_s" in r:
            sup_cpu[r["pid"]] = max(sup_cpu.get(r["pid"], 0.0), r["cpu_s"])
    driver_cpu = {}
    for r in rows:
        driver_cpu[r["by"]["pid"]] = max(driver_cpu.get(r["by"]["pid"], 0.0), r["by"].get("cpu_s") or 0.0)
    overhead_cpu = round(sum(sup_cpu.values()) + sum(driver_cpu.values()), 6)
    crit = {
        "launcher_dead_and_job_kept_computing": (not ev["LAUNCHER_AND_SESSION_GONE"]["launcher_alive"]
                                                 and ev["LAUNCHER_AND_SESSION_GONE"]["supervisor_alive"]
                                                 and ev["LAUNCHER_AND_SESSION_GONE"]["progress_rows_in_3s_after"] > 0),
        "launching_session_gone": not ev["LAUNCHER_AND_SESSION_GONE"]["launching_session_alive"],
        "worker_killed_mid_epoch": not ev["KILLED_WORKER"]["victim_alive"],
        "supervisor_and_worker_killed_mid_epoch": (not ev["KILLED_SUPERVISOR_AND_WORKER"]["supervisor_alive"]
                                                   and not ev["KILLED_SUPERVISOR_AND_WORKER"]["worker_alive"]),
        "nothing_ran_while_down": ev["ALL_DOWN"]["heads_unchanged_5s"],
        "resume_in_a_different_session": (ev["SUPERVISOR_RELAUNCHED"]["by"]["harness_session"] not in
                                          (ev["LAUNCHER_SELF_KILL"]["by"]["harness_session"], None)),
        "resumed_from_checkpoint_not_genesis": bool(resumed_from) and all(resumed_from.values()),
        "every_resume_verified": bool(resume_checks) and all(r["verdict"] == "VALID" for r in resume_checks),
        "every_epoch_published_once": all(v == list(range(1, m["epochs"] + 1)) for v in pubs.values())
                                      and acct["outcomes"]["PUBLISHED"] == m["epochs"] * len(pubs),
        "final_digest_equals_control": acct["run_digest"] == ctl["run_digest"],
        "final_state_equals_control": all(acct["chains"][c]["final_state_digest"] ==
                                          ctl["chains"][c]["final_state_digest"] for c in pubs),
        "wasted_work_accounted": acct["wasted"]["interrupted_attempts"] == 2 and acct["wasted"]["ticks_lower_bound"] > 0,
        "within_one_core_hour": acct["resources"]["total_cpu_s"] + ctl["cpu_s"] + overhead_cpu <= 3600,
    }
    result = {"schema": "rso.runner.fire_result.v1", "manifest_id": mid, "verdict": "PASS" if all(crit.values()) else
              "FAIL", "criteria": crit, "run_digest": acct["run_digest"], "control_run_digest": ctl["run_digest"],
              "control": {c: {k: v for k, v in ctl["chains"][c].items() if k != "epoch_digests"} for c in pubs},
              "control_cpu_s": ctl["cpu_s"], "supervisor_cpu_s_by_pid": sup_cpu,
              "driver_cpu_s_by_pid_lower_bound": driver_cpu,
              "cpu_s_total": round(acct["resources"]["total_cpu_s"] + ctl["cpu_s"] + overhead_cpu, 6),
              "resumed_from_head": resumed_from,
              "sessions": {e: ev[e]["by"]["harness_session"] for e in ("LAUNCHER_SELF_KILL", "KILLED_WORKER",
                                                                       "SUPERVISOR_RELAUNCHED")},
              "wasted": acct["wasted"], "interrupted": acct["interrupted"],
              "resources": acct["resources"], "resume_checks": resume_checks,
              "heads_at_resume": {c: h["head_index"] for c, h in resumed_heads.items()}}
    S.atomic_write_json(os.path.join(run_dir, "FIRE_RESULT.json"), result)
    log(run_dir, {"phase": "verify", "event": "RESULT", "verdict": result["verdict"], "criteria": crit})
    return 0 if result["verdict"] == "PASS" else 1


def phase_evidence(run_dir, out):
    """Copy the small records (no checkpoint bytes) into the repository."""
    os.makedirs(out, exist_ok=True)
    for name in ("RUN_MANIFEST.json", "FIRE_LOG.jsonl", "FIRE_RESULT.json", "FINAL_ACCOUNT.json"):
        if os.path.exists(os.path.join(run_dir, name)):
            shutil.copy2(os.path.join(run_dir, name), os.path.join(out, name))
    for d in ("supervisor",):
        for root, _, files in os.walk(os.path.join(run_dir, d)):
            for f in files:
                if f.startswith("."):
                    continue
                rel = os.path.relpath(os.path.join(root, f), run_dir)
                os.makedirs(os.path.dirname(os.path.join(out, rel)), exist_ok=True)
                shutil.copy2(os.path.join(root, f), os.path.join(out, rel))
    m, _ = RUN.load_manifest(run_dir)
    for c in RUN.chain_ids(m):
        for f in ("GENESIS.json", "HEAD.json", "publications.jsonl", "outcomes.jsonl", "events.jsonl"):
            src = os.path.join(RUN.pdir(run_dir, c), f)
            if os.path.exists(src):
                os.makedirs(os.path.join(out, "partitions", c), exist_ok=True)
                shutil.copy2(src, os.path.join(out, "partitions", c, f))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m rso.scale.runner.fire_test")
    ap.add_argument("phase", choices=("start", "kill", "resume", "verify", "evidence"))
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out")
    ap.add_argument("--timeout", type=int, default=540)
    ap.add_argument("--session-wait", type=int, default=180, help="kill: seconds to wait for the launching session")
    ap.add_argument("--rehearsal", action="store_true", help="start: small lattice, for rehearsing the phases")
    a = ap.parse_args(argv)
    rd = os.path.abspath(a.run_dir)
    if a.phase in ("start", "resume"):
        SUP.guard_code_root(RUN.E.REPO)
    if a.phase == "start":
        phase_start(rd, a.rehearsal)
    elif a.phase == "kill":
        phase_kill(rd, a.session_wait)
    elif a.phase == "resume":
        phase_resume(rd)
    elif a.phase == "verify":
        return phase_verify(rd, a.timeout)
    elif a.phase == "evidence":
        phase_evidence(rd, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
