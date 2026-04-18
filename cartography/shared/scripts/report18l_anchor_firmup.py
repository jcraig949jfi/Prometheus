"""
Report 18l — Firm up the tier-2 S4 anchor + complex-S3 at p=3 (Bhargava-Varma).

Two parallel extensions of the Cohen-Lenstra cascade:

(A) S4 complex quartic: extend α_p fit to p ∈ {17, 19, 23}. Does the
    clean R18k log(p) scaling α_p = 0.086 - 0.018·log(p) continue?

(B) S3 cubic at p=3: all prior S3 work used p ∈ {5, 7, 11, 13} because
    p=3 is the "bad" prime for S3 (3 | |S3|=6). Bhargava 2005 + Bhargava-
    Varma 2011 give refined predictions for S3 cubic 3-torsion. Empirically
    check Prob(3|h) convergence rate for complex S3 cubic at p=3 — does it
    show a specific exponent (candidate 1/3 or 1/4 for Bhargava-Varma)?

Output: cartography/docs/report18l_anchor_firmup_results.json.

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
OUTPUT = Path('cartography/docs/report18l_anchor_firmup_results.json')


def cm_prob(p, u, terms=200):
    """Cohen-Martinet Prob(p|h) for unit rank u, prime p ∤ |G|."""
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


def fit_alpha(buckets, primes, cm_fn, unit_rank):
    """For each prime, fit log10|rel_dev| vs bucket. Return α_p dict."""
    alphas = {}
    for p in primes:
        theo = cm_fn(p, unit_rank)
        pts = []
        for b in buckets:
            div = b['divisible_by_p'].get(p, 0)
            n = b['n']
            if n == 0: continue
            emp = div / n
            rel = (emp - theo) / theo if theo > 0 else None
            if rel is None or abs(rel) == 0: continue
            pts.append((b['bucket'], log10(abs(rel))))
        if len(pts) < 3:
            alphas[p] = None
            continue
        xs = [pt[0] for pt in pts]; ys = [pt[1] for pt in pts]
        fit = linreg_with_se(xs, ys)
        alphas[p] = {
            'alpha_p': -fit['slope'] if fit['slope'] is not None else None,
            'alpha_p_se': fit['slope_se'],
            'r2': fit['r2'], 'n_buckets': fit['n'],
            'theoretical': theo,
        }
    return alphas


def pull_buckets(cur, degree, galois_label, sig_filter, primes, cutoff_bucket):
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
        if n < 500: continue
        if cutoff_bucket is not None and b > cutoff_bucket: continue
        div = {p: int(row[2 + i]) for i, p in enumerate(primes)}
        buckets.append({'bucket': b, 'n': n, 'divisible_by_p': div})
    return buckets


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=300000')
    cur = conn.cursor()

    # ============================================================
    # PART A: S4 complex quartic extended primes
    # ============================================================
    print('[R18l-A] S4 complex extended to p ∈ {5,7,11,13,17,19,23}...')
    s4_primes = [5, 7, 11, 13, 17, 19, 23]
    s4_buckets = pull_buckets(cur, 4, '4T5', 'r2::int >= 1', s4_primes, cutoff_bucket=6)
    s4_alphas = fit_alpha(s4_buckets, s4_primes, cm_prob, unit_rank=1)

    # Refit log(p) scaling
    logp_pts = [(log(p), s4_alphas[p]['alpha_p'], s4_alphas[p]['alpha_p_se'])
                for p in s4_primes
                if s4_alphas[p] is not None and s4_alphas[p]['alpha_p'] is not None]
    if len(logp_pts) >= 3:
        xs = np.array([pt[0] for pt in logp_pts])
        ys = np.array([pt[1] for pt in logp_pts])
        ws = 1 / np.array([pt[2] for pt in logp_pts]) ** 2
        W = ws.sum()
        mx = np.sum(ws * xs) / W
        my = np.sum(ws * ys) / W
        sxx = np.sum(ws * (xs - mx) ** 2)
        sxy = np.sum(ws * (xs - mx) * (ys - my))
        slope = sxy / sxx
        intercept = my - slope * mx
        yhat = slope * xs + intercept
        r2 = 1 - np.sum(ws * (ys - yhat) ** 2) / np.sum(ws * (ys - my) ** 2)
        chi2 = float(np.sum(ws * (ys - yhat) ** 2))
        slope_se = float(np.sqrt(1 / sxx)) if sxx > 0 else None
        s4_logp_fit = {
            'slope': float(slope), 'slope_se': slope_se,
            'intercept': float(intercept), 'r2': float(r2),
            'chi2': chi2, 'dof': len(xs) - 2,
            'formula': f'α_p = {float(intercept):.4f} + {float(slope):.4f} · log(p)',
        }
        # R18k predicted: slope -0.0175, intercept 0.0862
        delta_slope = slope - (-0.0175)
        delta_intercept = intercept - 0.0862
        s4_logp_fit['comparison_to_R18k'] = {
            'r18k_intercept': 0.0862, 'r18k_slope': -0.0175,
            'delta_intercept': float(delta_intercept),
            'delta_slope': float(delta_slope),
            'durable_anchor': abs(delta_slope) < 0.01 and abs(delta_intercept) < 0.02,
        }
    else:
        s4_logp_fit = None

    # ============================================================
    # PART B: S3 complex cubic at p=3 (Bhargava-Varma territory)
    # ============================================================
    print('[R18l-B] S3 complex cubic at p=3 (Bhargava-Varma check)...')
    # For S3 cubic, we need a theoretical prediction for Prob(3|h)
    # Cohen-Lenstra with |G|-correction for p | |G|:
    # For S3 (|G|=6) and p=3, naive unit-rank CM does NOT apply.
    # Heuristic: Bhargava-Varma suggest 3-torsion of S3 cubic class group
    # converges to a specific limit computed via 3-isogeny L-function.
    # For complex S3 cubic (u=1), the empirical asymptote observed in
    # R18 was Prob(3|h) ≈ 0.4049 at n=843K. Use this as "empirical asymptote"
    # and fit convergence rate to it.
    s3c_buckets = pull_buckets(cur, 3, '3T2', 'r2::int >= 1', [3], cutoff_bucket=6)

    # Compute global Prob(3|h) asymptote from the largest bucket
    asymptotes = [(b['n'], b['divisible_by_p'][3] / b['n']) for b in s3c_buckets]
    # Use weighted mean across buckets as estimator of asymptote
    # (simple approach: use the n-weighted mean at the LARGEST bucket)
    if asymptotes:
        largest_bucket = max(s3c_buckets, key=lambda x: x['n'])
        asymptote_est = largest_bucket['divisible_by_p'][3] / largest_bucket['n']
    else:
        asymptote_est = None

    # Fit α for S3 complex at p=3 using empirical asymptote as the target
    if asymptote_est is not None:
        pts = []
        for b in s3c_buckets:
            emp = b['divisible_by_p'][3] / b['n']
            rel = (emp - asymptote_est) / asymptote_est if asymptote_est > 0 else None
            if rel is None or abs(rel) == 0: continue
            pts.append((b['bucket'], log10(abs(rel)), b['n']))
        if len(pts) >= 3:
            xs = [pt[0] for pt in pts]; ys = [pt[1] for pt in pts]
            fit = linreg_with_se(xs, ys)
            s3c_p3 = {
                'asymptote_empirical': asymptote_est,
                'bucket_data': [
                    {'bucket': b['bucket'], 'n': b['n'],
                     'emp_prob_3_divides_h': b['divisible_by_p'][3] / b['n']}
                    for b in s3c_buckets
                ],
                'fit': fit,
                'alpha_vs_empirical_asymptote': -fit['slope'] if fit['slope'] is not None else None,
                'alpha_se': fit['slope_se'],
            }
            # Compare to various candidates
            a = s3c_p3['alpha_vs_empirical_asymptote']
            se = s3c_p3['alpha_se']
            if a is not None and se and se > 0:
                candidates = {
                    'DH_1_6': 1/6, 'BV_1_4': 1/4, 'BV_1_3': 1/3, 'BV_1_2': 1/2,
                }
                s3c_p3['candidate_comparisons'] = {
                    name: {
                        'predicted': val,
                        'z': (a - val) / se,
                        'match_2sigma': abs((a - val) / se) < 2.0,
                    }
                    for name, val in candidates.items()
                }
        else:
            s3c_p3 = {'note': 'insufficient buckets'}
    else:
        s3c_p3 = {'note': 'no asymptote available'}

    cur.close(); conn.close()

    report = {
        'task': 'report18l_anchor_firmup',
        'parent': 'report18j_quartic_bst',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        's4_complex_extended_primes': {
            'primes_tested': s4_primes,
            'alpha_p_fits': s4_alphas,
            'log_p_fit_extended': s4_logp_fit,
        },
        's3_complex_cubic_at_p_3': s3c_p3,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18l] wrote {OUTPUT}')
    print()

    # Console
    print('== S4 COMPLEX — α_p at p = 5, 7, 11, 13, 17, 19, 23 ==')
    for p in s4_primes:
        a = s4_alphas[p]
        if a and a['alpha_p'] is not None:
            print(f'  p={p:>3}: α = {a["alpha_p"]:+.5f} ± {a["alpha_p_se"]:.5f}  '
                  f'(R²={a["r2"]:.4f})')
        else:
            print(f'  p={p:>3}: (insufficient)')
    print()
    if s4_logp_fit:
        print(f'  EXTENDED log(p) fit: α = {s4_logp_fit["intercept"]:.5f} '
              f'+ ({s4_logp_fit["slope"]:.5f}) · log(p)')
        print(f'  R² = {s4_logp_fit["r2"]:.4f}, χ² = {s4_logp_fit["chi2"]:.2f} (dof {s4_logp_fit["dof"]})')
        cmp = s4_logp_fit['comparison_to_R18k']
        print(f'  vs R18k fit (slope=-0.0175, intercept=0.0862):')
        print(f'    Δintercept = {cmp["delta_intercept"]:+.5f}')
        print(f'    Δslope     = {cmp["delta_slope"]:+.5f}')
        print(f'  Durable anchor (|Δslope|<0.01 AND |Δintercept|<0.02): {cmp["durable_anchor"]}')
    print()

    print('== S3 COMPLEX CUBIC at p=3 ==')
    if 'fit' in s3c_p3:
        print(f'  asymptote estimate (from largest bucket): {s3c_p3["asymptote_empirical"]:.5f}')
        for b in s3c_p3['bucket_data']:
            print(f'  bucket {b["bucket"]}: n={b["n"]:>8,}  emp Prob(3|h)={b["emp_prob_3_divides_h"]:.5f}')
        print(f'  α vs empirical asymptote = {s3c_p3["alpha_vs_empirical_asymptote"]:+.5f} '
              f'± {s3c_p3["alpha_se"]:.5f}')
        print(f'  R² of log-linear fit = {s3c_p3["fit"]["r2"]:.4f}')
        print(f'  Candidate matches:')
        for name, d in s3c_p3['candidate_comparisons'].items():
            print(f'    {name} (predicted {d["predicted"]:.4f}): z={d["z"]:+.3f}, match@2σ: {d["match_2sigma"]}')
    else:
        print(f'  {s3c_p3.get("note", "no data")}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
