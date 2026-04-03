"""
BSD Invariant Experiments — Sha Stratification & Spectral Tail Decomposition
=============================================================================
Triggered by: Wachs (2026) finding that Sha order displaces the first zero.

Experiment 1 (Sha Stratification Kill Test):
  Stratify rank-0 ECs by Sha order. Re-run first-zero ablation within each stratum.
  If ablation improvement vanishes when Sha is controlled → first zero noise IS Sha.
  If it persists → something beyond Sha confounds the first zero.

Experiment 2 (BSD Invariant Decomposition):
  For each BSD invariant (sha, regulator, faltings_height, degree/modular_degree),
  test correlation with position in zeros 5-19 space, controlling for rank and conductor.
"""

import duckdb
import numpy as np
import logging
import json
from collections import defaultdict
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.linear_model import Ridge
from scipy import stats

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"
REPORT_DIR = Path(__file__).parent.parent / "reports"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.bsd_experiments')


def load_ec_data():
    """Load ECs with zeros and BSD invariants."""
    duck = duckdb.connect(str(DB_PATH), read_only=True)
    rows = duck.execute("""
        SELECT ec.object_id, ec.lmfdb_iso, ec.conductor, ec.rank, ec.analytic_rank,
               ec.sha, ec.regulator, ec.faltings_height, ec.degree, ec.torsion,
               ec.manin_constant, ec.cm,
               oz.zeros_vector, oz.n_zeros_stored
        FROM elliptic_curves ec
        JOIN object_zeros oz ON ec.object_id = oz.object_id
        WHERE oz.zeros_vector IS NOT NULL
          AND ec.sha IS NOT NULL
        ORDER BY ec.object_id
    """).fetchall()
    duck.close()

    # Dedup by isogeny class
    seen_iso = set()
    data = []
    for (oid, iso, cond, rank, arank, sha, reg, fh, deg, tor, manin, cm,
         zvec, nz) in rows:
        if iso in seen_iso:
            continue
        seen_iso.add(iso)
        # zeros_vector layout: [20 zero slots (None-padded), root_number, analytic_rank, degree, log_cond]
        n = min(nz or 0, 20)
        zeros = np.array([float(zvec[i]) if i < n and zvec[i] is not None else 0.0
                          for i in range(20)])
        if n < 20:
            continue  # Skip objects with fewer than 20 zeros — can't do full ablation
        data.append({
            'id': oid, 'iso': iso, 'conductor': int(cond),
            'rank': int(rank or 0), 'analytic_rank': int(arank or 0),
            'sha': int(sha), 'regulator': float(reg) if reg else None,
            'faltings_height': float(fh) if fh else None,
            'modular_degree': int(deg) if deg else None,
            'torsion': int(tor or 0), 'manin': int(manin or 0), 'cm': int(cm or 0),
            'zeros': zeros,
        })
    return data


