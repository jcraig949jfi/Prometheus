#!/usr/bin/env python3
"""
CM nbp re-pool at coarser bins (Aporia wind-down directive 1776914593795).

Test Aporia's pre-registered prediction: CM should sign with O+ (positive rho)
because Hecke characters of imaginary quadratic fields decompose into O-type.

Coarse bins to dodge n<50 per bin at detailed granularity:
  low_nbp:  nbp in {1, 2}
  mid_nbp:  nbp in {3, 4}
  high_nbp: nbp >= 5

Output: ergon/results/cm_nbp_repool.json
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
OUT = Path(__file__).resolve().parent / "results" / "cm_nbp_repool.json"
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
    return [g/m for g in gaps]


def nbp_bin(n):
    if n <= 2: return 'low_nbp'
    if n <= 4: return 'mid_nbp'
    return 'high_nbp'


def main():
    print("CM nbp re-pool at coarser bins")
    print("=" * 72)

    print("Fetching ALL CM rank-0 EC ...")
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT e.cm::int, e.num_bad_primes::int, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0 AND e.cm::int != 0
          AND l.positive_zeros IS NOT NULL AND l.positive_zeros != '[]'
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")

    by_bin = defaultdict(list)
    for cm, nbp, raw in rows:
        g = local_4gap(parse_zeros(raw))
        if g is None or nbp is None: continue
        by_bin[nbp_bin(int(nbp))].append(g)

    print(f"\n{'bin':>10} {'n':>6}   {'gap1%':>8} {'gap2%':>8} {'gap3%':>8} {'gap4%':>8}")
    results = {}
    bin_order = ['low_nbp', 'mid_nbp', 'high_nbp']
    gap1_means = []
    gap4_means = []
    bin_labels_num = []
    for bin_name in bin_order:
        data = by_bin.get(bin_name, [])
        n = len(data)
        if n < 30:
            print(f"  {bin_name:<10}  n={n}  (< 30, noted)")
            continue
        arr = np.array(data)
        variances = [float(arr[:,i].var(ddof=1)) for i in range(4)]
        deficits = [(1 - v/NULL_VAR[i]) * 100 for i,v in enumerate(variances)]
        results[bin_name] = {
            'n': n,
            'variances': variances,
            'deficits_pct': deficits,
        }
        print(f"  {bin_name:<10}  n={n:>5}   {deficits[0]:>+8.2f} {deficits[1]:>+8.2f} {deficits[2]:>+8.2f} {deficits[3]:>+8.2f}")
        gap1_means.append(deficits[0])
        gap4_means.append(deficits[3])
        bin_labels_num.append({'low_nbp': 1, 'mid_nbp': 2, 'high_nbp': 3}[bin_name])

    if len(bin_labels_num) >= 3:
        r1, p1 = stats.spearmanr(bin_labels_num, gap1_means)
        r4, p4 = stats.spearmanr(bin_labels_num, gap4_means)
        print(f"\nSpearman(coarse_nbp, deficit):")
        print(f"  gap1: rho = {r1:+.3f}  p = {p1:.3g}")
        print(f"  gap4: rho = {r4:+.3f}  p = {p4:.3g}")
        # Compare to Aporia pre-registered: CM should sign with O+ (+rho)
        verdict_gap1 = "matches O+ (+)" if r1 > 0.3 else "matches USp (-)" if r1 < -0.3 else "inconclusive"
        verdict_gap4 = "matches O+ (+)" if r4 > 0.3 else "matches USp (-)" if r4 < -0.3 else "inconclusive"
        print(f"\nAporia pre-reg (CM sign with O+ / positive rho):")
        print(f"  gap1 verdict: {verdict_gap1}")
        print(f"  gap4 verdict: {verdict_gap4}")
        results['spearman'] = {
            'gap1_rho': float(r1), 'gap1_p': float(p1),
            'gap4_rho': float(r4), 'gap4_p': float(p4),
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=1, default=str)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
