"""Probe of the receipt's universe: monotone Datalog over {a,b,c}, P,Q,R, 5 rule templates.
Positive atoms only (negatives are never derived; contradiction handled analytically at the end).
Enumerates the full universal graph on 2^15 positive states and measures the properties
the spec demands: dead ends, HARD-stratum eligibility, search baseline honesty, behavioral rank."""
import itertools, collections, json, time, random, sys
random.seed(0)
INF = 10**9
def P(x): return x
def Q(x): return 3 + x
def R(x, y): return 6 + 3 * x + y
NPOS = 15
NAMES = [f"P({c})" for c in "abc"] + [f"Q({c})" for c in "abc"] + [f"R({x},{y})" for x in "abc" for y in "abc"]
acts = []  # (name, family, premise_mask, conclusion)
for x in range(3):
    for y in range(3):
        acts.append((f"MP[x={x},y={y}]", "MP", (1 << P(x)) | (1 << R(x, y)), Q(y)))
for x, y, z in itertools.product(range(3), repeat=3):
    acts.append((f"TR[{x},{y},{z}]", "TR", (1 << R(x, y)) | (1 << R(y, z)), R(x, z)))
for x in range(3):
    for y in range(3):
        acts.append((f"SY[x={x},y={y}]", "SY", (1 << Q(x)) | (1 << R(x, y)), R(y, x)))
for x in range(3):
    acts.append((f"PQ[{x}]", "PQ", 1 << P(x), Q(x)))
    acts.append((f"QP[{x}]", "QP", 1 << Q(x), P(x)))
NACT = len(acts)
NS = 1 << NPOS
t0 = time.time()
novel = [None] * NS
succs = [None] * NS
for s in range(NS):
    lst = [i for i, (_, _, pm, c) in enumerate(acts) if (s & pm) == pm and not (s >> c) & 1]
    novel[s] = lst
    succs[s] = sorted({s | (1 << acts[i][3]) for i in lst})
closure = [0] * NS
for s in range(NS - 1, -1, -1):
    closure[s] = s if not succs[s] else closure[succs[s][0]]
bad = sum(1 for s in range(NS) for u in succs[s] if closure[u] != closure[s])
assert bad == 0, bad
order = sorted(range(NS), key=lambda s: -bin(s).count("1"))
D = [None] * NS
for s in order:
    row = [0 if (s >> t) & 1 else INF for t in range(NPOS)]
    for u in succs[s]:
        du = D[u]
        for t in range(NPOS):
            v = du[t] + 1
            if v < row[t]:
                row[t] = v
    D[s] = row
t1 = time.time()
res = {}
res["nominal_actions"] = NACT
res["family_counts"] = dict(collections.Counter(a[1] for a in acts))
res["states"] = NS
res["fixpoint_states"] = sum(1 for s in range(NS) if not succs[s])
nb = [len(novel[s]) for s in range(NS)]
eb = [len(succs[s]) for s in range(NS)]
res["mean_nominal_novel_branching"] = sum(nb) / NS
res["mean_effective_branching_distinct_successors"] = sum(eb) / NS
res["max_nominal_novel_branching"] = max(nb)
res["max_effective_branching"] = max(eb)
viol = sum(1 for s in range(NS) for u in succs[s] if closure[u] != closure[s])
res["transitions_that_change_target_reachability"] = viol
probs = []
for s in range(NS):
    k = bin(s).count("1")
    if 2 <= k <= 5:
        for t in range(NPOS):
            if not (s >> t) & 1 and (closure[s] >> t) & 1:
                probs.append((s, t, D[s][t]))
