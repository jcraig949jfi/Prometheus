"""Smoke tests for Fire #10 active generators: F4, G5, H2."""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import Verdict
from theseus.generators.f4_frontier_pursuit import F4FrontierPursuitGenerator
from theseus.generators.g5_scale_invariance import G5ScaleInvarianceGenerator
from theseus.generators.h2_triangulation_protocol import (
    H2TriangulationProtocolGenerator,
)


def test_f4_emits_with_frontier_metadata():
    g = F4FrontierPursuitGenerator(batch_id="t", seed=0)
    r = g.next()
    assert r is not None
    assert r.generator_id == "f4"
    p = r.claim_payload
    assert p["sampling"] == "frontier_band_pursuit"
    assert "min_coverage_at_pick" in p


def test_g5_emits_scale_invariance_record():
    g = G5ScaleInvarianceGenerator(batch_id="t", seed=0)
    r = g.next()
    assert r is not None
    p = r.claim_payload
    assert "scale_factor" in p
    assert p["scale_factor"] in (2, 3, 5)
    assert p["scaled_value_a"] == p["scale_factor"] * p["value_a"]
    assert "G5_SCALE" in r.canonical_claim_text


def test_g5_equal_preserved_under_scale():
    """For relation=='equal', any scale preserves truth (a==b iff k·a==k·b)."""
    g = G5ScaleInvarianceGenerator(batch_id="t", seed=0)
    for _ in range(100):
        r = g.next()
        if r is None:
            continue
        p = r.claim_payload
        if p["relation"] == "equal":
            assert p["raw_holds"] == p["scaled_holds"]
            assert p["scale_invariant"] is True


def test_h2_bootstraps_and_emits(tmp_path):
    g = H2TriangulationProtocolGenerator(
        batch_id="t", seed=0, corpus_dir=tmp_path
    )
    found = False
    for _ in range(15):
        r = g.next()
        if r is not None:
            assert r.generator_id == "h2"
            assert "H2_METHOD" in r.canonical_claim_text
            p = r.claim_payload
            assert "method_r2s" in p
            assert "method_verdicts" in p
            assert r.step_trace is not None
            assert len(r.step_trace) >= 2
            found = True
            break
    assert found, "H2 should bootstrap and emit in 15 tries"


def test_h2_step_trace_has_method_metadata():
    g = H2TriangulationProtocolGenerator(batch_id="t", seed=0)
    for _ in range(20):
        r = g.next()
        if r is not None and r.step_trace:
            for step in r.step_trace:
                assert step["step_kind"] == "method_variant"
                assert "polyfit_" in step["step_method"]
                assert "sample_size_target" in step["step_input"]
                assert "degree" in step["step_input"]
            return
    pytest.fail("H2 didn't emit a step_trace in 20 tries")


def test_f4_g5_h2_registered_as_active():
    from theseus.registry import list_active

    actives = list_active()
    assert "f4" in actives
    assert "g5" in actives
    assert "h2" in actives
