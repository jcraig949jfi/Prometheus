"""
Aether AETH-01 (candidate semantics_id aeth01.v1) -- RunPod canary
on-pod entry point.

Runs a small preregistered differential corpus (same shape as
Aether/test/test_aeth01_gpu_differential.py) CPU-oracle vs GPU-kernel
on whichever backend `aeth01_gpu_kernel.py` selected (CuPy on real GPU
hardware, or NumPy fallback), times the GPU path, and writes
`receipt.json` (schema: `receipt_schema.json`). Does not launch or
terminate the pod itself -- that is the external `age_controller.py`.
The on-pod service stays alive for artifact collection before termination.

Pass/fail semantics (explicit, closed vocabulary -- see `FINAL_STATUSES`
below; a receipt with any other `status` string is itself a schema
violation, not just a bad result):

- `PASS`: every case (single-tick and multi-tick) matched, on a
  qualifying backend.
- `FAIL_MISMATCH`: at least one case disagreed.
- `FAIL_ENVIRONMENT`: this run intended to exercise a real GPU
  (`AETH01_CANARY_REQUIRE_GPU` unset or not `"0"`, the default) but
  `aeth01_gpu_kernel.py` fell back to NumPy -- meaning CuPy failed to
  import. This is ALWAYS a fail, never a silent pass, regardless of
  whether the NumPy-fallback arithmetic happens to match the CPU
  oracle (it would -- they're both plain Python/NumPy -- and that fact
  answers nothing about real GPU hardware, which is the one question
  this canary exists to answer, README.md).
- `FAIL_ERROR`: an unhandled exception occurred during the run.
- `FAIL_INCOMPLETE`: the placeholder status written to `receipt.json`
  BEFORE the run starts, also used if the full preregistered corpus
  was not completed. It must never be read as a pass by omission.

The process exit code is 0 iff `status == "PASS"`, nonzero otherwise --
callers (CI, an operator's shell) must not need to parse the receipt
just to know whether the run failed.
"""

import hashlib
import json
import math
import os
import platform
import random
import sys
import tempfile
import time
from datetime import datetime, timezone

import numpy as np

from aeth01_cpu_oracle import Aeth01World
from aeth01_gpu_kernel import gpu_step, BACKEND, np as gpu_np

SEMANTICS_ID = "aeth01.v1"
RECEIPT_PATH = "receipt.json"
_HERE = os.path.dirname(os.path.abspath(__file__))
_SOURCE_FILES = ("aeth01_cpu_oracle.py", "aeth01_gpu_kernel.py", "run_canary.py")

STATUS_PASS = "PASS"
STATUS_FAIL_MISMATCH = "FAIL_MISMATCH"
STATUS_FAIL_ENVIRONMENT = "FAIL_ENVIRONMENT"
STATUS_FAIL_ERROR = "FAIL_ERROR"
STATUS_FAIL_INCOMPLETE = "FAIL_INCOMPLETE"
FINAL_STATUSES = frozenset({
    STATUS_PASS, STATUS_FAIL_MISMATCH, STATUS_FAIL_ENVIRONMENT,
    STATUS_FAIL_ERROR, STATUS_FAIL_INCOMPLETE,
})

# Preregistered corpus: fixed seed, small worlds, modest trial count --
# this is a canary (one differential-match data point), not a campaign.
RNG_SEED = 0
TRIALS = 200            # single-tick trials.
MULTI_TICK_TRIALS = 20  # additional trajectories, each run for MULTI_TICK_STEPS ticks,
MULTI_TICK_STEPS = 5    # comparing CPU vs GPU state at EVERY intermediate tick, not
                         # just the final one (GPU_RUNPOD.md "Verify" tier).
MAX_DIM = 4
EXPECTED_CASES = 200 + 20 * 5
_FIELDS = ("opcode", "arg0", "arg1", "payload", "energy")

# Whether this run REQUIRES a real GPU backend (CuPy) to count as
# evidence. Defaults to REQUIRED -- this package's entire purpose is a
# real-hardware canary (README.md). Set AETH01_CANARY_REQUIRE_GPU=0
# only for local NumPy-fallback smoke-testing of this script itself,
# never when actually launched on a pod.
REQUIRE_GPU = os.environ.get("AETH01_CANARY_REQUIRE_GPU", "1") != "0"


def _sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _source_hashes():
    """sha256 of each bundled physics/harness source file, so a reviewer
    can confirm exactly which revision ran without needing git history
    on the pod (the image only ever contains a copy, not a checkout)."""
    out = {}
    for name in _SOURCE_FILES:
        path = os.path.join(_HERE, name)
        out[name] = _sha256_of(path) if os.path.exists(path) else None
    return out


