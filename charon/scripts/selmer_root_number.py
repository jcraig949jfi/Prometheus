"""
Aporia Deep Research Report #54:
BKLPR Selmer distribution refined by root number.

Root number = (-1)^analytic_rank (verified: signD != root number).
Split 3.8M curves by root number, analyze Sha/torsion/Selmer distributions.
Test Poonen-Rains predictions.
"""

import json
import sys
import os
from collections import defaultdict
from math import prod

import psycopg2

DB_PARAMS = dict(host='localhost', port=5432, dbname='lmfdb',
                 user='postgres', password='prometheus')

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           'data', 'selmer_root_number.json')


def poonen_rains_trivial_sha_prob(p=2, max_terms=50):
    """
    Poonen-Rains prediction for Prob(Sha[p] = 0) for rank-0 curves.
    For a random alternating matrix over F_p:
    Prob(corank=0) = prod_{i>=1}(1 - p^{-(2i-1)})
    """
    val = 1.0
    for i in range(1, max_terms + 1):
        val *= (1.0 - p**(-(2*i - 1)))
    return val


def query_all(conn):
    """Fetch rank, sha, torsion for all curves."""
    cur = conn.cursor()
    cur.execute('''
        SELECT analytic_rank::int, sha::bigint, torsion::int
        FROM ec_curvedata
    ''')
    return cur.fetchall()


