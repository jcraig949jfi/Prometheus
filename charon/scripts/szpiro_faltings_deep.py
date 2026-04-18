#!/usr/bin/env python3
"""
Charon: Deep investigation of H40 Szpiro-Faltings coupling.
Tests whether ρ=0.969 is trivially explained by shared Δ_min,
or whether a genuine residual operator exists.
"""

import json
import numpy as np
import psycopg2
from scipy import stats
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
OUT = r"F:\Prometheus\charon\data\szpiro_faltings_deep.json"

def fetch_data():
    """Pull all curves with non-null szpiro and faltings data."""
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT szpiro_ratio::float, faltings_height::float, stable_faltings_height::float,
               conductor::float, rank::int, num_bad_primes::int,
               semistable, torsion::int, sha::int, regulator::float,
               cm::int, "signD"::int, abc_quality::float, class_size::int,
               lmfdb_label
        FROM ec_curvedata
        WHERE szpiro_ratio IS NOT NULL
          AND faltings_height IS NOT NULL
          AND conductor IS NOT NULL
          AND szpiro_ratio != 'NaN'
          AND faltings_height != 'NaN'
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"Fetched {len(rows)} curves")

    cols = ['szpiro_ratio', 'faltings_height', 'stable_faltings_height',
            'conductor', 'rank', 'num_bad_primes', 'semistable', 'torsion',
            'sha', 'regulator', 'cm', 'signD', 'abc_quality', 'class_size', 'label']

    data = {c: [] for c in cols}
    for row in rows:
        for i, c in enumerate(cols):
            val = row[i]
            if c == 'semistable':
                val = 1 if val in (True, 'True', 't', 'true') else 0
            data[c].append(val)

    # Convert to numpy where possible
    for c in cols:
        if c != 'label':
            data[c] = np.array(data[c], dtype=float)

    return data


