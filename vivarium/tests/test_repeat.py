"""`repeat`: N observations in ONE world, with every axis declared.

Archaeon's blocker was that one queue row produced one world with one
observation, so no family could ever reach S17's >=4-observations-per-world
eligibility -- at any volume. This is that capability, and the four axes the
operator required are each tested for being DECLARED rather than defaulted:

    count            how many
    order            in what order they reach the ledger
    seed_derivation  how the seed moves between them
    state            whether executor state survives between them
    budget           what the whole thing is allowed to cost
"""
from __future__ import annotations

import copy
import json

import pytest

from conftest import ONE_REPEAT, make_spec
from test_blinding import RecordingClient, _runner_over
from viv import kinds as _kinds
from viv import spec as _spec
from viv.request import ExecutionRequest
from viv.runner import ExecutionFailure


def rep(**kw):
    out = copy.deepcopy(ONE_REPEAT)
    out.update(kw)
    out.setdefault("budget", {"max_seconds": 60,
                              "max_observations": out["count"]})
    if out["budget"]["max_observations"] < out["count"]:
        out["budget"]["max_observations"] = out["count"]
    return out


def walk_spec(count=4, state="persist", seed_derivation="sha256_index",
              steps=3, **kw):
    return make_spec(
        kind="random_walk_v0",
        outcome_rule={"field": "position", "op": ">=", "value": -1e18,
                      "if_true": "SURVIVED", "if_false": "FALSIFIED",
                      "if_indeterminate": "INCONCLUSIVE"},
        repeat=rep(count=count, state=state,
                   seed_derivation=seed_derivation), **kw)


def _walk_payload(spec, steps=3, scale=1.0):
    spec["work"] = {"kind": "random_walk_v0",
                    "payload": {"steps": steps, "step_scale": scale}}
    return spec


# --------------------------------------------------------------- declaration

@pytest.mark.parametrize("axis", ["count", "order", "seed_derivation",
                                  "state", "budget"])
def test_each_axis_must_be_declared(axis):
    spec = _walk_payload(walk_spec())
    del spec["repeat"][axis]
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert any(axis in r for r in exc.value.reasons)


def test_a_v3_spec_may_not_omit_repeat_entirely():
    spec = _walk_payload(walk_spec())
    del spec["repeat"]
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert any("repeat" in r for r in exc.value.reasons)


def test_v2_still_means_exactly_one_observation():
    """v2 had no repeat concept. That is its DEFINITION, not a default chosen
    now -- so a v2 spec stays admissible and resolves to one observation."""
    legacy = make_spec(legacy=True)
    assert _spec.validate(legacy) is legacy
    plan = _spec.repeat_plan(legacy)
    assert plan["count"] == 1
    assert plan["seeds"] == [legacy["world"]["seed_root"]]
    assert "spec_version 2" in plan["note"]


def test_a_v2_spec_carrying_a_repeat_block_is_refused_as_ambiguous():
    spec = make_spec(legacy=True)
    spec["repeat"] = rep(count=4)
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert any("predates" in r for r in exc.value.reasons)


# ------------------------------------------------------------ seed derivation

@pytest.mark.parametrize("how,expected", [
    ("constant", lambda s: [s, s, s]),
    ("linear_index", lambda s: [s, s + 1, s + 2]),
])
def test_seed_derivations_are_exact_and_declared(how, expected):
    spec = _walk_payload(walk_spec(count=3, seed_derivation=how))
    plan = _spec.repeat_plan(spec)
    assert plan["seeds"] == expected(spec["world"]["seed_root"])


def test_sha256_index_gives_distinct_well_spread_seeds():
    spec = _walk_payload(walk_spec(count=8, seed_derivation="sha256_index"))
    seeds = _spec.repeat_plan(spec)["seeds"]
    assert len(set(seeds)) == 8


def test_a_constant_seed_is_allowed_but_reported_as_degenerate():
    """Archaeon warned: one seed across repeats gives zero within-world
    variance and a unit that looks eligible while carrying no information.
    That is ARITHMETIC, not a judgement -- so Vivarium records it and still
    runs exactly what was asked."""
    spec = make_spec(kind="evaluate_bitstring",
                     repeat=rep(count=4, seed_derivation="constant",
                                state="reset"))
    plan = _spec.repeat_plan(spec)
    assert plan["degenerate_by_construction"] is True
    assert "zero by construction" in plan["note"]
    assert _spec.validate(spec) is spec        # allowed, not refused

    varied = make_spec(kind="evaluate_bitstring",
                       repeat=rep(count=4, seed_derivation="sha256_index",
                                  state="reset"))
    assert _spec.repeat_plan(varied)["degenerate_by_construction"] is False


# --------------------------------------------------------------------- state

def test_persist_is_refused_for_a_stateless_kind():
    """Otherwise a declared scientific choice would be a silent no-op."""
    spec = make_spec(kind="evaluate_bitstring",
                     repeat=rep(count=3, state="persist"))
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert any("stateless" in r for r in exc.value.reasons)
    assert _kinds.get("evaluate_bitstring").stateful is False
    assert _kinds.get("random_walk_v0").stateful is True


