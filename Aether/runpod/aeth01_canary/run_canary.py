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
"""

import json
import random
import time

import numpy as np

from aeth01_cpu_oracle import Aeth01World
from aeth01_gpu_kernel import gpu_step, BACKEND

SEMANTICS_ID = "aeth01.v1"

# Preregistered corpus: fixed seed, small worlds, modest trial count --
# this is a canary (one differential-match data point), not a campaign.
RNG_SEED = 0
TRIALS = 200
MAX_DIM = 4


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


def main():
    rng = random.Random(RNG_SEED)
    mismatches = []
    cpu_seconds = 0.0
    gpu_seconds = 0.0

    for i in range(TRIALS):
        (H, W, seed, tick, write_cost, maintenance_cost, replenish_numer,
         replenish_amount, mut_numer, grid) = make_trial(rng)

        t0 = time.perf_counter()
        w = Aeth01World(H, W, seed, write_cost, maintenance_cost,
                        replenish_numer, replenish_amount, mut_numer,
                        tick=tick, grid=grid)
        cpu_next = w.step()
        cpu_seconds += time.perf_counter() - t0

        opcode, arg0, arg1, payload, energy = to_arrays(grid)
        t0 = time.perf_counter()
        no_, na0, na1, npl, ne, _counters = gpu_step(
            H, W, seed, tick, write_cost, maintenance_cost, replenish_numer,
            replenish_amount, mut_numer, opcode, arg0, arg1, payload, energy,
        )
        gpu_seconds += time.perf_counter() - t0

        cpu_o, cpu_a0, cpu_a1, cpu_pl, cpu_e = to_arrays(cpu_next.grid)

        def as_host(x):
            return x.get() if hasattr(x, "get") else x

        ok = (
            np.array_equal(as_host(no_), cpu_o) and np.array_equal(as_host(na0), cpu_a0) and
            np.array_equal(as_host(na1), cpu_a1) and np.array_equal(as_host(npl), cpu_pl) and
            np.array_equal(as_host(ne), cpu_e)
        )
        if not ok:
            mismatches.append({
                "trial": i, "H": H, "W": W, "seed": seed, "tick": tick,
                "write_cost": write_cost, "maintenance_cost": maintenance_cost,
                "replenish_numer": replenish_numer, "replenish_amount": replenish_amount,
                "mut_numer": mut_numer, "grid": grid,
            })

    receipt = {
        "semantics_id": SEMANTICS_ID,
        "backend": BACKEND,
        "cases_run": TRIALS,
        "cases_matched": TRIALS - len(mismatches),
        "gpu_kernel_seconds": gpu_seconds,
        "cpu_oracle_seconds": cpu_seconds,
        "mismatches": mismatches,
    }
    with open("receipt.json", "w") as f:
        json.dump(receipt, f, indent=2, default=str)
    print(json.dumps({k: v for k, v in receipt.items() if k != "mismatches"}, indent=2))
    print(f"mismatches: {len(mismatches)}")


if __name__ == "__main__":
    main()
