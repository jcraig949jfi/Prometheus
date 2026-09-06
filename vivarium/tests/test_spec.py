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
    good = make_spec()
    cases = {
        "not an object": [],
        "unknown key": {**good, "sneaky": 1},
        "missing work": {k: v for k, v in good.items() if k != "work"},
        "omitted prediction": {k: v for k, v in good.items()
                               if k != "prediction"},
        "omitted pew": {k: v for k, v in good.items() if k != "pew"},
        "wrong version": {**good, "spec_version": 1},
        "unregistered kind": {**good, "work": {"kind": "rm_rf", "payload": {}}},
        "seed not an int": {**good, "world": {"seed_root": "424242"}},
        "bool is not an int": {**good, "world": {"seed_root": True}},
        "seed missing": {**good, "world": {}},
        "empty hypothesis": {**good, "hypothesis": ""},
    }
    for label, bad in cases.items():
        with pytest.raises(_spec.SpecError) as exc:
            _spec.validate(bad)
        assert exc.value.reasons, label


@pytest.mark.parametrize("field", ["notes", "experiment_kind", "family_id",
                                   "arm_id", "arm", "candidate_set_id",
                                   "policy", "created_by", "source_evidence",
                                   "spec_hash", "request_key"])
def test_provenance_is_banished_from_the_sealed_spec(field):
    """The measured F2 offenders and the whole relation vocabulary. Each one
    would change spec_hash without changing what is executed."""
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate({**make_spec(), field: "anything"})
    assert any(field in reason for reason in exc.value.reasons)


def test_world_name_is_not_accepted_and_is_derived_instead():
    bad = make_spec()
    bad["world"] = {"seed_root": 1, "name": "C_fossil-w"}
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(bad)
    assert any("world.name" in r for r in exc.value.reasons)

    h = _spec.spec_hash(make_spec())
    assert _spec.world_name(h) == "viv-" + h[7:23]


def test_a_kind_contract_forbids_both_missing_and_extra_parameters():
    """No defaults: `length` used to fall back to 24, which silently changed
    the hidden target and therefore the landscape."""
    missing = make_spec(kind="evaluate_bitstring")
    del missing["work"]["payload"]["length"]
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(missing)
    assert any("length" in r for r in exc.value.reasons)

    extra = make_spec(kind="evaluate_bitstring")
    extra["work"]["payload"]["tuning"] = 3
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(extra)
    assert any("tuning" in r for r in exc.value.reasons)

    ok = make_spec(kind="evaluate_bitstring")
    assert _spec.validate(ok) is ok


def test_an_external_kind_is_registrable_but_not_executable():
    """A candidate registered before selection need not be runnable today."""
    spec = {**make_spec(),
            "work": {"kind": "archaeon.probe.v0",
                     "payload": {"procedure": "archaeon.probe.v0",
                                 "probe_kind": "RESAMPLE_REGION",
                                 "replicates": 16, "worlds": ["w"],
                                 "players": [], "target": {},
                                 "hold_fixed": "region", "controls": []}},
            "outcome_rule": None}
    assert _spec.validate(spec) is spec
    assert _spec.is_executable(spec) is False
    assert _spec.is_executable(make_spec()) is True


def test_an_executable_kind_must_declare_an_outcome_rule():
    """SFE records an outcome for every observation and Vivarium authors none."""
    spec = {**make_spec(), "outcome_rule": None}
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert any("outcome_rule is required" in r for r in exc.value.reasons)


def test_validation_never_repairs_a_spec():
    """A malformed experiment must not silently mutate into a different one."""
    good = make_spec()
    before = copy.deepcopy(good)
    assert _spec.validate(good) is good
    assert good == before


def test_outcome_rule_is_applied_mechanically():
    rule = {"field": "score", "op": ">=", "value": 1.0,
            "if_true": "SURVIVED", "if_false": "FALSIFIED",
            "if_indeterminate": "INCONCLUSIVE"}
    spec = make_spec(kind="evaluate_bitstring", outcome_rule=rule)
    assert _spec.apply_outcome_rule(spec, {"score": 1.0})[0] == "SURVIVED"
    assert _spec.apply_outcome_rule(spec, {"score": 0.9})[0] == "FALSIFIED"


def test_if_indeterminate_is_required_and_is_the_requesters_branch():
    """Vivarium used to author INCONCLUSIVE under a condition the requester
    never anticipated. Now the branch is declared, and Vivarium takes it."""
    incomplete = {"field": "score", "op": ">=", "value": 1.0,
                  "if_true": "SURVIVED", "if_false": "FALSIFIED"}
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(make_spec(kind="evaluate_bitstring",
                                 outcome_rule=incomplete))
    assert any("if_indeterminate" in r for r in exc.value.reasons)

    # The requester may declare ANY branch, including a non-INCONCLUSIVE one.
    for declared in ("INCONCLUSIVE", "FALSIFIED"):
        rule = {**incomplete, "if_indeterminate": declared}
        spec = make_spec(kind="evaluate_bitstring", outcome_rule=rule)
        out, prov = _spec.apply_outcome_rule(spec, {"other": 3})
        assert out == declared and prov["reason"] == "field_absent"
        out, prov = _spec.apply_outcome_rule(spec, {"score": "not a number"})
        assert out == declared and prov["reason"] == "uncomparable"


def test_apply_outcome_rule_refuses_a_spec_with_no_rule():
    """Unreachable for an executable kind, and must never silently default."""
    with pytest.raises(_spec.SpecError):
        _spec.apply_outcome_rule({**make_spec(), "outcome_rule": None},
                                 {"score": 1.0})


def test_pew_block_requires_declared_scientific_identity():
    with pytest.raises(_spec.SpecError):
        _spec.validate(make_spec(pew={"players": ["p1"]}))
    # players MAY be empty -- an execution with no declared player is legal --
    # but encounter_id is the requester's and Vivarium never mints one.
    _spec.validate(make_spec(pew={"encounter_id": "enc_1", "players": []}))
    _spec.validate(make_spec(pew={"encounter_id": "enc_1",
                                  "players": ["p1"]}))
