"""Cycle-2 carrier instrumentation (DESIGN_C2 s2).

Cycle 1 attributed mechanism by removing HIDDEN NODES, which cannot see
an output-node self-loop and cannot distinguish "this node matters" from
"this EDGE closes the loop that matters". Everything here is edge- and
SCC-aware, and every carrier class the substrate offers is named and cut
separately:

    RECUR  a directed cycle among alive nodes (self-loop or longer)
    KEEP   the leak coefficient (the DESIGNATED carrier)
    PLAST  plastic weights (R != 0)

Nothing here rewards or names a cognitive function; a carrier is a
syntactic feature of the graph whose removal is measurable.
"""
from __future__ import annotations

import numpy as np

from . import search as R
from . import substrate as S


# ----------------------------------------------------------------------
# inventory
# ----------------------------------------------------------------------

def sccs(pop: S.Population, p: int):
    """Non-trivial strongly connected components of organism p:
    lists of node indices with a cycle among them (a self-loop counts)."""
    C = S.closure(pop.select([p]))[0]
    A = S.adjacency(pop.select([p]))[0]
    n = pop.cfg.n
    seen = set()
    out = []
    for i in range(n):
        if i in seen or not pop.alive[p, i]:
            continue
        comp = [j for j in range(n) if pop.alive[p, j] and C[i, j] and C[j, i]]
        if not comp:
            comp = []
        if i not in comp:
            comp = [i] + comp if A[i, i] else comp
        if len(comp) > 1 or (len(comp) == 1 and A[comp[0], comp[0]]):
            out.append(sorted(comp))
            seen.update(comp)
        elif A[i, i]:
            out.append([i]); seen.add(i)
    return out


def inventory(genome):
    pop = S.Population.from_genomes([genome])
    n = pop.cfg.n
    d = np.arange(n)
    A = S.adjacency(pop)[0]
    rec = S.recurrent_edge_mask(pop)[0]
    comps = sccs(pop, 0)
    return dict(
        n_hidden=int((pop.alive[0, S.OBS_DIM:n - S.N_OUT]).sum()),
        n_edges=int(A.sum()),
        self_loops=int((A[d, d] & pop.alive[0]).sum()),
        self_loops_on_output=int(sum(1 for i in range(n - S.N_OUT, n) if A[i, i])),
        recurrent_edges=int(rec.sum()),
        n_scc=len(comps), scc_sizes=[len(c) for c in comps],
        scc_nodes=[[int(x) for x in c] for c in comps],
        keep_nodes=int(((pop.keep[0] > 0.05) & pop.alive[0]).sum()),
        max_keep=float(pop.keep[0][pop.alive[0]].max()) if pop.alive[0].any() else 0.0,
        plastic_edges=int(((pop.R[0] != 0) & A).sum()),
    )


# ----------------------------------------------------------------------
# edge- and SCC-aware ablation
# ----------------------------------------------------------------------

def _cut(pop, which):
    q = pop.copy()
    n = q.cfg.n
    d = np.arange(n)
    if which == "self_loops":
        q.W1[0, d, d] = 0; q.W2[0, d, d] = 0; q.R[0, d, d] = 0
    elif which == "recurrent":
        m = S.recurrent_edge_mask(pop)[0]
        q.W1[0][m] = 0; q.W2[0][m] = 0; q.R[0][m] = 0
    elif which == "keep":
        q.keep[:] = 0
    elif which == "plasticity":
        q.R[:] = 0
    return q


