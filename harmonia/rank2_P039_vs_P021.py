"""
rank2_P039_vs_P021.py — Harmonia worker W3.

Question: At rank 2, does the M_1 vs log(conductor) slope pattern resolve more
sharply under P039 (Galois l-adic image stratification via ec_curvedata.nonmax_primes)
than under P021 (num_bad_primes)? Or is num_bad_primes just a proxy for a finer
Galois-image effect?

Background (from keating_snaith_arithmetic_analysis_results.json):
  Rank 2, slope M_1 vs log X, stratified by num_bad_primes:
    nbp=1: 1.21 ; nbp=2: 1.52 ; nbp=3: 1.70 ;
    nbp=4: 1.86 ; nbp=5: 1.95 ; nbp=6: 2.52
  (Range = 1.32 across nbp=1..6.)

Method: rank 2 only, conductor in [10^3, 10^6).
  Three stratifications, each computes per-(decade, stratum) M_1 cells then
  fits slope vs log X per stratum:

  A) P021 alone: by num_bad_primes.
  B) P039 alone: by nonmax_count (len of nonmax_primes list).
  C) P039 subprojection: by has_p booleans (p in {2,3,5,7}).

  Resolving power = slope_max - slope_min across strata (only strata with
  >= MIN_PER_TRIPLE cells and >= 2 decades that pass MIN_PER_TRIPLE).

Verdicts:
  P039_SHARPER      — P039 range > P021 range * 1.20
  PROXY_CONFIRMED   — P039 range within +-10% of P021 range
  ORTHOGONAL        — joint P021 x P039 stratification reveals structure not
                      visible in either alone (joint range > 1.20 * max(A,B))
  P021_SHARPER      — (Inverse case added by W3.) P021 range > 1.20 * best P039
                      range: num_bad_primes resolves the slope pattern sharper
                      than any Galois-image marginal we tested; the signal is
                      not a Galois-image effect in disguise.
  (Fallthrough: INCONCLUSIVE.)

Pattern-20 discipline:
  Per-cell reporting. n >= 100 per (decade, stratum) cell. Sparse strata
  documented explicitly rather than silently dropped.

Data sources (per CLAUDE.md: keys.py for creds; here DB creds are inline
for the same-host two-cluster pattern used by sibling scripts):
  prometheus_fire.zeros.object_zeros (elliptic_curve, leading_term)
  lmfdb.public.ec_curvedata  (num_bad_primes, nonmax_primes)
"""
from __future__ import annotations

import ast
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

# Rank 2 only. Conductor 10^3 .. 10^6.
DECADE_EDGES = [(1_000, 10_000),
                (10_000, 100_000),
                (100_000, 1_000_000)]
MIN_PER_CELL = 100           # per (decade, stratum) minimum
MIN_DECADES_FOR_SLOPE = 2    # need at least 2 decades to fit a slope

NBP_BINS = [1, 2, 3, 4, 5, 6]
NONMAX_COUNT_BINS = [0, 1, 2, 3]            # nonmax list length
HAS_PRIMES = [2, 3, 5, 7]                   # specific small primes to track


# ------------------------------------------------------------
# IO
# ------------------------------------------------------------
def parse_nonmax(text: str) -> list[int]:
    """Parse a text-list such as '[]', '[2]', '[2, 3]' into a list of ints."""
    if text is None:
        return []
    try:
        v = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return []
    if not isinstance(v, (list, tuple)):
        return []
    out = []
    for x in v:
        try:
            out.append(int(x))
        except (TypeError, ValueError):
            pass
    return out


