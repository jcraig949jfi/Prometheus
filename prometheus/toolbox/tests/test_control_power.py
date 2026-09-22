"""Control POWER (overnight C97; the C70/C95 lesson applied to the control slot): an expectation that can only
say MET is decoration. Before this file, one control (cheat) had a test where it said NOT_MET; the other seven
had never been seen to say anything but MET. Each test here builds the situation in which a control MUST say
NOT_MET or INDETERMINATE, and asserts that it does -- and that a well-formed run still reads MET."""
from __future__ import annotations

import itertools
import json
import pathlib

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry, ComponentRecord
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.ref.players import random_statemachine, random_statemachine_v2, constant_player
from prometheus.toolbox.ref.worlds import IntegerWorld

REG = default_registry()


def _exp(controls, world=None, players=None, substrate=None, objective="objective.yield_net.v1", n_seeds=2, **wp):
    params = dict(world_seed=4, n_players=1, start_charge=40, yield_amt=10); params.update(wp)
    return Experiment(family="ctrl_power", world=world or ref("world.integer.v1", **params), substrate=substrate or ref("substrate.flat.v1"),
                      players=players or [random_statemachine(3).manifest()], objective=ref(objective) if objective else None,
                      observers=[ref("observer.trace.v1"), ref("observer.series.v1")], controls=[ref(c) for c in controls],
                      seed_policy={"base": 1, "n_seeds": n_seeds}, budget={"episodes": 1, "horizon": 20})


def _run(e, tmp, name, registry=REG):
    low = lower(e, registry); assert low.ok, low.as_dict()
    return execute(low.job, pathlib.Path(tmp) / name, registry)


# ------------------------------------------------------------------------------------------ replay
def test_replay_says_not_met_for_a_world_that_lies_about_bit_replay(tmp_path):
    counter = itertools.count()

    class Drifting(IntegerWorld):                    # declares BIT, but every reset draws a fresh structure seed
        kind = "world.drifting.test"

        def reset(self, seed, keep=False):
            super().reset(seed + next(counter) * 1000003, keep)
    R = REG.fork(); R.register(ComponentRecord("world.drifting.test", "world", Drifting, IntegerWorld.capabilities, route="write", provenance={"author": "test"}, license="repository"))
    rep = _run(_exp(["control.replay.v1"], world=ref("world.drifting.test", world_seed=4)), tmp_path, "r.jsonl", R)
    assert rep.controls["replay"]["outcome"] == "NOT_MET" and rep.controls["replay"]["not_met"] == 2 and rep.valid is False
    rep = _run(_exp(["control.replay.v1"]), tmp_path, "ok.jsonl")
    assert rep.controls["replay"]["outcome"] == "MET"


# ------------------------------------------------------------------------------------------ negative
def test_negative_is_indeterminate_without_an_objective_and_not_met_when_the_abstainer_acts(tmp_path):
    rep = _run(_exp(["control.negative.v1"], objective=None), tmp_path, "n0.jsonl")
    assert rep.controls["negative"]["outcome"] == "INDETERMINATE", rep.controls["negative"]        # nothing to compare an abstainer against
    from prometheus.toolbox.ref import controls as CN

    class Loud(CN.NegativeControl):                  # a broken negative control whose "abstainer" acts
        def arm(self, exp, rng_seed):
            e = super().arm(exp, rng_seed); e.players = [constant_player([3, 3], meta={"control": "negative"}).manifest() for _ in exp.players]; return e
    R = REG.fork(); R.register(ComponentRecord("control.negative.v1", "control", Loud, frozenset(), route="write", provenance={"author": "test"}, license="repository"))
    rep = _run(_exp(["control.negative.v1"]), tmp_path, "n1.jsonl", R)
    assert rep.controls["negative"]["outcome"] == "NOT_MET" and rep.controls["negative"]["details"][0]["detail"]["arm_actions_total"] > 0
    rep = _run(_exp(["control.negative.v1"]), tmp_path, "n2.jsonl")
    assert rep.controls["negative"]["outcome"] == "MET"


