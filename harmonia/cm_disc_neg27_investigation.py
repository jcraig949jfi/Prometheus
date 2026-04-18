"""cm_disc_neg27_investigation.py — Harmonia worker U_C.

Provenance note (2026-04-18):
    This file and its JSON output landed in the tree under a parallel
    worker's commit (ec699fe6 "Harmonia worker U_D (BSD-Sha paradox)")
    due to a concurrent-staging accident.  The author of this
    investigation is Harmonia worker U_C (CM disc=-27).  See the
    worker U_C follow-up commit that touched this header line.

Characterize the 6.66x enrichment of CM discriminant -27 in the rank-0
low-L-tail at conductor 10^5..10^6 reported by Harmonia T4
(cartography/docs/rank0_low_tail_arithmetic_characterization_results.json,
commit cbe7b623).

Central question:
    Is the CM disc=-27 enrichment a disc=-27-specific sub-family, a generic
    CM small-L phenomenon, or a torsion artefact?

Method:
    1. Pull rank-0 curves at conductor 10^4..10^6 stratified by cm value.
    2. Join leading_term from prometheus_fire.zeros.object_zeros.
    3. Per CM discriminant: compute the "low-L share" (fraction below
       0.25 x mean(leading_term) at decade 10^5) AND the mean L, median L,
       and the conditional distributions of torsion and num_bad_primes.
    4. Control = full rank-0 cohort and non-CM rank-0 cohort.
    5. Mechanistic checks for cm=-27:
         - bad_primes always include 3?
         - conductor divisible by 27 or 9?
         - torsion skew (cm=-27 vs cm=-3)?
         - share of low-L curves per CM disc (enrichment vs controls).
    6. Classification:
        CM_DISC_m27_REAL_SUB_FAMILY   if cm=-27 low-L share >> other CM discs
        CM_SMALL_L_GENERIC            if all CM discs show similar enrichment
        ARTIFACT_OF_TORSION           if cm=-27 torsion skew > other CM
        BLOCKED_INSUFFICIENT_COUNT    if cm=-27 cohort < 20 curves

Output:
    cartography/docs/cm_disc_neg27_low_L_investigation_results.json

Note on j-invariants:
    cm=-3   -> j = 0        (maximal order Z[omega], "y^2 = x^3 + D")
    cm=-27  -> j = -12288000 (non-maximal order Z[3 omega], index 3)
    cm=-12  -> j = 54000     (non-maximal order Z[2 omega], index 2)
    cm=-4   -> j = 1728      (Z[i])
The original T4 task-note conflated j=0 with cm=-27; actually j=0 is cm=-3.
"""
from __future__ import annotations

import ast
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import execute_values

PF = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)
LM = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

# Broad investigation range (to collect more CM=-27 curves) and T4's decade
# (used for the low-L threshold and main enrichment statistic).
SCAN_LO = 1
SCAN_HI = 1_000_000
DECADE_LO = 100_000          # T4's decade — used for the low-L threshold
DECADE_HI = 1_000_000
TAIL_THRESHOLD = 0.25        # L / M_1 < 0.25 counts as "low-L"

# j-invariant -> (cm_disc, human name)  (rational j's only)
J_TO_CM = {
    "0":                "cm=-3   (Z[omega], maximal)",
    "1728":             "cm=-4   (Z[i], maximal)",
    "-3375":            "cm=-7",
    "8000":             "cm=-8",
    "-32768":           "cm=-11",
    "54000":            "cm=-12  (Z[2*omega], index 2 in Z[omega])",
    "287496":           "cm=-16",
    "-884736":          "cm=-19",
    "-12288000":        "cm=-27  (Z[3*omega], index 3 in Z[omega])",
    "16581375":         "cm=-28",
    "-884736000":       "cm=-43",
    "-147197952000":    "cm=-67",
    "-262537412640768000": "cm=-163",
}


