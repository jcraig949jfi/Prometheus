"""proteus.graph_grammar.v1 -- mutation over CONNECTIVITY, never over positions.

Every operator produces an EDIT LIST of primitive edits and the child is `apply_edits(parent,
edits)`; the operator never touches the manifest any other way. So a lineage record that carries
the edits reconstructs the child exactly (asserted in tests), which is the directive's "a child
must retain enough ancestry metadata to reconstruct exactly what changed".

Operators (name, pre-registered mass, what it does). Subtraction carries non-zero mass (R4) and
the neutrality of node count under no selection is MEASURED by test_graph_grammar.py, not
assumed. A "component" is the set of nodes control-reachable from a chosen root, capped at
K_MAX nodes in BFS order -- a part defined by connectivity only (R7: no theory of what a part is).

    NODE_ADD              .07  append one node of a random kind, unconnected (dormant by construction)
    NODE_REMOVE           .11  remove one node and every edge touching it
    SUBGRAPH_REMOVE       .10  remove a component (k <= K_MAX) and its edges
    NODE_KIND             .08  change one node's kind; edges to ports the new kind lacks are cut
    NODE_PARAM            .10  perturb a CONST immediate (signed delta or bit flip) or flip a node's persist flag
    EDGE_ADD              .10  add one data or control edge into a free port
    EDGE_CUT              .10  cut one edge (nodes persist: disconnect without deleting)
    EDGE_RETARGET         .10  move one edge's source (data) or destination (control) to another node
    SUBGRAPH_COPY         .04  copy a component with its internal edges, appended DORMANT (neutral growth)
    SUBGRAPH_COPY_ATTACH  .04  copy a component and attach its root to a free control out-port of a live node
    SUBGRAPH_MOVE         .06  cut a component root's incoming control edges and re-attach it elsewhere
    CROSSOVER_SUBGRAPH    .04  copy a component FROM THE MATE (self if none), attached with probability 1/2
    CONFIG_PERTURB        .06  step one manifest limit (state_words, tick_budget, out_cap, call_depth_max,
                               persist_state, entry) within published bounds

Mass history (pre-registered BEFORE any world runs this grammar; both measurements kept):
    v1-draft  NODE_ADD .06 / NODE_REMOVE .12: 200 organisms x 100 mutations, no selection, mean
              nodes 12.70 -> 10.09, drift -0.0261 nodes/step (sd .064): satisfies "growth is not
              the default" but is an authored SHRINK current, so it was rebalanced once.
    v1-draft2 NODE_ADD .08 / NODE_REMOVE .10: drift +0.0057 (seed 7) and +0.0194 (seed 8) per
              step -- upward, which R4 forbids as a default; rebalanced to the midpoint.
    v1        NODE_ADD .07 / NODE_REMOVE .11: measured in test_graph_grammar.py on three seeds; the
              test pins |mean drift| <= 0.02 nodes/step (pre-registered band) and fails outside it.
"""
from __future__ import annotations

from proteus.foundry.prng import SplitMix64

from .affordances import BOUNDS, CONTROL_OUT, DATA_IN, N_KINDS, N_PARAMS
from .identity import hash_obj
from .vm import CONST, MASK32, canonicalize, live_nodes

GRAMMAR_VERSION = "proteus.graph_grammar.v1"
K_MAX = 4

OPERATORS = (
    ("NODE_ADD",             0.07, "append one node of a random kind, unconnected (dormant)"),
    ("NODE_REMOVE",          0.11, "remove one node and every edge touching it"),
    ("SUBGRAPH_REMOVE",      0.10, "remove a control-connected component of k <= K_MAX nodes and its edges"),
    ("NODE_KIND",            0.08, "change one node's kind; edges to ports the new kind lacks are cut"),
    ("NODE_PARAM",           0.10, "perturb a CONST immediate (delta in [-8,8] or one bit) or flip persist"),
    ("EDGE_ADD",             0.10, "add one data or control edge into a free port"),
    ("EDGE_CUT",             0.10, "cut one edge; nodes persist"),
    ("EDGE_RETARGET",        0.10, "move one edge's source (data) or destination (control)"),
    ("SUBGRAPH_COPY",        0.04, "copy a component with internal edges, appended dormant"),
    ("SUBGRAPH_COPY_ATTACH", 0.04, "copy a component and attach its root to a free control out-port of a live node"),
    ("SUBGRAPH_MOVE",        0.06, "cut a component root's incoming control edges and re-attach it elsewhere"),
    ("CROSSOVER_SUBGRAPH",   0.04, "copy a component from the mate, attached with probability 1/2"),
    ("CONFIG_PERTURB",       0.06, "step one manifest limit within published bounds"),
)
NAMES = tuple(o[0] for o in OPERATORS)
WEIGHTS = tuple(o[1] for o in OPERATORS)
assert abs(sum(WEIGHTS) - 1.0) < 1e-9
GRAMMAR_HASH = hash_obj({"version": GRAMMAR_VERSION, "operators": OPERATORS, "k_max": K_MAX})


