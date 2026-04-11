"""
Maass Newform vs Oldform Coefficient Separation
================================================
Challenge: Can we systematically separate newforms from oldforms
using coefficient statistics at composite levels?

Approach:
  1. For each form at composite level N, test if c_p at primes p|N
     are degenerate (near-zero or redundant).
  2. Build 4 features: entropy, near-zero fraction, kurtosis, phase coherence.
  3. Binary classification via Random Forest.
  4. Measure: what fraction are oldform-like? Does removing them change M4/M2^2?
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats as sp_stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sympy import isprime, factorint

# ── paths ──
DATA = Path(__file__).resolve().parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUT_JSON = Path(__file__).resolve().parent / "maass_newform_oldform_results.json"


def load_data():
    with open(DATA) as f:
        return json.load(f)


def primes_up_to(n):
    """Sieve of Eratosthenes."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i in range(2, n + 1) if sieve[i]]


def coefficient_entropy(coeffs):
    """Shannon entropy of discretised coefficient distribution."""
    if len(coeffs) < 10:
        return 0.0
    hist, _ = np.histogram(coeffs, bins=30, density=True)
    hist = hist[hist > 0]
    if len(hist) == 0:
        return 0.0
    hist = hist / hist.sum()
    return -np.sum(hist * np.log2(hist))


def near_zero_fraction(coeffs, threshold=0.05):
    """Fraction of coefficients within `threshold` of zero."""
    arr = np.abs(np.array(coeffs))
    return float(np.mean(arr < threshold))


def kurtosis(coeffs):
    """Excess kurtosis."""
    if len(coeffs) < 4:
        return 0.0
    return float(sp_stats.kurtosis(coeffs, fisher=True))


def phase_coherence(coeffs):
    """
    Phase coherence: how much the signs of consecutive coefficients agree.
    High coherence → more structured (oldform-like pattern).
    """
    if len(coeffs) < 3:
        return 0.5
    signs = np.sign(coeffs[1:])  # skip c_0 = 1 always
    agreements = np.sum(signs[:-1] == signs[1:])
    return float(agreements / (len(signs) - 1))


def divisor_degeneracy_score(form, prime_list):
    """
    For a form at composite level N, check how many primes p|N
    have c_p near zero or are suspiciously degenerate.

    Returns fraction of primes dividing N where |c_p| < 0.1.
    For prime levels, returns 0.
    """
    level = form["level"]
    if level <= 1:
        return 0.0
    factors = factorint(level)
    if len(factors) <= 1 and list(factors.values())[0] == 1:
        # prime level — no oldform degeneracy expected
        return 0.0

    coeffs = form["coefficients"]
    n_coeffs = len(coeffs)
    degenerate_count = 0
    tested = 0

    for p in factors:
        if p < n_coeffs:
            # coefficients are indexed from 0, c_p is at index p
            # but c_0 = a(0), c_1 = a(1), etc. — a(n) at index n
            c_p = coeffs[p] if p < n_coeffs else None
            if c_p is not None:
                tested += 1
                if abs(c_p) < 0.1:
                    degenerate_count += 1

    if tested == 0:
        return 0.0
    return degenerate_count / tested


def compute_features(forms):
    """Compute 4 features + degeneracy score for all forms."""
    primes = primes_up_to(1000)
    results = []
    for form in forms:
        coeffs = np.array(form["coefficients"], dtype=float)
        if len(coeffs) < 20:
            continue
        feat = {
            "maass_id": form["maass_id"],
            "level": form["level"],
            "spectral_parameter": form["spectral_parameter"],
            "is_composite": not isprime(form["level"]) and form["level"] > 1,
            "entropy": coefficient_entropy(coeffs),
            "near_zero_frac": near_zero_fraction(coeffs),
            "kurtosis": kurtosis(coeffs),
            "phase_coherence": phase_coherence(coeffs),
            "divisor_degeneracy": divisor_degeneracy_score(form, primes),
        }
        results.append(feat)
    return results


