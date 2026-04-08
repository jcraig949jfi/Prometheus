"""
Abstraction Axis — compute "abstraction depth" for every object in the pipeline.
=================================================================================
Foundational objects (axioms, basic definitions) have depth 0.
Objects that build on them have depth 1, 2, ...  Applied / concrete results
sit at the highest depth.  This creates a vertical axis: up = abstract,
down = concrete.

Datasets covered:
  - mathlib  (import graph)
  - MMLKG    (Metamath-like Knowledge Graph theorem references)
  - OEIS     (cross-reference graph, core sequences as roots)

Usage:
    python abstraction_axis.py
"""

import collections
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow importing search_engine from this directory
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[2]                       # F:/Prometheus
sys.path.insert(0, str(SCRIPT_DIR))

from search_engine import (
    MATHLIB_GRAPH, MMLKG_REFS, OEIS_CROSSREFS,
)

CARTOGRAPHY = REPO / "cartography"
OEIS_KEYWORDS_PATH = CARTOGRAPHY / "oeis" / "data" / "oeis_keywords.json"
OUTPUT_PATH = CARTOGRAPHY / "convergence" / "data" / "abstraction_depths.json"


# ===================================================================
# Utility: BFS depth from a set of root nodes
# ===================================================================

def bfs_depths(adj: dict[str, set[str]], roots: set[str]) -> dict[str, int]:
    """BFS from *roots* along adjacency list *adj*.  Returns {node: depth}."""
    depths: dict[str, int] = {}
    queue = collections.deque()
    for r in roots:
        if r in adj or r in set().union(*adj.values()) if adj else False:
            pass  # root might not be a key but we still seed it
        depths[r] = 0
        queue.append(r)
    while queue:
        node = queue.popleft()
        d = depths[node]
        for nbr in adj.get(node, set()):
            if nbr not in depths:
                depths[nbr] = d + 1
                queue.append(nbr)
    return depths


