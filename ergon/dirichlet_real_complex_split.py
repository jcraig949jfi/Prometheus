#!/usr/bin/env python3
"""
Split Dirichlet nbp test by self_dual (real vs complex characters).

Per Charon/Aporia:
  self_dual='True'  → REAL character (order <= 2), orthogonal subfamily
  self_dual='False' → COMPLEX character (order > 2), unitary subfamily

Pre-registered (direction only):
  Complex (U-class): rho may be ≈ 0 OR +1 depending on whether nbp is U-inactive
  Real (O-class): rho > 0 expected

Output: ergon/results/dirichlet_real_complex.json
"""
import json, math, time
from collections import defaultdict
from pathlib import Path
import numpy as np
import psycopg2
from scipy import stats

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path(__file__).resolve().parent / "results" / "dirichlet_real_complex.json"
K_MAX = 24


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
    if n < 2: return 0
    count = 0; p = 2
    while p * p <= n:
        if n % p == 0:
            count += 1
            while n % p == 0: n //= p
        p += 1 if p == 2 else 2
    if n > 1: count += 1
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


def run_subset(label, sql_filter, null_var):
    print(f"\n=== {label} ===", flush=True)
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute(f"""
        SELECT origin, positive_zeros
        FROM lfunc_lfunctions
        WHERE degree::int = 1
          AND order_of_vanishing::int = 0
          AND origin LIKE 'Character/Dirichlet/%'
          AND positive_zeros IS NOT NULL AND positive_zeros != '[]'
          AND {sql_filter}
        LIMIT 40000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s", flush=True)

    by_nbp = defaultdict(list)
    for origin, raw in rows:
        parts = str(origin).split('/')
        if len(parts) < 4: continue
        try: modulus = int(parts[2])
        except: continue
        nbp = omega(modulus)
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        by_nbp[nbp].append(g)

    results = {}
    bins = []; g1s = []; g8s = []; g24s = []
    print(f"  {'nbp':>4} {'n':>6}   {'g1%':>7} {'g4%':>7} {'g8%':>7} {'g24%':>7}")
    for nbp in sorted(by_nbp):
        data = by_nbp[nbp]
        if len(data) < 50: continue
        arr = np.array(data)
        v = arr.var(axis=0, ddof=1)
        d = [(1 - v[i] / null_var[i]) * 100 for i in range(K_MAX)]
        results[nbp] = {'n': len(data), 'deficits': d}
        bins.append(nbp); g1s.append(d[0]); g8s.append(d[7]); g24s.append(d[23])
        print(f"  {nbp:>4} {len(data):>6}   {d[0]:>+7.2f} {d[3]:>+7.2f} {d[7]:>+7.2f} {d[23]:>+7.2f}")

    if len(bins) >= 3:
        r1, p1 = stats.spearmanr(bins, g1s)
        r8, p8 = stats.spearmanr(bins, g8s)
        r24, p24 = stats.spearmanr(bins, g24s)
        print(f"  Spearman rho: gap1={r1:+.3f} gap8={r8:+.3f} gap24={r24:+.3f}")
        results['spearman'] = {
            'gap1': {'rho': float(r1), 'p': float(p1)},
            'gap8': {'rho': float(r8), 'p': float(p8)},
            'gap24': {'rho': float(r24), 'p': float(p24)},
        }
    return results


def main():
    print("Dirichlet real-vs-complex split")
    rng = np.random.default_rng(1414)
    print("Generating GUE null (50K)...")
    null = gue_null(K_MAX, 50000, 40, rng)
    null_var = null.var(axis=0, ddof=1)

    results = {}
    results['complex'] = run_subset('COMPLEX Dirichlet (self_dual=False)', "self_dual = 'False'", null_var)
    results['real'] = run_subset('REAL Dirichlet (self_dual=True)', "self_dual = 'True'", null_var)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(results, f, indent=1, default=str)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
