"""Independent cleanup-only reaper for the accel-runpod canary pod.

Launched by the orchestrator as a SEPARATE detached process BEFORE the pod is
created, so it survives a crash/kill of the orchestrator. It can only list, get
and terminate -- it has no create path. It:

  1. waits for the pod-id file the orchestrator writes right after create;
  2. at the hard deadline (epoch seconds), terminates that pod AND any pod whose
     name starts with the run's name prefix (covers an ambiguous create whose
     id was never recorded);
  3. verifies absence from the inventory, re-terminating until absent or until
     --verify-seconds elapse; writes a small evidence JSON.

It also exits early (after a final sweep) if the orchestrator writes the
`<pod-id-file>.done` marker AND the pod is already absent.

    python independent_reaper.py --pod-id-file F --name-prefix P --deadline-epoch T
                                 --evidence E [--dialect v1]

Credential: RUNPOD_API_KEY from the environment only (never argv, never logged).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runpod_api as RA  # noqa: E402


def _ours(pod, pid, prefix):
    return pod.get("id") == pid or str(pod.get("name", "")).startswith(prefix)


def sweep(api, pid, prefix, log):
    try:
        pods = api.list_pods()
    except RA.ProviderError as e:
        log.append({"t": time.time(), "event": "list_error", "status": e.status})
        return None
    mine = [p for p in pods if isinstance(p, dict) and _ours(p, pid, prefix)]
    for p in mine:
        try:
            out = api.terminate_pod(p["id"])
        except RA.ProviderError as e:
            out = "ERR_%s" % e.status
        log.append({"t": time.time(), "event": "terminate", "pod": p["id"], "outcome": out})
    return len(mine)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pod-id-file", required=True)
    ap.add_argument("--name-prefix", required=True)
    ap.add_argument("--deadline-epoch", type=float, required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--dialect", default="v1")
    ap.add_argument("--verify-seconds", type=int, default=600)
    a = ap.parse_args()
    api = RA.RunPodAPI(a.dialect)
    log = [{"t": time.time(), "event": "armed", "deadline": a.deadline_epoch}]
    done_marker = a.pod_id_file + ".done"
    pid = None
    while time.time() < a.deadline_epoch:
        if pid is None and os.path.exists(a.pod_id_file):
            pid = open(a.pod_id_file, encoding="utf-8").read().strip() or None
        if os.path.exists(done_marker):
            log.append({"t": time.time(), "event": "controller_done_marker"})
            break
        time.sleep(20)
    if pid is None and os.path.exists(a.pod_id_file):
        pid = open(a.pod_id_file, encoding="utf-8").read().strip() or None
    log.append({"t": time.time(), "event": "reaping", "pod": pid})
    end = time.time() + a.verify_seconds
    absent = False
    while time.time() < end:
        n = sweep(api, pid, a.name_prefix, log)
        if n == 0:
            absent = True
            break
        time.sleep(15)
    log.append({"t": time.time(), "event": "final", "absent_confirmed": absent})
    with open(a.evidence, "w", encoding="utf-8") as f:
        json.dump({"pod": pid, "name_prefix": a.name_prefix, "absent_confirmed": absent,
                   "events": log}, f, indent=2)
    return 0 if absent else 1


if __name__ == "__main__":
    raise SystemExit(main())