def print_histogram(depths: dict[str, int], dataset: str):
    """Print a compact depth-distribution histogram."""
    if not depths:
        print(f"  [{dataset}] No depth data.\n")
        return
    counter = collections.Counter(depths.values())
    max_depth = max(counter)
    total = sum(counter.values())
    print(f"  [{dataset}] {total:,} objects, max depth {max_depth}")
    for d in range(max_depth + 1):
        cnt = counter.get(d, 0)
        bar = "#" * min(cnt * 60 // max(counter.values()), 60)
        print(f"    depth {d:3d}: {cnt:7,}  {bar}")
    print()


# ===================================================================
# Step 1: mathlib depth
# ===================================================================

def compute_mathlib_depths() -> dict[str, int]:
    """Load mathlib import graph, BFS from root modules (zero in-degree)."""
    if not MATHLIB_GRAPH.exists():
        print("  [mathlib] import_graph.json not found — skipping.")
        return {}

    with open(MATHLIB_GRAPH, "r") as f:
        graph = json.load(f)

    nodes = set()
    for n in graph.get("nodes", []):
        name = n if isinstance(n, str) else n.get("name", "")
        if name:
            nodes.add(name)

    # Build adjacency: source → {targets it imports}
    # An edge [A, B] means A imports B  (A depends on B).
    # For abstraction depth we want to BFS from the *most foundational*
    # (fewest inbound deps) outward along the direction "who uses me".
    # So we build a *reverse* adjacency: B → {A, ...} (B is used by A).
    fwd: dict[str, set[str]] = {}   # A → set of modules A imports
    rev: dict[str, set[str]] = {}   # B → set of modules that import B
    in_degree: dict[str, int] = {n: 0 for n in nodes}

    for edge in graph.get("edges", []):
        if isinstance(edge, dict):
            src = edge.get("source", "")
            tgt = edge.get("target", "")
        elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
            src, tgt = str(edge[0]), str(edge[1])
        else:
            continue
        fwd.setdefault(src, set()).add(tgt)
        rev.setdefault(tgt, set()).add(src)
        in_degree.setdefault(src, 0)
        in_degree.setdefault(tgt, 0)
        in_degree[src] += 0   # src imports tgt → tgt gets an inbound
        in_degree[tgt] += 1

    # Roots = zero in-degree (no one imports them because they are top-level
    # umbrella files) OR known foundational prefixes.
    roots = {n for n, deg in in_degree.items() if deg == 0}
    # Also add well-known foundational modules if present
    for candidate in ["Mathlib.Init", "Mathlib.Tactic.Basic", "Mathlib.Tactic",
                       "Mathlib.Mathport", "Init"]:
        if candidate in nodes:
            roots.add(candidate)

    if not roots:
        # Fallback: pick 20 lowest in-degree nodes
        sorted_nodes = sorted(in_degree.items(), key=lambda x: x[1])
        roots = {n for n, _ in sorted_nodes[:20]}

    print(f"  [mathlib] {len(nodes):,} nodes, {len(roots)} roots")

    # BFS along *forward* edges (A imports B → edge A→B).
    # Roots are umbrella/top-level modules.  An umbrella imports children,
    # so BFS along fwd gives depth = how many layers of import indirection.
    depths = bfs_depths(fwd, roots)

    print_histogram(depths, "mathlib")
    return depths


# ===================================================================
# Step 2: MMLKG depth
# ===================================================================

def compute_mmlkg_depths() -> dict[str, int]:
    """Load MMLKG theorem_references.csv, BFS from foundational articles."""
    if not MMLKG_REFS.exists():
        print("  [MMLKG] theorem_references.csv not found — skipping.")
        return {}

    # Build article-level adjacency: article_A references article_B
    # means A depends on B.  For depth, BFS outward from foundations
    # along the reverse direction: B is used by A → B → A.
    adj: dict[str, set[str]] = {}   # article → set of articles that reference it
    articles: set[str] = set()

    print("  [MMLKG] Loading theorem_references.csv ...")
    with open(MMLKG_REFS, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 4:
                continue
            src_article = parts[0].strip()
            tgt_article = parts[2].strip()
            if src_article and tgt_article and src_article != tgt_article:
                articles.add(src_article)
                articles.add(tgt_article)
                # src references tgt → tgt is more foundational.
                # BFS from foundations outward: tgt → src
                adj.setdefault(tgt_article, set()).add(src_article)

    FOUNDATIONS = {"tarski", "xboole_0", "xboole_1", "subset_1", "ordinal1",
                   "tarski_0", "boole", "enumset1", "zfmisc_1"}
    roots = {a for a in FOUNDATIONS if a in articles}
    if not roots:
        # Fallback: pick articles with highest out-degree in adj (most referenced)
        top = sorted(adj.items(), key=lambda x: -len(x[1]))[:10]
        roots = {a for a, _ in top}

    print(f"  [MMLKG] {len(articles):,} articles, {len(roots)} roots: {sorted(roots)}")

    depths = bfs_depths(adj, roots)
    print_histogram(depths, "MMLKG")
    return depths


# ===================================================================
# Step 3: OEIS depth
# ===================================================================

def compute_oeis_depths() -> dict[str, int]:
    """Load OEIS cross-references, BFS from top-100-in-degree core sequences."""
    if not OEIS_CROSSREFS.exists():
        print("  [OEIS] oeis_crossrefs.jsonl not found — skipping.")
        return {}

    # Load cross-reference graph
    xref_fwd: dict[str, set[str]] = {}   # src → set of targets
    xref_rev: dict[str, set[str]] = {}   # tgt → set of sources that reference it
    print("  [OEIS] Loading cross-references ...")
    count = 0
    with open(OEIS_CROSSREFS, "r", encoding="utf-8") as f:
        for line in f:
            try:
                edge = json.loads(line)
                src, tgt = edge["source"], edge["target"]
                xref_fwd.setdefault(src, set()).add(tgt)
                xref_rev.setdefault(tgt, set()).add(src)
                count += 1
            except (json.JSONDecodeError, KeyError):
                pass
    print(f"  [OEIS] {count:,} edges loaded")

    # Core sequences = top 100 by in-degree
    in_degrees = {seq: len(refs) for seq, refs in xref_rev.items()}
    top_100 = sorted(in_degrees.items(), key=lambda x: -x[1])[:100]
    roots = {seq for seq, _ in top_100}
    if top_100:
        print(f"  [OEIS] Top-5 cores: {[(s, d) for s, d in top_100[:5]]}")

    # BFS from cores outward along forward edges (A references B → A depends
    # on B, so B is more foundational).  But we want depth from cores outward
    # to sequences that reference them, so BFS along reverse direction:
    # core → sequences that reference core.
    # Actually, "core" sequences are the most-referenced = most foundational.
    # A references B means A uses B.  Sequences that USE cores are one step
    # away.  So BFS along xref_rev (who references whom → reverse = who is
    # referenced by whom and then who references *those*).
    # For outward BFS from cores: core is depth 0, anything that references
    # a core (i.e. uses it) is depth 1, etc.
    # xref_rev[B] = set of A's that reference B.  So xref_rev is the right
    # adjacency for "from B, find who depends on B".
    depths = bfs_depths(xref_rev, roots)

    print_histogram(depths, "OEIS")
    return depths


# ===================================================================
# Step 4: Nice vs non-nice analysis + report + save
# ===================================================================

def nice_analysis(oeis_depths: dict[str, int]):
    """Compare average depth for 'nice' vs non-nice OEIS sequences."""
    if not OEIS_KEYWORDS_PATH.exists():
        print("  [OEIS] oeis_keywords.json not found — skipping nice analysis.")
        return
    if not oeis_depths:
        return

    with open(OEIS_KEYWORDS_PATH, "r") as f:
        keywords = json.load(f)

    nice_depths = []
    non_nice_depths = []
    for seq_id, depth in oeis_depths.items():
        kw = keywords.get(seq_id, [])
        if "nice" in kw:
            nice_depths.append(depth)
        else:
            non_nice_depths.append(depth)

    if nice_depths:
        avg_nice = sum(nice_depths) / len(nice_depths)
        print(f"  [OEIS] 'nice' sequences:     n={len(nice_depths):,}, avg depth={avg_nice:.2f}")
    if non_nice_depths:
        avg_other = sum(non_nice_depths) / len(non_nice_depths)
        print(f"  [OEIS] non-nice sequences:    n={len(non_nice_depths):,}, avg depth={avg_other:.2f}")

    # Core analysis
    core_depths = []
    for seq_id, depth in oeis_depths.items():
        kw = keywords.get(seq_id, [])
        if "core" in kw:
            core_depths.append(depth)
    if core_depths:
        avg_core = sum(core_depths) / len(core_depths)
        print(f"  [OEIS] 'core' sequences:     n={len(core_depths):,}, avg depth={avg_core:.2f}")
    print()


def deepest_objects(depths: dict[str, int], dataset: str, n: int = 10):
    """Print the n deepest (most concrete/applied) objects."""
    if not depths:
        return
    ranked = sorted(depths.items(), key=lambda x: -x[1])[:n]
    print(f"  [{dataset}] Top-{n} deepest objects:")
    for obj_id, d in ranked:
        print(f"    depth {d:4d}: {obj_id}")
    print()


def save_results(mathlib_depths, mmlkg_depths, oeis_depths):
    """Save all depth scores to JSON."""
    output = {
        "mathlib": {k: v for k, v in sorted(mathlib_depths.items(), key=lambda x: x[1])},
        "mmlkg": {k: v for k, v in sorted(mmlkg_depths.items(), key=lambda x: x[1])},
        "oeis": {k: v for k, v in sorted(oeis_depths.items(), key=lambda x: x[1])},
        "metadata": {
            "mathlib_count": len(mathlib_depths),
            "mmlkg_count": len(mmlkg_depths),
            "oeis_count": len(oeis_depths),
            "mathlib_max_depth": max(mathlib_depths.values()) if mathlib_depths else 0,
            "mmlkg_max_depth": max(mmlkg_depths.values()) if mmlkg_depths else 0,
            "oeis_max_depth": max(oeis_depths.values()) if oeis_depths else 0,
        },
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=1)
    print(f"  Saved depths to {OUTPUT_PATH}")


# ===================================================================
# Main
# ===================================================================

def main():
    print("=" * 65)
    print("  Abstraction Axis — depth scoring")
    print("=" * 65)

    print("\n--- Step 1: mathlib import graph ---")
    mathlib_depths = compute_mathlib_depths()
    deepest_objects(mathlib_depths, "mathlib")

    print("--- Step 2: MMLKG theorem references ---")
    mmlkg_depths = compute_mmlkg_depths()
    deepest_objects(mmlkg_depths, "MMLKG")

    print("--- Step 3: OEIS cross-references ---")
    oeis_depths = compute_oeis_depths()
    deepest_objects(oeis_depths, "OEIS")

    print("--- Step 4: Analysis & save ---")
    nice_analysis(oeis_depths)
    save_results(mathlib_depths, mmlkg_depths, oeis_depths)

    print("=" * 65)
    print("  Done.")
    print("=" * 65)


if __name__ == "__main__":
    main()
