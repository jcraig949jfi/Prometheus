"""Frozen generic mutation process -- one per basis, no failure history.

Names are deliberately syntactic.  Nothing here knows about append/wrap/route/
memory/representation or any other semantics-of-change vocabulary; the offline
auditor in classifiers/ recovers those categories retrospectively.

Sequence bases (S2,S3,S4): validity-blind local edits on the token string.
Tree basis (S1): type-directed edits, so well-typedness is preserved by
construction.  That asymmetry is a property of the physics under test, not a
correction applied to one basis.
"""
import random

from substrates.common import PROG_MAX
from substrates import s1_tpc

SEQ_EDITS = ["E-SUBST", "E-INSERT", "E-DELETE", "E-TRANSPOSE", "E-DUPBLOCK", "E-SPLICE"]
TREE_EDITS = ["E-REPLACE", "E-PERTURB", "E-SWAP", "E-GRAFT", "E-PRUNE"]
DONOR_RNG = 555
DONOR_N = 32


def make_donors(sub, rng=None):
    r = random.Random(DONOR_RNG)
    return [sub.random_program(r, r.randrange(4, 16)) for _ in range(DONOR_N)]


# ---------------- sequence bases ----------------
def _seq_atomic(sub, prog, rng, donors):
    kind = rng.choice(SEQ_EDITS)
    n = len(prog)
    if kind == "E-SUBST":
        i = rng.randrange(n)
        t = sub.random_tokens(rng, 1)[0]
        return prog[:i] + (t,) + prog[i + 1:], kind
    if kind == "E-INSERT":
        i = rng.randrange(n + 1)
        t = sub.random_tokens(rng, 1)[0]
        return prog[:i] + (t,) + prog[i:], kind
    if kind == "E-DELETE":
        if n <= 1:
            return prog, kind
        i = rng.randrange(n)
        return prog[:i] + prog[i + 1:], kind
    if kind == "E-TRANSPOSE":
        if n < 2:
            return prog, kind
        i, j = rng.randrange(n), rng.randrange(n)
        if i == j:
            return prog, kind
        l = list(prog)
        l[i], l[j] = l[j], l[i]
        return tuple(l), kind
    if kind == "E-DUPBLOCK":
        i = rng.randrange(n)
        j = min(n, i + 1 + rng.randrange(4))
        blk = prog[i:j]
        k = rng.randrange(n + 1)
        return prog[:k] + blk + prog[k:], kind
    # E-SPLICE
    d = donors[rng.randrange(len(donors))]
    if not d:
        return prog, kind
    i = rng.randrange(n)
    j = min(n, i + 1 + rng.randrange(5))
    a = rng.randrange(len(d))
    b = min(len(d), a + 1 + rng.randrange(5))
    return prog[:i] + d[a:b] + prog[j:], kind


def mutate_seq(sub, prog, rng, radius, donors):
    cur = prog
    kinds = []
    for _ in range(radius):
        for _try in range(5):
            cand, kind = _seq_atomic(sub, cur, rng, donors)
            if 0 < len(cand) <= PROG_MAX:
                cur, k = cand, kind
                break
        else:
            i = rng.randrange(len(cur))
            cur = cur[:i] + (sub.random_tokens(rng, 1)[0],) + cur[i + 1:]
            k = "E-SUBST"
        kinds.append(k)
    return cur, kinds


# ---------------- tree basis ----------------
def _walk(tree, path=(), ty="LL"):
    yield path, tree, ty
    cts = s1_tpc.OPS[tree[0]][2]
    for i, k in enumerate(tree[2]):
        yield from _walk(k, path + (i,), cts[i])


def _get(tree, path):
    for i in path:
        tree = tree[2][i]
    return tree


def _put(tree, path, new):
    if not path:
        return new
    i = path[0]
    kids = list(tree[2])
    kids[i] = _put(kids[i], path[1:], new)
    return (tree[0], tree[1], tuple(kids))


