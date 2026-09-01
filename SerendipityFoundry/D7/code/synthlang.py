"""
Operations over the generic synthesis grammar: sampling, mutation, crossover.

Both Z0 (history-free) and Z1 (history-conditioned) use these SAME operators.
The only thing that differs between arms is the proposal weighting (`node_w`,
`art_w`) fed in.  There is no target-specific or barrier-specific structure here.
"""

from __future__ import annotations
from substrate import z_size, Grammar

NODE_TYPES = ["quote", "seq", "rep", "ifz", "nop"]


def _pick(rng, options, weights):
    w = [max(1e-9, weights.get(o, 1.0)) for o in options]
    tot = sum(w)
    x = rng.random() * tot
    acc = 0.0
    for o, wi in zip(options, w):
        acc += wi
        if x <= acc:
            return o
    return options[-1]


def random_program(rng, ids, g: Grammar, node_w=None, art_w=None, depth_budget=None):
    """Sample a random well-typed AST within the grammar's node ceiling."""
    node_w = node_w or {}
    art_w = art_w or {}
    budget = [g.max_nodes]
    if depth_budget is None:
        depth_budget = 6

    def leaf():
        budget[0] -= 1
        if not ids or _pick(rng, ["quote", "nop"],
                            {"quote": node_w.get("quote", 3.0),
                             "nop": node_w.get("nop", 0.4)}) == "nop":
            return ("nop",)
        aid = _pick(rng, ids, art_w)
        return ("quote", aid)

    def build(d):
        # choose leaf vs internal based on remaining budget & depth
        opts = ["quote", "nop"]
        if budget[0] > 2 and d < depth_budget:
            opts = ["quote", "nop", "seq"]
            if g.allow_rep:
                opts.append("rep")
            if g.allow_ifz:
                opts.append("ifz")
        t = _pick(rng, opts, node_w)
        if t in ("quote", "nop"):
            return leaf()
        budget[0] -= 1
        if t == "seq":
            a = build(d + 1)
            b = build(d + 1)
            return ("seq", a, b)
        if t == "rep":
            n = rng.randint(2, g.rep_max)
            return ("rep", n, build(d + 1))
        if t == "ifz":
            coord = rng.randint(0, g.ncoord - 1)  # machine coord index
            return ("ifz", coord, build(d + 1))
        return leaf()

    ast = build(0)
    return ast


def all_quoted(ast):
    t = ast[0]
    if t == "quote":
        return [ast[1]]
    if t == "nop":
        return []
    if t == "seq":
        return all_quoted(ast[1]) + all_quoted(ast[2])
    if t in ("rep", "ifz"):
        return all_quoted(ast[2])
    return []


def _nodes(ast, acc):
    acc.append(ast)
    t = ast[0]
    if t == "seq":
        _nodes(ast[1], acc)
        _nodes(ast[2], acc)
    elif t in ("rep", "ifz"):
        _nodes(ast[2], acc)
    return acc


def mutate(rng, ast, ids, g: Grammar, node_w=None, art_w=None):
    """Point mutation: regrow a random subtree or tweak a literal."""
    node_w = node_w or {}
    art_w = art_w or {}
    nodes = _nodes(ast, [])
    idx = rng.randrange(len(nodes))
    target = nodes[idx]

    def rebuild(node):
        if node is target:
            kind = rng.random()
            if node[0] == "rep" and kind < 0.4:
                return ("rep", rng.randint(2, g.rep_max), node[2])
            if node[0] == "ifz" and kind < 0.4:
                return ("ifz", (node[1] + 1) % g.ncoord, node[2])
            if node[0] == "quote" and kind < 0.5 and ids:
                return ("quote", _pick(rng, ids, art_w))
            # otherwise regrow a fresh small subtree
            sub = random_program(rng, ids, Grammar(rep_max=g.rep_max,
                                                   max_nodes=max(3, g.max_nodes // 2),
                                                   allow_ifz=g.allow_ifz,
                                                   allow_rep=g.allow_rep,
                                                   ncoord=g.ncoord),
                                  node_w=node_w, art_w=art_w)
            return sub
        t = node[0]
        if t == "seq":
            return ("seq", rebuild(node[1]), rebuild(node[2]))
        if t in ("rep", "ifz"):
            return (t, node[1], rebuild(node[2]))
        return node

    m = rebuild(ast)
    if z_size(m) > g.max_nodes:
        return ast
    return m


def crossover(rng, a, b, g: Grammar):
    """Swap a random subtree of b into a random position of a."""
    a_nodes = _nodes(a, [])
    b_nodes = _nodes(b, [])
    donor = b_nodes[rng.randrange(len(b_nodes))]
    tgt = a_nodes[rng.randrange(len(a_nodes))]

    def rebuild(node):
        if node is tgt:
            return donor
        t = node[0]
        if t == "seq":
            return ("seq", rebuild(node[1]), rebuild(node[2]))
        if t in ("rep", "ifz"):
            return (t, node[1], rebuild(node[2]))
        return node

    c = rebuild(a)
    if z_size(c) > g.max_nodes:
        return a
    return c
