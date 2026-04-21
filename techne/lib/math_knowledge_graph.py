"""TOOL_MATH_KNOWLEDGE_GRAPH — Extract mathematical knowledge graph from Prometheus research.

Parses research reports, problem catalogs, attack paradigms, and tensor data
into a NetworkX graph with mathematical concepts as nodes and relationships
(proves, uses, blocks, bridges, kills) as edges.

This is the mathematical analog of graphify's code extraction — but for
mathematical ideas instead of function calls.

Interface:
    extract_from_problems(jsonl_path) -> dict  # nodes + edges from problem catalog
    extract_from_research(md_path) -> dict     # nodes + edges from research reports
    extract_from_paradigms(json_path) -> dict  # nodes + edges from attack taxonomy
    extract_from_tensor(json_path) -> dict     # nodes + edges from tensor mapping
    build_math_graph(extractions) -> nx.Graph  # merge all into one graph
    analyze_math_graph(G) -> dict              # god nodes, bridges, gaps
    export_graph(G, out_dir) -> None           # HTML + JSON + report

Forged: 2026-04-21 | Tier: 1 (Python) | Techne first major tool
"""
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional

import networkx as nx

# ─── Node types ─────────────────────────────────────────────────────────────

NODE_TYPES = {
    "problem": "Open mathematical problem",
    "solved": "Solved problem (method known)",
    "concept": "Mathematical concept or structure",
    "paradigm": "Attack paradigm (method class)",
    "tactic": "Specific tactic within a paradigm",
    "tool": "Software tool or library",
    "feature": "Tensor feature (F-id)",
    "projection": "Tensor projection (P-id)",
    "agent": "Prometheus agent role",
    "dataset": "Mathematical dataset",
    "conjecture": "Named conjecture",
    "theorem": "Proven theorem",
    "person": "Mathematician",
}

EDGE_TYPES = {
    "proves": "Theorem proves conjecture",
    "uses": "Method uses tool/concept",
    "blocks": "Barrier blocks progress",
    "bridges": "Connects two domains",
    "kills": "Evidence falsifies claim",
    "enables": "Solving X enables Y",
    "contains": "Category contains member",
    "tests": "Agent tests cell",
    "maps_to": "Problem maps to tensor cell",
    "attacks": "Paradigm attacks problem",
    "requires": "Problem requires prerequisite",
    "extends": "Result extends prior work",
    "contradicts": "Results contradict each other",
    "related": "General relationship",
}


