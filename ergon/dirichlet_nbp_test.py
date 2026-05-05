#!/usr/bin/env python3
"""
Seed 13 (Aporia): Dirichlet L-functions as third universality class (Unitary).

Pre-registered prediction: rho(nbp, deficit) ~ 0 for Dirichlet L-functions
because U(N) family has no family-signed 2-point correction (all corrections
vanish in the Katz-Sarnak classification for unitary families).

Method: origin = 'Character/Dirichlet/<modulus>/<char>'. Number of bad primes =
number of distinct prime factors of modulus (cheap to factor at modulus < 10^5).

Dirichlet L-functions have ~350 zeros stored — we use 24-gap normalization.
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
OUT = Path(__file__).resolve().parent / "results" / "dirichlet_nbp.json"
K_MAX = 24
NULL_VAR_4GAP = [0.1472, 0.1741, 0.1725, 0.1468]


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


def omega(n):
    """Number of distinct prime factors (trial division up to sqrt(n))."""
    if n < 2: return 0
    count = 0
    p = 2
    while p * p <= n:
        if n % p == 0:
            count += 1
            while n % p == 0:
                n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        count += 1
    return count


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
    print("Seed 13: Dirichlet nbp test")
    print("=" * 72)

    print("Fetching rank-0 Dirichlet L-functions (sample)...")
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT origin, positive_zeros
        FROM lfunc_lfunctions
        WHERE degree::int = 1
          AND order_of_vanishing::int = 0
          AND origin LIKE 'Character/Dirichlet/%'
          AND positive_zeros IS NOT NULL AND positive_zeros != '[]'
        LIMIT 60000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} Dirichlet rows in {time.time()-t0:.0f}s")

    # Parse origin -> modulus -> omega
    by_nbp = defaultdict(list)
    n_valid = 0
    for origin, raw in rows:
        parts = str(origin).split('/')
        # origin = Character/Dirichlet/<modulus>/<char>
        if len(parts) < 4: continue
        try:
            modulus = int(parts[2])
        except: continue
        nbp = omega(modulus)
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        by_nbp[nbp].append(g)
        n_valid += 1
    print(f"  Parsed {n_valid} with 24 gaps each")

    # Matched GUE null
    print("Generating GUE null (50K)...")
    rng = np.random.default_rng(1313)
    null = gue_null(K_MAX, 50000, 40, rng)
    null_var = null.var(axis=0, ddof=1)

    print(f"\n{'nbp':>4} {'n':>6}   " + " ".join(f"{'g'+str(k)+'%':>7}" for k in [1,2,4,8,16,24]))
    results = {}
    bins = []
    g1s = []; g4s = []; g8s = []; g24s = []
    for nbp in sorted(by_nbp):
        data = by_nbp[nbp]
        if len(data) < 50: continue
        arr = np.array(data)
        variances = arr.var(axis=0, ddof=1)
        deficits = [(1 - v/null_var[i]) * 100 for i, v in enumerate(variances)]
        results[nbp] = {'n': len(data), 'deficits_pct': deficits}
        bins.append(nbp)
        g1s.append(deficits[0]); g4s.append(deficits[3])
        g8s.append(deficits[7]); g24s.append(deficits[23])
        row = f"{nbp:>4} {len(data):>6}   "
        for k in [1,2,4,8,16,24]:
            row += f"{deficits[k-1]:>+7.2f} "
        print(row)

    # Spearman at several k
    if len(bins) >= 3:
        print(f"\nSpearman(nbp, deficit) at various k:")
        for name, vals in [('gap1', g1s), ('gap4', g4s), ('gap8', g8s), ('gap24', g24s)]:
            r, p = stats.spearmanr(bins, vals)
            print(f"  {name}: rho = {r:+.3f}  p = {p:.3g}")
        results['spearman_gap1'] = {'rho': float(stats.spearmanr(bins, g1s).statistic), 'p': float(stats.spearmanr(bins, g1s).pvalue)}
        results['spearman_gap8'] = {'rho': float(stats.spearmanr(bins, g8s).statistic), 'p': float(stats.spearmanr(bins, g8s).pvalue)}
        results['spearman_gap24'] = {'rho': float(stats.spearmanr(bins, g24s).statistic), 'p': float(stats.spearmanr(bins, g24s).pvalue)}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=1, default=str)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
