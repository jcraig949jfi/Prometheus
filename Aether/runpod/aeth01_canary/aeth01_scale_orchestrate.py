"""AETH-01 bounded scaling orchestrator (ONE pod, terminate-guaranteed, <=$3).

Creates exactly one A40 (SECURE) pod. Boot cmd: download+checksum the 4 FROZEN
files, write the (non-frozen) bench harness + bearer-authed bench server via
quoted heredocs, pip install, then `unset RUNPOD_API_KEY RUNPOD_API_TOKEN
RUNPOD_TOKEN` IMMEDIATELY before `python3 pod_service.py &` (pod_service itself
is NOT modified). On-pod the boot script gates the scaling benchmark on a canary
status==PASS (polled from localhost:8080 with AGE_ARTIFACT_TOKEN); bench output
goes to /app/bench.log, served on 8081. This controller validates the canary
receipt over the 8080 proxy, retrieves bench.log over the 8081 proxy, then
ALWAYS terminates and verifies absence. Secrets never printed or placed on argv.
"""

import hashlib
import json
import os
import re
import secrets
import sys
import tempfile
import time
from urllib.request import Request, build_opener, ProxyHandler

# Self-contained: resolve the frozen canary sources from this script's own
# directory, so the orchestrator runs from a checkout with no absolute paths.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_TMP = tempfile.gettempdir()

UA = "AGE-AETH01-canary/1.0"
POD_ID_FILE = os.path.join(_TMP, "aeth01_scale_pod_id.txt")
ART_DIR = _TMP
REPORT = os.path.join(_TMP, "aeth01_scale_report.txt")
CANARY_DEADLINE_S = 900       # up to 15 min to obtain result.json
BENCH_DEADLINE_S = 1900       # up to ~32 min for the benchmark to finish
POLL_S = 15
HOURLY = float(os.environ.get("AETH01_HOURLY", "0.49"))  # A40 SECURE quote
GPU_ID = os.environ.get("AETH01_GPU_ID", "NVIDIA A40")
CLOUD = os.environ.get("AETH01_CLOUD", "SECURE")
DISK_GB = int(os.environ.get("AETH01_DISK_GB", "20"))
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
# The GitHub commit the pod downloads the 4 pinned files from. Override with
# AETH01_COMMIT after pushing an updated kernel (e.g. the memory-optimized one).
COMMIT = os.environ.get("AETH01_COMMIT", "ec63af505b4f1af0af3b0d54317a1ac29e9e975e")
RAW = ("https://raw.githubusercontent.com/jcraig949jfi/Prometheus/%s/"
       "Aether/runpod/aeth01_canary/%s")
_PINNED = ("aeth01_cpu_oracle.py", "aeth01_gpu_kernel.py", "run_canary.py", "pod_service.py")


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().rstrip("\n")


def _sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# Checksums are computed from the local sibling copies at run time, so the pod's
# downloaded files are verified against exactly the revision in this checkout
# (which must match the pushed AETH01_COMMIT).
FILES = [(name, _sha256_of(os.path.join(_HERE, name))) for name in _PINNED]

BENCH_SRC = _read(os.path.join(_HERE, "aeth01_bench.py"))
SERVER_SRC = _read(os.path.join(_HERE, "aeth01_bench_server.py"))

# Bash run on-pod AFTER pod_service is backgrounded: gate bench on canary PASS,
# then serve bench.log on 8081 (foreground) to keep the container alive.
GATE = r'''set +e
touch /app/bench.log
echo "AETH01_GATE waiting for canary result.json ..." >> /app/bench.log
for i in $(seq 1 180); do
  if curl -fsS -H "Authorization: Bearer $AGE_ARTIFACT_TOKEN" http://127.0.0.1:8080/result.json -o /app/result.json 2>/dev/null; then break; fi
  sleep 5
done
curl -fsS -H "Authorization: Bearer $AGE_ARTIFACT_TOKEN" http://127.0.0.1:8080/receipt.json -o /app/receipt.json 2>/dev/null
STATUS=$(python3 -c "import json;print(json.load(open('/app/receipt.json')).get('status'))" 2>/dev/null || echo NONE)
BACKEND=$(python3 -c "import json;print(json.load(open('/app/receipt.json')).get('backend'))" 2>/dev/null || echo NONE)
echo "AETH01_GATE canary status=$STATUS backend=$BACKEND" >> /app/bench.log
if [ "$STATUS" = "PASS" ]; then
  echo "AETH01_GATE canary PASS -> running scaling benchmark" >> /app/bench.log
  AETH01_SRC=/app AETH01_BENCH_WALL_S=1500 AETH01_PARITY_MAX=128 python3 -u /app/aeth01_bench.py >> /app/bench.log 2>&1
  echo "AETH01_BENCH_COMPLETE rc=$?" >> /app/bench.log
else
  echo "AETH01_BENCH_SKIPPED reason=canary_not_pass status=$STATUS" >> /app/bench.log
fi
python3 /app/aeth01_bench_server.py'''


