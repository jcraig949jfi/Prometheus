"""Ask the fabric a question by walking it — and judge usefulness against a null.

A static fabric is inert; a genius architecture and a hairball look identical
until something traverses them to answer a question. This module is that
traversal, and its `usefulness` command is the test-first JUDGE: the fabric is
useful only if traversing it answers a cross-domain question better than a null
fabric with the same shape would.

CLI:
  python -m agents.arachne.traverse usefulness
  python -m agents.arachne.traverse ask --concept totient
  python -m agents.arachne.traverse bridge --src "algolib:gcd" --dst "mathlib:Nat.gcd"
"""
from __future__ import annotations

import argparse
import random
import sys
from collections import deque, defaultdict
from pathlib import Path

_THIS = Path(__file__).resolve()
REPO = _THIS.parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from agents.arachne.fabric import Fabric

FABRIC_DIR = _THIS.parent / "fabric"


def _landscape(node: str) -> str:
    return node.split(":", 1)[0]


def load_graph(fabric: Fabric):
    """Undirected adjacency node -> list[(neighbor, op)]; plus edge list."""
    adj = defaultdict(list)
    edges = []
    for src, dst, op in fabric.iter_edges():
        adj[src].append((dst, op))
        adj[dst].append((src, op))
        edges.append((src, dst, op))
    return adj, edges


def bfs_path(adj, src, dst, max_len=8):
    if src not in adj or dst not in adj:
        return None
    seen = {src}
    q = deque([(src, [(src, None)])])
    while q:
        node, path = q.popleft()
        if node == dst:
            return path
        if len(path) > max_len:
            continue
        for nb, op in adj[node]:
            if nb not in seen:
                seen.add(nb)
                q.append((nb, path + [(nb, op)]))
    return None


def reachable_fraction(adj, pairs, max_len=6):
    hit = 0
    for u, v in pairs:
        if bfs_path(adj, u, v, max_len=max_len) is not None:
            hit += 1
    return hit / max(1, len(pairs))


def _sample_cross_pairs(nodes_by_ls, rng, n=120):
    ls = [k for k, v in nodes_by_ls.items() if v and k != "rosetta"]
    pairs = []
    if len(ls) < 2:
        return pairs
    for _ in range(n):
        a, b = rng.sample(ls, 2)
        pairs.append((rng.choice(nodes_by_ls[a]), rng.choice(nodes_by_ls[b])))
    return pairs


def usefulness(fabric: Fabric, rng, max_len=6, n_pairs=120):
    adj, edges = load_graph(fabric)
    nodes_by_ls = defaultdict(list)
    for n in fabric.nodes():
        nodes_by_ls[_landscape(n)].append(n)
    cross = [(s, d, op) for (s, d, op) in edges if _landscape(s) != _landscape(d)]
    intra = len(edges) - len(cross)

    pairs = _sample_cross_pairs(nodes_by_ls, rng, n=n_pairs)
    reach_real = reachable_fraction(adj, pairs, max_len=max_len)

    # NULL: keep intra-landscape structure, but rewire each cross edge to random
    # endpoints within the SAME landscape pair. Tests whether the concept-targeted
    # join lands on structurally integrating nodes, vs any cross link would do.
    null_adj = defaultdict(list)
    for (s, d, op) in edges:
        if _landscape(s) == _landscape(d):
            null_adj[s].append((d, op)); null_adj[d].append((s, op))
    for (s, d, op) in cross:
        la, lb = _landscape(s), _landscape(d)
        if nodes_by_ls[la] and nodes_by_ls[lb]:
            ns, nd = rng.choice(nodes_by_ls[la]), rng.choice(nodes_by_ls[lb])
            null_adj[ns].append((nd, op)); null_adj[nd].append((ns, op))
    reach_null = reachable_fraction(null_adj, pairs, max_len=max_len)

    return {
        "nodes": len(fabric.nodes()), "edges": len(edges),
        "intra_landscape_edges": intra, "cross_landscape_edges": len(cross),
        "nodes_by_landscape": {k: len(v) for k, v in nodes_by_ls.items()},
        "cross_pairs_sampled": len(pairs),
        "reach_real": round(reach_real, 3), "reach_null": round(reach_null, 3),
        "lift": round(reach_real - reach_null, 3),
        "verdict": ("cross-domain traversal beats null" if reach_real > reach_null + 0.02
                    else "no lift over null — concept join not yet adding targeted value"),
    }


def concept_view(fabric: Fabric, token: str, limit=25):
    """Ask: show me <concept> across landscapes + its 1-hop neighborhood."""
    token = token.lower()
    adj, _ = load_graph(fabric)
    seeds = [n for n in fabric.nodes() if token in n.lower()]
    out = {"token": token, "seed_nodes": len(seeds), "by_landscape": defaultdict(list),
           "cross_links": []}
    for s in seeds[:limit]:
        out["by_landscape"][_landscape(s)].append(s)
        for nb, op in adj.get(s, []):
            if _landscape(nb) != _landscape(s):
                out["cross_links"].append((s, op, nb))
    out["by_landscape"] = dict(out["by_landscape"])
    out["cross_links"] = out["cross_links"][:limit]
    return out


def main():
    ap = argparse.ArgumentParser(description="Ask the Arachne fabric")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("usefulness")
    pa = sub.add_parser("ask"); pa.add_argument("--concept", required=True)
    pb = sub.add_parser("bridge"); pb.add_argument("--src", required=True); pb.add_argument("--dst", required=True)
    args = ap.parse_args()

    fabric = Fabric(FABRIC_DIR)
    rng = random.Random(12345)
    import json
    if args.cmd == "usefulness":
        print(json.dumps(usefulness(fabric, rng), indent=2))
    elif args.cmd == "ask":
        print(json.dumps(concept_view(fabric, args.concept), indent=2, default=list))
    elif args.cmd == "bridge":
        adj, _ = load_graph(fabric)
        path = bfs_path(adj, args.src, args.dst)
        if path is None:
            print(f"no path within bound between {args.src} and {args.dst}")
        else:
            print(" -> ".join(f"[{op}] {n}" if op else n for n, op in path))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
