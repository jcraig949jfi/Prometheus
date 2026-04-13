"""
Sato-Tate weighted compression test for a_p sequences.

Standard compression (LZ/zlib) treats a_p values as uniform symbols -- null result (rho=0.017).
But a_p values follow the Sato-Tate distribution (semicircle) for non-CM curves.
The SURPRISE of each a_p under the ST model measures information content BEYOND the
expected distribution. If rank constrains a_p (BSD), high-rank curves should show
systematically different cross-entropy vs the ST baseline.

Key metric: cross-entropy of theta_p sequence against the Sato-Tate semicircle PDF,
where theta_p = a_p / (2*sqrt(p)).
"""

import json
import math
import numpy as np
from scipy import stats
from sympy import isprime, primerange
import psycopg2

# ---------- Sato-Tate helpers ----------

def sato_tate_pdf(x):
    """Semicircle distribution PDF on [-1, 1]: (2/pi) * sqrt(1 - x^2)."""
    if abs(x) >= 1.0:
        return 1e-15  # clamp to avoid log(0)
    return (2.0 / math.pi) * math.sqrt(1.0 - x * x)

def sato_tate_surprise(x):
    """Surprise (self-information) of x under Sato-Tate: -log2(P_ST(x))."""
    pdf_val = sato_tate_pdf(x)
    return -math.log2(max(pdf_val, 1e-15))

def extract_ap_at_primes(traces, max_primes=100):
    """
    traces[n] = a_n (trace of T_n on the newform).
    Extract a_p at prime indices p (0-indexed: traces[p-1] = a_p for p >= 2).
    Returns list of (p, a_p) pairs.
    """
    result = []
    n_traces = len(traces)
    for p in primerange(2, n_traces + 1):
        a_p = traces[p - 1]  # traces is 0-indexed, a_1=traces[0], a_2=traces[1], etc.
        result.append((int(p), int(a_p)))
        if len(result) >= max_primes:
            break
    return result

def compute_st_cross_entropy(prime_ap_pairs):
    """
    Compute cross-entropy of the theta_p sequence against Sato-Tate.
    theta_p = a_p / (2*sqrt(p))
    Returns (total_surprise, mean_surprise, n_primes, thetas).
    """
    surprises = []
    thetas = []
    for p, a_p in prime_ap_pairs:
        theta_p = a_p / (2.0 * math.sqrt(p))
        # Clamp to [-1, 1] (should already be there by Hasse bound, but numerical safety)
        theta_p = max(-0.9999, min(0.9999, theta_p))
        thetas.append(theta_p)
        surprises.append(sato_tate_surprise(theta_p))

    if not surprises:
        return 0.0, 0.0, 0, []

    total = sum(surprises)
    mean = total / len(surprises)
    return total, mean, len(surprises), thetas

