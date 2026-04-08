"""
Explorer: Bridge Troll — Systematically test whether disconnected dataset pairs can be bridged.
================================================================================================
Loads tensor bridge SVD results and concept links, then for every dataset pair
with bond_dim = 0 (no structural bridge detected), attempts to find:

  1. Shared concepts below SVD threshold (BRIDGEABLE)
  2. Indirect 2-hop bridges through a third dataset (INDIRECTLY BRIDGEABLE)
  3. Closest concepts by string overlap (TRULY DISCONNECTED)
  4. Size-starved pairs (NEEDS DATA)

Usage:
    python explorer_bridge_troll.py
"""

import json
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths & imports
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

REPO = Path(__file__).resolve().parents[3]
DATA_DIR = REPO / "cartography" / "convergence" / "data"
LINKS_FILE = DATA_DIR / "concept_links.jsonl"
BRIDGES_FILE = DATA_DIR / "tensor_bridges.json"
OUTPUT_FILE = DATA_DIR / "bridge_troll_report.json"

# Minimum objects in a dataset before we call it "NEEDS DATA"
MIN_OBJECTS_THRESHOLD = 50


# ---------------------------------------------------------------------------
# Load concept links: per-dataset concept sets, per-concept dataset sets
# ---------------------------------------------------------------------------

def load_concept_links():
    """
    Returns:
      - ds_concepts:   {dataset: set of concepts}
      - concept_datasets: {concept: set of datasets}
      - ds_object_count: {dataset: number of unique objects}
      - ds_objects_per_concept: {dataset: {concept: set of object_ids}}
    """
    ds_concepts = defaultdict(set)
    concept_datasets = defaultdict(set)
    ds_object_count = defaultdict(set)
    ds_objects_per_concept = defaultdict(lambda: defaultdict(set))

    print("[Troll] Loading concept_links.jsonl...")
    count = 0
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                ds = rec["dataset"]
                obj = rec["object_id"]
                con = rec["concept"]
                ds_concepts[ds].add(con)
                concept_datasets[con].add(ds)
                ds_object_count[ds].add(obj)
                ds_objects_per_concept[ds][con].add(obj)
                count += 1
            except (json.JSONDecodeError, KeyError):
                pass

    ds_obj_counts = {ds: len(objs) for ds, objs in ds_object_count.items()}
    print(f"  Loaded {count:,} links across {len(ds_concepts)} datasets")
    for ds in sorted(ds_concepts):
        print(f"    {ds:15s}: {ds_obj_counts.get(ds, 0):>6,} objects, "
              f"{len(ds_concepts[ds]):>6,} concepts")
    return ds_concepts, concept_datasets, ds_obj_counts, ds_objects_per_concept


# ---------------------------------------------------------------------------
# Load tensor bridge SVD results
# ---------------------------------------------------------------------------

