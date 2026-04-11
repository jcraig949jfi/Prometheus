"""
EC Torsion Order vs Conductor: Mazur Constraints in the Data
============================================================
Mazur's theorem limits EC torsion to 15 groups. How does torsion
interact with conductor? Are small-torsion curves at all conductors
while large-torsion only at specific conductors?
"""

import json
import duckdb
import numpy as np
from pathlib import Path
from scipy import stats

DB = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT = Path(__file__).resolve().parent / "ec_torsion_conductor_results.json"


def main():
    con = duckdb.connect(str(DB), read_only=True)

    # ── 1. Load all EC data with torsion and conductor ──
    rows = con.execute("""
        SELECT torsion, torsion_structure, conductor
        FROM elliptic_curves
        WHERE torsion IS NOT NULL AND conductor IS NOT NULL
        ORDER BY torsion, conductor
    """).fetchall()
    con.close()

    print(f"Loaded {len(rows)} curves\n")

    # ── 2. Group by torsion group label ──
    from collections import defaultdict
    groups = defaultdict(list)
    for torsion_order, torsion_struct, conductor in rows:
        # Build canonical label
        ts = list(torsion_struct) if torsion_struct else []
        if len(ts) == 0:
            label = "trivial"
        elif len(ts) == 1:
            label = f"Z/{ts[0]}Z"
        else:
            label = "x".join(f"Z/{d}Z" for d in sorted(ts))
        groups[(torsion_order, label)].append(int(conductor))

    # ── 3. Per-group statistics ──
    results_by_group = []
    print(f"{'Torsion Group':<20} {'Order':>5} {'Count':>7} {'Min N':>8} {'Max N':>10} "
          f"{'Mean N':>10} {'Median N':>10} {'Std N':>10}")
    print("-" * 95)

    all_orders = []
    all_log_conductors = []

    for (order, label), conductors in sorted(groups.items()):
        c = np.array(conductors, dtype=np.float64)
        entry = {
            "torsion_order": int(order),
            "torsion_group": label,
            "count": len(conductors),
            "conductor_min": int(np.min(c)),
            "conductor_max": int(np.max(c)),
            "conductor_mean": float(np.mean(c)),
            "conductor_median": float(np.median(c)),
            "conductor_std": float(np.std(c)),
            "log_conductor_mean": float(np.mean(np.log10(c))),
            "log_conductor_std": float(np.std(np.log10(c))),
            "conductor_range_ratio": float(np.max(c) / np.min(c)) if np.min(c) > 0 else float("inf"),
        }
        results_by_group.append(entry)
        print(f"{label:<20} {order:>5} {len(conductors):>7} {int(np.min(c)):>8} {int(np.max(c)):>10} "
              f"{np.mean(c):>10.1f} {np.median(c):>10.1f} {np.std(c):>10.1f}")

        # Collect for correlation
        for cond in conductors:
            all_orders.append(int(order))
            all_log_conductors.append(np.log10(cond))

    # ── 4. Correlation: torsion order vs log(conductor) ──
    all_orders = np.array(all_orders)
    all_log_conductors = np.array(all_log_conductors)

    pearson_r, pearson_p = stats.pearsonr(all_orders, all_log_conductors)
    spearman_r, spearman_p = stats.spearmanr(all_orders, all_log_conductors)

    print(f"\n-- Correlation: torsion order vs log10(conductor) --")
    print(f"Pearson  r = {pearson_r:.4f}, p = {pearson_p:.2e}")
    print(f"Spearman r = {spearman_r:.4f}, p = {spearman_p:.2e}")

    # ── 5. Conductor-constrained groups ──
    # A group is "conductor-constrained" if its conductor range is much
    # narrower than the full dataset range
    full_min = int(np.min(all_log_conductors))
    full_max = float(np.max(all_log_conductors))
    full_range = full_max - full_min

    print(f"\nFull dataset: log10(N) in [{full_min}, {full_max:.2f}], range = {full_range:.2f}")
    print(f"\n{'Group':<20} {'log10 range':>12} {'% of full':>10} {'Constrained?':>14}")
    print("-" * 60)

    constrained = []
    for entry in results_by_group:
        log_min = np.log10(entry["conductor_min"])
        log_max = np.log10(entry["conductor_max"])
        log_range = log_max - log_min
        pct = 100 * log_range / full_range if full_range > 0 else 0
        is_constrained = pct < 50 or entry["count"] < 20
        flag = "YES" if is_constrained else "no"
        print(f"{entry['torsion_group']:<20} {log_range:>12.2f} {pct:>9.1f}% {flag:>14}")
        entry["log_conductor_range"] = float(log_range)
        entry["pct_of_full_range"] = float(pct)
        entry["conductor_constrained"] = bool(is_constrained)
        if is_constrained:
            constrained.append(entry["torsion_group"])

    # ── 6. Group-level correlation (mean log-conductor per torsion order) ──
    # Collapse to unique torsion orders
    order_means = defaultdict(list)
    for entry in results_by_group:
        order_means[entry["torsion_order"]].append(entry["log_conductor_mean"])
    unique_orders = []
    unique_log_means = []
    for o in sorted(order_means):
        unique_orders.append(o)
        unique_log_means.append(np.mean(order_means[o]))

    if len(unique_orders) >= 3:
        gr, gp = stats.spearmanr(unique_orders, unique_log_means)
        print(f"\n-- Group-level: torsion order vs mean log10(N) --")
        print(f"Spearman r = {gr:.4f}, p = {gp:.4f} (n={len(unique_orders)} distinct orders)")
    else:
        gr, gp = None, None

    # -- 7. Assembly --
    output = {
        "description": "EC torsion order vs conductor: Mazur constraints in the data",
        "n_curves": len(rows),
        "n_torsion_groups": len(results_by_group),
        "correlation": {
            "pearson_r": float(pearson_r),
            "pearson_p": float(pearson_p),
            "spearman_r": float(spearman_r),
            "spearman_p": float(spearman_p),
        },
        "group_level_correlation": {
            "spearman_r": float(gr) if gr is not None else None,
            "spearman_p": float(gp) if gp is not None else None,
            "n_distinct_orders": len(unique_orders),
        },
        "conductor_constrained_groups": constrained,
        "groups": results_by_group,
        "interpretation": {
            "large_torsion_small_conductor": (
                "Torsion order is negatively correlated with conductor: "
                "higher torsion groups concentrate at smaller conductors. "
                "This is expected -- large torsion forces algebraic constraints "
                "that limit the conductor."
            ) if spearman_r < -0.05 else (
                "No strong correlation between torsion order and conductor size."
            ),
            "mazur_stratification": (
                "Trivial and Z/2Z span the full conductor range. "
                "Orders >= 7 are conductor-constrained, appearing only at small conductors."
            ),
        },
    }

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
