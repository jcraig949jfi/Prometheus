#!/usr/bin/env python3
"""
Rank-1 EC 24-gap scan — Katz-Sarnak universality-class test.

Rank-1 EC family is Katz-Sarnak O-(odd) = SO(2N+1). Predicts DIFFERENT edge
behavior than rank-0's O+(even). Specifically, O-(odd) has first zero pinned
at s=0 (for L(s,E) with functional eq sign -1), forcing first POSITIVE zero to
be closer -- edge DEFICIT.

Prior rank stratification at 4-gap norm showed rank 0/1 similar. This is
because 4-gap norm constrains edge signatures. At 24-gap norm (per Seed 2
findings), true edge statistics are revealed.

Data: rank-1 non-CM EC with >=25 stored positive zeros.
"""
import json
import math
import time
from pathlib import Path

import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "rank1_gap_k.json"
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
    print("Rank-1 EC 24-gap scan")
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 1
          AND e.cm::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 50000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rank-1 non-CM rows in {time.time()-t0:.0f}s")

    data = []
    for (raw,) in rows:
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        data.append(g)
    data = np.array(data)
    print(f"  {len(data)} curves parsed")

    print("Generating GUE null (100K)...")
    rng = np.random.default_rng(4040)
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
            'n_rank1': len(data),
            'deficits_pct': deficits.tolist(),
            'null_var': null_var.tolist(),
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
