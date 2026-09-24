"""The minimal GPU module: copy this directory and change two things.

Demonstrates the whole contract in one file:
  - read the run identity the platform provides;
  - emit telemetry as JSON lines to PROMETHEUS_TELEMETRY_PATH;
  - write declared artifacts under PROMETHEUS_ARTIFACT_DIR;
  - prove the secrets boundary held, from inside module code;
  - exit non-zero on failure so the platform can see it.

It needs no knowledge of RunPod, and it never sees a provider credential.
"""

import json
import os
import sys
import time

FORBIDDEN = ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN")


ORIGIN = time.monotonic()


def telemetry(path, record):
    """Append one JSON line. See TELEMETRY_SCHEMA.md.

    Both clocks are required. `t_utc` answers when, `t_elapsed_s`
    answers how far in. The pod and the controller keep different
    clocks, so a progress curve can only be placed against a cost
    curve using an origin the pod itself agrees with.

    This imports nothing from the platform, which is the point: a
    module is not obliged to depend on us in order to be observable.
    """
    record.setdefault("t_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                             time.gmtime()))
    record.setdefault("t_elapsed_s", round(time.monotonic() - ORIGIN, 3))
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
        fh.flush()


def main():
    run_id = os.environ.get("PROMETHEUS_RUN_ID", "unknown")
    out_dir = os.environ.get("PROMETHEUS_ARTIFACT_DIR", "out")
    tel = os.environ.get("PROMETHEUS_TELEMETRY_PATH",
                         os.path.join(out_dir, "telemetry.jsonl"))
    os.makedirs(out_dir, exist_ok=True)

    # The module's own check of the secrets boundary. The platform also
    # checks it in the bootstrap, but a module that cares can verify.
    leaked = [n for n in FORBIDDEN if os.environ.get(n)]
    if leaked:
        print("SECRETS_BOUNDARY_VIOLATION %s" % leaked, file=sys.stderr)
        return 92

    device = "cpu"
    steps = int(os.environ.get("HELLO_STEPS", "200"))
    try:
        import cupy as xp
        device = xp.cuda.runtime.getDeviceProperties(0)["name"].decode()
    except Exception:
        import numpy as xp

    telemetry(tel, {"kind": "start", "run_id": run_id, "device": device,
                    "steps": steps})

    total = 0.0
    t0 = time.monotonic()
    for step in range(steps):
        a = xp.arange(1 << 18, dtype=xp.float32)
        total += float((a * a).sum())
        if step % 50 == 0:
            # `units` is the reserved progress counter the
            # platform reads for cost per unit of useful work.
            telemetry(tel, {"kind": "progress", "step": step,
                            "units": step, "checksum": total})
    elapsed = time.monotonic() - t0

    result = {"run_id": run_id, "device": device, "steps": steps,
              "checksum": total, "elapsed_s": round(elapsed, 4),
              "steps_per_s": round(steps / elapsed, 2) if elapsed else None}
    with open(os.path.join(out_dir, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    telemetry(tel, {"kind": "end", "units": steps, "status": "ok",
                    **result})
    print("HELLO_GPU_OK " + json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
