"""Probe of a candidate replacement universe: bounded equational rewriting.
State = a word over {x, X, y, Y} (X = inverse of x) of length <= L.  Universal graph, problem-independent.
Actions = primitive inference steps applied at a position:
  cancel   : delete an adjacent inverse pair (xX, Xx, yY, Yy)
  introduce: insert an inverse pair (if length allows)  -- the reverse of cancel
  relator  : rewrite by a presentation relation, both directions
Two presentations: ABELIAN <x,y | xy=yx> (known coordinates: exponent vector) and BRAID <x,y | xyx=yxy> (B3).
Targets = all words of length <= 2 (21 targets).  D(s,t) = exact shortest derivation length (undirected graph)."""
import collections, json, random, sys, time
random.seed(0)
INF = 10**9
INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
ALPH = "xXyY"

def build(L, relators):
    # relators: list of (lhs, rhs) applied both directions
    rules = []  # (name, family, lhs, rhs)
    for a in ALPH:
        rules.append((f"cancel[{a}{INV[a]}]", "cancel", a + INV[a], ""))
    for a in ALPH:
        rules.append((f"introduce[{a}{INV[a]}]", "introduce", "", a + INV[a]))
    for i, (l, r) in enumerate(relators):
        rules.append((f"rel{i}[{l}->{r}]", "relator", l, r))
        rules.append((f"rel{i}[{r}->{l}]", "relator", r, l))
    states = [""]
    frontier = [""]
    for ln in range(1, L + 1):
        frontier = [w + a for w in frontier for a in ALPH]
        states.extend(frontier)
    idx = {w: i for i, w in enumerate(states)}
    succ = [None] * len(states)
    nominal = [0] * len(states)
    for w, i in idx.items():
        out = set(); n = 0
        for (nm, fam, l, r) in rules:
            k = len(l)
            if len(w) - k + len(r) > L:
                continue
            for p in range(len(w) - k + 1):
                if w[p:p + k] == l:
                    n += 1
                    out.add(idx[w[:p] + r + w[p + k:]])
        succ[i] = sorted(out); nominal[i] = n
    return states, idx, succ, nominal, rules

