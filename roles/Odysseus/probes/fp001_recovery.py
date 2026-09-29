"""FP-001 (MWO-0003 s5): Odysseus's disposable Fabric RECOVERY probe. Synthetic data only; no Fabric change.

Runs on the LIVE fabric store with the FROZEN node runtime (~/fabric-runtime, fabric-v0.2):
  1. submit one synthetic Task that needs a probe-only capability (so no fleet worker can claim it) and one lease;
  2. worker P1 claims it (Attempt 1, lease acquired); P1 is SIGKILLed mid-run: the intentional failure;
  3. worker P2 starts; its loop reaps Attempt 1 (abandoned, lease released, Task requeued), then claims Attempt 2;
  4. checks that the Task, the Attempts, the leases and the artifacts converge:
     - Task completed; Attempts = [abandoned, succeeded]; exactly one live Attempt at any time;
     - one lease per Attempt, both released, none unreleased on the resource;
     - artifacts only from Attempt 2 (the killed Attempt deposits nothing).

    EW_DB_HOST=192.168.1.202 python3 roles/Odysseus/probes/fp001_recovery.py
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from fabric import store as S  # noqa: E402

RUNTIME = Path(os.path.expanduser("~/fabric-runtime"))
CAP = "probe.fp001"
RES = "ubu001:fp001-probe"
TTL = 20


def worker(agent):
    return subprocess.Popen([sys.executable, "-m", "fabric", "worker", "--agent", agent, "--caps", CAP, "--executors",
                             "synthetic", "--ttl-s", str(TTL), "--poll-s", "1", "--idle-exit-s", "90", "--max-tasks", "1"],
                            cwd=str(RUNTIME), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def main():
    c = S.connect()
    t0 = time.time()
    base = subprocess.run(["git", "-C", str(RUNTIME), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    run = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    tid = S.submit(c, "Odysseus", "FP-001 recovery probe (synthetic)", "synthetic", required_caps=[CAP], resources=[RES],
                   params={"seconds": 25, "text": "fp001 successor output", "file": "fp001.txt"}, max_attempts=3,
                   idempotency_key="fp001-recovery-" + run, title="FP-001 Fabric recovery probe (MWO-0003 s5)",
                   thread_id="thr-fp-001")["task_id"]
    p1 = worker("worker.ubu001.probe1")
    att1 = None
    for _ in range(60):
        t = S.get_task(c, tid)
        if t["attempts"] and t["attempts"][-1]["status"] == "running":
            att1 = t["attempts"][-1]["attempt_id"]; break
        time.sleep(0.5)
    lease_during = [l for l in S.leases(c) if l["resource"] == RES]
    time.sleep(3)
    os.killpg(p1.pid, signal.SIGKILL); p1.wait()               # the intentional failure of Attempt 1
    killed_at = time.time()
    time.sleep(TTL + 3)                                       # let Attempt 1's heartbeat expire
    p2 = worker("worker.ubu001.probe2")
    deadline = time.time() + 180
    while time.time() < deadline and S.get_task(c, tid)["state"] not in S.TERMINAL:
        time.sleep(1)
    try:
        p2.wait(timeout=120)
    except subprocess.TimeoutExpired:
        p2.kill()
    t = S.get_task(c, tid)
    atts = [(a["attempt_id"], a["agent"], a["status"]) for a in t["attempts"]]
    cur = c.cursor()
    cur.execute("SELECT lease_id, attempt_id, released_at IS NOT NULL, release_reason FROM {}.leases WHERE resource = %s"
                " AND attempt_id = ANY(%s) ORDER BY acquired_at".format(S.schema()), (RES, [a[0] for a in atts]))
    leases = [list(r) for r in cur.fetchall()]; c.commit()
    unreleased = [l for l in S.leases(c) if l["resource"] == RES]
    arts = [(x["name"], x["attempt_id"], x["sha256"]) for x in t["artifacts"]]
    ev = [e["kind"] for e in S.events(c, tid)]
    att2 = atts[-1][0] if len(atts) >= 2 else None
    checks = {
        "task_completed": t["state"] == "completed",
        "attempts_abandoned_then_succeeded": [a[2] for a in atts] == ["abandoned", "succeeded"],
        "first_attempt_is_the_killed_one": bool(atts) and atts[0][0] == att1,
        "lease_held_during_attempt1": any(l["attempt_id"] == att1 for l in lease_during),
        "one_lease_per_attempt": sorted(l[1] for l in leases) == sorted(a[0] for a in atts),
        "all_leases_released": bool(leases) and all(l[2] for l in leases),
        "no_unreleased_lease_on_resource": unreleased == [],
        "no_artifacts_from_killed_attempt": all(a[1] != att1 for a in arts),
        "successor_artifacts_present": any(a[1] == att2 and a[0] == "fp001.txt" for a in arts),
        "reap_events_present": "abandoned" in ev or "attempt_abandoned" in ev,
    }
    out = {"probe": "roles/Odysseus/probes/fp001_recovery.py", "runtime_head": base, "task": tid, "attempts": atts,
           "leases": leases, "artifacts": arts, "events": ev, "checks": checks, "pass": all(checks.values()),
           "seconds_kill_to_completion": round(time.time() - killed_at, 1) if t["state"] == "completed" else None,
           "wall_seconds": round(time.time() - t0, 1)}
    print(json.dumps(out, indent=1, default=str))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
