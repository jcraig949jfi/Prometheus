"""DIAGNOSTIC PROBE (not adopted universe code): transformation monoid T_n as a PC-H candidate.

State = a map f: [n] -> [n] (n^n states).  Action g in {c = n-cycle, tau = swap(0,1), e = collapse 0->1}: f' = g o f.
Theory to falsify: t reachable from f  <=>  ker f refines ker t (f(i)=f(j) => t(i)=t(j)).
Targets (mechanical): every restricted-growth map of rank k (canonical representative of each set partition into k blocks).
Measures: reachability == kernel criterion; trap prevalence; rank-invisible traps; forward-region size and BFS
eccentricity after a trap; D distribution; retained-but-not-shortest edges; random-walk solve rate; BFS cost vs oracle.
Usage: python probe_tn.py 6 3
"""
import sys, json, itertools, collections, random
import numpy as np

n = int(sys.argv[1]); k = int(sys.argv[2]); genset = sys.argv[3]; seed = int(sys.argv[4]); random.seed(seed)
NS = n ** n
pw = n ** np.arange(n - 1, -1, -1, dtype=np.int64)
idx = np.arange(NS, dtype=np.int64)
F = np.stack([(idx // pw[i]) % n for i in range(n)], axis=1).astype(np.int64)  # F[s, i] = f(i)
rr = random.Random(seed)
def randmap(rank):
    while True:
        m_ = [rr.randrange(n) for _ in range(n)]
        if len(set(m_)) == rank: return np.array(m_)
if genset == "full":
    gens = {"cycle": np.array([(i + 1) % n for i in range(n)]), "swap01": np.array([1, 0] + list(range(2, n))), "collapse01": np.array([1] + list(range(1, n)))}
elif genset == "cycle+map":
    gens = {"cycle": np.array([(i + 1) % n for i in range(n)]), "map_r" + str(n - 2): randmap(n - 2), "map_r" + str(n - 1): randmap(n - 1)}
elif genset == "cycle+swap+map":
    gens = {"cycle": np.array([(i + 1) % n for i in range(n)]), "swap01": np.array([1, 0] + list(range(2, n))), "map_r" + str(n - 2): randmap(n - 2)}
print("generators", {k_: v.tolist() for k_, v in gens.items()})
edges = {}
for name, g in gens.items():
    Fp = g[F]; edges[name] = (Fp * pw).sum(axis=1)
src = np.concatenate([idx] * 3); dst = np.concatenate([edges[g] for g in gens]); gid = np.concatenate([np.full(NS, i) for i in range(3)])
# canonical rank-k targets: restricted growth strings with max label k-1
def rgs(n, k):
    out = []
    def rec(prefix, mx):
        if len(prefix) == n:
            if mx == k - 1: out.append(tuple(prefix))
            return
        for v in range(min(mx + 2, k)):
            rec(prefix + [v], max(mx, v))
    rec([0], 0); return out
targets = [int((np.array(t) * pw).sum()) for t in rgs(n, k)]
T = len(targets)
# reverse adjacency
order = np.argsort(dst, kind="stable"); rs, rd = dst[order], src[order]
rptr = np.searchsorted(rs, np.arange(NS + 1))
def rev_bfs(t):
    D = np.full(NS, -1, dtype=np.int16); D[t] = 0; fr = np.array([t]); d = 0
    while fr.size:
        d += 1
        cnt = rptr[fr + 1] - rptr[fr]; tot = int(cnt.sum())
        if not tot: break
        starts = np.repeat(rptr[fr], cnt); within = np.arange(tot) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        nb = np.unique(rd[starts + within]); fr = nb[D[nb] < 0]; D[fr] = d
    return D
D = np.stack([rev_bfs(t) for t in targets], axis=1)
# kernel criterion
pairs = list(itertools.combinations(range(n), 2))
KER = np.stack([F[:, i] == F[:, j] for i, j in pairs], axis=1)  # KER[s, p] = f identifies pair p
crit = np.stack([~(KER[:, :] & ~KER[t][None, :]).any(axis=1) for t in targets], axis=1)  # ker f subset ker t
res = {"n": n, "k": k, "genset": genset, "seed": seed, "generators": {k_: v.tolist() for k_, v in gens.items()}, "states": NS, "targets": T,
       "reachability_equals_kernel_criterion": bool(np.array_equal(crit, D >= 0)),
       "kernel_compatible_pairs": int(crit.sum()), "reachable_pairs": int((D >= 0).sum()),
       "kernel_compatible_but_unreachable_fraction": float(1 - (D >= 0).sum() / max(1, crit.sum())),
       "reachable_but_kernel_incompatible": int(((D >= 0) & ~crit).sum()),
       "targets_reachable_from_somewhere": int(((D >= 0).sum(axis=0) > 1).sum()),
       "live_fraction": float((D >= 0).mean())}
rank = np.array([len(set(row)) for row in F.tolist()]); rank_t = np.array([rank[t] for t in targets])
# traps
tot_live = 0; traps = 0; rank_visible = 0; by_gen = collections.Counter(); trap_succ = set(); retained = 0; on_sp = 0
for j in range(T):
    Ds, Dd = D[src, j], D[dst, j]; live = Ds >= 0; tr = live & (Dd < 0)
    tot_live += int(live.sum()); traps += int(tr.sum()); rank_visible += int((tr & (rank[dst] < rank_t[j])).sum())
    for gi in range(3): by_gen[list(gens)[gi]] += int((tr & (gid == gi)).sum())
    same_kernel_traps = 0
    trap_succ.update(dst[tr].tolist()); ret = live & (Dd >= 0); retained += int(ret.sum()); on_sp += int((ret & (Dd + 1 == Ds)).sum())
res.update({"live_triples": tot_live, "traps": traps, "trap_rate": traps / tot_live, "traps_by_generator": dict(by_gen),
            "traps_visible_by_rank_drop_below_target_rank": rank_visible, "rank_invisible_trap_fraction": 1 - rank_visible / max(1, traps),
            "retained_edges": retained, "retained_not_on_shortest_path": retained - on_sp, "distinct_trap_successors": len(trap_succ)})
# forward region + eccentricity after traps (sample)
fptr_order = np.argsort(src, kind="stable"); fs, fd = src[fptr_order], dst[fptr_order]; fptr = np.searchsorted(fs, np.arange(NS + 1))
def region(s):
    seen = {s}; fr = [s]; depth = 0
    while fr:
        nx = []
        for v in fr:
            for u in fd[fptr[v]:fptr[v + 1]].tolist():
                if u not in seen: seen.add(u); nx.append(u)
        if not nx: break
        fr = nx; depth += 1
    return len(seen), depth
samp = random.sample(sorted(trap_succ), min(200, len(trap_succ)))
regs = [region(s) for s in samp]
res["post_trap_region_size_quartiles"] = [int(np.percentile([r for r, _ in regs], q)) for q in (0, 25, 50, 75, 100)]
res["post_trap_eccentricity_quartiles"] = [int(np.percentile([e for _, e in regs], q)) for q in (0, 25, 50, 75, 100)]
live_D = D[D >= 0]; res["D_histogram"] = {int(v): int(c) for v, c in zip(*np.unique(live_D, return_counts=True))}
res["max_D"] = int(live_D.max())
# random greedy walk solve rate and forward BFS cost vs oracle on sampled problems with D >= 4
cand = np.argwhere(D >= 4); sel = cand[np.random.default_rng(0).choice(len(cand), min(400, len(cand)), replace=False)]
solved = 0; bfs_cost = []; orc = []
for s, j in sel:
    s = int(s); t = targets[j]; v = s
    for _ in range(60):
        if v == t: break
        v = int(fd[fptr[v] + random.randrange(3)])
    solved += v == t
    # forward BFS expansions
    seen = {s}; dq = collections.deque([s]); pops = 0; found = False
    while dq and not found:
        u = dq.popleft(); pops += 1
        if u == t: found = True; break
        for w_ in fd[fptr[u]:fptr[u + 1]].tolist():
            if w_ not in seen: seen.add(w_); dq.append(w_)
    bfs_cost.append(pops); orc.append(int(D[s, j]))
res["random_walk_solve_rate_D_ge_4"] = solved / len(sel); res["mean_forward_bfs_expansions"] = float(np.mean(bfs_cost)); res["mean_D_sampled"] = float(np.mean(orc))
res["oracle_SA_vs_forward_bfs_states"] = 1 - sum(orc) / sum(bfs_cost)
print(json.dumps(res, indent=1)); json.dump(res, open(f"probe_tn_n{n}_k{k}_{genset}_s{seed}.json", "w"), indent=1)
