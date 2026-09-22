"""DIAGNOSTIC PROBE (not adopted universe code): Tseitin XOR partial assignments on the cube graph Q3 (8 vertices, 12 edges).

State = partial assignment of the 12 edge variables (3^12 = 531,441 states).  Action = assign a free variable 0 or 1
(irreversible).  Constraint: for every vertex v, XOR of incident edges = charge(v), with total charge even (satisfiable).
Target set = all complete solutions (2^(12-8+1) = 32) ; reachability = the partial assignment extends to that solution.
Hidden invariant: consistency of a GF(2) linear system.  Cheap local reasoning: unit propagation on XOR constraints.
Measures: traps (assigning an implied variable wrongly), fraction caught by unit propagation at depth 0, DPLL refutation
depth of the residual after a trap (= exact lookahead horizon), post-trap region sizes.
Usage: python probe_tseitin.py
"""
import json, itertools, collections, random
import numpy as np
random.seed(0)
V = 8; edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
m = len(edges)
inc = [[e for e, (a, b) in enumerate(edges) if v in (a, b)] for v in range(V)]
charge = [1, 0, 1, 0, 0, 1, 0, 1]  # even total
assert sum(charge) % 2 == 0
# solutions
sols = []
for bits in range(1 << m):
    ok = all(sum(bits >> e & 1 for e in inc[v]) % 2 == charge[v] for v in range(V))
    if ok: sols.append(bits)
print("solutions", len(sols))
# partial assignment encoding: base-3 digits, 2 = unassigned
NS = 3 ** m
pw = 3 ** np.arange(m - 1, -1, -1, dtype=np.int64)
idx = np.arange(NS, dtype=np.int64)
A = np.stack([(idx // pw[i]) % 3 for i in range(m)], axis=1).astype(np.int8)
sol_bits = np.array([[s >> e & 1 for e in range(m)] for s in sols], dtype=np.int8)
# extendability to each solution: assigned variables must agree
ext = np.ones((NS, len(sols)), dtype=bool)
for e in range(m):
    assigned = A[:, e] != 2
    ext &= ~(assigned[:, None] & (A[:, e][:, None] != sol_bits[:, e][None, :]))
live_any = ext.any(axis=1)
res = {"vars": m, "states": NS, "solutions": len(sols), "live_states_fraction": float(live_any.mean())}
# traps: assign free var e to value b; trap for solution t iff ext[s,t] and not ext[s',t]
def succ_index(s_row, e, b):
    r = s_row.copy(); r[e] = b; return int((r.astype(np.int64) * pw).sum())
# unit propagation on XOR constraints: returns conflict flag and forced literals
def up(assign):
    a = list(assign); changed = True
    while changed:
        changed = False
        for v in range(V):
            un = [e for e in inc[v] if a[e] == 2]
            s = sum(a[e] for e in inc[v] if a[e] != 2) % 2
            if not un:
                if s != charge[v]: return True, a
            elif len(un) == 1:
                a[un[0]] = (charge[v] - s) % 2; changed = True
    return False, a
def refutation_depth(assign, limit=12):
    """min depth of a DPLL refutation (branch on any free variable, UP after each branch); inf if satisfiable."""
    conf, a = up(assign)
    if conf: return 0
    free = [e for e in range(m) if a[e] == 2]
    if not free: return 10**6  # satisfied
    best = 10**6
    for h in range(1, limit + 1):
        if any(max(refutation_depth_bounded(a, e, 0, h - 1), refutation_depth_bounded(a, e, 1, h - 1)) < 10**6 and
               refutation_depth_bounded(a, e, 0, h - 1) < 10**6 and refutation_depth_bounded(a, e, 1, h - 1) < 10**6 for e in free):
            return h
    return 10**6
from functools import lru_cache
@lru_cache(maxsize=None)
def _rd(key, h):
    a = list(key); conf, a = up(a)
    if conf: return 0
    free = [e for e in range(m) if a[e] == 2]
    if not free or h == 0: return 10**6
    for e in free:
        d0 = _rd(tuple(a[:e] + [0] + a[e + 1:]), h - 1)
        if d0 >= 10**6: continue
        d1 = _rd(tuple(a[:e] + [1] + a[e + 1:]), h - 1)
        if d1 < 10**6: return 1 + max(d0, d1)
    return 10**6
def refutation_depth_bounded(a, e, b, h):
    return _rd(tuple(a[:e] + [b] + a[e + 1:]), h)
def ref_depth(assign):
    for h in range(0, m + 1):
        if _rd(tuple(assign), h) < 10**6: return h
    return 10**6
# enumerate traps on a sample of live states with >=1 assigned var (all-target version is too big to hold; sample)
rng = np.random.default_rng(0)
live_idx = np.nonzero(live_any)[0]
nass = (A[live_idx] != 2).sum(axis=1); light = live_idx[nass <= 5]; samp = rng.choice(light, min(3000, len(light)), replace=False)
traps = 0; live_triples = 0; up_caught = 0; depths = collections.Counter(); region = []
for s in samp.tolist():
    row = A[s]; free = np.nonzero(row == 2)[0]
    for e in free.tolist():
        for b in (0, 1):
            sp = succ_index(row, e, b); r2 = A[sp]
            for j in range(len(sols)):
                if ext[s, j]:
                    live_triples += 1
                    if not ext[sp, j]:
                        traps += 1
                        if not ext[sp].any():  # residual unsat: a genuine (all-target) trap
                            pass
            if ext[s].any() and not ext[sp].any():
                conf, _ = up(r2.tolist()); up_caught += conf
                depths[ref_depth(r2.tolist())] += 1
                region.append(int(3 ** int((r2 == 2).sum())))
res.update({"sampled_live_states": len(samp), "live_triples": live_triples, "traps_per_target": traps, "trap_rate_per_target": traps / max(1, live_triples),
            "all_target_traps": int(sum(depths.values())), "caught_by_unit_propagation_at_depth0": up_caught,
            "dpll_refutation_depth_histogram": {str(k): v for k, v in sorted(depths.items())},
            "post_trap_region_size_quartiles": [int(np.percentile(region, q)) for q in (0, 25, 50, 75, 100)] if region else None})
print(json.dumps(res, indent=1)); json.dump(res, open("probe_tseitin_q3_light.json", "w"), indent=1)
