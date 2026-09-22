"""OQ-1.0.0: every gate fires on the defect the charter names and is silent on a clean case;
recall metrics carry eligible counts; the cheat stack (fires on everything) is labelled VACUOUS."""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import c6_observatory as oq   # noqa: E402


# ------------------------------------------------ 1. provenance / LLM-free floor

def test_provenance_census_is_an_eligibility_count_not_a_score():
    runs = [{"run_id": i, "provenance": p} for i, p in enumerate(
        ["LLM_PROPOSED"] * 6 + ["PROCEDURAL"] * 2 + ["EVOLUTION_GENERATED"] * 1 + ["HUMAN_DIRECTED"] * 1)]
    c = oq.provenance_census(runs)
    assert c["llm_free_fraction"] == 0.3 and c["search_diversity_eligibility"] == "ELIGIBLE"
    low = oq.provenance_census(runs[:7])           # 6 LLM + 1 procedural = 1/7
    assert low["search_diversity_eligibility"] == "INELIGIBLE_BELOW_FLOOR"
    assert oq.provenance_census([])["search_diversity_eligibility"] == "NOTHING_COULD_FIRE"
    with pytest.raises(oq.ObservatoryRefused, match="valid provenance"):
        oq.provenance_census([{"run_id": 0, "provenance": "INTERESTING"}])


# ------------------------------------------------------- 2. fixture custody

FIX = [
    {"fixture_id": "FX-01", "phenomenon_class": "NEUTRAL_STRUCTURE_LATER_USEFUL", "location": "run-7/lin-3",
     "expected": "fires lineage_discontinuity late", "spec": {"gen_useful": 400}},
    {"fixture_id": "FX-02", "phenomenon_class": "POPULATION_EFFECT_NO_EXCEPTIONAL_INDIVIDUAL", "location": "run-9/pop",
     "expected": "no individual detector; niche_divergence at population level", "spec": {}},
    {"fixture_id": "FX-03", "phenomenon_class": oq.UNKNOWN_MECHANISM, "location": "run-11/lin-1",
     "expected": "classifier must return UNKNOWN_MECHANISM", "spec": {"cause": "withheld"}},
    {"fixture_id": "FX-04", "phenomenon_class": "ANCESTRY_ONLY_EVENT", "location": "run-12/lin-5",
     "expected": "endpoint ordinary; only ancestry shows it", "spec": {}},
]


def test_seal_and_reveal_round_trip_and_tamper():
    reg = oq.seal_fixtures(FIX, sealed_at="2026-09-18T00:00:00+00:00")
    assert reg["n_fixtures"] == 4 and all("phenomenon_class" not in p or p["phenomenon_class"] == "" for p in reg["public_registry"])
    v = oq.verify_reveal(reg["public_registry"], reg["private_registry"])
    assert v["verified"] == ["FX-01", "FX-02", "FX-03", "FX-04"] and not v["void"]
    tampered = [dict(f) for f in reg["private_registry"]]
    tampered[1]["location"] = "run-10/pop"           # moved after sealing
    v2 = oq.verify_reveal(reg["public_registry"], tampered[:3])
    assert v2["void"] == ["FX-02"] and v2["unrevealed"] == ["FX-04"]
    with pytest.raises(oq.ObservatoryRefused, match="missing"):
        oq.seal_fixtures([{"fixture_id": "x"}])


# ------------------------------------------------------ 3. recall + firing table

def _esc(loc, cls, replays=True, probes=True, preserved="2026-09-18T01:00:00+00:00", classified="2026-09-18T02:00:00+00:00", all_freezes=True):
    return {"location": loc, "freezes": {k: all_freezes for k in oq.FREEZES},
            "replays": {"A_exact_replay": replays}, "causal_probes": {"E_mechanism_ablation": probes},
            "classification": cls, "preserved_at": preserved, "classified_at": classified}


def _firings(fired_locs, all_locs, detector="behavioral_novelty"):
    return [{"location": l, "detector": detector, "score": 1.0 if l in fired_locs else 0.0, "threshold": 0.5,
             "fired": l in fired_locs} for l in all_locs]


ALL = ["run-7/lin-3", "run-9/pop", "run-11/lin-1", "run-12/lin-5"] + ["run-%d/x" % i for i in range(20, 40)]


def test_recall_metrics_carry_eligible_counts_and_miss_list():
    fx = FIX
    firings = _firings({"run-7/lin-3", "run-11/lin-1", "run-25/x"}, ALL)
    esc = [_esc("run-7/lin-3", "NEUTRAL_STRUCTURE_LATER_USEFUL"),
           _esc("run-11/lin-1", oq.UNKNOWN_MECHANISM), _esc("run-25/x", oq.UNKNOWN_MECHANISM)]
    m = oq.recall_metrics(fx, firings, esc)
    assert m["detection"] == {**m["detection"], "count": 2, "eligible": 4}
    assert m["missed_fixtures"] == ["run-12/lin-5", "run-9/pop"]
    assert m["preservation"]["count"] == 2 and m["replay_success"]["count"] == 2
    assert m["classification_accuracy"]["count"] == 2 and m["unknown_retention"]["rate"] == 1.0
    assert m["false_escalation"]["count"] == 1 and m["false_escalation"]["eligible"] == 20
    assert m["stack_label"] == "INFORMATIVE"
    assert m["per_class_detection"]["ANCESTRY_ONLY_EVENT"] == {"hit": 0, "planted": 1}


def test_cheat_stack_that_fires_on_everything_is_vacuous_not_perfect():
    firings = _firings(set(ALL), ALL)
    esc = [_esc(f["location"], f["phenomenon_class"]) for f in FIX]
    m = oq.recall_metrics(FIX, firings, esc)
    assert m["detection"]["rate"] == 1.0 and m["false_escalation"]["rate"] == 1.0
    assert m["stack_label"] == "VACUOUS_FIRES_ON_EVERYTHING"


