"""
EC abc Quality: rad(N)/N distribution for elliptic curve conductors.

For a Frey curve y² = x(x-a^p)(x+b^p), the conductor equals rad(abc).
Semistable curves have squarefree conductor, so rad(N)=N.
The ratio rad(N)/N measures how far the conductor is from squarefree —
essentially the squarefree-core fraction, complement to semistable analysis.

Outputs: cartography/v2/ec_abc_quality_results.json
"""

import json
import sys
from pathlib import Path
from collections import Counter
import math

import duckdb
import numpy as np

DB_PATH = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "ec_abc_quality_results.json"


def rad(n):
    """Product of distinct prime factors of n."""
    if n <= 1:
        return max(n, 1)
    result = 1
    d = 2
    temp = abs(n)
    while d * d <= temp:
        if temp % d == 0:
            result *= d
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        result *= temp
    return result


def compute_szpiro_ratio(n):
    """rad(N)/N — always in (0, 1], equals 1 iff N is squarefree."""
    r = rad(n)
    return r / n


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Load all EC data
    df = con.execute("""
        SELECT conductor, rank, semistable, cm, torsion, regulator, sha, degree
        FROM elliptic_curves
        WHERE conductor IS NOT NULL AND conductor > 0
    """).fetchall()
    cols = ["conductor", "rank", "semistable", "cm", "torsion", "regulator", "sha", "degree"]
    con.close()

    print(f"Loaded {len(df)} elliptic curves")

    # Compute rad(N)/N for each curve
    records = []
    for row in df:
        rec = dict(zip(cols, row))
        N = int(rec["conductor"])
        r = rad(N)
        ratio = r / N
        rec["rad_N"] = r
        rec["rad_ratio"] = ratio
        rec["is_squarefree"] = (r == N)
        records.append(rec)

    ratios = np.array([r["rad_ratio"] for r in records])
    conductors = np.array([r["conductor"] for r in records])
    ranks = np.array([r["rank"] if r["rank"] is not None else -1 for r in records])
    semistable_flags = np.array([r["semistable"] for r in records])
    squarefree_flags = np.array([r["is_squarefree"] for r in records])

    # --- Distribution statistics ---
    print(f"\n=== rad(N)/N Distribution ===")
    print(f"  N curves:     {len(ratios)}")
    print(f"  Mean:         {np.mean(ratios):.6f}")
    print(f"  Median:       {np.median(ratios):.6f}")
    print(f"  Std:          {np.std(ratios):.6f}")
    print(f"  Min:          {np.min(ratios):.6f}")
    print(f"  Max:          {np.max(ratios):.6f}")

    # Percentiles
    pcts = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    pct_vals = {str(p): float(np.percentile(ratios, p)) for p in pcts}
    print(f"  Percentiles:  {pct_vals}")

    # Squarefree fraction
    n_sqfree = int(np.sum(squarefree_flags))
    frac_sqfree = n_sqfree / len(ratios)
    print(f"\n  Squarefree (rad=N): {n_sqfree}/{len(ratios)} = {frac_sqfree:.4f}")

    # Cross-check with semistable flag
    n_semistable = int(np.sum([1 for r in records if r["semistable"] is True]))
    print(f"  Semistable flag:    {n_semistable}/{len(ratios)} = {n_semistable/len(ratios):.4f}")

    # Agreement between squarefree conductor and semistable
    agree = sum(1 for r in records if r["is_squarefree"] == (r["semistable"] is True))
    print(f"  Squarefree==Semistable agreement: {agree}/{len(ratios)} = {agree/len(ratios):.4f}")

    # --- Histogram bins ---
    bin_edges = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.01]
    hist, _ = np.histogram(ratios, bins=bin_edges)
    histogram = {f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}": int(hist[i]) for i in range(len(hist))}
    print(f"\n  Histogram: {histogram}")

    # --- By rank ---
    print(f"\n=== rad(N)/N by Rank ===")
    rank_stats = {}
    for rk in sorted(set(ranks)):
        if rk < 0:
            continue
        mask = ranks == rk
        r_sub = ratios[mask]
        if len(r_sub) == 0:
            continue
        sqfree_sub = squarefree_flags[mask]
        stats = {
            "count": int(len(r_sub)),
            "mean_ratio": float(np.mean(r_sub)),
            "median_ratio": float(np.median(r_sub)),
            "frac_squarefree": float(np.mean(sqfree_sub)),
        }
        rank_stats[int(rk)] = stats
        print(f"  Rank {rk}: n={stats['count']}, mean={stats['mean_ratio']:.4f}, "
              f"median={stats['median_ratio']:.4f}, sqfree={stats['frac_squarefree']:.4f}")

    # --- By CM status ---
    print(f"\n=== rad(N)/N by CM Status ===")
    cm_stats = {}
    for has_cm in [False, True]:
        mask = np.array([r["cm"] != 0 for r in records]) if has_cm else np.array([r["cm"] == 0 for r in records])
        r_sub = ratios[mask]
        if len(r_sub) == 0:
            continue
        sqfree_sub = squarefree_flags[mask]
        label = "CM" if has_cm else "non-CM"
        stats = {
            "count": int(len(r_sub)),
            "mean_ratio": float(np.mean(r_sub)),
            "median_ratio": float(np.median(r_sub)),
            "frac_squarefree": float(np.mean(sqfree_sub)),
        }
        cm_stats[label] = stats
        print(f"  {label}: n={stats['count']}, mean={stats['mean_ratio']:.4f}, "
              f"sqfree={stats['frac_squarefree']:.4f}")

    # --- Conductor size vs ratio ---
    print(f"\n=== rad(N)/N by Conductor Magnitude ===")
    log_cond = np.log10(conductors.astype(float))
    cond_bins = [(0, 2), (2, 3), (3, 4), (4, 5), (5, 7)]
    cond_stats = {}
    for lo, hi in cond_bins:
        mask = (log_cond >= lo) & (log_cond < hi)
        r_sub = ratios[mask]
        if len(r_sub) == 0:
            continue
        sqfree_sub = squarefree_flags[mask]
        label = f"10^{lo}-10^{hi}"
        stats = {
            "count": int(len(r_sub)),
            "mean_ratio": float(np.mean(r_sub)),
            "median_ratio": float(np.median(r_sub)),
            "frac_squarefree": float(np.mean(sqfree_sub)),
        }
        cond_stats[label] = stats
        print(f"  N in [{label}]: n={stats['count']}, mean={stats['mean_ratio']:.4f}, "
              f"sqfree={stats['frac_squarefree']:.4f}")

    # --- Extreme cases: smallest rad(N)/N ---
    sorted_by_ratio = sorted(records, key=lambda r: r["rad_ratio"])
    extremes_low = []
    for r in sorted_by_ratio[:20]:
        extremes_low.append({
            "conductor": int(r["conductor"]),
            "rad_N": int(r["rad_N"]),
            "rad_ratio": round(r["rad_ratio"], 6),
            "rank": int(r["rank"]) if r["rank"] is not None else None,
        })
    print(f"\n=== 20 Lowest rad(N)/N ===")
    for e in extremes_low:
        print(f"  N={e['conductor']}, rad={e['rad_N']}, ratio={e['rad_ratio']}, rank={e['rank']}")

    # --- Unique conductor analysis ---
    cond_set = sorted(set(int(r["conductor"]) for r in records))
    cond_ratios = {N: rad(N) / N for N in cond_set}
    unique_ratios = np.array(list(cond_ratios.values()))
    print(f"\n=== Unique Conductors ===")
    print(f"  N unique conductors: {len(cond_set)}")
    print(f"  Squarefree: {sum(1 for v in cond_ratios.values() if v == 1.0)}/{len(cond_set)} "
          f"= {sum(1 for v in cond_ratios.values() if v == 1.0)/len(cond_set):.4f}")
    print(f"  Mean rad(N)/N: {np.mean(unique_ratios):.6f}")

    # --- Assemble results ---
    results = {
        "description": "EC abc quality: rad(N)/N distribution for elliptic curve conductors",
        "note": "rad(N)/N = 1 iff N squarefree iff semistable. Measures distance from Frey-curve regime.",
        "n_curves": len(ratios),
        "n_unique_conductors": len(cond_set),
        "distribution": {
            "mean": float(np.mean(ratios)),
            "median": float(np.median(ratios)),
            "std": float(np.std(ratios)),
            "min": float(np.min(ratios)),
            "max": float(np.max(ratios)),
            "percentiles": pct_vals,
        },
        "histogram": histogram,
        "squarefree_analysis": {
            "n_squarefree_curves": n_sqfree,
            "frac_squarefree_curves": round(frac_sqfree, 6),
            "n_semistable_flag": n_semistable,
            "frac_semistable_flag": round(n_semistable / len(ratios), 6),
            "agreement_sqfree_vs_semistable": round(agree / len(ratios), 6),
            "n_unique_squarefree_conductors": sum(1 for v in cond_ratios.values() if v == 1.0),
            "frac_unique_squarefree": round(
                sum(1 for v in cond_ratios.values() if v == 1.0) / len(cond_set), 6
            ),
        },
        "by_rank": rank_stats,
        "by_cm_status": cm_stats,
        "by_conductor_magnitude": cond_stats,
        "extremes_lowest_ratio": extremes_low,
        "interpretation": {
            "abc_connection": (
                "For Frey curves E_{a,b}: y^2 = x(x-a^p)(x+b^p), conductor = rad(abc). "
                "Semistable (squarefree conductor) curves live in the Frey regime. "
                "Non-squarefree conductors have primes dividing N to power >= 2, "
                "meaning additive reduction — these are further from the abc/Szpiro landscape."
            ),
            "szpiro_ratio": (
                "Szpiro's conjecture: log|Delta| <= (6+eps)*log(N). "
                "rad(N)/N measures multiplicative complexity of the conductor. "
                "Low ratio = highly composite conductor = more room for Szpiro slack."
            ),
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
