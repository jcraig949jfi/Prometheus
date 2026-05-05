#!/usr/bin/env python3
"""
Seed 1 PROPER: Genus-2 curves (USp(4) Sato-Tate) 24-gap scan.

Data: 11,856 rank-0 degree-4 Genus2Curve L-functions (confirmed in LMFDB).
Comparison with rank-0 EC non-CM (SU(2), O+(even)) and CM EC (U(1)-product).

Katz-Sarnak prediction for USp(4) family:
  Edge: different density function than O+ or U. Specific USp edge statistics.
  Bulk: UNIVERSAL sine-kernel (same as all classical groups asymptotically).

Output: ergon/results/g2c_gap_k.json
"""
import json
import math
import time
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "g2c_gap_k.json"
K_MAX = 24


def parse_zeros(raw):
    if raw is None: return None
    s = str(raw).strip()
    if s in ('','[]','{}','None'): return None
    s = s.replace('{','[').replace('}',']')
    try: return [float(z) for z in json.loads(s)]
    except: return None


def local_k_gaps(zeros, kmax=K_MAX):
    if zeros is None or len(zeros) < kmax + 1: return None
    zeros = sorted(zeros)[:kmax + 1]
    gaps = np.array([zeros[i+1] - zeros[i] for i in range(kmax)])
    m = np.mean(gaps)
    if m <= 0: return None
    return gaps / m


def gue_null(kmax, M, N, rng):
    mid = N // 2 - kmax // 2
    out = np.zeros((M, kmax))
    for m in range(M):
        re = rng.standard_normal((N, N))
        im = rng.standard_normal((N, N))
        A = (re + 1j * im) / np.sqrt(2.0)
        H = (A + A.conj().T) / np.sqrt(2.0)
        w = np.sort(np.linalg.eigvalsh(H))
        gaps = np.diff(w)
        local = gaps[mid:mid+kmax]
        lm = local.mean()
        if lm <= 0: continue
        out[m] = local / lm
    return out


def main():
    print("G2C (USp(4)) 24-gap scan — Seed 1 proper")
    print("=" * 72)

    print("Fetching rank-0 Genus2Curve L-functions...")
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT positive_zeros
        FROM lfunc_lfunctions
        WHERE origin LIKE 'Genus2Curve/%'
          AND order_of_vanishing::int = 0
          AND degree::int = 4
          AND positive_zeros IS NOT NULL
          AND positive_zeros != '[]'
        LIMIT 15000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")

    data = []
    for (raw,) in rows:
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        data.append(g)
    data = np.array(data)
    print(f"  {len(data)} G2C L-functions with 24 gaps each")

    print("Generating matched-GUE null (100K)...")
    rng = np.random.default_rng(5050)
    null = gue_null(K_MAX, M=100000, N=40, rng=rng)
    null_var = null.var(axis=0, ddof=1)

    data_var = data.var(axis=0, ddof=1)
    deficits = (1 - data_var / null_var) * 100

    print(f"\n{'k':>3} {'data':>8} {'null':>8} {'deficit%':>9}")
    for k in range(K_MAX):
        print(f"{k+1:>3} {data_var[k]:>8.4f} {null_var[k]:>8.4f} {deficits[k]:>+9.2f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'n_g2c': len(data),
            'deficits_pct': deficits.tolist(),
            'null_var': null_var.tolist(),
            'data_var': data_var.tolist(),
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