def _cost_context():
    """Echo AGE controller quote/budget and process timeout, not actual spend.
    All fields are null when run standalone (e.g. local smoke test).
    The external controller bounds pod lifetime separately from compute time.
    """
    def _float_env(name):
        v = os.environ.get(name)
        try:
            value = float(v) if v is not None else None
            return value if value is not None and math.isfinite(value) else None
        except ValueError:
            return None

    return {
        "hourly_rate_usd": _float_env("AETH01_CANARY_HOURLY_RATE"),
        "max_dollar_budget_usd": _float_env("AETH01_CANARY_MAX_DOLLAR_BUDGET"),
        "watchdog_timeout_seconds": _float_env("AETH01_CANARY_TIMEOUT_SECONDS"),
    }


def _versions():
    try:
        cupy_version = __import__("cupy").__version__ if BACKEND == "cupy" else None
    except Exception:  # pragma: no cover -- defensive only.
        cupy_version = None
    return {
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "cupy_version": cupy_version,
    }


def write_receipt(receipt):
    """Publish complete JSON atomically, leaving the previous receipt on failure."""
    if receipt["status"] not in FINAL_STATUSES:
        raise AssertionError(f"unknown status {receipt['status']!r} is a schema violation")
    payload = json.dumps(receipt, indent=2, allow_nan=False) + "\n"
    target = os.path.abspath(RECEIPT_PATH)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=os.path.dirname(target),
            prefix=os.path.basename(target) + ".", suffix=".tmp", delete=False,
        ) as f:
            temporary = f.name
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)


def make_trial(rng):
    H = rng.randint(1, MAX_DIM)
    W = rng.randint(1, MAX_DIM)
    seed = rng.randint(0, 2**64 - 1)
    tick = rng.randint(0, 2**63)
    write_cost = rng.randint(0, 255)
    maintenance_cost = rng.randint(0, 255)
    replenish_numer = rng.choice([0, 1, 1 << 16, 1 << 31, 1 << 32])
    replenish_amount = rng.randint(0, 255)
    mut_numer = rng.choice([0, 1, 1 << 16, 1 << 31, 1 << 32])
    grid = []
    for _r in range(H):
        row = []
        for _c in range(W):
            if rng.random() < 0.5:
                site = (1, rng.randint(0, 255), rng.randint(0, 255),
                        rng.randint(0, 255), rng.randint(0, 255))
            else:
                site = (rng.choice([x for x in range(256) if x != 1]),
                        rng.randint(0, 4), rng.randint(0, 4),
                        rng.randint(0, 4), rng.randint(0, 255))
            row.append(site)
        grid.append(row)
    return H, W, seed, tick, write_cost, maintenance_cost, replenish_numer, replenish_amount, mut_numer, grid


def to_arrays(grid):
    a = np.array(grid, dtype=np.uint8)
    return a[:, :, 0], a[:, :, 1], a[:, :, 2], a[:, :, 3], a[:, :, 4]


def _as_host(x):
    return x.get() if hasattr(x, "get") else x


def _synchronize_gpu():
    if BACKEND == "cupy":
        gpu_np.cuda.get_current_stream().synchronize()


def _output_diff(cpu_arrays, gpu_arrays):
    """Every differing field/site, including malformed output shapes."""
    differences = []
    for field, cpu, gpu in zip(_FIELDS, cpu_arrays, gpu_arrays):
        if cpu.shape != gpu.shape:
            differences.append({
                "field": field, "cpu_shape": list(cpu.shape), "gpu_shape": list(gpu.shape),
            })
        else:
            for row, col in np.argwhere(cpu != gpu):
                differences.append({
                    "field": field, "row": int(row), "col": int(col),
                    "cpu": int(cpu[row, col]), "gpu": int(gpu[row, col]),
                })
    return differences


def run_corpus(rng, num_trials, num_ticks):
    """Run `num_trials` independent worlds for `num_ticks` ticks each,
    CPU oracle vs GPU-kernel, comparing state at EVERY tick (not just
    the final one -- GPU_RUNPOD.md "Verify" tier requirement). A
    trajectory stops comparing at its first divergence (a later tick
    starting from an already-disagreeing state would only add noise to
    the mismatch list, not new information). Returns
    (cases_run, mismatches, cpu_seconds, gpu_seconds)."""
    mismatches = []
    cases_run = 0
    cpu_seconds = 0.0
    gpu_seconds = 0.0

    for i in range(num_trials):
        (H, W, seed, tick0, write_cost, maintenance_cost, replenish_numer,
         replenish_amount, mut_numer, grid) = make_trial(rng)
        w = Aeth01World(H, W, seed, write_cost, maintenance_cost,
                        replenish_numer, replenish_amount, mut_numer,
                        tick=tick0, grid=grid)
        gpu_arrays = tuple(gpu_np.asarray(a) for a in to_arrays(w.grid))

        for t in range(num_ticks):
            cases_run += 1
            t0 = time.perf_counter()
            cpu_next = w.step()
            cpu_seconds += time.perf_counter() - t0

            _synchronize_gpu()
            t0 = time.perf_counter()
            *gpu_next, _counters = gpu_step(
                w.H, w.W, w.seed, w.tick, w.write_cost, w.maintenance_cost,
                w.replenish_numer, w.replenish_amount, w.mut_numer,
                *gpu_arrays,
            )
            _synchronize_gpu()
            gpu_seconds += time.perf_counter() - t0

            if len(gpu_next) != len(_FIELDS):
                raise ValueError("gpu_step must return five state arrays and counters")
            cpu_arrays = to_arrays(cpu_next.grid)
            gpu_host = tuple(_as_host(a) for a in gpu_next)
            ok = all(np.array_equal(cpu, gpu) for cpu, gpu in zip(cpu_arrays, gpu_host))
            if not ok:
                mismatches.append({
                    "trial": i, "tick_index": t, "H": H, "W": W, "seed": seed,
                    "tick": w.tick, "write_cost": write_cost,
                    "maintenance_cost": maintenance_cost,
                    "replenish_numer": replenish_numer,
                    "replenish_amount": replenish_amount, "mut_numer": mut_numer,
                    "grid": w.grid,
                    "cpu_output": {name: a.tolist() for name, a in zip(_FIELDS, cpu_arrays)},
                    "gpu_output": {name: a.tolist() for name, a in zip(_FIELDS, gpu_host)},
                    "output_diff": _output_diff(cpu_arrays, gpu_host),
                })
                break
            w = cpu_next
            gpu_arrays = tuple(gpu_next)

    return cases_run, mismatches, cpu_seconds, gpu_seconds


