"""
rank2_specific_bad_primes.py — Harmonia worker T5.

Question: Does the rank-2 F041a nbp-ladder have a specific-prime axis beneath
it? I.e., does "has prime p in bad_primes" (for p in the Mazur-Kenku list
{2, 3, 5, 7, 11, 13, 17, 23, 37}) carry more slope-separation than bare
num_bad_primes count?

Background (W3 ran by Harmonia worker W3 in rank2_P039_vs_P021_stratification):
  - P021 (num_bad_primes) slope-range at rank 2 = 1.316 (sharpest yet).
  - P039 (Galois l-adic image nonmax_count) range = 0.305 — coarser.
  - has_p over nonmax_primes showed |range| ~ 0.014 for has_2 alone.

T5: look at the REAL bad_primes set (not just nonmax primes).  Does specific-
prime presence in bad_primes give a sharper ladder than the count alone?

Method:
  1. Parse ec_curvedata.bad_primes (text list-of-ints) per row.
  2. Build indicator columns has_p for p in {2,3,5,7,11,13,17,23,37}.
  3. For each indicator and each decade 10^3..10^6, compute mean(leading_term)
     for has_p=True and has_p=False cohorts.
  4. Fit slope of each cohort's mean vs log X across decades. Report
     slope_diff_p = slope[True] - slope[False].
  5. Max-min slope-range across all indicators.
  6. Joint 3-way: (num_bad_primes_bin) x has_2 x has_3 — does it exceed
     pure P021 range of 1.316?

Pattern-20: per-cell n >= 100 for inclusion in slope fit.

Verdict triggers:
  PRIME_p_DOMINANT            — some p has |slope_diff_p| > 1.0.
  3WAY_JOINT_EXCEEDS          — joint (nbp, has_2, has_3) range > 1.316.
  COUNT_REMAINS_SHARPEST      — all slope_diffs < 0.3 in abs and joint
                                does not exceed nbp alone.

Data sources:
  prometheus_fire.zeros.object_zeros (elliptic_curve, leading_term)
  lmfdb.public.ec_curvedata  (num_bad_primes, bad_primes)
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
MIN_DECADES_FOR_SLOPE = 2

NBP_BINS = [1, 2, 3, 4, 5, 6]

# Mazur-Kenku list of torsion-theoretic "special" small primes.
MAZUR_KENKU_PRIMES = [2, 3, 5, 7, 11, 13, 17, 23, 37]

# Reference: W3 P021 nbp-ladder slope-range at rank 2.
W3_P021_RANGE = 1.316


# ------------------------------------------------------------
# IO
# ------------------------------------------------------------
def parse_int_list(text):
    """'[]', '[2, 3]', '[5, 7, 11]' -> list[int]. None/garbage -> []."""
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
    """Join rank-2 zeros x ec_curvedata on lmfdb_label."""
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
    print(f"[T5] zeros rank=2 rows in 10^3..10^6: {len(labels)}")

    nbp_map: dict[str, int] = {}
    bp_map: dict[str, list[int]] = {}
    CHUNK = 5000
    with psycopg2.connect(**LM) as lm:
        for i in range(0, len(labels), CHUNK):
            batch = labels[i:i + CHUNK]
            cur = lm.cursor()
            cur.execute("""
                SELECT lmfdb_label,
                       NULLIF(num_bad_primes, '')::int,
                       bad_primes
                FROM public.ec_curvedata
                WHERE lmfdb_label = ANY(%s)
            """, (batch,))
            for lbl, nbp, bp in cur.fetchall():
                if nbp is None:
                    continue
                nbp_map[lbl] = int(nbp)
                bp_map[lbl] = parse_int_list(bp)

    out = []
    for lbl, (cond, lt) in zr.items():
        if lbl not in nbp_map:
            continue
        out.append({
            "label": lbl,
            "conductor": cond,
            "leading_term": lt,
            "num_bad_primes": nbp_map[lbl],
            "bad_primes": bp_map[lbl],
        })
    print(f"[T5] joined rank=2 rows: {len(out)}")
    return out


# ------------------------------------------------------------
# Stats
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


def stratify(rows, key_fn, stratum_values):
    cells = defaultdict(list)
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


def slope_range(fits):
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
    print(f"[T5] start {started}")
    rows = load_joined()
    if not rows:
        raise SystemExit("No rows; abort.")

    # Prevalence of each tracked prime in bad_primes.
    prevalence = {}
    for p in MAZUR_KENKU_PRIMES:
        cnt = sum(1 for r in rows if p in r["bad_primes"])
        prevalence[p] = {"n_has_p": cnt, "n_total": len(rows),
                         "frac": cnt / max(len(rows), 1)}
    print(f"[T5] prevalence of has_p in bad_primes: "
          + ", ".join(f"{p}:{prevalence[p]['frac']:.3f}"
                      for p in MAZUR_KENKU_PRIMES))

    # ---- 1. has_p marginals ----
    fits_per_p = {}
    for p in MAZUR_KENKU_PRIMES:
        def kf(r, pp=p):
            return bool(pp in r["bad_primes"])
        fp = stratify(rows, key_fn=kf, stratum_values=[False, True])
        rg = slope_range(fp)
        s_true = fp.get("True", {}).get("slope")
        s_false = fp.get("False", {}).get("slope")
        diff = (s_true - s_false) if (s_true is not None and s_false is not None) else None
        fits_per_p[f"has_{p}"] = {
            "prime": p,
            "by_stratum": fp,
            "range": rg,
            "slope_true": s_true,
            "slope_false": s_false,
            "slope_diff": diff,
        }

    # Max abs slope_diff across all tracked primes.
    max_abs_diff = None
    best_p = None
    for key, v in fits_per_p.items():
        d = v["slope_diff"]
        if d is None:
            continue
        ad = abs(d)
        if max_abs_diff is None or ad > max_abs_diff:
            max_abs_diff = ad
            best_p = key

    # Overall slope range across all has_p strata (min slope across any cohort
    # to max slope across any cohort for any prime).
    all_slopes = []
    for key, v in fits_per_p.items():
        for stratum, f in v["by_stratum"].items():
            if f["slope"] is not None:
                all_slopes.append((key, stratum, f["slope"]))
    overall_min = min((s for _,_,s in all_slopes), default=None)
    overall_max = max((s for _,_,s in all_slopes), default=None)
    overall_range = (overall_max - overall_min) if all_slopes else None

    # ---- 2. Plain P021 (num_bad_primes) baseline re-compute ----
    fits_nbp = stratify(rows,
                        key_fn=lambda r: r["num_bad_primes"]
                        if r["num_bad_primes"] in NBP_BINS else None,
                        stratum_values=NBP_BINS)
    range_nbp = slope_range(fits_nbp)

    # ---- 3. Joint 3-way (nbp, has_2, has_3) ----
    def joint3(r):
        nbp = r["num_bad_primes"]
        if nbp not in NBP_BINS:
            return None
        h2 = 2 in r["bad_primes"]
        h3 = 3 in r["bad_primes"]
        return f"nbp={nbp}_h2={int(h2)}_h3={int(h3)}"

    joint_strata = [f"nbp={n}_h2={a}_h3={b}"
                    for n in NBP_BINS for a in (0, 1) for b in (0, 1)]
    fits_joint = stratify(rows, key_fn=joint3, stratum_values=joint_strata)
    range_joint = slope_range(fits_joint)

    # ---- Verdict ----
    verdict = "COUNT_REMAINS_SHARPEST"
    verdict_reason = []

    rJ = range_joint["range"]
    rN = range_nbp["range"]

    # PRIME_p_DOMINANT: any single-prime indicator beats slope_diff > 1.0.
    if max_abs_diff is not None and max_abs_diff > 1.0:
        verdict = f"PRIME_p_DOMINANT ({best_p})"
        verdict_reason.append(
            f"{best_p} slope_diff = {fits_per_p[best_p]['slope_diff']:.3f} "
            f"(|diff|={max_abs_diff:.3f}) exceeds 1.0 ladder threshold.")

    # 3WAY_JOINT_EXCEEDS: joint > W3 reference (or nbp recomputed).
    ref = W3_P021_RANGE
    if rN is not None:
        ref = max(ref, rN)
    if rJ is not None and rJ > ref:
        if verdict.startswith("PRIME_p"):
            verdict_reason.append(
                f"Joint (nbp,h2,h3) range={rJ:.3f} also exceeds P021 ref "
                f"{ref:.3f}.")
        else:
            verdict = "3WAY_JOINT_EXCEEDS"
            verdict_reason.append(
                f"Joint (nbp,h2,h3) range={rJ:.3f} exceeds P021 reference "
                f"{ref:.3f}.")

    if verdict == "COUNT_REMAINS_SHARPEST":
        max_disp = max_abs_diff if max_abs_diff is not None else 0.0
        verdict_reason.append(
            f"No prime yielded |slope_diff| > 1.0 (max |diff| = "
            f"{max_disp:.3f}, on {best_p}) and joint (nbp,h2,h3) range "
            f"({rJ}) did not exceed P021 ref {ref:.3f}. "
            f"num_bad_primes COUNT remains the sharpest rank-2 axis tested."
        )

    # ---- Package ----
    finished = datetime.now(timezone.utc).isoformat()
    results = {
        "task_id": "rank2_specific_bad_prime_stratification",
        "drafted_by": "Harmonia_worker_T5",
        "started": started,
        "finished": finished,
        "scope": {
            "rank": 2,
            "conductor_range": "[1000, 1000000)",
            "decade_edges": DECADE_EDGES,
            "min_per_cell": MIN_PER_CELL,
            "n_joined_rows": len(rows),
            "tracked_primes_mazur_kenku": MAZUR_KENKU_PRIMES,
            "w3_p021_reference_range": W3_P021_RANGE,
        },
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "prevalence_in_bad_primes": prevalence,
        "headline_metrics": {
            "P021_num_bad_primes_range_recomputed": rN,
            "best_specific_prime_indicator":        best_p,
            "best_specific_prime_abs_slope_diff":   max_abs_diff,
            "specific_prime_slope_diffs":           {
                k: v["slope_diff"] for k, v in fits_per_p.items()
            },
            "overall_has_p_cohort_slope_range":     overall_range,
            "joint_nbp_has2_has3_range":            rJ,
        },
        "specific_prime_marginals": fits_per_p,
        "num_bad_primes_baseline": {
            "strata": fits_nbp,
            "range": range_nbp,
        },
        "joint_3way_nbp_has2_has3": {
            "strata": fits_joint,
            "range": range_joint,
        },
        "interpretation": (
            "Tests whether a specific small prime p (from the Mazur-Kenku "
            "set) being a bad prime carries more slope-separation than the "
            "mere count of bad primes. If no |slope_diff_p| > 1.0 and the "
            "joint 3-way (nbp, has_2, has_3) does not beat pure P021's "
            "range (1.316), the rank-2 ladder lives in the COUNT of bad "
            "primes, not in any specific small prime's presence."
        ),
        "pattern_20_discipline": [
            "Rank 2 only; conductor 10^3..10^6; decade-bucketed.",
            "Per-(stratum, decade) M_1 computed; n>=100 for inclusion in fit.",
            "Sparse strata reported with sparse=True and excluded from fit.",
            "Slope = OLS of M_1 vs log(conductor_mid) across <=3 decades.",
            "Each decade's conductor_mid = sqrt(lo*hi).",
            "bad_primes parsed via ast.literal_eval; unparseable -> [].",
        ],
    }

    out_path = os.path.join("cartography", "docs",
                            "rank2_specific_bad_prime_stratification_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[T5] wrote {out_path}")
    print(f"[T5] verdict: {verdict}")
    print(f"[T5] P021(nbp) range={rN}, best_p={best_p} |diff|={max_abs_diff}, "
          f"joint(nbp,h2,h3) range={rJ}")


if __name__ == "__main__":
    main()
