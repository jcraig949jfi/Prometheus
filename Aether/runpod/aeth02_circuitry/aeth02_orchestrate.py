"""AETH-02 circuitry orchestrator: ONE pod, terminate-guaranteed, budgeted.

Generated from aeth01_firstlight_orchestrate.py so its safety properties
carry over unchanged: refuse to create unless the inventory is empty,
exactly one pod, gate the science on a real-GPU canary PASS, a
controller-side DOLLAR CEILING, a pod-side wall clock, the artifact
server up BEFORE the science, and terminate in a finally with absence
verified. Differences: it ships the graph observatory and runs
aeth02_runner.py, whose phase list comes from the environment.

Same shape and same safety properties as aeth01_scale_orchestrate.py --
refuse to create if the inventory is not empty, create exactly one pod,
never retry in a way that can create a second, gate the science on a
real-GPU canary PASS, and terminate in a `finally` and verify absence --
with two differences this run needs:

  1. it runs the first-light worlds instead of the scaling benchmark;
  2. it enforces a DOLLAR CEILING itself. The run is hours rather than
     minutes, so "the controller will terminate when it finishes" is not
     a sufficient cost bound. The controller terminates when the
     estimated spend reaches the ceiling, whatever the pod is doing, and
     the pod-side runner carries its own independent wall-clock budget
     so a controller that dies cannot leave the pod working forever.

Secrets are never printed or placed on argv.
"""

import json
import os
import re
import secrets
import sys
import tempfile
import time
from urllib.request import Request, build_opener, ProxyHandler

_HERE = os.path.dirname(os.path.abspath(__file__))
_CANARY = os.path.join(os.path.dirname(_HERE), "aeth01_canary")
_OBSERVATORY = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "observatory")
_PHASES_ENV = "AETH02_PHASES"
sys.path.insert(0, _CANARY)
_TMP = tempfile.gettempdir()

UA = "AGE-AETH01-canary/1.0"
ART_DIR = _TMP
POD_ID_FILE = os.path.join(_TMP, "aeth02_pod_id.txt")
REPORT = os.path.join(_TMP, "aeth02_report.txt")

CANARY_DEADLINE_S = 900
POLL_S = 60
HOURLY = float(os.environ.get("AETH01_HOURLY", "0.49"))
DOLLAR_CEILING = float(os.environ.get("AETH02_CEILING", "0.60"))
GPU_ID = os.environ.get("AETH01_GPU_ID", "NVIDIA A40")
CLOUD = os.environ.get("AETH01_CLOUD", "SECURE")
DISK_GB = int(os.environ.get("AETH01_DISK_GB", "20"))
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
COMMIT = os.environ["AETH01_COMMIT"]
RAW = ("https://raw.githubusercontent.com/jcraig949jfi/Prometheus/%s/"
       "Aether/runpod/aeth01_canary/%s")
_PINNED = ("aeth01_cpu_oracle.py", "aeth01_gpu_kernel.py", "run_canary.py",
           "pod_service.py")

POD_BUDGET_S = float(os.environ.get("AETH02_BUDGET_S", "2400"))
PLAN = os.environ.get("AETH02_PLAN", "calibration")

P32 = 1 << 32


def prob(p):
    return int(round(p * P32))


# B_balanced exactly as First Light ran it, so the trajectory is directly
# comparable (the directive asks to continue the existing conditions
# rather than invent new ones). B_balanced is the only regime First Light
# left unresolved: still changing at tick 5,000.
B_BALANCED = dict(write_cost=1, maintenance_cost=1,
                  replenish_numer=int(round(0.125 * (1 << 32))),
                  replenish_amount=8)
B_SEED0 = 0x5C011701      # First Light B_balanced|seed0's physics seed
B_RNG0 = 0xA37E01         # and its initialization seed


def _phase(name, size, ticks, rng_seed=B_RNG0, seed=B_SEED0):
    params = dict(B_BALANCED)
    params.update(seed=seed, mut_numer=int(round(0.1 * (1 << 32))))
    return {"name": name, "size": size, "ticks": ticks,
            "init_regime": "sparse_soup", "write_density": 0.50,
            "energy_mode": "uniform", "rng_seed": rng_seed,
            "params": params}


# CALIBRATION: learn the cost curve and take an early read on whether any
# cycles exist at all, for well under a dollar, before committing to the
# long trajectory. Sizes ascend so a truncation still yields the cheap
# points.
CALIBRATION = [
    _phase("econ_1024", 1024, 300),
    _phase("econ_2048", 2048, 300),
    _phase("econ_4096", 4096, 300),
    _phase("probe_4096", 4096, 2000),
]