def _tree_atomic(tree, rng):
    kind = rng.choice(TREE_EDITS)
    nodes = list(_walk(tree))
    path, nd, ty = nodes[rng.randrange(len(nodes))]
    if kind == "E-REPLACE":
        b = max(1, s1_tpc.size(nd) + rng.randrange(-1, 3))
        return _put(tree, path, s1_tpc.gen(ty, b, rng)), kind
    if kind == "E-PERTURB":
        na = (nd[1] + rng.choice([-1, 1])) % s1_tpc.NARG
        return _put(tree, path, (nd[0], na, nd[2])), kind
    if kind == "E-SWAP":
        same = [(p, n) for (p, n, t) in nodes if t == ty and p != path]
        same = [(p, n) for (p, n) in same
                if p[:len(path)] != path and path[:len(p)] != p]
        if not same:
            return tree, kind
        p2, n2 = same[rng.randrange(len(same))]
        t1 = _put(tree, path, n2)
        return _put(t1, p2, nd), kind
    if kind == "E-GRAFT":
        cands = [s for s in s1_tpc.BY_TYPE[ty] if ty in s1_tpc.OPS[s][2]]
        if not cands:
            return tree, kind
        slot = cands[rng.randrange(len(cands))]
        cts = s1_tpc.OPS[slot][2]
        slots = [i for i, c in enumerate(cts) if c == ty]
        hole = slots[rng.randrange(len(slots))]
        kids = []
        for i, c in enumerate(cts):
            kids.append(nd if i == hole else s1_tpc.gen(c, 1, rng))
        return _put(tree, path, (slot, rng.randrange(s1_tpc.NARG), tuple(kids))), kind
    # E-PRUNE
    cts = s1_tpc.OPS[nd[0]][2]
    same_kids = [k for i, k in enumerate(nd[2]) if cts[i] == ty]
    if same_kids:
        return _put(tree, path, same_kids[rng.randrange(len(same_kids))]), kind
    leaf = s1_tpc.LEAF_BY_TYPE[ty][rng.randrange(len(s1_tpc.LEAF_BY_TYPE[ty]))]
    return _put(tree, path, (leaf, rng.randrange(s1_tpc.NARG), ())), kind


def mutate_tree(sub, prog, rng, radius, donors=None):
    tree = sub.decode(prog)
    if tree is None:
        return prog, []
    kinds = []
    for _ in range(radius):
        done = False
        for _try in range(6):
            cand, kind = _tree_atomic(tree, rng)
            if s1_tpc.size(cand) <= PROG_MAX:
                tree, k = cand, kind
                done = True
                break
        if not done:
            nodes = list(_walk(tree))
            path, nd, ty = nodes[rng.randrange(len(nodes))]
            cts = s1_tpc.OPS[nd[0]][2]
            same_kids = [kk for i, kk in enumerate(nd[2]) if cts[i] == ty]
            if same_kids:
                tree = _put(tree, path, same_kids[0])
            else:
                leaf = s1_tpc.LEAF_BY_TYPE[ty][0]
                tree = _put(tree, path, (leaf, nd[1], ()))
            k = "E-PRUNE"
        kinds.append(k)
    return sub.encode(tree), kinds


def mutate(basis, sub, prog, rng, radius, donors):
    if basis == "S1":
        return mutate_tree(sub, prog, rng, radius, donors)
    return mutate_seq(sub, prog, rng, radius, donors)


# ---------------- generic recombination (used by M0d) ----------------
def recombine(basis, sub, p, q, rng):
    """Substrate-native generic crossover: one-point on token strings for the
    sequence bases, type-matched subtree exchange for the tree basis."""
    if basis == "S1":
        tp, tq = sub.decode(p), sub.decode(q)
        if tp is None or tq is None:
            return p
        np_ = list(_walk(tp))
        nq = list(_walk(tq))
        rng.shuffle(np_)
        for path, nd, ty in np_:
            same = [(p2, n2) for (p2, n2, t2) in nq if t2 == ty]
            if not same:
                continue
            _p2, n2 = same[rng.randrange(len(same))]
            cand = _put(tp, path, n2)
            if s1_tpc.size(cand) <= PROG_MAX:
                return sub.encode(cand)
        return p
    i = rng.randrange(1, len(p)) if len(p) > 1 else 1
    j = rng.randrange(0, len(q))
    c = p[:i] + q[j:]
    if len(c) > PROG_MAX:
        c = c[:PROG_MAX]
    if not c:
        c = p
    return c