def load_svd_results():
    """Load bond dimensions from tensor_bridges.json."""
    print("[Troll] Loading tensor_bridges.json...")
    with open(BRIDGES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    svd = data.get("svd_bond_dimensions", {})
    print(f"  Loaded {len(svd)} dataset pair SVD results")
    return svd


# ---------------------------------------------------------------------------
# String similarity for closest-concept matching
# ---------------------------------------------------------------------------

def _concept_words(concept):
    """Extract meaningful words from a concept name."""
    # Strip prefixes like verb_involves_, crossing_, integer_, etc.
    c = concept.lower()
    for prefix in ("verb_involves_", "crossing_", "integer_", "has_property_"):
        if c.startswith(prefix):
            c = c[len(prefix):]
    # Split on underscores and non-alpha
    import re
    words = set(re.split(r"[^a-z]+", c))
    words.discard("")
    return words


def concept_similarity(c1, c2):
    """Jaccard similarity of word tokens in two concept names."""
    w1 = _concept_words(c1)
    w2 = _concept_words(c2)
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def find_closest_concepts(concepts_a, concepts_b, top_k=5):
    """
    Find the top-k most similar concept pairs between two sets.
    Returns list of (concept_a, concept_b, similarity).
    """
    best = []
    # For efficiency, only compare verb concepts and non-trivial concepts
    # Filter out very generic concepts
    filtered_a = [c for c in concepts_a if len(c) > 5]
    filtered_b = [c for c in concepts_b if len(c) > 5]

    # If sets are huge, subsample
    max_compare = 500
    if len(filtered_a) > max_compare:
        filtered_a = sorted(filtered_a)[:max_compare]
    if len(filtered_b) > max_compare:
        filtered_b = sorted(filtered_b)[:max_compare]

    for ca in filtered_a:
        for cb in filtered_b:
            sim = concept_similarity(ca, cb)
            if sim > 0:
                best.append((ca, cb, sim))

    best.sort(key=lambda x: -x[2])
    return best[:top_k]


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run_bridge_troll():
    t0 = time.time()

    # 1. Load data
    ds_concepts, concept_datasets, ds_obj_counts, ds_objects_per_concept = load_concept_links()
    svd_results = load_svd_results()

    # 2. Find all pairs with bond_dim = 0
    disconnected_pairs = []
    for pair_key, info in svd_results.items():
        if info.get("bond_dim", -1) == 0:
            parts = pair_key.split("--")
            if len(parts) == 2:
                disconnected_pairs.append((parts[0], parts[1]))

    print(f"\n[Troll] Found {len(disconnected_pairs)} disconnected pairs (bond_dim = 0)")

    # 3. Build connectivity map for indirect bridge detection
    # connected_pairs: set of (d1, d2) where bond_dim > 0
    connected_pairs = set()
    bond_dims = {}
    for pair_key, info in svd_results.items():
        parts = pair_key.split("--")
        if len(parts) == 2:
            bd = info.get("bond_dim", 0)
            bond_dims[(parts[0], parts[1])] = bd
            bond_dims[(parts[1], parts[0])] = bd
            if bd > 0:
                connected_pairs.add((parts[0], parts[1]))
                connected_pairs.add((parts[1], parts[0]))

    all_datasets = sorted(ds_concepts.keys())

    # 4. Analyze each disconnected pair
    print(f"\n[Troll] Analyzing each disconnected pair...")
    results = []

    for d1, d2 in sorted(disconnected_pairs):
        concepts_a = ds_concepts.get(d1, set())
        concepts_b = ds_concepts.get(d2, set())
        obj_count_a = ds_obj_counts.get(d1, 0)
        obj_count_b = ds_obj_counts.get(d2, 0)

        entry = {
            "pair": f"{d1}--{d2}",
            "dataset_a": d1,
            "dataset_b": d2,
            "objects_a": obj_count_a,
            "objects_b": obj_count_b,
            "concepts_a_count": len(concepts_a),
            "concepts_b_count": len(concepts_b),
        }

        # Check for NEEDS DATA
        if obj_count_a < MIN_OBJECTS_THRESHOLD or obj_count_b < MIN_OBJECTS_THRESHOLD:
            small_ds = d1 if obj_count_a < obj_count_b else d2
            entry["classification"] = "NEEDS_DATA"
            entry["reason"] = (
                f"{small_ds} has only {min(obj_count_a, obj_count_b)} objects "
                f"(threshold: {MIN_OBJECTS_THRESHOLD})"
            )
            entry["shared_concepts"] = []
            entry["indirect_bridges"] = []
            entry["closest_concepts"] = []
            results.append(entry)
            continue

        # Check for shared concepts (even below SVD threshold)
        shared = concepts_a & concepts_b
        shared_list = sorted(shared)

        # Filter shared concepts: separate verb vs noun
        shared_verbs = [c for c in shared_list if c.startswith("verb_")]
        shared_nouns = [c for c in shared_list if not c.startswith("verb_")]

        entry["shared_concepts"] = shared_list
        entry["n_shared"] = len(shared)
        entry["n_shared_verbs"] = len(shared_verbs)
        entry["n_shared_nouns"] = len(shared_nouns)
        entry["shared_verbs"] = shared_verbs[:20]
        entry["shared_nouns"] = shared_nouns[:20]

        # Check for indirect bridges (2-hop)
        indirect_bridges = []
        for dc in all_datasets:
            if dc == d1 or dc == d2:
                continue
            a_to_c = bond_dims.get((d1, dc), bond_dims.get((dc, d1), 0))
            c_to_b = bond_dims.get((dc, d2), bond_dims.get((d2, dc), 0))
            if a_to_c > 0 and c_to_b > 0:
                # Find the bridging concepts in each hop
                shared_ac = ds_concepts.get(d1, set()) & ds_concepts.get(dc, set())
                shared_cb = ds_concepts.get(dc, set()) & ds_concepts.get(d2, set())
                indirect_bridges.append({
                    "intermediary": dc,
                    "bond_dim_a_c": a_to_c,
                    "bond_dim_c_b": c_to_b,
                    "shared_concepts_a_c": len(shared_ac),
                    "shared_concepts_c_b": len(shared_cb),
                    "bridging_concepts_sample": sorted(shared_ac & shared_cb)[:10],
                })
        entry["indirect_bridges"] = indirect_bridges
        entry["n_indirect_bridges"] = len(indirect_bridges)

        # Find closest concepts if no direct shared concepts
        if len(shared) == 0:
            closest = find_closest_concepts(concepts_a, concepts_b, top_k=5)
            entry["closest_concepts"] = [
                {"concept_a": ca, "concept_b": cb, "similarity": round(sim, 4)}
                for ca, cb, sim in closest
            ]
        else:
            entry["closest_concepts"] = []

        # Classify
        if len(shared) > 0:
            # Concepts exist but SVD didn't detect them -- below threshold
            entry["classification"] = "BRIDGEABLE"
            # Identify the specific concept that would create the strongest bridge
            # Score by: how many objects in each dataset have this concept?
            bridge_scores = []
            for concept in shared_list:
                objs_a = len(ds_objects_per_concept.get(d1, {}).get(concept, set()))
                objs_b = len(ds_objects_per_concept.get(d2, {}).get(concept, set()))
                bridge_scores.append({
                    "concept": concept,
                    "objects_in_a": objs_a,
                    "objects_in_b": objs_b,
                    "bridge_strength": objs_a * objs_b,
                })
            bridge_scores.sort(key=lambda x: -x["bridge_strength"])
            entry["best_bridge_concept"] = bridge_scores[0] if bridge_scores else None
            entry["top_bridge_concepts"] = bridge_scores[:5]
            entry["reason"] = (
                f"{len(shared)} shared concepts exist but below SVD threshold. "
                f"Best bridge: {bridge_scores[0]['concept']} "
                f"({bridge_scores[0]['objects_in_a']} x {bridge_scores[0]['objects_in_b']} objects)"
                if bridge_scores else "Shared concepts found but no objects"
            )
        elif len(indirect_bridges) > 0:
            entry["classification"] = "INDIRECTLY_BRIDGEABLE"
            best_hop = max(indirect_bridges,
                           key=lambda x: x["bond_dim_a_c"] + x["bond_dim_c_b"])
            entry["best_indirect"] = best_hop
            entry["reason"] = (
                f"No direct shared concepts, but {len(indirect_bridges)} 2-hop "
                f"bridges exist. Best path: {d1} -> {best_hop['intermediary']} -> {d2} "
                f"(bond dims {best_hop['bond_dim_a_c']}, {best_hop['bond_dim_c_b']})"
            )
        else:
            entry["classification"] = "TRULY_DISCONNECTED"
            if entry["closest_concepts"]:
                cc = entry["closest_concepts"][0]
                entry["reason"] = (
                    f"No shared concepts, no indirect bridges. "
                    f"Closest pair: '{cc['concept_a']}' ~ '{cc['concept_b']}' "
                    f"(similarity {cc['similarity']:.3f})"
                )
            else:
                entry["reason"] = "No shared concepts, no indirect bridges, no similar concepts found"

        results.append(entry)

    # 5. Print summary
    class_counts = Counter(r["classification"] for r in results)
    print(f"\n[Troll] Classification summary:")
    for cls in ["BRIDGEABLE", "INDIRECTLY_BRIDGEABLE", "TRULY_DISCONNECTED", "NEEDS_DATA"]:
        print(f"  {cls:25s}: {class_counts.get(cls, 0)}")

    print(f"\n[Troll] Detailed results:")
    for r in results:
        print(f"  {r['pair']:30s} -> {r['classification']:25s} | {r.get('reason', '')[:70]}")

    # 6. Build output
    elapsed = time.time() - t0

    # Separate by classification for easy consumption
    bridgeable = [r for r in results if r["classification"] == "BRIDGEABLE"]
    indirect = [r for r in results if r["classification"] == "INDIRECTLY_BRIDGEABLE"]
    truly_disc = [r for r in results if r["classification"] == "TRULY_DISCONNECTED"]
    needs_data = [r for r in results if r["classification"] == "NEEDS_DATA"]

    output = {
        "meta": {
            "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "description": (
                "Bridge troll: systematic test of disconnected dataset pairs "
                "for hidden or indirect bridges"
            ),
            "total_disconnected_pairs": len(disconnected_pairs),
            "elapsed_seconds": round(elapsed, 2),
        },
        "summary": {
            "BRIDGEABLE": len(bridgeable),
            "INDIRECTLY_BRIDGEABLE": len(indirect),
            "TRULY_DISCONNECTED": len(truly_disc),
            "NEEDS_DATA": len(needs_data),
            "verdict": (
                f"{len(bridgeable)} pairs have shared concepts below SVD threshold, "
                f"{len(indirect)} reachable via 2-hop, "
                f"{len(truly_disc)} truly disconnected, "
                f"{len(needs_data)} need more data."
            ),
        },
        "bridgeable": bridgeable,
        "indirectly_bridgeable": indirect,
        "truly_disconnected": truly_disc,
        "needs_data": needs_data,
        "all_results": results,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[Troll] Saved {OUTPUT_FILE}")
    print(f"[Troll] Done in {elapsed:.1f}s")

    # Highlight actionable findings
    if bridgeable:
        print(f"\n[Troll] ACTION: {len(bridgeable)} pairs are BRIDGEABLE -- "
              f"shared concepts exist but SVD missed them:")
        for r in bridgeable[:5]:
            bc = r.get("best_bridge_concept", {})
            print(f"  {r['pair']}: bridge via '{bc.get('concept', '?')}' "
                  f"({bc.get('objects_in_a', 0)}x{bc.get('objects_in_b', 0)} objects)")

    return output


if __name__ == "__main__":
    run_bridge_troll()
