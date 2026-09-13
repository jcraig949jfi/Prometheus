"""Mechanism trace on one state: where along the greedy-lex tree does the exact optimum diverge, and what do the
continuation states look like (block structure)? Uses the S5 producer's DP (memoised) for the optimum."""
import sys
import numpy as np
sys.path.insert(0, r"F:\Prometheus-worktrees\archaeon-pass-1804"); sys.path.insert(0, ".")
from archaeon.producer import s5_producers as O
from s5_explore import World

L = 8; W = World(L); D = W.D

def describe(S):
    """target-free structure of a feasible subset: per position P(1), and the multiset of pairwise distances"""
    X = ((S[:, None] >> np.arange(L)) & 1)
    p1 = X.mean(0)
    fixed = int(((p1 == 0) | (p1 == 1)).sum())
    return "N %2d fixed %d p1 %s" % (len(S), fixed, "".join("F" if p in (0, 1) else ("h" if abs(p - 0.5) < 1e-9 else ("+" if p > 0.5 else "-")) for p in p1))

def greedy_probe(S):
    er, n = W.er1num_all(S); return int(np.flatnonzero(er == er.min())[0])

stats = {"memo_hits": 0, "fresh_subsets": 0}
def opt_value(S):
    return O._dp(L, D, np.array(sorted(S), dtype=np.int64), stats)

def walk(S, depth, path):
    if len(S) == 1 or depth > 3: return
    g = greedy_probe(S); ov, oq = opt_value(S)
    er, n = W.er1num_all(S)
    # expected cost of the greedy probe under OPTIMAL continuation, vs opt
    cg = 1.0
    for e in range(L + 1):
        cell = S[D[g, S] == e]
        if len(cell) > 1: cg += (len(cell) / len(S)) * opt_value(cell)[0]
    flag = "DIVERGE %.4f vs %.4f" % (cg, ov) if cg > ov + 1e-9 else "same"
    print("  " * depth + "[%s] %s | greedy q=%s part %s | opt q=%s | greedy-under-opt-continuation %s" % (path, describe(S), format(g, "08b")[::-1], {e: int(n[g, e]) for e in range(L + 1) if n[g, e]}, format(oq, "08b")[::-1], flag))
    for e in range(L + 1):
        cell = S[D[g, S] == e]
        if len(cell) > 1: walk(cell, depth + 1, path + "/%d" % e)

for name, fos in (("shell m2 L8", [(0, 2)]), ("counterexample", [(0, 3), (15, 5)])):
    S0 = W.feasible(fos); print("==", name, "opt E %.4f" % opt_value(S0)[0])
    walk(S0, 0, "root")
