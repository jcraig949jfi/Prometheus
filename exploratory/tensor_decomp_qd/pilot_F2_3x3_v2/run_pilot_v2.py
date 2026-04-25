"""
Full pilot orchestrator for v2 (4-to-3 flip-graph moves).

Sequence:
  1. canonicalizer unit tests (re-use v1)
  2. rank_3_tensor_decomp + try_reduce_4_to_3 unit tests (v2)
  3. quadruple scan over Laderman: count reducible (true rank <= 3)
  4. MAP-Elites v2 (3 reseeds x 500 gens x pop 30)
  5. report

Run: python -m exploratory.tensor_decomp_qd.pilot_F2_3x3_v2.run_pilot_v2
"""
from __future__ import annotations
import sys
import time
import itertools
import numpy as np
from collections import defaultdict

from ..pilot_F2_3x3.test_gauge import run_all as run_v1_unit_tests
from ..pilot_F2_3x3.gauge import canonicalize
from ..pilot_F2_3x3.descriptors import RANK_MIN_THEORY, NAIVE_RANK
from ..pilot_F2_3x3.known_decomps import naive_decomp, laderman_decomp
from .test_flipgraph_v2 import run_all as run_v2_unit_tests
from .quadruple_scan import main as run_quadruple_scan
from .map_elites_v2 import run_evolution_v2, ForbiddenCellViolation


def run_reseeded(n_runs=3, n_generations=500, population_size=30):
    archives = []
    counters = []
    for run_idx in range(n_runs):
        print(f"\n--- Reseed {run_idx + 1}/{n_runs} (seed={run_idx}) ---")
        arch, ctr = run_evolution_v2(
            n_generations=n_generations,
            population_size=population_size,
            seed=run_idx,
            seed_known=True,
            verbose=True,
        )
        archives.append(arch)
        counters.append(ctr)
    return archives, counters


def report(archives, counters, scan_result):
    print("\n" + "=" * 72)
    print("  3x3 PILOT v2 REPORT (with 4-to-3 moves)")
    print("=" * 72)

    naive_b = None
    A, B, C = naive_decomp()
    (_, _, _), naive_b = canonicalize(A, B, C)

    print("\n[Quadruple scan summary]")
    print(f"  total quadruples: {scan_result['n_combos']}")
    print(f"  mode-3 flattening rank distribution: {scan_result['counts_mode3']}")
    print(f"  reducible (true rank <= 3): {scan_result['counts_true']['rank<=3']}")
    print(f"  not reducible (rank >= 4): {scan_result['counts_true']['rank=4_or_more']}")

    for i, (arch, ctr) in enumerate(zip(archives, counters)):
        print(f"\n[Archive {i + 1}]")
        for line in arch.summary_lines():
            print(" ", line)
        print(f"  flip-graph fires: 3->2={ctr.n_3to2}, 2->2={ctr.n_2to2}, "
              f"4->3={ctr.n_4to3}")

    # Forbidden-cell check.
    print("\n[Check 1] Forbidden rank cells (rank < {})".format(RANK_MIN_THEORY))
    forbidden = False
    for i, arch in enumerate(archives):
        for cell in arch.cells:
            if cell[0] < RANK_MIN_THEORY:
                print(f"  VIOLATION: archive {i + 1} cell {cell}")
                forbidden = True
    if not forbidden:
        print(f"  OK: all archives respect rank >= {RANK_MIN_THEORY}")

    # Naive present.
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

    # Min rank.
    print("\n[Check 3] Minimum rank found across archives")
    min_ranks = [arch.min_rank_found() for arch in archives]
    print(f"  min ranks per archive: {min_ranks}")
    overall_min = min(m for m in min_ranks if m is not None)
    print(f"  overall min rank: {overall_min}")

    # Outcome diagnosis.
    print("\n[Diagnosis]")
    if forbidden:
        print("  OUTCOME C — forbidden cells occupied (canonicalizer bug)")
        return 'C'
    if not naive_found_all:
        print("  OUTCOME C — naive rank-27 not rediscovered in all runs")
        return 'C'

    n_reducible = scan_result['counts_true']['rank<=3']
    if n_reducible == 0 and overall_min >= 23:
        print("  OUTCOME B1 — Laderman is structurally isolated under 4-to-3 moves over F_2.")
        print("  No quadruple of Laderman columns has true tensor rank <= 3 over F_2.")
        print("  This is a STRONGER no-go result than v1's: even the larger 4-to-3")
        print("  move-class cannot escape the Laderman orbit, and not for tuning")
        print("  reasons but because the necessary algebraic patterns don't exist.")
        return 'B1'
    if overall_min < 23:
        print(f"  OUTCOME A — found rank-{overall_min} decomposition; 4-to-3 moves break "
              f"Laderman isolation. (Total 4-to-3 fires: {sum(c.n_4to3 for c in counters)})")
        return 'A'
    print("  OUTCOME B — stuck at rank 23 despite reducible quadruples existing.")
    return 'B'


def main():
    t_total = time.time()

    # 1. v1 canonicalizer unit tests.
    print("=" * 72)
    print("  STEP 1: v1 canonicalizer unit tests")
    print("=" * 72)
    run_v1_unit_tests()

    # 2. v2 rank_3_tensor_decomp + try_reduce_4_to_3 unit tests.
    print("\n" + "=" * 72)
    print("  STEP 2: v2 rank_3_tensor_decomp unit tests")
    print("=" * 72)
    run_v2_unit_tests()

    # 3. Quadruple scan.
    print("\n" + "=" * 72)
    print("  STEP 3: quadruple scan over Laderman columns")
    print("=" * 72)
    scan_result = run_quadruple_scan()

    # 4. MAP-Elites v2.
    print("\n" + "=" * 72)
    print("  STEP 4: MAP-Elites v2 (3 reseeds x 500 gens x pop 30)")
    print("=" * 72)
    t0 = time.time()
    archives, counters = run_reseeded(n_runs=3, n_generations=500, population_size=30)
    print(f"\nTotal evolution time: {time.time() - t0:.1f}s")

    # 5. Report.
    outcome = report(archives, counters, scan_result)

    print(f"\nTotal pilot time: {time.time() - t_total:.1f}s")

    if outcome == 'A':
        sys.exit(0)
    elif outcome in ('B', 'B1'):
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
