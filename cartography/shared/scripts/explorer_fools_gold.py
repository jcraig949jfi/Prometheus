"""
Explorer: Fool's Gold Assay — re-examine tautological pairs for hidden verb bridges.
=====================================================================================
The tensor validation sweep classified 6 dataset pairs as tautological (confounds).
This script digs deeper: are they truly fool's gold, or did we miss hidden verb bridges?

Checks:
  1. ALL shared concepts (not just top 5)
  2. Any verb concepts shared (even rare ones)
  3. "Hidden verbs": noun-form concepts that encode operations
  4. Newly-added verb extractors that might have created bridges post-sweep

Usage:  python explorer_fools_gold.py
Output: cartography/convergence/data/fools_gold_assay.json
"""

import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

REPO = SCRIPT_DIR.parents[2]
DATA_DIR = REPO / "cartography" / "convergence" / "data"
LINKS_PATH = DATA_DIR / "concept_links.jsonl"
SWEEP_PATH = DATA_DIR / "tensor_validation_sweep.json"
CONCEPTS_PATH = DATA_DIR / "concepts.jsonl"
OUTPUT_PATH = DATA_DIR / "fools_gold_assay.json"

# ---------------------------------------------------------------------------
# Concept classification (mirrors tensor_validation_sweep.py)
# ---------------------------------------------------------------------------
TAUTOLOGICAL_PATTERNS = [
    re.compile(r"^integer_\d+$"),
    re.compile(r"^conductor_\d+$"),
    re.compile(r"^determinant_\d+$"),
    re.compile(r"^crossing_\d+$"),
    re.compile(r"^degree_\d+$"),
    re.compile(r"^dimension_\d+$"),
    re.compile(r"^rank_\d+$"),
    re.compile(r"^fvector_"),
    re.compile(r"^point_group_"),
    re.compile(r"^spacegroup_\d+$"),
    re.compile(r"^crystal_"),
]

GENERIC_CONCEPTS = {
    "prime", "odd", "even", "small_integer", "medium_integer", "large_integer",
    "perfect_square", "perfect_cube", "supersingular",
}

STRUCTURAL_PATTERN = re.compile(r"^verb_")

DOMAIN_PREFIXES = [
    "has_", "namespace_", "topic_", "mizar_", "galois_", "ramification_",
    "collection_", "graph_", "topo_", "object_type_", "symbol_", "extension_",
    "class_",
]

# ---------------------------------------------------------------------------
# Hidden verb detection
# ---------------------------------------------------------------------------
# Concepts that are noun-form but encode mathematical operations/structures.
# These are potential bridges the sweep would have missed because they don't
# start with "verb_" but represent genuine mathematical relationships.
HIDDEN_VERB_PATTERNS = {
    # Topic concepts that encode operations
    re.compile(r"^topic_Zeta"): "zeta function (operation)",
    re.compile(r"^topic_Integral"): "integration (operation)",
    re.compile(r"^topic_Sum"): "summation (operation)",
    re.compile(r"^topic_Product"): "product (operation)",
    re.compile(r"^topic_Limit"): "limits (operation)",
    re.compile(r"^topic_Convergence"): "convergence analysis",
    re.compile(r"^topic_Modular"): "modular arithmetic (operation)",
    re.compile(r"^topic_Elliptic"): "elliptic theory (structural)",
    re.compile(r"^topic_Prime"): "primality (operation)",
    re.compile(r"^topic_Factor"): "factorization (operation)",
    re.compile(r"^topic_Transform"): "transformation (operation)",
    re.compile(r"^topic_Recurrence"): "recurrence (structural)",
    re.compile(r"^topic_Polynomial"): "polynomial operations",
    re.compile(r"^topic_Derivative"): "differentiation (operation)",
    re.compile(r"^topic_Series"): "series expansion (operation)",
    re.compile(r"^topic_Analytic"): "analytic continuation (operation)",
    re.compile(r"^topic_Functional"): "functional equations",
    re.compile(r"^topic_Dirichlet"): "Dirichlet series/characters",
    re.compile(r"^topic_Gauss"): "Gaussian operations",
    re.compile(r"^topic_Fourier"): "Fourier analysis",
    re.compile(r"^topic_Theta"): "theta functions",
    re.compile(r"^topic_Gamma"): "gamma function",
    re.compile(r"^topic_Beta"): "beta function",
    # Symbol concepts that encode operations
    re.compile(r"^symbol_Integral"): "integration symbol",
    re.compile(r"^symbol_Sum"): "summation symbol",
    re.compile(r"^symbol_Product"): "product symbol",
    re.compile(r"^symbol_Zeta"): "zeta function symbol",
    re.compile(r"^symbol_Gamma"): "gamma function symbol",
    re.compile(r"^symbol_Exp"): "exponential symbol",
    re.compile(r"^symbol_Log"): "logarithm symbol",
    re.compile(r"^symbol_Sqrt"): "square root symbol",
    # Namespace concepts that are operational
    re.compile(r"^namespace_Analysis"): "analysis (operational namespace)",
    re.compile(r"^namespace_Topology"): "topology (structural namespace)",
    re.compile(r"^namespace_CategoryTheory"): "category theory (verb namespace)",
    re.compile(r"^namespace_MeasureTheory"): "measure theory (verb namespace)",
    # Mizar topics that encode mathematical operations
    re.compile(r"^mizar_topic_integr"): "integration (Mizar)",
    re.compile(r"^mizar_topic_mesfunc"): "measure functions (Mizar)",
    re.compile(r"^mizar_topic_comseq"): "convergent sequences (Mizar)",
    re.compile(r"^mizar_topic_rfunct"): "real functions (Mizar)",
    re.compile(r"^mizar_topic_polynom"): "polynomials (Mizar)",
    # has_ prefixed concepts that encode functional properties
    re.compile(r"^has_alexander_polynomial"): "polynomial invariant",
    re.compile(r"^has_jones_polynomial"): "polynomial invariant",
    re.compile(r"^wildly_ramified"): "ramification structure",
    re.compile(r"^supersingular_isogeny"): "isogeny structure",
}


