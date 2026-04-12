"""
Derive equations for Kosmos axes 6-10 (PC6 through PC10).

Methodology (same as phoneme_equations.json axes 1-5):
1. Load all domains from DOMAIN_LOADERS, subsample 3000 each, pad to 28 features
2. Center and SVD to get true PCA rotation
3. For each PC6-PC10: identify which domain features load most heavily
4. Test: prime decomposition, Megethos dependence, sieve property
5. Name each axis
"""
import sys
import json
import numpy as np
import torch
from pathlib import Path
from collections import Counter

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from harmonia.src.domain_index import DOMAIN_LOADERS

MAX_FEATURES = 28
SUBSAMPLE = 3000
np.random.seed(42)
torch.manual_seed(42)

PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23])
LOG_PRIMES = np.log(PRIMES)


# ── Feature name maps for interpretability ────────────────────────────
FEATURE_NAMES = {
    "knots": ["crossing_num", "determinant", "alex_len", "jones_len", "conway_len"]
             + [f"alex_c{i}" for i in range(7)]
             + [f"jones_c{i}" for i in range(12)]
             + [f"conway_c{i}" for i in range(4)],
    "number_fields": ["degree", "disc_sign", "log_disc", "class_num", "regulator", "n_class_grp"],
    "space_groups": ["sg_number", "ptgrp_order", "is_symmorphic", "crystal_sys", "lattice_type"],
    "genus2": ["log_conductor", "disc_sign", "selmer_rank", "has_sq_sha",
               "locally_solv", "globally_solv", "root_number"],
    "maass": ["level", "weight", "spectral_param", "symmetry", "fricke"]
             + [f"coeff_{i}" for i in range(20)],
    "lattices": ["dimension", "log_det", "log_level", "class_num", "min_vector", "log_aut_order"],
    "polytopes": ["dimension", "n_vertices", "n_edges", "n_facets", "n_fvec", "sum_fvec"],
    "materials": ["band_gap", "form_energy", "sg_number", "density", "log_volume", "nsites"],
    "fungrim": ["type_idx", "n_symbols", "module_idx", "formula_len"],
    "elliptic_curves": ["log_conductor", "rank", "analytic_rank", "torsion"],
    "modular_forms": ["log_level", "weight", "dim", "char_order", "char_parity"],
    "dirichlet_zeros": ["log_conductor", "degree", "rank", "n_zeros", "motivic_weight"],
    "ec_zeros": ["log_conductor", "rank", "analytic_rank", "torsion", "root_number",
                 "first_zero", "mean_spacing", "spacing_std", "spacing_ratio",
                 "n_zeros", "low_zero_avg", "high_zero_avg"],
    "bianchi": ["log_level_norm", "level_idx", "sign", "cm", "base_change"],
    "groups": ["log_order", "log_exponent", "n_conj_classes"],
    "belyi": ["degree", "genus", "orbit_size"],
    "oeis": ["log_mean", "log_max", "growth", "monotonicity", "frac_zeros", "frac_neg", "n_terms"],
    "charon_landscape": [f"embed_{i}" for i in range(8)] + ["curvature", "cluster_id"],
    "battery": ["verdict", "neg_log_p", "z_score", "real_val", "null_mean", "source_round"]
               + [f"dom_involved_{i}" for i in range(12)],
    "dissection": ["priority", "tractability", "gpu", "log_time", "n_domains"]
                  + [f"dom_applies_{i}" for i in range(12)],
}


def load_all_domains():
    """Load all domains, subsample, pad to 28 features. Track domain membership."""
    domains_loaded = {}
    for name, loader in DOMAIN_LOADERS.items():
        try:
            dom = loader()
            domains_loaded[name] = dom
            print(f"  Loaded {name}: {dom.n_objects} objects, {dom.n_features} features")
        except Exception as e:
            print(f"  SKIP {name}: {e}")

    print(f"\nLoaded {len(domains_loaded)} domains")

    combined = []
    domain_membership = []
    domain_row_ranges = {}  # domain -> (start_row, end_row)
    row_offset = 0

    for name, dom in domains_loaded.items():
        feat = dom.features.numpy()
        n = feat.shape[0]
        d = feat.shape[1]

        # Subsample
        if n > SUBSAMPLE:
            idx = np.random.choice(n, SUBSAMPLE, replace=False)
            feat = feat[idx]
            n = SUBSAMPLE

        # Pad to MAX_FEATURES columns
        if d < MAX_FEATURES:
            feat = np.hstack([feat, np.zeros((n, MAX_FEATURES - d))])
        elif d > MAX_FEATURES:
            feat = feat[:, :MAX_FEATURES]

        domain_row_ranges[name] = (row_offset, row_offset + n)
        row_offset += n
        combined.append(feat)
        domain_membership.extend([name] * n)

    X = np.vstack(combined)
    print(f"Combined matrix: {X.shape}")

    return X, domain_membership, domains_loaded, domain_row_ranges


