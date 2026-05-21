"""Unit tests for E5MathWorldWikipediaScrapeGenerator."""
from __future__ import annotations

import json
from pathlib import Path

from theseus.emit.record_schema import ClaimKind, Verdict
from theseus.generators.base import GeneratorStatus
from theseus.generators.e5_mathworld_wikipedia_scrape import (
    E5MathWorldWikipediaScrapeGenerator,
    _extract_claims_from_text,
)


def _write_cache(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def test_extract_claims_picks_up_states_that():
    text = "The Riemann hypothesis states that every nontrivial zero has real part one-half."
    out = _extract_claims_from_text(text)
    assert len(out) >= 1
    assert "states that" in out[0].lower()


def test_extract_claims_picks_up_proved_by():
    text = "The modularity theorem was proved by Wiles and others over a decade."
    out = _extract_claims_from_text(text)
    assert len(out) >= 1
    assert "proved by" in out[0].lower()


def test_extract_claims_picks_up_conjecture_plural():
    text = "Various conjectures predict that the gap distribution converges to the Poisson law."
    out = _extract_claims_from_text(text)
    assert len(out) >= 1


def test_generator_status_is_active():
    assert E5MathWorldWikipediaScrapeGenerator.status == GeneratorStatus.ACTIVE


def test_generator_emits_records_from_cache(tmp_path):
    cache = tmp_path / "wiki.jsonl"
    _write_cache(cache, [
        {
            "title": "Riemann_hypothesis",
            "extract": "The Riemann hypothesis states that every nontrivial zero of the Riemann zeta function lies on the critical line.",
            "url": "https://en.wikipedia.org/wiki/Riemann_hypothesis",
        },
        {
            "title": "Poincare_conjecture",
            "extract": "The Poincare conjecture was proved by Perelman in a series of papers.",
            "url": "https://en.wikipedia.org/wiki/Poincare_conjecture",
        },
    ])

    g = E5MathWorldWikipediaScrapeGenerator(batch_id="test", cache_path=cache)
    records = []
    while True:
        r = g.next()
        if r is None:
            break
        records.append(r)

    assert len(records) >= 2
    for r in records:
        assert r.generator_id == "e5"
        assert r.claim_kind == ClaimKind.LITERATURE_MINED.value
        assert r.verdict == Verdict.UNVERIFIED.value
        assert "page_title" in r.claim_payload


def test_generator_handles_missing_cache(tmp_path):
    g = E5MathWorldWikipediaScrapeGenerator(
        batch_id="test",
        cache_path=tmp_path / "missing.jsonl",
    )
    assert g.next() is None


def test_registry_can_resolve_e5():
    from theseus.registry import get_generator_class

    cls = get_generator_class("e5")
    assert cls is E5MathWorldWikipediaScrapeGenerator
