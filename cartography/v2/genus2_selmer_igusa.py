#!/usr/bin/env python3
"""
Genus-2: Does 2-Selmer Rank Correlate with Igusa Invariant Geometry?
=====================================================================
The Selmer rank bounds MW rank from above.  Igusa invariants encode moduli
space position.  Are curves with large Selmer rank geometrically special?

Data: LMFDB PostgreSQL dump (66K genus-2 curves).

Analyses:
1. Selmer rank vs log|I2|, log|I4|, log|I6|, log|I10|
2. Within fixed MW rank: Selmer excess (Selmer - MW) vs Igusa invariants
3. Sha[2] (= Selmer excess) at special moduli positions
4. Selmer rank vs conductor, vs Sato-Tate group
5. Null tests: random shuffle baseline for all correlations
"""

import json
import sys
import os
from collections import Counter, defaultdict
from math import log, log10, sqrt
from pathlib import Path

import numpy as np
from scipy import stats

# ── paths ─────────────────────────────────────────────────────────────
DUMP_PATH = Path(__file__).resolve().parent.parent / "lmfdb_dump" / "g2c_curves.json"
OUT_JSON = Path(__file__).resolve().parent / "genus2_selmer_igusa_results.json"


def parse_ic(raw):
    """Parse igusa_clebsch_inv string to list of ints."""
    if isinstance(raw, list):
        parts = raw
    elif isinstance(raw, str):
        s = raw.strip().strip("[]")
        parts = [p.strip().strip("'\"") for p in s.split(",")]
    else:
        return None
    if len(parts) != 4:
        return None
    try:
        return [int(x) for x in parts]
    except (ValueError, TypeError):
        return None


def load_data():
    """Load and parse the LMFDB dump."""
    with open(DUMP_PATH) as f:
        dump = json.load(f)

    records = []
    skipped = 0
    for rec in dump["records"]:
        ic = parse_ic(rec.get("igusa_clebsch_inv"))
        selmer = rec.get("two_selmer_rank")
        mw = rec.get("mw_rank")
        cond = rec.get("cond")
        st = rec.get("st_group")

        if ic is None or selmer is None or mw is None or cond is None:
            skipped += 1
            continue

        I2, I4, I6, I10 = ic
        records.append({
            "label": rec.get("label", ""),
            "conductor": cond,
            "mw_rank": mw,
            "two_selmer_rank": selmer,
            "selmer_excess": selmer - mw,       # measures Sha[2]
            "I2": I2, "I4": I4, "I6": I6, "I10": I10,
            "st_group": st or "unknown",
        })

    print(f"Loaded {len(records)} records ({skipped} skipped)")
    return records


def safe_log(x):
    """log(|x|+1) to handle zeros and negatives."""
    return log(abs(x) + 1)


# ══════════════════════════════════════════════════════════════════════
# Analysis 1: Global Selmer rank vs log|Igusa invariants|
# ══════════════════════════════════════════════════════════════════════
def analysis_selmer_vs_igusa(records):
    """Spearman correlation between two_selmer_rank and log|I_k|."""
    selmer = np.array([r["two_selmer_rank"] for r in records])
    results = {}

    for inv_name in ["I2", "I4", "I6", "I10"]:
        log_vals = np.array([safe_log(r[inv_name]) for r in records])
        rho, p = stats.spearmanr(selmer, log_vals)
        results[inv_name] = {
            "spearman_rho": round(float(rho), 6),
            "p_value": float(p),
            "significant": p < 0.001,
        }

    # Also Pearson on log values
    for inv_name in ["I2", "I4", "I6", "I10"]:
        log_vals = np.array([safe_log(r[inv_name]) for r in records])
        r_val, p = stats.pearsonr(selmer, log_vals)
        results[inv_name]["pearson_r"] = round(float(r_val), 6)
        results[inv_name]["pearson_p"] = float(p)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 2: Selmer excess within fixed MW rank