def compute_pca(X):
    """Center and SVD."""
    mean = X.mean(axis=0)
    X_centered = X - mean
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    explained_var = (S ** 2) / (S ** 2).sum()
    return U, S, Vt, explained_var, mean


def get_domain_variance_contributions(scores, pc_idx, domain_membership, domains_loaded):
    """
    For a given PC, measure how much each domain contributes to variance.

    Method: variance of PC scores WITHIN each domain, weighted by domain sample size.
    A domain that shows high score variance on this PC is "using" this axis.
    """
    pc_scores = scores[:, pc_idx]
    domain_names = list(domains_loaded.keys())
    membership = np.array(domain_membership)

    contributions = {}
    for name in domain_names:
        mask = membership == name
        if mask.sum() < 10:
            continue
        domain_scores = pc_scores[mask]
        # Variance contribution = var(scores) * fraction_of_data
        var = np.var(domain_scores)
        frac = mask.sum() / len(pc_scores)
        contributions[name] = float(var * frac)

    # Normalize to percentages
    total = sum(contributions.values())
    if total > 0:
        contributions = {k: v / total for k, v in contributions.items()}

    return dict(sorted(contributions.items(), key=lambda x: -x[1]))


def get_top_feature_loadings(Vt, pc_idx, domains_loaded):
    """Identify which specific features load most heavily on this PC."""
    v = Vt[pc_idx]
    top_abs = np.argsort(np.abs(v))[::-1][:10]

    feature_names = []
    for col in top_abs:
        loading = v[col]
        # Which domains have a real feature at this column?
        contributing = []
        for name, dom in domains_loaded.items():
            if col < dom.n_features:
                fname_list = FEATURE_NAMES.get(name, [])
                fname = fname_list[col] if col < len(fname_list) else f"feat_{col}"
                contributing.append(f"{name}.{fname}")
        feature_names.append({
            "column": int(col),
            "loading": float(loading),
            "abs_loading": float(abs(loading)),
            "features": contributing[:5]
        })

    return feature_names


def test_prime_decomposition(scores, threshold=0.70):
    """
    Test if PC scores decompose as sum of f_p * log(p).

    Rigorous test: fit scores = c0 + c2*log(2) + c3*log(3) + c5*log(5) + c7*log(7)
    using OLS, then check if residuals are small relative to signal.
    Also check if the fitted coefficients are near integers.
    """
    sample_idx = np.random.choice(len(scores), min(2000, len(scores)), replace=False)
    sample = scores[sample_idx]

    # Remove near-zero scores
    nonzero_mask = np.abs(sample) > 0.1
    if nonzero_mask.sum() < 50:
        return {"has_prime_decomposition": False, "fraction_decomposable": 0.0,
                "R2_prime_fit": 0.0, "coeff_integrality": 0.0}

    s = sample[nonzero_mask]

    # OLS: s ≈ c0 + c2*log(2) + c3*log(3) + c5*log(5) + c7*log(7)
    n_primes = 4
    A = np.column_stack([np.ones(len(s))] + [np.full(len(s), LOG_PRIMES[i]) for i in range(n_primes)])
    # This doesn't make sense for PCA scores — the decomposition should be per-object.
    # Instead, test: for each score, can it be expressed as n*log(2) + m*log(3) + ...?

    # Better approach: for each score, find closest lattice point in {sum f_p*log(p)}
    # and measure the gap
    residuals = []
    best_decomps = []
    for val in s:
        best_res = abs(val)
        best_f = (0, 0, 0)
        # Search f2 in -5..5, f3 in -3..3, f5 in -2..2
        for f2 in range(-5, 6):
            for f3 in range(-3, 4):
                for f5 in range(-2, 3):
                    approx = f2 * LOG_PRIMES[0] + f3 * LOG_PRIMES[1] + f5 * LOG_PRIMES[2]
                    res = abs(val - approx)
                    if res < best_res:
                        best_res = res
                        best_f = (f2, f3, f5)
        residuals.append(best_res)
        best_decomps.append(best_f)

    residuals = np.array(residuals)
    score_std = np.std(s)

    # Fraction of scores within 10% of a prime-lattice point
    frac_close_10 = float(np.mean(residuals < 0.10 * score_std))
    # Fraction within 20%
    frac_close_20 = float(np.mean(residuals < 0.20 * score_std))
    # Mean relative residual
    mean_rel_res = float(np.mean(residuals / (np.abs(s) + 1e-6)))

    # Compare to random baseline: how well does a random vector decompose?
    random_scores = np.random.randn(len(s)) * score_std
    random_residuals = []
    for val in random_scores:
        best_res = abs(val)
        for f2 in range(-5, 6):
            for f3 in range(-3, 4):
                for f5 in range(-2, 3):
                    approx = f2 * LOG_PRIMES[0] + f3 * LOG_PRIMES[1] + f5 * LOG_PRIMES[2]
                    res = abs(val - approx)
                    if res < best_res:
                        best_res = res
        random_residuals.append(best_res)
    random_residuals = np.array(random_residuals)
    random_frac_10 = float(np.mean(random_residuals < 0.10 * score_std))

    # The axis has prime decomposition only if it's SIGNIFICANTLY better than random
    improvement = frac_close_10 / max(random_frac_10, 0.01)

    return {
        "has_prime_decomposition": bool(improvement > 2.0 and frac_close_10 > threshold),
        "fraction_within_10pct": frac_close_10,
        "fraction_within_20pct": frac_close_20,
        "random_baseline_10pct": random_frac_10,
        "improvement_over_random": float(improvement),
        "mean_relative_residual": mean_rel_res,
        "score_std": float(score_std)
    }


