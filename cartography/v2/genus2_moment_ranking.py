#!/usr/bin/env python3
"""
Genus-2 Sato-Tate Moment Ranking: Which individual moments best separate ST groups?

Starting from the 98.3% classification accuracy with 20-dim moment vectors,
this script identifies which individual moments carry the most discriminative
power for genus-2 Sato-Tate group classification.

Approach:
1. Join LMFDB equation data with ST group labels via (conductor, discriminant)
2. Sample curves with oversampling of rare ST groups
3. Compute trace of Frobenius a_p at good primes p <= PRIME_BOUND
4. Compute moments M_k = mean(a_p^k / p^{k/2}) for k=1..10
5. 1-NN classification with leave-one-out CV for each individual moment
6. Greedy forward selection to find minimal moment subsets
7. Compare to full moment vector accuracy

Output: genus2_moment_ranking_results.json
"""

import json
import math
import os
import sys
import time
import numpy as np
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
LMFDB_PATH = os.path.join(os.path.dirname(__file__), '..', 'genus2', 'data', 'genus2_curves_lmfdb.json')
FULL_PATH = os.path.join(os.path.dirname(__file__), '..', 'genus2', 'data', 'genus2_curves_full.json')
RESULTS_PATH = os.path.join(os.path.dirname(__file__), 'genus2_moment_ranking_results.json')

MAX_SAMPLE = 2000       # total curves to use
PRIME_BOUND = 199       # compute traces at primes up to this
MAX_MOMENTS = 10        # M_1 through M_10
MIN_GROUP_SIZE = 3      # minimum curves per ST group to include in classification


# ---------------------------------------------------------------------------
# Primes
# ---------------------------------------------------------------------------
def sieve_primes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

ALL_PRIMES = sieve_primes(PRIME_BOUND)
print(f"Using {len(ALL_PRIMES)} primes up to {PRIME_BOUND}")


# ---------------------------------------------------------------------------
# Data loading and joining
# ---------------------------------------------------------------------------
def load_and_join():
    """Join LMFDB (equations) with full data (ST groups) via (conductor, discriminant)."""
    print("Loading data files...")
    with open(LMFDB_PATH) as f:
        lmfdb_data = json.load(f)
    with open(FULL_PATH) as f:
        full_data = json.load(f)

    lmfdb_records = lmfdb_data['records']
    print(f"  LMFDB records: {len(lmfdb_records)}")
    print(f"  Full records: {len(full_data)}")

    # Index full data by (conductor, discriminant)
    full_by_cd = defaultdict(list)
    for r in full_data:
        full_by_cd[(r['conductor'], r['discriminant'])].append(r)

    # Parse discriminant from LMFDB label: N.iso.D.i
    def parse_disc(label):
        parts = label.split('.')
        return int(parts[2]) if len(parts) >= 3 else None

    # Join
    result = []
    for r in lmfdb_records:
        disc = parse_disc(r['label'])
        if disc is None:
            continue
        matches = full_by_cd.get((r['conductor'], disc), [])
        if len(matches) >= 1:
            st_groups = set(m['st_group'] for m in matches)
            if len(st_groups) == 1:
                new_r = dict(r)
                new_r['st_group'] = matches[0]['st_group']
                result.append(new_r)

    print(f"  Joined: {len(result)} curves with both equation and ST group")
    return result


