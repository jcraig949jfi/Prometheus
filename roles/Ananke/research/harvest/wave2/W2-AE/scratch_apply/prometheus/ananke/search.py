"""The OUTER search over update laws (declared: a plain mutation +
truncation-selection loop over world genomes -- the search, not the
substrate; resemblance: genetic algorithm over linear register programs).

Rules carried in from sibling campaigns:
- fresh training worlds every generation (no memorising a seed set);
- the champion is chosen on TRAINING evaluations only, then evaluated
  ONCE on held-out worlds from a disjoint seed namespace (Ares: never
  argmax on the held-out set);
- the zero-communication control of the champion is always run on the
  same held-out worlds (the matched control every claim needs);
- plants are never injected (mission s17).
"""
from __future__ import annotations

import dataclasses
import time

import numpy as np

from . import assays, envs
from .engine import Controls
from .physics import Physics
from .rng import H_int

TRAIN_NS, FINAL_NS, HELD_NS = 0x7A1, 0xF1A, 0x4E1D


@dataclasses.dataclass(frozen=True)
class SearchSpec:
    pop: int = 48
    M: int = 8               # training worlds per genome per generation (even)
    gens: int = 20
    elite: int = 4
    trunc: float = 0.25
    p_field: float = 0.04    # per-field resample probability
    p_instr: float = 0.15    # whole-instruction resample (per genome)
    p_swap: float = 0.10
    p_cross: float = 0.30
    M_final: int = 16        # final training re-evaluation of the last population
    M_held: int = 64         # held-out worlds for the champion
    w_contrast: float = 0.10  # selection-only shaping: + w_contrast*max(contrast,0) + w_any*sens_any
    w_any: float = 0.02       # (max total bonus 0.12; claims and champion choice use accuracy only)

    def to_dict(self):
        return dataclasses.asdict(self)


def random_genomes(g: np.random.Generator, n: int, ph: Physics) -> np.ndarray:
    x = g.integers(0, 256, size=(n, ph.rules, ph.prog_len, 5))
    x[..., 4] = g.integers(-128, 128, size=x.shape[:-1])
    return x


def _rand_instr(g, shape):
    x = g.integers(0, 256, size=(*shape, 5))
    x[..., 4] = g.integers(-128, 128, size=shape)
    return x


def mutate(g: np.random.Generator, parent: np.ndarray, sp: SearchSpec) -> np.ndarray:
    c = parent.copy()
    G, L, _ = c.shape
    fresh = _rand_instr(g, (G, L))
    mask = g.random((G, L, 5)) < sp.p_field
    c = np.where(mask, fresh, c)
    if g.random() < sp.p_instr:
        c[g.integers(G), g.integers(L)] = _rand_instr(g, ())
    if g.random() < sp.p_swap:
        r = g.integers(G)
        i, j = g.integers(L, size=2)
        c[r, [i, j]] = c[r, [j, i]]
    return c


def crossover(g, a, b):
    m = g.random(a.shape[:2]) < 0.5
    return np.where(m[..., None], a, b)


def evolve(ph: Physics, env: envs.EnvSpec, search_seed: int, sp: SearchSpec,
           device="cuda", log=None) -> dict:
    t_start = time.time()
    g = np.random.default_rng(search_seed)
    pop = random_genomes(g, sp.pop, ph)
    curve = []
    gen0_tel = None
    n_evals = 0
    for gen in range(sp.gens):
        seeds = assays.world_seeds(H_int(search_seed, TRAIN_NS, gen), sp.M)
        r = assays.evaluate(ph, pop, env, seeds, device=device)
        n_evals += sp.pop * sp.M
        acc = r.mean()
        f = acc + sp.w_contrast * np.maximum(r.sens_act, 0) + sp.w_any * r.sens_any  # declared shaping
        if gen == 0:
            gen0_tel = {k: float(np.mean(v)) for k, v in r.tel.items()}
            gen0_tel["acc_mean"] = float(acc.mean())
            gen0_tel["acc_max"] = float(acc.max())
            gen0_tel["frac_sensitive_any"] = float(np.mean(r.sens_any > 0))
            gen0_tel["frac_contrast_pos"] = float(np.mean(r.sens_act > 0))
            gen0_tel["frac_emitting"] = float(np.mean(r.tel["emit_rate"] > 0))
        order = np.argsort(-f, kind="stable")
        curve.append({"gen": gen, "best_fit": float(f[order[0]]), "best_acc": float(acc[order[0]]),
                      "max_acc": float(acc.max()), "mean_acc": float(acc.mean()),
                      "mean_sens_any": float(r.sens_any.mean()),
                      "max_contrast": float(r.sens_act.max())})
        if log:
            log(curve[-1])
        if gen == sp.gens - 1:
            break
        k = max(2, int(sp.pop * sp.trunc))
        parents = pop[order[:k]]
        nxt = [pop[order[i]] for i in range(sp.elite)]
        while len(nxt) < sp.pop:
            a = parents[g.integers(k)]
            if g.random() < sp.p_cross:
                a = crossover(g, a, parents[g.integers(k)])
            nxt.append(mutate(g, a, sp))
        pop = np.stack(nxt)
    # champion: re-evaluate the final population on fresh TRAINING worlds
    fseeds = assays.world_seeds(H_int(search_seed, FINAL_NS), sp.M_final)
    rf = assays.evaluate(ph, pop, env, fseeds, device=device)
    n_evals += sp.pop * sp.M_final
    ci = int(np.argmax(rf.mean()))      # champion by training ACCURACY only (no shaping)
    champ = pop[ci]
    # held-out: champion and its zero-comm control on disjoint worlds, once
    hseeds = assays.world_seeds(H_int(search_seed, HELD_NS), sp.M_held)
    rh = assays.evaluate(ph, champ[None], env, hseeds, device=device)
    rz = assays.evaluate(ph, champ[None], env, hseeds, ctrl=Controls(zero_comm=True), device=device)
    n_evals += 2 * sp.M_held
    ph_pair = rh.pair_acc()[0]
    pz_pair = rz.pair_acc()[0]
    m, lo, hi = assays.pair_ci(ph_pair)
    dm, dlo, dhi = assays.pair_ci(ph_pair - pz_pair)
    tw = assays.twin_assay(ph, champ[None], env, hseeds[:16], device=device)
    return {
        "curve": curve,
        "gen0": gen0_tel,
        "champion": champ.tolist(),
        "champ_train_final": float(rf.mean()[ci]),
        "pop_final_mean": float(rf.mean().mean()),
        "held": {"acc": float(m), "lo99": float(lo), "hi99": float(hi),
                 "zero_comm": float(pz_pair.mean()),
                 "comm_delta": float(dm), "comm_delta_lo99": float(dlo), "comm_delta_hi99": float(dhi)},
        "held_tel": {k: float(v[0]) for k, v in rh.tel.items()},
        "twin": {k: float(v[0]) for k, v in tw.items()},
        "n_world_evals": n_evals,
        "wall_s": time.time() - t_start,
    }
