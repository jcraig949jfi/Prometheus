"""The Kairos claim lint tests its own claims (base rule 3: instrument self-falsification).

negative: a fully declared packet yields nothing (the lint does not hallucinate).
positive: planted omissions yield exactly the planted codes (the lint detects real signal).
cheat:    every key present, no property behind it, yields exactly the planted codes
          (the lint reads the property, never the label).
Plus: determinism, order-insensitivity over experiments, the gate-inside-SE case,
and the rule that INCONCLUSIVE claims are not attacked for missing positives.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

SCIENCE = Path(__file__).resolve().parents[1]   # roles/Kairos/science
if str(SCIENCE) not in sys.path:
    sys.path.insert(0, str(SCIENCE))

import claim_lint as L  # noqa: E402

FX = SCIENCE / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FX / (name + ".json")).read_text(encoding="utf-8"))


def _codes(result: dict) -> list:
    return sorted(f["code"] for f in result["findings"])


def test_negative_control_yields_no_findings():
    r = L.lint(_load("negative_control"))
    assert r["findings"] == [], _codes(r)
    assert r["attack_surface"] == []
    assert r["counts"] == {"ATTACK": 0, "NOTE": 0, "UNDECLARED": 0}


def test_positive_control_yields_exactly_the_planted_codes():
    p = _load("positive_control")
    r = L.lint(p)
    assert _codes(r) == p["_expected"]


def test_cheat_control_labels_without_properties_are_caught():
    p = _load("cheat_control")
    r = L.lint(p)
    assert _codes(r) == p["_expected"]
    # every ATTACK here is a present-but-empty key: the lint read the property
    attack_paths = {f.get("path", "") for f in r["findings"] if f["severity"] == "ATTACK"}
    assert any(path.endswith("controls.cheat") for path in attack_paths)


def test_gate_inside_se_is_not_a_gate():
    p = _load("gate_inside_se")
    r = L.lint(p)
    assert _codes(r) == p["_expected"]
    f = r["findings"][0]
    assert f["severity"] == "ATTACK" and "0.006" in f["message"]


def test_gate_outside_se_is_a_gate():
    p = _load("gate_inside_se")
    p["analysis"]["spec"]["gate"]["threshold"] = 0.90   # 0.052 away, SE 0.0195
    assert L.lint(p)["findings"] == []


def test_gate_unreachable_fires_on_either_side_of_the_range():
    p = _load("negative_control")
    for thr in (-1.5, 1.5):
        q = copy.deepcopy(p)
        q["analysis"]["spec"]["gate"]["threshold"] = thr
        assert "K_GATE_UNREACHABLE" in _codes(L.lint(q))
    q = copy.deepcopy(p)
    q["analysis"]["spec"]["gate"]["threshold"] = 0.14   # X-2 case reversed: inside
    assert "K_GATE_UNREACHABLE" not in _codes(L.lint(q))


def test_inconclusive_claims_are_not_attacked_for_missing_positives():
    p = _load("positive_control")
    p["claim"]["status"] = "INCONCLUSIVE"
    codes = _codes(L.lint(p))
    for c in ("K_NULL_UNDECLARED", "K_CONTROLS_UNDECLARED", "K_EFFECT_SIZE_NO_SE",
              "K_CONCLUSION_EXCEEDS_VERIFIED_N", "K_TRANSPORT_WITHOUT_SURFACE"):
        assert c not in codes
    # the kill-geometry checks are about experiments, not the claim's status
    assert "K_SINGLE_EXPERIMENT_TERMINAL" in codes
    assert "K_KILL_ON_INSTRUMENT_FINDING" in codes


def test_eligible_count_zero_is_allowed_only_for_inconclusive():
    p = _load("negative_control")
    p["analysis"]["spec"]["gate"]["eligible_count"] = 0
    assert "K_ELIGIBLE_COUNT_ZERO" in _codes(L.lint(p))
    p["claim"]["status"] = "INCONCLUSIVE"
    assert "K_ELIGIBLE_COUNT_ZERO" not in _codes(L.lint(p))


def test_undeclared_is_never_reported_as_false():
    p = _load("positive_control")
    r = L.lint(p)
    undeclared = [f for f in r["findings"] if f["severity"] == "UNDECLARED"]
    assert undeclared, "the indeterminate branch must exist"
    for f in undeclared:
        assert "not" not in f["code"].lower() or f["code"].endswith("UNDECLARED")


def test_measurement_at_range_edge_is_unmeasurable_not_a_kill():
    p = _load("negative_control")
    p["experiments"][2]["measurement_at_range_edge"] = True
    assert "K_MEASUREMENT_FAILURE_AS_KILL" in _codes(L.lint(p))


def test_deterministic_and_order_insensitive_over_experiments():
    p = _load("cheat_control")
    a = L.lint(p)
    p2 = copy.deepcopy(p)
    p2["experiments"].reverse()
    b = L.lint(p2)
    assert _codes(a) == _codes(b)
    assert L.lint(p) == a


def test_missing_sections_do_not_crash_and_read_as_undeclared():
    r = L.lint({"claim": {"claim_id": "x", "status": "SUPPORTED"}})
    codes = _codes(r)
    assert "K_NULL_UNDECLARED" in codes and "K_GATE_UNDECLARED" in codes
    assert r["counts"]["ATTACK"] == 0   # nothing was asserted, so nothing is attacked


def test_cli_runs_on_the_fixtures(tmp_path):
    rc = L.main([str(FX / "negative_control.json"), str(FX / "cheat_control.json")])
    assert rc == 0


def test_fixture_expectations_are_self_describing():
    for name in ("positive_control", "cheat_control", "gate_inside_se"):
        p = _load(name)
        assert p["_expected"] == sorted(p["_expected"]), name