def compute_st_kl_divergence(thetas, n_bins=50):
    """
    Empirical KL divergence: D_KL(empirical || Sato-Tate).
    Discretize into bins on [-1, 1], compute KL.
    """
    if len(thetas) < 10:
        return float('nan')

    bin_edges = np.linspace(-1, 1, n_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = 2.0 / n_bins

    # Empirical histogram
    counts, _ = np.histogram(thetas, bins=bin_edges)
    empirical = counts / counts.sum()

    # ST expected
    st_probs = np.array([sato_tate_pdf(c) * bin_width for c in bin_centers])
    st_probs = st_probs / st_probs.sum()  # normalize

    # KL divergence (only where empirical > 0)
    kl = 0.0
    for i in range(n_bins):
        if empirical[i] > 0 and st_probs[i] > 0:
            kl += empirical[i] * math.log2(empirical[i] / st_probs[i])

    return float(kl)


# ---------- main ----------

def main():
    print("Connecting to LMFDB...")
    conn = psycopg2.connect(
        host='devmirror.lmfdb.xyz',
        port=5432,
        dbname='lmfdb',
        user='lmfdb',
        password='lmfdb'
    )
    cur = conn.cursor()

    print("Pulling newform data (weight=2, dim=1, ordered by level)...")
    cur.execute("""
        SELECT label, level, traces, analytic_rank
        FROM mf_newforms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level
        LIMIT 10000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"Retrieved {len(rows)} newforms")

    # Precompute primes up to max traces length for efficiency
    # (sympy primerange is fast enough but let's cache)

    # Parse and filter: need at least 100 traces
    MIN_TRACES = 100
    records = []
    for label, level, traces, rank in rows:
        if traces is None or rank is None:
            continue
        if isinstance(traces, str):
            traces = json.loads(traces)
        if not isinstance(traces, (list, tuple)) or len(traces) < MIN_TRACES:
            continue
        try:
            traces = [int(x) for x in traces]
        except (ValueError, TypeError):
            continue
        records.append({
            'label': label,
            'level': int(level),
            'traces': traces,
            'rank': int(rank)
        })
        if len(records) >= 5000:
            break

    print(f"Valid records with >= {MIN_TRACES} traces: {len(records)}")

    # Compute Sato-Tate cross-entropy for each form
    print("Computing Sato-Tate cross-entropy metrics...")
    for i, rec in enumerate(records):
        if (i + 1) % 500 == 0:
            print(f"  Processing {i+1}/{len(records)}...")

        prime_ap = extract_ap_at_primes(rec['traces'], max_primes=100)
        total_surp, mean_surp, n_primes, thetas = compute_st_cross_entropy(prime_ap)
        kl_div = compute_st_kl_divergence(thetas)

        rec['st_total_surprise'] = total_surp
        rec['st_mean_surprise'] = mean_surp
        rec['st_n_primes'] = n_primes
        rec['st_kl_divergence'] = kl_div
        rec['thetas'] = thetas  # keep for analysis

    # Theoretical ST cross-entropy: H(ST) = -integral of P_ST(x) * log2(P_ST(x)) dx
    # For the semicircle (2/pi)*sqrt(1-x^2), the entropy is known:
    # H = log2(pi/2) - 1/(2*ln2) ≈ 0.6515 - 0.7213 ≈ ... let's compute numerically
    from scipy.integrate import quad
    def st_entropy_integrand(x):
        p = sato_tate_pdf(x)
        if p <= 0:
            return 0.0
        return -p * math.log2(p)
    h_st, _ = quad(st_entropy_integrand, -1, 1)
    print(f"\nSato-Tate entropy H(ST) = {h_st:.6f} bits")
    print(f"(Mean surprise should converge to H(ST) for ST-distributed data)")

    # Stratify by rank
    rank_groups = {}
    for rec in records:
        r = min(rec['rank'], 2)
        rank_groups.setdefault(r, []).append(rec)

    print("\n=== RESULTS BY RANK (Sato-Tate cross-entropy) ===")
    summary = {}
    for r in sorted(rank_groups.keys()):
        grp = rank_groups[r]
        mean_surp = [x['st_mean_surprise'] for x in grp]
        total_surp = [x['st_total_surprise'] for x in grp]
        kl = [x['st_kl_divergence'] for x in grp if not math.isnan(x['st_kl_divergence'])]
        label = f"rank_{r}" if r < 2 else "rank_2+"
        summary[label] = {
            'count': len(grp),
            'mean_surprise_mean': float(np.mean(mean_surp)),
            'mean_surprise_std': float(np.std(mean_surp)),
            'mean_surprise_median': float(np.median(mean_surp)),
            'total_surprise_mean': float(np.mean(total_surp)),
            'total_surprise_std': float(np.std(total_surp)),
            'kl_divergence_mean': float(np.mean(kl)) if kl else None,
            'kl_divergence_std': float(np.std(kl)) if kl else None,
            'excess_vs_st_entropy': float(np.mean(mean_surp) - h_st),
        }
        print(f"\n{label} (n={len(grp)}):")
        print(f"  Mean surprise:    {np.mean(mean_surp):.6f} +/- {np.std(mean_surp):.6f} bits")
        print(f"  Excess vs H(ST):  {np.mean(mean_surp) - h_st:.6f} bits")
        print(f"  Total surprise:   {np.mean(total_surp):.2f} +/- {np.std(total_surp):.2f} bits")
        if kl:
            print(f"  KL(empirical||ST): {np.mean(kl):.6f} +/- {np.std(kl):.6f} bits")

    # Correlation tests
    print("\n=== CORRELATION TESTS ===")
    ranks_all = [rec['rank'] for rec in records]
    mean_surp_all = [rec['st_mean_surprise'] for rec in records]
    total_surp_all = [rec['st_total_surprise'] for rec in records]
    kl_all = [rec['st_kl_divergence'] for rec in records]

    rho_ms, p_ms = stats.spearmanr(ranks_all, mean_surp_all)
    rho_ts, p_ts = stats.spearmanr(ranks_all, total_surp_all)
    # KL may have NaN, filter
    valid_kl = [(r, k) for r, k in zip(ranks_all, kl_all) if not math.isnan(k)]
    if valid_kl:
        rho_kl, p_kl = stats.spearmanr([x[0] for x in valid_kl], [x[1] for x in valid_kl])
    else:
        rho_kl, p_kl = float('nan'), float('nan')

    print(f"Spearman rho (rank vs mean_surprise):  {rho_ms:.6f}, p={p_ms:.2e}")
    print(f"Spearman rho (rank vs total_surprise):  {rho_ts:.6f}, p={p_ts:.2e}")
    print(f"Spearman rho (rank vs KL divergence):   {rho_kl:.6f}, p={p_kl:.2e}")

    correlations = {
        'mean_surprise': {'spearman_rho': float(rho_ms), 'p_value': float(p_ms)},
        'total_surprise': {'spearman_rho': float(rho_ts), 'p_value': float(p_ts)},
        'kl_divergence': {'spearman_rho': float(rho_kl), 'p_value': float(p_kl)},
    }

    # Mann-Whitney U between rank 0 and rank 1
    mw_results = {}
    if 0 in rank_groups and 1 in rank_groups:
        ms0 = [x['st_mean_surprise'] for x in rank_groups[0]]
        ms1 = [x['st_mean_surprise'] for x in rank_groups[1]]
        u_stat, u_p = stats.mannwhitneyu(ms0, ms1, alternative='two-sided')
        n0, n1 = len(ms0), len(ms1)
        effect_size = 1 - (2 * u_stat) / (n0 * n1)
        cohens_d = (np.mean(ms1) - np.mean(ms0)) / np.sqrt((np.std(ms0)**2 + np.std(ms1)**2) / 2)

        print(f"\nMann-Whitney U (rank0 vs rank1, mean_surprise): U={u_stat:.0f}, p={u_p:.2e}")
        print(f"  Rank-biserial r = {effect_size:.4f}")
        print(f"  Cohen's d = {cohens_d:.4f}")
        print(f"  Rank-0 mean: {np.mean(ms0):.6f}, Rank-1 mean: {np.mean(ms1):.6f}")
        print(f"  Difference: {np.mean(ms1) - np.mean(ms0):.6f} bits")

        # Also test KL divergence
        kl0 = [x['st_kl_divergence'] for x in rank_groups[0] if not math.isnan(x['st_kl_divergence'])]
        kl1 = [x['st_kl_divergence'] for x in rank_groups[1] if not math.isnan(x['st_kl_divergence'])]
        if kl0 and kl1:
            u_kl, p_kl_mw = stats.mannwhitneyu(kl0, kl1, alternative='two-sided')
            print(f"Mann-Whitney U (rank0 vs rank1, KL div): U={u_kl:.0f}, p={p_kl_mw:.2e}")
            mw_results['kl_divergence'] = {'U': float(u_kl), 'p_value': float(p_kl_mw)}

        mw_results['mean_surprise'] = {
            'U': float(u_stat), 'p_value': float(u_p),
            'rank_biserial': float(effect_size),
            'cohens_d': float(cohens_d),
            'rank0_mean': float(np.mean(ms0)),
            'rank1_mean': float(np.mean(ms1)),
            'difference_bits': float(np.mean(ms1) - np.mean(ms0)),
        }

    # Conductor-matched control
    print("\n=== CONDUCTOR-MATCHED CONTROL ===")
    level_rank = {}
    for rec in records:
        level_rank.setdefault(rec['level'], {}).setdefault(rec['rank'], []).append(rec)

    matched_diffs_ms = []
    matched_diffs_kl = []
    matched_levels = []
    for level, rdict in level_rank.items():
        if 0 in rdict and 1 in rdict:
            mean_ms0 = np.mean([x['st_mean_surprise'] for x in rdict[0]])
            mean_ms1 = np.mean([x['st_mean_surprise'] for x in rdict[1]])
            matched_diffs_ms.append(mean_ms1 - mean_ms0)

            kl0 = [x['st_kl_divergence'] for x in rdict[0] if not math.isnan(x['st_kl_divergence'])]
            kl1 = [x['st_kl_divergence'] for x in rdict[1] if not math.isnan(x['st_kl_divergence'])]
            if kl0 and kl1:
                matched_diffs_kl.append(np.mean(kl1) - np.mean(kl0))
            matched_levels.append(level)

    conductor_matched = {}
    if matched_diffs_ms:
        t_ms, tp_ms = stats.ttest_1samp(matched_diffs_ms, 0)
        print(f"Conductor-matched pairs: {len(matched_diffs_ms)}")
        print(f"Mean surprise diff (rank1 - rank0): {np.mean(matched_diffs_ms):.6f}, t={t_ms:.3f}, p={tp_ms:.2e}")
        conductor_matched['n_matched_levels'] = len(matched_diffs_ms)
        conductor_matched['mean_surprise_diff_mean'] = float(np.mean(matched_diffs_ms))
        conductor_matched['mean_surprise_diff_t'] = float(t_ms)
        conductor_matched['mean_surprise_diff_p'] = float(tp_ms)

        if matched_diffs_kl:
            t_kl, tp_kl = stats.ttest_1samp(matched_diffs_kl, 0)
            print(f"KL div diff (rank1 - rank0): {np.mean(matched_diffs_kl):.6f}, t={t_kl:.3f}, p={tp_kl:.2e}")
            conductor_matched['kl_diff_mean'] = float(np.mean(matched_diffs_kl))
            conductor_matched['kl_diff_t'] = float(t_kl)
            conductor_matched['kl_diff_p'] = float(tp_kl)
    else:
        print("No conductor-matched rank-0/rank-1 pairs found.")

    # Level-binned control: partial correlation removing level effect
    print("\n=== PARTIAL CORRELATION (removing level effect) ===")
    levels_all = np.array([rec['level'] for rec in records], dtype=float)
    ranks_arr = np.array(ranks_all, dtype=float)
    ms_arr = np.array(mean_surp_all, dtype=float)

    # Partial Spearman: regress out level from both rank and mean_surprise
    from scipy.stats import spearmanr
    # Rank-transform for partial Spearman
    rank_of_rank = stats.rankdata(ranks_arr)
    rank_of_ms = stats.rankdata(ms_arr)
    rank_of_level = stats.rankdata(levels_all)

    # Residualize
    slope_r, intercept_r, _, _, _ = stats.linregress(rank_of_level, rank_of_rank)
    resid_rank = rank_of_rank - (slope_r * rank_of_level + intercept_r)

    slope_m, intercept_m, _, _, _ = stats.linregress(rank_of_level, rank_of_ms)
    resid_ms = rank_of_ms - (slope_m * rank_of_level + intercept_m)

    partial_rho, partial_p = stats.pearsonr(resid_rank, resid_ms)
    print(f"Partial Spearman (rank vs mean_surprise | level): rho={partial_rho:.6f}, p={partial_p:.2e}")

    partial_corr = {
        'partial_spearman_rho': float(partial_rho),
        'partial_spearman_p': float(partial_p),
    }

    # Permutation null: shuffle ranks, recompute correlation
    print("\n=== PERMUTATION NULL (1000 shuffles) ===")
    np.random.seed(42)
    n_perms = 1000
    null_rhos = []
    for _ in range(n_perms):
        shuffled = np.random.permutation(ranks_arr)
        r, _ = stats.spearmanr(shuffled, ms_arr)
        null_rhos.append(r)

    observed_rho = rho_ms
    perm_p = np.mean(np.abs(null_rhos) >= abs(observed_rho))
    print(f"Observed rho: {observed_rho:.6f}")
    print(f"Null distribution: mean={np.mean(null_rhos):.6f}, std={np.std(null_rhos):.6f}")
    print(f"Permutation p-value: {perm_p:.4f}")

    perm_null = {
        'observed_rho': float(observed_rho),
        'null_mean': float(np.mean(null_rhos)),
        'null_std': float(np.std(null_rhos)),
        'permutation_p': float(perm_p),
        'n_permutations': n_perms,
    }

    # Assemble output
    output = {
        'hypothesis': 'Sato-Tate cross-entropy of a_p sequence discriminates rank',
        'method': (
            'For each newform, compute theta_p = a_p/(2*sqrt(p)) at prime indices. '
            'Under Sato-Tate, theta_p ~ semicircle on [-1,1]. '
            'Surprise = -log2(P_ST(theta_p)). '
            'Cross-entropy = mean surprise measures deviation from ST baseline. '
            'Rank information (BSD constraints) should appear as systematic excess/deficit.'
        ),
        'data': {
            'source': 'LMFDB mf_newforms (weight=2, dim=1)',
            'total_records': len(records),
            'min_traces': MIN_TRACES,
            'primes_used': records[0]['st_n_primes'] if records else 0,
        },
        'sato_tate_entropy_bits': float(h_st),
        'rank_stratified': summary,
        'correlations': correlations,
        'mann_whitney': mw_results,
        'conductor_matched_control': conductor_matched,
        'partial_correlation_control': partial_corr,
        'permutation_null': perm_null,
        'prior_test_comparison': {
            'standard_compression_rho': 0.017,
            'standard_compression_verdict': 'NULL',
        },
        'verdict': None,
    }

    # Determine verdict
    sig = 0.01
    raw_sig = p_ms < sig
    conductor_sig = conductor_matched.get('mean_surprise_diff_p', 1.0) < sig
    partial_sig = partial_p < sig
    perm_sig = perm_p < sig

    if raw_sig and conductor_sig and partial_sig:
        output['verdict'] = (
            'SIGNAL: ST cross-entropy correlates with rank, '
            'survives conductor matching AND partial correlation control'
        )
    elif raw_sig and (conductor_sig or partial_sig):
        output['verdict'] = (
            'POSSIBLE: ST cross-entropy shows raw correlation with rank, '
            'partially survives controls'
        )
    elif raw_sig:
        output['verdict'] = (
            'CONFOUNDED: raw ST cross-entropy correlation exists but '
            'does not survive conductor/level controls'
        )
    else:
        output['verdict'] = (
            'NULL: no significant correlation between ST cross-entropy and rank'
        )

    print(f"\n=== VERDICT: {output['verdict']} ===")

    # Save
    outpath = 'D:/Prometheus/harmonia/results/st_weighted_compression.json'
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {outpath}")

if __name__ == '__main__':
    main()