def classify_concept(concept: str) -> str:
    """Classify a concept as TAUTOLOGICAL, STRUCTURAL, or GENERIC."""
    if concept in GENERIC_CONCEPTS:
        return "GENERIC"
    for pat in TAUTOLOGICAL_PATTERNS:
        if pat.match(concept):
            return "TAUTOLOGICAL"
    if STRUCTURAL_PATTERN.match(concept):
        return "STRUCTURAL"
    for prefix in DOMAIN_PREFIXES:
        if concept.startswith(prefix):
            return "STRUCTURAL"
    return "STRUCTURAL"


def detect_hidden_verb(concept: str) -> str | None:
    """Check if a concept is a hidden verb (noun-form but operational)."""
    for pattern, description in HIDDEN_VERB_PATTERNS.items():
        if pattern.match(concept):
            return description
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print("=" * 70)
    print("  FOOL'S GOLD ASSAY — Re-examining tautological pairs")
    print("=" * 70)

    # 1. Load sweep results
    if not SWEEP_PATH.exists():
        print(f"  ERROR: {SWEEP_PATH} not found. Run tensor_validation_sweep.py first.")
        return
    sweep = json.loads(SWEEP_PATH.read_text(encoding="utf-8"))

    # 2. Identify the confound pairs (tautological verdict, 0 structural concepts)
    confound_pairs = []
    for pair_data in sweep["pairs"]:
        if pair_data["verdict"] == "TAUTOLOGICAL" and pair_data["n_structural"] == 0:
            confound_pairs.append(pair_data)

    print(f"\n  Found {len(confound_pairs)} confound pairs to re-examine:")
    for p in confound_pairs:
        print(f"    {p['pair']}: {p['n_shared_concepts']} shared concepts, "
              f"confound={p.get('confound_type', 'unknown')}")

    # 3. Load ALL concept links and build per-dataset concept sets
    print(f"\n  Loading concept links from {LINKS_PATH.name}...")
    ds_concepts = defaultdict(lambda: defaultdict(int))  # {dataset: {concept: count}}

    with open(LINKS_PATH, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            ds = rec["dataset"]
            concept = rec["concept"]
            ds_concepts[ds][concept] += 1

    total_concepts_loaded = sum(len(v) for v in ds_concepts.values())
    print(f"  Loaded concepts for {len(ds_concepts)} datasets ({total_concepts_loaded:,} concept entries)")

    # 4. Load the concept index to check for newly-added verb extractors
    concept_index = {}
    if CONCEPTS_PATH.exists():
        with open(CONCEPTS_PATH, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                concept_index[rec["id"]] = rec
        print(f"  Concept index: {len(concept_index):,} concepts")
    else:
        print(f"  WARNING: {CONCEPTS_PATH} not found; skipping concept index check")

    # Count verb concepts in index
    n_verb_in_index = sum(1 for c in concept_index.values() if c.get("type") == "verb")
    print(f"  Verb concepts in index: {n_verb_in_index:,}")

    # 5. Analyze each confound pair
    print(f"\n{'='*70}")
    print("  PAIR-BY-PAIR ANALYSIS")
    print(f"{'='*70}")

    results = []
    for pair_data in confound_pairs:
        pair_name = pair_data["pair"]
        ds1, ds2 = pair_name.split("--")
        print(f"\n  --- {pair_name} ---")

        concepts_ds1 = ds_concepts.get(ds1, {})
        concepts_ds2 = ds_concepts.get(ds2, {})

        if not concepts_ds1:
            print(f"    WARNING: No concepts found for {ds1}")
        if not concepts_ds2:
            print(f"    WARNING: No concepts found for {ds2}")

        # All shared concepts
        shared_all = set(concepts_ds1.keys()) & set(concepts_ds2.keys())
        print(f"    Total shared concepts: {len(shared_all)}")

        # Classify all shared concepts
        classification = defaultdict(list)
        for c in sorted(shared_all):
            ctype = classify_concept(c)
            classification[ctype].append(c)

        for ctype, concepts in sorted(classification.items()):
            print(f"      {ctype}: {len(concepts)}")
            if len(concepts) <= 10:
                for c in concepts:
                    print(f"        - {c} (ds1={concepts_ds1[c]}, ds2={concepts_ds2[c]})")
            else:
                for c in concepts[:5]:
                    print(f"        - {c} (ds1={concepts_ds1[c]}, ds2={concepts_ds2[c]})")
                print(f"        ... and {len(concepts) - 5} more")

        # Check for verb concepts
        verb_shared = [c for c in shared_all if STRUCTURAL_PATTERN.match(c)]
        print(f"\n    Verb concepts shared: {len(verb_shared)}")
        for vc in verb_shared:
            print(f"      - {vc} (ds1={concepts_ds1[vc]}, ds2={concepts_ds2[vc]})")

        # Check for hidden verbs
        hidden_verbs = []
        for c in shared_all:
            hv = detect_hidden_verb(c)
            if hv:
                hidden_verbs.append({
                    "concept": c,
                    "description": hv,
                    "count_ds1": concepts_ds1[c],
                    "count_ds2": concepts_ds2[c],
                })
        print(f"    Hidden verbs found: {len(hidden_verbs)}")
        for hv in hidden_verbs:
            print(f"      - {hv['concept']}: {hv['description']} "
                  f"(ds1={hv['count_ds1']}, ds2={hv['count_ds2']})")

        # Check for concepts in the index that are verb-typed but not verb-prefixed
        # (newly added extractors might have created bridges)
        new_potential_bridges = []
        for c in shared_all:
            if c in concept_index and concept_index[c].get("type") == "verb":
                if not STRUCTURAL_PATTERN.match(c):
                    new_potential_bridges.append({
                        "concept": c,
                        "index_entry": concept_index[c],
                        "count_ds1": concepts_ds1[c],
                        "count_ds2": concepts_ds2[c],
                    })

        # Also check: are there verb concepts in EITHER dataset that are CLOSE
        # to the other dataset's concepts? (near-miss bridges)
        verb_ds1_only = [c for c in concepts_ds1 if STRUCTURAL_PATTERN.match(c) and c not in shared_all]
        verb_ds2_only = [c for c in concepts_ds2 if STRUCTURAL_PATTERN.match(c) and c not in shared_all]
        print(f"\n    Verb concepts in {ds1} only: {len(verb_ds1_only)}")
        print(f"    Verb concepts in {ds2} only: {len(verb_ds2_only)}")

        # Look for near-misses: verb concepts that differ only by suffix
        near_misses = []
        verb_stems_ds1 = {}
        for vc in verb_ds1_only:
            # Extract stem: verb_involves_X -> X
            parts = vc.split("_", 2)
            if len(parts) >= 3:
                stem = parts[2]
                verb_stems_ds1[stem] = vc

        for vc in verb_ds2_only:
            parts = vc.split("_", 2)
            if len(parts) >= 3:
                stem = parts[2]
                if stem in verb_stems_ds1:
                    near_misses.append({
                        "stem": stem,
                        "ds1_concept": verb_stems_ds1[stem],
                        "ds2_concept": vc,
                        "count_ds1": concepts_ds1[verb_stems_ds1[stem]],
                        "count_ds2": concepts_ds2[vc],
                    })

        if near_misses:
            print(f"    Near-miss verb bridges: {len(near_misses)}")
            for nm in near_misses[:10]:
                print(f"      stem='{nm['stem']}': {nm['ds1_concept']} <-> {nm['ds2_concept']}")

        # Verdict
        if verb_shared:
            verdict = "UPGRADED"
            reason = f"Found {len(verb_shared)} verb bridge(s): {[v for v in verb_shared[:5]]}"
        elif hidden_verbs:
            verdict = "UPGRADED"
            reason = f"Found {len(hidden_verbs)} hidden verb bridge(s): {[h['concept'] for h in hidden_verbs[:5]]}"
        elif new_potential_bridges:
            verdict = "UPGRADED"
            reason = f"Found {len(new_potential_bridges)} newly-indexed verb bridge(s)"
        elif near_misses:
            verdict = "NEEDS_MORE_DATA"
            reason = (f"No direct verb bridges, but {len(near_misses)} near-miss stem(s) "
                      f"suggest better concept extraction could find bridges")
        else:
            verdict = "CONFIRMED_FOOLS_GOLD"
            reason = "No verb concepts, no hidden verbs, no near-misses"

        print(f"\n    VERDICT: {verdict}")
        print(f"    Reason:  {reason}")

        result = {
            "pair": pair_name,
            "datasets": [ds1, ds2],
            "original_sweep": {
                "n_shared_concepts": pair_data["n_shared_concepts"],
                "n_tautological": pair_data["n_tautological"],
                "n_structural": pair_data["n_structural"],
                "confound_type": pair_data.get("confound_type", "unknown"),
                "raw_correlation": pair_data.get("raw_correlation"),
                "partial_correlation": pair_data.get("partial_correlation"),
            },
            "deep_analysis": {
                "total_shared_concepts": len(shared_all),
                "shared_by_type": {
                    ctype: len(concepts) for ctype, concepts in sorted(classification.items())
                },
                "all_shared_concepts": [
                    {
                        "concept": c,
                        "type": classify_concept(c),
                        "count_ds1": concepts_ds1[c],
                        "count_ds2": concepts_ds2[c],
                        "hidden_verb": detect_hidden_verb(c),
                    }
                    for c in sorted(shared_all)
                ],
                "verb_bridges": [
                    {
                        "concept": vc,
                        "count_ds1": concepts_ds1[vc],
                        "count_ds2": concepts_ds2[vc],
                    }
                    for vc in verb_shared
                ],
                "hidden_verbs": hidden_verbs,
                "newly_indexed_bridges": new_potential_bridges,
                "near_miss_stems": near_misses[:20],
                "verb_concepts_ds1_only": len(verb_ds1_only),
                "verb_concepts_ds2_only": len(verb_ds2_only),
            },
            "verdict": verdict,
            "reason": reason,
        }
        results.append(result)

    # 6. Summary
    elapsed = time.time() - t0
    verdicts = Counter(r["verdict"] for r in results)

    print(f"\n{'='*70}")
    print(f"  FOOL'S GOLD ASSAY SUMMARY")
    print(f"{'='*70}")
    print(f"  Pairs analyzed:        {len(results)}")
    print(f"  CONFIRMED_FOOLS_GOLD:  {verdicts.get('CONFIRMED_FOOLS_GOLD', 0)}")
    print(f"  UPGRADED:              {verdicts.get('UPGRADED', 0)}")
    print(f"  NEEDS_MORE_DATA:       {verdicts.get('NEEDS_MORE_DATA', 0)}")
    print(f"  Time elapsed:          {elapsed:.1f}s")
    print(f"{'='*70}")

    # 7. Save
    output = {
        "meta": {
            "generated": datetime.now().isoformat(timespec="seconds"),
            "sweep_source": str(SWEEP_PATH.name),
            "n_confound_pairs": len(confound_pairs),
            "elapsed_seconds": round(elapsed, 2),
            "concept_index_size": len(concept_index),
            "verb_concepts_in_index": n_verb_in_index,
        },
        "verdict_summary": dict(verdicts),
        "pairs": results,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
