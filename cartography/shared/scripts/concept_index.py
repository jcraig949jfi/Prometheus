"""
Concept Index — Atomic concept extraction and bridge detection.
================================================================
Extracts normalized concepts from all datasets and finds cross-domain
bridges (Swanson's ABC model as a database join).

Concepts are atomic: "prime", "modular_form", "determinant_5", "conductor_11".
Links are many-to-many: each dataset object maps to multiple concepts.
Bridges are concept-sharing pairs across different datasets.

Storage:
  convergence/data/concepts.jsonl       — the atoms
  convergence/data/concept_links.jsonl  — many-to-many edges
  convergence/data/bridges.jsonl        — cross-domain bridges

Usage:
    from concept_index import build_index, find_bridges
    build_index()        # Extract concepts from all datasets
    find_bridges()       # Detect cross-domain connections

    python concept_index.py   # Full build + bridge detection
"""

import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

CONVERGENCE = Path(__file__).resolve().parents[2] / "convergence"
CONCEPTS_FILE = CONVERGENCE / "data" / "concepts.jsonl"
LINKS_FILE = CONVERGENCE / "data" / "concept_links.jsonl"
BRIDGES_FILE = CONVERGENCE / "data" / "bridges.jsonl"


def _is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


def _number_concepts(n: int) -> list[str]:
    """Extract mathematical property concepts from an integer."""
    concepts = []
    if isinstance(n, int) and n > 0:
        concepts.append(f"integer_{n}")
        if _is_prime(n):
            concepts.append("prime")
        if n % 2 == 1:
            concepts.append("odd")
        else:
            concepts.append("even")
        if int(math.sqrt(n)) ** 2 == n:
            concepts.append("perfect_square")
        if n < 100:
            concepts.append("small_integer")
        elif n < 1000:
            concepts.append("medium_integer")
        else:
            concepts.append("large_integer")
    return concepts


# ---------------------------------------------------------------------------
# Extractors — one per dataset
# ---------------------------------------------------------------------------

def extract_knotinfo() -> tuple[list[dict], list[dict]]:
    """Extract concepts from KnotInfo knots."""
    from search_engine import _load_knots, _knots_cache, KNOTS_JSON
    if not KNOTS_JSON.exists(): return [], []
    _load_knots()

    concepts = set()
    links = []

    for knot in _knots_cache.get("knots", []):
        name = knot["name"]
        det = knot.get("determinant")
        crossing = knot.get("crossing_number", 0)

        knot_concepts = [f"crossing_{crossing}"]
        if det is not None:
            knot_concepts.extend(_number_concepts(det))
            knot_concepts.append(f"determinant_{det}")
        if knot.get("alex_coeffs"):
            knot_concepts.append("has_alexander_polynomial")
        if knot.get("jones_coeffs"):
            knot_concepts.append("has_jones_polynomial")

        for c in knot_concepts:
            concepts.add(c)
            links.append({
                "concept": c, "dataset": "KnotInfo", "object_id": name,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "KnotInfo"} for c in concepts], links


def extract_lmfdb() -> tuple[list[dict], list[dict]]:
    """Extract concepts from LMFDB objects."""
    from search_engine import _get_duck, CHARON_DB
    if not CHARON_DB.exists(): return [], []

    concepts = set()
    links = []

    con = _get_duck()
    rows = con.execute("""
        SELECT lmfdb_label, object_type, conductor,
               json_extract_string(properties, '$.rank') as rank
        FROM objects LIMIT 50000
    """).fetchall()
    con.close()

    for label, obj_type, conductor, rank in rows:
        obj_concepts = [f"object_type_{obj_type}"]

        if conductor:
            c = int(conductor)
            obj_concepts.extend(_number_concepts(c))
            obj_concepts.append(f"conductor_{c}")

        if rank is not None:
            obj_concepts.append(f"rank_{rank}")

        for concept in obj_concepts:
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "LMFDB", "object_id": label,
                "relationship": "has_property",
            })

    return [{"id": c, "type": "property", "source": "LMFDB"} for c in concepts], links


