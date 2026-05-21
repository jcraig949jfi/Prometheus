"""Unit tests for E2ArxivAbstractMiningGenerator."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.emit.record_schema import ClaimKind, Verdict
from theseus.generators.base import GeneratorStatus
from theseus.generators.e2_arxiv_abstract_mining import (
    E2ArxivAbstractMiningGenerator,
    _extract_claims_from_text,
)


def _write_cache(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def test_extract_claims_picks_up_theorem_pattern():
    text = "Our main theorem establishes that every nontrivial zero lies on the critical line."
    out = _extract_claims_from_text(text)
    assert len(out) == 1
    assert "theorem" in out[0].lower()


def test_extract_claims_picks_up_we_prove_pattern():
    text = "We prove that the Mahler measure of every Lehmer polynomial exceeds the Lehmer constant."
    out = _extract_claims_from_text(text)
    assert len(out) == 1
    assert "we prove" in out[0].lower()


def test_extract_claims_filters_too_short():
    # Short fragment shouldn't match.
    text = "Theorem 1. QED."
    out = _extract_claims_from_text(text)
    assert out == []


def test_extract_claims_dedups_within_text():
    text = (
        "Theorem 1: every prime p satisfies an unspecified bound on the curve. "
        "Theorem 1: every prime p satisfies an unspecified bound on the curve."
    )
    out = _extract_claims_from_text(text)
    # Dedup within a single text.
    assert len(out) == 1


def test_generator_status_is_active():
    assert E2ArxivAbstractMiningGenerator.status == GeneratorStatus.ACTIVE


def test_generator_emits_records_from_cache(tmp_path):
    cache = tmp_path / "abstracts.jsonl"
    _write_cache(cache, [
        {
            "arxiv_id": "2401.00001",
            "title": "On a conjecture in number theory",
            "abstract": "We prove that the Riemann hypothesis implies that every prime gap is bounded.",
            "categories": ["math.NT"],
            "published": "2024-01-01T00:00:00+00:00",
        },
        {
            "arxiv_id": "2401.00002",
            "title": "Algebraic geometry note",
            "abstract": "We establish that every smooth variety admits a desingularization.",
            "categories": ["math.AG"],
            "published": "2024-01-02T00:00:00+00:00",
        },
    ])

    g = E2ArxivAbstractMiningGenerator(batch_id="test", cache_path=cache)
    records = []
    while True:
        r = g.next()
        if r is None:
            break
        records.append(r)

    assert len(records) >= 2
    for r in records:
        assert r.generator_id == "e2"
        assert r.claim_kind == ClaimKind.LITERATURE_MINED.value
        assert r.verdict == Verdict.UNVERIFIED.value
        assert r.claim_payload["arxiv_id"].startswith("2401.0")
        assert r.method == "regex_pattern_match"


def test_generator_handles_missing_cache(tmp_path):
    """No cache file → generator emits nothing gracefully (no crash)."""
    g = E2ArxivAbstractMiningGenerator(
        batch_id="test",
        cache_path=tmp_path / "nonexistent.jsonl",
    )
    assert g.next() is None


def test_generator_idempotent_record_ids(tmp_path):
    """Same cache → same record_ids on re-run (content-addressed)."""
    cache = tmp_path / "abstracts.jsonl"
    _write_cache(cache, [
        {
            "arxiv_id": "2401.00010",
            "title": "Test",
            "abstract": "Theorem: every nontrivial conjecture admits at least one counterexample.",
            "categories": ["math.NT"],
        },
    ])

    g1 = E2ArxivAbstractMiningGenerator(batch_id="b1", cache_path=cache)
    g2 = E2ArxivAbstractMiningGenerator(batch_id="b2", cache_path=cache)
    ids1 = [r.record_id for r in iter(g1)]
    ids2 = [r.record_id for r in iter(g2)]
    # Same canonical_claim_text → same record_id regardless of batch_id.
    assert ids1 == ids2 and len(ids1) > 0


def test_registry_can_resolve_e2():
    """After lift to its own module, registry must point at the new class."""
    from theseus.registry import get_generator_class

    cls = get_generator_class("e2")
    assert cls is E2ArxivAbstractMiningGenerator
