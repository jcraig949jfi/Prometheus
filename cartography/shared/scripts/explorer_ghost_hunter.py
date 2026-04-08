"""
Explorer Ghost Hunter — Sharpen bridge ghosts into specific mathematical predictions.
=====================================================================================
Takes the 5 BRIDGE_GHOSTs from ghost_nodes.json and for each one:

1. Identifies mathematical object type (operator, function, group, representation, formula)
2. Determines the two domains it connects and bridge direction
3. Infers a candidate defining property from the verb concepts
4. Explains why existing structures fail to fill this role

Usage:
    python explorer_ghost_hunter.py
"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

CONVERGENCE = SCRIPT_DIR.parents[1] / "convergence"
GHOST_FILE = CONVERGENCE / "data" / "ghost_nodes.json"
LINKS_FILE = CONVERGENCE / "data" / "concept_links.jsonl"
OUTPUT_FILE = CONVERGENCE / "data" / "ghost_predictions.json"

# ---------------------------------------------------------------------------
# Verb-to-object-type mapping
# ---------------------------------------------------------------------------
VERB_TO_OBJECT_TYPE = {
    "verb_involves_galois":   "group/representation",
    "verb_involves_zeta":     "function",
    "verb_involves_counting": "combinatorial formula",
    "verb_involves_prime":    "arithmetic structure",
    "verb_involves_lattice":  "geometric structure",
    "verb_involves_long":     "extended construction",
}

# Verb-to-mathematical-domain mapping
VERB_TO_DOMAIN = {
    "verb_involves_galois":   "algebraic number theory (Galois theory)",
    "verb_involves_zeta":     "analytic number theory (zeta/L-functions)",
    "verb_involves_counting": "enumerative combinatorics",
    "verb_involves_prime":    "prime number theory",
    "verb_involves_lattice":  "lattice theory / algebraic geometry",
    "verb_involves_long":     "asymptotic / long-range structure",
}

# Candidate property inference: pair of verbs -> predicted property
PAIR_TO_PROPERTY = {
    ("verb_involves_counting", "verb_involves_prime"): (
        "A prime-counting formula — a combinatorial identity whose terms "
        "enumerate prime-related objects (e.g., a closed-form or generating "
        "function for prime partitions, prime k-tuples, or sieve residues)"
    ),
    ("verb_involves_galois", "verb_involves_long"): (
        "A Galois representation with long-range structure — an automorphic "
        "form or Galois module whose image extends over a long exact sequence, "
        "connecting local Galois cohomology to global invariants"
    ),
    ("verb_involves_galois", "verb_involves_zeta"): (
        "A Galois representation whose L-function has specific zeta properties — "
        "the Artin L-function or automorphic L-function attached to a Galois "
        "representation, encoding arithmetic of the representation in analytic data"
    ),
    ("verb_involves_lattice", "verb_involves_zeta"): (
        "A lattice zeta function — an Epstein zeta function or theta series "
        "attached to a lattice, encoding the lattice's geometry in analytic "
        "continuation and functional equation properties"
    ),
    ("verb_involves_long", "verb_involves_zeta"): (
        "A zeta function with long-range asymptotic behavior — a Dirichlet "
        "series or spectral zeta function whose analytic properties (pole "
        "structure, growth in critical strip) encode long-range correlations"
    ),
}

# Why existing objects fail: pair -> structural gap explanation
PAIR_TO_GAP_REASON = {
    ("verb_involves_counting", "verb_involves_prime"): (
        "Fungrim has prime-related formulas and counting-related formulas "
        "separately, but no single formula that COMBINES combinatorial "
        "enumeration with primality. Existing prime formulas are analytic "
        "(PrimePi, prime zeta), not combinatorial. Existing counting formulas "
        "enumerate partitions/permutations but ignore prime structure."
    ),
    ("verb_involves_galois", "verb_involves_long"): (
        "mathlib formalizes Galois theory (field extensions, automorphisms) "
        "and long exact sequences separately. The missing bridge is a "
        "formalized connection: Galois cohomology's long exact sequence "
        "as a computational tool. mathlib's Galois theory stops at finite "
        "extensions; the 'long' structure (infinite Galois groups, profinite "
        "completions) lacks formalization."
    ),
    ("verb_involves_galois", "verb_involves_zeta"): (
        "mathlib has Galois theory and some L-function stubs but no "
        "formalized Artin L-function or connection between Galois "
        "representations and zeta/L-functions. Fungrim has the formulas "
        "(e.g., Dedekind zeta factoring over Artin L-functions) but these "
        "exist as analytic identities, not as algebraic objects mathlib "
        "could typecheck."
    ),
    ("verb_involves_lattice", "verb_involves_zeta"): (
        "mathlib formalizes lattices (as submodules, as ordered sets) and "
        "has basic zeta function definitions, but no Epstein zeta function "
        "or theta series for lattices. Fungrim has Jacobi theta and "
        "Dedekind eta formulas involving lattices, but the lattice-zeta "
        "bridge (lattice -> theta series -> L-function) is not in mathlib's "
        "formalized scope."
    ),
    ("verb_involves_long", "verb_involves_zeta"): (
        "mathlib has some zeta function definitions but no asymptotic analysis "
        "machinery. Fungrim has asymptotic expansions of zeta functions but "
        "these are formula-level, not structural. The missing object is a "
        "formalized asymptotic framework for Dirichlet series — connecting "
        "pole structure to long-range behavior of arithmetic functions."
    ),
}


# ---------------------------------------------------------------------------
# Load concept links
# ---------------------------------------------------------------------------
def load_concept_links():
    """Load concept_links.jsonl into useful indices."""
    print("[1/5] Loading concept links ...")
    t0 = time.time()

    # dataset_concept_objects[ds][concept] = set of object_ids
    dataset_concept_objects = defaultdict(lambda: defaultdict(set))
    # object_concepts[(ds, oid)] = set of concepts
    object_concepts = defaultdict(set)

    with open(LINKS_FILE) as f:
        for line in f:
            r = json.loads(line)
            c, ds, oid = r["concept"], r["dataset"], r["object_id"]
            dataset_concept_objects[ds][c].add(oid)
            object_concepts[(ds, oid)].add(c)

    elapsed = time.time() - t0
    n_links = sum(
        len(objs)
        for ds_data in dataset_concept_objects.values()
        for objs in ds_data.values()
    )
    print(f"       {n_links:,} links across {len(dataset_concept_objects)} datasets ({elapsed:.1f}s)")
    return dataset_concept_objects, object_concepts


# ---------------------------------------------------------------------------
# Load ghost nodes
# ---------------------------------------------------------------------------
def load_bridge_ghosts():
    """Load ghost_nodes.json and extract only BRIDGE_GHOST entries."""
    print("[2/5] Loading bridge ghosts ...")
    with open(GHOST_FILE) as f:
        data = json.load(f)

    bridges = [g for g in data["ghosts"] if g["ghost_type"] == "BRIDGE_GHOST"]
    print(f"       {len(bridges)} bridge ghosts found (from {data['total_ghosts']} total)")
    return bridges


# ---------------------------------------------------------------------------
# Infer object type from verb pair
# ---------------------------------------------------------------------------
def infer_object_type(c1, c2):
    """Infer the mathematical object type from the two verb concepts."""
    t1 = VERB_TO_OBJECT_TYPE.get(c1, "unknown structure")
    t2 = VERB_TO_OBJECT_TYPE.get(c2, "unknown structure")

    # The bridge object sits at the intersection — pick the more specific type
    # Priority: function > group/representation > geometric structure > formula
    priority = {
        "function": 4,
        "group/representation": 3,
        "geometric structure": 2,
        "combinatorial formula": 1,
        "arithmetic structure": 1,
        "extended construction": 0,
    }

    p1, p2 = priority.get(t1, 0), priority.get(t2, 0)
    primary = t1 if p1 >= p2 else t2
    secondary = t2 if p1 >= p2 else t1

    return {
        "primary_type": primary,
        "secondary_type": secondary,
        "description": f"{primary} with {secondary} properties",
    }


# ---------------------------------------------------------------------------
# Find gap objects (have one concept but not the other)
# ---------------------------------------------------------------------------
def find_gap_objects(c1, c2, datasets, dataset_concept_objects, object_concepts):
    """
    For each dataset, find objects that have concept A but not B (and vice versa).
    These are the 'gap objects' — closest to the ghost, having one half of the bridge.
    """
    gap_a_not_b = {}  # ds -> list of objects with c1 but not c2
    gap_b_not_a = {}  # ds -> list of objects with c2 but not c1
    have_both = {}    # ds -> list of objects with both

    for ds in datasets:
        objs_c1 = dataset_concept_objects[ds].get(c1, set())
        objs_c2 = dataset_concept_objects[ds].get(c2, set())

        both = objs_c1 & objs_c2
        only_c1 = objs_c1 - objs_c2
        only_c2 = objs_c2 - objs_c1

        if only_c1:
            gap_a_not_b[ds] = sorted(only_c1)[:20]  # cap for readability
        if only_c2:
            gap_b_not_a[ds] = sorted(only_c2)[:20]
        if both:
            have_both[ds] = sorted(both)[:20]

    return gap_a_not_b, gap_b_not_a, have_both


# ---------------------------------------------------------------------------
# Determine bridge direction
# ---------------------------------------------------------------------------
def determine_direction(c1, c2, datasets_should, dataset_concept_objects):
    """
    Which dataset has MORE objects with concept A? That's the 'source' side.
    The dataset with fewer is the 'target' — the ghost fills the gap from source to target.
    """
    concept_counts = defaultdict(lambda: defaultdict(int))

    for ds in datasets_should:
        concept_counts[ds][c1] = len(dataset_concept_objects[ds].get(c1, set()))
        concept_counts[ds][c2] = len(dataset_concept_objects[ds].get(c2, set()))

    # Aggregate: total objects with c1 vs c2 across all datasets
    total_c1 = sum(concept_counts[ds][c1] for ds in datasets_should)
    total_c2 = sum(concept_counts[ds][c2] for ds in datasets_should)

    if total_c1 >= total_c2:
        source_concept = c1
        target_concept = c2
    else:
        source_concept = c2
        target_concept = c1

    source_domain = VERB_TO_DOMAIN.get(source_concept, "unknown")
    target_domain = VERB_TO_DOMAIN.get(target_concept, "unknown")

    return {
        "source_concept": source_concept,
        "target_concept": target_concept,
        "source_domain": source_domain,
        "target_domain": target_domain,
        "source_object_count": total_c1 if source_concept == c1 else total_c2,
        "target_object_count": total_c2 if source_concept == c1 else total_c1,
        "direction_summary": f"{source_domain} --> {target_domain}",
    }


# ---------------------------------------------------------------------------
# Check why existing objects don't fill the role
# ---------------------------------------------------------------------------
def analyze_existing_failure(c1, c2, have_both, datasets_have, datasets_missing,
                             object_concepts):
    """
    For objects that DO have both concepts, explain why they exist in
    datasets_have but not datasets_missing.
    """
    pair_key = (c1, c2)

    # Collect the extra concepts on objects that have both
    extra_concepts = defaultdict(int)
    exemplars = []

    for ds in datasets_have:
        objs = have_both.get(ds, [])
        for oid in objs[:10]:
            concepts = object_concepts.get((ds, oid), set())
            for c in concepts:
                if c != c1 and c != c2 and c.startswith("verb_"):
                    extra_concepts[c] += 1
            exemplars.append({
                "dataset": ds,
                "object_id": oid,
                "all_verb_concepts": sorted(
                    c for c in concepts if c.startswith("verb_")
                ),
            })

    # Sort extra concepts by frequency
    top_extra = sorted(extra_concepts.items(), key=lambda x: -x[1])[:10]

    structural_reason = PAIR_TO_GAP_REASON.get(pair_key, (
        f"The datasets that have this bridge ({', '.join(datasets_have)}) "
        f"contain objects where {c1} and {c2} co-occur, but the missing "
        f"dataset(s) ({', '.join(datasets_missing)}) lack such objects. "
        f"This suggests a formalization or representation gap rather than "
        f"a mathematical impossibility."
    ))

    return {
        "structural_reason": structural_reason,
        "exemplar_objects": exemplars[:5],
        "common_extra_verbs": [{"concept": c, "count": n} for c, n in top_extra],
    }


# ---------------------------------------------------------------------------
# Sharpen one ghost into a prediction
# ---------------------------------------------------------------------------
def sharpen_ghost(ghost, dataset_concept_objects, object_concepts):
    """Convert a raw bridge ghost into a detailed prediction."""
    c1, c2 = ghost["c1"], ghost["c2"]
    datasets_have = ghost["datasets_have"]
    datasets_missing = ghost["datasets_missing"]
    datasets_should = ghost["datasets_should"]

    all_datasets = sorted(set(datasets_have + datasets_missing + datasets_should))

    # 1. Object type
    object_type = infer_object_type(c1, c2)

    # 2. Gap objects
    gap_a_not_b, gap_b_not_a, have_both = find_gap_objects(
        c1, c2, all_datasets, dataset_concept_objects, object_concepts
    )

    # 3. Bridge direction
    direction = determine_direction(c1, c2, datasets_should, dataset_concept_objects)

    # 4. Candidate property
    pair_key = (c1, c2)
    candidate_property = PAIR_TO_PROPERTY.get(pair_key, (
        f"An object combining {VERB_TO_DOMAIN.get(c1, c1)} with "
        f"{VERB_TO_DOMAIN.get(c2, c2)}"
    ))

    # 5. Why existing structures fail
    failure_analysis = analyze_existing_failure(
        c1, c2, have_both, datasets_have, datasets_missing, object_concepts
    )

    # Count gap objects for summary
    gap_a_count = sum(len(v) for v in gap_a_not_b.values())
    gap_b_count = sum(len(v) for v in gap_b_not_a.values())
    both_count = sum(len(v) for v in have_both.values())

    prediction = {
        "ghost_id": f"BRIDGE_{c1}_x_{c2}",
        "verb_concepts": [c1, c2],
        "score": ghost["score"],
        "pull": ghost["pull"],
        "mode": ghost["mode"],

        # 1. Mathematical object type
        "object_type": object_type,

        # 2. Domains and direction
        "domains": {
            "domain_1": VERB_TO_DOMAIN.get(c1, c1),
            "domain_2": VERB_TO_DOMAIN.get(c2, c2),
        },
        "bridge_direction": direction,

        # 3. Candidate defining property
        "candidate_property": candidate_property,

        # 4. Why existing structures fail
        "failure_analysis": failure_analysis,

        # Evidence summary
        "evidence": {
            "datasets_have_bridge": datasets_have,
            "datasets_missing_bridge": datasets_missing,
            "datasets_should_have": datasets_should,
            "gap_objects_with_c1_only": {
                ds: objs[:5] for ds, objs in gap_a_not_b.items()
            },
            "gap_objects_with_c2_only": {
                ds: objs[:5] for ds, objs in gap_b_not_a.items()
            },
            "objects_with_both": {
                ds: objs[:5] for ds, objs in have_both.items()
            },
            "counts": {
                "c1_only": gap_a_count,
                "c2_only": gap_b_count,
                "both": both_count,
            },
        },

        # Human-readable summary
        "prediction_summary": (
            f"PREDICTED: A {object_type['description']} connecting "
            f"{VERB_TO_DOMAIN.get(c1, c1)} to {VERB_TO_DOMAIN.get(c2, c2)}. "
            f"Direction: {direction['direction_summary']}. "
            f"Currently {both_count} objects have both concepts (in {', '.join(datasets_have)}), "
            f"but {', '.join(datasets_missing)} lack such an object despite having "
            f"{gap_a_count} objects with {c1} alone and {gap_b_count} with {c2} alone."
        ),
    }

    return prediction


# ---------------------------------------------------------------------------
# Print human-readable report
# ---------------------------------------------------------------------------
def print_report(predictions):
    """Print a human-readable report of all ghost predictions."""
    print(f"\n{'=' * 78}")
    print(f"  BRIDGE GHOST PREDICTIONS — {len(predictions)} ghosts sharpened")
    print(f"{'=' * 78}")

    for i, p in enumerate(predictions, 1):
        print(f"\n{'-' * 78}")
        print(f"  Ghost #{i}: {p['ghost_id']}")
        print(f"  Score: {p['score']:.1f}  |  Pull: {p['pull']:.1f}  |  Mode: {p['mode']}")
        print(f"{'-' * 78}")

        print(f"\n  [1] OBJECT TYPE")
        print(f"      Primary:   {p['object_type']['primary_type']}")
        print(f"      Secondary: {p['object_type']['secondary_type']}")
        print(f"      Combined:  {p['object_type']['description']}")

        print(f"\n  [2] DOMAINS & DIRECTION")
        print(f"      Domain 1:  {p['domains']['domain_1']}")
        print(f"      Domain 2:  {p['domains']['domain_2']}")
        d = p["bridge_direction"]
        print(f"      Direction: {d['direction_summary']}")
        print(f"      Source has {d['source_object_count']} objects, "
              f"target has {d['target_object_count']} objects")

        print(f"\n  [3] CANDIDATE DEFINING PROPERTY")
        # Wrap long property text
        prop = p["candidate_property"]
        words = prop.split()
        line = "      "
        for w in words:
            if len(line) + len(w) + 1 > 78:
                print(line)
                line = "      " + w
            else:
                line += (" " if line.strip() else "") + w
        if line.strip():
            print(line)

        print(f"\n  [4] WHY EXISTING STRUCTURES FAIL")
        reason = p["failure_analysis"]["structural_reason"]
        words = reason.split()
        line = "      "
        for w in words:
            if len(line) + len(w) + 1 > 78:
                print(line)
                line = "      " + w
            else:
                line += (" " if line.strip() else "") + w
        if line.strip():
            print(line)

        # Show exemplars if any
        exemplars = p["failure_analysis"].get("exemplar_objects", [])
        if exemplars:
            print(f"\n      Exemplar objects that DO have both concepts:")
            for ex in exemplars[:3]:
                verbs = ", ".join(ex["all_verb_concepts"][:6])
                print(f"        - {ex['dataset']}/{ex['object_id']}: [{verbs}]")

        extra = p["failure_analysis"].get("common_extra_verbs", [])
        if extra:
            print(f"\n      Common additional verbs on bridge objects:")
            for ev in extra[:5]:
                print(f"        - {ev['concept']} (x{ev['count']})")

        # Gap object counts
        ev = p["evidence"]["counts"]
        print(f"\n  [EVIDENCE]")
        print(f"      Objects with {p['verb_concepts'][0]} only: {ev['c1_only']}")
        print(f"      Objects with {p['verb_concepts'][1]} only: {ev['c2_only']}")
        print(f"      Objects with BOTH: {ev['both']}")
        print(f"      Have bridge: {', '.join(p['evidence']['datasets_have_bridge'])}")
        print(f"      Missing bridge: {', '.join(p['evidence']['datasets_missing_bridge'])}")

    print(f"\n{'=' * 78}")
    print(f"  Full predictions saved to: {OUTPUT_FILE}")
    print(f"{'=' * 78}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()

    # Load data
    dataset_concept_objects, object_concepts = load_concept_links()
    bridges = load_bridge_ghosts()

    if not bridges:
        print("No bridge ghosts found. Nothing to do.")
        return

    # Sharpen each bridge ghost
    print(f"\n[3/5] Sharpening {len(bridges)} bridge ghosts ...")
    predictions = []
    for i, ghost in enumerate(bridges, 1):
        print(f"       Ghost {i}/{len(bridges)}: {ghost['c1']} x {ghost['c2']}")
        pred = sharpen_ghost(ghost, dataset_concept_objects, object_concepts)
        predictions.append(pred)

    # Save predictions
    print(f"\n[4/5] Saving predictions to {OUTPUT_FILE} ...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_bridge_ghosts": len(predictions),
        "predictions": predictions,
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=2)

    # Print human-readable report
    print("\n[5/5] Generating report ...")
    print_report(predictions)

    print(f"Done in {time.time() - t_start:.1f}s total.")


if __name__ == "__main__":
    main()
