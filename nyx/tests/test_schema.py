"""The Chop Shop validator falsifies itself (base role rule 3: negative, positive, cheat).

Positive: a complete organ and a clean pressure pass.
Negative: an organ with an absent question fails with MISSING_FIELD, and "unknown" in
          the same slot passes -- absence and unknown are different facts.
Cheat:    an organ whose every answer is "unknown" is rejected HOLLOW (the detector
          measures content, not key presence); a pressure that names the organ is
          rejected LEAK (the detector can see a mechanism restated as a condition).
And every committed specimen record validates, so a bad record cannot land on main
without this test saying so.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from nyx.chop import schema as S

HERE = Path(__file__).resolve().parent
FIX = HERE.parent / "chop" / "fixtures"
SPECIMENS = HERE.parent / "specimens"


def _load(name: str) -> dict:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def _codes(findings):
    return sorted({c for c, _ in findings})


def test_positive_organ_passes():
    assert S.validate(_load("organ_positive.json")) == []


def test_positive_pressure_passes():
    assert S.validate(_load("pressure_positive.json")) == []


def test_negative_absent_question_fails_but_unknown_passes():
    rec = _load("organ_negative_missing_cheat.json")
    assert "MISSING_FIELD" in _codes(S.validate(rec))
    rec2 = copy.deepcopy(rec)
    rec2["questions"]["cheat"] = "unknown"
    assert S.validate(rec2) == []


def test_cheat_hollow_organ_is_rejected():
    codes = _codes(S.validate(_load("organ_cheat_hollow.json")))
    assert "HOLLOW" in codes, codes


def test_cheat_hollow_by_mechanism_and_interface_alone():
    rec = _load("organ_positive.json")
    rec["questions"]["mechanism"] = "unknown"
    rec["questions"]["interface"] = "Unknown "
    assert "HOLLOW" in _codes(S.validate(rec))


def test_cheat_leaking_pressure_is_rejected():
    codes = _codes(S.validate(_load("pressure_cheat_leak.json")))
    assert "LEAK" in codes, codes


def test_leak_check_is_case_insensitive_and_scoped_to_condition_fields():
    rec = _load("pressure_positive.json")
    rec["condition"] = "a world where a COUNTER of steps is kept"
    assert "LEAK" in _codes(S.validate(rec))
    rec = _load("pressure_positive.json")
    rec["cheat_control"] = "an organism born with the counter"   # allowed: the cheat may name it
    assert S.validate(rec) == []


def test_no_ancestor_is_a_defect():
    rec = _load("organ_positive.json")
    rec["provenance"]["ancestor"] = ""
    assert "NO_ANCESTOR" in _codes(S.validate(rec))


def test_bad_kind_and_schema():
    assert _codes(S.validate({"record_kind": "SOUP"})) == ["BAD_KIND"]
    rec = _load("organ_positive.json")
    rec["schema"] = "nyx.chop/99"
    assert "BAD_SCHEMA" in _codes(S.validate(rec))


def test_every_committed_specimen_record_validates():
    results = S.validate_tree(SPECIMENS)
    assert results, "no specimen records found under nyx/specimens"
    bad = {k: v for k, v in results.items() if v}
    assert not bad, json.dumps(bad, indent=1)


def test_cli_exit_codes(tmp_path):
    assert S.main([str(FIX / "organ_positive.json")]) == 0
    assert S.main([str(FIX / "organ_cheat_hollow.json")]) == 1
    assert S.main([]) == 2
