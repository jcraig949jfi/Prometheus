"""The emergence test frozen in roles/Arachne/prereg/PREREG_EMERGENCE_v0.md
(commit dbd5345c0). Reads only the frozen specimen. Writes
roles/Arachne/ledgers/emergence_2026-06-04.json (statistics, every null
sample, ablation rows, controls, readings) and a progress log it writes
itself (no shell redirection). Nothing here decides; it prints.

    python roles/Arachne/science/emergence.py controls   # instrument controls only
    python roles/Arachne/science/emergence.py full       # controls, nulls, stats, ablation
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from specimen import Specimen, REPO  # noqa: E402

EQ_OPS = ["shares_prefix", "same_conductor", "same_determinant", "same_order", "same_exponent",
          "isogenous", "same_crossing", "same_n_conjugacy", "same_signature"]
N_SAMPLES = 10
SWAP_MULT = 5
LEDGER = REPO / "roles" / "Arachne" / "ledgers" / "emergence_2026-06-04.json"
LOG = REPO / "roles" / "Arachne" / "ledgers" / "emergence_progress.log"


def log(msg: str) -> None:
    line = "{} {}".format(time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n"); f.flush()


def ls_of(n: str) -> str:
    return n.split(":", 1)[0]


# ---------------------------------------------------------------- graph build
def build_graph(edges) -> nx.Graph:
    G = nx.Graph()
    for e in edges:
        u, v = e["src"], e["dst"]
        if u == v:
            continue
        if G.has_edge(u, v):
            G[u][v]["ops"].add(e["op"]); G[u][v]["crawlers"].add(e["crawler"])
        else:
            G.add_edge(u, v, ops={e["op"]}, crawlers={e["crawler"]})
    return G


def eq_classes(edges) -> dict:
    """op -> {class_id: set(nodes)} from connected components of that op's pairs."""
    out = {}
    for op in EQ_OPS:
        H = nx.Graph([(e["src"], e["dst"]) for e in edges if e["op"] == op and e["src"] != e["dst"]])
        if H.number_of_edges() == 0:
            continue
        out[op] = {i: set(c) for i, c in enumerate(nx.connected_components(H))}
    return out


# ---------------------------------------------------------------- partitions
def louvain(G: nx.Graph, seed: int = 0) -> dict:
    if G.number_of_edges() == 0:
        return {n: i for i, n in enumerate(G.nodes())}
    comms = nx.community.louvain_communities(G, seed=seed)
    return {n: i for i, c in enumerate(comms) for n in c}


def modularity(G: nx.Graph, part: dict) -> float:
    if G.number_of_edges() == 0:
        return 0.0
    groups = defaultdict(set)
    for n, c in part.items():
        groups[c].add(n)
    return float(nx.community.modularity(G, list(groups.values())))


def nmi(a: dict, b: dict) -> float:
    keys = [k for k in a if k in b]
    n = len(keys)
    if n == 0:
        return 0.0
    ca, cb, cab = Counter(), Counter(), Counter()
    for k in keys:
        ca[a[k]] += 1; cb[b[k]] += 1; cab[(a[k], b[k])] += 1
    ha = -sum(c / n * math.log(c / n) for c in ca.values())
    hb = -sum(c / n * math.log(c / n) for c in cb.values())
    mi = sum(c / n * math.log((c / n) / ((ca[i] / n) * (cb[j] / n))) for (i, j), c in cab.items())
    d = math.sqrt(ha * hb)
    return float(mi / d) if d > 0 else 0.0


def ari(a: dict, b: dict) -> float:
    keys = [k for k in a if k in b]
    n = len(keys)
    if n < 2:
        return 1.0
    ca, cb, cab = Counter(), Counter(), Counter()
    for k in keys:
        ca[a[k]] += 1; cb[b[k]] += 1; cab[(a[k], b[k])] += 1
    c2 = lambda x: x * (x - 1) / 2  # noqa: E731
    sum_ab = sum(c2(c) for c in cab.values())
    sum_a = sum(c2(c) for c in ca.values()); sum_b = sum(c2(c) for c in cb.values())
    tot = c2(n)
    expected = sum_a * sum_b / tot
    mx = (sum_a + sum_b) / 2
    return 1.0 if mx == expected else float((sum_ab - expected) / (mx - expected))