def _make_id(text: str) -> str:
    """Normalize text into a stable node ID."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower().strip())
    return cleaned.strip("_")[:80]


# ─── Problem catalog extractor ──────────────────────────────────────────────

def extract_from_problems(jsonl_path: str) -> dict:
    """Extract nodes and edges from the open problems catalog (questions.jsonl)."""
    nodes = []
    edges = []
    path = Path(jsonl_path)
    if not path.exists():
        return {"nodes": [], "edges": []}

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            p = json.loads(line)
        except json.JSONDecodeError:
            continue

        pid = p.get("id", "")
        title = p.get("title", p.get("name", ""))
        domain = p.get("domain", p.get("subdomain", ""))
        status = p.get("status", "open")

        node_type = "solved" if status == "solved" else "problem"
        node_id = _make_id(pid) if pid else _make_id(title)

        nodes.append({
            "id": node_id,
            "label": f"{pid}: {title[:60]}" if pid else title[:60],
            "type": node_type,
            "domain": domain,
            "source_file": str(path),
            "problem_id": pid,
        })

        # Domain edge
        if domain:
            domain_id = _make_id(f"domain_{domain}")
            nodes.append({
                "id": domain_id,
                "label": domain,
                "type": "concept",
                "source_file": str(path),
            })
            edges.append({
                "source": domain_id,
                "target": node_id,
                "relation": "contains",
                "confidence": "EXTRACTED",
            })

    return {"nodes": _dedup_nodes(nodes), "edges": edges}


# ─── Research report extractor ──────────────────────────────────────────────

def extract_from_research(md_path: str) -> dict:
    """Extract nodes and edges from a deep research batch report."""
    nodes = []
    edges = []
    path = Path(md_path)
    if not path.exists():
        return {"nodes": [], "edges": []}

    text = path.read_text(encoding="utf-8")

    # Extract report entries (## Report #N: Title (Agent))
    report_pattern = re.compile(
        r"##\s+Report\s+#(\d+):\s+(.+?)\s+\((\w+)\)",
        re.IGNORECASE
    )

    for match in report_pattern.finditer(text):
        num, title, agent = match.groups()
        report_id = _make_id(f"report_{num}_{title}")

        nodes.append({
            "id": report_id,
            "label": f"#{num}: {title}",
            "type": "problem",
            "source_file": str(path),
        })

        # Agent edge
        agent_id = _make_id(f"agent_{agent}")
        nodes.append({
            "id": agent_id,
            "label": agent,
            "type": "agent",
            "source_file": str(path),
        })
        edges.append({
            "source": agent_id,
            "target": report_id,
            "relation": "tests",
            "confidence": "EXTRACTED",
        })

    # Extract tensor cells (F### x P###)
    cell_pattern = re.compile(r"\b(F\d{3}[a-z]?)\s*[x×]\s*(P\d{3})\b")
    for match in cell_pattern.finditer(text):
        f_id, p_id = match.groups()
        f_node = _make_id(f"feature_{f_id}")
        p_node = _make_id(f"projection_{p_id}")

        nodes.append({"id": f_node, "label": f_id, "type": "feature", "source_file": str(path)})
        nodes.append({"id": p_node, "label": p_id, "type": "projection", "source_file": str(path)})
        edges.append({
            "source": f_node, "target": p_node,
            "relation": "maps_to", "confidence": "EXTRACTED",
        })

    # Extract named conjectures/theorems
    conjecture_pattern = re.compile(
        r"\b((?:[A-Z][a-z]+[-–]?)+(?:\s+(?:[A-Z][a-z]+[-–]?))*)\s+"
        r"(conjecture|theorem|lemma|hypothesis|inequality|formula|bound)",
        re.IGNORECASE
    )
    for match in conjecture_pattern.finditer(text):
        name, obj_type = match.groups()
        name = name.strip()
        if len(name) < 3 or name.lower() in ("the", "this", "that", "our", "key"):
            continue
        cid = _make_id(f"{obj_type}_{name}")
        label = f"{name} {obj_type}"
        ntype = "theorem" if obj_type.lower() in ("theorem", "lemma") else "conjecture"
        nodes.append({"id": cid, "label": label, "type": ntype, "source_file": str(path)})

    # Extract tool mentions
    tool_pattern = re.compile(
        r"\b(SnapPy|SageMath|Sage|PARI|Magma|GAP|Macaulay2|eclib|"
        r"Lean\s*4|Coq|Isabelle|CaDiCaL|Z3|nauty|polymake|TensorLy|"
        r"FLINT|Arb|mpmath|scipy|numpy|chipfiring|JavaKh)\b",
        re.IGNORECASE
    )
    seen_tools = set()
    for match in tool_pattern.finditer(text):
        tool_name = match.group(1)
        tool_id = _make_id(f"tool_{tool_name}")
        if tool_id not in seen_tools:
            seen_tools.add(tool_id)
            nodes.append({
                "id": tool_id, "label": tool_name,
                "type": "tool", "source_file": str(path),
            })

    # Extract key findings marked with **
    finding_pattern = re.compile(r"\*\*Key finding\*\*:\s*(.+?)(?:\n|$)", re.IGNORECASE)
    for match in finding_pattern.finditer(text):
        finding = match.group(1).strip()
        fid = _make_id(f"finding_{finding[:40]}")
        nodes.append({
            "id": fid, "label": finding[:80],
            "type": "concept", "source_file": str(path),
        })

    return {"nodes": _dedup_nodes(nodes), "edges": edges}


# ─── Attack paradigm extractor ──────────────────────────────────────────────

def extract_from_paradigms(json_path: str) -> dict:
    """Extract nodes and edges from the attack paradigms catalog."""
    nodes = []
    edges = []
    path = Path(json_path)
    if not path.exists():
        return {"nodes": [], "edges": []}

    data = json.loads(path.read_text(encoding="utf-8"))

    for p in data.get("paradigms", []):
        pid = _make_id(f"paradigm_{p['id']}")
        nodes.append({
            "id": pid,
            "label": f"{p['id']}: {p['name']}",
            "type": "paradigm",
            "source_file": str(path),
            "status": p.get("prometheus_status", ""),
        })

        # Tactics
        for tactic in p.get("tactics", []):
            tid = _make_id(f"tactic_{tactic}")
            nodes.append({
                "id": tid, "label": tactic.replace("_", " "),
                "type": "tactic", "source_file": str(path),
            })
            edges.append({
                "source": pid, "target": tid,
                "relation": "contains", "confidence": "EXTRACTED",
            })

        # Tools
        for tool in p.get("tools", []):
            tool_id = _make_id(f"tool_{tool}")
            nodes.append({
                "id": tool_id, "label": tool,
                "type": "tool", "source_file": str(path),
            })
            edges.append({
                "source": pid, "target": tool_id,
                "relation": "uses", "confidence": "EXTRACTED",
            })

        # Solved problems
        for solved in data.get("solved_problems_by_paradigm", {}).get(p["id"], []):
            sid = _make_id(f"solved_{solved}")
            nodes.append({
                "id": sid, "label": solved.replace("_", " "),
                "type": "solved", "source_file": str(path),
            })
            edges.append({
                "source": pid, "target": sid,
                "relation": "attacks", "confidence": "EXTRACTED",
            })

    # Physics imports
    for imp in data.get("physics_imports", []):
        imp_id = _make_id(f"physics_{imp['source']}")
        nodes.append({
            "id": imp_id, "label": imp["source"].replace("_", " "),
            "type": "concept", "source_file": str(path),
        })
        for par in imp.get("paradigms", []):
            pid = _make_id(f"paradigm_{par}")
            edges.append({
                "source": imp_id, "target": pid,
                "relation": "bridges", "confidence": "EXTRACTED",
            })

    # Keystones
    for ks in data.get("top5_keystones", []):
        kid = _make_id(f"keystone_{ks['method']}")
        nodes.append({
            "id": kid, "label": f"Keystone: {ks['method']}",
            "type": "concept", "source_file": str(path),
        })

    return {"nodes": _dedup_nodes(nodes), "edges": edges}


# ─── Tensor mapping extractor ───────────────────────────────────────────────

def extract_from_tensor_mapping(json_path: str) -> dict:
    """Extract nodes and edges from the literature-to-tensor mapping."""
    nodes = []
    edges = []
    path = Path(json_path)
    if not path.exists():
        return {"nodes": [], "edges": []}

    data = json.loads(path.read_text(encoding="utf-8"))

    for m in data.get("mappings", []):
        # Paper node
        paper_id = _make_id(f"paper_{m.get('paper_key', '')}")
        nodes.append({
            "id": paper_id,
            "label": m.get("title", "")[:60],
            "type": "concept",
            "source_file": str(path),
            "year": m.get("year"),
            "citations": m.get("citations", 0),
        })

        # Feature and projection nodes
        f_id = m.get("F", "")
        p_id = m.get("P", "")
        if f_id and f_id != "OUT_OF_TENSOR":
            f_node = _make_id(f"feature_{f_id}")
            p_node = _make_id(f"projection_{p_id}")
            nodes.append({"id": f_node, "label": f_id, "type": "feature", "source_file": str(path)})
            nodes.append({"id": p_node, "label": p_id, "type": "projection", "source_file": str(path)})

            edges.append({
                "source": paper_id, "target": f_node,
                "relation": "maps_to", "confidence": "EXTRACTED",
            })
            edges.append({
                "source": paper_id, "target": p_node,
                "relation": "maps_to", "confidence": "EXTRACTED",
            })

        # Problem edge
        pid = m.get("problem_id", "")
        if pid:
            prob_node = _make_id(pid)
            edges.append({
                "source": paper_id, "target": prob_node,
                "relation": "related", "confidence": "EXTRACTED",
            })

    return {"nodes": _dedup_nodes(nodes), "edges": edges}


# ─── Graph builder ──────────────────────────────────────────────────────────

def build_math_graph(extractions: list) -> nx.Graph:
    """Build a unified NetworkX graph from multiple extraction dicts."""
    G = nx.Graph()

    for ext in extractions:
        for node in ext.get("nodes", []):
            nid = node["id"]
            G.add_node(nid, **{k: v for k, v in node.items() if k != "id"})

        for edge in ext.get("edges", []):
            src, tgt = edge["source"], edge["target"]
            if src in G and tgt in G:
                G.add_edge(src, tgt,
                           relation=edge.get("relation", "related"),
                           confidence=edge.get("confidence", "INFERRED"))

    return G


def cluster_graph(G: nx.Graph) -> dict:
    """Cluster graph into communities using Louvain."""
    if len(G) == 0:
        return {}
    communities = nx.community.louvain_communities(G, seed=42)
    comm_map = {}
    for i, comm in enumerate(communities):
        for node in comm:
            G.nodes[node]["community"] = i
            comm_map.setdefault(i, []).append(node)
    return comm_map


# ─── Analysis ───────────────────────────────────────────────────────────────

def analyze_math_graph(G: nx.Graph) -> dict:
    """Analyze the mathematical knowledge graph."""
    communities = cluster_graph(G)

    # God nodes (most connected)
    degree = dict(G.degree())
    god = sorted(degree.items(), key=lambda x: -x[1])[:20]
    god_nodes = [{
        "id": nid,
        "label": G.nodes[nid].get("label", nid),
        "type": G.nodes[nid].get("type", "unknown"),
        "degree": deg,
        "community": G.nodes[nid].get("community", -1),
    } for nid, deg in god]

    # Bridge nodes (high betweenness centrality)
    if len(G) > 2 and nx.is_connected(G):
        betweenness = nx.betweenness_centrality(G)
    elif len(G) > 2:
        betweenness = nx.betweenness_centrality(G)
    else:
        betweenness = {}

    bridges = sorted(betweenness.items(), key=lambda x: -x[1])[:15]
    bridge_nodes = [{
        "id": nid,
        "label": G.nodes[nid].get("label", nid),
        "type": G.nodes[nid].get("type", "unknown"),
        "betweenness": round(bc, 4),
        "community": G.nodes[nid].get("community", -1),
    } for nid, bc in bridges if bc > 0]

    # Cross-community edges (surprising connections)
    cross_edges = []
    for u, v, data in G.edges(data=True):
        cu = G.nodes[u].get("community", -1)
        cv = G.nodes[v].get("community", -1)
        if cu != cv and cu >= 0 and cv >= 0:
            cross_edges.append({
                "source": u, "source_label": G.nodes[u].get("label", u),
                "target": v, "target_label": G.nodes[v].get("label", v),
                "relation": data.get("relation", "related"),
                "communities": (cu, cv),
            })

    # Isolated nodes (degree 0-1)
    isolated = [nid for nid, deg in degree.items() if deg <= 1]

    # Type distribution
    type_counts = defaultdict(int)
    for _, data in G.nodes(data=True):
        type_counts[data.get("type", "unknown")] += 1

    # Community summaries
    comm_summaries = {}
    for cid, members in communities.items():
        types = defaultdict(int)
        for m in members:
            types[G.nodes[m].get("type", "unknown")] += 1
        labels = [G.nodes[m].get("label", m) for m in members[:5]]
        comm_summaries[cid] = {
            "size": len(members),
            "types": dict(types),
            "sample_labels": labels,
        }

    return {
        "n_nodes": len(G),
        "n_edges": G.number_of_edges(),
        "n_communities": len(communities),
        "god_nodes": god_nodes,
        "bridge_nodes": bridge_nodes,
        "cross_community_edges": cross_edges[:30],
        "n_isolated": len(isolated),
        "type_distribution": dict(type_counts),
        "community_summaries": comm_summaries,
    }


def export_graph(G: nx.Graph, analysis: dict, out_dir: str) -> None:
    """Export graph as JSON and markdown report."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # JSON export
    graph_data = nx.node_link_data(G)
    (out / "math_graph.json").write_text(
        json.dumps(graph_data, indent=2, default=str), encoding="utf-8"
    )

    # Analysis JSON
    (out / "math_analysis.json").write_text(
        json.dumps(analysis, indent=2, default=str), encoding="utf-8"
    )

    # Markdown report
    md = _render_report(G, analysis)
    (out / "MATH_KNOWLEDGE_REPORT.md").write_text(md, encoding="utf-8")

    print(f"Exported: {len(G)} nodes, {G.number_of_edges()} edges, "
          f"{analysis['n_communities']} communities → {out}")


