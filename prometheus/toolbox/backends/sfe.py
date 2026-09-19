"""SFE lowering: Experiment IR -> archaeon.frontier.experiment_spec.v1 (the Deep Frontier scheduler's input,
archaeon/frontier/specs.py), which Vivarium/Archaeon execute against SFE.

STATUS 2026-09-18: PARTIAL, with the mismatches named (directive s5: never paper over). A frontier spec is
an EVOLUTION SEGMENT -- a population from a foundry or the C4 parents, `generations` of descent under the
campaign-6 segment evaluator, frozen detectors, tiered freezes. The kernel IR is an EXPERIMENT ON GIVEN
PLAYERS (or a selector-proposed population) under an explicit objective and observers. The two overlap
only where the IR says: selector = frontier segment, players = [] (the foundry proposes), world kind in the
frontier's WORLD_KINDS, objective = the segment's fixed reward, observers = the frozen detectors.

lower(exp, registry) -> Lowering
    OK                     when every IR field has a faithful frontier expression (job = validated spec dict)
    TARGET_UNSUPPORTED     otherwise, with one reason per unmappable field
    UNAVAILABLE_INTERFACE  when archaeon.frontier.specs cannot be imported on this tree
"""
from __future__ import annotations

from typing import Any, Dict, List

from prometheus.toolbox.ir import Experiment, Lowering

# IR world kind -> frontier world block builder. Only kinds the frontier evaluator can construct.
WORLD_MAP = {
    "world.c6.composed.v1":    lambda params: {"kind": "c6.composed.v1", "params": params},
    "world.c6.composed.sample": lambda params: {"kind": "c6.composed.sample", "seed": int(params.get("seed", 0)), "bin": params.get("bin")},
    "world.wse.v1":            lambda params: {"kind": "wse.WorldSpec", "knobs": params},
}
PROFILE_MAP = {"proteus.tape.v0": "v0", "proteus.graph.v1": "graph", "repb.fizzle.v1": "repb_fizzle"}
CONTROL_MAP = {"control.replay.v1": {"kind": "replay_A", "spec_delta": {}},
               "control.scratch.v1": {"kind": "initialization", "spec_delta": {"organism.population.seed": "+1"}}}
SELECTOR_KIND = "selector.frontier.segment.v1"     # the IR's name for "let the frontier's segment loop evolve the population"


def mismatches(exp: Experiment) -> List[str]:
    out: List[str] = []
    if exp.world["kind"] not in WORLD_MAP:
        out.append("world.kind %r has no frontier expression (frontier WORLD_KINDS: wse.WorldSpec, c6.composed.v1, c6.composed.sample); "
                   "a kernel world enters SFE only through a frontier world kind or a new executor kind Vivarium claims" % exp.world["kind"])
    if exp.selector is None or exp.selector.get("kind") != SELECTOR_KIND:
        out.append("frontier spec is an evolution segment (population x generations); IR without selector=%s has fixed players and no lowering" % SELECTOR_KIND)
    if exp.players:
        out.append("frontier populations come from a foundry or c4_parents; explicit PlayerSpecs cannot be injected (%d given)" % len(exp.players))
    if exp.substrate["kind"] != "substrate.flat.v1" and not exp.substrate["kind"].startswith("substrate.proteus"):
        out.append("substrate %r: the frontier runs Proteus runtimes only (profiles v0|graph|repb_fizzle)" % exp.substrate["kind"])
    prof = (exp.selector or {}).get("params", {}).get("profile")
    if prof is not None and prof not in PROFILE_MAP.values():
        out.append("selector.params.profile %r not in %s" % (prof, sorted(PROFILE_MAP.values())))
    if exp.objective and exp.objective["kind"] != "objective.frontier.segment_reward.v1":
        out.append("objective %r: the segment evaluator's reward (per_ask|episode) is fixed; only objective.frontier.segment_reward.v1 lowers" % exp.objective["kind"])
    for o in exp.observers:
        if o["kind"] != "observer.frontier.detectors.v1":
            out.append("observer %r: frontier observation is the frozen detector set; only observer.frontier.detectors.v1 lowers" % o["kind"])
    for c in exp.controls:
        if c["kind"] not in CONTROL_MAP:
            out.append("control %r has no frontier spec_delta (frontier controls: seed, initialization, budget, replay_A, replay_D)" % c["kind"])
    for iv in exp.interventions:
        if iv.get("wrappers"):
            out.append("intervention %r uses kernel wrappers %s; the frontier applies no observation wrappers (schedules only)" % (iv.get("name"), sorted(iv["wrappers"])))
    if exp.transforms:
        out.append("transforms are not part of a frontier spec (descent is the foundry grammar)")
    return out


def lower(exp: Experiment, registry) -> Lowering:
    eid = exp.experiment_id()
    reasons = mismatches(exp)
    if reasons:
        return Lowering("sfe", "TARGET_UNSUPPORTED", eid, reasons=reasons)
    try:
        from archaeon.frontier import specs as S
    except Exception as exc:                                    # noqa: BLE001
        return Lowering("sfe", "UNAVAILABLE_INTERFACE", eid, reasons=["archaeon.frontier.specs not importable: %s" % str(exc)[:120]])
    sp = exp.selector["params"]
    world = WORLD_MAP[exp.world["kind"]](dict(exp.world.get("params", {})))
    try:
        spec = S.make_spec(family_id=exp.family, world=world, profile=sp.get("profile", "v0"),
                           population={"source": sp.get("population_source", "foundry"), "seed": exp.seed_policy["base"], "N": int(sp.get("N", 8))},
                           E=int(exp.budget.get("episodes", 1)), generations=int(sp.get("generations", 1)), chunk=int(sp.get("chunk", 250)),
                           schedule={"kind": sp.get("schedule", "stable"), "seed": exp.seed_policy["base"]}, seed=exp.seed_policy["base"],
                           budget_evaluations=int(exp.budget.get("evaluations", int(sp.get("N", 8)) * int(sp.get("generations", 1)))),
                           lane=exp.provenance.get("lane", "PROCEDURAL") if exp.provenance.get("lane") in S.LANES else "PROCEDURAL",
                           generator="prometheus.toolbox.backends.sfe", controls=[CONTROL_MAP[c["kind"]] for c in exp.controls],
                           note="lowered from kernel IR %s" % eid)
    except Exception as exc:                                    # noqa: BLE001
        return Lowering("sfe", "TARGET_UNSUPPORTED", eid, reasons=["frontier validate_spec refused: %s" % str(exc)[:200]])
    return Lowering("sfe", "OK", eid, job=spec)