def test_reset_and_persist_produce_different_trajectories():
    """The whole reason a stateful kind exists: under reset the repeats are
    independent draws, under persist they are one trajectory."""
    from viv import executors as _ex

    spec = _walk_payload(walk_spec(count=4, state="reset"))
    seeds = _spec.repeat_plan(spec)["seeds"]

    reset_positions = []
    for s in seeds:
        reset_positions.append(
            _ex.run(spec, seed=s, state=_ex.new_state("random_walk_v0"))["position"])

    carried = _ex.new_state("random_walk_v0")
    persist_positions = [_ex.run(spec, seed=s, state=carried)["position"]
                         for s in seeds]

    assert reset_positions != persist_positions
    # under reset each run starts from 0; under persist the start moves
    assert all(abs(p) < 1e9 for p in reset_positions)
    assert persist_positions[-1] != reset_positions[-1]


# -------------------------------------------------------------------- budget

def test_count_may_not_exceed_the_declared_observation_budget():
    spec = _walk_payload(walk_spec(count=4))
    spec["repeat"]["budget"]["max_observations"] = 2
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert any("max_observations" in r for r in exc.value.reasons)


def test_a_non_positive_time_budget_is_refused():
    spec = _walk_payload(walk_spec(count=2))
    spec["repeat"]["budget"]["max_seconds"] = 0
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert any("max_seconds" in r for r in exc.value.reasons)


def test_exhausting_the_time_budget_fails_with_its_own_class():
    """A budget that stops a run mid-repeat is a declared bound doing its job,
    and must be distinguishable from an executor that broke."""
    spec = _walk_payload(walk_spec(count=6, state="reset"), steps=2)
    spec["repeat"]["budget"]["max_seconds"] = 1e-9   # exhausted immediately
    sealed = _spec.spec_hash(spec)
    client = RecordingClient()
    runner = _runner_over(client, sealed)
    req = ExecutionRequest(experiment_id="e",
                           spec_json=_spec.canonical_bytes(spec),
                           spec_hash=sealed)
    with pytest.raises(ExecutionFailure) as exc:
        runner.run(req)
    assert exc.value.failure_class == "BUDGET_EXCEEDED"
    assert "budget exhausted" in str(exc.value)
    # partial repeats are preserved, not discarded
    assert exc.value.partial.crossed_boundary is True


# ------------------------------------------------------- the execution itself

def _run(spec):
    sealed = _spec.spec_hash(spec)
    client = RecordingClient()
    runner = _runner_over(client, sealed)
    result = runner.run(ExecutionRequest(
        experiment_id="e", spec_json=_spec.canonical_bytes(spec),
        spec_hash=sealed))
    return result, client


def test_n_repeats_produce_n_observations_in_one_world():
    """The capability Archaeon asked for, stated as its own test."""
    result, client = _run(_walk_payload(walk_spec(count=4)))
    obs = [c for c in client.calls if c[0] == "observation"]
    worlds = {c[1]["wid"] for c in obs}
    exps = {c[1]["exp_id"] for c in obs}
    assert len(obs) == 4
    assert len(worlds) == 1 and len(exps) == 1
    assert len(result.obs_ids) == 4


def test_observations_carry_their_index_in_declared_order():
    result, client = _run(_walk_payload(walk_spec(count=4)))
    obs = [c for c in client.calls if c[0] == "observation"]
    assert [c[1]["content"]["repeat_index"] for c in obs] == [0, 1, 2, 3]
    assert all(c[1]["content"]["repeat_count"] == 4 for c in obs)
    assert result.order_check["checked"] and result.order_check["in_order"]


def test_repeats_after_the_first_are_declared_SFE_replications():
    """Same world, same experiment: SFE's is_repeat fires engine-side and its
    F3 guard requires the flag. This is the execution path where SFE's
    replication semantics genuinely apply."""
    _, client = _run(_walk_payload(walk_spec(count=3)))
    obs = [c for c in client.calls if c[0] == "observation"]
    assert [c[1]["replication"] for c in obs] == [False, True, True]


def test_one_work_item_carries_the_whole_trajectory():
    """There is no SFE route to enqueue a second work item for one experiment,
    so every observation cites a work result that genuinely contains it."""
    _, client = _run(_walk_payload(walk_spec(count=3)))
    completes = [c for c in client.calls if c[0] == "complete"]
    assert len(completes) == 1
    payload = completes[0][1]["result"]
    assert len(payload["repeats"]) == 3
    assert [r["repeat_index"] for r in payload["repeats"]] == [0, 1, 2]
    assert payload["repeat_plan"]["state"] == "persist"
    obs = [c for c in client.calls if c[0] == "observation"]
    assert {c[1]["work_id"] for c in obs} == {"wrk_fixed"}


def test_each_repeat_runs_under_its_own_derived_seed():
    result, _ = _run(_walk_payload(walk_spec(count=4)))
    seeds = [r["seed"] for r in result.repeats]
    assert seeds == _spec.repeat_plan(
        _walk_payload(walk_spec(count=4)))["seeds"]
    assert len(set(seeds)) == 4


def test_the_summary_records_every_declared_axis():
    result, _ = _run(_walk_payload(walk_spec(count=3, state="persist")))
    r = result.summary["repeat"]
    for axis in ("count", "order", "seed_derivation", "state", "budget",
                 "seeds", "degenerate_by_construction", "order_check",
                 "elapsed_s"):
        assert axis in r, "the record lost %s" % axis
    assert r["count"] == 3 and r["state"] == "persist"


def test_a_v2_spec_still_runs_as_one_observation():
    result, client = _run(make_spec(legacy=True))
    assert len([c for c in client.calls if c[0] == "observation"]) == 1
    assert result.summary["repeat"]["count"] == 1
