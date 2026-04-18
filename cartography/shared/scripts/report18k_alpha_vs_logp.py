"""
Report 18k — Does α_p scale with log(p)? Cross-stratum regression.

Parent: R18d, R18h, R18j. We now have empirical α_p (Cohen-Lenstra
convergence exponent) across multiple strata and multiple primes. The
cluster-constancy hypothesis failed in complex-S3 (R18j). Question:
is there a CLEAN FUNCTIONAL FORM α_p = f(log p) within each stratum?

Method: for each (family, signature) stratum with ≥4 primes fit, linear
regression of α_p on log(p). If R² high → clean log(p) scaling.
Otherwise the α_p variation with p is irregular.

Strata surveyed:
  - Imaginary quadratic (R18d, 8 primes)
  - Real quadratic (R18d, 8 primes)
  - Complex S3 cubic (R18h, 4 primes)
  - Real S3 cubic (R18h, 4 primes)
  - D4 complex (R18j, 4 primes) — noting negative α issue
  - D4 real (R18j, 4 primes)
  - S4 complex (R18j, 4 primes)

Output: cartography/docs/report18k_alpha_vs_logp_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import log, log10
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUTPUT = Path('cartography/docs/report18k_alpha_vs_logp_results.json')

# Collected α_p values from prior reports.
# Each entry: {prime: (alpha, se)}
STRATUM_DATA = {
    'imaginary_quadratic_R18d': {  # from R18d
        3:  (0.16503, 0.01580),
        5:  (0.28138, 0.00825),
        7:  (0.26923, 0.03880),
        11: (0.25735, 0.03594),
        13: (0.34001, 0.03706),
        17: (0.34733, 0.04527),
        19: (0.38469, 0.01853),
        23: (0.33621, 0.03875),
    },
    'real_quadratic_R18d': {
        3:  (0.15797, 0.01291),
        5:  (0.22995, 0.01687),
        7:  (0.24530, 0.01670),
        11: (0.23102, 0.01761),
        13: (0.21755, 0.02665),
        17: (0.20731, 0.01550),
        19: (0.17297, 0.01205),
        23: (0.15507, 0.01912),
    },
    'complex_s3_R18h': {
        5:  (0.21321, 0.00429),
        7:  (0.19637, 0.03747),
        11: (0.27917, 0.01889),
        13: (0.22314, 0.02397),
    },
    'real_s3_R18h': {
        5:  (0.15797, 0.00726),
        7:  (0.13328, 0.02147),
        11: (0.14734, 0.00160),
        13: (0.11296, 0.04958),
    },
    'd4_complex_R18j': {
        5:  (-0.13801, 0.04055),
        7:  (-0.11459, 0.03013),
        11: (-0.10496, 0.03600),
        13: (-0.13439, 0.03514),
    },
    'd4_real_R18j': {
        5:  (-0.08568, 0.02958),
        7:  (-0.12262, 0.06170),
        11: (-0.13188, 0.03239),
        13: (-0.02434, 0.06698),
    },
    's4_complex_R18j': {
        5:  (0.05865, 0.00809),
        7:  (0.05154, 0.00736),
        11: (0.04386, 0.00521),
        13: (0.04290, 0.01013),
    },
}


def weighted_linreg(xs, ys, ses):
    xs = np.asarray(xs, dtype=float); ys = np.asarray(ys, dtype=float)
    w = 1 / np.asarray(ses, dtype=float) ** 2
    W = np.sum(w)
    mx = np.sum(w * xs) / W
    my = np.sum(w * ys) / W
    sxx = np.sum(w * (xs - mx) ** 2)
    sxy = np.sum(w * (xs - mx) * (ys - my))
    slope = sxy / sxx if sxx > 0 else None
    intercept = my - slope * mx if slope is not None else None
    yhat = slope * xs + intercept if slope is not None else None
    ss_res = np.sum(w * (ys - yhat) ** 2) if yhat is not None else None
    ss_tot = np.sum(w * (ys - my) ** 2)
    r2 = 1 - ss_res / ss_tot if (ss_tot > 0 and ss_res is not None) else None
    slope_se = float(np.sqrt(1 / sxx)) if sxx > 0 else None
    # χ² of residuals around the fit
    chi2 = float(np.sum(((ys - yhat) / np.asarray(ses, dtype=float)) ** 2)) if yhat is not None else None
    return {
        'slope_alpha_per_log_p': float(slope) if slope is not None else None,
        'slope_se': slope_se,
        'intercept': float(intercept) if intercept is not None else None,
        'r2_weighted': float(r2) if r2 is not None else None,
        'chi2': chi2,
        'dof': int(len(xs) - 2),
        'n_primes': int(len(xs)),
    }


def main():
    report = {
        'task': 'report18k_alpha_vs_logp',
        'parent_reports': ['report18d_extended_primes', 'report18h_s3_cubic_bst', 'report18j_quartic_bst'],
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'model': 'α_p = β_0 + β_1 · log(p)',
        'strata': {},
    }

    for name, prime_data in STRATUM_DATA.items():
        primes = sorted(prime_data.keys())
        alphas = [prime_data[p][0] for p in primes]
        ses = [prime_data[p][1] for p in primes]
        logp = [log(p) for p in primes]

        fit = weighted_linreg(logp, alphas, ses)
        # Additional: verdict
        chi2_reduced = fit['chi2'] / fit['dof'] if fit['dof'] > 0 else None
        # Good log(p) fit: R² > 0.8 AND chi2_reduced < 2
        if fit['r2_weighted'] is not None:
            good_fit = fit['r2_weighted'] > 0.8 and (chi2_reduced is None or chi2_reduced < 2.0)
        else:
            good_fit = None

        report['strata'][name] = {
            'primes': primes,
            'alphas': alphas,
            'ses': ses,
            'log_p': logp,
            'fit': fit,
            'chi2_reduced': chi2_reduced,
            'clean_log_p_scaling': good_fit,
        }

    # Collect "clean log(p) scaling" strata
    clean = {name for name, d in report['strata'].items() if d.get('clean_log_p_scaling')}
    report['clean_log_p_scaling_strata'] = sorted(clean)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18k] wrote {OUTPUT}')
    print()

    # Console
    print('== α_p vs log(p) FITS PER STRATUM ==')
    print(f'{"stratum":>28} {"n":>3} {"slope":>12} {"intercept":>12} {"R²":>8} {"χ²/dof":>8} {"clean?":>7}')
    for name, d in report['strata'].items():
        f_ = d['fit']
        print(f"{name:>28} {f_['n_primes']:>3} "
              f"{f_['slope_alpha_per_log_p']:>+12.5f} "
              f"{f_['intercept']:>+12.5f} "
              f"{f_['r2_weighted']:>+8.4f} "
              f"{d['chi2_reduced']:>+8.3f} "
              f"{str(d['clean_log_p_scaling']):>7}")
    print()
    print('Strata with clean log(p) scaling:', report['clean_log_p_scaling_strata'] or '(none)')

    return 0


if __name__ == '__main__':
    sys.exit(main())
