"""HT-5b0b3ebb8d / W4 Pass 4 attacks R and ALT. See NOTES.md (written first).

Writes rows.jsonl: one row per (attack, arm, seed), flushed per row. Prints
no treatment statistic. ORIG is a re-analysis (evaluate.py) of round-1 rows
and of the R rows written here.
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True  # never write __pycache__ into the round-1 directory

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.dirname(HERE)
sys.path.insert(0, R1)
import world as w1  # noqa: E402  round-1 world, imported unchanged

ROWS = os.path.join(HERE, "rows.jsonl")
R_SEEDS = list(range(100, 160))
ALT_SEEDS = list(range(200, 260))
R_PARAMS = dict(w1.PARAMS, attack="R", seeds=[R_SEEDS[0], R_SEEDS[-1]],
                rng="default_rng(1000+seed)", null_twin_rng=777)
ALT_PARAMS = dict(w1.PARAMS, attack="ALT", seeds=[ALT_SEEDS[0], ALT_SEEDS[-1]],
                  rng="default_rng(1000+seed)",
                  world_change="interior states 1..6: +1 out-edge to bg, +1 in-edge from bg; redraw Dirichlet for changed states",
                  shift="remove 4 chain transitions of disabled mechanism (states kept)",
                  fail_rule="any transition of supporting path (BFS shortest in true pre-shift world) removed",
                  null_twin="remove 4 true transitions uniformly at random, default_rng(900000+seed)",
                  strata="visit decile x supporting-path length")


# ---------------------------------------------------------------- R
def run_R(write):
    per_seed = {}
    for seed in R_SEEDS:
        treat, pc, ctx = w1.run_seed(seed)
        per_seed[seed] = (treat, ctx)
        base = dict(attack="R", params=R_PARAMS, seed=seed, **ctx)
        write(dict(arm="TREATMENT", beliefs=treat, **base))
        write(dict(arm="POSITIVE_CONTROL", beliefs=pc, **base))
        write(dict(arm="CHEAT", beliefs=[dict(b, fail=b["lucky"], fail_true=b["fail"]) for b in treat],
                   cheat="fail := lucky", **base))
    # NULL_TWIN: round-1 procedure (permute lucky within pooled visit decile, rng 777)
    allb = [(seed, i, b) for seed in R_SEEDS for i, b in enumerate(per_seed[seed][0])]
    vals = np.array([b["visit"] for _, _, b in allb])
    edges = np.quantile(vals, np.linspace(0.1, 0.9, 9))
    dec = np.searchsorted(edges, vals, side="right")
    rng = np.random.default_rng(777)
    newflag = np.array([b["lucky"] for _, _, b in allb])
    for d in np.unique(dec):
        ix = np.where(dec == d)[0]
        newflag[ix] = rng.permutation(newflag[ix])
    nt = {seed: [] for seed in R_SEEDS}
    for k, (seed, i, b) in enumerate(allb):
        nt[seed].append(dict(b, lucky=int(newflag[k]), lucky_orig=b["lucky"]))
    for seed in R_SEEDS:
        write(dict(attack="R", arm="NULL_TWIN", beliefs=nt[seed], params=R_PARAMS, seed=seed,
                   null_twin_deciles=edges.tolist(), **per_seed[seed][1]))


# ---------------------------------------------------------------- ALT
def build_alt_world(rng):
    world, probs = w1.build_world(rng)
    bg = w1.PARAMS["background"]
    changed = set()
    for i in range(1, 7):
        b = int(rng.choice(bg))
        world[i].append(b)
        changed.add(i)
        cand = [x for x in bg if i not in world[x]]
        src = int(rng.choice(cand))
        world[src].append(i)
        changed.add(src)
    for s in sorted(changed):
        wts = rng.dirichlet([w1.PARAMS["dirichlet_alpha"]] * len(world[s]))
        probs[s] = (list(world[s]), wts)
    return world, probs


def run_alt_seed(seed):
    P = w1.PARAMS
    rng = np.random.default_rng(P["seed_base"] + seed)
    world, probs = build_alt_world(rng)
    traces = w1.sample_traces(rng, probs)
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
    removed_T = set(w1.chain_edges(dchain))
    interior_all = [1, 2, 3, 4, 5, 6]
    dinterior = dchain[1:-1]
    shifted_T = {a: [b for b in bs if (a, b) not in removed_T] for a, bs in world.items()}

    pairs = [(s, t) for s in range(P["n_states"]) for t in range(P["n_states"]) if s != t]
    idx = rng.choice(len(pairs), size=P["n_formulas"], replace=False)
    formulas = [pairs[i] for i in idx]

    def support(s, t):
        return w1.bfs_path(world, s, t)

    # planted cases (positive control): s->t not a true transition, supporting path uses a removed transition
    cand = []
    for (s, t) in pairs:
        if (s, t) in true_edges:
            continue
        sp = support(s, t)
        if sp is None:
            continue
        if any(e in removed_T for e in zip(sp[:-1], sp[1:])):
            cand.append((s, t))
    k = min(P["n_planted"], len(cand))
    pick = rng.choice(len(cand), size=k, replace=False) if k else []
    planted = [cand[int(i)] for i in pick]

    # null twin shift: same count, uniform over all true transitions
    nrng = np.random.default_rng(900000 + seed)
    te_sorted = sorted(true_edges)
    nix = nrng.choice(len(te_sorted), size=len(removed_T), replace=False)
    removed_N = {te_sorted[int(i)] for i in nix}
    shifted_N = {a: [b for b in bs if (a, b) not in removed_N] for a, bs in world.items()}

    def beliefs_for(model_edges_x, formula_list, planted_set, removed, shifted):
        adj = {}
        for a, b in model_edges_x:
            adj.setdefault(a, []).append(b)
        out = []
        for (s, t) in formula_list:
            true_pre = w1.reachable(world, s, t)
            verified = w1.reachable(adj, s, t)
            if not (true_pre and verified):
                continue
            path = w1.bfs_path(adj, s, t)
            pedges = list(zip(path[:-1], path[1:]))
            sp = support(s, t)
            spedges = list(zip(sp[:-1], sp[1:]))
            grounded = w1.contiguous_in(traces, path)
            out.append(dict(
                s=s, t=t, witness=path, support=sp, support_len=len(spedges), witness_len=len(pedges),
                lucky=int(not grounded),
                fail=int(any(e in removed for e in spedges)),
                reach_fail=int(not w1.reachable(shifted, s, t)),
                witness_hit=int(any(e in removed for e in pedges)),
                visit=float(np.mean(visits[path])),
                uses_abduced=int(any(e not in observed for e in pedges)),
                uses_fabricated=int(any(e not in true_edges for e in pedges)),
                endpoint_in_disabled=int(s in dinterior or t in dinterior),
                endpoint_in_mech_interior=int(s in interior_all or t in interior_all),
                planted=int((s, t) in planted_set),
            ))
        return out

    treat = beliefs_for(model_edges, formulas, set(), removed_T, shifted_T)
    null = beliefs_for(model_edges, formulas, set(), removed_N, shifted_N)
    pc_model = model_edges | set(planted)
    pc_forms = [f for f in formulas if f not in set(planted)] + planted
    pc = beliefs_for(pc_model, pc_forms, set(planted), removed_T, shifted_T)
    ctx = dict(disabled=disabled, removed_treatment=sorted([list(e) for e in removed_T]),
               removed_null=sorted([list(e) for e in removed_N]),
               n_observed_edges=len(observed), n_abduced=len(abduced), n_fabricated=len(fabricated),
               n_true_edges=len(true_edges), visits=visits.tolist(),
               world={str(k): v for k, v in world.items()},
               formulas=[list(f) for f in formulas], planted=[list(p) for p in planted],
               n_planted_candidates=len(cand))
    return treat, null, pc, ctx


def run_ALT(write):
    for seed in ALT_SEEDS:
        treat, null, pc, ctx = run_alt_seed(seed)
        base = dict(attack="ALT", params=ALT_PARAMS, seed=seed, **ctx)
        write(dict(arm="TREATMENT", beliefs=treat, **base))
        write(dict(arm="NULL_TWIN", beliefs=null, **base))
        write(dict(arm="POSITIVE_CONTROL", beliefs=pc, **base))
        write(dict(arm="CHEAT", beliefs=[dict(b, fail=b["lucky"], fail_true=b["fail"]) for b in treat],
                   cheat="fail := lucky", **base))


def main():
    t0 = time.process_time()
    if os.path.exists(ROWS):
        os.remove(ROWS)
    with open(ROWS, "w", encoding="utf-8") as f:
        def write(row):
            f.write(json.dumps(row) + "\n")
            f.flush()
        run_R(write)
        run_ALT(write)
        cpu = time.process_time() - t0
        write(dict(attack="_META", arm="_META", attack_cpu_seconds=cpu))
    print("attack cpu seconds", round(cpu, 2), "(no statistics printed here)")


if __name__ == "__main__":
    main()