def _render_report(G: nx.Graph, analysis: dict) -> str:
    """Render a markdown report from the analysis."""
    lines = [
        "# Mathematical Knowledge Graph — Prometheus",
        f"## {analysis['n_nodes']} nodes, {analysis['n_edges']} edges, "
        f"{analysis['n_communities']} communities",
        "",
        "---",
        "",
        "## Node Types",
        "",
        "| Type | Count |",
        "|------|-------|",
    ]
    for t, c in sorted(analysis["type_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"| {t} | {c} |")

    lines.extend([
        "",
        "---",
        "",
        "## God Nodes (most connected mathematical concepts)",
        "",
    ])
    for i, g in enumerate(analysis["god_nodes"][:15]):
        lines.append(
            f"{i+1}. **{g['label']}** ({g['type']}) — "
            f"{g['degree']} connections, community {g['community']}"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Bridge Nodes (highest betweenness — connect distant communities)",
        "",
    ])
    for b in analysis["bridge_nodes"][:10]:
        lines.append(
            f"- **{b['label']}** ({b['type']}) — "
            f"betweenness {b['betweenness']}, community {b['community']}"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Surprising Cross-Community Connections",
        "",
    ])
    for e in analysis["cross_community_edges"][:20]:
        lines.append(
            f"- {e['source_label']} --{e['relation']}--> {e['target_label']} "
            f"(communities {e['communities'][0]} ↔ {e['communities'][1]})"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Community Map",
        "",
    ])
    for cid, summary in sorted(analysis["community_summaries"].items()):
        type_str = ", ".join(f"{t}:{c}" for t, c in sorted(summary["types"].items(), key=lambda x: -x[1]))
        sample = ", ".join(summary["sample_labels"][:3])
        lines.append(f"### Community {cid} ({summary['size']} nodes)")
        lines.append(f"- Types: {type_str}")
        lines.append(f"- Sample: {sample}")
        lines.append("")

    lines.extend([
        "---",
        "",
        f"## Gaps: {analysis['n_isolated']} isolated nodes (degree ≤ 1)",
        "",
        "*These concepts have at most one connection — possible missing edges or unmapped territory.*",
        "",
        "---",
        "",
        "*Generated by Techne mathematical knowledge extractor, Prometheus 2026-04-21*",
    ])

    return "\n".join(lines)