def phase1_residual(data):
    """Phase 1: Characterize the residual after linear fit."""
    print("\n=== PHASE 1: Residual Characterization ===")
    results = {}

    szpiro = data['szpiro_ratio']
    faltings = data['faltings_height']
    log_cond = np.log(data['conductor'])
    nbp = data['num_bad_primes']

    # Raw correlation
    r_raw, p_raw = stats.pearsonr(szpiro, faltings)
    print(f"Raw correlation szpiro vs faltings: r={r_raw:.6f}, p={p_raw:.2e}")
    results['raw_correlation'] = {'r': float(r_raw), 'p': float(p_raw)}

    # Partial correlation controlling for log_cond and num_bad_primes
    # Regress both on controls, correlate residuals
    X = np.column_stack([np.ones(len(szpiro)), log_cond, nbp])
    beta_s = np.linalg.lstsq(X, szpiro, rcond=None)[0]
    beta_f = np.linalg.lstsq(X, faltings, rcond=None)[0]
    resid_s = szpiro - X @ beta_s
    resid_f = faltings - X @ beta_f
    r_partial, p_partial = stats.pearsonr(resid_s, resid_f)
    print(f"Partial corr (ctrl log_cond, nbp): r={r_partial:.6f}, p={p_partial:.2e}")
    results['partial_correlation'] = {'r': float(r_partial), 'p': float(p_partial)}

    # Linear fit: faltings = a*szpiro + b*log_cond + c*nbp + d
    X_full = np.column_stack([np.ones(len(szpiro)), szpiro, log_cond, nbp])
    beta_full = np.linalg.lstsq(X_full, faltings, rcond=None)[0]
    pred = X_full @ beta_full
    residual = faltings - pred

    ss_res = np.sum(residual**2)
    ss_tot = np.sum((faltings - np.mean(faltings))**2)
    r2 = 1 - ss_res / ss_tot
    print(f"R² (szpiro + log_cond + nbp -> faltings): {r2:.6f}")
    print(f"Coefficients: intercept={beta_full[0]:.6f}, szpiro={beta_full[1]:.6f}, "
          f"log_cond={beta_full[2]:.6f}, nbp={beta_full[3]:.6f}")

    results['linear_fit'] = {
        'r_squared': float(r2),
        'coefficients': {
            'intercept': float(beta_full[0]),
            'szpiro': float(beta_full[1]),
            'log_cond': float(beta_full[2]),
            'num_bad_primes': float(beta_full[3])
        },
        'residual_std': float(np.std(residual)),
        'residual_mean': float(np.mean(residual))
    }

    # Test predictors of residual
    predictors = {
        'rank': data['rank'],
        'torsion': data['torsion'],
        'cm': data['cm'],
        'sha': data['sha'],
        'class_size': data['class_size'],
        'semistable': data['semistable'],
        'signD': data['signD'],
        'regulator': data['regulator'],
        'abc_quality': data['abc_quality']
    }

    pred_results = {}
    print("\nResidual predictors:")
    for name, vals in predictors.items():
        mask = np.isfinite(vals) & np.isfinite(residual)
        if mask.sum() < 100:
            continue
        r, p = stats.pearsonr(vals[mask], residual[mask])
        # Effect size: how much variance does this explain?
        X_pred = np.column_stack([np.ones(mask.sum()), vals[mask]])
        b = np.linalg.lstsq(X_pred, residual[mask], rcond=None)[0]
        pred_r = X_pred @ b
        r2_pred = 1 - np.sum((residual[mask] - pred_r)**2) / np.sum((residual[mask] - np.mean(residual[mask]))**2)
        print(f"  {name:15s}: r={r:+.6f}, R²={r2_pred:.6f}, p={p:.2e}")
        pred_results[name] = {'r': float(r), 'r_squared': float(r2_pred), 'p': float(p)}

    results['residual_predictors'] = pred_results

    # Normality test (on subsample for speed)
    idx = np.random.RandomState(42).choice(len(residual), min(10000, len(residual)), replace=False)
    stat_sw, p_sw = stats.shapiro(residual[idx])
    skew = float(stats.skew(residual))
    kurt = float(stats.kurtosis(residual))
    print(f"\nResidual distribution: skew={skew:.4f}, kurtosis={kurt:.4f}, Shapiro p={p_sw:.2e}")
    results['residual_distribution'] = {
        'skew': skew, 'kurtosis': kurt,
        'shapiro_p': float(p_sw),
        'is_normal': p_sw > 0.05
    }

    return results, residual, beta_full


