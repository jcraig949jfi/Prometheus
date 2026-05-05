#!/usr/bin/env python3
"""
Maass GL3 gap-k scan (degree-3 capstone, Aporia-endorsed).

Caveat: LMFDB Maass GL3 L-functions are mostly level-1 (trivial conductor,
no bad primes). So the nbp stratification that made Dirichlet/EC/G2C
distinguishable CAN'T be done here. Instead report pooled degree-3 edge/bulk
profile for comparison.

Zeros stored: 11-15 per L-function. Use k_max = 8.
"""
import json, math, time
from pathlib import Path
import numpy as np
import psycopg2

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path("F:/prometheus/ergon/results/maass_gl3_gap_k.json")
K_MAX = 8


def parse_zeros(raw):
    if raw is None: return None
    s = str(raw).strip()
    if s in ('','[]','{}','None'): return None
    s = s.replace('{','[').replace('}',']')
    try: return [float(z) for z in json.loads(s)]
    except: return None


def local_k_gaps(zeros, kmax):
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
    print("Maass GL3 (degree-3) gap-k scan — capstone")
    print("=" * 72)
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT positive_zeros
        FROM lfunc_lfunctions
        WHERE origin LIKE 'ModularForm/GL3/Q/Maass/%'
          AND degree::int = 3
          AND order_of_vanishing::int = 0
          AND positive_zeros IS NOT NULL AND positive_zeros != '[]'
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} Maass GL3 rows in {time.time()-t0:.0f}s")

    data = []
    for (raw,) in rows:
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        data.append(g)
    data = np.array(data)
    print(f"  {len(data)} curves parsed")

    if len(data) < 30:
        print("Too few curves; aborting")
        return

    print("Generating GUE null (100K)...")
    rng = np.random.default_rng(909090)
    null = gue_null(K_MAX, 100000, 40, rng)
    null_var = null.var(axis=0, ddof=1)

    data_var = data.var(axis=0, ddof=1)
    deficits = (1 - data_var / null_var) * 100

    print(f"\n{'k':>3} {'data':>8} {'null':>8} {'deficit%':>9}")
    EC_D = [7.7, 7.9, 16.6, 23.4, 26.3, 32.2, 30.9, 34.1]  # EC 8-gap from earlier
    MF_D = [-53.7, -26.3, -5.5, 4.3, 13.9, 21.0, 27.0, 31.0]  # MF 8-gap from earlier
    for k in range(K_MAX):
        print(f"{k+1:>3} {data_var[k]:>8.4f} {null_var[k]:>8.4f} {deficits[k]:>+9.2f}"
              f"   (EC: {EC_D[k]:+.1f}, MF: {MF_D[k]:+.1f})")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'n_maass_gl3': len(data),
            'deficits_pct': deficits.tolist(),
        }, f, indent=1)
    print(f"\nSaved {OUT}")
    print("\nNote: Maass GL3 L-functions are level-1 (no nbp stratification possible).")
    print("This scan gives pooled degree-3 edge/bulk profile.")
    print("Comparing: EC(deg2), MF(deg2), Maass GL3(deg3), G2C(deg4, see g2c_gap_k.json)")


if __name__ == "__main__":
    main()