# ─── Utility ────────────────────────────────────────────────────────────────

def _dedup_nodes(nodes: list) -> list:
    """Deduplicate nodes by ID, keeping the last (richest) version."""
    seen = {}
    for n in nodes:
        seen[n["id"]] = n
    return list(seen.values())


# ─── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    base = Path(".")
    if len(sys.argv) > 1:
        base = Path(sys.argv[1])

    print("Mathematical Knowledge Graph Builder")
    print("=" * 50)

    extractions = []

    # Problems catalog
    problems_path = base / "aporia" / "mathematics" / "questions.jsonl"
    if problems_path.exists():
        ext = extract_from_problems(str(problems_path))
        print(f"Problems: {len(ext['nodes'])} nodes, {len(ext['edges'])} edges")
        extractions.append(ext)

    # Research reports
    for batch in ["deep_research_batch1.md", "deep_research_batch2.md", "deep_research_batch3.md"]:
        rpath = base / "aporia" / "docs" / batch
        if rpath.exists():
            ext = extract_from_research(str(rpath))
            print(f"{batch}: {len(ext['nodes'])} nodes, {len(ext['edges'])} edges")
            extractions.append(ext)

    # Attack paradigms
    paradigms_path = base / "aporia" / "data" / "attack_paradigms.json"
    if paradigms_path.exists():
        ext = extract_from_paradigms(str(paradigms_path))
        print(f"Paradigms: {len(ext['nodes'])} nodes, {len(ext['edges'])} edges")
        extractions.append(ext)

    # Tensor mapping
    tensor_path = base / "cartography" / "docs" / "literature_to_tensor_mapping.json"
    if tensor_path.exists():
        ext = extract_from_tensor_mapping(str(tensor_path))
        print(f"Tensor mapping: {len(ext['nodes'])} nodes, {len(ext['edges'])} edges")
        extractions.append(ext)

    if not extractions:
        print("No data sources found. Run from Prometheus root directory.")
        sys.exit(1)

    # Build
    G = build_math_graph(extractions)
    print(f"\nMerged graph: {len(G)} nodes, {G.number_of_edges()} edges")

    # Analyze
    analysis = analyze_math_graph(G)

    # Export
    out_dir = str(base / "techne" / "math-graph-out")
    export_graph(G, analysis, out_dir)

    # Print highlights
    print(f"\n{'=' * 50}")
    print(f"GOD NODES (most connected mathematical concepts):")
    for g in analysis["god_nodes"][:10]:
        print(f"  {g['degree']:3d} edges — {g['label']} [{g['type']}]")

    print(f"\nBRIDGE NODES (connect distant communities):")
    for b in analysis["bridge_nodes"][:8]:
        print(f"  bc={b['betweenness']:.4f} — {b['label']} [{b['type']}]")

    print(f"\nSURPRISING CONNECTIONS (cross-community):")
    for e in analysis["cross_community_edges"][:8]:
        print(f"  {e['source_label'][:30]} --{e['relation']}--> {e['target_label'][:30]}")

    print(f"\n{analysis['n_communities']} communities, {analysis['n_isolated']} isolated nodes")
    print(f"\nFull report: {out_dir}/MATH_KNOWLEDGE_REPORT.md")