# ------------------------------------------------------------------------------------------ positive
def test_positive_says_not_met_when_maximal_actions_cannot_move_the_world(tmp_path):
    rep = _run(_exp(["control.positive.v1"], act_cost=1000), tmp_path, "p.jsonl")       # every action refused for charge: trace equals the primary's
    assert rep.controls["positive"]["outcome"] == "NOT_MET" and rep.controls["positive"]["details"][0]["detail"]["trace_differs_from_primary"] is False
    rep = _run(_exp(["control.positive.v1"]), tmp_path, "p2.jsonl")
    assert rep.controls["positive"]["outcome"] == "MET"


# ------------------------------------------------------------------------------------------ sham
def test_sham_is_indeterminate_when_the_shuffle_changed_no_behaviour(tmp_path):
    # a one-cell machine: shuffling one cell is the identity; the sham arm's trace equals the primary's
    one = random_statemachine(3, n_states=1, n_buckets=1).manifest()
    rep = _run(_exp(["control.sham.v1"], players=[one]), tmp_path, "s0.jsonl")
    assert rep.controls["sham"]["outcome"] == "INDETERMINATE" and "no behaviour" in rep.controls["sham"]["details"][0]["detail"]["note"]
    rep = _run(_exp(["control.sham.v1"], players=[random_statemachine(3, n_states=6, n_buckets=8).manifest()]), tmp_path, "s1.jsonl")
    assert rep.controls["sham"]["outcome"] == "MET" and rep.controls["sham"]["details"][0]["detail"]["trace_differs_from_primary"] is True


# ------------------------------------------------------------------------------------------ scratch
def test_scratch_says_not_met_when_the_fresh_player_has_the_primary_genome(tmp_path):
    from prometheus.toolbox.ref import controls as CN

    class NotFresh:                                   # a broken "fresh" transform: returns the genome it was given
        kind = "transform.fresh_identity.test"; accepts = frozenset({"player.statemachine.v1"})
        def manifest(self): return {"kind": self.kind}
        def apply(self, spec, rng_seed):
            from prometheus.toolbox.contracts import PlayerSpec
            return PlayerSpec(spec["representation"], spec["payload"], spec.get("initial_state", {}), frozenset(spec.get("requires", ())), spec.get("meta", {}))
    R = REG.fork()
    R.register(ComponentRecord("transform.fresh_identity.test", "transform", NotFresh, frozenset(), route="write", provenance={"author": "test"}, license="repository"))

    class Scratch2(CN.ScratchControl):
        transform = "transform.fresh_identity.test"
    R.register(ComponentRecord("control.scratch.v1", "control", Scratch2, frozenset(), route="write", provenance={"author": "test"}, license="repository"))
    rep = _run(_exp(["control.scratch.v1"]), tmp_path, "sc0.jsonl", R)
    assert rep.controls["scratch"]["outcome"] == "NOT_MET" and rep.controls["scratch"]["details"][0]["detail"]["players_with_unchanged_genome"] == [0]
    rep = _run(_exp(["control.scratch.v1"]), tmp_path, "sc1.jsonl")
    assert rep.controls["scratch"]["outcome"] == "MET" and rep.controls["scratch"]["details"][0]["detail"]["players_with_unchanged_genome"] == []


# ------------------------------------------------------------------------------------------ permutation
def test_permutation_is_indeterminate_when_it_cannot_change_the_observation(tmp_path):
    rep = _run(_exp(["control.permutation.v1"], obs_regs=0), tmp_path, "pm0.jsonl")     # a 1-element observation (charge only) has one permutation
    assert rep.controls["permutation"]["outcome"] == "INDETERMINATE", rep.controls["permutation"]
    rep = _run(_exp(["control.permutation.v1"], obs_regs=4), tmp_path, "pm1.jsonl")
    assert rep.controls["permutation"]["outcome"] == "MET" and rep.controls["permutation"]["details"][0]["detail"]["trace_equal_to_primary"] is False


