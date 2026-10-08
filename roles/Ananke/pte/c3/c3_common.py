"""PTE-C3 common (72h push; operator order roles/Ananke/prompts/2026-10-07_72h_c3_c4_c5/, 8c48ebfdf).

evolve_c3 = the C2B/C2C lineage-tagged GA loop (identical RNG consumption; the selector spec M and the shaping
weights are parameters) plus PER-GENERATION LINEAGE FUNCTION MONITORING on a dedicated monitor world set that is
disjoint from training, final and held worlds:
  every `monitor_every`-th generation (default 3; plus the last), two genomes are scored on the monitor worlds with
  the frozen competence ruler (cadence chosen at the C3S flight: per-generation monitoring cost ~4x the search):
    * LB  = the best lineage member by this generation's fitness (lineage share >= .5), if any;
    * GB  = the generation's best genome by fitness.
  recorded: their B (FLIP) / accuracy, the lineage count, and the lineage's best fitness rank.
The monitor never feeds selection. Monitoring evaluations do not touch the GA RNG.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "c2c"))
import c2c_common as X  # noqa: E402
B = X.B
C = X.C
from prometheus.ananke import assays  # noqa: E402
from prometheus.ananke.search import FINAL_NS, TRAIN_NS, random_genomes  # noqa: E402

C3_NS = 0xC3001007
MONITOR_KEY = 0x404E
MONITOR_WORLDS = 64


def monitor_seeds(cell_key):
    return assays.world_seeds(C.H_int(C3_NS, MONITOR_KEY, cell_key), MONITOR_WORLDS)


def _fn(role, pt, ep):
    c = C.competence(role, pt, ep)
    return {"status": c["status"], "acc": c["all"]["mean"], "B": c["B"]["mean"] if "B" in c else None}


def evolve_c3(ph, env, sseed, sp, device, mutate=None, init=None, role="FLIP", mon_seeds=None, monitor=True,
              monitor_every=3):
    mutate = mutate or B.mutate_tagged
    g = np.random.default_rng(sseed)
    pop = random_genomes(g, sp.pop, ph)
    tags = np.zeros(pop.shape[:3], dtype=bool)
    if init is not None:
        pop[0] = init; tags[0] = True
    curve = []
    for gen in range(sp.gens):
        seeds = assays.world_seeds(C.H_int(sseed, TRAIN_NS, gen), sp.M)
        r = assays.evaluate(ph, pop, env, seeds, device=device)
        acc = r.mean()
        f = acc + sp.w_contrast * np.maximum(r.sens_act, 0) + sp.w_any * r.sens_any
        order = np.argsort(-f, kind="stable")
        share = tags.mean((1, 2)); lin = share >= B.LINEAGE_MIN_SHARE
        rec = {"gen": gen, "max_acc": float(acc.max()), "mean_acc": float(acc.mean()), "best_fit": float(f[order[0]]),
               "n_lineage": int(lin.sum())}
        if lin.any():
            lb = int(order[np.flatnonzero(lin[order])[0]])
            rec.update(lineage_rank=int(np.flatnonzero(lin[order])[0]), lineage_best_train_acc=float(acc[lb]))
        if monitor and mon_seeds is not None and (gen % monitor_every == 0 or gen == sp.gens - 1):
            progs = [pop[order[0]]] + ([pop[lb]] if lin.any() else [])
            pt, ep = C.eval_programs(ph, env, mon_seeds, progs, device=device)
            rec["GB"] = _fn(role, pt[0], ep)
            if lin.any():
                rec["LB"] = _fn(role, pt[1], ep)
        curve.append(rec)
        if gen == sp.gens - 1:
            break
        k = max(2, int(sp.pop * sp.trunc))
        par, ptag = pop[order[:k]], tags[order[:k]]
        nxt = [pop[order[i]] for i in range(sp.elite)]
        ntag = [tags[order[i]] for i in range(sp.elite)]
        while len(nxt) < sp.pop:
            ia = int(g.integers(k))
            a, ta = par[ia], ptag[ia]
            if g.random() < sp.p_cross:
                ib = int(g.integers(k))
                a, ta = B.crossover_tagged(g, a, par[ib], ta, ptag[ib])
            c, t = mutate(g, a, ta, sp)
            nxt.append(c); ntag.append(t)
        pop, tags = np.stack(nxt), np.stack(ntag)
    fs = assays.world_seeds(C.H_int(sseed, FINAL_NS), sp.M_final)
    rf = assays.evaluate(ph, pop, env, fs, device=device)
    ci = int(np.argmax(rf.mean()))
    return {"pop": pop, "tags": tags, "curve": curve, "champ_index": ci, "final_train_acc": rf.mean()}
