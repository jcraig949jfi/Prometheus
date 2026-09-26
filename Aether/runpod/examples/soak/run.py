"""A long, boring, steady GPU workload for qualifying the PLATFORM over time.

The science is deliberately trivial. What this module exists to expose is
drift: whether anything about the pod, the proxy, the controller or the
module changes over an hour when nothing about the work does.

WORK UNITS are SECONDS of soak, read from PROMETHEUS_WORK_UNITS, so a
scout is a genuinely shorter soak and the platform's cost model prices
time directly.

Every SOAK_REPORT_S seconds it emits one `progress` record carrying, for
that window only:

  - step latency p50 / p95 / p99 / max (synchronised), and TFLOP/s;
  - device memory: CuPy pool used/held, and the driver's free/total;
  - host resident memory of this process (VmRSS);
  - bytes written so far to the growing artifact `series.jsonl`.

Window statistics, not cumulative ones, because a cumulative mean hides a
slow creep behind an hour of good behaviour. The same row is appended to
`series.jsonl`, so the artifact grows steadily for the whole run, and a
4 MiB checkpoint is written every SOAK_CKPT_EVERY_S seconds (the latest as
`ckpt.bin`, earlier ones kept on disk undeclared) so the artifact
directory grows too.

CONTROLLED FAULTS, for qualifying real-provider behaviour, off by default:
SOAK_FAULT in {none, exit, hang, killserver} fires once at SOAK_FAULT_AT_S:

  exit        leave with status 3 and no `end` record, as a crash would;
  hang        stop emitting and sleep forever, as a deadlock would;
  killserver  kill the pod's artifact server process, then carry on to a
              normal finish that nobody can read.

Imports nothing from the platform. Runs on NumPy when CuPy is absent, so
the conformance test can execute it on a machine without a GPU.
"""

import hashlib
import json
import os
import signal
import sys
import time

FORBIDDEN = ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN")
ORIGIN = time.monotonic()


