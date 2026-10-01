"""HT-5b0b3ebb8d / W4 world. See IMPLEMENTATION_NOTES.md (written first).

Writes rows.jsonl (one JSON object per (arm, seed)), flushed per row.
"""
import json
import os
import time
from collections import deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

PARAMS = dict(
    n_states=16, start=0, goal=15,
    mech_A=[0, 1, 2, 3, 15], mech_B=[0, 4, 5, 6, 15],
    background=list(range(7, 15)),
    n_traces=80, trace_len=20, n_formulas=30, n_seeds=60, seed_base=1000,
    n_planted=5, null_twin_rng=777, abduction="reverse_of_observed",
    witness="bfs_shortest_lowest_index", grounding="contiguous_in_some_trace",
    visit_covariate="mean_visits_on_witness_states", dirichlet_alpha=1.0,
)


def chain_edges(chain):
    return [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]


def build_world(rng):
    P = PARAMS
    out = {s: [] for s in range(P["n_states"])}
    for ch in (P["mech_A"], P["mech_B"]):
        for a, b in chain_edges(ch):
            out[a].append(b)
    bg = P["background"]
    ring = [0] + bg
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        out[a].append(b)
    pool = [0] + bg
    for s in bg:
        cand = [x for x in pool if x != s and x not in out[s]]
        out[s].append(int(rng.choice(cand)))
    cand = [x for x in bg if x not in out[0]]
    out[0].append(int(rng.choice(cand)))
    out[P["goal"]].append(0)
    probs = {}
    for s, succ in out.items():
        w = rng.dirichlet([P["dirichlet_alpha"]] * len(succ))
        probs[s] = (list(succ), w)
    return out, probs


def sample_traces(rng, probs):
    P = PARAMS
    traces = []
    for _ in range(P["n_traces"]):
        s = P["start"]
        tr = [s]
        for _ in range(P["trace_len"]):
            succ, w = probs[s]
            s = int(succ[rng.choice(len(succ), p=w)])
            tr.append(s)
        traces.append(tr)
    return traces


def reachable(adj, s, t):
    seen = {s}
    dq = deque([s])
    while dq:
        u = dq.popleft()
        for v in adj.get(u, ()):
            if v == t:
                return True
            if v not in seen:
                seen.add(v)
                dq.append(v)
    return False


def bfs_path(adj, s, t):
    prev = {s: None}
    dq = deque([s])
    while dq:
        u = dq.popleft()
        for v in sorted(adj.get(u, ())):
            if v not in prev:
                prev[v] = u
                if v == t:
                    path = [t]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    return path[::-1]
                dq.append(v)
    return None


def contiguous_in(traces, path):
    k = len(path)
    for tr in traces:
        for i in range(len(tr) - k + 1):
            if tr[i:i + k] == path:
                return True
    return False


