"""Fabric pilot harness -- P1, P2 (local), P3, P4, P5, P8 with REAL worker processes on this host.

Every worker is a separate OS process (python -m fabric worker ...) talking to
the canonical store; failures are induced for real (SIGKILL of a worker's
process group). Evidence per test: fabric/pilot/evidence/<P>.json.

    EW_DB_HOST=192.168.1.202 python3 fabric/pilot/run_pilot.py P1 P2L P3 P4 P5 P8
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from fabric import store as S  # noqa: E402

EV = Path(__file__).parent / "evidence"; EV.mkdir(exist_ok=True)
PY = sys.executable
PRINCIPAL = "PilotHarness"
RESEARCH = ["repo.read", "research.repo_readonly", "research.synthesis", "compute.cpu.light", "python.stdlib"]


def now():
    return time.strftime("%FT%TZ", time.gmtime())


def worker(agent, caps, *, ttl=20, idle=60, extra=()):
    return subprocess.Popen([PY, "-m", "fabric", "worker", "--agent", agent, "--caps", *caps, "--executors", "synthetic",
                             "--poll-s", "1", "--ttl-s", str(ttl), "--idle-exit-s", str(idle), *extra],
                            cwd=str(REPO), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)


def stop(p):
    if p.poll() is None:
        os.killpg(p.pid, signal.SIGTERM)
        try:
            p.wait(10)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL); p.wait()


def submit(conn, key, caps, seconds=2, **kw):
    params = dict({"seconds": seconds, "text": "pilot " + key}, **kw.pop("params", {}))
    return S.submit(conn, PRINCIPAL, "pilot task " + key, "synthetic", required_caps=caps, params=params,
                    idempotency_key="pilot-{}-{}".format(RUN, key), thread_id="thr-fabricpilot0", **kw)["task_id"]


def wait(pred, timeout, step=1.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        v = pred()
        if v:
            return v
        time.sleep(step)
    return None


def state(conn, tid):
    return S.get_task(conn, tid)["state"]


def completer(conn, tid):
    t = S.get_task(conn, tid)
    ok = [a for a in t["attempts"] if a["status"] == "succeeded"]
    return ok[0]["agent"] if ok else None


def save(name, obj):
    obj = dict(obj, test=name, run=RUN, finished=now())
    (EV / (name + ".json")).write_text(json.dumps(obj, indent=1, default=str))
    print(json.dumps({"test": name, "pass": obj.get("pass")}), flush=True)
    return obj


# ---------------------------------------------------------------------------- tests
def p1(conn):
    """capability routing: research tasks must go only to the worker that has the capability."""
    full = worker("worker.pilot.full", RESEARCH); lite = worker("worker.pilot.lite", ["compute.cpu.light"])
    ids = {"r1": submit(conn, "p1-r1", ["research.repo_readonly"]), "r2": submit(conn, "p1-r2", ["research.repo_readonly"]),
           "s1": submit(conn, "p1-s1", ["research.synthesis"]), "c1": submit(conn, "p1-c1", ["compute.cpu.light"])}
    wait(lambda: all(state(conn, t) == "completed" for t in ids.values()), 120)
    who = {k: completer(conn, t) for k, t in ids.items()}
    lite_attempts = [a for t in ids.values() for a in S.get_task(conn, t)["attempts"] if a["agent"] == "worker.pilot.lite"]
    stop(full); stop(lite)
    c1_attempts = {x["attempt_id"] for x in S.get_task(conn, ids["c1"])["attempts"]}
    ok = (all(state(conn, t) == "completed" for t in ids.values())                 # everything done
          and all(who[k] == "worker.pilot.full" for k in ("r1", "r2", "s1"))              # research only by the capable worker
          and all(a["attempt_id"] in c1_attempts for a in lite_attempts))          # lite touched nothing but compute
    return save("P1", {"pass": ok, "tasks": ids, "completed_by": who,
                       "lite_attempts": [(a["attempt_id"], a["status"]) for a in lite_attempts],
                       "note": "no task named a machine; pilot.lite advertises only compute.cpu.light"})


def p2_local(conn):
    """atomic claim under contention: 20 tasks, 3 worker processes started together; every task exactly one attempt."""
    ids = [submit(conn, "p2-%02d" % i, ["research.repo_readonly"], seconds=0.5) for i in range(20)]
    ws = [worker("worker.pilot.race%d" % i, RESEARCH) for i in range(3)]
    wait(lambda: all(state(conn, t) == "completed" for t in ids), 180)
    for w in ws:
        stop(w)
    per = {t: [(a["agent"], a["status"]) for a in S.get_task(conn, t)["attempts"]] for t in ids}
    claims = sum(1 for t in ids for e in S.events(conn, t) if e["kind"] == "claimed")
    ok = all(len(v) == 1 and v[0][1] == "succeeded" for v in per.values()) and claims == 20
    by = {}
    for v in per.values():
        by[v[0][0]] = by.get(v[0][0], 0) + 1
    return save("P2-local", {"pass": ok, "tasks": 20, "claimed_events": claims, "attempts_per_task": {t: len(v) for t, v in per.items()},
                             "tasks_by_worker": by, "note": "same host; cross-host race is P2 (needs worker.ubu002)"})


def p3(conn):
    """the principal's process exits; the task survives and is retrievable by a new process."""
    r = subprocess.run([PY, "-m", "fabric", "submit", "--as", "PilotPrincipal", "--executor", "synthetic", "--cap", "research.synthesis",
                        "--param", "seconds=3", "--param", 'text="survived the principal"', "--instruction", "p3 task",
                        "--key", "pilot-%s-p3" % RUN], cwd=str(REPO), capture_output=True, text=True)
    tid = json.loads(r.stdout)["task_id"]
    principal_pid_alive = False                      # subprocess.run returned: the principal process is gone
    before = state(conn, tid)
    w = worker("worker.pilot.full", RESEARCH)
    wait(lambda: state(conn, tid) == "completed", 60)
    stop(w)
    got = subprocess.run([PY, "-m", "fabric", "show", tid], cwd=str(REPO), capture_output=True, text=True)   # a NEW process
    t = json.loads(got.stdout)
    fin = [a for a in t["artifacts"] if a["name"] == "final_text.md"]
    text = S.artifact_content(conn, fin[0]["artifact_id"])["content"].decode() if fin else None
    ok = before == "submitted" and t["state"] == "completed" and text and "survived the principal" in text
    return save("P3", {"pass": ok, "task": tid, "state_after_principal_exit": before, "final_state": t["state"],
                       "retrieved_by_new_process": True, "final_text": text, "principal_process_alive": principal_pid_alive})