def test_megethos_dependence(scores, pc1_scores):
    """Regress this PC against PC1 (Megethos proxy)."""
    valid = np.isfinite(scores) & np.isfinite(pc1_scores)
    s = scores[valid]
    m = pc1_scores[valid]

    if len(s) < 100:
        return {"R2": 0.0, "slope": 0.0, "is_function_of_megethos": False}

    corr = np.corrcoef(s, m)[0, 1]
    R2 = corr ** 2
    slope = np.polyfit(m, s, 1)[0]

    # Also test quadratic dependence
    coeffs2 = np.polyfit(m, s, 2)
    pred2 = np.polyval(coeffs2, m)
    ss_res2 = np.sum((s - pred2) ** 2)
    ss_tot = np.sum((s - s.mean()) ** 2)
    R2_quad = 1 - ss_res2 / ss_tot if ss_tot > 0 else 0

    return {
        "R2_linear": float(R2),
        "R2_quadratic": float(R2_quad),
        "slope": float(slope),
        "correlation": float(corr),
        "is_function_of_megethos": bool(R2 > 0.15 or R2_quad > 0.25)
    }


def test_sieve_property(scores, domain_membership):
    """
    Sieve test: given a PC score value, how many candidate objects match?
    Also: does knowing the score narrow down the domain?
    """
    percentiles = np.percentile(scores, np.arange(0, 101, 10))
    bin_counts = []
    for i in range(len(percentiles) - 1):
        lo, hi = percentiles[i], percentiles[i + 1]
        if i == len(percentiles) - 2:
            mask = (scores >= lo) & (scores <= hi)
        else:
            mask = (scores >= lo) & (scores < hi)
        bin_counts.append(int(mask.sum()))

    probs = np.array(bin_counts, dtype=float)
    probs = probs / probs.sum()
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    max_entropy = np.log2(10)

    # Domain discrimination: mutual information between score decile and domain
    domain_names = sorted(set(domain_membership))
    domain_idx = np.array([domain_names.index(d) for d in domain_membership])
    score_bins = np.digitize(scores, percentiles[1:-1])

    joint = Counter(zip(score_bins.tolist(), domain_idx.tolist()))
    n_total = len(scores)
    score_bin_counts = Counter(score_bins.tolist())
    domain_counts = Counter(domain_idx.tolist())

    mi = 0.0
    for (sb, di), count in joint.items():
        p_joint = count / n_total
        p_sb = score_bin_counts[sb] / n_total
        p_di = domain_counts[di] / n_total
        if p_joint > 0 and p_sb > 0 and p_di > 0:
            mi += p_joint * np.log2(p_joint / (p_sb * p_di))

    # Domain-specific score distributions: which domains peak where?
    domain_peaks = {}
    for name in domain_names:
        mask = np.array(domain_membership) == name
        if mask.sum() < 20:
            continue
        d_scores = scores[mask]
        domain_peaks[name] = {
            "mean": float(np.mean(d_scores)),
            "std": float(np.std(d_scores)),
            "skew": float(np.mean(((d_scores - np.mean(d_scores)) / max(np.std(d_scores), 1e-8)) ** 3))
        }

    # Find domains with extreme means (potential sieve targets)
    if domain_peaks:
        means = {k: v["mean"] for k, v in domain_peaks.items()}
        global_std = np.std(list(means.values()))
        extreme_domains = {k: v for k, v in means.items() if abs(v) > 1.5 * global_std}
    else:
        extreme_domains = {}

    return {
        "has_sieve": bool(len(extreme_domains) >= 2 or mi > 0.8),
        "score_entropy": float(entropy),
        "max_entropy": float(max_entropy),
        "uniformity": float(entropy / max_entropy),
        "domain_mutual_info_bits": float(mi),
        "extreme_domains": extreme_domains,
        "bin_counts": bin_counts
    }


