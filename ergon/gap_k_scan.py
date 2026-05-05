#!/usr/bin/env python3
"""
Aporia Seed 2: extend gap-k analysis for k in [1, 20] on rank-0 EC.

Question: is the gap4 compression (~33% deficit) a characteristic scale, or does
compression continue deepening monotonically through k=20?

Two scenarios pre-registered:
  (A) MONOTONE: compression deepens with k beyond k=4. Would imply a structural
      "all-scales" constraint.
  (B) CHARACTERISTIC SCALE: compression peaks around some k* then relaxes back
      toward GUE. Would imply a specific mesoscopic constraint.

Setup: for each rank-0 EC curve with >=25 stored zeros, compute all gaps
gap_1, gap_2, ..., gap_24, normalized by the mean of ALL of those 24 gaps.
Compare each gap_k's variance to a matched GUE null (N=40 matrices with
SAME 24-gap-mean normalization).

Null generation: 50K GUE matrices of size N=40, take gaps in mid-bulk positions
so each matrix contributes a 24-consecutive-gaps sequence, normalize by mean of
those 24 gaps.

Output: ergon/results/gap_k_scan.json (+ stdout table)
"""
import json
import math
import time
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "gap_k_scan.json"

K_MAX = 24  # analyze gap_1 through gap_24


def parse_zeros(raw):
    if raw is None: return None
    s = str(raw).strip()
    if s in ('','[]','{}','None'): return None
    s = s.replace('{','[').replace('}',']')
    try: return [float(z) for z in json.loads(s)]
    except: return None


def local_k_gaps(zeros, kmax=K_MAX):
    if zeros is None or len(zeros) < kmax + 1:
        return None
    zeros = sorted(zeros)[:kmax + 1]
    gaps = np.array([zeros[i+1] - zeros[i] for i in range(kmax)])
    m = np.mean(gaps)
    if m <= 0:
        return None
    return gaps / m  # normalize by local mean over these kmax gaps


def gue_null(kmax, M, N, rng):
    """For M GUE matrices of size N, extract kmax consecutive mid-bulk gaps,
    normalize by their mean."""
    mid = N // 2 - kmax // 2
    out = np.zeros((M, kmax))
    for m in range(M):
        re = rng.standard_normal((N, N))
        im = rng.standard_normal((N, N))
        A = (re + 1j * im) / np.sqrt(2.0)
        H = (A + A.conj().T) / np.sqrt(2.0)
        w = np.sort(np.linalg.eigvalsh(H))
        gaps = np.diff(w)
        local = gaps[mid:mid + kmax]
        lm = local.mean()
        if lm <= 0:
            continue
        out[m] = local / lm
    return out


def main():
    print(f"Aporia Seed 2: gap-k scan for k in [1, {K_MAX}]")
    print("=" * 72)

    # Fetch rank-0 EC
    print("Fetching rank-0 EC with >=25 zeros...")
    t0 = time.time()
    conn = psycopg2.connect(**DB); cur = conn.cursor()
    cur.execute(f"""
        SELECT l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 50000
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")

    data = []
    for (raw,) in rows:
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        data.append(g)
    data = np.array(data)
    print(f"  {len(data)} curves parsed with {K_MAX} gaps each")

    # GUE matched null (N=40 mid-bulk)
    print("\nGenerating matched-GUE null (200K matrices)...")
    t0 = time.time()
    rng = np.random.default_rng(2024)
    null = gue_null(K_MAX, M=200000, N=40, rng=rng)
    print(f"  {null.shape[0]} matrices in {time.time()-t0:.0f}s")

    # Compute variance per gap_k
    data_var = data.var(axis=0, ddof=1)
    null_var = null.var(axis=0, ddof=1)
    deficit_pct = (1 - data_var / null_var) * 100

    # Standard error per bin
    def se_var(v, n):
        return math.sqrt(2 * v * v / n)

    print(f"\n{'k':>3} {'data_var':>9} {'null_var':>9} {'deficit%':>10} {'z-score':>10}")
    for k in range(K_MAX):
        se_d = se_var(data_var[k], len(data))
        se_n = se_var(null_var[k], len(null))
        se = math.sqrt(se_d**2 + se_n**2)
        z = (data_var[k] - null_var[k]) / se if se > 0 else 0
        print(f"{k+1:>3} {data_var[k]:>9.4f} {null_var[k]:>9.4f} "
              f"{deficit_pct[k]:>+10.2f} {z:>+10.2f}")

    # Save
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'k_max': K_MAX,
            'n_curves': len(data),
            'n_null_matrices': int(null.shape[0]),
            'data_var_per_k': data_var.tolist(),
            'null_var_per_k': null_var.tolist(),
            'deficit_pct_per_k': deficit_pct.tolist(),
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