# ══════════════════════════════════════════════════════════════════════
def analysis_selmer_excess(records):
    """Within fixed MW rank, correlate Selmer excess with Igusa invariants."""
    by_mw = defaultdict(list)
    for r in records:
        by_mw[r["mw_rank"]].append(r)

    results = {}
    for mw_rank in sorted(by_mw.keys()):
        group = by_mw[mw_rank]
        if len(group) < 50:
            continue

        excess = np.array([r["selmer_excess"] for r in group])
        # Skip if no variance in excess
        if np.std(excess) < 1e-10:
            results[f"mw_rank_{mw_rank}"] = {
                "n": len(group),
                "excess_values": dict(Counter(int(e) for e in excess)),
                "note": "no variance in selmer excess",
            }
            continue

        inv_corrs = {}
        for inv_name in ["I2", "I4", "I6", "I10"]:
            log_vals = np.array([safe_log(r[inv_name]) for r in group])
            rho, p = stats.spearmanr(excess, log_vals)
            inv_corrs[inv_name] = {
                "spearman_rho": round(float(rho), 6),
                "p_value": float(p),
                "significant": p < 0.001,
            }

        # Mean Igusa invariants per excess level
        excess_stats = {}
        for ex_val in sorted(set(int(e) for e in excess)):
            sub = [r for r in group if r["selmer_excess"] == ex_val]
            excess_stats[str(ex_val)] = {
                "count": len(sub),
                "mean_log_I2": round(float(np.mean([safe_log(r["I2"]) for r in sub])), 4),
                "mean_log_I4": round(float(np.mean([safe_log(r["I4"]) for r in sub])), 4),
                "mean_log_I6": round(float(np.mean([safe_log(r["I6"]) for r in sub])), 4),
                "mean_log_I10": round(float(np.mean([safe_log(r["I10"]) for r in sub])), 4),
                "mean_conductor": round(float(np.mean([r["conductor"] for r in sub])), 1),
            }

        results[f"mw_rank_{mw_rank}"] = {
            "n": len(group),
            "excess_distribution": dict(Counter(int(e) for e in excess)),
            "correlations": inv_corrs,
            "excess_level_stats": excess_stats,
        }

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 3: Sha geometry — do curves with Sha[2] > 0 cluster?
# ══════════════════════════════════════════════════════════════════════
def analysis_sha_geometry(records):
    """Compare Igusa invariant distributions: Sha=0 vs Sha>0."""
    sha_zero = [r for r in records if r["selmer_excess"] == 0]
    sha_pos = [r for r in records if r["selmer_excess"] > 0]

    results = {
        "sha_zero_count": len(sha_zero),
        "sha_positive_count": len(sha_pos),
        "invariant_comparisons": {},
    }

    for inv_name in ["I2", "I4", "I6", "I10"]:
        vals_zero = np.array([safe_log(r[inv_name]) for r in sha_zero])
        vals_pos = np.array([safe_log(r[inv_name]) for r in sha_pos])

        # Mann-Whitney U test
        if len(vals_zero) > 0 and len(vals_pos) > 0:
            u_stat, u_p = stats.mannwhitneyu(vals_zero, vals_pos, alternative="two-sided")
            ks_stat, ks_p = stats.ks_2samp(vals_zero, vals_pos)
            effect_size = (np.mean(vals_pos) - np.mean(vals_zero)) / max(
                np.std(np.concatenate([vals_zero, vals_pos])), 1e-10
            )
        else:
            u_stat, u_p, ks_stat, ks_p, effect_size = 0, 1, 0, 1, 0

        results["invariant_comparisons"][inv_name] = {
            "sha_zero_mean": round(float(np.mean(vals_zero)), 4) if len(vals_zero) > 0 else None,
            "sha_zero_median": round(float(np.median(vals_zero)), 4) if len(vals_zero) > 0 else None,
            "sha_positive_mean": round(float(np.mean(vals_pos)), 4) if len(vals_pos) > 0 else None,
            "sha_positive_median": round(float(np.median(vals_pos)), 4) if len(vals_pos) > 0 else None,
            "cohen_d": round(float(effect_size), 4),
            "mann_whitney_p": float(u_p),
            "ks_p": float(ks_p),
            "significant_mw": u_p < 0.001,
            "significant_ks": ks_p < 0.001,
        }

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 4: Selmer rank vs conductor
# ══════════════════════════════════════════════════════════════════════
def analysis_selmer_vs_conductor(records):
    """Correlation between Selmer rank and log(conductor)."""
    selmer = np.array([r["two_selmer_rank"] for r in records])
    log_cond = np.array([log(r["conductor"]) for r in records])

    rho, p = stats.spearmanr(selmer, log_cond)
    r_val, p_pear = stats.pearsonr(selmer, log_cond)

    # Binned means
    cond_bins = np.percentile(log_cond, [0, 25, 50, 75, 100])
    bin_stats = []
    for i in range(4):
        mask = (log_cond >= cond_bins[i]) & (log_cond < cond_bins[i + 1] + (1 if i == 3 else 0))
        if mask.sum() > 0:
            bin_stats.append({
                "log_cond_range": f"[{cond_bins[i]:.1f}, {cond_bins[i+1]:.1f})",
                "n": int(mask.sum()),
                "mean_selmer": round(float(selmer[mask].mean()), 4),
                "std_selmer": round(float(selmer[mask].std()), 4),
            })

    return {
        "spearman_rho": round(float(rho), 6),
        "spearman_p": float(p),
        "pearson_r": round(float(r_val), 6),
        "pearson_p": float(p_pear),
        "quartile_stats": bin_stats,
    }


