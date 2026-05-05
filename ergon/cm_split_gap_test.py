#!/usr/bin/env python3
"""
F011 mechanism (c) probe — Euler-product family split on rank-0 EC.

Testing whether the gap-index gradient partitions by reduction type / CM structure.
If the Euler product is the structural lever, families with distinct local factors
(CM vs non-CM; multiplicative vs additive reduction) should show different
compression magnitudes.

Split 1: CM vs non-CM (cm IS NOT NULL vs NULL)
Split 2: multiplicative-reduction worst bad prime vs additive

For each split, compute gap1..gap4 variance vs matched-GUE null and report
deficit % per family.

Output: ergon/results/cm_split_gap.json + stdout table.
"""
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "cm_split_gap.json"

NULL_VAR = [0.1472, 0.1741, 0.1725, 0.1468]  # matched-GUE local-4-gap null
NULL_M = 200000


def parse_zeros(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if s in ('', '[]', '{}', 'None'):
        return None
    s = s.replace('{', '[').replace('}', ']')
    try:
        return [float(z) for z in json.loads(s)]
    except Exception:
        return None


def local_4gap(zeros):
    if zeros is None or len(zeros) < 5:
        return None
    zeros = sorted(zeros)[:5]
    gaps = [zeros[i+1] - zeros[i] for i in range(4)]
    m = np.mean(gaps)
    if m <= 0:
        return None
    return [g / m for g in gaps]


def deficit(v, null_v, n):
    se = math.sqrt(2 * v * v / max(n, 2) + 2 * null_v * null_v / NULL_M)
    return ((1 - v / null_v) * 100.0, (v - null_v) / se if se else 0.0)


def cell_report(label, data, null_var=NULL_VAR):
    n = len(data)
    if n < 50:
        print(f"  {label:<40} n={n:>6}  (< 50, skipping)")
        return None
    arr = np.array(data)
    variances = [float(arr[:, i].var(ddof=1)) for i in range(4)]
    row = {'label': label, 'n': n, 'variances': variances, 'deficits_pct': [], 'z_scores': []}
    s = f"  {label:<40} n={n:>6}  "
    for i, v in enumerate(variances):
        pct, z = deficit(v, null_var[i], n)
        row['deficits_pct'].append(round(pct, 2))
        row['z_scores'].append(round(z, 2))
        s += f"g{i+1} {pct:+5.1f}%(z={z:+6.1f})  "
    print(s)
    return row


def fetch(query):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    t0 = time.time()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")
    return rows


def main():
    all_results = {}
    print("=" * 80)
    print("F011 mechanism (c) probe: CM vs non-CM + reduction-type family split")
    print("=" * 80)
    print(f"Matched-GUE null: {NULL_VAR}")
    print()

    # ---- CM split ----
    print("Fetching rank-0 EC: cm, minimal_weierstrass, zeros ...")
    rows = fetch("""
        SELECT e.cm,
               l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 200000
    """)
    cm_curves = []
    non_cm = []
    for cm, raw in rows:
        g = local_4gap(parse_zeros(raw))
        if g is None:
            continue
        if cm is not None and cm != 0:
            cm_curves.append(g)
        else:
            non_cm.append(g)
    print(f"\n--- CM split ---")
    all_results['CM'] = cell_report('CM (cm!=NULL)', cm_curves)
    all_results['non_CM'] = cell_report('non-CM (cm=NULL)', non_cm)

    # ---- Torsion split: as a separate structural axis ----
    print("\nFetching rank-0 EC with torsion + zeros ...")
    rows = fetch("""
        SELECT e.torsion::int, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 200000
    """)
    torsion_bins = defaultdict(list)
    for tor, raw in rows:
        g = local_4gap(parse_zeros(raw))
        if g is None or tor is None:
            continue
        if tor in (1, 2, 3, 4, 5, 6, 7, 8):
            torsion_bins[tor].append(g)
    print("\n--- Torsion split ---")
    for tor in sorted(torsion_bins):
        all_results[f'torsion_{tor}'] = cell_report(f'torsion = {tor}', torsion_bins[tor])

    # ---- Reduction type at worst bad prime ----
    # ec_curvedata has local_data (json) with reduction_type per bad prime.
    # Approximate: use bool_has_multiplicative / has_additive from summary cols if present.
    # Fallback: just num_bad_primes strata (already in tamagawa data, can cross-reference).
    print("\n(reduction-type split requires local_data JSON parse; skipping in v1)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            "null_var": NULL_VAR,
            "null_M": NULL_M,
            "results": all_results,
        }, f, indent=1, default=str)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