def run_seed(seed):
    P = PARAMS
    rng = np.random.default_rng(P["seed_base"] + seed)
    world, probs = build_world(rng)
    traces = sample_traces(rng, probs)
    true_edges = {(a, b) for a, bs in world.items() for b in bs}
    observed = set()
    for tr in traces:
        for i in range(len(tr) - 1):
            observed.add((tr[i], tr[i + 1]))
    abduced = {(b, a) for (a, b) in observed if (b, a) not in observed}
    fabricated = {e for e in abduced if e not in true_edges}
    model_edges = observed | abduced
    visits = np.zeros(P["n_states"], dtype=int)
    for tr in traces:
        for s in tr:
            visits[s] += 1

    disabled = "A" if rng.random() < 0.5 else "B"
    dchain = P["mech_A"] if disabled == "A" else P["mech_B"]
    dedges = set(chain_edges(dchain))
    dinterior = dchain[1:-1]
    shifted = {a: [b for b in bs if (a, b) not in dedges] for a, bs in world.items()}

    pairs = [(s, t) for s in range(P["n_states"]) for t in range(P["n_states"]) if s != t]
    idx = rng.choice(len(pairs), size=P["n_formulas"], replace=False)
    formulas = [pairs[i] for i in idx]

    # planted cases for POSITIVE_CONTROL
    psrc = rng.choice(P["background"], size=P["n_planted"], replace=False)
    ptgt = rng.choice(dinterior, size=P["n_planted"], replace=True)
    planted = [(int(a), int(b)) for a, b in zip(psrc, ptgt)]

    def beliefs_for(model_edges_x, formula_list, planted_set):
        adj = {}
        for a, b in model_edges_x:
            adj.setdefault(a, []).append(b)
        out = []
        for (s, t) in formula_list:
            true_pre = reachable(world, s, t)
            verified = reachable(adj, s, t)
            if not (true_pre and verified):
                continue
            path = bfs_path(adj, s, t)
            pedges = list(zip(path[:-1], path[1:]))
            grounded = contiguous_in(traces, path)
            fail = not reachable(shifted, s, t)
            out.append(dict(
                s=s, t=t, witness=path, lucky=int(not grounded), fail=int(fail),
                visit=float(np.mean(visits[path])),
                uses_abduced=int(any(e not in observed for e in pedges)),
                uses_fabricated=int(any(e not in true_edges for e in pedges)),
                touches_disabled=int(any(x in dinterior for x in path)),
                planted=int((s, t) in planted_set),
            ))
        return out

    treat = beliefs_for(model_edges, formulas, set())
    pc_model = model_edges | set(planted)
    pc_forms = [f for f in formulas if f not in set(planted)] + planted
    pc = beliefs_for(pc_model, pc_forms, set(planted))
    ctx = dict(disabled=disabled, n_observed_edges=len(observed),
               n_abduced=len(abduced), n_fabricated=len(fabricated),
               n_true_edges=len(true_edges), visits=visits.tolist(),
               formulas=[list(f) for f in formulas], planted=[list(p) for p in planted])
    return treat, pc, ctx


def main():
    t0 = time.process_time()
    if os.path.exists(ROWS):
        os.remove(ROWS)
    per_seed = {}
    with open(ROWS, "w", encoding="utf-8") as f:
        def w(row):
            f.write(json.dumps(row) + "\n")
            f.flush()
        for seed in range(PARAMS["n_seeds"]):
            treat, pc, ctx = run_seed(seed)
            per_seed[seed] = (treat, ctx)
            base = dict(params=PARAMS, seed=seed, **ctx)
            w(dict(arm="TREATMENT", beliefs=treat, **base))
            w(dict(arm="CONTROL", beliefs=[dict(b, lucky=None, lucky_ignored=b["lucky"]) for b in treat], **base))
            w(dict(arm="POSITIVE_CONTROL", beliefs=pc, **base))
            w(dict(arm="CHEAT", beliefs=[dict(b, fail=b["lucky"], fail_true=b["fail"]) for b in treat],
                   cheat="fail := lucky", **base))
        # NULL_TWIN: permute lucky flags within pooled visit decile across seeds
        allb = [(seed, i, b) for seed in range(PARAMS["n_seeds"]) for i, b in enumerate(per_seed[seed][0])]
        vals = np.array([b["visit"] for _, _, b in allb])
        edges = np.quantile(vals, np.linspace(0.1, 0.9, 9))
        dec = np.searchsorted(edges, vals, side="right")
        rng = np.random.default_rng(PARAMS["null_twin_rng"])
        newflag = np.array([b["lucky"] for _, _, b in allb])
        for d in np.unique(dec):
            ix = np.where(dec == d)[0]
            newflag[ix] = rng.permutation(newflag[ix])
        nt = {seed: [] for seed in range(PARAMS["n_seeds"])}
        for k, (seed, i, b) in enumerate(allb):
            nt[seed].append(dict(b, lucky=int(newflag[k]), lucky_orig=b["lucky"]))
        for seed in range(PARAMS["n_seeds"]):
            ctx = per_seed[seed][1]
            w(dict(arm="NULL_TWIN", beliefs=nt[seed], params=PARAMS, seed=seed,
                   null_twin_deciles=edges.tolist(), **ctx))
        cpu = time.process_time() - t0
        w(dict(arm="_META", world_cpu_seconds=cpu))
    print("world cpu seconds", round(cpu, 2))


if __name__ == "__main__":
    main()
