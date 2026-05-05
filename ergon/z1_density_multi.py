#!/usr/bin/env python3
"""
1-level density ruler across multiple families:
  rank-0 EC non-CM  (O+ symmetry)
  rank-1 EC non-CM  (O- symmetry)
  rank-0 EC CM      (mixed/product?)
  rank-0 G2C        (USp(4) symmetry)

For each family, compute unfolded z_1 = z_1 * log(N/2pi) / pi.
USp(4) theoretical z_1 mean is HIGHER than O+ (edge repulsion even stronger).

Output: ergon/results/z1_density_multi.json
"""
import json
import math
import time
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "z1_density_multi.json"


def parse_first_zero(raw):
    if raw is None: return None
    s = str(raw).strip()
    if s in ('','[]','{}','None'): return None
    s = s.replace('{','[').replace('}',']')
    try:
        vals = json.loads(s)
        return float(vals[0]) if vals else None
    except: return None


def unfold(z1, N):
    if N is None or N <= 3: return None
    return z1 * math.log(N / (2 * math.pi)) / math.pi


def fetch_ec(rank, cm_cond):
    """cm_cond: '= 0' or '!= 0'"""
    print(f"ec rank={rank} cm {cm_cond} ...", flush=True)
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute(f"""
        SELECT e.conductor::float, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = {rank}
          AND e.cm::int {cm_cond}
          AND l.positive_zeros IS NOT NULL AND l.positive_zeros != '[]'
        LIMIT 15000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"   {len(rows)} rows in {time.time()-t0:.0f}s", flush=True)
    return rows


def fetch_g2c():
    print("g2c rank-0 ...", flush=True)
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT conductor::float, positive_zeros
        FROM lfunc_lfunctions
        WHERE origin LIKE 'Genus2Curve/%'
          AND order_of_vanishing::int = 0
          AND degree::int = 4
          AND positive_zeros IS NOT NULL AND positive_zeros != '[]'
        LIMIT 15000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"   {len(rows)} rows in {time.time()-t0:.0f}s", flush=True)
    return rows


def report(label, rows, degree=2):
    """degree=2 for EC, 4 for g2c (affects mean-spacing formula)."""
    unf = []
    raw = []
    for cond, zraw in rows:
        z1 = parse_first_zero(zraw)
        if z1 is None or cond is None or cond <= 3: continue
        # For degree d L-function, mean spacing ~ 2pi / (d * log(N/2pi))
        # so unfolded z1 = z1 * d * log(N/2pi) / (2pi)
        mean_spacing = 2 * math.pi / (degree * math.log(cond / (2 * math.pi)))
        if mean_spacing <= 0: continue
        unf.append(z1 / mean_spacing)
        raw.append(z1)
    if not unf:
        return None
    unf = np.array(unf); raw = np.array(raw)
    r = {
        'label': label,
        'n': len(unf),
        'degree': degree,
        'raw_mean': float(raw.mean()),
        'raw_std': float(raw.std()),
        'unf_mean': float(unf.mean()),
        'unf_std': float(unf.std()),
        'unf_median': float(np.median(unf)),
    }
    print(f"\n  {label}  n={len(unf)}  degree={degree}")
    print(f"    raw z1 mean={r['raw_mean']:.4f} std={r['raw_std']:.4f}")
    print(f"    unfolded z1: mean={r['unf_mean']:.4f} std={r['unf_std']:.4f} median={r['unf_median']:.4f}")
    return r


def main():
    print("1-level density multi-family ruler")
    print("=" * 72)

    families = []
    families.append(report('EC_rank0_nonCM (O+)', fetch_ec(0, '= 0'), degree=2))
    families.append(report('EC_rank1_nonCM (O-)', fetch_ec(1, '= 0'), degree=2))
    families.append(report('EC_rank0_CM (mixed)', fetch_ec(0, '!= 0'), degree=2))
    families.append(report('G2C_rank0 (USp4)', fetch_g2c(), degree=4))

    # Summary table
    print(f"\n{'family':<30} {'n':>7} {'unf_z1_mean':>12} {'unf_z1_std':>11}")
    for f in families:
        if f is None: continue
        print(f"  {f['label']:<28} {f['n']:>7} {f['unf_mean']:>12.4f} {f['unf_std']:>11.4f}")

    # ratios to rank-0 O+
    baseline = next((f for f in families if f and f['label'].startswith('EC_rank0_nonCM')), None)
    if baseline:
        print(f"\n  Ratios to rank-0 non-CM (O+) baseline mean={baseline['unf_mean']:.4f}:")
        for f in families:
            if f is None or f is baseline: continue
            ratio = f['unf_mean'] / baseline['unf_mean']
            print(f"    {f['label']}: {ratio:.4f}x")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({'families': [fa for fa in families if fa]}, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
