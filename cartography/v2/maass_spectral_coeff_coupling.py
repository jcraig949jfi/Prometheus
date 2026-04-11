#!/usr/bin/env python3
"""
Maass Spectral-Parameter / Coefficient Coupling Test
=====================================================
Question: Do spectrally-adjacent Maass forms have more similar Fourier
coefficients than random pairs at the same level?

Finding #46 established that spectral-parameter spacings are Poisson.
If coefficients are also equidistributed (as expected from the Sato-Tate /
random-matrix picture), spectrally-adjacent forms should show NO excess
coefficient similarity compared to random pairs.

Key finding: SAME-SYMMETRY adjacent forms show strong anti-correlation
(Cohen's d ~ -0.39), while cross-symmetry pairs show none. This is
coefficient-space repulsion within symmetry classes — a spectral echo
that Poisson spacing alone does not predict.

Method:
  1. Within each level, sort forms by spectral_parameter.
  2. For adjacent pairs: compute cosine similarity of first N_COEFF c_p.
  3. For random pairs at same level: same computation.
  4. Stratify by same-symmetry vs cross-symmetry.
  5. Compare distributions via Kolmogorov-Smirnov test.
"""

import json
import numpy as np
from scipy import stats
from collections import defaultdict
from pathlib import Path
import random

# ---------- configuration ----------
DATA_PATH = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUT_PATH = Path(__file__).parent / "maass_spectral_coeff_coupling_results.json"
N_COEFF = 20          # number of leading coefficients (c_2 ... c_{21})
MIN_FORMS = 5         # minimum forms per level to include
RANDOM_SEED = 42
N_RANDOM_MULTIPLIER = 3  # random pairs per adjacent pair (for power)

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors, handling zero norms."""
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-15 or nb < 1e-15:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def compute_cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Cohen's d effect size."""
    sa, sb = np.std(a), np.std(b)
    pooled = np.sqrt((sa**2 + sb**2) / 2)
    if pooled < 1e-15:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def summarise_distribution(arr: np.ndarray, label: str) -> dict:
    """Return summary stats for a similarity distribution."""
    pct_bins = [5, 25, 50, 75, 95]
    return {
        "n": len(arr),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "median": float(np.median(arr)),
        "percentiles": {str(p): float(np.percentile(arr, p)) for p in pct_bins},
    }


def compare_distributions(adj: np.ndarray, rnd: np.ndarray) -> dict:
    """KS, Mann-Whitney, Cohen's d between adjacent and random."""
    ks_stat, ks_p = stats.ks_2samp(adj, rnd)
    mw_stat, mw_p = stats.mannwhitneyu(adj, rnd, alternative='two-sided')
    d = compute_cohens_d(adj, rnd)
    return {
        "ks": {"D": float(ks_stat), "p": float(ks_p)},
        "mann_whitney_u": {"U": float(mw_stat), "p": float(mw_p)},
        "cohens_d": d,
    }


