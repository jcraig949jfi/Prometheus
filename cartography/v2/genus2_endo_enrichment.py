"""
Genus-2 Endomorphism Ring → Mod-p Fingerprint Enrichment Analysis

Hypothesis: The GL_2 enrichment slope law (0.044·rank² - 0.242) extends to genus-2,
with richer endomorphism algebras producing steeper mod-p enrichment slopes.

Approach:
1. Load genus-2 curves from LMFDB data (66K curves with equations + endo ring type)
2. Compute trace of Frobenius mod p for p=3,5,7,11 via point counting
3. Group by endomorphism type (Q, QxQ, CMxQ, M_2(Q), RM, M_2(CM), CM, QM)
4. Compute within-group enrichment: P(shared fingerprint | same group) / P(shared fingerprint | random)
5. Compute enrichment slope vs prime
6. Compare to GL_2 law
"""

import json
import os
import sys
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
import time

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'genus2', 'data', 'genus2_curves_lmfdb.json')
RESULTS_PATH = os.path.join(os.path.dirname(__file__), 'genus2_endo_enrichment_results.json')

PRIMES = [3, 5, 7, 11]

# Endomorphism algebra "richness" ranking (for slope comparison)
# Q = generic (GL_2-type, dimension 1)
# Q x Q = split (rank ~2 in some sense)
# RM = real multiplication (rank ~2)
# CM = complex multiplication (rank ~2)
# CM x Q = mixed (rank ~3)
# M_2(Q) = matrix algebra (rank ~4, QM-type)
# QM = quaternionic multiplication (rank ~4)
# M_2(CM) = full (rank ~8)
ENDO_RANK = {
    'Q': 1,
    'Q x Q': 2,
    'RM': 2,
    'CM': 2,
    'CM x Q': 3,
    'M_2(Q)': 4,
    'QM': 4,
    'M_2(CM)': 8,
}


def count_points_mod_p(f_coeffs, h_coeffs, p):
    """Count affine points on y^2 + h(x)*y = f(x) over F_p."""
    count = 0
    # Precompute powers of x
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

        # y^2 + hx*y - fx = 0 mod p
        for y in range(p):
            if (y * y + hx * y - fx) % p == 0:
                count += 1

    # Points at infinity
    deg_f = len(f_coeffs) - 1
    while deg_f > 0 and f_coeffs[deg_f] % p == 0:
        deg_f -= 1
    if deg_f % 2 == 1:
        count += 1
    else:
        lc = f_coeffs[deg_f] % p if deg_f >= 0 else 0
        if lc == 0:
            count += 1
        elif pow(lc, (p - 1) // 2, p) == 1:
            count += 2

    return count


def compute_trace(f_coeffs, h_coeffs, p):
    """Compute trace of Frobenius: a_p = p + 1 - #C(F_p)."""
    n = count_points_mod_p(f_coeffs, h_coeffs, p)
    return p + 1 - n


def parse_equation(eq):
    """Parse LMFDB equation format [[f_coeffs], [h_coeffs]]."""
    f_coeffs = eq[0]
    h_coeffs = eq[1]
    return f_coeffs, h_coeffs


def compute_enrichment(fingerprints_by_group, p):
    """
    Compute enrichment ratio for a given prime p.

    Enrichment = P(same fingerprint | same group) / P(same fingerprint | random)

    For each group, compute fraction of pairs sharing the same fingerprint mod p,
    then compare to the global random baseline.
    """
    # Global fingerprint distribution
    all_fps = []
    group_fps = {}

    for group, fps in fingerprints_by_group.items():
        if len(fps) < 10:  # skip tiny groups
            continue
        fp_list = [f % p for f in fps]
        group_fps[group] = fp_list
        all_fps.extend(fp_list)

    if not all_fps:
        return {}

    # Random baseline: probability two random curves share fingerprint
    global_counts = Counter(all_fps)
    n_total = len(all_fps)
    p_random = sum(c * (c - 1) for c in global_counts.values()) / (n_total * (n_total - 1)) if n_total > 1 else 0

    # Per-group enrichment
    results = {}
    for group, fp_list in group_fps.items():
        n = len(fp_list)
        if n < 2:
            continue
        counts = Counter(fp_list)
        p_same = sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))
        enrichment = p_same / p_random if p_random > 0 else 0
        results[group] = {
            'n_curves': n,
            'p_same_group': round(p_same, 6),
            'p_random': round(p_random, 6),
            'enrichment': round(enrichment, 4),
            'fingerprint_distribution': {str(k): v for k, v in sorted(counts.items())},
        }

    return results


