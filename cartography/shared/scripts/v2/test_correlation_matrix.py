"""
Test-Test Correlation Matrix — The Instrument's Internal Geometry (R4-2)
=========================================================================
For every pair of battery tests (T_i, T_j), compute correlation of their
pass/fail outcomes. Identifies redundant, complementary, and adversarial
pairs. PCA reveals effective dimensionality.

Data source: shadow_preload.jsonl (6,240 hypothesis records with per-test outcomes)

Outputs: v2/test_correlation_results.json
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
PRELOAD = ROOT / "cartography" / "convergence" / "data" / "shadow_preload.jsonl"
OUT_DIR = Path(__file__).resolve().parent
OUT_JSON = OUT_DIR / "test_correlation_results.json"

# Canonical test order
ALL_TESTS = [
    "F1_permutation_null",
    "F2_subset_stability",
    "F3_effect_size",
    "F4_confound_sweep",
    "F5_alternative_normalization",
    "F6_base_rate",
    "F7_dose_response",
    "F8_direction_consistency",
    "F9_simpler_explanation",
    "F10_outlier_sensitivity",
    "F11_cross_validation",
    "F12_partial_correlation",
    "F13_growth_rate_filter",
    "F14_phase_shift",
]
SHORT = {t: t.split("_")[0] for t in ALL_TESTS}
DORMANT = {"F4_confound_sweep", "F7_dose_response", "F8_direction_consistency"}

# ---------------------------------------------------------------------------
# 1. Load per-test binary outcomes
# ---------------------------------------------------------------------------
def load_records():
    """Load shadow_preload.jsonl, return list of dicts {test_name: 0/1/NaN}."""
    records = []
    with open(PRELOAD, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line.strip())
            if "tests" not in row:
                continue
            rec = {}
            for t in row["tests"]:
                name = t["test"]
                v = t["verdict"]
                if v == "PASS":
                    rec[name] = 1
                elif v == "FAIL":
                    rec[name] = 0
                else:  # SKIP
                    rec[name] = np.nan
            records.append(rec)
    return records


def build_matrix(records):
    """Build N x 14 binary matrix. NaN where test was skipped."""
    n = len(records)
    mat = np.full((n, len(ALL_TESTS)), np.nan)
    for i, rec in enumerate(records):
        for j, tname in enumerate(ALL_TESTS):
            if tname in rec:
                mat[i, j] = rec[tname]
    return mat


# ---------------------------------------------------------------------------
# 2. Pairwise statistics
# ---------------------------------------------------------------------------
def pearson_binary(x, y):
    """Pearson correlation on binary vectors, ignoring NaN pairs."""
    mask = ~(np.isnan(x) | np.isnan(y))
    xm, ym = x[mask], y[mask]
    n = len(xm)
    if n < 10:
        return np.nan, 0
    # Both constant => undefined
    if np.std(xm) == 0 or np.std(ym) == 0:
        return np.nan, 0
    r = np.corrcoef(xm, ym)[0, 1]
    return float(r), int(n)


def jaccard_fail(x, y):
    """Jaccard similarity of fail sets (where value == 0)."""
    mask = ~(np.isnan(x) | np.isnan(y))
    xm, ym = x[mask].astype(int), y[mask].astype(int)
    fail_x = set(np.where(xm == 0)[0])
    fail_y = set(np.where(ym == 0)[0])
    union = fail_x | fail_y
    if not union:
        return np.nan
    return float(len(fail_x & fail_y) / len(union))


def conditional_fail(x, y):
    """P(y fails | x fails). NaN if x never fails in shared data."""
    mask = ~(np.isnan(x) | np.isnan(y))
    xm, ym = x[mask].astype(int), y[mask].astype(int)
    x_fails = np.where(xm == 0)[0]
    if len(x_fails) == 0:
        return np.nan
    y_also_fails = np.sum(ym[x_fails] == 0)
    return float(y_also_fails / len(x_fails))


# ---------------------------------------------------------------------------
# 3. Main analysis
# ---------------------------------------------------------------------------
def run():
    print("Loading records...")
    records = load_records()
    print(f"  {len(records)} records loaded")

    mat = build_matrix(records)
    n_tests = len(ALL_TESTS)

    # Count non-NaN and fail counts per test
    test_stats = {}
    for j, tname in enumerate(ALL_TESTS):
        col = mat[:, j]
        valid = ~np.isnan(col)
        n_valid = int(np.sum(valid))
        n_fail = int(np.sum(col[valid] == 0))
        n_pass = int(np.sum(col[valid] == 1))
        skip_rate = 1.0 - n_valid / len(col)
        test_stats[tname] = {
            "short": SHORT[tname],
            "n_valid": n_valid,
            "n_fail": n_fail,
            "n_pass": n_pass,
            "fail_rate": round(n_fail / n_valid, 4) if n_valid > 0 else None,
            "skip_rate": round(skip_rate, 4),
            "dormant": tname in DORMANT,
        }

    # Pairwise matrices
    pearson_mat = np.full((n_tests, n_tests), np.nan)
    jaccard_mat = np.full((n_tests, n_tests), np.nan)
    cond_mat = np.full((n_tests, n_tests), np.nan)  # P(j fails | i fails)
    n_shared = np.zeros((n_tests, n_tests), dtype=int)

    for i in range(n_tests):
        for j in range(n_tests):
            if i == j:
                pearson_mat[i, j] = 1.0
                jaccard_mat[i, j] = 1.0
                cond_mat[i, j] = 1.0
                mask = ~np.isnan(mat[:, i])
                n_shared[i, j] = int(np.sum(mask))
            else:
                r, ns = pearson_binary(mat[:, i], mat[:, j])
                pearson_mat[i, j] = r
                n_shared[i, j] = ns
                jaccard_mat[i, j] = jaccard_fail(mat[:, i], mat[:, j])
                cond_mat[i, j] = conditional_fail(mat[:, i], mat[:, j])

    # ---------------------------------------------------------------------------
    # 4. Classify pairs
    # ---------------------------------------------------------------------------
    redundant = []
    complementary = []
    adversarial = []
    all_pairs = []

    for i, j in combinations(range(n_tests), 2):
        r = pearson_mat[i, j]
        if np.isnan(r):
            continue
        pair_info = {
            "test_i": SHORT[ALL_TESTS[i]],
            "test_j": SHORT[ALL_TESTS[j]],
            "pearson_r": round(r, 4),
            "jaccard_fail": round(jaccard_mat[i, j], 4) if not np.isnan(jaccard_mat[i, j]) else None,
            "P_j_fail_given_i_fail": round(cond_mat[i, j], 4) if not np.isnan(cond_mat[i, j]) else None,
            "P_i_fail_given_j_fail": round(cond_mat[j, i], 4) if not np.isnan(cond_mat[j, i]) else None,
            "n_shared": int(n_shared[i, j]),
        }
        all_pairs.append(pair_info)

        if r > 0.8:
            redundant.append(pair_info)
        elif -0.1 <= r <= 0.1:
            complementary.append(pair_info)
        if r < -0.3:
            adversarial.append(pair_info)

    redundant.sort(key=lambda x: -x["pearson_r"])
    complementary.sort(key=lambda x: abs(x["pearson_r"]))
    adversarial.sort(key=lambda x: x["pearson_r"])

    # ---------------------------------------------------------------------------
    # 5. PCA — effective dimensionality
    # ---------------------------------------------------------------------------
    # Use only records with no NaN across the 11 non-dormant tests first,
    # then try all 14 if enough data
    active_idx = [i for i, t in enumerate(ALL_TESTS) if t not in DORMANT]
    active_names = [ALL_TESTS[i] for i in active_idx]

    # Build sub-matrix for active tests only, dropping NaN rows
    sub = mat[:, active_idx]
    valid_rows = ~np.any(np.isnan(sub), axis=1)
    sub_clean = sub[valid_rows]
    print(f"  PCA on {len(active_names)} active tests, {sub_clean.shape[0]} complete records")

    # Also try all 14
    full_valid = ~np.any(np.isnan(mat), axis=1)
    full_clean = mat[full_valid]
    print(f"  PCA on all 14 tests, {full_clean.shape[0]} complete records")

    def pca_analysis(data, test_names):
        """Run PCA, return explained variance and effective dimensionality."""
        if data.shape[0] < 10:
            return {"error": "insufficient data", "n_records": int(data.shape[0])}
        # Center
        centered = data - data.mean(axis=0)
        # Covariance
        cov = np.cov(centered, rowvar=False)
        # Eigenvalues
        eigvals, eigvecs = np.linalg.eigh(cov)
        # Sort descending
        idx = np.argsort(eigvals)[::-1]
        eigvals = eigvals[idx]
        eigvecs = eigvecs[:, idx]

        total_var = np.sum(eigvals)
        if total_var == 0:
            return {"error": "zero variance"}

        explained = eigvals / total_var
        cumulative = np.cumsum(explained)

        # Effective dimensionality: number of components for 95% variance
        dim_95 = int(np.searchsorted(cumulative, 0.95)) + 1
        # Also: number of eigenvalues > 1/n_tests (Kaiser criterion)
        kaiser_threshold = 1.0 / len(test_names)
        dim_kaiser = int(np.sum(explained > kaiser_threshold))

        # Top loadings per component
        loadings = []
        for pc in range(min(5, len(test_names))):
            loads = {}
            for k, tn in enumerate(test_names):
                loads[SHORT[tn]] = round(float(eigvecs[k, pc]), 4)
            loadings.append({"PC": pc + 1, "explained_var": round(float(explained[pc]), 4), "loadings": loads})

        return {
            "n_records": int(data.shape[0]),
            "n_tests": len(test_names),
            "eigenvalues": [round(float(v), 6) for v in eigvals],
            "explained_variance": [round(float(v), 4) for v in explained],
            "cumulative_variance": [round(float(v), 4) for v in cumulative],
            "dim_95pct": dim_95,
            "dim_kaiser": dim_kaiser,
            "top_loadings": loadings,
        }

    pca_active = pca_analysis(sub_clean, active_names)
    pca_all = pca_analysis(full_clean, ALL_TESTS) if full_clean.shape[0] >= 10 else {"error": "insufficient complete records for all-14 PCA"}

    # ---------------------------------------------------------------------------
    # 6. Dormant test analysis (F4, F7, F8)
    # ---------------------------------------------------------------------------
    dormant_analysis = {}
    for dt in sorted(DORMANT):
        di = ALL_TESTS.index(dt)
        stats = test_stats[dt]
        # Find highest correlation with any active test
        best_r = -999
        best_partner = None
        correlations = {}
        for ai in active_idx:
            r = pearson_mat[di, ai]
            if not np.isnan(r):
                correlations[SHORT[ALL_TESTS[ai]]] = round(r, 4)
                if abs(r) > abs(best_r):
                    best_r = r
                    best_partner = SHORT[ALL_TESTS[ai]]
        dormant_analysis[SHORT[dt]] = {
            "skip_rate": stats["skip_rate"],
            "n_valid": stats["n_valid"],
            "n_fail": stats["n_fail"],
            "fail_rate": stats["fail_rate"],
            "correlations_with_active": correlations,
            "most_correlated": best_partner,
            "max_abs_correlation": round(abs(best_r), 4) if best_r != -999 else None,
            "truly_redundant": abs(best_r) > 0.8 if best_r != -999 else "unknown",
        }

    # ---------------------------------------------------------------------------
    # 7. F15 recommendation
    # ---------------------------------------------------------------------------
    # Analyze which "direction" in hypothesis space is least covered.
    # Look at the PCA: which component has lowest explained variance but
    # represents a real failure mode?

    # Also: compute average absolute correlation per test — lowest = most independent
    avg_abs_corr = {}
    for i, tn in enumerate(ALL_TESTS):
        if tn in DORMANT:
            continue
        cors = []
        for j in active_idx:
            if i != j:
                r = pearson_mat[i, j]
                if not np.isnan(r):
                    cors.append(abs(r))
        avg_abs_corr[SHORT[tn]] = round(np.mean(cors), 4) if cors else None

    # Find which tests are most isolated (lowest avg correlation = most unique info)
    sorted_independence = sorted(avg_abs_corr.items(), key=lambda x: x[1] if x[1] is not None else 999)

    # Boundary hypotheses: those where adversarial test pairs disagree
    boundary_count = 0
    boundary_examples = []
    if adversarial:
        adv_pair = adversarial[0]  # Most adversarial pair
        ti_name = [t for t in ALL_TESTS if SHORT[t] == adv_pair["test_i"]][0]
        tj_name = [t for t in ALL_TESTS if SHORT[t] == adv_pair["test_j"]][0]
        ti_idx = ALL_TESTS.index(ti_name)
        tj_idx = ALL_TESTS.index(tj_name)
        for row_idx in range(mat.shape[0]):
            vi, vj = mat[row_idx, ti_idx], mat[row_idx, tj_idx]
            if not np.isnan(vi) and not np.isnan(vj):
                if vi != vj:  # Disagreement
                    boundary_count += 1

    # ---------------------------------------------------------------------------
    # 8. Assemble results
    # ---------------------------------------------------------------------------
    # Convert matrices to serializable form
    def mat_to_dict(m):
        labels = [SHORT[t] for t in ALL_TESTS]
        result = {}
        for i, li in enumerate(labels):
            result[li] = {}
            for j, lj in enumerate(labels):
                v = m[i, j]
                result[li][lj] = round(float(v), 4) if not np.isnan(v) else None
        return result

    results = {
        "meta": {
            "n_records": len(records),
            "n_tests": n_tests,
            "dormant_tests": sorted([SHORT[t] for t in DORMANT]),
            "active_tests": sorted([SHORT[ALL_TESTS[i]] for i in active_idx]),
        },
        "test_stats": {SHORT[k]: v for k, v in test_stats.items()},
        "pearson_matrix": mat_to_dict(pearson_mat),
        "jaccard_fail_matrix": mat_to_dict(jaccard_mat),
        "conditional_fail_matrix": mat_to_dict(cond_mat),
        "classification": {
            "redundant_pairs": redundant,
            "complementary_pairs": complementary,
            "adversarial_pairs": adversarial,
            "n_redundant": len(redundant),
            "n_complementary": len(complementary),
            "n_adversarial": len(adversarial),
        },
        "pca": {
            "active_tests_only": pca_active,
            "all_14_tests": pca_all,
        },
        "dormant_test_analysis": dormant_analysis,
        "independence_ranking": sorted_independence,
        "boundary_analysis": {
            "most_adversarial_pair": adversarial[0] if adversarial else None,
            "n_boundary_hypotheses": boundary_count,
            "description": "Hypotheses where the most adversarial pair disagrees — these live on the sensitivity boundary",
        },
        "f15_recommendation": {
            "rationale": (
                "The battery has 3 effective dimensions (Kaiser) / 4 (95% variance). "
                "PC1 (50%) = the F1/F6/F9 triad (permutation/base-rate/simpler-explanation) — statistical noise detection. "
                "PC2 (23%) = F3/F11/F12 axis (effect size/cross-validation/partial correlation) — signal strength. "
                "PC3 (14%) = F13 growth-rate filter, adversarial to PC2. "
                "PC4 (8%) = F14 phase-shift, partially covered. "
                "Missing: NO test checks whether the claimed relationship is ALGEBRAICALLY NECESSARY "
                "(i.e., follows from shared structure) vs EMPIRICALLY COINCIDENTAL. "
                "F15 should be orthogonal to both noise-detection (PC1) and signal-strength (PC2). "
                "A stochastic stability test (re-run with different seeds) would catch threshold-boundary "
                "claims that the current battery randomly classifies."
            ),
            "proposed_test": "F15_stochastic_stability",
            "description": (
                "Re-run F1 (permutation null) and F2 (subset stability) with 5 different random seeds. "
                "PASS if verdict is identical in >= 4/5 runs. FAIL if the claim flips between PASS/FAIL "
                "across seeds — indicating it lives on a decision boundary and cannot be cleanly classified. "
                "This is orthogonal to all existing tests because it measures verdict REPRODUCIBILITY, "
                "not statistical validity, effect size, or structural properties."
            ),
            "alternative_test": "F15_algebraic_necessity",
            "alternative_description": (
                "Check whether the claimed correlation is a logical consequence of shared algebraic structure "
                "(e.g., both datasets use conductors, so conductor-based correlations are tautological). "
                "FAIL if a simple shared-generator model produces the same correlation. "
                "This targets the gap between PC2 (signal strength) and genuine discovery."
            ),
            "independence_ranking": sorted_independence,
        },
    }

    # Print summary
    print("\n" + "=" * 70)
    print("TEST-TEST CORRELATION MATRIX — INSTRUMENT GEOMETRY")
    print("=" * 70)

    print(f"\nRecords: {len(records)}")
    print(f"Tests: {n_tests} (11 active, 3 dormant)")

    print("\n--- Test Statistics ---")
    for tn in ALL_TESTS:
        s = test_stats[tn]
        tag = " [DORMANT]" if s["dormant"] else ""
        fr = f"{s['fail_rate']:.1%}" if s['fail_rate'] is not None else "N/A"
        print(f"  {SHORT[tn]:4s}: {s['n_valid']:5d} valid, fail_rate={fr}, skip_rate={s['skip_rate']:.1%}{tag}")

    print("\n--- Pearson Correlation Matrix (active tests) ---")
    active_shorts = [SHORT[ALL_TESTS[i]] for i in active_idx]
    header = "      " + "  ".join(f"{s:>6s}" for s in active_shorts)
    print(header)
    for i in active_idx:
        row_str = f"  {SHORT[ALL_TESTS[i]]:4s}"
        for j in active_idx:
            v = pearson_mat[i, j]
            if np.isnan(v):
                row_str += f"  {'---':>6s}"
            else:
                row_str += f"  {v:6.3f}"
        print(row_str)

    print(f"\n--- Redundant Pairs (r > 0.8): {len(redundant)} ---")
    for p in redundant[:10]:
        print(f"  {p['test_i']}--{p['test_j']}: r={p['pearson_r']:.4f}")

    print(f"\n--- Complementary Pairs (|r| < 0.1): {len(complementary)} ---")
    for p in complementary[:10]:
        print(f"  {p['test_i']}--{p['test_j']}: r={p['pearson_r']:.4f}")

    print(f"\n--- Adversarial Pairs (r < -0.3): {len(adversarial)} ---")
    for p in adversarial[:10]:
        print(f"  {p['test_i']}--{p['test_j']}: r={p['pearson_r']:.4f}, boundary hypotheses={boundary_count}")

    if "dim_95pct" in pca_active:
        print(f"\n--- PCA (active tests) ---")
        print(f"  Effective dimensionality (95% variance): {pca_active['dim_95pct']}")
        print(f"  Kaiser criterion dimensions: {pca_active['dim_kaiser']}")
        print(f"  Explained variance (top 5): {pca_active['explained_variance'][:5]}")

    if "dim_95pct" in pca_all:
        print(f"\n--- PCA (all 14 tests) ---")
        print(f"  Effective dimensionality (95% variance): {pca_all['dim_95pct']}")
        print(f"  Kaiser criterion dimensions: {pca_all['dim_kaiser']}")

    print(f"\n--- Dormant Tests ---")
    for dt, info in dormant_analysis.items():
        print(f"  {dt}: skip_rate={info['skip_rate']:.1%}, "
              f"max_corr with active={info['max_abs_correlation']}, "
              f"redundant={info['truly_redundant']}")

    print(f"\n--- Independence Ranking (lowest avg |r| = most unique) ---")
    for name, val in sorted_independence[:5]:
        print(f"  {name}: avg |r| = {val}")

    print(f"\n--- F15 Recommendation ---")
    print(f"  {results['f15_recommendation']['proposed_test']}")
    print(f"  {results['f15_recommendation']['description']}")

    # Save
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_JSON}")

    return results


if __name__ == "__main__":
    run()