def extract_fungrim() -> tuple[list[dict], list[dict]]:
    """Extract concepts from Fungrim formulas."""
    from search_engine import FUNGRIM_JSON
    if not FUNGRIM_JSON.exists(): return [], []
    data = json.loads(FUNGRIM_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for formula in data.get("formulas", []):
        fid = formula["id"]
        module = formula["module"]
        concepts.add(f"topic_{module}")
        links.append({
            "concept": f"topic_{module}", "dataset": "Fungrim", "object_id": fid,
            "relationship": "in_module",
        })
        for symbol in formula.get("symbols", []):
            sym_concept = f"symbol_{symbol}"
            concepts.add(sym_concept)
            links.append({
                "concept": sym_concept, "dataset": "Fungrim", "object_id": fid,
                "relationship": "uses_symbol",
            })

    return [{"id": c, "type": "symbol" if c.startswith("symbol_") else "topic",
             "source": "Fungrim"} for c in concepts], links


def extract_antedb() -> tuple[list[dict], list[dict]]:
    """Extract concepts from ANTEDB theorems."""
    from search_engine import ANTEDB_JSON
    if not ANTEDB_JSON.exists(): return [], []
    data = json.loads(ANTEDB_JSON.read_text(encoding="utf-8"))

    concepts = set()
    links = []

    for chapter in data.get("chapters", []):
        ch_name = chapter["chapter"]
        concepts.add(f"topic_{ch_name}")
        for thm in chapter.get("theorems", []):
            tid = f"{ch_name}/{thm['label']}"
            links.append({
                "concept": f"topic_{ch_name}", "dataset": "ANTEDB", "object_id": tid,
                "relationship": "in_chapter",
            })
            for val in thm.get("numerical_values", []):
                concepts.add(f"bound_{val}")
                links.append({
                    "concept": f"bound_{val}", "dataset": "ANTEDB", "object_id": tid,
                    "relationship": "has_bound",
                })

    return [{"id": c, "type": "topic" if "topic_" in c else "bound",
             "source": "ANTEDB"} for c in concepts], links


def extract_mathlib() -> tuple[list[dict], list[dict]]:
    """Extract concepts from mathlib namespace hierarchy."""
    from search_engine import MATHLIB_GRAPH, _load_mathlib, _mathlib_graph
    if not MATHLIB_GRAPH.exists(): return [], []
    _load_mathlib()

    concepts = set()
    links = []

    for node in _mathlib_graph.get("nodes", []):
        name = node if isinstance(node, str) else node.get("name", "")
        parts = name.split(".")
        # Extract namespace as concept
        if len(parts) >= 2:
            ns = parts[1] if parts[0] == "Mathlib" else parts[0]
            concept = f"namespace_{ns}"
            concepts.add(concept)
            links.append({
                "concept": concept, "dataset": "mathlib", "object_id": name,
                "relationship": "in_namespace",
            })
        # Last part is often the specific topic
        if len(parts) >= 3:
            topic = parts[-1]
            if len(topic) > 3:
                concept = f"topic_{topic}"
                concepts.add(concept)
                links.append({
                    "concept": concept, "dataset": "mathlib", "object_id": name,
                    "relationship": "about",
                })

    return [{"id": c, "type": "namespace" if "namespace_" in c else "topic",
             "source": "mathlib"} for c in concepts], links


# ---------------------------------------------------------------------------
# Build and query
# ---------------------------------------------------------------------------

def build_index() -> dict:
    """Extract concepts from all datasets. Returns stats."""
    print("Building concept index...")
    CONVERGENCE.joinpath("data").mkdir(parents=True, exist_ok=True)

    all_concepts = {}  # id → concept dict
    all_links = []

    extractors = [
        ("KnotInfo", extract_knotinfo),
        ("LMFDB", extract_lmfdb),
        ("Fungrim", extract_fungrim),
        ("ANTEDB", extract_antedb),
        ("mathlib", extract_mathlib),
    ]

    for name, fn in extractors:
        print(f"  Extracting {name}...")
        try:
            concepts, links = fn()
            for c in concepts:
                cid = c["id"]
                if cid not in all_concepts:
                    all_concepts[cid] = c
                else:
                    # Merge sources
                    existing = all_concepts[cid]
                    if c["source"] not in existing.get("sources", [existing["source"]]):
                        existing.setdefault("sources", [existing["source"]]).append(c["source"])
            all_links.extend(links)
            print(f"    {len(concepts)} concepts, {len(links)} links")
        except Exception as e:
            print(f"    ERROR: {e}")

    # Write concepts
    with open(CONCEPTS_FILE, "w", encoding="utf-8") as f:
        for c in sorted(all_concepts.values(), key=lambda x: x["id"]):
            f.write(json.dumps(c) + "\n")

    # Write links
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        for link in all_links:
            f.write(json.dumps(link) + "\n")

    stats = {
        "n_concepts": len(all_concepts),
        "n_links": len(all_links),
        "by_dataset": defaultdict(int),
    }
    for link in all_links:
        stats["by_dataset"][link["dataset"]] += 1
    stats["by_dataset"] = dict(stats["by_dataset"])

    print(f"\nIndex built: {stats['n_concepts']} concepts, {stats['n_links']} links")
    print(f"  By dataset: {stats['by_dataset']}")
    return stats


def find_bridges(min_datasets: int = 2, max_results: int = 100) -> list[dict]:
    """Find concepts shared across multiple datasets — these are bridge points."""
    print("\nFinding bridges...")

    # Load links
    links_by_concept = defaultdict(lambda: defaultdict(list))
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            link = json.loads(line)
            links_by_concept[link["concept"]][link["dataset"]].append(link["object_id"])

    # Find concepts present in 2+ datasets
    bridges = []
    for concept, datasets in links_by_concept.items():
        if len(datasets) >= min_datasets:
            # Skip trivial concepts (too many objects = not informative)
            total_objects = sum(len(objs) for objs in datasets.values())
            if total_objects > 10000:
                continue

            bridge = {
                "concept": concept,
                "n_datasets": len(datasets),
                "datasets": {ds: len(objs) for ds, objs in datasets.items()},
                "total_objects": total_objects,
                "sample_objects": {ds: objs[:5] for ds, objs in datasets.items()},
                "specificity": 1.0 / max(total_objects, 1),
            }
            bridges.append(bridge)

    # Sort by: more datasets first, then more specific (fewer total objects)
    bridges.sort(key=lambda b: (-b["n_datasets"], b["total_objects"]))

    # Write bridges
    with open(BRIDGES_FILE, "w", encoding="utf-8") as f:
        for b in bridges[:max_results]:
            f.write(json.dumps(b) + "\n")

    # Stats
    by_n_datasets = defaultdict(int)
    for b in bridges:
        by_n_datasets[b["n_datasets"]] += 1

    print(f"Found {len(bridges)} bridge concepts")
    print(f"  By dataset count: {dict(by_n_datasets)}")

    # Show top bridges
    print(f"\nTop 20 bridges:")
    for b in bridges[:20]:
        ds_str = ", ".join(f"{ds}({n})" for ds, n in sorted(b["datasets"].items()))
        print(f"  {b['concept']:40s} | {b['n_datasets']} datasets | {ds_str}")

    return bridges[:max_results]


if __name__ == "__main__":
    stats = build_index()
    bridges = find_bridges()
    print(f"\nBridges saved to {BRIDGES_FILE}")
