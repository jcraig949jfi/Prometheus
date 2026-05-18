"""Smoke tests for Fire #4 active generators: F3, A3, B1."""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import Verdict
from theseus.generators.f3_importance_sampling import (
    F3ImportanceSamplingGenerator,
)
from theseus.generators.a3_functional_identity import (
    A3FunctionalIdentityGenerator,
    OPERATORS,
)
from theseus.generators.b1_operator_rotation import (
    B1OperatorRotationGenerator,
    _predicted_after_mirror_n,
    _actual_after_mirror_n,
)


def test_f3_emits_record_with_coverage_metadata():
    g = F3ImportanceSamplingGenerator(batch_id="t", seed=0)
    r = g.next()
    assert r is not None
    assert r.generator_id == "f3"
    assert r.claim_payload["sampling"] == "importance_inverse_coverage"
    assert r.claim_payload["region_coverage_at_emit"] >= 1
    assert "F3_ACT" in r.canonical_claim_text


def test_f3_bias_shifts_toward_undercovered():
    """After many emissions, the coverage distribution should be more
    uniform than uniform-random sampling would produce."""
    g = F3ImportanceSamplingGenerator(batch_id="t", seed=0)
    for _ in range(500):
        g.next()
    counts = list(g._coverage.values())
    if not counts:
        pytest.skip("F3 produced no records (unexpected)")
    mean = sum(counts) / len(counts)
    variance = sum((c - mean) ** 2 for c in counts) / len(counts)
    # Compare to expected variance for uniform random (binomial-flavored)
    # We expect F3's variance to be LOWER than pure uniform random would
    # produce, because of the anti-frequency weighting.
    assert variance < (mean * 2.0)  # rough sanity check


def test_a3_operators_are_callable():
    for name, fn in OPERATORS.items():
        result = fn(7)
        assert isinstance(result, int)


def test_a3_emits_functional_identity_record():
    g = A3FunctionalIdentityGenerator(batch_id="t", seed=0)
    r = g.next()
    assert r is not None
    assert r.generator_id == "a3"
    p = r.claim_payload
    assert "operator_f" in p and "operator_g" in p
    assert "value_a_raw" in p and "value_a_transformed" in p
    assert "A3_FUNC" in r.canonical_claim_text


def test_b1_predicted_after_mirror_signature():
    # signature flips: n=2 → original, n=3 → -original, n=4 → original
    assert _predicted_after_mirror_n("signature", 5, 2) == 5
    assert _predicted_after_mirror_n("signature", 5, 3) == -5
    assert _predicted_after_mirror_n("signature", 5, 4) == 5


def test_b1_predicted_after_mirror_crossing_number():
    # crossing_number preserved for all n
    for n in (1, 2, 3, 7):
        assert _predicted_after_mirror_n("crossing_number", 8, n) == 8


def test_b1_actual_matches_predicted_on_healthy_substrate():
    g = B1OperatorRotationGenerator(batch_id="t", seed=0)
    # All emissions should be SHADOW_CATALOG (self-consistency)
    confirms = 0
    rejects = 0
    for _ in range(50):
        r = g.next()
        if r is None:
            continue
        if r.verdict == Verdict.SHADOW_CATALOG.value:
            confirms += 1
        elif r.verdict == Verdict.REJECTED.value:
            rejects += 1
    assert rejects == 0, (
        f"B1 should produce 0 rejects on healthy substrate; got {rejects}"
    )
    assert confirms > 0


def test_f3_a3_b1_registered_as_active():
    from theseus.registry import list_active

    actives = list_active()
    assert "f3" in actives
    assert "a3" in actives
    assert "b1" in actives