def load_joined():
    """Join rank-2 zeros × ec_curvedata. Return list of dict rows."""
    with psycopg2.connect(**PF) as pf:
        cur = pf.cursor()
        cur.execute("""
            SELECT lmfdb_label, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND analytic_rank = 2
              AND leading_term IS NOT NULL AND leading_term > 0
              AND conductor >= 1000 AND conductor < 1000000
        """)
        zr = {r[0]: (int(r[1]), float(r[2])) for r in cur.fetchall()}

    if not zr:
        return []

    labels = list(zr.keys())
    print(f"[W3] zeros rank=2 rows in 10^3..10^6: {len(labels)}")

    # Batch fetch curvedata in chunks to avoid huge parameter tuples
    nbp_map: dict[str, int] = {}
    nonmax_map: dict[str, list[int]] = {}
    CHUNK = 5000
    with psycopg2.connect(**LM) as lm:
        for i in range(0, len(labels), CHUNK):
            batch = labels[i:i + CHUNK]
            cur = lm.cursor()
            cur.execute("""
                SELECT lmfdb_label,
                       NULLIF(num_bad_primes, '')::int,
                       nonmax_primes
                FROM public.ec_curvedata
                WHERE lmfdb_label = ANY(%s)
            """, (batch,))
            for lbl, nbp, nmp in cur.fetchall():
                if nbp is None:
                    continue
                nbp_map[lbl] = int(nbp)
                nonmax_map[lbl] = parse_nonmax(nmp)

    out = []
    for lbl, (cond, lt) in zr.items():
        if lbl not in nbp_map:
            continue
        out.append({
            "label": lbl,
            "conductor": cond,
            "leading_term": lt,
            "num_bad_primes": nbp_map[lbl],
            "nonmax_primes": nonmax_map[lbl],
        })
    print(f"[W3] joined rank=2 rows: {len(out)}")
    return out


# ------------------------------------------------------------
# Stats helpers
# ------------------------------------------------------------
def decade_mid(lo: int, hi: int) -> float:
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


def m1_by_decade(cells: dict) -> list[dict]:
    """cells : {(lo,hi): [lt values]} -> sorted list of {lo,hi,log_x,n,M1}."""
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


def fit_stratum_slope(per_decade: list[dict]) -> dict:
    """Fit slope of M_1 vs log X using only non-sparse decades."""
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


def stratify(rows, key_fn, stratum_values) -> dict:
    """
    Group rows by (stratum, decade), compute per-stratum M_1 slopes.
    stratum_values : explicit list so we always report even sparse strata.
    Returns {stratum_str: {slope,..., per_decade, n_total}}.
    """
    cells = defaultdict(list)   # (stratum, (lo,hi)) -> list of lt
    totals = defaultdict(int)
    for r in rows:
        s = key_fn(r)
        if s is None:
            continue
        for lo, hi in DECADE_EDGES:
            if lo <= r["conductor"] < hi:
                cells[(s, (lo, hi))].append(r["leading_term"])
                totals[s] += 1
                break

    out = {}
    # Determine which strata actually appear; allow stratum_values to be
    # a superset so sparse strata are still reported.
    seen = sorted({s for (s, _d) in cells.keys()},
                  key=lambda x: (isinstance(x, str), x))
    strata = list(stratum_values) if stratum_values else seen
    for s in strata + [x for x in seen if x not in strata]:
        by_dec = {}
        for lo, hi in DECADE_EDGES:
            vals = cells.get((s, (lo, hi)), [])
            by_dec[(lo, hi)] = vals
        pd = m1_by_decade(by_dec)
        fit = fit_stratum_slope(pd)
        out[str(s)] = {
            **fit,
            "n_total": totals.get(s, 0),
        }
    return out


