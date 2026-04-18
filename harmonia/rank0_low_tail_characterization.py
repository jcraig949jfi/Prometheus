"""rank0_low_tail_characterization.py — Harmonia worker T4.

Characterize the arithmetic structure of rank-0 curves with unusually small
L(1,E) at conductor decade [10^5, 10^6).

Background (W5, threads_A_low_tail_B_nbp6_outlier):
    Empirical Pr[L/M_1 < 0.25] at rank 0 is 0.107 at decade 10^5 — orders of
    magnitude below the SO(2N) Haar prediction at matched N_eff (~0.37).  The
    deviation is MONOTONE GROWING across decades, but the finite-N regime is
    clearly still well below Haar.  Are these low-tail curves a distinct
    arithmetic sub-family (e.g. CM-rich, high-torsion, small-regulator) or
    a generic finite-N CFKRS artifact?

Question:
    On (decade=[1e5,1e6), analytic_rank=0, leading_term>0) we define
        low_tail  := {curves with leading_term / M_1(decade) < 0.25},
        normal    := complement.
    For each of six arithmetic axes we compare the proportion of a given
    property in low_tail vs the overall (union) proportion and report the
    enrichment ratio.  Pattern-5 gate:
        any axis shows enrichment > 2.0x or < 0.5x → SUB_FAMILY_FOUND,
        all axes enrichments stay within [0.8, 1.25] → GENERIC_TAIL_NO_ENRICHMENT,
        otherwise → MIXED.

Axes:
    1. num_bad_primes (integer)
    2. torsion (integer; Mazur values 1..12, 14, 15, 16)
    3. sha (integer; should be a square; ~1 for most rank-0)
    4. cm (integer; 0 for non-CM; -3,-4,-7,-8,-11,-19,-43,-67,-163 for CM)
    5. semistable (bool)
    6. nonmax_primes length (Galois ℓ-adic non-maximal image)
    7. class_size (bonus — isogeny class cardinality)

Output: cartography/docs/rank0_low_tail_arithmetic_characterization_results.json
"""
from __future__ import annotations

import ast
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2

PF = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)
LM = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

DECADE_LO = 100_000
DECADE_HI = 1_000_000
TAIL_THRESHOLD = 0.25   # L/M_1 < this


