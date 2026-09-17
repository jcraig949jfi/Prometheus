"""D2b (2026-09-16): every IMPLEMENTED kind names a value_checker, and the
checker is the function its executor calls at entry.

    POSITIVE  each kind's checker refuses a bad value with the field named,
              through spec.validate (admission)
    NEGATIVE  each kind's pinned-fixture payload passes its checker with
              no reasons (the fixtures in test_wp0f_fixtures.py are the
              known-good payloads)
    CHEAT     the executor and the checker agree: for every implemented
              kind, the executor module's run path references the same
              function the registry names (by identity, not by name), so
              a checker edited in one place cannot silently diverge
"""
from __future__ import annotations

import importlib

import pytest

from viv import kinds as _kinds
from viv import spec as _spec
from tests.test_wp0f_fixtures import FIXTURES, _CEGIS_PAYLOAD, _PROBE_PAYLOAD  # noqa: F401


def _checker(kind):
    mod, fn = _kinds.get(kind).value_checker.split(":")
    return getattr(importlib.import_module(mod), fn)


def test_every_implemented_kind_names_a_checker():
    missing = [name for name in _kinds.implemented()
               if not _kinds.get(name).retired
               and not _kinds.get(name).value_checker and name != "noop_v0"]
    assert missing == [], missing


@pytest.mark.parametrize("kind,payload,seed,_d", FIXTURES)
def test_negative_pinned_fixture_payloads_pass_their_checker(kind, payload, seed, _d):
    k = _kinds.get(kind)
    if not k.value_checker:
        pytest.skip("no checker (noop)")
    assert _checker(kind)(dict(payload)) == []
    assert k.check(dict(payload)) == []


BAD = [
    ("evaluate_bitstring", {"bits": "0" * 24, "length": 24}, {"length": 0}, "length"),
    ("evaluate_bitstring", {"bits": "0" * 24, "length": 24}, {"bits": "0" * 23}, "bits"),
    ("random_walk_v0", {"steps": 3, "step_scale": 1.0}, {"steps": 0}, "steps"),
    ("random_walk_v0", {"steps": 3, "step_scale": 1.0}, {"step_scale": "x"}, "step_scale"),
    ("eca_rule_eval_v1", {"rule_number": 110, "n_cells": 7, "steps": 8}, {"rule_number": 256}, "rule_number"),
    ("eca_rule_eval_v1", {"rule_number": 110, "n_cells": 7, "steps": 8}, {"steps": -1}, "steps"),
    ("cegis_boolean_v1", dict(_CEGIS_PAYLOAD), {"termination": "never"}, "termination"),
    ("cegis_boolean_v1", dict(_CEGIS_PAYLOAD), {"max_candidates": 0}, "max_candidates"),
    ("cegis_boolean_v1", dict(_CEGIS_PAYLOAD), {"target_truth_table": "01"}, "target_truth_table"),
    ("artifact_probe_v1", dict(_PROBE_PAYLOAD), {"reduction": "median"}, "reduction"),
]


@pytest.mark.parametrize("kind,good,bad,field", BAD)
def test_positive_a_bad_value_is_refused_at_admission_naming_its_field(kind, good, bad, field):
    payload = dict(good); payload.update(bad)
    reasons = _kinds.get(kind).check(payload)
    assert reasons and field in "\n".join(reasons), reasons
    spec = {"spec_version": 3, "world": {"seed_root": 1}, "hypothesis": "D2b",
            "prediction": None, "work": {"kind": kind, "payload": payload},
            "outcome_rule": {"field": "executor", "op": "==", "value": kind,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE", "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential", "seed_derivation": "constant",
                       "state": "reset", "budget": {"max_seconds": 60, "max_observations": 1}}}
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert field in "\n".join(exc.value.reasons)


@pytest.mark.parametrize("kind,runner_mod,run_name", [
    ("ca_density_v0", "viv.ca_density", "run"),
    ("cegis_boolean_v1", "viv.cegis_boolean", "run"),
    ("eca_rule_eval_v1", "viv.eca_rule_eval", "run"),
    ("artifact_probe_v1", "viv.artifact_probe", "run"),
    ("random_walk_v0", "viv.executors", "_random_walk_v0"),
    ("evaluate_bitstring", "viv.executors", "_evaluate_bitstring"),
])
def test_cheat_executor_calls_the_registered_checker_by_identity(kind, runner_mod, run_name, monkeypatch):
    """Replace the registered checker with one that records the call; the
    executor's run path must hit THAT object. A copy-pasted second checker
    in the executor would leave `seen` empty."""
    mod_name, fn_name = _kinds.get(kind).value_checker.split(":")
    mod = importlib.import_module(mod_name)
    seen = []

    def spy(payload):
        seen.append(dict(payload))
        return ["spy refusal"]

    monkeypatch.setattr(mod, fn_name, spy)
    runner = getattr(importlib.import_module(runner_mod), run_name)
    good = next(p for k, p, *_ in FIXTURES if k == kind)
    with pytest.raises(Exception) as exc:
        if runner_mod == "viv.executors":
            spec = {"work": {"kind": kind, "payload": dict(good)}}
            runner(spec, seed=1, state=None) if run_name == "_random_walk_v0" \
                else runner(spec, seed=1)
        elif kind in ("cegis_boolean_v1", "artifact_probe_v1"):
            runner(dict(good), seed=1, inputs={})
        else:
            runner(dict(good), seed=1)
    assert seen, "the executor did not call the registered checker"
    assert "spy refusal" in str(exc.value)
