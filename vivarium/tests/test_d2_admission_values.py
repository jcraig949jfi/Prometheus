"""D2 (backlog, opened 2026-09-10; closed 2026-09-16): payload VALUES are
validated at ADMISSION, not only at execution.

The wound: Archaeon lost 24 rows of cs-c3-1 to `"ic_density_set": null`
where the contract wants `[null]`. The executor refused correctly -- after
each run had already created and COMMITTED a world and an experiment, and a
failed row is terminal. Every one of those 24 is now a committed-but-
unobserved orphan in the ledger.

Mechanism: a kind names a pure `value_checker` ("module:function") in the
registry; Kind.check() runs it once the keys are exact, so spec.validate()
-- which enqueue() calls before storing anything and the loop calls before
BUILD -- refuses the value. The executor calls the SAME function at its
entry, so the two cannot drift.

    POSITIVE  the exact payload that lost 24 rows is refused by
              spec.validate, by enqueue (no row is created), and by the
              loop's stage-2 validate on a pre-D2 row (before any world)
    NEGATIVE  a well-formed payload passes all three unchanged; a kind
              with no value_checker is untouched
    CHEAT     a checker that cannot be imported, or that raises, is a
              REFUSAL, never a pass; keys-wrong payloads do not reach the
              checker (the key reasons are the contract's first word)
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from viv import kinds as _kinds
from viv import queue as _q
from viv import spec as _spec

REPO = Path(__file__).resolve().parent.parent.parent
GOLDEN = REPO / "herakles" / "evca" / "tests" / "golden_c1b.json"
pytestmark = pytest.mark.skipif(not GOLDEN.exists(),
                                reason="herakles/evca is not on this branch")

PAR = "0504058705000f77037755837bffb77f"


def _spec_with(density_set):
    return {"spec_version": 3, "world": {"seed_root": 20260916},
            "hypothesis": "D2", "prediction": None,
            "work": {"kind": "ca_density_v0",
                     "payload": {"rule_hex": PAR, "radius": 3, "n_cells": 21,
                                 "steps": 42, "n_ic": 8,
                                 "ic_density_set": density_set,
                                 "success_criterion": "at_T",
                                 "transform": "none"}},
            "outcome_rule": {"field": "accuracy", "op": ">=", "value": 0.0,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 60, "max_observations": 1}}}


# ------------------------------------------------------------- positive

def test_the_payload_that_lost_24_rows_is_refused_at_validate():
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(_spec_with(None))
    text = "\n".join(exc.value.reasons)
    assert "ic_density_set" in text and "[null]" in text


def test_enqueue_refuses_it_and_creates_no_row(conn, schema):
    before = _q.counts(conn, schema=schema)
    with pytest.raises(_spec.SpecError):
        _q.enqueue(conn, created_by="d2-test", source_reason="D2 positive",
                   experiment_spec=_spec_with(None), schema=schema)
    assert _q.counts(conn, schema=schema) == before


def test_loop_stage2_refuses_a_pre_d2_row_before_build(conn, schema):
    """A row stored BEFORE the checker existed reaches the loop with the bad
    value inside; stage 2 (validate) refuses it, and nothing after stage 2
    -- build, world, dispatch -- runs. Stored by hand, bypassing enqueue."""
    import json
    from viv import loop as _loop
    spec = _spec_with(None)
    h = _spec.spec_hash(spec)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + schema + ".research_experiment_queue "
                    "(created_by, source_reason, experiment_spec, spec_hash) "
                    "VALUES (%s, %s, %s, %s) RETURNING experiment_id",
                    ("d2-test", "pre-D2 row", json.dumps(spec), h))
        eid = cur.fetchone()[0]
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    v = _loop.Vivarium.__new__(_loop.Vivarium)          # no engine, no config
    with pytest.raises(_spec.SpecError):
        v.validate(row)


# ------------------------------------------------------------- negative

def test_a_well_formed_payload_passes_unchanged():
    spec = _spec_with([None, 0.35, {"count": 5}])
    assert _spec.validate(spec) is spec
    assert _kinds.get("ca_density_v0").check(spec["work"]["payload"]) == []


def test_kinds_without_a_checker_are_untouched():
    k = _kinds.get("noop_v0")
    assert k.value_checker == ""
    assert k.check({}) == []


@pytest.mark.parametrize("bad,field", [
    ({"radius": 2}, "radius"), ({"n_cells": 20}, "n_cells"),
    ({"steps": -1}, "steps"), ({"n_ic": 0}, "n_ic"),
    ({"rule_hex": "zz"}, "rule_hex"), ({"transform": "rotate"}, "transform"),
    ({"success_criterion": "AT_T"}, "success_criterion"),
    ({"ic_density_set": []}, "ic_density_set"),
    ({"ic_density_set": [1.5]}, "ic_density_set"),
])
def test_every_value_refusal_names_its_field(bad, field):
    spec = _spec_with([None])
    spec["work"]["payload"].update(bad)
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(spec)
    assert field in "\n".join(exc.value.reasons)


# ---------------------------------------------------------------- cheat

def test_cheat_an_unimportable_checker_refuses_not_passes():
    k = dataclasses.replace(_kinds.get("ca_density_v0"),
                            value_checker="viv.no_such_module:nothing")
    reasons = k.check(_spec_with([None])["work"]["payload"])
    assert reasons and "could not be value-checked" in reasons[0]


def test_cheat_a_raising_checker_refuses_not_passes(monkeypatch):
    from viv import ca_density as _cd
    monkeypatch.setattr(_cd, "payload_problems",
                        lambda payload: (_ for _ in ()).throw(RuntimeError("boom")))
    reasons = _kinds.get("ca_density_v0").check(_spec_with([None])["work"]["payload"])
    assert reasons and "RuntimeError: boom" in reasons[0]


def test_cheat_wrong_keys_never_reach_the_checker(monkeypatch):
    from viv import ca_density as _cd
    called = []
    monkeypatch.setattr(_cd, "payload_problems", lambda p: called.append(p) or [])
    payload = _spec_with([None])["work"]["payload"]
    del payload["steps"]
    reasons = _kinds.get("ca_density_v0").check(payload)
    assert reasons and "missing" in reasons[0] and called == []
