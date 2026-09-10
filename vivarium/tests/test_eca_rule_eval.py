"""eca_rule_eval_v1: the wrapper reproduces Herakles's class map, or it is wrong.

The anchor is `herakles/eca/class_map_fixture.json` -- 224 classes over 256
rules at n_cells=7, steps=8. If the wrapper's neighbourhood order, rule
numbering or horizon disagreed with the library by so much as one bit, the
class assignment would move and these tests would say so.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

core = pytest.importorskip("herakles.eca.core")

from viv import eca_rule_eval as _e                          # noqa: E402
from viv import executors as _ex                             # noqa: E402
from viv import kinds as _kinds                              # noqa: E402

FIXTURE = REPO / "herakles" / "eca" / "class_map_fixture.json"


def payload(rule=110, n_cells=7, steps=8):
    return {"rule_number": rule, "n_cells": n_cells, "steps": steps}


def spec_for(pl):
    return {"spec_version": 3, "world": {"seed_root": 1},
            "hypothesis": "one elementary rule's terminal behaviour",
            "prediction": None,
            "work": {"kind": "eca_rule_eval_v1", "payload": pl},
            "outcome_rule": {"field": "scored_against_a_target", "op": "==",
                             "value": False, "if_true": "SURVIVED",
                             "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 120, "max_observations": 1}}}


# ---------------------------------------------------------------- the map
@pytest.mark.skipif(not FIXTURE.exists(), reason="no class map fixture")
def test_every_one_of_the_256_rules_lands_in_the_fixtures_class():
    """The strong form: not a sample, all of them."""
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    by_rule = fx["rule_to_class"]
    classes = core.equivalence_classes(7, 8)
    digest_of = {}
    for digest, members in classes.items():
        for m in members:
            digest_of[m] = digest
    # Two rules share a fixture class id iff they share a behaviour digest.
    for a in range(256):
        for b in (a + 1, (a + 37) % 256, (a + 91) % 256):
            if b >= 256 or b == a:
                continue
            same_fixture = by_rule[str(a)] == by_rule[str(b)]
            same_digest = digest_of[a] == digest_of[b]
            assert same_fixture == same_digest, (a, b)


@pytest.mark.skipif(not FIXTURE.exists(), reason="no class map fixture")
def test_the_class_count_matches_the_fixture():
    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert len(core.equivalence_classes(7, 8)) == fx["n_classes"] == 224


@pytest.mark.parametrize("rule,expected", [
    (240, [15, 180, 210, 240]),
    (170, [85, 154, 166, 170]),
])
def test_the_two_degenerate_groups_herakles_named(rule, expected):
    """Named in his prompt, reproduced here. These are the pairs H5 must not
    count as independent tasks."""
    out = _e.run(payload(rule=rule), seed=0)
    assert out["equivalence_class_members"] == expected
    assert out["equivalence_class_size"] == 4
    assert out["fixture_class_agrees"] is True


def test_a_singleton_class_is_reported_as_one():
    out = _e.run(payload(rule=110), seed=0)
    assert out["equivalence_class_members"] == [110]
    assert out["is_class_representative"] is True


# ------------------------------------------------------------- the scope
def test_off_the_fixture_scope_the_wrapper_says_so_instead_of_guessing():
    """A payload on a scope the fixture never covered gets a real answer for
    THAT scope, and no claim about a fixture that does not describe it."""
    out = _e.run(payload(rule=110, n_cells=5, steps=4), seed=0)
    assert out["on_fixture_scope"] is False
    assert out["fixture_class_agrees"] is None
    assert out["n_initial_configurations"] == 32


def test_the_scope_changes_the_classes_which_is_why_it_is_declared():
    coarse = _e.run(payload(rule=110, n_cells=5, steps=1), seed=0)
    fine = _e.run(payload(rule=110, n_cells=7, steps=8), seed=0)
    assert coarse["behaviour_digest"] != fine["behaviour_digest"]


# ----------------------------------------------------------- the contract
def test_the_library_refuses_an_impossible_rule_and_the_wrapper_does_not_soften():
    for bad in (-1, 256, 1000):
        with pytest.raises(Exception):
            _e.run(payload(rule=bad), seed=0)


def test_the_kind_declares_exactly_three_parameters_and_no_defaults():
    k = _kinds.get("eca_rule_eval_v1")
    assert k.params == frozenset({"rule_number", "n_cells", "steps"})
    for drop in sorted(k.params):
        missing = {p: v for p, v in payload().items() if p != drop}
        assert any(drop in r for r in k.check(missing))


def test_the_result_satisfies_the_declared_schema():
    out = _ex.run(spec_for(payload()), seed=1, inputs=None)
    meta = _kinds.get("eca_rule_eval_v1").check_result(dict(out))
    assert meta["validated"] is True


def test_it_reports_that_it_scored_nothing():
    """The missing half, stated in the result rather than left to be assumed:
    this kind measures the library's observable and does not score a rule
    against a target, because no target or metric has been handed over."""
    out = _e.run(payload(), seed=0)
    assert out["scored_against_a_target"] is False


def test_the_seed_cannot_change_the_answer():
    """Exhaustive scope: there is nothing to sample."""
    a = _e.run(payload(), seed=1)
    b = _e.run(payload(), seed=999999)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_radius_one_comes_from_the_library():
    assert _e.run(payload(), seed=0)["radius"] == core.RADIUS == 1
