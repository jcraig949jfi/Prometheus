"""
Report 18p — Amplitude-normalized regime-transition test.

Parent: R18o. The 2-term fit rel_dev = c1·X^(-1/6) + c2·X^(-1/3) broke down
at p≥13 in imaginary quadratic. Possible cause: the secondary-term
coefficient c1 scales with the CL asymptote amplitude CL(p). Model C
normalizes this out:

  Model C: rel_dev / CL(p) = d1 · X^(-1/6) + d2 · X^(-1/3)

If d1 is roughly prime-independent (i.e., the secondary term scales as
CL(p) · X^(-1/6) across primes), this is the clean form of the regime-
transition hypothesis.

Alternatively: d2 might be the one that is prime-independent. Either
way, Model C disambiguates the source of the c1 variation in R18o.

Output: cartography/docs/report18p_amplitude_normalized_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import sqrt
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

INPUT = Path('cartography/docs/report18d_extended_primes_results.json')
OUTPUT = Path('cartography/docs/report18p_amplitude_normalized_results.json')


def model_c_fit(xs_bucket, rel_devs):
    """Fit rel_dev = d1·X^(-1/6) + d2·X^(-1/3) where rel_dev here already
    equals (emp - CL)/CL. So d1, d2 are dimensionless coefficients.

    Same structure as Model B in R18o but with the interpretation that d1
    is expected to be roughly constant across primes if regime transition
    holds."""
    xs = np.asarray(xs_bucket, dtype=float)
    ys = np.asarray(rel_devs, dtype=float)
    u1 = 10 ** (-xs / 6)
    u2 = 10 ** (-xs / 3)
    A = np.column_stack([u1, u2])
    (d1, d2), _, _, _ = np.linalg.lstsq(A, ys, rcond=None)
    yhat = d1 * u1 + d2 * u2
    residuals = ys - yhat
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((ys - ys.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {
        'd1': float(d1), 'd2': float(d2),
        'chi2': ss_res, 'r2': r2,
        'residuals': residuals.tolist(),
        'n_buckets': int(len(xs)),
    }


def universality_test(coeffs_by_prime):
    """Given {p: coeff}, test if values are constant across primes.
    Returns mean, std, and max absolute deviation from mean."""
    vals = np.array([v for v in coeffs_by_prime.values() if v is not None and np.isfinite(v)])
    if len(vals) < 2:
        return None
    mean = float(vals.mean())
    std = float(vals.std(ddof=1)) if len(vals) > 1 else 0.0
    return {
        'mean': mean, 'std': std, 'n': int(len(vals)),
        'max_abs_deviation': float(np.max(np.abs(vals - mean))),
        'cv_percent': float(std / abs(mean) * 100) if abs(mean) > 1e-12 else None,
    }


def main():
    if not INPUT.exists():
        print(f'ERROR: {INPUT} not found', file=sys.stderr); sys.exit(1)
    parent = json.load(open(INPUT))

    PRIMES = [3, 5, 7, 11, 13, 17, 19, 23]
    families = ('imaginary_quadratic', 'real_quadratic')

    report = {
        'task': 'report18p_amplitude_normalized',
        'parent': 'report18o_regime_transition',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'model_c': 'rel_dev = d1 · X^(-1/6) + d2 · X^(-1/3)',
        'hypothesis': (
            'If rel_dev is already normalized by CL(p) (which it IS — rel_dev is '
            'defined as (emp - CL)/CL), then the coefficients d1, d2 from a 2-term '
            'fit may be prime-independent. Test: is either d1 or d2 cluster-constant '
            'across primes within a family?'
        ),
        'families': {},
    }

    for fam_name in families:
        fam_data = parent['families'][fam_name]['buckets']

        per_prime = {}
        for p in PRIMES:
            pts = []
            for b in fam_data:
                rel = b['per_prime'][str(p)]['relative_deviation']
                if rel is None: continue
                pts.append((b['log10_disc_bucket'], rel))
            if len(pts) < 4:
                per_prime[p] = {'note': f'only {len(pts)} buckets'}
                continue
            xs = [pt[0] for pt in pts]
            devs = [pt[1] for pt in pts]
            per_prime[p] = model_c_fit(xs, devs)

        # Universality test on d1 and d2
        d1s = {p: per_prime[p].get('d1') for p in PRIMES if 'd1' in per_prime[p]}
        d2s = {p: per_prime[p].get('d2') for p in PRIMES if 'd2' in per_prime[p]}
        u_d1 = universality_test(d1s)
        u_d2 = universality_test(d2s)

        # Also check sign stability
        d1_signs = {p: ('pos' if d1s[p] and d1s[p] > 0 else 'neg') for p in d1s if d1s[p] is not None}
        d2_signs = {p: ('pos' if d2s[p] and d2s[p] > 0 else 'neg') for p in d2s if d2s[p] is not None}

        report['families'][fam_name] = {
            'per_prime': per_prime,
            'd1_values_by_prime': d1s,
            'd2_values_by_prime': d2s,
            'd1_universality': u_d1,
            'd2_universality': u_d2,
            'd1_sign_stability': d1_signs,
            'd2_sign_stability': d2_signs,
        }

    # Headline: which coefficient is cluster-constant?
    imag = report['families']['imaginary_quadratic']
    real = report['families']['real_quadratic']

    verdicts = {}
    for fam_name, fam in zip(('imaginary', 'real'), (imag, real)):
        d1_u = fam['d1_universality']; d2_u = fam['d2_universality']
        cv1 = d1_u['cv_percent'] if d1_u else None
        cv2 = d2_u['cv_percent'] if d2_u else None
        # Which coefficient has smaller coefficient of variation (CV)?
        verdicts[fam_name] = {
            'd1_cv_percent': cv1,
            'd2_cv_percent': cv2,
            'more_universal': 'd2' if (cv1 is not None and cv2 is not None and cv2 < cv1)
                              else 'd1' if cv1 is not None else None,
        }

    report['verdicts'] = verdicts
    # Final call
    if verdicts['imaginary']['d2_cv_percent'] and verdicts['imaginary']['d2_cv_percent'] < 30:
        report['final_verdict'] = 'REGIME_TRANSITION_CONFIRMED — d2 cluster-constant'
    elif verdicts['imaginary']['d1_cv_percent'] and verdicts['imaginary']['d1_cv_percent'] < 30:
        report['final_verdict'] = 'SECONDARY_DOMINATES — d1 cluster-constant'
    else:
        report['final_verdict'] = 'MIXED_NO_CLEAN_UNIVERSALITY'

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18p] wrote {OUTPUT}')
    print()

    for fam_name in families:
        fam = report['families'][fam_name]
        print(f'== {fam_name.upper()} ==')
        print(f'{"p":>3} {"d1":>12} {"d2":>12} {"r2":>8}')
        for p in PRIMES:
            pp = fam['per_prime'].get(p, {})
            if 'd1' in pp:
                print(f'{p:>3} {pp["d1"]:>+12.5f} {pp["d2"]:>+12.5f} {pp["r2"]:>+8.4f}')
        u1 = fam['d1_universality']; u2 = fam['d2_universality']
        if u1:
            print(f'  d1 universality: mean={u1["mean"]:+.5f}, std={u1["std"]:.5f}, CV={u1["cv_percent"]:.1f}%')
        if u2:
            print(f'  d2 universality: mean={u2["mean"]:+.5f}, std={u2["std"]:.5f}, CV={u2["cv_percent"]:.1f}%')
        print()

    print(f'FINAL: {report["final_verdict"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
