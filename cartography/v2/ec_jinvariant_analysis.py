"""
EC j-Invariant Distribution and Special Values
================================================
Analyzes the distribution of j-invariants across elliptic curves in the
Charon DuckDB database. j=0 (CM by Z[zeta_3]) and j=1728 (CM by Z[i])
correspond to curves with extra automorphisms.

j-invariant is stored as jinv_num / jinv_den (rational number).
"""

import json
import math
import numpy as np
from collections import Counter
from pathlib import Path

import duckdb

DB_PATH = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "ec_jinvariant_results.json"


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Load all relevant data
    rows = con.execute("""
        SELECT jinv_num, jinv_den, conductor, rank, cm
        FROM elliptic_curves
        WHERE jinv_den IS NOT NULL AND jinv_den != 0
    """).fetchall()
    con.close()

    total = len(rows)
    print(f"Total curves with valid j-invariant: {total}")

    # Build arrays
    j_num = np.array([r[0] for r in rows])
    j_den = np.array([r[1] for r in rows])
    j_val = j_num / j_den  # float j-invariant
    conductors = np.array([r[2] for r in rows])
    ranks = np.array([r[3] for r in rows])
    cm_vals = np.array([r[4] for r in rows])

    # --- 1. Distinct j-invariants ---
    # Use (num, den) pairs normalized by GCD for exact rational comparison
    j_rational = set()
    for n, d in zip(j_num, j_den):
        # Normalize sign: den > 0
        if d < 0:
            n, d = -n, -d
        g = math.gcd(int(abs(n)), int(abs(d)))
        j_rational.add((int(n / g), int(d / g)))
    n_distinct = len(j_rational)
    print(f"Distinct j-invariants (rational): {n_distinct}")

    # --- 2. Distribution of |j| ---
    abs_j = np.abs(j_val)
    abs_j_finite = abs_j[np.isfinite(abs_j)]
    log_abs_j = np.log10(abs_j_finite + 1)  # +1 to handle j=0

    pctiles = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]
    abs_j_percentiles = {str(p): float(np.percentile(abs_j_finite, p)) for p in pctiles}
    log_abs_j_percentiles = {str(p): float(np.percentile(log_abs_j, p)) for p in pctiles}

    print(f"\n|j| percentiles:")
    for p in pctiles:
        print(f"  {p}%: {abs_j_percentiles[str(p)]:.4e}")

    # --- 3. Special values: j=0 and j=1728 ---
    # j=0 means jinv_num=0
    j_zero_mask = (j_num == 0)
    n_j_zero = int(j_zero_mask.sum())
    frac_j_zero = n_j_zero / total

    # j=1728 means jinv_num/jinv_den = 1728
    # Check with tolerance for float, but also exact rational
    j_1728_mask = np.abs(j_val - 1728.0) < 1e-6
    n_j_1728 = int(j_1728_mask.sum())
    frac_j_1728 = n_j_1728 / total

    print(f"\nj=0 (CM by -3): {n_j_zero} curves ({frac_j_zero:.4%})")
    print(f"j=1728 (CM by -4): {n_j_1728} curves ({frac_j_1728:.4%})")

    # Cross-check with cm field
    cm_minus3 = int((cm_vals == -3).sum())
    cm_minus4 = int((cm_vals == -4).sum())
    cm_nonzero = int((cm_vals != 0).sum())
    print(f"CM=-3 from cm field: {cm_minus3}")
    print(f"CM=-4 from cm field: {cm_minus4}")
    print(f"Total CM curves: {cm_nonzero}")

    # --- 4. Most common j-invariants ---
    j_counter = Counter()
    for n, d in zip(j_num, j_den):
        if d < 0:
            n, d = -n, -d
        g = math.gcd(int(abs(n)), int(abs(d)))
        key = (int(n / g), int(d / g))
        j_counter[key] += 1

    top_20 = j_counter.most_common(20)
    print(f"\nTop 20 most common j-invariants:")
    top_20_list = []
    for (num, den), count in top_20:
        j_float = num / den if den != 0 else float('inf')
        label = f"{num}/{den}" if den != 1 else str(num)
        print(f"  j={label} (={j_float:.4f}): {count} curves")
        top_20_list.append({
            "jinv_num": num,
            "jinv_den": den,
            "jinv_float": round(j_float, 6),
            "count": count
        })

    # --- 5. j vs conductor correlation ---
    finite_mask = np.isfinite(j_val)
    corr_j_cond = float(np.corrcoef(np.log10(np.abs(j_val[finite_mask]) + 1),
                                      np.log10(conductors[finite_mask].astype(float)))[0, 1])
    print(f"\nCorrelation log|j| vs log(conductor): {corr_j_cond:.4f}")

    # Mean conductor by j-value bucket
    j_buckets = {}
    for j, c in zip(j_val[finite_mask], conductors[finite_mask]):
        if j == 0:
            bucket = "j=0"
        elif abs(j - 1728) < 1e-6:
            bucket = "j=1728"
        elif abs(j) < 100:
            bucket = "|j|<100"
        elif abs(j) < 10000:
            bucket = "100<=|j|<10K"
        elif abs(j) < 1e8:
            bucket = "10K<=|j|<100M"
        else:
            bucket = "|j|>=100M"
        j_buckets.setdefault(bucket, []).append(int(c))

    conductor_by_jbucket = {}
    print("\nMean conductor by j-bucket:")
    for bucket in ["j=0", "j=1728", "|j|<100", "100<=|j|<10K", "10K<=|j|<100M", "|j|>=100M"]:
        if bucket in j_buckets:
            vals = j_buckets[bucket]
            conductor_by_jbucket[bucket] = {
                "count": len(vals),
                "mean_conductor": round(float(np.mean(vals)), 2),
                "median_conductor": float(np.median(vals))
            }
            print(f"  {bucket}: n={len(vals)}, mean_cond={np.mean(vals):.1f}, median_cond={np.median(vals):.1f}")

    # --- 6. j vs rank ---
    rank_vals = sorted(set(ranks))
    j_by_rank = {}
    print(f"\nj-invariant statistics by rank:")
    for r in rank_vals:
        mask = (ranks == r) & finite_mask
        if mask.sum() == 0:
            continue
        j_r = j_val[mask]
        abs_j_r = np.abs(j_r)
        n_zero = int((j_r == 0).sum())
        n_1728 = int((np.abs(j_r - 1728) < 1e-6).sum())
        entry = {
            "count": int(mask.sum()),
            "n_j_zero": n_zero,
            "n_j_1728": n_1728,
            "frac_j_zero": round(n_zero / mask.sum(), 6),
            "frac_j_1728": round(n_1728 / mask.sum(), 6),
            "median_abs_j": float(np.median(abs_j_r)),
            "mean_log_abs_j": float(np.mean(np.log10(abs_j_r + 1)))
        }
        j_by_rank[int(r)] = entry
        print(f"  rank {r}: n={entry['count']}, j=0: {n_zero} ({entry['frac_j_zero']:.4%}), "
              f"j=1728: {n_1728} ({entry['frac_j_1728']:.4%}), "
              f"median|j|={entry['median_abs_j']:.2e}")

    # --- 7. j-height distribution ---
    # Height = log max(|num|, |den|)
    j_heights = []
    for n, d in zip(j_num, j_den):
        h = math.log(max(abs(n), abs(d), 1))  # natural log, floor at 1
        j_heights.append(h)
    j_heights = np.array(j_heights)

    height_percentiles = {str(p): round(float(np.percentile(j_heights, p)), 4) for p in pctiles}
    print(f"\nj-height (ln max(|num|,|den|)) percentiles:")
    for p in pctiles:
        print(f"  {p}%: {height_percentiles[str(p)]:.4f}")

    # Height by rank
    height_by_rank = {}
    for r in rank_vals:
        mask = ranks == r
        if mask.sum() == 0:
            continue
        h_r = j_heights[mask]
        height_by_rank[int(r)] = {
            "mean": round(float(np.mean(h_r)), 4),
            "median": round(float(np.median(h_r)), 4),
            "std": round(float(np.std(h_r)), 4)
        }

    print(f"\nj-height by rank:")
    for r in sorted(height_by_rank):
        e = height_by_rank[r]
        print(f"  rank {r}: mean={e['mean']:.2f}, median={e['median']:.2f}, std={e['std']:.2f}")

    # --- Assemble results ---
    results = {
        "metadata": {
            "source": "charon/data/charon.duckdb, table elliptic_curves",
            "total_curves": total,
            "distinct_j_invariants": n_distinct,
            "date": "2026-04-10"
        },
        "special_values": {
            "j_zero": {
                "count": n_j_zero,
                "fraction": round(frac_j_zero, 6),
                "cm_discriminant": -3,
                "note": "Extra automorphism group Z/6Z"
            },
            "j_1728": {
                "count": n_j_1728,
                "fraction": round(frac_j_1728, 6),
                "cm_discriminant": -4,
                "note": "Extra automorphism group Z/4Z"
            },
            "total_cm_curves": cm_nonzero,
            "cm_minus3_from_field": cm_minus3,
            "cm_minus4_from_field": cm_minus4
        },
        "abs_j_percentiles": abs_j_percentiles,
        "log_abs_j_percentiles": log_abs_j_percentiles,
        "top_20_j_invariants": top_20_list,
        "j_vs_conductor": {
            "correlation_log_abs_j_vs_log_conductor": corr_j_cond,
            "conductor_by_j_bucket": conductor_by_jbucket
        },
        "j_by_rank": j_by_rank,
        "j_height": {
            "percentiles_ln": height_percentiles,
            "by_rank": height_by_rank
        }
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
