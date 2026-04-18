"""
Report 18j — BST convergence on D4 (4T3) and S4 (4T5) quartic; complex-S3
universality test.

Parent: R18h, R18i. This script extends the BST-convergence methodology
to D4 (4T3) and S4 (4T5) quartic fields, and also tests whether the
complex-S3 α_p values from R18h are cluster-constant across primes (the
"universality" question at the complex-S3 level, analogous to R18c's
original failed p≥5 cluster claim for quadratic).

Cohen-Martinet predictions for quartic fields at p ∤ |G|:

D4 (|G|=8): p ∈ {3, 5, 7, 11, 13}. CM product formula for D4 over Q uses
  unit rank u = r_1 + r_2 - 1; we stratify by signature:
    Signature (4,0) totally real: u = 3, Prob(p|h) = 1 - ∏_{k=4}^∞ (1-p^-k)
    Signature (2,1)              : u = 2, Prob(p|h) = 1 - ∏_{k=3}^∞ (1-p^-k)
    Signature (0,2) totally complex: u = 1, Prob(p|h) = 1 - ∏_{k=2}^∞ (1-p^-k)

S4 (|G|=24): p ∈ {5, 7, 11, 13}. Same unit-rank-based formula.

Cutoffs from R18i:
  4T3 (D4): SMOOTH (no sharp cutoff; extend analysis to higher |disc|)
  4T5 (S4): cutoff at |disc| ≤ 10^7 (bucket 6); restrict to that regime.

Universality test: for complex-S3 cubic α_p from R18h (already computed),
compute weighted mean + χ² to check if α_5, α_7, α_11, α_13 are consistent
with a single common α. Same for D4 / S4 results.

Output: cartography/docs/report18j_quartic_bst_results.json.

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
PRIMES = [5, 7, 11, 13]
OUTPUT = Path('cartography/docs/report18j_quartic_bst_results.json')


def cm_prob_unit_rank(p, u, terms=200):
    """Cohen-Martinet Prob(p | h) for extensions of Q with unit rank u.

    Formula: 1 - ∏_{k=u+1}^∞ (1 - p^-k). When p ∤ |G|.
    """
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


def weighted_universality(alpha_dict):
    """Given {prime_str: {'alpha_p', 'alpha_p_se'}}, test if α is cluster-constant.

    Returns {weighted_mean, chi2, dof, z_per_prime, max_abs_z, universal_2sigma}.
    """
    vals = []; ses = []; primes = []
    for p, d in alpha_dict.items():
        a = d.get('alpha_p'); s = d.get('alpha_p_se')
        if a is not None and s is not None and s > 0:
            vals.append(a); ses.append(s); primes.append(int(p))
    if len(vals) < 2:
        return None
    vals = np.array(vals); ses = np.array(ses)
    w = 1 / ses ** 2
    mean = float(np.sum(w * vals) / np.sum(w))
    mean_se = float(1 / np.sqrt(np.sum(w)))
    chi2 = float(np.sum(((vals - mean) / ses) ** 2))
    z_per = {int(p): float((v - mean) / s) for p, v, s in zip(primes, vals, ses)}
    max_z = max(abs(z) for z in z_per.values())
    return {
        'weighted_mean': mean, 'mean_se': mean_se,
        'chi2': chi2, 'dof': len(vals) - 1,
        'z_per_prime_vs_mean': z_per, 'max_abs_z': max_z,
        'cluster_constant_at_2sigma': max_z < 2.0,
        'cluster_constant_at_3sigma': max_z < 3.0,
    }


def fit_stratum(cur, degree, galois_label, sig_filter, unit_rank, cutoff_bucket):
    """Run BST-convergence fit for a (degree, galois, signature) stratum.

    cutoff_bucket: buckets > this are excluded (set to None if no cutoff).
    """
    # Using psycopg2 params (%s) below, so escape literal % as %% in the
    # modulo operator for the FILTER clauses.
    filter_cols = ',\n          '.join(
        f"count(*) FILTER (WHERE (class_number::bigint) %% {p} = 0) AS d{p}"
        for p in PRIMES
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
    rows = cur.fetchall()

    buckets = []
    for row in rows:
        b = int(row[0]); n = int(row[1])
        if n < 500:
            continue
        if cutoff_bucket is not None and b > cutoff_bucket:
            continue
        per_prime = {}
        for i, p in enumerate(PRIMES):
            k = int(row[2 + i])
            emp = k / n
            theo = cm_prob_unit_rank(p, unit_rank)
            rel = (emp - theo) / theo if theo > 0 else None
            per_prime[str(p)] = {
                'empirical': emp, 'theoretical': theo,
                'relative_deviation': rel, 'n_divisible': k,
            }
        buckets.append({'log10_disc_bucket': b, 'n': n, 'per_prime': per_prime})

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
                'r2': fit['r2'], 'n_buckets': fit['n'],
            }
        else:
            alphas[str(p)] = {'alpha_p': None, 'note': 'insufficient buckets'}

    return {
        'buckets_used': buckets,
        'alpha_p_fits': alphas,
        'unit_rank': unit_rank,
        'cutoff_bucket': cutoff_bucket,
    }


def main():
    conn = psycopg2.connect(**PG, connect_timeout=10,
                            options='-c statement_timeout=300000')
    cur = conn.cursor()

    # D4 (4T3): no sharp cutoff, use buckets up to 15 (reasonable upper bound)
    # S4 (4T5): cutoff at bucket 6 per R18i
    strata = [
        {'label': 'D4_complex',    'degree': 4, 'gal': '4T3', 'sig': 'r2::int >= 1', 'u': 1, 'cut': 15},
        {'label': 'D4_real',       'degree': 4, 'gal': '4T3', 'sig': 'r2::int = 0',  'u': 3, 'cut': 15},
        {'label': 'S4_complex',    'degree': 4, 'gal': '4T5', 'sig': 'r2::int >= 1', 'u': 1, 'cut': 6},
        {'label': 'S4_real',       'degree': 4, 'gal': '4T5', 'sig': 'r2::int = 0',  'u': 3, 'cut': 6},
    ]

    stratum_results = {}
    for s in strata:
        print(f"[R18j] fitting {s['label']} (degree {s['degree']}, {s['gal']}, u={s['u']}, cutoff<={s['cut']})...")
        stratum_results[s['label']] = fit_stratum(
            cur, s['degree'], s['gal'], s['sig'], s['u'], s['cut']
        )

    cur.close(); conn.close()

    # Universality tests per stratum
    universality = {}
    for name, sr in stratum_results.items():
        u = weighted_universality(sr['alpha_p_fits'])
        universality[name] = u

    # Complex-S3 universality (from R18h; pull pre-computed α_p)
    complex_s3_alphas_from_r18h = {
        '5':  {'alpha_p': 0.21321, 'alpha_p_se': 0.00429},
        '7':  {'alpha_p': 0.19637, 'alpha_p_se': 0.03747},
        '11': {'alpha_p': 0.27917, 'alpha_p_se': 0.01889},
        '13': {'alpha_p': 0.22314, 'alpha_p_se': 0.02397},
    }
    complex_s3_universality = weighted_universality(complex_s3_alphas_from_r18h)

    # DH 1/6 comparison for each stratum / prime
    dh = 1 / 6
    dh_comparisons = []
    for name, sr in stratum_results.items():
        for p in PRIMES:
            fp = sr['alpha_p_fits'].get(str(p), {})
            a = fp.get('alpha_p'); se = fp.get('alpha_p_se')
            if a is None or se is None or se <= 0:
                continue
            z = (a - dh) / se
            dh_comparisons.append({
                'stratum': name, 'prime': p,
                'alpha_p': a, 'se': se,
                'dh_1_6': dh, 'z_vs_dh': z,
                'match_2sigma': abs(z) < 2.0,
            })

    report = {
        'task': 'report18j_quartic_bst',
        'parent': 'report18h_s3_cubic_bst',
        'drafted_by': 'Harmonia_M2_sessionD',
        'date': '2026-04-18',
        'strata': stratum_results,
        'per_stratum_universality': universality,
        'complex_s3_universality_from_r18h': {
            'per_prime_inputs': complex_s3_alphas_from_r18h,
            'result': complex_s3_universality,
        },
        'dh_1_6_comparisons': dh_comparisons,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'[R18j] wrote {OUTPUT}')
    print()

    # Console output
    print('== COMPLEX-S3 α_p UNIVERSALITY TEST (from R18h data) ==')
    u = complex_s3_universality
    if u:
        print(f'  primes: {list(u["z_per_prime_vs_mean"].keys())}')
        print(f'  weighted mean α = {u["weighted_mean"]:.5f} ± {u["mean_se"]:.5f}')
        print(f'  χ² = {u["chi2"]:.3f} (dof {u["dof"]})  max|z| = {u["max_abs_z"]:.3f}')
        print(f'  cluster_constant @ 2σ: {u["cluster_constant_at_2sigma"]}  @ 3σ: {u["cluster_constant_at_3sigma"]}')
    print()

    print('== QUARTIC BST-CONVERGENCE FITS ==')
    for name in ('D4_complex', 'D4_real', 'S4_complex', 'S4_real'):
        print(f'{name}:')
        ap = stratum_results[name]['alpha_p_fits']
        for p in PRIMES:
            f_ = ap[str(p)]
            a = f_.get('alpha_p'); se = f_.get('alpha_p_se')
            n_b = f_.get('n_buckets'); r2 = f_.get('r2')
            if a is None:
                print(f'  p={p}: (insufficient data)')
            else:
                print(f'  p={p}: α = {a:+.5f} ± {se:.5f}  (R²={r2:.4f}, n_buckets={n_b})')
        # Universality per stratum
        u_ = universality[name]
        if u_:
            print(f'  universality: weighted_mean={u_["weighted_mean"]:.5f}±{u_["mean_se"]:.5f}, '
                  f'max|z|={u_["max_abs_z"]:.2f}, '
                  f'cluster-const @2σ: {u_["cluster_constant_at_2sigma"]}')
        print()

    print('== DH 1/6 SCORECARD ACROSS QUARTIC STRATA ==')
    n_match = sum(1 for c in dh_comparisons if c['match_2sigma'])
    n_total = len(dh_comparisons)
    print(f'  {n_match}/{n_total} matches at 2σ')
    for c in dh_comparisons:
        match = '✓' if c['match_2sigma'] else '✗'
        print(f"  {c['stratum']:>12} p={c['prime']:>3}  α={c['alpha_p']:+.5f}  "
              f"z_vs_DH={c['z_vs_dh']:+.3f}  {match}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