# ══════════════════════════════════════════════════════════════════════
# Analysis 5: Selmer rank vs Sato-Tate group
# ══════════════════════════════════════════════════════════════════════
def analysis_selmer_vs_st(records):
    """Mean Selmer rank by Sato-Tate group."""
    by_st = defaultdict(list)
    for r in records:
        by_st[r["st_group"]].append(r)

    results = {}
    for st, group in sorted(by_st.items(), key=lambda x: -len(x[1])):
        selmer = [r["two_selmer_rank"] for r in group]
        excess = [r["selmer_excess"] for r in group]
        results[st] = {
            "count": len(group),
            "mean_selmer": round(float(np.mean(selmer)), 4),
            "std_selmer": round(float(np.std(selmer)), 4),
            "mean_excess": round(float(np.mean(excess)), 4),
            "mean_mw_rank": round(float(np.mean([r["mw_rank"] for r in group])), 4),
            "selmer_distribution": dict(Counter(selmer)),
        }

    # Kruskal-Wallis test across all ST groups with n >= 30
    groups_for_kw = []
    for st, group in by_st.items():
        if len(group) >= 30:
            groups_for_kw.append([r["two_selmer_rank"] for r in group])

    if len(groups_for_kw) >= 2:
        h_stat, kw_p = stats.kruskal(*groups_for_kw)
        kw_result = {
            "h_statistic": round(float(h_stat), 4),
            "p_value": float(kw_p),
            "n_groups": len(groups_for_kw),
            "significant": kw_p < 0.001,
        }
    else:
        kw_result = {"note": "insufficient groups for Kruskal-Wallis"}

    return {"by_st_group": results, "kruskal_wallis": kw_result}


