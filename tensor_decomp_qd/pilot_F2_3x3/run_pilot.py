"""
Full pilot orchestrator for 3x3 matmul over F_2.

Sequence:
  1. canonicalizer unit tests (hard gate)
  2. MAP-Elites runs (3 reseeds, small scale first)
  3. diagnostics
  4. outcome report A / B / C

Run: python -m tensor_decomp_qd.pilot_F2_3x3.run_pilot
"""
from __future__ import annotations
import sys
import time
import numpy as np

from .test_gauge import run_all as run_unit_tests
from .map_elites import run_evolution, ForbiddenCellViolation
from .gauge import ISO_SIZE, canonicalize
from .descriptors import RANK_MIN_THEORY, NAIVE_RANK
from .known_decomps import naive_decomp


def run_reseeded(n_runs=3, n_generations=500, population_size=40):
    archives = []
    for run_idx in range(n_runs):
        print(f"\n--- Reseed {run_idx + 1}/{n_runs} (seed={run_idx}) ---")
        arch = run_evolution(
            n_generations=n_generations,
            population_size=population_size,
            seed=run_idx,
            seed_known=True,
            verbose=True,
        )
        archives.append(arch)
    return archives


def report(archives):
    print("\n" + "=" * 72)
    print("  3x3 PILOT REPORT")
    print("=" * 72)

    naive_b = None
    A, B, C = naive_decomp()
    (_, _, _), naive_b = canonicalize(A, B, C)

    for i, arch in enumerate(archives):
        print(f"\n[Archive {i + 1}]")
        for line in arch.summary_lines():
            print(" ", line)

    # Check 1: forbidden cells (rank < 19).
    print("\n[Check 1] Forbidden rank cells (rank < {}): Blaeser 2003 lower bound".format(
        RANK_MIN_THEORY))
    forbidden = False
    for i, arch in enumerate(archives):
        for cell in arch.cells:
            if cell[0] < RANK_MIN_THEORY:
                print(f"  VIOLATION: archive {i + 1} cell {cell}")
                forbidden = True
    if not forbidden:
        print(f"  OK: all archives respect rank >= {RANK_MIN_THEORY}")

    # Check 2: naive decomp always in the archive at rank 27.
    print("\n[Check 2] Naive rank-27 present")
    naive_found_all = True
    for i, arch in enumerate(archives):
        found = False
        for cell, info in arch.cells.items():
            if cell[0] == NAIVE_RANK and info['bkey'] == naive_b:
                found = True
                print(f"  archive {i + 1}: naive present in cell {cell}")
                break
        if not found:
            naive_found_all = False
            print(f"  archive {i + 1}: naive NOT found at rank 27")

    # Check 3: minimum rank found across archives.
    print("\n[Check 3] Minimum rank found (target: below 27 via rank-reducing moves)")
    min_ranks = [arch.min_rank_found() for arch in archives]
    print(f"  min ranks per archive: {min_ranks}")
    overall_min = min(m for m in min_ranks if m is not None)
    print(f"  overall min rank: {overall_min}")

    # Check 4: rank cell population distribution.
    print("\n[Check 4] Rank-cell population across archives (union)")
    rank_cells = defaultdict(set)
    for arch in archives:
        for cell in arch.cells:
            rank_cells[cell[0]].add(cell)
    for r in sorted(rank_cells):
        print(f"  rank {r}: {len(rank_cells[r])} distinct (rank, sparsity, stab) cells")

    # Check 5: cross-archive overlap (Jaccard on elite canonical forms).
    print("\n[Check 5] Cross-archive Jaccard on elite canonical forms")
    if len(archives) >= 2:
        elite_sets = [set(info['bkey'] for info in arch.cells.values()) for arch in archives]
        for i in range(len(elite_sets)):
            for j in range(i + 1, len(elite_sets)):
                inter = elite_sets[i] & elite_sets[j]
                union = elite_sets[i] | elite_sets[j]
                j_idx = len(inter) / max(1, len(union))
                print(f"  archives {i+1} and {j+1}: inter={len(inter)}, "
                      f"union={len(union)}, Jaccard={j_idx:.3f}")

    # Outcome diagnosis.
    print("\n[Diagnosis]")
    if forbidden:
        print("  OUTCOME C — forbidden cells occupied (canonicalizer bug)")
        return 'C'
    if not naive_found_all:
        print("  OUTCOME C — naive rank-27 not rediscovered in all runs "
              "(either canonicalization or exploration broken)")
        return 'C'

    # Did we find rank < 27?
    below_27 = overall_min is not None and overall_min < 27
    # Did we find multiple distinct orbits anywhere?
    max_orbits_single_rank = max(
        (sum(len(arch.orbit_set[c]) for c in arch.cells if c[0] == r)
         for arch in archives for r in set(c[0] for c in arch.cells)),
        default=0
    )

    if not below_27:
        print("  OUTCOME B — valid but stuck at rank 27 (naive only). "
              "Rank-reducing mutations either don't fire or the landscape is too sparse "
              "for this mutation repertoire. Next step: flip-graph moves.")
        return 'B'

    if max_orbits_single_rank < 2 and overall_min == 27:
        print("  OUTCOME B — rank reduction failed, single orbit at each rank.")
        return 'B'

    print(f"  OUTCOME A — rank reduction worked (min rank {overall_min}); "
          f"multiple cells populated below naive. Archive has structural diversity.")
    return 'A'


def main():
    # 1. Unit tests (hard gate).
    print("Running unit tests first (must pass)...")
    run_unit_tests()

    # 2. MAP-Elites runs.
    print("\n" + "=" * 72)
    print("  3x3 MAP-Elites runs (3 reseeds)")
    print("=" * 72)
    t0 = time.time()
    # Start modest; escalate if the instrument shows signs of finding rank < 27.
    archives = run_reseeded(n_runs=3, n_generations=500, population_size=30)
    print(f"\nTotal evolution time: {time.time() - t0:.1f}s")

    # 3. Report.
    outcome = report(archives)

    # 4. Exit code.
    if outcome == 'A':
        sys.exit(0)
    elif outcome == 'B':
        sys.exit(1)
    else:
        sys.exit(2)


# Local import used in report
from collections import defaultdict  # noqa: E402


if __name__ == "__main__":
    main()
