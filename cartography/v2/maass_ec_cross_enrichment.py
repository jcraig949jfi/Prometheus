"""
Cross-Family Mod-p Fingerprint Enrichment: Maass Forms vs Elliptic Curves
=========================================================================
Tests whether Maass forms at level N and elliptic curves at conductor N
share mod-p fingerprint structure beyond random chance.

Within-family enrichment is established (~8x for EC, ~4-8x for Maass).
This tests CROSS-FAMILY enrichment: does the Langlands correspondence
create detectable fingerprint bridges between these two families?

Method:
1. For each shared N (level=conductor), pair every Maass form with every EC
2. For primes p in {3,5,7}: extract a_p from both objects
   - EC: a_p is integer, compute a_p mod p (standard)
   - Maass: a_p is real (~N(0,1)), discretize via floor(a_p) mod p
     (also test quantile-binned version for robustness)
3. Agreement = fraction of cross-pairs where both map to same residue
4. Enrichment = observed agreement / (1/p) [uniform baseline]
5. Null: permute Maass-EC pairings across different N values
6. Battery: multiple primes, fingerprint lengths, significance via permutation

Key subtlety: EC a_p mod p has genuine arithmetic meaning (related to
reduction type, supersingularity). Maass a_p are Hecke eigenvalues,
continuous real numbers. Two comparison strategies:
  A) "Floor mod p": floor(a_p) mod p — crude but preserves sign structure
  B) "Quantile mod p": bin into p equal-count bins — removes scale effects
  C) "Sign agreement": sgn(a_p) for both — minimal, robust
"""

import json
import numpy as np
from collections import Counter, defaultdict
import os
import time
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAASS_PATH = os.path.join(SCRIPT_DIR, "..", "maass", "data", "maass_with_coefficients.json")
DUCKDB_PATH = os.path.join(SCRIPT_DIR, "..", "..", "charon", "data", "charon.duckdb")
OUT_PATH = os.path.join(SCRIPT_DIR, "maass_ec_cross_enrichment_results.json")

PRIMES = [2, 3, 5, 7, 11, 13]
FINGERPRINT_PRIMES = [3, 5, 7]  # primes for mod-p fingerprint
FINGERPRINT_LENGTHS = [1, 2, 3]  # how many primes in fingerprint tuple
N_PERMUTATIONS = 1000


def load_maass_data():
    """Load Maass forms, return dict: level -> list of {maass_id, coefficients}."""
    with open(MAASS_PATH) as f:
        raw = json.load(f)
    by_level = defaultdict(list)
    for m in raw:
        if m['n_coefficients'] >= 15:  # need at least a_13
            by_level[m['level']].append({
                'id': m['maass_id'],
                'coeffs': m['coefficients'],
                'n_coeffs': m['n_coefficients']
            })
    return by_level


def load_ec_data(overlap_levels):
    """Load EC data from DuckDB for given conductors."""
    try:
        import duckdb
    except ImportError:
        print("ERROR: duckdb not installed")
        sys.exit(1)

    con = duckdb.connect(DUCKDB_PATH, read_only=True)
    placeholders = ','.join(str(l) for l in overlap_levels)
    rows = con.execute(f"""
        SELECT conductor, lmfdb_label, aplist, anlist
        FROM elliptic_curves
        WHERE conductor IN ({placeholders})
        AND aplist IS NOT NULL
    """).fetchall()
    con.close()

    by_conductor = defaultdict(list)
    for conductor, label, aplist, anlist in rows:
        by_conductor[conductor].append({
            'label': label,
            'aplist': list(aplist) if aplist else [],
            'anlist': list(anlist) if anlist else []
        })
    return by_conductor


def get_ec_ap(ec, prime_index):
    """Get a_p for EC from aplist (index into first 25 primes)."""
    if prime_index < len(ec['aplist']):
        return ec['aplist'][prime_index]
    return None