# ══════════════════════════════════════════════════════════════════════
# Analysis 6: Null test — shuffle baseline
# ══════════════════════════════════════════════════════════════════════
def analysis_null_test(records, n_shuffles=1000):
    """Shuffle Selmer ranks and recompute correlations to establish null."""
    rng = np.random.RandomState(42)
    selmer = np.array([r["two_selmer_rank"] for r in records])

    null_results = {}
    for inv_name in ["I2", "I4", "I6", "I10"]:
        log_vals = np.array([safe_log(r[inv_name]) for r in records])

        # Observed correlation
        obs_rho, _ = stats.spearmanr(selmer, log_vals)

        # Null distribution
        null_rhos = []
        for _ in range(n_shuffles):
            shuffled = rng.permutation(selmer)
            rho_null, _ = stats.spearmanr(shuffled, log_vals)
            null_rhos.append(rho_null)

        null_rhos = np.array(null_rhos)
        null_mean = float(np.mean(null_rhos))
        null_std = float(np.std(null_rhos))
        z_score = (obs_rho - null_mean) / max(null_std, 1e-10)

        null_results[inv_name] = {
            "observed_rho": round(float(obs_rho), 6),
            "null_mean": round(null_mean, 6),
            "null_std": round(null_std, 6),
            "z_score": round(z_score, 2),
            "exceeds_null_99pct": abs(obs_rho) > np.percentile(np.abs(null_rhos), 99),
        }

    # Also null test for Selmer vs log(conductor)
    log_cond = np.array([log(r["conductor"]) for r in records])
    obs_rho, _ = stats.spearmanr(selmer, log_cond)
    null_rhos = []
    for _ in range(n_shuffles):
        shuffled = rng.permutation(selmer)
        rho_null, _ = stats.spearmanr(shuffled, log_cond)
        null_rhos.append(rho_null)
    null_rhos = np.array(null_rhos)
    null_mean = float(np.mean(null_rhos))
    null_std = float(np.std(null_rhos))
    z_score = (obs_rho - null_mean) / max(null_std, 1e-10)
    null_results["conductor"] = {
        "observed_rho": round(float(obs_rho), 6),
        "null_mean": round(null_mean, 6),
        "null_std": round(null_std, 6),
        "z_score": round(z_score, 2),
        "exceeds_null_99pct": abs(obs_rho) > np.percentile(np.abs(null_rhos), 99),
    }

    return null_results


# ══════════════════════════════════════════════════════════════════════
# Analysis 7: Igusa invariant ratios — moduli coordinates
# ══════════════════════════════════════════════════════════════════════
def analysis_igusa_ratios(records):
    """
    Absolute Igusa invariants (ratios) that are moduli-theoretic coordinates.
    j1 = I2^5 / I10, j2 = I2^3 * I4 / I10, j3 = I2^2 * I6 / I10
    These are the genus-2 analogues of the j-invariant.
    """
    # Compute absolute Igusa invariants where I10 != 0
    valid = [r for r in records if r["I10"] != 0]
    print(f"  Computing Igusa ratios for {len(valid)} curves (I10 != 0)")

    for r in valid:
        I2, I4, I6, I10 = r["I2"], r["I4"], r["I6"], r["I10"]
        r["j1"] = I2**5 / I10 if I10 != 0 else None
        r["j2"] = (I2**3 * I4) / I10 if I10 != 0 else None
        r["j3"] = (I2**2 * I6) / I10 if I10 != 0 else None

    valid = [r for r in valid if r["j1"] is not None]

    selmer = np.array([r["two_selmer_rank"] for r in valid])
    excess = np.array([r["selmer_excess"] for r in valid])

    results = {}
    for jname in ["j1", "j2", "j3"]:
        log_j = np.array([safe_log(r[jname]) for r in valid])

        rho_sel, p_sel = stats.spearmanr(selmer, log_j)
        rho_exc, p_exc = stats.spearmanr(excess, log_j)

        results[jname] = {
            "selmer_spearman": round(float(rho_sel), 6),
            "selmer_p": float(p_sel),
            "excess_spearman": round(float(rho_exc), 6),
            "excess_p": float(p_exc),
        }

    return {"n_valid": len(valid), "correlations": results}


