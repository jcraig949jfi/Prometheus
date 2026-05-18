"""Smoke tests for Fire #8 active generators: A5, C3, D4."""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import Verdict
from theseus.generators.a5_distribution_match import (
    A5DistributionMatchGenerator,
    _ks_two_sample,
    _standardize,
)
from theseus.generators.c3_region_slide import C3RegionSlideGenerator
from theseus.generators.d4_boundary_crossing import D4BoundaryCrossingGenerator


def test_ks_identical_samples():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [1.0, 2.0, 3.0, 4.0, 5.0]
    d, p = _ks_two_sample(xs, ys)
    assert d < 0.01
    assert p > 0.9


def test_ks_disjoint_samples():
    xs = [1.0, 2.0, 3.0]
    ys = [100.0, 200.0, 300.0]
    d, p = _ks_two_sample(xs, ys)
    assert d > 0.9


def test_standardize_zero_mean_unit_variance():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    zs = _standardize(xs)
    assert abs(sum(zs) / len(zs)) < 1e-9
    var = sum(z * z for z in zs) / len(zs)
    assert abs(var - 1.0) < 1e-6


def test_a5_emits_distribution_record():
    g = A5DistributionMatchGenerator(batch_id="t", seed=0, sample_size=10)
    r = g.next()
    assert r is not None
    assert r.generator_id == "a5"
    p = r.claim_payload
    assert "ks_d_statistic" in p
    assert "ks_p_value" in p
    assert p["standardized"] is True
    assert "A5_KS" in r.canonical_claim_text


def test_c3_emits_invariant_slide():
    g = C3RegionSlideGenerator(batch_id="t", seed=0)
    found = False
    for _ in range(15):
        r = g.next()
        if r is not None:
            assert r.generator_id == "c3"
            p = r.claim_payload
            assert "slide_side" in p
            assert "original_invariant_a" in p
            assert p["original_invariant_a"] != p["invariant_a"] or p["original_invariant_b"] != p["invariant_b"]
            assert "C3_SLIDE" in r.canonical_claim_text
            found = True
            break
    assert found, "C3 should emit a slide record in 15 tries"


def test_d4_bootstraps_and_emits(tmp_path):
    g = D4BoundaryCrossingGenerator(batch_id="t", seed=0, corpus_dir=tmp_path)
    found = False
    for _ in range(20):
        r = g.next()
        if r is not None:
            assert r.generator_id == "d4"
            p = r.claim_payload
            assert "epsilon" in p and "tight_boundary" in p
            assert p["pass_record_id"] != p["kill_record_id"]
            assert "D4_BOUND" in r.canonical_claim_text
            found = True
            break
    assert found, "D4 should bootstrap and emit a boundary record"


def test_a5_c3_d4_registered_as_active():
    from theseus.registry import list_active

    actives = list_active()
    assert "a5" in actives
    assert "c3" in actives
    assert "d4" in actives
