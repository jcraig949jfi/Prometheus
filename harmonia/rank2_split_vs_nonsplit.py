"""
rank2_split_vs_nonsplit.py — Harmonia worker U_B.

Question: The F041a rank-2 slope-vs-num_bad_primes ladder lives in the
semistable (multiplicative) half (T3 commit 68225787: slope_range_semistable
0.570 vs slope_range_additive 0.279, common-support nbp=2..5). Multiplicative
reduction splits into SPLIT (Kodaira I_n, a_p=+1) and NON-SPLIT (Kodaira I_n*
or twisted, a_p=-1). Does one subtype carry the ladder, or is it orthogonal?

Data path:
  - lmfdb.public.ec_curvedata has NO direct split/non-split column.
  - lmfdb.public.lfunc_lfunctions.bad_lfactors encodes the local L-factor at
    each bad prime as a list of polynomial coefficients:
       [1]       -> additive      (a_p = 0)
       [1, -1]   -> split mult    (a_p = +1, local factor 1 - T)
       [1, 1]    -> non-split mult (a_p = -1, local factor 1 + T)
  - EC L-functions live per isogeny class; reduction type is an isogeny-class
    invariant, so per-class bad_lfactors applies to every curve in the class.
  - Origin label: 'EllipticCurve/Q/{conductor}/{iso_class_letter}' maps to
    ec_curvedata.lmfdb_iso = '{conductor}.{iso_class_letter}'.

Method:
  1. Load rank=2 rows from zeros.object_zeros, conductor in [10^3, 10^6).
  2. Join ec_curvedata for num_bad_primes, semistable, lmfdb_iso, conductor.
  3. Restrict to semistable=True (T3 established that's where the ladder lives).
  4. Join lfunc_lfunctions.bad_lfactors by iso (group at the class level).
  5. Parse each bad_lfactor; classify curve as:
       all_split      : every bad prime has coefs [1, -1]  (a_p=+1)
       all_nonsplit   : every bad prime has coefs [1, 1]   (a_p=-1)
       mixed          : at least one of each
  6. Stratify each cohort by (nbp, decade), fit slope of mean(leading_term)
     vs log(conductor) per nbp, take slope_range across common-support nbp
     strata.
  7. Verdict on ratios:
       slope_range_split / slope_range_nonsplit > 1.3  -> "split carries"
       slope_range_split / slope_range_nonsplit < 1/1.3 -> "non-split carries"
       otherwise                                       -> "orthogonal to split/non-split"

Pattern 20: n >= 100 per (cohort, decade, nbp) triple before a cell is used.
Pattern 9: sparse cells are surfaced explicitly.
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

DECADE_EDGES = [(1_000, 10_000),
                (10_000, 100_000),
                (100_000, 1_000_000)]
MIN_PER_CELL = 100
NBP_BINS = [1, 2, 3, 4, 5, 6]
COHORTS = ["all_split", "all_nonsplit", "mixed"]

VERDICT_THRESHOLD = 1.3


def parse_semistable(text):
    if text is None:
        return None
    t = text.strip().lower()
    if t in ("true", "t", "1"):
        return True
    if t in ("false", "f", "0"):
        return False
    return None


def classify_bad_lfactors(bad_lfactors_text):
    """Return one of: 'all_split', 'all_nonsplit', 'mixed', 'has_additive',
    or None on parse failure."""
    if bad_lfactors_text is None:
        return None
    try:
        data = ast.literal_eval(bad_lfactors_text)
    except (ValueError, SyntaxError):
        return None
    if not isinstance(data, list) or not data:
        return None
    has_split = False
    has_nonsplit = False
    has_additive = False
    for entry in data:
        if not (isinstance(entry, (list, tuple)) and len(entry) == 2):
            return None
        _, coefs = entry
        if not isinstance(coefs, (list, tuple)):
            return None
        if len(coefs) == 1:
            # [1] -> additive
            has_additive = True
        elif len(coefs) == 2:
            c = coefs[1]
            if c == -1:
                has_split = True
            elif c == 1:
                has_nonsplit = True
            else:
                # Unexpected coefficient
                return None
        else:
            # 3-term L-factor shouldn't happen for EC semistable primes
            return None
    if has_additive:
        # Shouldn't appear on a semistable curve; flag for exclusion
        return "has_additive"
    if has_split and not has_nonsplit:
        return "all_split"
    if has_nonsplit and not has_split:
        return "all_nonsplit"
    if has_split and has_nonsplit:
        return "mixed"
    return None


def load_lfactors_map():
    """Pull iso_label -> bad_lfactors map from lfunc_lfunctions for EC origins.

    origin shape: 'EllipticCurve/Q/{conductor}/{iso_class_letter}'
    iso_label we produce: '{conductor}.{iso_class_letter}'
    """
    lfac = {}
    with psycopg2.connect(**LM) as lm:
        cur = lm.cursor()
        cur.execute("""
            SELECT origin, bad_lfactors
            FROM public.lfunc_lfunctions
            WHERE origin LIKE 'EllipticCurve/Q/%%'
              AND bad_lfactors IS NOT NULL
        """)
        for origin, bf in cur:
            parts = origin.split("/")
            if len(parts) != 4:
                continue
            cond, letter = parts[2], parts[3]
            iso = f"{cond}.{letter}"
            lfac[iso] = bf
    return lfac


def load_joined_rank2():
    """Load rank=2, conductor 10^3..10^6, semistable=True curves with
    split/non-split classification via bad_lfactors."""
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
    print(f"[U_B] rank=2 zeros rows in 10^3..10^6: {len(zr)}")

    labels = list(zr.keys())
    nbp_map = {}
    semi_map = {}
    iso_map = {}
    CHUNK = 5000
    with psycopg2.connect(**LM) as lm:
        for i in range(0, len(labels), CHUNK):
            batch = labels[i:i + CHUNK]
            cur = lm.cursor()
            cur.execute("""
                SELECT lmfdb_label,
                       NULLIF(num_bad_primes, '')::int,
                       semistable,
                       lmfdb_iso
                FROM public.ec_curvedata
                WHERE lmfdb_label = ANY(%s)
            """, (batch,))
            for lbl, nbp, semi, iso in cur.fetchall():
                if nbp is None:
                    continue
                sb = parse_semistable(semi)
                if sb is None:
                    continue
                nbp_map[lbl] = int(nbp)
                semi_map[lbl] = sb
                iso_map[lbl] = iso
    print(f"[U_B] rank=2 ec_curvedata joined: {len(nbp_map)}")

    # All rank-2 rows before semistable filter
    rows_all = []
    for lbl, (cond, lt) in zr.items():
        if lbl not in nbp_map:
            continue
        rows_all.append({
            "label": lbl,
            "conductor": cond,
            "leading_term": lt,
            "num_bad_primes": nbp_map[lbl],
            "semistable": semi_map[lbl],
            "iso": iso_map[lbl],
        })
    n_all = len(rows_all)
    n_semi = sum(1 for r in rows_all if r["semistable"])
    print(f"[U_B] rank=2 joined (any semistable): {n_all}; semistable only: {n_semi}")

    # Restrict to semistable
    rows_semi = [r for r in rows_all if r["semistable"]]

    # Load lfactors map for only the iso classes we need (scan full EC lfunc)
    print(f"[U_B] loading EC L-function bad_lfactors map...")
    lfac_all = load_lfactors_map()
    print(f"[U_B] lfac_all entries: {len(lfac_all)}")

    # Classify each curve
    classified = []
    n_missing_lfac = 0
    n_parse_fail = 0
    n_has_additive = 0
    cohort_counts = defaultdict(int)
    for r in rows_semi:
        iso = r["iso"]
        bf = lfac_all.get(iso)
        if bf is None:
            n_missing_lfac += 1
            continue
        cohort = classify_bad_lfactors(bf)
        if cohort is None:
            n_parse_fail += 1
            continue
        if cohort == "has_additive":
            # Shouldn't happen for semistable=True; skip for cleanliness.
            n_has_additive += 1
            continue
        cohort_counts[cohort] += 1
        classified.append({**r, "cohort": cohort})

    print(f"[U_B] classified: {len(classified)}  "
          f"missing_lfac={n_missing_lfac}  parse_fail={n_parse_fail}  "
          f"has_additive(contradiction)={n_has_additive}")
    print(f"[U_B] cohort counts:")
    for c in COHORTS:
        print(f"       {c}: {cohort_counts[c]}")

    return classified, {
        "n_rank2_zeros": len(zr),
        "n_rank2_joined": n_all,
        "n_rank2_semistable": n_semi,
        "n_missing_lfac": n_missing_lfac,
        "n_parse_fail": n_parse_fail,
        "n_has_additive": n_has_additive,
        "cohort_counts": dict(cohort_counts),
    }


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
        sparse = arr.size < MIN_PER_CELL
        out.append({"lo": lo, "hi": hi, "n": int(arr.size),
                    "log_X_mid": math.log(decade_mid(lo, hi)),
                    "M_1": float(arr.mean()) if arr.size else None,
                    "sparse": bool(sparse)})
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


def stratify_by_nbp(rows):
    """For a cohort, bin by (nbp, decade) -> list[leading_term]."""
    cells = defaultdict(list)
    totals = defaultdict(int)
    for r in rows:
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


def analyse(classified):
    # Partition by cohort
    per_cohort = {c: [r for r in classified if r["cohort"] == c] for c in COHORTS}

    cohort_fits = {}
    for c, rows in per_cohort.items():
        cohort_fits[c] = stratify_by_nbp(rows)

    # Slope ranges per cohort (full support)
    cohort_ranges_full = {c: slope_range_from_nbp_map(cohort_fits[c]) for c in COHORTS}

    # Common-support across all 3 cohorts
    common_keys = []
    for nbp in NBP_BINS:
        k = str(nbp)
        slopes = [cohort_fits[c][k]["slope"] for c in COHORTS]
        if all(s is not None for s in slopes):
            common_keys.append(k)

    cohort_ranges_common = {c: slope_range_from_nbp_map(cohort_fits[c], restrict_keys=common_keys)
                             for c in COHORTS}

    # Also pairwise common between split and nonsplit only (the main comparison)
    sn_common_keys = []
    for nbp in NBP_BINS:
        k = str(nbp)
        if (cohort_fits["all_split"][k]["slope"] is not None
                and cohort_fits["all_nonsplit"][k]["slope"] is not None):
            sn_common_keys.append(k)
    split_range_sn = slope_range_from_nbp_map(cohort_fits["all_split"],
                                               restrict_keys=sn_common_keys)
    nonsplit_range_sn = slope_range_from_nbp_map(cohort_fits["all_nonsplit"],
                                                  restrict_keys=sn_common_keys)

    # Headline ratio
    sr = split_range_sn["range"]
    nr = nonsplit_range_sn["range"]
    if sr is not None and nr is not None and nr > 0:
        ratio_split_over_nonsplit = sr / nr
    else:
        ratio_split_over_nonsplit = None

    # Verdict
    if ratio_split_over_nonsplit is None:
        verdict = "INCONCLUSIVE (insufficient common support)"
        carrier = "insufficient_coverage"
    elif ratio_split_over_nonsplit > VERDICT_THRESHOLD:
        verdict = "split carries the ladder"
        carrier = "split"
    elif ratio_split_over_nonsplit < 1.0 / VERDICT_THRESHOLD:
        verdict = "non-split carries the ladder"
        carrier = "nonsplit"
    else:
        verdict = "orthogonal to split/non-split"
        carrier = "orthogonal"

    # Sparse-cell catalogue
    sparse_cells = []
    cell_coverage = {}
    for c in COHORTS:
        for nbp in NBP_BINS:
            k = str(nbp)
            fit = cohort_fits[c][k]
            cell_coverage[f"cohort={c}_nbp={nbp}"] = {
                "n_total": fit["n_total"],
                "per_decade_n": [(r["lo"], r["hi"], r["n"], r["sparse"])
                                 for r in fit["per_decade"]],
                "n_decades_valid": fit["n_decades_valid"],
            }
            for r in fit["per_decade"]:
                if r["sparse"]:
                    sparse_cells.append({
                        "cohort": c, "nbp": nbp,
                        "decade": [r["lo"], r["hi"]], "n": r["n"],
                    })

    # Per-cohort nbp slope lists for transparency
    per_cohort_slopes = {c: {k: cohort_fits[c][k]["slope"] for k in cohort_fits[c]}
                          for c in COHORTS}

    return {
        "cohort_counts": {c: len(per_cohort[c]) for c in COHORTS},
        "cohort_nbp_slopes": per_cohort_slopes,
        "cohort_ranges_full": cohort_ranges_full,
        "cohort_ranges_common_triple": cohort_ranges_common,
        "common_support_nbp_keys_triple": common_keys,
        "split_vs_nonsplit_common_keys": sn_common_keys,
        "split_range_common_sn": split_range_sn,
        "nonsplit_range_common_sn": nonsplit_range_sn,
        "ratio_split_over_nonsplit": ratio_split_over_nonsplit,
        "verdict": verdict,
        "carrier": carrier,
        "cohort_fits_detail": cohort_fits,
        "cell_coverage": cell_coverage,
        "sparse_cells": sparse_cells,
        "n_sparse_cells": len(sparse_cells),
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[U_B] start {started}")

    classified, data_stats = load_joined_rank2()
    if not classified:
        raise SystemExit("No classified rank-2 semistable rows; abort.")

    analysis = analyse(classified)

    # Re-baseline against T3's marginal semistable slope range
    # T3 reported slope_range_semistable_common = 0.570
    # Our cohort_ranges should bracket that.
    print(f"[U_B] cohort slope ranges (full): "
          f"{ {c: v['range'] for c, v in analysis['cohort_ranges_full'].items()} }")
    print(f"[U_B] split common-support range (vs non-split): "
          f"{analysis['split_range_common_sn']['range']}")
    print(f"[U_B] non-split common-support range (vs split): "
          f"{analysis['nonsplit_range_common_sn']['range']}")
    print(f"[U_B] ratio split/nonsplit: {analysis['ratio_split_over_nonsplit']}")
    print(f"[U_B] verdict: {analysis['verdict']}")

    finished = datetime.now(timezone.utc).isoformat()
    results = {
        "task_id": "rank2_split_vs_nonsplit_multiplicative",
        "drafted_by": "Harmonia_worker_U_B",
        "started": started,
        "finished": finished,
        "scope": {
            "rank": 2,
            "restrict": "semistable=True (per T3 commit 68225787)",
            "conductor_range": "[1000, 1000000)",
            "decade_edges": DECADE_EDGES,
            "min_per_cell": MIN_PER_CELL,
            "nbp_bins": NBP_BINS,
            "cohorts": COHORTS,
            "verdict_threshold": VERDICT_THRESHOLD,
        },
        "data_path": (
            "lmfdb.public.lfunc_lfunctions.bad_lfactors encodes per-bad-prime "
            "local L-factor coefficients. [1,-1]=split multiplicative (a_p=+1), "
            "[1,1]=non-split multiplicative (a_p=-1), [1]=additive. EC L-functions "
            "are per isogeny class (reduction type is class-invariant), joined "
            "via origin='EllipticCurve/Q/{conductor}/{iso_letter}' <-> "
            "ec_curvedata.lmfdb_iso='{conductor}.{iso_letter}'."
        ),
        "data_stats": data_stats,
        "headline": {
            "verdict": analysis["verdict"],
            "carrier": analysis["carrier"],
            "cohort_counts": analysis["cohort_counts"],
            "split_range_common_sn": analysis["split_range_common_sn"]["range"],
            "nonsplit_range_common_sn": analysis["nonsplit_range_common_sn"]["range"],
            "ratio_split_over_nonsplit": analysis["ratio_split_over_nonsplit"],
            "split_vs_nonsplit_common_keys": analysis["split_vs_nonsplit_common_keys"],
            "cohort_ranges_full": {c: v["range"] for c, v in analysis["cohort_ranges_full"].items()},
        },
        "analysis": analysis,
        "interpretation": (
            "T3 established the F041a rank-2 slope-vs-num_bad_primes ladder "
            "lives in the semistable (multiplicative) half. This pass splits "
            "the semistable cohort by per-prime multiplicative subtype: SPLIT "
            "(all bad primes a_p=+1, Kodaira I_n) vs NON-SPLIT (all a_p=-1) "
            "vs MIXED (both subtypes present). The headline ratio compares "
            "slope_range(split) to slope_range(nonsplit) on common nbp "
            "support. ratio>1.3 => SPLIT carries the ladder; ratio<1/1.3 "
            "=> NON-SPLIT carries; otherwise orthogonal. If orthogonal, the "
            "ladder is a count-of-multiplicative-primes effect, not a "
            "root-of-unity-sign effect at those primes. If one side dominates, "
            "the ladder is coupled to the sign pattern of the Frobenius "
            "eigenvalue at multiplicative primes, sharpening the mechanism "
            "beyond 'multiplicative reduction' to a specific subtype."
        ),
        "pattern_20_discipline": [
            "Per-(cohort, decade, nbp) cell reported with n and sparse flag.",
            "Slope fit uses only cells with n>=100.",
            "Sparse cells surfaced as Pattern-9 coverage cliffs.",
            "Decade_mid = sqrt(lo*hi); OLS over valid decades.",
            "Ratio verdict computed on split-vs-nonsplit common nbp support.",
            "bad_lfactors parsed as LMFDB polynomial coefficients; "
            "[1,-1]=split, [1,1]=non-split, [1]=additive (should not appear "
            "on semistable-True curves).",
        ],
    }

    out_path = os.path.join("cartography", "docs",
                            "rank2_split_vs_nonsplit_multiplicative_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[U_B] wrote {out_path}")
    print(f"[U_B] HEADLINE verdict: {analysis['verdict']} "
          f"(ratio={analysis['ratio_split_over_nonsplit']})")


if __name__ == "__main__":
    main()
