"""
rank2_P021_x_P026.py — Harmonia worker T3.

Question: Does the rank-2 F041a slope-vs-num_bad_primes ladder sharpen under
joint stratification with P026 (semistable vs additive reduction)?

Background:
  W2 confirmed F041a at rank 2: slopes 1.21 -> 2.52 monotone across nbp=1..6,
  amp 27.6x over null.
  W3 ruled out Galois l-adic image (nonmax_count range 0.305 vs nbp range 1.316).
  Open question: is the ladder a nbp x (semistable vs additive) interaction?

Kodaira would be finer but is DERIVABLE-NOT-STORED (P035 draft). P026 semistable
flag is the cheap proxy that IS in ec_curvedata.semistable (text 'True'/'False').

Method:
  1. Filter rank=2, conductor [10^3, 10^6), non-null leading_term.
  2. Parse semistable text to bool.
  3. Stratify jointly by (num_bad_primes in 1..6, semistable in {True, False}):
     6 x 2 = 12 cells per conductor decade (3 decades).
  4. For each (nbp, semistable) pair, fit slope of mean(leading_term) vs
     log(conductor) across decades.
  5. Report slope matrix, differences, which half carries the ladder.
  6. Ratio slope_range_additive / slope_range_semistable:
       > 1.3   : additive carries the ladder
       [0.8,1.3]: orthogonal to semistable
       < 0.8   : semistable carries the ladder (surprise)

Pattern 20: n >= 100 per (rank, decade, nbp, semistable) quadruple.

Secondary: redo at rank 3 where coverage allows.

Data:
  prometheus_fire.zeros.object_zeros (elliptic_curve, leading_term, rank)
  lmfdb.public.ec_curvedata (num_bad_primes, semistable) joined on lmfdb_label.
"""
from __future__ import annotations

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

DECADE_EDGES = [(1_000, 10_000),
                (10_000, 100_000),
                (100_000, 1_000_000)]
MIN_PER_CELL = 100            # per (decade, stratum) minimum
MIN_DECADES_FOR_SLOPE = 2     # need at least 2 decades to fit a slope

NBP_BINS = [1, 2, 3, 4, 5, 6]
SEMI_BINS = [False, True]     # False=additive, True=semistable


def parse_semistable(text):
    if text is None:
        return None
    t = text.strip().lower()
    if t in ("true", "t", "1"):
        return True
    if t in ("false", "f", "0"):
        return False
    return None


def load_joined(rank: int):
    """Join rank-N zeros x ec_curvedata. Return list of dict rows."""
    with psycopg2.connect(**PF) as pf:
        cur = pf.cursor()
        cur.execute("""
            SELECT lmfdb_label, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND analytic_rank = %s
              AND leading_term IS NOT NULL AND leading_term > 0
              AND conductor >= 1000 AND conductor < 1000000
        """, (rank,))
        zr = {r[0]: (int(r[1]), float(r[2])) for r in cur.fetchall()}

    if not zr:
        return []

    labels = list(zr.keys())
    print(f"[T3] rank={rank} zeros rows in 10^3..10^6: {len(labels)}")

    nbp_map = {}
    semi_map = {}
    CHUNK = 5000
    with psycopg2.connect(**LM) as lm:
        for i in range(0, len(labels), CHUNK):
            batch = labels[i:i + CHUNK]
            cur = lm.cursor()
            cur.execute("""
                SELECT lmfdb_label,
                       NULLIF(num_bad_primes, '')::int,
                       semistable
                FROM public.ec_curvedata
                WHERE lmfdb_label = ANY(%s)
            """, (batch,))
            for lbl, nbp, semi in cur.fetchall():
                if nbp is None:
                    continue
                sb = parse_semistable(semi)
                if sb is None:
                    continue
                nbp_map[lbl] = int(nbp)
                semi_map[lbl] = sb

    out = []
    for lbl, (cond, lt) in zr.items():
        if lbl not in nbp_map:
            continue
        out.append({
            "label": lbl,
            "conductor": cond,
            "leading_term": lt,
            "num_bad_primes": nbp_map[lbl],
            "semistable": semi_map[lbl],
        })
    print(f"[T3] rank={rank} joined rows: {len(out)}")
    return out


