"""
Report 18b — Cohen-Lenstra convergence by |disc| bucket.

Follow-up to report18_cohen_lenstra.py. The parent audit found that
empirical Prob(p | h) is systematically 3-25% BELOW asymptotic Cohen-Lenstra
predictions across all tested strata. The literature attributes this to
finite-disc bias (Bhargava-Shankar-Tsimerman quantitative bounds).

This script tests that attribution directly:
  - Stratify imaginary quadratic (2T1, complex) and real quadratic
    (2T1, real) by log10(|disc|) bucket.
  - Compute empirical Prob(p | h) per bucket at primes p ∈ {3, 5, 7, 11}.
  - Compare to asymptotic CL.
  - Test: does the signed relative deviation (emp - theo) / theo shrink
    monotonically toward 0 as |disc| grows?

If YES + the shrink rate matches the BST O(|d|^{-alpha}) prediction, this
is a clean calibration-anchor-adjacent reproduction of known convergence
behavior (Pattern 5 / known-math). If NO (deviation stays flat or grows
with |disc|), this is a frontier signal warranting full investigation.

Output: cartography/docs/report18b_cl_disc_convergence_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import sqrt
from pathlib import Path
import psycopg2

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='lmfdb', password='lmfdb')
PRIMES = [3, 5, 7, 11]


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


def run_strata(cur, galois_label, sig_bucket, theo_fn, bucket_col='log10_disc_bucket'):
    """For each |disc| bucket, count rows and p-divisibility. Return list of
    per-bucket dicts with empirical Prob(p|h), theoretical, z-score."""
    # Bucket by floor(log10(disc_abs::bigint)). Splits coarsely by discriminant
    # magnitude. Bucket edges at 10^0, 10^1, ..., 10^15+.
    sig_filter = "r2::int = 0" if sig_bucket == 'real' else "r2::int >= 1"
    cur.execute(f"""
        SELECT
          floor(log(greatest(disc_abs::bigint, 1)) / log(10))::int AS bucket,
          count(*) AS n,
          count(*) FILTER (WHERE (class_number::bigint) %% 3  = 0) AS d3,
          count(*) FILTER (WHERE (class_number::bigint) %% 5  = 0) AS d5,
          count(*) FILTER (WHERE (class_number::bigint) %% 7  = 0) AS d7,
          count(*) FILTER (WHERE (class_number::bigint) %% 11 = 0) AS d11
        FROM nf_fields
        WHERE degree::int = 2
          AND galois_label = %s
          AND {sig_filter}
          AND class_number IS NOT NULL
          AND disc_abs IS NOT NULL
        GROUP BY bucket
        ORDER BY bucket
    """, (galois_label,))
    rows = cur.fetchall()
    out = []
    for bucket, n, d3, d5, d7, d11 in rows:
        if n < 100:
            continue  # n ≥ 100 adequacy discipline
        divs = {3: int(d3), 5: int(d5), 7: int(d7), 11: int(d11)}
        per_prime = {}
        for p in PRIMES:
            emp = divs[p] / n
            theo = theo_fn(p)
            se = sqrt(theo * (1 - theo) / n)
            z = (emp - theo) / se if se > 0 else None
            rel = (emp - theo) / theo if theo > 0 else None
            per_prime[str(p)] = {
                'empirical': emp,
                'theoretical': theo,
                'z': z,
                'relative_deviation': rel,
            }
        out.append({
            'log10_disc_bucket': int(bucket),
            'disc_range': f'[1e{bucket}, 1e{bucket+1})',
            'n': int(n),
            'per_prime': per_prime,
        })
    return out


def convergence_monotone(bucket_results, p):
    """Check if |relative_deviation| shrinks as bucket number grows."""
    devs = [(b['log10_disc_bucket'], abs(b['per_prime'][str(p)]['relative_deviation']))
            for b in bucket_results if b['per_prime'][str(p)]['relative_deviation'] is not None]
    if len(devs) < 2:
        return {'monotone': None, 'n_points': len(devs)}
    monotone_decreasing = all(devs[i][1] <= devs[i-1][1] + 0.005
                              for i in range(1, len(devs)))
    # Check overall trend via simple correlation of bucket vs |dev|
    import numpy as np
    xs = np.array([d[0] for d in devs])
    ys = np.array([d[1] for d in devs])
    if len(xs) >= 3 and np.std(xs) > 0 and np.std(ys) > 0:
        corr = float(np.corrcoef(xs, ys)[0, 1])
    else:
        corr = None
    return {
        'n_points': len(devs),
        'strictly_monotone_decreasing_plus_slack_0.005': monotone_decreasing,
        'pearson_bucket_vs_absdev': corr,
        'trend_matches_bst_convergence': (corr is not None and corr < -0.5),
    }


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=300000')
    cur = conn.cursor()

    print('[R18b] fetching imaginary quadratic by |disc| bucket...')
    imag = run_strata(cur, '2T1', 'complex', cl_asymptote_imaginary)
    print(f'[R18b]   {len(imag)} adequate buckets')

    print('[R18b] fetching real quadratic by |disc| bucket...')
    real = run_strata(cur, '2T1', 'real', cl_asymptote_real)
    print(f'[R18b]   {len(real)} adequate buckets')

    cur.close(); conn.close()

    # Convergence diagnostics per prime
    imag_conv = {str(p): convergence_monotone(imag, p) for p in PRIMES}
    real_conv = {str(p): convergence_monotone(real, p) for p in PRIMES}

    # Count how many primes show BST-consistent convergence in each family
    imag_bst = sum(1 for p in PRIMES if imag_conv[str(p)]['trend_matches_bst_convergence'])
    real_bst = sum(1 for p in PRIMES if real_conv[str(p)]['trend_matches_bst_convergence'])

    verdict_imag = ('BST_CONVERGENCE_CONFIRMED' if imag_bst >= 3
                    else 'BST_CONVERGENCE_PARTIAL' if imag_bst >= 2
                    else 'BST_CONVERGENCE_REJECTED')
    verdict_real = ('BST_CONVERGENCE_CONFIRMED' if real_bst >= 3
                    else 'BST_CONVERGENCE_PARTIAL' if real_bst >= 2
                    else 'BST_CONVERGENCE_REJECTED')

    result = {
        'task': 'report18b_cl_disc_convergence',
        'parent': 'report18_cohen_lenstra',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'claim_under_test': (
            'The systematic empirical-below-asymptotic deviation found in '
            'Report 18 is the Bhargava-Shankar-Tsimerman finite-|disc| '
            'convergence phenomenon. If so, |relative_deviation| should '
            'shrink as |disc| bucket grows.'
        ),
        'primes_tested': PRIMES,
        'imaginary_quadratic': {
            'buckets': imag,
            'convergence_diagnostics_per_prime': imag_conv,
            'bst_consistent_primes_out_of_4': imag_bst,
            'verdict': verdict_imag,
        },
        'real_quadratic': {
            'buckets': real,
            'convergence_diagnostics_per_prime': real_conv,
            'bst_consistent_primes_out_of_4': real_bst,
            'verdict': verdict_real,
        },
        'global_verdict': (
            'BST_CONVERGENCE_CONFIRMED_BOTH_FAMILIES'
            if imag_bst >= 3 and real_bst >= 3
            else 'MIXED' if imag_bst + real_bst >= 4
            else 'BST_CONVERGENCE_REJECTED'
        ),
    }

    outpath = Path('cartography/docs/report18b_cl_disc_convergence_results.json')
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with open(outpath, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f'[R18b] wrote {outpath}')
    print()
    print('== IMAGINARY QUADRATIC — |rel_dev| by bucket ==')
    print(f'{"bucket":>8} {"n":>10} {"p=3":>10} {"p=5":>10} {"p=7":>10} {"p=11":>10}')
    for b in imag:
        row = f'{b["log10_disc_bucket"]:>8} {b["n"]:>10,}'
        for p in PRIMES:
            rel = b['per_prime'][str(p)]['relative_deviation']
            row += f'  {rel*100:+.2f}%' if rel is not None else '         —'
        print(row)
    for p in PRIMES:
        d = imag_conv[str(p)]
        print(f'  p={p}: pearson(bucket, |rel_dev|) = {d["pearson_bucket_vs_absdev"]}, BST-consistent: {d["trend_matches_bst_convergence"]}')
    print(f'Imaginary verdict: {verdict_imag}')
    print()
    print('== REAL QUADRATIC — |rel_dev| by bucket ==')
    print(f'{"bucket":>8} {"n":>10} {"p=3":>10} {"p=5":>10} {"p=7":>10} {"p=11":>10}')
    for b in real:
        row = f'{b["log10_disc_bucket"]:>8} {b["n"]:>10,}'
        for p in PRIMES:
            rel = b['per_prime'][str(p)]['relative_deviation']
            row += f'  {rel*100:+.2f}%' if rel is not None else '         —'
        print(row)
    for p in PRIMES:
        d = real_conv[str(p)]
        print(f'  p={p}: pearson(bucket, |rel_dev|) = {d["pearson_bucket_vs_absdev"]}, BST-consistent: {d["trend_matches_bst_convergence"]}')
    print(f'Real verdict: {verdict_real}')
    print()
    print(f'Global verdict: {result["global_verdict"]}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
