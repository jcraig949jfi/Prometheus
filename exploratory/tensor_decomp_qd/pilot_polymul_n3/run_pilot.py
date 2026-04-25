"""Full pilot orchestrator: unit tests -> reseeded MAP-Elites -> diagnostics.

Run: python -m exploratory.tensor_decomp_qd.pilot_polymul_n3.run_pilot

Outcome diagnosis (mirrors sibling pilots):
  A    — multiple distinct rank-6 orbits, real Pareto fronts, stable canonicalization
  B1   — single rank-6 orbit found, canonicalization stable, but no diversity at low rank
  B2   — multiple rank-6 orbits across reseeds but reseed-disagreement (looser than B1)
  C    — forbidden cells occupied OR fundamental canonicalizer instability
"""
from __future__ import annotations
import sys
import time
from collections import defaultdict

from .test_gauge import run_all as run_unit_tests
from .map_elites import run_evolution
from .descriptors import RANK_MIN_HARD
from .gauge import canonicalize, GAUGE_SIZE
from .known_decomps import karatsuba6_decomp, naive_decomp


def _karatsuba_canonical_bytes():
    U, V, W = karatsuba6_decomp()
    _, b = canonicalize(U, V, W)
    return b


def _naive_canonical_bytes():
    U, V, W = naive_decomp()
    _, b = canonicalize(U, V, W)
    return b


def neighborhood_probe_summary(U, V, W, n_flips_max=3, max_per_distance=20000, rng_seed=0):
    """Sample bit-flip neighborhoods around (U, V, W) and report how many
    are valid polymul decomps (and how many fall in distinct orbits).
    """
    import numpy as np
    from itertools import combinations
    from .core import is_polymul_decomp
    from .gauge import canonicalize as canon

    rng = np.random.default_rng(rng_seed)
    base = (U.copy(), V.copy(), W.copy())
    sizes = (U.size, V.size, W.size)
    total_bits = sum(sizes)

    (_, _, _), ref = canon(*base)

    out = {}
    for k in range(1, n_flips_max + 1):
        # Enumerate or sample combinations of k bit positions.
        combos_total = 1
        n = total_bits
        for ii in range(k):
            combos_total = combos_total * (n - ii) // (ii + 1)
        # Sampling.
        n_sample = min(combos_total, max_per_distance)
        valid = 0
        distinct_orbits = set()
        for trial in range(n_sample):
            # pick k distinct positions
            pos = rng.choice(total_bits, size=k, replace=False)
            U2, V2, W2 = base[0].copy(), base[1].copy(), base[2].copy()
            for p in pos:
                if p < sizes[0]:
                    flat = U2.reshape(-1)
                    flat[p] ^= 1
                elif p < sizes[0] + sizes[1]:
                    flat = V2.reshape(-1)
                    flat[p - sizes[0]] ^= 1
                else:
                    flat = W2.reshape(-1)
                    flat[p - sizes[0] - sizes[1]] ^= 1
            if is_polymul_decomp(U2, V2, W2):
                valid += 1
                (_, _, _), bt = canon(U2, V2, W2)
                if bt != ref:
                    distinct_orbits.add(bt)
        out[k] = (valid, len(distinct_orbits), n_sample, combos_total)
    return out


def run_reseeded(n_runs: int = 3, n_generations: int = 1000, population_size: int = 50):
    archives = []
    for run_idx in range(n_runs):
        print(f"\n--- Reseed {run_idx + 1}/{n_runs} (seed={run_idx}) ---")
        t0 = time.time()
        a = run_evolution(
            n_generations=n_generations,
            population_size=population_size,
            seed=run_idx,
            seed_known=True,
            verbose=True,
        )
        print(f"  total time: {time.time() - t0:.1f}s")
        archives.append(a)
    return archives