res["candidate_problems_sinit_2to5_facts_t_reachable"] = len(probs)
dist = collections.Counter(d for _, _, d in probs)
res["D_distribution"] = {str(k): dist[k] for k in sorted(dist)}
res["eligible_D_ge_3"] = sum(v for k, v in dist.items() if k >= 3)
res["eligible_EASY_3_4"] = sum(v for k, v in dist.items() if 3 <= k <= 4)
res["eligible_MEDIUM_5_6"] = sum(v for k, v in dist.items() if 5 <= k <= 6)
res["eligible_HARD_ge_7"] = sum(v for k, v in dist.items() if k >= 7)
res["max_D_anywhere"] = max(v for s in range(NS) for v in D[s] if v < INF)
def bfs_cost(s0, t):
    seen = {s0}; dq = collections.deque([s0]); popped = 0
    while dq:
        s = dq.popleft(); popped += 1
        if (s >> t) & 1:
            return popped
        for u in succs[s]:
            if u not in seen:
                seen.add(u); dq.append(u)
    return -1
def reach_count(s0):
    seen = {s0}; dq = collections.deque([s0])
    while dq:
        s = dq.popleft()
        for u in succs[s]:
            if u not in seen:
                seen.add(u); dq.append(u)
    return len(seen)
def chain_cost(s0, t):
    s = s0; derived = 0
    while not (s >> t) & 1:
        new = {acts[i][3] for i in novel[s]}
        if not new:
            return -1
        for c in sorted(new):
            s |= 1 << c; derived += 1
            if c == t:
                return derived
    return derived
sample = random.sample(probs, min(3000, len(probs)))
bfs = []; chain = []; dd = []; rc = []
for s, t, d in sample:
    bfs.append(bfs_cost(s, t)); chain.append(chain_cost(s, t)); dd.append(d); rc.append(reach_count(s))
res["sampled_problems"] = len(sample)
res["mean_reachable_states_per_problem"] = sum(rc) / len(rc)
res["max_reachable_states_per_problem"] = max(rc)
res["mean_BFS_expansions"] = sum(bfs) / len(bfs)
res["mean_forward_chaining_facts_derived"] = sum(chain) / len(chain)
res["mean_D"] = sum(dd) / len(dd)
res["search_avoided_ceiling_vs_BFS"] = 1 - sum(dd) / sum(bfs)
res["search_avoided_ceiling_vs_forward_chaining"] = 1 - sum(dd) / sum(chain)
for lo, hi, name in [(3, 4, "EASY"), (5, 6, "MEDIUM"), (7, 99, "HARD")]:
    idx = [i for i in range(len(sample)) if lo <= dd[i] <= hi]
    if idx:
        res[f"{name}_n_meanBFS_meanChain_meanD"] = [len(idx), sum(bfs[i] for i in idx) / len(idx), sum(chain[i] for i in idx) / len(idx), sum(dd[i] for i in idx) / len(idx)]
off = 0; tot = 0
for s, t, d in sample:
    for i in novel[s]:
        tot += 1
        if D[s | (1 << acts[i][3])][t] + 1 != d:
            off += 1
res["off_shortest_path_action_fraction_at_s_init"] = off / tot
rows = collections.Counter(tuple(D[s]) for s in range(NS))
res["distinct_D_rows_all_states"] = len(rows)
res["distinct_closures"] = len(set(closure))
by_c = collections.Counter(a[3] for a in acts)
res["nominal_actions_per_conclusion_atom"] = {NAMES[c]: by_c[c] for c in sorted(by_c)}
res["effective_operator_rank_distinct_successor_maps"] = len({acts[i][3] for i in range(NACT)})
lost = 0; anyneg = 0; n = 0
for s, t, d in sample:
    negs = random.sample([i for i in range(NPOS) if not (s >> i) & 1 and i != t], 2)
    forb = sum(1 << i for i in negs)
    if closure[s] & forb:
        anyneg += 1
    cur = s
    while True:
        new = {acts[i][3] for i in novel[cur] if not (forb >> acts[i][3]) & 1}
        if not new: break
        for c in new: cur |= 1 << c
    if not (cur >> t) & 1:
        lost += 1
    n += 1
res["neg2_problems_whose_closure_hits_a_negated_atom"] = anyneg / n
res["neg2_problems_where_target_only_derivable_THROUGH_negated_atom"] = lost / n
res["enumeration_seconds"] = round(t1 - t0, 1)
print(json.dumps(res, indent=1))
json.dump(res, open(sys.argv[1], "w"), indent=1)
