"""
Extract mathlib4 file-level import graph from source.
No Lean build needed -- just regex on import statements.
"""

import re
import json
import logging
import sys
from pathlib import Path
from collections import defaultdict
from datetime import date

MATHLIB_DIR = Path(__file__).parent.parent / "data" / "mathlib4"
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(REPORT_DIR / f"import_graph_{date.today()}.log",
                                  mode="w", encoding="utf-8")])
log = logging.getLogger("cart.mathlib")

IMPORT_RE = re.compile(r'^import\s+(.+)$', re.MULTILINE)


def extract_imports():
    """Extract import graph from .lean files."""
    lean_files = list(MATHLIB_DIR.rglob("*.lean"))
    log.info(f"Found {len(lean_files)} .lean files")

    edges = []
    nodes = set()
    imports_per_file = {}

    for f in lean_files:
        # Module name from path: Mathlib/Algebra/Group/Basic.lean -> Mathlib.Algebra.Group.Basic
        rel = f.relative_to(MATHLIB_DIR)
        module = str(rel).replace("/", ".").replace("\\", ".").removesuffix(".lean")
        nodes.add(module)

        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        file_imports = []
        for match in IMPORT_RE.finditer(content):
            imported = match.group(1).strip()
            # Handle multi-imports: import Mathlib.Foo\nimport Mathlib.Bar
            for imp in imported.split("\n"):
                imp = imp.strip()
                if imp and not imp.startswith("--"):
                    nodes.add(imp)
                    edges.append((module, imp))
                    file_imports.append(imp)

        imports_per_file[module] = file_imports

    return nodes, edges, imports_per_file


def analyze_graph(nodes, edges, imports_per_file):
    """Basic graph analysis."""
    log.info(f"\n{'='*70}")
    log.info("MATHLIB IMPORT GRAPH ANALYSIS")
    log.info(f"{'='*70}")
    log.info(f"Nodes (modules): {len(nodes)}")
    log.info(f"Edges (imports): {len(edges)}")
    log.info(f"Mean imports per file: {len(edges)/max(len(imports_per_file),1):.1f}")

    # Degree distribution
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    for src, tgt in edges:
        out_degree[src] += 1
        in_degree[tgt] += 1

    # Most imported modules (highest in-degree = most foundational)
    log.info(f"\nTop 20 most-imported modules (foundations):")
    for mod, deg in sorted(in_degree.items(), key=lambda x: -x[1])[:20]:
        log.info(f"  {deg:>5} imports <- {mod}")

    # Highest out-degree (modules that import the most = most complex/integrative)
    log.info(f"\nTop 20 highest-importing modules (integrators):")
    for mod, deg in sorted(out_degree.items(), key=lambda x: -x[1])[:20]:
        log.info(f"  {deg:>5} imports -> {mod}")

    # Namespace distribution
    namespaces = defaultdict(int)
    for node in nodes:
        parts = node.split(".")
        if len(parts) >= 2:
            ns = parts[0] + "." + parts[1]
        else:
            ns = parts[0]
        namespaces[ns] += 1

    log.info(f"\nTop 20 namespaces:")
    for ns, n in sorted(namespaces.items(), key=lambda x: -x[1])[:20]:
        log.info(f"  {ns}: {n} modules")

    # Cross-namespace edges (imports between different top-level namespaces)
    cross_ns = 0
    within_ns = 0
    cross_ns_pairs = defaultdict(int)
    for src, tgt in edges:
        src_ns = src.split(".")[1] if len(src.split(".")) > 1 else src.split(".")[0]
        tgt_ns = tgt.split(".")[1] if len(tgt.split(".")) > 1 else tgt.split(".")[0]
        if src_ns != tgt_ns:
            cross_ns += 1
            cross_ns_pairs[(src_ns, tgt_ns)] += 1
        else:
            within_ns += 1

    log.info(f"\nCross-namespace imports: {cross_ns} ({100*cross_ns/(cross_ns+within_ns):.1f}%)")
    log.info(f"Within-namespace imports: {within_ns}")

    log.info(f"\nTop 20 cross-namespace import pairs:")
    for (s, t), n in sorted(cross_ns_pairs.items(), key=lambda x: -x[1])[:20]:
        log.info(f"  {s} -> {t}: {n}")

    # Connected components (treating as undirected)
    adj = defaultdict(set)
    for src, tgt in edges:
        adj[src].add(tgt)
        adj[tgt].add(src)

    visited = set()
    components = []
    for node in nodes:
        if node in visited:
            continue
        queue = [node]
        comp = set()
        while queue:
            n = queue.pop(0)
            if n in visited:
                continue
            visited.add(n)
            comp.add(n)
            for neighbor in adj.get(n, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
        components.append(comp)

    components.sort(key=len, reverse=True)
    log.info(f"\nConnected components: {len(components)}")
    log.info(f"Largest: {len(components[0])} nodes")
    if len(components) > 1:
        log.info(f"Second: {len(components[1])} nodes")
    log.info(f"Isolated: {sum(1 for c in components if len(c) == 1)}")

    return {
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "n_components": len(components),
        "largest_component": len(components[0]),
        "top_foundations": [(mod, deg) for mod, deg in sorted(in_degree.items(), key=lambda x: -x[1])[:10]],
        "top_integrators": [(mod, deg) for mod, deg in sorted(out_degree.items(), key=lambda x: -x[1])[:10]],
        "cross_namespace_pct": round(100 * cross_ns / max(cross_ns + within_ns, 1), 1),
    }


def main():
    log.info(f"Extracting import graph from {MATHLIB_DIR}")

    if not MATHLIB_DIR.exists():
        log.error(f"mathlib4 not found at {MATHLIB_DIR}. Clone it first.")
        return

    nodes, edges, imports = extract_imports()
    results = analyze_graph(nodes, edges, imports)

    # Save graph as JSON
    graph_path = Path(__file__).parent.parent / "data" / "import_graph.json"
    with open(graph_path, "w") as f:
        json.dump({
            "nodes": list(nodes),
            "edges": edges,
            "metadata": results,
        }, f, indent=2)
    log.info(f"\nGraph saved to {graph_path}")

    log.info(f"\n{'='*70}")
    log.info("EXTRACTION COMPLETE")
    log.info(f"{'='*70}")


if __name__ == "__main__":
    main()