def p4(conn):
    """kill a worker mid-attempt; the attempt is abandoned, nothing falsely completes, a second worker finishes."""
    tid = submit(conn, "p4", ["research.synthesis"], seconds=20, max_attempts=3)
    a = worker("worker.pilot.victim", RESEARCH, ttl=15)
    wait(lambda: state(conn, tid) == "working", 60, 0.5)
    first = S.get_task(conn, tid)["attempts"][-1]["attempt_id"]
    time.sleep(3)
    os.killpg(a.pid, signal.SIGKILL); a.wait(); killed_at = now()
    b = worker("worker.pilot.rescuer", RESEARCH, ttl=15)
    t_rescue = time.time()
    wait(lambda: state(conn, tid) == "completed", 120)
    stop(b)
    t = S.get_task(conn, tid)
    att = {x["attempt_id"]: x for x in t["attempts"]}
    first_arts = [x for x in t["artifacts"] if x["attempt_id"] == first]
    ev = [(e["kind"], e["attempt_id"]) for e in S.events(conn, tid)]
    ok = att[first]["status"] == "abandoned" and not first_arts and t["state"] == "completed" and len(t["attempts"]) == 2 \
        and t["attempts"][1]["agent"] == "worker.pilot.rescuer" and t["attempts"][1]["status"] == "succeeded"
    return save("P4", {"pass": ok, "task": tid, "killed_attempt": first, "killed_at": killed_at,
                       "attempts": [(x["attempt_id"], x["agent"], x["status"], x["error"]) for x in t["attempts"]],
                       "artifacts_from_killed_attempt": len(first_arts), "seconds_kill_to_completion": round(time.time() - t_rescue, 1),
                       "events": ev})


