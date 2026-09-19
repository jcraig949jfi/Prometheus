"""Ares search: rollouts, a plain mutation-selection GA, per-generation
measures, ancestry, dissection and receipts. The optimizer is
deliberately dumb (truncation + tournament + elitism); it carries none of
the capability under study.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time

import numpy as np

from . import substrate as S
from .worlds import WORLDS, W9MatchingPennies

def _balanced_eval_seeds(n_per_side=16, start=10_000):
    """Held-out episode seeds chosen so the first binary draw (W4 regime,
    W5 token, W11 truth share it) is exactly balanced. Deterministic."""
    zeros, ones, s = [], [], start
    while len(zeros) < n_per_side or len(ones) < n_per_side:
        b = int(np.random.default_rng(s).integers(0, 2))
        (ones if b else zeros).append(s)
        s += 1
    return sorted(zeros[:n_per_side] + ones[:n_per_side])


EVAL_SEEDS = _balanced_eval_seeds()   # 32 held-out episodes, fixed for every run


# ----------------------------------------------------------------------
# rollouts
# ----------------------------------------------------------------------

def rollout(pop: S.Population, world, seeds, record=False):
    """Mean lifetime reward per organism over `seeds` episodes. With
    record=True also returns traces (actions, rewards, per-step info)."""
    rt = S.Runtime(pop)
    P = pop.P
    total = np.zeros(P, dtype=np.float64)
    traces = dict(actions=[], rewards=[], info=[]) if record else None
    for sd in seeds:
        rng = np.random.default_rng(sd)
        rt.reset()
        obs = world.reset(rng, P)
        acts = np.zeros((world.T, P), dtype=np.int8) if record else None
        rews = np.zeros((world.T, P), dtype=np.float32) if record else None
        infos = [] if record else None
        alive = np.ones(P, dtype=bool)
        for t in range(world.T):
            a = rt.step(obs)
            obs, r, alive_now, info = world.step(a)
            r = np.where(alive, r, 0.0)
            total += r
            alive = alive & alive_now
            if record:
                acts[t] = a; rews[t] = r; infos.append(info)
        if record:
            traces["actions"].append(acts); traces["rewards"].append(rews); traces["info"].append(infos)
    fit = total / len(seeds)
    return (fit, traces) if record else fit


def rollout_two_sided(popA: S.Population, popB, world: W9MatchingPennies, seeds, rng_pair):
    """W9. popB may be None (static opponent from the world's mode)."""
    rtA = S.Runtime(popA)
    rtB = S.Runtime(popB) if popB is not None else None
    P = popA.P
    totA = np.zeros(P); totB = np.zeros(popB.P) if popB is not None else None
    choiceA = np.zeros(P)
    for sd in seeds:
        rng = np.random.default_rng(sd)
        rtA.reset()
        obsA, obsB = world.reset(rng, P)
        if rtB is not None:
            rtB.reset()
            perm = rng_pair.permutation(popB.P)[:P]
        for t in range(world.T):
            aA = rtA.step(obsA)
            if rtB is not None:
                aB_full = rtB.step(obsB[np.argsort(perm)] if popB.P == P else obsB)
                aB = aB_full[perm] if popB.P == P else aB_full
            else:
                aB = world.static_b()
            obsA, obsB_next, rA, rB = world.step(aA, aB)
            totA += rA
            choiceA += (np.where(aA == 0, 1, aA) == 1)
            if rtB is not None:
                totB[perm] += rB
                obsB = obsB_next[np.argsort(perm)] if popB.P == P else obsB_next
    n = len(seeds)
    return totA / n, (totB / n if totB is not None else None), choiceA / (n * world.T)


# ----------------------------------------------------------------------
# GA
# ----------------------------------------------------------------------

def make_world(name, mode):
    if name == "W6":            # scarcity uses W3's task
        return WORLDS["W3"](mode)
    if name == "W9":
        return W9MatchingPennies(mode)
    return WORLDS[name](mode)


def _behaviour_stats(actions):
    """actions: (S, T, P) -> per-organism action histogram entropy (P,)
    and mean pairwise L1 between histograms (behavioural diversity)."""
    S_, T, P = actions.shape
    flat = actions.transpose(2, 0, 1).reshape(P, -1)
    hist = np.stack([(flat == k).mean(1) for k in range(3)], axis=1)
    ent = -(hist * np.log(hist + 1e-9)).sum(1)
    idx = np.arange(min(P, 32))
    h = hist[idx]
    div = np.abs(h[:, None, :] - h[None, :, :]).sum(-1)
    return ent, float(div[np.triu_indices(len(idx), 1)].mean()) if len(idx) > 1 else 0.0


def _random_subgraph_like(src_pop, nodes, rng):
    """A fresh random subgraph with the same node count and internal edge
    count as `nodes` in src_pop (the W8 shuffled control)."""
    k = len(nodes)
    tmp = S.Population(src_pop.cfg, 1)
    hs = np.arange(S.OBS_DIM, S.OBS_DIM + k)
    tmp.alive[0, hs] = True
    tmp.op[0, hs] = rng.integers(0, S.N_OPS, size=k)
    tmp.bias[0, hs] = rng.normal(0, 0.5, size=k)
    tmp.keep[0, hs] = src_pop.keep[0, nodes]                     # same keep profile, permuted
    n_int = int(((src_pop.W1[0][np.ix_(nodes, nodes)] != 0) | (src_pop.W2[0][np.ix_(nodes, nodes)] != 0)).sum())
    n_in = int(((src_pop.W1[0][np.ix_(nodes, np.arange(S.OBS_DIM))] != 0) | (src_pop.W2[0][np.ix_(nodes, np.arange(S.OBS_DIM))] != 0)).sum())
    outs = np.arange(src_pop.cfg.n - S.N_OUT, src_pop.cfg.n)
    n_out = int(((src_pop.W1[0][np.ix_(outs, nodes)] != 0) | (src_pop.W2[0][np.ix_(outs, nodes)] != 0)).sum())
    for _ in range(n_int):
        i, j = rng.choice(hs), rng.choice(hs)
        (tmp.W1 if rng.random() < 0.5 else tmp.W2)[0, i, j] = rng.normal(0, 1.0)
    for _ in range(n_in):
        (tmp.W1 if rng.random() < 0.5 else tmp.W2)[0, rng.choice(hs), rng.integers(0, S.OBS_DIM)] = rng.normal(0, 1.0)
    for _ in range(n_out):
        (tmp.W1 if rng.random() < 0.5 else tmp.W2)[0, rng.choice(outs), rng.choice(hs)] = rng.normal(0, 1.0)
    return tmp, list(hs)


def _do_transplant(pop, src_pop, src_nodes, frac, rng, random_control):
    """Splice a subgraph into `frac` of the non-elite population. Returns
    the list of (recipient, slots, ops) signatures."""
    P = pop.P
    recips = rng.choice(np.arange(P // 8, P), size=max(1, int(frac * P)), replace=False)
    sigs = []
    for r in recips:
        if random_control:
            s_pop, s_nodes = _random_subgraph_like(src_pop, src_nodes, rng)
        else:
            s_pop, s_nodes = src_pop, src_nodes
        slots = S.splice_subgraph(pop, int(r), s_pop, 0, s_nodes, rng)
        if slots is None:
            continue
        sigs.append((tuple(slots), tuple(int(pop.op[r, x]) for x in slots)))
    return sigs


def _carriers(pop, sigs):
    """Fraction of the population carrying at least one transplant signature
    (all slots alive with the transplanted ops)."""
    if not sigs:
        return 0.0
    carry = np.zeros(pop.P, dtype=bool)
    for slots, ops in sigs:
        ok = np.ones(pop.P, dtype=bool)
        for x, o in zip(slots, ops):
            ok &= pop.alive[:, x] & (pop.op[:, x] == o)
        carry |= ok
    return float(carry.mean())


def run(world_name, mode, cfg: S.Config, P=128, G=120, eps=4, seed=0,
        log_every=5, tag=None, elite_frac=0.125, verbose=False, transplant=None):
    """One GA run. Returns a JSON-able dict with the log, champion genome,
    champion ancestry and a receipt. `transplant` (W8 protocol): dict with
    source (genome), nodes (hidden node indices in the source), every
    (generations), frac (of the population), random_control (bool)."""
    t0 = time.time()
    rng = np.random.default_rng(seed)
    world = make_world(world_name, mode)
    pop = S.random_population(cfg, P, rng)
    tp_log = []
    tp_sigs = []
    if transplant is not None:
        src_pop = S.Population.from_genomes([transplant["source"]])
        src_nodes = [int(x) for x in transplant["nodes"]]
    next_id = P
    ancestry = {int(i): dict(parent=-1, gen=0, mut=[]) for i in pop.ids}
    n_elite = max(1, int(P * elite_frac))
    log = []
    parent_fit = None
    best_ever = (-np.inf, None)
    for g in range(G):
        seeds = [int(x) for x in rng.integers(0, 2**31 - 1, size=eps)]
        fit, traces = rollout(pop, world, seeds, record=True)
        order = np.argsort(-fit)
        champ = int(order[0])
        # mutation survival: children whose fitness >= parent's - 5% of |parent|
        if parent_fit is not None:
            child = np.flatnonzero(pop.parents >= 0)
            pf = np.array([parent_fit.get(int(pop.parents[c]), np.nan) for c in child])
            ok = ~np.isnan(pf)
            msurv = float(np.mean(fit[child][ok] >= pf[ok] - 0.05 * np.abs(pf[ok]))) if ok.any() else float("nan")
        else:
            msurv = float("nan")
        if g % log_every == 0 or g == G - 1:
            ho = rollout(pop.select([champ]), world, EVAL_SEEDS)[0]
            st = S.structure_stats(pop)
            ent, bdiv = _behaviour_stats(np.stack(traces["actions"]))
            row = dict(gen=g, best_train=float(fit[champ]), mean_train=float(fit.mean()),
                       champ_heldout=float(ho), mutation_survival=msurv,
                       struct_div=S.structural_diversity(pop, rng), behav_div=bdiv,
                       champ_entropy=float(ent[champ]),
                       champ=dict(id=int(pop.ids[champ]), **{k: (int(v[champ]) if v.ndim == 1 and v.dtype.kind in "iu" else
                                                              (float(v[champ]) if v.ndim == 1 else [int(x) for x in v[champ]]))
                                                            for k, v in st.items()}),
                       pop_mean=dict(**{k: float(v.mean()) for k, v in st.items() if v.ndim == 1}))
            log.append(row)
            if verbose:
                print(f"{world_name}/{mode} g{g:3d} train {fit[champ]:8.2f} held {ho:8.2f} mean {fit.mean():8.2f} "
                      f"hid {st['n_hidden'][champ]} edges {st['n_edges'][champ]} keep {st['n_keep'][champ]} cyc {st['n_cyclic'][champ]}")
            if ho > best_ever[0]:
                best_ever = (float(ho), pop.genome(champ))
        if transplant is not None and g > 0 and g % transplant["every"] == 0:
            ret = _carriers(pop, tp_sigs) if tp_sigs else float("nan")
            tp_sigs = _do_transplant(pop, src_pop, src_nodes, transplant["frac"], rng, transplant["random_control"])
            tp_log.append(dict(gen=g, retained_from_previous=ret, n_recipients=len(tp_sigs)))
        # next generation
        parent_fit = {int(pop.ids[i]): float(fit[i]) for i in range(P)}
        elite_idx = order[:n_elite]
        new = pop.select(list(elite_idx) + [0] * (P - n_elite))
        new.parents[:n_elite] = -1     # elites are not children this generation
        half = order[: max(2, P // 2)]
        for k in range(n_elite, P):
            cands = rng.choice(half, size=3)
            par = int(cands[np.argmax(fit[cands])])
            src = pop.select([par])
            for name in ("alive", "op", "bias", "keep", "W1", "W2", "R"):
                getattr(new, name)[k] = getattr(src, name)[0]
            muts = S.mutate_one(new, k, rng)
            new.ids[k] = next_id; new.parents[k] = pop.ids[par]
            ancestry[next_id] = dict(parent=int(pop.ids[par]), gen=g + 1, mut=muts)
            next_id += 1
        pop = new
    # final champion on held-out
    fit = rollout(pop, world, EVAL_SEEDS)
    champ = int(np.argmax(fit))
    final = dict(heldout=float(fit[champ]), genome=pop.genome(champ))
    chain = []
    i = int(pop.ids[champ])
    while i in ancestry and len(chain) < 10_000:
        a = ancestry[i]
        chain.append(dict(id=i, parent=a["parent"], gen=a["gen"], mut=a["mut"]))
        i = a["parent"]
    if transplant is not None:
        tp_log.append(dict(gen=G, retained_from_previous=_carriers(pop, tp_sigs) if tp_sigs else float("nan"), n_recipients=0))
    return dict(world=world_name, mode=mode, cfg=cfg.to_dict(), P=P, G=G, eps=eps, seed=seed, tag=tag,
                log=log, final=final, best_ever=dict(heldout=best_ever[0], genome=best_ever[1]),
                ancestry=chain, transplant_log=tp_log, elapsed_s=time.time() - t0,
                receipt=receipt(cfg, world_name, mode, P, G, eps, seed))


def run_coevo(mode, cfg: S.Config, P=128, G=120, eps=4, seed=0, log_every=5, tag=None, elite_frac=0.125, verbose=False):
    """W9: two populations, A rewarded for matching, B for mismatching.
    absent/shuffled: B is static and only A evolves."""
    t0 = time.time()
    rng = np.random.default_rng(seed)
    world = W9MatchingPennies(mode)
    popA = S.random_population(cfg, P, rng)
    popB = S.random_population(cfg, P, rng, next_id=P) if mode == "present" else None
    n_elite = max(1, int(P * elite_frac))
    log = []
    choice_series = []
    ids = 2 * P
    for g in range(G):
        seeds = [int(x) for x in rng.integers(0, 2**31 - 1, size=eps)]
        fA, fB, chA = rollout_two_sided(popA, popB, world, seeds, rng)
        choice_series.append(float(chA.mean()))
        if g % log_every == 0 or g == G - 1:
            st = S.structure_stats(popA)
            c = int(np.argmax(fA))
            hoA = rollout_two_sided(popA.select([c]), popB, world, EVAL_SEEDS, rng)[0][0] if popB is None else float(fA[c])
            row = dict(gen=g, best_train=float(fA[c]), mean_train=float(fA.mean()), champ_heldout=float(hoA),
                       struct_div=S.structural_diversity(popA, rng), meanchoice1=float(chA.mean()),
                       champ={k: (int(v[c]) if v.ndim == 1 and v.dtype.kind in "iu" else (float(v[c]) if v.ndim == 1 else [int(x) for x in v[c]])) for k, v in st.items()},
                       pop_mean={k: float(v.mean()) for k, v in st.items() if v.ndim == 1})
            log.append(row)
            if verbose:
                print(f"W9/{mode} g{g:3d} A {fA[c]:6.2f} mean {fA.mean():6.2f} p(1) {chA.mean():.2f} hid {st['n_hidden'][c]} cyc {st['n_cyclic'][c]}")

        def next_gen(pop, fit):
            nonlocal ids
            order = np.argsort(-fit)
            new = pop.select(list(order[:n_elite]) + [0] * (P - n_elite))
            half = order[: P // 2]
            for k in range(n_elite, P):
                cands = rng.choice(half, size=3)
                par = int(cands[np.argmax(fit[cands])])
                src = pop.select([par])
                for name in ("alive", "op", "bias", "keep", "W1", "W2", "R"):
                    getattr(new, name)[k] = getattr(src, name)[0]
                S.mutate_one(new, k, rng)
                new.ids[k] = ids; new.parents[k] = pop.ids[par]; ids += 1
            return new
        popA = next_gen(popA, fA)
        if popB is not None:
            popB = next_gen(popB, fB)
    fA, _, _ = rollout_two_sided(popA, popB, world, EVAL_SEEDS, rng)
    c = int(np.argmax(fA))
    cs = np.array(choice_series)
    ac = [float(np.corrcoef(cs[:-k], cs[k:])[0, 1]) if len(cs) > k + 2 and cs[:-k].std() > 0 and cs[k:].std() > 0 else float("nan")
          for k in (1, 5, 10, 20)]
    return dict(world="W9", mode=mode, cfg=cfg.to_dict(), P=P, G=G, eps=eps, seed=seed, tag=tag, log=log,
                final=dict(heldout=float(fA[c]), genome=popA.genome(c)),
                choice_series=choice_series, choice_autocorr=dict(zip(["lag1", "lag5", "lag10", "lag20"], ac)),
                elapsed_s=time.time() - t0, receipt=receipt(cfg, "W9", mode, P, G, eps, seed))


# ----------------------------------------------------------------------
# dissection
# ----------------------------------------------------------------------

def dissect(genome, world_name, mode, seeds=EVAL_SEEDS):
    """Node-ablation sensitivity of one organism plus its behaviour trace
    on the held-out episodes. Returns a JSON-able dict."""
    cfg = S.Config(**genome["cfg"])
    pop = S.Population.from_genomes([genome], cfg)
    world = make_world(world_name, mode)
    var, removed = S.ablation_population(pop, 0)
    fit = rollout(var, world, seeds)
    base = float(fit[0])
    abl = [dict(node=h, op=genome["op"][h], keep=genome["keep"][h], fit=float(f), delta=float(f - base))
           for h, f in zip(removed[1:], fit[1:])]
    # substrate ablations: no persistent state; no plasticity
    outs = {}
    for label, kw in (("no_state", dict(allow_keep=False, reset_each_step=True)),
                      ("no_plasticity", dict(allow_plasticity=False))):
        c2 = S.Config(**{**genome["cfg"], **kw})
        p2 = S.Population.from_genomes([genome], c2)
        outs[label] = float(rollout(p2, world, seeds)[0])
    _, traces = rollout(pop, world, seeds[:4], record=True)
    acts = np.stack(traces["actions"])[:, :, 0]      # (S, T)
    return dict(base=base, node_ablation=abl, substrate_ablation=outs,
                actions=acts.astype(int).tolist(), info=[[_jsonable(i) for i in ep] for ep in traces["info"]])


def transfer(genome, targets, seeds=EVAL_SEEDS):
    """Evaluate one organism on other worlds (present mode)."""
    cfg = S.Config(**genome["cfg"])
    pop = S.Population.from_genomes([genome], cfg)
    out = {}
    for w in targets:
        if w == "W9":
            continue
        out[w] = float(rollout(pop, make_world(w, "present"), seeds)[0])
    return out


def _jsonable(d):
    o = {}
    for k, v in d.items():
        if isinstance(v, np.ndarray):
            o[k] = v[0].item() if v.ndim == 1 and v.shape[0] > 0 and v.dtype != bool else (v[0].item() if v.ndim == 1 else v.tolist())
        elif isinstance(v, (np.generic,)):
            o[k] = v.item()
        else:
            o[k] = v
    return o


# ----------------------------------------------------------------------
# receipts
# ----------------------------------------------------------------------

def code_commit():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        return subprocess.check_output(["git", "-C", here, "rev-parse", "HEAD"], timeout=30).decode().strip()
    except Exception:
        return "UNKNOWN"


def receipt(cfg, world, mode, P, G, eps, seed):
    spec = dict(cfg=cfg.to_dict(), world=world, mode=mode, P=P, G=G, eps=eps, seed=seed, eval_seeds=EVAL_SEEDS)
    h = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    return dict(config_hash=h, code_commit=code_commit(), spec=spec,
                utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
