"""Memory-footprint regression guard for the aeth01.v1 GPU kernel.

Nothing else in this suite measures ALLOCATION, only behavior. The
2026-09-22 optimization round (GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md)
cut peak per-tick allocation 240.00 -> 113.01 bytes/site, which is what
makes a 16384^2 lattice fit in 48 GB. Widening one dtype back to int64
would give that away silently: every behavioral test would still pass
and the capability would just quietly disappear.

This file also pins the kernel to digests produced on REAL A40 hardware
under CuPy, not merely to agreement with the local CPU oracle.

The measurement self-check matters as much as the measurement. If
tracemalloc could not see NumPy's allocations, every figure here would
read zero and a ceiling assertion would pass vacuously -- a green test
that measured nothing. `test_tracemalloc_can_see_numpy_allocations`
fails in that case, so the ceiling test cannot be trivially green.
"""

import hashlib
import tracemalloc

import numpy as np
import pytest

from reference.gpu_aeth01 import gpu_step


# Measured on the unmodified kernel at 251bc987e, NumPy backend. Kept as
# the thing the current kernel must stay well under, not as a target.
BASELINE_BYTES_PER_SITE = 240.00

# Ceiling, not an expectation. Measured after the round: 113.01. The gap
# absorbs backend and version wobble; it does NOT absorb re-widening a
# field array to int64, which costs 6 or more bytes/site each.
CEILING_BYTES_PER_SITE = 130.0

# aeth01_bench.py's fixed benchmark parameters.
SEED = 0x1234ABCD
WRITE_COST, MAINT = 10, 1
REPL_NUMER, REPL_AMT, MUT_NUMER = 1 << 31, 5, 1 << 31
TICKS_TOTAL = 7  # 2 warmup + 5 measured

# Final-state digests from RUNPOD_SCALE_RECEIPT_2026-09-22.md, produced
# on an NVIDIA A40 under CuPy 13.3.0 -- not regenerated from this code.
A40_DIGESTS = {
    16: "1000219c591e1595",
    32: "9f65f15cb87b630f",
    64: "3ce333436da923b0",
    128: "3ab66c98546a3a95",
    256: "7383c7d828504a30",
}


def _build_host(n):
    """Byte-identical to aeth01_bench.py's build_host."""
    rs = np.random.RandomState(SEED & 0x7FFFFFFF)
    opc = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    mask = rs.randint(0, 2, size=(n, n)).astype(bool)
    opc = np.where(mask, np.uint8(1), opc).astype(np.uint8)
    arg0 = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    arg1 = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    payload = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    energy = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    return opc, arg0, arg1, payload, energy


def _step(n, tick, fields):
    return gpu_step(n, n, SEED, tick, WRITE_COST, MAINT, REPL_NUMER,
                    REPL_AMT, MUT_NUMER, *fields)


def _peak_bytes_per_site(n, reps=3):
    fields = _build_host(n)
    tracemalloc.start()
    try:
        peaks = []
        for _ in range(reps):
            tracemalloc.reset_peak()
            before = tracemalloc.get_traced_memory()[0]
            out = _step(n, 3, fields)
            peaks.append(tracemalloc.get_traced_memory()[1] - before)
            del out
    finally:
        tracemalloc.stop()
    return min(peaks) / (n * n)


def test_tracemalloc_can_see_numpy_allocations():
    # Guards every other number in this file: if NumPy's data allocations
    # are invisible to tracemalloc, the footprint test measures nothing.
    size = 4_000_000
    tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        before = tracemalloc.get_traced_memory()[0]
        block = np.zeros(size, dtype=np.uint8)
        observed = tracemalloc.get_traced_memory()[1] - before
        del block
    finally:
        tracemalloc.stop()
    assert observed >= size, (
        f"tracemalloc saw {observed} bytes for a {size}-byte NumPy array; "
        "allocation measurement is not working, so the footprint ceiling "
        "below would pass without measuring anything")


@pytest.mark.parametrize("n", [128, 256, 512])
def test_peak_allocation_stays_under_ceiling(n):
    per_site = _peak_bytes_per_site(n)
    assert per_site <= CEILING_BYTES_PER_SITE, (
        f"peak allocation regressed to {per_site:.2f} bytes/site at {n}x{n} "
        f"(ceiling {CEILING_BYTES_PER_SITE}). A 16384^2 lattice needs "
        f"{per_site * 268435456 / 2**30:.1f} GB at this rate; the A40 has 48 GB. "
        "See Aether/AETH-01/GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md.")


def test_peak_allocation_is_materially_below_the_pre_optimization_baseline():
    per_site = _peak_bytes_per_site(512)
    assert per_site < 0.6 * BASELINE_BYTES_PER_SITE, (
        f"{per_site:.2f} bytes/site is not materially below the "
        f"{BASELINE_BYTES_PER_SITE} bytes/site the kernel used before the "
        "2026-09-22 optimization round")


@pytest.mark.parametrize("n", sorted(A40_DIGESTS))
def test_final_state_digest_matches_real_a40_hardware(n):
    fields = _build_host(n)
    for tick in range(TICKS_TOTAL):
        fields = _step(n, tick, fields)[:5]
    digest = hashlib.sha256()
    for field in fields:
        digest.update(np.ascontiguousarray(field).tobytes())
    assert digest.hexdigest()[:16] == A40_DIGESTS[n], (
        f"{n}x{n} final state no longer matches the digest recorded on a "
        "real A40 in RUNPOD_SCALE_RECEIPT_2026-09-22.md: aeth01.v1 "
        "semantics changed (SEMANTIC_PARITY_FAILURE)")
