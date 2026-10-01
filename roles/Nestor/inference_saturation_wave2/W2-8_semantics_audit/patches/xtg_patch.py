"""PROPOSED replacement for X-TASK-GATE's end-of-run competence readout (run_xtg.py lines 95-98). NOT applied.

Frozen readout (verbatim logic):
    r._validate(force=True)
    ci = r.spec.cue_index()
    comp = [o for o in alive if o.held >= HELD_MIN and o.probe >= ci + 1]

Defects it carries (REPORT.md D1, D6, D7, D15):
  * the post-run _validate is answered from val_cache (genome-keyed), so `held` may be another niche's task;
  * `ci` is the BASE spec's cue index; COEVO_ENV niches may run ANSWER_BEFORE_READ, where probe <= 2 < 3 always;
  * NEUTRAL_BRIDGE half credit lets a reader that ignores the regime score 0.75, so "competent" admits the
    non-conditional intermediate.

Proposed readout: score every live organism FRESH (no cache) on ITS OWN niche's task, with the bridge credit removed
(VALLEY scoring of the same episodes), and test the reader condition against that task's own cue index.
"""
from __future__ import annotations

HELD_MIN = 0.5


def frozen_competent(r, o, held_min=HELD_MIN):
    """run_xtg.py's inline expression, for side-by-side tests."""
    return o.held >= held_min and o.probe >= r.spec.cue_index() + 1


def readout(r, o, tasks, held_min=HELD_MIN):
    """-> dict(competent, held_exact, probe, cue_index, niche_spec). Pure: no world RNG, no cache, no state change."""
    spec = r._env_spec_for(o)
    exact = tasks.TaskSpec(transform=spec.transform, read_order=spec.read_order, bridge="VALLEY",
                           n_episodes=spec.n_episodes, budget=spec.budget, neutral=spec.neutral,
                           output_gate=spec.output_gate, cue_cost=spec.cue_cost)
    seed = r.seed * 7919 + r.epoch
    res = tasks.competence(r._genome(o), exact, seed=seed, held_seed=seed + 500000)
    ci = spec.cue_index()
    return {"competent": res["held"] >= held_min and res["reads_at_answer"] >= ci + 1,
            "held_exact": res["held"], "probe": res["reads_at_answer"], "cue_index": ci,
            "niche_spec": (spec.transform, spec.read_order)}