def get_maass_ap(maass, prime):
    """Get a_p for Maass form (coefficient at index p-1, 0-indexed)."""
    idx = prime - 1  # coefficients[0] = a_1 = 1, coefficients[1] = a_2, etc.
    if idx < maass['n_coeffs'] and idx < len(maass['coeffs']):
        return maass['coeffs'][idx]
    return None


# The first 25 primes for aplist indexing
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
             53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def prime_to_aplist_index(p):
    """Convert prime to index in aplist."""
    try:
        return PRIMES_25.index(p)
    except ValueError:
        return None


def compute_cross_fingerprint_agreement(maass_list, ec_list, primes, fp_length, method='floor_mod', level=None):
    """
    For each (Maass, EC) pair at the same N, compute fingerprint agreement.
    Excludes primes that divide N (bad primes).

    method: 'floor_mod' | 'quantile' | 'sign'
    Returns: (n_agreeing, n_total, agreement_rate)
    """
    # Filter out bad primes (p | N)
    good_primes = [p for p in primes[:fp_length] if level is None or level % p != 0]
    if len(good_primes) == 0:
        return 0, 0, 0.0

    n_agree = 0
    n_total = 0

    for maass in maass_list:
        for ec in ec_list:
            # Build fingerprints using only good primes
            maass_fp = []
            ec_fp = []
            valid = True

            for p in good_primes:
                ap_idx = prime_to_aplist_index(p)

                ec_ap = get_ec_ap(ec, ap_idx) if ap_idx is not None else None
                maass_ap = get_maass_ap(maass, p)

                if ec_ap is None or maass_ap is None:
                    valid = False
                    break

                # EC fingerprint: a_p mod p
                ec_residue = ec_ap % p

                if method == 'floor_mod':
                    # Floor then mod: preserves integer structure
                    maass_residue = int(np.floor(maass_ap)) % p
                elif method == 'sign':
                    # Sign agreement only (binary)
                    ec_residue = 1 if ec_ap > 0 else 0
                    maass_residue = 1 if maass_ap > 0 else 0
                else:
                    maass_residue = int(np.floor(maass_ap)) % p

                maass_fp.append(maass_residue)
                ec_fp.append(ec_residue)

            if valid and len(maass_fp) == len(good_primes):
                n_total += 1
                if tuple(maass_fp) == tuple(ec_fp):
                    n_agree += 1

    rate = n_agree / n_total if n_total > 0 else 0.0
    return n_agree, n_total, rate


def compute_cross_mi(maass_list, ec_list, prime):
    """
    Compute mutual information between EC a_p mod p and Maass floor(a_p) mod p.
    More sensitive than exact agreement for detecting any correlation.
    """
    ap_idx = prime_to_aplist_index(prime)
    if ap_idx is None:
        return None

    ec_residues = []
    maass_residues = []

    for maass in maass_list:
        for ec in ec_list:
            ec_ap = get_ec_ap(ec, ap_idx)
            maass_ap = get_maass_ap(maass, prime)
            if ec_ap is not None and maass_ap is not None:
                ec_residues.append(ec_ap % prime)
                maass_residues.append(int(np.floor(maass_ap)) % prime)

    if len(ec_residues) < 10:
        return None

    # Joint distribution
    joint = Counter(zip(ec_residues, maass_residues))
    n = len(ec_residues)

    # Marginals
    ec_marginal = Counter(ec_residues)
    maass_marginal = Counter(maass_residues)

    # MI = sum p(x,y) log(p(x,y) / (p(x)p(y)))
    mi = 0.0
    for (x, y), count in joint.items():
        pxy = count / n
        px = ec_marginal[x] / n
        py = maass_marginal[y] / n
        if pxy > 0 and px > 0 and py > 0:
            mi += pxy * np.log2(pxy / (px * py))

    return mi


