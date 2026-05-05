#!/usr/bin/env python3
"""
Fast-path: fetch ALL 2,134 CM rank-0 EC with zeros (tight filter, ~seconds).
Compute gap1..gap4 local-4-gap variance, compare to matched-GUE null.
Cross-validates Charon's n=18 finding at n=2134.

Output: ergon/results/cm_only_fast.json
"""
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "cm_only_fast.json"
NULL_VAR = [0.1472, 0.1741, 0.1725, 0.1468]
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


def cell(label, data):
    n = len(data)
    if n < 10:
        print(f"  {label:<40} n={n:>6}  (< 10, skipping)")
        return None
    arr = np.array(data)
    variances = [float(arr[:, i].var(ddof=1)) for i in range(4)]
    s = f"  {label:<40} n={n:>6}  "
    row = {'label': label, 'n': n, 'variances': variances, 'deficits': [], 'z': []}
    for i, v in enumerate(variances):
        pct, z = deficit(v, NULL_VAR[i], n)
        row['deficits'].append(round(pct, 2))
        row['z'].append(round(z, 2))
        s += f"g{i+1} {pct:+5.1f}(z={z:+5.1f})  "
    print(s)
    return row


def main():
    print("CM rank-0 EC fast-path gap analysis")
    print("=" * 80)
    t0 = time.time()
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT e.cm::int, e.conductor::float, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND e.cm::int != 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    print(f"Fetched {len(rows)} CM rank-0 curves in {time.time()-t0:.1f}s")

    # Parse and organize
    by_cm = defaultdict(list)
    by_cond = defaultdict(list)
    all_curves = []
    for cm, cond, raw in rows:
        g = local_4gap(parse_zeros(raw))
        if g is None:
            continue
        by_cm[int(cm)].append(g)
        if cond is not None and cond > 0:
            cq = int(np.clip(math.floor(math.log(cond)), 0, 15))
            by_cond[cq].append(g)
        all_curves.append(g)

    print(f"\n--- Pooled CM rank-0 ---")
    pooled = cell('all CM', all_curves)

    print(f"\n--- Per-CM-discriminant ---")
    per_cm = {}
    for cm_val in sorted(by_cm.keys()):
        per_cm[cm_val] = cell(f'cm = {cm_val}', by_cm[cm_val])

    print(f"\n--- By log(conductor) bin ---")
    per_cond = {}
    for cq in sorted(by_cond):
        per_cond[cq] = cell(f'log_c in [{cq},{cq+1})', by_cond[cq])

    # Non-CM comparison from prior LMFDB 200K run for context
    print(f"\n--- Non-CM reference (from higher_gap_analysis pooled 200K) ---")
    print(f"  non-CM gap1/gap4 deficit ~ 20%/33% (Sha=1 partial avg)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            "null_var": NULL_VAR,
            "n_rows": len(rows),
            "pooled_CM": pooled,
            "per_cm": per_cm,
            "per_cond": per_cond,
            "cm_discriminant_counts": {str(k): len(v) for k, v in by_cm.items()},
        }, f, indent=1, default=str)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
