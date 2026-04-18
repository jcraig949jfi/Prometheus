"""
Report 18d — Cohen-Lenstra convergence α_p extended to p ∈ {13, 17, 19, 23}.

Follow-up to R18c. R18c established that α_p (BST convergence exponent)
clusters at ~0.16 for p=3 and ~0.23-0.28 for p ∈ {5, 7, 11}. This script
extends to higher primes to test whether the p≥5 cluster holds.

Method: repeat the R18b + R18c pipeline for p ∈ {13, 17, 19, 23}, using
the same |disc|-bucket stratification and linear-log fit.

Output: cartography/docs/report18d_extended_primes_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import sqrt, log10
from pathlib import Path
import numpy as np
import psycopg2

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='lmfdb', password='lmfdb')

# Extended primes — union of R18c primes + new ones for cluster firm-up
ALL_PRIMES = [3, 5, 7, 11, 13, 17, 19, 23]
NEW_PRIMES = [13, 17, 19, 23]


def cl_asymptote_imaginary(p, terms=200):
    eta = 1.0
    for k in range(1, terms + 1):
        eta *= (1 - p ** -k)
    return 1.0 - eta


def cl_asymptote_real(p, terms=200):
    eta = 1.0
    for k in range(2, terms + 1):
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


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=300000')
    cur = conn.cursor()

    # For each family, stratify by |disc| bucket and count divisibility at ALL_PRIMES.
    families = {
        'imaginary_quadratic': {'sig': 'r2::int >= 1', 'theo_fn': cl_asymptote_imaginary},
        'real_quadratic':      {'sig': 'r2::int = 0',  'theo_fn': cl_asymptote_real},
    }

    # Build a dynamic SELECT with one count-FILTER clause per prime.
    # No psycopg2 params below; single % (not %%)
    filter_cols = ',\n          '.join(
        f"count(*) FILTER (WHERE (class_number::bigint) % {p} = 0) AS d{p}"
        for p in ALL_PRIMES
    )

    results = {'imaginary_quadratic': {}, 'real_quadratic': {}}
    for fam_name, fam in families.items():
        print(f'[R18d] fetching {fam_name} by |disc| bucket...')
        cur.execute(f"""
            SELECT
              floor(log(greatest(disc_abs::bigint, 1)) / log(10))::int AS bucket,
              count(*) AS n,
              {filter_cols}
            FROM nf_fields
            WHERE degree::int = 2
              AND galois_label = '2T1'
              AND {fam['sig']}
              AND class_number IS NOT NULL
              AND disc_abs IS NOT NULL
            GROUP BY bucket
            ORDER BY bucket
        """)
        rows = cur.fetchall()

        buckets = []
        for row in rows:
            bucket = int(row[0])
            n = int(row[1])
            if n < 1000:
                continue
            per_prime = {}
            for i, p in enumerate(ALL_PRIMES):
                k = int(row[2 + i])
                emp = k / n
                theo = fam['theo_fn'](p)
                rel = (emp - theo) / theo if theo > 0 else None
                se = sqrt(theo * (1 - theo) / n) if n > 0 else None
                z = (emp - theo) / se if (se and se > 0) else None
                per_prime[str(p)] = {
                    'empirical': emp,
                    'theoretical': theo,
                    'z': z,
                    'relative_deviation': rel,
                    'n_divisible': k,
                }
            buckets.append({
                'log10_disc_bucket': bucket,
                'n': n,
                'per_prime': per_prime,
            })

        # Fit α_p per prime
        alphas = {}
        for p in ALL_PRIMES:
            pts = [(b['log10_disc_bucket'], log10(abs(b['per_prime'][str(p)]['relative_deviation'])))
                   for b in buckets
                   if b['per_prime'][str(p)]['relative_deviation'] is not None
                   and abs(b['per_prime'][str(p)]['relative_deviation']) > 0]
            if len(pts) >= 3:
                xs = [p_[0] for p_ in pts]; ys = [p_[1] for p_ in pts]
                fit = linreg_with_se(xs, ys)
                alphas[str(p)] = {
                    'alpha_p': -fit['slope'] if fit['slope'] is not None else None,
                    'alpha_p_se': fit['slope_se'],
                    'r2': fit['r2'],
                    'n_buckets': fit['n'],
                }
            else:
                alphas[str(p)] = {'alpha_p': None, 'note': 'insufficient buckets'}

        results[fam_name] = {'buckets': buckets, 'alpha_p_fits': alphas}

    cur.close(); conn.close()

    # Cluster analysis for p ≥ 5 using extended primes
    for fam_name in results:
        alphas_ge5 = [(int(p), results[fam_name]['alpha_p_fits'][p]['alpha_p'],
                       results[fam_name]['alpha_p_fits'][p].get('alpha_p_se'))
                      for p in results[fam_name]['alpha_p_fits']
                      if int(p) >= 5
                      and results[fam_name]['alpha_p_fits'][p]['alpha_p'] is not None]
        if len(alphas_ge5) >= 3:
            vals = np.array([a[1] for a in alphas_ge5])
            ses = np.array([a[2] for a in alphas_ge5 if a[2] is not None])
            if len(ses) == len(vals):
                w = 1 / ses ** 2
                alpha_cluster = float(np.sum(w * vals) / np.sum(w))
                alpha_cluster_se = float(1 / np.sqrt(np.sum(w)))
                chi2 = float(np.sum(((vals - alpha_cluster) / ses) ** 2))
                dof = len(vals) - 1
                z_per_prime = {int(a[0]): float((a[1] - alpha_cluster) / a[2])
                               for a in alphas_ge5}
                results[fam_name]['p_ge_5_cluster'] = {
                    'primes_in_cluster': [int(a[0]) for a in alphas_ge5],
                    'alpha_cluster_weighted_mean': alpha_cluster,
                    'alpha_cluster_se': alpha_cluster_se,
                    'chi2': chi2,
                    'dof': dof,
                    'z_per_prime_vs_cluster': z_per_prime,
                    'max_abs_z': max(abs(z) for z in z_per_prime.values()),
                    'cluster_constant_at_2sigma': max(abs(z) for z in z_per_prime.values()) < 2.0,
                    'cluster_constant_at_3sigma': max(abs(z) for z in z_per_prime.values()) < 3.0,
                }

    # Family comparison at p=3 with extended set (sanity)
    p3_fam_match = {}
    for p in ALL_PRIMES:
        ia = results['imaginary_quadratic']['alpha_p_fits'][str(p)].get('alpha_p')
        ise = results['imaginary_quadratic']['alpha_p_fits'][str(p)].get('alpha_p_se')
        ra = results['real_quadratic']['alpha_p_fits'][str(p)].get('alpha_p')
        rse = results['real_quadratic']['alpha_p_fits'][str(p)].get('alpha_p_se')
        if None in (ia, ise, ra, rse):
            continue
        diff = ia - ra; dse = sqrt(ise ** 2 + rse ** 2)
        p3_fam_match[str(p)] = {
            'imag': ia, 'imag_se': ise,
            'real': ra, 'real_se': rse,
            'z_diff': diff / dse if dse > 0 else None,
            'family_universal_at_2sigma': abs(diff / dse) < 2.0 if dse > 0 else None,
        }

    report = {
        'task': 'report18d_extended_primes',
        'parent': 'report18c_bst_rate_fit',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'primes_tested': ALL_PRIMES,
        'new_primes_this_run': NEW_PRIMES,
        'families': results,
        'family_comparison_per_prime': p3_fam_match,
    }

    outpath = Path('cartography/docs/report18d_extended_primes_results.json')
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18d] wrote {outpath}')
    print()

    # Console summary
    print('== EXTENDED α_p FITS (8 primes × 2 families) ==')
    print(f'{"family":>14} {"p":>4} {"alpha_p":>12} {"±se":>10} {"r²":>7}')
    for fam_name in results:
        for p in ALL_PRIMES:
            f_ = results[fam_name]['alpha_p_fits'][str(p)]
            a = f_.get('alpha_p'); se = f_.get('alpha_p_se'); r2 = f_.get('r2')
            if a is None: continue
            print(f'{fam_name[:14]:>14} {p:>4} {a:>+12.5f} {se:>+10.5f} {r2:>+7.4f}')
    print()

    print('== p ≥ 5 CLUSTER (extended) ==')
    for fam_name in results:
        c = results[fam_name].get('p_ge_5_cluster')
        if not c: continue
        print(f'{fam_name}:')
        print(f'  primes: {c["primes_in_cluster"]}')
        print(f'  α_cluster = {c["alpha_cluster_weighted_mean"]:.5f} ± {c["alpha_cluster_se"]:.5f}')
        print(f'  χ² = {c["chi2"]:.3f} (dof {c["dof"]})  max|z| = {c["max_abs_z"]:.3f}')
        print(f'  cluster_constant @ 2σ: {c["cluster_constant_at_2sigma"]}, '
              f'@ 3σ: {c["cluster_constant_at_3sigma"]}')
    print()

    print('== FAMILY UNIVERSALITY PER PRIME ==')
    for p, fc in p3_fam_match.items():
        z = fc['z_diff']
        u = fc['family_universal_at_2sigma']
        print(f'  p={p:>3}: imag={fc["imag"]:+.5f}  real={fc["real"]:+.5f}  '
              f'z_diff={z:+.3f}  universal @ 2σ: {u}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