def carrier_ablation(genome, world_name, mode, seeds, floor=0.0):
    """Intact plus one evaluation per carrier class cut, per SCC cut and
    per recurrent edge cut. Returns a JSON-able dict."""
    pop = S.Population.from_genomes([genome])
    world = R.make_world(world_name, mode)
    base = float(R.rollout(pop, world, seeds)[0])
    out = dict(base=base, inventory=inventory(genome))
    for which in ("self_loops", "recurrent", "keep", "plasticity"):
        out["cut_" + which] = float(R.rollout(_cut(pop, which), world, seeds)[0])
    # every cross-step channel at once
    q = _cut(_cut(pop, "recurrent"), "plasticity"); q.keep[:] = 0
    c2 = S.Config(**{**genome["cfg"], "allow_keep": False, "reset_each_step": True, "allow_plasticity": False})
    out["cut_all"] = float(R.rollout(S.Population.from_genomes([genome], c2), world, seeds)[0])
    # per SCC
    comps = sccs(pop, 0)
    scc_rows = []
    for comp in comps:
        q = pop.copy()
        idx = np.array(comp)
        q.W1[0][np.ix_(idx, idx)] = 0; q.W2[0][np.ix_(idx, idx)] = 0; q.R[0][np.ix_(idx, idx)] = 0
        f = float(R.rollout(q, world, seeds)[0])
        scc_rows.append(dict(nodes=[int(x) for x in comp], size=len(comp),
                             has_output=bool(any(x >= pop.cfg.n - S.N_OUT for x in comp)),
                             fit=f, delta=f - base))
    out["scc_ablation"] = scc_rows
    # per recurrent edge
    m = S.recurrent_edge_mask(pop)[0]
    edge_rows = []
    for i, j in np.argwhere(m):
        q = pop.copy()
        q.W1[0, i, j] = 0; q.W2[0, i, j] = 0; q.R[0, i, j] = 0
        f = float(R.rollout(q, world, seeds)[0])
        edge_rows.append(dict(src=int(j), dst=int(i), self_loop=bool(i == j),
                              on_output=bool(i >= pop.cfg.n - S.N_OUT), fit=f, delta=f - base))
    out["recurrent_edge_ablation"] = edge_rows
    gain = max(base - floor, 1e-9)
    coll = lambda v: (v - floor) <= 0.25 * gain
    out["collapses"] = {k: bool(coll(out["cut_" + k])) for k in ("self_loops", "recurrent", "keep", "plasticity")}
    out["collapses"]["all"] = bool(coll(out["cut_all"]))
    out["carrier_class"] = classify(out, floor)
    out["load_bearing_edges"] = [e for e in edge_rows if e["delta"] <= -0.25 * gain]
    return out


def classify(abl, floor):
    """Which carrier class is load-bearing. AT_FLOOR when there is no
    gain to attribute; NONE when no cross-step cut collapses it."""
    base = abl["base"]
    c = abl["collapses"]
    if not c["all"]:
        return "NONE"
    live = [k for k in ("recurrent", "keep", "plasticity") if c[k]]
    if not live:
        return "REDUNDANT"
    if len(live) == 1:
        return {"recurrent": "RECUR", "keep": "KEEP", "plasticity": "PLAST"}[live[0]]
    return "MIXED:" + "+".join(sorted(live))


# ----------------------------------------------------------------------
# mutational opportunity (the denominator cycle 1 lacked)
# ----------------------------------------------------------------------

def opportunity(cfg: S.Config, n_trials=4000, seed=0, base_pop=None):
    """P(a single mutation CREATES each carrier, given it is absent).
    Measured on the substrate the GA actually uses: draw a random
    organism, strip its carriers, apply ONE mutation, look."""
    rng = np.random.default_rng(seed)
    created = dict(recurrent=0, keep=0, plasticity=0)
    eligible = dict(recurrent=0, keep=0, plasticity=0)
    mut_counts = {}
    for _ in range(n_trials):
        pop = base_pop.copy() if base_pop is not None else S.random_population(cfg, 1, rng)
        n = cfg.n
        d = np.arange(n)
        pop.W1[0, d, d] = 0; pop.W2[0, d, d] = 0; pop.R[0, d, d] = 0
        S.strip_cycles(pop, 0, rng)
        pop.keep[:] = 0
        pop.R[:] = 0
        before = dict(recurrent=int(S.n_recurrent_edges(pop)[0]),
                      keep=int((pop.keep[0] > 0.05).sum()), plasticity=int((pop.R[0] != 0).sum()))
        for k in eligible:
            if before[k] == 0:
                eligible[k] += 1
        muts = S.mutate_one(pop, 0, rng, n_mut=1)
        for m in muts:
            mut_counts[m] = mut_counts.get(m, 0) + 1
        after = dict(recurrent=int(S.n_recurrent_edges(pop)[0]),
                     keep=int((pop.keep[0] > 0.05).sum()), plasticity=int((pop.R[0] != 0).sum()))
        for k in created:
            if before[k] == 0 and after[k] > 0:
                created[k] += 1
    return dict(n_trials=n_trials, created=created, eligible=eligible,
                p_create={k: created[k] / max(eligible[k], 1) for k in created},
                mutation_draws=mut_counts, cfg=cfg.to_dict())


