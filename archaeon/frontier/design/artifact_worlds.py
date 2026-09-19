"""WORLD-GENERATOR MUTATION: artifact worlds (niche construction across generations).

The Campaign 6 generator resets every world state each generation; the directive's s4 asks for worlds whose useful
structure appears only over long histories and for organism-mediated environmental modification. This family turns on
persist_shared for coupled worlds with objects: what one generation writes into the shared cells and leaves in the shared
pools is what the next generation is born into. The generator itself is unchanged; the mutation is the option, recorded
in every spec and in the segment spec hash, so the family is reproducible from records and seeds.

Sweep: 12 procedural worlds forced to contain coupling + objects + resources (bins 4-8), x {persist_shared on, off},
v0 profile, N=32, E=8, 800 generations, unlabeled schedules. Readout (digest): objects_changed per generation, reward
median trajectory, ENDOGENOUS entries, environmental_modification firings -- compared on/off pairwise.
"""
from __future__ import annotations

from archaeon.frontier import specs as SP
from archaeon.frontier.nominate import queue_specs
from archaeon.campaign6.worlds import sample_world

FAMILY = "W-artifacts"


def emit(reg, q, priority=None):
    pr = priority if priority is not None else 1.5
    lid = next((r["lineage_id"] for r in reg.all() if r["originating_observation"].get("key") == FAMILY), None)
    if lid is None:
        lid = reg.create(originating_observation={"key": FAMILY, "source": "directive s4 (world families)", "ref": "archaeon/campaign6/worlds/runtime.py",
                                                  "summary": "generator mutation: shared world state persists across generations (artifacts, niche construction)"},
                         mode="BREADTH", title="Artifact worlds: shared state carried across generations", tags=["W", "niche"], world_generator_version="archaeon.c6.world_gen/0.1+persist_shared")
    items = []; found = 0; seed = 50000
    while found < 12 and seed < 51000:
        rec = sample_world(seed, bin_target=4 + (found % 5))
        if all(f in rec["features"] for f in ("coupling", "objects", "resources")):
            for on in (True, False):
                w = {"kind": "c6.composed.v1", "params": rec["params"]}
                items.append((SP.make_spec(family_id=FAMILY, experiment_id="%s/w%d_%s" % (FAMILY, seed, "persist" if on else "reset"), world=w, profile="v0",
                                           population={"source": "c4_parents", "seed": 1, "N": 32}, E=8, generations=800, chunk=400, schedule={"kind": "unlabeled", "seed": seed}, seed=seed,
                                           budget_evaluations=32 * 800, lane="MIXED", generator="design.artifact_worlds", world_options={"persist_shared": on}), "persist" if on else "reset"))
            found += 1
        seed += 1
    ids = queue_specs(reg, q, lid, items, "EXPLORATION", pr, "design.artifact_worlds: persist_shared on/off pairs")
    return {"lineage": lid, "worlds": found, "queued": ids}
