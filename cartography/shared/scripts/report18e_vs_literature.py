"""
Report 18e — Compare empirical α_p against literature BST / CL-convergence
predictions.

Parent: R18d (8 primes × 2 families, empirical α_p fits). This script
encodes a handful of literature-predicted convergence exponents and tests
which (if any) match the empirical α_p at each (family, prime).

Literature sources (confidence varies):
  L1. Davenport-Heilbronn 1971: asymptotic for cubic-field count;
      error term `O(X^{-1/6})` for the 3-torsion contribution to
      quadratic class groups → PRED α_{p=3, imag} ≈ 1/6 ≈ 0.1667.

  L2. Bhargava-Shankar-Tsimerman 2013: effective rate for average
      |Cl(K)[p]| minus 1 over |disc| ≤ X scales as `O(X^{-1/p})` for
      "good" primes → PRED α_p ≈ 1/p asymptotically, but for FINITE
      |disc| ~ 10^5-10^6 the EFFECTIVE rate is often closer to 1/4-1/3.

  L3. Ellenberg-Pierce-Wood / Zhao / Klüners: bounds of form
      `O(X^{-δ})` with δ small (δ ∈ [1/8, 1/4]) for k-th moments of
      p-parts of class groups.

  L4. Cohen-Lenstra numerical tables (Cohen 1983; Buhler-Gupta 1997):
      for imag quad, at |d| < 10^5, bias ~ 5-15%; at |d| < 10^8,
      bias ~ 1-3%. Consistent with α ~ 0.15-0.25 across primes.

Caveat: these literature rates are bounds / upper-envelope estimates, NOT
pinned-down closed forms for Prob(p | h) specifically. Our empirical α_p
is one of the first direct fits on LMFDB-scale data.

Output: cartography/docs/report18e_vs_literature_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import sqrt
from pathlib import Path

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

INPUT = Path('cartography/docs/report18d_extended_primes_results.json')
OUTPUT = Path('cartography/docs/report18e_vs_literature_results.json')


# Literature-predicted α_p exponents. Confidence: 'strong' = pinned-down
# closed form; 'weak' = order-of-magnitude upper/lower envelope.
LITERATURE_PREDICTIONS = [
    {
        'name': 'DH_1/6',
        'label': 'Davenport-Heilbronn 1971 — α = 1/6 for p=3 imag quad',
        'applies_to': [('imaginary_quadratic', '3')],
        'predicted_alpha': 1 / 6,
        'confidence': 'strong',
        'note': 'Error-term exponent in cubic field counting; translates to α_{p=3}.',
    },
    {
        'name': 'BST_1_over_p',
        'label': 'BST 2013 asymptotic — α = 1/p',
        'applies_to': [('imaginary_quadratic', str(p)) for p in (3, 5, 7, 11, 13, 17, 19, 23)]
                     + [('real_quadratic',      str(p)) for p in (3, 5, 7, 11, 13, 17, 19, 23)],
        'predicted_alpha_fn': lambda p: 1 / int(p),
        'confidence': 'weak',
        'note': 'True as asymptotic p → ∞; at LMFDB |disc| scale, likely FAR too small for larger primes.',
    },
    {
        'name': 'EPW_1_over_4',
        'label': 'EPW / BST effective — α ≈ 1/4',
        'applies_to': [('imaginary_quadratic', str(p)) for p in (5, 7, 11, 13, 17, 19, 23)]
                     + [('real_quadratic',      str(p)) for p in (5, 7, 11, 13, 17, 19, 23)],
        'predicted_alpha': 1 / 4,
        'confidence': 'weak',
        'note': 'Common effective bound in Ellenberg-Pierce-Wood-type arguments.',
    },
    {
        'name': 'Klueners_1_over_8',
        'label': 'Klüners 2006 — α = 1/8',
        'applies_to': [('imaginary_quadratic', str(p)) for p in (3, 5, 7)]
                     + [('real_quadratic',      str(p)) for p in (3, 5, 7)],
        'predicted_alpha': 1 / 8,
        'confidence': 'weak',
        'note': 'Unconditional lower bound for p-torsion statistics.',
    },
]


def main():
    if not INPUT.exists():
        print(f'ERROR: {INPUT} not found — run R18d first', file=sys.stderr)
        sys.exit(1)
    parent = json.load(open(INPUT))

    # Pull α_p fits from R18d
    fam_fits = {}
    for fam_name in ('imaginary_quadratic', 'real_quadratic'):
        fam_fits[fam_name] = parent['families'][fam_name]['alpha_p_fits']

    # For each (family, prime, prediction) compute z-score
    comparisons = []
    for fam_name in fam_fits:
        for p_str, fit in fam_fits[fam_name].items():
            alpha = fit.get('alpha_p')
            se = fit.get('alpha_p_se')
            if alpha is None or se is None or se <= 0:
                continue
            for pred in LITERATURE_PREDICTIONS:
                if (fam_name, p_str) not in pred['applies_to']:
                    continue
                predicted = pred['predicted_alpha_fn'](p_str) if 'predicted_alpha_fn' in pred \
                           else pred['predicted_alpha']
                z = (alpha - predicted) / se
                comparisons.append({
                    'prediction_name': pred['name'],
                    'prediction_label': pred['label'],
                    'confidence': pred['confidence'],
                    'family': fam_name,
                    'prime': int(p_str),
                    'empirical_alpha': alpha,
                    'empirical_se': se,
                    'predicted_alpha': predicted,
                    'z': z,
                    'matches_at_2sigma': abs(z) < 2.0,
                    'matches_at_3sigma': abs(z) < 3.0,
                })

    # Summarize per prediction: how many (family, prime) matches at 2σ?
    by_prediction = {}
    for c in comparisons:
        name = c['prediction_name']
        d = by_prediction.setdefault(name, {'label': c['prediction_label'],
                                            'confidence': c['confidence'],
                                            'n_checks': 0, 'n_match_2sigma': 0,
                                            'n_match_3sigma': 0, 'details': []})
        d['n_checks'] += 1
        if c['matches_at_2sigma']:
            d['n_match_2sigma'] += 1
        if c['matches_at_3sigma']:
            d['n_match_3sigma'] += 1
        d['details'].append({
            'family': c['family'], 'prime': c['prime'],
            'empirical': c['empirical_alpha'],
            'predicted': c['predicted_alpha'],
            'z': c['z'],
        })

    # Best-match prediction
    best = max(by_prediction.items(),
               key=lambda kv: kv[1]['n_match_2sigma'])
    verdict = {
        'best_prediction': best[0],
        'best_match_2sigma': f'{best[1]["n_match_2sigma"]}/{best[1]["n_checks"]}',
        'best_match_3sigma': f'{best[1]["n_match_3sigma"]}/{best[1]["n_checks"]}',
    }

    report = {
        'task': 'report18e_vs_literature',
        'parent': 'report18d_extended_primes',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'caveat': (
            'Literature α-exponents are order-of-magnitude envelopes or bounds, '
            'not closed-form predictions for Prob(p|h). DH_1/6 is the only '
            'strong-confidence pinpoint; others are weak comparisons.'
        ),
        'predictions_tested': [
            {k: v for k, v in p.items() if k != 'applies_to' and k != 'predicted_alpha_fn'}
            for p in LITERATURE_PREDICTIONS
        ],
        'by_prediction': by_prediction,
        'all_comparisons': comparisons,
        'best_match_summary': verdict,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18e] wrote {OUTPUT}')
    print()

    # Console summary
    print('== LITERATURE PREDICTION MATCH SCORECARD ==')
    for name, d in by_prediction.items():
        print(f'  {name:20s} [{d["confidence"]:>6}]: '
              f'{d["n_match_2sigma"]:>3}/{d["n_checks"]:<3} @ 2σ,  '
              f'{d["n_match_3sigma"]:>3}/{d["n_checks"]:<3} @ 3σ  '
              f'— {d["label"]}')
    print()

    # Strong-confidence detail: DH_1/6
    dh = by_prediction.get('DH_1/6')
    if dh:
        print('== DH_1/6 DETAIL (strong-confidence pinpoint) ==')
        for c in dh['details']:
            verdict_str = '✓' if abs(c['z']) < 2 else ('~' if abs(c['z']) < 3 else '✗')
            print(f"  {c['family']:>20} p={c['prime']:>3}: "
                  f"empirical={c['empirical']:+.5f}  predicted={c['predicted']:+.5f}  "
                  f"z={c['z']:+.3f}  {verdict_str}")
    print()

    # Quick imag-imag match of empirical α_{p=3} to 1/6
    print('== MATCHES TO DAVENPORT-HEILBRONN 1/6 ==')
    for c in comparisons:
        if c['prediction_name'] == 'DH_1/6':
            print(f"  {c['family']} p={c['prime']}: "
                  f"empirical = {c['empirical_alpha']:.5f}, "
                  f"predicted = {c['predicted_alpha']:.5f} (= 1/6), "
                  f"z = {c['z']:+.3f}, match@2σ: {c['matches_at_2sigma']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