def phase2_functional(data):
    """Phase 2: Is the relationship exactly linear or curved?"""
    print("\n=== PHASE 2: Functional Relationship ===")
    results = {}

    szpiro = data['szpiro_ratio']
    faltings = data['faltings_height']
    log_cond = np.log(data['conductor'])

    # Polynomial fits: faltings vs szpiro after partialling out log_cond
    # First partial out log_cond from both
    X_c = np.column_stack([np.ones(len(szpiro)), log_cond])
    b_s = np.linalg.lstsq(X_c, szpiro, rcond=None)[0]
    b_f = np.linalg.lstsq(X_c, faltings, rcond=None)[0]
    s_resid = szpiro - X_c @ b_s
    f_resid = faltings - X_c @ b_f

    ss_tot = np.sum((f_resid - np.mean(f_resid))**2)

    for deg in [1, 2, 3]:
        X_poly = np.column_stack([s_resid**d for d in range(deg+1)])
        b = np.linalg.lstsq(X_poly, f_resid, rcond=None)[0]
        pred = X_poly @ b
        r2 = 1 - np.sum((f_resid - pred)**2) / ss_tot
        print(f"Degree {deg}: R²={r2:.8f}")
        results[f'degree_{deg}'] = {'r_squared': float(r2), 'coefficients': [float(x) for x in b]}

    # Does curvature matter?
    r2_1 = results['degree_1']['r_squared']
    r2_2 = results['degree_2']['r_squared']
    r2_3 = results['degree_3']['r_squared']
    n = len(szpiro)

    # F-test: deg 2 vs deg 1
    f_stat_21 = ((r2_2 - r2_1) / 1) / ((1 - r2_2) / (n - 3))
    p_21 = 1 - stats.f.cdf(f_stat_21, 1, n - 3)
    print(f"F-test deg2 vs deg1: F={f_stat_21:.2f}, p={p_21:.2e}")
    results['curvature_test'] = {
        'f_stat_2v1': float(f_stat_21), 'p_2v1': float(p_21),
        'curvature_significant': p_21 < 0.001,
        'r2_improvement_2v1': float(r2_2 - r2_1),
        'r2_improvement_3v2': float(r2_3 - r2_2)
    }

    # Does adding rank/torsion/cm improve R²?
    X_base = np.column_stack([np.ones(n), szpiro, log_cond])
    b_base = np.linalg.lstsq(X_base, faltings, rcond=None)[0]
    r2_base = 1 - np.sum((faltings - X_base @ b_base)**2) / np.sum((faltings - np.mean(faltings))**2)

    augment_results = {}
    for name, vals in [('rank', data['rank']), ('torsion', data['torsion']),
                        ('cm', data['cm']), ('sha', data['sha'])]:
        mask = np.isfinite(vals)
        X_aug = np.column_stack([X_base[mask], vals[mask]])
        b_aug = np.linalg.lstsq(X_aug, faltings[mask], rcond=None)[0]
        r2_aug = 1 - np.sum((faltings[mask] - X_aug @ b_aug)**2) / np.sum((faltings[mask] - np.mean(faltings[mask]))**2)
        delta = r2_aug - r2_base
        print(f"Adding {name:10s}: R2={r2_aug:.8f}, dR2={delta:+.8f}")
        augment_results[name] = {'r_squared': float(r2_aug), 'delta_r2': float(delta)}

    results['augmented_models'] = augment_results
    results['base_r2'] = float(r2_base)

    return results


