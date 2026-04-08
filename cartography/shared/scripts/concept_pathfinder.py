"""
Concept Pathfinder — Q10: Proof Interpolation
==============================================
Finds the shortest concept-path between any two mathematical objects
across datasets using BFS on the concept bridge layer.

The path IS the interpolated proof sketch: each hop through a shared
concept is a reasoning step connecting two domains.

Usage:
    python concept_pathfinder.py
"""

import json
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

REPO = SCRIPT_DIR.parents[2]
CONVERGENCE_DATA = REPO / "cartography" / "convergence" / "data"
LINKS_FILE = CONVERGENCE_DATA / "concept_links.jsonl"
OUTPUT_FILE = CONVERGENCE_DATA / "concept_paths.json"


# ---------------------------------------------------------------------------
# Index builder — dict-based, no networkx
# ---------------------------------------------------------------------------

def build_indices(links_file: Path = LINKS_FILE):
    """
    Build two lookup dicts from the concept links file:
      concept_to_objects: concept -> list of (dataset, object_id)
      object_to_concepts: (dataset, object_id) -> list of concepts

    Streams the file — never holds all 1M+ raw records in memory.
    """
    concept_to_objects = defaultdict(list)
    object_to_concepts = defaultdict(list)

    t0 = time.time()
    n = 0
    with open(links_file, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            concept = rec["concept"]
            ds = rec["dataset"]
            oid = rec["object_id"]
            key = (ds, oid)
            concept_to_objects[concept].append(key)
            object_to_concepts[key].append(concept)
            n += 1

    elapsed = time.time() - t0
    print(f"[pathfinder] Loaded {n:,} links "
          f"({len(concept_to_objects):,} concepts, "
          f"{len(object_to_concepts):,} objects) in {elapsed:.1f}s")
    return concept_to_objects, object_to_concepts


# ---------------------------------------------------------------------------
# BFS pathfinder
# ---------------------------------------------------------------------------

def find_path(source_dataset, source_id, target_dataset, target_id,
              concept_to_objects, object_to_concepts, max_hops=6):
    """
    BFS through the bipartite concept graph:
      object -> concept -> object -> concept -> ... -> target

    Returns a list of hops: [(concept, dataset, object_id), ...]
    The first entry is the source, the last is the target.
    Each intermediate entry shows the concept used to bridge and the
    intermediate object reached.

    Returns None if no path found within max_hops.
    """
    source = (source_dataset, source_id)
    target = (target_dataset, target_id)

    if source not in object_to_concepts:
        print(f"  [!] Source {source} not in index")
        return None
    if target not in object_to_concepts:
        print(f"  [!] Target {target} not in index")
        return None

    # Direct connection check
    source_concepts = set(object_to_concepts[source])
    target_concepts = set(object_to_concepts[target])
    shared = source_concepts & target_concepts
    if shared:
        bridge = min(shared, key=lambda c: len(concept_to_objects[c]))
        return [
            {"type": "object", "dataset": source_dataset, "object_id": source_id},
            {"type": "concept", "concept": bridge},
            {"type": "object", "dataset": target_dataset, "object_id": target_id},
        ]

    # BFS: alternating layers of objects and concepts
    # State: (type, key) where type is 'object' or 'concept'
    # Object key = (dataset, object_id), concept key = concept string
    visited_objects = {source}
    visited_concepts = set()

    # Queue entries: (node_type, node_key, path_so_far)
    queue = deque()
    # Expand source into its concepts
    for c in object_to_concepts[source]:
        if c not in visited_concepts:
            visited_concepts.add(c)
            path = [
                {"type": "object", "dataset": source_dataset, "object_id": source_id},
                {"type": "concept", "concept": c},
            ]
            # Check if this concept directly reaches target
            if target in _fast_check_concept(c, concept_to_objects):
                path.append({"type": "object", "dataset": target_dataset, "object_id": target_id})
                return path
            queue.append(("concept", c, path))

    hop = 0
    while queue and hop < max_hops:
        next_queue = deque()
        # Process current layer
        while queue:
            node_type, node_key, path = queue.popleft()

            if node_type == "concept":
                # Expand concept -> objects (cap to avoid explosion on common concepts)
                objects = concept_to_objects[node_key]
                # Limit fan-out: prefer objects from the target dataset
                targets_first = sorted(objects, key=lambda o: (0 if o[0] == target_dataset else 1))
                for obj in targets_first[:200]:
                    if obj in visited_objects:
                        continue
                    visited_objects.add(obj)
                    new_path = path + [{"type": "object", "dataset": obj[0], "object_id": obj[1]}]
                    if obj == target:
                        return new_path
                    next_queue.append(("object", obj, new_path))

            elif node_type == "object":
                # Expand object -> concepts
                for c in object_to_concepts[node_key]:
                    if c in visited_concepts:
                        continue
                    visited_concepts.add(c)
                    new_path = path + [{"type": "concept", "concept": c}]
                    # Check if this concept reaches target
                    if target in _fast_check_concept(c, concept_to_objects):
                        new_path.append({"type": "object", "dataset": target_dataset, "object_id": target_id})
                        return new_path
                    next_queue.append(("concept", c, new_path))

        queue = next_queue
        hop += 1

    return None  # No path found


def _fast_check_concept(concept, concept_to_objects):
    """Return set of (dataset, object_id) for a concept — used for target check."""
    return set(map(tuple, concept_to_objects[concept]))


# ---------------------------------------------------------------------------
# Bridge concept finder
# ---------------------------------------------------------------------------

def find_bridge_concept(dataset_a, dataset_b, concept_to_objects, object_to_concepts,
                        top_n=10):
    """
    Find the concept(s) connecting the most objects between two datasets.
    Returns list of (concept, count_a, count_b, total) sorted by total desc.
    """
    results = []
    for concept, objects in concept_to_objects.items():
        count_a = sum(1 for ds, _ in objects if ds == dataset_a)
        count_b = sum(1 for ds, _ in objects if ds == dataset_b)
        if count_a > 0 and count_b > 0:
            results.append({
                "concept": concept,
                "count_in_A": count_a,
                "count_in_B": count_b,
                "total_bridged": count_a + count_b,
            })

    results.sort(key=lambda r: r["total_bridged"], reverse=True)
    return results[:top_n]


# ---------------------------------------------------------------------------
# Helper: find an object in a dataset matching a pattern
# ---------------------------------------------------------------------------

def find_object(dataset, pattern, object_to_concepts, limit=5):
    """Find objects in a dataset whose ID contains pattern (case-insensitive)."""
    pattern_lower = pattern.lower()
    matches = []
    for (ds, oid) in object_to_concepts:
        if ds == dataset and pattern_lower in oid.lower():
            matches.append(oid)
            if len(matches) >= limit:
                break
    return matches


def find_object_by_concept(dataset, concept_pattern, concept_to_objects, limit=5):
    """Find objects in a dataset that have a concept matching the pattern."""
    pattern_lower = concept_pattern.lower()
    seen = set()
    matches = []
    for concept, objects in concept_to_objects.items():
        if pattern_lower in concept.lower():
            for ds, oid in objects:
                if ds == dataset and oid not in seen:
                    seen.add(oid)
                    matches.append(oid)
                    if len(matches) >= limit:
                        return matches
    return matches


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def format_path(path):
    """Format a path for human reading."""
    if path is None:
        return "  No path found."
    lines = []
    for i, hop in enumerate(path):
        if hop["type"] == "object":
            lines.append(f"  [{hop['dataset']}] {hop['object_id']}")
        elif hop["type"] == "concept":
            lines.append(f"    --({hop['concept']})-->")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main: run test cases and save results
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("Concept Pathfinder — Q10: Proof Interpolation")
    print("=" * 70)

    c2o, o2c = build_indices()

    # -------------------------------------------------------------------
    # Find actual objects for our test cases
    # Use concept-aware search for better matches
    # -------------------------------------------------------------------
    print("\n--- Locating test objects ---")

    # Fungrim: find objects with zeta-related concepts
    fungrim_zeta = find_object_by_concept("Fungrim", "riemann_zeta", c2o)
    if not fungrim_zeta:
        fungrim_zeta = find_object_by_concept("Fungrim", "zeta", c2o)
    if not fungrim_zeta:
        fungrim_zeta = find_object("Fungrim", "zeta", o2c)
    print(f"Fungrim zeta objects: {fungrim_zeta[:3]}")

    # mathlib: find NumberTheory objects with zeta or number-theoretic concepts
    mathlib_nt = find_object_by_concept("mathlib", "zeta", c2o)
    if not mathlib_nt:
        mathlib_nt = find_object("mathlib", "NumberTheory", o2c)
    print(f"mathlib zeta/NumberTheory objects: {mathlib_nt[:3]}")

    knot_objects = find_object("KnotInfo", "3_1", o2c)
    print(f"KnotInfo knot objects: {knot_objects[:3]}")

    lmfdb_ec = find_object("LMFDB", "11.a", o2c)
    print(f"LMFDB elliptic curves: {lmfdb_ec[:3]}")

    antedb_objects = find_object_by_concept("ANTEDB", "verb_involves_prime", c2o)
    if not antedb_objects:
        antedb_objects = find_object("ANTEDB", "prime", o2c)
    print(f"ANTEDB prime objects: {antedb_objects[:3]}")

    isogeny_objects = find_object("Isogenies", "isogeny", o2c)
    print(f"Isogenies objects: {isogeny_objects[:3]}")

    # -------------------------------------------------------------------
    # Test 1: Fungrim zeta -> mathlib NumberTheory
    # -------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TEST 1: Fungrim zeta formula -> mathlib NumberTheory module")
    print("=" * 70)

    src_fungrim = fungrim_zeta[0] if fungrim_zeta else None
    tgt_mathlib = mathlib_nt[0] if mathlib_nt else None

    path1 = None
    if src_fungrim and tgt_mathlib:
        t0 = time.time()
        path1 = find_path("Fungrim", src_fungrim, "mathlib", tgt_mathlib, c2o, o2c)
        print(f"  Time: {time.time() - t0:.2f}s")
        print(format_path(path1))
    else:
        print("  Could not find test objects.")

    # -------------------------------------------------------------------
    # Test 2: KnotInfo knot -> LMFDB elliptic curve
    # -------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TEST 2: KnotInfo knot -> LMFDB elliptic curve")
    print("=" * 70)

    src_knot = knot_objects[0] if knot_objects else None
    tgt_lmfdb = lmfdb_ec[0] if lmfdb_ec else None

    path2 = None
    if src_knot and tgt_lmfdb:
        t0 = time.time()
        path2 = find_path("KnotInfo", src_knot, "LMFDB", tgt_lmfdb, c2o, o2c)
        print(f"  Time: {time.time() - t0:.2f}s")
        print(format_path(path2))
    else:
        print("  Could not find test objects.")

    # -------------------------------------------------------------------
    # Test 3: ANTEDB theorem -> Isogenies graph
    # -------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TEST 3: ANTEDB theorem -> Isogenies graph")
    print("=" * 70)

    src_ante = antedb_objects[0] if antedb_objects else None
    tgt_iso = isogeny_objects[0] if isogeny_objects else None

    path3 = None
    if src_ante and tgt_iso:
        t0 = time.time()
        path3 = find_path("ANTEDB", src_ante, "Isogenies", tgt_iso, c2o, o2c)
        print(f"  Time: {time.time() - t0:.2f}s")
        print(format_path(path3))
    else:
        print("  Could not find test objects.")

    # -------------------------------------------------------------------
    # Bridge concept analysis
    # -------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("BRIDGE CONCEPTS")
    print("=" * 70)

    pairs = [
        ("Fungrim", "mathlib"),
        ("KnotInfo", "LMFDB"),
        ("ANTEDB", "Isogenies"),
        ("LMFDB", "NumberFields"),
        ("mathlib", "MMLKG"),
    ]
    bridge_results = {}
    for da, db in pairs:
        bridges = find_bridge_concept(da, db, c2o, o2c, top_n=5)
        bridge_results[f"{da}--{db}"] = bridges
        print(f"\n  {da} <-> {db}:")
        for b in bridges[:3]:
            print(f"    {b['concept']:40s}  A={b['count_in_A']:5d}  B={b['count_in_B']:5d}  total={b['total_bridged']}")

    # -------------------------------------------------------------------
    # Save results
    # -------------------------------------------------------------------
    output = {
        "meta": {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "description": "Concept pathfinder results — proof interpolation via BFS on concept bridge layer",
        },
        "test_paths": [],
        "bridge_concepts": bridge_results,
    }

    test_cases = [
        {"name": "Fungrim_zeta -> mathlib_NumberTheory",
         "source": {"dataset": "Fungrim", "object_id": src_fungrim},
         "target": {"dataset": "mathlib", "object_id": tgt_mathlib},
         "path": path1},
        {"name": "KnotInfo_knot -> LMFDB_elliptic_curve",
         "source": {"dataset": "KnotInfo", "object_id": src_knot},
         "target": {"dataset": "LMFDB", "object_id": tgt_lmfdb},
         "path": path2},
        {"name": "ANTEDB_theorem -> Isogenies_graph",
         "source": {"dataset": "ANTEDB", "object_id": src_ante},
         "target": {"dataset": "Isogenies", "object_id": tgt_iso},
         "path": path3},
    ]
    output["test_paths"] = test_cases

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[pathfinder] Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
