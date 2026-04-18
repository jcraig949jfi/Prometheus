"""
Report 18c — Extract BST convergence rate α_p from the Cohen-Lenstra data.

Model: |rel_dev(bucket)| = c_p · 10^(-α_p · bucket), where
  bucket = floor(log10(|disc_abs|)),
  |rel_dev| = (empirical_Prob(p|h) - CL_asymptote) / CL_asymptote.

Equivalently: log10(|rel_dev|) = log10(c_p) - α_p · bucket.

α_p is the convergence exponent: |rel_dev| shrinks by factor 10^α_p per
decade of |disc|. Literature benchmarks (Bhargava-Shankar-Tsimerman, Cohen-
Lenstra, Stevenhagen, Malle): α varies by problem but typical orders are
α ∈ [1/8, 1/2] depending on which moment of the class-group distribution.

Question: is α_p prime-independent (→ universal convergence rate, cleanest
F-anchor candidate) or does it show systematic p-dependence (→ more
nuanced story)?

Inputs: cartography/docs/report18b_cl_disc_convergence_results.json
(bulk buckets 3-6 from the previous task; n ≥ 1000 per bucket).

Output: cartography/docs/report18c_bst_rate_fit_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import log10, sqrt
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PRIMES = [3, 5, 7, 11]
INPUT = Path('cartography/docs/report18b_cl_disc_convergence_results.json')
OUTPUT = Path('cartography/docs/report18c_bst_rate_fit_results.json')


def linreg_with_se(xs, ys):
    """Simple OLS slope + intercept + standard errors.

    Returns: {slope, intercept, slope_se, intercept_se, r2, n}.
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    n = len(xs)
    if n < 3:
        return {'slope': None, 'intercept': None, 'slope_se': None,
                'intercept_se': None, 'r2': None, 'n': int(n)}
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
    intercept_se = float(np.sqrt(sigma2 * (1 / n + mx ** 2 / sxx))) if sxx > 0 else 0.0
    return {'slope': float(slope), 'intercept': float(intercept),
            'slope_se': slope_se, 'intercept_se': intercept_se,
            'r2': float(r2), 'n': int(n)}


def fit_one_family(buckets, prime, min_n=1000):
    """For a given prime and family, fit log10(|rel_dev|) vs bucket."""
    pts = []
    for b in buckets:
        if b['n'] < min_n:
            continue
        rel = b['per_prime'][str(prime)]['relative_deviation']
        if rel is None or abs(rel) == 0:
            continue
        pts.append((b['log10_disc_bucket'], log10(abs(rel)), b['n']))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ns = [p[2] for p in pts]
    fit = linreg_with_se(xs, ys)
    # α_p is the negative of the slope (since we wrote rel_dev = c · 10^(-α·bucket))
    if fit['slope'] is not None:
        fit['alpha_p'] = -fit['slope']
        fit['alpha_p_se'] = fit['slope_se']
        fit['c_p'] = 10 ** fit['intercept'] if fit['intercept'] is not None else None
    return {
        'buckets_used': [int(x) for x in xs],
        'ns': ns,
        'log10_abs_rel_dev': [float(y) for y in ys],
        'fit': fit,
    }


def is_prime_independent(per_prime_alphas, tolerance_sigma=2.0):
    """Check if α_p values are consistent with a single common α across primes.

    Use weighted mean + χ² test on the null H0: α_p = α_common.
    """
    vals = []
    ses = []
    for p, d in per_prime_alphas.items():
        a = d['fit'].get('alpha_p')
        s = d['fit'].get('alpha_p_se')
        if a is not None and s is not None and s > 0:
            vals.append(a)
            ses.append(s)
    if len(vals) < 2:
        return {'prime_independent': None, 'n_primes': len(vals)}
    vals = np.array(vals); ses = np.array(ses)
    w = 1 / ses ** 2
    alpha_common = float(np.sum(w * vals) / np.sum(w))
    alpha_common_se = float(1.0 / np.sqrt(np.sum(w)))
    chi2 = float(np.sum(((vals - alpha_common) / ses) ** 2))
    dof = len(vals) - 1
    # Per-prime z from common
    z_per_prime = {}
    primes = sorted(per_prime_alphas.keys(), key=int)
    for p, v, s in zip(primes, vals, ses):
        z_per_prime[p] = float((v - alpha_common) / s)
    max_abs_z = max(abs(z) for z in z_per_prime.values())
    prime_independent = max_abs_z < tolerance_sigma
    return {
        'alpha_common_weighted': alpha_common,
        'alpha_common_se': alpha_common_se,
        'chi2': chi2,
        'dof': dof,
        'z_per_prime_vs_common': z_per_prime,
        'max_abs_z': max_abs_z,
        'prime_independent_at_2sigma': prime_independent,
    }