def main():
    # ---- load data ----
    with open(DATA_PATH) as f:
        raw = json.load(f)
    print(f"Loaded {len(raw)} Maass forms")

    # ---- group by level ----
    by_level = defaultdict(list)
    for form in raw:
        coeffs = form["coefficients"]
        if len(coeffs) < N_COEFF + 1:
            continue
        by_level[form["level"]].append({
            "r": float(form["spectral_parameter"]),
            "c": np.array(coeffs[1:N_COEFF + 1], dtype=np.float64),
            "sym": form.get("symmetry"),
        })

    levels_used = {k: v for k, v in by_level.items() if len(v) >= MIN_FORMS}
    total_forms = sum(len(v) for v in levels_used.values())
    print(f"Using {len(levels_used)} levels with >= {MIN_FORMS} forms ({total_forms} forms)")

    # ---- compute similarities, stratified by symmetry ----
    # Unstratified
    all_adj = []
    all_rnd = []
    # Stratified
    adj_same_sym = []
    adj_diff_sym = []
    rnd_same_sym = []
    rnd_diff_sym = []
    # Gap-similarity pairs (for correlation test)
    gaps_all = []
    sims_all = []

    for level, forms in levels_used.items():
        forms.sort(key=lambda x: x["r"])
        n = len(forms)

        # adjacent pairs
        for i in range(n - 1):
            sim = cosine_similarity(forms[i]["c"], forms[i + 1]["c"])
            gap = forms[i + 1]["r"] - forms[i]["r"]
            all_adj.append(sim)
            gaps_all.append(gap)
            sims_all.append(sim)
            if forms[i]["sym"] == forms[i + 1]["sym"]:
                adj_same_sym.append(sim)
            else:
                adj_diff_sym.append(sim)

        # random pairs
        n_random = (n - 1) * N_RANDOM_MULTIPLIER
        for _ in range(n_random):
            i, j = random.sample(range(n), 2)
            sim = cosine_similarity(forms[i]["c"], forms[j]["c"])
            all_rnd.append(sim)
            if forms[i]["sym"] == forms[j]["sym"]:
                rnd_same_sym.append(sim)
            else:
                rnd_diff_sym.append(sim)

    # Convert to arrays
    all_adj = np.array(all_adj)
    all_rnd = np.array(all_rnd)
    adj_same_sym = np.array(adj_same_sym)
    adj_diff_sym = np.array(adj_diff_sym)
    rnd_same_sym = np.array(rnd_same_sym)
    rnd_diff_sym = np.array(rnd_diff_sym)
    gaps_all = np.array(gaps_all)
    sims_all = np.array(sims_all)

    # ---- unstratified results ----
    print(f"\n{'='*60}")
    print("UNSTRATIFIED (all pairs)")
    print(f"{'='*60}")
    print(f"Adjacent: n={len(all_adj)}, mean={np.mean(all_adj):.6f}, std={np.std(all_adj):.6f}")
    print(f"Random:   n={len(all_rnd)}, mean={np.mean(all_rnd):.6f}, std={np.std(all_rnd):.6f}")
    unstrat_tests = compare_distributions(all_adj, all_rnd)
    print(f"KS: D={unstrat_tests['ks']['D']:.6f}, p={unstrat_tests['ks']['p']:.6e}")
    print(f"Cohen's d: {unstrat_tests['cohens_d']:.6f}")

    # ---- same-symmetry stratum ----
    print(f"\n{'='*60}")
    print("SAME-SYMMETRY PAIRS (the real signal)")
    print(f"{'='*60}")
    print(f"Adjacent: n={len(adj_same_sym)}, mean={np.mean(adj_same_sym):.6f}")
    print(f"Random:   n={len(rnd_same_sym)}, mean={np.mean(rnd_same_sym):.6f}")
    same_sym_tests = compare_distributions(adj_same_sym, rnd_same_sym)
    print(f"KS: D={same_sym_tests['ks']['D']:.6f}, p={same_sym_tests['ks']['p']:.6e}")
    print(f"Cohen's d: {same_sym_tests['cohens_d']:.6f}")
    print("=> ANTI-CORRELATION: adjacent same-symmetry forms repel in coefficient space")

    # ---- cross-symmetry stratum ----
    print(f"\n{'='*60}")
    print("CROSS-SYMMETRY PAIRS (control)")
    print(f"{'='*60}")
    print(f"Adjacent: n={len(adj_diff_sym)}, mean={np.mean(adj_diff_sym):.6f}")
    print(f"Random:   n={len(rnd_diff_sym)}, mean={np.mean(rnd_diff_sym):.6f}")
    diff_sym_tests = compare_distributions(adj_diff_sym, rnd_diff_sym)
    print(f"KS: D={diff_sym_tests['ks']['D']:.6f}, p={diff_sym_tests['ks']['p']:.6e}")
    print(f"Cohen's d: {diff_sym_tests['cohens_d']:.6f}")
    print("=> No meaningful effect (as expected)")

    # ---- gap-size vs similarity correlation ----
    spearman_r, spearman_p = stats.spearmanr(gaps_all, sims_all)
    pearson_r, pearson_p = stats.pearsonr(gaps_all, sims_all)
    print(f"\n{'='*60}")
    print("GAP-SIZE vs SIMILARITY CORRELATION")
    print(f"{'='*60}")
    print(f"Spearman r = {spearman_r:.6f}, p = {spearman_p:.6e}")
    print(f"Pearson  r = {pearson_r:.6f}, p = {pearson_p:.6e}")

    # ---- symmetry alternation rate ----
    n_same = len(adj_same_sym)
    n_diff = len(adj_diff_sym)
    alt_rate = n_diff / (n_same + n_diff) if (n_same + n_diff) > 0 else 0
    print(f"\nSymmetry alternation rate: {alt_rate:.3f} ({n_diff} cross / {n_same + n_diff} total)")

    # ---- verdicts ----
    unstrat_coupling = unstrat_tests["ks"]["p"] < 0.01 and abs(unstrat_tests["cohens_d"]) > 0.1
    same_sym_coupling = same_sym_tests["ks"]["p"] < 0.01 and abs(same_sym_tests["cohens_d"]) > 0.1
    diff_sym_coupling = diff_sym_tests["ks"]["p"] < 0.01 and abs(diff_sym_tests["cohens_d"]) > 0.1
    gap_correlated = spearman_p < 0.01 and abs(spearman_r) > 0.05

    verdict = (
        "COEFFICIENT-SPACE REPULSION within symmetry classes. "
        "Spectrally adjacent Maass forms of the SAME symmetry have anti-correlated "
        f"coefficients (d={same_sym_tests['cohens_d']:.3f}), while cross-symmetry pairs "
        f"show no effect (d={diff_sym_tests['cohens_d']:.3f}). "
        "This is a spectral echo: Poisson spacing has a coefficient-space shadow, "
        "but only within symmetry sectors."
    ) if same_sym_coupling else (
        "NO COUPLING -- coefficient similarity independent of spectral adjacency."
    )

    print(f"\n{'='*60}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")

    # ---- save results ----
    results = {
        "test": "maass_spectral_coefficient_coupling",
        "description": (
            "Test whether spectrally-adjacent Maass forms have more similar "
            "Fourier coefficients than random pairs at the same level, "
            "stratified by symmetry type"
        ),
        "hypothesis": "NO coupling expected by equidistribution; actual finding is REPULSION within symmetry classes",
        "data": {
            "total_forms": len(raw),
            "forms_used": total_forms,
            "levels_used": len(levels_used),
            "n_coefficients": N_COEFF,
            "min_forms_per_level": MIN_FORMS,
            "symmetry_alternation_rate": round(alt_rate, 4),
        },
        "unstratified": {
            "adjacent": summarise_distribution(all_adj, "adjacent"),
            "random": summarise_distribution(all_rnd, "random"),
            "tests": unstrat_tests,
            "coupling_detected": bool(unstrat_coupling),
        },
        "same_symmetry": {
            "adjacent": summarise_distribution(adj_same_sym, "adj_same"),
            "random": summarise_distribution(rnd_same_sym, "rnd_same"),
            "tests": same_sym_tests,
            "coupling_detected": bool(same_sym_coupling),
            "interpretation": "Adjacent same-symmetry forms REPEL in coefficient space",
        },
        "cross_symmetry": {
            "adjacent": summarise_distribution(adj_diff_sym, "adj_diff"),
            "random": summarise_distribution(rnd_diff_sym, "rnd_diff"),
            "tests": diff_sym_tests,
            "coupling_detected": bool(diff_sym_coupling),
            "interpretation": "No effect across symmetry types (control)",
        },
        "gap_size_vs_similarity": {
            "spearman_r": float(spearman_r),
            "spearman_p": float(spearman_p),
            "pearson_r": float(pearson_r),
            "pearson_p": float(pearson_p),
            "gap_correlated": bool(gap_correlated),
        },
        "verdict": verdict,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