def load_rank0_leading_terms() -> dict:
    """Return {lmfdb_label: (conductor, leading_term)} for rank-0, decade=[1e5,1e6)."""
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
        """, (DECADE_LO, DECADE_HI))
        for lbl, cond, lt in cur.fetchall():
            out[lbl] = (int(cond), float(lt))
    return out


def load_arithmetic(labels: list[str]) -> dict:
    """Return {lmfdb_label: dict(arithmetic fields)} by chunked IN queries."""
    out = {}
    COLS = (
        "lmfdb_label, num_bad_primes, torsion, sha, cm, semistable, "
        "class_size, nonmax_primes"
    )
    chunk = 5000
    with psycopg2.connect(**LM) as conn:
        cur = conn.cursor()
        # Use a temporary table for fast membership
        cur.execute("DROP TABLE IF EXISTS _tmp_lt_labels")
        cur.execute("CREATE TEMP TABLE _tmp_lt_labels (lmfdb_label text PRIMARY KEY)")
        from psycopg2.extras import execute_values
        for i in range(0, len(labels), chunk):
            execute_values(
                cur,
                "INSERT INTO _tmp_lt_labels (lmfdb_label) VALUES %s ON CONFLICT DO NOTHING",
                [(l,) for l in labels[i:i+chunk]],
                page_size=1000,
            )
        cur.execute(f"""
            SELECT {COLS}
            FROM public.ec_curvedata
            WHERE lmfdb_label IN (SELECT lmfdb_label FROM _tmp_lt_labels)
        """)
        for row in cur.fetchall():
            lbl, nbp, tor, sha, cm, ss, csize, nmp = row
            out[lbl] = {
                "num_bad_primes": _int_or_none(nbp),
                "torsion": _int_or_none(tor),
                "sha": _int_or_none(sha),
                "cm": _int_or_none(cm),
                "semistable": _bool_or_none(ss),
                "class_size": _int_or_none(csize),
                "nonmax_primes_len": _list_len_or_none(nmp),
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


def compare_distributions(
    low_tail_rows: list[dict],
    all_rows: list[dict],
    field: str,
    bins: list | None = None,
) -> dict:
    """Return per-value counts and proportions for low-tail vs overall; compute
    enrichment ratio low_tail_share / overall_share per value."""
    def _tally(rows):
        c = Counter()
        n_present = 0
        for r in rows:
            v = r.get(field)
            if v is None:
                continue
            n_present += 1
            c[v] += 1
        return c, n_present

    lt_counts, lt_n = _tally(low_tail_rows)
    all_counts, all_n = _tally(all_rows)

    if bins is None:
        keys = sorted(set(lt_counts) | set(all_counts), key=lambda k: (k is None, k))
    else:
        keys = bins

    per_value = {}
    max_enrich = 0.0
    min_enrich = float("inf")
    max_enrich_key = None
    min_enrich_key = None
    for k in keys:
        lt_c = int(lt_counts.get(k, 0))
        al_c = int(all_counts.get(k, 0))
        lt_share = lt_c / lt_n if lt_n > 0 else 0.0
        al_share = al_c / all_n if all_n > 0 else 0.0
        # Need enough mass to make enrichment meaningful: require >=20 low-tail and
        # >= 0.005 overall share to include this bin in min/max enrichment.
        enrich = (lt_share / al_share) if al_share > 0 else None
        per_value[str(k)] = {
            "low_tail_count": lt_c,
            "low_tail_share": lt_share,
            "overall_count": al_c,
            "overall_share": al_share,
            "enrichment_ratio": enrich,
        }
        if enrich is not None and lt_c >= 20 and al_share >= 0.005:
            if enrich > max_enrich:
                max_enrich = enrich
                max_enrich_key = k
            if enrich < min_enrich:
                min_enrich = enrich
                min_enrich_key = k
    return {
        "field": field,
        "low_tail_n_present": lt_n,
        "overall_n_present": all_n,
        "per_value": per_value,
        "max_enrichment_ratio": max_enrich if max_enrich_key is not None else None,
        "max_enrichment_key": str(max_enrich_key) if max_enrich_key is not None else None,
        "min_enrichment_ratio": min_enrich if min_enrich_key is not None else None,
        "min_enrichment_key": str(min_enrich_key) if min_enrich_key is not None else None,
    }


def compare_binary(low_tail_rows: list[dict], all_rows: list[dict],
                   field: str, pred) -> dict:
    """Compare proportion satisfying a predicate (True/False) across cohorts."""
    def _tally(rows):
        n = 0; t = 0
        for r in rows:
            v = r.get(field)
            if v is None:
                continue
            n += 1
            if pred(v):
                t += 1
        return n, t
    lt_n, lt_t = _tally(low_tail_rows)
    all_n, all_t = _tally(all_rows)
    lt_share = lt_t / lt_n if lt_n > 0 else 0.0
    all_share = all_t / all_n if all_n > 0 else 0.0
    enrich = (lt_share / all_share) if all_share > 0 else None
    return {
        "field": field,
        "low_tail_true_count": lt_t,
        "low_tail_n": lt_n,
        "low_tail_share": lt_share,
        "overall_true_count": all_t,
        "overall_n": all_n,
        "overall_share": all_share,
        "enrichment_ratio": enrich,
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[{started}] Loading rank-0 leading terms at decade [{DECADE_LO}, {DECADE_HI})")
    zeros = load_rank0_leading_terms()
    labels = list(zeros.keys())
    print(f"  n rank-0 curves with leading_term > 0: {len(labels)}")

    # Decade-level M_1 = mean of leading_term
    lts = np.asarray([zeros[l][1] for l in labels], dtype=float)
    m1 = float(lts.mean())
    threshold_val = TAIL_THRESHOLD * m1
    print(f"  M_1(decade) = {m1:.6f},  threshold = {threshold_val:.6f}")

    low_tail_labels = [l for l in labels if zeros[l][1] < threshold_val]
    n_low = len(low_tail_labels)
    n_all = len(labels)
    print(f"  low-tail n = {n_low}  ({100.0 * n_low / n_all:.2f}%)")

    print("Joining arithmetic fields from lmfdb.public.ec_curvedata...")
    arith = load_arithmetic(labels)
    print(f"  arithmetic rows joined: {len(arith)}")

    all_rows = [arith[l] for l in labels if l in arith]
    low_tail_rows = [arith[l] for l in low_tail_labels if l in arith]
    print(f"  all_rows={len(all_rows)}, low_tail_rows={len(low_tail_rows)}")

    # --------------------------------------------------------------------
    axes = {}

    # 1. num_bad_primes — integer bins
    axes["num_bad_primes"] = compare_distributions(low_tail_rows, all_rows,
                                                     "num_bad_primes")
    # 2. torsion — Mazur: 1,2,3,4,5,6,7,8,9,10,12, and 2-torsion blocks 14,15,16
    axes["torsion"] = compare_distributions(low_tail_rows, all_rows, "torsion")

    # 3. sha — should be 1 for most rank-0; rare departures
    axes["sha"] = compare_distributions(low_tail_rows, all_rows, "sha")

    # 4. cm — 0 vs non-zero (a single binary gate) AND per-value distribution
    axes["cm"] = compare_distributions(low_tail_rows, all_rows, "cm")
    axes["cm_is_CM"] = compare_binary(low_tail_rows, all_rows, "cm",
                                       lambda v: v != 0)

    # 5. semistable — binary
    axes["semistable"] = compare_binary(low_tail_rows, all_rows, "semistable",
                                          lambda v: v is True)

    # 6. nonmax_primes length — integer
    axes["nonmax_primes_len"] = compare_distributions(low_tail_rows, all_rows,
                                                        "nonmax_primes_len")
    axes["nonmax_primes_nonempty"] = compare_binary(low_tail_rows, all_rows,
                                                      "nonmax_primes_len",
                                                      lambda v: (v or 0) > 0)

    # 7. class_size — integer
    axes["class_size"] = compare_distributions(low_tail_rows, all_rows,
                                                 "class_size")

    # ---------------- Pattern-5 verdict ----------------
    GATE_HIGH = 2.0
    GATE_LOW = 0.5
    NEUTRAL_HIGH = 1.25
    NEUTRAL_LOW = 0.8

    enrichments = []
    for key, ax in axes.items():
        if "max_enrichment_ratio" in ax and ax["max_enrichment_ratio"] is not None:
            enrichments.append((key + "::max@" + str(ax["max_enrichment_key"]),
                                ax["max_enrichment_ratio"]))
        if "min_enrichment_ratio" in ax and ax["min_enrichment_ratio"] is not None:
            enrichments.append((key + "::min@" + str(ax["min_enrichment_key"]),
                                ax["min_enrichment_ratio"]))
        if "enrichment_ratio" in ax and ax["enrichment_ratio"] is not None:
            # binary axes
            enrichments.append((key, ax["enrichment_ratio"]))

    any_sub_family = []
    all_generic = True
    for k, r in enrichments:
        if r >= GATE_HIGH or (r > 0 and r <= GATE_LOW):
            any_sub_family.append((k, r))
        if not (NEUTRAL_LOW <= r <= NEUTRAL_HIGH):
            all_generic = False

    if any_sub_family:
        verdict = "SUB_FAMILY_FOUND"
    elif all_generic:
        verdict = "GENERIC_TAIL_NO_ENRICHMENT"
    else:
        verdict = "MIXED"

    # Top 5 most extreme enrichments
    ranked = sorted(enrichments, key=lambda t: abs(math.log(max(t[1], 1e-9))),
                    reverse=True)[:8]

    finished = datetime.now(timezone.utc).isoformat()
    out = {
        "task": "rank0_low_tail_arithmetic_characterization",
        "worker": "Harmonia_T4",
        "started": started,
        "finished": finished,
        "config": {
            "decade_lo": DECADE_LO,
            "decade_hi": DECADE_HI,
            "tail_threshold": TAIL_THRESHOLD,
            "gate_high": GATE_HIGH,
            "gate_low": GATE_LOW,
            "neutral_band": [NEUTRAL_LOW, NEUTRAL_HIGH],
            "min_cell_count_for_enrichment": 20,
            "min_overall_share_for_enrichment": 0.005,
        },
        "cohort": {
            "n_rank0_total": n_all,
            "n_low_tail": n_low,
            "low_tail_fraction": n_low / n_all,
            "M_1_decade": m1,
            "threshold_leading_term": threshold_val,
            "n_arithmetic_joined": len(arith),
            "n_all_rows_used": len(all_rows),
            "n_low_tail_rows_used": len(low_tail_rows),
        },
        "axes": axes,
        "top_enrichments": [{"key": k, "enrichment": r} for k, r in ranked],
        "verdict": {
            "label": verdict,
            "any_sub_family_hits": [{"key": k, "enrichment": r}
                                     for k, r in any_sub_family],
            "all_axes_within_neutral_band_0_8_to_1_25": all_generic,
            "notes": (
                "Enrichment = low_tail_share(value) / overall_share(value). "
                "Values > 2 or < 0.5 flag sub-family structure; [0.8,1.25] "
                "flags generic finite-N tail. Binary axes (cm_is_CM, "
                "semistable, nonmax_primes_nonempty) have a single enrichment "
                "number; count/distribution axes report max and min across "
                "values with enough support (>=20 low-tail hits and overall "
                "share >= 0.5%%)."
            ),
        },
    }

    out_path = "D:/Prometheus/cartography/docs/rank0_low_tail_arithmetic_characterization_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[{finished}] wrote {out_path}")
    print(f"VERDICT: {verdict}")
    if any_sub_family:
        print("Sub-family axes:")
        for k, r in any_sub_family:
            print(f"  {k}: enrichment = {r:.3f}")
    print("Top 8 enrichments (|log|-ranked):")
    for k, r in ranked:
        print(f"  {k}: {r:.3f}")


if __name__ == "__main__":
    main()
