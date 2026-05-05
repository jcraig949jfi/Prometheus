#!/usr/bin/env python3
"""
Rank stratification of F011 gap-index gradient.

Question: is the compression pattern (deficit deepens gap1 -> gap4) rank-specific
to rank-0 EC, or universal across ranks?

Rank-1 EC L-functions vanish at s=1, so the first few zeros are displaced upward.
Expect the gap statistics to differ. Rank-2+ rarer but distinctive.

Sample: rank 0, 1, 2 from ec_curvedata joined to lfunc_lfunctions. Compute
local-4-gap variance per rank, compare to matched-GUE null
(0.1472 / 0.1741 / 0.1725 / 0.1468).

Output: ergon/results/rank_stratification.json
"""
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "rank_stratification.json"
NULL_VAR = [0.1472, 0.1741, 0.1725, 0.1468]
NULL_M = 200000


def parse_zeros(raw):
    if raw is None: return None
    s = str(raw).strip()
    if s in ('','[]','{}','None'): return None
    s = s.replace('{','[').replace('}',']')
    try: return [float(z) for z in json.loads(s)]
    except: return None


def local_4gap(zeros):
    if zeros is None or len(zeros) < 5: return None
    zeros = sorted(zeros)[:5]
    gaps = [zeros[i+1] - zeros[i] for i in range(4)]
    m = np.mean(gaps)
    if m <= 0: return None
    return [g/m for g in gaps]


def deficit(v, null_v, n):
    se = math.sqrt(2*v*v/max(n,2) + 2*null_v*null_v/NULL_M)
    pct = (1 - v/null_v) * 100
    z = (v - null_v) / se if se > 0 else 0
    return pct, z


def fetch(rank_target, limit=100000):
    print(f"  rank={rank_target} fetch (LIMIT {limit})...", flush=True)
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute(f"""
        SELECT e.conductor::float, e.cm::int, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = {rank_target}
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT {limit}
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"    {len(rows)} rows in {time.time()-t0:.0f}s", flush=True)
    return rows


def analyse(rows, label):
    gap_data = [[] for _ in range(4)]
    for cond, cm, raw in rows:
        g = local_4gap(parse_zeros(raw))
        if g is None: continue
        for i, v in enumerate(g):
            gap_data[i].append(v)
    n = len(gap_data[0])
    if n < 50:
        print(f"  {label}: n={n} too small")
        return None
    variances = [float(np.var(g, ddof=1)) for g in gap_data]
    deficits = [deficit(v, NULL_VAR[i], n) for i, v in enumerate(variances)]
    print(f"\n  {label}  n={n}")
    print(f"    gap   var       null      deficit%    z-score")
    for i, (v, (pct, z)) in enumerate(zip(variances, deficits)):
        print(f"    {i+1}     {v:.4f}   {NULL_VAR[i]:.4f}   {pct:+6.1f}     {z:+7.1f}")
    return {
        'label': label, 'n': n,
        'variances': variances,
        'deficits_pct': [round(d[0], 2) for d in deficits],
        'z_scores': [round(d[1], 2) for d in deficits],
    }


def main():
    print("Rank stratification of F011 gap-index gradient")
    print("=" * 72)

    results = {}

    # Rank 0 baseline
    rows_r0 = fetch(0, limit=50000)
    results['rank_0'] = analyse(rows_r0, 'rank = 0 (EC)')

    # Rank 1
    rows_r1 = fetch(1, limit=50000)
    results['rank_1'] = analyse(rows_r1, 'rank = 1 (EC)')

    # Rank 2 (rarer)
    rows_r2 = fetch(2, limit=50000)
    results['rank_2'] = analyse(rows_r2, 'rank = 2 (EC)')

    # Rank 3+ (very rare)
    rows_r3 = fetch(3, limit=10000)
    results['rank_3'] = analyse(rows_r3, 'rank = 3+ (EC)')

    # Summary
    print(f"\n{'='*72}")
    print("SUMMARY -- deficit pattern by rank")
    print(f"{'='*72}")
    print(f"  {'rank':>6} {'n':>8}   {'gap1%':>8} {'gap2%':>8} {'gap3%':>8} {'gap4%':>8} {'gap4-gap1':>10}")
    for r, data in results.items():
        if data is None: continue
        d = data['deficits_pct']
        print(f"  {r:>6} {data['n']:>8}   {d[0]:>8.1f} {d[1]:>8.1f} {d[2]:>8.1f} {d[3]:>8.1f} {d[3]-d[0]:>10.2f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'null_var': NULL_VAR,
            'results': results,
        }, f, indent=1, default=str)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
