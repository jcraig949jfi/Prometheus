"""
Test whether a_p sequence compressibility predicts elliptic curve rank.

Hypothesis: high-rank EC have constrained a_p values (from BSD), which might
make their coefficient sequences more or less compressible. This treats a_p
as an information-theoretic object, not an invariant.
"""

import json
import zlib
import struct
import math
import random
import numpy as np
from collections import Counter
from scipy import stats
import psycopg2

# ---------- helpers ----------

def traces_to_bytes(traces, n=50):
    """Convert first n trace values to a byte sequence."""
    vals = traces[:n]
    return struct.pack(f'{len(vals)}i', *vals)

def compressibility(data_bytes):
    """Compression ratio: compressed_len / original_len. Lower = more compressible."""
    if len(data_bytes) == 0:
        return 1.0
    compressed = zlib.compress(data_bytes, level=9)
    return len(compressed) / len(data_bytes)

def shannon_entropy(traces, n=50):
    """Shannon entropy of first n trace values."""
    vals = traces[:n]
    counts = Counter(vals)
    total = len(vals)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())

def lz_complexity(traces, n=50):
    """LZ complexity: number of distinct substrings in Lempel-Ziv decomposition."""
    s = ''.join(str(v) + ',' for v in traces[:n])
    n_len = len(s)
    i, complexity = 0, 0
    seen = set()
    current = ''
    for ch in s:
        current += ch
        if current not in seen:
            seen.add(current)
            complexity += 1
            current = ''
    if current:
        complexity += 1
    return complexity