def phase3_outliers(data, residual):
    """Phase 3: What breaks the coupling?"""
    print("\n=== PHASE 3: Outlier Characterization ===")
    results = {}

    # Top 1000 by |residual|
    abs_resid = np.abs(residual)
    top_idx = np.argsort(abs_resid)[-1000:]

    # Characterize outliers vs rest
    rest_idx = np.argsort(abs_resid)[:-1000]

    comparisons = {}
    for name in ['rank', 'torsion', 'cm', 'conductor', 'num_bad_primes', 'class_size', 'sha', 'semistable']:
        vals = data[name]
        out_mean = float(np.nanmean(vals[top_idx]))
        rest_mean = float(np.nanmean(vals[rest_idx]))
        out_std = float(np.nanstd(vals[top_idx]))

        # Mann-Whitney U test
        try:
            u_stat, u_p = stats.mannwhitneyu(vals[top_idx], vals[rest_idx], alternative='two-sided')
            u_p = float(u_p)
        except:
            u_p = 1.0

        print(f"  {name:15s}: outliers={out_mean:.4f}±{out_std:.4f}, rest={rest_mean:.4f}, MW p={u_p:.2e}")
        comparisons[name] = {
            'outlier_mean': out_mean, 'rest_mean': rest_mean,
            'outlier_std': out_std, 'mw_p': u_p,
            'significantly_different': u_p < 0.001
        }

    results['outlier_vs_rest'] = comparisons

    # CM curves specifically
    cm_mask = data['cm'] != 0
    non_cm_mask = data['cm'] == 0
    cm_resid_std = float(np.std(residual[cm_mask])) if cm_mask.sum() > 0 else 0
    non_cm_resid_std = float(np.std(residual[non_cm_mask]))
    cm_resid_mean = float(np.mean(np.abs(residual[cm_mask]))) if cm_mask.sum() > 0 else 0
    non_cm_resid_mean = float(np.mean(np.abs(residual[non_cm_mask])))

    print(f"\nCM curves: n={cm_mask.sum()}, |resid| mean={cm_resid_mean:.6f}, std={cm_resid_std:.6f}")
    print(f"Non-CM:    n={non_cm_mask.sum()}, |resid| mean={non_cm_resid_mean:.6f}, std={non_cm_resid_std:.6f}")

    results['cm_analysis'] = {
        'n_cm': int(cm_mask.sum()),
        'n_non_cm': int(non_cm_mask.sum()),
        'cm_resid_abs_mean': cm_resid_mean,
        'non_cm_resid_abs_mean': non_cm_resid_mean,
        'cm_resid_std': cm_resid_std,
        'non_cm_resid_std': non_cm_resid_std,
        'cm_worse': cm_resid_mean > non_cm_resid_mean
    }

    # Fraction of outliers that are CM
    cm_in_outliers = float(np.mean(data['cm'][top_idx] != 0))
    cm_overall = float(np.mean(data['cm'] != 0))
    print(f"CM fraction in outliers: {cm_in_outliers:.4f} vs overall: {cm_overall:.4f}")
    results['cm_enrichment_in_outliers'] = {
        'cm_frac_outliers': cm_in_outliers,
        'cm_frac_overall': cm_overall,
        'enrichment_ratio': cm_in_outliers / cm_overall if cm_overall > 0 else 0
    }

    # Rank distribution in outliers
    for r in range(5):
        frac_out = float(np.mean(data['rank'][top_idx] == r))
        frac_rest = float(np.mean(data['rank'][rest_idx] == r))
        print(f"  Rank {r}: outliers={frac_out:.4f}, rest={frac_rest:.4f}")

    results['rank_distribution'] = {
        f'rank_{r}': {
            'outlier_frac': float(np.mean(data['rank'][top_idx] == r)),
            'rest_frac': float(np.mean(data['rank'][rest_idx] == r))
        }
        for r in range(5)
    }

    # Sign of residual in outliers
    pos_frac = float(np.mean(residual[top_idx] > 0))
    print(f"Fraction of outlier residuals > 0: {pos_frac:.4f}")
    results['outlier_sign_bias'] = pos_frac

    return results