def main() -> int:
    started_at = datetime.now(timezone.utc).isoformat()
    receipt = {
        "semantics_id": SEMANTICS_ID,
        "run_id": os.environ.get("AETH01_RUN_ID") or None,
        "backend": BACKEND,
        "status": STATUS_FAIL_INCOMPLETE,
        "cases_expected": EXPECTED_CASES,
        "cases_run": 0,
        "cases_matched": 0,
        "single_tick_trials": TRIALS,
        "multi_tick_trials": MULTI_TICK_TRIALS,
        "multi_tick_steps": MULTI_TICK_STEPS,
        "rng_seed": RNG_SEED,
        "gpu_kernel_seconds": 0.0,
        "cpu_oracle_seconds": 0.0,
        "mismatches": [],
        "started_at_utc": started_at,
        "finished_at_utc": None,
        "source_hashes": dict.fromkeys(_SOURCE_FILES),
        "cost_context": _cost_context(),
        **_versions(),
    }
    # Placeholder written BEFORE the run starts: if this process is
    # killed (watchdog.sh, Ctrl-C, host failure) before reaching any of
    # the write_receipt() calls below, THIS is what a reader finds on
    # disk -- FAIL_INCOMPLETE, never PASS by omission.
    write_receipt(receipt)

    try:
        receipt["source_hashes"] = _source_hashes()
        if any(value is None for value in receipt["source_hashes"].values()):
            raise ValueError("missing bundled canary source file")
        if BACKEND != "cupy" and REQUIRE_GPU:
            receipt["status"] = STATUS_FAIL_ENVIRONMENT
            print(
                f"[run_canary] FAIL_ENVIRONMENT: backend={BACKEND!r} but a GPU backend "
                "was required (AETH01_CANARY_REQUIRE_GPU != '0').",
                file=sys.stderr,
            )
        else:
            rng = random.Random(RNG_SEED)
            corpus_counts = []
            for label, trials, ticks in (
                ("single_tick", TRIALS, 1),
                ("multi_tick", MULTI_TICK_TRIALS, MULTI_TICK_STEPS),
            ):
                cases, mismatches, cpu_seconds, gpu_seconds = run_corpus(rng, trials, ticks)
                # Retain completed evidence even if the next corpus raises.
                corpus_counts.append(cases)
                receipt["cases_run"] += cases
                receipt["cases_matched"] += cases - len(mismatches)
                receipt["cpu_oracle_seconds"] += cpu_seconds
                receipt["gpu_kernel_seconds"] += gpu_seconds
                receipt["mismatches"].extend(dict(mm, corpus=label) for mm in mismatches)
            complete = (
                (TRIALS, MULTI_TICK_TRIALS, MULTI_TICK_STEPS, RNG_SEED) == (200, 20, 5, 0)
                and corpus_counts == [200, 100]
            )
            receipt["status"] = (
                STATUS_FAIL_MISMATCH if receipt["mismatches"] else
                STATUS_PASS if complete else STATUS_FAIL_INCOMPLETE
            )
    except Exception as exc:  # noqa: BLE001 -- any failure here is itself a real finding.
        receipt["status"] = STATUS_FAIL_ERROR
        receipt["error"] = repr(exc)
        print(f"[run_canary] FAIL_ERROR: unhandled exception: {exc!r}", file=sys.stderr)

    receipt["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_receipt(receipt)

    print(json.dumps({k: v for k, v in receipt.items() if k != "mismatches"}, indent=2))
    print(f"mismatches: {len(receipt['mismatches'])}")
    print(f"[run_canary] final status: {receipt['status']}")
    return 0 if receipt["status"] == STATUS_PASS else 1


if __name__ == "__main__":
    sys.exit(main())
