#!/usr/bin/env python3
"""
1-level density test: does the FIRST positive zero height z_1 differ between
rank-0 and rank-1 EC families as Katz-Sarnak O+(even) vs O-(odd) predicts?

For rank-r EC L-function, the mean spacing near zero is pi/log(N/2pi) where
N = conductor. Unfolded z_1 = z_1 / (pi/log(N/2pi)) = z_1 * log(N/2pi) / pi.

Katz-Sarnak prediction:
  rank-0 family O+(even): z_1 density has a REPULSION from 0 (first zero pushed up).
  rank-1 family O-(odd):  z_1 density has EVEN LARGER REPULSION from 0 (SO(2N+1)
                          has a forced 0 eigenvalue so nearest neighbors are pushed).
So <z_1> should be LARGER for rank-1 than rank-0 at matched conductor.

Output: ergon/results/z1_density.json
"""
import json
import math
import time
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "z1_density.json"


def parse_first_zero(raw):
    if raw is None: return None
    s = str(raw).strip()
    if s in ('','[]','{}','None'): return None
    s = s.replace('{','[').replace('}',']')
    try:
        vals = json.loads(s)
        if not vals: return None
        return float(vals[0])
    except: return None


def unfold(z1, N):
    """Normalize z_1 by mean spacing at that height."""
    if N is None or N < 3:
        return None
    return z1 * math.log(N / (2 * math.pi)) / math.pi


def fetch(rank):
    print(f"rank={rank} ...", flush=True)
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute(f"""
        SELECT e.conductor::float, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = {rank}
          AND e.cm::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 30000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"   {len(rows)} rows in {time.time()-t0:.0f}s", flush=True)
    return rows


def main():
    print("1-level density test: z_1 for rank-0 vs rank-1 non-CM EC")
    print("=" * 72)

    results = {}
    for rank in [0, 1]:
        rows = fetch(rank)
        unfolded = []
        raw_z1 = []
        for cond, zraw in rows:
            z1 = parse_first_zero(zraw)
            if z1 is None or cond is None or cond <= 0:
                continue
            u = unfold(z1, cond)
            if u is None: continue
            unfolded.append(u)
            raw_z1.append(z1)
        if not unfolded: continue
        unfolded = np.array(unfolded)
        raw_z1 = np.array(raw_z1)
        results[rank] = {
            'n': len(unfolded),
            'z1_raw_mean': float(raw_z1.mean()),
            'z1_raw_std': float(raw_z1.std()),
            'z1_raw_median': float(np.median(raw_z1)),
            'z1_unfolded_mean': float(unfolded.mean()),
            'z1_unfolded_std': float(unfolded.std()),
            'z1_unfolded_median': float(np.median(unfolded)),
        }
        print(f"\n  rank={rank}  n={len(unfolded)}")
        print(f"    raw z1:       mean={results[rank]['z1_raw_mean']:.4f}  std={results[rank]['z1_raw_std']:.4f}  median={results[rank]['z1_raw_median']:.4f}")
        print(f"    unfolded z1:  mean={results[rank]['z1_unfolded_mean']:.4f}  std={results[rank]['z1_unfolded_std']:.4f}  median={results[rank]['z1_unfolded_median']:.4f}")

    # Comparison
    if 0 in results and 1 in results:
        r0 = results[0]['z1_unfolded_mean']
        r1 = results[1]['z1_unfolded_mean']
        ratio = r1 / r0 if r0 > 0 else float('nan')
        print(f"\nKatz-Sarnak prediction: rank-1 <z_1_unfolded> should be > rank-0 <z_1_unfolded>.")
        print(f"  rank-0: {r0:.4f}")
        print(f"  rank-1: {r1:.4f}")
        print(f"  ratio r1/r0: {ratio:.4f}")
        delta = r1 - r0
        se = math.sqrt(results[0]['z1_unfolded_std']**2 / results[0]['n']
                       + results[1]['z1_unfolded_std']**2 / results[1]['n'])
        z = delta / se if se > 0 else float('nan')
        print(f"  delta: {delta:+.4f}   SE: {se:.4f}   z: {z:+.1f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