def permutation_null(all_maass_by_level, all_ec_by_conductor, overlap_levels,
                     primes, fp_length, method, n_perms):
    """
    Null model: randomly reassign Maass forms to EC conductors.
    Returns distribution of agreement rates under null.
    """
    rng = np.random.RandomState(42)
    null_rates = []

    # Pool all maass forms from overlap levels
    all_maass = []
    for N in overlap_levels:
        all_maass.extend(all_maass_by_level[N])

    # Pool all ec forms from overlap levels
    all_ec = []
    level_for_ec = []
    for N in overlap_levels:
        for ec in all_ec_by_conductor[N]:
            all_ec.append(ec)
            level_for_ec.append(N)

    if len(all_maass) == 0 or len(all_ec) == 0:
        return []

    for _ in range(n_perms):
        # Shuffle maass assignments
        shuffled_maass = list(all_maass)
        rng.shuffle(shuffled_maass)

        # Assign shuffled maass to EC pairings
        n_agree = 0
        n_total = 0
        idx = 0

        for N in overlap_levels:
            n_maass_at_N = len(all_maass_by_level[N])
            n_ec_at_N = len(all_ec_by_conductor[N])
            if n_maass_at_N == 0 or n_ec_at_N == 0:
                continue

            # Take next chunk of shuffled maass
            chunk = shuffled_maass[idx:idx + n_maass_at_N]
            idx += n_maass_at_N
            if idx > len(shuffled_maass):
                idx = idx % len(shuffled_maass)

            a, t, r = compute_cross_fingerprint_agreement(
                chunk, all_ec_by_conductor[N], primes, fp_length, method, level=N)
            n_agree += a
            n_total += t

        if n_total > 0:
            null_rates.append(n_agree / n_total)

    return null_rates