# ------------------------------------------------------------------ primitive edits
def apply_edits(m: dict, edits: list) -> dict:
    """Replay a list of primitive edits on a manifest (pure). The ONLY way a child is built."""
    m = {"schema_version": m["schema_version"], "nodes": [dict(n, params=list(n.get("params", []))) for n in m["nodes"]],
         "data_edges": [list(e) for e in m["data_edges"]], "control_edges": [list(e) for e in m["control_edges"]],
         "entry": m["entry"], "state_words": m["state_words"], "tick_budget": m["tick_budget"],
         "out_cap": m["out_cap"], "call_depth_max": m["call_depth_max"], "persist_state": m["persist_state"]}
    for e in edits:
        (kind, arg), = e.items()
        if kind == "add_nodes":
            m["nodes"].extend(dict(n, params=list(n.get("params", []))) for n in arg)
        elif kind == "remove_nodes":
            rm = set(arg["indices"])
            keep = [i for i in range(len(m["nodes"])) if i not in rm]
            remap = {old: new for new, old in enumerate(keep)}
            m["nodes"] = [m["nodes"][i] for i in keep]
            m["data_edges"] = [[remap[s], remap[d], p] for s, d, p in m["data_edges"] if s in remap and d in remap]
            m["control_edges"] = [[remap[s], p, remap[d]] for s, p, d in m["control_edges"] if s in remap and d in remap]
            m["entry"] = remap[m["entry"]] if m["entry"] in remap else remap[arg["entry_if_removed"]]
        elif kind == "set_kind":
            i, k, params = arg
            m["nodes"][i] = dict(m["nodes"][i], kind=k, params=list(params))
            m["data_edges"] = [e for e in m["data_edges"] if not (e[1] == i and e[2] >= DATA_IN[k])]
            m["control_edges"] = [e for e in m["control_edges"] if not (e[0] == i and e[1] >= CONTROL_OUT[k])]
        elif kind == "set_params":
            i, params = arg
            m["nodes"][i] = dict(m["nodes"][i], params=list(params))
        elif kind == "set_persist":
            i, flag = arg
            m["nodes"][i] = dict(m["nodes"][i], persist=bool(flag))
        elif kind == "add_data_edges":
            for s, d, p in arg:
                m["data_edges"] = [e for e in m["data_edges"] if not (e[1] == d and e[2] == p)] + [[s, d, p]]
        elif kind == "add_control_edges":
            for s, p, d in arg:
                m["control_edges"] = [e for e in m["control_edges"] if not (e[0] == s and e[1] == p)] + [[s, p, d]]
        elif kind == "cut_data_edges":
            cut = {tuple(x) for x in arg}
            m["data_edges"] = [e for e in m["data_edges"] if tuple(e) not in cut]
        elif kind == "cut_control_edges":
            cut = {tuple(x) for x in arg}
            m["control_edges"] = [e for e in m["control_edges"] if tuple(e) not in cut]
        elif kind == "set_config":
            for key, val in arg.items():
                m[key] = val
        else:
            raise ValueError("unknown edit " + kind)
    return canonicalize(m)


# ------------------------------------------------------------------ helpers
def component(m: dict, root: int, k_max: int = K_MAX) -> list:
    succ = {}
    for s, _p, d in m["control_edges"]:
        succ.setdefault(s, []).append(d)
    out, seen, queue = [], set(), [root]
    while queue and len(out) < k_max:
        x = queue.pop(0)
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
        queue.extend(sorted(succ.get(x, ())))
    return out


