"""Specification hashing and validation."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

from conftest import make_spec
from viv import spec as _spec

ENGINE = Path(__file__).resolve().parent.parent.parent / \
    "SerendipityFoundry" / "SerendipityFoundryEngine"


def test_same_specification_hashes_identically():
    a, b = make_spec(), make_spec()
    assert a == b
    assert _spec.spec_hash(a) == _spec.spec_hash(b)


def test_key_order_does_not_change_the_hash():
    a = make_spec()
    b = {k: a[k] for k in reversed(list(a))}
    assert list(a) != list(b)
    assert _spec.spec_hash(a) == _spec.spec_hash(b)


def test_changed_specification_hashes_differently():
    a = make_spec()
    for mutate in (lambda s: s["world"].__setitem__("seed_root", 424243),
                   lambda s: s["work"]["payload"].__setitem__("bits", "1" * 24),
                   lambda s: s.__setitem__("hypothesis", "something else")):
        b = copy.deepcopy(a)
        mutate(b)
        assert _spec.spec_hash(a) != _spec.spec_hash(b)


@pytest.mark.skipif(not ENGINE.exists(), reason="engine source not on this host")
def test_hash_matches_the_engine_canonicalization():
    """The queue's hash must be the hash SFE seals, or the two records are
    about different objects. Drift here is a test failure, not a surprise in
    production."""
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))
    from sfe.ids import content_hash

    for obj in (make_spec(), {"z": [1, {"a": None}], "é": "ü"}, {}, {"n": 1.5}):
        assert _spec.spec_hash(obj) == content_hash(obj)


def test_malformed_specifications_are_rejected_with_reasons():
    cases = {
        "not an object": [],
        "unknown key": {**make_spec(), "sneaky": 1},
        "missing work": {k: v for k, v in make_spec().items() if k != "work"},
        "wrong version": {**make_spec(), "spec_version": 2},
        "unknown executor": {**make_spec(),
                             "work": {"kind": "rm_rf", "payload": {}}},
        "seed not an int": {**make_spec(),
                            "world": {"name": "w", "seed_root": "424242"}},
        "bool is not an int": {**make_spec(),
                               "world": {"name": "w", "seed_root": True}},
        "empty hypothesis": {**make_spec(), "hypothesis": ""},
    }
    for label, bad in cases.items():
        with pytest.raises(_spec.SpecError) as exc:
            _spec.validate(bad)
        assert exc.value.reasons, label


def test_validation_never_repairs_a_spec():
    """A malformed experiment must not silently mutate into a different one."""
    good = make_spec()
    before = copy.deepcopy(good)
    assert _spec.validate(good) is good
    assert good == before


def test_outcome_rule_is_applied_mechanically():
    rule = {"field": "score", "op": ">=", "value": 1.0,
            "if_true": "SURVIVED", "if_false": "FALSIFIED"}
    spec = make_spec(outcome_rule=rule)
    assert _spec.apply_outcome_rule(spec, {"score": 1.0})[0] == "SURVIVED"
    assert _spec.apply_outcome_rule(spec, {"score": 0.9})[0] == "FALSIFIED"


def test_absent_rule_or_absent_field_is_inconclusive_not_negative():
    """A missing measurement is not a negative measurement."""
    outcome, prov = _spec.apply_outcome_rule(make_spec(), {"score": 1.0})
    assert outcome == "INCONCLUSIVE" and prov["reason"] == "no_outcome_rule_declared"

    rule = {"field": "score", "op": ">=", "value": 1.0,
            "if_true": "SURVIVED", "if_false": "FALSIFIED"}
    outcome, prov = _spec.apply_outcome_rule(make_spec(outcome_rule=rule),
                                             {"other": 3})
    assert outcome == "INCONCLUSIVE" and prov["reason"] == "field_absent"

    outcome, prov = _spec.apply_outcome_rule(make_spec(outcome_rule=rule),
                                             {"score": "not a number"})
    assert outcome == "INCONCLUSIVE" and prov["reason"] == "uncomparable"


def test_pew_block_requires_declared_scientific_identity():
    with pytest.raises(_spec.SpecError):
        _spec.validate(make_spec(extra={"pew": {"players": ["p1"]}}))
    with pytest.raises(_spec.SpecError):
        _spec.validate(make_spec(extra={"pew": {"encounter_id": "enc_1",
                                                "players": []}}))
    _spec.validate(make_spec(extra={"pew": {"encounter_id": "enc_1",
                                            "players": ["p1"]}}))
