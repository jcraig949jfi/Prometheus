#!/usr/bin/env python3
"""
G2C num_bad_primes stratification — test mechanism (c) Euler-arithmetic in USp(4).

If the nbp → compression mechanism is UNIVERSAL (not symmetry-class-specific),
it should hold across EC (O+) AND G2C (USp(4)). This test confirms.

JOIN g2c_curves (has bad_primes list) to lfunc_lfunctions via
origin='Genus2Curve/Q/<cond>/<class>' ← label like '<cond>.<class>.<cond>.1'.

Output: ergon/results/g2c_nbp.json
"""
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2
from scipy import stats

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "g2c_nbp.json"
NULL_VAR = [0.1472, 0.1741, 0.1725, 0.1468]


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
    return [g / m for g in gaps]


def parse_bad_primes(raw):
    if raw is None: return 0
    s = str(raw).strip()
    try:
        return len(json.loads(s.replace("'", '"')))
    except Exception:
        return 0


def main():
    print("G2C nbp stratification (Euler-arithmetic in USp(4))")
    print("=" * 72)

    print("Fetching G2C rank-0 curves + bad_primes JOIN L-functions...")
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT g.bad_primes, g.cond, l.positive_zeros
        FROM g2c_curves g
        JOIN lfunc_lfunctions l
          ON l.origin = 'Genus2Curve/Q/' || g.cond || '/' || split_part(g.label, '.', 2)
        WHERE g.analytic_rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
          AND l.degree::int = 4
        LIMIT 15000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")

    by_nbp = defaultdict(list)
    for bp_raw, cond, zraw in rows:
        nbp = parse_bad_primes(bp_raw)
        g = local_4gap(parse_zeros(zraw))
        if g is None: continue
        by_nbp[nbp].append(g)

    print(f"\n{'nbp':>4} {'n':>7}   {'gap1%':>8} {'gap2%':>8} {'gap3%':>8} {'gap4%':>8}")
    results = {}
    nbps = []
    pcts = {i:[] for i in range(4)}
    for nbp in sorted(by_nbp):
        data = by_nbp[nbp]
        if len(data) < 50: continue
        arr = np.array(data)
        variances = [float(arr[:, i].var(ddof=1)) for i in range(4)]
        deficits = [(1 - v / NULL_VAR[i]) * 100 for i, v in enumerate(variances)]
        results[nbp] = {
            'n': len(data),
            'variances': variances,
            'deficits_pct': deficits,
        }
        nbps.append(nbp)
        for i in range(4):
            pcts[i].append(deficits[i])
        print(f"{nbp:>4} {len(data):>7}   {deficits[0]:>+8.2f} {deficits[1]:>+8.2f} {deficits[2]:>+8.2f} {deficits[3]:>+8.2f}")

    # Spearman
    print(f"\nSpearman(nbp, deficit) on 4-gap scale:")
    for k in range(4):
        if len(nbps) >= 3:
            r, p = stats.spearmanr(nbps, pcts[k])
            print(f"  gap{k+1}: rho = {r:+.3f}  p = {p:.3g}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'null_var': NULL_VAR,
            'per_nbp': {str(k): v for k, v in results.items()},
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
