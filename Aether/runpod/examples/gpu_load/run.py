"""A load module: enough GPU work to measure the platform against.

`hello_gpu` proves the path works; it runs 0.67 s of compute inside a
35 s pod and moves 1,164 bytes, so it measures overhead and nothing else.
This module exists so that a flight can measure the other things:

  - sustained throughput, as matrix multiplies per second and TFLOP/s;
  - per-step latency, synchronised, so a stall is visible as a step;
  - real device memory, via a ballast allocation of a declared size;
  - artifact transfer, via a binary artifact of a declared size.

WORK UNITS are matmuls. The count comes from PROMETHEUS_WORK_UNITS, which
the platform sets from `work_units.estimate`, so a scout of this module is
genuinely smaller than its campaign while every other input is identical.
LOAD_STEPS is a local fallback only.

Imports nothing from the platform. Runs on NumPy when CuPy is absent, so
the conformance test can execute it on a machine without a GPU.
"""

import hashlib
import json
import os
import sys
import time

FORBIDDEN = ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN")
ORIGIN = time.monotonic()


def emit(path, kind, **fields):
    record = {"kind": kind,
              "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "t_elapsed_s": round(time.monotonic() - ORIGIN, 3)}
    record.update(fields)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
        fh.flush()


def percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    k = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return sorted_vals[k]


def main():
    run_id = os.environ.get("PROMETHEUS_RUN_ID", "local")
    out_dir = os.environ.get("PROMETHEUS_ARTIFACT_DIR", "out")
    tel = os.environ.get("PROMETHEUS_TELEMETRY_PATH",
                         os.path.join(out_dir, "telemetry.jsonl"))
    os.makedirs(out_dir, exist_ok=True)

    leaked = [n for n in FORBIDDEN if os.environ.get(n)]
    if leaked:
        print("SECRETS_BOUNDARY_VIOLATION %s" % leaked, file=sys.stderr)
        return 92

    steps = int(os.environ.get("PROMETHEUS_WORK_UNITS")
                or os.environ.get("LOAD_STEPS", "100"))
    n = int(os.environ.get("LOAD_N", "4096"))
    ballast_mb = int(os.environ.get("LOAD_BALLAST_MB", "0"))
    artifact_mb = int(os.environ.get("LOAD_ARTIFACT_MB", "1"))
    seed = int(os.environ.get("LOAD_SEED", "20260926"))
    report_every = max(1, int(os.environ.get("LOAD_REPORT_EVERY", "250")))

    device = "cpu"
    gpu = False
    try:
        import cupy as xp
        device = xp.cuda.runtime.getDeviceProperties(0)["name"].decode()
        gpu = True
    except Exception:
        import numpy as xp

    def sync():
        if gpu:
            xp.cuda.Stream.null.synchronize()

    emit(tel, "start", run_id=run_id, device=device, steps=steps, n=n,
         ballast_mb=ballast_mb, artifact_mb=artifact_mb, seed=seed, units=0)

    # Ballast: held, touched, and checksummed at the end so it cannot be
    # optimised away or silently paged. Its purpose is to make device
    # memory a quantity the platform sampler has something to see.
    ballast = None
    if ballast_mb > 0:
        ballast = xp.ones(ballast_mb * (1 << 20) // 4, dtype=xp.float32)
        sync()

    rng = xp.random.RandomState(seed)
    a = rng.standard_normal((n, n)).astype(xp.float32) / float(n) ** 0.5
    b = rng.standard_normal((n, n)).astype(xp.float32) / float(n) ** 0.5
    c = a
    sync()

    latencies = []
    t_start = time.monotonic()
    for step in range(steps):
        t0 = time.perf_counter()
        c = c @ b
        # Keep the values bounded without a data-dependent branch.
        c = c / (xp.abs(c).max() + xp.float32(1e-6))
        sync()
        latencies.append(time.perf_counter() - t0)
        if (step + 1) % report_every == 0:
            window = latencies[-report_every:]
            per = sum(window) / len(window)
            emit(tel, "progress", units=step + 1,
                 step_latency_s_mean=round(per, 6),
                 tflops=round(2.0 * n ** 3 / per / 1e12, 3) if per else None)
    elapsed = time.monotonic() - t_start

    checksum = float(c.sum())
    ballast_sum = float(ballast.sum()) if ballast is not None else 0.0

    # The heavy artifact: deterministic bytes of the declared size, derived
    # from the final state, so it is content rather than padding and a
    # corrupted transfer is detectable by the recorded digest.
    host = c.get() if gpu else c
    seedbytes = host.astype("float32").tobytes()[:1 << 20]
    want = artifact_mb * (1 << 20)
    blob = (seedbytes * (want // max(1, len(seedbytes)) + 1))[:want]
    with open(os.path.join(out_dir, "state.bin"), "wb") as fh:
        fh.write(blob)
    digest = hashlib.sha256(blob).hexdigest()

    ordered = sorted(latencies)
    mean = elapsed / steps if steps else None
    result = {
        "run_id": run_id, "device": device, "steps": steps, "n": n,
        "seed": seed, "elapsed_s": round(elapsed, 4),
        "matmuls_per_s": round(steps / elapsed, 3) if elapsed else None,
        "tflops": round(2.0 * n ** 3 * steps / elapsed / 1e12, 3)
        if elapsed else None,
        "step_latency_s": {
            "mean": round(mean, 6) if mean else None,
            "p50": round(percentile(ordered, 0.50), 6) if ordered else None,
            "p99": round(percentile(ordered, 0.99), 6) if ordered else None,
            "max": round(ordered[-1], 6) if ordered else None,
            # The first step pays for kernel selection and warm-up; it is
            # reported apart so it does not masquerade as a stall.
            "first": round(latencies[0], 6) if latencies else None},
        "checksum": checksum, "ballast_mb": ballast_mb,
        "ballast_checksum": ballast_sum,
        "artifact": {"path": "state.bin", "bytes": len(blob),
                     "sha256": digest},
    }
    with open(os.path.join(out_dir, "result.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    emit(tel, "end", units=steps, status="ok", elapsed_s=round(elapsed, 4),
         tflops=result["tflops"], state_sha256=digest)
    print("GPU_LOAD_OK " + json.dumps({k: result[k] for k in
                                       ("device", "steps", "tflops",
                                        "elapsed_s")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