def decade_mid(lo, hi):
    return math.sqrt(lo * hi)


def slope_fit(xs, ys):
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
    if len(xs) > 2:
        pred = slope * x + (my - slope * mx)
        s2 = float(((y - pred) ** 2).sum() / (len(xs) - 2))
        se = math.sqrt(s2 / den) if den > 0 else 0.0
    else:
        se = 0.0
    return slope, float(se)


def m1_by_decade(cells):
    out = []
    for (lo, hi), vals in cells.items():
        arr = np.asarray(vals, dtype=float)
        if arr.size < MIN_PER_CELL:
            out.append({"lo": lo, "hi": hi, "n": int(arr.size),
                        "log_X_mid": math.log(decade_mid(lo, hi)),
                        "M_1": float(arr.mean()) if arr.size else None,
                        "sparse": True})
            continue
        out.append({"lo": lo, "hi": hi, "n": int(arr.size),
                    "log_X_mid": math.log(decade_mid(lo, hi)),
                    "M_1": float(arr.mean()),
                    "sparse": False})
    out.sort(key=lambda r: r["log_X_mid"])
    return out


def fit_stratum_slope(per_decade):
    valid = [r for r in per_decade if not r["sparse"]]
    log_x = [r["log_X_mid"] for r in valid]
    m1 = [r["M_1"] for r in valid]
    slope, se = slope_fit(log_x, m1)
    return {
        "slope": slope,
        "se": se,
        "n_decades_valid": len(valid),
        "n_decades_total": len(per_decade),
        "per_decade": per_decade,
    }


def stratify_joint(rows):
    """
    Stratify by (nbp, semistable). Return nested dict
    result[nbp][semistable_str] = fit dict.
    """
    cells = defaultdict(list)
    totals = defaultdict(int)
    for r in rows:
        nbp = r["num_bad_primes"]
        if nbp not in NBP_BINS:
            continue
        semi = r["semistable"]
        for lo, hi in DECADE_EDGES:
            if lo <= r["conductor"] < hi:
                cells[(nbp, semi, (lo, hi))].append(r["leading_term"])
                totals[(nbp, semi)] += 1
                break

    out = {}
    for nbp in NBP_BINS:
        out[str(nbp)] = {}
        for semi in SEMI_BINS:
            by_dec = {}
            for lo, hi in DECADE_EDGES:
                by_dec[(lo, hi)] = cells.get((nbp, semi, (lo, hi)), [])
            pd = m1_by_decade(by_dec)
            fit = fit_stratum_slope(pd)
            out[str(nbp)][str(semi)] = {
                **fit,
                "n_total": totals.get((nbp, semi), 0),
            }
    return out


def stratify_nbp_only(rows, semi_filter=None):
    """Marginal P021 slopes optionally restricted to one semistable half."""
    cells = defaultdict(list)
    totals = defaultdict(int)
    for r in rows:
        if semi_filter is not None and r["semistable"] != semi_filter:
            continue
        nbp = r["num_bad_primes"]
        if nbp not in NBP_BINS:
            continue
        for lo, hi in DECADE_EDGES:
            if lo <= r["conductor"] < hi:
                cells[(nbp, (lo, hi))].append(r["leading_term"])
                totals[nbp] += 1
                break
    out = {}
    for nbp in NBP_BINS:
        by_dec = {}
        for lo, hi in DECADE_EDGES:
            by_dec[(lo, hi)] = cells.get((nbp, (lo, hi)), [])
        pd = m1_by_decade(by_dec)
        fit = fit_stratum_slope(pd)
        out[str(nbp)] = {**fit, "n_total": totals.get(nbp, 0)}
    return out


def slope_range_from_nbp_map(nbp_fits, restrict_keys=None):
    if restrict_keys is None:
        items = [(k, f["slope"]) for k, f in nbp_fits.items()
                 if f["slope"] is not None]
    else:
        items = [(k, nbp_fits[k]["slope"]) for k in restrict_keys
                 if k in nbp_fits and nbp_fits[k]["slope"] is not None]
    slopes = [v for _, v in items]
    if len(slopes) < 2:
        return {"slope_min": None, "slope_max": None, "range": None,
                "n_strata_fitted": len(slopes),
                "fitted_strata": [k for k, _ in items]}
    return {
        "slope_min": float(min(slopes)),
        "slope_max": float(max(slopes)),
        "range": float(max(slopes) - min(slopes)),
        "n_strata_fitted": len(slopes),
        "fitted_strata": [k for k, _ in items],
    }


