"""Smoke tests for Fire #1 active generators: A2, C2, D2."""
from __future__ import annotations

from theseus.emit.record_schema import Verdict
from theseus.generators.a2_statistical_correlation import (
    A2StatisticalCorrelationGenerator,
)
from theseus.generators.c2_threshold_mutation import (
    C2ThresholdMutationGenerator,
)
from theseus.generators.d2_margin_bracket import D2MarginBracketGenerator


def test_a2_emits_correlation_record():
    g = A2StatisticalCorrelationGenerator(batch_id="t", seed=0, sample_size=20)
    r = g.next()
    assert r is not None
    assert r.generator_id == "a2"
    p = r.claim_payload
    assert "r_raw" in p and "r_detrended" in p
    assert "p_raw" in p and "p_detrended" in p
    assert p["detrend_control"] == "log(conductor)"
    assert -1.01 <= p["r_raw"] <= 1.01
    assert -1.01 <= p["r_detrended"] <= 1.01


def test_a2_detrending_is_recorded_in_canonical_text():
    g = A2StatisticalCorrelationGenerator(batch_id="t", seed=0, sample_size=20)
    r = g.next()
    assert r is not None
    assert "detrend" in r.canonical_claim_text.lower()


def test_c2_bootstraps_and_mutates_threshold():
    g = C2ThresholdMutationGenerator(batch_id="t", seed=0, parents=None)
    found = False
    for _ in range(15):
        r = g.next()
        if r is not None:
            assert r.generator_id == "c2"
            p = r.claim_payload
            assert p["new_threshold"] != p["original_threshold"]
            assert p["relation"].startswith("abs_diff_le_")
            assert "C2_THRESH" in r.canonical_claim_text
            found = True
            break
    assert found, "C2 should produce a record in 15 tries"


def test_d2_bootstraps_and_emits_bracket():
    g = D2MarginBracketGenerator(batch_id="t", seed=0)
    found = False
    for _ in range(20):
        r = g.next()
        if r is not None:
            assert r.generator_id == "d2"
            p = r.claim_payload
            assert "margin" in p and "in_bracket" in p
            assert p["band"] in (
                "barely_survives", "barely_fails",
                "comfortable_survival", "comfortable_failure",
            )
            assert "D2_BRACKET" in r.canonical_claim_text
            found = True
            break
    assert found, "D2 should produce a record in 20 tries"


def test_a2_c2_d2_registered_as_active():
    """Registry round-trip: registry.list_active() returns the new generators."""
    from theseus.registry import list_active

    actives = list_active()
    assert "a2" in actives
    assert "c2" in actives
    assert "d2" in actives
