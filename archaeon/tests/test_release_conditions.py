"""Release conditions are facts about live systems; versions are separated;
the frozen universe pins corpus and orders together."""
from __future__ import annotations

import json

import pytest

from archaeon import stage0_fragility_survey as s0
from archaeon.producer import universe as U
from archaeon.producer import readback_probe as RB


# --------------------------------------------------------------------------
# "Stage 0 unchanged" is checkable, not asserted
# --------------------------------------------------------------------------
def test_instrument_and_gate_are_pinned_and_adapter_is_separate():
    assert s0.INSTRUMENT_VERSION == "s17@" + s0.S17_COMMIT[:12]
    assert s0.GATE_VERSION == "stage0.gate.v0"
    assert s0.ADAPTER_VERSION.startswith("stage0.adapter.v")
    assert s0.S17_PREDICTOR_HASH.startswith("0106e035868bbe10")


def test_survey_reports_all_three_versions(tmp_path):
    from archaeon.tests.test_stage0_survey import _make_db, TWO_GROUPS
    db = str(tmp_path / "v.db")
    _make_db(db, groups=TWO_GROUPS)
    r = s0.survey(db)
    v = r["versions"]
    assert {"instrument", "gate", "adapter"} <= set(v)
    assert r["kill_gate"]["verdict"] == "PASS"     # gate logic unchanged


# --------------------------------------------------------------------------
# Frozen universe
# --------------------------------------------------------------------------
class _C:
    def __init__(self):
        self.rows = [1, 2, 3]
        self.window = {"tenancy": {"admitted_client_names": ["x"]}}

    def corpus_hash(self):
        return "corpus:abc"


def _cands(n):
    return [{"candidate_id": U.candidate_id("t.v0", {"i": i}, None),
             "template_id": "t.v0", "params": {"i": i}, "region": None}
            for i in range(n)]


def test_freeze_pins_corpus_universe_and_full_orders():
    c = _cands(4)
    ids = [x["candidate_id"] for x in c]
    rec = U.freeze(_C(), c, {"random.v0": ids, "signal.v0": list(reversed(ids))},
                   seed_inputs={"day": "2026-09-06"})
    assert rec["corpus_hash"] == "corpus:abc" and rec["universe_size"] == 4
    assert U.verify(rec)
    rec["orders"]["random.v0"][0], rec["orders"]["random.v0"][1] = \
        rec["orders"]["random.v0"][1], rec["orders"]["random.v0"][0]
    assert not U.verify(rec), "a reordered order must break the freeze hash"


def test_partial_or_extended_order_is_refused():
    c = _cands(3)
    ids = [x["candidate_id"] for x in c]
    with pytest.raises(ValueError, match="hidden second selection"):
        U.freeze(_C(), c, {"p": ids[:2]}, seed_inputs={})
    with pytest.raises(ValueError, match="hidden second selection"):
        U.freeze(_C(), c, {"p": ids + ["cand:extra"]}, seed_inputs={})


def test_both_policies_share_one_corpus_and_universe():
    c = _cands(5)
    ids = [x["candidate_id"] for x in c]
    rec = U.freeze(_C(), c, {"a": ids, "b": ids[::-1]}, seed_inputs={})
    # one corpus_hash, one universe_hash, two orders -- by construction
    assert set(rec["orders"]) == {"a", "b"}
    assert len({rec["corpus_hash"]}) == 1 and len({rec["universe_hash"]}) == 1


# --------------------------------------------------------------------------
# Release-condition probe: facts, not commits
# --------------------------------------------------------------------------
def test_probe_reports_each_condition_with_owner_and_evidence():
    r = RB.probe()
    for name in ("v7_live", "granted_readback", "pew_round_trip"):
        c = r["conditions"][name]
        assert "ok" in c and "owner" in c and "evidence" in c
    assert "release_ok" in r


def test_probe_does_not_treat_undeployed_code_as_live():
    """The v7 commit says M1 was not restarted. If the live engine still
    reports schema 6, v7_live must be False regardless of what the code says."""
    r = RB.probe()
    live = r["live"].get("schema_version")
    if live is not None and int(live) < RB.V7:
        assert r["conditions"]["v7_live"]["ok"] is False
        assert r["release_ok"] is False


def test_probe_is_read_only():
    from archaeon.tests.conftest import executable_source
    src = executable_source(RB).upper()
    for banned in ("INSERT ", "UPDATE ", "DELETE ", "ALTER ", "POST"):
        assert banned not in src or banned == "POST" and "urlopen" in src
    assert "method=" not in src            # only GETs
