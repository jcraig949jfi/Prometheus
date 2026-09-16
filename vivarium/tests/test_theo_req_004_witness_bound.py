"""THEO-REQ-004 (comms #246, 2026-09-14): a COMPLETE witness of exactly
WITNESS_LIMIT entries was refused as "exactly at its declared maximum and the
executor declared no truncation", and row theo:*:rou1 FAILED after 6 of 8
repeats on a repeat with exactly 64 wrong of 100.

The validator's rule is kept: a vector at its ceiling is legal only with the
executor's word. The defect was that the executor only spoke when the bound
BIT; it now declares the truncation state of every bounded vector both ways,
from the same full `wrong` array. Neither the library's definition
(truncated = wrong.size > limit) nor the validator's boundary moves.

The ceiling is driven down to the fixture's known wrong-count (par genome,
n_ic 16: exactly 2 wrong, witness [6, 8]) so the exactly-at-ceiling case is
executed, not simulated.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from viv import ca_density as _cd
from viv import executors as _ex
from viv import kinds as _kinds
from viv.result_schema import ResultSchemaError, validate_result
from viv.result_schema import Field as R

REPO = Path(__file__).resolve().parent.parent.parent
GOLDEN = REPO / "herakles" / "evca" / "tests" / "golden_c1b.json"
pytestmark = pytest.mark.skipif(not GOLDEN.exists(),
                                reason="herakles/evca is not on this branch")

PAR = "0504058705000f77037755837bffb77f"


def _spec(n_ic=16, seed=20260908):
    return {"spec_version": 3, "world": {"seed_root": seed},
            "hypothesis": "THEO-REQ-004", "prediction": None,
            "work": {"kind": "ca_density_v0",
                     "payload": {"rule_hex": PAR, "radius": 3, "n_cells": 21,
                                 "steps": 42, "n_ic": n_ic,
                                 "ic_density_set": [None],
                                 "success_criterion": "at_T",
                                 "transform": "none"}},
            "outcome_rule": {"field": "accuracy", "op": ">=", "value": 0.0,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 300, "max_observations": 1}}}


@pytest.fixture()
def ceiling(monkeypatch):
    """Drive the executor's bound and the kind's declared bound to `n`
    together, which is the invariant ca_density.py states they share."""
    kind = _kinds.get("ca_density_v0")

    def set_to(n):
        monkeypatch.setattr(_cd, "WITNESS_LIMIT", n)
        for name in ("misclassified_ic", "witness"):
            monkeypatch.setitem(kind.result_schema, name,
                                dataclasses.replace(kind.result_schema[name],
                                                    bounds=(0, n)))
    return set_to


def test_fixture_has_exactly_two_wrong():
    out = _ex.run(_spec(), seed=20260908, state=None)
    assert out["misclassified_ic"] == [6, 8]
    assert out["n_incorrect_at_T"] == 2


def test_positive_a_complete_witness_exactly_at_the_ceiling_is_accepted(ceiling):
    ceiling(2)
    out = _ex.run(_spec(), seed=20260908, state=None)      # validates inside
    assert out["misclassified_ic"] == [6, 8]
    assert out["witness_truncated"] is False
    meta = _kinds.get("ca_density_v0").check_result(
        dict(out), truncation={"misclassified_ic": False, "witness": False})
    assert meta["vectors"]["misclassified_ic"]["length"] == 2
    assert meta["vectors"]["misclassified_ic"]["truncated"] is False


def test_positive_a_witness_that_the_bound_bit_is_declared_truncated(ceiling):
    ceiling(1)
    out = _ex.run(_spec(), seed=20260908, state=None)
    assert out["misclassified_ic"] == [6]
    assert out["witness_truncated"] is True
    assert out["n_incorrect_at_T"] == 2                     # the count survives


def test_executor_declares_both_ways():
    from viv.ca_density import run as cd_run
    spec = _spec()
    out = cd_run(spec["work"]["payload"], seed=20260908)
    assert out["_truncated"] == {"misclassified_ic": False, "witness": False}


def test_negative_the_validator_still_refuses_an_undeclared_vector_at_ceiling():
    """The rule the defect was mistaken for is unchanged."""
    vec = {"witness": R("vector", element="integer", bounds=(0, 2)),
           "accuracy": R("number")}
    body = {"witness": [6, 8], "accuracy": 0.875, "executor": "k",
            "reproducibility": "BIT_DETERMINISTIC"}
    with pytest.raises(ResultSchemaError) as exc:
        validate_result("k", vec, body)
    assert any("declared no truncation" in r for r in exc.value.reasons)
    meta = validate_result("k", vec, body, truncation={"witness": False})
    assert meta["vectors"]["witness"]["truncated"] is False


def test_cheat_declaring_complete_does_not_admit_a_vector_over_the_ceiling():
    """An executor's word covers the ceiling case only; it cannot talk a
    65-entry vector past a bound of 64."""
    vec = {"witness": R("vector", element="integer", bounds=(0, 2)),
           "accuracy": R("number")}
    body = {"witness": [1, 2, 3], "accuracy": 0.5, "executor": "k",
            "reproducibility": "BIT_DETERMINISTIC"}
    with pytest.raises(ResultSchemaError) as exc:
        validate_result("k", vec, body, truncation={"witness": False})
    assert any("above the declared maximum 2" in r for r in exc.value.reasons)


def test_cegis_declares_both_ways_too():
    from viv import cegis_boolean as _cb
    from tests.test_wp0f_fixtures import _CEGIS_PAYLOAD
    out = _cb.run(dict(_CEGIS_PAYLOAD), seed=20260910, inputs={})
    assert out["_truncated"] == {"witnesses": out["witness_truncated"]}
    assert out["witness_truncated"] is False


# ------------------------------------------------- (2) the per-IC mask

def _unpack(hex_mask: str, n: int):
    import numpy as np
    b = np.frombuffer(bytes.fromhex(hex_mask), dtype=np.uint8)
    return np.unpackbits(b, bitorder="big")[:n].astype(bool)


def test_mask_positive_unpacks_to_the_witness_and_the_digest():
    import hashlib
    import numpy as np
    out = _ex.run(_spec(), seed=20260908, state=None)
    n = out["n_ic_total"]
    mask = _unpack(out["success_mask_hex"], n)
    assert len(out["success_mask_hex"]) == 2 * ((n + 7) // 8)
    assert sorted(np.flatnonzero(~mask).tolist()) == out["misclassified_ic"]
    assert int(mask.sum()) == n - out["n_incorrect_at_T"]
    assert ("sha256:" + hashlib.sha256(mask.astype(np.uint8).tobytes())
            .hexdigest()[:32]) == out["mask_digest"]


def test_mask_follows_the_declared_criterion():
    """Under `stable` the mask is the stable mask, and its digest says so."""
    import hashlib
    import numpy as np
    spec = _spec()
    spec["work"]["payload"]["success_criterion"] = "stable"
    out = _ex.run(spec, seed=20260908, state=None)
    mask = _unpack(out["success_mask_hex"], out["n_ic_total"])
    d = "sha256:" + hashlib.sha256(mask.astype(np.uint8).tobytes()).hexdigest()[:32]
    assert d == out["mask_digest_stable"] == out["mask_digest"]


def test_mask_survives_a_bitten_witness_bound(ceiling):
    """The whole point: with the witness cut to 1 entry the mask still names
    both failing ICs."""
    import numpy as np
    ceiling(1)
    out = _ex.run(_spec(), seed=20260908, state=None)
    assert out["misclassified_ic"] == [6]
    mask = _unpack(out["success_mask_hex"], out["n_ic_total"])
    assert np.flatnonzero(~mask).tolist() == [6, 8]


def test_mask_cheat_a_padding_bit_cannot_pose_as_an_ic():
    """n_ic_total = 16 fills exactly two bytes; at 17 the pad is zero and is
    NOT counted as a failure by a reader that honours n_ic_total."""
    import numpy as np
    out = _ex.run(_spec(n_ic=17), seed=20260908, state=None)
    raw = np.unpackbits(np.frombuffer(bytes.fromhex(out["success_mask_hex"]),
                                      dtype=np.uint8), bitorder="big")
    assert raw.size == 24 and not raw[17:].any()
    mask = _unpack(out["success_mask_hex"], 17)
    assert np.flatnonzero(~mask).tolist() == out["misclassified_ic"]


def test_mask_is_the_librarys_encoding_under_at_T():
    """One encoding, one owner: under at_T the kind's field is byte-identical
    to core.classify's correct_mask_hex, and core.unpack_mask_hex inverts it."""
    import numpy as np
    from viv.ca_density import _evca
    core = _evca()[1]
    out = _ex.run(_spec(), seed=20260908, state=None)
    p = _spec()["work"]["payload"]
    table = core.decode_table(p["rule_hex"]) if hasattr(core, "decode_table") \
        else core.require_table(core.parse_table(p["rule_hex"]))
    ics = core.make_ics(p["n_ic"], p["n_cells"], 20260908)
    lib = core.classify(table, ics, p["steps"])
    assert out["success_mask_hex"] == lib["correct_mask_hex"]
    mask = core.unpack_mask_hex(out["success_mask_hex"], out["n_ic_total"])
    assert np.flatnonzero(~mask.astype(bool)).tolist() == out["misclassified_ic"]
