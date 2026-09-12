"""DIAGNOSTIC PROBE (not adopted universe code): power-automaton (subset) universes of random 2-letter automata.

State = nonempty subset S of [n]; action = letter x; S' = x(S).  Irreversible because images can only shrink.
Question: do subsets of the SAME size split into different consequence classes (so that the size count is not the
whole invariant), how long are shortest words (horizon), and how big are post-trap regions?
Cerny automaton C_n is included as the known case where size IS the whole invariant.
Usage: python probe_subset_automata.py 10 8
"""
import sys, json, random, collections, itertools
import numpy as np

n = int(sys.argv[1]); seeds = int(sys.argv[2])
NSUB = 1 << n

def analyse(letters, name):
    L = len(letters)
    succ = np.zeros((NSUB, L), dtype=np.int64)
    for S in range(1, NSUB):
        for li, x in enumerate(letters):
            img = 0
            for i in range(n):
                if S >> i & 1: img |= 1 << x[i]
            succ[S, li] = img
    # reachability matrix among subsets reachable from the full set (the natural corpus)
    full = NSUB - 1
    reach_from = {}
    def bfs(s):
        seen = {s}; fr = [s]; depth = 0
        while fr:
            nx = []
            for v in fr:
                for u in succ[v]:
                    u = int(u)
                    if u not in seen: seen.add(u); nx.append(u)
            if not nx: break
            fr = nx; depth += 1
        return seen, depth
    R, _ = bfs(full); R = sorted(R)
    size = {S: bin(S).count("1") for S in R}
    # for each reachable subset, its forward-reachable set (as a frozenset) -> consequence class
    fwd = {S: bfs(S)[0] for S in R}
    same_size_pairs = 0; same_size_unreachable = 0
    by_size = collections.defaultdict(list)
    for S in R: by_size[size[S]].append(S)
    for sz, lst in by_size.items():
        for a in lst:
            for b in lst:
                if a != b:
                    same_size_pairs += 1
                    if b not in fwd[a]: same_size_unreachable += 1
    # traps w.r.t. targets = all reachable singletons (synchronization targets) and all reachable subsets of size 2
    targets = [S for S in R if size[S] <= 2]
    live = 0; traps = 0; size_invisible = 0; regions = []; eccs = []
    for S in R:
        for li in range(L):
            Sp = int(succ[S, li])
            for t in targets:
                if t in fwd[S]:
                    live += 1
                    if t not in fwd[Sp]:
                        traps += 1
                        if size[Sp] >= size[t]: size_invisible += 1
    samp = random.sample(R, min(150, len(R)))
    for S in samp:
        reg, ecc = bfs(S); regions.append(len(reg)); eccs.append(ecc)
    # diameter-ish: max shortest distance from full set
    dist = {full: 0}; fr = [full]; d = 0
    while fr:
        nx = []; d += 1
        for v in fr:
            for u in succ[v]:
                u = int(u)
                if u not in dist: dist[u] = d; nx.append(u)
        fr = nx
    return {"automaton": name, "n": n, "reachable_subsets_from_full": len(R), "same_size_ordered_pairs": same_size_pairs,
            "same_size_pairs_not_mutually_reachable_fraction": same_size_unreachable / max(1, same_size_pairs),
            "targets": len(targets), "live_triples": live, "traps": traps, "trap_rate": traps / max(1, live),
            "size_invisible_trap_fraction": size_invisible / max(1, traps),
            "region_size_quartiles": [int(np.percentile(regions, q)) for q in (0, 25, 50, 75, 100)],
            "eccentricity_quartiles": [int(np.percentile(eccs, q)) for q in (0, 25, 50, 75, 100)],
            "max_shortest_distance_from_full_set": max(dist.values())}

out = []
cerny = [[(i + 1) % n for i in range(n)], [1 if i == 0 else i for i in range(n)]]
out.append(analyse(cerny, "Cerny C_n"))
rng = random.Random(1)
for s in range(seeds):
    a = list(range(n)); rng.shuffle(a); b = [rng.randrange(n) for _ in range(n)]
    out.append(analyse([a, b], f"random perm + random map, seed {s}"))
for s in range(3):
    a = [rng.randrange(n) for _ in range(n)]; b = [rng.randrange(n) for _ in range(n)]
    out.append(analyse([a, b], f"two random maps, seed {s}"))
print(json.dumps(out, indent=1)); json.dump(out, open(f"probe_subset_automata_n{n}.json", "w"), indent=1)
