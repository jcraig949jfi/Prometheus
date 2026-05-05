#!/usr/bin/env python3
"""
MF (holomorphic modular form) 24-gap scan.

Modularity theorem: every rank-0 non-CM EC has a weight-2 newform attached;
these are the same family. MF rank-0 non-CM should show the same 24-gap
spacing signature as EC rank-0 non-CM.

LMFDB origin prefix: 'ModularForm/GL2/Q/holomorphic/'.
Only degree=2 newforms (weight 2) match EC.
"""
import json, math, time
from pathlib import Path
import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "mf_gap_k.json"
K_MAX = 8  # MF only stores ~10 zeros per L-function


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
    print("MF 24-gap scan — Modularity cross-check with EC")
    print("=" * 72)

    print("Fetching rank-0 weight-2 MF newforms...")
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT positive_zeros
        FROM lfunc_lfunctions
        WHERE origin LIKE 'ModularForm/GL2/Q/holomorphic/%'
          AND order_of_vanishing::int = 0
          AND degree::int = 2
          AND positive_zeros IS NOT NULL AND positive_zeros != '[]'
        LIMIT 50000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} MF rows in {time.time()-t0:.0f}s")

    data = []
    for (raw,) in rows:
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        data.append(g)
    data = np.array(data)
    print(f"  {len(data)} MF L-functions with 24 gaps each")

    print("Generating GUE null (100K)...")
    rng = np.random.default_rng(7777)
    null = gue_null(K_MAX, M=100000, N=40, rng=rng)
    null_var = null.var(axis=0, ddof=1)

    data_var = data.var(axis=0, ddof=1)
    deficits = (1 - data_var / null_var) * 100

    print(f"\n{'k':>3} {'data':>8} {'null':>8} {'MF def%':>9}")
    for k in range(K_MAX):
        print(f"{k+1:>3} {data_var[k]:>8.4f} {null_var[k]:>8.4f} {deficits[k]:>+9.2f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'n_mf': len(data),
            'deficits_pct': deficits.tolist(),
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
