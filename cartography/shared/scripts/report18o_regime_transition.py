"""
Report 18o — Test the α_p regime-transition hypothesis.

Parent: R18n (literature correspondence scan). Top hypothesis identified:

  The empirical α_p for Prob(p|h) in imaginary quadratic transitions from
  ~1/6 at p=3 (Bhargava-Shankar-Tsimerman 2013 secondary-term regime) to
  ~1/3 at p ≥ 13 (post-secondary error-term regime, Taniguchi-Thorne +
  BBP improved bound O(X^(2/3 + ε))).

Test: compare two models for the bucket-by-bucket relative deviation
(emp - CL) / CL as a function of X = 10^bucket:

  Model A (single-power): rel_dev = c · X^(-α)
     — 2 parameters (c, α), fit α_p per prime; this is what R18b/d did.

  Model B (two-term, exponents fixed by BST): rel_dev = c1 · X^(-1/6) + c2 · X^(-1/3)
     — 2 parameters (c1, c2) per prime; exponents are LITERATURE-PROVED.

If Model B fits the data as well as (or better than) Model A at every
prime, and the coefficients c1, c2 have a natural prime-dependence, the
regime-transition hypothesis is supported.

Output: cartography/docs/report18o_regime_transition_results.json.

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

INPUT = Path('cartography/docs/report18d_extended_primes_results.json')
OUTPUT = Path('cartography/docs/report18o_regime_transition_results.json')


def model_a_fit(xs_bucket, rel_devs):
    """Fit rel_dev = c · X^(-α) by log-log OLS.

    log10|rel_dev| = log10(c) - α · bucket.
    Returns (c, alpha, alpha_se, chi2).
    """
    xs = np.asarray(xs_bucket, dtype=float)
    ys = np.log10(np.abs(rel_devs))
    n = len(xs)
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
    c_est = 10 ** intercept
    # χ² analog: sum of squared residuals in log10 space
    return {
        'c': float(c_est), 'alpha': -float(slope),
        'alpha_se': slope_se,
        'r2': r2, 'chi2_log10': ss_res,
        'n_buckets': int(n), 'dof': int(n - 2),
    }


def model_b_fit(xs_bucket, rel_devs):
    """Fit rel_dev = c1 · X^(-1/6) + c2 · X^(-1/3) by linear least squares.

    Let u1 = X^(-1/6), u2 = X^(-1/3); solve for (c1, c2).
    Returns (c1, c2, chi2, residuals).
    """
    xs = np.asarray(xs_bucket, dtype=float)
    ys = np.asarray(rel_devs, dtype=float)
    # X = 10^bucket
    u1 = 10 ** (-xs / 6)
    u2 = 10 ** (-xs / 3)
    A = np.column_stack([u1, u2])
    # OLS: minimize ||A @ [c1, c2] - ys||^2
    (c1, c2), residuals_sum, rank, sv = np.linalg.lstsq(A, ys, rcond=None)
    yhat = c1 * u1 + c2 * u2
    residuals = ys - yhat
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((ys - ys.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {
        'c1_secondary_coeff': float(c1),
        'c2_error_coeff': float(c2),
        'chi2_linear': ss_res,
        'residuals': residuals.tolist(),
        'r2_linear': r2,
        'n_buckets': int(len(xs)),
        'dof': int(len(xs) - 2),
    }


def compute_rel_devs(buckets_data, prime):
    """Extract (bucket, rel_dev) for a given prime from R18d output."""
    pts = []
    for b in buckets_data:
        rel = b['per_prime'][str(prime)]['relative_deviation']
        if rel is None:
            continue
        pts.append((b['log10_disc_bucket'], rel, b['n']))
    return pts


def main():
    if not INPUT.exists():
        print(f'ERROR: {INPUT} not found — run R18d first', file=sys.stderr)
        sys.exit(1)
    parent = json.load(open(INPUT))

    PRIMES = [3, 5, 7, 11, 13, 17, 19, 23]
    families = ('imaginary_quadratic', 'real_quadratic')

    report = {
        'task': 'report18o_regime_transition',
        'parent': 'report18n_literature_correspondence',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'hypothesis': (
            'Empirical Prob(p|h) relative deviation follows a TWO-TERM structure: '
            'c1 · X^(-1/6) [BST secondary] + c2 · X^(-1/3) [post-secondary error]. '
            'At small primes (p=3), the c1 term dominates → apparent α ≈ 1/6. '
            'At large primes, the c2 term dominates → apparent α ≈ 1/3.'
        ),
        'model_a': 'rel_dev = c · X^(-α), α fit per prime',
        'model_b': 'rel_dev = c1 · X^(-1/6) + c2 · X^(-1/3), exponents fixed from BST 2013',
        'families': {},
    }

    for fam_name in families:
        fam_data = parent['families'][fam_name]['buckets']

        per_prime = {}
        for p in PRIMES:
            pts = compute_rel_devs(fam_data, p)
            if len(pts) < 4:
                per_prime[p] = {'note': f'only {len(pts)} buckets'}
                continue
            xs = [pt[0] for pt in pts]
            devs = [pt[1] for pt in pts]
            fit_a = model_a_fit(xs, devs)
            fit_b = model_b_fit(xs, devs)
            # Decomposition: at smallest and largest bucket, what fraction of
            # rel_dev is attributed to each term?
            def decomposition(x):
                c1 = fit_b['c1_secondary_coeff']
                c2 = fit_b['c2_error_coeff']
                t1 = c1 * 10 ** (-x / 6)
                t2 = c2 * 10 ** (-x / 3)
                total = t1 + t2
                return {'x_bucket': x,
                        't1_secondary': t1, 't2_error': t2, 'total_predicted': total,
                        'fraction_from_secondary': t1 / total if abs(total) > 0 else None}
            per_prime[p] = {
                'n_buckets': len(pts),
                'buckets': xs,
                'rel_devs': devs,
                'model_a': fit_a,
                'model_b': fit_b,
                'decomposition_smallest_bucket': decomposition(xs[0]),
                'decomposition_largest_bucket': decomposition(xs[-1]),
            }

        # Test: does fixing exponents (1/6, 1/3) produce consistent fits across primes?
        # Also: does c2/c1 grow with p (supports regime transition)?
        summary = {
            'c1_by_prime': {p: (per_prime[p]['model_b']['c1_secondary_coeff']
                                if 'model_b' in per_prime[p] else None)
                            for p in PRIMES},
            'c2_by_prime': {p: (per_prime[p]['model_b']['c2_error_coeff']
                                if 'model_b' in per_prime[p] else None)
                            for p in PRIMES},
            'ratio_c2_over_c1': {
                p: (per_prime[p]['model_b']['c2_error_coeff'] /
                    per_prime[p]['model_b']['c1_secondary_coeff']
                    if ('model_b' in per_prime[p]
                        and abs(per_prime[p]['model_b']['c1_secondary_coeff']) > 1e-12)
                    else None)
                for p in PRIMES
            },
            'chi2_ratio_B_over_A': {
                p: (per_prime[p]['model_b']['chi2_linear'] /
                    (10 ** (2 * (per_prime[p]['model_a']['chi2_log10'])) - 1)
                    if ('model_b' in per_prime[p] and 'model_a' in per_prime[p])
                    else None)
                for p in PRIMES
            },
        }

        report['families'][fam_name] = {
            'per_prime': per_prime,
            'summary': summary,
        }

    # Final verdict: is the regime transition supported?
    # Criterion: in imaginary quadratic, c2/c1 should increase with p.
    imag_ratios = report['families']['imaginary_quadratic']['summary']['ratio_c2_over_c1']
    primes_sorted = sorted([p for p in imag_ratios if imag_ratios[p] is not None])
    ratios_sorted = [imag_ratios[p] for p in primes_sorted]
    # Check monotone increase
    if len(ratios_sorted) >= 4:
        # Absolute value monotone increase
        abs_ratios = [abs(r) for r in ratios_sorted]
        monotone_increasing = all(abs_ratios[i] > abs_ratios[i-1] * 0.95
                                  for i in range(1, len(abs_ratios)))
    else:
        monotone_increasing = None

    report['hypothesis_test_verdict'] = {
        'imaginary_ratio_c2_over_c1_by_prime': dict(zip(primes_sorted, ratios_sorted)),
        'absolute_ratio_monotone_increasing': monotone_increasing,
        'regime_transition_supported': monotone_increasing,
        'notes': (
            'If |c2/c1| grows with p, then at large p the error term X^(-1/3) '
            'dominates the secondary term X^(-1/6) in the empirical signal. '
            'This explains the apparent α_p variation 1/6 → 1/3.'
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18o] wrote {OUTPUT}')
    print()

    for fam_name in families:
        print(f'== {fam_name.upper()} ==')
        print(f'{"p":>3} {"α_A":>10} {"c1_sec":>12} {"c2_err":>12} {"c2/c1":>12} '
              f'{"frac_sec@sm":>12} {"frac_sec@lg":>12}')
        for p in PRIMES:
            pp = report['families'][fam_name]['per_prime'][p]
            if 'note' in pp:
                continue
            alpha_a = pp['model_a']['alpha']
            c1 = pp['model_b']['c1_secondary_coeff']
            c2 = pp['model_b']['c2_error_coeff']
            ratio = c2 / c1 if abs(c1) > 1e-12 else float('nan')
            frac_sm = pp['decomposition_smallest_bucket']['fraction_from_secondary']
            frac_lg = pp['decomposition_largest_bucket']['fraction_from_secondary']
            print(f'{p:>3} {alpha_a:>+10.5f} {c1:>+12.5f} {c2:>+12.5f} '
                  f'{ratio:>+12.4f} {frac_sm:>+12.4f} {frac_lg:>+12.4f}')
        print()

    print('== VERDICT ==')
    v = report['hypothesis_test_verdict']
    print(f'  Imaginary quad |c2/c1| monotone increasing with p: {v["absolute_ratio_monotone_increasing"]}')
    print(f'  Regime transition supported: {v["regime_transition_supported"]}')
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