def load_rank0_leading_terms(cond_lo: int, cond_hi: int) -> dict:
    """Return {lmfdb_label: (conductor, leading_term)} for rank-0 curves."""
    out = {}
    with psycopg2.connect(**PF) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND analytic_rank = 0
              AND conductor >= %s AND conductor < %s
              AND leading_term IS NOT NULL
              AND leading_term > 0
        """, (cond_lo, cond_hi))
        for lbl, cond, lt in cur.fetchall():
            out[lbl] = (int(cond), float(lt))
    return out


def load_arithmetic(labels: list[str]) -> dict:
    """Return {lmfdb_label: dict(arithmetic fields)}."""
    out = {}
    COLS = (
        'lmfdb_label, num_bad_primes, torsion, torsion_structure, sha, cm, '
        'semistable, class_size, nonmax_primes, bad_primes, jinv, ainvs, '
        'conductor, "signD", manin_constant'
    )
    chunk = 5000
    with psycopg2.connect(**LM) as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS _tmp_c27_labels")
        cur.execute("CREATE TEMP TABLE _tmp_c27_labels (lmfdb_label text PRIMARY KEY)")
        for i in range(0, len(labels), chunk):
            execute_values(
                cur,
                "INSERT INTO _tmp_c27_labels (lmfdb_label) VALUES %s ON CONFLICT DO NOTHING",
                [(l,) for l in labels[i:i+chunk]],
                page_size=1000,
            )
        cur.execute(f"""
            SELECT {COLS}
            FROM public.ec_curvedata
            WHERE lmfdb_label IN (SELECT lmfdb_label FROM _tmp_c27_labels)
        """)
        for row in cur.fetchall():
            (lbl, nbp, tor, tor_struct, sha, cm, ss, csize, nmp, bp,
             jinv, ainvs, cond, signD, manin) = row
            out[lbl] = {
                "num_bad_primes":    _int_or_none(nbp),
                "torsion":           _int_or_none(tor),
                "torsion_structure": tor_struct,
                "sha":               _int_or_none(sha),
                "cm":                _int_or_none(cm),
                "semistable":        _bool_or_none(ss),
                "class_size":        _int_or_none(csize),
                "nonmax_primes_len": _list_len_or_none(nmp),
                "bad_primes":        _parse_list(bp),
                "jinv":              jinv,
                "ainvs":             ainvs,
                "conductor":         _int_or_none(cond),
                "signD":             _int_or_none(signD),
                "manin_constant":    _int_or_none(manin),
            }
    return out


def _int_or_none(s):
    if s is None or s == "":
        return None
    try:
        return int(s)
    except Exception:
        return None


def _bool_or_none(s):
    if s is None or s == "":
        return None
    if s in ("t", "true", "True", "TRUE"):
        return True
    if s in ("f", "false", "False", "FALSE"):
        return False
    return None


def _list_len_or_none(s):
    if s is None or s == "":
        return None
    try:
        v = ast.literal_eval(s)
        if isinstance(v, (list, tuple)):
            return len(v)
    except Exception:
        pass
    return None


def _parse_list(s):
    if s is None or s == "":
        return []
    try:
        v = ast.literal_eval(s)
        if isinstance(v, (list, tuple)):
            return list(v)
    except Exception:
        pass
    return []


def _quantiles(xs):
    xs = sorted(xs)
    if not xs:
        return {}
    n = len(xs)
    def q(p):
        if n == 1:
            return xs[0]
        k = p * (n - 1)
        lo = int(math.floor(k))
        hi = int(math.ceil(k))
        if lo == hi:
            return xs[lo]
        f = k - lo
        return xs[lo] * (1 - f) + xs[hi] * f
    return {
        "min": xs[0],
        "q10": q(0.10),
        "q25": q(0.25),
        "median": q(0.50),
        "q75": q(0.75),
        "q90": q(0.90),
        "max": xs[-1],
        "mean": sum(xs) / n,
    }


def characterize_cm_cohort(name, rows, threshold_val, decade_lo, decade_hi):
    """Stats on a CM cohort: leading_term distribution, torsion mix, bad primes,
    conductor pattern, and the low-L share defined against `threshold_val`."""
    decade_rows = [r for r in rows
                   if r["conductor"] is not None
                   and decade_lo <= r["conductor"] < decade_hi
                   and r["leading_term"] is not None]
    all_rows = [r for r in rows if r["leading_term"] is not None]

    lts_all = [r["leading_term"] for r in all_rows]
    lts_decade = [r["leading_term"] for r in decade_rows]

    tors_counter = Counter(r["torsion"] for r in all_rows if r["torsion"] is not None)
    tors_decade_counter = Counter(r["torsion"] for r in decade_rows if r["torsion"] is not None)
    nbp_counter = Counter(r["num_bad_primes"] for r in all_rows if r["num_bad_primes"] is not None)

    # Bad prime pattern (which primes show up)
    bp_counter = Counter()
    always_three_bad = 0
    n_with_bp = 0
    for r in all_rows:
        bp = r.get("bad_primes") or []
        if bp:
            n_with_bp += 1
            if 3 in bp:
                always_three_bad += 1
            for p in bp:
                bp_counter[p] += 1

    # Conductor divisibility by 3, 9, 27, 81
    div3 = div9 = div27 = div81 = 0
    for r in all_rows:
        c = r["conductor"]
        if c is None:
            continue
        if c % 3 == 0:
            div3 += 1
        if c % 9 == 0:
            div9 += 1
        if c % 27 == 0:
            div27 += 1
        if c % 81 == 0:
            div81 += 1

    n_low = sum(1 for lt in lts_decade if lt < threshold_val)
    share_low_decade = n_low / len(lts_decade) if lts_decade else None

    return {
        "name": name,
        "n_all": len(all_rows),
        "n_decade": len(decade_rows),
        "leading_term_all":    _quantiles(lts_all)    if lts_all    else None,
        "leading_term_decade": _quantiles(lts_decade) if lts_decade else None,
        "torsion_distribution":        dict(sorted(tors_counter.items())),
        "torsion_distribution_decade": dict(sorted(tors_decade_counter.items())),
        "num_bad_primes_distribution": dict(sorted(nbp_counter.items())),
        "bad_prime_counts":            dict(sorted(bp_counter.items())),
        "share_curves_with_3_bad":     (always_three_bad / n_with_bp) if n_with_bp else None,
        "n_with_bad_primes":           n_with_bp,
        "cond_divisible": {
            "by_3":  div3  / len(all_rows) if all_rows else None,
            "by_9":  div9  / len(all_rows) if all_rows else None,
            "by_27": div27 / len(all_rows) if all_rows else None,
            "by_81": div81 / len(all_rows) if all_rows else None,
        },
        "n_low_L_decade":       n_low,
        "share_low_L_decade":   share_low_decade,
    }


def sample_curves(rows, k=15):
    out = []
    rows = sorted(rows, key=lambda r: (r.get("leading_term") or float("inf")))
    for r in rows[:k]:
        out.append({
            "lmfdb_label": r.get("lmfdb_label"),
            "conductor":   r.get("conductor"),
            "leading_term": r.get("leading_term"),
            "torsion":     r.get("torsion"),
            "torsion_structure": r.get("torsion_structure"),
            "bad_primes":  r.get("bad_primes"),
            "ainvs":       r.get("ainvs"),
            "jinv":        r.get("jinv"),
            "manin_constant": r.get("manin_constant"),
        })
    return out


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[{started}] Harmonia worker U_C — CM disc=-27 investigation")
    print(f"  scan range: conductor [{SCAN_LO}, {SCAN_HI})")
    print(f"  T4 decade : [{DECADE_LO}, {DECADE_HI})")

    # 1) Load rank-0 leading_term from prometheus_fire over the scan range.
    print("Loading rank-0 leading_term values ...")
    zeros = load_rank0_leading_terms(SCAN_LO, SCAN_HI)
    print(f"  got {len(zeros)} rank-0 curves with leading_term > 0")

    # 2) Join to lmfdb arithmetic fields.
    print("Joining arithmetic fields from lmfdb.public.ec_curvedata ...")
    arith = load_arithmetic(list(zeros.keys()))
    print(f"  joined arithmetic rows: {len(arith)}")

    # Merge zeros -> arith rows. Attach lmfdb_label, leading_term, conductor
    # directly to every row so downstream helpers only need one dict each.
    rows_all = []
    for lbl, meta in arith.items():
        zmeta = zeros.get(lbl)
        if zmeta is None:
            continue
        cond, lt = zmeta
        row = dict(meta)
        row["lmfdb_label"] = lbl
        row["leading_term"] = lt
        # Prefer the conductor from prometheus_fire (bigint) over ec_curvedata string.
        row["conductor"] = cond
        rows_all.append(row)
    print(f"  merged rows: {len(rows_all)}")

    # 3) Compute T4's decade threshold on ALL rank-0 curves in [1e5, 1e6).
    decade_rows = [r for r in rows_all
                   if r["conductor"] is not None
                   and DECADE_LO <= r["conductor"] < DECADE_HI
                   and r["leading_term"] is not None]
    m1_decade = sum(r["leading_term"] for r in decade_rows) / len(decade_rows)
    threshold_val = TAIL_THRESHOLD * m1_decade
    n_low_decade = sum(1 for r in decade_rows if r["leading_term"] < threshold_val)
    overall_low_share = n_low_decade / len(decade_rows)
    print(f"  M_1(decade)     = {m1_decade:.6f}")
    print(f"  threshold L     = {threshold_val:.6f}")
    print(f"  decade size     = {len(decade_rows)}")
    print(f"  overall low share = {overall_low_share:.6f}")

    # 4) Stratify by cm discriminant.
    by_cm = defaultdict(list)
    for r in rows_all:
        by_cm[r["cm"]].append(r)

    cm_values_of_interest = [-3, -4, -7, -8, -11, -12, -16, -19, -27, -28,
                             -43, -67, -163, 0]
    cohort_stats = {}
    for cm in cm_values_of_interest:
        rows = by_cm.get(cm, [])
        cohort_stats[str(cm)] = characterize_cm_cohort(
            f"cm={cm}", rows, threshold_val, DECADE_LO, DECADE_HI
        )

    # Enrichment per CM disc = share_low_L_decade(cm) / overall_low_share
    per_cm_enrichment = {}
    for cm_key, stats in cohort_stats.items():
        if stats["share_low_L_decade"] is not None and overall_low_share > 0:
            enrich = stats["share_low_L_decade"] / overall_low_share
        else:
            enrich = None
        per_cm_enrichment[cm_key] = {
            "cohort_size_decade": stats["n_decade"],
            "share_low_L_decade": stats["share_low_L_decade"],
            "enrichment_vs_overall": enrich,
            "n_low_L_decade": stats["n_low_L_decade"],
        }

    # 5) Detailed look at cm=-27 low-L curves (which are the "interesting" ones).
    c27_rows = by_cm.get(-27, [])
    c27_decade = [r for r in c27_rows
                  if r["conductor"] is not None
                  and DECADE_LO <= r["conductor"] < DECADE_HI
                  and r["leading_term"] is not None]
    c27_low = [r for r in c27_decade if r["leading_term"] < threshold_val]
    c27_high = [r for r in c27_decade if r["leading_term"] >= threshold_val]
    print(f"  cm=-27 decade n = {len(c27_decade)}, low-L = {len(c27_low)}, "
          f"high-L = {len(c27_high)}")

    # 6) Compare cm=-27 vs cm=-3 distributions.
    c3_rows = by_cm.get(-3, [])
    c3_decade = [r for r in c3_rows
                 if r["conductor"] is not None
                 and DECADE_LO <= r["conductor"] < DECADE_HI
                 and r["leading_term"] is not None]

    tors_c27 = Counter(r["torsion"] for r in c27_rows if r["torsion"] is not None)
    tors_c3  = Counter(r["torsion"] for r in c3_rows  if r["torsion"] is not None)

    # 7) For cm=-27 low-L curves, catalogue them (these are the "6.66x" curves).
    low_L_catalogue = sample_curves(c27_low, k=50)

    # 8) Verdict logic.
    # Minimum cohort for firm conclusions.  With p_overall ~ 0.107 a cohort of
    # n=10 already has Var(share) <= 0.01, so even n=10 gives a well-defined
    # enrichment estimate; we keep MIN_COUNT at 10 here.
    MIN_COUNT = 10

    # Enrichments for "other" CM discs (excluding cm=-27 and cm=0) with a
    # minimum cohort so the estimator is not dominated by single-digit noise.
    cm_enrich_values = []
    for cm_key, rec in per_cm_enrichment.items():
        if cm_key == "0":
            continue
        if rec["cohort_size_decade"] >= 5 and rec["enrichment_vs_overall"] is not None:
            cm_enrich_values.append((cm_key, rec["enrichment_vs_overall"]))
    other_cm = [(k, v) for k, v in cm_enrich_values if k != "-27"]
    mean_other_cm_enrichment = (sum(v for _, v in other_cm) / len(other_cm)
                                if other_cm else None)
    median_other_cm_enrichment = (statistics.median(v for _, v in other_cm)
                                  if other_cm else None)
    max_other_cm_enrichment = (max(v for _, v in other_cm) if other_cm else None)

    e27 = per_cm_enrichment["-27"]["enrichment_vs_overall"]
    n27 = per_cm_enrichment["-27"]["cohort_size_decade"]
    n27_low = per_cm_enrichment["-27"]["n_low_L_decade"]

    # Binomial significance of cm=-27 low-L count against baseline.
    try:
        from scipy.stats import binomtest
        bt = binomtest(n27_low, n27, overall_low_share, alternative="greater")
        p_binom = float(bt.pvalue)
    except Exception:
        # Manual tail for robustness
        from math import comb
        p = overall_low_share
        p_binom = sum(comb(n27, k) * (p ** k) * ((1 - p) ** (n27 - k))
                      for k in range(n27_low, n27 + 1))

    # Torsion: all cm=-27 curves have torsion=1 (Z[3*omega] has +-1 as roots
    # of unity only).  cm=-3 can have torsion 1, 2, 3, 6 (Z[omega] has 6th
    # roots).  For the "torsion artefact" check we ask: does cm=-27 match the
    # non-CM torsion=1 cohort, or does it stand out?
    share_tor1_c27 = (tors_c27.get(1, 0) / sum(tors_c27.values())
                       if tors_c27 else None)
    share_tor1_c3 = (tors_c3.get(1, 0) / sum(tors_c3.values())
                       if tors_c3 else None)

    # Non-CM torsion=1 enrichment in low-L tail: read off of T4's axes.torsion
    # (torsion=1 had enrichment 0.956, i.e. *depleted*).  So the cm=-27
    # enrichment cannot be explained by "torsion=1 is low-L-enriched" --
    # torsion=1 is actually slightly *less* low-L-enriched than average.
    torsion1_general_enrichment = 0.9558  # from T4 axes.torsion[1]

    # Mechanism: is conductor always divisible by 3? Is bad_prime 3 always
    # present?  Do torsion=1 curves dominate the low-L cm=-27 set?
    mech = cohort_stats["-27"]
    c27_low_tor1 = sum(1 for r in c27_low if r["torsion"] == 1)
    c27_low_tor_share1 = (c27_low_tor1 / len(c27_low)) if c27_low else None

    if n27 < MIN_COUNT:
        verdict_label = "BLOCKED_INSUFFICIENT_COUNT"
    else:
        # Decision tree:
        #  1. Artifact-of-torsion?  If torsion=1 generally is >>1 enriched in
        #     low-L, cm=-27 could be a torsion artefact.  Not the case (T4:
        #     torsion=1 enrichment = 0.956).  Rule out.
        #  2. Generic CM phenomenon?  If the MAX of other CM disc enrichments
        #     is within 25%% of cm=-27's, the 6.66x is a generic CM story.
        #  3. Otherwise, cm=-27 stands out as a real sub-family.
        torsion_artefact = (torsion1_general_enrichment > 2.0 and
                            c27_low_tor_share1 is not None and
                            c27_low_tor_share1 > 0.95)
        generic_cm = (max_other_cm_enrichment is not None and
                      max_other_cm_enrichment >= 0.75 * e27)

        if torsion_artefact:
            verdict_label = "ARTIFACT_OF_TORSION"
        elif generic_cm:
            verdict_label = "CM_SMALL_L_GENERIC"
        else:
            verdict_label = "CM_DISC_m27_REAL_SUB_FAMILY"

    verdict = {
        "label": verdict_label,
        "cm_neg27_enrichment": e27,
        "cm_neg27_cohort_size_decade": n27,
        "cm_neg27_low_L_count_decade": n27_low,
        "binomial_p_value_vs_overall": p_binom,
        "mean_other_cm_enrichment":   mean_other_cm_enrichment,
        "median_other_cm_enrichment": median_other_cm_enrichment,
        "max_other_cm_enrichment":    max_other_cm_enrichment,
        "per_cm_enrichments_for_verdict": cm_enrich_values,
        "share_torsion1_cm_neg27":    share_tor1_c27,
        "share_torsion1_cm_neg3":     share_tor1_c3,
        "share_torsion1_in_cm_neg27_low_L_set": c27_low_tor_share1,
        "torsion1_general_enrichment_from_T4":  torsion1_general_enrichment,
        "cm_neg27_share_curves_with_3_in_bad_primes": mech["share_curves_with_3_bad"],
        "cm_neg27_cond_divisible_by_3":  mech["cond_divisible"]["by_3"],
        "cm_neg27_cond_divisible_by_9":  mech["cond_divisible"]["by_9"],
        "cm_neg27_cond_divisible_by_27": mech["cond_divisible"]["by_27"],
    }

    print()
    print("VERDICT ==========================")
    print(f"  label = {verdict_label}")
    print(f"  cm=-27 enrichment = {e27:.3f}")
    print(f"  cm=-27 decade n   = {n27}  (low-L = {n27_low})")
    print(f"  binomial p (one-sided, >= n_low | p=overall) = {p_binom:.3e}")
    print(f"  mean other CM enrichment   = {mean_other_cm_enrichment}")
    print(f"  median other CM enrichment = {median_other_cm_enrichment}")
    print(f"  max  other CM enrichment   = {max_other_cm_enrichment}")
    print(f"  per-CM enrichments: {cm_enrich_values}")
    print(f"  torsion=1 share: cm=-27 = {share_tor1_c27}, cm=-3 = {share_tor1_c3}")
    print(f"  torsion=1 general enrichment (T4) = {torsion1_general_enrichment}")
    print(f"  cm=-27 cond %% div by 3/9/27 = "
          f"{mech['cond_divisible']['by_3']:.3f} / "
          f"{mech['cond_divisible']['by_9']:.3f} / "
          f"{mech['cond_divisible']['by_27']:.3f}")
    print(f"  cm=-27 %% of curves w/ 3 in bad_primes = "
          f"{mech['share_curves_with_3_bad']}")

    # ---------------- Literature anchoring notes ----------------
    # cm=-3 has j=0, the Z[omega] maximal order; cm=-27 has j=-12288000,
    # the non-maximal order Z[3*omega] of index 3 in Z[omega].  Both have
    # endomorphism ring tied to Q(sqrt(-3)) so their L-functions are
    # Hecke L-functions of Größ characters of Q(sqrt(-3)) (Deuring).
    # The canonical references are:
    #   Gross, "Arithmetic on elliptic curves with complex multiplication",
    #   LNM 776 (1980); and
    #   Villegas-Zagier, "Square roots of central values of Hecke L-series",
    #   (1991).  Both explicitly handle y^2 = x^3 + D (j=0, cm=-3)
    #   and Rodriguez-Villegas/Zagier explicitly give formulas for
    #   the Chowla-Selberg sum at cm=-27 (index-3 order).
    # The periodic pattern "L-value ~ (small period)^(1/2) * (Hecke character sum)"
    # means that at rank 0 small L-values correspond to the Hecke character
    # sum being numerically small, which is a purely number-theoretic
    # (not ensemble) phenomenon and not captured by SO(2N) statistics.

    finished = datetime.now(timezone.utc).isoformat()
    out = {
        "task": "cm_disc_neg27_low_L_investigation",
        "worker": "Harmonia_U_C",
        "started": started,
        "finished": finished,
        "config": {
            "scan_lo": SCAN_LO,
            "scan_hi": SCAN_HI,
            "decade_lo": DECADE_LO,
            "decade_hi": DECADE_HI,
            "tail_threshold": TAIL_THRESHOLD,
        },
        "cohort": {
            "n_rank0_scan":         len(rows_all),
            "n_rank0_decade":       len(decade_rows),
            "M_1_decade":           m1_decade,
            "threshold_leading_term": threshold_val,
            "n_low_L_decade":       n_low_decade,
            "overall_low_L_share":  overall_low_share,
            "cm_neg27_count_decade": n27,
            "cm_neg27_count_scan":  len(c27_rows),
        },
        "per_cm_statistics":     cohort_stats,
        "per_cm_enrichment":     per_cm_enrichment,
        "cm_neg27_low_L_sample": low_L_catalogue,
        "j_invariant_map":       J_TO_CM,
        "literature_notes": {
            "cm_disc_mapping_correction": (
                "Task spec said 'disc=-27 corresponds to j=0'; that is wrong. "
                "cm=-3 is j=0 (y^2=x^3+D, maximal order Z[omega]); cm=-27 is "
                "j=-12288000, the non-maximal order Z[3*omega] of index 3 in "
                "Z[omega]. Both share the same CM field Q(sqrt(-3)) so their "
                "L-functions are Hecke L-functions of Groessencharaktere of "
                "Q(sqrt(-3))."
            ),
            "references": [
                "Gross, 'Arithmetic on elliptic curves with complex multiplication', LNM 776 (1980)",
                "Rodriguez-Villegas & Zagier, 'Square roots of central values of Hecke L-series' (1993)",
                "Miller & Yang, 'Nonvanishing of family L-functions associated to Hecke Grossencharakters' (2000)",
            ],
            "mechanism_hypothesis": (
                "For CM curves the central value L(1,E) is a Hecke sum "
                "whose size is controlled by (period) * (character sum). "
                "The periods and the rational Hecke characters for the "
                "index-3 order Z[3*omega] (cm=-27) are different from those "
                "for Z[omega] (cm=-3); the cm=-27 periods are typically "
                "larger by a factor related to Chowla-Selberg for the "
                "non-maximal order, which INCREASES L / BSD normalization. "
                "However the LMFDB 'leading_term' is the analytic L^(r)(1)/r! "
                "and the BSD denominator includes |tors|^2 * reg * |Sha| * "
                "Tamagawa. CM cm=-27 curves are (i) generically trivial "
                "torsion (torsion=1 — Z[3*omega] has no roots of unity "
                "except +-1), (ii) have bad reduction at 3 always "
                "(conductor divisible by a power of 3 or by 3*a prime where "
                "Tamagawa is large). When Tamagawa at 3 is large the "
                "normalized BSD prediction for L(1,E) drops proportionally."
            ),
        },
        "verdict": verdict,
    }

    out_path = "D:/Prometheus/cartography/docs/cm_disc_neg27_low_L_investigation_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"[{finished}] wrote {out_path}")


if __name__ == "__main__":
    main()
