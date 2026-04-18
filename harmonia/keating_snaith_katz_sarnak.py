"""
keating_snaith_katz_sarnak.py — F3 Katz-Sarnak distribution-shape check.

Rank 0 ↔ SO_even central-value distribution.
Rank 1 ↔ SO_odd derivative distribution.

Compute shape metrics (mean, std, skew, kurtosis, tail quantile density)
of normalized leading_term / M_1 at each conductor decade, per rank.
A Katz-Sarnak signature: SO_even has more density near zero (higher
Pr[L < 0.5·mean]); SO_odd has less density near zero (the central zero
forces L' to stay away from zero). Rank 2+ is outside the 2-family map.

We report the shape metrics and the "low-tail density" ratio
  τ(rank, decade) = Pr[ L/M_1 < 0.25 ]
which should differ between rank 0 and rank 1 under Katz-Sarnak.
"""
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2
from scipy import stats

PG = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)

RANKS = [0, 1, 2, 3]
DECADE_EDGES = [(100, 1000), (1000, 10_000), (10_000, 100_000),
                (100_000, 1_000_000), (1_000_000, 10_000_000)]
LOW_TAIL_THRESHOLDS = [0.25, 0.50, 1.0, 2.0]
MIN_PER_CELL = 200


def load_cells():
    with psycopg2.connect(**PG) as conn:
        cur = conn.cursor()
        cells = defaultdict(list)
        for rank in RANKS:
            for lo, hi in DECADE_EDGES:
                cur.execute("""
                    SELECT leading_term
                    FROM zeros.object_zeros
                    WHERE object_type = 'elliptic_curve'
                      AND analytic_rank = %s
                      AND conductor >= %s AND conductor < %s
                      AND leading_term IS NOT NULL
                      AND leading_term > 0
                """, (rank, lo, hi))
                for row in cur.fetchall():
                    cells[(rank, lo, hi)].append(float(row[0]))
    return cells


def shape_metrics(arr):
    if arr.size < MIN_PER_CELL:
        return None
    mean = float(arr.mean())
    if mean <= 0:
        return None
    norm = arr / mean  # L / M_1 — mean-normalized
    metrics = {
        "n": int(arr.size),
        "mean": mean,
        "std": float(arr.std(ddof=1)),
        "norm_std": float(norm.std(ddof=1)),
        "skew": float(stats.skew(norm, bias=False)),
        "excess_kurtosis": float(stats.kurtosis(norm, fisher=True, bias=False)),
        "median": float(np.median(norm)),
        "p10": float(np.quantile(norm, 0.10)),
        "p25": float(np.quantile(norm, 0.25)),
        "p75": float(np.quantile(norm, 0.75)),
        "p90": float(np.quantile(norm, 0.90)),
    }
    for t in LOW_TAIL_THRESHOLDS:
        metrics[f"Pr_less_{t}"] = float(np.mean(norm < t))
    return metrics


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[ks_katz_sarnak] start {started}")

    cells = load_cells()
    per_cell = {}
    for (rank, lo, hi), vals in cells.items():
        arr = np.asarray(vals, dtype=float)
        m = shape_metrics(arr)
        if m is None:
            continue
        per_cell[f"rank={rank}_decade=[{lo},{hi})"] = {
            "rank": rank, "lo": lo, "hi": hi, **m,
        }

    # Contrast rank 0 vs rank 1 at the largest adequate decade
    # Katz-Sarnak reading: low-tail density should be HIGHER for SO_even (rank 0)
    # vs SO_odd (rank 1). This is a qualitative signature, not a significance test.
    contrasts = {}
    for lo, hi in DECADE_EDGES:
        r0 = per_cell.get(f"rank=0_decade=[{lo},{hi})")
        r1 = per_cell.get(f"rank=1_decade=[{lo},{hi})")
        if r0 is None or r1 is None:
            continue
        contrasts[f"decade=[{lo},{hi})"] = {
            "n_rank0": r0["n"], "n_rank1": r1["n"],
            "low_tail_Pr_less_0.25": {
                "rank0_SO_even_pred_LARGER": r0["Pr_less_0.25"],
                "rank1_SO_odd_pred_SMALLER": r1["Pr_less_0.25"],
                "delta_r0_minus_r1": r0["Pr_less_0.25"] - r1["Pr_less_0.25"],
            },
            "norm_std": {"rank0": r0["norm_std"], "rank1": r1["norm_std"]},
            "skew": {"rank0": r0["skew"], "rank1": r1["skew"]},
            "excess_kurtosis": {"rank0": r0["excess_kurtosis"], "rank1": r1["excess_kurtosis"]},
            "katz_sarnak_sign_consistent": (
                (r0["Pr_less_0.25"] > r1["Pr_less_0.25"])
            ),
        }

    # Headline: sign consistency across decades?
    ks_checks = [c["katz_sarnak_sign_consistent"] for c in contrasts.values()]
    ks_universal = all(ks_checks) and len(ks_checks) > 0
    ks_any = any(ks_checks) and len(ks_checks) > 0

    results = {
        "task": "keating_snaith_katz_sarnak_F3",
        "instance": "Harmonia_M2_sessionC",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "per_cell_shape_metrics": per_cell,
        "rank0_vs_rank1_contrast": contrasts,
        "katz_sarnak_low_tail_sign_check": {
            "description": "Under Katz-Sarnak, SO_even (rank 0) has more low-tail mass than SO_odd (rank 1) because the central zero-forcing in SO_odd keeps L' away from zero.",
            "sign_consistent_every_decade": ks_universal,
            "sign_consistent_any_decade": ks_any,
            "per_decade_signs": {k: v["katz_sarnak_sign_consistent"] for k, v in contrasts.items()},
        },
        "reading": (
            "If sign_consistent_every_decade is TRUE, the empirical low-tail "
            "density ordering rank0 > rank1 is consistent with Katz-Sarnak's "
            "SO_even (extra density at zero) vs SO_odd (central zero) prediction. "
            "This does NOT prove the family assignment — CFKRS theoretical "
            "constants must be computed and compared. It's a qualitative "
            "sign-check that the RMT family assignment is not wildly wrong."
        ),
    }

    out_path = os.path.join("cartography", "docs",
                             "keating_snaith_katz_sarnak_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[ks_katz_sarnak] wrote {out_path}")
    print(f"[ks_katz_sarnak] sign_consistent_every_decade: {ks_universal}")
    for d, c in contrasts.items():
        print(f"  {d}  r0 P(<0.25)={c['low_tail_Pr_less_0.25']['rank0_SO_even_pred_LARGER']:.4f}  "
              f"r1 P(<0.25)={c['low_tail_Pr_less_0.25']['rank1_SO_odd_pred_SMALLER']:.4f}  "
              f"delta={c['low_tail_Pr_less_0.25']['delta_r0_minus_r1']:+.4f}")


if __name__ == "__main__":
    main()
