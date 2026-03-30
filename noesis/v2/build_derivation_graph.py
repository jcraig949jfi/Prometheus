"""
Build a NetworkX DiGraph encoding all 20 derivation chains from the
structural-primitives mining response.

Author: Aletheia (Structural Mathematician, Project Prometheus)
Date: 2026-03-29
"""

import json
import re
import networkx as nx
from collections import Counter
from pathlib import Path

# ── Canonical transformation ontology ──
TRANSFORM_TYPES = [
    "MAP", "LIFT", "REDUCE", "LIMIT", "LINEARIZE", "VARIATIONAL", "DUALIZE",
    "REPRESENT", "QUANTIZE", "DISCRETIZE", "CONTINUOUSIZE", "STOCHASTICIZE",
    "DETERMINIZE", "LOCALIZE", "GLOBALIZE", "SYMMETRIZE", "BREAK_SYMMETRY",
    "EXTEND", "RESTRICT", "COMPOSE"
]

# ── All 20 chains, transcribed from the council response ──
CHAINS = [
    {
        "chain_id": "C001", "name": "Classical_to_Quantum",
        "steps": [
            {"id": 1, "content": "dq/dt=dH/dp; dp/dt=-dH/dq", "type": "equation"},
            {"id": 2, "content": "[x,p]=ihbar", "type": "equation"},
            {"id": 3, "content": "ihbar*dpsi/dt=H*psi", "type": "equation"},
            {"id": 4, "content": "H*psi=E*psi", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "QUANTIZE", "operation": "Poisson->commutator", "invertible": False},
            {"from": 2, "to": 3, "type": "REPRESENT", "operation": "p->-ihbar*nabla", "invertible": False},
            {"from": 3, "to": 4, "type": "REDUCE", "operation": "separation of variables", "invertible": True},
        ],
        "invariants": ["symplectic_structure"],
    },
    {
        "chain_id": "C002", "name": "Newton_to_Hamiltonian",
        "steps": [
            {"id": 1, "content": "F=ma", "type": "equation"},
            {"id": 2, "content": "Euler-Lagrange", "type": "equation"},
            {"id": 3, "content": "H=pq_dot-L", "type": "equation"},
            {"id": 4, "content": "Hamilton equations", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "VARIATIONAL"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "REPRESENT"},
        ],
        "invariants": ["dynamics"],
    },
    {
        "chain_id": "C003", "name": "Thermo_to_Information",
        "steps": [
            {"id": 1, "content": "S=k*log(W)", "type": "equation"},
            {"id": 2, "content": "S=-k*sum(p*log(p))", "type": "equation"},
            {"id": 3, "content": "H=-sum(p*log(p))", "type": "equation"},
            {"id": 4, "content": "coding theorem", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "STOCHASTICIZE"},
            {"from": 2, "to": 3, "type": "REDUCE"},
            {"from": 3, "to": 4, "type": "MAP"},
        ],
        "invariants": ["entropy_concavity"],
    },
    {
        "chain_id": "C004", "name": "Wave_to_Schrodinger",
        "steps": [
            {"id": 1, "content": "d2psi/dt2=c2*nabla2(psi)", "type": "equation"},
            {"id": 2, "content": "omega2=c2*k2", "type": "equation"},
            {"id": 3, "content": "E=p2/2m", "type": "equation"},
            {"id": 4, "content": "ihbar*dpsi/dt=H*psi", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "REDUCE"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "QUANTIZE"},
        ],
        "invariants": ["wave_structure"],
    },
    {
        "chain_id": "C005", "name": "Heat_to_Brownian",
        "steps": [
            {"id": 1, "content": "du/dt=D*nabla2(u)", "type": "equation"},
            {"id": 2, "content": "Fokker-Planck", "type": "equation"},
            {"id": 3, "content": "Langevin", "type": "equation"},
            {"id": 4, "content": "Brownian motion", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "STOCHASTICIZE"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "LIMIT"},
        ],
        "invariants": ["probability_conservation"],
    },
    {
        "chain_id": "C006", "name": "Maxwell_to_Photon",
        "steps": [
            {"id": 1, "content": "Maxwell equations", "type": "equation"},
            {"id": 2, "content": "wave equation", "type": "equation"},
            {"id": 3, "content": "EM waves", "type": "equation"},
            {"id": 4, "content": "photons", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "MAP"},
            {"from": 2, "to": 3, "type": "REPRESENT"},
            {"from": 3, "to": 4, "type": "QUANTIZE"},
        ],
        "invariants": ["gauge_symmetry"],
    },
    {
        "chain_id": "C007", "name": "Action_to_Field",
        "steps": [
            {"id": 1, "content": "S=int(L dt)", "type": "equation"},
            {"id": 2, "content": "S=int(L d4x)", "type": "equation"},
            {"id": 3, "content": "field Euler-Lagrange", "type": "equation"},
            {"id": 4, "content": "Noether current", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "LIFT"},
            {"from": 2, "to": 3, "type": "VARIATIONAL"},
            {"from": 3, "to": 4, "type": "MAP"},
        ],
        "invariants": ["stationarity"],
    },
    {
        "chain_id": "C008", "name": "Fourier_extension",
        "steps": [
            {"id": 1, "content": "Fourier series", "type": "equation"},
            {"id": 2, "content": "Fourier transform", "type": "equation"},
            {"id": 3, "content": "Parseval", "type": "equation"},
            {"id": 4, "content": "spectral decomposition", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "LIMIT"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "REPRESENT"},
        ],
        "invariants": ["inner_product"],
    },
    {
        "chain_id": "C009", "name": "Probability_to_Measure",
        "steps": [
            {"id": 1, "content": "finite probability", "type": "equation"},
            {"id": 2, "content": "measure space", "type": "equation"},
            {"id": 3, "content": "Lebesgue integral", "type": "equation"},
            {"id": 4, "content": "random variable", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "EXTEND"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "REPRESENT"},
        ],
        "invariants": ["additivity"],
    },
    {
        "chain_id": "C010", "name": "Logic_to_Computation",
        "steps": [
            {"id": 1, "content": "propositional logic", "type": "equation"},
            {"id": 2, "content": "lambda calculus", "type": "equation"},
            {"id": 3, "content": "typed lambda", "type": "equation"},
            {"id": 4, "content": "programs as proofs", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "MAP"},
            {"from": 2, "to": 3, "type": "EXTEND"},
            {"from": 3, "to": 4, "type": "MAP"},
        ],
        "invariants": ["composition"],
    },
    {
        "chain_id": "C011", "name": "Linear_to_Quantum",
        "steps": [
            {"id": 1, "content": "vector space", "type": "equation"},
            {"id": 2, "content": "Hilbert space", "type": "equation"},
            {"id": 3, "content": "operators", "type": "equation"},
            {"id": 4, "content": "expectation", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "EXTEND"},
            {"from": 2, "to": 3, "type": "REPRESENT"},
            {"from": 3, "to": 4, "type": "MAP"},
        ],
        "invariants": ["linearity"],
    },
    {
        "chain_id": "C012", "name": "Graph_to_Diffusion",
        "steps": [
            {"id": 1, "content": "adjacency", "type": "equation"},
            {"id": 2, "content": "Laplacian", "type": "equation"},
            {"id": 3, "content": "heat kernel", "type": "equation"},
            {"id": 4, "content": "diffusion", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "MAP"},
            {"from": 2, "to": 3, "type": "REPRESENT"},
            {"from": 3, "to": 4, "type": "MAP"},
        ],
        "invariants": ["conservation"],
    },
    {
        "chain_id": "C013", "name": "Optimization_to_Variational",
        "steps": [
            {"id": 1, "content": "finite optimization", "type": "equation"},
            {"id": 2, "content": "functional", "type": "equation"},
            {"id": 3, "content": "Euler-Lagrange", "type": "equation"},
            {"id": 4, "content": "constraints", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "LIFT"},
            {"from": 2, "to": 3, "type": "VARIATIONAL"},
            {"from": 3, "to": 4, "type": "EXTEND"},
        ],
        "invariants": ["extremum"],
    },
    {
        "chain_id": "C014", "name": "Group_to_Rep",
        "steps": [
            {"id": 1, "content": "group", "type": "equation"},
            {"id": 2, "content": "representation", "type": "equation"},
            {"id": 3, "content": "irreps", "type": "equation"},
            {"id": 4, "content": "characters", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "REPRESENT"},
            {"from": 2, "to": 3, "type": "REDUCE"},
            {"from": 3, "to": 4, "type": "MAP"},
        ],
        "invariants": ["symmetry"],
    },
    {
        "chain_id": "C015", "name": "Topology_to_Homology",
        "steps": [
            {"id": 1, "content": "topological space", "type": "equation"},
            {"id": 2, "content": "simplicial complex", "type": "equation"},
            {"id": 3, "content": "chain complex", "type": "equation"},
            {"id": 4, "content": "homology", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "DISCRETIZE"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "REDUCE"},
        ],
        "invariants": ["topological_invariance"],
    },
    {
        "chain_id": "C016", "name": "Geometry_to_GR",
        "steps": [
            {"id": 1, "content": "manifold", "type": "equation"},
            {"id": 2, "content": "metric", "type": "equation"},
            {"id": 3, "content": "curvature", "type": "equation"},
            {"id": 4, "content": "Einstein eq", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "EXTEND"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "MAP"},
        ],
        "invariants": ["coordinate_invariance"],
    },
    {
        "chain_id": "C017", "name": "Stats_to_Bayes",
        "steps": [
            {"id": 1, "content": "likelihood", "type": "equation"},
            {"id": 2, "content": "prior", "type": "equation"},
            {"id": 3, "content": "posterior", "type": "equation"},
            {"id": 4, "content": "sequential inference", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "EXTEND"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "COMPOSE"},
        ],
        "invariants": ["probability"],
    },
    {
        "chain_id": "C018", "name": "Field_to_Galois",
        "steps": [
            {"id": 1, "content": "field", "type": "equation"},
            {"id": 2, "content": "extension", "type": "equation"},
            {"id": 3, "content": "automorphism", "type": "equation"},
            {"id": 4, "content": "Galois group", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "EXTEND"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "REPRESENT"},
        ],
        "invariants": ["algebraic_structure"],
    },
    {
        "chain_id": "C019", "name": "PDE_to_Functional",
        "steps": [
            {"id": 1, "content": "PDE", "type": "equation"},
            {"id": 2, "content": "weak form", "type": "equation"},
            {"id": 3, "content": "Sobolev", "type": "equation"},
            {"id": 4, "content": "operator spectrum", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "REDUCE"},
            {"from": 2, "to": 3, "type": "EXTEND"},
            {"from": 3, "to": 4, "type": "REPRESENT"},
        ],
        "invariants": ["linearity"],
    },
    {
        "chain_id": "C020", "name": "Dynamics_to_Chaos",
        "steps": [
            {"id": 1, "content": "deterministic system", "type": "equation"},
            {"id": 2, "content": "iteration", "type": "equation"},
            {"id": 3, "content": "Lyapunov exponent", "type": "equation"},
            {"id": 4, "content": "chaos", "type": "equation"},
        ],
        "transformations": [
            {"from": 1, "to": 2, "type": "COMPOSE"},
            {"from": 2, "to": 3, "type": "MAP"},
            {"from": 3, "to": 4, "type": "LIMIT"},
        ],
        "invariants": ["state_space"],
    },
]


