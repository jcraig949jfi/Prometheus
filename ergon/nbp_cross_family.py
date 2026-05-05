#!/usr/bin/env python3
"""
Test whether nbp sign matches across CM and rank.

Question: is nbp's direction of correlation with compression driven by:
  (a) Symmetry class (O+, O-, U(1)-ish, USp)?
  (b) L-function degree (2 vs 4)?
  (c) Family composition (CM vs non-CM)?

Run nbp-stratified gap1/gap4 deficit on:
  EC rank-0 non-CM (O+)  : PRIOR result rho = +1.0 at bulk
  EC rank-1 non-CM (O-)  : NEW test
  EC rank-0 CM           : NEW test
"""
import json, math, time
from collections import defaultdict
from pathlib import Path
import numpy as np
import psycopg2
from scipy import stats

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "nbp_cross_family.json"
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


def run_family(label, rank, cm_cond, limit=80000):
    print(f"\n--- {label} (rank={rank} cm {cm_cond}) ---", flush=True)
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute(f"""
        SELECT e.num_bad_primes::int, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = {rank} AND e.cm::int {cm_cond}
          AND l.positive_zeros IS NOT NULL AND l.positive_zeros != '[]'
        LIMIT {limit}
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s", flush=True)

    by_nbp = defaultdict(list)
    for nbp, raw in rows:
        g = local_4gap(parse_zeros(raw))
        if g is None: continue
        by_nbp[int(nbp or 0)].append(g)

    result = {}
    nbps_valid = []
    pcts = {0:[], 3:[]}  # just gap1 and gap4
    print(f"  {'nbp':>4} {'n':>7} {'gap1%':>8} {'gap4%':>8}")
    for nbp in sorted(by_nbp):
        data = by_nbp[nbp]
        if len(data) < 50: continue
        arr = np.array(data)
        v = [float(arr[:, i].var(ddof=1)) for i in range(4)]
        deficits = [(1 - v[i] / NULL_VAR[i]) * 100 for i in range(4)]
        result[nbp] = {'n': len(data), 'variances': v, 'deficits_pct': deficits}
        nbps_valid.append(nbp)
        pcts[0].append(deficits[0])
        pcts[3].append(deficits[3])
        print(f"  {nbp:>4} {len(data):>7} {deficits[0]:>+8.2f} {deficits[3]:>+8.2f}")

    # Spearman
    if len(nbps_valid) >= 3:
        r1, p1 = stats.spearmanr(nbps_valid, pcts[0])
        r4, p4 = stats.spearmanr(nbps_valid, pcts[3])
        print(f"  Spearman(nbp, gap1): {r1:+.3f}  p={p1:.3g}")
        print(f"  Spearman(nbp, gap4): {r4:+.3f}  p={p4:.3g}")
        return {'per_nbp': result, 'spearman': {'gap1': {'rho': r1, 'p': p1}, 'gap4': {'rho': r4, 'p': p4}}}
    else:
        print("  Too few bins for Spearman")
        return {'per_nbp': result}


def main():
    print("Cross-family nbp direction test")
    print("=" * 72)

    results = {}
    results['EC_rank1_nonCM'] = run_family('EC rank-1 non-CM (O-)', 1, '= 0', limit=80000)
    results['EC_rank0_CM']    = run_family('EC rank-0 CM',          0, '!= 0', limit=20000)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=1, default=str)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