def _copy_component(m: dict, src: dict, comp: list) -> tuple:
    """Nodes + internal edges of `comp` (indices into src) re-indexed to append after m's nodes.
    Returns (new_nodes, data_edges, control_edges, index_of_root_copy)."""
    base = len(m["nodes"])
    remap = {old: base + i for i, old in enumerate(comp)}
    nodes = [dict(src["nodes"][i], params=list(src["nodes"][i].get("params", []))) for i in comp]
    de = [[remap[s], remap[d], p] for s, d, p in src["data_edges"] if s in remap and d in remap]
    ce = [[remap[s], p, remap[d]] for s, p, d in src["control_edges"] if s in remap and d in remap]
    return nodes, de, ce, remap[comp[0]]


def _free_control_ports(m: dict, nodes: list) -> list:
    used = {(s, p) for s, p, _d in m["control_edges"]}
    return [(s, p) for s in nodes for p in range(CONTROL_OUT[m["nodes"][s]["kind"]]) if (s, p) not in used]


def _free_data_ports(m: dict) -> list:
    used = {(d, p) for _s, d, p in m["data_edges"]}
    return [(d, p) for d in range(len(m["nodes"])) for p in range(DATA_IN[m["nodes"][d]["kind"]]) if (d, p) not in used]


def _rand_node(rng: SplitMix64) -> dict:
    k = rng.randbelow(N_KINDS)
    return {"kind": k, "params": [rng.next_u32() & MASK32 for _ in range(N_PARAMS[k])], "persist": False}


# ------------------------------------------------------------------ operators -> edit lists
def op_node_add(m, rng, mate):
    return [{"add_nodes": [_rand_node(rng)]}]


def op_node_remove(m, rng, mate):
    n = len(m["nodes"])
    if n <= BOUNDS["n_nodes"]["min"]:
        return []
    i = rng.randbelow(n)
    others = [j for j in range(n) if j != i]
    return [{"remove_nodes": {"indices": [i], "entry_if_removed": others[rng.randbelow(len(others))]}}]


def op_subgraph_remove(m, rng, mate):
    n = len(m["nodes"])
    comp = component(m, rng.randbelow(n), rng.randint(1, K_MAX))
    if n - len(comp) < BOUNDS["n_nodes"]["min"]:
        return []
    others = [j for j in range(n) if j not in set(comp)]
    return [{"remove_nodes": {"indices": sorted(comp), "entry_if_removed": others[rng.randbelow(len(others))]}}]


def op_node_kind(m, rng, mate):
    i = rng.randbelow(len(m["nodes"]))
    k = rng.randbelow(N_KINDS)
    return [{"set_kind": [i, k, [rng.next_u32() & MASK32 for _ in range(N_PARAMS[k])]]}]


def op_node_param(m, rng, mate):
    consts = [i for i, nd in enumerate(m["nodes"]) if nd["kind"] == CONST]
    if consts and rng.unit() < 0.7:
        i = consts[rng.randbelow(len(consts))]
        v = m["nodes"][i]["params"][0]
        if rng.unit() < 0.5:
            v = (v + rng.randint(-8, 8)) & MASK32
        else:
            v ^= 1 << rng.randbelow(32)
        return [{"set_params": [i, [v]]}]
    i = rng.randbelow(len(m["nodes"]))
    return [{"set_persist": [i, not m["nodes"][i].get("persist", False)]}]


def op_edge_add(m, rng, mate):
    n = len(m["nodes"])
    fd, fc = _free_data_ports(m), _free_control_ports(m, list(range(n)))
    choices = [("d", x) for x in fd] + [("c", x) for x in fc]
    if not choices:
        return []
    typ, port = choices[rng.randbelow(len(choices))]
    if typ == "d":
        d, p = port
        return [{"add_data_edges": [[rng.randbelow(n), d, p]]}]
    s, p = port
    return [{"add_control_edges": [[s, p, rng.randbelow(n)]]}]


def op_edge_cut(m, rng, mate):
    edges = [("d", e) for e in m["data_edges"]] + [("c", e) for e in m["control_edges"]]
    if not edges:
        return []
    typ, e = edges[rng.randbelow(len(edges))]
    return [{"cut_data_edges": [list(e)]}] if typ == "d" else [{"cut_control_edges": [list(e)]}]


def op_edge_retarget(m, rng, mate):
    n = len(m["nodes"])
    edges = [("d", e) for e in m["data_edges"]] + [("c", e) for e in m["control_edges"]]
    if not edges:
        return []
    typ, e = edges[rng.randbelow(len(edges))]
    if typ == "d":
        s, d, p = e
        return [{"add_data_edges": [[rng.randbelow(n), d, p]]}]          # replaces the edge into (d, p)
    s, p, d = e
    return [{"add_control_edges": [[s, p, rng.randbelow(n)]]}]           # replaces the edge out of (s, p)