def generate_random_control(traces_list, n=50):
    """Generate random integer sequences matching the range of actual traces."""
    all_vals = []
    for t in traces_list:
        all_vals.extend(t[:n])
    lo, hi = min(all_vals), max(all_vals)

    results = []
    for t in traces_list:
        length = min(len(t), n)
        fake = [random.randint(lo, hi) for _ in range(length)]
        results.append(fake)
    return results

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

    print("Pulling newform data...")
    cur.execute("""
        SELECT label, level, traces, analytic_rank
        FROM mf_newforms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        LIMIT 20000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"Retrieved {len(rows)} newforms")

    # Parse and filter
    records = []
    for label, level, traces, rank in rows:
        if traces is None or rank is None:
            continue
        # traces comes as a list from postgres
        if isinstance(traces, str):
            traces = json.loads(traces)
        if not isinstance(traces, (list, tuple)) or len(traces) < 10:
            continue
        # Ensure integers
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

    print(f"Valid records: {len(records)}")

    # Compute compressibility metrics
    print("Computing compressibility metrics...")
    for rec in records:
        t = rec['traces']
        b = traces_to_bytes(t)
        rec['compress_ratio'] = compressibility(b)
        rec['entropy'] = shannon_entropy(t)
        rec['lz_complexity'] = lz_complexity(t)

    # Stratify by rank
    rank_groups = {}
    for rec in records:
        r = rec['rank']
        if r >= 2:
            r = 2  # group 2+
        rank_groups.setdefault(r, []).append(rec)

    print("\n=== RESULTS BY RANK ===")
    summary = {}
    for r in sorted(rank_groups.keys()):
        grp = rank_groups[r]
        cr = [x['compress_ratio'] for x in grp]
        ent = [x['entropy'] for x in grp]
        lzc = [x['lz_complexity'] for x in grp]
        label = f"rank_{r}" if r < 2 else "rank_2+"
        summary[label] = {
            'count': len(grp),
            'compress_ratio_mean': float(np.mean(cr)),
            'compress_ratio_std': float(np.std(cr)),
            'compress_ratio_median': float(np.median(cr)),
            'entropy_mean': float(np.mean(ent)),
            'entropy_std': float(np.std(ent)),
            'lz_complexity_mean': float(np.mean(lzc)),
            'lz_complexity_std': float(np.std(lzc)),
        }
        print(f"\n{label} (n={len(grp)}):")
        print(f"  Compression ratio: {np.mean(cr):.4f} +/- {np.std(cr):.4f}")
        print(f"  Shannon entropy:   {np.mean(ent):.4f} +/- {np.std(ent):.4f}")
        print(f"  LZ complexity:     {np.mean(lzc):.1f} +/- {np.std(lzc):.1f}")

    # Correlation tests
    print("\n=== CORRELATION TESTS ===")
    ranks_all = [rec['rank'] for rec in records]
    cr_all = [rec['compress_ratio'] for rec in records]
    ent_all = [rec['entropy'] for rec in records]
    lzc_all = [rec['lz_complexity'] for rec in records]

    rho_cr, p_cr = stats.spearmanr(ranks_all, cr_all)
    rho_ent, p_ent = stats.spearmanr(ranks_all, ent_all)
    rho_lz, p_lz = stats.spearmanr(ranks_all, lzc_all)

    print(f"Spearman rho (rank vs compress_ratio): {rho_cr:.6f}, p={p_cr:.2e}")
    print(f"Spearman rho (rank vs entropy):        {rho_ent:.6f}, p={p_ent:.2e}")
    print(f"Spearman rho (rank vs lz_complexity):  {rho_lz:.6f}, p={p_lz:.2e}")

    correlations = {
        'compress_ratio': {'spearman_rho': float(rho_cr), 'p_value': float(p_cr)},
        'entropy': {'spearman_rho': float(rho_ent), 'p_value': float(p_ent)},
        'lz_complexity': {'spearman_rho': float(rho_lz), 'p_value': float(p_lz)},
    }

    # Mann-Whitney U between rank 0 and rank 1
    if 0 in rank_groups and 1 in rank_groups:
        cr0 = [x['compress_ratio'] for x in rank_groups[0]]
        cr1 = [x['compress_ratio'] for x in rank_groups[1]]
        u_stat, u_p = stats.mannwhitneyu(cr0, cr1, alternative='two-sided')
        ent0 = [x['entropy'] for x in rank_groups[0]]
        ent1 = [x['entropy'] for x in rank_groups[1]]
        u_ent_stat, u_ent_p = stats.mannwhitneyu(ent0, ent1, alternative='two-sided')

        # Effect size (rank-biserial correlation)
        n0, n1 = len(cr0), len(cr1)
        effect_size_cr = 1 - (2 * u_stat) / (n0 * n1)

        print(f"\nMann-Whitney U (rank0 vs rank1, compress_ratio): U={u_stat:.0f}, p={u_p:.2e}, r_rb={effect_size_cr:.4f}")
        print(f"Mann-Whitney U (rank0 vs rank1, entropy):        U={u_ent_stat:.0f}, p={u_ent_p:.2e}")

        correlations['mann_whitney_compress'] = {
            'U': float(u_stat), 'p_value': float(u_p),
            'rank_biserial': float(effect_size_cr)
        }
        correlations['mann_whitney_entropy'] = {
            'U': float(u_ent_stat), 'p_value': float(u_ent_p)
        }

    # Control: conductor-matched comparison
    # For rank-0 and rank-1 at same conductor level
    print("\n=== CONDUCTOR-MATCHED CONTROL ===")
    level_rank = {}
    for rec in records:
        level_rank.setdefault(rec['level'], {}).setdefault(rec['rank'], []).append(rec)

    matched_diffs_cr = []
    matched_diffs_ent = []
    matched_levels = []
    for level, rdict in level_rank.items():
        if 0 in rdict and 1 in rdict:
            mean_cr0 = np.mean([x['compress_ratio'] for x in rdict[0]])
            mean_cr1 = np.mean([x['compress_ratio'] for x in rdict[1]])
            mean_ent0 = np.mean([x['entropy'] for x in rdict[0]])
            mean_ent1 = np.mean([x['entropy'] for x in rdict[1]])
            matched_diffs_cr.append(mean_cr1 - mean_cr0)
            matched_diffs_ent.append(mean_ent1 - mean_ent0)
            matched_levels.append(level)

    conductor_matched = {}
    if matched_diffs_cr:
        t_cr, tp_cr = stats.ttest_1samp(matched_diffs_cr, 0)
        t_ent, tp_ent = stats.ttest_1samp(matched_diffs_ent, 0)
        print(f"Conductor-matched pairs: {len(matched_diffs_cr)}")
        print(f"Mean compress_ratio diff (rank1 - rank0): {np.mean(matched_diffs_cr):.6f}, t={t_cr:.3f}, p={tp_cr:.2e}")
        print(f"Mean entropy diff (rank1 - rank0):        {np.mean(matched_diffs_ent):.6f}, t={t_ent:.3f}, p={tp_ent:.2e}")
        conductor_matched = {
            'n_matched_levels': len(matched_diffs_cr),
            'compress_ratio_diff_mean': float(np.mean(matched_diffs_cr)),
            'compress_ratio_diff_t': float(t_cr),
            'compress_ratio_diff_p': float(tp_cr),
            'entropy_diff_mean': float(np.mean(matched_diffs_ent)),
            'entropy_diff_t': float(t_ent),
            'entropy_diff_p': float(tp_ent),
        }
    else:
        print("No conductor-matched rank-0/rank-1 pairs found.")

    # Random null model
    print("\n=== RANDOM NULL MODEL ===")
    random.seed(42)
    all_traces = [rec['traces'] for rec in records]
    fake_traces = generate_random_control(all_traces)

    fake_cr = [compressibility(traces_to_bytes(ft)) for ft in fake_traces]
    real_cr = [rec['compress_ratio'] for rec in records]

    print(f"Real compress_ratio mean:   {np.mean(real_cr):.4f} +/- {np.std(real_cr):.4f}")
    print(f"Random compress_ratio mean: {np.mean(fake_cr):.4f} +/- {np.std(fake_cr):.4f}")

    # Are real sequences more compressible than random?
    u_null, p_null = stats.mannwhitneyu(real_cr, fake_cr, alternative='two-sided')
    print(f"Mann-Whitney (real vs random): U={u_null:.0f}, p={p_null:.2e}")

    # Does the rank signal survive in random?
    fake_by_rank = {}
    for i, rec in enumerate(records):
        r = min(rec['rank'], 2)
        fake_by_rank.setdefault(r, []).append(fake_cr[i])

    null_summary = {
        'real_mean': float(np.mean(real_cr)),
        'real_std': float(np.std(real_cr)),
        'random_mean': float(np.mean(fake_cr)),
        'random_std': float(np.std(fake_cr)),
        'mann_whitney_U': float(u_null),
        'mann_whitney_p': float(p_null),
    }

    print("\nRandom null by rank assignment:")
    for r in sorted(fake_by_rank.keys()):
        vals = fake_by_rank[r]
        label = f"rank_{r}" if r < 2 else "rank_2+"
        print(f"  {label}: {np.mean(vals):.4f} +/- {np.std(vals):.4f}")
        null_summary[f'{label}_mean'] = float(np.mean(vals))
        null_summary[f'{label}_std'] = float(np.std(vals))

    # Assemble final output
    output = {
        'hypothesis': 'a_p sequence compressibility predicts elliptic curve rank',
        'data': {
            'source': 'LMFDB mf_newforms (weight=2, dim=1)',
            'total_records': len(records),
            'traces_length_used': 50,
        },
        'rank_stratified': summary,
        'correlations': correlations,
        'conductor_matched_control': conductor_matched,
        'random_null': null_summary,
        'verdict': None,  # filled below
    }

    # Determine verdict
    sig_threshold = 0.01
    any_sig = (p_cr < sig_threshold or p_ent < sig_threshold or p_lz < sig_threshold)
    conductor_sig = conductor_matched.get('compress_ratio_diff_p', 1.0) < sig_threshold

    if any_sig and conductor_sig:
        output['verdict'] = 'SIGNAL: compressibility correlates with rank, survives conductor matching'
    elif any_sig and not conductor_sig:
        output['verdict'] = 'CONFOUNDED: raw correlation exists but does not survive conductor matching — likely driven by level'
    else:
        output['verdict'] = 'NULL: no significant correlation between a_p compressibility and rank'

    print(f"\n=== VERDICT: {output['verdict']} ===")

    # Save
    outpath = 'D:/Prometheus/harmonia/results/ap_compression.json'
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {outpath}")

if __name__ == '__main__':
    main()