def classify_ratio(ratio):
    if ratio is None:
        return "INCONCLUSIVE (insufficient coverage)"
    if ratio > 1.3:
        return "additive carries the ladder"
    if ratio < 0.8:
        return "semistable carries the ladder (surprise)"
    return "orthogonal to semistable"


def analyse_rank(rank, rows):
    """Return the full result block for a given rank."""
    joint = stratify_joint(rows)

    # Marginal P021 ladder (no semistable split) for reference
    nbp_marginal = stratify_nbp_only(rows, semi_filter=None)
    nbp_additive = stratify_nbp_only(rows, semi_filter=False)
    nbp_semi = stratify_nbp_only(rows, semi_filter=True)

    # Slope matrix view
    slope_matrix = {}
    for nbp in NBP_BINS:
        n_str = str(nbp)
        slope_matrix[n_str] = {
            "additive": joint[n_str]["False"]["slope"],
            "semistable": joint[n_str]["True"]["slope"],
        }

    # Difference slope_additive - slope_semistable per nbp
    diff_per_nbp = {}
    for nbp in NBP_BINS:
        n_str = str(nbp)
        sa = joint[n_str]["False"]["slope"]
        ss = joint[n_str]["True"]["slope"]
        if sa is not None and ss is not None:
            diff_per_nbp[n_str] = float(sa - ss)
        else:
            diff_per_nbp[n_str] = None

    # Per-cell n counts
    cell_coverage = {}
    sparse_cells = []
    for nbp in NBP_BINS:
        n_str = str(nbp)
        for semi in SEMI_BINS:
            s_str = str(semi)
            fit = joint[n_str][s_str]
            per_dec = fit["per_decade"]
            cell_coverage[f"nbp={nbp}_semi={semi}"] = {
                "n_total": fit["n_total"],
                "per_decade_n": [(r["lo"], r["hi"], r["n"], r["sparse"])
                                 for r in per_dec],
                "n_decades_valid": fit["n_decades_valid"],
            }
            for r in per_dec:
                if r["sparse"]:
                    sparse_cells.append({
                        "nbp": nbp, "semistable": semi,
                        "decade": [r["lo"], r["hi"]], "n": r["n"],
                    })

    # Slope ranges per half
    additive_half = {str(nbp): joint[str(nbp)]["False"] for nbp in NBP_BINS}
    semi_half = {str(nbp): joint[str(nbp)]["True"] for nbp in NBP_BINS}

    range_additive_full = slope_range_from_nbp_map(additive_half)
    range_semistable_full = slope_range_from_nbp_map(semi_half)
    range_marginal = slope_range_from_nbp_map(nbp_marginal)

    # Common-support fair comparison: only nbp strata where BOTH halves
    # have a fittable slope. This eliminates the coverage-cliff confound
    # where (say) nbp=1 is only present in semistable half.
    common_keys = [str(nbp) for nbp in NBP_BINS
                   if additive_half[str(nbp)]["slope"] is not None
                   and semi_half[str(nbp)]["slope"] is not None]
    range_additive_common = slope_range_from_nbp_map(additive_half,
                                                     restrict_keys=common_keys)
    range_semistable_common = slope_range_from_nbp_map(semi_half,
                                                       restrict_keys=common_keys)

    # Headline ratio is the common-support ratio (fair).
    ra_full = range_additive_full["range"]
    rs_full = range_semistable_full["range"]
    ra_common = range_additive_common["range"]
    rs_common = range_semistable_common["range"]

    if ra_common is not None and rs_common is not None and rs_common > 0:
        ratio_common = ra_common / rs_common
    else:
        ratio_common = None
    if ra_full is not None and rs_full is not None and rs_full > 0:
        ratio_full = ra_full / rs_full
    else:
        ratio_full = None

    verdict = classify_ratio(ratio_common)

    # Which half carries more ladder amplitude (on common support)?
    if ra_common is not None and rs_common is not None:
        if ra_common > rs_common:
            carrier = "additive"
        elif rs_common > ra_common:
            carrier = "semistable"
        else:
            carrier = "tie"
    else:
        carrier = "insufficient coverage"

    ra = ra_common
    rs = rs_common
    ratio = ratio_common

    return {
        "rank": rank,
        "n_joined_rows": len(rows),
        "joint_slope_matrix_nbp_x_semistable": slope_matrix,
        "diff_slope_additive_minus_semistable_per_nbp": diff_per_nbp,
        "marginal_nbp_slopes": {s: f["slope"]
                                for s, f in nbp_marginal.items()},
        "additive_half_nbp_slopes": {s: f["slope"]
                                     for s, f in additive_half.items()},
        "semistable_half_nbp_slopes": {s: f["slope"]
                                       for s, f in semi_half.items()},
        "slope_range_additive": ra,
        "slope_range_semistable": rs,
        "slope_range_additive_full": ra_full,
        "slope_range_semistable_full": rs_full,
        "slope_range_additive_common": ra_common,
        "slope_range_semistable_common": rs_common,
        "slope_range_marginal": range_marginal["range"],
        "ratio_additive_over_semistable": ratio,
        "ratio_additive_over_semistable_full": ratio_full,
        "ratio_additive_over_semistable_common": ratio_common,
        "common_support_nbp_keys": common_keys,
        "range_additive_detail": range_additive_full,
        "range_semistable_detail": range_semistable_full,
        "range_additive_common_detail": range_additive_common,
        "range_semistable_common_detail": range_semistable_common,
        "verdict": verdict,
        "carrier": carrier,
        "joint_detail": joint,
        "marginal_detail": nbp_marginal,
        "additive_half_detail": nbp_additive,
        "semistable_half_detail": nbp_semi,
        "cell_coverage": cell_coverage,
        "sparse_cells": sparse_cells,
        "n_sparse_cells": len(sparse_cells),
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[T3] start {started}")

    # ------- Primary: rank 2 -------
    rows_r2 = load_joined(2)
    if not rows_r2:
        raise SystemExit("rank=2 join empty; abort.")

    # Sanity: split of semistable within rank 2
    r2_semi_count = sum(1 for r in rows_r2 if r["semistable"])
    r2_add_count = len(rows_r2) - r2_semi_count
    print(f"[T3] rank=2: semistable={r2_semi_count} additive={r2_add_count}")

    res_r2 = analyse_rank(2, rows_r2)
    print(f"[T3] rank=2 common nbp support    = {res_r2['common_support_nbp_keys']}")
    print(f"[T3] rank=2 slope_range_additive  (common) = {res_r2['slope_range_additive_common']}")
    print(f"[T3] rank=2 slope_range_semistable(common) = {res_r2['slope_range_semistable_common']}")
    print(f"[T3] rank=2 slope_range_additive  (full)   = {res_r2['slope_range_additive_full']}")
    print(f"[T3] rank=2 slope_range_semistable(full)   = {res_r2['slope_range_semistable_full']}")
    print(f"[T3] rank=2 ratio (common-support) = {res_r2['ratio_additive_over_semistable_common']}")
    print(f"[T3] rank=2 ratio (full)           = {res_r2['ratio_additive_over_semistable_full']}")
    print(f"[T3] rank=2 verdict               : {res_r2['verdict']}")

    # ------- Secondary: rank 3 (coverage permitting) -------
    rows_r3 = load_joined(3)
    if rows_r3:
        r3_semi_count = sum(1 for r in rows_r3 if r["semistable"])
        r3_add_count = len(rows_r3) - r3_semi_count
        print(f"[T3] rank=3: semistable={r3_semi_count} additive={r3_add_count}")
        res_r3 = analyse_rank(3, rows_r3)
        print(f"[T3] rank=3 common nbp support    = {res_r3['common_support_nbp_keys']}")
        print(f"[T3] rank=3 slope_range_additive  (common) = {res_r3['slope_range_additive_common']}")
        print(f"[T3] rank=3 slope_range_semistable(common) = {res_r3['slope_range_semistable_common']}")
        print(f"[T3] rank=3 ratio (common)        = {res_r3['ratio_additive_over_semistable_common']}")
        print(f"[T3] rank=3 verdict               : {res_r3['verdict']}")
    else:
        res_r3 = {"rank": 3, "n_joined_rows": 0, "note": "no rank-3 rows"}

    finished = datetime.now(timezone.utc).isoformat()
    results = {
        "task_id": "rank2_P021_x_P026_semistable",
        "drafted_by": "Harmonia_worker_T3",
        "started": started,
        "finished": finished,
        "scope": {
            "primary_rank": 2,
            "secondary_rank": 3,
            "conductor_range": "[1000, 1000000)",
            "decade_edges": DECADE_EDGES,
            "min_per_cell": MIN_PER_CELL,
            "nbp_bins": NBP_BINS,
            "semi_bins": [str(b) for b in SEMI_BINS],
        },
        "headline": {
            "rank_2_verdict": res_r2["verdict"],
            "rank_2_carrier": res_r2["carrier"],
            "rank_2_common_support_nbp_keys": res_r2["common_support_nbp_keys"],
            "rank_2_slope_range_additive_common":
                res_r2["slope_range_additive_common"],
            "rank_2_slope_range_semistable_common":
                res_r2["slope_range_semistable_common"],
            "rank_2_ratio_common_support":
                res_r2["ratio_additive_over_semistable_common"],
            "rank_2_slope_range_additive_full":
                res_r2["slope_range_additive_full"],
            "rank_2_slope_range_semistable_full":
                res_r2["slope_range_semistable_full"],
            "rank_2_ratio_full_support":
                res_r2["ratio_additive_over_semistable_full"],
            "rank_2_slope_range_marginal": res_r2["slope_range_marginal"],
            "rank_3_verdict": res_r3.get("verdict"),
            "rank_3_ratio_common_support":
                res_r3.get("ratio_additive_over_semistable_common"),
        },
        "rank_2": res_r2,
        "rank_3": res_r3,
        "interpretation": (
            "F041a rank-2 slope ladder vs num_bad_primes (W2: nbp=1..6 slopes "
            "1.21..2.52). Here we split each nbp cell by P026 semistable vs "
            "additive reduction. Kodaira (P035) is finer but not stored; the "
            "semistable flag is a cheap dichotomous proxy. ratio>1.3 means "
            "the ladder's resolving power lives mostly in the additive half "
            "(reduction type is coupled to the zero statistic); ratio in "
            "[0.8,1.3] means the ladder is orthogonal to reduction type "
            "(F041a is a num_bad_primes effect per se, not a reduction-type "
            "effect); ratio<0.8 would be a surprise and would demand Kodaira. "
            "PATTERN-9 NOTE: rank-2 nbp=1 and nbp=6 each have one side with "
            "n<100, so the full-support range is apples-to-oranges (semistable "
            "half covers nbp 1..6 while additive half only 2..5). The "
            "headline verdict uses the COMMON-SUPPORT ratio (nbp strata where "
            "both halves fit a slope) — this is the fair comparison and is "
            "what the verdict categories are applied to. The full-support "
            "number is reported for transparency but is confounded by the "
            "coverage cliff at the extremes of nbp."
        ),
        "pattern_20_discipline": [
            "Per-(rank, decade, nbp, semistable) cell reported with n and sparse flag.",
            "Slope fit uses only cells with n>=100.",
            "Sparse cells surfaced as Pattern-9 coverage cliffs in sparse_cells[].",
            "Decade_mid = sqrt(lo*hi); OLS over 2..3 decades.",
            "semistable parsed from text 'True'/'False' to bool.",
            "Common-support ratio used for verdict (fair comparison).",
            "Full-support ratio also reported for transparency.",
            "rank 3 secondary pass documented even if cells go sparse.",
        ],
    }

    out_path = os.path.join("cartography", "docs",
                            "rank2_P021_x_P026_semistable_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[T3] wrote {out_path}")
    print(f"[T3] RANK 2 HEADLINE: {res_r2['verdict']} "
          f"(ratio={res_r2['ratio_additive_over_semistable']})")


if __name__ == "__main__":
    main()
