"""
Report 18m — Degree-6 systematic α_p audit + D4 shifted-CM test.

Parent: R18i (cutoff audit), R18j (D4 non-convergence under naive CM).
Two tracks:

(A) Degree-6 audit: pull α_p via EMPIRICAL asymptote (not pinned CM) for
    several 6T* strata. Check which match DH 1/6, or show log(p) scaling,
    or cluster-const. Provides a scoping pass on higher-degree behavior.

(B) D4 shifted-CM test: naive CM predicts a specific Prob(p|h) asymptote
    but empirical settles at a DIFFERENT value. Fit a constant additive
    offset c_p: empirical = CM(p) + c_p across buckets at large |disc|.
    If c_p is stable and roughly the same across primes (or scales cleanly
    with p), Bartel-Lenstra's D4-refinement is empirically captured by
    this additive shift.

Output: cartography/docs/report18m_deg6_d4_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import log, log10, sqrt
from pathlib import Path
import numpy as np
import psycopg2

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='lmfdb', password='lmfdb')
OUTPUT = Path('cartography/docs/report18m_deg6_d4_results.json')
PRIMES = [5, 7, 11, 13]


def cm_prob(p, u, terms=200):
    eta = 1.0
    for k in range(u + 1, terms + 1):
        eta *= (1 - p ** -k)
    return 1.0 - eta


def linreg_with_se(xs, ys):
    xs = np.asarray(xs, dtype=float); ys = np.asarray(ys, dtype=float)
    n = len(xs)
    if n < 3:
        return {'slope': None, 'slope_se': None, 'r2': None, 'n': int(n)}
    mx = xs.mean(); my = ys.mean()
    sxx = float(np.sum((xs - mx) ** 2))
    sxy = float(np.sum((xs - mx) * (ys - my)))
    slope = sxy / sxx
    intercept = my - slope * mx
    yhat = slope * xs + intercept
    ss_res = float(np.sum((ys - yhat) ** 2))
    ss_tot = float(np.sum((ys - my) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    sigma2 = ss_res / (n - 2) if n > 2 else 0.0
    slope_se = float(np.sqrt(sigma2 / sxx)) if sxx > 0 else 0.0
    return {'slope': float(slope), 'intercept': float(intercept),
            'slope_se': slope_se, 'r2': float(r2), 'n': int(n)}


def pull_buckets(cur, degree, galois_label, sig_filter, primes, cutoff_bucket, min_n=500):
    filter_cols = ',\n          '.join(
        f"count(*) FILTER (WHERE (class_number::bigint) %% {p} = 0) AS d{p}"
        for p in primes
    )
    cur.execute(f"""
        SELECT floor(log(greatest(disc_abs::numeric, 1)) / log(10))::int AS bucket,
               count(*) AS n,
               {filter_cols}
        FROM nf_fields
        WHERE degree = %s AND galois_label = %s AND {sig_filter}
          AND class_number IS NOT NULL AND disc_abs IS NOT NULL
        GROUP BY bucket ORDER BY bucket
    """, (str(degree), galois_label))
    buckets = []
    for row in cur.fetchall():
        b = int(row[0]); n = int(row[1])
        if n < min_n: continue
        if cutoff_bucket is not None and b > cutoff_bucket: continue
        div = {p: int(row[2 + i]) for i, p in enumerate(primes)}
        buckets.append({'bucket': b, 'n': n, 'divisible_by_p': div})
    return buckets


def fit_alpha_empirical_asymptote(buckets, primes):
    """For each prime, fit log10|emp - asymptote| / asymptote vs bucket where
    asymptote is estimated from the LARGEST bucket."""
    if not buckets:
        return {}
    largest = max(buckets, key=lambda b: b['n'])
    result = {}
    for p in primes:
        asym = largest['divisible_by_p'][p] / largest['n'] if largest['n'] > 0 else None
        if asym is None or asym <= 0:
            result[p] = {'alpha_p': None, 'note': 'zero asymptote'}
            continue
        pts = []
        for b in buckets:
            if b['bucket'] == largest['bucket']: continue  # skip the reference
            emp = b['divisible_by_p'][p] / b['n']
            rel = (emp - asym) / asym
            if abs(rel) == 0: continue
            pts.append((b['bucket'], log10(abs(rel))))
        if len(pts) < 3:
            result[p] = {'alpha_p': None, 'note': f'only {len(pts)} other buckets'}
            continue
        xs = [pt[0] for pt in pts]; ys = [pt[1] for pt in pts]
        fit = linreg_with_se(xs, ys)
        # Note: we use empirical asymptote, so the 'convergence to asymptote'
        # is by construction; we're measuring how FAST empirical stabilizes.
        result[p] = {
            'asymptote_est': asym,
            'asymptote_bucket': largest['bucket'],
            'asymptote_n': largest['n'],
            'alpha_p': -fit['slope'] if fit['slope'] is not None else None,
            'alpha_p_se': fit['slope_se'],
            'r2': fit['r2'],
            'n_buckets_used': fit['n'],
        }
    return result


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=300000')
    cur = conn.cursor()

    # ============================================================
    # PART A: Degree-6 audit (cutoffs from R18i)
    # ============================================================
    print('[R18m-A] Degree-6 stratum audit...')
    deg6_strata = [
        {'label': '6T3',  'gal': '6T3',  'cut': None},   # smooth
        {'label': '6T11', 'gal': '6T11', 'cut': 16},     # cut off 10^17
        {'label': '6T12', 'gal': '6T12', 'cut': None},   # smooth
        {'label': '6T13', 'gal': '6T13', 'cut': 8},      # sharp cut 10^9
        {'label': '6T16', 'gal': '6T16', 'cut': None},   # smooth
    ]
    deg6_results = {}
    for s in deg6_strata:
        # Just pool both signatures — degree-6 signatures don't stratify well for naive CM
        buckets = pull_buckets(cur, 6, s['gal'], '1=1', PRIMES, s['cut'], min_n=500)
        if len(buckets) < 4:
            deg6_results[s['label']] = {'note': f'only {len(buckets)} adequate buckets', 'buckets': buckets}
            continue
        alphas = fit_alpha_empirical_asymptote(buckets, PRIMES)
        deg6_results[s['label']] = {
            'n_buckets': len(buckets),
            'bucket_range': (buckets[0]['bucket'], buckets[-1]['bucket']),
            'alpha_p_fits_vs_empirical_asymptote': alphas,
        }

    # ============================================================
    # PART B: D4 shifted-CM test
    # ============================================================
    print('[R18m-B] D4 shifted-CM additive-offset test...')
    # D4 complex (u=1) and D4 real (u=3)
    d4_families = [
        {'label': 'D4_complex', 'sig': 'r2::int >= 1', 'u': 1},
        {'label': 'D4_real',    'sig': 'r2::int = 0',  'u': 3},
    ]
    d4_results = {}
    for fam in d4_families:
        buckets = pull_buckets(cur, 4, '4T3', fam['sig'], PRIMES, cutoff_bucket=15, min_n=500)
        # For each prime, compute offset c_p = emp - CM per bucket, check stability
        per_prime = {}
        for p in PRIMES:
            theo = cm_prob(p, fam['u'])
            offsets = []
            for b in buckets:
                emp = b['divisible_by_p'][p] / b['n']
                offsets.append({
                    'bucket': b['bucket'], 'n': b['n'],
                    'emp': emp, 'cm': theo,
                    'offset': emp - theo,
                    'ratio': emp / theo if theo > 0 else None,
                })
            # Check if offsets stabilize in large buckets
            offs = [o['offset'] for o in offsets if o['n'] >= 1000]
            if len(offs) >= 3:
                offs_arr = np.array(offs)
                per_prime[p] = {
                    'cm_prediction': theo,
                    'offsets_by_bucket': offsets,
                    'offset_mean_large_n': float(offs_arr.mean()),
                    'offset_std_large_n': float(offs_arr.std()),
                    'offset_stable': float(offs_arr.std()) < 0.05 * abs(float(offs_arr.mean())) + 0.003,
                }
        d4_results[fam['label']] = per_prime

    cur.close(); conn.close()

    report = {
        'task': 'report18m_deg6_d4',
        'parent': 'report18l_anchor_firmup',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'deg6_audit': deg6_results,
        'd4_shifted_cm_test': d4_results,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18m] wrote {OUTPUT}')
    print()

    # Console
    print('== DEGREE-6 α_p vs EMPIRICAL ASYMPTOTE ==')
    for label, d in deg6_results.items():
        print(f'\n{label}:')
        if 'note' in d:
            print(f'  {d["note"]}')
            continue
        print(f'  n_buckets = {d["n_buckets"]}, bucket_range = {d["bucket_range"]}')
        for p in PRIMES:
            a = d['alpha_p_fits_vs_empirical_asymptote'][p]
            if a.get('alpha_p') is not None:
                print(f'  p={p:>3}: α = {a["alpha_p"]:+.5f} ± {a["alpha_p_se"]:.5f}, R²={a["r2"]:.4f}, '
                      f'asymptote={a["asymptote_est"]:.4f}')
            else:
                print(f'  p={p:>3}: {a.get("note", "no fit")}')
    print()

    print('== D4 SHIFTED-CM OFFSET TEST ==')
    for fam_label, per_prime in d4_results.items():
        print(f'\n{fam_label}:')
        for p in PRIMES:
            if p not in per_prime: continue
            d = per_prime[p]
            print(f'  p={p:>3}: CM = {d["cm_prediction"]:.5f}, mean offset (large n) = '
                  f'{d["offset_mean_large_n"]:+.5f} ± {d["offset_std_large_n"]:.5f}  '
                  f'(stable: {d["offset_stable"]})')

    return 0


if __name__ == '__main__':
    sys.exit(main())