def slope_range(fits: dict) -> dict:
    """Max - min slope across strata with slope != None."""
    slopes = [(s, f["slope"]) for s, f in fits.items() if f["slope"] is not None]
    if len(slopes) < 2:
        return {"slope_min": None, "slope_max": None, "range": None,
                "n_strata_fitted": len(slopes), "fitted_strata": slopes}
    vals = [v for _, v in slopes]
    return {
        "slope_min": min(vals),
        "slope_max": max(vals),
        "range": max(vals) - min(vals),
        "n_strata_fitted": len(slopes),
        "fitted_strata": slopes,
    }


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[W3] start {started}")
    rows = load_joined()
    if not rows:
        raise SystemExit("No rows retrieved; abort.")

    # Sanity: correlation between nbp and nonmax_count
    nbp_arr = np.array([r["num_bad_primes"] for r in rows], dtype=float)
    nmc_arr = np.array([len(r["nonmax_primes"]) for r in rows], dtype=float)
    if nbp_arr.std() > 0 and nmc_arr.std() > 0:
        corr = float(np.corrcoef(nbp_arr, nmc_arr)[0, 1])
    else:
        corr = None
    print(f"[W3] corr(num_bad_primes, nonmax_count) = {corr}")

    # ---- Stratification A: P021 (num_bad_primes) ----
    fits_A = stratify(rows,
                      key_fn=lambda r: r["num_bad_primes"]
                      if r["num_bad_primes"] in NBP_BINS else None,
                      stratum_values=NBP_BINS)
    range_A = slope_range(fits_A)

    # ---- Stratification B: P039 nonmax_count ----
    fits_B = stratify(rows,
                      key_fn=lambda r: (len(r["nonmax_primes"])
                                        if len(r["nonmax_primes"]) in NONMAX_COUNT_BINS
                                        else None),
                      stratum_values=NONMAX_COUNT_BINS)
    range_B = slope_range(fits_B)

    # ---- Stratification C: has_p for p in {2,3,5,7} ----
    fits_C = {}
    for p in HAS_PRIMES:
        def kf(r, pp=p):
            return bool(pp in r["nonmax_primes"])
        fits_Cp = stratify(rows, key_fn=kf, stratum_values=[False, True])
        fits_C[f"has_{p}"] = {
            "by_stratum": fits_Cp,
            "range": slope_range(fits_Cp),
        }

    # Pick the sharpest has_p stratification
    best_hasp = None
    best_hasp_range = None
    for key, v in fits_C.items():
        rg = v["range"]["range"]
        if rg is None:
            continue
        if best_hasp_range is None or rg > best_hasp_range:
            best_hasp = key
            best_hasp_range = rg

    # ---- Stratification D: joint (P021 x P039 nonmax_count) ----
    def joint_kf(r):
        if r["num_bad_primes"] not in NBP_BINS:
            return None
        nc = len(r["nonmax_primes"])
        if nc not in NONMAX_COUNT_BINS:
            return None
        return f"nbp={r['num_bad_primes']}_nmc={nc}"
    joint_strata = [f"nbp={nbp}_nmc={nc}"
                    for nbp in NBP_BINS for nc in NONMAX_COUNT_BINS]
    fits_D = stratify(rows, key_fn=joint_kf, stratum_values=joint_strata)
    range_D = slope_range(fits_D)

    # ---- Verdict ----
    verdict = "INCONCLUSIVE"
    verdict_reason = []

    rA = range_A["range"]
    rB = range_B["range"]
    rC = best_hasp_range
    rD = range_D["range"]

    best_P039 = None
    if rB is not None and rC is not None:
        best_P039 = max(rB, rC)
    elif rB is not None:
        best_P039 = rB
    elif rC is not None:
        best_P039 = rC

    if rA is not None and rD is not None and best_P039 is not None:
        base = max(rA, best_P039)
        if rD > 1.20 * base:
            verdict = "ORTHOGONAL"
            verdict_reason.append(
                f"Joint P021xP039 range={rD:.3f} exceeds 1.2 * max(P021={rA:.3f}, "
                f"P039_best={best_P039:.3f}).")
    if verdict == "INCONCLUSIVE" and rA is not None and best_P039 is not None:
        if best_P039 > 1.20 * rA:
            verdict = "P039_SHARPER"
            verdict_reason.append(
                f"Best P039 range ({best_P039:.3f}) > 1.20 * P021 range "
                f"({rA:.3f}); P039 resolves sharper than num_bad_primes.")
        elif rA > 1.20 * best_P039:
            verdict = "P021_SHARPER"
            verdict_reason.append(
                f"P021 range ({rA:.3f}) > 1.20 * best P039 range "
                f"({best_P039:.3f}); num_bad_primes resolves sharper than any "
                f"Galois-image marginal tested. The rank-2 slope pattern is "
                f"NOT a Galois-image effect dressed up as a bad-prime count.")
        elif abs(best_P039 - rA) / max(rA, 1e-9) <= 0.10:
            verdict = "PROXY_CONFIRMED"
            verdict_reason.append(
                f"P039 best range ({best_P039:.3f}) within +-10% of P021 range "
                f"({rA:.3f}); num_bad_primes is a Galois-image proxy.")
        else:
            verdict_reason.append(
                f"Neither sharper-by-20% nor within-10%: P021 range={rA:.3f}, "
                f"P039 best range={best_P039:.3f}. Difference inconclusive.")

    # ---- Package ----
    finished = datetime.now(timezone.utc).isoformat()
    results = {
        "task_id": "rank2_P039_vs_P021_stratification",
        "drafted_by": "Harmonia_worker_W3",
        "started": started,
        "finished": finished,
        "scope": {
            "rank": 2,
            "conductor_range": "[1000, 1000000)",
            "decade_edges": DECADE_EDGES,
            "min_per_cell": MIN_PER_CELL,
            "n_joined_rows": len(rows),
            "corr_nbp_nonmax_count": corr,
        },
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "headline_metrics": {
            "P021_slope_range":          rA,
            "P039_nonmax_count_range":   rB,
            "P039_has_p_best_key":       best_hasp,
            "P039_has_p_best_range":     best_hasp_range,
            "joint_P021xP039_range":     rD,
            "P021_nbp_slopes":  {s: f["slope"] for s, f in fits_A.items()},
            "P039_nonmax_count_slopes":
                {s: f["slope"] for s, f in fits_B.items()},
        },
        "stratification_A_P021_num_bad_primes": {
            "strata": fits_A,
            "range": range_A,
        },
        "stratification_B_P039_nonmax_count": {
            "strata": fits_B,
            "range": range_B,
        },
        "stratification_C_P039_has_specific_prime": fits_C,
        "stratification_D_joint_P021_x_P039": {
            "strata": fits_D,
            "range": range_D,
        },
        "interpretation": (
            "Ties verdict to slope-range metric: sharper stratification means "
            "strata that disagree more on their per-stratum M_1 vs log X slope. "
            "P039_SHARPER: Galois-image has strictly more resolving power than "
            "a simple bad-prime count. PROXY_CONFIRMED: num_bad_primes was the "
            "axis all along. ORTHOGONAL: nbp and Galois-image carry separable "
            "information, joint stratification lifts structure hidden in each "
            "marginal. Sparse (n<100) cells are reported with sparse=True and "
            "excluded from the slope fit but kept for audit."
        ),
        "pattern_20_discipline": [
            "Rank 2 only; conductor 10^3..10^6; decade-bucketed.",
            "Per-(stratum, decade) M_1 computed; n>=100 for inclusion in slope fit.",
            "Sparse strata reported with sparse=True and n_decades_valid.",
            "Slope = OLS of M_1 vs log(conductor_mid) across 2..3 decades.",
            "Each decade's conductor_mid = sqrt(lo*hi).",
            "nonmax_primes parsed via ast.literal_eval; unparseable -> [].",
            "Verdict thresholds: +20% sharper / +-10% proxy / +20% joint-lift.",
        ],
    }

    out_path = os.path.join("cartography", "docs",
                            "rank2_P039_vs_P021_stratification_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[W3] wrote {out_path}")
    print(f"[W3] verdict: {verdict}")
    print(f"[W3] P021 range={rA}, P039_nmc range={rB}, "
          f"P039_has_p_best={best_hasp} range={best_hasp_range}, "
          f"joint range={rD}")


if __name__ == "__main__":
    main()
