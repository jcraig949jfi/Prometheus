"""Unit tests for G2FunctionalEquationGenerator."""
from __future__ import annotations

from theseus.emit.record_schema import ClaimKind, Verdict
from theseus.generators.base import GeneratorStatus
from theseus.generators.g2_functional_equation import (
    G2FunctionalEquationGenerator,
    _get_conductor,
    _get_rank,
    SAMPLE_S_VALUES,
)


def test_get_conductor_valid():
    assert _get_conductor({"base": {"conductor": 37}}) == 37


def test_get_conductor_missing_returns_none():
    assert _get_conductor({"base": {}}) is None
    assert _get_conductor({"base": {"conductor": None}}) is None


def test_get_rank_valid():
    assert _get_rank({"base": {"rank": 2}}) == 2


def test_generator_status_is_active():
    assert G2FunctionalEquationGenerator.status == GeneratorStatus.ACTIVE


def test_sample_s_values_include_center():
    assert 1.0 in SAMPLE_S_VALUES
    assert all(0 < s < 2 for s in SAMPLE_S_VALUES)


def test_generator_emits_unverified_records():
    g = G2FunctionalEquationGenerator(batch_id="test", seed=0)
    if not g._eligible:
        return  # empty catalog, nothing to test
    records = []
    for _ in range(20):
        r = g.next()
        if r is None:
            break
        records.append(r)
    assert len(records) >= 1
    for r in records:
        assert r.generator_id == "g2"
        assert r.claim_kind == ClaimKind.SYMMETRY_TRANSFORM.value
        # All G2 records are UNVERIFIED — sigma routes them downstream.
        assert r.verdict == Verdict.UNVERIFIED.value
        assert r.claim_payload["conductor"] is not None
        assert r.claim_payload["s_sample"] in SAMPLE_S_VALUES
        assert "FE_relation" in r.claim_payload
        assert r.method == "catalog_FE_claim_emission"


def test_generator_seed_determinism():
    g1 = G2FunctionalEquationGenerator(batch_id="b1", seed=99)
    g2 = G2FunctionalEquationGenerator(batch_id="b2", seed=99)
    ids1 = []
    ids2 = []
    for _ in range(20):
        r1 = g1.next()
        r2 = g2.next()
        if r1 is not None and r2 is not None:
            ids1.append(r1.record_id)
            ids2.append(r2.record_id)
    assert ids1 == ids2


def test_generator_covers_multiple_s_values_in_a_run():
    """Verify sampling actually visits multiple s-values across a batch."""
    g = G2FunctionalEquationGenerator(batch_id="test", seed=42)
    s_seen = set()
    for _ in range(100):
        r = g.next()
        if r is None:
            break
        s_seen.add(r.claim_payload["s_sample"])
    if g._eligible:
        # With 3 s-values and 100 draws, we should hit all 3 ~always.
        assert len(s_seen) >= 2


def test_registry_can_resolve_g2():
    from theseus.registry import get_generator_class

    cls = get_generator_class("g2")
    assert cls is G2FunctionalEquationGenerator
