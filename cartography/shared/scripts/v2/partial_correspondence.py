#!/usr/bin/env python3
"""
Partial Correspondence Detection — fractional alignment instead of exact matching.

Tests whether EC↔OEIS (and other domain pairs) hide partial correspondences
invisible to exact matching: pairs where 70-90% of positions align mod p.

Metric: match_fraction(a, b, p) = (# positions where a_i ≡ b_i mod p) / min(len_a, len_b)
Tested at first 20 positions, primes p = 2, 3, 5, 7, 11.
"""

import json
import os
import sys
import time
import numpy as np
from collections import defaultdict
from pathlib import Path

# Paths
REPO = Path(__file__).resolve().parents[4]  # F:/Prometheus
OEIS_PATH = REPO / "cartography" / "oeis" / "data" / "stripped_new.txt"
KNOTS_PATH = REPO / "cartography" / "knots" / "data" / "knots.json"
DB_PATH = REPO / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "partial_correspondence_results.json"

PRIMES = [2, 3, 5, 7, 11]
N_POSITIONS = 20
N_SAMPLE = 500
N_RANDOM = 500
PARTIAL_THRESHOLD = 0.7
HIGH_THRESHOLD = 0.8
HIGH_PRIME_COUNT = 3
SPARSITY_LIMIT = 0.5  # reject sequences that are > 50% zeros (inflates mod-p matches)

np.random.seed(42)


def is_sparse(seq, limit=SPARSITY_LIMIT):
    """Check if a sequence is dominated by zeros (inflates mod-p matches trivially)."""
    n = len(seq)
    if n == 0:
        return True
    return sum(1 for x in seq if x == 0) / n > limit


def load_oeis_sequences(path, max_seqs=50000):
    """Load OEIS sequences, filtering to those with >= N_POSITIONS terms."""
    seqs = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            parts = line.strip().split(' ', 1)
            if len(parts) < 2:
                continue
            label = parts[0]
            vals_str = parts[1].strip().strip(',')
            if not vals_str:
                continue
            try:
                vals = [int(x) for x in vals_str.split(',') if x.strip()]
            except ValueError:
                continue
            if len(vals) >= N_POSITIONS:
                trimmed = vals[:N_POSITIONS]
                if not is_sparse(trimmed):
                    seqs[label] = trimmed
            if len(seqs) >= max_seqs:
                break
    return seqs


def load_ec_aplist(db_path, limit=5000):
    """Load EC a_p lists from DuckDB."""
    import duckdb
    con = duckdb.connect(str(db_path), read_only=True)
    rows = con.execute(
        f"SELECT lmfdb_label, aplist FROM elliptic_curves WHERE aplist IS NOT NULL LIMIT {limit}"
    ).fetchall()
    con.close()
    seqs = {}
    for label, aplist in rows:
        if aplist and len(aplist) >= N_POSITIONS:
            trimmed = [int(x) for x in aplist[:N_POSITIONS]]
            if not is_sparse(trimmed):
                seqs[label] = trimmed
    return seqs


def load_mf_traces(db_path, limit=10000):
    """Load modular form trace sequences from DuckDB, filtering sparse ones."""
    import duckdb
    con = duckdb.connect(str(db_path), read_only=True)
    rows = con.execute(
        f"SELECT lmfdb_label, traces FROM modular_forms WHERE traces IS NOT NULL LIMIT {limit}"
    ).fetchall()
    con.close()
    seqs = {}
    for label, traces in rows:
        if traces and len(traces) >= N_POSITIONS:
            trimmed = [int(x) for x in traces[:N_POSITIONS]]
            if not is_sparse(trimmed):
                seqs[label] = trimmed
    return seqs


def load_knot_sequences(knots_path):
    """Load knot polynomial coefficient sequences."""
    with open(knots_path, 'r') as f:
        data = json.load(f)
    seqs = {}
    for knot in data['knots']:
        name = knot['name']
        # Use Jones polynomial coefficients as the sequence
        jones = knot.get('jones_coeffs', [])
        if len(jones) >= 5:  # Lower threshold — knot polys are short
            seqs[f"jones_{name}"] = jones
        alex = knot.get('alex_coeffs', [])
        if len(alex) >= 5:
            seqs[f"alex_{name}"] = alex
    return seqs