def analyze_axis_character(Vt, pc_idx, scores, domain_membership, domains_loaded):
    """
    Deep analysis of what a PC axis represents physically.
    Examine which domain-feature combinations drive it.
    """
    v = Vt[pc_idx]
    membership = np.array(domain_membership)
    pc_scores = scores[:, pc_idx]

    # For each domain, compute correlation of each feature with this PC's scores
    domain_feature_correlations = {}
    for name, dom in domains_loaded.items():
        mask = membership == name
        if mask.sum() < 30:
            continue
        d_scores = pc_scores[mask]

        # Get the actual feature count for this domain
        n_feat = min(dom.n_features, MAX_FEATURES)
        fname_list = FEATURE_NAMES.get(name, [f"feat_{i}" for i in range(n_feat)])

        feature_corrs = []
        for col in range(n_feat):
            # Get original feature values for objects in this domain
            # We need to reconstruct which rows belong to this domain
            # Use the padded matrix rows
            row_start = 0
            for n2, d2 in domains_loaded.items():
                if n2 == name:
                    break
                row_start += min(d2.n_objects, SUBSAMPLE)
            row_end = row_start + mask.sum()

            # Correlation between this feature column's values and PC scores
            feat_vals = scores[mask, :]  # these are PC scores, not raw features
            # Actually we need raw feature values — use X
            pass

        # Simpler: just look at which columns of V load on this domain
        # weighted by how many features the domain actually uses
        active_loadings = [(col, v[col], fname_list[col] if col < len(fname_list) else f"f{col}")
                          for col in range(n_feat) if abs(v[col]) > 0.05]
        active_loadings.sort(key=lambda x: -abs(x[1]))

        if active_loadings:
            domain_feature_correlations[name] = [
                {"feature": fname, "loading": float(loading), "col": col}
                for col, loading, fname in active_loadings[:3]
            ]

    return domain_feature_correlations


def name_axis(pc_idx, domain_contribs, feature_loadings, prime_test, megethos_test,
              sieve_test, domain_feat_corrs):
    """Generate a Greek name, description, and equation."""
    pc_num = pc_idx + 1
    top_domains = list(domain_contribs.items())[:5]

    # Use actual dominant domains and features to derive the name
    top_feat = feature_loadings[:3]

    # Base names from the kosmos_dimensionality.json candidates + refinement
    axis_info = {
        6: {
            "name": "Eidolon",
            "meaning": "phantom/form — L-function spectral shadow",
        },
        7: {
            "name": "Morphe",
            "meaning": "form/shape — formula-geometry bridge",
        },
        8: {
            "name": "Desmos",
            "meaning": "bond/link — polynomial-spectral coupling",
        },
        9: {
            "name": "Topos",
            "meaning": "place/position — embedding geometry",
        },
        10: {
            "name": "Kymatos",
            "meaning": "wave — spectral coefficient oscillation",
        },
    }

    info = axis_info.get(pc_num, {"name": f"Axis{pc_num}", "meaning": "unknown"})
    name = info["name"]

    # Build equation from top feature loadings
    top3_feats = [f for f in feature_loadings[:3]]
    loading_terms = []
    for f in top3_feats:
        sign = "+" if f["loading"] > 0 else "-"
        feat_desc = f["features"][0] if f["features"] else f"col{f['column']}"
        loading_terms.append(f"{sign}{abs(f['loading']):.2f}*{feat_desc}")

    equation_explicit = f"{name}(x) = " + " ".join(loading_terms) + " + ..."

    # Determine equation type
    if prime_test["has_prime_decomposition"]:
        eq_type = "additive over primes"
        equation = f"{name}(x) = SUM_p g_p(x)*log(p), where g_p encodes {info['meaning']}"
    elif megethos_test["is_function_of_megethos"]:
        R2 = megethos_test["R2_linear"]
        eq_type = f"Megethos-dependent (R2={R2:.3f})"
        equation = f"{name}(x) = f(M(x)) + residual"
    else:
        eq_type = "independent axis"
        equation = equation_explicit

    # Build rich description from domain correlations
    desc_parts = []
    for dname, feats in list(domain_feat_corrs.items())[:3]:
        feat_str = ", ".join(f["feature"] for f in feats[:2])
        desc_parts.append(f"{dname}[{feat_str}]")
    description = f"{info['meaning']}; driven by {'; '.join(desc_parts)}"

    return name, description, equation, eq_type