def test_silent_stack_is_measured_as_zero_not_nothing_could_fire():
    m = oq.recall_metrics(FIX, _firings(set(), ALL), [])
    assert m["detection"]["rate"] == 0.0 and m["detection"]["label"] == "MEASURED"
    assert m["preservation"]["label"] == "NOTHING_COULD_FIRE"


def test_detector_table_event_classes():
    f = [{"location": "L1", "detector": "behavioral_novelty", "fired": True},
         {"location": "L1", "detector": "structural_reuse", "fired": False},
         {"location": "L2", "detector": "classifier_failure_unknown_behavior", "fired": True},
         {"location": "L2", "detector": "niche_divergence", "fired": True}]
    t = oq.detector_table(f)
    assert t["event_classes"][oq.DISAGREEMENT] == ["L1"]
    assert t["event_classes"][oq.NONE_OF_THE_ABOVE] == ["L2"] and t["event_classes"]["MULTI_RULER"] == ["L2"]
    with pytest.raises(oq.ObservatoryRefused, match="unknown detector"):
        oq.detector_table([{"location": "L", "detector": "interestingness", "fired": True}])


# ------------------------------------------------------- 4. escalation order

def test_preservation_before_explanation():
    ok = oq.check_escalation_order(_esc("L", "X"))
    assert ok["freezes"] == 9
    with pytest.raises(oq.ObservatoryRefused, match="before preservation completed"):
        oq.check_escalation_order(_esc("L", "X", preserved="2026-09-18T03:00:00+00:00", classified="2026-09-18T02:00:00+00:00"))
    with pytest.raises(oq.ObservatoryRefused, match="preservation incomplete"):
        oq.check_escalation_order(_esc("L", "X", all_freezes=False))


# ------------------------------------------------ 5. classification admission

def test_unknown_is_default_and_named_mechanism_needs_replay_and_probe():
    assert oq.admit_classification(_esc("L", None, replays=False, probes=False), oq.UNKNOWN_MECHANISM) == oq.UNKNOWN_MECHANISM
    with pytest.raises(oq.ObservatoryRefused, match="needs a reproducing replay"):
        oq.admit_classification(_esc("L", None, replays=False, probes=True), "EXAPTATION")
    with pytest.raises(oq.ObservatoryRefused, match="causal"):
        oq.admit_classification(_esc("L", None, replays=True, probes=False), "EXAPTATION")
    assert oq.admit_classification(_esc("L", None), "EXAPTATION") == "EXAPTATION"
    e = _esc("L", None); e["evidence_kind"] = "RESEMBLANCE"
    with pytest.raises(oq.ObservatoryRefused, match="resemblance"):
        oq.admit_classification(e, "EXAPTATION")


# ---------------------------------------------------------- 6. success classes

def test_six_classes_returned_never_collapsed():
    vs = [oq.SuccessClassVerdict(c, "INCONCLUSIVE", 10, ("path/a",)) for c in oq.SUCCESS_CLASSES]
    r = oq.campaign_return(vs)
    assert set(r["classes"]) == set(oq.SUCCESS_CLASSES) and r["collapsed_pass_fail"] is None
    with pytest.raises(oq.ObservatoryRefused, match="missing"):
        oq.campaign_return(vs[:5])
    with pytest.raises(oq.ObservatoryRefused, match="assertion"):
        oq.campaign_return(vs[:5] + [oq.SuccessClassVerdict("SCALING_HEALTH", "SUPPORTED", 3, ())])
    with pytest.raises(oq.ObservatoryRefused, match="nothing could fire"):
        oq.campaign_return(vs[:5] + [oq.SuccessClassVerdict("SCALING_HEALTH", "SUPPORTED", 0, ("p",))])
    with pytest.raises(oq.ObservatoryRefused, match="not reduced"):
        oq.refuse_collapse("PASS")


# ------------------------------------------------------ 7. forbidden conclusions

def test_forbidden_conclusions_fire_on_insufficient_evidence_only():
    with pytest.raises(oq.ObservatoryRefused, match="forbidden"):
        oq.refuse_forbidden_conclusion("open-ended evolution failed", ["no_dramatic_discovery"])
    with pytest.raises(oq.ObservatoryRefused, match="forbidden"):
        oq.refuse_forbidden_conclusion("intelligence emerged", ["large_scalar_improvement"])
    with pytest.raises(oq.ObservatoryRefused, match="forbidden"):
        oq.refuse_forbidden_conclusion("nothing happened", ["flat_fitness"])
    with pytest.raises(oq.ObservatoryRefused, match="forbidden"):
        oq.refuse_forbidden_conclusion("absence of phenomena", ["absence_of_detection_without_recall_calibration"])
    with pytest.raises(oq.ObservatoryRefused, match="no evidence"):
        oq.refuse_forbidden_conclusion("mechanism X occurred", [])
    # with a replay and an ablation on record the sentence is not refused HERE
    assert oq.refuse_forbidden_conclusion("nothing happened", ["flat_fitness", "detector_table_all_silent_after_recall_calibration"])


# ------------------------------------------------------- the complexity curve

def test_recall_by_complexity_bins_with_eligible_counts():
    firings = _firings({"run-7/lin-3", "run-11/lin-1"}, ALL)
    rows = oq.recall_by_complexity(FIX, firings, lambda loc: "rich" if loc.startswith("run-1") else "plain")
    d = {r["complexity_bin"]: r for r in rows}
    assert d["plain"]["planted"] == 2 and d["plain"]["detected"] == 1
    assert d["rich"]["planted"] == 2 and d["rich"]["detected"] == 1
    assert all(r["label"] == "MEASURED" for r in rows)
