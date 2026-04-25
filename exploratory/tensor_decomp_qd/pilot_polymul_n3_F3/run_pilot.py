"""Full pilot orchestrator for polymul-3 over F_3.

Run: python -m exploratory.tensor_decomp_qd.pilot_polymul_n3_F3.run_pilot
"""
from __future__ import annotations
import sys
import time
import itertools
from collections import defaultdict
import numpy as np

from .test_gauge import run_all as run_unit_tests
from .map_elites import run_evolution
from .descriptors import RANK_MIN_HARD
from .gauge import canonicalize, GAUGE_SIZE
from .core import is_polymul_decomp, P
from .known_decomps import karatsuba6_decomp, naive_decomp


def _karatsuba_canonical_bytes():
    U, V, W = karatsuba6_decomp()
    _, b = canonicalize(U, V, W)
    return b


def _naive_canonical_bytes():
    U, V, W = naive_decomp()
    _, b = canonicalize(U, V, W)
    return b


def neighborhood_probe_summary(U, V, W, n_flips_max=2, max_per_distance=20000,
                               rng_seed=0, exhaustive_2flip=True):
    """Probe k-flip neighborhoods around (U, V, W) over F_3.

    Each "flip" perturbs one entry by a random delta in {1, 2} mod 3.
    For each base position we have 2 perturbations, so there are
    C(N, k) * 2^k possible "k-flip" perturbations. We enumerate the
    position-subsets exhaustively when possible, and for each we try
    all 2^k delta-tuples.
    """
    rng = np.random.default_rng(rng_seed)
    base = (U.copy(), V.copy(), W.copy())
    sizes = (U.size, V.size, V.size if False else V.size)  # placeholder
    sizes = (U.size, V.size, W.size)
    total_bits = sum(sizes)

    (_, _, _), ref = canonicalize(*base)

    out = {}
    for k in range(1, n_flips_max + 1):
        positions_total = 1
        n = total_bits
        for ii in range(k):
            positions_total = positions_total * (n - ii) // (ii + 1)

        # Each k-position subset has (P-1)^k = 2^k delta-tuples.
        delta_count = (P - 1) ** k
        combos_total = positions_total * delta_count

        do_exhaustive = (k == 1) or (k == 2 and exhaustive_2flip)
        valid = 0
        distinct_orbits = set()
        if do_exhaustive:
            # Full enumeration of (positions, delta-tuple) pairs.
            for pos in itertools.combinations(range(total_bits), k):
                for deltas in itertools.product(range(1, P), repeat=k):
                    U2, V2, W2 = base[0].copy(), base[1].copy(), base[2].copy()
                    for p, d in zip(pos, deltas):
                        if p < sizes[0]:
                            flat = U2.reshape(-1)
                            flat[p] = (int(flat[p]) + d) % P
                        elif p < sizes[0] + sizes[1]:
                            flat = V2.reshape(-1)
                            flat[p - sizes[0]] = (int(flat[p - sizes[0]]) + d) % P
                        else:
                            flat = W2.reshape(-1)
                            flat[p - sizes[0] - sizes[1]] = \
                                (int(flat[p - sizes[0] - sizes[1]]) + d) % P
                    if is_polymul_decomp(U2, V2, W2):
                        valid += 1
                        (_, _, _), bt = canonicalize(U2, V2, W2)
                        if bt != ref:
                            distinct_orbits.add(bt)
            n_sample = combos_total
        else:
            n_sample = min(combos_total, max_per_distance)
            for trial in range(n_sample):
                pos = rng.choice(total_bits, size=k, replace=False)
                deltas = rng.integers(1, P, size=k)
                U2, V2, W2 = base[0].copy(), base[1].copy(), base[2].copy()
                for p, d in zip(pos, deltas):
                    if p < sizes[0]:
                        flat = U2.reshape(-1)
                        flat[p] = (int(flat[p]) + int(d)) % P
                    elif p < sizes[0] + sizes[1]:
                        flat = V2.reshape(-1)
                        flat[p - sizes[0]] = (int(flat[p - sizes[0]]) + int(d)) % P
                    else:
                        flat = W2.reshape(-1)
                        flat[p - sizes[0] - sizes[1]] = \
                            (int(flat[p - sizes[0] - sizes[1]]) + int(d)) % P
                if is_polymul_decomp(U2, V2, W2):
                    valid += 1
                    (_, _, _), bt = canonicalize(U2, V2, W2)
                    if bt != ref:
                        distinct_orbits.add(bt)
        out[k] = (valid, len(distinct_orbits), n_sample, combos_total)
    return out


