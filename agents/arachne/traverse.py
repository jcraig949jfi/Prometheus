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


def bfs_dist(adj, src, dst, banned=None, max_len=8):
    """Shortest hop distance src->dst, optionally skipping one undirected edge.
    Returns max_len+1 if unreachable within the bound (so it's comparable)."""
    if src == dst:
        return 0
    seen = {src}
    q = deque([(src, 0)])
    while q:
        node, d = q.popleft()
        if d >= max_len:
            continue
        for nb, _ in adj.get(node, []):
            if banned and ((node, nb) == banned or (nb, node) == banned):
                continue
            if nb == dst:
                return d + 1
            if nb not in seen:
                seen.add(nb)
                q.append((nb, d + 1))
    return max_len + 1


def holdout(fabric, rng, max_len=8, n_rand=8):
    """Corrected judge: held-out bridge recovery. For each VERIFIED cross-domain
    edge (op=computes), remove it and ask whether the rest of the fabric still
    places its true endpoint CLOSER than random same-landscape nodes. If real
    pairs are reliably closer in the residual graph, the structure carries the
    bridge beyond the explicit edge — that's cross-domain signal, not the edge
    we planted. Path-distance based, so it works on a sparse fabric."""
    adj, edges = load_graph(fabric)
    nodes_by_ls = defaultdict(list)
    for n in fabric.nodes():
        nodes_by_ls[_landscape(n)].append(n)
    gt = [(s, d) for (s, d, op) in edges if op == "computes"]
    rng.shuffle(gt)
    gt = gt[:60]
    closer = ties = total = 0
    sum_real = sum_rand = 0.0
    for (u, v) in gt:
        lv = _landscape(v)
        if len(nodes_by_ls.get(lv, [])) < n_rand + 1:
            continue
        d_real = bfs_dist(adj, u, v, banned=(u, v), max_len=max_len)
        rand_v = rng.sample(nodes_by_ls[lv], n_rand)
        d_rand = [bfs_dist(adj, u, w, banned=(u, v), max_len=max_len) for w in rand_v]
        med = sorted(d_rand)[len(d_rand) // 2]
        total += 1
        sum_real += d_real
        sum_rand += sum(d_rand) / len(d_rand)
        if d_real < med:
            closer += 1
        elif d_real == med:
            ties += 1
    if total == 0:
        return {"verdict": "no ground-truth (computes) edges to test", "tested": 0}
    return {
        "tested_bridges": total,
        "mean_residual_dist_real": round(sum_real / total, 3),
        "mean_residual_dist_random": round(sum_rand / total, 3),
        "real_closer_than_random_frac": round(closer / total, 3),
        "ties_frac": round(ties / total, 3),
        "verdict": ("fabric structure recovers held-out bridges (real closer than random)"
                    if closer / total > 0.5 + 1.0 / (total ** 0.5)
                    else "no recovery signal yet — bridges not predicted by surrounding structure"),
    }


def harvest(fabric, out_path=None):
    """Surface what's interesting without claiming emergence: verified anchors,
    hubs, cross-landscape edge mix, and candidate void targets (sequences that
    cluster with computed ones but have no known computing function)."""
    import json as _json
    from collections import Counter
    anchors, op_counts, deg = [], Counter(), Counter()
    has_computes = set()
    prefix_deg = Counter()
    for src, dst, op in [(e[0], e[1], e[2]) for e in fabric.iter_edges()]:
        op_counts[op] += 1
        deg[src] += 1; deg[dst] += 1
        if op == "computes":
            has_computes.add(dst)
        if op == "shares_prefix":
            prefix_deg[src] += 1; prefix_deg[dst] += 1
    # full records for anchors (need null_p)
    for line in fabric.edges_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = _json.loads(line)
        except Exception:
            continue
        if e.get("op") == "computes" and e.get("null_p", 1) <= 0.15:
            anchors.append((e["src"], e["dst"], round(e["null_p"], 2)))
    anchors = sorted(set(anchors))
    # candidate void targets: heavily prefix-clustered OEIS seqs with NO computing fn
    gaps = [(n, prefix_deg[n]) for n in prefix_deg
            if n.startswith("oeis:") and n not in has_computes and prefix_deg[n] >= 4]
    gaps.sort(key=lambda x: -x[1])
    top_hubs = deg.most_common(15)

    lines = ["# Arachne harvest", "",
             f"## Verified cross-domain anchors (computes, null_p<=0.15): {len(anchors)}"]
    for s, d, np_ in anchors[:40]:
        lines.append(f"- `{s}`  --computes-->  `{d}`  (null_p={np_})")
    lines.append("")
    lines.append(f"## Candidate void targets ({len(gaps)})")
    lines.append("_OEIS sequences tightly prefix-clustered but with NO known computing function "
                 "in the fabric — 'find a function that computes this' leads._")
    for n, dg in gaps[:25]:
        lines.append(f"- `{n}`  (shares_prefix degree {dg})")
    lines.append("")
    lines.append("## Edge mix")
    for op, c in op_counts.most_common():
        lines.append(f"- {op}: {c}")
    lines.append("")
    lines.append("## Top hubs (degree)")
    for n, dg in top_hubs:
        lines.append(f"- `{n}`: {dg}")
    text = "\n".join(lines)
    if out_path:
        Path(out_path).write_text(text, encoding="utf-8")
    return {"anchors": len(anchors), "void_targets": len(gaps),
            "op_counts": dict(op_counts), "out_path": out_path}


def main():
    ap = argparse.ArgumentParser(description="Ask the Arachne fabric")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("usefulness")
    sub.add_parser("holdout")
    sub.add_parser("harvest")
    pa = sub.add_parser("ask"); pa.add_argument("--concept", required=True)
    pb = sub.add_parser("bridge"); pb.add_argument("--src", required=True); pb.add_argument("--dst", required=True)
    args = ap.parse_args()

    fabric = Fabric(FABRIC_DIR)
    rng = random.Random(12345)
    import json
    if args.cmd == "usefulness":
        print(json.dumps(usefulness(fabric, rng), indent=2))
    elif args.cmd == "holdout":
        print(json.dumps(holdout(fabric, rng), indent=2))
    elif args.cmd == "harvest":
        from datetime import datetime, timezone
        out = FABRIC_DIR.parent / "state" / f"harvest_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
        print(json.dumps(harvest(fabric, out_path=str(out)), indent=2))
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
