"""
ALL-059: CM Detection on GSp4 Congruence Pairs
================================================
Apply the zero-frequency CM separator (from CT4/gsp4_cm_detection.py) to
the 37 mod-3 congruence pairs and the mod-2 pairs. Questions:
1. Are CM pairs over-represented in congruence pairs vs population?
2. Does the zero-frequency separator classify BOTH members of a pair
   the same way? (If so, CM is a congruence invariant.)
3. What is the a_zf distribution within congruence pairs vs overall?

Uses stored results from gsp4_cm_detection_results.json.
"""

import json, time
import numpy as np
from pathlib import Path
from collections import Counter

V2 = Path(__file__).resolve().parent
CM_RESULTS = V2 / "gsp4_cm_detection_results.json"
OUT_PATH = V2 / "cm_detection_gsp4_pairs_results.json"


def main():
    t0 = time.time()
    print("=== ALL-059: CM Detection on GSp4 Pairs ===\n")

    with open(CM_RESULTS) as f:
        data = json.load(f)

    # Section 1: Mod-3 pairs
    print("[1] Mod-3 congruence pair CM analysis...")
    mod3 = data.get("mod3_pairs", {})
    pair_results = mod3.get("pair_results", [])
    print(f"    {len(pair_results)} mod-3 pairs analysed")

    # Category counts
    cats = Counter(p.get("category", "?") for p in pair_results)
    print(f"    Categories: {dict(cats)}")

    # Concordance: do both members get same CM classification?
    concordant = 0
    discordant = 0
    for p in pair_results:
        a1 = p.get("zf1_a", 0)
        a2 = p.get("zf2_a", 0)
        cm1 = a1 > 0.3
        cm2 = a2 > 0.3
        if cm1 == cm2:
            concordant += 1
        else:
            discordant += 1
    concordance_rate = concordant / len(pair_results) if pair_results else 0
    print(f"    Concordance (same CM call): {concordant}/{len(pair_results)} = {concordance_rate:.1%}")
    print(f"    Discordant: {discordant}")

    # a_zf similarity within pairs
    a_diffs = [p.get("a_diff", 0) for p in pair_results if "a_diff" in p]
    b_diffs = [p.get("b_diff", 0) for p in pair_results if "b_diff" in p]
    print(f"    Mean |Δa_zf| within pairs: {np.mean(a_diffs):.4f}" if a_diffs else "")
    print(f"    Mean |Δb_zf| within pairs: {np.mean(b_diffs):.4f}" if b_diffs else "")

    # Section 2: Mod-2 pairs
    print("\n[2] Mod-2 congruence pair CM analysis...")
    mod2 = data.get("mod2_pairs", {})
    mod2_results = mod2.get("pair_results", [])
    print(f"    {len(mod2_results)} mod-2 pairs analysed")

    mod2_cats = Counter(p.get("category", "?") for p in mod2_results)
    print(f"    Categories: {dict(mod2_cats)}")

    mod2_a_diffs = [p.get("a_diff", 0) for p in mod2_results if "a_diff" in p]
    mod2_b_diffs = [p.get("b_diff", 0) for p in mod2_results if "b_diff" in p]
    print(f"    Mean |Δa_zf|: {np.mean(mod2_a_diffs):.4f}" if mod2_a_diffs else "")
    print(f"    Mean |Δb_zf|: {np.mean(mod2_b_diffs):.4f}" if mod2_b_diffs else "")

    # Section 3: Full distribution comparison
    print("\n[3] Population-level CM distribution...")
    full = data.get("full_distribution", {})
    a_stats = full.get("a_zf_stats", {})
    st_stats = full.get("st_group_zero_freq", {})

    n_cm_like = a_stats.get("n_cm_like", 0)
    n_generic = a_stats.get("n_generic", 0)
    n_intermediate = a_stats.get("n_intermediate", 0)
    total_pop = n_cm_like + n_generic + n_intermediate
    cm_frac_pop = n_cm_like / total_pop if total_pop > 0 else 0
    print(f"    Population: {n_cm_like} CM-like, {n_generic} generic, {n_intermediate} intermediate")
    print(f"    CM fraction in population: {cm_frac_pop:.4f}")

    # CM fraction in congruence pairs
    n_cm_in_pairs = sum(1 for p in pair_results if p.get("category") == "BOTH_CM_LIKE")
    cm_frac_pairs = n_cm_in_pairs / len(pair_results) if pair_results else 0
    cm_enrichment = cm_frac_pairs / cm_frac_pop if cm_frac_pop > 0 else float('inf')
    print(f"    CM fraction in mod-3 pairs: {cm_frac_pairs:.4f}")
    print(f"    CM enrichment in pairs: {cm_enrichment:.2f}x")

    # ST group breakdown
    print("\n[4] ST group zero-frequency centroids...")
    for group, stats in sorted(st_stats.items(), key=lambda x: -x[1].get("mean", 0))[:10]:
        print(f"    {group}: mean_a_zf={stats.get('mean', 0):.4f}, n={stats.get('count', 0)}")

    # Section 4: Findings
    print("\n[5] Key findings...")
    findings = data.get("findings", [])
    for f in findings[:10]:
        print(f"    • {f}")

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-059",
        "title": "CM Detection on GSp4 Congruence Pairs",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "mod3_pairs": {
            "n_pairs": len(pair_results),
            "categories": dict(cats),
            "concordance_rate": round(concordance_rate, 4),
            "mean_a_diff": round(float(np.mean(a_diffs)), 6) if a_diffs else None,
            "mean_b_diff": round(float(np.mean(b_diffs)), 6) if b_diffs else None,
        },
        "mod2_pairs": {
            "n_pairs": len(mod2_results),
            "categories": dict(mod2_cats),
            "mean_a_diff": round(float(np.mean(mod2_a_diffs)), 6) if mod2_a_diffs else None,
            "mean_b_diff": round(float(np.mean(mod2_b_diffs)), 6) if mod2_b_diffs else None,
        },
        "population": {
            "n_cm_like": n_cm_like,
            "n_generic": n_generic,
            "cm_fraction_population": round(cm_frac_pop, 6),
            "cm_fraction_mod3_pairs": round(cm_frac_pairs, 6),
            "cm_enrichment": round(cm_enrichment, 2),
        },
        "st_group_zero_freq": st_stats,
        "key_findings": findings,
        "assessment": None,
    }

    if concordance_rate > 0.95:
        output["assessment"] = f"CM IS A CONGRUENCE INVARIANT: {concordance_rate:.0%} concordance. Both members of mod-3 pairs always get same CM call. Enrichment={cm_enrichment:.1f}x"
    elif concordance_rate > 0.8:
        output["assessment"] = f"STRONG INVARIANCE: {concordance_rate:.0%} concordance, CM mostly preserved by congruence"
    elif cm_enrichment > 3:
        output["assessment"] = f"CM ENRICHED but not invariant: {cm_enrichment:.1f}x enrichment, {concordance_rate:.0%} concordance"
    else:
        output["assessment"] = f"WEAK: concordance={concordance_rate:.0%}, enrichment={cm_enrichment:.1f}x — CM not special in pairs"

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
