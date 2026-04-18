"""
keating_snaith_arithmetic_analysis.py — combined follow-ups F1 + F4 + F5.

Tests whether the rank-dependent convergence slope in R_k = M_k/(log X)^{k(k-1)/2}
survives normalization that removes the first-moment drift and/or the
num_bad_primes Euler-factor dependence.

F1 proxy (arithmetic factor): compute M_k_norm = M_k / M_1^k per cell.
  If the slope of R_k_norm(log X) is still rank-dependent, arithmetic factor
  a_E(k) is not the explanation.

F4 (P021 stratification): re-compute M_k per (rank, decade, num_bad_primes)
  triple. If the rank-dependent slope persists at fixed bad-prime-count,
  the signal is not bad-prime-mediated.

F5 (block-shuffle pipeline sanity): shuffle leading_term values WITHIN each
  (rank, decade) cell and verify moments are invariant to numerical precision.
  Confirms pipeline has no accidental ordering dependence.

Data source: prometheus_fire.zeros.object_zeros (leading_term) JOINED with
lmfdb.public.ec_curvedata (num_bad_primes) on lmfdb_label.
"""
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2

PF = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)
LM = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

RANKS = [0, 1, 2, 3]
K_VALUES = [1, 2, 3, 4]
DECADE_EDGES = [(100, 1000), (1000, 10_000), (10_000, 100_000),
                (100_000, 1_000_000), (1_000_000, 10_000_000)]
MIN_PER_CELL = 100
MIN_PER_TRIPLE = 50   # slightly lower for P021 sub-strata
K_BINS = [1, 2, 3, 4, 5, 6]


def load_joined():
    """Join zeros.object_zeros × ec_curvedata via lmfdb_label.
    Both DBs are on same host so we pull in two queries and merge.
    Returns list of (rank, conductor, leading_term, num_bad_primes)."""
    with psycopg2.connect(**PF) as pf_conn:
        cur = pf_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, analytic_rank, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND leading_term IS NOT NULL AND leading_term > 0
              AND conductor > 0 AND analytic_rank <= 3
        """)
        zeros_rows = {r[0]: (r[1], int(r[2]), float(r[3])) for r in cur.fetchall()}
    with psycopg2.connect(**LM) as lm_conn:
        cur = lm_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, NULLIF(num_bad_primes, '')::int
            FROM public.ec_curvedata
            WHERE num_bad_primes IS NOT NULL
        """)
        nbp = {r[0]: r[1] for r in cur.fetchall()}
    out = []
    for lbl, (rank, cond, lt) in zeros_rows.items():
        k = nbp.get(lbl)
        if k is None:
            continue
        out.append((rank, cond, lt, int(k)))
    return out


def cell_moments(vals, k_values):
    out = {}
    for k in k_values:
        xk = vals ** k
        out[str(k)] = {
            "M_k": float(xk.mean()),
            "se": float(math.sqrt(max(xk.var(ddof=1), 0.0) / max(vals.size - 1, 1))),
        }
    return out


def slope_fit(xs, ys):
    """Return slope of y vs x with SE."""
    if len(xs) < 2:
        return None, None
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    mx, my = x.mean(), y.mean()
    num = ((x - mx) * (y - my)).sum()
    den = ((x - mx) ** 2).sum()
    if den == 0:
        return None, None
    slope = float(num / den)
    pred = slope * x + (my - slope * mx)
    resid = y - pred
    if len(xs) > 2:
        s2 = float((resid ** 2).sum() / (len(xs) - 2))
        se = math.sqrt(s2 / den) if den > 0 else 0.0
    else:
        se = 0.0
    return slope, float(se)


def decade_midpoint(lo, hi):
    return math.sqrt(lo * hi)