def sample_curves(curves, max_total):
    """Sample curves with oversampling of rare ST groups."""
    by_st = defaultdict(list)
    for c in curves:
        by_st[c['st_group']].append(c)

    # Filter groups with minimum size
    valid_groups = {g: cs for g, cs in by_st.items() if len(cs) >= MIN_GROUP_SIZE}
    print(f"\n  ST groups with >= {MIN_GROUP_SIZE} curves: {len(valid_groups)}")
    for g in sorted(valid_groups, key=lambda x: -len(valid_groups[x])):
        print(f"    {g}: {len(valid_groups[g])}")

    selected = []

    # First: take ALL curves from rare groups (< 50 curves)
    for g, cs in sorted(valid_groups.items(), key=lambda x: len(x[1])):
        if len(cs) <= 50:
            selected.extend(cs)

    # Fill remaining budget from larger groups proportionally
    remaining = max_total - len(selected)
    if remaining > 0:
        large = [(g, cs) for g, cs in valid_groups.items() if len(cs) > 50]
        total_large = sum(len(cs) for _, cs in large)
        for g, cs in large:
            n_take = max(10, int(remaining * len(cs) / total_large))
            step = max(1, len(cs) // n_take)
            selected.extend(cs[::step][:n_take])

    # Deduplicate by label
    seen = set()
    unique = []
    for c in selected:
        if c['label'] not in seen:
            seen.add(c['label'])
            unique.append(c)

    print(f"\n  Selected {len(unique)} curves")
    st_counts = Counter(c['st_group'] for c in unique)
    for g, cnt in sorted(st_counts.items(), key=lambda x: -x[1]):
        print(f"    {g}: {cnt}")

    return unique


# ---------------------------------------------------------------------------
# Point counting and trace computation
# ---------------------------------------------------------------------------
def count_points_mod_p(f_coeffs, h_coeffs, p):
    """Count #C(F_p) for y^2 + h(x)*y = f(x) over F_p."""
    count = 0

    for x in range(p):
        fx = 0
        xpow = 1
        for c in f_coeffs:
            fx = (fx + c * xpow) % p
            xpow = (xpow * x) % p

        hx = 0
        xpow = 1
        for c in h_coeffs:
            hx = (hx + c * xpow) % p
            xpow = (xpow * x) % p

        # y^2 + hx*y - fx = 0  =>  discriminant = hx^2 + 4*fx
        disc = (hx * hx + 4 * fx) % p
        if disc == 0:
            count += 1
        elif pow(disc, (p - 1) // 2, p) == 1:
            count += 2

    # Points at infinity
    deg_f = len(f_coeffs) - 1
    while deg_f > 0 and f_coeffs[deg_f] % p == 0:
        deg_f -= 1

    if deg_f == 6:
        lc = f_coeffs[-1] % p
        if all(c == 0 for c in h_coeffs):
            if lc == 0:
                count += 1
            elif pow(lc, (p - 1) // 2, p) == 1:
                count += 2
        else:
            count += 2  # generic case with h != 0
    elif deg_f == 5:
        count += 1

    return count


def parse_equation(eq):
    """Parse LMFDB equation [[f_coeffs], [h_coeffs]]."""
    if isinstance(eq, str):
        import ast
        eq = ast.literal_eval(eq)
    f_coeffs = [int(c) for c in eq[0]]
    h_coeffs = [int(c) for c in eq[1]] if len(eq) > 1 and eq[1] else []
    return f_coeffs, h_coeffs


def compute_trace(f_coeffs, h_coeffs, p):
    """Trace of Frobenius: a_p = p + 1 - #C(F_p)."""
    n = count_points_mod_p(f_coeffs, h_coeffs, p)
    return p + 1 - n


def is_bad_prime(conductor, p):
    """A prime p is bad if it divides the conductor."""
    return conductor % p == 0


# ---------------------------------------------------------------------------
# Moment computation
# ---------------------------------------------------------------------------
def compute_moments(curves, primes, max_k=10):
    """
    For each curve, compute M_k = mean over good primes of (a_p / p^{1/2})^k
    for k = 1..max_k.

    Returns: numpy array of shape (n_curves, max_k), list of st_groups, list of labels
    """
    n = len(curves)
    moments = np.zeros((n, max_k))
    st_groups = []
    labels = []

    t0 = time.time()
    for i, curve in enumerate(curves):
        if (i + 1) % 100 == 0 or i == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / max(elapsed, 0.01)
            eta = (n - i - 1) / max(rate, 0.01)
            print(f"  Computing traces: {i+1}/{n} ({rate:.1f} curves/s, ETA {eta:.0f}s)")

        f_coeffs, h_coeffs = parse_equation(curve['equation'])
        cond = curve['conductor']

        # Collect normalized traces at good primes
        norm_traces = []
        for p in primes:
            if is_bad_prime(cond, p):
                continue
            a_p = compute_trace(f_coeffs, h_coeffs, p)
            norm_traces.append(a_p / math.sqrt(p))

        if len(norm_traces) < 5:
            # Too few good primes; fill with NaN
            moments[i, :] = np.nan
        else:
            arr = np.array(norm_traces)
            for k in range(max_k):
                moments[i, k] = np.mean(arr ** (k + 1))

        st_groups.append(curve['st_group'])
        labels.append(curve['label'])

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s")

    return moments, st_groups, labels


# ---------------------------------------------------------------------------
# Classification: 1-NN with leave-one-out CV
# ---------------------------------------------------------------------------
def loo_1nn_accuracy(features, labels_arr):
    """
    Leave-one-out 1-NN classification accuracy.
    features: (n, d) numpy array
    labels_arr: (n,) numpy array of integer labels
    Returns: accuracy (float)
    """
    n = len(features)
    correct = 0

    # Precompute pairwise distances
    # For efficiency, compute full distance matrix
    if features.ndim == 1:
        features = features.reshape(-1, 1)

    # Use broadcasting for distance computation
    # D[i,j] = ||x_i - x_j||^2
    sq = np.sum(features ** 2, axis=1)
    D = sq[:, None] + sq[None, :] - 2 * features @ features.T

    # Set diagonal to inf so a point doesn't match itself
    np.fill_diagonal(D, np.inf)

    # Find nearest neighbor for each point
    nn_idx = np.argmin(D, axis=1)
    predictions = labels_arr[nn_idx]
    accuracy = np.mean(predictions == labels_arr)

    return accuracy


def compute_individual_moment_aris(moments, st_groups):
    """Compute LOO 1-NN accuracy for each individual moment."""
    # Encode ST groups as integers
    unique_groups = sorted(set(st_groups))
    group_to_idx = {g: i for i, g in enumerate(unique_groups)}
    labels_arr = np.array([group_to_idx[g] for g in st_groups])

    results = {}
    for k in range(moments.shape[1]):
        feat = moments[:, k:k+1]
        # Skip if any NaN
        valid = ~np.isnan(feat).any(axis=1)
        if valid.sum() < 10:
            results[k+1] = {'accuracy': 0.0, 'n_valid': int(valid.sum())}
            continue

        acc = loo_1nn_accuracy(feat[valid], labels_arr[valid])
        results[k+1] = {
            'accuracy': float(acc),
            'n_valid': int(valid.sum()),
        }
        print(f"  M_{k+1}: accuracy = {acc:.4f} ({valid.sum()} curves)")

    return results, labels_arr, unique_groups


def greedy_forward_selection(moments, labels_arr, max_features=None):
    """
    Greedy forward selection: at each step, add the moment that gives
    the biggest accuracy boost.
    """
    if max_features is None:
        max_features = moments.shape[1]

    valid = ~np.isnan(moments).any(axis=1)
    M = moments[valid]
    L = labels_arr[valid]

    n_features = M.shape[1]
    selected = []
    remaining = list(range(n_features))
    history = []

    for step in range(min(max_features, n_features)):
        best_acc = -1
        best_feat = None

        for feat_idx in remaining:
            trial = selected + [feat_idx]
            feat_subset = M[:, trial]
            acc = loo_1nn_accuracy(feat_subset, L)
            if acc > best_acc:
                best_acc = acc
                best_feat = feat_idx

        selected.append(best_feat)
        remaining.remove(best_feat)
        history.append({
            'step': step + 1,
            'added_moment': f'M_{best_feat + 1}',
            'moment_index': best_feat + 1,
            'selected_moments': [f'M_{s+1}' for s in selected],
            'accuracy': float(best_acc),
            'n_curves': int(len(L)),
        })
        print(f"  Step {step+1}: add M_{best_feat+1} -> accuracy = {best_acc:.4f}")

        # Early stopping if perfect
        if best_acc >= 0.999:
            print(f"  Reached near-perfect accuracy at step {step+1}, stopping.")
            break

    return history


def compute_full_accuracy(moments, labels_arr):
    """Compute LOO 1-NN with all moments."""
    valid = ~np.isnan(moments).any(axis=1)
    M = moments[valid]
    L = labels_arr[valid]
    acc = loo_1nn_accuracy(M, L)
    return float(acc), int(valid.sum())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("Genus-2 Sato-Tate Moment Ranking")
    print("=" * 70)

    # 1. Load and join data
    curves = load_and_join()

    # 2. Sample
    sampled = sample_curves(curves, MAX_SAMPLE)

    # 3. Compute moments
    print(f"\nComputing moments M_1..M_{MAX_MOMENTS} at {len(ALL_PRIMES)} primes...")
    moments, st_groups, labels = compute_moments(sampled, ALL_PRIMES, MAX_MOMENTS)

    # Filter out curves with NaN moments
    valid_mask = ~np.isnan(moments).any(axis=1)
    print(f"\nValid curves (no NaN): {valid_mask.sum()} / {len(moments)}")

    # 4. Individual moment ranking
    print("\n--- Individual Moment Accuracy (LOO 1-NN) ---")
    individual_results, labels_arr, unique_groups = compute_individual_moment_aris(moments, st_groups)

    # Rank by accuracy
    ranked = sorted(individual_results.items(), key=lambda x: -x[1]['accuracy'])
    print("\n  Ranking:")
    for rank, (k, res) in enumerate(ranked, 1):
        print(f"    #{rank}: M_{k} = {res['accuracy']:.4f}")

    # 5. Greedy forward selection
    print("\n--- Greedy Forward Selection ---")
    greedy_history = greedy_forward_selection(moments, labels_arr)

    # 6. Full moment accuracy
    print("\n--- Full Moment Vector (all 10) ---")
    full_acc, full_n = compute_full_accuracy(moments, labels_arr)
    print(f"  Full 10-moment accuracy: {full_acc:.4f} ({full_n} curves)")

    # Find saturation point (where adding moments gives < 0.5% improvement)
    saturation_point = len(greedy_history)
    for i in range(1, len(greedy_history)):
        improvement = greedy_history[i]['accuracy'] - greedy_history[i-1]['accuracy']
        if improvement < 0.005:
            saturation_point = i  # i-th step (0-indexed), so i moments needed
            break

    # 7. Per-group analysis: which groups are hardest to classify?
    print("\n--- Per-Group Analysis ---")
    valid = ~np.isnan(moments).any(axis=1)
    M_valid = moments[valid]
    L_valid = labels_arr[valid]

    # Use the best 2-moment pair from greedy selection
    if len(greedy_history) >= 2:
        best_pair_indices = [h['moment_index'] - 1 for h in greedy_history[:2]]
        feat_pair = M_valid[:, best_pair_indices]
        sq = np.sum(feat_pair ** 2, axis=1)
        D = sq[:, None] + sq[None, :] - 2 * feat_pair @ feat_pair.T
        np.fill_diagonal(D, np.inf)
        nn_idx = np.argmin(D, axis=1)
        predictions = L_valid[nn_idx]

        group_accuracy = {}
        for g_idx, g_name in enumerate(unique_groups):
            mask = L_valid == g_idx
            if mask.sum() == 0:
                continue
            g_acc = np.mean(predictions[mask] == g_idx)
            group_accuracy[g_name] = {
                'accuracy': float(g_acc),
                'n_curves': int(mask.sum()),
            }
            print(f"    {g_name}: {g_acc:.4f} ({mask.sum()} curves)")
    else:
        group_accuracy = {}

    # 8. Moment statistics by ST group
    print("\n--- Moment Means by ST Group ---")
    moment_stats = {}
    for g_idx, g_name in enumerate(unique_groups):
        mask = (labels_arr == g_idx) & valid_mask
        if mask.sum() == 0:
            continue
        means = np.mean(moments[mask], axis=0)
        stds = np.std(moments[mask], axis=0)
        moment_stats[g_name] = {
            'n': int(mask.sum()),
            'means': {f'M_{k+1}': float(means[k]) for k in range(MAX_MOMENTS)},
            'stds': {f'M_{k+1}': float(stds[k]) for k in range(MAX_MOMENTS)},
        }
        top_moments = ', '.join(f'M{k+1}={means[k]:.3f}' for k in range(3))
        print(f"    {g_name} (n={mask.sum()}): {top_moments}")

    # Compile results
    results = {
        'metadata': {
            'description': 'Genus-2 Sato-Tate moment ranking for classification',
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'prime_bound': PRIME_BOUND,
            'n_primes': len(ALL_PRIMES),
            'max_moments': MAX_MOMENTS,
            'n_curves_sampled': len(sampled),
            'n_curves_valid': int(valid_mask.sum()),
            'n_st_groups': len(unique_groups),
            'st_groups': unique_groups,
        },
        'individual_moment_ranking': {
            'ranked': [
                {
                    'rank': rank,
                    'moment': f'M_{k}',
                    'moment_index': k,
                    'accuracy': res['accuracy'],
                }
                for rank, (k, res) in enumerate(ranked, 1)
            ],
            'best_single_moment': f'M_{ranked[0][0]}',
            'best_single_accuracy': ranked[0][1]['accuracy'],
        },
        'greedy_forward_selection': {
            'history': greedy_history,
            'saturation_point': saturation_point,
            'saturation_accuracy': greedy_history[saturation_point - 1]['accuracy'] if greedy_history else 0,
        },
        'full_moment_accuracy': {
            'accuracy': full_acc,
            'n_curves': full_n,
            'n_moments': MAX_MOMENTS,
        },
        'per_group_accuracy': group_accuracy,
        'moment_statistics_by_group': moment_stats,
    }

    # Save
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_PATH}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Best single moment: {results['individual_moment_ranking']['best_single_moment']} "
          f"(accuracy: {results['individual_moment_ranking']['best_single_accuracy']:.4f})")
    print(f"Saturation point: {saturation_point} moments "
          f"(accuracy: {results['greedy_forward_selection']['saturation_accuracy']:.4f})")
    print(f"Full 10-moment accuracy: {full_acc:.4f}")
    if greedy_history:
        print(f"Best 2-moment pair: {greedy_history[1]['selected_moments']}" if len(greedy_history) >= 2 else "")
        print(f"Best 3-moment set: {greedy_history[2]['selected_moments']}" if len(greedy_history) >= 3 else "")


if __name__ == '__main__':
    main()