def log(msg):
    print("[orch %s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def load_key():
    with open(r"C:\runpod_key\keys.txt", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if re.fullmatch(r"rpa_[A-Za-z0-9]+", s):
                return s
    raise SystemExit("no rpa_ key found")


def build_script():
    L = ["set -e", "mkdir -p /app", "cd /app"]
    for name, _h in FILES:
        L.append("curl -fsSL '%s' -o '%s'" % (RAW % (COMMIT, name), name))
    L.append("cat > checksums.txt <<'CHKEOF'")
    for name, h in FILES:
        L.append("%s  %s" % (h, name))
    L.append("CHKEOF")
    L.append("sha256sum -c checksums.txt")
    L.append("cat > aeth01_bench.py <<'AETH01_BENCH_PY_EOF'")
    L.append(BENCH_SRC)
    L.append("AETH01_BENCH_PY_EOF")
    L.append("cat > aeth01_bench_server.py <<'AETH01_BENCH_SRV_EOF'")
    L.append(SERVER_SRC)
    L.append("AETH01_BENCH_SRV_EOF")
    L.append("pip install --no-cache-dir 'numpy==2.2.0' 'cupy-cuda12x==13.3.0'")
    L.append("unset RUNPOD_API_KEY RUNPOD_API_TOKEN RUNPOD_TOKEN")
    L.append("python3 pod_service.py &")
    L.append(GATE)
    return "\n".join(L)


def make_body(run_id):
    return {
        "name": "aeth01-scale-" + run_id[-8:],
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
        },
        "entrypoint": ["/bin/bash", "-c"],
        "cmd": [build_script()],
    }


def create_with_reconcile(api, body):
    import runpod_api
    for attempt in range(1, 4):
        try:
            pod = api.create_pod(body)
            log("create attempt %d -> 201 pod_id=%s status=%s"
                % (attempt, pod.get("id"), pod.get("desiredStatus") or pod.get("status")))
            return pod
        except runpod_api.ProviderError as e:
            log("create attempt %d ProviderError status=%s; reconciling" % (attempt, e.status))
            pods = api.list_pods()
            if pods:
                log("reconcile: %d pod(s) present -> adopting, NO further creates" % len(pods))
                return pods[0]
            log("reconcile: 0 pods present (clean no-pod failure)")
            if attempt < 3:
                time.sleep(5)
    log("all 3 create attempts failed with no pod created -> STOP")
    return None


def _save(name, data):
    path = os.path.join(ART_DIR, "aeth01_" + name)
    mode = "wb" if isinstance(data, (bytes, bytearray)) else "w"
    with open(path, mode) as f:
        f.write(data)
    return path


def _validate(result_obj, receipt_obj, run_id):
    reasons = []
    if not (isinstance(result_obj, dict) and result_obj.get("finished") is True
            and result_obj.get("exit_code") == 0 and result_obj.get("run_id") == run_id):
        reasons.append("result.json not a finished exit_code=0 run-bound record")
    r = receipt_obj if isinstance(receipt_obj, dict) else {}
    if r.get("status") != "PASS":
        reasons.append("receipt.status=%r != PASS" % r.get("status"))
    if r.get("run_id") != run_id:
        reasons.append("receipt.run_id mismatch")
    if r.get("backend") != "cupy":
        reasons.append("receipt.backend=%r != cupy (no real GPU)" % r.get("backend"))
    if r.get("cases_expected") != 300 or r.get("cases_run") != 300 or r.get("cases_matched") != 300:
        reasons.append("cases not 300/300/300 (expected=%s run=%s matched=%s)"
                       % (r.get("cases_expected"), r.get("cases_run"), r.get("cases_matched")))
    if r.get("mismatches"):
        reasons.append("%d mismatch(es)" % len(r.get("mismatches")))
    if not r.get("finished_at_utc"):
        reasons.append("receipt.finished_at_utc empty")
    return (not reasons), reasons


def monitor_canary(api, pod_id, run_id):
    """Poll the 8080 proxy for result.json; validate the PASS receipt.
    Returns (ok, receipt_obj). Always writes verdict + artifacts."""
    import runpod_api
    art = runpod_api.ArtifactClient()
    deadline = time.monotonic() + CANARY_DEADLINE_S
    last = None
    while time.monotonic() < deadline:
        try:
            pod = api.get_pod(pod_id)
            status = None if pod is None else (pod.get("desiredStatus") or pod.get("status"))
        except runpod_api.ProviderError as e:
            status = "GET_ERR(%s)" % e.status
        if status != last:
            log("pod status=%s" % status)
            last = status
        try:
            result = art.fetch(pod_id, "result.json")
        except runpod_api.ProviderError as e:
            result = None
            log("result.json fetch status=%s (waiting)" % e.status)
        if result:
            log("result.json received (%d bytes)" % len(result))
            _save("result.json", result)
            receipt = canary = None
            try:
                receipt = art.fetch(pod_id, "receipt.json")
            except runpod_api.ProviderError:
                pass
            try:
                canary = art.fetch(pod_id, "canary.log")
            except runpod_api.ProviderError:
                pass
            if receipt:
                _save("receipt.json", receipt)
            if canary:
                _save("canary.log", canary)
            robj = json.loads(result.decode("utf-8", "replace"))
            recobj = json.loads(receipt.decode("utf-8", "replace")) if receipt else None
            ok, reasons = _validate(robj, recobj, run_id)
            log("CANARY VALIDATION %s" % ("PASS" if ok else "FAIL: " + "; ".join(reasons)))
            if recobj:
                log("receipt: status=%s backend=%s cases=%s/%s matched=%s gpu_s=%s"
                    % (recobj.get("status"), recobj.get("backend"), recobj.get("cases_run"),
                       recobj.get("cases_expected"), recobj.get("cases_matched"),
                       recobj.get("gpu_kernel_seconds")))
            with open(os.path.join(ART_DIR, "aeth01_scale_verdict.txt"), "w") as f:
                f.write("CANARY_%s\nrun_id=%s\n" % ("PASS" if ok else "FAIL", run_id))
                if reasons:
                    f.write("reasons: %s\n" % "; ".join(reasons))
            return ok, recobj
        time.sleep(POLL_S)
    log("CANARY TIMEOUT after %ds, no result.json -> FAIL" % CANARY_DEADLINE_S)
    with open(os.path.join(ART_DIR, "aeth01_scale_verdict.txt"), "w") as f:
        f.write("CANARY_FAIL\nrun_id=%s\nreasons: monitor timeout, no result.json\n" % run_id)
    return False, None


def fetch_bench(pod_id):
    url = "https://%s-8081.proxy.runpod.net/bench.log" % pod_id
    opener = build_opener(ProxyHandler({}))
    req = Request(url, method="GET", headers={"Accept": "text/plain", "User-Agent": UA})
    req.add_unredirected_header("Authorization", "Bearer " + os.environ["AGE_ARTIFACT_TOKEN"])
    try:
        with opener.open(req, timeout=25) as r:
            if r.getcode() == 200:
                return r.read().decode("utf-8", "replace")
    except Exception:
        return None
    return None


def parse_bench(text):
    recs, stop = [], None
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith("AETH01_BENCH {"):
            try:
                recs.append(json.loads(s[len("AETH01_BENCH "):]))
            except Exception:
                pass
        elif s.startswith("AETH01_BENCH_STOP") or s.startswith("AETH01_BENCH_DONE"):
            stop = s
    return recs, stop


def monitor_bench(pod_id):
    deadline = time.monotonic() + BENCH_DEADLINE_S
    text = None
    while time.monotonic() < deadline:
        text = fetch_bench(pod_id)
        if text is not None:
            recs, _stop = parse_bench(text)
            log("bench.log %d bytes, %d size-records so far" % (len(text), len(recs)))
            if "AETH01_BENCH_COMPLETE" in text or "AETH01_BENCH_SKIPPED" in text:
                log("benchmark terminal marker seen")
                break
        else:
            log("bench.log not yet reachable (waiting)")
        time.sleep(POLL_S)
    if text is not None:
        _save("bench.log", text)
    return text


def terminate_and_verify(api, pod_id):
    import runpod_api
    log("terminating pod %s ..." % pod_id)
    try:
        log("terminate outcome: %s" % api.terminate_pod(pod_id))
    except runpod_api.ProviderError as e:
        log("terminate ProviderError status=%s (will still verify absence)" % e.status)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            pods = api.list_pods()
        except runpod_api.ProviderError as e:
            log("list during verify status=%s; retrying" % e.status)
            time.sleep(10)
            continue
        if pod_id not in [p.get("id") for p in pods]:
            log("ABSENCE CONFIRMED: pod %s not in inventory (size=%d)" % (pod_id, len(pods)))
            return True
        log("pod still present; waiting ...")
        time.sleep(10)
    log("WARNING: absence NOT confirmed within 180s; manual check required")
    return False


def write_report(run_id, canary_ok, receipt, bench_text, elapsed_s):
    recs, stop = parse_bench(bench_text or "")
    largest = max((r["size"] for r in recs), default=None)
    peak = max((r.get("sites_per_sec") or 0 for r in recs), default=0)
    lines = ["AETH-01 SCALING RUN REPORT", "run_id=%s" % run_id,
             "gpu=%s vram=48GB cloud=%s hourly=$%.2f" % (GPU_ID, CLOUD, HOURLY),
             "canary=%s" % ("PASS" if canary_ok else "FAIL")]
    if receipt:
        lines.append("canary_backend=%s cases=%s/%s gpu_kernel_seconds=%s"
                     % (receipt.get("backend"), receipt.get("cases_matched"),
                        receipt.get("cases_expected"), receipt.get("gpu_kernel_seconds")))
    lines.append("largest_successful_lattice=%s (%s sites)"
                 % (largest, largest * largest if largest else "n/a"))
    lines.append("peak_sites_per_sec=%s" % (round(peak, 1) if peak else "n/a"))
    lines.append("first_limiting_boundary=%s" % (stop or "none recorded"))
    lines.append("pod_wall_seconds=%.0f est_cost=$%.3f" % (elapsed_s, elapsed_s / 3600.0 * HOURLY))
    lines.append("--- scaling curve (size, tick_med_s, sites/sec, mem_used_mb, parity, digest) ---")
    for r in recs:
        lines.append("  %-6d %-10s %-12s %-9s %-7s %s"
                     % (r.get("size"), r.get("tick_med_s"), r.get("sites_per_sec"),
                        r.get("mem_used_mb"), r.get("parity"), r.get("digest")))
    text = "\n".join(lines) + "\n"
    with open(REPORT, "w") as f:
        f.write(text)
    print(text, flush=True)


def main():
    os.environ["RUNPOD_API_KEY"] = load_key()
    run_id = "aeth01-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + secrets.token_hex(4)
    os.environ["AETH01_RUN_ID"] = run_id
    os.environ["AGE_ARTIFACT_TOKEN"] = secrets.token_urlsafe(32)
    log("RUN_ID=%s (artifact token generated, not shown)" % run_id)

    import runpod_api
    api = runpod_api.RunPodAPI()

    baseline = api.list_pods()
    if baseline:
        log("ABORT: baseline not empty (%d pods) -> refusing to create" % len(baseline))
        return 3
    log("baseline confirmed empty (0 pods)")

    pod = create_with_reconcile(api, make_body(run_id))
    if pod is None:
        return 4
    pod_id = pod["id"]
    with open(POD_ID_FILE, "w") as f:
        f.write(pod_id)
    log("pod_id persisted to %s" % POD_ID_FILE)

    t0 = time.monotonic()
    canary_ok = False
    receipt = None
    bench_text = None
    try:
        canary_ok, receipt = monitor_canary(api, pod_id, run_id)
        if canary_ok:
            log("canary PASS -> retrieving scaling benchmark")
            bench_text = monitor_bench(pod_id)
        else:
            log("canary not PASS -> skipping benchmark; collecting artifacts and stopping")
    finally:
        terminate_and_verify(api, pod_id)
        elapsed = time.monotonic() - t0
        write_report(run_id, canary_ok, receipt, bench_text, elapsed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
