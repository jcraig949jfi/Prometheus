"""Known-positive ROUTE construction under the search's OWN mutation operator, exact mutator transition probabilities,
and semantics-preserving synonyms.

Route intermediates (Nyx M2: "genomes on an edit path UNDER THE ARM'S OWN OPERATOR", not witness prefixes).
A PRUNE of program P is a program Q such that ONE forward TFS-1 mutation (tfs1.mutate.Mutator, max_fill F) can turn Q
into P and size(Q) < size(P). Two prune moves exist (each the exact inverse of a forward operator):
  reverse-replace : a value-typed subterm u of P with 2 <= size(u) <= F is replaced by a LEAF of the same type in the
                    same scope (literal 0..3, an in-scope lambda variable, xs, or an arity-0 entry). Forward: replace
                    that leaf by u (u is a size <= F term of the mutator's tables).
  reverse-insert  : a node u = op(a_1..a_m) whose argument a_i has u's (value) type and whose OTHER arguments all have
                    size <= F-1 is replaced by a_i. Forward: insert op around a_i with those other arguments.
  (Forward hoist only shrinks, so it never appears on a pruning path.)
The PRUNING LATTICE of witness W = every program reachable from W by prune moves (W excluded from 'intermediates').
The CANONICAL ROUTE = the greedy path from W that always takes the prune giving the smallest program (ties: smallest
canonical text), reversed so that it runs start -> W. Every step is a legal single forward mutation (tested), so the
route is a real path of the mutator; it is canonical, NOT proven shortest (OPEN DECISION O5).

step_probability(parent, child): the EXACT probability that ONE mutation attempt of Mutator.mutate on `parent` returns
`child` (sum over operator x site x random choices that produce it). Mutator.mutate retries a failed/oversize attempt
up to 20 times; p_eff = p_single / (1 - p_none) is reported with p_none estimated by sampling. Tested against
empirical child frequencies.
"""
from collections import Counter
from typing import Dict, List, Optional, Tuple

from tfs1 import core as C
from tfs1.enum import canon_comm
from tfs1.mutate import Mutator, replace_at


def canon_text(t) -> str:
    return C.to_str(canon_comm(t))


def subterm(t, path):
    for i in path:
        if t[0] in ("int", "var", "xs", "hole") or i >= len(t):
            return None
        t = t[i]
    return t


def _leaves(mut: Mutator, ty: str, ctx) -> List[tuple]:
    return [lt for lt, _s in mut.E._leaves(ty, ctx)]


def prunes(mut: Mutator, t, T: str) -> List[Tuple[str, tuple]]:
    """All (move, Q) prune moves of t (deduplicated by Q)."""
    out, seen = [], set()
    F = mut.max_fill
    for path, u, ty, ctx in mut.sites(t, T):
        if ty not in C.VALUE_TYPES or u[0] in ("int", "var", "xs", "hole"):
            continue
        su = C.size(u)
        if 2 <= su <= F:
            for leaf in _leaves(mut, ty, ctx):
                q = replace_at(t, path, leaf)
                if q not in seen:
                    seen.add(q)
                    out.append(("reverse-replace", q))
        if u[0] in ("lam", "app"):
            continue
        ats = C.PRIM_SIGS[u[0]][0] if u[0] in C.PRIM_SIGS else mut.lib.sig(u[0])[0]
        for i, at in enumerate(ats):
            if at != ty:
                continue
            if all(C.size(a) <= max(1, F - 1) for j, a in enumerate(u[1:]) if j != i):
                q = replace_at(t, path, u[1 + i])
                if q not in seen:
                    seen.add(q)
                    out.append(("reverse-insert", q))
    return out


