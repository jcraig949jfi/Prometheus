"""
Lattice Theta Series Mod-p Phase Coherence vs Arithmetic Invariants

Extends the phase coherence-rank bridge (rho=0.197 for elliptic curves) to
lattice theta series. Tests whether mod-p fingerprint entropy of theta
coefficients predicts geometric properties: kissing number, packing density,
determinant, class number.

Data: LMFDB lat_lattices (39,293 lattices)
"""

import json
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

DATA_PATH = "F:/Prometheus/cartography/lmfdb_dump/lat_lattices.json"
OUTPUT_PATH = "F:/Prometheus/cartography/v2/theta_modp_entropy_results.json"

PRIMES = [3, 5, 7, 11]


def compute_modp_entropy(theta_series, p):
    """Shannon entropy of the mod-p residue distribution of theta coefficients."""
    residues = [int(a) % p for a in theta_series]
    counts = Counter(residues)
    total = len(residues)
    probs = np.array([counts.get(r, 0) / total for r in range(p)])
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


def compute_fingerprint_vector(theta_series, primes=PRIMES):
    """Compute entropy for each prime, return vector + mean."""
    entropies = {}
    for p in primes:
        entropies[f"H_mod{p}"] = compute_modp_entropy(theta_series, p)
    entropies["H_mean"] = np.mean(list(entropies.values()))
    return entropies


def spearman_with_pval(x, y):
    """Spearman correlation with p-value, handling edge cases."""
    x, y = np.array(x), np.array(y)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 5 or np.std(x) == 0 or np.std(y) == 0:
        return {"rho": None, "p_value": None, "n": int(len(x))}
    rho, pval = stats.spearmanr(x, y)
    return {"rho": round(float(rho), 6), "p_value": float(pval), "n": int(len(x))}