def build_graph(chains):
    """Build a NetworkX DiGraph from all derivation chains."""
    G = nx.DiGraph()

    # Track content -> canonical node_id for cross-chain deduplication
    content_to_node = {}

    for chain in chains:
        cid = chain["chain_id"]
        cname = chain["name"]

        # Map local step ids to global node ids
        local_to_global = {}

        for step in chain["steps"]:
            content = step["content"]
            stype = step.get("type", "equation")

            # Check for cross-chain node sharing (same content = same concept)
            if content in content_to_node:
                node_id = content_to_node[content]
                # Add this chain to the node's chain list
                existing_chains = G.nodes[node_id].get("chain_ids", [])
                if cid not in existing_chains:
                    existing_chains.append(cid)
                    G.nodes[node_id]["chain_ids"] = existing_chains
            else:
                node_id = f"{cid}_s{step['id']}"
                content_to_node[content] = node_id
                G.add_node(
                    node_id,
                    content=content,
                    chain_ids=[cid],
                    chain_name=cname,
                    step_id=step["id"],
                    structure_type=stype,
                )

            local_to_global[step["id"]] = node_id

        # Add edges (transformations)
        for t in chain["transformations"]:
            src = local_to_global[t["from"]]
            dst = local_to_global[t["to"]]
            ttype = t["type"]
            invertible = t.get("invertible", None)
            operation = t.get("operation", "")

            # Determine structure preserved/destroyed from ontology semantics
            structure_preserved = _infer_preserved(ttype)
            structure_destroyed = _infer_destroyed(ttype)

            G.add_edge(
                src, dst,
                transformation_type=ttype,
                invertible=invertible,
                operation=operation,
                chain_id=cid,
                chain_name=cname,
                structure_preserved=structure_preserved,
                structure_destroyed=structure_destroyed,
            )

    return G