def main():
    t0 = time.time()
    print("Loading Maass data...")
    maass_by_level = load_maass_data()
    print(f"  {sum(len(v) for v in maass_by_level.values())} forms across {len(maass_by_level)} levels")

    overlap_levels = sorted(maass_by_level.keys())
    print(f"\nLoading EC data for {len(overlap_levels)} candidate levels...")
    ec_by_conductor = load_ec_data(overlap_levels)
    print(f"  {sum(len(v) for v in ec_by_conductor.values())} ECs across {len(ec_by_conductor)} conductors")

    # Find actual overlap
    shared_N = sorted(set(maass_by_level.keys()) & set(ec_by_conductor.keys()))
    print(f"\n  Shared N (level=conductor): {len(shared_N)} values")
    print(f"  Examples: {shared_N[:20]}")

    # Count pairs
    total_pairs = sum(len(maass_by_level[N]) * len(ec_by_conductor[N]) for N in shared_N)
    print(f"  Total cross-pairs: {total_pairs:,}")

    results = {
        'metadata': {
            'n_shared_levels': len(shared_N),
            'shared_levels': shared_N,
            'total_maass': sum(len(maass_by_level[N]) for N in shared_N),
            'total_ec': sum(len(ec_by_conductor[N]) for N in shared_N),
            'total_cross_pairs': total_pairs,
            'fingerprint_primes': FINGERPRINT_PRIMES,
            'n_permutations': N_PERMUTATIONS,
        },
        'tests': []
    }

    # ======================================================
    # Test 1: Exact fingerprint agreement (floor_mod)
    # ======================================================
    print("\n=== Test 1: Floor-mod fingerprint agreement ===")
    for fp_len in FINGERPRINT_LENGTHS:
        primes_used = FINGERPRINT_PRIMES[:fp_len]
        n_agree_total = 0
        n_pairs_total = 0
        per_level = {}

        for N in shared_N:
            a, t, r = compute_cross_fingerprint_agreement(
                maass_by_level[N], ec_by_conductor[N], FINGERPRINT_PRIMES, fp_len, 'floor_mod', level=N)
            n_agree_total += a
            n_pairs_total += t
            if t > 0:
                per_level[str(N)] = {'agree': a, 'total': t, 'rate': round(r, 6)}

        obs_rate = n_agree_total / n_pairs_total if n_pairs_total > 0 else 0
        # Expected under independence: product of 1/p for each good prime
        # Since bad primes are excluded per-level, use average good-prime count
        # For simplicity, use the primes that are good for most levels
        expected_rate = 1.0
        for p in primes_used:
            expected_rate *= 1.0 / p
        enrichment = obs_rate / expected_rate if expected_rate > 0 else 0

        print(f"  fp_len={fp_len}, primes={primes_used}")
        print(f"    Observed: {obs_rate:.6f}, Expected: {expected_rate:.6f}, Enrichment: {enrichment:.3f}x")
        print(f"    ({n_agree_total}/{n_pairs_total} pairs agree)")

        # Permutation null
        print(f"    Running {N_PERMUTATIONS} permutations...")
        null_rates = permutation_null(
            maass_by_level, ec_by_conductor, shared_N,
            FINGERPRINT_PRIMES, fp_len, 'floor_mod', N_PERMUTATIONS)

        if null_rates:
            null_mean = np.mean(null_rates)
            null_std = np.std(null_rates)
            z_score = (obs_rate - null_mean) / null_std if null_std > 0 else 0
            p_value = np.mean([1.0 if nr >= obs_rate else 0.0 for nr in null_rates])
            print(f"    Null mean: {null_mean:.6f} +/- {null_std:.6f}")
            print(f"    z-score: {z_score:.2f}, p-value: {p_value:.4f}")
        else:
            null_mean = null_std = z_score = p_value = None

        results['tests'].append({
            'test': 'floor_mod_fingerprint',
            'fp_length': fp_len,
            'primes_used': primes_used,
            'observed_rate': round(obs_rate, 8),
            'expected_uniform': round(expected_rate, 8),
            'enrichment': round(enrichment, 4),
            'n_agree': n_agree_total,
            'n_pairs': n_pairs_total,
            'null_mean': round(null_mean, 8) if null_mean is not None else None,
            'null_std': round(null_std, 8) if null_std is not None else None,
            'z_score': round(z_score, 3) if z_score is not None else None,
            'p_value': round(p_value, 4) if p_value is not None else None,
            'per_level_top10': dict(sorted(per_level.items(),
                                           key=lambda x: x[1]['rate'], reverse=True)[:10]),
        })

    # ======================================================
    # Test 2: Sign agreement at each prime
    # ======================================================
    print("\n=== Test 2: Sign agreement per prime ===")
    sign_results = []
    for p in PRIMES:
        ap_idx = prime_to_aplist_index(p)
        n_same_sign = 0
        n_total = 0

        for N in shared_N:
            if N % p == 0:
                continue  # skip bad primes
            for maass in maass_by_level[N]:
                for ec in ec_by_conductor[N]:
                    ec_ap = get_ec_ap(ec, ap_idx)
                    maass_ap = get_maass_ap(maass, p)
                    if ec_ap is not None and maass_ap is not None and ec_ap != 0 and abs(maass_ap) > 0.01:
                        n_total += 1
                        if (ec_ap > 0) == (maass_ap > 0):
                            n_same_sign += 1

        rate = n_same_sign / n_total if n_total > 0 else 0
        enrichment = rate / 0.5  # expected 50% under independence
        print(f"  p={p}: sign agreement = {rate:.4f} ({n_same_sign}/{n_total}), enrichment = {enrichment:.3f}x")

        sign_results.append({
            'prime': p,
            'sign_agreement': round(rate, 6),
            'enrichment_vs_50pct': round(enrichment, 4),
            'n_agree': n_same_sign,
            'n_total': n_total
        })

    results['tests'].append({
        'test': 'sign_agreement',
        'per_prime': sign_results
    })

    # ======================================================
    # Test 3: Mutual information per prime
    # ======================================================
    print("\n=== Test 3: Mutual information (EC a_p mod p) vs (Maass floor(a_p) mod p) ===")
    mi_results = []
    for p in FINGERPRINT_PRIMES:
        # Observed MI — exclude levels where p | N (bad prime)
        all_ec_res = []
        all_maass_res = []
        for N in shared_N:
            if N % p == 0:
                continue  # skip bad primes
            for maass in maass_by_level[N]:
                for ec in ec_by_conductor[N]:
                    ap_idx = prime_to_aplist_index(p)
                    ec_ap = get_ec_ap(ec, ap_idx)
                    maass_ap = get_maass_ap(maass, p)
                    if ec_ap is not None and maass_ap is not None:
                        all_ec_res.append(ec_ap % p)
                        all_maass_res.append(int(np.floor(maass_ap)) % p)

        n = len(all_ec_res)
        if n < 10:
            continue

        # Compute observed MI
        joint = Counter(zip(all_ec_res, all_maass_res))
        ec_marg = Counter(all_ec_res)
        maass_marg = Counter(all_maass_res)

        mi_obs = 0.0
        for (x, y), count in joint.items():
            pxy = count / n
            px = ec_marg[x] / n
            py = maass_marg[y] / n
            if pxy > 0 and px > 0 and py > 0:
                mi_obs += pxy * np.log2(pxy / (px * py))

        # Null MI: shuffle one column
        rng = np.random.RandomState(42)
        null_mis = []
        maass_arr = np.array(all_maass_res)
        ec_arr = np.array(all_ec_res)
        for _ in range(N_PERMUTATIONS):
            shuffled = rng.permutation(maass_arr)
            joint_null = Counter(zip(ec_arr, shuffled))
            mi_null = 0.0
            for (x, y), count in joint_null.items():
                pxy = count / n
                px = ec_marg[x] / n
                py = maass_marg[y] / n
                if pxy > 0 and px > 0 and py > 0:
                    mi_null += pxy * np.log2(pxy / (px * py))
            null_mis.append(mi_null)

        null_mean = np.mean(null_mis)
        null_std = np.std(null_mis)
        z_mi = (mi_obs - null_mean) / null_std if null_std > 0 else 0

        print(f"  p={p}: MI={mi_obs:.6f} bits, null={null_mean:.6f}+/-{null_std:.6f}, z={z_mi:.2f}")

        # Distribution of EC residues and Maass residues
        ec_dist = {str(k): round(v/n, 4) for k, v in sorted(ec_marg.items())}
        maass_dist = {str(k): round(v/n, 4) for k, v in sorted(maass_marg.items())}

        mi_results.append({
            'prime': p,
            'mi_bits': round(mi_obs, 8),
            'null_mean': round(null_mean, 8),
            'null_std': round(null_std, 8),
            'z_score': round(z_mi, 3),
            'n_pairs': n,
            'ec_residue_dist': ec_dist,
            'maass_residue_dist': maass_dist
        })

    results['tests'].append({
        'test': 'mutual_information',
        'per_prime': mi_results
    })

    # ======================================================
    # Test 4: Residue-conditioned Maass coefficient statistics
    # ======================================================
    print("\n=== Test 4: Maass a_p distribution conditioned on EC a_p mod p ===")
    cond_results = []
    for p in FINGERPRINT_PRIMES:
        ap_idx = prime_to_aplist_index(p)
        # Group Maass a_p values by the EC a_p mod p of their paired EC
        # Exclude bad primes (p | N)
        conditioned = defaultdict(list)

        for N in shared_N:
            if N % p == 0:
                continue  # skip bad primes
            for maass in maass_by_level[N]:
                maass_ap = get_maass_ap(maass, p)
                if maass_ap is None:
                    continue
                for ec in ec_by_conductor[N]:
                    ec_ap = get_ec_ap(ec, ap_idx)
                    if ec_ap is not None:
                        conditioned[ec_ap % p].append(maass_ap)

        # Compare means across EC residue classes
        class_stats = {}
        for res in range(p):
            vals = conditioned.get(res, [])
            if len(vals) > 10:
                class_stats[str(res)] = {
                    'n': len(vals),
                    'mean': round(np.mean(vals), 6),
                    'std': round(np.std(vals), 6),
                    'median': round(np.median(vals), 6)
                }

        # F-test: are means significantly different across residue classes?
        groups = [np.array(conditioned[r]) for r in range(p) if len(conditioned.get(r, [])) > 10]
        if len(groups) >= 2:
            grand_mean = np.mean(np.concatenate(groups))
            ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
            ss_within = sum(np.sum((g - np.mean(g))**2) for g in groups)
            k = len(groups)
            n_total = sum(len(g) for g in groups)
            if ss_within > 0 and n_total > k:
                f_stat = (ss_between / (k - 1)) / (ss_within / (n_total - k))
            else:
                f_stat = 0
        else:
            f_stat = 0

        print(f"  p={p}: F-stat={f_stat:.4f}, classes: {list(class_stats.keys())}")
        for res, stats in sorted(class_stats.items()):
            print(f"    residue {res}: mean={stats['mean']:.4f}, n={stats['n']}")

        cond_results.append({
            'prime': p,
            'f_statistic': round(f_stat, 6),
            'class_stats': class_stats
        })

    results['tests'].append({
        'test': 'conditioned_distribution',
        'per_prime': cond_results
    })

    # ======================================================
    # Test 5: Level-specific enrichment (are some N special?)
    # ======================================================
    print("\n=== Test 5: Level-specific cross-enrichment hotspots ===")
    level_enrichments = {}
    for N in shared_N:
        maass_list = maass_by_level[N]
        ec_list = ec_by_conductor[N]
        if len(maass_list) < 5 or len(ec_list) < 1:
            continue

        # Use fp_length=1 at p=3 for maximum sample size (skip if 3|N)
        p = 3
        if N % p == 0:
            continue
        ap_idx = prime_to_aplist_index(p)
        n_agree = 0
        n_total = 0

        for maass in maass_list:
            for ec in ec_list:
                ec_ap = get_ec_ap(ec, ap_idx)
                maass_ap = get_maass_ap(maass, p)
                if ec_ap is not None and maass_ap is not None:
                    n_total += 1
                    if ec_ap % p == int(np.floor(maass_ap)) % p:
                        n_agree += 1

        if n_total > 0:
            rate = n_agree / n_total
            expected = 1.0 / p
            enrichment = rate / expected
            level_enrichments[str(N)] = {
                'n_maass': len(maass_list),
                'n_ec': len(ec_list),
                'n_pairs': n_total,
                'agreement_rate': round(rate, 6),
                'enrichment': round(enrichment, 4),
            }

    # Sort by enrichment
    sorted_levels = sorted(level_enrichments.items(), key=lambda x: x[1]['enrichment'], reverse=True)
    print(f"  Top 10 enriched levels (p=3):")
    for lev, info in sorted_levels[:10]:
        print(f"    N={lev}: enrichment={info['enrichment']:.3f}x "
              f"(rate={info['agreement_rate']:.4f}, {info['n_pairs']} pairs)")
    print(f"  Bottom 5:")
    for lev, info in sorted_levels[-5:]:
        print(f"    N={lev}: enrichment={info['enrichment']:.3f}x "
              f"(rate={info['agreement_rate']:.4f}, {info['n_pairs']} pairs)")

    results['tests'].append({
        'test': 'level_specific_enrichment',
        'prime': 3,
        'n_levels_tested': len(level_enrichments),
        'top_10': dict(sorted_levels[:10]),
        'bottom_5': dict(sorted_levels[-5:]),
        'mean_enrichment': round(np.mean([v['enrichment'] for v in level_enrichments.values()]), 4),
        'std_enrichment': round(np.std([v['enrichment'] for v in level_enrichments.values()]), 4),
    })

    # ======================================================
    # Summary
    # ======================================================
    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Determine verdict
    any_significant = False
    for test in results['tests']:
        if 'z_score' in test and test['z_score'] is not None:
            if abs(test['z_score']) > 3:
                any_significant = True
        if 'per_prime' in test:
            for sub in test.get('per_prime', []):
                if 'z_score' in sub and sub['z_score'] is not None:
                    if abs(sub['z_score']) > 3:
                        any_significant = True

    verdict = "ENRICHED" if any_significant else "NULL (no cross-family enrichment detected)"
    print(f"\nVERDICT: {verdict}")

    results['verdict'] = verdict
    results['elapsed_seconds'] = round(elapsed, 2)

    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == '__main__':
    main()
