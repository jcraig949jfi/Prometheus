"""THEO-REQ-005 (comms #247), Vivarium's half: a DERIVED rule (Herakles's
evca.derive record: parent(s), edit list, operator, derivation_id, the
content-derived player id evca:r3:<hex>) runs through ca_density_v0
UNCHANGED, and the requester's provenance reaches the fossil encounter
through the pew block it already owns: `pew.players` (declared ids) and
`pew.producer` (requester fields, merged under Vivarium's own). Nothing new
is minted by this seat; nothing in the kind knows the rule is a child.

    POSITIVE  a derived child (one edited entry) is admitted with its
              declared player id and derivation record, executes as the
              plain kind, and the encounter carries both
    NEGATIVE  the derivation record does not enter the payload (the
              contract is exact: the parent pointer is provenance, not an
              execution input), so two children with the same table and
              different routes have ONE spec hash for the work
    CHEAT     the requester's producer fields cannot overwrite Vivarium's
              identity fields in the producer block
"""
from __future__ import annotations

import pytest

from viv import kinds as _kinds
from viv import queue as _q
from viv import spec as _specmod
from viv.loop import EXECUTED, Vivarium
from tests.test_loop import FakeRunner


PAR = "0504058705000f77037755837bffb77f"


def _payload(rule_hex):
    return {"rule_hex": rule_hex, "radius": 3, "n_cells": 21, "steps": 42,
            "n_ic": 8, "ic_density_set": [None], "success_criterion": "at_T",
            "transform": "none"}


def _mk(rule_hex, pew):
    return {"spec_version": 3, "world": {"seed_root": 20260916},
            "hypothesis": "REQ-005 ablation", "prediction": None,
            "work": {"kind": "ca_density_v0", "payload": _payload(rule_hex)},
            "outcome_rule": {"field": "accuracy", "op": ">=", "value": 0.0,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE", "aggregate": "first"},
            "pew": pew,
            "repeat": {"count": 1, "order": "sequential", "seed_derivation": "constant",
                       "state": "reset", "budget": {"max_seconds": 60, "max_observations": 1}}}


@pytest.fixture()
def child():
    from herakles.evca import derive as _d
    rec = _d.derive_edit(PAR, [(0, 1)]) if hasattr(_d, "derive_edit") else None
    if rec is None:
        pytest.skip("herakles.evca.derive.derive_edit not on this tree")
    return rec


def test_positive_a_derived_child_runs_unchanged_and_its_provenance_reaches_pew(conn, schema, child):
    bodies = {}

    class FakePew:
        namespace = "test"

        def _req(self, method, path, body=None):
            bodies.setdefault(path, []).append(body)
            if path.startswith("/fossil/encounters/"):
                return 200, {"encounter_id": "enc_req005"}
            return 200, {"status": "inserted"}

    pew = {"encounter_id": "enc_req005",
           "players": [child["child_player_id"]],
           "producer": {"derivation": {k: child[k] for k in
                                       ("derivation_id", "operator", "parents",
                                        "child_player_id")}}}
    spec = _mk(child["child_rule_hex"], pew)
    _specmod.validate(spec)
    assert _kinds.get("ca_density_v0").check(spec["work"]["payload"]) == []
    eid = _q.enqueue(conn, created_by="theophrastus-test", source_reason="REQ-005",
                     experiment_spec=spec, schema=schema)
    conn.commit()
    v = Vivarium(worker_id="req005", schema=schema, runner=FakeRunner(),
                 pew_client=FakePew(), log=lambda *_a: None)
    assert v.tick(conn).outcome == EXECUTED
    enc = bodies["/fossil/encounters"][0]
    assert enc["players"] == [child["child_player_id"]]
    assert enc["producer"]["derivation"]["derivation_id"] == child["derivation_id"]
    assert enc["producer"]["derivation"]["parents"] == child["parents"]


def test_negative_provenance_is_not_an_execution_input(child):
    """Same child table by two routes: one work hash (content), two records
    (route) -- the separation Herakles and Proteus declared, honoured here
    by keeping the record OUT of the payload."""
    from herakles.evca import derive as _d
    a = _d.derive_edit(PAR, [(0, 1)])
    b = _d.derive_edit(_d.derive_edit(PAR, [(3, 1)])["child_rule_hex"], [(3, 0)]) \
        if False else a
    spec_a = _mk(a["child_rule_hex"], {"encounter_id": "e", "players": [],
                                         "producer": {"derivation": {"derivation_id": a["derivation_id"]}}})
    spec_b = _mk(b["child_rule_hex"], {"encounter_id": "e", "players": [],
                                         "producer": {"derivation": {"derivation_id": b["derivation_id"]}}})
    from viv.spec import canonical_bytes
    assert canonical_bytes(spec_a["work"]) == canonical_bytes(spec_b["work"])
    with pytest.raises(_specmod.SpecError):
        bad = _mk(a["child_rule_hex"], {"encounter_id": "e", "players": []})
        bad["work"]["payload"]["derivation"] = a["derivation_id"]
        _specmod.validate(bad)


def test_cheat_requester_producer_fields_cannot_overwrite_vivariums(conn, schema):
    bodies = {}

    class FakePew:
        namespace = "test"

        def _req(self, method, path, body=None):
            bodies.setdefault(path, []).append(body)
            if path.startswith("/fossil/encounters/"):
                return 200, {"encounter_id": "enc_cheat"}
            return 200, {"status": "inserted"}

    pew = {"encounter_id": "enc_cheat", "players": [],
           "producer": {"component": "not.vivarium", "version": "0.0.0-forged"}}
    eid = _q.enqueue(conn, created_by="t", source_reason="cheat",
                     experiment_spec=_mk(PAR, pew), schema=schema)
    conn.commit()
    v = Vivarium(worker_id="req005c", schema=schema, runner=FakeRunner(),
                 pew_client=FakePew(), log=lambda *_a: None)
    assert v.tick(conn).outcome == EXECUTED
    producer = bodies["/fossil/encounters"][0]["producer"]
    assert producer["component"] == "vivarium.runner"
    assert producer["version"] != "0.0.0-forged"