def _infer_preserved(ttype):
    """Infer what structure is preserved by a transformation type."""
    preserved = {
        "MAP": "algebraic_relations",
        "LIFT": "local_structure",
        "REDUCE": "essential_structure",
        "LIMIT": "limiting_behavior",
        "LINEARIZE": "first_order_structure",
        "VARIATIONAL": "extremal_structure",
        "DUALIZE": "pairing_structure",
        "REPRESENT": "abstract_structure",
        "QUANTIZE": "algebraic_structure",
        "DISCRETIZE": "combinatorial_structure",
        "CONTINUOUSIZE": "topological_structure",
        "STOCHASTICIZE": "expectation_structure",
        "DETERMINIZE": "mean_behavior",
        "LOCALIZE": "local_properties",
        "GLOBALIZE": "global_properties",
        "SYMMETRIZE": "invariant_structure",
        "BREAK_SYMMETRY": "remaining_symmetries",
        "EXTEND": "original_structure",
        "RESTRICT": "compatible_structure",
        "COMPOSE": "compositional_structure",
    }
    return preserved.get(ttype, "unknown")


def _infer_destroyed(ttype):
    """Infer what structure is destroyed by a transformation type."""
    destroyed = {
        "MAP": "non-functorial_detail",
        "LIFT": "finite_dimensionality",
        "REDUCE": "higher_order_detail",
        "LIMIT": "finite_approximation",
        "LINEARIZE": "nonlinear_terms",
        "VARIATIONAL": "pointwise_detail",
        "DUALIZE": "original_perspective",
        "REPRESENT": "abstraction",
        "QUANTIZE": "commutativity",
        "DISCRETIZE": "continuity",
        "CONTINUOUSIZE": "discrete_structure",
        "STOCHASTICIZE": "determinism",
        "DETERMINIZE": "stochastic_detail",
        "LOCALIZE": "global_coherence",
        "GLOBALIZE": "local_detail",
        "SYMMETRIZE": "asymmetric_features",
        "BREAK_SYMMETRY": "full_symmetry",
        "EXTEND": "simplicity",
        "RESTRICT": "generality",
        "COMPOSE": "independence",
    }
    return destroyed.get(ttype, "unknown")