def phase4_conductor_strata(data, residual):
    """Phase 4: Conductor-stratified stability."""
    print("\n=== PHASE 4: Conductor-Stratified Stability ===")
    results = {}

    log_cond = np.log(data['conductor'])
    szpiro = data['szpiro_ratio']
    faltings = data['faltings_height']
    cond = data['conductor']

    strata = [
        ('1-100', 1, 100),
        ('100-1K', 100, 1000),
        ('1K-10K', 1000, 10000),
        ('10K-100K', 10000, 100000),
        ('100K-1M', 100000, 1000000),
        ('1M+', 1000000, 1e15)
    ]

    stratum_results = {}
    for name, lo, hi in strata:
        mask = (cond >= lo) & (cond < hi)
        n = mask.sum()
        if n < 50:
            continue

        # Fit within stratum
        X = np.column_stack([np.ones(n), szpiro[mask]])
        b = np.linalg.lstsq(X, faltings[mask], rcond=None)[0]
        pred = X @ b
        resid = faltings[mask] - pred
        ss_res = np.sum(resid**2)
        ss_tot = np.sum((faltings[mask] - np.mean(faltings[mask]))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        r_corr, p_corr = stats.pearsonr(szpiro[mask], faltings[mask])

        print(f"  {name:12s}: n={n:>8d}, slope={b[1]:.6f}, intercept={b[0]:.6f}, "
              f"R²={r2:.6f}, resid_std={np.std(resid):.6f}")

        stratum_results[name] = {
            'n': int(n),
            'slope': float(b[1]),
            'intercept': float(b[0]),
            'r_squared': float(r2),
            'correlation': float(r_corr),
            'residual_std': float(np.std(resid)),
            'residual_mean': float(np.mean(resid))
        }

    results['strata'] = stratum_results

    # Is slope changing significantly?
    slopes = [v['slope'] for v in stratum_results.values()]
    if len(slopes) >= 3:
        slope_range = max(slopes) - min(slopes)
        slope_cv = np.std(slopes) / np.mean(slopes) if np.mean(slopes) != 0 else 0
        print(f"\nSlope range: {slope_range:.6f}, CV: {slope_cv:.6f}")
        results['slope_stability'] = {
            'slope_range': float(slope_range),
            'slope_cv': float(slope_cv),
            'scale_dependent': slope_cv > 0.05
        }

    # Does residual variance change with conductor?
    resid_stds = [v['residual_std'] for v in stratum_results.values()]
    ns = [v['n'] for v in stratum_results.values()]
    if len(resid_stds) >= 3:
        log_mids = [np.log((lo+hi)/2) for (_, lo, hi) in strata[:len(resid_stds)]]
        r_var, p_var = stats.pearsonr(log_mids, resid_stds)
        print(f"Residual std vs log(conductor): r={r_var:.4f}, p={p_var:.2e}")
        results['heteroscedasticity'] = {
            'r_residstd_vs_logcond': float(r_var),
            'p': float(p_var),
            'variance_changes': abs(r_var) > 0.5
        }

    return results


def phase5_operator(data):
    """Phase 5: Test the theoretical discriminant-based formula."""
    print("\n=== PHASE 5: The Operator Question ===")
    results = {}

    szpiro = data['szpiro_ratio']
    faltings = data['faltings_height']
    log_cond = np.log(data['conductor'])

    # Theory: h(E) = (1/12) * log|Δ_min| - (1/2)*log(2π) + period_terms
    # And: szpiro = log|Δ_min| / log(N)
    # So: log|Δ_min| = szpiro * log(N)
    # Therefore: h_predicted = (szpiro * log(N)) / 12 - log(2π)/2

    log_delta_min = szpiro * log_cond  # reconstructed log|Δ_min|
    h_predicted_theory = log_delta_min / 12.0 - np.log(2 * np.pi) / 2.0

    # Test this exact formula
    theory_resid = faltings - h_predicted_theory
    r_theory, p_theory = stats.pearsonr(h_predicted_theory, faltings)
    ss_res = np.sum(theory_resid**2)
    ss_tot = np.sum((faltings - np.mean(faltings))**2)
    r2_theory = 1 - ss_res / ss_tot

    print(f"Theoretical formula: h = szpiro*log(N)/12 - log(2π)/2")
    print(f"  R² = {r2_theory:.8f}")
    print(f"  r  = {r_theory:.8f}")
    print(f"  Residual mean = {np.mean(theory_resid):.6f}")
    print(f"  Residual std  = {np.std(theory_resid):.6f}")

    results['exact_formula'] = {
        'formula': 'h = szpiro * log(N) / 12 - log(2pi) / 2',
        'r_squared': float(r2_theory),
        'correlation': float(r_theory),
        'residual_mean': float(np.mean(theory_resid)),
        'residual_std': float(np.std(theory_resid))
    }

    # Now allow a free intercept and slope: h = a * (szpiro * log(N)) + b
    X_theory = np.column_stack([np.ones(len(szpiro)), log_delta_min])
    b_fit = np.linalg.lstsq(X_theory, faltings, rcond=None)[0]
    pred_fit = X_theory @ b_fit
    resid_fit = faltings - pred_fit
    r2_fit = 1 - np.sum(resid_fit**2) / ss_tot

    print(f"\nFitted: h = {b_fit[1]:.8f} * log|Δ_min| + {b_fit[0]:.8f}")
    print(f"  Theory predicts slope = 1/12 = {1/12:.8f}")
    print(f"  Actual slope = {b_fit[1]:.8f}")
    print(f"  Slope ratio = {b_fit[1] * 12:.8f}")
    print(f"  R² = {r2_fit:.8f}")
    print(f"  Residual std = {np.std(resid_fit):.6f}")

    results['fitted_formula'] = {
        'slope': float(b_fit[1]),
        'intercept': float(b_fit[0]),
        'theoretical_slope': 1/12,
        'slope_ratio_to_theory': float(b_fit[1] * 12),
        'r_squared': float(r2_fit),
        'residual_std': float(np.std(resid_fit))
    }

    # Is log|Δ_min| = szpiro * log(N) sufficient to explain the coupling?
    # Compare: (A) faltings ~ szpiro + log_cond  vs (B) faltings ~ log_delta_min
    X_A = np.column_stack([np.ones(len(szpiro)), szpiro, log_cond])
    b_A = np.linalg.lstsq(X_A, faltings, rcond=None)[0]
    r2_A = 1 - np.sum((faltings - X_A @ b_A)**2) / ss_tot

    X_B = np.column_stack([np.ones(len(szpiro)), log_delta_min])
    b_B = np.linalg.lstsq(X_B, faltings, rcond=None)[0]
    r2_B = 1 - np.sum((faltings - X_B @ b_B)**2) / ss_tot

    print(f"\nModel A (szpiro + log_cond separately): R² = {r2_A:.8f}")
    print(f"Model B (log|Δ_min| = szpiro*log_cond):  R² = {r2_B:.8f}")
    print(f"ΔR² = {r2_A - r2_B:+.8f}")

    trivially_explained = r2_B > 0.99 and abs(r2_A - r2_B) < 0.001
    print(f"\nIs coupling trivially explained by shared Δ_min? {'YES — KILL' if trivially_explained else 'NO — genuine residual'}")

    results['discriminant_test'] = {
        'r2_separate': float(r2_A),
        'r2_product': float(r2_B),
        'delta_r2': float(r2_A - r2_B),
        'trivially_explained': trivially_explained
    }

    # If not trivially explained, what does the residual from the theory formula look like?
    # Residual = faltings - (slope * log|Δ_min| + intercept)
    # What predicts this residual?
    print("\nResidual from log|Δ_min| fit — predictors:")
    pred_results = {}
    for name in ['rank', 'torsion', 'cm', 'sha', 'class_size', 'semistable',
                  'signD', 'regulator', 'num_bad_primes', 'abc_quality']:
        vals = data[name]
        mask = np.isfinite(vals) & np.isfinite(resid_fit)
        if mask.sum() < 100:
            continue
        r, p = stats.pearsonr(vals[mask], resid_fit[mask])
        if abs(r) > 0.01 or p < 0.001:
            print(f"  {name:15s}: r={r:+.6f}, p={p:.2e}")
        pred_results[name] = {'r': float(r), 'p': float(p)}

    results['theory_residual_predictors'] = pred_results

    # The real test: does szpiro carry info BEYOND log|Δ_min|?
    # h = a * log|Δ_min| + b * szpiro + c  (if b≠0, szpiro adds info beyond Δ_min)
    X_both = np.column_stack([np.ones(len(szpiro)), log_delta_min, szpiro])
    b_both = np.linalg.lstsq(X_both, faltings, rcond=None)[0]
    r2_both = 1 - np.sum((faltings - X_both @ b_both)**2) / ss_tot

    # F-test for szpiro coefficient
    n = len(szpiro)
    f_szpiro = ((r2_both - r2_B) / 1) / ((1 - r2_both) / (n - 3))
    p_szpiro = 1 - stats.f.cdf(f_szpiro, 1, n - 3)

    print(f"\nDoes szpiro add info beyond log|Δ_min|?")
    print(f"  R² with both: {r2_both:.8f}, ΔR²={r2_both - r2_B:+.8f}")
    print(f"  F={f_szpiro:.2f}, p={p_szpiro:.2e}")
    print(f"  Szpiro coefficient: {b_both[2]:.8f}")

    results['szpiro_beyond_discriminant'] = {
        'r2_with_both': float(r2_both),
        'delta_r2': float(r2_both - r2_B),
        'szpiro_coeff': float(b_both[2]),
        'f_stat': float(f_szpiro),
        'p': float(p_szpiro),
        'szpiro_adds_info': p_szpiro < 0.001
    }

    # Stable Faltings height test
    stable_falt = data['stable_faltings_height']
    mask_stable = np.isfinite(stable_falt)
    if mask_stable.sum() > 1000:
        diff_stable = faltings[mask_stable] - stable_falt[mask_stable]
        print(f"\nFaltings vs Stable Faltings: mean diff={np.mean(diff_stable):.8f}, "
              f"std={np.std(diff_stable):.8f}, max|diff|={np.max(np.abs(diff_stable)):.8f}")
        r_stable, _ = stats.pearsonr(faltings[mask_stable], stable_falt[mask_stable])
        print(f"  Correlation: {r_stable:.8f}")
        results['stable_vs_unstable'] = {
            'mean_diff': float(np.mean(diff_stable)),
            'std_diff': float(np.std(diff_stable)),
            'max_abs_diff': float(np.max(np.abs(diff_stable))),
            'correlation': float(r_stable),
            'identical': np.std(diff_stable) < 1e-6
        }

    return results


def main():
    np.random.seed(42)
    data = fetch_data()

    # Phase 1
    p1_results, residual, beta = phase1_residual(data)

    # Phase 2
    p2_results = phase2_functional(data)

    # Phase 3
    p3_results = phase3_outliers(data, residual)

    # Phase 4
    p4_results = phase4_conductor_strata(data, residual)

    # Phase 5
    p5_results = phase5_operator(data)

    # Verdict
    print("\n" + "="*60)
    print("VERDICT")
    print("="*60)

    trivial = p5_results.get('discriminant_test', {}).get('trivially_explained', False)
    r2_product = p5_results.get('discriminant_test', {}).get('r2_product', 0)
    slope = p5_results.get('fitted_formula', {}).get('slope', 0)
    slope_ratio = p5_results.get('fitted_formula', {}).get('slope_ratio_to_theory', 0)
    szpiro_adds = p5_results.get('szpiro_beyond_discriminant', {}).get('szpiro_adds_info', False)

    if trivial:
        verdict = "KILL: Szpiro-Faltings coupling is trivially explained by shared log|Δ_min|"
        verdict_detail = (f"Both Szpiro ratio and Faltings height are functions of log|Δ_min|. "
                         f"The product szpiro * log(N) = log|Δ_min| explains R²={r2_product:.6f} of Faltings height. "
                         f"Fitted slope {slope:.6f} vs theoretical 1/12={1/12:.6f} (ratio={slope_ratio:.4f}). "
                         f"No independent operator maps one to the other — they share an ingredient.")
    else:
        verdict = "ALIVE: Genuine residual exists beyond shared discriminant"
        verdict_detail = (f"log|Δ_min| alone gives R²={r2_product:.6f}. "
                         f"Szpiro adds info beyond Δ_min: {szpiro_adds}. "
                         f"Slope deviation from 1/12: ratio={slope_ratio:.4f}.")

    print(verdict)
    print(verdict_detail)

    all_results = {
        'hypothesis': 'H40: Szpiro-Faltings coupling',
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'phase1_residual': p1_results,
        'phase2_functional': p2_results,
        'phase3_outliers': p3_results,
        'phase4_conductor_strata': p4_results,
        'phase5_operator': p5_results,
        'n_curves': len(data['szpiro_ratio'])
    }

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.bool_, np.integer)):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, bool):
                return int(obj)
            return super().default(obj)

    with open(OUT, 'w') as f:
        json.dump(all_results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {OUT}")


if __name__ == '__main__':
    main()
