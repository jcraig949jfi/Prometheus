"""Orchestrator for 3x3 matmul over Q (small-int-bounded) pilot.

Sequence:
  1. Run unit tests (gauge-invariance must hold under signed permutations).
  2. Compute invariant tuples for Laderman + cyclic-conjugate variants.
     Whether they differ is the OUTCOME-A test.
  3. Run MAP-Elites with invariant-tuple cell key (3 reseeds x 500 gens).
  4. Report:
     - distinct invariant-tuple cells per rank (especially rank 23)
     - whether multiple rank-23 cells were found (outcome A vs B)
"""
from __future__ import annotations
import sys
import time
from collections import defaultdict

from .test_gauge import run_all as run_unit_tests
from .map_elites import run_evolution
from .descriptors import RANK_MIN_THEORY, NAIVE_RANK
from .known_decomps import (
    laderman_decomp, smirnov_variant_decomp, smirnov_variant2_decomp,
    laderman_transpose_decomp,
)
from .descriptors import invariant_tuple, invariant_tuple_hash


def main():
    print("\n" + "=" * 72)
    print("  Q 3x3 pilot — invariant-tuple-keyed MAP-Elites (small-int-bounded Q)")
    print("=" * 72)

    run_unit_tests()

    # -------------------------------------------------------------------------
    # Outcome-A test: enumerate known rank-23 variants and compare invariant
    # tuples. The cyclic-conjugate of Laderman uses the matmul tensor's Z_3
    # AUTOMORPHISM (slot-swap) which is NOT in GL_3(Q)^3 — so a DIFFERENT
    # invariant tuple here means "distinct GL_3(Q)^3 orbit", which IS outcome A.
    # -------------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("  Outcome-A diagnostic: invariant tuples of known rank-23 variants")
    print("=" * 72)

    variants = [
        ("Laderman 1976", laderman_decomp),
        ("Laderman cyclic-conj-1", smirnov_variant_decomp),
        ("Laderman cyclic-conj-2", smirnov_variant2_decomp),
        ("Laderman transpose-conj", laderman_transpose_decomp),
    ]
    hashes = {}
    for name, fn in variants:
        A, B, C = fn()
        tup = invariant_tuple(A, B, C, include_triples=True)
        h = invariant_tuple_hash(tup)
        hashes[name] = h
        print(f"  {name:30s}  rank={tup[0]}  hash={h}")
    distinct = len(set(hashes.values()))
    print(f"\n  Distinct rank-23 invariant tuples: {distinct}")
    if distinct > 1:
        print(f"  -> OUTCOME A (initial diagnosis): multiple rank-23 GL_3(Q)^3 orbits.")
    else:
        print(f"  -> OUTCOME B (initial diagnosis): all variants share invariant tuple.")

    # -------------------------------------------------------------------------
    # MAP-Elites with all four variants as seeds.
    # -------------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("  MAP-Elites (3 reseeds x 500 gens x pop 30)")
    print("=" * 72)

    archives = []
    for seed in range(3):
        print(f"\n--- Reseed {seed+1}/3 ---")
        t0 = time.time()
        a = run_evolution(n_generations=500, population_size=30, seed=seed,
                          verbose=True, include_triples=True,
                          seed_smirnov=True)
        print(f"  total time: {time.time()-t0:.1f}s")
        archives.append(a)

    # -------------------------------------------------------------------------
    # Final report.
    # -------------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("  PILOT REPORT")
    print("=" * 72)

    for i, a in enumerate(archives):
        print(f"\n[Archive {i+1}]")
        for line in a.summary_lines():
            print(f"  {line}")

    # Forbidden-rank check.
    print(f"\n[Check] Forbidden rank cells (rank < {RANK_MIN_THEORY}: Blaeser bound)")
    any_forbidden = False
    for i, a in enumerate(archives):
        for cell in a.cells:
            if cell[0] < RANK_MIN_THEORY:
                print(f"  VIOLATION: archive {i+1} cell {cell}")
                any_forbidden = True
    if not any_forbidden:
        print(f"  OK: all archives respect rank >= {RANK_MIN_THEORY}")

    # Distinct invariant-tuple counts per rank (union across reseeds).
    rank_tup_hashes = defaultdict(set)
    for a in archives:
        for cell, info in a.cells.items():
            rank_tup_hashes[cell[0]].add(info['hash'])
    print("\n[Check] Distinct invariant-tuple hashes per rank (union across reseeds)")
    for r in sorted(rank_tup_hashes):
        n = len(rank_tup_hashes[r])
        print(f"  rank {r:2d}: {n:3d} distinct invariant-tuple class(es)")

    # Diagnose outcome.
    min_rank = min((c[0] for a in archives for c in a.cells), default=None)
    rank_23_count = len(rank_tup_hashes.get(23, set()))
    rank_27_count = len(rank_tup_hashes.get(27, set()))
    print("\n[Diagnosis]")
    print(f"  rank-23 invariant-tuple classes found: {rank_23_count}")
    print(f"  rank-27 invariant-tuple classes found: {rank_27_count}")
    if any_forbidden:
        print("  OUTCOME C — forbidden cells occupied (canonicalizer/bound bug)")
    elif rank_23_count > 1:
        print("  OUTCOME A — multiple rank-23 invariant-tuple classes found")
    elif rank_23_count == 1:
        print("  OUTCOME B — single rank-23 class (Laderman seed) reached")
    elif min_rank is not None and min_rank > 23:
        print(f"  OUTCOME B-1 — rank 23 not reached (min rank: {min_rank})")
    else:
        print(f"  OUTCOME unclear — min rank {min_rank}")


if __name__ == "__main__":
    main()