def emit(path, kind, **fields):
    record = {"kind": kind,
              "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "t_elapsed_s": round(time.monotonic() - ORIGIN, 3)}
    record.update(fields)
    line = json.dumps(record, sort_keys=True) + "\n"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()
    return line


def pct(sorted_vals, q):
    if not sorted_vals:
        return None
    k = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return round(sorted_vals[k], 6)


def rss_bytes():
    try:
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        return None
    return None


def is_server_argv(args):
    """True only for `python3 ... /app/_serve.py`: an interpreter whose
    ARGUMENT is the server script.

    The first version matched `_serve.py` anywhere in the command line,
    which also matched the pod's bootstrap shell -- `bash -c <script>`,
    whose script text mentions the server -- and killed the container's
    main process instead (Iteration 3, flight F2).
    """
    if not args or b"python" not in os.path.basename(args[0]):
        return False
    return any(a == b"_serve.py" or a.endswith(b"/_serve.py")
               for a in args[1:])


def kill_artifact_server():
    """Kill the platform's artifact server, and nothing else."""
    killed = []
    for pid in os.listdir("/proc") if os.path.isdir("/proc") else []:
        if not pid.isdigit():
            continue
        try:
            with open("/proc/%s/cmdline" % pid, "rb") as fh:
                args = [a for a in fh.read().split(b"\0") if a]
        except OSError:
            continue
        if is_server_argv(args) and int(pid) != os.getpid():
            try:
                os.kill(int(pid), signal.SIGKILL)
                killed.append(int(pid))
            except OSError:
                pass
    return killed


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

    duration = float(os.environ.get("PROMETHEUS_WORK_UNITS")
                     or os.environ.get("SOAK_SECONDS", "10"))
    n = int(os.environ.get("SOAK_N", "4096"))
    report_s = float(os.environ.get("SOAK_REPORT_S", "10"))
    ckpt_every = float(os.environ.get("SOAK_CKPT_EVERY_S", "600"))
    ckpt_mb = int(os.environ.get("SOAK_CKPT_MB", "4"))
    seed = int(os.environ.get("SOAK_SEED", "20260926"))
    fault = os.environ.get("SOAK_FAULT", "none").strip().lower()
    fault_at = float(os.environ.get("SOAK_FAULT_AT_S", "0") or 0)

    device, gpu = "cpu", False
    try:
        import cupy as xp
        device = xp.cuda.runtime.getDeviceProperties(0)["name"].decode()
        gpu = True
    except Exception:
        import numpy as xp

    def sync():
        if gpu:
            xp.cuda.Stream.null.synchronize()

    def device_mem():
        if not gpu:
            return {}
        pool = xp.get_default_memory_pool()
        free, total = xp.cuda.runtime.memGetInfo()
        return {"pool_used_b": int(pool.used_bytes()),
                "pool_held_b": int(pool.total_bytes()),
                "device_free_b": int(free), "device_total_b": int(total)}

    emit(tel, "start", run_id=run_id, device=device, duration_s=duration,
         n=n, report_s=report_s, ckpt_every_s=ckpt_every, ckpt_mb=ckpt_mb,
         seed=seed, fault=fault, fault_at_s=fault_at, units=0)

    rng = xp.random.RandomState(seed)
    a = rng.standard_normal((n, n)).astype(xp.float32) / float(n) ** 0.5
    b = rng.standard_normal((n, n)).astype(xp.float32) / float(n) ** 0.5
    c = a
    sync()

    series_path = os.path.join(out_dir, "series.jsonl")
    t_start = time.monotonic()
    next_report = t_start + report_s
    next_ckpt = t_start + ckpt_every
    window, steps, windows, ckpts = [], 0, 0, 0
    fired = False
    series_bytes = 0
    ckpt_digest = None
    while True:
        now = time.monotonic()
        elapsed = now - t_start
        if elapsed >= duration:
            break
        if fault != "none" and not fired and elapsed >= fault_at:
            fired = True
            emit(tel, "event", message="injecting fault %s" % fault,
                 units=int(elapsed))
            if fault == "exit":
                return 3
            if fault == "hang":
                while True:
                    time.sleep(3600)
            if fault == "killserver":
                emit(tel, "event", message="killed artifact server pids %s"
                     % kill_artifact_server(), units=int(elapsed))
        t0 = time.perf_counter()
        c = c @ b
        c = c / (xp.abs(c).max() + xp.float32(1e-6))
        sync()
        window.append(time.perf_counter() - t0)
        steps += 1
        now = time.monotonic()
        if now >= next_report:
            ordered = sorted(window)
            mean = sum(window) / len(window)
            row = {"window": windows, "steps": len(window),
                   "elapsed_s": round(now - t_start, 3),
                   "latency_p50_s": pct(ordered, 0.50),
                   "latency_p95_s": pct(ordered, 0.95),
                   "latency_p99_s": pct(ordered, 0.99),
                   "latency_max_s": round(ordered[-1], 6),
                   "tflops": round(2.0 * n ** 3 / mean / 1e12, 3),
                   "rss_b": rss_bytes()}
            row.update(device_mem())
            line = json.dumps(row, sort_keys=True) + "\n"
            with open(series_path, "a", encoding="utf-8") as fh:
                fh.write(line)
            series_bytes += len(line)
            row["series_bytes"] = series_bytes
            emit(tel, "progress", units=int(now - t_start), **row)
            window = []
            windows += 1
            next_report += report_s
        if now >= next_ckpt:
            host = c.get() if gpu else c
            seedbytes = host.astype("float32").tobytes()[:1 << 20]
            want = ckpt_mb * (1 << 20)
            blob = (seedbytes * (want // max(1, len(seedbytes)) + 1))[:want]
            with open(os.path.join(out_dir, "ckpt_%03d.bin" % ckpts), "wb") as fh:
                fh.write(blob)
            with open(os.path.join(out_dir, "ckpt.bin"), "wb") as fh:
                fh.write(blob)
            ckpt_digest = hashlib.sha256(blob).hexdigest()
            emit(tel, "event", message="checkpoint %d" % ckpts,
                 units=int(now - t_start), ckpt_sha256=ckpt_digest)
            ckpts += 1
            next_ckpt += ckpt_every

    elapsed = time.monotonic() - t_start
    if ckpt_digest is None:
        blob = b"\0" * (ckpt_mb * (1 << 20))
        with open(os.path.join(out_dir, "ckpt.bin"), "wb") as fh:
            fh.write(blob)
        ckpt_digest = hashlib.sha256(blob).hexdigest()
    result = {"run_id": run_id, "device": device, "duration_s": duration,
              "elapsed_s": round(elapsed, 3), "steps": steps,
              "windows": windows, "checkpoints": ckpts, "n": n,
              "checksum": float(c.sum()), "ckpt_sha256": ckpt_digest,
              "series_bytes": series_bytes, "fault": fault,
              "fault_fired": fired}
    with open(os.path.join(out_dir, "result.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    emit(tel, "end", units=int(elapsed), status="ok",
         elapsed_s=round(elapsed, 3), steps=steps, windows=windows,
         checkpoints=ckpts)
    print("SOAK_OK " + json.dumps({k: result[k] for k in
                                   ("device", "elapsed_s", "steps",
                                    "windows", "checkpoints")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
