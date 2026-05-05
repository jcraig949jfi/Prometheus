#!/usr/bin/env python3
"""
Non-CM Euler-product analog of |D|: num_bad_primes stratification.

Hypothesis: within non-CM rank-0 EC, the gap-compression depth varies with
num_bad_primes (omega(N)). Fewer bad primes -> most primes behave with generic
Sato-Tate SU(2); compression depth driven by global structure. Many bad primes ->
more Euler factors are simplified (bad = (1 - a_p p^-s)^-1 with a_p in {-1,0,1}),
potentially changing compression.

Separate from the Tamagawa-mediation test which focused on class_size effects,
this isolates nbp as a candidate non-CM predictor to add to the closure regression.

Output: ergon/results/nbp_split_nonCM.json
"""
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "nbp_split_nonCM.json"
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


def main():
    print("Non-CM num_bad_primes stratification")
    print("=" * 72)

    print("Fetching rank-0 non-CM EC with num_bad_primes + zeros ...")
    t0 = time.time()
    c = psycopg2.connect(**DB)
    cur = c.cursor()
    cur.execute("""
        SELECT e.num_bad_primes::int, e.conductor::float, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND e.cm::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 150000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")

    by_nbp = defaultdict(list)
    for nbp, cond, raw in rows:
        g = local_4gap(parse_zeros(raw))
        if g is None: continue
        by_nbp[int(nbp or 0)].append(g)
    print(f"\n{'nbp':>4} {'n':>8}   {'gap1%':>8} {'gap2%':>8} {'gap3%':>8} {'gap4%':>8} {'gap4-gap1':>10}")

    results = {}
    for nbp in sorted(by_nbp):
        data = by_nbp[nbp]
        if len(data) < 50: continue
        arr = np.array(data)
        variances = [float(arr[:, i].var(ddof=1)) for i in range(4)]
        deficits = [deficit(v, NULL_VAR[i], len(data)) for i, v in enumerate(variances)]
        pcts = [d[0] for d in deficits]
        zs = [d[1] for d in deficits]
        grad = pcts[3] - pcts[0]
        print(f"{nbp:>4} {len(data):>8}   {pcts[0]:>8.1f} {pcts[1]:>8.1f} {pcts[2]:>8.1f} {pcts[3]:>8.1f} {grad:>+10.2f}")
        results[nbp] = {
            'n': len(data),
            'variances': variances,
            'deficits_pct': [round(p, 2) for p in pcts],
            'z_scores': [round(z, 2) for z in zs],
            'gradient_gap4_minus_gap1': round(grad, 2),
        }

    # Spearman correlation between nbp and gap1 deficit / gap4 deficit
    nbps = sorted(results.keys())
    nbp_arr = np.array(nbps)
    g1_arr = np.array([results[n]['deficits_pct'][0] for n in nbps])
    g4_arr = np.array([results[n]['deficits_pct'][3] for n in nbps])
    weights = np.array([results[n]['n'] for n in nbps])

    from scipy import stats
    r1, p1 = stats.spearmanr(nbp_arr, g1_arr)
    r4, p4 = stats.spearmanr(nbp_arr, g4_arr)
    print(f"\nSpearman(nbp, gap1_deficit) = {r1:.3f}  p = {p1:.3g}")
    print(f"Spearman(nbp, gap4_deficit) = {r4:.3f}  p = {p4:.3g}")

    # Weighted Pearson
    def wpearson(x, y, w):
        mx = np.average(x, weights=w); my = np.average(y, weights=w)
        cov = np.average((x - mx)*(y - my), weights=w)
        sx = np.sqrt(np.average((x - mx)**2, weights=w))
        sy = np.sqrt(np.average((y - my)**2, weights=w))
        return cov / (sx * sy) if sx > 0 and sy > 0 else np.nan
    wp1 = wpearson(nbp_arr, g1_arr, weights)
    wp4 = wpearson(nbp_arr, g4_arr, weights)
    print(f"Weighted Pearson(nbp, gap1) = {wp1:.3f}")
    print(f"Weighted Pearson(nbp, gap4) = {wp4:.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'null_var': NULL_VAR,
            'results': {str(k): v for k, v in results.items()},
            'spearman_nbp_gap1': {'rho': float(r1), 'p': float(p1)},
            'spearman_nbp_gap4': {'rho': float(r4), 'p': float(p4)},
            'weighted_pearson_nbp_gap1': float(wp1),
            'weighted_pearson_nbp_gap4': float(wp4),
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