def report(archives):
    print("\n" + "=" * 72)
    print("  PILOT REPORT")
    print("=" * 72)

    kar_b = _karatsuba_canonical_bytes()
    nai_b = _naive_canonical_bytes()

    for i, a in enumerate(archives):
        print(f"\n[Archive {i + 1}]")
        for line in a.summary_lines():
            print(f"  {line}")

    # --- Check 1: forbidden-rank cells ---
    print(f"\n[Check 1] Forbidden rank cells (rank < {RANK_MIN_HARD})")
    any_forbidden = False
    for i, a in enumerate(archives):
        for cell in a.cells:
            if cell[0] < RANK_MIN_HARD:
                print(f"  VIOLATION: archive {i+1} cell {cell}")
                any_forbidden = True
    if not any_forbidden:
        print(f"  OK: all archives respect rank >= {RANK_MIN_HARD}")

    # --- Check 2: known seeds present ---
    print("\n[Check 2] Known seeds present in archives")
    for i, a in enumerate(archives):
        kar_found = False; nai_found = False
        for cell, info in a.cells.items():
            if info['bkey'] == kar_b:
                kar_found = True
            if info['bkey'] == nai_b:
                nai_found = True
        print(f"  archive {i+1}: Karatsuba found = {kar_found}, naive found = {nai_found}")

    # --- Check 3: per-rank orbit counts ---
    print("\n[Check 3] Distinct orbits per rank (union across reseeds)")
    rank_orbits: dict[int, set] = defaultdict(set)
    for a in archives:
        for cell, orbits in a.orbit_set.items():
            rank_orbits[cell[0]].update(orbits)
    for r in sorted(rank_orbits):
        print(f"  rank {r}: {len(rank_orbits[r])} orbits")

    # --- Check 4: pairwise reseed agreement ---
    print("\n[Check 4] Pairwise Jaccard between archives' canonical sets")
    sets = [set(info['bkey'] for info in a.cells.values()) for a in archives]
    if len(sets) >= 2:
        jaccards = []
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                inter = sets[i] & sets[j]
                union = sets[i] | sets[j]
                jac = len(inter) / max(1, len(union))
                jaccards.append(jac)
                print(f"  archives {i+1},{j+1}: |inter|={len(inter)}, |union|={len(union)}, "
                      f"Jaccard={jac:.3f}")
        avg_jac = sum(jaccards) / len(jaccards)
        print(f"  avg Jaccard = {avg_jac:.3f}")
    else:
        avg_jac = None

    # --- Check 5: rank-6 sparsity / Pareto ---
    print("\n[Check 5] Rank-6 sparsity values (per archive)")
    for i, a in enumerate(archives):
        sparsities = set()
        for cell, info in a.cells.items():
            if cell[0] == 6:
                sparsities.add(round(info['sparsity'], 4))
        print(f"  archive {i+1}: rank-6 distinct sparsity = {sorted(sparsities)}")

    # --- Check 6: neighborhood probe from each seed ---
    print("\n[Check 6] Neighborhood probe (Karatsuba and naive, distance 1 and 2)")
    U, V, W = karatsuba6_decomp()
    probe_kar = neighborhood_probe_summary(U, V, W, n_flips_max=2, max_per_distance=5000)
    print(f"  Karatsuba seed: {probe_kar}")
    U, V, W = naive_decomp()
    probe_nai = neighborhood_probe_summary(U, V, W, n_flips_max=2, max_per_distance=5000)
    print(f"  Naive seed:     {probe_nai}")

    # --- Outcome diagnosis ---
    print("\n[Diagnosis]")
    if any_forbidden:
        print("  OUTCOME C — forbidden cells occupied")
        return 'C'

    n_rank6_orbits = len(rank_orbits.get(6, set()))
    if n_rank6_orbits == 0:
        print("  OUTCOME C — no valid rank-6 found; check seeding/canonicalizer")
        return 'C'

    if n_rank6_orbits >= 2:
        print(f"  OUTCOME A — {n_rank6_orbits} distinct rank-6 orbits found across reseeds. "
              f"Polymul tensor admits non-trivial QD diversity at the optimum.")
        return 'A'

    if avg_jac is not None and avg_jac < 0.5:
        print("  OUTCOME B2 — single rank-6 orbit but reseed disagreement at higher ranks. "
              "Canonicalizer holds; exploration is stochastic.")
        return 'B2'
    print("  OUTCOME B1 — single rank-6 orbit reproduced across all reseeds. "
          "Canonicalization stable; the rank-6 layer is essentially unique under our gauge "
          "and mutation repertoire. Tensor smaller / less saturated than 2x2 matmul "
          "(orbit space at the optimum is still trivial).")
    return 'B1'


def main():
    # 1. Unit tests (hard gate).
    run_unit_tests()

    # 2. Reseeded MAP-Elites.
    print("\n" + "=" * 72)
    print("  MAP-Elites reseeded runs (3 reseeds x 5000 generations each)")
    print("=" * 72)
    t0 = time.time()
    archives = run_reseeded(n_runs=3, n_generations=5000, population_size=80)
    print(f"\nTotal evolution time: {time.time() - t0:.1f}s")

    # 3. Diagnose.
    outcome = report(archives)

    # 4. Exit code by outcome.
    if outcome == 'A':
        sys.exit(0)
    elif outcome.startswith('B'):
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