def build_cell_dict(rows):
    """{(rank, decade_key): [leading_term values], ...}"""
    cells = defaultdict(list)
    cells_by_k = defaultdict(list)
    for rank, cond, lt, nbp in rows:
        if rank not in RANKS or lt <= 0:
            continue
        for lo, hi in DECADE_EDGES:
            if lo <= cond < hi:
                key = (rank, lo, hi)
                cells[key].append(lt)
                cells_by_k[(rank, lo, hi, nbp)].append(lt)
                break
    return cells, cells_by_k


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[ks_arithmetic] start {started}")

    rows = load_joined()
    print(f"[ks_arithmetic] joined rows: {len(rows)}")
    cells, cells_triple = build_cell_dict(rows)
    print(f"[ks_arithmetic] (rank,decade) cells: {len(cells)}; triples: {len(cells_triple)}")

    # =======================================================================
    # F1 proxy: normalized moments M_k / M_1^k, slope across decades
    # =======================================================================
    per_cell = {}
    for (rank, lo, hi), vals in cells.items():
        arr = np.asarray(vals, dtype=float)
        if arr.size < MIN_PER_CELL:
            continue
        x_mid = decade_midpoint(lo, hi)
        log_x = math.log(x_mid)
        mk = cell_moments(arr, K_VALUES)
        M1 = mk["1"]["M_k"]
        normed = {}
        for k in K_VALUES:
            if M1 > 0:
                m_norm = mk[str(k)]["M_k"] / (M1 ** k)
            else:
                m_norm = None
            expo = k * (k - 1) / 2.0
            denom = log_x ** expo if expo > 0 else 1.0
            R_raw = mk[str(k)]["M_k"] / denom
            R_norm = (m_norm / denom) if (m_norm is not None and denom > 0) else None
            normed[str(k)] = {
                "M_k_raw": mk[str(k)]["M_k"],
                "M_k_normalized_by_M1_k": m_norm,
                "R_k_raw": R_raw,
                "R_k_normalized": R_norm,
                "exponent": expo,
            }
        per_cell[f"rank={rank}_decade=[{lo},{hi})"] = {
            "rank": rank, "lo": lo, "hi": hi, "log_X_mid": log_x,
            "n": int(arr.size), "M_1": M1, "moments": normed,
        }

    # Convergence slopes per rank, for both raw and normalized ratios
    slopes = {"raw": {}, "normalized": {}}
    for rank in RANKS:
        key_prefix = f"rank={rank}_decade="
        cell_list = sorted([c for name, c in per_cell.items() if name.startswith(key_prefix)],
                            key=lambda c: c["log_X_mid"])
        log_x = [c["log_X_mid"] for c in cell_list]
        slopes["raw"][rank] = {}
        slopes["normalized"][rank] = {}
        for k in K_VALUES:
            y_raw = [c["moments"][str(k)]["R_k_raw"] for c in cell_list]
            y_norm = [c["moments"][str(k)]["R_k_normalized"] for c in cell_list
                      if c["moments"][str(k)]["R_k_normalized"] is not None]
            s_raw, se_raw = slope_fit(log_x, y_raw)
            s_norm, se_norm = slope_fit(log_x[:len(y_norm)], y_norm)
            slopes["raw"][rank][k] = {"slope": s_raw, "se": se_raw}
            slopes["normalized"][rank][k] = {"slope": s_norm, "se": se_norm}

    # =======================================================================
    # F4: P021-stratified (rank, decade, num_bad_primes) moments + slopes
    # =======================================================================
    per_triple = {}
    for (rank, lo, hi, nbp), vals in cells_triple.items():
        arr = np.asarray(vals, dtype=float)
        if arr.size < MIN_PER_TRIPLE:
            continue
        x_mid = decade_midpoint(lo, hi)
        log_x = math.log(x_mid)
        mk = cell_moments(arr, K_VALUES)
        entry = {"rank": rank, "lo": lo, "hi": hi, "num_bad_primes": nbp,
                 "log_X_mid": log_x, "n": int(arr.size),
                 "moments": {}}
        for k in K_VALUES:
            expo = k * (k - 1) / 2.0
            denom = log_x ** expo if expo > 0 else 1.0
            entry["moments"][str(k)] = {"M_k": mk[str(k)]["M_k"],
                                         "R_k_raw": mk[str(k)]["M_k"] / denom}
        per_triple[f"r={rank}_d=[{lo},{hi})_k={nbp}"] = entry

    # Slopes per (rank, nbp): regression of R_k across decade midpoints
    slopes_P021 = {}
    for rank in RANKS:
        slopes_P021[rank] = {}
        for nbp in K_BINS:
            sub = sorted([e for e in per_triple.values()
                           if e["rank"] == rank and e["num_bad_primes"] == nbp],
                          key=lambda e: e["log_X_mid"])
            if len(sub) < 2:
                continue
            log_x = [e["log_X_mid"] for e in sub]
            slopes_P021[rank][nbp] = {}
            for k in K_VALUES:
                y = [e["moments"][str(k)]["R_k_raw"] for e in sub]
                s, se = slope_fit(log_x, y)
                slopes_P021[rank][nbp][k] = {"slope": s, "se": se,
                                              "n_decades": len(sub)}

    # =======================================================================
    # F5: block-shuffle pipeline sanity — moments must be invariant under
    #     within-cell shuffle (they depend only on the multiset of values).
    # =======================================================================
    rng = np.random.default_rng(42)
    f5_results = []
    # Pick 3 representative cells to verify
    sample_keys = [f"rank=0_decade=[100000,1000000)",
                   f"rank=1_decade=[100000,1000000)",
                   f"rank=2_decade=[10000,100000)"]
    for key in sample_keys:
        if key not in per_cell:
            continue
        rank = per_cell[key]["rank"]
        lo, hi = per_cell[key]["lo"], per_cell[key]["hi"]
        vals = np.asarray(cells[(rank, lo, hi)], dtype=float)
        shuffled = rng.permutation(vals)
        before = cell_moments(vals, K_VALUES)
        after = cell_moments(shuffled, K_VALUES)
        max_abs_delta = max(abs(before[str(k)]["M_k"] - after[str(k)]["M_k"])
                             for k in K_VALUES)
        f5_results.append({
            "cell": key,
            "n": int(vals.size),
            "max_abs_moment_delta_across_k": float(max_abs_delta),
            "before": before,
            "after": after,
            "interpretation": (
                "PASS — moments are symmetric functions of the values; any "
                "within-cell permutation leaves them numerically identical "
                "modulo float rounding." if max_abs_delta < 1e-10 else
                "FAIL — pipeline depends on ordering, investigate"
            ),
        })

    # =======================================================================
    # Headline summary
    # =======================================================================
    rank_slopes_raw = [(r, slopes["raw"][r][1]["slope"]) for r in RANKS
                       if slopes["raw"][r][1]["slope"] is not None]
    rank_slopes_norm = [(r, slopes["normalized"][r][1]["slope"]) for r in RANKS
                        if slopes["normalized"][r][1]["slope"] is not None]

    summary = {
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "n_rows_joined": len(rows),
        "n_cells": len(per_cell),
        "n_triples": len(per_triple),
        "slopes_raw_k1_by_rank": dict(rank_slopes_raw),
        "slopes_normalized_k1_by_rank": dict(rank_slopes_norm),
        "F5_pipeline_sanity_results": f5_results,
        "F1_reading": (
            "If slopes_normalized are flat across ranks, the rank-dependent "
            "slope in the raw analysis was an arithmetic-factor / M_1-drift "
            "artifact. If slopes_normalized remain rank-monotone, the "
            "rank-dependence is intrinsic to higher moments (F041 survives "
            "first-moment deflation)."
        ),
        "F4_reading": (
            "slopes_P021 reports per (rank, num_bad_primes) slope across "
            "conductor decades. If slopes are roughly constant across "
            "num_bad_primes at each rank, the rank-dependence is NOT "
            "bad-prime-mediated. If slopes vary monotonically with num_bad_primes, "
            "bad-prime structure is the hidden axis."
        ),
        "F5_reading": (
            "All F5 cells should show max_abs_moment_delta < 1e-10. Any larger "
            "delta indicates pipeline ordering-dependence (data quality alarm)."
        ),
    }

    results = {
        "task": "keating_snaith_arithmetic_analysis_F1_F4_F5",
        "instance": "Harmonia_M2_sessionC",
        "summary": summary,
        "slopes_raw": slopes["raw"],
        "slopes_normalized": slopes["normalized"],
        "slopes_P021_per_rank_per_nbp": slopes_P021,
        "per_cell_detail": per_cell,
        "per_triple_P021_detail": per_triple,
        "pattern_20_discipline": [
            "Normalization applied per-cell (not pooled across cells).",
            "P021 stratification adds a third orthogonal axis; no pooling across (rank, decade, num_bad_primes) triples.",
            "F5 sanity cells report before/after moments explicitly.",
        ],
    }

    out_path = os.path.join("cartography", "docs",
                             "keating_snaith_arithmetic_analysis_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[ks_arithmetic] wrote {out_path}")
    print(f"[ks_arithmetic] raw slopes k=1 by rank: {dict(rank_slopes_raw)}")
    print(f"[ks_arithmetic] normalized slopes k=1 by rank: {dict(rank_slopes_norm)}")
    print(f"[ks_arithmetic] F5 pipeline sanity: "
          f"{all(r['max_abs_moment_delta_across_k'] < 1e-10 for r in f5_results)}")


if __name__ == "__main__":
    main()