# ══════════════════════════════════════════════════════════════════════
# Analysis 8: Mean-spacing normalization check
# ══════════════════════════════════════════════════════════════════════
def analysis_conductor_normalization(records):
    """
    Key null check: are Igusa correlations just conductor effects in disguise?
    Within conductor bins, recompute Selmer vs Igusa correlations.
    """
    log_conds = np.array([log(r["conductor"]) for r in records])
    # Quartile bins
    edges = np.percentile(log_conds, [0, 25, 50, 75, 100])

    results = {}
    for i in range(4):
        lo, hi = edges[i], edges[i + 1]
        sub = [r for j, r in enumerate(records)
               if log_conds[j] >= lo and (log_conds[j] < hi or (i == 3 and log_conds[j] <= hi))]
        if len(sub) < 100:
            continue

        selmer = np.array([r["two_selmer_rank"] for r in sub])
        if np.std(selmer) < 1e-10:
            continue

        inv_corrs = {}
        for inv_name in ["I2", "I4", "I6", "I10"]:
            log_vals = np.array([safe_log(r[inv_name]) for r in sub])
            rho, p = stats.spearmanr(selmer, log_vals)
            inv_corrs[inv_name] = {
                "spearman_rho": round(float(rho), 6),
                "p_value": float(p),
            }

        results[f"quartile_{i+1}"] = {
            "log_cond_range": f"[{lo:.1f}, {hi:.1f}]",
            "n": len(sub),
            "correlations": inv_corrs,
        }

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════
def main():
    print("=" * 70)
    print("Genus-2: 2-Selmer Rank vs Igusa Invariant Geometry")
    print("=" * 70)

    records = load_data()

    # Basic stats
    selmer_counts = Counter(r["two_selmer_rank"] for r in records)
    excess_counts = Counter(r["selmer_excess"] for r in records)
    mw_counts = Counter(r["mw_rank"] for r in records)
    print(f"\nSelmer rank distribution: {dict(sorted(selmer_counts.items()))}")
    print(f"MW rank distribution:     {dict(sorted(mw_counts.items()))}")
    print(f"Selmer excess dist:       {dict(sorted(excess_counts.items()))}")

    output = {
        "title": "Genus-2: 2-Selmer Rank vs Igusa Invariant Geometry",
        "data_source": str(DUMP_PATH),
        "n_curves": len(records),
        "distributions": {
            "two_selmer_rank": dict(sorted(selmer_counts.items())),
            "mw_rank": dict(sorted(mw_counts.items())),
            "selmer_excess": dict(sorted(excess_counts.items())),
        },
    }

    print("\n[1/8] Global Selmer rank vs log|Igusa invariants| ...")
    output["global_selmer_vs_igusa"] = analysis_selmer_vs_igusa(records)

    print("[2/8] Selmer excess within fixed MW rank ...")
    output["selmer_excess_by_mw_rank"] = analysis_selmer_excess(records)

    print("[3/8] Sha geometry: Sha=0 vs Sha>0 ...")
    output["sha_geometry"] = analysis_sha_geometry(records)

    print("[4/8] Selmer rank vs conductor ...")
    output["selmer_vs_conductor"] = analysis_selmer_vs_conductor(records)

    print("[5/8] Selmer rank vs Sato-Tate group ...")
    output["selmer_vs_st_group"] = analysis_selmer_vs_st(records)

    print("[6/8] Null test (1000 shuffles) ...")
    output["null_test"] = analysis_null_test(records)

    print("[7/8] Absolute Igusa invariant ratios ...")
    output["igusa_ratios"] = analysis_igusa_ratios(records)

    print("[8/8] Conductor-normalized correlations ...")
    output["conductor_normalized"] = analysis_conductor_normalization(records)

    # ── verdict ───────────────────────────────────────────────────────
    verdict_lines = []
    g = output["global_selmer_vs_igusa"]
    for inv in ["I2", "I4", "I6", "I10"]:
        rho = g[inv]["spearman_rho"]
        sig = g[inv]["significant"]
        verdict_lines.append(f"  Selmer vs log|{inv}|: rho={rho:.4f} {'***' if sig else 'ns'}")

    sc = output["selmer_vs_conductor"]
    verdict_lines.append(f"  Selmer vs log(conductor): rho={sc['spearman_rho']:.4f}")

    null = output["null_test"]
    genuine = sum(1 for inv in null if null[inv].get("exceeds_null_99pct", False))
    verdict_lines.append(f"  Null test: {genuine}/{len(null)} exceed 99th percentile of null")

    sha = output["sha_geometry"]
    sha_sig = sum(
        1 for inv in sha["invariant_comparisons"]
        if sha["invariant_comparisons"][inv].get("significant_ks", False)
    )
    verdict_lines.append(f"  Sha geometry: {sha_sig}/4 invariants significantly different (KS)")

    output["verdict"] = "\n".join(verdict_lines)
    print("\n" + "=" * 70)
    print("VERDICT:")
    print(output["verdict"])

    # ── save ──────────────────────────────────────────────────────────
    with open(OUT_JSON, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved to {OUT_JSON}")


if __name__ == "__main__":
    main()