def compute_enrichment_slopes(enrichment_by_prime):
    """
    For each endo group, fit enrichment vs log(p) to get slope.
    Also compute the GL_2 predicted slope from 0.044*rank^2 - 0.242.
    """
    groups = set()
    for p_data in enrichment_by_prime.values():
        groups.update(p_data.keys())

    slopes = {}
    for group in sorted(groups):
        primes_used = []
        enrichments = []
        for p in PRIMES:
            if group in enrichment_by_prime.get(p, {}):
                primes_used.append(p)
                enrichments.append(enrichment_by_prime[p][group]['enrichment'])

        if len(primes_used) < 2:
            continue

        log_primes = np.log(primes_used)
        enrichments = np.array(enrichments)

        # Linear fit: enrichment = slope * log(p) + intercept
        coeffs = np.polyfit(log_primes, enrichments, 1)
        slope = coeffs[0]
        intercept = coeffs[1]

        # GL_2 predicted slope
        rank = ENDO_RANK.get(group, 1)
        gl2_predicted = 0.044 * rank**2 - 0.242

        slopes[group] = {
            'endo_rank': rank,
            'enrichment_slope': round(float(slope), 6),
            'enrichment_intercept': round(float(intercept), 6),
            'gl2_predicted_slope': round(gl2_predicted, 6),
            'slope_ratio': round(float(slope) / gl2_predicted, 4) if gl2_predicted != 0 else None,
            'primes_used': primes_used,
            'enrichments': [round(e, 4) for e in enrichments.tolist()],
        }

    return slopes


