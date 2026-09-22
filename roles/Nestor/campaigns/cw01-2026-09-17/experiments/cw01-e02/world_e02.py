"""cw01-e02 — transformation economics, and whether gains form a RATCHET.

The substrate is purely economic. T2 costs less on a low-dispersion payload, and
only T1 lowers dispersion; T3 costs less and yields more on a low-structure
payload, and only T2 lowers structure. Nothing in the world rewards the ordering
T1 -> T2 -> T3. If a lineage discovers it, that is a finding.

The ratchet hypothesis in gene terms: raising `p_factor` is worth little while
dispersion is high, because T2 is then expensive. Adopting T1 (a modest gain of
its own) makes T2 cheap, which makes a later rise in `p_factor` profitable. So the
later gain is CONDITIONAL on the earlier one — or it isn't, and this returns NULL.

REUSE (VI): T4's occupancy economics are identical to e01's addressable region and
were verified there (Q1/Q6, 5 instrument defects fixed). `Region` and `Refused` are
IMPORTED from world_e01, not copied. e01's fixes are inherited, not re-earned.

Honest limitation, same as e01: a 9-gene real-valued policy vector, not a rich
program. Two of those genes are declared NEUTRAL by construction and exist to be
the cost-matched sham for the K1 knockout.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cw01-e01"))
from world_e01 import Refused, Region                     # noqa: E402  (deliberate reuse)

GENE_BOUNDS = {
    "p_norm": (0.0, 1.0),
    "p_factor": (0.0, 1.0),
    "factor_threshold": (0.0, 1.0),
    "p_bind": (0.0, 1.0),
    "cells_frac": (0.015, 0.125),
    "persist_steps": (1.0, 50.0),
    "reduce_eagerness": (0.0, 1.0),
    "neutral_a": (0.0, 1.0),      # NO phenotype by construction — the K1 sham
    "neutral_b": (0.0, 1.0),      # NO phenotype by construction — the K1 sham
}
NEUTRAL_GENES = ("neutral_a", "neutral_b")
GENE_NAMES = tuple(GENE_BOUNDS)


def seed_genome(rng):
    return {g: float(rng.uniform(*b)) for g, b in GENE_BOUNDS.items()}


def mutate(genome, rng, sigma=0.12):
    out = {}
    for g, v in genome.items():
        lo, hi = GENE_BOUNDS[g]
        out[g] = float(np.clip(v + rng.normal(0.0, sigma * (hi - lo)), lo, hi))
    return out


# ------------------------------------------------------------------ the physics

def t2_cost(cfg, dispersion):
    t = cfg["transformations"]["T2_factor"]
    return t["cost_base"] * (1.0 + 2.0 * dispersion)


def t3_cost(cfg, size, structure):
    t = cfg["transformations"]["T3_reduce"]
    return t["cost_base"] * size * (1.0 + 1.5 * structure)


def t3_info(size, structure):
    return math.log2(1.0 + size) * (1.0 - structure)


def make_items(cfg, rng, n_steps):
    p = cfg["payload"]
    d = p["size_distribution"]
    mu, sigma = math.log(d["median"]), d["sigma"]
    lo, hi = d["clip"]
    gap = p["recurrence_gap_distribution"]
    items, schedule = [], {}
    for t in range(n_steps):
        items.append({
            "id": t, "origin": t,
            "size": float(np.clip(rng.lognormal(mu, sigma), lo, hi)),
            "dispersion": float(rng.uniform(p["dispersion_init"]["lo"], p["dispersion_init"]["hi"])),
            "structure": float(rng.uniform(p["structure_init"]["lo"], p["structure_init"]["hi"])),
        })
        if rng.random() < p["recurrence_rate"]:
            g = int(np.clip(rng.geometric(1.0 / gap["mean_steps"]), *gap["clip"]))
            if t + g < n_steps:
                schedule.setdefault(t + g, []).append(t)
    return items, schedule


def run_episode(genome, cfg, arm, stream_seed, policy_seed=None, intervention=None,
                backend="mem", rconn=None, ns=""):
    """One organism, one episode. stream_seed drives the WORLD; policy_seed the organism.

    Keeping them separate is what makes arms comparable — the lesson of CW01-D010,
    where arm-dependent seeding produced a fake +40% advantage.
    """
    arms = cfg["arms"][arm]
    T = cfg["transformations"]
    wrng = np.random.Generator(np.random.PCG64(stream_seed))
    prng = np.random.Generator(np.random.PCG64(stream_seed if policy_seed is None else policy_seed))

    n_steps = cfg["pressure"]["steps_per_episode"]
    budget = cfg["pressure"]["step_compute_budget"]
    items, schedule = make_items(cfg, wrng, n_steps)

    t4 = T["T4_bind"]
    region = Region(t4["cells"], t4["cost_write_per_cell"], t4["cost_read_per_cell"],
                    t4["cost_hold_per_cell_per_step"], arms["T4_enabled"], backend, rconn, ns)
    cells = max(1, int(round(genome["cells_frac"] * t4["cells"])))

    cost = info = 0.0
    m = dict(compute_used=0.0, t1_applied=0, t2_applied=0, t3_applied=0,
             binds=0, reads=0, resumes=0, refusals=0, ordered=0, unordered=0,
             world_interactions=0, transformations_total=0, completed=0)

    for step in range(n_steps):
        todo = [dict(items[step])]
        for o in schedule.get(step, []):
            todo.append(dict(items[o], recurred=True))

        spent_this_step = 0.0
        for it in todo:
            m["world_interactions"] += 1
            size, disp, struct = it["size"], it["dispersion"], it["structure"]
            key = it["origin"]
            did_t1 = False

            # CW01-D019: draw ALL policy coins up front, unconditionally.
            # `flag and prng.random() < gene` short-circuits when the flag is False,
            # so the random STREAM becomes arm-dependent. That is CW01-D010 again --
            # the defect that faked a +40% advantage in e01 -- reproduced in new code.
            # Drawing every coin regardless of arm or branch makes RNG consumption
            # identical across arms BY CONSTRUCTION rather than by care.
            r_t1, r_t2, r_t3, r_bind = (prng.random(), prng.random(),
                                        prng.random(), prng.random())

            # A recurring item may resume a previously transformed payload.
            # CW01-D021: this read was gated on the ARM FLAG ONLY, with no gene. An
            # organism therefore paid 0.5 to look on every recurrence even when
            # p_bind=0 guaranteed nothing had ever been stored -- a forced cost with
            # no genetic control, which evolution cannot escape. It also made Q10b
            # fail: treatment and control_no_T4 differed by exactly 28 wasted reads
            # x 0.5 = 14.0 cost while producing identical info. Gating on p_bind
            # makes p_bind=0 genuinely disable the whole T4 mechanism.
            if it.get("recurred") and arms["T4_enabled"] and r_bind < genome["p_bind"]:
                try:
                    c, hit, rem = region.read(key)
                    cost += c; m["reads"] += 1
                    if hit and rem is not None:
                        struct = rem                     # restore the FACTORED state only;
                        # Region carries one float slot, and structure is what T3 pays for.
                        # Overwriting dispersion with it too would be incoherent physics.
                        m["resumes"] += 1
                        region.drop(key)
                except Refused:
                    m["refusals"] += 1

            # T1 normalise
            if arms["T1_enabled"] and r_t1 < genome["p_norm"]:
                cost += T["T1_normalise"]["cost"]; spent_this_step += T["T1_normalise"]["cost"]
                disp *= 0.20
                m["t1_applied"] += 1; m["transformations_total"] += 1
                did_t1 = True

            # T2 factor — gated on dispersion, which ONLY T1 lowers.
            # This gate is the economic dependency; no rule mentions ordering.
            if arms["T2_enabled"] and r_t2 < genome["p_factor"] \
                    and disp <= genome["factor_threshold"]:
                c = t2_cost(cfg, disp)
                cost += c; spent_this_step += c
                struct *= 0.25
                m["t2_applied"] += 1; m["transformations_total"] += 1
                if did_t1:
                    m["ordered"] += 1
                else:
                    m["unordered"] += 1

            # T3 reduce — emits output, or bind the partial payload for later
            if spent_this_step < budget and r_t3 < genome["reduce_eagerness"]:
                c = t3_cost(cfg, size, struct)
                cost += c; spent_this_step += c; m["compute_used"] += c
                info += t3_info(size, struct)
                m["t3_applied"] += 1; m["transformations_total"] += 1
                m["completed"] += 1
            elif arms["T4_enabled"] and r_bind < genome["p_bind"]:
                try:
                    c, stored = region.write(key, cells, struct, step)
                    if stored:
                        cost += c; m["binds"] += 1
                except Refused:
                    m["refusals"] += 1

        region.expire(step, genome["persist_steps"])
        cost += region.hold_tick()

        if intervention == "T4_erase":
            region.erase()
        elif intervention == "T4_sham":
            cost += region.sham_release()

    m["cell_steps_held"] = region.cell_steps_held
    m["refusals"] += region.refusals
    m["info"], m["cost"] = info, cost
    m["score"] = info / cost if cost > 0 else 0.0
    return m


# ------------------------------------------------------------------- evolution

def evolve(cfg, arm, generations, n_org, mkseed, backend="mem", rconn=None, ns="",
           selection=True):
    """selection=False is the NO-SELECTION control that calibrates the gain detector (Q11)."""
    aid = cfg["attempt_id"]
    rng = np.random.Generator(np.random.PCG64(mkseed(aid, f"evo|{arm}|{selection}", 0)))
    pop = [seed_genome(rng) for _ in range(n_org)]
    ancestor = [dict(g) for g in pop]

    def ep(g, tag, i):
        return run_episode(g, cfg, arm, mkseed(aid, f"stream|{tag}", i),
                           policy_seed=mkseed(aid, f"policy|{tag}", i),
                           backend=backend, rconn=rconn, ns=ns)

    anc_mean = float(np.mean([ep(g, "anc", i)["score"] for i, g in enumerate(ancestor)]))
    elite_n = max(2, int(n_org * cfg["population"]["elite_fraction"]))
    sigma = cfg["population"]["mutation_sigma"]
    hist = []

    for gen in range(generations):
        res = [ep(g, f"g{gen}", i) for i, g in enumerate(pop)]
        sc = np.array([r["score"] for r in res])
        rec = {"gen": gen, "mean": float(sc.mean()), "best": float(sc.max()),
               "ancestor_relative": float(sc.mean() - anc_mean)}
        for k in ("t1_applied", "t2_applied", "t3_applied", "ordered", "unordered",
                  "binds", "resumes", "cost", "info"):
            rec["mean_" + k] = float(np.mean([r[k] for r in res]))
        for g in GENE_NAMES:
            rec["gene_" + g] = float(np.mean([p[g] for p in pop]))
        hist.append(rec)

        if selection:
            elite = [pop[i] for i in np.argsort(-sc)[:elite_n]]
            pop = [mutate(elite[i % len(elite)], rng, sigma) for i in range(n_org)]
        else:
            pop = [seed_genome(rng) for _ in range(n_org)]   # no inheritance, no selection

    return {"arm": arm, "selection": selection, "ancestor_mean": anc_mean,
            "history": hist, "final_pop": pop, "ancestor_pop": ancestor}


# --------------------------------------------------------------- gain detection

def detect_gains(history, effect_size_min_pct, persistence_generations, baseline_window=5,
                 min_sd_separation=3.0):
    """A GAIN is a step up that STAYS up AND clears the local noise floor.

    CW01-D022: the first version tested percent lift only. On a no-selection null it
    reported 3 gains with lifts of 5.12%, 10.12% and 11.54%, and on pure synthetic
    noise it still fired. The arithmetic: the null's lineage mean has sd ~0.0097 on a
    mean of ~0.13, i.e. 7.4% RELATIVE -- so a 2% lift threshold sat far below the
    noise floor and a percent criterion could never work.

    The fix is a noise-RELATIVE criterion: the step must also clear
    `min_sd_separation` pooled standard deviations. A percent threshold alone cannot
    distinguish a real step from sampling variance, whatever value it is set to.

    Thresholds still come from WORLD.json and are fixed before running, so a gain
    cannot be defined post-hoc to fit whatever the curve did (threat 2).
    """
    means = [h["mean"] for h in history]
    gains = []
    for g in range(baseline_window, len(means) - persistence_generations):
        before = means[max(0, g - baseline_window):g]
        after = means[g:g + persistence_generations]
        base = float(np.mean(before))
        if base <= 0:
            continue
        lift = 100.0 * (float(np.mean(after)) - base) / base
        pooled = float(np.std(list(before) + list(after), ddof=1))
        sep = (float(np.mean(after)) - base) / pooled if pooled > 0 else 0.0
        if lift >= effect_size_min_pct and min(after) > base and sep >= min_sd_separation:
            if gains and g - gains[-1]["gen"] < persistence_generations:
                continue                       # one event, not many
            gains.append({"gen": g, "lift_pct": lift, "baseline": base,
                          "level": float(np.mean(after)), "sd_separation": sep})
    return gains
