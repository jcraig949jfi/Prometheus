#!/usr/bin/env python3
"""
CRITICAL TEST per Aporia 1776909087367: does nbp's Spearman rho=1.0 signal
(prior nbp_split_nonCM.py) SURVIVE at deep gap-k under 24-gap normalization?

If yes: nbp predicts TRUE bulk rigidity. Mechanism (c) Euler-arithmetic channel
      is real and lives at deep k.
If no (rho collapses to ~0 at k>=8): nbp was tracking edge-excess artifact.
      Mechanism (c) gap1 story collapses as a normalization artifact.

Protocol: fetch rank-0 non-CM EC with nbp, conductor, and >=25 zeros. Compute
24-gap-normalized gap_k for k in [1, 24]. Stratify by nbp (6 bins). Compute
deficit vs matched-GUE null per (nbp, k). Regress deficit on nbp at each k,
report Spearman.

Output: ergon/results/nbp_bulk_k.json
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
OUT = Path(__file__).resolve().parent / "results" / "nbp_bulk_k.json"
K_MAX = 24


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
    print("nbp vs gap-k under 24-gap normalization")
    print("=" * 72)

    print("Fetching rank-0 non-CM EC with >=25 zeros + nbp ...")
    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT e.num_bad_primes::int, l.positive_zeros
        FROM ec_curvedata e
        JOIN lfunc_lfunctions l
          ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                         || '/' || split_part(e.lmfdb_iso, '.', 2)
        WHERE e.rank::int = 0
          AND e.cm::int = 0
          AND l.positive_zeros IS NOT NULL
          AND l.positive_zeros != '[]'
        LIMIT 120000
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")

    by_nbp = defaultdict(list)
    for nbp, raw in rows:
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if g is None: continue
        by_nbp[int(nbp or 0)].append(g)

    print("\nGenerating matched-GUE null (50K matrices)...")
    rng = np.random.default_rng(2025)
    null = gue_null(K_MAX, M=50000, N=40, rng=rng)
    null_var = null.var(axis=0, ddof=1)

    # Per-nbp per-k deficit
    print("\nPer-nbp variance per gap_k:")
    print(f"{'nbp':>4} {'n':>7}" + "".join(f" {'g'+str(k+1)+'%':>7}" for k in [0,3,7,11,15,19,23]))
    per_nbp = {}
    for nbp in sorted(by_nbp):
        data = by_nbp[nbp]
        if len(data) < 50: continue
        arr = np.array(data)
        variances = arr.var(axis=0, ddof=1)
        deficits = [(1 - v/null_var[k]) * 100 for k, v in enumerate(variances)]
        per_nbp[nbp] = {
            'n': len(data),
            'variances': variances.tolist(),
            'deficits_pct': deficits,
        }
        row = f"{nbp:>4} {len(data):>7}"
        for k in [0,3,7,11,15,19,23]:
            row += f" {deficits[k]:>+7.1f}"
        print(row)

    # Spearman(nbp, deficit) at each k
    print(f"\nSpearman(nbp, deficit) at each k:")
    print(f"{'k':>3} {'rho':>7} {'p':>12}")
    nbps = sorted(per_nbp.keys())
    nbp_arr = np.array(nbps)
    spearmans = []
    for k in range(K_MAX):
        deficits_at_k = np.array([per_nbp[n]['deficits_pct'][k] for n in nbps])
        try:
            r, p = stats.spearmanr(nbp_arr, deficits_at_k)
        except Exception:
            r, p = float('nan'), float('nan')
        spearmans.append({'k': k+1, 'rho': float(r), 'p': float(p)})
        if k+1 in [1,4,8,12,16,20,24]:
            print(f"{k+1:>3} {r:>7.3f} {p:>12.3g}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'null_var_per_k': null_var.tolist(),
            'per_nbp': {str(k): v for k, v in per_nbp.items()},
            'spearman_per_k': spearmans,
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