def main():
    print("Loading genus-2 curves...")
    with open(DATA_PATH) as f:
        data = json.load(f)

    records = data['records']
    print(f"Total records: {len(records)}")

    # Count by endo type
    endo_counts = Counter(r['endomorphism_ring'] for r in records)
    print("\nEndomorphism ring distribution:")
    for k, v in endo_counts.most_common():
        print(f"  {k}: {v}")

    # Parse equations
    print("\nParsing equations...")
    curves = []
    parse_errors = 0
    for r in records:
        try:
            eq = json.loads(r['equation']) if isinstance(r['equation'], str) else r['equation']
            f_coeffs, h_coeffs = parse_equation(eq)
            curves.append({
                'label': r['label'],
                'conductor': r['conductor'],
                'endo_ring': r['endomorphism_ring'],
                'f_coeffs': f_coeffs,
                'h_coeffs': h_coeffs,
            })
        except Exception as e:
            parse_errors += 1

    print(f"Parsed: {len(curves)}, errors: {parse_errors}")

    # Sample for performance: use all curves for small groups, sample large groups
    MAX_PER_GROUP = 5000
    grouped = defaultdict(list)
    for c in curves:
        grouped[c['endo_ring']].append(c)

    sampled_curves = []
    for group, group_curves in grouped.items():
        if len(group_curves) > MAX_PER_GROUP:
            np.random.seed(42)
            indices = np.random.choice(len(group_curves), MAX_PER_GROUP, replace=False)
            sampled_curves.extend([group_curves[i] for i in indices])
            print(f"  Sampled {group}: {MAX_PER_GROUP}/{len(group_curves)}")
        else:
            sampled_curves.extend(group_curves)
            print(f"  Full {group}: {len(group_curves)}")

    print(f"\nTotal curves for analysis: {len(sampled_curves)}")

    # Compute traces
    print("\nComputing traces of Frobenius...")
    traces = defaultdict(lambda: defaultdict(list))  # traces[p][endo_group] = [trace_values]

    t0 = time.time()
    for i, c in enumerate(sampled_curves):
        if i % 2000 == 0 and i > 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            eta = (len(sampled_curves) - i) / rate
            print(f"  {i}/{len(sampled_curves)} ({rate:.0f} curves/s, ETA {eta:.0f}s)")

        for p in PRIMES:
            # Skip if conductor divisible by p (bad reduction)
            if c['conductor'] % p == 0:
                continue
            trace = compute_trace(c['f_coeffs'], c['h_coeffs'], p)
            traces[p][c['endo_ring']].append(trace)

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s")

    # Compute enrichment for each prime
    print("\nComputing enrichment...")
    enrichment_by_prime = {}
    for p in PRIMES:
        print(f"\n  p = {p}:")
        enrichment = compute_enrichment(traces[p], p)
        enrichment_by_prime[p] = enrichment
        for group, data in sorted(enrichment.items()):
            print(f"    {group:12s}: n={data['n_curves']:5d}, enrichment={data['enrichment']:.4f}")

    # Compute slopes
    print("\nComputing enrichment slopes...")
    slopes = compute_enrichment_slopes(enrichment_by_prime)

    print("\n" + "=" * 80)
    print("ENRICHMENT SLOPE RESULTS")
    print("=" * 80)
    print(f"{'Endo Ring':12s} {'Rank':4s} {'Slope':10s} {'GL2 Pred':10s} {'Ratio':8s} {'Enrichments'}")
    print("-" * 80)
    for group, s in sorted(slopes.items(), key=lambda x: x[1]['endo_rank']):
        pred = f"{s['gl2_predicted_slope']:.4f}" if s['gl2_predicted_slope'] is not None else "N/A"
        ratio = f"{s['slope_ratio']:.4f}" if s['slope_ratio'] is not None else "N/A"
        enrichments_str = ", ".join(f"p={p}:{e:.3f}" for p, e in zip(s['primes_used'], s['enrichments']))
        print(f"{group:12s} {s['endo_rank']:4d} {s['enrichment_slope']:10.4f} {pred:>10s} {ratio:>8s}   {enrichments_str}")

    # GL_2 law comparison
    print("\n" + "=" * 80)
    print("GL_2 LAW COMPARISON")
    print("=" * 80)

    ranks = []
    measured_slopes = []
    for group, s in slopes.items():
        ranks.append(s['endo_rank'])
        measured_slopes.append(s['enrichment_slope'])

    if len(ranks) >= 3:
        ranks_arr = np.array(ranks, dtype=float)
        slopes_arr = np.array(measured_slopes)

        # Fit: slope = a * rank^2 + b
        A = np.column_stack([ranks_arr**2, np.ones_like(ranks_arr)])
        result = np.linalg.lstsq(A, slopes_arr, rcond=None)
        a_fit, b_fit = result[0]

        print(f"\nGL_2 law:     slope = 0.044 * rank^2 - 0.242")
        print(f"Genus-2 fit:  slope = {a_fit:.4f} * rank^2 + ({b_fit:.4f})")
        print(f"\nCoefficient ratio (genus2/GL2): {a_fit/0.044:.4f}")
        print(f"Intercept shift: {b_fit - (-0.242):.4f}")

        # Residuals
        predicted = a_fit * ranks_arr**2 + b_fit
        residuals = slopes_arr - predicted
        rmse = np.sqrt(np.mean(residuals**2))
        print(f"RMSE of quadratic fit: {rmse:.6f}")

        gl2_law_comparison = {
            'gl2_law': {'a': 0.044, 'b': -0.242},
            'genus2_fit': {'a': round(float(a_fit), 6), 'b': round(float(b_fit), 6)},
            'coefficient_ratio': round(float(a_fit / 0.044), 4),
            'intercept_shift': round(float(b_fit + 0.242), 4),
            'rmse': round(float(rmse), 6),
        }
    else:
        gl2_law_comparison = {'note': 'insufficient groups for quadratic fit'}
        print("Insufficient groups with enough data for quadratic fit.")

    # Save results
    results = {
        'description': 'Genus-2 endomorphism ring -> mod-p fingerprint enrichment analysis',
        'hypothesis': 'GL_2 enrichment slope law (0.044*rank^2 - 0.242) extends to genus-2 with endo algebra rank',
        'primes': PRIMES,
        'n_curves_total': len(records),
        'n_curves_analyzed': len(sampled_curves),
        'endo_distribution': {k: v for k, v in endo_counts.most_common()},
        'enrichment_by_prime': {str(p): {
            group: {
                'n_curves': d['n_curves'],
                'enrichment': d['enrichment'],
                'p_same_group': d['p_same_group'],
                'p_random': d['p_random'],
            }
            for group, d in data.items()
        } for p, data in enrichment_by_prime.items()},
        'enrichment_slopes': slopes,
        'gl2_law_comparison': gl2_law_comparison,
    }

    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == '__main__':
    main()