def label_forms(features):
    """
    Heuristic labelling for training:
    - Prime-level forms are 'newform' (label=0) — at prime level, all forms are new.
    - Level-1 forms are 'newform' (label=0).
    - Composite-level forms get soft labels from degeneracy + entropy.

    For the classifier, we train on prime-level (known newforms) vs
    the most degenerate composite-level forms (likely oldforms).
    """
    # Use prime-level forms as clean newform examples
    prime_feats = [f for f in features if not f["is_composite"]]
    composite_feats = [f for f in features if f["is_composite"]]

    # For composite forms, flag those with high degeneracy AND low entropy
    # as likely oldforms
    if composite_feats:
        entropies = np.array([f["entropy"] for f in composite_feats])
        degens = np.array([f["divisor_degeneracy"] for f in composite_feats])
        nz_fracs = np.array([f["near_zero_frac"] for f in composite_feats])

        # Oldform-like: high degeneracy OR (low entropy AND high near-zero fraction)
        ent_thresh = np.percentile(entropies, 25)
        nz_thresh = np.percentile(nz_fracs, 75)

        for i, f in enumerate(composite_feats):
            is_oldform_like = (
                degens[i] > 0.5
                or (entropies[i] < ent_thresh and nz_fracs[i] > nz_thresh)
            )
            f["oldform_label"] = 1 if is_oldform_like else 0

    for f in prime_feats:
        f["oldform_label"] = 0  # known newforms

    return prime_feats, composite_feats


def train_classifier(prime_feats, composite_feats):
    """
    Train Random Forest:
    - Positive class: composite forms flagged as oldform-like (heuristic)
    - Negative class: prime-level forms (known newforms)
    """
    feature_names = ["entropy", "near_zero_frac", "kurtosis", "phase_coherence"]

    # Build training set: all prime-level (label=0) + heuristic-labelled composite
    all_feats = prime_feats + composite_feats
    X = np.array([[f[k] for k in feature_names] for f in all_feats])
    y = np.array([f["oldform_label"] for f in all_feats])

    # Handle NaN/inf
    X = np.nan_to_num(X, nan=0.0, posinf=10.0, neginf=-10.0)

    clf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, class_weight="balanced")

    # Cross-validation
    cv_scores = cross_val_score(clf, X, y, cv=5, scoring="f1")

    # Fit on full data
    clf.fit(X, y)
    importances = dict(zip(feature_names, clf.feature_importances_.tolist()))

    # Predict probabilities for all composite forms
    X_comp = np.array([[f[k] for k in feature_names] for f in composite_feats])
    X_comp = np.nan_to_num(X_comp, nan=0.0, posinf=10.0, neginf=-10.0)
    probs = clf.predict_proba(X_comp)[:, 1]  # P(oldform)

    for i, f in enumerate(composite_feats):
        f["oldform_prob"] = float(probs[i])

    return clf, cv_scores, importances


def compute_m4_m2_ratio(forms_data, indices=None):
    """Compute M4/M2^2 for gap distribution of spectral parameters."""
    if indices is not None:
        sps = sorted([float(forms_data[i]["spectral_parameter"]) for i in indices
                       if isinstance(forms_data[i]["spectral_parameter"], (int, float))
                       or (isinstance(forms_data[i]["spectral_parameter"], str)
                           and forms_data[i]["spectral_parameter"].replace('.','',1).replace('-','',1).isdigit())])
    else:
        sps = sorted([float(f["spectral_parameter"]) for f in forms_data
                       if isinstance(f["spectral_parameter"], (int, float))
                       or (isinstance(f["spectral_parameter"], str)
                           and f["spectral_parameter"].replace('.','',1).replace('-','',1).isdigit())])

    if len(sps) < 10:
        return None, None, None

    gaps = np.diff(sps)
    if np.mean(gaps) > 0:
        gaps = gaps / np.mean(gaps)  # normalize

    m2 = np.mean(gaps**2)
    m4 = np.mean(gaps**4)
    ratio = m4 / (m2**2) if m2 > 0 else None
    return float(m2), float(m4), ratio