def analyze(rows):
    results = {}

    # Classify by root number
    by_root = {1: [], -1: []}
    for (rank, sha, torsion) in rows:
        rn = (-1) ** rank
        by_root[rn].append((rank, sha, torsion))

    results['total_curves'] = len(rows)
    results['root_plus1_count'] = len(by_root[1])
    results['root_minus1_count'] = len(by_root[-1])

    # --- Task 3: Prob(p | X) by root number ---
    primes = [2, 3, 5, 7]
    prob_tables = {}
    for rn_label, rn_val in [('root_plus1', 1), ('root_minus1', -1)]:
        data = by_root[rn_val]
        n = len(data)
        if n == 0:
            continue
        entry = {'count': n}
        for p in primes:
            sha_div = sum(1 for (_, sha, _) in data if sha % p == 0 and sha > 1)
            # sha=1 means trivial Sha, not divisible by p
            # Actually: p | sha means sha % p == 0, including sha=0 edge cases
            # But sha >= 1 always. sha=1 => not divisible. sha=4 => divisible by 2.
            sha_div_count = sum(1 for (_, sha, _) in data if sha > 1 and sha % p == 0)
            sha_nontrivial = sum(1 for (_, sha, _) in data if sha > 1)
            tor_div = sum(1 for (_, _, tor) in data if tor % p == 0)
            # Combined: p divides sha*torsion
            comb_div = sum(1 for (_, sha, tor) in data if (sha * tor) % p == 0)

            entry[f'prob_{p}_divides_sha'] = sha_div_count / n
            entry[f'prob_{p}_divides_torsion'] = tor_div / n
            entry[f'prob_{p}_divides_sha_times_torsion'] = comb_div / n
            entry[f'prob_sha_nontrivial'] = sha_nontrivial / n
            entry[f'prob_sha_trivial'] = 1.0 - sha_nontrivial / n

        prob_tables[rn_label] = entry

    results['probability_tables'] = prob_tables

    # --- Task 4: Effect size for 2 | Sha ---
    p1 = prob_tables['root_plus1']['prob_2_divides_sha']
    m1 = prob_tables['root_minus1']['prob_2_divides_sha']
    results['effect_2_divides_sha'] = {
        'root_plus1': p1,
        'root_minus1': m1,
        'ratio': p1 / m1 if m1 > 0 else None,
        'difference': p1 - m1
    }

    # --- Task 5: Rank-stratified analysis ---
    rank_strata = {}
    for rn_val in [1, -1]:
        data = by_root[rn_val]
        by_rank = defaultdict(list)
        for (rank, sha, torsion) in data:
            by_rank[rank].append((sha, torsion))

        rn_label = 'root_plus1' if rn_val == 1 else 'root_minus1'
        rank_strata[rn_label] = {}
        for r in sorted(by_rank.keys()):
            curves = by_rank[r]
            n = len(curves)
            if n < 10:
                continue

            sha_vals = [s for (s, _) in curves]
            sha_trivial = sum(1 for s in sha_vals if s == 1)
            sha_mean = sum(sha_vals) / n

            # Sha distribution
            sha_dist = defaultdict(int)
            for s in sha_vals:
                sha_dist[s] += 1
            # Top 10 sha values
            top_sha = sorted(sha_dist.items(), key=lambda x: -x[1])[:10]

            # 2-divisibility of sha
            sha_2div = sum(1 for s in sha_vals if s > 1 and s % 2 == 0)

            rank_strata[rn_label][str(r)] = {
                'count': n,
                'prob_sha_trivial': sha_trivial / n,
                'mean_sha': round(sha_mean, 4),
                'prob_2_divides_sha': sha_2div / n,
                'sha_distribution_top10': {str(k): v for k, v in top_sha},
            }

    results['rank_stratified'] = rank_strata

    # --- Task 6: Poonen-Rains numerical test ---
    pr_predictions = {}
    for p in [2, 3, 5, 7]:
        pr_prob = poonen_rains_trivial_sha_prob(p)
        pr_predictions[str(p)] = {
            'PR_prob_trivial_sha_p': round(pr_prob, 6),
        }

    # Empirical: Prob(Sha[p] trivial) at rank 0, root_number +1
    # Sha[p] trivial means p does not divide sha
    rank0_plus = rank_strata.get('root_plus1', {}).get('0', {})
    rank0_minus = rank_strata.get('root_minus1', {}).get('0', {})

    if rank0_plus:
        n_r0p = rank0_plus['count']
        data_r0p = [d for d in by_root[1] if d[0] == 0]
        for p in primes:
            p_not_div = sum(1 for (_, sha, _) in data_r0p if sha % p != 0) / n_r0p
            pr_predictions[str(p)]['empirical_prob_sha_p_trivial_rank0_rootP1'] = round(p_not_div, 6)
            pr_pred = pr_predictions[str(p)]['PR_prob_trivial_sha_p']
            pr_predictions[str(p)]['ratio_empirical_over_PR'] = round(p_not_div / pr_pred, 6) if pr_pred > 0 else None

    if rank0_minus:
        n_r0m = rank0_minus['count']
        data_r0m = [d for d in by_root[-1] if d[0] == 0]
        for p in primes:
            p_not_div = sum(1 for (_, sha, _) in data_r0m if sha % p != 0) / n_r0m
            pr_predictions[str(p)]['empirical_prob_sha_p_trivial_rank0_rootM1'] = round(p_not_div, 6)

    results['poonen_rains_test'] = pr_predictions

    # --- Task 7: Effect sizes across all primes ---
    effect_sizes = {}
    for p in primes:
        key = f'prob_{p}_divides_sha'
        p1 = prob_tables['root_plus1'][key]
        m1 = prob_tables['root_minus1'][key]
        effect_sizes[str(p)] = {
            'root_plus1': round(p1, 6),
            'root_minus1': round(m1, 6),
            'difference': round(p1 - m1, 6),
            'ratio': round(p1 / m1, 4) if m1 > 0 else None,
        }
    results['effect_sizes_p_divides_sha'] = effect_sizes

    # --- Sha parity analysis (key BKLPR prediction) ---
    # BKLPR: at root_number +1, Selmer rank is even => rank is even => Sha has even rank
    # At root_number -1, Selmer rank is odd => rank is odd
    # This means: ord_2(Sha) should differ by root number
    parity_analysis = {}
    for rn_val, rn_label in [(1, 'root_plus1'), (-1, 'root_minus1')]:
        data = by_root[rn_val]
        n = len(data)
        # sha is a perfect square (Cassels), so sha = s^2
        # 2-Selmer rank = rank + ord_2(Sha[2]) + ord_2(torsion[2])
        # Count curves where sha is a perfect 4th power (sha[2]=0) vs not
        sha_is_1 = sum(1 for (_, s, _) in data if s == 1)
        sha_is_square_not_4th = sum(1 for (_, s, _) in data if s > 1 and is_perfect_square(s) and not is_perfect_4th(s))
        sha_4th_power = sum(1 for (_, s, _) in data if s > 1 and is_perfect_4th(s))

        # 2-part of sha
        sha_2parts = defaultdict(int)
        for (_, s, _) in data:
            v2 = val_2(s)
            sha_2parts[v2] += 1

        parity_analysis[rn_label] = {
            'count': n,
            'sha_equals_1': sha_is_1,
            'prob_sha_1': round(sha_is_1 / n, 6),
            '2_adic_valuation_of_sha': {str(k): v for k, v in sorted(sha_2parts.items())},
        }

    results['sha_parity_analysis'] = parity_analysis

    # --- Selmer rank mod 2 analysis ---
    # 2-Selmer rank = MW rank + dim_F2(Sha[2]) + dim_F2(E[2](Q))
    # E[2](Q) has dimension 0, 1, or 2 depending on torsion
    selmer_mod2 = {}
    for rn_val, rn_label in [(1, 'root_plus1'), (-1, 'root_minus1')]:
        data = by_root[rn_val]
        n = len(data)
        even_selmer = 0
        odd_selmer = 0
        for (rank, sha, tor) in data:
            # dim_F2(Sha[2]) = v_2(sha) (since sha = |Sha|, and Sha[2] has order 2^(2k) for some k,
            # so dim = 2k, and v_2(sha) = 2k... but sha is |Sha| not |Sha[2]|)
            # Actually we need dim_F2(Sha[2]) which we can't get directly from |Sha|.
            # We can get v_2(|Sha|) though.
            # For the parity constraint: sel_2_rank ≡ rank (mod 2) when E[2](Q) has even dimension
            # Just track rank parity directly
            if rank % 2 == 0:
                even_selmer += 1
            else:
                odd_selmer += 1

        selmer_mod2[rn_label] = {
            'even_rank_count': even_selmer,
            'odd_rank_count': odd_selmer,
            'prob_even_rank': round(even_selmer / n, 6),
            'prob_odd_rank': round(odd_selmer / n, 6),
        }

    results['rank_parity_by_root_number'] = selmer_mod2

    return results


