"""Single-pod RunPod orchestrator for ACCEL_CANARY_RUNPOD_v1 (WRITTEN, NOT EXECUTED).

ONE pod, pinned SHA, run the canary, fetch the verdict JSON, ALWAYS terminate.
Hard money ceiling: refuses to start unless the worst-case estimate <= $3.00.

Termination is layered (any one suffices):
  1. try/finally + signal handlers in this controller -> terminate + verify absence;
  2. an INDEPENDENT detached reaper process (independent_reaper.py), armed BEFORE
     create, that terminates the pod (and any pod carrying this run's name
     prefix) at the hard wall-clock deadline even if this controller dies;
  3. a controller-side wall-clock kill: monitoring stops at --max-wall-min;
  4. on-pod `timeout` around the canary (bounds compute, not billing).

Usage (operator, after providing the items listed in runpod/README.md):
    set RUNPOD_API_KEY in the environment (never on argv)
    python orchestrate_runpod_canary.py --commit <pushed SHA> --print-body   # dry run, no calls
    python orchestrate_runpod_canary.py --commit <pushed SHA> --i-accept-cost

Outputs (local): runpod_out/<run_id>/{ACCEL_EQUIVALENCE_runpod-backend_<pod>.json,
canary.log, controller_receipt.json, reaper_evidence.json}.
"""
import argparse
import hashlib
import json
import os
import secrets
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ACCEL = HERE.parent
ENGINE = ACCEL.parent
REPO_REL = "roles/Aphrodite/engine"
sys.path.insert(0, str(HERE))

CEILING_USD = 3.00
SAFETY = 1.25                 # billing-granularity / startup slack multiplier
RAW = "https://raw.githubusercontent.com/jcraig949jfi/Prometheus/%s/%s"

# Files the pod needs, relative to roles/Aphrodite/engine. Checksums are taken
# from `git show <commit>:<path>` so the pod verifies exactly the pinned commit.
POD_FILES = ["engine.py", "basis_v4.py", "run_tier3c.py", "tier3c.py", "conformance.py",
             "meta_tribunal.py", "semantics.py", "improver.py",
             "TIER3C_RESULTS_2026-09-22.json", "TIER3C_ARTIFACT_2026-09-22.json",
             "accel/fasteval.py", "accel/run_canary.py", "accel/runpod/pod_serve.py"]

# ---- pod kinds. Prices are ASSUMPTIONS; the operator must confirm the live quote.
KINDS = {
    # CPU pod via RunPod REST v1 (computeType=CPU). Body UNVERIFIED on this account.
    "cpu": {"dialect": "v1", "hourly_usd": 0.40, "vcpus": 8,
            "image": "python:3.12.10-slim"},
    # Fallback: cheapest community GPU pod through the v2 body shape that WAS
    # smoke-tested 2026-09-22 (the canary only uses its CPUs).
    "gpu-host": {"dialect": "v2", "hourly_usd": 0.20, "gpu_id": "NVIDIA GeForce RTX 3070",
                 "cloud": "COMMUNITY", "image": "python:3.12.10-slim"},
}