def run_reseeded(n_runs: int = 3, n_generations: int = 1500, population_size: int = 80):
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
    print("  PILOT REPORT — polymul n=3 over F_3")
    print("=" * 72)

    kar_b = _karatsuba_canonical_bytes()
    nai_b = _naive_canonical_bytes()

    for i, a in enumerate(archives):
        print(f"\n[Archive {i + 1}]")
        for line in a.summary_lines():
            print(f"  {line}")

    print(f"\n[Check 1] Forbidden rank cells (rank < {RANK_MIN_HARD})")
    any_forbidden = False
    for i, a in enumerate(archives):
        for cell in a.cells:
            if cell[0] < RANK_MIN_HARD:
                print(f"  VIOLATION: archive {i+1} cell {cell}")
                any_forbidden = True
    if not any_forbidden:
        print(f"  OK: all archives respect rank >= {RANK_MIN_HARD}")

    # Soft-watch for rank 5 (would be a discovery).
    rank5_seen = False
    for a in archives:
        for cell in a.cells:
            if cell[0] == 5:
                rank5_seen = True
    if rank5_seen:
        print("  *** SOFT-WATCH: rank-5 decomposition found! Investigate carefully — "
              "would be unprecedented for polymul-3 over F_3.")

    print("\n[Check 2] Known seeds present in archives")
    for i, a in enumerate(archives):
        kar_found = False; nai_found = False
        for cell, info in a.cells.items():
            if info['bkey'] == kar_b:
                kar_found = True
            if info['bkey'] == nai_b:
                nai_found = True
        print(f"  archive {i+1}: Karatsuba6 found = {kar_found}, naive9 found = {nai_found}")

    print("\n[Check 3] Distinct orbits per rank (union across reseeds)")
    rank_orbits: dict[int, set] = defaultdict(set)
    for a in archives:
        for cell, orbits in a.orbit_set.items():
            rank_orbits[cell[0]].update(orbits)
    for r in sorted(rank_orbits):
        print(f"  rank {r}: {len(rank_orbits[r])} orbits")

    print("\n[Check 4] Pairwise Jaccard between archives")
    sets = [set(info['bkey'] for info in a.cells.values()) for a in archives]
    avg_jac = None
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

    print("\n[Check 5] Per-rank sparsity values per archive")
    for i, a in enumerate(archives):
        per_rank = defaultdict(set)
        for cell, info in a.cells.items():
            per_rank[cell[0]].add(round(info['sparsity'], 4))
        for r in sorted(per_rank):
            print(f"  archive {i+1}: rank-{r} distinct sparsity = {sorted(per_rank[r])}")

    print("\n[Check 6] Neighborhood probe (Karatsuba6 and naive9, distance 1 and 2 EXHAUSTIVE)")
    U, V, W = karatsuba6_decomp()
    print(f"  Karatsuba6 seed dims: U {U.shape}, V {V.shape}, W {W.shape}, "
          f"total entries = {U.size + V.size + W.size}")
    probe_kar = neighborhood_probe_summary(U, V, W, n_flips_max=2, exhaustive_2flip=True)
    print(f"  Karatsuba6 seed: {probe_kar}")
    U, V, W = naive_decomp()
    print(f"  Naive9 seed dims: U {U.shape}, V {V.shape}, W {W.shape}, "
          f"total entries = {U.size + V.size + W.size}")
    probe_nai = neighborhood_probe_summary(U, V, W, n_flips_max=2, exhaustive_2flip=True)
    print(f"  Naive9 seed:    {probe_nai}")

    print("\n[Diagnosis]")
    if any_forbidden:
        print("  OUTCOME C — forbidden cells occupied")
        return 'C'

    n_rank6_orbits = len(rank_orbits.get(6, set()))
    n_rank5_orbits = len(rank_orbits.get(5, set()))

    if rank5_seen:
        print(f"  OUTCOME A* — rank-5 decomposition discovered (would be unprecedented).")
        return 'A'

    if n_rank6_orbits == 0:
        print("  OUTCOME C — no valid rank-6 found; check seeding/canonicalizer")
        return 'C'

    if n_rank6_orbits >= 2:
        print(f"  OUTCOME A — {n_rank6_orbits} distinct rank-6 orbits found across reseeds. "
              "Polymul over F_3 admits non-trivial QD diversity at the optimum.")
        return 'A'

    kar_2flip_distinct = probe_kar.get(2, (0, 0, 0, 0))[1]

    if avg_jac is not None and avg_jac < 0.5:
        print("  OUTCOME B2 — single rank-6 orbit but reseed disagreement at higher ranks.")
        return 'B2'
    print("  OUTCOME B1 — single rank-6 orbit reproduced across all reseeds.")
    if kar_2flip_distinct == 0:
        print(f"           Karatsuba6 is Hamming-isolated under 2-flip (consistent with B1-strong).")
    else:
        print(f"           Karatsuba6 has {kar_2flip_distinct} 2-flip neighbors hitting other orbits.")
    return 'B1'


def main():
    run_unit_tests()

    print("\n" + "=" * 72)
    print("  MAP-Elites reseeded runs (3 reseeds x 1500 generations each)")
    print("=" * 72)
    t0 = time.time()
    archives = run_reseeded(n_runs=3, n_generations=1500, population_size=80)
    print(f"\nTotal evolution time: {time.time() - t0:.1f}s")

    outcome = report(archives)
    if outcome == 'A':
        sys.exit(0)
    elif outcome.startswith('B'):
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
