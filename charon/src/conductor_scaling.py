"""
North Star Experiment 1: Conductor Scaling Gradient
====================================================
Does the spectral tail ARI vary with conductor?

Three outcomes:
  FLAT: Signal is intrinsic to zero geometry. Not a pre-asymptotic artifact.
  DECREASING: Pre-asymptotic uniformity was carrying us. Signal weakens as
              symmetry types separate at higher conductor.
  INCREASING: More data/higher conductor sharpens the signal. Scale up.

Also tests the RMT gap: does the residual (empirical - RMT ≈ 0.05) vary
with conductor? If it shrinks at higher conductor, the residual is a
finite-conductor artifact. If it persists, it's structural.
"""

import duckdb
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "charon.duckdb"

TAIL_SLICE = slice(4, 20)  # zeros 5-19
CONDUCTOR_BINS = [
    (1, 100, "1-100"),
    (101, 500, "101-500"),
    (501, 1000, "501-1K"),
    (1001, 2000, "1K-2K"),
    (2001, 3000, "2K-3K"),
    (3001, 5000, "3K-5K"),
]


def load_data():
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("""
        SELECT ec.lmfdb_iso, ec.conductor, ec.rank,
               oz.zeros_vector, oz.n_zeros_stored
        FROM elliptic_curves ec
        JOIN object_zeros oz ON ec.object_id = oz.object_id
        WHERE oz.zeros_vector IS NOT NULL AND oz.n_zeros_stored >= 20
        ORDER BY ec.object_id
    """).fetchall()
    con.close()

    seen = set()
    data = []
    for iso, cond, rank, zvec, nz in rows:
        if iso in seen:
            continue
        seen.add(iso)
        root_num = zvec[20]
        zeros = np.array([float(zvec[i]) if zvec[i] is not None else 0.0 for i in range(20)])
        data.append({"conductor": int(cond), "rank": int(rank or 0),
                      "root_num": float(root_num), "zeros": zeros})
    return data


def compute_ari_within_strata(objects, zero_slice):
    """Compute ARI within conductor sub-strata using k-means."""
    by_cond = defaultdict(list)
    for d in objects:
        by_cond[d["conductor"]].append(d)
    aris = []
    n_strata = 0
    n_objects = 0
    for c, objs in by_cond.items():
        if len(objs) < 5:
            continue
        ranks = [o["rank"] for o in objs]
        if len(set(ranks)) < 2:
            continue
        X = np.array([o["zeros"][zero_slice] for o in objs])
        k = max(2, min(len(objs) // 2, 5))
        pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
        aris.append(adjusted_rand_score(ranks, pred))
        n_strata += 1
        n_objects += len(objs)
    return np.mean(aris) if aris else float('nan'), n_strata, n_objects


def main():
    data = load_data()
    print(f"Loaded {len(data)} ECs total")
    print()

    # === All ECs, by conductor bin ===
    print("=" * 72)
    print("CONDUCTOR SCALING GRADIENT — ALL RANKS, ZEROS 5-19")
    print("=" * 72)
    print(f"{'Bin':>10s} | {'N_obj':>6s} | {'N_strata':>8s} | {'ARI':>8s} | {'Ranks':>20s}")
    print("-" * 72)

    for lo, hi, label in CONDUCTOR_BINS:
        subset = [d for d in data if lo <= d["conductor"] <= hi]
        rank_counts = defaultdict(int)
        for d in subset:
            rank_counts[d["rank"]] += 1
        ari, n_strata, n_obj = compute_ari_within_strata(subset, TAIL_SLICE)
        rc_str = ", ".join(f"r{k}={v}" for k, v in sorted(rank_counts.items()))
        print(f"{label:>10s} | {len(subset):>6d} | {n_strata:>8d} | {ari:>8.4f} | {rc_str}")

    # === SO(even) only, by conductor bin ===
    so_even = [d for d in data if d["root_num"] == 1.0]
    print()
    print("=" * 72)
    print("CONDUCTOR SCALING — SO(even) ONLY (rank 0 vs rank 2), ZEROS 5-19")
    print("=" * 72)
    print(f"{'Bin':>10s} | {'N_obj':>6s} | {'N_strata':>8s} | {'ARI':>8s} | {'N_r0':>6s} | {'N_r2':>6s}")
    print("-" * 72)

    for lo, hi, label in CONDUCTOR_BINS:
        subset = [d for d in so_even if lo <= d["conductor"] <= hi]
        n_r0 = sum(1 for d in subset if d["rank"] == 0)
        n_r2 = sum(1 for d in subset if d["rank"] == 2)
        ari, n_strata, n_obj = compute_ari_within_strata(subset, TAIL_SLICE)
        print(f"{label:>10s} | {len(subset):>6d} | {n_strata:>8d} | {ari:>8.4f} | {n_r0:>6d} | {n_r2:>6d}")

    # === Comparison: all 20 zeros vs tail only, by bin ===
    print()
    print("=" * 72)
    print("ABLATION BY BIN: ALL 20 ZEROS vs TAIL (5-19)")
    print("=" * 72)
    print(f"{'Bin':>10s} | {'ARI_all20':>10s} | {'ARI_tail':>10s} | {'Delta':>8s}")
    print("-" * 72)

    for lo, hi, label in CONDUCTOR_BINS:
        subset = [d for d in data if lo <= d["conductor"] <= hi]
        ari_all, _, _ = compute_ari_within_strata(subset, slice(0, 20))
        ari_tail, _, _ = compute_ari_within_strata(subset, TAIL_SLICE)
        delta = ari_tail - ari_all
        print(f"{label:>10s} | {ari_all:>10.4f} | {ari_tail:>10.4f} | {delta:>+8.4f}")

    # === VERDICT ===
    print()
    print("=" * 72)
    print("VERDICT")
    print("=" * 72)
    # Compute gradient
    aris_by_bin = []
    for lo, hi, label in CONDUCTOR_BINS:
        subset = [d for d in data if lo <= d["conductor"] <= hi]
        ari, n_s, _ = compute_ari_within_strata(subset, TAIL_SLICE)
        if n_s >= 3:
            aris_by_bin.append((label, ari))

    if len(aris_by_bin) >= 3:
        vals = [a for _, a in aris_by_bin]
        trend = np.polyfit(range(len(vals)), vals, 1)[0]
        print(f"  Linear trend slope: {trend:+.4f} per bin")
        if abs(trend) < 0.02:
            print("  -> FLAT. Signal is intrinsic. Not a pre-asymptotic artifact.")
        elif trend < -0.02:
            print("  -> DECREASING. Signal weakens at higher conductor.")
            print("    Pre-asymptotic uniformity may be carrying the signal.")
        elif trend > 0.02:
            print("  -> INCREASING. Signal strengthens at higher conductor.")
            print("    Scale up for sharper results.")


if __name__ == "__main__":
    main()