def main():
    if not INPUT.exists():
        print(f'ERROR: {INPUT} not found — run report18b first', file=sys.stderr)
        sys.exit(1)
    parent = json.load(open(INPUT))

    families = {
        'imaginary_quadratic': parent['imaginary_quadratic']['buckets'],
        'real_quadratic': parent['real_quadratic']['buckets'],
    }

    report = {
        'task': 'report18c_bst_rate_fit',
        'parent': 'report18b_cl_disc_convergence',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'model': '|rel_dev(bucket)| = c_p · 10^(-alpha_p · bucket)',
        'primes_tested': PRIMES,
        'families': {},
    }

    for family_name, buckets in families.items():
        per_prime = {}
        for p in PRIMES:
            per_prime[str(p)] = fit_one_family(buckets, p, min_n=1000)
        prime_indep = is_prime_independent(per_prime)
        report['families'][family_name] = {
            'per_prime': per_prime,
            'prime_independence_test': prime_indep,
        }

    # Family-independence: compare imag α vs real α at each prime
    family_comparison = {}
    for p in PRIMES:
        ia = report['families']['imaginary_quadratic']['per_prime'][str(p)]['fit'].get('alpha_p')
        ise = report['families']['imaginary_quadratic']['per_prime'][str(p)]['fit'].get('alpha_p_se')
        ra = report['families']['real_quadratic']['per_prime'][str(p)]['fit'].get('alpha_p')
        rse = report['families']['real_quadratic']['per_prime'][str(p)]['fit'].get('alpha_p_se')
        if None in (ia, ise, ra, rse):
            continue
        diff = ia - ra
        diff_se = sqrt(ise ** 2 + rse ** 2)
        family_comparison[str(p)] = {
            'imag_alpha': ia, 'imag_se': ise,
            'real_alpha': ra, 'real_se': rse,
            'diff': diff, 'diff_se': diff_se,
            'z_imag_vs_real': diff / diff_se if diff_se > 0 else None,
            'same_at_2sigma': abs(diff / diff_se) < 2.0 if diff_se > 0 else None,
        }
    report['family_comparison_imag_vs_real'] = family_comparison

    # Pooled fit across all 8 (family × prime) series
    all_alphas = []
    all_ses = []
    labels = []
    for fam in families:
        for p in PRIMES:
            fit = report['families'][fam]['per_prime'][str(p)]['fit']
            if fit.get('alpha_p') is not None and fit.get('alpha_p_se') is not None and fit['alpha_p_se'] > 0:
                all_alphas.append(fit['alpha_p'])
                all_ses.append(fit['alpha_p_se'])
                labels.append(f'{fam[:4]}_p{p}')
    all_alphas = np.array(all_alphas); all_ses = np.array(all_ses)
    w = 1 / all_ses ** 2
    alpha_grand = float(np.sum(w * all_alphas) / np.sum(w))
    alpha_grand_se = float(1.0 / np.sqrt(np.sum(w)))
    chi2_grand = float(np.sum(((all_alphas - alpha_grand) / all_ses) ** 2))
    dof_grand = len(all_alphas) - 1
    z_grand = {lab: float((a - alpha_grand) / s)
               for lab, a, s in zip(labels, all_alphas, all_ses)}
    report['grand_pooled_fit'] = {
        'alpha_grand_weighted_mean': alpha_grand,
        'alpha_grand_se': alpha_grand_se,
        'chi2': chi2_grand,
        'dof': dof_grand,
        'z_per_series_vs_grand': z_grand,
        'max_abs_z': max(abs(z) for z in z_grand.values()),
        'universal_at_2sigma': max(abs(z) for z in z_grand.values()) < 2.0,
        'universal_at_3sigma': max(abs(z) for z in z_grand.values()) < 3.0,
    }

    verdict = (
        'BST_RATE_UNIVERSAL_CANDIDATE_F_ANCHOR'
        if report['grand_pooled_fit']['universal_at_2sigma']
        else 'BST_RATE_FAMILY_OR_PRIME_DEPENDENT'
        if report['grand_pooled_fit']['universal_at_3sigma']
        else 'BST_RATE_STRUCTURED_NON_UNIVERSAL'
    )
    report['verdict'] = verdict

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18c] wrote {OUTPUT}')
    print()

    # Console summary
    print('== PER-PRIME α_p fits (slope of log10|rel_dev| vs bucket, sign-flipped) ==')
    print(f'{"family":>12} {"p":>4} {"alpha_p":>12} {"±se":>10} {"r2":>7} {"n_buckets":>10}')
    for fam in families:
        for p in PRIMES:
            fit = report['families'][fam]['per_prime'][str(p)]['fit']
            a = fit.get('alpha_p')
            se = fit.get('alpha_p_se')
            r2 = fit.get('r2')
            n = fit.get('n')
            if a is None:
                continue
            print(f'{fam[:12]:>12} {p:>4} {a:>+12.5f} {se:>+10.5f} {r2:>+7.4f} {n:>10}')
    print()

    print('== PRIME-INDEPENDENCE within family ==')
    for fam in families:
        pi = report['families'][fam]['prime_independence_test']
        print(f'{fam}:')
        print(f"  α_common = {pi['alpha_common_weighted']:.5f} ± {pi['alpha_common_se']:.5f}")
        print(f"  χ² = {pi['chi2']:.3f} (dof {pi['dof']})  max|z| = {pi['max_abs_z']:.3f}")
        print(f"  prime_independent_at_2sigma: {pi['prime_independent_at_2sigma']}")
    print()

    print('== FAMILY-COMPARISON (imag α_p vs real α_p) ==')
    for p in PRIMES:
        fc = report['family_comparison_imag_vs_real'].get(str(p))
        if fc is None: continue
        print(f"  p={p}: imag={fc['imag_alpha']:+.5f}±{fc['imag_se']:.5f}  "
              f"real={fc['real_alpha']:+.5f}±{fc['real_se']:.5f}  "
              f"z_diff={fc['z_imag_vs_real']:+.3f}  same@2σ: {fc['same_at_2sigma']}")
    print()

    print('== GRAND POOLED FIT (all 8 family×prime series) ==')
    g = report['grand_pooled_fit']
    print(f"  α_grand = {g['alpha_grand_weighted_mean']:.5f} ± {g['alpha_grand_se']:.5f}")
    print(f"  χ² = {g['chi2']:.3f} (dof {g['dof']})  max|z| = {g['max_abs_z']:.3f}")
    print(f"  universal_at_2σ: {g['universal_at_2sigma']}  universal_at_3σ: {g['universal_at_3sigma']}")
    print()
    print(f'VERDICT: {verdict}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