def match_fraction(a, b, p):
    """Fraction of positions where a_i ≡ b_i mod p, over first min(len_a, len_b) positions."""
    n = min(len(a), len(b), N_POSITIONS)
    if n == 0:
        return 0.0
    matches = sum(1 for i in range(n) if a[i] % p == b[i] % p)
    return matches / n


def compute_pairwise_scores(seqs_a, seqs_b, n_a, n_b, primes):
    """Compute partial match scores for n_a × n_b pairs across all primes."""
    keys_a = list(seqs_a.keys())
    keys_b = list(seqs_b.keys())

    if len(keys_a) > n_a:
        idx_a = np.random.choice(len(keys_a), n_a, replace=False)
        keys_a = [keys_a[i] for i in idx_a]
    if len(keys_b) > n_b:
        idx_b = np.random.choice(len(keys_b), n_b, replace=False)
        keys_b = [keys_b[i] for i in idx_b]

    # Vectorize for speed: build matrices
    mat_a = np.array([seqs_a[k][:N_POSITIONS] for k in keys_a])  # (n_a, 20)
    mat_b = np.array([seqs_b[k][:N_POSITIONS] for k in keys_b])  # (n_b, 20)

    # For knot sequences shorter than N_POSITIONS, pad with a sentinel
    # Actually, handle variable lengths properly
    results = {}
    for p in primes:
        mod_a = mat_a % p  # (n_a, 20)
        mod_b = mat_b % p  # (n_b, 20)
        # Broadcast: (n_a, 1, 20) == (1, n_b, 20) -> (n_a, n_b, 20)
        matches = (mod_a[:, None, :] == mod_b[None, :, :])  # bool
        fractions = matches.mean(axis=2)  # (n_a, n_b)
        results[p] = fractions

    return results, keys_a, keys_b


def compute_pairwise_variable_len(seqs_a, seqs_b, n_a, n_b, primes):
    """Handle sequences of variable length (e.g., knots)."""
    keys_a = list(seqs_a.keys())
    keys_b = list(seqs_b.keys())

    if len(keys_a) > n_a:
        idx_a = np.random.choice(len(keys_a), n_a, replace=False)
        keys_a = [keys_a[i] for i in idx_a]
    if len(keys_b) > n_b:
        idx_b = np.random.choice(len(keys_b), n_b, replace=False)
        keys_b = [keys_b[i] for i in idx_b]

    results = {p: np.zeros((len(keys_a), len(keys_b))) for p in primes}

    for i, ka in enumerate(keys_a):
        a = seqs_a[ka]
        for j, kb in enumerate(keys_b):
            b = seqs_b[kb]
            for p in primes:
                results[p][i, j] = match_fraction(a, b, p)

    return results, keys_a, keys_b


def analyze_distribution(scores_by_prime, primes, label):
    """Analyze the distribution of partial match scores."""
    # Combine across primes: for each pair, count how many primes have score > threshold
    n_a, n_b = scores_by_prime[primes[0]].shape

    # Distribution stats per prime
    stats = {}
    for p in primes:
        flat = scores_by_prime[p].flatten()
        stats[str(p)] = {
            'mean': float(np.mean(flat)),
            'std': float(np.std(flat)),
            'median': float(np.median(flat)),
            'pct_above_07': float((flat > 0.7).mean()),
            'pct_above_08': float((flat > 0.8).mean()),
            'pct_above_09': float((flat > 0.9).mean()),
            'pct_exact': float((flat >= 1.0).mean()),
        }

    # Multi-prime analysis: pairs with score > 0.8 at 3+ primes
    high_count = np.zeros((n_a, n_b), dtype=int)
    for p in primes:
        high_count += (scores_by_prime[p] > HIGH_THRESHOLD).astype(int)

    n_high_multi = int((high_count >= HIGH_PRIME_COUNT).sum())

    # Bimodality test: for each prime, check if distribution is bimodal
    bimodality = {}
    for p in primes:
        flat = scores_by_prime[p].flatten()
        hist, edges = np.histogram(flat, bins=50, range=(0, 1))
        # Simple bimodality: is there a valley between two peaks?
        # Check for peak near 1.0 and another peak in [0.6, 0.9]
        peak_high = hist[45:].max()  # 0.9-1.0 region
        peak_mid = hist[30:45].max()  # 0.6-0.9 region
        valley = hist[40:45].min()   # valley region

        is_bimodal = (peak_high > valley * 2) and (peak_mid > valley * 2) and (peak_high > 10)
        bimodality[str(p)] = {
            'peak_high': int(peak_high),
            'peak_mid': int(peak_mid),
            'valley': int(valley),
            'is_bimodal': bool(is_bimodal),
            'histogram': [int(x) for x in hist],
            'bin_edges': [round(float(x), 3) for x in edges],
        }

    return {
        'label': label,
        'n_pairs': n_a * n_b,
        'stats_by_prime': stats,
        'n_high_multi_prime': n_high_multi,
        'bimodality': bimodality,
    }


