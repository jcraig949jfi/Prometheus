"""Smoke tests for Fire #9 active generators: F2, G4, H4."""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import Verdict
from theseus.generators.f2_anti_frequency import F2AntiFrequencyGenerator
from theseus.generators.g4_reflection_duality import G4ReflectionDualityGenerator
from theseus.generators.h4_bridge_extension import H4BridgeExtensionGenerator


def test_f2_picks_least_covered():
    g = F2AntiFrequencyGenerator(batch_id="t", seed=0)
    for _ in range(96):  # one cycle through 96 regions
        g.next()
    counts = list(g._coverage.values())
    assert max(counts) - min(counts) <= 1, (
        f"F2 strict anti-frequency should have nearly-uniform coverage; "
        f"got min={min(counts)} max={max(counts)}"
    )


def test_f2_records_have_sampling_metadata():
    g = F2AntiFrequencyGenerator(batch_id="t", seed=0)
    r = g.next()
    assert r is not None
    assert r.claim_payload["sampling"] == "strict_anti_frequency"
    assert "region_coverage_at_emit" in r.claim_payload


def test_g4_emits_reflection_record():
    g = G4ReflectionDualityGenerator(batch_id="t", seed=0)
    r = g.next()
    assert r is not None
    assert r.generator_id == "g4"
    p = r.claim_payload
    assert "raw_holds" in p and "reflected_holds" in p
    assert "reflection_symmetric" in p
    assert p["reflected_value_a"] == -p["value_a"]
    assert "G4_REFL" in r.canonical_claim_text


def test_g4_symmetric_implies_same_truth():
    """When reflection_symmetric is True, raw and reflected must agree."""
    g = G4ReflectionDualityGenerator(batch_id="t", seed=0)
    for _ in range(50):
        r = g.next()
        if r is None:
            continue
        p = r.claim_payload
        if p["reflection_symmetric"]:
            assert p["raw_holds"] == p["reflected_holds"]
        else:
            assert p["raw_holds"] != p["reflected_holds"]


def test_h4_bootstraps_and_emits():
    g = H4BridgeExtensionGenerator(batch_id="t", seed=0)
    found = False
    for _ in range(20):
        r = g.next()
        if r is not None:
            assert r.generator_id == "h4"
            p = r.claim_payload
            assert "n_holding" in p and "n_tested" in p
            assert p["n_tested"] >= 1
            assert "extensions" in p
            assert "H4_BRIDGE" in r.canonical_claim_text
            found = True
            break
    assert found, "H4 should produce a record in 20 tries"


def test_h4_verdict_logic():
    g = H4BridgeExtensionGenerator(batch_id="t", seed=0)
    for _ in range(30):
        r = g.next()
        if r is None:
            continue
        p = r.claim_payload
        if p["n_holding"] >= 2:
            assert r.verdict == Verdict.SHADOW_CATALOG.value
        elif p["n_holding"] == 1:
            assert r.verdict == Verdict.INCONCLUSIVE.value
        else:
            assert r.verdict == Verdict.REJECTED.value


def test_f2_g4_h4_registered_as_active():
    from theseus.registry import list_active

    actives = list_active()
    assert "f2" in actives
    assert "g4" in actives
    assert "h4" in actives
