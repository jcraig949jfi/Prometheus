"""
Report 18h — BST-style convergence on S3 cubic fields.

Parent: R18b/e/f/g (BST convergence on quadratic class groups). This script
extends the same methodology to S3 cubic fields (degree=3, galois_label=3T2).

Bhargava 2005 proved the Davenport-Heilbronn analogue for S3 cubics: the
average number of 3-torsion elements in Cl(K) over S3 cubic fields with
|disc| ≤ X follows a DH-type asymptotic. Does empirical Prob(p | h) on our
LMFDB S3-cubic data converge with the same universal 1/6 rate?

Cohen-Martinet predictions for S3 cubic fields:
  - For p ∤ |S3| = 6 (i.e., p ∈ {5, 7, 11, 13, ...}):
      Signature (1,1) totally complex: Prob(p|h) = 1 - ∏_{k=2}^∞ (1 - p^-k)
        (matches real quadratic CL by coincidence of the unit-rank formula)
      Signature (3,0) totally real:    Prob(p|h) = 1 - ∏_{k=3}^∞ (1 - p^-k)
        (one more missing factor per extra unit-rank dimension)
  - For p | |S3| (p = 2 or 3): Bhargava-Varma refined heuristic; we do NOT
    pin a closed form here — just test empirical convergence rate.

Hypothesis: after clean CL-Martinet comparison at p ≥ 5, the convergence
rate α should match DH 1/6 at p=5,7,11 for both signatures.

Output: cartography/docs/report18h_s3_cubic_bst_results.json.

Author: Harmonia_M2_sessionD, 2026-04-18.
"""
import json
import sys
import io
from math import log10, sqrt
from pathlib import Path
import numpy as np
import psycopg2

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PG = dict(host='192.168.1.176', port=5432, dbname='lmfdb',
          user='lmfdb', password='lmfdb')

PRIMES = [5, 7, 11, 13]  # avoid p=3 where CM-formula is more subtle
OUTPUT = Path('cartography/docs/report18h_s3_cubic_bst_results.json')


def cm_prob_s3_complex(p, terms=200):
    """Cohen-Martinet Prob(p | h) for S3 cubic, signature (1,1)."""
    eta = 1.0
    for k in range(2, terms + 1):
        eta *= (1 - p ** -k)
    return 1.0 - eta


def cm_prob_s3_real(p, terms=200):
    """Cohen-Martinet Prob(p | h) for S3 cubic, signature (3,0)."""
    eta = 1.0
    for k in range(3, terms + 1):
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

    filter_cols = ',\n          '.join(
        f"count(*) FILTER (WHERE (class_number::bigint) % {p} = 0) AS d{p}"
        for p in PRIMES
    )

    families = {
        'complex_s3': {'sig': 'r2::int >= 1', 'theo_fn': cm_prob_s3_complex},
        'real_s3':    {'sig': 'r2::int = 0',  'theo_fn': cm_prob_s3_real},
    }

    results = {}
    for fam_name, fam in families.items():
        print(f'[R18h] fetching S3 cubic {fam_name}...')
        # S3 cubic discriminants can exceed bigint (10^18) — cast to numeric to
        # compute the log10 bucket safely.
        cur.execute(f"""
            SELECT
              floor(log(greatest(disc_abs::numeric, 1)) / log(10))::int AS bucket,
              count(*) AS n,
              {filter_cols}
            FROM nf_fields
            WHERE degree::int = 3
              AND galois_label = '3T2'
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
            # LMFDB S3 cubic enumeration is complete through bucket 6
            # (|disc| ≤ 10^7); buckets >= 7 are a different source / selection
            # bias regime. Restrict to complete-coverage window.
            if n < 500:
                continue
            if bucket > 6:
                continue
            per_prime = {}
            for i, p in enumerate(PRIMES):
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
        for p in PRIMES:
            pts = [(b['log10_disc_bucket'], log10(abs(b['per_prime'][str(p)]['relative_deviation'])))
                   for b in buckets
                   if b['per_prime'][str(p)]['relative_deviation'] is not None
                   and abs(b['per_prime'][str(p)]['relative_deviation']) > 0]
            if len(pts) >= 3:
                xs = [x[0] for x in pts]; ys = [x[1] for x in pts]
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

    # Compare all α_p to DH 1/6
    dh = 1 / 6
    dh_comparisons = []
    for fam_name in results:
        for p in PRIMES:
            f_ = results[fam_name]['alpha_p_fits'][str(p)]
            a = f_.get('alpha_p')
            se = f_.get('alpha_p_se')
            if a is None or se is None or se <= 0:
                continue
            z = (a - dh) / se
            dh_comparisons.append({
                'family': fam_name, 'prime': p,
                'alpha_p': a, 'se': se,
                'dh_1_6': dh, 'z': z,
                'match_2sigma': abs(z) < 2.0,
            })

    n_match_2s = sum(1 for c in dh_comparisons if c['match_2sigma'])
    n_total = len(dh_comparisons)

    report = {
        'task': 'report18h_s3_cubic_bst',
        'parent': 'report18g_scholz_rate_fit',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'hypothesis': (
            'DH 1/6 convergence rate generalizes from quadratic (R18e) to S3 cubic. '
            'Empirical α_p for S3 cubic at p ∈ {5, 7, 11, 13} should match 1/6.'
        ),
        'primes_tested': PRIMES,
        'families': results,
        'dh_1_6_comparisons': dh_comparisons,
        'dh_match_score': f'{n_match_2s}/{n_total} @ 2σ',
        'verdict': (
            'DH_1_6_GENERALIZES_TO_S3_CUBIC' if n_match_2s == n_total
            else 'DH_1_6_PARTIAL_GENERALIZATION' if n_match_2s >= n_total // 2
            else 'DH_1_6_DOES_NOT_GENERALIZE_TO_S3'
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18h] wrote {OUTPUT}')
    print()

    # Console summary
    print('== S3 CUBIC CM PRED vs EMPIRICAL, per bucket ==')
    for fam_name in results:
        print(f'{fam_name}:')
        print(f'  {"bucket":>7} {"n":>10} {"p=5 emp/theo":>18} {"p=7 emp/theo":>18} '
              f'{"p=11 emp/theo":>18} {"p=13 emp/theo":>18}')
        for b in results[fam_name]['buckets']:
            row = f'  {b["log10_disc_bucket"]:>7} {b["n"]:>10,}'
            for p in PRIMES:
                d = b['per_prime'][str(p)]
                row += f'  {d["empirical"]:.4f}/{d["theoretical"]:.4f}'
            print(row)
    print()

    print('== α_p FITS FOR S3 CUBIC (log-log slope) ==')
    print(f'  {"family":>12} {"p":>4} {"alpha_p":>12} {"±se":>10} {"r²":>7} {"z vs DH 1/6":>12}')
    for c in dh_comparisons:
        print(f'  {c["family"]:>12} {c["prime"]:>4} {c["alpha_p"]:>+12.5f} '
              f'{c["se"]:>+10.5f} {"—":>7} {c["z"]:>+12.3f}')
    print()
    print(f'DH 1/6 match score: {n_match_2s}/{n_total} @ 2σ')
    print(f'VERDICT: {report["verdict"]}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