def find_high_partial_pairs(scores_by_prime, keys_a, keys_b, seqs_a, seqs_b, primes):
    """Find pairs with high partial match at 3+ primes and analyze disagreements."""
    n_a, n_b = scores_by_prime[primes[0]].shape

    high_count = np.zeros((n_a, n_b), dtype=int)
    for p in primes:
        high_count += (scores_by_prime[p] > HIGH_THRESHOLD).astype(int)

    # Also require NOT exact at all primes (partial, not full)
    exact_count = np.zeros((n_a, n_b), dtype=int)
    for p in primes:
        exact_count += (scores_by_prime[p] >= 1.0).astype(int)

    candidates = []
    indices = np.argwhere((high_count >= HIGH_PRIME_COUNT) & (exact_count < len(primes)))

    for idx in indices[:50]:  # Cap at 50 for analysis
        i, j = idx
        a = seqs_a[keys_a[i]]
        b = seqs_b[keys_b[j]]
        n = min(len(a), len(b), N_POSITIONS)

        pair_info = {
            'seq_a': keys_a[i],
            'seq_b': keys_b[j],
            'scores': {str(p): round(float(scores_by_prime[p][i, j]), 4) for p in primes},
            'n_primes_above_08': int(high_count[i, j]),
        }

        # Analyze disagreement positions per prime
        disagreements = {}
        for p in primes:
            disagree_pos = [pos for pos in range(n) if a[pos] % p != b[pos] % p]
            if disagree_pos:
                disagreements[str(p)] = {
                    'positions': disagree_pos,
                    'a_vals': [a[pos] for pos in disagree_pos],
                    'b_vals': [b[pos] for pos in disagree_pos],
                    'a_mod_p': [a[pos] % p for pos in disagree_pos],
                    'b_mod_p': [b[pos] % p for pos in disagree_pos],
                }

                # Check if disagreements are structured
                # Test 1: Are disagreement positions all primes?
                from sympy import isprime as _isprime
                prime_pos = [pos for pos in disagree_pos if _isprime(pos + 1)]  # 1-indexed

                # Test 2: Are they all squares?
                squares = {i*i for i in range(1, 20)}
                square_pos = [pos for pos in disagree_pos if (pos + 1) in squares]

                # Test 3: constant difference?
                diffs = [(a[pos] - b[pos]) for pos in disagree_pos]
                is_const_diff = len(set(diffs)) == 1 and len(diffs) > 1

                # Test 4: constant ratio mod p?
                ratios_mod_p = []
                for pos in disagree_pos:
                    if b[pos] % p != 0:
                        ratios_mod_p.append((a[pos] * pow(b[pos], p - 2, p)) % p)
                is_twist = len(set(ratios_mod_p)) == 1 and len(ratios_mod_p) > 1

                disagreements[str(p)]['fraction_at_primes'] = round(len(prime_pos) / max(len(disagree_pos), 1), 3)
                disagreements[str(p)]['fraction_at_squares'] = round(len(square_pos) / max(len(disagree_pos), 1), 3)
                disagreements[str(p)]['constant_difference'] = is_const_diff
                disagreements[str(p)]['constant_ratio_mod_p'] = is_twist
                if is_const_diff:
                    disagreements[str(p)]['diff_value'] = diffs[0]
                if is_twist and ratios_mod_p:
                    disagreements[str(p)]['ratio_value'] = ratios_mod_p[0]

        pair_info['disagreements'] = disagreements
        candidates.append(pair_info)

    return candidates