# ---------------------------------------------------------------- statistics
def bfs_dist(G, s, t, banned, max_len):
    if s == t:
        return 0
    seen = {s}; frontier = [s]
    for d in range(1, max_len + 1):
        nxt = []
        for u in frontier:
            for w in G.neighbors(u):
                if (u, w) == banned or (w, u) == banned:
                    continue
                if w == t:
                    return d
                if w not in seen:
                    seen.add(w); nxt.append(w)
        frontier = nxt
        if not frontier:
            break
    return max_len + 1


def stat_bridge_redundancy(G: nx.Graph, computes_pairs, rng: random.Random, n_rand=8, max_len=8) -> dict:
    by_ls = defaultdict(list)
    for n in G.nodes():
        by_ls[ls_of(n)].append(n)
    closer = ties = total = 0
    for (u, v) in computes_pairs:
        if u not in G or v not in G:
            continue
        pool = by_ls[ls_of(v)]
        if len(pool) < n_rand + 1:
            continue
        d_real = bfs_dist(G, u, v, (u, v), max_len)
        d_rand = sorted(bfs_dist(G, u, w, (u, v), max_len) for w in rng.sample(pool, n_rand))
        med = d_rand[len(d_rand) // 2]
        total += 1
        if d_real < med:
            closer += 1
        elif d_real == med:
            ties += 1
    return {"tested": total, "closer_frac": round(closer / total, 3) if total else None, "ties_frac": round(ties / total, 3) if total else None}


def stat_cross_concentration(G: nx.Graph, part: dict) -> dict:
    cnt = Counter()
    for u, v in G.edges():
        if ls_of(u) != ls_of(v):
            a, b = sorted((part.get(u, -1), part.get(v, -1)))
            cnt[(a, b)] += 1
    vals = sorted(cnt.values())
    if not vals:
        return {"pairs": 0, "max": 0, "gini": None}
    n = len(vals); s = sum(vals)
    gini = (2 * sum((i + 1) * x for i, x in enumerate(vals)) / (n * s) - (n + 1) / n) if s else 0.0
    return {"community_pairs": n, "max": vals[-1], "gini": round(float(gini), 4)}


def stat_mixed_triangles(G: nx.Graph) -> dict:
    total = mixed = 0
    for u, v in G.edges():
        if u > v:
            continue
        cu = set(G.neighbors(u)); cv = set(G.neighbors(v))
        for w in cu & cv:
            if w < v:            # each triangle once: u < v < w
                continue
            total += 1
            labels = set(G[u][v]["crawlers"]) | set(G[u][w]["crawlers"]) | set(G[v][w]["crawlers"])
            if len(labels) >= 2:
                mixed += 1
    return {"triangles": total, "mixed": mixed, "mixed_frac": round(mixed / total, 4) if total else None}


def stat_hub_share(G: nx.Graph, classes: dict, k: int = 8) -> dict:
    out = {}
    for op, cls in classes.items():
        tot = hub = 0
        for cid, nodes in cls.items():
            sub_edges = [(u, v) for u, v in G.subgraph(nodes).edges() if op in G[u][v]["ops"]]
            if not sub_edges:
                continue
            deg = Counter()
            for u, v in sub_edges:
                deg[u] += 1; deg[v] += 1
            top = set(n for n, _ in deg.most_common(k))
            tot += len(sub_edges); hub += sum(1 for u, v in sub_edges if u in top or v in top)
        out[op] = round(hub / tot, 4) if tot else None
    return out


def dominant_op(G: nx.Graph, landscape: str) -> str:
    c = Counter()
    for u, v, d in G.edges(data=True):
        if ls_of(u) == landscape and ls_of(v) == landscape:
            for op in d["ops"]:
                if op in EQ_OPS:
                    c[op] += 1
    return c.most_common(1)[0][0] if c else None


def all_stats(G: nx.Graph, classes: dict, computes_pairs, seed: int = 0, want=("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9")) -> dict:
    out = {}
    part = louvain(G, seed=seed)
    if "S1" in want:
        out["S1_modularity"] = round(modularity(G, part), 4)
    if "S2" in want:
        lab = {n: ls_of(n) for n in G.nodes()}
        out["S2_nmi_landscape"] = round(nmi(part, lab), 4); out["S2_ari_landscape"] = round(ari(part, lab), 4)
        out["S2_n_communities"] = len(set(part.values()))
    if "S3" in want:
        s3 = {}
        for L in ("oeis", "knots", "groups", "lmfdb"):
            op = dominant_op(G, L)
            if op is None or op not in classes:
                continue
            sub = G.subgraph([n for n in G if ls_of(n) == L]).copy()
            sub.remove_nodes_from([n for n in list(sub) if sub.degree(n) == 0])
            p = louvain(sub, seed=seed)
            lab = {}
            for cid, nodes in classes[op].items():
                for n in nodes:
                    lab[n] = cid
            for n in sub:
                lab.setdefault(n, "single:" + n)
            s3[L] = {"op": op, "n_classes": len(classes[op]), "nmi": round(nmi(p, lab), 4), "ari": round(ari(p, lab), 4)}
        out["S3_within_landscape"] = s3
    if "S4" in want:
        out["S4_transitivity"] = round(float(nx.transitivity(G)), 4)
        out["S4_avg_clustering"] = round(float(nx.average_clustering(G)), 4)
    if "S5" in want:
        comps = sorted((len(c) for c in nx.connected_components(G)), reverse=True)
        out["S5_giant_frac"] = round(comps[0] / G.number_of_nodes(), 4); out["S5_components"] = len(comps)
    if "S6" in want:
        out["S6_bridge_redundancy"] = stat_bridge_redundancy(G, computes_pairs, random.Random(12345))
    if "S7" in want:
        out["S7_cross_concentration"] = stat_cross_concentration(G, part)
    if "S8" in want:
        out["S8_mixed_triangles"] = stat_mixed_triangles(G)
    if "S9" in want:
        out["S9_hub8_share"] = stat_hub_share(G, classes)
    return out


# ---------------------------------------------------------------- nulls
def null_N1(G: nx.Graph, seed: int) -> nx.Graph:
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from(G.edges())
    m = H.number_of_edges()
    nx.double_edge_swap(H, nswap=SWAP_MULT * m, max_tries=200 * m, seed=seed)
    for u, v in H.edges():
        H[u][v]["ops"] = {"swapped"}; H[u][v]["crawlers"] = {"swapped"}
    assert sorted(d for _, d in H.degree()) == sorted(d for _, d in G.degree())
    return H


def _bipartite_swap(pairs, rng: random.Random, nswap: int):
    """degree-preserving swaps inside a list of (a, b) cross pairs with a in
    landscape L1 and b in L2; returns a new list of pairs."""
    pairs = list(pairs); existing = set(pairs)
    n = len(pairs)
    if n < 2:
        return pairs
    done = tries = 0
    while done < nswap and tries < 50 * nswap:
        tries += 1
        i, j = rng.randrange(n), rng.randrange(n)
        if i == j:
            continue
        (a, b), (c, d) = pairs[i], pairs[j]
        if a == c or b == d or (a, d) in existing or (c, b) in existing:
            continue
        existing.discard((a, b)); existing.discard((c, d)); existing.add((a, d)); existing.add((c, b))
        pairs[i], pairs[j] = (a, d), (c, b); done += 1
    return pairs


def null_N2(G: nx.Graph, seed: int) -> nx.Graph:
    rng = random.Random(seed)
    H = nx.Graph(); H.add_nodes_from(G.nodes())
    for L in sorted(set(ls_of(n) for n in G)):
        sub = nx.Graph(); sub.add_nodes_from(n for n in G if ls_of(n) == L)
        sub.add_edges_from((u, v) for u, v in G.edges() if ls_of(u) == L and ls_of(v) == L)
        m = sub.number_of_edges()
        if m >= 2 and sub.number_of_nodes() >= 4:
            nx.double_edge_swap(sub, nswap=SWAP_MULT * m, max_tries=200 * m, seed=rng.randrange(10 ** 9))
        H.add_edges_from(sub.edges())
    cross = defaultdict(list)
    for u, v in G.edges():
        lu, lv = ls_of(u), ls_of(v)
        if lu != lv:
            if lu > lv:
                u, v, lu, lv = v, u, lv, lu
            cross[(lu, lv)].append((u, v))
    for key, pairs in cross.items():
        for a, b in _bipartite_swap(pairs, rng, SWAP_MULT * len(pairs)):
            H.add_edge(a, b)
    for u, v in H.edges():
        H[u][v]["ops"] = {"swapped"}; H[u][v]["crawlers"] = {"swapped"}
    assert sorted(d for _, d in H.degree()) == sorted(d for _, d in G.degree())
    ck_g = Counter(tuple(sorted((ls_of(u), ls_of(v)))) for u, v in G.edges())
    ck_h = Counter(tuple(sorted((ls_of(u), ls_of(v)))) for u, v in H.edges())
    assert ck_g == ck_h
    return H


def _class_edges(edges, classes):
    """op -> class_id -> list of edge dicts (typed edges of that op inside that class)."""
    idx = {op: {n: cid for cid, nodes in cls.items() for n in nodes} for op, cls in classes.items()}
    out = defaultdict(lambda: defaultdict(list))
    for e in edges:
        op = e["op"]
        if op in idx and e["src"] != e["dst"]:
            cid = idx[op].get(e["src"])
            if cid is not None and idx[op].get(e["dst"]) == cid:
                out[op][cid].append(e)
    return out


def _rebuild(edges_kept, drawn):
    return build_graph(edges_kept + drawn)


def null_N3(edges, classes, seed: int) -> nx.Graph:
    rng = random.Random(seed)
    ce = _class_edges(edges, classes)
    eq_ids = set(id(e) for op in ce for cid in ce[op] for e in ce[op][cid])
    kept = [e for e in edges if id(e) not in eq_ids]
    drawn = []
    for op in ce:
        for cid, es in ce[op].items():
            nodes = sorted(classes[op][cid])
            m = len(set((min(e["src"], e["dst"]), max(e["src"], e["dst"])) for e in es))
            allpairs = list(combinations(nodes, 2))
            assert m <= len(allpairs)
            chosen = rng.sample(allpairs, m)
            labels = [e["crawler"] for e in es]; rng.shuffle(labels)
            for (u, v), lab in zip(chosen, labels):
                drawn.append({"src": u, "dst": v, "op": op, "crawler": lab, "null_p": 0.5})
    H = _rebuild(kept, drawn)
    # preservation: class edge counts
    ce2 = _class_edges(drawn, classes)
    for op in ce:
        for cid in ce[op]:
            m0 = len(set((min(e["src"], e["dst"]), max(e["src"], e["dst"])) for e in ce[op][cid]))
            m1 = len(set((min(e["src"], e["dst"]), max(e["src"], e["dst"])) for e in ce2[op][cid]))
            assert m0 == m1, (op, cid, m0, m1)
    return H


def null_N4(G: nx.Graph, edges, classes, seed: int, k: int = 8) -> nx.Graph:
    rng = random.Random(seed)
    ce = _class_edges(edges, classes)
    eq_ids = set(id(e) for op in ce for cid in ce[op] for e in ce[op][cid])
    kept = [e for e in edges if id(e) not in eq_ids]
    drawn = []
    for op in ce:
        for cid, es in ce[op].items():
            nodes = sorted(classes[op][cid])
            pairs0 = set((min(e["src"], e["dst"]), max(e["src"], e["dst"])) for e in es)
            m = len(pairs0)
            deg = Counter()
            for u, v in pairs0:
                deg[u] += 1; deg[v] += 1
            hubs = [n for n, _ in deg.most_common(min(k, len(nodes)))]
            chosen = set(); tries = 0
            while len(chosen) < m and tries < 200 * m + 50:
                tries += 1
                x = rng.choice(nodes); h = rng.choice(hubs)
                if x == h:
                    continue
                chosen.add((min(x, h), max(x, h)))
            if len(chosen) < m:      # star capacity exhausted: fill with uniform class pairs
                rest = [p for p in combinations(nodes, 2) if p not in chosen]
                chosen |= set(rng.sample(rest, m - len(chosen)))
            labels = [e["crawler"] for e in es]; rng.shuffle(labels)
            for (u, v), lab in zip(sorted(chosen), labels):
                drawn.append({"src": u, "dst": v, "op": op, "crawler": lab, "null_p": 0.5})
    H = _rebuild(kept, drawn)
    ce2 = _class_edges(drawn, classes)
    for op in ce:
        for cid in ce[op]:
            m0 = len(set((min(e["src"], e["dst"]), max(e["src"], e["dst"])) for e in ce[op][cid]))
            m1 = len(set((min(e["src"], e["dst"]), max(e["src"], e["dst"])) for e in ce2[op][cid]))
            assert m0 == m1, (op, cid, m0, m1)
    return H


# ---------------------------------------------------------------- ablation
def ablate(G: nx.Graph, full_part: dict, unit: str, rng: random.Random, n_null: int = 10) -> dict:
    owned = [(u, v) for u, v, d in G.edges(data=True) if d["crawlers"] == {unit}]
    if not owned:
        return {"unit": unit, "pairs_removed": 0, "ari": 1.0, "null_aris": [], "load_bearing": False}
    H = G.copy(); H.remove_edges_from(owned)
    H.remove_nodes_from([n for n in list(H) if H.degree(n) == 0])
    a = ari(full_part, louvain(H, seed=0))
    mix = Counter(tuple(sorted((ls_of(u), ls_of(v)))) for u, v in owned)
    by_mix = defaultdict(list)
    for u, v in G.edges():
        by_mix[tuple(sorted((ls_of(u), ls_of(v))))].append((u, v))
    nulls = []
    for _ in range(n_null):
        rem = []
        for key, cnt in mix.items():
            rem += rng.sample(by_mix[key], min(cnt, len(by_mix[key])))
        Hn = G.copy(); Hn.remove_edges_from(rem)
        Hn.remove_nodes_from([n for n in list(Hn) if Hn.degree(n) == 0])
        nulls.append(round(ari(full_part, louvain(Hn, seed=0)), 4))
    return {"unit": unit, "pairs_removed": len(owned), "ari": round(a, 4), "null_aris": nulls,
            "null_min": min(nulls), "load_bearing": a < min(nulls)}


# ---------------------------------------------------------------- controls
def controls() -> dict:
    out = {}
    # partition instrument
    rng = random.Random(1)
    P = nx.planted_partition_graph(2, 100, 0.3, 0.01, seed=1)
    P = nx.relabel_nodes(P, {n: "a:{}".format(n) for n in P})
    blocks = {n: int(n.split(":")[1]) // 100 for n in P}
    part = louvain(P, seed=0)
    out["partition_positive_nmi"] = round(nmi(part, blocks), 4)
    shuffled = list(blocks.values()); rng.shuffle(shuffled)
    out["partition_negative_nmi"] = round(nmi(part, dict(zip(blocks.keys(), shuffled))), 4)
    out["partition_positive_pass"] = out["partition_positive_nmi"] > 0.9
    out["partition_negative_pass"] = out["partition_negative_nmi"] < 0.1
    # cheat: planted clique into a copy of the real G must come back as one community
    S = Specimen(); G = build_graph(S.edges)
    C = G.copy()
    fresh = ["cheat:{}".format(i) for i in range(60)]
    C.add_edges_from(((a, b) for a, b in combinations(fresh, 2)), ops={"cheat"}, crawlers={"cheat"})
    C.add_edge(fresh[0], next(iter(G.nodes())), ops={"cheat"}, crawlers={"cheat"})
    pc = louvain(C, seed=0)
    out["cheat_planted_clique_one_community"] = len(set(pc[n] for n in fresh)) == 1
    out["cheat_planted_clique_pure"] = sum(1 for n in C if pc[n] == pc[fresh[0]]) - 60 <= 1
    # ablation instrument
    full = louvain(G, seed=0)
    neg = ablate(G, full, "no-such-crawler", random.Random(0), n_null=2)
    out["ablation_negative_ari_1"] = neg["ari"] == 1.0
    pos = ablate(C, louvain(C, seed=0), "cheat", random.Random(0), n_null=3)
    out["ablation_positive_reduces_ari"] = pos["ari"] < 1.0
    # null preservation (asserted inside the generators on a small sample)
    classes = eq_classes(S.edges)
    null_N1(G, 0); null_N2(G, 0); null_N3(S.edges, classes, 0); null_N4(G, S.edges, classes, 0)
    out["null_preservation_asserts_pass"] = True
    out["all_pass"] = all(v for k, v in out.items() if k.endswith("_pass") or k.startswith("cheat") or k.startswith("ablation"))
    return out


# ---------------------------------------------------------------- readings
def surprising(obs, samples):
    vals = [s for s in samples if s is not None]
    if obs is None or not vals:
        return None
    lo, hi = min(vals), max(vals)
    pct = sum(1 for s in vals if s <= obs) / len(vals)
    return {"observed": obs, "null_min": lo, "null_max": hi, "null_mean": round(sum(vals) / len(vals), 4),
            "percentile": round(pct, 2), "surprising": obs < lo or obs > hi,
            "direction": "above" if obs > hi else ("below" if obs < lo else "inside")}


def flatten(st: dict) -> dict:
    f = {}
    for k, v in st.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, dict):
                    for k3, v3 in vv.items():
                        if isinstance(v3, (int, float)):
                            f["{}.{}.{}".format(k, kk, k3)] = v3
                elif isinstance(vv, (int, float)):
                    f["{}.{}".format(k, kk)] = vv
        elif isinstance(v, (int, float)):
            f[k] = v
    return f


def run_full() -> dict:
    LOG.write_text("", encoding="utf-8")
    log("controls")
    ctl = controls()
    log("controls: " + json.dumps(ctl))
    if not ctl["all_pass"]:
        return {"controls": ctl, "aborted": "controls failed; statistics not read"}
    S = Specimen(); G = build_graph(S.edges); classes = eq_classes(S.edges)
    computes = [(e["src"], e["dst"]) for e in S.edges if e["op"] == "computes"]
    log("observed statistics")
    obs = all_stats(G, classes, computes)
    log("observed: " + json.dumps(obs))
    nulls = {"N1": [], "N2": [], "N3": [], "N4": []}
    want = {"N1": ("S1", "S2", "S4", "S5"), "N2": ("S1", "S2", "S4", "S5", "S6", "S7"),
            "N3": ("S1", "S2", "S3", "S4", "S5", "S6", "S8", "S9"), "N4": ("S1", "S2", "S3", "S4", "S5", "S8", "S9")}
    for i in range(N_SAMPLES):
        for name in ("N1", "N2", "N3", "N4"):
            t0 = time.time()
            if name == "N1":
                H = null_N1(G, 100 + i)
            elif name == "N2":
                H = null_N2(G, 200 + i)
            elif name == "N3":
                H = null_N3(S.edges, classes, 300 + i)
            else:
                H = null_N4(G, S.edges, classes, 400 + i)
            st = all_stats(H, classes, computes, want=want[name])
            nulls[name].append(st)
            log("{} sample {} in {:.1f}s: {}".format(name, i, time.time() - t0, json.dumps(flatten(st))))
    fo = flatten(obs)
    comparisons = {}
    for name, samples in nulls.items():
        fl = [flatten(s) for s in samples]
        comparisons[name] = {k: surprising(fo.get(k), [s.get(k) for s in fl]) for k in fl[0].keys() if k in fo}
    # ablation
    log("ablation")
    full = louvain(G, seed=0)
    counts = Counter(e["crawler"] for e in S.edges)
    units = sorted([c for c, n in counts.items() if n >= 50 and c not in ("rosetta", "operational")]) + ["rosetta", "operational"]
    rng = random.Random(7)
    abl = []
    for j, u in enumerate(units):
        r = ablate(G, full, u, rng, n_null=10)
        abl.append(r)
        log("ablate {} {}/{}: removed={} ari={} null_min={} load_bearing={}".format(u, j + 1, len(units), r["pairs_removed"], r["ari"], r.get("null_min"), r["load_bearing"]))
    load_bearing = [r["unit"] for r in abl if r["load_bearing"]]
    # readings
    s2 = obs["S2_nmi_landscape"]; s3 = obs["S3_within_landscape"]
    s3_low = [L for L, v in s3.items() if v["nmi"] < 0.5]
    reading_a = "TABLE_OF_CONTENTS" if (s2 >= 0.5 and not s3_low) else "CROSS_CUTTING"
    reading_b = "STABLE" if not load_bearing else "NOT_STABLE"
    keys_c = [k for k in fo if k.split(".")[0].split("_")[0] in ("S1", "S3", "S4", "S6", "S7", "S8")]
    surp_n3 = [k for k in keys_c if comparisons["N3"].get(k) and comparisons["N3"][k]["surprising"]]
    surp_n4 = [k for k in keys_c if comparisons["N4"].get(k) and comparisons["N4"][k]["surprising"]]
    if not surp_n3:
        reading_c = "NOTHING_BEYOND_E0"
    elif not surp_n4:
        reading_c = "NOTHING_BEYOND_E1"
    else:
        reading_c = "CANDIDATE_STRUCTURE"
    emergence = (reading_a == "CROSS_CUTTING" and reading_b == "STABLE" and reading_c == "CANDIDATE_STRUCTURE")
    out = {
        "prereg": "roles/Arachne/prereg/PREREG_EMERGENCE_v0.md @ dbd5345c0",
        "specimen_hashes": S.hashes,
        "graph": {"nodes": G.number_of_nodes(), "pairs": G.number_of_edges(), "typed_edges": len(S.edges)},
        "controls": ctl,
        "observed": obs,
        "null_samples": nulls,
        "comparisons": comparisons,
        "ablation": {"eligible_units": len(units), "rows": abl, "load_bearing": load_bearing},
        "readings": {"a_partition": reading_a, "a_detail": {"S2_nmi": s2, "S3_low": s3_low},
                     "b_ablation": reading_b, "b_detail": {"load_bearing": load_bearing},
                     "c_nulls": reading_c, "c_detail": {"surprising_under_N3": surp_n3, "surprising_under_N4": surp_n4},
                     "EMERGENCE_EARNED": emergence},
    }
    LEDGER.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    log("readings: " + json.dumps(out["readings"]))
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "controls"
    if mode == "controls":
        print(json.dumps(controls(), indent=1))
    else:
        run_full()