def lattice(mut: Mutator, w, T: str, cap: int = 20000) -> Dict:
    """BFS over prune moves from w. Nodes are keyed by EXACT canonical-printer text (commuted spellings are distinct
    genotypes). Returns {'nodes': {text: {'term', 'depth' (prunes from w), 'size', 'prunes': [(q_text, move)]}},
    'truncated'}."""
    key = C.to_str(w)
    nodes = {key: {"term": w, "depth": 0, "size": C.size(w), "prunes": []}}
    frontier = [key]
    d = 0
    truncated = False
    while frontier:
        d += 1
        nxt = []
        for k in frontier:
            for mv, q in prunes(mut, nodes[k]["term"], T):
                qk = C.to_str(q)
                nodes[k]["prunes"].append((qk, mv))
                if qk not in nodes:
                    if len(nodes) >= cap:
                        truncated = True
                        continue
                    nodes[qk] = {"term": q, "depth": d, "size": C.size(q), "prunes": []}
                    nxt.append(qk)
        frontier = nxt
    return {"nodes": nodes, "truncated": truncated}


def all_paths(lat: Dict, w_text: str, cap: int = 200_000) -> Dict:
    """Every pruning path from w down to a lattice sink, returned as start -> w lists of node texts (the lattice is a
    DAG: every prune strictly shrinks). Stops at `cap` paths (truncated=True)."""
    nodes = lat["nodes"]
    out, truncated = [], False
    stack = [(w_text, [w_text])]
    while stack:
        k, path = stack.pop()
        ps = [q for q, _m in nodes[k]["prunes"] if q in nodes]
        if not ps:
            out.append(path[::-1])
            if len(out) >= cap:
                truncated = True
                break
            continue
        for q in sorted(set(ps), reverse=True):
            stack.append((q, path + [q]))
    return {"paths": out, "truncated": truncated}


_DIGITS_LAST = str.maketrans("0123456789", "~~~~~~~~~~")


def _structural_key(text: str) -> str:
    """Tie-break among equal-size prunes: prefer keeping variables (data flow) over literals, then text."""
    return text.translate(_DIGITS_LAST) + "|" + text


def credit_route(mut: Mutator, w, T: str, score) -> List[Dict]:
    """The most credit-favourable pruning path: from w, always take the prune with the highest score(term) (a tuple,
    e.g. (exact, partial)); ties -> smaller size -> structural key. Returned start -> w. Uses dev feedback only."""
    seq, moves, t = [w], [], w
    while True:
        ps = prunes(mut, t, T)
        if not ps:
            break
        mv, q = min(ps, key=lambda p: (tuple(-x for x in score(p[1])), C.size(p[1]),
                                        _structural_key(C.to_str(p[1]))))
        moves.append({"reverse-replace": "replace", "reverse-insert": "insert"}[mv])
        seq.append(q)
        t = q
    seq.reverse()
    moves.reverse()
    return [{"term": x, "text": C.to_str(x), "size": C.size(x),
             "forward_move_from_prev": (moves[i - 1] if i > 0 else None)} for i, x in enumerate(seq)]


def canonical_route(mut: Mutator, w, T: str) -> List[Dict]:
    """Greedy max-shrink pruning path from w, returned start -> w. forward_move_from_prev names the forward operator
    that turns the previous element into this one."""
    seq = [w]
    moves = []
    t = w
    while True:
        ps = prunes(mut, t, T)
        if not ps:
            break
        mv, q = min(ps, key=lambda p: (C.size(p[1]), _structural_key(C.to_str(p[1]))))
        moves.append({"reverse-replace": "replace", "reverse-insert": "insert"}[mv])
        seq.append(q)
        t = q
    seq.reverse()
    moves.reverse()
    return [{"term": x, "text": C.to_str(x), "size": C.size(x),
             "forward_move_from_prev": (moves[i - 1] if i > 0 else None)} for i, x in enumerate(seq)]