def _copy_edits(m, src, comp, attach_from=None):
    if len(m["nodes"]) + len(comp) > BOUNDS["n_nodes"]["max"]:
        return []
    nodes, de, ce, root = _copy_component(m, src, comp)
    edits = [{"add_nodes": nodes}]
    if de:
        edits.append({"add_data_edges": de})
    if ce:
        edits.append({"add_control_edges": ce})
    if attach_from is not None:
        s, p = attach_from
        edits.append({"add_control_edges": [[s, p, root]]})
    return edits


def op_subgraph_copy(m, rng, mate):
    comp = component(m, rng.randbelow(len(m["nodes"])), rng.randint(1, K_MAX))
    return _copy_edits(m, m, comp)


def op_subgraph_copy_attach(m, rng, mate):
    comp = component(m, rng.randbelow(len(m["nodes"])), rng.randint(1, K_MAX))
    live = sorted(live_nodes(m))
    free = _free_control_ports(m, live)
    if not free:
        return _copy_edits(m, m, comp)
    return _copy_edits(m, m, comp, attach_from=free[rng.randbelow(len(free))])


def op_subgraph_move(m, rng, mate):
    n = len(m["nodes"])
    root = rng.randbelow(n)
    incoming = [e for e in m["control_edges"] if e[2] == root]
    edits = []
    if incoming:
        edits.append({"cut_control_edges": [list(e) for e in incoming]})
    free = [(s, p) for s, p in _free_control_ports(m, list(range(n))) if s != root] + \
           [(s, p) for s, p, _d in incoming]
    if free:
        s, p = free[rng.randbelow(len(free))]
        edits.append({"add_control_edges": [[s, p, root]]})
    return edits


def op_crossover_subgraph(m, rng, mate):
    src = mate if mate is not None else m
    comp = component(src, rng.randbelow(len(src["nodes"])), rng.randint(1, K_MAX))
    attach = None
    if rng.unit() < 0.5:
        free = _free_control_ports(m, sorted(live_nodes(m)))
        if free:
            attach = free[rng.randbelow(len(free))]
    return _copy_edits(m, src, comp, attach_from=attach)


def op_config_perturb(m, rng, mate):
    key = rng.choice(["state_words", "tick_budget", "out_cap", "call_depth_max", "persist_state", "entry"])
    if key == "persist_state":
        return [{"set_config": {key: not m[key]}}]
    if key == "entry":
        return [{"set_config": {key: rng.randbelow(len(m["nodes"]))}}]
    b = BOUNDS[key]
    cur = m[key]
    if key in ("state_words", "tick_budget"):
        nxt = cur * 2 if rng.unit() < 0.5 else max(1, cur // 2)
    else:
        nxt = cur + (1 if rng.unit() < 0.5 else -1)
    nxt = min(b["max"], max(b["min"], nxt))
    return [{"set_config": {key: nxt}}] if nxt != cur else []


IMPL = {
    "NODE_ADD": op_node_add, "NODE_REMOVE": op_node_remove, "SUBGRAPH_REMOVE": op_subgraph_remove,
    "NODE_KIND": op_node_kind, "NODE_PARAM": op_node_param, "EDGE_ADD": op_edge_add,
    "EDGE_CUT": op_edge_cut, "EDGE_RETARGET": op_edge_retarget, "SUBGRAPH_COPY": op_subgraph_copy,
    "SUBGRAPH_COPY_ATTACH": op_subgraph_copy_attach, "SUBGRAPH_MOVE": op_subgraph_move,
    "CROSSOVER_SUBGRAPH": op_crossover_subgraph, "CONFIG_PERTURB": op_config_perturb,
}
assert set(IMPL) == set(NAMES)


def mutate(manifest: dict, rng: SplitMix64, mate: dict | None = None, name: str | None = None):
    """One operator draw (or the named operator). Returns (child_manifest, record) where record =
    {operator, edits, pre_hash, post_hash} and child == apply_edits(manifest, edits)."""
    op = name or rng.weighted(NAMES, WEIGHTS)
    edits = IMPL[op](manifest, rng, mate)
    child = apply_edits(manifest, edits)
    return child, {"operator": op, "edits": edits, "pre_hash": hash_obj(manifest), "post_hash": hash_obj(child),
                   "noop": hash_obj(child) == hash_obj(manifest)}
