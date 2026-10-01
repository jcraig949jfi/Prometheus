"""D1 / D6 / D7 demonstration (no world run: one Runner, `_place`, `_env_epoch`, `_validate` only).

D1  val_cache is keyed on genome bytes only, but the task an organism is scored on depends on its niche
    (RESERVOIR easy niche; COEVO_ENV per-niche task). The second organism carrying a genome receives the FIRST
    organism's score, computed on a different task.
D6  run_xtg's reader filter uses the BASE spec's cue_index (FORCED_READ -> 2, needs probe >= 3), while COEVO_ENV
    niches may run ANSWER_BEFORE_READ (2 inputs): probe <= 2 there, so no organism in such a niche can ever be
    "competent".
D7  run_xtg's post-run `_validate(force=True)` is answered entirely from val_cache (zero new evaluations).
"""
from __future__ import annotations

import _paths  # noqa: F401
import run_dc
import run_dd
import run_ds
import tasks
import world

world.z8 = run_dc.dense_z8()
a = run_ds.cells()[run_dd.CELLS["ffa6"]]
cell = dict(a["cell"], atlas_axis="NONE", pressure="TASK_GATED_INTERACTION")   # exactly run_xtg's TG cell
r = world.Runner(cell, 31_000_000, tier=a["tier"])
r._env_epoch()                                   # epoch 0: initialises env_pop from the world RNG (as step() would)
env_initial = [(e["transform"], e["read_order"]) for e in r.env_pop]

# Force two niches onto different tasks so the demonstration does not depend on the draw.
r.env_pop[0].update(transform="ADD37", read_order="FORCED_READ")
r.env_pop[1].update(transform="XOR5A", read_order="ANSWER_BEFORE_READ")
spec0 = r._env_spec_for(type("O", (), {"niche": 0})())
spec1 = r._env_spec_for(type("O", (), {"niche": 1})())
g = r._pad(tasks.witness(spec0))                 # a correct program for niche 0's task

calls = {"n": 0}
_orig = tasks.competence


def counting(*k, **kw):
    calls["n"] += 1
    return _orig(*k, **kw)


tasks.competence = counting
x = r._place(g, 0, niche=0)
y = r._place(g, 1, niche=1)
r._validate(force=True)
direct1 = _orig(g, spec1, seed=r.seed * 7919 + r.epoch, held_seed=r.seed * 7919 + r.epoch + 500000)
direct0 = _orig(g, spec0, seed=r.seed * 7919 + r.epoch, held_seed=r.seed * 7919 + r.epoch + 500000)
evals_first = calls["n"]
r._validate(force=True)                          # what run_xtg does after run() (run() itself already did one)
evals_second = calls["n"] - evals_first

# D6: a perfect reader for niche 1's ABR task, placed in niche 1.
r2 = world.Runner(cell, 31_000_001, tier=a["tier"])
r2._env_epoch()
r2.env_pop[1].update(transform="XOR1", read_order="ANSWER_BEFORE_READ")
s1 = r2._env_spec_for(type("O", (), {"niche": 1})())
gr = r2._pad(tasks.witness(s1))
z = r2._place(gr, 0, niche=1)
r2._validate(force=True)
ci = r2.spec.cue_index()
tasks.competence = _orig

_paths.dump("d1_valcache.json", {
    "env_pop_initial_draw_seed31000000": env_initial,
    "D1": {"niche0_spec": spec0.as_dict(), "niche1_spec": spec1.as_dict(),
           "org_in_niche0_held": x.held, "org_in_niche1_held_RECORDED": y.held,
           "org_in_niche1_held_TRUE_for_its_task": direct1["held"],
           "niche0_true": direct0["held"],
           "competence_evaluations_for_two_organisms": evals_first},
    "D7": {"evaluations_in_post_run_validate": evals_second},
    "D6": {"reader_in_ABR_niche_held": z.held, "probe": z.probe, "run_xtg_cue_index_used": ci,
           "passes_run_xtg_reader_filter": bool(z.held >= 0.5 and z.probe >= ci + 1)},
})