def main():
    print("Loading lattice data...")
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)

    records = data['records']
    print(f"Loaded {len(records)} lattices")

    # --- Step 1: Compute mod-p entropies for all lattices ---
    print("Computing mod-p fingerprint entropies...")
    enriched = []
    for r in records:
        theta = r.get('theta_series')
        if theta is None or len(theta) < 10:
            continue

        entry = {
            'label': r.get('label', ''),
            'dim': r['dim'],
            'det': r['det'],
            'class_number': r.get('class_number'),
            'kissing': r['kissing'],
            'density': float(r['density']) if r.get('density') else None,
            'minimum': r.get('minimum'),
            'level': r.get('level'),
        }
        fp = compute_fingerprint_vector(theta)
        entry.update(fp)
        enriched.append(entry)

    print(f"Enriched {len(enriched)} lattices with entropy fingerprints")

    # --- Step 2: Overall correlations ---
    print("\n=== OVERALL CORRELATIONS ===")
    targets = ['kissing', 'det', 'class_number', 'dim']
    entropy_keys = [f"H_mod{p}" for p in PRIMES] + ["H_mean"]

    overall_correlations = {}
    for target in targets:
        overall_correlations[target] = {}
        for ek in entropy_keys:
            x = [e[ek] for e in enriched if e.get(target) is not None]
            y = [e[target] for e in enriched if e.get(target) is not None]
            corr = spearman_with_pval(x, y)
            overall_correlations[target][ek] = corr
            if ek == "H_mean":
                sig = "***" if corr['p_value'] and corr['p_value'] < 0.001 else ""
                print(f"  H_mean vs {target}: rho={corr['rho']}, p={corr['p_value']:.2e}, n={corr['n']} {sig}")

    # --- Step 3: Within-dimension correlations (avoid Simpson's paradox) ---
    print("\n=== WITHIN-DIMENSION CORRELATIONS ===")
    dim_groups = defaultdict(list)
    for e in enriched:
        dim_groups[e['dim']].append(e)

    within_dim = {}
    for dim in sorted(dim_groups.keys()):
        group = dim_groups[dim]
        if len(group) < 20:
            continue

        within_dim[str(dim)] = {
            'n': len(group),
            'correlations': {}
        }

        # Kissing number distribution in this dimension
        kiss_vals = [e['kissing'] for e in group]
        kiss_unique = len(set(kiss_vals))
        within_dim[str(dim)]['kissing_unique_values'] = kiss_unique
        within_dim[str(dim)]['kissing_range'] = [int(min(kiss_vals)), int(max(kiss_vals))]

        for target in ['kissing', 'det', 'class_number']:
            within_dim[str(dim)]['correlations'][target] = {}
            for ek in entropy_keys:
                x = [e[ek] for e in group if e.get(target) is not None]
                y = [e[target] for e in group if e.get(target) is not None]
                corr = spearman_with_pval(x, y)
                within_dim[str(dim)]['correlations'][target][ek] = corr

        # Print summary for kissing
        c = within_dim[str(dim)]['correlations']['kissing']['H_mean']
        if c['rho'] is not None:
            sig = "***" if c['p_value'] and c['p_value'] < 0.001 else ""
            print(f"  dim={dim}: H_mean vs kissing: rho={c['rho']:.4f}, p={c['p_value']:.2e}, "
                  f"n={c['n']}, unique_kissing={kiss_unique} {sig}")

    # --- Step 4: Entropy distribution statistics ---
    print("\n=== ENTROPY DISTRIBUTION BY DIMENSION ===")
    entropy_stats = {}
    for dim in sorted(dim_groups.keys()):
        group = dim_groups[dim]
        if len(group) < 5:
            continue
        h_means = [e['H_mean'] for e in group]
        entropy_stats[str(dim)] = {
            'n': len(group),
            'H_mean_mean': round(float(np.mean(h_means)), 4),
            'H_mean_std': round(float(np.std(h_means)), 4),
            'H_mean_min': round(float(np.min(h_means)), 4),
            'H_mean_max': round(float(np.max(h_means)), 4),
        }
        print(f"  dim={dim}: H_mean = {np.mean(h_means):.4f} +/- {np.std(h_means):.4f} (n={len(group)})")

    # --- Step 5: Predictive test — can mod-p entropy predict kissing number? ---
    print("\n=== PREDICTIVE TEST: ENTROPY -> KISSING (within dimension) ===")
    predictive_results = {}
    for dim in sorted(dim_groups.keys()):
        group = dim_groups[dim]
        if len(group) < 30:
            continue

        kiss_vals = np.array([e['kissing'] for e in group])
        if len(set(kiss_vals)) < 2:
            continue

        # Build feature matrix: [H_mod3, H_mod5, H_mod7, H_mod11]
        X = np.array([[e[f"H_mod{p}"] for p in PRIMES] for e in group])
        y = kiss_vals

        # Simple: split into above/below median kissing, test if entropy differs
        median_kiss = np.median(y)
        above = X[y > median_kiss]
        below = X[y <= median_kiss]

        if len(above) < 5 or len(below) < 5:
            continue

        # Multivariate: use H_mean as simple predictor
        h_means = np.array([e['H_mean'] for e in group])

        # KS test: do high-kissing and low-kissing lattices have different entropy?
        ks_stat, ks_pval = stats.ks_2samp(
            h_means[y > median_kiss],
            h_means[y <= median_kiss]
        )

        # R^2 from linear regression of log(kissing) on H_mean
        log_kiss = np.log(y.astype(float) + 1)
        slope, intercept, r_val, p_val, se = stats.linregress(h_means, log_kiss)

        predictive_results[str(dim)] = {
            'n': int(len(group)),
            'median_kissing': float(median_kiss),
            'ks_stat': round(float(ks_stat), 6),
            'ks_pval': float(ks_pval),
            'R2_log_kissing': round(float(r_val**2), 6),
            'linreg_p': float(p_val),
            'slope': round(float(slope), 6),
        }

        print(f"  dim={dim}: KS={ks_stat:.4f} (p={ks_pval:.2e}), "
              f"R²(log_kiss)={r_val**2:.4f} (p={p_val:.2e}), n={len(group)}")

    # --- Step 6: Per-prime discriminative power ---
    print("\n=== PER-PRIME DISCRIMINATIVE POWER (dim=3, largest group) ===")
    per_prime = {}
    if '3' in within_dim:
        group = dim_groups[3]
        kiss_vals = np.array([e['kissing'] for e in group])
        median_kiss = np.median(kiss_vals)

        for p in PRIMES:
            h_vals = np.array([e[f'H_mod{p}'] for e in group])
            above = h_vals[kiss_vals > median_kiss]
            below = h_vals[kiss_vals <= median_kiss]
            if len(above) >= 5 and len(below) >= 5:
                ks, pv = stats.ks_2samp(above, below)
                per_prime[str(p)] = {
                    'ks_stat': round(float(ks), 6),
                    'ks_pval': float(pv),
                    'mean_above': round(float(np.mean(above)), 4),
                    'mean_below': round(float(np.mean(below)), 4),
                }
                print(f"  mod-{p}: KS={ks:.4f} (p={pv:.2e}), "
                      f"mean_above={np.mean(above):.4f}, mean_below={np.mean(below):.4f}")

    # --- Step 7: Null test — random shuffle ---
    print("\n=== NULL TEST: SHUFFLED KISSING (dim=3) ===")
    null_results = {}
    if len(dim_groups[3]) >= 30:
        group = dim_groups[3]
        h_means = np.array([e['H_mean'] for e in group])
        kiss_vals = np.array([e['kissing'] for e in group])

        real_rho, _ = stats.spearmanr(h_means, kiss_vals)
        null_rhos = []
        np.random.seed(42)
        for _ in range(10000):
            shuffled = np.random.permutation(kiss_vals)
            r, _ = stats.spearmanr(h_means, shuffled)
            null_rhos.append(r)

        null_rhos = np.array(null_rhos)
        z_score = (real_rho - np.mean(null_rhos)) / np.std(null_rhos)
        p_empirical = np.mean(np.abs(null_rhos) >= np.abs(real_rho))

        null_results = {
            'real_rho': round(float(real_rho), 6),
            'null_mean': round(float(np.mean(null_rhos)), 6),
            'null_std': round(float(np.std(null_rhos)), 6),
            'z_score': round(float(z_score), 4),
            'p_empirical': float(p_empirical),
        }
        print(f"  Real rho={real_rho:.4f}, null mean={np.mean(null_rhos):.4f} +/- {np.std(null_rhos):.4f}")
        print(f"  z-score={z_score:.2f}, empirical p={p_empirical:.4f}")

    # --- Step 8: Comparison to G10 result ---
    print("\n=== COMPARISON TO G10 (96.6% kissing accuracy from k-NN) ===")
    g10_note = (
        "G10 achieves 96.6% kissing accuracy using full theta_series as feature vector "
        "in k-NN. This analysis tests whether the predictive power comes from mod-p "
        "residue structure (information-theoretic fingerprint) rather than the full "
        "coefficient vector."
    )

    # Check: how much variance does mod-p entropy explain?
    if len(dim_groups[3]) >= 30:
        group = dim_groups[3]
        X = np.array([[e[f"H_mod{p}"] for p in PRIMES] for e in group])
        y = np.array([e['kissing'] for e in group])

        # Simple: classify into kissing bins using entropy thresholds
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.model_selection import cross_val_score

        # Entropy-only features
        scores_entropy = cross_val_score(
            KNeighborsClassifier(n_neighbors=5), X, y, cv=5, scoring='accuracy'
        )

        # Full theta series features
        theta_features = []
        for r in records:
            if r['dim'] == 3 and r.get('theta_series') and len(r['theta_series']) >= 10:
                theta_features.append(r['theta_series'])

        if len(theta_features) == len(group):
            X_full = np.array(theta_features)
            scores_full = cross_val_score(
                KNeighborsClassifier(n_neighbors=5), X_full, y, cv=5, scoring='accuracy'
            )
        else:
            scores_full = None

        g10_comparison = {
            'entropy_knn_accuracy_mean': round(float(np.mean(scores_entropy)), 4),
            'entropy_knn_accuracy_std': round(float(np.std(scores_entropy)), 4),
            'full_theta_knn_accuracy_mean': round(float(np.mean(scores_full)), 4) if scores_full is not None else None,
            'full_theta_knn_accuracy_std': round(float(np.std(scores_full)), 4) if scores_full is not None else None,
            'note': g10_note,
        }

        print(f"  Entropy-only k-NN: {np.mean(scores_entropy)*100:.1f}% +/- {np.std(scores_entropy)*100:.1f}%")
        if scores_full is not None:
            print(f"  Full theta k-NN:   {np.mean(scores_full)*100:.1f}% +/- {np.std(scores_full)*100:.1f}%")
            ratio = np.mean(scores_entropy) / np.mean(scores_full) if np.mean(scores_full) > 0 else None
            g10_comparison['entropy_explains_fraction'] = round(float(ratio), 4) if ratio else None
            print(f"  Entropy explains ~{ratio*100:.1f}% of full-theta accuracy" if ratio else "")
    else:
        g10_comparison = {'note': 'Insufficient dim=3 data for comparison'}

    # --- Assemble results ---
    results = {
        'metadata': {
            'task': 'Lattice theta series mod-p phase coherence vs arithmetic invariants',
            'data_source': 'LMFDB lat_lattices',
            'n_lattices': len(enriched),
            'primes': PRIMES,
            'reference_bridge': 'EC phase coherence rho=0.197',
            'date': '2026-04-10',
        },
        'overall_correlations': overall_correlations,
        'within_dimension_correlations': within_dim,
        'entropy_distribution_by_dim': entropy_stats,
        'predictive_test': predictive_results,
        'per_prime_discriminative_power_dim3': per_prime,
        'null_test_dim3': null_results,
        'g10_comparison': g10_comparison,
        'summary': {},
    }

    # Build summary
    dim3_kiss = within_dim.get('3', {}).get('correlations', {}).get('kissing', {}).get('H_mean', {})
    dim3_rho = dim3_kiss.get('rho')
    dim3_p = dim3_kiss.get('p_value')

    overall_kiss_rho = overall_correlations.get('kissing', {}).get('H_mean', {}).get('rho')

    results['summary'] = {
        'overall_H_mean_vs_kissing_rho': overall_kiss_rho,
        'within_dim3_H_mean_vs_kissing_rho': dim3_rho,
        'within_dim3_pvalue': dim3_p,
        'null_test_z_score': null_results.get('z_score'),
        'null_test_p_empirical': null_results.get('p_empirical'),
        'entropy_knn_accuracy': g10_comparison.get('entropy_knn_accuracy_mean'),
        'full_theta_knn_accuracy': g10_comparison.get('full_theta_knn_accuracy_mean'),
        'verdict': '',
    }

    # Determine verdict
    if dim3_rho is not None and dim3_p is not None:
        if abs(dim3_rho) > 0.1 and dim3_p < 0.001:
            verdict = (f"SIGNAL: Within dim=3, mod-p entropy correlates with kissing "
                       f"(rho={dim3_rho:.3f}, p={dim3_p:.2e}). ")
        elif abs(dim3_rho) > 0.05 and dim3_p < 0.05:
            verdict = (f"WEAK SIGNAL: Within dim=3, mod-p entropy shows weak correlation "
                       f"with kissing (rho={dim3_rho:.3f}, p={dim3_p:.2e}). ")
        else:
            verdict = (f"NO SIGNAL: Within dim=3, mod-p entropy does not correlate with "
                       f"kissing (rho={dim3_rho:.3f}, p={dim3_p:.2e}). ")
    else:
        verdict = "INSUFFICIENT DATA for within-dimension test. "

    if g10_comparison.get('entropy_knn_accuracy_mean') and g10_comparison.get('full_theta_knn_accuracy_mean'):
        ratio = g10_comparison['entropy_knn_accuracy_mean'] / g10_comparison['full_theta_knn_accuracy_mean']
        if ratio < 0.3:
            verdict += "Mod-p entropy captures <30% of full-theta predictive power — G10 success is NOT explained by residue structure alone."
        elif ratio < 0.7:
            verdict += f"Mod-p entropy captures ~{ratio*100:.0f}% of full-theta predictive power — partial explanation of G10."
        else:
            verdict += f"Mod-p entropy captures ~{ratio*100:.0f}% of full-theta predictive power — G10 success IS largely explained by residue structure."

    results['summary']['verdict'] = verdict
    print(f"\n=== VERDICT ===\n{verdict}")

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