def p5(conn):
    """a held lease makes the heavy task wait while the worker completes research work instead."""
    hold = S.lease_acquire(conn, "pilot:cpu8", "PilotHolder", "ubu001", purpose="P5: someone else's campaign", ttl_s=900)
    heavy = submit(conn, "p5-heavy", ["compute.cpu.light"], seconds=3, resources=["pilot:cpu8"], priority=10)
    light = submit(conn, "p5-research", ["research.repo_readonly"], seconds=3)
    w = worker("worker.pilot.full", RESEARCH)
    t0 = time.time()
    wait(lambda: state(conn, light) == "completed", 60)
    research_done = time.time() - t0
    time.sleep(5)
    heavy_while_held = S.get_task(conn, heavy)
    released = S.lease_release(conn, hold["lease_id"], hold["token"], "PilotHolder"); t_rel = time.time()
    wait(lambda: state(conn, heavy) == "completed", 60)
    heavy_after = S.get_task(conn, heavy)
    stop(w)
    ev = [e["kind"] for e in S.events(conn, heavy)]
    ok = hold["result"] == "ACQUIRED" and heavy_while_held["state"] == "submitted" and heavy_while_held["waiting_reason"] == \
        "resource pilot:cpu8 busy" and state(conn, light) == "completed" and heavy_after["state"] == "completed" and released
    return save("P5", {"pass": ok, "lease": hold.get("lease_id"), "heavy": heavy, "research": light,
                       "research_completed_after_s": round(research_done, 1),
                       "heavy_state_while_held": heavy_while_held["state"], "heavy_waiting_reason": heavy_while_held["waiting_reason"],
                       "heavy_completed_after_release_s": round(time.time() - t_rel, 1), "heavy_events": ev})


def p8(conn, task_id):
    """restart the gateway; the task as seen over A2A is unchanged."""
    port = 8712
    env = dict(os.environ, FABRIC_GATEWAY_URL="http://127.0.0.1:%d" % port)

    def rpc(method, params):
        req = urllib.request.Request("http://127.0.0.1:%d/a2a/jsonrpc" % port, method="POST",
                                     data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                                     headers={"Content-Type": "application/json", "A2A-Version": "1.0"})
        return json.loads(urllib.request.urlopen(req, timeout=30).read())

    def start():
        g = subprocess.Popen([PY, "-m", "fabric", "gateway", "--port", str(port)], cwd=str(REPO), env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, start_new_session=True)
        time.sleep(2)
        return g
    g = start(); before = rpc("GetTask", {"id": task_id}); lst1 = rpc("ListTasks", {"pageSize": 5})
    os.killpg(g.pid, signal.SIGKILL); g.wait()
    down_err = None
    try:
        rpc("GetTask", {"id": task_id})
    except Exception as e:
        down_err = type(e).__name__
    g = start(); after = rpc("GetTask", {"id": task_id}); lst2 = rpc("ListTasks", {"pageSize": 5})
    stop(g)
    ok = before == after and down_err is not None and lst1["result"]["totalSize"] <= lst2["result"]["totalSize"]
    return save("P8", {"pass": ok, "task": task_id, "identical_before_after": before == after, "gateway_down_error": down_err,
                       "state": after["result"]["status"]["state"], "list_total_before": lst1["result"]["totalSize"],
                       "list_total_after": lst2["result"]["totalSize"]})


RUN = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
if __name__ == "__main__":
    # A closed world: the fleet's real workers (e.g. worker.ubu002) share the canonical "fabric" schema and would
    # legitimately claim pilot tasks whose capabilities they have (seen 2026-09-28: ubu002 took P1's r2). The pilot
    # therefore runs in its own schema; its worker subprocesses inherit FABRIC_SCHEMA.
    os.environ.setdefault("FABRIC_SCHEMA", "fabric_pilot_" + RUN.lower())
    S.init_schema(S.connect(require_schema=False))
    print(json.dumps({"pilot_schema": S.schema()}), flush=True)
    conn = S.connect()
    out = {}
    for name in sys.argv[1:] or ["P1", "P2L", "P3", "P4", "P5", "P8"]:
        if name == "P1": out["P1"] = p1(conn)
        if name == "P2L": out["P2L"] = p2_local(conn)
        if name == "P3": out["P3"] = p3(conn)
        if name == "P4": out["P4"] = p4(conn)
        if name == "P5": out["P5"] = p5(conn)
        if name == "P8":
            tid = (out.get("P4") or {}).get("task") or S.list_tasks(conn, state="completed", limit=1)[0]["task_id"]
            out["P8"] = p8(conn, tid)
