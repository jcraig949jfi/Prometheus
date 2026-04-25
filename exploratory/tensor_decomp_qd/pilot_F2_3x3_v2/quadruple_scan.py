"""
Scan all C(23, 4) = 8855 quadruples of Laderman columns.

For each quadruple (i, j, k, l):
  - Compute T_ijkl = sum of 4 rank-1 contributions.
  - Compute mode-1, mode-2, mode-3 flattening ranks.
  - If mode-3 rank <= 3, attempt true rank-3 decomposition.
  - Record outcome.

Outcome buckets:
  - 'rank0..rank2': trivial (collapses to a smaller tensor).
  - 'rank3': true tensor rank exactly 3 over F_2 (rank reduction possible).
  - 'rank4': true tensor rank exactly 4 (no reduction; rank stays at 4).
  - 'mode3_le3_but_true_rank>3': mode-3 flattening rank <= 3 but no
    rank-3 decomp exists (rare; means another mode is the bottleneck).

Acceptance criterion: count how many quadruples are reducible (true rank <= 3).
If any -> we can break Laderman isolation under 4-to-3 moves.

Run: python -m exploratory.tensor_decomp_qd.pilot_F2_3x3_v2.quadruple_scan
"""
from __future__ import annotations
import itertools
import time
import numpy as np

from ..pilot_F2_3x3.known_decomps import laderman_decomp
from ..pilot_F2_3x3.core import DIM
from .flipgraph_v2 import (
    rank_F2, rank_3_tensor_decomp, compute_T_sum,
)


def mode_flattening_ranks(T):
    """Return (rank_mode1, rank_mode2, rank_mode3) over F_2.

    Mode-k flattening: matricize keeping mode-k as rows, others combined as cols.
    """
    M1 = T.reshape(DIM, DIM * DIM)        # mode-1
    M2 = T.transpose(1, 0, 2).reshape(DIM, DIM * DIM)
    M3 = T.transpose(2, 0, 1).reshape(DIM, DIM * DIM)
    return rank_F2(M1), rank_F2(M2), rank_F2(M3)


def main():
    print("Loading Laderman decomposition...")
    A, B, C = laderman_decomp()
    r = A.shape[1]
    print(f"  rank = {r}")

    n_combos = 0
    counts_mode_max = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}   # max flattening rank
    counts_mode3 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}      # mode-3 only
    counts_true = {'rank<=3': 0, 'rank=4_or_more': 0}
    reducible_quadruples = []

    t0 = time.time()
    quads = list(itertools.combinations(range(r), 4))
    print(f"Scanning {len(quads)} quadruples...")
    for n, (i, j, k, l) in enumerate(quads):
        n_combos += 1
        T = compute_T_sum(A, B, C, [i, j, k, l])
        m1, m2, m3 = mode_flattening_ranks(T)
        max_mode = max(m1, m2, m3)
        if max_mode <= 4:
            counts_mode_max[max_mode] = counts_mode_max.get(max_mode, 0) + 1
        else:
            counts_mode_max[4] += 1   # cap-bin
        # mode-3 only:
        m3_bin = min(m3, 4)
        counts_mode3[m3_bin] = counts_mode3.get(m3_bin, 0) + 1

        # If mode-3 flattening is <=3, true tensor rank could be <=3. Try.
        if m3 <= 3:
            decomp = rank_3_tensor_decomp(T)
            if decomp is not None:
                counts_true['rank<=3'] += 1
                reducible_quadruples.append((i, j, k, l, len(decomp)))
            else:
                counts_true['rank=4_or_more'] += 1   # true rank > 3 even though mode-3 <= 3
        else:
            counts_true['rank=4_or_more'] += 1

        if (n + 1) % 1000 == 0:
            print(f"  {n+1}/{len(quads)} done ({time.time()-t0:.1f}s); "
                  f"reducible so far: {counts_true['rank<=3']}")

    elapsed = time.time() - t0
    print(f"\nScan complete in {elapsed:.1f}s")
    print(f"  total quadruples scanned: {n_combos}")
    print()
    print("Maximum flattening rank distribution (max(rank(M_1), rank(M_2), rank(M_3))):")
    for r_val, cnt in sorted(counts_mode_max.items()):
        print(f"  max-mode rank {r_val}: {cnt:5d}")
    print()
    print("Mode-3 flattening rank distribution:")
    for r_val, cnt in sorted(counts_mode3.items()):
        print(f"  mode-3 rank {r_val}: {cnt:5d}")
    print()
    print("True tensor rank classification:")
    for label, cnt in counts_true.items():
        print(f"  {label}: {cnt:5d}")
    print()
    print(f"REDUCIBLE QUADRUPLES (true rank <= 3): {len(reducible_quadruples)}")
    if reducible_quadruples:
        print("First 5 reducible quadruples (i, j, k, l, decomp_size):")
        for tup in reducible_quadruples[:5]:
            print(f"  {tup}")

    return {
        'n_combos': n_combos,
        'counts_mode_max': counts_mode_max,
        'counts_mode3': counts_mode3,
        'counts_true': counts_true,
        'reducible_quadruples': reducible_quadruples,
    }


if __name__ == "__main__":
    main()
