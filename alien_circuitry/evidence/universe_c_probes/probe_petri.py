"""DIAGNOSTIC PROBE (not adopted universe code): random bounded Petri nets as a U-C1 candidate.

State = marking M in {0..B}^p.  Action = fire transition j (enabled iff M >= pre_j; M' = M - pre_j + post_j; firings that
exceed the bound B on any place are illegal, so the cap is a hard resource limit).  Targets (mechanical) = the reachable markings
with the minimum reachable token total (first 60 in index order).
Hidden linear structure: place invariants y (y.C = 0) give y.M constant along every path; the state equation
M_t - M = C x, x >= 0 gives an LP-relaxation certificate.  We measure how many traps those cheap certificates explain.
Usage: python probe_petri.py <seed> <places> <transitions> <bound>
"""
import sys, json, random, collections, itertools
import numpy as np
from scipy.optimize import linprog
from scipy.linalg import null_space

seed, p, q, B = (int(x) for x in sys.argv[1:5]); rng = random.Random(seed)
pre = np.zeros((p, q), dtype=np.int64); post = np.zeros((p, q), dtype=np.int64)
for j in range(q):
    for pl in rng.sample(range(p), rng.choice([1, 1, 2])): pre[pl, j] = 1
    for pl in rng.sample(range(p), rng.choice([1, 1, 2])): post[pl, j] = 1
C = post - pre
NS = (B + 1) ** p
pw = (B + 1) ** np.arange(p - 1, -1, -1, dtype=np.int64)
idx = np.arange(NS, dtype=np.int64)
Mk = np.stack([(idx // pw[i]) % (B + 1) for i in range(p)], axis=1).astype(np.int64)
srcs = []; dsts = []; tids = []
for j in range(q):
    en = (Mk >= pre[:, j]).all(axis=1)
    Mp = Mk + C[:, j][None, :]
    ok = en & (Mp <= B).all(axis=1) & (Mp >= 0).all(axis=1)
    s = idx[ok]; d = (Mp[ok] * pw).sum(axis=1)
    srcs.append(s); dsts.append(d); tids.append(np.full(len(s), j))
src = np.concatenate(srcs); dst = np.concatenate(dsts); tid = np.concatenate(tids)
outdeg = np.bincount(src, minlength=NS)
# initial marking: B tokens spread; reachable set
M0 = int(((np.array([1] * p) * pw).sum()))
fo = np.argsort(src, kind="stable"); fs, fd = src[fo], dst[fo]; fptr = np.searchsorted(fs, np.arange(NS + 1))
def fwd(s):
    seen = {s}; fr = [s]; depth = 0
    while fr:
        nx = []
        for v in fr:
            for u in fd[fptr[v]:fptr[v + 1]].tolist():
                if u not in seen: seen.add(u); nx.append(u)
        if not nx: break
        fr = nx; depth += 1
    return seen, depth
R, _ = fwd(M0)
tot = {t: int(Mk[t].sum()) for t in R}; mn = min(tot.values()); targets = sorted(t for t in R if tot[t] == mn)[:60]
if not targets:
    print(json.dumps({"seed": seed, "note": "no low-token targets reachable"})); sys.exit()
T = len(targets)
ro = np.argsort(dst, kind="stable"); rs, rd = dst[ro], src[ro]; rptr = np.searchsorted(rs, np.arange(NS + 1))
def rev_bfs(t):
    D = np.full(NS, -1, dtype=np.int16); D[t] = 0; fr = np.array([t]); d = 0
    while fr.size:
        d += 1; cnt = rptr[fr + 1] - rptr[fr]; tot = int(cnt.sum())
        if not tot: break
        starts = np.repeat(rptr[fr], cnt); within = np.arange(tot) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        nb = np.unique(rd[starts + within]); fr = nb[D[nb] < 0]; D[fr] = d
    return D
D = np.stack([rev_bfs(t) for t in targets], axis=1)
Rarr = np.array(sorted(R))
# invariants
Y = null_space(C.T.astype(float))  # columns y with y.C = 0
def inv_compatible(M, t):
    if Y.shape[1] == 0: return True
    return np.allclose(Y.T @ M, Y.T @ Mk[t], atol=1e-6)
def lp_compatible(M, t):
    b = Mk[t] - M
    r = linprog(np.zeros(q), A_eq=C.astype(float), b_eq=b.astype(float), bounds=[(0, None)] * q, method="highs")
    return r.status == 0
live = 0; traps = 0; by_t = collections.Counter(); inv_caught = 0; lp_caught = 0; trap_succ = set(); ret = 0; on_sp = 0
Rset = set(Rarr.tolist())
mask_edges = np.isin(src, Rarr)
es, ed, et = src[mask_edges], dst[mask_edges], tid[mask_edges]
for j, t in enumerate(targets):
    Ds, Dd = D[es, j], D[ed, j]; lv = Ds >= 0; tr = lv & (Dd < 0)
    live += int(lv.sum()); traps += int(tr.sum())
    for jj in range(q): by_t[jj] += int((tr & (et == jj)).sum())
    r_ = lv & (Dd >= 0); ret += int(r_.sum()); on_sp += int((r_ & (Dd + 1 == Ds)).sum())
    for e in np.nonzero(tr)[0][:: max(1, int(tr.sum()) // 300 + 1)].tolist():
        trap_succ.add((int(ed[e]), j))
samp = random.sample(sorted(trap_succ), min(400, len(trap_succ)))
for s, j in samp:
    inv_caught += not inv_compatible(Mk[s], targets[j]); lp_caught += not lp_compatible(Mk[s], targets[j])
regs = [fwd(s)[0] for s, _ in samp[:150]]; eccs = [fwd(s)[1] for s, _ in samp[:150]]
res = {"seed": seed, "places": p, "transitions": q, "bound": B, "states": NS, "reachable_from_M0": len(R), "edges": int(len(src)),
       "targets": T, "place_invariants": int(Y.shape[1]), "mean_outdeg_reachable": float(outdeg[Rarr].mean()),
       "live_triples": live, "traps": traps, "trap_rate": traps / max(1, live), "traps_by_transition": dict(by_t),
       "sampled_trap_successors": len(samp), "caught_by_place_invariants": inv_caught, "caught_by_state_equation_LP": lp_caught,
       "beyond_linear_fraction": 1 - lp_caught / max(1, len(samp)),
       "retained_edges": ret, "retained_not_on_shortest_path": ret - on_sp,
       "post_trap_region_quartiles": [int(np.percentile([len(r) for r in regs], qq)) for qq in (0, 25, 50, 75, 100)],
       "post_trap_ecc_quartiles": [int(np.percentile(eccs, qq)) for qq in (0, 25, 50, 75, 100)],
       "max_D_from_reachable": int(D[Rarr].max())}
print(json.dumps(res, indent=1)); json.dump(res, open(f"probe_petri_s{seed}_p{p}_q{q}_B{B}.json", "w"), indent=1)
