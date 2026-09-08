"""WP-0b (Herakles F-4): structural degeneracy is about the DECLARATION.

`degenerate_by_construction` used to carry `not kind.stateful`, which said: a
stateful kind at a constant seed might still differ between repeats, so do not
call it degenerate. True under `persist`; false under `reset`, which is the
case being tested. Under reset each repeat is handed a fresh state object, so
nothing carries and a stateful kind is in exactly the same position as a
stateless one.

Two distinctions the tests hold apart:

  STRUCTURAL degeneracy   computed from the declaration, before execution:
                          "could these repeats have differed?"
  OBSERVED zero variance  a fact about numbers that came back. A result, not
                          a structural defect.

and: `stateful` is a CROSS-EXECUTION flag. It says whether state survives from
one repeat to the next, and nothing about state inside a single execution.
"""
from __future__ import annotations

import pytest

from conftest import make_spec
from test_repeat import rep
from viv import executors as _ex
from viv import kinds as _kinds
from viv import spec as _spec

WALK = {"kind": "random_walk_v0", "payload": {"steps": 4, "step_scale": 1.0}}
RULE = {"field": "position", "op": ">=", "value": -1e18,
        "if_true": "SURVIVED", "if_false": "FALSIFIED",
        "if_indeterminate": "INCONCLUSIVE", "aggregate": "all"}


def walk(count=4, state="reset", seed_derivation="constant"):
    s = make_spec(kind="random_walk_v0",
                  repeat=rep(count=count, state=state,
                             seed_derivation=seed_derivation))
    s["work"] = dict(WALK)
    s["outcome_rule"] = dict(RULE)
    return s


# ------------------------------------------------------------------- 0b-a

def test_0b_a_a_stateful_kind_under_reset_at_a_constant_seed_is_degenerate():
    """The whole point of the fix. Nothing carries under reset, so a constant
    seed makes every repeat the same computation whatever the kind."""
    s = walk(count=4, state="reset", seed_derivation="constant")
    assert _kinds.get("random_walk_v0").stateful is True
    plan = _spec.repeat_plan(s)
    assert plan["degenerate_by_construction"] is True
    assert "constant seed" in plan["note"] and "state=reset" in plan["note"]


def test_0b_a_and_the_replay_really_is_identical():
    """Structural degeneracy claims the repeats CANNOT differ. Executing them
    has to agree, or the flag is a story rather than arithmetic."""
    s = walk(count=4, state="reset", seed_derivation="constant")
    seeds = _spec.repeat_plan(s)["seeds"]
    assert len(set(seeds)) == 1
    results = [_ex.run(s, seed=sd, state=_ex.new_state("random_walk_v0"))
               for sd in seeds]
    positions = [r["position"] for r in results]
    assert len(set(positions)) == 1, positions
    assert all(r["start_position"] == 0.0 for r in results)


def test_0b_a_a_stateless_kind_is_still_degenerate_the_same_way():
    """The fix must not have swapped one kind-dependent answer for another."""
    s = make_spec(kind="evaluate_bitstring",
                  repeat=rep(count=4, state="reset",
                             seed_derivation="constant"))
    assert _kinds.get("evaluate_bitstring").stateful is False
    assert _spec.repeat_plan(s)["degenerate_by_construction"] is True


# ------------------------------------------------------------------- 0b-b

def test_0b_b_persist_is_never_auto_marked_degenerate():
    """Under persist the state DOES carry, so a constant seed still produces a
    trajectory. Declared behaviour, followed."""
    s = walk(count=4, state="persist", seed_derivation="constant")
    plan = _spec.repeat_plan(s)
    assert plan["degenerate_by_construction"] is False
    assert plan["note"] == ""

    carried = _ex.new_state("random_walk_v0")
    positions = [_ex.run(s, seed=sd, state=carried)["position"]
                 for sd in plan["seeds"]]
    assert len(set(positions)) == 4, "persist collapsed into one value"


@pytest.mark.parametrize("how", ["sha256_index", "linear_index"])
@pytest.mark.parametrize("state", ["reset", "persist"])
def test_0b_b_changing_seeds_are_never_degenerate(how, state):
    s = walk(count=4, state=state, seed_derivation=how)
    plan = _spec.repeat_plan(s)
    assert plan["degenerate_by_construction"] is False
    assert len(set(plan["seeds"])) == 4


def test_0b_b_count_one_is_not_degenerate_at_any_seed():
    """One repeat cannot have within-repeat variance to lose."""
    s = walk(count=1, state="reset", seed_derivation="constant")
    assert _spec.repeat_plan(s)["degenerate_by_construction"] is False


# ------------------------------------------------------------------- 0b-c

def test_0b_c_equal_measurements_across_different_trajectories_are_not_degenerate():
    """A constant SCORE across genuinely different runs is a RESULT. The flag
    is about the declaration, and must stay False here or it would be making
    a claim about the numbers."""
    s = walk(count=4, state="reset", seed_derivation="sha256_index")
    plan = _spec.repeat_plan(s)
    assert plan["degenerate_by_construction"] is False

    results = [_ex.run(s, seed=sd, state=_ex.new_state("random_walk_v0"))
               for sd in plan["seeds"]]
    # the trajectories genuinely differ...
    assert len({r["position"] for r in results}) == 4
    # ...while a field that is constant BY THE KIND'S CONTRACT does not, and
    # that observed constancy is not structural degeneracy.
    assert len({r["steps"] for r in results}) == 1
    assert _spec.repeat_plan(s)["degenerate_by_construction"] is False


def test_0b_c_the_flag_is_computed_without_running_anything():
    """Structural, therefore available before execution. If it needed results
    it would be observed variance wearing the wrong name."""
    s = walk(count=3, state="reset", seed_derivation="constant")
    plan = _spec.repeat_plan(s)          # no executor touched
    assert plan["degenerate_by_construction"] is True
    assert set(plan) >= {"count", "order", "seed_derivation", "state",
                         "budget", "seeds", "degenerate_by_construction"}


def test_0b_c_a_v2_spec_is_never_degenerate():
    """v2 is one observation. There is nothing to be degenerate between."""
    plan = _spec.repeat_plan(make_spec(legacy=True))
    assert plan["degenerate_by_construction"] is False
    assert plan["count"] == 1