def ablation_ari(objects, zero_slice, target='rank'):
    """Compute ARI for rank clustering using a specific zero slice, within conductor strata."""
    by_cond = defaultdict(list)
    for obj in objects:
        by_cond[obj['conductor']].append(obj)

    eligible = {c: objs for c, objs in by_cond.items() if len(objs) >= 5}
    aris = []
    for cond, objs in eligible.items():
        X = np.array([o['zeros'][zero_slice] for o in objs])
        true_labels = [o[target] for o in objs]
        if len(set(true_labels)) < 2:
            continue
        k = max(2, min(len(objs) // 2, 5))
        pred = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
        aris.append(adjusted_rand_score(true_labels, pred))
    return np.mean(aris) if aris else 0.0, len(aris)


# ================================================================
# EXPERIMENT 1: Sha Stratification Kill Test
# ================================================================

def experiment_1_sha_stratification(data):
    """
    Kill test: The original ablation clusters rank-0 + rank-1 together.
    If Sha variance in the rank-0 population is what makes the first zero noisy,
    then restricting rank-0 to Sha=1 (removing Sha variance) should eliminate
    the ablation improvement.

    Method: keep ALL rank-1 ECs, vary which rank-0 ECs we include.
    """
    log.info("=" * 70)
    log.info("EXPERIMENT 1: SHA STRATIFICATION KILL TEST")
    log.info("=" * 70)

    rank0 = [d for d in data if d['rank'] == 0]
    rank1 = [d for d in data if d['rank'] == 1]
    log.info(f"Rank-0 ECs: {len(rank0)}, Rank-1 ECs: {len(rank1)}")

    # Sha distribution within rank 0
    sha_counts = defaultdict(int)
    for d in rank0:
        sha_counts[d['sha']] += 1
    log.info("Sha distribution (rank 0):")
    for s in sorted(sha_counts):
        log.info(f"  Sha={s}: {sha_counts[s]}")

    configs = {
        'all_20':     slice(0, 20),
        'drop_1':     slice(1, 20),
        'drop_2':     slice(2, 20),
        'zeros_5_19': slice(4, 20),
        'first_only': slice(0, 1),
    }

    # A. Baseline: ALL rank-0 + rank-1 (reproduce original ablation)
    all_ec = rank0 + rank1
    log.info(f"\n--- A. Baseline: ALL ECs (n={len(all_ec)}) ---")
    baseline_results = {}
    for name, sl in configs.items():
        ari, n_strata = ablation_ari(all_ec, sl)
        baseline_results[name] = ari
        log.info(f"  {name:15s}: ARI = {ari:.4f} ({n_strata} strata)")

    # B. Sha-controlled: Sha=1 rank-0 + ALL rank-1
    sha1_r0 = [d for d in rank0 if d['sha'] == 1]
    controlled = sha1_r0 + rank1
    log.info(f"\n--- B. Sha-controlled: Sha=1 rank-0 + ALL rank-1 (n={len(controlled)}) ---")
    controlled_results = {}
    for name, sl in configs.items():
        ari, n_strata = ablation_ari(controlled, sl)
        controlled_results[name] = ari
        log.info(f"  {name:15s}: ARI = {ari:.4f} ({n_strata} strata)")

    # C. Sha-enriched: Sha>1 rank-0 + ALL rank-1 (amplify Sha confound)
    sha_gt1_r0 = [d for d in rank0 if d['sha'] > 1]
    enriched = sha_gt1_r0 + rank1
    log.info(f"\n--- C. Sha-enriched: Sha>1 rank-0 + ALL rank-1 (n={len(enriched)}) ---")
    enriched_results = {}
    for name, sl in configs.items():
        ari, n_strata = ablation_ari(enriched, sl)
        enriched_results[name] = ari
        log.info(f"  {name:15s}: ARI = {ari:.4f} ({n_strata} strata)")

    # D. THE KILL TEST
    log.info("\n--- D. KILL TEST VERDICT ---")
    base_delta = baseline_results['zeros_5_19'] - baseline_results['all_20']
    ctrl_delta = controlled_results['zeros_5_19'] - controlled_results['all_20']
    enr_delta  = enriched_results['zeros_5_19'] - enriched_results['all_20']

    log.info(f"  Baseline ablation delta:     {base_delta:+.4f}")
    log.info(f"  Sha-controlled delta:        {ctrl_delta:+.4f}")
    log.info(f"  Sha-enriched delta:          {enr_delta:+.4f}")

    if abs(ctrl_delta) < 0.002:
        verdict = "KILLED"
        log.info("  VERDICT: KILLED — Ablation improvement vanishes when Sha is controlled.")
        log.info("           The first zero's noise IS Sha.")
    elif ctrl_delta > 0.002:
        verdict = "SURVIVED"
        log.info("  VERDICT: SURVIVED — Ablation improvement persists within Sha=1.")
        log.info("           Something beyond Sha confounds the first zero.")
    else:
        verdict = "REVERSED"
        log.info("  VERDICT: REVERSED — Ablation HURTS when Sha is controlled.")

    if enr_delta > base_delta * 1.5:
        log.info("  BONUS: Sha-enriched amplifies the effect → Sha is part of the mechanism.")
    elif abs(enr_delta - base_delta) < 0.002:
        log.info("  BONUS: Sha-enriched has no extra effect → Sha is NOT the mechanism.")

    # E. First-zero statistics by Sha group (Wachs replication)
    log.info("\n--- E. First-zero displacement by Sha (Wachs replication) ---")
    for sha_val in sorted(sha_counts):
        group = [d for d in rank0 if d['sha'] == sha_val]
        if len(group) < 10:
            continue
        z1 = np.array([d['zeros'][0] for d in group])
        log.info(f"  Sha={sha_val:>2}: n={len(group):>5}, first_zero mean={z1.mean():.6f}, "
                 f"std={z1.std():.6f}, median={np.median(z1):.6f}")

    sha1_objs = [d for d in rank0 if d['sha'] == 1]
    sha_gt1_objs = [d for d in rank0 if d['sha'] > 1]
    z1_sha1 = np.array([d['zeros'][0] for d in sha1_objs])
    z1_sha_gt1 = np.array([d['zeros'][0] for d in sha_gt1_objs]) if sha_gt1_objs else np.array([])
    if len(z1_sha_gt1) > 10:
        t_stat, p_val = stats.ttest_ind(z1_sha1, z1_sha_gt1)
        cohens_d = (z1_sha_gt1.mean() - z1_sha1.mean()) / np.sqrt(
            (z1_sha1.std()**2 + z1_sha_gt1.std()**2) / 2)
        log.info(f"\n  Sha=1 vs Sha>1 first zero: t={t_stat:.4f}, p={p_val:.2e}, Cohen's d={cohens_d:.4f}")

    return verdict, baseline_results, controlled_results, enriched_results


# ================================================================
# EXPERIMENT 2: BSD Invariant Decomposition
# ================================================================

def experiment_2_bsd_decomposition(data):
    """
    For each BSD invariant, measure:
    1. Correlation with first-zero position (controlling for conductor)
    2. Correlation with spectral tail centroid (zeros 5-19 mean)
    3. Predictive R² of invariant → zero position via Ridge regression
    4. Variance explained per zero index (which invariant maps to which zero?)
    """
    log.info("=" * 70)
    log.info("EXPERIMENT 2: BSD INVARIANT DECOMPOSITION")
    log.info("=" * 70)

    rank0 = [d for d in data if d['rank'] == 0]
    log.info(f"Rank-0 ECs: {len(rank0)}")

    # BSD invariants to test
    invariants = ['sha', 'regulator', 'faltings_height', 'modular_degree']

    # A. Per-invariant correlation with each zero index
    log.info("\n--- A. Partial correlation: BSD invariant vs each zero index ---")
    log.info("       (controlling for log(conductor))")

    results = {}
    for inv_name in invariants:
        eligible = [d for d in rank0 if d[inv_name] is not None and d[inv_name] != 0]
        if len(eligible) < 100:
            log.info(f"  {inv_name}: skipped (n={len(eligible)} < 100)")
            continue

        inv_vals = np.array([d[inv_name] for d in eligible], dtype=float)
        log_cond = np.log(np.array([d['conductor'] for d in eligible], dtype=float))
        zeros_mat = np.array([d['zeros'] for d in eligible])

        # Log-transform skewed invariants
        if inv_name in ('sha', 'modular_degree'):
            inv_vals = np.log1p(inv_vals)

        # Partial correlation: regress out conductor from both
        inv_resid = inv_vals - Ridge(alpha=1.0).fit(log_cond.reshape(-1, 1), inv_vals).predict(log_cond.reshape(-1, 1))

        corrs_by_zero = []
        for zi in range(20):
            z_col = zeros_mat[:, zi]
            z_resid = z_col - Ridge(alpha=1.0).fit(log_cond.reshape(-1, 1), z_col).predict(log_cond.reshape(-1, 1))
            r, p = stats.pearsonr(inv_resid, z_resid)
            corrs_by_zero.append((r, p))

        results[inv_name] = corrs_by_zero

        # Print: first 4 zeros and tail (5-19)
        log.info(f"\n  {inv_name} (n={len(eligible)}):")
        for zi in range(4):
            r, p = corrs_by_zero[zi]
            sig = "***" if p < 0.001 else "** " if p < 0.01 else "*  " if p < 0.05 else "   "
            log.info(f"    zero {zi+1:2d}: r={r:+.4f} p={p:.2e} {sig}")
        # Tail summary
        tail_rs = [corrs_by_zero[zi][0] for zi in range(4, 20)]
        tail_ps = [corrs_by_zero[zi][1] for zi in range(4, 20)]
        log.info(f"    zeros 5-20: mean |r|={np.mean(np.abs(tail_rs)):.4f}, "
                 f"max |r|={np.max(np.abs(tail_rs)):.4f}, "
                 f"n_sig(p<0.01)={sum(1 for p in tail_ps if p < 0.01)}/16")

    # B. Separate conductor R² from BSD-only R²
    log.info("\n--- B. Variance decomposition: conductor vs BSD (per zero index) ---")
    log.info("       Model 1: log(cond) only → R²_cond")
    log.info("       Model 2: log(cond) + BSD → R²_full")
    log.info("       BSD increment: R²_full - R²_cond")

    # Filter: need non-constant regulator (skip for rank 0) and valid BSD invariants
    bsd_inv = ['sha', 'faltings_height', 'modular_degree']  # regulator=1 for all rank-0
    eligible = [d for d in rank0
                if all(d[inv] is not None for inv in bsd_inv) and d['modular_degree'] != 0]

    if len(eligible) > 100:
        log.info(f"  Using {len(eligible)} rank-0 ECs with all BSD invariants")

        log_cond = np.log(np.array([d['conductor'] for d in eligible], dtype=float)).reshape(-1, 1)
        X_bsd = np.column_stack([
            np.log1p(np.array([d['sha'] for d in eligible], dtype=float)),
            np.array([d['faltings_height'] for d in eligible], dtype=float),
            np.log1p(np.array([d['modular_degree'] for d in eligible], dtype=float)),
        ])
        X_full = np.column_stack([log_cond, X_bsd])

        r2_cond_list, r2_full_list, r2_bsd_list = [], [], []
        for zi in range(20):
            y = np.array([d['zeros'][zi] for d in eligible])
            ss_tot = np.sum((y - y.mean()) ** 2)
            if ss_tot == 0:
                r2_cond_list.append(0); r2_full_list.append(0); r2_bsd_list.append(0)
                continue

            # Conductor-only model
            m1 = Ridge(alpha=1.0).fit(log_cond, y)
            r2_c = 1 - np.sum((y - m1.predict(log_cond))**2) / ss_tot

            # Full model (conductor + BSD)
            m2 = Ridge(alpha=1.0).fit(X_full, y)
            r2_f = 1 - np.sum((y - m2.predict(X_full))**2) / ss_tot

            r2_bsd = r2_f - r2_c
            r2_cond_list.append(r2_c); r2_full_list.append(r2_f); r2_bsd_list.append(r2_bsd)

            tag = "<<<" if r2_bsd > 0.01 else ""
            log.info(f"    zero {zi+1:2d}: R²_cond={r2_c:.4f}  R²_full={r2_f:.4f}  "
                     f"BSD_increment={r2_bsd:+.4f} {tag}")

        log.info(f"\n  Summary:")
        log.info(f"    First 4 zeros:  mean R²_cond={np.mean(r2_cond_list[:4]):.4f}, "
                 f"mean BSD_incr={np.mean(r2_bsd_list[:4]):.4f}")
        log.info(f"    Zeros 5-20:     mean R²_cond={np.mean(r2_cond_list[4:]):.4f}, "
                 f"mean BSD_incr={np.mean(r2_bsd_list[4:]):.4f}")

        if np.mean(r2_bsd_list[:4]) > 3 * np.mean(r2_bsd_list[4:]):
            log.info("  FINDING: BSD signal concentrated in central zeros. Tail is BSD-independent.")
        elif np.mean(r2_bsd_list[4:]) > np.mean(r2_bsd_list[:4]):
            log.info("  FINDING: BSD signal STRONGER in tail than central zeros. Unexpected.")
        else:
            log.info("  FINDING: BSD signal spreads across all zeros, no clean separation.")

    return results


# ================================================================
# MAIN
# ================================================================

def main():
    log.info("Loading EC data with BSD invariants...")
    data = load_ec_data()
    log.info(f"Loaded {len(data)} ECs (deduplicated by isogeny class)")

    # Experiment 1
    verdict, baseline_res, controlled_res, enriched_res = experiment_1_sha_stratification(data)

    # Experiment 2
    corr_results = experiment_2_bsd_decomposition(data)

    log.info("\n" + "=" * 70)
    log.info("ALL EXPERIMENTS COMPLETE")
    log.info("=" * 70)


if __name__ == "__main__":
    main()
