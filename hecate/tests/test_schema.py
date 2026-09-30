"""Validator controls: a valid program passes (positive), and each rule the
validator claims to enforce is shown to FIRE on a program built to break it
(cheat controls: success deliberately faked)."""

import copy

import pytest

from hecate.schema import RESEARCH_AXES, validate_program

TID = "HT-0000000000"


def _valid():
    p0 = {"id": "P0", "triplicateId": TID, "index": 0, "added": ["new interpretation"],
          "generator": {"model": "claude-opus-5-5", "search": False},
          "decision": "DEEPEN",
          "research_state": {a: "unknown" for a in RESEARCH_AXES}}
    mech = {"id": "M1", "triplicateId": TID, "passId": "P0", "kind": "mechanism",
            "layer": "speculation", "statement": "s",
            "questions": {k: "x" for k in (
                "what_exists", "what_changes", "what_persists", "what_is_selected",
                "what_can_reproduce", "what_can_learn", "what_can_transfer",
                "distinguishing_observable")}}
    return {
        "id": TID,
        "concepts": [{"name": "A"}, {"name": "B"}, {"name": "C"}],
        "provenance": {"source": "hephaestus", "sourceArtifact": "x#L1",
                       "historicalId": "A + B + C"},
        "passes": [p0], "hypotheses": [mech], "lenses": [], "experiments": [],
        "candidateEngines": [], "currentVerdict": "SPECULATIVE",
        "evidenceSummary": {},
    }


def test_positive_control_valid_program_passes():
    assert validate_program(_valid()) == []


def _breaks(mutate):
    p = copy.deepcopy(_valid())
    mutate(p)
    return validate_program(p)


@pytest.mark.parametrize("name,mutate,needle", [
    ("historical provenance without artifact",
     lambda p: p["provenance"].pop("sourceArtifact"), "sourceArtifact"),
    ("renamed source",
     lambda p: p["provenance"].update(source="HECATE"), "provenance.source"),
    ("hypothesis pointing at another triplicate",
     lambda p: p["hypotheses"][0].update(triplicateId="HT-other"), "triplicateId"),
    ("hypothesis pointing at a pass that does not exist",
     lambda p: p["hypotheses"][0].update(passId="P9"), "passId"),
    ("claimed supported conclusion with no evidence",
     lambda p: p["hypotheses"][0].update(layer="supported_conclusion"), "evidence_rows"),
    ("supported conclusion with rows but no prereg",
     lambda p: p["hypotheses"][0].update(layer="supported_conclusion", evidence_rows=["r"]), "prereg"),
    ("PROMISING with no predicate",
     lambda p: p.update(currentVerdict="PROMISING"), "predicate"),
    ("PROMISING with a FAILED predicate",
     lambda p: p.update(currentVerdict="PROMISING", evidenceSummary={
         "predicate": {"prereg": "x", "rows": "y", "result": "FAIL"}}), "predicate"),
    ("REJECT with no rows",
     lambda p: p.update(currentVerdict="REJECT"), "rows"),
    ("pass that adds nothing",
     lambda p: p["passes"][0].update(added=[]), "added"),
    ("pass addition outside the charter list",
     lambda p: p["passes"][0].update(added=["more brainstorming"]), "charter list"),
    ("mechanism with an unanswered question",
     lambda p: p["hypotheses"][0]["questions"].update(what_is_selected=""), "what_is_selected"),
    ("one number for everything",
     lambda p: p["passes"][0]["research_state"].pop("artifact_risk"), "artifact_risk"),
])
def test_cheat_controls_each_rule_fires(name, mutate, needle):
    errs = _breaks(mutate)
    assert errs, f"validator accepted: {name}"
    assert any(needle in e for e in errs), (name, errs)


def test_evidence_verdict_accepted_only_with_passing_predicate():
    p = _valid()
    p["currentVerdict"] = "PROMISING"
    p["evidenceSummary"] = {"predicate": {"prereg": "roles/Hecate/prereg/x",
                                          "rows": "hecate/programs/x/rows.jsonl",
                                          "result": "PASS"}}
    assert validate_program(p) == []