def single_mutation_gradient(genome, world_name, mode, seeds, floor=0.0, n=300, seed=0):
    """Fitness effect of ONE mutation applied to a carrier-stripped
    champion, split by whether that mutation created a carrier. Answers
    'what gradient does each carrier offer at the moment it appears'."""
    rng = np.random.default_rng(seed)
    world = R.make_world(world_name, mode)
    stripped = _cut(_cut(_cut(S.Population.from_genomes([genome]), "recurrent"), "keep"), "plasticity")
    f0 = float(R.rollout(stripped, world, seeds)[0])
    rows = []
    for _ in range(n):
        q = stripped.copy()
        muts = S.mutate_one(q, 0, rng, n_mut=1)
        inv_rec = int(S.n_recurrent_edges(q)[0])
        inv_keep = int((q.keep[0] > 0.05).sum())
        inv_plast = int((q.R[0] != 0).sum())
        f = float(R.rollout(q, world, seeds)[0])
        rows.append(dict(mut=muts, d=f - f0, made_recur=inv_rec > 0, made_keep=inv_keep > 0, made_plast=inv_plast > 0))
    def summ(key):
        v = [r["d"] for r in rows if r[key]]
        return dict(n=len(v), mean=float(np.mean(v)) if v else None, max=float(np.max(v)) if v else None,
                    p_improve=float(np.mean([x > 0.5 for x in v])) if v else None)
    return dict(stripped_fitness=f0, n=n,
                recur=summ("made_recur"), keep=summ("made_keep"), plast=summ("made_plast"),
                none=dict(n=sum(1 for r in rows if not (r["made_recur"] or r["made_keep"] or r["made_plast"])),
                          mean=float(np.mean([r["d"] for r in rows if not (r["made_recur"] or r["made_keep"] or r["made_plast"])] or [0.0]))))


# ----------------------------------------------------------------------
# edge-aware transplant and carrier swap (cycle-1 blind spot fixed)
# ----------------------------------------------------------------------

def splice_carrier(dst_pop, dp, src_genome, nodes, rng):
    """Move a carrier subcircuit, EDGES INCLUDED. Hidden nodes take free
    hidden slots; an OUTPUT node in the carrier maps onto the host's SAME
    output node (so an output self-loop actually moves -- cycle 1 could
    not do this). Input edges keep their channel. Returns the node map."""
    src = S.Population.from_genomes([src_genome])
    cfg = dst_pop.cfg
    n = cfg.n
    hid = [x for x in nodes if x < n - S.N_OUT]
    out = [x for x in nodes if x >= n - S.N_OUT]
    free = np.flatnonzero(~dst_pop.alive[dp, S.OBS_DIM:S.OBS_DIM + cfg.n_hidden]) + S.OBS_DIM
    if len(free) < len(hid):
        return None
    slots = rng.choice(free, size=len(hid), replace=False) if hid else []
    m = {int(s): int(d) for s, d in zip(hid, slots)}
    m.update({int(o): int(o) for o in out})
    for s, d in m.items():
        dst_pop.alive[dp, d] = True
        dst_pop.op[dp, d] = src.op[0, s]
        dst_pop.bias[dp, d] = src.bias[0, s]
        dst_pop.keep[dp, d] = src.keep[0, s]
    for s, d in m.items():
        for j in range(n):
            for A_s, A_d in ((src.W1, dst_pop.W1), (src.W2, dst_pop.W2), (src.R, dst_pop.R)):
                w = A_s[0, s, j]
                if w == 0:
                    continue
                if j in m:                      # internal edge (incl. self-loop)
                    A_d[dp, d, m[j]] = w
                elif j < S.OBS_DIM:             # input channel keeps its identity
                    A_d[dp, d, j] = w
                else:                           # external: re-attach at random
                    cand = np.flatnonzero(dst_pop.alive[dp])
                    A_d[dp, d, int(rng.choice(cand))] = w
        for i in range(n):
            if i in m:
                continue
            for A_s, A_d in ((src.W1, dst_pop.W1), (src.W2, dst_pop.W2), (src.R, dst_pop.R)):
                w = A_s[0, i, s]
                if w == 0:
                    continue
                if i >= n - S.N_OUT:
                    A_d[dp, i, d] = w
                else:
                    a = dst_pop.alive[dp].copy(); a[:S.OBS_DIM] = False
                    cand = np.flatnonzero(a)
                    if len(cand):
                        A_d[dp, int(rng.choice(cand)), d] = w
    return m