def main():
    print("Loading Maass forms...")
    forms = load_data()
    print(f"  {len(forms)} forms loaded")

    print("Computing features...")
    features = compute_features(forms)
    print(f"  {len(features)} forms with features")

    # Counts
    composite_count = sum(1 for f in features if f["is_composite"])
    prime_count = sum(1 for f in features if not f["is_composite"])
    print(f"  Prime/level-1 forms: {prime_count}")
    print(f"  Composite-level forms: {composite_count}")

    print("Labelling and training classifier...")
    prime_feats, composite_feats = label_forms(features)

    heuristic_oldforms = sum(1 for f in composite_feats if f["oldform_label"] == 1)
    print(f"  Heuristic oldform-like (composite): {heuristic_oldforms}/{len(composite_feats)} "
          f"({100*heuristic_oldforms/len(composite_feats):.1f}%)")

    clf, cv_scores, importances = train_classifier(prime_feats, composite_feats)
    print(f"  RF cross-val F1: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")
    print(f"  Feature importances: {importances}")

    # Classifier-based oldform probabilities
    high_prob_oldforms = sum(1 for f in composite_feats if f["oldform_prob"] > 0.5)
    print(f"\n  RF-predicted oldforms (P>0.5): {high_prob_oldforms}/{len(composite_feats)} "
          f"({100*high_prob_oldforms/len(composite_feats):.1f}%)")

    # ── M4/M2^2 analysis ──
    print("\nComputing M4/M2^2 ratios...")

    # Build index maps
    id_to_idx = {f["maass_id"]: i for i, f in enumerate(forms)}

    # All forms
    m2_all, m4_all, ratio_all = compute_m4_m2_ratio(forms)
    print(f"  All forms: M4/M2^2 = {ratio_all:.4f}")

    # Composite-level forms only
    comp_ids = [f["maass_id"] for f in composite_feats]
    comp_indices = [id_to_idx[mid] for mid in comp_ids if mid in id_to_idx]
    m2_comp, m4_comp, ratio_comp = compute_m4_m2_ratio(forms, comp_indices)
    print(f"  Composite-level forms: M4/M2^2 = {ratio_comp:.4f}" if ratio_comp else "  Composite: insufficient data")

    # Composite minus oldforms (newforms only at composite levels)
    newform_comp_ids = [f["maass_id"] for f in composite_feats if f["oldform_prob"] <= 0.5]
    newform_comp_indices = [id_to_idx[mid] for mid in newform_comp_ids if mid in id_to_idx]
    m2_new, m4_new, ratio_new = compute_m4_m2_ratio(forms, newform_comp_indices)
    print(f"  Composite newforms only: M4/M2^2 = {ratio_new:.4f}" if ratio_new else "  Composite newforms: insufficient data")

    # Oldforms only
    oldform_ids = [f["maass_id"] for f in composite_feats if f["oldform_prob"] > 0.5]
    oldform_indices = [id_to_idx[mid] for mid in oldform_ids if mid in id_to_idx]
    m2_old, m4_old, ratio_old = compute_m4_m2_ratio(forms, oldform_indices)
    print(f"  Oldforms only: M4/M2^2 = {ratio_old:.4f}" if ratio_old else "  Oldforms: insufficient data")

    # All forms minus oldforms
    all_minus_old_ids = set(f["maass_id"] for f in features) - set(oldform_ids)
    all_minus_old_indices = [id_to_idx[mid] for mid in all_minus_old_ids if mid in id_to_idx]
    m2_clean, m4_clean, ratio_clean = compute_m4_m2_ratio(forms, all_minus_old_indices)
    print(f"  All minus oldforms: M4/M2^2 = {ratio_clean:.4f}" if ratio_clean else "  All minus oldforms: insufficient data")

    # ── Feature distributions ──
    print("\nFeature distributions (composite level):")
    for feat_name in ["entropy", "near_zero_frac", "kurtosis", "phase_coherence"]:
        vals_new = [f[feat_name] for f in composite_feats if f["oldform_prob"] <= 0.5]
        vals_old = [f[feat_name] for f in composite_feats if f["oldform_prob"] > 0.5]
        if vals_new and vals_old:
            t_stat, p_val = sp_stats.ttest_ind(vals_new, vals_old)
            print(f"  {feat_name}: newform mean={np.mean(vals_new):.4f}, "
                  f"oldform mean={np.mean(vals_old):.4f}, t={t_stat:.2f}, p={p_val:.2e}")

    # ── Oldform probability distribution by level factorization ──
    print("\nOldform fraction by number of prime factors:")
    from collections import defaultdict
    by_omega = defaultdict(list)
    for f in composite_feats:
        omega = len(factorint(f["level"]))  # number of distinct prime factors
        by_omega[omega].append(f["oldform_prob"])
    for omega in sorted(by_omega):
        probs = by_omega[omega]
        frac = sum(1 for p in probs if p > 0.5) / len(probs)
        print(f"  omega={omega}: {sum(1 for p in probs if p > 0.5)}/{len(probs)} "
              f"oldform-like ({100*frac:.1f}%), mean P(old)={np.mean(probs):.3f}")

    # ── Build results ──
    # Top 20 most oldform-like
    top_oldforms = sorted(composite_feats, key=lambda f: f["oldform_prob"], reverse=True)[:20]

    results = {
        "challenge": "Maass Newform vs Oldform Coefficient Separation",
        "dataset": str(DATA),
        "n_forms": len(forms),
        "n_features_computed": len(features),
        "n_prime_level": prime_count,
        "n_composite_level": composite_count,
        "heuristic_oldforms": heuristic_oldforms,
        "heuristic_oldform_fraction": round(heuristic_oldforms / composite_count, 4) if composite_count > 0 else 0,
        "classifier": {
            "type": "RandomForest",
            "n_estimators": 200,
            "max_depth": 8,
            "cv_f1_mean": round(float(cv_scores.mean()), 4),
            "cv_f1_std": round(float(cv_scores.std()), 4),
            "feature_importances": {k: round(v, 4) for k, v in importances.items()},
        },
        "rf_predicted_oldforms": high_prob_oldforms,
        "rf_oldform_fraction_of_composite": round(high_prob_oldforms / composite_count, 4) if composite_count > 0 else 0,
        "m4_m2_squared": {
            "all_forms": round(ratio_all, 4) if ratio_all else None,
            "composite_level": round(ratio_comp, 4) if ratio_comp else None,
            "composite_newforms_only": round(ratio_new, 4) if ratio_new else None,
            "oldforms_only": round(ratio_old, 4) if ratio_old else None,
            "all_minus_oldforms": round(ratio_clean, 4) if ratio_clean else None,
            "delta_removing_oldforms": round(ratio_clean - ratio_all, 4) if (ratio_clean and ratio_all) else None,
        },
        "feature_distributions_composite": {},
        "oldform_by_omega": {},
        "top_20_oldform_like": [
            {
                "maass_id": f["maass_id"],
                "level": f["level"],
                "spectral_parameter": f["spectral_parameter"],
                "oldform_prob": round(f["oldform_prob"], 4),
                "entropy": round(f["entropy"], 4),
                "near_zero_frac": round(f["near_zero_frac"], 4),
                "kurtosis": round(f["kurtosis"], 4),
                "phase_coherence": round(f["phase_coherence"], 4),
            }
            for f in top_oldforms
        ],
    }

    # Feature distribution stats
    for feat_name in ["entropy", "near_zero_frac", "kurtosis", "phase_coherence"]:
        vals_new = [f[feat_name] for f in composite_feats if f["oldform_prob"] <= 0.5]
        vals_old = [f[feat_name] for f in composite_feats if f["oldform_prob"] > 0.5]
        if vals_new and vals_old:
            t_stat, p_val = sp_stats.ttest_ind(vals_new, vals_old)
            results["feature_distributions_composite"][feat_name] = {
                "newform_mean": round(float(np.mean(vals_new)), 4),
                "oldform_mean": round(float(np.mean(vals_old)), 4),
                "t_statistic": round(float(t_stat), 2),
                "p_value": float(f"{p_val:.2e}"),
            }

    for omega in sorted(by_omega):
        probs = by_omega[omega]
        results["oldform_by_omega"][str(omega)] = {
            "n_forms": len(probs),
            "n_oldform_like": sum(1 for p in probs if p > 0.5),
            "fraction": round(sum(1 for p in probs if p > 0.5) / len(probs), 4),
            "mean_prob": round(float(np.mean(probs)), 4),
        }

    # Verdict
    if ratio_clean and ratio_all:
        delta = ratio_clean - ratio_all
        if abs(delta) > 0.05:
            verdict = f"SIGNIFICANT: removing oldforms shifts M4/M2^2 by {delta:+.4f}"
        else:
            verdict = f"MARGINAL: removing oldforms shifts M4/M2^2 by only {delta:+.4f}"
    else:
        verdict = "INSUFFICIENT DATA for M4/M2^2 comparison"

    results["verdict"] = verdict
    print(f"\nVERDICT: {verdict}")

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_JSON}")


if __name__ == "__main__":
    main()