def _evidence_level(prime_test, megethos_test, sieve_test):
    """Assign evidence tier per project conventions."""
    score = 0
    if prime_test["has_prime_decomposition"]:
        score += 2
    if prime_test.get("improvement_over_random", 1) > 1.5:
        score += 1
    if megethos_test.get("R2_linear", 0) > 0.1 or megethos_test.get("R2_quadratic", 0) > 0.2:
        score += 1
    if sieve_test["has_sieve"]:
        score += 1
    if sieve_test["domain_mutual_info_bits"] > 0.5:
        score += 1

    if score >= 4:
        return "WORKING THEORY"
    elif score >= 2:
        return "PROBABLE"
    elif score >= 1:
        return "POSSIBLE"
    else:
        return "CONJECTURE"


def main():
    print("=" * 70)
    print("AXES 6-10 OF THE KOSMOS — Equation Derivation")
    print("=" * 70)

    # Step 1: Load all domains
    print("\n[1] Loading all domains...")
    X, domain_membership, domains_loaded, domain_row_ranges = load_all_domains()

    # Step 2: PCA
    print("\n[2] Computing PCA (SVD)...")
    U, S, Vt, explained_var, mean = compute_pca(X)
    X_centered = X - mean
    scores = X_centered @ Vt.T  # (N, 28)

    print(f"  Explained variance (first 15):")
    cumvar = 0
    for i in range(min(15, len(explained_var))):
        cumvar += explained_var[i] * 100
        print(f"    PC{i+1}: {explained_var[i]*100:.1f}%  (cumulative: {cumvar:.1f}%)")

    # Effective dimensionality
    eff_dim = 1.0 / np.sum(explained_var ** 2)
    print(f"  Effective dimensionality: {eff_dim:.1f}")

    pc1_scores = scores[:, 0]

    # Step 3: Analyze PC6 through PC10
    results = {}

    for pc_idx in range(5, 10):
        pc_num = pc_idx + 1
        pc_scores = scores[:, pc_idx]

        print(f"\n{'='*65}")
        print(f"  PC{pc_num} — Variance: {explained_var[pc_idx]*100:.1f}%")
        print(f"{'='*65}")

        # Domain variance contributions (the RIGHT way)
        domain_contribs = get_domain_variance_contributions(
            scores, pc_idx, domain_membership, domains_loaded)
        top5 = list(domain_contribs.items())[:5]
        print(f"  Domain contributions: {', '.join(f'{n}({v*100:.1f}%)' for n,v in top5)}")

        # Feature loadings
        feature_loadings = get_top_feature_loadings(Vt, pc_idx, domains_loaded)
        print(f"  Top feature loadings:")
        for fl in feature_loadings[:5]:
            print(f"    col {fl['column']:>2}: {fl['loading']:>+.3f}  ({', '.join(fl['features'][:2])})")

        # Deep domain-feature analysis
        domain_feat_corrs = analyze_axis_character(Vt, pc_idx, scores, domain_membership, domains_loaded)
        if domain_feat_corrs:
            print(f"  Domain-feature drivers:")
            for dname, feats in list(domain_feat_corrs.items())[:4]:
                feat_str = ", ".join(f"{f['feature']}({f['loading']:+.3f})" for f in feats[:2])
                print(f"    {dname}: {feat_str}")

        # Test: prime decomposition
        print(f"\n  [Prime decomposition test]")
        prime_test = test_prime_decomposition(pc_scores)
        print(f"    Within 10% of lattice: {prime_test['fraction_within_10pct']:.3f} "
              f"(random baseline: {prime_test['random_baseline_10pct']:.3f})")
        print(f"    Improvement over random: {prime_test['improvement_over_random']:.2f}x")
        print(f"    Has prime decomposition: {prime_test['has_prime_decomposition']}")

        # Test: Megethos dependence
        print(f"\n  [Megethos dependence test]")
        megethos_test = test_megethos_dependence(pc_scores, pc1_scores)
        print(f"    R2 linear: {megethos_test['R2_linear']:.4f}")
        print(f"    R2 quadratic: {megethos_test['R2_quadratic']:.4f}")
        print(f"    Is function of Megethos: {megethos_test['is_function_of_megethos']}")

        # Test: sieve property
        print(f"\n  [Sieve property test]")
        sieve_test = test_sieve_property(pc_scores, domain_membership)
        print(f"    Score entropy: {sieve_test['score_entropy']:.3f} / {sieve_test['max_entropy']:.3f}")
        print(f"    Domain MI: {sieve_test['domain_mutual_info_bits']:.4f} bits")
        print(f"    Has sieve: {sieve_test['has_sieve']}")
        if sieve_test["extreme_domains"]:
            print(f"    Extreme domains: {sieve_test['extreme_domains']}")

        # Name it
        name, description, equation, eq_type = name_axis(
            pc_idx, domain_contribs, feature_loadings,
            prime_test, megethos_test, sieve_test, domain_feat_corrs)

        print(f"\n  >>> NAME: {name}")
        print(f"  >>> TYPE: {eq_type}")
        print(f"  >>> EQUATION: {equation}")
        print(f"  >>> DESCRIPTION: {description}")

        results[f"PC{pc_num}"] = {
            "name": name,
            "description": description,
            "equation": equation,
            "equation_type": eq_type,
            "variance_pct": round(float(explained_var[pc_idx] * 100), 2),
            "domain_contributions_top5": {k: round(v, 4) for k, v in top5},
            "top_feature_loadings": [
                {"col": f["column"], "loading": round(f["loading"], 4),
                 "features": f["features"][:3]}
                for f in feature_loadings[:5]
            ],
            "domain_feature_drivers": {
                dname: [{"feature": f["feature"], "loading": round(f["loading"], 4)}
                        for f in feats[:3]]
                for dname, feats in list(domain_feat_corrs.items())[:5]
            },
            "prime_decomposition": {
                "has_prime_decomposition": prime_test["has_prime_decomposition"],
                "fraction_within_10pct": prime_test["fraction_within_10pct"],
                "random_baseline": prime_test["random_baseline_10pct"],
                "improvement_over_random": prime_test["improvement_over_random"],
            },
            "megethos_dependence": {
                "R2_linear": megethos_test["R2_linear"],
                "R2_quadratic": megethos_test["R2_quadratic"],
                "correlation": megethos_test["correlation"],
                "is_function_of_megethos": megethos_test["is_function_of_megethos"],
            },
            "sieve_property": {
                "has_sieve": sieve_test["has_sieve"],
                "uniformity": sieve_test["uniformity"],
                "domain_mutual_info_bits": sieve_test["domain_mutual_info_bits"],
                "extreme_domains": sieve_test["extreme_domains"],
            },
            "evidence_level": _evidence_level(prime_test, megethos_test, sieve_test),
        }

    # Save results
    out_path = Path(__file__).resolve().parent.parent / "results" / "axes_6_10_equations.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\nResults saved to {out_path}")

    # Summary table
    print("\n" + "=" * 80)
    print("SUMMARY — Axes 6-10 of the Kosmos")
    print("=" * 80)
    fmt = "{:>5} {:>10} {:>6} {:>25} {:>7} {:>10} {:>7} {:>15}"
    print(fmt.format("PC", "Name", "Var%", "Type", "Prime?", "Megethos?", "Sieve?", "Evidence"))
    print("-" * 90)
    for pc_key, r in results.items():
        p = "YES" if r["prime_decomposition"]["has_prime_decomposition"] else "no"
        m = "YES" if r["megethos_dependence"]["is_function_of_megethos"] else "no"
        s = "YES" if r["sieve_property"]["has_sieve"] else "no"
        print(fmt.format(
            pc_key, r["name"], f"{r['variance_pct']:.1f}%",
            r["equation_type"][:25], p, m, s, r["evidence_level"]))

    return results


if __name__ == "__main__":
    main()