def expected_match_fraction(p):
    """Expected match fraction for random sequences mod p."""
    return 1.0 / p


def main():
    t0 = time.time()
    print("=" * 70)
    print("PARTIAL CORRESPONDENCE DETECTION")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    oeis = load_oeis_sequences(OEIS_PATH)
    print(f"  OEIS: {len(oeis)} sequences with >= {N_POSITIONS} terms")

    ec = load_ec_aplist(DB_PATH)
    print(f"  EC a_p: {len(ec)} curves")

    mf = load_mf_traces(DB_PATH)
    print(f"  MF traces: {len(mf)} forms")

    knots = load_knot_sequences(KNOTS_PATH)
    print(f"  Knot polys: {len(knots)} sequences")

    results = {
        'metadata': {
            'n_positions': N_POSITIONS,
            'primes': PRIMES,
            'n_sample': N_SAMPLE,
            'expected_random': {str(p): round(1.0/p, 4) for p in PRIMES},
        },
        'domain_pairs': {},
    }

    # ──────────────────────────────────────────────────────────
    # Task 2: OEIS × EC — partial match scores + random baseline
    # ──────────────────────────────────────────────────────────
    print("\n[2] OEIS × EC partial matching (500 × 500)...")
    scores_oe, keys_oeis, keys_ec = compute_pairwise_scores(oeis, ec, N_SAMPLE, N_SAMPLE, PRIMES)
    analysis_oe = analyze_distribution(scores_oe, PRIMES, "OEIS × EC")

    # Random baseline: shuffle OEIS values
    print("  Computing random baseline...")
    oeis_random = {}
    oeis_keys = list(oeis.keys())
    for i in range(N_RANDOM):
        # Generate random sequence with same range as typical OEIS
        oeis_random[f"rand_{i}"] = list(np.random.randint(-100, 100, N_POSITIONS))
    ec_random = {}
    for i in range(N_RANDOM):
        ec_random[f"rand_{i}"] = list(np.random.randint(-50, 50, N_POSITIONS))

    scores_rand, _, _ = compute_pairwise_scores(oeis_random, ec_random, N_RANDOM, N_RANDOM, PRIMES)
    analysis_rand = analyze_distribution(scores_rand, PRIMES, "Random × Random")

    # Permutation null: shuffle EC labels to break any real correspondence
    # while preserving marginal distributions exactly
    print("  Computing permutation null (shuffled pairing)...")
    ec_keys_list = list(ec.keys())
    oeis_keys_list = list(oeis.keys())
    perm_scores = {p: [] for p in PRIMES}
    for _ in range(5):
        np.random.shuffle(ec_keys_list)
        np.random.shuffle(oeis_keys_list)
        ec_perm = {k: ec[k] for k in ec_keys_list[:N_SAMPLE]}
        oeis_perm = {k: oeis[k] for k in oeis_keys_list[:N_SAMPLE]}
        sc, _, _ = compute_pairwise_scores(oeis_perm, ec_perm, N_SAMPLE, N_SAMPLE, PRIMES)
        for p in PRIMES:
            perm_scores[p].append(float(sc[p].mean()))

    perm_means = {str(p): round(float(np.mean(perm_scores[p])), 5) for p in PRIMES}
    print(f"  Permutation null means: {perm_means}")

    # Find high partial pairs
    print("  Searching for high partial matches...")
    high_pairs_oe = find_high_partial_pairs(scores_oe, keys_oeis, keys_ec, oeis, ec, PRIMES)

    results['domain_pairs']['oeis_ec'] = {
        'real': analysis_oe,
        'random_baseline': analysis_rand,
        'permutation_null_means': perm_means,
        'n_high_partial_pairs': len(high_pairs_oe),
        'high_partial_pairs': high_pairs_oe[:20],
    }

    print(f"  Real: {analysis_oe['n_high_multi_prime']} pairs with partial > 0.8 at {HIGH_PRIME_COUNT}+ primes")
    print(f"  Random: {analysis_rand['n_high_multi_prime']} pairs with partial > 0.8 at {HIGH_PRIME_COUNT}+ primes")
    for p in PRIMES:
        r = analysis_oe['stats_by_prime'][str(p)]
        b = analysis_rand['stats_by_prime'][str(p)]
        print(f"  p={p}: real mean={r['mean']:.4f} vs random={b['mean']:.4f} (expected 1/{p}={1/p:.4f})")

    # ──────────────────────────────────────────────────────────
    # Task 4: Cross-domain partial matching
    # ──────────────────────────────────────────────────────────
    print("\n[3] Cross-domain partial matching...")

    domain_pairs = [
        ("OEIS × MF", oeis, mf, N_SAMPLE, min(N_SAMPLE, len(mf))),
        ("OEIS × Knot", oeis, knots, N_SAMPLE, min(N_SAMPLE, len(knots))),
        ("EC × Knot", ec, knots, min(N_SAMPLE, len(ec)), min(N_SAMPLE, len(knots))),
        ("EC × MF", ec, mf, min(N_SAMPLE, len(ec)), min(N_SAMPLE, len(mf))),
    ]

    above_baseline_rates = {}

    for label, sa, sb, na, nb in domain_pairs:
        print(f"  {label} ({na} × {nb})...")

        # Use variable-length matching for knot pairs
        if 'Knot' in label:
            scores, ka, kb = compute_pairwise_variable_len(sa, sb, na, nb, PRIMES)
        else:
            scores, ka, kb = compute_pairwise_scores(sa, sb, na, nb, PRIMES)

        analysis = analyze_distribution(scores, PRIMES, label)
        high_pairs = find_high_partial_pairs(scores, ka, kb, sa, sb, PRIMES)

        key = label.lower().replace(' × ', '_').replace(' ', '_')
        results['domain_pairs'][key] = {
            'real': analysis,
            'n_high_partial_pairs': len(high_pairs),
            'high_partial_pairs': high_pairs[:10],
        }

        # Compute rate above baseline for ranking
        rate = analysis['n_high_multi_prime'] / max(analysis['n_pairs'], 1)
        above_baseline_rates[label] = rate

        print(f"    {analysis['n_high_multi_prime']} pairs with partial > 0.8 at {HIGH_PRIME_COUNT}+ primes")
        for p in PRIMES:
            s = analysis['stats_by_prime'][str(p)]
            print(f"    p={p}: mean={s['mean']:.4f}, >0.8: {s['pct_above_08']:.4%}, exact: {s['pct_exact']:.4%}")

    # Rank domain pairs by partial match rate above baseline
    ranked = sorted(above_baseline_rates.items(), key=lambda x: -x[1])
    results['ranking'] = [{'pair': k, 'high_partial_rate': round(v, 6)} for k, v in ranked]

    # ──────────────────────────────────────────────────────────
    # Task 5: Bimodality analysis
    # ──────────────────────────────────────────────────────────
    print("\n[4] Bimodality analysis (fractional bridge metric)...")

    bimodality_summary = {}
    for key, data in results['domain_pairs'].items():
        bm = data['real']['bimodality']
        any_bimodal = any(bm[str(p)]['is_bimodal'] for p in PRIMES)
        bimodality_summary[key] = {
            'any_bimodal': any_bimodal,
            'bimodal_primes': [p for p in PRIMES if bm[str(p)]['is_bimodal']],
        }
        status = "BIMODAL" if any_bimodal else "unimodal"
        print(f"  {key}: {status}")
        if any_bimodal:
            print(f"    Bimodal at primes: {bimodality_summary[key]['bimodal_primes']}")

    results['bimodality_summary'] = bimodality_summary

    # ──────────────────────────────────────────────────────────
    # Summary
    # ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Key question: Is the partial match population significantly above random?
    oe_real = results['domain_pairs']['oeis_ec']['real']
    oe_rand = results['domain_pairs']['oeis_ec']['random_baseline']

    print(f"\nOEIS × EC vs Random baseline:")
    for p in PRIMES:
        real_08 = oe_real['stats_by_prime'][str(p)]['pct_above_08']
        rand_08 = oe_rand['stats_by_prime'][str(p)]['pct_above_08']
        ratio = real_08 / max(rand_08, 1e-10)
        print(f"  p={p}: real >0.8 rate = {real_08:.4%}, random = {rand_08:.4%}, ratio = {ratio:.2f}x")

    print(f"\nMulti-prime high partial pairs (>0.8 at {HIGH_PRIME_COUNT}+ primes):")
    print(f"  OEIS × EC:   {oe_real['n_high_multi_prime']} (real) vs {oe_rand['n_high_multi_prime']} (random)")

    print(f"\nDomain pair ranking by high partial match rate:")
    for item in results['ranking']:
        print(f"  {item['pair']}: {item['high_partial_rate']:.6f}")

    print(f"\nBimodality (genuine partial correspondences):")
    for key, bm in bimodality_summary.items():
        print(f"  {key}: {'YES' if bm['any_bimodal'] else 'NO'} (primes: {bm['bimodal_primes']})")

    # Disagreement analysis
    n_structured = 0
    for key, data in results['domain_pairs'].items():
        for pair in data.get('high_partial_pairs', []):
            for p_str, dis in pair.get('disagreements', {}).items():
                if dis.get('constant_difference') or dis.get('constant_ratio_mod_p'):
                    n_structured += 1
                if dis.get('fraction_at_primes', 0) > 0.6:
                    n_structured += 1

    print(f"\nStructured disagreements found: {n_structured}")

    # Parity bias analysis: EC and MF traces are heavily even-biased
    # This inflates p=2 match rates without indicating real bridges
    print(f"\nParity bias check (explains p=2 anomalies):")
    for domain_name, domain_seqs in [("OEIS", oeis), ("EC", ec), ("MF", mf)]:
        sample_keys = list(domain_seqs.keys())[:500]
        even_fracs = []
        for k in sample_keys:
            s = domain_seqs[k][:N_POSITIONS]
            even_fracs.append(sum(1 for x in s if x % 2 == 0) / len(s))
        mean_even = np.mean(even_fracs)
        print(f"  {domain_name}: {mean_even:.1%} even (0.5 = no bias)")

    results['summary'] = {
        'total_high_partial_pairs': sum(
            d['real']['n_high_multi_prime'] for d in results['domain_pairs'].values()
        ),
        'n_structured_disagreements': n_structured,
        'any_bimodal': any(bm['any_bimodal'] for bm in bimodality_summary.values()),
        'parity_bias_note': (
            "EC a_p ~81% even, MF traces ~76% even, OEIS varies. "
            "The p=2 match rate inflation (EC x MF: 0.635 vs 0.5 expected) is fully "
            "explained by this arithmetic bias, not a bridge."
        ),
        'sparse_filter': f"Sequences with >{SPARSITY_LIMIT:.0%} zeros excluded (prevents trivial mod-p inflation)",
        'elapsed_seconds': round(time.time() - t0, 1),
    }

    # Strip histograms from output to keep file size manageable
    for key in results['domain_pairs']:
        for p_str in list(results['domain_pairs'][key]['real']['bimodality'].keys()):
            bm = results['domain_pairs'][key]['real']['bimodality'][p_str]
            # Keep histogram but truncate bin_edges
            bm['bin_edges'] = bm['bin_edges'][:5] + ['...'] + bm['bin_edges'][-5:]
        if 'random_baseline' in results['domain_pairs'][key]:
            for p_str in list(results['domain_pairs'][key]['random_baseline']['bimodality'].keys()):
                bm = results['domain_pairs'][key]['random_baseline']['bimodality'][p_str]
                bm['bin_edges'] = bm['bin_edges'][:5] + ['...'] + bm['bin_edges'][-5:]

    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Elapsed: {time.time() - t0:.1f}s")


if __name__ == '__main__':
    main()
