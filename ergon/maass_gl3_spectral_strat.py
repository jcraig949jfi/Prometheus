#!/usr/bin/env python3
"""
Maass GL3 stratified by spectral parameter magnitude.

Since Maass GL3 is level 1 (no nbp), stratify by the two spectral parameters in
the origin path:  ModularForm/GL3/Q/Maass/<level>/<weight>/<sp1>_<sp2>/<eigval>/

Candidate predictors for the nbp-analog:
  - |sp1| + |sp2|       (total spectral magnitude)
  - max(|sp1|, |sp2|)   (larger parameter)
  - |sp1 * sp2|         (product, for "skewness" of spectral pair)

Pre-registered (per Aporia hypothesis a):
  If dimension-driven: degree-3 rho(spectral proxy, deficit) ~ +0.4 to +0.7 (mid-way)
  If Sp-unique: degree-3 rho ~ +1 (everything non-Sp is positive)
  If Unitary-zero: degree-3 rho ~ 0

Output: ergon/results/maass_gl3_spectral.json
"""
import json, math, re, time
from collections import defaultdict
from pathlib import Path
import numpy as np
import psycopg2
from scipy import stats

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
OUT = Path("F:/prometheus/ergon/results/maass_gl3_spectral.json")
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


def parse_spectral(origin):
    """Extract (sp1, sp2) from 'ModularForm/GL3/Q/Maass/<lvl>/<w>/<sp1>_<sp2>/<ev>/'."""
    parts = str(origin).split('/')
    # parts[6] should be '<sp1>_<sp2>' (trailing slash makes empty last)
    if len(parts) < 7: return None
    sp_field = parts[6]
    m = re.match(r'^(-?\d+\.?\d*)_(-?\d+\.?\d*)$', sp_field)
    if not m: return None
    try:
        return float(m.group(1)), float(m.group(2))
    except: return None


def gue_null(kmax, M, N, rng):
    mid = N // 2 - kmax // 2
    out = np.zeros((M, kmax))
    for m in range(M):
        re_ = rng.standard_normal((N, N))
        im_ = rng.standard_normal((N, N))
        A = (re_ + 1j * im_) / np.sqrt(2.0)
        H = (A + A.conj().T) / np.sqrt(2.0)
        w = np.sort(np.linalg.eigvalsh(H))
        gaps = np.diff(w)
        local = gaps[mid:mid+kmax]
        lm = local.mean()
        if lm <= 0: continue
        out[m] = local / lm
    return out


def main():
    print("Maass GL3 spectral-parameter stratification")
    print("=" * 72)

    t0 = time.time()
    c = psycopg2.connect(**DB); cur = c.cursor()
    cur.execute("""
        SELECT origin, positive_zeros
        FROM lfunc_lfunctions
        WHERE origin LIKE 'ModularForm/GL3/Q/Maass/%'
          AND degree::int = 3
          AND order_of_vanishing::int = 0
          AND positive_zeros IS NOT NULL AND positive_zeros != '[]'
    """)
    rows = cur.fetchall()
    cur.close(); c.close()
    print(f"  {len(rows)} rows in {time.time()-t0:.0f}s")

    # Parse each: (sp1, sp2, gaps)
    parsed = []
    for origin, raw in rows:
        sp = parse_spectral(origin)
        g = local_k_gaps(parse_zeros(raw), K_MAX)
        if sp is None or g is None: continue
        parsed.append((sp[0], sp[1], g))
    print(f"  {len(parsed)} parsed with spectral params and {K_MAX} gaps")

    # Compute proxies
    sp_abs_sum = np.array([abs(p[0]) + abs(p[1]) for p in parsed])
    sp_max = np.array([max(abs(p[0]), abs(p[1])) for p in parsed])
    gaps = np.array([p[2] for p in parsed])

    # Distribution of the magnitude proxy
    print(f"\nspectral-abs-sum quartiles: {np.percentile(sp_abs_sum, [0, 25, 50, 75, 100])}")
    print(f"spectral-max quartiles:      {np.percentile(sp_max, [0, 25, 50, 75, 100])}")

    # Quartile bin by sp_abs_sum
    quarts = np.quantile(sp_abs_sum, np.linspace(0, 1, 5))
    print(f"\nsp_abs_sum quartile bounds: {quarts}")
    bin_lab = np.clip(np.searchsorted(quarts, sp_abs_sum, side='right') - 1, 0, 3)

    print("\nGenerating GUE null (100K)...")
    rng = np.random.default_rng(31415)
    null = gue_null(K_MAX, 100000, 40, rng)
    null_var = null.var(axis=0, ddof=1)

    print(f"\n{'Q_sp':>4} {'n':>6}   " + "".join(f"{'g'+str(k+1)+'%':>8}" for k in range(K_MAX)))
    quartile_rows = []
    for q in range(4):
        idx = np.where(bin_lab == q)[0]
        if len(idx) < 30: continue
        data = gaps[idx]
        variances = data.var(axis=0, ddof=1)
        deficits = [(1 - v / null_var[k]) * 100 for k, v in enumerate(variances)]
        quartile_rows.append({'quartile': q, 'n': int(len(idx)), 'deficits_pct': deficits,
                               'sp_abs_sum_mean': float(sp_abs_sum[idx].mean())})
        print(f"{q:>4} {len(idx):>6}   " + "".join(f"{d:>+8.2f}" for d in deficits))

    # Spearman against sp_abs_sum quartile
    qs = [r['quartile'] for r in quartile_rows]
    for k in [0, 3, 7]:
        vals = [r['deficits_pct'][k] for r in quartile_rows]
        if len(qs) >= 3:
            r, p = stats.spearmanr(qs, vals)
            print(f"  Spearman(sp_abs_sum_quartile, gap{k+1}_deficit) = {r:+.3f}  p = {p:.3g}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump({
            'n_parsed': len(parsed),
            'null_var': null_var.tolist(),
            'per_quartile': quartile_rows,
        }, f, indent=1)
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