def random_carrier_like(genome, nodes, rng):
    """A fresh random subcircuit with the same node count, the same
    internal/input/output edge counts AND the same number of recurrent
    edges: the control for 'any subgraph would have helped'."""
    src = S.Population.from_genomes([genome])
    cfg = src.cfg
    n = cfg.n
    idx = np.array(nodes)
    n_int = int(((src.W1[0][np.ix_(idx, idx)] != 0) | (src.W2[0][np.ix_(idx, idx)] != 0)).sum())
    ins = np.arange(S.OBS_DIM)
    n_in = int(((src.W1[0][np.ix_(idx, ins)] != 0) | (src.W2[0][np.ix_(idx, ins)] != 0)).sum())
    outs = np.arange(n - S.N_OUT, n)
    n_out = int(((src.W1[0][np.ix_(outs, idx)] != 0) | (src.W2[0][np.ix_(outs, idx)] != 0)).sum())
    g = dict(cfg=dict(cfg.to_dict()), id=-1, parent=-1,
             alive=[1 if (i < S.OBS_DIM or i >= n - S.N_OUT or i in nodes) else 0 for i in range(n)],
             op=[S.OPS[int(rng.integers(0, S.N_OPS))] for _ in range(n)],
             bias=[float(rng.normal(0, 0.5)) for _ in range(n)],
             keep=[float(src.keep[0, i]) if i in nodes else 0.0 for i in range(n)],
             edges=[])
    pool = list(nodes)
    for _ in range(n_int):
        g["edges"].append([int(rng.choice(pool)), int(rng.choice(pool)), float(rng.normal(0, 1)), 0.0, 0.0])
    for _ in range(n_in):
        g["edges"].append([int(rng.integers(0, S.OBS_DIM)), int(rng.choice(pool)), float(rng.normal(0, 1)), 0.0, 0.0])
    for _ in range(n_out):
        g["edges"].append([int(rng.choice(pool)), int(rng.integers(n - S.N_OUT, n)), float(rng.normal(0, 1)), 0.0, 0.0])
    return g


def transplant(genome, nodes, world_name, mode, seeds, cfg, floor=0.0, n_hosts=64, seed=0):
    """Splice the carrier into naive hosts; compare with the matched
    random control. PORTABLE if the gap is >= 25% of the champion's gain."""
    rng = np.random.default_rng(seed)
    world = R.make_world(world_name, mode)
    base = float(R.rollout(S.Population.from_genomes([genome]), world, seeds)[0])
    hosts_e = S.random_population(cfg, n_hosts, rng)
    hosts_r = S.random_population(cfg, n_hosts, rng)
    ctrl = random_carrier_like(genome, nodes, rng)
    ok_e = ok_r = 0
    for i in range(n_hosts):
        if splice_carrier(hosts_e, i, genome, nodes, rng) is not None:
            ok_e += 1
        if splice_carrier(hosts_r, i, ctrl, nodes, rng) is not None:
            ok_r += 1
    fe = R.rollout(hosts_e, world, seeds)
    fr = R.rollout(hosts_r, world, seeds)
    return dict(nodes=[int(x) for x in nodes], champion=base, spliced_evolved=ok_e, spliced_random=ok_r,
                evolved_mean=float(fe.mean()), evolved_max=float(fe.max()), evolved_top10=float(np.sort(fe)[-max(1, n_hosts // 10):].mean()),
                random_mean=float(fr.mean()), random_max=float(fr.max()), random_top10=float(np.sort(fr)[-max(1, n_hosts // 10):].mean()),
                gap=float(fe.mean() - fr.mean()),
                portable=bool((fe.mean() - fr.mean()) >= 0.25 * max(base - floor, 1e-9)))


def swap(host_genome, donor_genome, host_nodes, donor_nodes, world_name, mode, seeds, floor=0.0, seed=0):
    """Remove the host champion's own carrier, then graft the donor's.
    Does memory function follow the machinery between two independently
    evolved lineages?"""
    rng = np.random.default_rng(seed)
    world = R.make_world(world_name, mode)
    intact = float(R.rollout(S.Population.from_genomes([host_genome]), world, seeds)[0])
    cut = _cut(S.Population.from_genomes([host_genome]), "recurrent")
    cut.keep[:] = 0
    f_cut = float(R.rollout(cut, world, seeds)[0])
    grafted = cut.copy()
    # free the donor's hidden slots in the host before splicing
    m = splice_carrier(grafted, 0, donor_genome, donor_nodes, rng)
    f_graft = float(R.rollout(grafted, world, seeds)[0]) if m is not None else None
    rec = None
    if f_graft is not None and (intact - f_cut) > 1e-9:
        rec = (f_graft - f_cut) / (intact - f_cut)
    return dict(host_intact=intact, host_carrier_cut=f_cut, after_graft=f_graft,
                recovery_fraction=rec, spliced=m is not None)
