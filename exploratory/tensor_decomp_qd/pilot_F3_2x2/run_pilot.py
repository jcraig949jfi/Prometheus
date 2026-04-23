"""Orchestrator for 2x2 matmul over F_3 pilot."""
from __future__ import annotations
import sys
import time
from collections import defaultdict

from .test_gauge import run_all as run_unit_tests
from .map_elites import run_evolution
from .descriptors import RANK_MIN_THEORY


def main():
    run_unit_tests()

    print("\n" + "=" * 72)
    print("  F_3 2x2 MAP-Elites (3 reseeds)")
    print("=" * 72)
    archives = []
    for seed in range(3):
        print(f"\n--- Reseed {seed+1}/3 ---")
        t0 = time.time()
        a = run_evolution(n_generations=2000, population_size=50, seed=seed, verbose=True)
        print(f"  total time: {time.time()-t0:.1f}s")
        archives.append(a)

    # Report
    print("\n" + "=" * 72)
    print("  PILOT REPORT")
    print("=" * 72)
    for i, a in enumerate(archives):
        print(f"\n[Archive {i+1}]")
        for line in a.summary_lines():
            print(f"  {line}")

    # Forbidden-rank check.
    print(f"\n[Check] Forbidden rank cells (rank < {RANK_MIN_THEORY}: Hopcroft-Kerr bound)")
    any_forbidden = False
    for i, a in enumerate(archives):
        for cell in a.cells:
            if cell[0] < RANK_MIN_THEORY:
                print(f"  VIOLATION: archive {i+1} cell {cell}")
                any_forbidden = True
    if not any_forbidden:
        print(f"  OK: all archives respect rank >= {RANK_MIN_THEORY}")

    # Orbit counts.
    rank_orbits = defaultdict(set)
    for a in archives:
        for cell, orbits in a.orbit_set.items():
            rank_orbits[cell[0]].update(orbits)
    print("\n[Check] Unique orbits per rank (union across reseeds)")
    for r in sorted(rank_orbits):
        print(f"  rank {r}: {len(rank_orbits[r])} orbits")

    # Diagnose outcome.
    min_rank = min((c[0] for a in archives for c in a.cells), default=None)
    max_orbits_rank_7 = len(rank_orbits.get(7, set()))
    print("\n[Diagnosis]")
    if any_forbidden:
        print("  OUTCOME C — forbidden cells occupied")
    elif min_rank == 7 and max_orbits_rank_7 > 1:
        print("  OUTCOME A — multiple rank-7 orbits found")
    elif min_rank == 7:
        print("  OUTCOME B1 — single rank-7 orbit (essentially unique under gauge)")
    else:
        print(f"  OUTCOME unclear — min rank {min_rank}")


if __name__ == "__main__":
    main()