# TRAJECTORY: Track 1 as the operator resolved it after the calibration
# measured 4096^2 x 50,000 at $3.24, over the cap. Three INDEPENDENT
# 2048^2 worlds at the full 50,000 ticks: the requested temporal horizon
# is preserved, replication is gained, and the measured cost is
# 3 x 50,000 x 0.1221 s = 18,315 s = 5.09 h = $2.49.
#
# Distinct seeds for both the initialization RNG and the physics seed.
# Seeds 0 and 1 are First Light's own B_balanced seeds, so two of the
# three trajectories extend worlds whose first 5,000 ticks are already
# recorded; the third is new.
_TRAJ_SEEDS = [(0xA37E01, 0x5C011701),
               (0xA37E02, 0x5C011702),
               (0xA37E03, 0x5C011703)]

TRAJECTORY = [
    _phase("B_long_seed%d" % i, 2048, 50000, rng_seed=rng, seed=phys)
    for i, (rng, phys) in enumerate(_TRAJ_SEEDS)
]

PLANS = {"calibration": CALIBRATION, "trajectory": TRAJECTORY}


def build_worlds():
    return PLANS[PLAN]


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().rstrip("\n")


def _sha256_of(path):
    import hashlib
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


FILES = [(n, _sha256_of(os.path.join(_CANARY, n))) for n in _PINNED]
SHIPPED = [
    ("/app/observatory/__init__.py", _read(os.path.join(_OBSERVATORY, "__init__.py"))),
    ("/app/observatory/aeth01_observatory.py",
     _read(os.path.join(_OBSERVATORY, "aeth01_observatory.py"))),
    ("/app/observatory/aeth01_run.py",
     _read(os.path.join(_OBSERVATORY, "aeth01_run.py"))),
    ("/app/observatory/aeth01_graph.py",
     _read(os.path.join(_OBSERVATORY, "aeth01_graph.py"))),
    ("/app/aeth02_runner.py", _read(os.path.join(_HERE, "aeth02_runner.py"))),
    ("/app/aeth01_bench_server.py",
     _read(os.path.join(_CANARY, "aeth01_bench_server.py"))),
]

GATE = r'''set +e
touch /app/bench.log
# The artifact server comes up BEFORE the science, not after it. The
# first-light run is hours long, so a server started afterwards would
# mean no progress visibility for its whole duration, and -- worse --
# terminating a pod mid-run would destroy every sample it had taken,
# because nothing could be fetched until the runner exited. With the
# server first, the log is retrievable at any moment and a truncated run
# still yields all the samples it managed to take.
python3 /app/aeth01_bench_server.py &
SERVER_PID=$!
echo "AETH02_SERVER_UP pid=$SERVER_PID" >> /app/bench.log
for i in $(seq 1 180); do
  if curl -fsS -H "Authorization: Bearer $AGE_ARTIFACT_TOKEN" http://127.0.0.1:8080/result.json -o /app/result.json 2>/dev/null; then break; fi
  sleep 5
done
curl -fsS -H "Authorization: Bearer $AGE_ARTIFACT_TOKEN" http://127.0.0.1:8080/receipt.json -o /app/receipt.json 2>/dev/null
STATUS=$(python3 -c "import json;print(json.load(open('/app/receipt.json')).get('status'))" 2>/dev/null || echo NONE)
echo "AETH02_GATE canary status=$STATUS" >> /app/bench.log
if [ "$STATUS" = "PASS" ]; then
  AETH01_SRC=/app python3 -u /app/aeth02_runner.py >> /app/aeth02.stdout 2>&1
  echo "AETH02_RUNNER_EXIT rc=$?" >> /app/bench.log
else
  echo "AETH02_SKIPPED reason=canary_not_pass status=$STATUS" >> /app/bench.log
fi
wait $SERVER_PID'''


