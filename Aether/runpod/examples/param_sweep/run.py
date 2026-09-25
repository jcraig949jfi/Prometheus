"""A second example, written from a DIFFERENT seat's point of view.

`hello_gpu` is a smoke test. This is what an ordinary experiment looks
like: a parameter sweep that evaluates a batch of candidate settings on
the GPU, reports progress in its OWN denominator, and writes a result
another process can read.

It exists to keep an honest check on the platform. `hello_gpu` was
written alongside the platform and cannot prove the contract generalises;
this module counts `evaluations`, not site-ticks, has no relationship to
Aether's physics, imports nothing from `prometheus_gpu`, and would be a
reasonable starting point for a seat doing hyperparameter search,
sensitivity analysis or a scan over initial conditions.

If a platform change breaks this module but leaves `hello_gpu` working,
the platform has grown a dependency on its own first example.

Contract used, and nothing else:
  PROMETHEUS_RUN_ID, PROMETHEUS_ARTIFACT_DIR, PROMETHEUS_TELEMETRY_PATH,
  plus whatever this module put in its own `env_allowlist`.
"""

import json
import os
import sys
import time

FORBIDDEN = ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN",
             "AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN")

ORIGIN = time.monotonic()


def emit(path, kind, **fields):
    """One JSON line per record. The whole telemetry contract, inline."""
    record = {"kind": kind,
              "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "t_elapsed_s": round(time.monotonic() - ORIGIN, 3)}
    record.update(fields)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
        fh.flush()


def candidates(count, seed):
    """Deterministic grid. A sweep whose points depend on an unrecorded
    random state cannot be re-run, which makes its results unusable."""
    out = []
    state = int(seed) & 0xFFFFFFFF
    for index in range(count):
        state = (1103515245 * state + 12345) & 0xFFFFFFFF
        out.append({"index": index,
                    "scale": 0.5 + (state % 1000) / 1000.0,
                    "offset": ((state >> 10) % 200) / 100.0 - 1.0})
    return out


def evaluate(xp, sample, size):
    """Stand-in objective. Replace this with the thing you actually score."""
    grid = xp.linspace(-1.0, 1.0, size, dtype=xp.float32)
    shaped = xp.sin(grid * float(sample["scale"])) + float(sample["offset"])
    return float((shaped * shaped).mean())


def main():
    run_id = os.environ.get("PROMETHEUS_RUN_ID", "local")
    out_dir = os.environ.get("PROMETHEUS_ARTIFACT_DIR", "out")
    tel = os.environ.get("PROMETHEUS_TELEMETRY_PATH",
                         os.path.join(out_dir, "telemetry.jsonl"))
    os.makedirs(out_dir, exist_ok=True)

    leaked = [name for name in FORBIDDEN if os.environ.get(name)]
    if leaked:
        # Fail loudly rather than continuing: a module that can read a
        # controller credential is a platform defect, and a run that
        # quietly proceeds hides it.
        print("SECRETS_BOUNDARY_VIOLATION %s" % leaked, file=sys.stderr)
        return 92

    count = int(os.environ.get("SWEEP_CANDIDATES", "64"))
    size = int(os.environ.get("SWEEP_GRID", "65536"))
    seed = int(os.environ.get("SWEEP_SEED", "20260924"))

    device = "cpu"
    try:
        import cupy as xp
        device = xp.cuda.runtime.getDeviceProperties(0)["name"].decode()
    except Exception:
        import numpy as xp

    # The effective configuration goes into telemetry, so the receipt can
    # prove what actually ran rather than what was intended. A run whose
    # parameters are invisible is a run nobody can trust later.
    emit(tel, "start", run_id=run_id, device=device, candidates=count,
         grid=size, seed=seed, units=0)

    best = None
    scores = []
    for sample in candidates(count, seed):
        score = evaluate(xp, sample, size)
        scores.append({"index": sample["index"], "score": score,
                       "scale": sample["scale"], "offset": sample["offset"]})
        if best is None or score < best["score"]:
            best = scores[-1]
            emit(tel, "event", message="new best", units=sample["index"] + 1,
                 index=sample["index"], score=score)
        if (sample["index"] + 1) % 16 == 0:
            emit(tel, "progress", units=sample["index"] + 1,
                 best_score=best["score"])

    result = {"run_id": run_id, "device": device, "seed": seed,
              "candidates": count, "grid": size, "best": best,
              "scores": scores}
    with open(os.path.join(out_dir, "sweep.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)

    emit(tel, "end", units=count, status="ok", best_score=best["score"],
         best_index=best["index"])
    print("PARAM_SWEEP_OK best=%d score=%.6f"
          % (best["index"], best["score"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
