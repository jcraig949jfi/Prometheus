#!/usr/bin/env python3
"""
Export unfolded z_1 per curve for Figure 2 (Katz-Sarnak 1-level density histogram).

4 families, ~75K rows total:
  EC rank-0 non-CM (O+):       ~15K
  EC rank-1 non-CM (O-):       ~15K
  EC CM rank-0 (mixed):         2K
  G2C rank-0 (USp(4)):         ~12K
"""
import json
import math
import time
import csv
from pathlib import Path

import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path("F:/prometheus/ergon/results/paper_artifacts/figure2_unfolded_z1.csv")


def parse_first_zero(raw):
    if raw is None: return None
    s = str(raw).strip()
    if s in ('','[]','{}','None'): return None
    s = s.replace('{','[').replace('}',']')
    try:
        vals = json.loads(s)
        return float(vals[0]) if vals else None
    except: return None


def unfold(z1, N, d):
    if N is None or N <= 3: return None
    return z1 * d * math.log(N / (2 * math.pi)) / (2 * math.pi)


def fetch_ec(rank, cm_cond, limit=15000):
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute(f"""
        SELECT e.conductor::float, l.positive_zeros
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
    print(f"  rank={rank} cm {cm_cond}: {len(rows)} rows in {time.time()-t0:.0f}s")
    return rows


def fetch_g2c(limit=15000):
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute(f"""
        SELECT conductor::float, positive_zeros
        FROM lfunc_lfunctions
        WHERE origin LIKE 'Genus2Curve/%'
          AND order_of_vanishing::int = 0
          AND degree::int = 4
          AND positive_zeros IS NOT NULL AND positive_zeros != '[]'
        LIMIT {limit}
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  g2c rank-0: {len(rows)} rows in {time.time()-t0:.0f}s")
    return rows


def main():
    print("Figure 2: unfolded z_1 per curve, 4 families")
    print("=" * 72)

    families = {}
    print("Fetching EC rank-0 non-CM...")
    families["EC_rank0_nonCM_OPlus"] = (fetch_ec(0, "= 0"), 2)
    print("Fetching EC rank-1 non-CM...")
    families["EC_rank1_nonCM_OMinus"] = (fetch_ec(1, "= 0"), 2)
    print("Fetching EC rank-0 CM...")
    families["EC_rank0_CM"] = (fetch_ec(0, "!= 0"), 2)
    print("Fetching G2C...")
    families["G2C_rank0_USp4"] = (fetch_g2c(), 4)

    # Compute unfolded z_1
    per_fam = {}
    for fam, (rows, deg) in families.items():
        vals = []
        for cond, raw in rows:
            z1 = parse_first_zero(raw)
            if z1 is None: continue
            u = unfold(z1, cond, deg)
            if u is None: continue
            vals.append(u)
        per_fam[fam] = vals
        print(f"  {fam}: {len(vals)} parsed, degree={deg}")

    # Export as long-format CSV (family, unfolded_z1)
    OUT.parent.mkdir(exist_ok=True, parents=True)
    with open(OUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["family", "unfolded_z1"])
        for fam, vals in per_fam.items():
            for v in vals:
                w.writerow([fam, round(v, 6)])
    total = sum(len(v) for v in per_fam.values())
    print(f"\nSaved {total} rows to {OUT}")


if __name__ == "__main__":
    main()
