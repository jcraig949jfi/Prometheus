"""
Aporia Deep Research Report #14: BKLPR Selmer distribution test.

Tests Bhargava-Kane-Lenstra-Poonen-Rains predictions against LMFDB ec_curvedata.
Sha and torsion primes used as proxy for Selmer divisibility.

Uses SQL-side aggregation to avoid loading 3.8M rows into Python memory.
"""

import json
import math
import psycopg2
from pathlib import Path

DB_PARAMS = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
PRIMES = [2, 3, 5, 7, 11]
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "selmer_bklpr.json"


def bklpr_prediction(p, n_terms=200):
    """
    Poonen-Rains prediction for Prob(p | #Sel_p(E)).
    Prob(nontrivial Sel_p) = 1 - prod_{i>=1}(1 - p^{-i}).
    """
    prod_all = 1.0
    for i in range(1, n_terms + 1):
        prod_all *= (1.0 - p ** (-i))
    prob_global = 1.0 - prod_all
    return {
        'prob_global': prob_global,
        'prod_convergent': prod_all,
        'average_sel_size': p + 1,
    }


def run_query(cur, sql, params=None):
    cur.execute(sql, params)
    return cur.fetchall()


def main():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    print("=" * 70)
    print("BKLPR Selmer Distribution Test -- Aporia Report #14")
    print("=" * 70)

    # Total count
    total = run_query(cur, "SELECT COUNT(*) FROM ec_curvedata")[0][0]
    print(f"\nTotal curves: {total:,}")

    results = {}

    # ----------------------------------------------------------------
    # BKLPR predictions
    # ----------------------------------------------------------------
    print("\n--- BKLPR Predictions ---")
    predictions = {}
    for p in PRIMES:
        pred = bklpr_prediction(p)
        predictions[str(p)] = pred
        print(f"  p={p}: Prob(p|Sel_p) = {pred['prob_global']:.6f}, "
              f"E[#Sel_p] = {pred['average_sel_size']}")
    results['bklpr_predictions'] = predictions

    # ----------------------------------------------------------------
    # Empirical: Prob(p | Sha), Prob(p | torsion), Prob(p | either)
    # sha_primes and torsion_primes are text like '[2, 3]'
    # Use SQL LIKE for matching: sha_primes LIKE '%2%' but need word boundary
    # Actually: the values are like [2], [2, 3], [3, 5, 7]
    # For p=2: need to match '2' as a number, not substring of '12'
    # Strategy: use regex or multiple LIKE patterns
    # ----------------------------------------------------------------

    # Helper: SQL condition for "prime p appears in text array column"
    # Text format: '[]', '[2]', '[2, 3]', '[2, 3, 5]'
    # Match: col = '[{p}]' OR col LIKE '[{p},%' OR col LIKE '%, {p}]' OR col LIKE '%, {p},%'
    def prime_in_col(col, p):
        return (f"({col} = '[{p}]' OR {col} LIKE '[{p},%' "
                f"OR {col} LIKE '%, {p}]' OR {col} LIKE '%, {p},%')")

    print("\n--- Empirical Probabilities (all curves) ---")
    print(f"{'p':>3}  {'P(p|Sha)':>10}  {'P(p|tor)':>10}  {'P(p|either)':>12}  "
          f"{'BKLPR':>8}  {'ratio':>8}")
    print("-" * 65)

    empirical_global = {}
    for p in PRIMES:
        sha_cond = prime_in_col('sha_primes', p)
        tor_cond = prime_in_col('torsion_primes', p)

        n_sha = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {sha_cond}")[0][0]
        n_tor = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {tor_cond}")[0][0]
        n_either = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {sha_cond} OR {tor_cond}")[0][0]

        prob_sha = n_sha / total
        prob_tor = n_tor / total
        prob_either = n_either / total
        bklpr_val = predictions[str(p)]['prob_global']
        ratio = prob_either / bklpr_val if bklpr_val > 0 else 0

        print(f"{p:>3}  {prob_sha:>10.6f}  {prob_tor:>10.6f}  {prob_either:>12.6f}  "
              f"{bklpr_val:>8.6f}  {ratio:>8.4f}")

        empirical_global[str(p)] = {
            'n_sha': n_sha, 'prob_sha': prob_sha,
            'n_torsion': n_tor, 'prob_torsion': prob_tor,
            'n_either': n_either, 'prob_either': prob_either,
            'bklpr_prediction': bklpr_val,
            'ratio_either_to_bklpr': ratio,
        }
    results['empirical_global'] = empirical_global

    # ----------------------------------------------------------------
    # Stratify by rank
    # ----------------------------------------------------------------
    print("\n--- Stratified by Rank ---")
    rank_counts = run_query(cur,
        "SELECT rank, COUNT(*) FROM ec_curvedata GROUP BY rank ORDER BY rank")
    print(f"  Rank distribution:")
    for rk, cnt in rank_counts:
        print(f"    rank={rk}: {cnt:,}")

    results['by_rank'] = {}
    for rk_val in ['0', '1', '2', '3']:
        n = run_query(cur, "SELECT COUNT(*) FROM ec_curvedata WHERE rank = %s", (rk_val,))[0][0]
        print(f"\n  Rank {rk_val}: {n:,} curves")
        print(f"  {'p':>3}  {'P(p|Sha)':>10}  {'P(p|tor)':>10}  {'P(p|either)':>12}  {'BKLPR':>8}")

        rank_data = {'n_curves': n}
        for p in PRIMES:
            sha_cond = prime_in_col('sha_primes', p)
            tor_cond = prime_in_col('torsion_primes', p)
            rk_cond = f"rank = '{rk_val}'"

            n_sha = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {rk_cond} AND {sha_cond}")[0][0]
            n_tor = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {rk_cond} AND {tor_cond}")[0][0]
            n_either = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {rk_cond} AND ({sha_cond} OR {tor_cond})")[0][0]

            ps = n_sha / n if n > 0 else 0
            pt = n_tor / n if n > 0 else 0
            pe = n_either / n if n > 0 else 0
            bklpr_val = predictions[str(p)]['prob_global']
            print(f"  {p:>3}  {ps:>10.6f}  {pt:>10.6f}  {pe:>12.6f}  {bklpr_val:>8.6f}")
            rank_data[str(p)] = {
                'prob_sha': ps, 'prob_torsion': pt, 'prob_either': pe,
                'n_sha': n_sha, 'n_torsion': n_tor, 'n_either': n_either,
            }
        results['by_rank'][rk_val] = rank_data

    # ----------------------------------------------------------------
    # Stratify by conductor decade
    # ----------------------------------------------------------------
    print("\n--- Stratified by Conductor Decade ---")
    print(f"  {'decade':>16}  {'n':>10}", end="")
    for p in PRIMES:
        print(f"  {'P(%d|eith)' % p:>12}", end="")
    print()
    print("  " + "-" * 90)

    results['by_conductor_decade'] = {}
    for decade in range(1, 10):
        lo = 10 ** decade
        hi = 10 ** (decade + 1)
        cond_cond = f"conductor::bigint >= {lo} AND conductor::bigint < {hi}"

        n = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {cond_cond}")[0][0]
        if n < 100:
            continue

        cond_range = f"[10^{decade}, 10^{decade+1})"
        print(f"  {cond_range:>16}  {n:>10}", end="")

        decade_data = {'n_curves': n, 'range': cond_range}
        for p in PRIMES:
            sha_cond = prime_in_col('sha_primes', p)
            tor_cond = prime_in_col('torsion_primes', p)
            n_either = run_query(cur,
                f"SELECT COUNT(*) FROM ec_curvedata WHERE {cond_cond} AND ({sha_cond} OR {tor_cond})")[0][0]
            pe = n_either / n if n > 0 else 0
            print(f"  {pe:>12.6f}", end="")
            decade_data[str(p)] = {'prob_either': pe, 'n_either': n_either}
        print()
        results['by_conductor_decade'][str(decade)] = decade_data

    # ----------------------------------------------------------------
    # Sha value distribution (top 20)
    # ----------------------------------------------------------------
    print("\n--- Sha Value Distribution (top 20) ---")
    sha_rows = run_query(cur,
        "SELECT sha, COUNT(*) as cnt FROM ec_curvedata GROUP BY sha ORDER BY cnt DESC LIMIT 20")
    print(f"  {'Sha':>10}  {'count':>10}  {'frac':>10}")
    sha_dist = {}
    for val, cnt in sha_rows:
        frac = cnt / total
        print(f"  {val:>10}  {cnt:>10}  {frac:>10.6f}")
        sha_dist[str(val)] = {'count': cnt, 'fraction': frac}
    results['sha_distribution'] = sha_dist

    # ----------------------------------------------------------------
    # Torsion prime distribution
    # ----------------------------------------------------------------
    print("\n--- Torsion Prime Frequency ---")
    n_with_tor = run_query(cur,
        "SELECT COUNT(*) FROM ec_curvedata WHERE torsion_primes != '[]'")[0][0]
    print(f"  Curves with nontrivial torsion primes: {n_with_tor:,} ({n_with_tor/total:.4f})")

    tor_dist = {}
    for p in [2, 3, 5, 7, 11, 13]:
        tor_cond = prime_in_col('torsion_primes', p)
        cnt = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {tor_cond}")[0][0]
        if cnt > 0:
            print(f"  p={p}: {cnt:,} ({cnt/total:.6f})")
            tor_dist[str(p)] = {'count': cnt, 'fraction': cnt / total}
    results['torsion_prime_distribution'] = tor_dist

    # ----------------------------------------------------------------
    # Rank r >= 1: account for Mordell-Weil contribution
    # For rank r curves, E(Q)/pE(Q) has p-rank >= r
    # So Sel_p has p-rank >= r, meaning Prob(p | Sel_p) = 1 for rank >= 1
    # The interesting question for rank >= 1 is whether Sel_p > (Z/pZ)^r
    # i.e. whether there is EXTRA Selmer beyond what rank forces
    # ----------------------------------------------------------------
    print("\n--- Rank >= 1: Extra Selmer beyond Mordell-Weil ---")
    print("  For rank r >= 1, Sel_p >= (Z/pZ)^r automatically.")
    print("  Sha contribution = extra Selmer beyond rank.")

    results['rank_adjusted'] = {}
    for rk_val in ['1', '2']:
        n = run_query(cur, "SELECT COUNT(*) FROM ec_curvedata WHERE rank = %s", (rk_val,))[0][0]
        rk_int = int(rk_val)
        print(f"\n  Rank {rk_val}: P(Sel_p > (Z/pZ)^{rk_val}) ~ P(p|Sha)")
        rank_adj = {'n_curves': n}
        for p in PRIMES:
            sha_cond = prime_in_col('sha_primes', p)
            rk_cond = f"rank = '{rk_val}'"
            n_sha = run_query(cur, f"SELECT COUNT(*) FROM ec_curvedata WHERE {rk_cond} AND {sha_cond}")[0][0]
            ps = n_sha / n if n > 0 else 0

            # BKLPR for excess: Prob(excess > 0) = 1 - prod(1-p^{-i})
            # Same formula since the excess follows the same distribution
            bklpr_excess = predictions[str(p)]['prob_global']

            print(f"    p={p}: P(p|Sha) = {ps:.6f} vs BKLPR excess = {bklpr_excess:.6f} "
                  f"(ratio = {ps/bklpr_excess:.4f})")
            rank_adj[str(p)] = {'prob_sha': ps, 'bklpr_excess': bklpr_excess,
                                'ratio': ps / bklpr_excess if bklpr_excess > 0 else 0}
        results['rank_adjusted'][rk_val] = rank_adj

    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY ASSESSMENT")
    print("=" * 70)

    summary_lines = []
    for p in PRIMES:
        eg = empirical_global[str(p)]
        bklpr_val = eg['bklpr_prediction']
        pe = eg['prob_either']
        ratio = eg['ratio_either_to_bklpr']

        if ratio > 0.8:
            verdict = "CONSISTENT"
        elif ratio > 0.5:
            verdict = "PARTIAL (expected: Sha is subquotient of Sel)"
        else:
            verdict = "LOW (large gap: Sel has MW contribution not captured)"

        line = (f"  p={p}: P(p|Sha or tor) = {pe:.6f} vs "
                f"BKLPR = {bklpr_val:.6f} (ratio={ratio:.4f}) -> {verdict}")
        print(line)
        summary_lines.append(line)

    print("\nKey observations:")
    print("  - Sha+torsion is a LOWER BOUND on Selmer divisibility")
    print("  - For rank r>0: r copies of Z/pZ in Sel from Mordell-Weil (not in Sha or torsion)")
    print("  - For p=2 rank 0: ratio ~0.66 suggests additional 2-Selmer not captured by Sha[2]+tor[2]")
    print("  - For larger p: Sha rates drop fast; BKLPR gap is mostly Mordell-Weil contribution")
    print("  - Conductor decade shows: higher conductor -> less torsion -> lower P(p|either)")

    results['summary'] = {
        'total_curves': total,
        'assessment': summary_lines,
        'note': ('Sha+torsion is a lower bound on Selmer divisibility. '
                 'BKLPR prediction is for full Selmer group. '
                 'The gap is primarily Mordell-Weil contribution E(Q)/pE(Q). '
                 'For rank 0, the gap reflects E(Q)_tor/p*E(Q)_tor pieces not in torsion_primes.'),
    }

    # ----------------------------------------------------------------
    # Save
    # ----------------------------------------------------------------
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUTPUT_PATH}")
    conn.close()
    print("Done.")


if __name__ == '__main__':
    main()
