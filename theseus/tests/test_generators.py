"""Smoke tests for v0.1 active generators: each can emit at least one record."""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import Verdict
from theseus.generators.a1_catalog_cross_product import (
    A1CatalogCrossProductGenerator,
)
from theseus.generators.b5_conservation_law import B5ConservationLawGenerator
from theseus.generators.c1_claim_mutation import C1ClaimMutationGenerator
from theseus.generators.d1_kill_neighborhood import D1KillNeighborhoodGenerator
from theseus.generators.e1_research_batch_parser import (
    E1ResearchBatchParserGenerator,
)


def test_a1_emits_record():
    g = A1CatalogCrossProductGenerator(batch_id="t", seed=0)
    r = g.next()
    assert r is not None
    assert r.generator_id == "a1"
    assert r.verdict in (Verdict.SHADOW_CATALOG.value, Verdict.REJECTED.value)
    assert "knot" in r.canonical_claim_text or "ec" in r.canonical_claim_text


def test_a1_emits_multiple_unique_records():
    g = A1CatalogCrossProductGenerator(batch_id="t", seed=0)
    seen_ids = set()
    for _ in range(20):
        r = g.next()
        if r is not None:
            seen_ids.add(r.record_id)
    # In 20 draws we should hit at least a few distinct (a, b, i, j, rel) tuples
    assert len(seen_ids) >= 3


def test_b5_emits_record():
    g = B5ConservationLawGenerator(batch_id="t", seed=0)
    r = g.next()
    assert r is not None
    assert r.generator_id == "b5"
    assert r.verdict in (Verdict.SHADOW_CATALOG.value, Verdict.REJECTED.value)


def test_c1_bootstraps_from_a1():
    """C1 with no parents bootstraps using internal A1 seed."""
    g = C1ClaimMutationGenerator(batch_id="t", seed=0, parents=None)
    # First call seeds, then mutates. Both should succeed for at least
    # a few of 10 tries.
    found = False
    for _ in range(10):
        r = g.next()
        if r is not None:
            assert r.generator_id == "c1"
            assert "MUT" in r.canonical_claim_text
            found = True
            break
    assert found, "C1 should produce at least one record in 10 tries"


def test_d1_bootstraps_from_a1():
    g = D1KillNeighborhoodGenerator(batch_id="t", seed=0)
    # D1 needs a kill from A1 first. Allow up to 20 tries.
    found = False
    for _ in range(20):
        r = g.next()
        if r is not None:
            assert r.generator_id == "d1"
            assert "KILL_NBHD" in r.canonical_claim_text
            found = True
            break
    # D1 may legitimately fail to bootstrap on very lucky seeds — but
    # in expectation it should find a kill in 20 tries given how many
    # A1 emissions are REJECTED
    assert found, "D1 should produce at least one record in 20 tries"


def test_e1_handles_missing_root(tmp_path):
    g = E1ResearchBatchParserGenerator(batch_id="t", root=tmp_path)
    r = g.next()
    # Empty root → no records
    assert r is None


def test_e1_extracts_claim_pattern(tmp_path):
    batch_dir = tmp_path / "deep_research_batch_test"
    batch_dir.mkdir()
    (batch_dir / "report.md").write_text(
        "Background prose. Theorem: every elliptic curve has a finite "
        "Mordell-Weil group rank. More prose.",
        encoding="utf-8",
    )
    g = E1ResearchBatchParserGenerator(batch_id="t", root=tmp_path)
    r = g.next()
    assert r is not None
    assert r.generator_id == "e1"
    assert r.verdict == Verdict.UNVERIFIED.value
    assert "Theorem" in r.canonical_claim_text
