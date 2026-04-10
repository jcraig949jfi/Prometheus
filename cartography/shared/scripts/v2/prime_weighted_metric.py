#!/usr/bin/env python3
"""
M9: Prime-Weighted Distance Metric from the Scaling Law
(ALL-045, ChatGPT Part 3 #2)

For each pair of forms, defines four distance metrics with different prime weightings
and evaluates which best recovers known mathematical structure (CM, Galois image,
twists, congruences).

Key question: does information-weighted d_info outperform uniform d_uniform?
"""

import json
import sys
import time
import numpy as np
from pathlib import Path
from collections import defaultdict

# ── Setup paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[3]
sys.path.insert(0, str(REPO_ROOT))

import duckdb

DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
ENTROPY_PATH = SCRIPT_DIR / "reconstruction_entropy_results.json"
SYMMETRY_PATH = SCRIPT_DIR / "symmetry_detection_results.json"
GALOIS_PATH = SCRIPT_DIR / "galois_image_results.json"
CONGRUENCE_PATH = SCRIPT_DIR / "congruence_graph.json"
OUTPUT_PATH = SCRIPT_DIR / "prime_weighted_metric_results.json"

# The 25 smallest primes (the fingerprint dimension from M5)
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
             53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

# Full list of 168 primes up to 997 (same order as ap_coeffs in DuckDB)
def sieve_primes(n):
    """Sieve of Eratosthenes."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(n + 1) if is_prime[i]]

PRIMES_168 = sieve_primes(997)
assert len(PRIMES_168) == 168

# Map prime -> index in PRIMES_168
PRIME_TO_IDX = {p: i for i, p in enumerate(PRIMES_168)}

N_SAMPLE = 2000
RNG = np.random.default_rng(42)


def load_forms():
    """Load weight-2, dim-1, trivial character forms from DuckDB."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute("""
        SELECT lmfdb_label, level, is_cm, sato_tate_group, ap_coeffs
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level, lmfdb_label
    """).fetchall()
    con.close()

    forms = []
    for label, level, is_cm, st_group, ap_json in rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        # ap is list of [a_p] for each of 168 primes
        ap_vals = [x[0] for x in ap]  # flatten single-element lists
        forms.append({
            'label': label,
            'level': level,
            'is_cm': bool(is_cm),
            'st_group': st_group,
            'ap': np.array(ap_vals, dtype=np.int64)
        })
    return forms


def load_galois_classes():
    """Load combined Galois image classification."""
    with open(GALOIS_PATH) as f:
        data = json.load(f)
    # Map label -> class
    label_to_class = {}
    # Use combined_classification distribution keys as reference
    # Need to reconstruct from per-ell data
    # Actually the R3-2 results don't have per-form labels directly
    # We'll use CM + Sato-Tate as proxy for Galois class
    return data


def load_twist_pairs():
    """Load twist pairs from CT4 symmetry detection."""
    with open(SYMMETRY_PATH) as f:
        data = json.load(f)
    pairs = []
    for p in data.get('quadratic_twists', {}).get('pairs', []):
        pairs.append((p['form_f'], p['form_g']))
    return pairs


def load_congruence_pairs():
    """Load congruence pairs from C07 congruence graph."""
    with open(CONGRUENCE_PATH) as f:
        data = json.load(f)
    pairs = []
    for ell_str, info in data.items():
        ell = int(ell_str)
        for cong in info.get('congruences', []):
            pairs.append((cong['form_a'], cong['form_b'], ell))
    return pairs


def load_entropy_info():
    """Load information gain per prime from M5."""
    with open(ENTROPY_PATH) as f:
        data = json.load(f)
    # single_prime_entropy has mod_3, mod_5, mod_7, mod_11
    info = {}
    for key, val in data['single_prime_entropy'].items():
        ell = int(key.split('_')[1])
        info[ell] = val['information_gain_bits']
    return info


def build_fingerprints(forms, ells):
    """
    Build fingerprint matrix: for each form, compute a_p mod ell for each
    of the 25 smallest primes, for each ell.

    Returns dict: ell -> (n_forms, 25) uint16 array of a_p mod ell
    """
    # Indices of the 25 primes in the 168-prime array
    idx_25 = [PRIME_TO_IDX[p] for p in PRIMES_25]

    n = len(forms)
    fingerprints = {}
    for ell in ells:
        fp = np.zeros((n, 25), dtype=np.int64)
        for i, f in enumerate(forms):
            fp[i] = f['ap'][idx_25] % ell
        fingerprints[ell] = fp
    return fingerprints


def compute_disagreement_matrices(fingerprints, ells):
    """
    For each ell, compute (n, n) matrix of FRACTION of 25 primes where
    forms disagree mod ell. This gives finer resolution than binary any/all.

    Also returns binary version for congruence checking.
    """
    n = fingerprints[ells[0]].shape[0]
    disagree_frac = {}
    disagree_binary = {}

    for ell in ells:
        fp = fingerprints[ell]  # (n, 25)
        d_frac = np.zeros((n, n), dtype=np.float32)
        d_bin = np.zeros((n, n), dtype=np.float32)
        chunk = 200
        for start in range(0, n, chunk):
            end = min(start + chunk, n)
            diff = fp[start:end, np.newaxis, :] != fp[np.newaxis, :, :]
            d_frac[start:end] = diff.mean(axis=2).astype(np.float32)
            d_bin[start:end] = diff.any(axis=2).astype(np.float32)
        disagree_frac[ell] = d_frac
        disagree_binary[ell] = d_bin

    return disagree_frac, disagree_binary


def compute_distance_matrices(disagree, ells, entropy_info, alpha_values):
    """
    Compute four distance matrices from the disagreement matrices.
    Returns dict of metric_name -> distance matrix.
    """
    n = disagree[ells[0]].shape[0]

    # Stack disagreement matrices: (n_ells, n, n)
    D_stack = np.stack([disagree[ell] for ell in ells], axis=0)

    # 1. d_uniform: equal weight
    d_uniform = D_stack.mean(axis=0)

    # 2. d_log: log(ell) weighted
    log_weights = np.array([np.log(ell) for ell in ells])
    log_weights_norm = log_weights / log_weights.sum()
    d_log = np.einsum('e,eij->ij', log_weights_norm, D_stack)

    # 3. d_info: information-weighted (from M5 entropy)
    # For ells not in entropy_info, interpolate/extrapolate
    # M5 has mod_3, mod_5, mod_7, mod_11
    # For other ells, use log interpolation: I(ell) ~ a * log(ell) + b
    known_ells = sorted(entropy_info.keys())
    known_info = [entropy_info[e] for e in known_ells]

    # Fit log model: I(ell) = a * log(ell) + b
    log_known = np.log(known_ells)
    coeffs = np.polyfit(log_known, known_info, 1)

    info_weights = np.array([
        entropy_info.get(ell, coeffs[0] * np.log(ell) + coeffs[1])
        for ell in ells
    ])
    # Clip to positive
    info_weights = np.maximum(info_weights, 0.01)
    info_weights_norm = info_weights / info_weights.sum()
    d_info = np.einsum('e,eij->ij', info_weights_norm, D_stack)

    # 4. d_power: ell^alpha weighted — scan alpha values
    d_power_dict = {}
    for alpha in alpha_values:
        power_weights = np.array([ell**alpha for ell in ells])
        power_weights_norm = power_weights / power_weights.sum()
        d_power_dict[alpha] = np.einsum('e,eij->ij', power_weights_norm, D_stack)

    results = {
        'd_uniform': d_uniform,
        'd_log': d_log,
        'd_info': d_info,
    }
    for alpha, d in d_power_dict.items():
        results[f'd_power_{alpha:.1f}'] = d

    return results, info_weights


def evaluate_cm_separation(dist_matrices, is_cm):
    """
    AUC for CM vs non-CM classification using distance-based approach.
    For each form, compute mean distance to CM forms vs mean distance to non-CM forms.
    Score = mean_dist_to_nonCM - mean_dist_to_CM (higher means CM cluster more tightly).
    Use this as a classifier score, compute AUC.
    """
    from sklearn.metrics import roc_auc_score

    cm_idx = np.where(is_cm)[0]
    noncm_idx = np.where(~is_cm)[0]

    if len(cm_idx) < 5:
        return {name: float('nan') for name in dist_matrices}

    results = {}
    for name, D in dist_matrices.items():
        # For each form, compute average distance to CM vs non-CM
        mean_to_cm = D[:, cm_idx].mean(axis=1)
        mean_to_noncm = D[:, noncm_idx].mean(axis=1)
        # Score: closer to CM -> more likely CM
        scores = mean_to_noncm - mean_to_cm
        try:
            auc = roc_auc_score(is_cm, scores)
        except Exception:
            auc = float('nan')
        results[name] = float(auc)
    return results


def evaluate_galois_silhouette(dist_matrices, class_labels):
    """Silhouette score for Galois image classes."""
    from sklearn.metrics import silhouette_score

    # Need at least 2 classes with 2+ members
    unique, counts = np.unique(class_labels, return_counts=True)
    valid = unique[counts >= 2]
    if len(valid) < 2:
        return {name: float('nan') for name in dist_matrices}

    # Filter to valid classes
    mask = np.isin(class_labels, valid)
    labels_f = class_labels[mask]

    results = {}
    for name, D in dist_matrices.items():
        D_f = D[np.ix_(mask, mask)]
        try:
            score = silhouette_score(D_f, labels_f, metric='precomputed')
        except Exception:
            score = float('nan')
        results[name] = float(score)
    return results


def evaluate_twist_recovery(dist_matrices, label_to_idx, twist_pairs):
    """
    For each twist pair in our sample, check what rank the partner has
    when sorted by distance.
    """
    results = {}
    valid_pairs = []
    for f, g in twist_pairs:
        if f in label_to_idx and g in label_to_idx:
            valid_pairs.append((label_to_idx[f], label_to_idx[g]))

    if not valid_pairs:
        return {name: {'n_pairs': 0} for name in dist_matrices}

    for name, D in dist_matrices.items():
        ranks = []
        distances = []
        for i, j in valid_pairs:
            # Rank of j among all forms sorted by distance from i
            dists = D[i]
            rank = (dists < dists[j]).sum()  # how many are closer
            ranks.append(int(rank))
            distances.append(float(dists[j]))

        results[name] = {
            'n_pairs': len(valid_pairs),
            'mean_rank': float(np.mean(ranks)),
            'median_rank': float(np.median(ranks)),
            'mean_distance': float(np.mean(distances)),
            'pct_in_top10': float(np.mean([r < 10 for r in ranks])),
            'pct_at_rank0': float(np.mean([r == 0 for r in ranks])),
        }
    return results


def evaluate_congruence_recovery(dist_matrices, label_to_idx, congruence_pairs):
    """
    For congruence pairs, check if they have distance 0 or near-0.
    """
    results = {}
    valid_pairs = []
    for f, g, ell in congruence_pairs:
        if f in label_to_idx and g in label_to_idx:
            valid_pairs.append((label_to_idx[f], label_to_idx[g], ell))

    if not valid_pairs:
        return {name: {'n_pairs': 0} for name in dist_matrices}

    for name, D in dist_matrices.items():
        distances = []
        zero_count = 0
        for i, j, ell in valid_pairs:
            d = float(D[i, j])
            distances.append(d)
            if d < 1e-10:
                zero_count += 1

        results[name] = {
            'n_pairs': len(valid_pairs),
            'n_at_zero': zero_count,
            'pct_at_zero': float(zero_count / len(valid_pairs)),
            'mean_distance': float(np.mean(distances)),
            'median_distance': float(np.median(distances)),
            'min_distance': float(np.min(distances)),
            'max_distance': float(np.max(distances)),
        }
    return results


def check_triangle_inequality(D, n_triples=10000):
    """Sample triples and check triangle inequality."""
    n = D.shape[0]
    rng = np.random.default_rng(123)

    # Sample random triples
    idx = rng.integers(0, n, size=(n_triples, 3))
    i, j, k = idx[:, 0], idx[:, 1], idx[:, 2]

    d_ij = D[i, j]
    d_jk = D[j, k]
    d_ik = D[i, k]

    # Triangle inequality: d(i,k) <= d(i,j) + d(j,k)
    violations = (d_ik > d_ij + d_jk + 1e-10).sum()
    max_violation = float(np.max(d_ik - d_ij - d_jk))

    return {
        'n_triples': n_triples,
        'n_violations': int(violations),
        'pct_violations': float(violations / n_triples),
        'max_violation': max_violation,
        'is_metric': violations == 0,
    }


def compute_geometry(D):
    """Compute basic geometric properties."""
    # Diameter
    diameter = float(D.max())

    # Mean distance
    # Upper triangle only (excluding diagonal)
    n = D.shape[0]
    iu = np.triu_indices(n, k=1)
    upper = D[iu]
    mean_dist = float(upper.mean())
    std_dist = float(upper.std())

    # Natural clusters via simple k-means on distance matrix
    # Use spectral embedding first, then k-means
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.manifold import MDS

    # MDS embedding to 10D for clustering
    # Use a subset for speed
    n_embed = min(n, 1000)
    idx = np.arange(n_embed)

    # Try DBSCAN on the distance matrix directly
    dbscan_results = {}
    for eps in [0.1, 0.2, 0.3, 0.5]:
        db = DBSCAN(eps=eps, min_samples=5, metric='precomputed')
        labels = db.fit_predict(D[:n_embed, :n_embed])
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = (labels == -1).sum()
        dbscan_results[f'eps_{eps}'] = {
            'n_clusters': int(n_clusters),
            'n_noise': int(n_noise),
            'pct_noise': float(n_noise / n_embed),
        }

    return {
        'diameter': diameter,
        'mean_distance': mean_dist,
        'std_distance': std_dist,
        'dbscan': dbscan_results,
    }


def classify_galois_image_from_ap(ap_vals, is_cm, primes=None):
    """
    Classify Galois image from a_p data using zero-frequency heuristics.

    For dim=1 weight=2 newforms over Q at each small ell:
    - Borel (rational isogeny): a_p ≡ 0 (mod ell) for ~1/2 of good primes at ell=2
    - CM/Cartan: a_p = 0 for ~1/2 of primes (inert primes)
    - Full GL_2: a_p mod ell roughly uniform

    We use the 168 primes in ap_vals and classify by zero-frequency at each ell.
    """
    if primes is None:
        primes = sieve_primes(997)

    if is_cm:
        return 'CM'

    # Check mod-2: if ALL a_p are even -> borel_isogeny (2-isogeny)
    ap = np.array(ap_vals)
    mod2_zeros = (ap % 2 == 0)

    # Exclude bad primes (typically first few where level divides p)
    # Use primes beyond index 5 for stability
    good_slice = slice(5, None)
    n_good = len(ap[good_slice])

    frac_even = mod2_zeros[good_slice].mean()
    if frac_even > 0.95:
        return 'borel_isogeny'

    # Check mod-3: Borel means a_p concentrates on QR classes
    mod3 = ap[good_slice] % 3
    frac_zero_mod3 = (mod3 == 0).mean()
    if frac_zero_mod3 > 0.45:  # Borel mod-3 threshold
        return 'borel_mod3'

    # Check mod-5: similar
    mod5 = ap[good_slice] % 5
    frac_zero_mod5 = (mod5 == 0).mean()
    if frac_zero_mod5 > 0.35:
        return 'borel_mod5'

    # Check if borel_mod2 (a_p even more often than full but not all)
    if frac_even > 0.55:
        return 'borel_mod2'

    return 'full_image'


def main():
    t0 = time.time()
    print("M9: Prime-Weighted Distance Metric")
    print("=" * 60)

    # ── Load data ────────────────────────────────────────────────
    print("Loading forms from DuckDB...")
    all_forms = load_forms()
    print(f"  Loaded {len(all_forms)} forms")

    print("Loading twist pairs...")
    twist_pairs = load_twist_pairs()
    print(f"  {len(twist_pairs)} twist pairs")

    print("Loading congruence pairs...")
    congruence_pairs = load_congruence_pairs()
    print(f"  {len(congruence_pairs)} congruence pairs")

    print("Loading entropy info...")
    entropy_info = load_entropy_info()
    print(f"  Info bits: {entropy_info}")

    # ── Sample 2000 forms ────────────────────────────────────────
    # Strategic sampling: ensure we get CM forms, twist pairs, congruence pairs
    print("\nSampling 2000 forms (stratified)...")

    label_set = {f['label'] for f in all_forms}
    label_to_form_idx = {f['label']: i for i, f in enumerate(all_forms)}

    # Must-include: CM forms
    must_include = set()
    for i, f in enumerate(all_forms):
        if f['is_cm']:
            must_include.add(i)

    # Must-include: twist pair members
    for a, b in twist_pairs:
        if a in label_to_form_idx:
            must_include.add(label_to_form_idx[a])
        if b in label_to_form_idx:
            must_include.add(label_to_form_idx[b])

    # Must-include: congruence pair members
    for a, b, ell in congruence_pairs:
        if a in label_to_form_idx:
            must_include.add(label_to_form_idx[a])
        if b in label_to_form_idx:
            must_include.add(label_to_form_idx[b])

    must_include = list(must_include)
    print(f"  Must-include: {len(must_include)} forms (CM + twist + congruence)")

    # Fill remaining with random
    remaining = list(set(range(len(all_forms))) - set(must_include))
    n_random = max(0, N_SAMPLE - len(must_include))
    if n_random > 0 and len(remaining) > 0:
        random_idx = RNG.choice(remaining, size=min(n_random, len(remaining)), replace=False)
        sample_idx = np.concatenate([must_include, random_idx])
    else:
        sample_idx = np.array(must_include[:N_SAMPLE])

    sample_idx = sample_idx[:N_SAMPLE].astype(int)
    np.sort(sample_idx)

    sample_forms = [all_forms[i] for i in sample_idx]
    n = len(sample_forms)
    print(f"  Final sample: {n} forms")

    # Build label -> sample index mapping
    label_to_sidx = {f['label']: i for i, f in enumerate(sample_forms)}

    # ── Fingerprints and disagreement ────────────────────────────
    # Use ells = [3, 5, 7, 11] (the ones M5 measured)
    ells = [3, 5, 7, 11]

    print(f"\nBuilding fingerprints for ells={ells}, 25 primes each...")
    fingerprints = build_fingerprints(sample_forms, ells)

    print("Computing disagreement matrices (vectorized, fractional)...")
    disagree, disagree_binary = compute_disagreement_matrices(fingerprints, ells)

    # ── Distance matrices ────────────────────────────────────────
    alpha_values = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

    print("Computing distance matrices...")
    dist_matrices, info_weights = compute_distance_matrices(
        disagree, ells, entropy_info, alpha_values
    )
    print(f"  {len(dist_matrices)} distance matrices computed")
    print(f"  Info weights: {dict(zip(ells, info_weights))}")

    # ── Evaluation ───────────────────────────────────────────────
    print("\n--- Evaluation ---")

    # 1. CM separation (AUC)
    is_cm = np.array([f['is_cm'] for f in sample_forms])
    print(f"\n1. CM separation (n_cm={is_cm.sum()}, n_noncm={(~is_cm).sum()})...")
    cm_auc = evaluate_cm_separation(dist_matrices, is_cm)
    for name, auc in sorted(cm_auc.items(), key=lambda x: -x[1] if not np.isnan(x[1]) else -999):
        print(f"   {name:20s}: AUC = {auc:.4f}")

    # 2. Galois image silhouette
    # Classify from a_p data (richer than Sato-Tate which is same for all non-CM)
    class_labels = np.array([
        classify_galois_image_from_ap(f['ap'], f['is_cm']) for f in sample_forms
    ])
    unique_classes = np.unique(class_labels)
    print(f"\n2. Galois image clustering ({len(unique_classes)} classes)...")
    # Limit to top classes (by count) for meaningful silhouette
    class_counts = defaultdict(int)
    for c in class_labels:
        class_counts[c] += 1
    top_classes = sorted(class_counts.keys(), key=lambda x: -class_counts[x])[:10]
    print(f"   Top classes: {[(c, class_counts[c]) for c in top_classes[:5]]}")

    galois_sil = evaluate_galois_silhouette(dist_matrices, class_labels)
    for name, sil in sorted(galois_sil.items(), key=lambda x: -x[1] if not np.isnan(x[1]) else -999):
        print(f"   {name:20s}: silhouette = {sil:.4f}")

    # 3. Twist recovery
    print(f"\n3. Twist pair recovery...")
    twist_recovery = evaluate_twist_recovery(dist_matrices, label_to_sidx, twist_pairs)
    for name in ['d_uniform', 'd_log', 'd_info', 'd_power_1.0', 'd_power_2.0', 'd_power_5.0']:
        if name in twist_recovery:
            tr = twist_recovery[name]
            if tr['n_pairs'] > 0:
                print(f"   {name:20s}: mean_rank={tr['mean_rank']:.1f}, "
                      f"mean_dist={tr['mean_distance']:.4f}, "
                      f"top10={tr['pct_in_top10']:.1%}")

    # 4. Congruence recovery
    print(f"\n4. Congruence pair recovery...")
    cong_recovery = evaluate_congruence_recovery(dist_matrices, label_to_sidx, congruence_pairs)
    for name in ['d_uniform', 'd_log', 'd_info', 'd_power_1.0', 'd_power_2.0', 'd_power_5.0']:
        if name in cong_recovery:
            cr = cong_recovery[name]
            if cr['n_pairs'] > 0:
                print(f"   {name:20s}: at_zero={cr['n_at_zero']}/{cr['n_pairs']} "
                      f"({cr['pct_at_zero']:.1%}), mean_dist={cr['mean_distance']:.4f}")

    # ── Optimize alpha ───────────────────────────────────────────
    print("\n--- Alpha Optimization ---")
    alpha_scores = {}
    for alpha in alpha_values:
        name = f'd_power_{alpha:.1f}'
        if name in cm_auc and name in galois_sil:
            # Composite score: AUC + silhouette (both should be maximized)
            score = cm_auc[name] + galois_sil[name]
            alpha_scores[alpha] = {
                'auc': cm_auc[name],
                'silhouette': galois_sil[name],
                'composite': score,
            }
            print(f"  alpha={alpha:.1f}: AUC={cm_auc[name]:.4f}, "
                  f"sil={galois_sil[name]:.4f}, composite={score:.4f}")

    best_alpha = max(alpha_scores, key=lambda a: alpha_scores[a]['composite'])
    print(f"\n  Best alpha: {best_alpha:.1f}")

    # ── Geometry of best metric ──────────────────────────────────
    # Determine best overall metric
    all_metrics = ['d_uniform', 'd_log', 'd_info', f'd_power_{best_alpha:.1f}']
    metric_scores = {}
    for name in all_metrics:
        auc = cm_auc.get(name, 0)
        sil = galois_sil.get(name, 0)
        if np.isnan(auc): auc = 0
        if np.isnan(sil): sil = 0
        metric_scores[name] = auc + sil

    best_metric_name = max(metric_scores, key=metric_scores.get)
    best_D = dist_matrices[best_metric_name]

    print(f"\n--- Geometry of best metric: {best_metric_name} ---")

    # Triangle inequality
    print("Checking triangle inequality (10,000 triples)...")
    tri = check_triangle_inequality(best_D)
    print(f"  Violations: {tri['n_violations']}/{tri['n_triples']} "
          f"({tri['pct_violations']:.2%})")
    print(f"  Max violation: {tri['max_violation']:.6f}")
    print(f"  Is metric: {tri['is_metric']}")

    # Geometry
    print("Computing geometry...")
    geom = compute_geometry(best_D)
    print(f"  Diameter: {geom['diameter']:.4f}")
    print(f"  Mean distance: {geom['mean_distance']:.4f} +/- {geom['std_distance']:.4f}")
    print(f"  DBSCAN clusters:")
    for eps_key, info in geom['dbscan'].items():
        print(f"    {eps_key}: {info['n_clusters']} clusters, "
              f"{info['pct_noise']:.1%} noise")

    # Also check geometry for d_uniform for comparison
    print(f"\n--- Geometry of d_uniform (for comparison) ---")
    tri_uniform = check_triangle_inequality(dist_matrices['d_uniform'])
    print(f"  Triangle violations: {tri_uniform['n_violations']}")
    geom_uniform = compute_geometry(dist_matrices['d_uniform'])
    print(f"  Diameter: {geom_uniform['diameter']:.4f}")
    print(f"  Mean distance: {geom_uniform['mean_distance']:.4f}")

    # ── Per-ell congruence analysis ────────────────────────────────
    print("\n--- Per-ell congruence distance (sanity check) ---")
    per_ell_cong = {}
    for ell in ells:
        D_ell = disagree_binary[ell]  # single-ell binary disagreement
        ell_cong_pairs = [(label_to_sidx[a], label_to_sidx[b])
                          for a, b, e in congruence_pairs
                          if e == ell and a in label_to_sidx and b in label_to_sidx]
        if ell_cong_pairs:
            dists = [float(D_ell[i, j]) for i, j in ell_cong_pairs]
            n_zero = sum(1 for d in dists if d < 1e-10)
            per_ell_cong[ell] = {
                'n_pairs': len(ell_cong_pairs),
                'n_agree_all25': n_zero,
                'pct_agree': float(n_zero / len(ell_cong_pairs)),
                'mean_disagree': float(np.mean(dists)),
            }
            print(f"  ell={ell}: {n_zero}/{len(ell_cong_pairs)} agree on all 25 primes, "
                  f"mean_disagree={np.mean(dists):.4f}")

    # ── Key question ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("KEY QUESTION: Does d_info outperform d_uniform?")
    info_auc = cm_auc.get('d_info', float('nan'))
    unif_auc = cm_auc.get('d_uniform', float('nan'))
    info_sil = galois_sil.get('d_info', float('nan'))
    unif_sil = galois_sil.get('d_uniform', float('nan'))

    print(f"  CM AUC:     d_info={info_auc:.4f}  vs  d_uniform={unif_auc:.4f}  "
          f"delta={info_auc - unif_auc:+.4f}")
    print(f"  Silhouette: d_info={info_sil:.4f}  vs  d_uniform={unif_sil:.4f}  "
          f"delta={info_sil - unif_sil:+.4f}")

    # Also compare twist and congruence recovery
    info_twist = twist_recovery.get('d_info', {}).get('mean_rank', float('inf'))
    unif_twist = twist_recovery.get('d_uniform', {}).get('mean_rank', float('inf'))
    info_cong = cong_recovery.get('d_info', {}).get('mean_distance', float('inf'))
    unif_cong = cong_recovery.get('d_uniform', {}).get('mean_distance', float('inf'))
    print(f"  Twist rank: d_info={info_twist:.1f}  vs  d_uniform={unif_twist:.1f}")
    print(f"  Cong dist:  d_info={info_cong:.4f}  vs  d_uniform={unif_cong:.4f}  "
          f"delta={info_cong - unif_cong:+.4f}")

    # Count wins across 4 criteria (lower twist rank, higher AUC, higher sil, lower cong dist)
    info_wins = 0
    info_wins += (info_auc > unif_auc + 1e-6)
    info_wins += (info_sil > unif_sil + 1e-6)
    info_wins += (info_twist < unif_twist - 0.01)
    info_wins += (info_cong < unif_cong - 1e-4)

    if info_wins >= 3:
        verdict = "YES — information weighting clearly improves classification"
    elif info_wins >= 1:
        verdict = ("MARGINAL — information weighting shows small improvements on some metrics "
                   f"({info_wins}/4 criteria)")
    else:
        verdict = "NO — uniform weighting is already optimal (or indistinguishable)"
    print(f"  VERDICT: {verdict}")

    # ── Save results ─────────────────────────────────────────────
    elapsed = time.time() - t0

    # Build comparison table
    comparison = {}
    for name in dist_matrices:
        entry = {
            'cm_auc': cm_auc.get(name, None),
            'galois_silhouette': galois_sil.get(name, None),
        }
        if name in twist_recovery:
            entry['twist_mean_rank'] = twist_recovery[name].get('mean_rank', None)
            entry['twist_pct_top10'] = twist_recovery[name].get('pct_in_top10', None)
        if name in cong_recovery:
            entry['congruence_pct_zero'] = cong_recovery[name].get('pct_at_zero', None)
            entry['congruence_mean_dist'] = cong_recovery[name].get('mean_distance', None)
        comparison[name] = entry

    output = {
        'metadata': {
            'challenge': 'M9',
            'description': 'Prime-weighted distance metric from scaling law',
            'n_forms_total': len(all_forms),
            'n_sample': n,
            'n_cm_in_sample': int(is_cm.sum()),
            'ells_used': ells,
            'primes_per_ell': 25,
            'n_twist_pairs_in_sample': twist_recovery.get('d_uniform', {}).get('n_pairs', 0),
            'n_congruence_pairs_in_sample': cong_recovery.get('d_uniform', {}).get('n_pairs', 0),
            'alpha_values_scanned': alpha_values,
            'info_weights': {str(ell): float(w) for ell, w in zip(ells, info_weights)},
            'elapsed_seconds': round(elapsed, 1),
        },
        'metric_comparison': comparison,
        'alpha_optimization': {
            'scores': {str(a): s for a, s in alpha_scores.items()},
            'best_alpha': best_alpha,
        },
        'key_question': {
            'info_vs_uniform': {
                'cm_auc_info': float(info_auc),
                'cm_auc_uniform': float(unif_auc),
                'cm_auc_delta': float(info_auc - unif_auc),
                'silhouette_info': float(info_sil),
                'silhouette_uniform': float(unif_sil),
                'silhouette_delta': float(info_sil - unif_sil),
                'twist_rank_info': float(info_twist),
                'twist_rank_uniform': float(unif_twist),
                'congruence_dist_info': float(info_cong),
                'congruence_dist_uniform': float(unif_cong),
                'congruence_dist_delta': float(info_cong - unif_cong),
                'wins_out_of_4': int(info_wins),
                'verdict': verdict,
            }
        },
        'geometry': {
            'best_metric': best_metric_name,
            'triangle_inequality': tri,
            'diameter': geom['diameter'],
            'mean_distance': geom['mean_distance'],
            'std_distance': geom['std_distance'],
            'dbscan_clusters': geom['dbscan'],
        },
        'geometry_uniform': {
            'triangle_inequality': tri_uniform,
            'diameter': geom_uniform['diameter'],
            'mean_distance': geom_uniform['mean_distance'],
        },
        'twist_recovery': {k: v for k, v in twist_recovery.items()
                          if k in ['d_uniform', 'd_log', 'd_info', f'd_power_{best_alpha:.1f}']},
        'congruence_recovery': {k: v for k, v in cong_recovery.items()
                               if k in ['d_uniform', 'd_log', 'd_info', f'd_power_{best_alpha:.1f}']},
        'per_ell_congruence': per_ell_cong,
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {OUTPUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == '__main__':
    main()
