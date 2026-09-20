"""
Aether AETH-01 (candidate semantics_id aeth01.v1) -- RunPod canary
on-pod entry point.

Runs a small preregistered differential corpus (same shape as
Aether/test/test_aeth01_gpu_differential.py) CPU-oracle vs GPU-kernel
on whichever backend `aeth01_gpu_kernel.py` selected (CuPy on real GPU
hardware, or NumPy fallback), times the GPU path, and writes
`receipt.json` (schema: `receipt_schema.json`). Does not launch or
terminate the pod itself -- that is `launch_pod.sh` / `terminate_pod.sh`,
run by the operator.

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
  BEFORE the run starts, overwritten unconditionally once a real
  verdict is reached. If this is what a reader finds on disk, the run
  never reached a verdict (e.g. it was still running, or `watchdog.sh`
  SIGKILLed it) -- it must never be read as a pass by omission.

The process exit code is 0 iff `status == "PASS"`, nonzero otherwise --
callers (CI, an operator's shell) must not need to parse the receipt
just to know whether the run failed.
"""

import hashlib
import json
import os
import platform
import random
import sys
import time
from datetime import datetime, timezone

import numpy as np

from aeth01_cpu_oracle import Aeth01World
from aeth01_gpu_kernel import gpu_step, BACKEND

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
    """Best-effort echo of the cost-control inputs `launch_pod.sh`
    derived this run's watchdog timeout from, if it set them (it sets
    AETH01_CANARY_TIMEOUT_SECONDS always; HOURLY_RATE/MAX_DOLLAR_BUDGET
    are echoed here only if also exported -- see launch_pod.sh). All
    fields are null when run standalone (e.g. local smoke test)."""
    def _float_env(name):
        v = os.environ.get(name)
        try:
            return float(v) if v is not None else None
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
    assert receipt["status"] in FINAL_STATUSES, f"unknown status {receipt['status']!r} is a schema violation"
    with open(RECEIPT_PATH, "w") as f:
        json.dump(receipt, f, indent=2, default=str)


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
                cell = (1, rng.randint(0, 255), rng.randint(0, 255),
                        rng.randint(0, 255), rng.randint(0, 255))
            else:
                cell = (rng.choice([x for x in range(256) if x != 1]),
                        rng.randint(0, 4), rng.randint(0, 4),
                        rng.randint(0, 4), rng.randint(0, 255))
            row.append(cell)
        grid.append(row)
    return H, W, seed, tick, write_cost, maintenance_cost, replenish_numer, replenish_amount, mut_numer, grid


def to_arrays(grid):
    a = np.array(grid, dtype=np.uint8)
    return a[:, :, 0], a[:, :, 1], a[:, :, 2], a[:, :, 3], a[:, :, 4]


def _as_host(x):
    return x.get() if hasattr(x, "get") else x


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
        gpu_o, gpu_a0, gpu_a1, gpu_pl, gpu_e = to_arrays(w.grid)

        for t in range(num_ticks):
            cases_run += 1
            t0 = time.perf_counter()
            cpu_next = w.step()
            cpu_seconds += time.perf_counter() - t0

            t0 = time.perf_counter()
            no_, na0, na1, npl, ne, _counters = gpu_step(
                w.H, w.W, w.seed, w.tick, w.write_cost, w.maintenance_cost,
                w.replenish_numer, w.replenish_amount, w.mut_numer,
                gpu_o, gpu_a0, gpu_a1, gpu_pl, gpu_e,
            )
            gpu_seconds += time.perf_counter() - t0

            cpu_o, cpu_a0, cpu_a1, cpu_pl, cpu_e = to_arrays(cpu_next.grid)
            ok = (
                np.array_equal(_as_host(no_), cpu_o) and np.array_equal(_as_host(na0), cpu_a0) and
                np.array_equal(_as_host(na1), cpu_a1) and np.array_equal(_as_host(npl), cpu_pl) and
                np.array_equal(_as_host(ne), cpu_e)
            )
            if not ok:
                mismatches.append({
                    "trial": i, "tick_index": t, "H": H, "W": W, "seed": seed,
                    "tick": w.tick, "write_cost": write_cost,
                    "maintenance_cost": maintenance_cost,
                    "replenish_numer": replenish_numer,
                    "replenish_amount": replenish_amount, "mut_numer": mut_numer,
                    "grid": w.grid,
                })
                break
            w = cpu_next
            gpu_o, gpu_a0, gpu_a1, gpu_pl, gpu_e = cpu_o, cpu_a0, cpu_a1, cpu_pl, cpu_e

    return cases_run, mismatches, cpu_seconds, gpu_seconds


def main() -> int:
    started_at = datetime.now(timezone.utc).isoformat()
    receipt = {
        "semantics_id": SEMANTICS_ID,
        "backend": BACKEND,
        "status": STATUS_FAIL_INCOMPLETE,
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
        "source_hashes": _source_hashes(),
        "cost_context": _cost_context(),
        **_versions(),
    }
    # Placeholder written BEFORE the run starts: if this process is
    # killed (watchdog.sh, Ctrl-C, host failure) before reaching any of
    # the write_receipt() calls below, THIS is what a reader finds on
    # disk -- FAIL_INCOMPLETE, never PASS by omission.
    write_receipt(receipt)

    if BACKEND != "cupy" and REQUIRE_GPU:
        receipt["status"] = STATUS_FAIL_ENVIRONMENT
        receipt["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        write_receipt(receipt)
        print(
            f"[run_canary] FAIL_ENVIRONMENT: backend={BACKEND!r} but a GPU backend "
            "was required (AETH01_CANARY_REQUIRE_GPU != '0'). CuPy failed to "
            "import -- this is a finding about the pod's environment, never a "
            "silent pass, regardless of whether NumPy-fallback arithmetic would "
            "have matched the CPU oracle.",
            file=sys.stderr,
        )
        return 1

    try:
        rng = random.Random(RNG_SEED)
        single_run, single_mm, cpu_s1, gpu_s1 = run_corpus(rng, TRIALS, 1)
        multi_run, multi_mm, cpu_s2, gpu_s2 = run_corpus(rng, MULTI_TICK_TRIALS, MULTI_TICK_STEPS)
    except Exception as exc:  # noqa: BLE001 -- any failure here is itself a real finding.
        receipt["status"] = STATUS_FAIL_ERROR
        receipt["error"] = repr(exc)
        receipt["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        write_receipt(receipt)
        print(f"[run_canary] FAIL_ERROR: unhandled exception: {exc!r}", file=sys.stderr)
        return 1

    cases_run = single_run + multi_run
    mismatches = single_mm + multi_mm
    receipt.update({
        "cases_run": cases_run,
        "cases_matched": cases_run - len(mismatches),
        "gpu_kernel_seconds": gpu_s1 + gpu_s2,
        "cpu_oracle_seconds": cpu_s1 + cpu_s2,
        "mismatches": mismatches,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    })
    receipt["status"] = STATUS_PASS if not mismatches else STATUS_FAIL_MISMATCH
    write_receipt(receipt)

    print(json.dumps({k: v for k, v in receipt.items() if k != "mismatches"}, indent=2))
    print(f"mismatches: {len(mismatches)}")
    print(f"[run_canary] final status: {receipt['status']}")
    return 0 if receipt["status"] == STATUS_PASS else 1


if __name__ == "__main__":
    sys.exit(main())
