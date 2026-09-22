"""AETH-01 first-light orchestrator: ONE pod, terminate-guaranteed, budgeted.

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
sys.path.insert(0, _CANARY)
_TMP = tempfile.gettempdir()

UA = "AGE-AETH01-canary/1.0"
ART_DIR = _TMP
POD_ID_FILE = os.path.join(_TMP, "aeth01_firstlight_pod_id.txt")
REPORT = os.path.join(_TMP, "aeth01_firstlight_report.txt")

CANARY_DEADLINE_S = 900
POLL_S = 60
HOURLY = float(os.environ.get("AETH01_HOURLY", "0.49"))
DOLLAR_CEILING = float(os.environ.get("AETH01_FL_CEILING", "2.60"))
GPU_ID = os.environ.get("AETH01_GPU_ID", "NVIDIA A40")
CLOUD = os.environ.get("AETH01_CLOUD", "SECURE")
DISK_GB = int(os.environ.get("AETH01_DISK_GB", "20"))
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
COMMIT = os.environ["AETH01_COMMIT"]
RAW = ("https://raw.githubusercontent.com/jcraig949jfi/Prometheus/%s/"
       "Aether/runpod/aeth01_canary/%s")
_PINNED = ("aeth01_cpu_oracle.py", "aeth01_gpu_kernel.py", "run_canary.py",
           "pod_service.py")

SIZE = int(os.environ.get("AETH01_FL_SIZE", "4096"))
TICKS = int(os.environ.get("AETH01_FL_TICKS", "5000"))
POD_BUDGET_S = float(os.environ.get("AETH01_FL_BUDGET_S", "16200"))

P32 = 1 << 32


def prob(p):
    return int(round(p * P32))


# Three ECONOMICS.md resource regimes x two independent seeds, all at
# EXPERIMENTS.md regime 2 (sparse soup) 50% and perturbation 0.1, chosen
# from SCOUT_FINDINGS_2026-09-22.md. Ordered so that if the ceiling
# truncates the run, the worlds already finished are the informative
# ones: each regime appears once before any regime repeats.
_REGIMES = [
    ("C_free_compute", dict(write_cost=0, maintenance_cost=0,
                            replenish_numer=0, replenish_amount=0)),
    ("B_balanced", dict(write_cost=1, maintenance_cost=1,
                        replenish_numer=prob(0.125), replenish_amount=8)),
    ("A_execution_only", dict(write_cost=1, maintenance_cost=0,
                              replenish_numer=0, replenish_amount=0)),
]
_SEEDS = [(0xA37E01, 0x5C011701), (0xA37E02, 0x5C011702)]


def build_worlds():
    worlds = []
    for slot, (rng_seed, physics_seed) in enumerate(_SEEDS):
        for name, params in _REGIMES:
            p = dict(params)
            p.update(seed=physics_seed, mut_numer=prob(0.1))
            worlds.append({
                "name": "%s|seed%d" % (name, slot),
                "init_regime": "sparse_soup",
                "write_density": 0.50,
                "energy_mode": "uniform",
                "rng_seed": rng_seed,
                "params": p,
            })
    return worlds


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
    ("/app/aeth01_firstlight.py", _read(os.path.join(_HERE, "aeth01_firstlight.py"))),
    ("/app/aeth01_bench_server.py",
     _read(os.path.join(_CANARY, "aeth01_bench_server.py"))),
]

GATE = r'''set +e
touch /app/bench.log
for i in $(seq 1 180); do
  if curl -fsS -H "Authorization: Bearer $AGE_ARTIFACT_TOKEN" http://127.0.0.1:8080/result.json -o /app/result.json 2>/dev/null; then break; fi
  sleep 5
done
curl -fsS -H "Authorization: Bearer $AGE_ARTIFACT_TOKEN" http://127.0.0.1:8080/receipt.json -o /app/receipt.json 2>/dev/null
STATUS=$(python3 -c "import json;print(json.load(open('/app/receipt.json')).get('status'))" 2>/dev/null || echo NONE)
echo "AETH01_FL_GATE canary status=$STATUS" >> /app/bench.log
if [ "$STATUS" = "PASS" ]; then
  AETH01_SRC=/app python3 -u /app/aeth01_firstlight.py >> /app/firstlight.stdout 2>&1
  echo "AETH01_FL_RUNNER_EXIT rc=$?" >> /app/bench.log
else
  echo "AETH01_FL_SKIPPED reason=canary_not_pass status=$STATUS" >> /app/bench.log
fi
python3 /app/aeth01_bench_server.py'''


def log(msg):
    print("[fl %s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


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
        "name": "aeth01-fl-" + run_id[-8:],
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
            "AETH01_FL_SIZE": str(SIZE),
            "AETH01_FL_TICKS": str(TICKS),
            "AETH01_FL_BUDGET_S": str(POD_BUDGET_S),
            "AETH01_FL_WORLDS": json.dumps(worlds),
        },
        "entrypoint": ["/bin/bash", "-c"],
        "cmd": [build_script(worlds)],
    }


def _save(name, data):
    path = os.path.join(ART_DIR, "aeth01_fl_" + name)
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
            worlds_done = fetched.count('"kind": "world_end"')
            samples = fetched.count('"kind": "sample"')
            log("log %d bytes, %d world_end, %d samples, $%.3f spent"
                % (len(fetched), worlds_done, samples, spend))
            if "AETH01_FL_COMPLETE" in fetched or "AETH01_FL_SKIPPED" in fetched:
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
    run_id = ("aeth01fl-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
              + "-" + secrets.token_hex(4))
    os.environ["AGE_ARTIFACT_TOKEN"] = secrets.token_urlsafe(32)
    worlds = build_worlds()
    log("RUN_ID=%s  %d worlds, %d^2, %d ticks, ceiling $%.2f"
        % (run_id, len(worlds), SIZE, TICKS, DOLLAR_CEILING))
    log("pinned commit %s" % COMMIT)
    for name, digest in FILES:
        log("  downloaded %-24s %s" % (name, digest[:16]))
    import hashlib as _h
    for path, body in SHIPPED:
        log("  shipped    %-24s %s" % (os.path.basename(path),
            _h.sha256((body + "
").encode("utf-8")).hexdigest()[:16]))
    for w in worlds:
        log("  world %-24s %s" % (w["name"], w["params"]))

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
            _save("firstlight.log", text)
        summary = ("run_id=%s canary=%s stop=%s pod_wall_s=%.0f est_cost=$%.3f\n"
                   % (run_id, "PASS" if canary_ok else "FAIL", why, elapsed,
                      elapsed / 3600.0 * HOURLY))
        with open(REPORT, "w") as f:
            f.write(summary)
        print(summary, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