# ------------------------------------------------------------------------------------------ ablation
def test_ablation_says_not_met_when_the_ablated_arm_still_uses_a_workspace(tmp_path):
    from prometheus.toolbox.ref import controls as CN

    class Leaky(CN.AblationControl):                  # a broken ablation that forgets the substrate
        def arm(self, exp, rng_seed):
            e = super().arm(exp, rng_seed); e.substrate = dict(exp.substrate); return e
    R = REG.fork(); R.register(ComponentRecord("control.ablation.v1", "control", Leaky, frozenset(), route="write", provenance={"author": "test"}, license="repository"))
    v2 = random_statemachine_v2(5, write_every=1).manifest()
    rep = _run(_exp(["control.ablation.v1"], players=[v2], substrate=ref("substrate.kv.v1")), tmp_path, "a0.jsonl", R)
    assert rep.controls["ablation"]["outcome"] == "NOT_MET" and rep.controls["ablation"]["details"][0]["detail"]["arm_ws_ops"] > 0
    rep = _run(_exp(["control.ablation.v1"], players=[v2], substrate=ref("substrate.kv.v1")), tmp_path, "a1.jsonl")
    assert rep.controls["ablation"]["outcome"] == "MET"


# C129: the controls' vocabulary as a PROPERTY over random IRs: every outcome is MET / NOT_MET / INDETERMINATE; an
# INDETERMINATE pair carries a note or a missing/failed run; a sham or scratch MET pair has a changed trace and
# scratch a changed genome; a replay MET pair on a BIT world has equal traces; the job's valid flag is exactly
# "no failed, none unstarted, every control MET".
_CTRL_COVERAGE = {"pairs": 0, "kinds": set()}


@pytest.mark.parametrize("seed", list(range(900, 960)))
def test_control_vocabulary_over_random_compositions(tmp_path, seed):
    from prometheus.toolbox.tests.test_fuzz import random_experiment
    e = random_experiment(seed)
    if e.validate() or not e.controls:
        return
    low = lower(e, REG)
    if not low.ok:
        return
    rep = execute(low.job, tmp_path / "r.jsonl", REG)
    rows = {(r["arm"], json.dumps(r["sweep_point"], sort_keys=True), r["seed"]): r for r in read_all(tmp_path / "r.jsonl") if r["arm"] != "SUMMARY"}
    assert rep.valid == (rep.n_failed == 0 and rep.runs_not_started == 0 and all(c["outcome"] == "MET" for c in rep.controls.values()))
    for arm, c in rep.controls.items():
        assert c["outcome"] in ("MET", "NOT_MET", "INDETERMINATE") and c["pairs"] == c["met"] + c["not_met"] + c["indeterminate"]
        _CTRL_COVERAGE["kinds"].add(arm)
        prim = {k: r for k, r in rows.items() if k[0] == "primary"}
        for k, p in prim.items():
            a = rows.get((arm, k[1], k[2]))
            if a is None or a["status"] != "COMPLETED" or p["status"] != "COMPLETED":
                continue
            _CTRL_COVERAGE["pairs"] += 1
            ctrl = REG.make("control.%s.v1" % arm); o = ctrl.expectation(p, a)
            assert o["outcome"] in ("MET", "NOT_MET", "INDETERMINATE"), (seed, arm, o)
            if o["outcome"] == "INDETERMINATE":
                assert isinstance(o["detail"], dict) and ("note" in o["detail"] or "reason" in o["detail"]), (seed, arm, o)
            if arm in ("sham", "scratch") and o["outcome"] == "MET":
                assert p["trace_hashes"] != a["trace_hashes"], (seed, arm)
            if arm == "scratch" and o["outcome"] == "MET":
                assert all(p["science"]["player_fingerprints"][str(i)]["spec_hash"] != a["science"]["player_fingerprints"][str(i)]["spec_hash"] for i in o["detail"]["transformed_players"])
            if arm == "replay" and o["outcome"] == "MET" and p["replay_class"] == "BIT":
                assert p["trace_hashes"] == a["trace_hashes"]
            if arm == "cheat" and o["outcome"] == "MET":
                assert p["trace_hashes"] != a["trace_hashes"]


def test_the_control_property_was_actually_exercised():
    assert _CTRL_COVERAGE["pairs"] >= 30 and len(_CTRL_COVERAGE["kinds"]) >= 6, {"pairs": _CTRL_COVERAGE["pairs"], "kinds": sorted(_CTRL_COVERAGE["kinds"])}