def log(msg):
    print("[accel-orch %s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def pinned_files(commit):
    out = []
    for rel in POD_FILES:
        blob = subprocess.run(["git", "show", "%s:%s/%s" % (commit, REPO_REL, rel)],
                              cwd=str(ENGINE), capture_output=True, check=True).stdout
        out.append((rel, hashlib.sha256(blob).hexdigest()))
    return out


def boot_script(commit, files, canary_wall_s, vcpus):
    manifest = json.dumps({rel: sha for rel, sha in files})
    return "\n".join([
        # RunPod injects RUNPOD_API_KEY into every pod: remove it FIRST
        # (AETH-01 RUNPOD_SMOKE_RECEIPT_2026-09-22, lines ~137-180).
        "unset RUNPOD_API_KEY RUNPOD_API_TOKEN RUNPOD_TOKEN",
        "set -e",
        "mkdir -p /app/eng/accel/runpod /app/out /app/scratch",
        "echo '{\"state\":\"booting\"}' > /app/out/status.json",
        "python3 - <<'ACCEL_FETCH_EOF'",
        "import hashlib, json, urllib.request",
        "files = json.loads(%r)" % manifest,
        "for rel, sha in files.items():",
        "    url = %r %% (%r, %r + '/' + rel)" % (RAW, commit, REPO_REL),
        "    req = urllib.request.Request(url, headers={'User-Agent': 'accel-canary/1.0'})",
        "    data = urllib.request.urlopen(req, timeout=60).read()",
        "    if hashlib.sha256(data).hexdigest() != sha:",
        "        raise SystemExit('CHECKSUM MISMATCH ' + rel)",
        "    open('/app/eng/' + rel, 'wb').write(data)",
        "print('fetched+verified', len(files), 'files')",
        "ACCEL_FETCH_EOF",
        "pip install --no-cache-dir --disable-pip-version-check -q 'numpy==2.4.3' || true",
        "cd /app/eng",
        "python3 /app/eng/accel/runpod/pod_serve.py &",
        "set +e",
        "W=$(python3 -c 'import os;print(max(1,min(%d,len(os.sched_getaffinity(0)))))')" % vcpus,
        "echo '{\"state\":\"running\"}' > /app/out/status.json",
        "timeout %d python3 -u /app/eng/accel/run_canary.py --host runpod-${RUNPOD_POD_ID:-pod}"
        " --workers $W --out /app/out --scratch /app/scratch > /app/out/canary.log 2>&1"
        % canary_wall_s,
        "RC=$?",
        "cp /app/out/ACCEL_EQUIVALENCE_runpod-backend_*.json /app/out/ACCEL_EQUIVALENCE.json",
        "echo \"{\\\"state\\\":\\\"done\\\",\\\"rc\\\":$RC}\" > /app/out/status.json",
        "sleep infinity",
    ])


def make_body(kind, name, env, script):
    k = KINDS[kind]
    if k["dialect"] == "v1":
        return {"name": name, "computeType": "CPU", "cpuFlavorIds": ["cpu3c", "cpu5c"],
                "vcpuCount": k["vcpus"], "imageName": k["image"], "containerDiskInGb": 10,
                "cloudType": "SECURE", "ports": ["8080/http"], "env": env,
                "dockerEntrypoint": ["/bin/bash", "-c"], "dockerStartCmd": [script]}
    return {"name": name, "image": k["image"], "gpu": {"id": k["gpu_id"], "count": 1},
            "cloud": k["cloud"], "disk": 10, "ports": ["8080/http"], "env": env,
            "entrypoint": ["/bin/bash", "-c"], "cmd": [script]}


def estimate(hourly, max_wall_min):
    return round(hourly * (max_wall_min / 60.0) * SAFETY + 0.05, 3)   # + disk/egress


class _Stop(Exception):
    pass


def _raise_stop(*_a):
    raise _Stop()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="pushed SHA the pod downloads")
    ap.add_argument("--kind", choices=sorted(KINDS), default="cpu")
    ap.add_argument("--hourly", type=float, default=None, help="live $/hr quote")
    ap.add_argument("--max-wall-min", type=int, default=90)
    ap.add_argument("--print-body", action="store_true", help="dry run: no provider calls")
    ap.add_argument("--i-accept-cost", action="store_true")
    ap.add_argument("--out", default=str(HERE / "runpod_out"))
    a = ap.parse_args()

    k = KINDS[a.kind]
    hourly = a.hourly if a.hourly is not None else k["hourly_usd"]
    est = estimate(hourly, a.max_wall_min)
    log("kind=%s hourly=$%.3f max_wall=%d min worst-case estimate=$%.3f (ceiling $%.2f)"
        % (a.kind, hourly, a.max_wall_min, est, CEILING_USD))
    if est > CEILING_USD:
        log("REFUSE: estimated cost exceeds the $3 ceiling")
        return 3

    files = pinned_files(a.commit)
    canary_wall_s = max(300, a.max_wall_min * 60 - 15 * 60)   # leave 15 min for boot+fetch
    run_id = "accelrp-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + secrets.token_hex(3)
    token = secrets.token_urlsafe(32)
    env = {"ACCEL_ARTIFACT_TOKEN": token, "ACCEL_RUN_ID": run_id, "ACCEL_PINNED_SHA": a.commit}
    body = make_body(a.kind, run_id, env, boot_script(a.commit, files, canary_wall_s,
                                                      k.get("vcpus", 8)))
    if a.print_body:
        shown = json.loads(json.dumps(body))
        shown["env"]["ACCEL_ARTIFACT_TOKEN"] = "<per-run random token>"
        print(json.dumps(shown, indent=2))
        log("DRY RUN: no provider call made")
        return 0
    if not a.i_accept_cost:
        log("REFUSE: pass --i-accept-cost to authorise up to $%.2f" % est)
        return 3
    if not os.environ.get("RUNPOD_API_KEY"):
        log("REFUSE: RUNPOD_API_KEY not set in the environment")
        return 3

    import runpod_api as RA
    api = RA.RunPodAPI(k["dialect"])
    base = api.list_pods()
    if base:
        log("REFUSE: baseline inventory not empty (%d pod(s)); refusing to create" % len(base))
        return 3

    out = Path(a.out) / run_id
    out.mkdir(parents=True, exist_ok=True)
    pid_file = out / "pod_id.txt"
    deadline = time.time() + a.max_wall_min * 60
    reaper = subprocess.Popen(
        [sys.executable, str(HERE / "independent_reaper.py"), "--pod-id-file", str(pid_file),
         "--name-prefix", run_id, "--deadline-epoch", str(deadline + 120),
         "--evidence", str(out / "reaper_evidence.json"), "--dialect", k["dialect"]],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "DETACHED_PROCESS", 0)
        | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        start_new_session=(os.name != "nt"))
    log("independent reaper armed (pid %d), hard deadline in %d min" % (reaper.pid,
                                                                         a.max_wall_min + 2))

    for sig in ("SIGINT", "SIGTERM", "SIGBREAK", "SIGHUP"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), _raise_stop)

    receipt = {"run_id": run_id, "commit": a.commit, "kind": a.kind, "hourly": hourly,
               "estimate_usd": est, "pod_id": None, "verdict": None}
    pod_id, t0 = None, time.time()
    try:
        try:
            pod = api.create_pod(body)
        except RA.ProviderError as e:
            log("create failed (HTTP %s) -> reconciling by inventory, NO blind retry" % e.status)
            pods = [p for p in api.list_pods() if str(p.get("name", "")).startswith(run_id)]
            pod = pods[0] if pods else None
        if pod is None:
            log("no pod exists -> STOP")
            return 4
        pod_id = pod["id"]
        pid_file.write_text(pod_id, encoding="utf-8")
        receipt["pod_id"] = pod_id
        log("pod %s created" % pod_id)
        state = None
        while time.time() < deadline - 60:
            st = RA.fetch_artifact(pod_id, 8080, "status.json", token)
            if st:
                try:
                    state = json.loads(st.decode()).get("state")
                except Exception:          # noqa: BLE001
                    state = None
                if state == "done":
                    break
            time.sleep(20)
        log("pod state at stop of monitoring: %s" % state)
        for name, local in (("ACCEL_EQUIVALENCE.json",
                             "ACCEL_EQUIVALENCE_runpod-backend_%s.json" % pod_id),
                            ("canary.log", "canary.log")):
            data = RA.fetch_artifact(pod_id, 8080, name, token)
            if data:
                (out / local).write_bytes(data)
        eq = out / ("ACCEL_EQUIVALENCE_runpod-backend_%s.json" % pod_id)
        if eq.exists():
            rep = json.loads(eq.read_text(encoding="utf-8"))
            receipt["verdict"] = rep.get("verdict")
            receipt["pinned_sha_on_pod"] = rep.get("pinned_sha_env")
            log("VERDICT %s" % receipt["verdict"])
        else:
            receipt["verdict"] = "NO_RESULT"
            log("no verdict JSON retrieved -> NO_RESULT (not equivalence)")
    except _Stop:
        log("signal received -> terminating")
    finally:
        absent = False
        if pod_id:
            for _ in range(12):
                try:
                    log("terminate %s -> %s" % (pod_id, api.terminate_pod(pod_id)))
                except RA.ProviderError as e:
                    log("terminate error HTTP %s (will verify)" % e.status)
                try:
                    if pod_id not in [p.get("id") for p in api.list_pods()]:
                        absent = True
                        break
                except RA.ProviderError:
                    pass
                time.sleep(10)
        (Path(str(pid_file) + ".done")).write_text("done", encoding="utf-8")
        elapsed = time.time() - t0
        receipt.update({"absent_confirmed": absent, "wall_seconds": round(elapsed, 1),
                        "cost_upper_bound_usd": round(elapsed / 3600 * hourly * SAFETY, 3)})
        (out / "controller_receipt.json").write_text(json.dumps(receipt, indent=2),
                                                     encoding="utf-8")
        log("ABSENCE %s; est cost <= $%.3f; receipt in %s"
            % ("CONFIRMED" if absent else "NOT CONFIRMED -- CHECK CONSOLE NOW",
               receipt["cost_upper_bound_usd"], out))
    return 0 if receipt["verdict"] == "EQUIVALENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