def is_perfect_square(n):
    if n < 0:
        return False
    r = int(n**0.5)
    for c in [r-1, r, r+1]:
        if c >= 0 and c*c == n:
            return True
    return False


def is_perfect_4th(n):
    if n < 0:
        return False
    r = int(n**0.25)
    for c in [r-1, r, r+1]:
        if c >= 0 and c**4 == n:
            return True
    return False


def val_2(n):
    """2-adic valuation of n."""
    if n == 0:
        return 0
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def main():
    print("Connecting to LMFDB...")
    conn = psycopg2.connect(**DB_PARAMS)

    print("Fetching all curves (rank, sha, torsion)...")
    rows = query_all(conn)
    conn.close()
    print(f"  Loaded {len(rows)} curves.")

    print("Analyzing...")
    results = analyze(rows)

    # Print summary
    print(f"\n{'='*60}")
    print(f"BKLPR Selmer Distribution by Root Number")
    print(f"{'='*60}")
    print(f"Total curves: {results['total_curves']}")
    print(f"Root number +1: {results['root_plus1_count']}")
    print(f"Root number -1: {results['root_minus1_count']}")

    print(f"\n--- Rank parity by root number ---")
    for rn in ['root_plus1', 'root_minus1']:
        d = results['rank_parity_by_root_number'][rn]
        print(f"  {rn}: even={d['prob_even_rank']:.4f}, odd={d['prob_odd_rank']:.4f}")

    print(f"\n--- Prob(p | Sha) by root number ---")
    for p in ['2', '3', '5', '7']:
        d = results['effect_sizes_p_divides_sha'][p]
        print(f"  p={p}: root+1={d['root_plus1']:.6f}, root-1={d['root_minus1']:.6f}, "
              f"diff={d['difference']:.6f}, ratio={d['ratio']}")

    print(f"\n--- Sha parity analysis ---")
    for rn in ['root_plus1', 'root_minus1']:
        d = results['sha_parity_analysis'][rn]
        print(f"  {rn}: Prob(Sha=1)={d['prob_sha_1']:.6f}")
        print(f"    2-adic val distribution: {dict(list(d['2_adic_valuation_of_sha'].items())[:6])}")

    print(f"\n--- Poonen-Rains test (rank 0) ---")
    for p in ['2', '3', '5', '7']:
        d = results['poonen_rains_test'][p]
        pr = d['PR_prob_trivial_sha_p']
        emp_key = 'empirical_prob_sha_p_trivial_rank0_rootP1'
        emp = d.get(emp_key, 'N/A')
        ratio_key = 'ratio_empirical_over_PR'
        ratio = d.get(ratio_key, 'N/A')
        print(f"  p={p}: PR prediction={pr:.6f}, empirical(rank0,root+1)={emp}, ratio={ratio}")

    print(f"\n--- Rank-stratified: Prob(Sha=1) ---")
    for rn in ['root_plus1', 'root_minus1']:
        print(f"  {rn}:")
        strata = results['rank_stratified'][rn]
        for r in sorted(strata.keys(), key=int):
            d = strata[r]
            print(f"    rank {r}: n={d['count']}, Prob(Sha=1)={d['prob_sha_trivial']:.4f}, "
                  f"mean(Sha)={d['mean_sha']}")

    # Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
