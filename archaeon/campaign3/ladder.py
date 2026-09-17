"""The delay ladder as a reusable route (campaign 3, C3-SFE-03 / C3-SFE-05; parent C2-SFE-06).

One population climbs rungs R0=W0 (delay 0), R1 delay 1, R2 delay 2, R3 delay 4 (K=1, D=1,
4-bit) under a fixed schedule (rung_gens generations per rung). A share p of each generation's
training battery comes from EARLIER rungs (an ecological revisit pressure, never a reward for
retaining anything). Dense transition probes (telemetry.probe_plan) evaluate the elite on every
rung; transition_events() locates when competence appears, collapses and recovers.

run_ladder(job) -> row with the rung x generation matrix, per-rung events, generality (first
generation at which the elite scores >= GENERAL_MIN on every rung), adaptation speed per
transition, revisit cost, final and peak per rung, genotype/behaviour of the elite.
Options: p_after_general (C3-SFE-05: the revisit share once the elite is general, e.g. 0.0),
probe dense/sparse windows, rung_gens.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional

from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign3.c3base import CAMPAIGN_SEED

RUNGS = [WorldSpec("W0", value_bits=4), WorldSpec("W1_d1", delay=1, value_bits=4), WorldSpec("W1_d2", delay=2, value_bits=4), WorldSpec("W1_d4", delay=4, value_bits=4)]
LABELS = ["R0", "R1", "R2", "R3"]
PROBE_EPISODES = 24
GENERAL_MIN = 0.75


def battery(g: int, seed: int, rung: int, p: float, E: int) -> list:
    """(E - n_rev) episodes from the current rung, n_rev from earlier rungs round-robin; keyed on
    (g, seed) so every arm draws the same episodes per rung."""
    n_rev = int(round(p * E)) if rung > 0 else 0
    cur = episodes_for(RUNGS[rung], CAMPAIGN_SEED, "train", g * 100003 + seed, E)
    eps = list(cur[: E - n_rev])
    for i in range(n_rev):
        r = i % rung
        old = episodes_for(RUNGS[r], CAMPAIGN_SEED, "train", g * 100003 + seed, E)
        eps.append(old[(i // rung) % len(old)])
    return eps


def run_ladder(job: dict) -> dict:
    p, seed, N, E, rung_gens = job["p"], job["seed"], job["N"], job["E"], job["rung_gens"]
    p_after = job.get("p_after_general")                     # None: keep p throughout
    dense, sparse = job.get("dense", 5), job.get("sparse", 5)
    G_ = rung_gens * len(RUNGS)
    transitions = [rung_gens * i for i in range(1, len(RUNGS))]
    plan = set(T.probe_plan(G_, transitions, dense=dense, sparse=sparse))
    t0 = time.time()
    ev = Evolution(RUNGS[0], REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c3-ladder-p%s" % p, foundry=FOUNDRY_C2)
    probes = [(lab, episodes_for(spec, CAMPAIGN_SEED, "eval", seed, PROBE_EPISODES), 7) for lab, spec in zip(LABELS, RUNGS)]
    matrix: List[dict] = []; schedule = []
    general_gen = None; p_now = p; revisit_cost = 0; p_switched_at = None
    for g in range(G_):
        rung = min(len(RUNGS) - 1, g // rung_gens)
        ev.spec = RUNGS[rung]
        eps = battery(g, seed, rung, p_now, E)
        revisit_cost += (len(eps) - len(episodes_for(RUNGS[rung], CAMPAIGN_SEED, "train", g * 100003 + seed, E)[: E - int(round(p_now * E)) if rung > 0 else E]))
        row = ev.evaluate_generation(episodes=eps, last=(g == G_ - 1))
        schedule.append({"gen": g, "rung": rung, "p": p_now, "best": row["best_reward"], "mean": row["mean_reward"]})
        if g in plan or g == G_ - 1:
            elite = ev.scored[0][1]["manifest"]
            m = T.rung_matrix_row(evaluate, elite, probes, g) | {"rung": rung, "p": p_now}
            matrix.append(m)
            if general_gen is None and all(m[lab] >= GENERAL_MIN for lab in LABELS):
                general_gen = g
                if p_after is not None and p_switched_at is None:
                    p_now = p_after; p_switched_at = g
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    events = {lab: T.transition_events(matrix, lab, appear=GENERAL_MIN, collapse=0.25) for lab in LABELS}
    final = {lab: matrix[-1][lab] for lab in LABELS}
    peak = {lab: max(m[lab] for m in matrix) for lab in LABELS}
    # adaptation speed: generations from the transition into rung k to the first probe with rung-k competence >= GENERAL_MIN
    adapt = {}
    for k, t in enumerate(transitions, start=1):
        first = next((m["gen"] for m in matrix if m["gen"] >= t and m[LABELS[k]] >= GENERAL_MIN), None)
        adapt[LABELS[k]] = None if first is None else first - t
    # generality: which rung was being trained when it appeared; abrupt vs gradual on R3
    rung_at_general = None if general_gen is None else min(len(RUNGS) - 1, general_gen // rung_gens)
    r3_first_quarter = next((m["gen"] for m in matrix if m["R3"] >= 0.25), None)
    r3_first_general = next((m["gen"] for m in matrix if m["R3"] >= GENERAL_MIN), None)
    rise = None if (r3_first_quarter is None or r3_first_general is None) else r3_first_general - r3_first_quarter
    survives = general_gen is not None and all(final[lab] >= GENERAL_MIN for lab in LABELS)
    ho = {lab: round(evaluate(res["elite"]["manifest"], episodes_for(spec, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=11)["reward"], 4) for lab, spec in zip(LABELS, RUNGS)}
    return {"arm": job.get("arm", "p%s" % p), "p": p, "p_after_general": p_after, "p_switched_at": p_switched_at, "seed": seed, "matrix": matrix, "schedule": schedule,
            "events": events, "general_gen": general_gen, "rung_at_general": rung_at_general, "r3_rise_gens": rise, "general_survives": survives,
            "final_r0": final["R0"], "final_r1": final["R1"], "final_r2": final["R2"], "final_r3": final["R3"], "peak_r0": peak["R0"], "peak_r3": peak["R3"],
            "retention_r0": round(final["R0"] / peak["R0"], 4) if peak["R0"] > 0 else None, "fell_r0_at": events["R0"]["collapsed"], "recovered_r0_at": events["R0"]["recovered"],
            "adapt_gens": adapt, "revisit_cost_episodes": revisit_cost, "heldout_by_rung": ho, "general_heldout": 1 if all(v >= GENERAL_MIN for v in ho.values()) else 0,
            "reached_r0_by_rung_end": 1 if any(s["best"] >= 0.5 for s in schedule[:rung_gens]) else 0,
            "elite_summary": res["elite_summary"], "elite_manifest": res["elite"]["manifest"], "persist": res["elite_eval"]["persist"],
            "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}
