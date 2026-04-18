#!/usr/bin/env python3
"""
Wachs (2026) First-Zero Displacement Reproduction on LMFDB Data
Literature Q3 / P6: Does first-zero displacement predict gap-variance suppression?

Wachs found: |Sha| >= 4 curves have first zeros displaced higher and subsequent
zeros more tightly packed, surviving controls for L(1,E), real period, and conductor.

We reproduce:
  1. Sha-stratified z1, gap1, gap-variance, mean-all-gaps
  2. Conductor-decile control
  3. Stable Faltings height quintile control (period proxy)
  4. P6 prediction: correlation(delta_z1, delta_var) across Sha bins

Gaudin GUE nearest-neighbor variance: 4 - pi ~ 0.178
"""

import json
import sys
import numpy as np
import psycopg2
from collections import defaultdict
from scipy import stats as sp_stats

DB_PARAMS = dict(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
GAUDIN_VAR = 4.0 - np.pi  # ~0.178


# ── Parsing ──────────────────────────────────────────────────────────────────

def parse_zeros(raw):
    """Parse positive_zeros from postgres text -> list of floats."""
    if raw is None:
        return None
    if isinstance(raw, (list, tuple)):
        try:
            return [float(z) for z in raw]
        except (ValueError, TypeError):
            return None
    s = str(raw).strip()
    if s in ('', '[]', '{}', 'None'):
        return None
    s = s.replace('{', '[').replace('}', ']')
    try:
        vals = json.loads(s)
        return [float(z) for z in vals]
    except Exception:
        return None


# ── Per-curve metrics ────────────────────────────────────────────────────────

def curve_metrics(zeros):
    """Return (z1, gap1, gap1_normalized, all_gaps_normalized) or None."""
    if zeros is None or len(zeros) < 3:
        return None
    zeros = sorted(zeros)
    z1 = zeros[0]
    gaps = [zeros[i+1] - zeros[i] for i in range(len(zeros) - 1)]
    mean_gap = np.mean(gaps)
    if mean_gap <= 0:
        return None
    norm_gaps = [g / mean_gap for g in gaps]
    return z1, gaps[0], norm_gaps[0], norm_gaps


# ── Sha group statistics ────────────────────────────────────────────────────

def sha_group_stats(records, min_count=20):
    """
    records: list of (sha, conductor, faltings_height, zeros_raw)
    Returns dict: sha_val -> {n, mean_z1, mean_gap1, var_gap1_norm, mean_all_gaps_norm}
    """
    buckets = defaultdict(lambda: dict(z1=[], gap1=[], gap1_norm=[], all_gaps_norm=[]))
    for sha, cond, fh, zeros_raw in records:
        zeros = parse_zeros(zeros_raw)
        m = curve_metrics(zeros)
        if m is None:
            continue
        z1, gap1, gap1_norm, all_gaps_norm = m
        buckets[sha]['z1'].append(z1)
        buckets[sha]['gap1'].append(gap1)
        buckets[sha]['gap1_norm'].append(gap1_norm)
        buckets[sha]['all_gaps_norm'].extend(all_gaps_norm)

    out = {}
    for sha_val, d in sorted(buckets.items()):
        n = len(d['z1'])
        if n < min_count:
            continue
        out[sha_val] = dict(
            n=n,
            mean_z1=np.mean(d['z1']),
            mean_gap1=np.mean(d['gap1']),
            var_gap1_norm=np.var(d['gap1_norm'], ddof=1) if n > 1 else np.nan,
            mean_all_gaps_norm=np.mean(d['all_gaps_norm']),
        )
    return out


def print_sha_table(sha_stats, label=""):
    """Pretty-print Sha group statistics."""
    if label:
        print(f"\n{'='*80}")
        print(f"  {label}")
        print(f"{'='*80}")
    print(f"{'Sha':>6} {'N':>8} {'mean_z1':>10} {'mean_gap1':>10} "
          f"{'var(gap1)':>10} {'var/Gaud':>10} {'mean_gaps':>10}")
    print("-" * 76)
    for sha_val, s in sorted(sha_stats.items()):
        ratio = s['var_gap1_norm'] / GAUDIN_VAR if not np.isnan(s['var_gap1_norm']) else np.nan
        print(f"{sha_val:>6} {s['n']:>8} {s['mean_z1']:>10.6f} {s['mean_gap1']:>10.6f} "
              f"{s['var_gap1_norm']:>10.6f} {ratio:>10.4f} {s['mean_all_gaps_norm']:>10.6f}")


# ── Controlled analysis ─────────────────────────────────────────────────────

def controlled_analysis(records, control_col_idx, n_quantiles, control_name):
    """
    Stratify by quantiles of a control variable, then compute Sha stats within each stratum.
    records: list of (sha, conductor, faltings_height, zeros_raw)
    control_col_idx: 1 for conductor, 2 for faltings_height
    """
    print(f"\n{'#'*80}")
    print(f"  CONTROLLED BY {control_name} ({n_quantiles} quantiles)")
    print(f"{'#'*80}")

    # Filter valid control values
    valid = [(r, r[control_col_idx]) for r in records if r[control_col_idx] is not None]
    if not valid:
        print("  No valid control values found.")
        return {}

    control_vals = np.array([v for _, v in valid])
    quantile_edges = np.quantile(control_vals, np.linspace(0, 1, n_quantiles + 1))

    all_stratum_stats = {}
    for q in range(n_quantiles):
        lo, hi = quantile_edges[q], quantile_edges[q + 1]
        if q == n_quantiles - 1:
            stratum = [r for r, v in valid if lo <= v <= hi]
        else:
            stratum = [r for r, v in valid if lo <= v < hi]

        label = f"{control_name} Q{q+1}: [{lo:.4f}, {hi:.4f}]  (n={len(stratum)})"
        s = sha_group_stats(stratum, min_count=10)
        if s:
            print_sha_table(s, label)
            all_stratum_stats[q] = s

    return all_stratum_stats


# ── P6 prediction test ──────────────────────────────────────────────────────

def p6_displacement_variance_correlation(sha_stats):
    """
    P6: Does delta_z1(Sha) predict delta_var(Sha)?
    Compute correlation between first-zero displacement and gap variance across Sha bins.
    """
    print(f"\n{'='*80}")
    print("  P6: DISPLACEMENT-VARIANCE CORRELATION")
    print(f"{'='*80}")

    if len(sha_stats) < 3:
        print("  Too few Sha groups for correlation test.")
        return

    sha_vals = sorted(sha_stats.keys())
    z1_means = np.array([sha_stats[s]['mean_z1'] for s in sha_vals])
    gap_vars = np.array([sha_stats[s]['var_gap1_norm'] for s in sha_vals])
    ns = np.array([sha_stats[s]['n'] for s in sha_vals])

    # Delta from Sha=1 baseline
    baseline_z1 = sha_stats.get(1, sha_stats[sha_vals[0]])['mean_z1']
    baseline_var = sha_stats.get(1, sha_stats[sha_vals[0]])['var_gap1_norm']
    delta_z1 = z1_means - baseline_z1
    delta_var = gap_vars - baseline_var

    print(f"\n  Sha bins: {sha_vals}")
    print(f"  N per bin: {ns.tolist()}")
    print(f"  z1 means:  {[f'{v:.6f}' for v in z1_means]}")
    print(f"  gap1 var:  {[f'{v:.6f}' for v in gap_vars]}")
    print(f"  delta_z1:  {[f'{v:.6f}' for v in delta_z1]}")
    print(f"  delta_var: {[f'{v:.6f}' for v in delta_var]}")

    # Pearson correlation
    if len(sha_vals) >= 3:
        r_pearson, p_pearson = sp_stats.pearsonr(delta_z1, delta_var)
        print(f"\n  Pearson r(delta_z1, delta_var) = {r_pearson:.4f}  (p = {p_pearson:.4g})")
    else:
        r_pearson = np.nan
        print("\n  Too few points for Pearson.")

    # Spearman (rank) correlation
    if len(sha_vals) >= 3:
        r_spearman, p_spearman = sp_stats.spearmanr(delta_z1, delta_var)
        print(f"  Spearman r(delta_z1, delta_var) = {r_spearman:.4f}  (p = {p_spearman:.4g})")
    else:
        r_spearman = np.nan

    # Weighted correlation (by sqrt(N))
    if len(sha_vals) >= 3:
        w = np.sqrt(ns.astype(float))
        wm_z1 = np.average(delta_z1, weights=w)
        wm_var = np.average(delta_var, weights=w)
        cov = np.average((delta_z1 - wm_z1) * (delta_var - wm_var), weights=w)
        std_z1 = np.sqrt(np.average((delta_z1 - wm_z1)**2, weights=w))
        std_var = np.sqrt(np.average((delta_var - wm_var)**2, weights=w))
        r_weighted = cov / (std_z1 * std_var) if std_z1 > 0 and std_var > 0 else np.nan
        print(f"  Weighted r(delta_z1, delta_var) = {r_weighted:.4f}  (weights=sqrt(N))")

    # Interpretation
    print(f"\n  VERDICT: ", end="")
    if abs(r_pearson) > 0.7 and not np.isnan(r_pearson):
        print("STRONG correlation — displacement predicts variance suppression")
    elif abs(r_pearson) > 0.4 and not np.isnan(r_pearson):
        print("MODERATE correlation — partial prediction")
    else:
        print("WEAK/NO correlation — displacement and variance are independent channels")

    return dict(r_pearson=r_pearson, r_spearman=r_spearman)


# ── Wachs direction tests ───────────────────────────────────────────────────

def wachs_direction_tests(sha_stats):
    """Test Wachs's specific directional predictions."""
    print(f"\n{'='*80}")
    print("  WACHS DIRECTION TESTS")
    print(f"{'='*80}")

    sha_vals = sorted(sha_stats.keys())
    if 1 not in sha_stats:
        print("  No Sha=1 baseline; using smallest Sha group.")

    baseline_sha = 1 if 1 in sha_stats else sha_vals[0]
    large_sha = [s for s in sha_vals if s >= 4]

    if not large_sha:
        print("  No Sha >= 4 groups with sufficient data.")
        return

    b = sha_stats[baseline_sha]
    print(f"\n  Baseline (Sha={baseline_sha}): z1={b['mean_z1']:.6f}, "
          f"gap1={b['mean_gap1']:.6f}, var={b['var_gap1_norm']:.6f}")

    for sha_val in large_sha:
        s = sha_stats[sha_val]
        z1_up = s['mean_z1'] > b['mean_z1']
        gap_tight = s['mean_gap1'] < b['mean_gap1']
        var_down = s['var_gap1_norm'] < b['var_gap1_norm']

        print(f"\n  Sha={sha_val} (n={s['n']}):")
        print(f"    z1 displaced UP:      {'YES' if z1_up else 'NO'}  "
              f"({s['mean_z1']:.6f} vs {b['mean_z1']:.6f}, "
              f"delta={s['mean_z1'] - b['mean_z1']:+.6f})")
        print(f"    gap1 tighter:         {'YES' if gap_tight else 'NO'}  "
              f"({s['mean_gap1']:.6f} vs {b['mean_gap1']:.6f}, "
              f"delta={s['mean_gap1'] - b['mean_gap1']:+.6f})")
        print(f"    gap1 var suppressed:  {'YES' if var_down else 'NO'}  "
              f"({s['var_gap1_norm']:.6f} vs {b['var_gap1_norm']:.6f}, "
              f"delta={s['var_gap1_norm'] - b['var_gap1_norm']:+.6f})")

        # Mann-Whitney U test: z1 distribution
        # (we don't have individual values here, but we can note the effect size)
        if s['n'] >= 20 and b['n'] >= 20:
            cohen_d_z1 = (s['mean_z1'] - b['mean_z1']) / np.sqrt(
                (b['var_gap1_norm'] + s['var_gap1_norm']) / 2) if (b['var_gap1_norm'] + s['var_gap1_norm']) > 0 else 0
            print(f"    Effect size (z1 shift / pooled gap-var SD): {cohen_d_z1:.4f}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Wachs (2026) First-Zero Displacement Reproduction")
    print("=" * 80)

    # ── 1. Query ─────────────────────────────────────────────────────────────
    print("\n[1] Querying rank-0 curves with zeros from LMFDB...")
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    query = """
    SELECT e.sha::int, e.conductor::float, e.stable_faltings_height::float, l.positive_zeros
    FROM ec_curvedata e
    JOIN lfunc_lfunctions l
      ON l.origin = 'EllipticCurve/Q/' || split_part(e.lmfdb_iso, '.', 1)
                     || '/' || split_part(e.lmfdb_iso, '.', 2)
    WHERE e.rank::int = 0
      AND l.positive_zeros IS NOT NULL
      AND l.positive_zeros != '[]'
      AND e.sha::int >= 1
    LIMIT 200000
    """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"  Fetched {len(rows)} curves.")
    if len(rows) == 0:
        print("  ERROR: No data returned. Check table/column names.")
        sys.exit(1)

    # Convert to records: (sha, conductor, faltings_height, zeros_raw)
    records = [(int(r[0]), r[1], r[2], r[3]) for r in rows]

    # Distribution of Sha values
    sha_counts = defaultdict(int)
    for sha, _, _, _ in records:
        sha_counts[sha] += 1
    print(f"\n  Sha distribution:")
    for s in sorted(sha_counts.keys())[:20]:
        print(f"    Sha={s}: {sha_counts[s]}")
    if len(sha_counts) > 20:
        print(f"    ... ({len(sha_counts)} distinct Sha values total)")

    # ── 2. Overall Sha stratification ────────────────────────────────────────
    print("\n[2] Sha-stratified zero statistics (no controls)...")
    sha_stats = sha_group_stats(records, min_count=20)
    print_sha_table(sha_stats, "OVERALL SHA STRATIFICATION")

    # ── 3. Wachs direction tests ─────────────────────────────────────────────
    print("\n[3] Wachs direction tests...")
    wachs_direction_tests(sha_stats)

    # ── 4. Conductor control (deciles) ───────────────────────────────────────
    print("\n[4] Conductor-controlled analysis...")
    cond_strata = controlled_analysis(records, control_col_idx=1, n_quantiles=10,
                                       control_name="Conductor")

    # ── 5. Faltings height control (quintiles) ───────────────────────────────
    print("\n[5] Faltings-height-controlled analysis...")
    fh_strata = controlled_analysis(records, control_col_idx=2, n_quantiles=5,
                                     control_name="Faltings Height")

    # ── 6. P6 prediction: displacement-variance correlation ──────────────────
    print("\n[6] P6 prediction test...")
    p6_result = p6_displacement_variance_correlation(sha_stats)

    # ── 7. Robustness: does the correlation survive controls? ────────────────
    print(f"\n{'='*80}")
    print("  ROBUSTNESS: P6 WITHIN CONDUCTOR DECILES")
    print(f"{'='*80}")
    for q, stratum_stats in sorted(cond_strata.items()):
        if len(stratum_stats) >= 3:
            sha_vals = sorted(stratum_stats.keys())
            z1s = [stratum_stats[s]['mean_z1'] for s in sha_vals]
            vrs = [stratum_stats[s]['var_gap1_norm'] for s in sha_vals]
            if len(z1s) >= 3:
                r, p = sp_stats.pearsonr(z1s, vrs)
                print(f"  Conductor Q{q+1}: r={r:.4f} (p={p:.4g}, n_sha_bins={len(sha_vals)})")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print("  SUMMARY")
    print(f"{'='*80}")
    print(f"  Total curves analyzed: {len(records)}")
    print(f"  Sha groups with n>=20: {len(sha_stats)}")
    if sha_stats:
        sha1 = sha_stats.get(1, {})
        sha4plus = {k: v for k, v in sha_stats.items() if k >= 4}
        if sha1 and sha4plus:
            avg_z1_large = np.mean([v['mean_z1'] for v in sha4plus.values()])
            avg_var_large = np.mean([v['var_gap1_norm'] for v in sha4plus.values()])
            print(f"  Sha=1 baseline: z1={sha1['mean_z1']:.6f}, var={sha1['var_gap1_norm']:.6f}")
            print(f"  Sha>=4 average:  z1={avg_z1_large:.6f}, var={avg_var_large:.6f}")
            print(f"  z1 displacement: {avg_z1_large - sha1['mean_z1']:+.6f}")
            print(f"  var suppression: {avg_var_large - sha1['var_gap1_norm']:+.6f}")
    if p6_result:
        print(f"  P6 Pearson r: {p6_result['r_pearson']:.4f}")
        print(f"  P6 Spearman r: {p6_result['r_spearman']:.4f}")
    print()


if __name__ == '__main__':
    main()