def log(msg):
    print("[a2 %s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def load_key():
    with open(r"C:\runpod_key\keys.txt", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if re.fullmatch(r"rpa_[A-Za-z0-9]+", s):
                return s
    raise SystemExit("no rpa_ key found")


def build_script(worlds):
    L = ["set -e", "mkdir -p /app/observatory", "cd /app"]
    for name, _h in FILES:
        L.append("curl -fsSL '%s' -o '%s'" % (RAW % (COMMIT, name), name))
    L.append("cat > checksums.txt <<'CHKEOF'")
    for name, h in FILES:
        L.append("%s  %s" % (h, name))
    L.append("CHKEOF")
    L.append("sha256sum -c checksums.txt")
    for i, (path, body) in enumerate(SHIPPED):
        tag = "AETH01_SHIP_%d_EOF" % i
        L.append("cat > %s <<'%s'" % (path, tag))
        L.append(body)
        L.append(tag)
    L.append("pip install --no-cache-dir 'numpy==2.2.0' 'cupy-cuda12x==13.3.0'")
    L.append("unset RUNPOD_API_KEY RUNPOD_API_TOKEN RUNPOD_TOKEN")
    L.append("python3 pod_service.py &")
    L.append(GATE)
    return "\n".join(L)


def make_body(run_id, worlds):
    return {
        "name": "aeth02-" + run_id[-8:],
        "image": IMAGE,
        "gpu": {"id": GPU_ID, "count": 1},
        "cloud": CLOUD,
        "disk": DISK_GB,
        "ports": ["8080/http", "8081/http"],
        "env": {
            "AGE_ARTIFACT_TOKEN": os.environ["AGE_ARTIFACT_TOKEN"],
            "AETH01_RUN_ID": run_id,
            "AETH01_CANARY_TIMEOUT_SECONDS": "600",
            "AETH01_CANARY_HOURLY_RATE": str(HOURLY),
            "AETH01_CANARY_MAX_DOLLAR_BUDGET": "3",
            "AETH02_BUDGET_S": str(POD_BUDGET_S),
            "AETH02_HOURLY": str(HOURLY),
            "AETH02_PHASES": json.dumps(worlds),
        },
        "entrypoint": ["/bin/bash", "-c"],
        "cmd": [build_script(worlds)],
    }


def _save(name, data):
    path = os.path.join(ART_DIR, "aeth02_" + name)
    mode = "wb" if isinstance(data, (bytes, bytearray)) else "w"
    with open(path, mode) as f:
        f.write(data)
    return path


def _validate(result_obj, receipt_obj, run_id):
    reasons = []
    if not (isinstance(result_obj, dict) and result_obj.get("finished") is True
            and result_obj.get("exit_code") == 0
            and result_obj.get("run_id") == run_id):
        reasons.append("result.json not a finished exit_code=0 run-bound record")
    r = receipt_obj if isinstance(receipt_obj, dict) else {}
    if r.get("status") != "PASS":
        reasons.append("receipt.status=%r != PASS" % r.get("status"))
    if r.get("run_id") != run_id:
        reasons.append("receipt.run_id mismatch")
    if r.get("backend") != "cupy":
        reasons.append("receipt.backend=%r != cupy (no real GPU)" % r.get("backend"))
    if (r.get("cases_expected"), r.get("cases_run"), r.get("cases_matched")) != (300, 300, 300):
        reasons.append("cases not 300/300/300")
    if r.get("mismatches"):
        reasons.append("%d mismatch(es)" % len(r.get("mismatches")))
    return (not reasons), reasons


def monitor_canary(api, pod_id, run_id):
    import runpod_api
    art = runpod_api.ArtifactClient()
    deadline = time.monotonic() + CANARY_DEADLINE_S
    while time.monotonic() < deadline:
        try:
            result = art.fetch(pod_id, "result.json")
        except runpod_api.ProviderError:
            result = None
        if result:
            _save("result.json", result)
            receipt = None
            try:
                receipt = art.fetch(pod_id, "receipt.json")
            except runpod_api.ProviderError:
                pass
            if receipt:
                _save("receipt.json", receipt)
            robj = json.loads(result.decode("utf-8", "replace"))
            recobj = json.loads(receipt.decode("utf-8", "replace")) if receipt else None
            ok, reasons = _validate(robj, recobj, run_id)
            log("CANARY %s%s" % ("PASS" if ok else "FAIL: ", "; ".join(reasons)))
            if recobj:
                log("receipt: backend=%s cases=%s/%s gpu_s=%s"
                    % (recobj.get("backend"), recobj.get("cases_matched"),
                       recobj.get("cases_expected"), recobj.get("gpu_kernel_seconds")))
            return ok, recobj
        time.sleep(15)
    log("CANARY TIMEOUT, no result.json")
    return False, None


def fetch_log(pod_id):
    url = "https://%s-8081.proxy.runpod.net/bench.log" % pod_id
    opener = build_opener(ProxyHandler({}))
    req = Request(url, method="GET",
                  headers={"Accept": "text/plain", "User-Agent": UA})
    req.add_unredirected_header("Authorization",
                                "Bearer " + os.environ["AGE_ARTIFACT_TOKEN"])
    try:
        with opener.open(req, timeout=60) as r:
            if r.getcode() == 200:
                return r.read().decode("utf-8", "replace")
    except Exception:
        return None
    return None


def monitor_run(pod_id, t0):
    """Poll until the runner finishes or the DOLLAR CEILING is reached."""
    text = None
    while True:
        elapsed = time.time() - t0
        spend = elapsed / 3600.0 * HOURLY
        if spend >= DOLLAR_CEILING:
            log("DOLLAR CEILING reached: $%.3f >= $%.2f after %.0fs -> stopping"
                % (spend, DOLLAR_CEILING, elapsed))
            text = fetch_log(pod_id) or text
            return text, "ceiling"
        fetched = fetch_log(pod_id)
        if fetched is not None:
            text = fetched
            worlds_done = fetched.count('"kind": "phase_end"')
            samples = fetched.count('"kind": "sample"')
            log("log %d bytes, %d phase_end, %d samples, $%.3f spent"
                % (len(fetched), worlds_done, samples, spend))
            if "AETH02_COMPLETE" in fetched or "AETH02_SKIPPED" in fetched:
                return text, "complete"
        else:
            log("log not reachable yet ($%.3f spent)" % spend)
        time.sleep(POLL_S)


def terminate_and_verify(api, pod_id):
    import runpod_api
    log("terminating %s" % pod_id)
    try:
        log("terminate outcome: %s" % api.terminate_pod(pod_id))
    except runpod_api.ProviderError as e:
        log("terminate ProviderError status=%s (verifying anyway)" % e.status)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            pods = api.list_pods()
        except runpod_api.ProviderError:
            time.sleep(10)
            continue
        if pod_id not in [p.get("id") for p in pods]:
            log("ABSENCE CONFIRMED (ACTIVE_POD_COUNT %d)" % len(pods))
            return True
        time.sleep(10)
    log("WARNING: absence NOT confirmed in 180s")
    return False


def main():
    os.environ["RUNPOD_API_KEY"] = load_key()
    run_id = ("aeth02-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
              + "-" + secrets.token_hex(4))
    os.environ["AGE_ARTIFACT_TOKEN"] = secrets.token_urlsafe(32)
    worlds = build_worlds()
    log("RUN_ID=%s  plan=%s  %d phases, ceiling $%.2f, pod budget %.0fs"
        % (run_id, PLAN, len(worlds), DOLLAR_CEILING, POD_BUDGET_S))
    log("pinned commit %s" % COMMIT)
    for name, digest in FILES:
        log("  downloaded %-24s %s" % (name, digest[:16]))
    import hashlib as _h
    for path, body in SHIPPED:
        digest = _h.sha256(body.encode("utf-8")).hexdigest()
        log("  shipped    %-24s %s" % (os.path.basename(path), digest[:16]))
    for w in worlds:
        log("  phase %-18s %5d^2 x %6d ticks" % (w["name"], w["size"], w["ticks"]))

    import runpod_api
    api = runpod_api.RunPodAPI()
    baseline = api.list_pods()
    if baseline:
        log("ABORT: baseline not empty (%d pods)" % len(baseline))
        return 3
    log("baseline confirmed empty (0 pods)")

    pod = api.create_pod(make_body(run_id, worlds))
    pod_id = pod["id"]
    with open(POD_ID_FILE, "w") as f:
        f.write(pod_id)
    log("pod %s created (id persisted to %s)" % (pod_id, POD_ID_FILE))

    t0 = time.time()
    text, why = None, "not_started"
    canary_ok = False
    try:
        canary_ok, _receipt = monitor_canary(api, pod_id, run_id)
        if canary_ok:
            text, why = monitor_run(pod_id, t0)
        else:
            why = "canary_fail"
            text = fetch_log(pod_id)
    finally:
        terminate_and_verify(api, pod_id)
        elapsed = time.time() - t0
        if text:
            _save("circuitry.log", text)
        summary = ("run_id=%s canary=%s stop=%s pod_wall_s=%.0f est_cost=$%.3f\n"
                   % (run_id, "PASS" if canary_ok else "FAIL", why, elapsed,
                      elapsed / 3600.0 * HOURLY))
        with open(REPORT, "w") as f:
            f.write(summary)
        print(summary, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