def analyze_graph(G):
    """Compute and print graph analytics."""
    print("=" * 70)
    print("DERIVATION GRAPH ANALYSIS")
    print("=" * 70)

    # Basic stats
    print(f"\nTotal nodes:  {G.number_of_nodes()}")
    print(f"Total edges:  {G.number_of_edges()}")

    # Transformation type distribution
    print("\n--- Transformation Type Distribution ---")
    type_counts = Counter()
    for u, v, data in G.edges(data=True):
        type_counts[data["transformation_type"]] += 1

    for ttype in TRANSFORM_TYPES:
        count = type_counts.get(ttype, 0)
        if count > 0:
            bar = "#" * count
            print(f"  {ttype:<20s} {count:>2d}  {bar}")

    total_used = sum(type_counts.values())
    types_used = len(type_counts)
    types_unused = len(TRANSFORM_TYPES) - types_used
    print(f"\n  Types used:   {types_used}/{len(TRANSFORM_TYPES)}")
    print(f"  Types unused: {types_unused}  ({', '.join(t for t in TRANSFORM_TYPES if t not in type_counts)})")

    # Cross-chain bridge points
    print("\n--- Cross-Chain Bridge Points ---")
    bridges = []
    for node, data in G.nodes(data=True):
        chain_ids = data.get("chain_ids", [])
        if len(chain_ids) > 1:
            bridges.append((node, data["content"], chain_ids))

    if bridges:
        for node_id, content, chains in bridges:
            print(f"  [{node_id}] '{content}' appears in chains: {', '.join(chains)}")
    else:
        print("  No exact content matches across chains.")
        # Check for near-matches (semantic bridges)
        print("\n  Semantic near-matches (same content appearing in different chains):")
        content_map = {}
        for node, data in G.nodes(data=True):
            c = data["content"].lower().strip()
            content_map.setdefault(c, []).append((node, data.get("chain_ids", [])))
        found_semantic = False
        for content, entries in content_map.items():
            if len(entries) > 1:
                all_chains = set()
                for _, cids in entries:
                    all_chains.update(cids)
                if len(all_chains) > 1:
                    found_semantic = True
                    print(f"    '{content}' -> nodes: {[e[0] for e in entries]}, chains: {all_chains}")
        if not found_semantic:
            print("    None found (chains are largely disjoint in node content)")

    # Connected components (treat as undirected for component analysis)
    print("\n--- Connected Components ---")
    undirected = G.to_undirected()
    components = list(nx.connected_components(undirected))
    print(f"  Number of components: {len(components)}")
    for i, comp in enumerate(sorted(components, key=len, reverse=True)):
        chain_ids_in_comp = set()
        for n in comp:
            chain_ids_in_comp.update(G.nodes[n].get("chain_ids", []))
        print(f"  Component {i+1}: {len(comp)} nodes, chains: {sorted(chain_ids_in_comp)}")

    # Most connected nodes (by degree)
    print("\n--- Most Connected Nodes (Top 10 by degree) ---")
    degree_list = sorted(G.degree(), key=lambda x: x[1], reverse=True)
    for node, deg in degree_list[:10]:
        content = G.nodes[node]["content"]
        chains = G.nodes[node].get("chain_ids", [])
        print(f"  [{node}] deg={deg}  '{content}'  (chains: {', '.join(chains)})")

    # Summary analysis
    print("\n" + "=" * 70)
    print("STRUCTURAL ANALYSIS SUMMARY")
    print("=" * 70)

    top_type = type_counts.most_common(1)[0]
    print(f"""
1. DOMINANT TRANSFORMATION: MAP ({type_counts['MAP']}/60 edges = {type_counts['MAP']*100//60}%)
   MAP is the most common transformation, appearing in nearly every chain.
   This reflects that structure-preserving morphisms are the fundamental
   connective tissue of mathematical derivation.

2. TRANSFORMATION PATTERN: The most common 3-step signatures are:
""")

    # Find chain signatures
    sig_counts = Counter()
    for chain in CHAINS:
        sig = " -> ".join(t["type"] for t in chain["transformations"])
        sig_counts[sig] += 1

    for sig, count in sig_counts.most_common(5):
        chains_with_sig = [c["chain_id"] for c in CHAINS
                          if " -> ".join(t["type"] for t in c["transformations"]) == sig]
        print(f"   {sig}  ({count}x: {', '.join(chains_with_sig)})")

    print(f"""
3. STRUCTURAL OBSERVATIONS:
   - EXTEND appears {type_counts.get('EXTEND', 0)} times: generalization is a primary driver
   - REPRESENT appears {type_counts.get('REPRESENT', 0)} times: making abstract concrete
   - QUANTIZE appears {type_counts.get('QUANTIZE', 0)} times: all in physics chains
   - VARIATIONAL appears {type_counts.get('VARIATIONAL', 0)} times: extremal principles
   - STOCHASTICIZE appears {type_counts.get('STOCHASTICIZE', 0)} times: deterministic->random
   - Only {types_used}/20 ontology types are used across these 20 chains
   - The unused types ({', '.join(t for t in TRANSFORM_TYPES if t not in type_counts)})
     suggest these chains don't yet cover symmetry-breaking, localization,
     or determinization patterns -- areas for future chain discovery.

4. GRAPH TOPOLOGY:
   - Each chain is a linear 4-node path (no branching within chains)
   - Cross-chain connections exist where identical concepts appear
     (e.g., Schrodinger equation in C001 and C004, Euler-Lagrange in C002/C007/C013)
   - The graph is primarily a collection of parallel derivation paths
     with occasional bridge nodes creating a partially connected structure.
""")


def save_graph(G, path):
    """Save graph in GraphML format."""
    # GraphML can't handle list attributes; convert chain_ids to string
    G_export = G.copy()
    for node in G_export.nodes():
        chain_ids = G_export.nodes[node].get("chain_ids", [])
        G_export.nodes[node]["chain_ids"] = ",".join(chain_ids)
        # Convert any None to empty string for GraphML
        for key, val in G_export.nodes[node].items():
            if val is None:
                G_export.nodes[node][key] = ""

    for u, v in G_export.edges():
        for key, val in G_export.edges[u, v].items():
            if val is None:
                G_export.edges[u, v][key] = ""
            elif isinstance(val, bool):
                G_export.edges[u, v][key] = str(val)

    nx.write_graphml(G_export, str(path))
    print(f"\nGraph saved to: {path}")


def main():
    G = build_graph(CHAINS)
    analyze_graph(G)

    output_path = Path("F:/prometheus/noesis/v2/derivation_graph.graphml")
    save_graph(G, output_path)

    print(f"\nNodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print("Done.")


if __name__ == "__main__":
    main()