# ================================================================ exact transition probabilities
class StepProb:
    def __init__(self, mut: Mutator):
        self.mut = mut
        self._idx: Dict = {}
        w = list(mut.weights)
        tot = sum(w)
        self.w = dict(zip(mut.OPS, [x / tot for x in w]))

    def _table(self, ty, ctx, n):
        key = (ty, ctx, n)
        c = self._idx.get(key)
        if c is None:
            c = Counter(t for t, _s in self.mut.E.arg_terms(ty, ctx, n))
            self._idx[key] = (c, sum(c.values()))
            c = self._idx[key]
        return c

    def p_random_term(self, ty, ctx, term, max_n) -> float:
        E = self.mut.E
        sizes = [n for n in range(1, max_n + 1) if E._arg_count(ty, ctx, n) > 0]
        n = C.size(term)
        if n not in sizes:
            return 0.0
        cnt, tot = self._table(ty, ctx, n)
        return cnt.get(term, 0) / tot / len(sizes)

    def single(self, parent, child, T: str) -> float:
        mut = self.mut
        sites = mut.sites(parent, T)
        S = len(sites)
        total = 0.0
        for path, u, ty, ctx in sites:
            cu = subterm(child, path)
            if cu is None or replace_at(parent, path, cu) != child:
                continue
            total += self.w["replace"] / S * self.p_random_term(ty, ctx, cu, mut.max_fill)
            if ty not in C.VALUE_TYPES:
                continue
            cands = [(name, ats, i) for name, ats, rt in mut.E.by_ret[ty] for i, at in enumerate(ats) if at == ty]
            if cands and cu[0] not in ("int", "var", "xs", "hole", "lam", "app"):
                for name, ats, i in cands:
                    if cu[0] != name or len(cu) - 1 != len(ats) or cu[1 + i] != u:
                        continue
                    p = 1.0 / len(cands)
                    for j, at in enumerate(ats):
                        if j != i:
                            p *= self.p_random_term(at, ctx, cu[1 + j], max(1, mut.max_fill - 1))
                    total += self.w["insert"] / S * p
            desc = []

            def go(v, vty, top):
                if not top and vty == ty:
                    desc.append(v)
                tag = v[0]
                if tag in ("int", "var", "xs", "hole", "lam", "app"):
                    return
                ats2 = C.PRIM_SIGS[tag][0] if tag in C.PRIM_SIGS else mut.lib.sig(tag)[0]
                for a, at in zip(v[1:], ats2):
                    if at in C.VALUE_TYPES:
                        go(a, at, False)
            go(u, ty, True)
            if desc:
                total += self.w["hoist"] / S * sum(1 for d in desc if d == cu) / len(desc)
        return total

    def p_none(self, parent, T: str, rng, n: int = 2000) -> float:
        """Estimated probability that one mutation attempt yields nothing usable (inapplicable or oversize)."""
        mut = self.mut
        sites = mut.sites(parent, T)
        bad = 0
        for _ in range(n):
            op = rng.choices(mut.OPS, weights=mut.weights)[0]
            site = sites[rng.randrange(len(sites))]
            ch = getattr(mut, "_" + op)(parent, site, rng)
            if ch is None or C.size(ch) > mut.max_size:
                bad += 1
        return bad / n


# ================================================================ synonyms (semantics-preserving rewrites)
def _wraps(u, ty):
    if ty == C.INT:
        return [("add", ("int", 0), u), ("mul", ("int", 1), u), ("sub", u, ("int", 0)), ("div", u, ("int", 1)),
                ("neg", ("neg", u))]
    if ty == C.LIST:
        return [("rev", ("rev", u)), ("drop", ("int", 0), u)]
    if ty == C.BOOL:
        return [("not", ("not", u)), ("and", u, u)]
    return []


def synonyms(mut: Mutator, t, T: str, rng, k: int = 6) -> List[tuple]:
    """Up to k distinct programs semantically identical to t (same value AND same FAIL behaviour on every input under
    the strict contract semantics): identity wrappers at a random value-typed site, or a commutative argument swap.
    (neg (neg u)) is exact because |u| <= 10^18 is already guaranteed."""
    sites = [s for s in mut.sites(t, T) if s[2] in C.VALUE_TYPES]
    out, seen = [], {t}
    tries = 0
    while len(out) < k and tries < 50 * k:
        tries += 1
        path, u, ty, ctx = sites[rng.randrange(len(sites))]
        opts = _wraps(u, ty)
        if u[0] in C.COMMUTATIVE and len(u) == 3 and u[1] != u[2]:
            opts.append((u[0], u[2], u[1]))
        q = replace_at(t, path, opts[rng.randrange(len(opts))])
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out
