"""
Report 18g — Fit the convergence rate of the Scholz ratio toward 3/2.

Parent: R18f. That task found E[3^r_3 | imag] / E[3^r_3 | real] converges
monotonically to CL-predicted 3/2 as |disc| grows, with deviation shrinking
from 3.5% (bucket 3) to 1.1% (bucket 6). This script FITS the convergence
exponent and compares it to the Davenport-Heilbronn 1/6 rate found in R18e.

Model: |ratio(bucket) - 3/2| = c · 10^(-α_scholz · bucket).
Equivalently: log10|dev_from_1.5| = log10(c) - α_scholz · bucket.

Hypothesis (triple-confirmation): if α_scholz ≈ 1/6 ≈ 0.167, then
Davenport-Heilbronn's 1/6 is a UNIVERSAL finite-|disc| convergence rate
for 3-torsion observables on quadratic class groups, not just for the
specific Prob(3|h) statistic.

Output: cartography/docs/report18g_scholz_rate_fit_results.json.

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

INPUT = Path('cartography/docs/report18f_scholz_3rank_results.json')
OUTPUT = Path('cartography/docs/report18g_scholz_rate_fit_results.json')


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
    if not INPUT.exists():
        print(f'ERROR: {INPUT} not found — run R18f first', file=sys.stderr)
        sys.exit(1)
    parent = json.load(open(INPUT))

    scholz_data = parent['scholz_reflection_check_per_bucket']
    # Extract (bucket, |ratio - 1.5|) for each bucket
    pts = []
    for b_str, d in scholz_data.items():
        ratio = d.get('ratio_imag_over_real')
        if ratio is None: continue
        dev = abs(ratio - 1.5)
        if dev <= 0: continue
        pts.append((int(b_str), dev, ratio))

    pts.sort()
    xs = [p[0] for p in pts]
    ys = [log10(p[1]) for p in pts]

    fit = linreg_with_se(xs, ys)
    alpha_scholz = -fit['slope'] if fit['slope'] is not None else None
    alpha_scholz_se = fit['slope_se']

    # Compare to DH 1/6 (from R18e)
    dh = 1 / 6
    z_vs_dh = (alpha_scholz - dh) / alpha_scholz_se if (alpha_scholz_se and alpha_scholz_se > 0) else None

    # Also compare to the raw α_{p=3} from R18d for cross-reference
    # (those are Prob(p|h) convergence exponents)
    alpha_p3_imag = 0.16503
    alpha_p3_real = 0.15797

    # Projection: if alpha_scholz ≈ 1/6, at what bucket does |dev| fall below 0.001?
    if alpha_scholz is not None and alpha_scholz > 0:
        c_p = 10 ** fit['intercept']
        bucket_for_001_dev = (log10(c_p) - log10(0.001)) / alpha_scholz
    else:
        c_p = None
        bucket_for_001_dev = None

    report = {
        'task': 'report18g_scholz_rate_fit',
        'parent': 'report18f_scholz_3rank',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'hypothesis': (
            'Davenport-Heilbronn 1/6 is the UNIVERSAL finite-|disc| convergence rate '
            'for 3-torsion observables on quadratic class groups. If so, fitting '
            '|Scholz_ratio - 3/2| vs log10(|disc|) bucket should yield an exponent '
            'α_scholz ≈ 1/6 ≈ 0.1667.'
        ),
        'data_points': pts,
        'fit': fit,
        'alpha_scholz': alpha_scholz,
        'alpha_scholz_se': alpha_scholz_se,
        'c_coefficient': c_p,
        'cross_check_alpha_p3_imag_from_R18e': alpha_p3_imag,
        'cross_check_alpha_p3_real_from_R18e': alpha_p3_real,
        'dh_1_6_prediction': dh,
        'z_vs_dh_1_6': z_vs_dh,
        'match_dh_at_2sigma': abs(z_vs_dh) < 2.0 if z_vs_dh is not None else None,
        'match_dh_at_1sigma': abs(z_vs_dh) < 1.0 if z_vs_dh is not None else None,
        'projection_bucket_for_0.001_dev': bucket_for_001_dev,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18g] wrote {OUTPUT}')
    print()

    print('== SCHOLZ RATIO CONVERGENCE FIT ==')
    print(f'  model: |ratio(bucket) - 1.5| = c · 10^(-alpha_scholz · bucket)')
    print()
    print('  Data:')
    print(f'  {"bucket":>7} {"ratio":>10} {"dev_from_1.5":>15} {"log10|dev|":>12}')
    for (b, d, r_) in pts:
        print(f'  {b:>7} {r_:>10.5f} {d:>+15.5f} {log10(d):>+12.5f}')
    print()
    print(f'  alpha_scholz = {alpha_scholz:.5f} ± {alpha_scholz_se:.5f}')
    print(f'  c coefficient = {c_p:.5f}')
    print(f'  R² = {fit["r2"]:.5f}  (n={fit["n"]})')
    print()
    print('== COMPARISON TO DAVENPORT-HEILBRONN 1/6 ==')
    print(f'  alpha_scholz = {alpha_scholz:+.5f}')
    print(f'  alpha_{{p=3, imag}} (R18d) = {alpha_p3_imag:+.5f}')
    print(f'  alpha_{{p=3, real}} (R18d) = {alpha_p3_real:+.5f}')
    print(f'  DH 1/6 = {dh:+.5f}')
    print(f'  z_scholz_vs_dh = {z_vs_dh:+.3f}')
    print(f'  match @ 2σ: {abs(z_vs_dh) < 2.0}')
    print(f'  match @ 1σ: {abs(z_vs_dh) < 1.0}')
    print()
    print(f'  Projection: at what log10|disc| would deviation drop to 0.001?')
    print(f'  bucket ≈ {bucket_for_001_dev:.1f}  (|disc| ≈ 10^{bucket_for_001_dev:.1f})')

    return 0


if __name__ == '__main__':
    sys.exit(main())
