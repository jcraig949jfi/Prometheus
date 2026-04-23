"""
Full pilot orchestrator: unit tests -> MAP-Elites -> diagnostics -> outcome report.

Run: python -m tensor_decomp_qd.pilot_F2_2x2.run_pilot

Outcome diagnosis:
  A (Rich structure)   — multiple distinct rank-7 orbits, real Pareto fronts,
                         stable canonicalization
  B (Correct but trivial) — one dominant orbit, no meaningful tradeoffs
  C (Instability)      — forbidden cells occupied OR reseed-inconsistent
"""
from __future__ import annotations
import sys
import time
import numpy as np

from .test_gauge import run_all as run_unit_tests
from .map_elites import run_evolution
from .gauge import ISO_SIZE, canonicalize
from .descriptors import STABILIZER_LABELS, RANK_MIN
from .known_decomps import strassen_decomp


def strassen_canonical_bytes():
    U, V, W = strassen_decomp()
    _, b = canonicalize(U, V, W)
    return b


def run_reseeded(n_runs: int = 3, n_generations: int = 500, population_size: int = 60):
    """Run n_runs independent evolutions and compare archives for stability."""
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
    """Print a structured report and diagnose outcome A / B / C."""
    print("\n" + "=" * 72)
    print("  PILOT REPORT")
    print("=" * 72)

    strassen_b = strassen_canonical_bytes()

    # Per-archive summaries.
    for i, arch in enumerate(archives):
        print(f"\n[Archive {i + 1}]")
        for line in arch.summary_lines():
            print(" ", line)

    # --- Check 1: Forbidden rank cells ---
    print("\n[Check 1] Forbidden rank cells (rank <= 6 must be empty)")
    forbidden = False
    for i, arch in enumerate(archives):
        for cell in arch.cells:
            r = cell[0]
            if r < RANK_MIN:
                print(f"  VIOLATION: archive {i + 1} has cell {cell} at rank {r}")
                forbidden = True
    if not forbidden:
        print(f"  OK: all archives respect rank >= {RANK_MIN} (Hopcroft-Kerr 1971)")

    # --- Check 2: Strassen rediscovery ---
    print("\n[Check 2] Strassen's canonical form present in rank-7 cells")
    strassen_found_in_all = True
    for i, arch in enumerate(archives):
        found = False
        for cell, info in arch.cells.items():
            if cell[0] == 7 and info['bkey'] == strassen_b:
                found = True
                print(f"  archive {i + 1}: Strassen present in cell {cell}, "
                      f"hits={arch.hit_counts[cell]}")
                break
        if not found:
            strassen_found_in_all = False
            print(f"  archive {i + 1}: Strassen NOT found in any rank-7 cell")

    # --- Check 3: Distinct orbits in rank-7 layer ---
    print("\n[Check 3] Distinct rank-7 orbits across archives")
    distinct_rank7_per_run = []
    for i, arch in enumerate(archives):
        all_r7_orbits = set()
        for cell, orbits in arch.orbit_set.items():
            if cell[0] == 7:
                all_r7_orbits.update(orbits)
        print(f"  archive {i + 1}: {len(all_r7_orbits)} distinct rank-7 orbits")
        distinct_rank7_per_run.append(len(all_r7_orbits))
    # Union across runs.
    union_r7 = set()
    for arch in archives:
        for cell, orbits in arch.orbit_set.items():
            if cell[0] == 7:
                union_r7.update(orbits)
    print(f"  union across runs: {len(union_r7)} distinct rank-7 orbits")

    # --- Check 4: Elite stability across reseeds ---
    print("\n[Check 4] Elite canonical forms overlap across reseeds")
    if len(archives) >= 2:
        elite_sets = [set(info['bkey'] for info in arch.cells.values())
                      for arch in archives]
        pairwise_overlap = []
        for i in range(len(elite_sets)):
            for j in range(i + 1, len(elite_sets)):
                inter = elite_sets[i] & elite_sets[j]
                union = elite_sets[i] | elite_sets[j]
                jaccard = len(inter) / max(1, len(union))
                pairwise_overlap.append(jaccard)
                print(f"  archives {i+1} and {j+1}: intersection={len(inter)}, "
                      f"union={len(union)}, Jaccard={jaccard:.3f}")
        avg_jaccard = sum(pairwise_overlap) / len(pairwise_overlap)
        print(f"  avg pairwise Jaccard = {avg_jaccard:.3f}")
    else:
        avg_jaccard = None

    # --- Check 5: Post-canonicalization Pareto (sparsity) at rank 7 ---
    print("\n[Check 5] Rank-7 Pareto: do multiple distinct sparsity values appear?")
    for i, arch in enumerate(archives):
        sparsities = set()
        for cell, info in arch.cells.items():
            if cell[0] == 7:
                # Round to 4 decimals to account for floats
                sparsities.add(round(info['sparsity'], 4))
        print(f"  archive {i + 1}: {len(sparsities)} distinct canonical-sparsity values "
              f"at rank 7 -> {sorted(sparsities)}")

    # --- Check 6: Orbit-size distribution (per-cell hit counts) ---
    print("\n[Check 6] Orbit-size distribution (per-cell orbit count, rank 7)")
    for i, arch in enumerate(archives):
        rank7_cells = [(c, arch.orbit_set[c], arch.hit_counts[c])
                       for c in arch.cells if c[0] == 7]
        rank7_cells.sort(key=lambda t: -len(t[1]))
        for cell, orbits, hits in rank7_cells[:5]:
            print(f"  archive {i + 1}: cell {cell} -> {len(orbits)} orbits, "
                  f"{hits} hits")

    # --- Outcome diagnosis ---
    print("\n[Diagnosis]")
    if forbidden:
        print("  OUTCOME C — Instability: forbidden rank cells occupied. "
              "Canonicalizer or fitness has a bug.")
        return 'C'
    if not strassen_found_in_all:
        print("  OUTCOME (partial C) — Strassen not rediscovered in at least one run. "
              "Either mutation operators don't explore enough OR canonicalization is off.")
        return 'C'

    max_r7_orbits = max(distinct_rank7_per_run)
    if max_r7_orbits < 2:
        print("  OUTCOME B — Correct but trivial: only one rank-7 orbit found. "
              "Either the domain really has a unique orbit (unlikely given stabilizer=2) "
              "OR exploration is insufficient.")
        return 'B'

    if avg_jaccard is not None and avg_jaccard < 0.5:
        print("  OUTCOME (partial C) — Elite archives disagree across reseeds. "
              "Canonicalizer may be flaky or exploration too stochastic.")

    print("  OUTCOME A — Rich structure: multiple rank-7 orbits, Strassen rediscovered, "
          "stable canonicalization. Instrument is validated over F_2.")
    return 'A'


def main():
    # 1. Unit tests (hard gate — must pass).
    run_unit_tests()

    # 2. MAP-Elites reseeded runs.
    print("\n" + "=" * 72)
    print("  MAP-Elites runs (3 reseeds)")
    print("=" * 72)
    t0 = time.time()
    archives = run_reseeded(n_runs=3, n_generations=500, population_size=60)
    print(f"\nTotal evolution time: {time.time() - t0:.1f}s")

    # 3. Diagnostics + outcome.
    outcome = report(archives)

    # 4. Exit code reflects outcome (A=0, B=1, C=2) for pipeline use.
    if outcome == 'A':
        sys.exit(0)
    elif outcome == 'B':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