def analyse(name, L, relators):
    t0 = time.time()
    states, idx, succ, nominal, rules = build(L, relators)
    NS = len(states)
    targets = [w for w in states if len(w) <= 2]
    T = len(targets)
    D = [[INF] * T for _ in range(NS)]
    for j, t in enumerate(targets):
        ti = idx[t]; D[ti][j] = 0
        dq = collections.deque([ti])
        while dq:
            s = dq.popleft(); d = D[s][j] + 1
            for u in succ[s]:
                if D[u][j] == INF:
                    D[u][j] = d; dq.append(u)
    t1 = time.time()
    res = {"universe": name, "L": L, "rule_types": len(rules), "states": NS, "targets": T}
    res["mean_nominal_branching"] = sum(nominal) / NS
    res["mean_effective_branching_distinct_successors"] = sum(len(s) for s in succ) / NS
    res["fixpoint_states_no_action"] = sum(1 for s in succ if not s)
    # empty-word target (the word problem)
    j0 = targets.index("")
    live = [s for s in range(NS) if D[s][j0] < INF]
    res["states_from_which_empty_word_reachable"] = len(live)
    # trap transitions: live -> dead, for the empty-word target
    traps = 0; live_edges = 0; trap_succ_with_actions = 0; dead_comp_sizes = []
    dead_seen = set()
    for s in live:
        for u in succ[s]:
            live_edges += 1
            if D[u][j0] == INF:
                traps += 1
                if succ[u]:
                    trap_succ_with_actions += 1
    res["trap_transitions_fraction_of_edges_from_live_states"] = traps / max(1, live_edges)
    res["trap_successors_that_still_have_legal_actions_fraction"] = trap_succ_with_actions / max(1, traps)
    # size of dead region entered by a trap (how many more steps could look alive)
    comp = {}
    for s in live:
        for u in succ[s]:
            if D[u][j0] == INF and u not in comp:
                seen = {u}; dq = collections.deque([u])
                while dq:
                    v = dq.popleft()
                    for w_ in succ[v]:
                        if w_ not in seen:
                            seen.add(w_); dq.append(w_)
                comp[u] = len(seen)
    if comp:
        cs = sorted(comp.values())
        res["dead_region_size_after_trap_median_max"] = [cs[len(cs) // 2], cs[-1]]
    # problems: w_init length 3..L, any target, D>=1
    probs = [(s, j, D[s][j]) for s in range(NS) if len(states[s]) >= 3 for j in range(T) if 0 < D[s][j] < INF]
    dist = collections.Counter(d for _, _, d in probs)
    res["candidate_problems"] = len(probs)
    res["D_distribution"] = {str(k): dist[k] for k in sorted(dist)}
    res["eligible_EASY_3_4"] = sum(v for k, v in dist.items() if 3 <= k <= 4)
    res["eligible_MEDIUM_5_6"] = sum(v for k, v in dist.items() if 5 <= k <= 6)
    res["eligible_HARD_ge_7"] = sum(v for k, v in dist.items() if k >= 7)
    res["max_D"] = max(dist)
    # search costs: plain BFS expansions vs bidirectional BFS vs D
    def bfs_cost(s0, tj):
        ti = idx[targets[tj]]
        seen = {s0}; dq = collections.deque([s0]); popped = 0
        while dq:
            s = dq.popleft(); popped += 1
            if s == ti:
                return popped
            for u in succ[s]:
                if u not in seen:
                    seen.add(u); dq.append(u)
        return -1
    def bibfs_cost(s0, tj):
        ti = idx[targets[tj]]
        if s0 == ti: return 1
        A = {s0: 0}; B = {ti: 0}; fa = [s0]; fb = [ti]; popped = 0
        while fa and fb:
            if len(fa) <= len(fb):
                nf = []
                for s in fa:
                    popped += 1
                    for u in succ[s]:
                        if u in B: return popped
                        if u not in A: A[u] = 1; nf.append(u)
                fa = nf
            else:
                nf = []
                for s in fb:
                    popped += 1
                    for u in succ[s]:
                        if u in A: return popped
                        if u not in B: B[u] = 1; nf.append(u)
                fb = nf
        return -1
    sample = random.sample(probs, min(1500, len(probs)))
    bf = []; bb = []; dd = []
    for s, j, d in sample:
        bf.append(bfs_cost(s, j)); bb.append(bibfs_cost(s, j)); dd.append(d)
    res["sampled_problems"] = len(sample)
    res["mean_BFS_expansions"] = sum(bf) / len(bf)
    res["mean_bidirectional_BFS_expansions"] = sum(bb) / len(bb)
    res["mean_D"] = sum(dd) / len(dd)
    res["search_avoided_ceiling_vs_BFS"] = 1 - sum(dd) / sum(bf)
    res["search_avoided_ceiling_vs_bidirectional_BFS"] = 1 - sum(dd) / sum(bb)
    for lo, hi, nm in [(3, 4, "EASY"), (5, 6, "MEDIUM"), (7, 99, "HARD")]:
        ii = [i for i in range(len(sample)) if lo <= dd[i] <= hi]
        if ii:
            res[f"{nm}_n_meanBFS_meanBiBFS_meanD"] = [len(ii), sum(bf[i] for i in ii) / len(ii), sum(bb[i] for i in ii) / len(ii), sum(dd[i] for i in ii) / len(ii)]
    # off-shortest-path fraction and trap fraction at problem starts
    off = 0; tot = 0; trap_at_start = 0
    for s, j, d in sample:
        for u in succ[s]:
            tot += 1
            if D[u][j] + 1 != d: off += 1
            if D[u][j] == INF: trap_at_start += 1
    res["off_shortest_path_action_fraction_at_s_init"] = off / tot
    res["trap_action_fraction_at_s_init"] = trap_at_start / tot
    # behavioral classes: distinct D rows (over 21 targets) among states
    rows = collections.Counter(tuple(min(v, 99) for v in D[s]) for s in range(NS))
    res["distinct_D_rows"] = len(rows)
    # exponent-vector classes (true coordinates in the abelian case; a syntactic invariant in both)
    def expv(w):
        return (w.count("x") - w.count("X"), w.count("y") - w.count("Y"))
    res["distinct_exponent_vectors"] = len({expv(w) for w in states})
    # does D-row factor through exponent vector?  count D-rows per exponent class
    per = collections.defaultdict(set)
    for s in range(NS):
        per[expv(states[s])].add(tuple(min(v, 99) for v in D[s]))
    res["mean_distinct_D_rows_per_exponent_class"] = sum(len(v) for v in per.values()) / len(per)
    # operator families: nominal rule types vs distinct successor maps are trivially merged by the state; report families
    res["rule_families"] = dict(collections.Counter(r[1] for r in rules))
    res["seconds"] = round(t1 - t0, 1)
    return res

if __name__ == "__main__":
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    out = []
    out.append(analyse("ABELIAN", L, [("xy", "yx"), ("xY", "Yx"), ("Xy", "yX"), ("XY", "YX")]))
    out.append(analyse("BRAID_B3", L, [("xyx", "yxy"), ("XYX", "YXY")]))
    print(json.dumps(out, indent=1))
    json.dump(out, open(f"rewrite_results_L{L}.json", "w"), indent=1)
