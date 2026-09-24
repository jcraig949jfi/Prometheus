"""PURSUIT: the boom-bust maximum on coupled worlds.

Observed (receipts, 2026-09-19): on the bin-7 world with coupling + hazards + history + locality + objects + resources,
the population's reward maximum jumps by >= 2 bands between adjacent archived generations and collapses within a few,
repeatedly (e.g. .151 -> .296 at 54 -> 55; .0 -> .164 at 65 -> 66), while the median stays ~.05 and an ENDOGENOUS
entry is written every generation. Two readings, neither assumed:
  H_order    an artefact of SEQUENTIAL evaluation in a shared-pool world (the first organism evaluated sees the full
             pool; elites are evaluated first) -> the spikes belong to evaluation ORDER, not to organisms
  H_pop      a population-level effect with no exceptional individual (a directive fixture class)
Designs (all on the SAME world record and seed; one thing changes per arm; N = 32, E = 8, 600 generations):
  A  baseline (eval_order population)                       -- the observed condition, re-run as a spec
  B  eval_order seeded_shuffle                              -- H_order: spikes should track order, not lineage
  C  coupling OFF (same params, coupling.on = false)        -- no shared pool: no spikes under either H
  D  persist_shared across generations                      -- niche construction: depletion carried, spikes should change shape
  E  N = 8 and N = 128                                      -- population-size dependence of the spike rate
  F  nominated FULL freezes of the top-3 at the spike generations seen (55, 66, 184, 223) in arm A -> forensic packets
  G  3 seeds of A and B                                     -- the comparison the readings need
Readout (code, digest): spike rate = archived generations with reward_max jump >= 2/16 per 100 generations, per arm.
"""
from __future__ import annotations

import json
from archaeon.frontier import specs as SP
from archaeon.frontier.nominate import queue_specs
from archaeon.campaign6.worlds import sample_world

FAMILY = "P-boom"
WORLD_SEED = 10001
import json as _json
from pathlib import Path as _Path
_BW = _json.loads((_Path(__file__).resolve().parent / "BOOM_WORLD.json").read_text(encoding="utf-8"))   # the exact world params of the observed runs, copied from the receipt
SPIKE_GENS = [55, 66, 184, 223]


def base_spec(**kw):
    w = {"kind": "c6.composed.v1", "params": _BW["params"]}
    args = dict(family_id=FAMILY, world=w, profile="v0", population={"source": "c4_parents", "seed": 1, "N": 32}, E=8, generations=600, chunk=300,
                schedule={"kind": "unlabeled", "seed": WORLD_SEED}, seed=WORLD_SEED, budget_evaluations=32 * 600, lane="LLM_PROPOSED", generator="design.boom")
    args.update(kw)
    return SP.make_spec(**args)


def emit(reg, q, priority=None):
    pr = priority if priority is not None else 3.0
    lid = next((r["lineage_id"] for r in reg.all() if r["originating_observation"].get("key") == FAMILY), None)
    if lid is None:
        lid = reg.create(originating_observation={"key": FAMILY, "source": "receipts B-scatter.T000.d_seed* (2026-09-19)", "ref": "archaeon/frontier/runs/B-scatter/",
                                                  "summary": "boom-bust reward maximum on a coupled bin-7 world; median flat; endogenous entry every generation"},
                         mode="DEPTH", title="Boom-bust maximum on coupled worlds: evaluation order or population effect?", tags=["P", "coupling", "order"],
                         representation_limits=["v0 profile only in the first sweep"])
    items = []
    for seed in (1, 2, 3):
        items.append((base_spec(experiment_id="%s/A_baseline_s%d" % (FAMILY, seed), seed=WORLD_SEED + seed, world_options={"eval_order": "population"},
                                nominate={"generations": SPIKE_GENS, "top_k": 3} if seed == 1 else None, measurements=["population_shift", "max_spike"]), "A_baseline"))
        items.append((base_spec(experiment_id="%s/B_shuffle_s%d" % (FAMILY, seed), seed=WORLD_SEED + seed, world_options={"eval_order": "seeded_shuffle"}, measurements=["population_shift", "max_spike"]), "B_shuffle"))
    params = json.loads(json.dumps(_BW["params"])); params["coupling"] = {"on": False}
    items.append((base_spec(experiment_id="%s/C_no_coupling" % FAMILY, world={"kind": "c6.composed.v1", "params": params}, seed=WORLD_SEED + 1), "C_no_coupling"))
    items.append((base_spec(experiment_id="%s/D_persist_shared" % FAMILY, seed=WORLD_SEED + 1, world_options={"persist_shared": True}), "D_persist_shared"))
    items.append((base_spec(experiment_id="%s/F_popcapture_s1" % FAMILY, seed=WORLD_SEED + 1, world_options={"eval_order": "population"},
                            nominate={"generations": SPIKE_GENS, "top_k": 32, "window": 2, "population": True}, measurements=["population_shift", "max_spike"]), "F_popcapture"))
    for N in (8, 128):
        items.append((base_spec(experiment_id="%s/E_N%d" % (FAMILY, N), seed=WORLD_SEED + 1, population={"source": "c4_parents", "seed": 1, "N": N}, budget_evaluations=N * 600), "E_N"))
    ids = queue_specs(reg, q, lid, items, "EXPLOITATION", pr, "design.boom: order vs population effect")
    # v2 (2026-09-19): the same-seed premise of v1 was false (run_id was folded into every stream). Arms sharing a seed now
    # share world_options.stream_key, so one thing changes per arm. Old runs stay as independent-stream data.
    items2 = []
    for seed in (1, 2, 3):
        key = "P-boom.stream.s%d" % seed
        items2.append((base_spec(experiment_id="%s/K_A_baseline_s%d" % (FAMILY, seed), seed=WORLD_SEED + seed, world_options={"eval_order": "population", "stream_key": key}, measurements=["population_shift", "max_spike"]), "K_A_baseline"))
        items2.append((base_spec(experiment_id="%s/K_B_shuffle_s%d" % (FAMILY, seed), seed=WORLD_SEED + seed, world_options={"eval_order": "seeded_shuffle", "stream_key": key}, measurements=["population_shift", "max_spike"]), "K_B_shuffle"))
        items2.append((base_spec(experiment_id="%s/K_C_no_coupling_s%d" % (FAMILY, seed), world={"kind": "c6.composed.v1", "params": params}, seed=WORLD_SEED + seed, world_options={"stream_key": key}, measurements=["population_shift", "max_spike"]), "K_C_no_coupling"))
        items2.append((base_spec(experiment_id="%s/K_D_persist_s%d" % (FAMILY, seed), seed=WORLD_SEED + seed, world_options={"persist_shared": True, "stream_key": key}, measurements=["population_shift", "max_spike"]), "K_D_persist"))
    items2.append((base_spec(experiment_id="%s/K_F_popcapture_s1" % FAMILY, seed=WORLD_SEED + 1, world_options={"eval_order": "population", "stream_key": "P-boom.stream.s1"},
                             nominate={"generations": SPIKE_GENS, "top_k": 32, "window": 2, "population": True}, measurements=["population_shift", "max_spike"]), "K_F_popcapture"))
    ids += queue_specs(reg, q, lid, items2, "EXPLOITATION", pr + 0.5, "design.boom v2: shared streams (stream_key) -- one thing changes per arm")
    return {"lineage": lid, "queued": ids}
