"""Unit tests for E4LMFDBKnowledgeMiningGenerator."""
from __future__ import annotations

import json
from pathlib import Path

from theseus.emit.record_schema import ClaimKind, Verdict
from theseus.generators.base import GeneratorStatus
from theseus.generators.e4_lmfdb_knowledge_mining import (
    E4LMFDBKnowledgeMiningGenerator,
    _extract_claims_from_text,
    _strip_tex,
)


def _write_cache(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def test_strip_tex_removes_inline_math():
    text = "The Riemann zeta function $\\zeta(s) = \\sum 1/n^s$ converges for some s."
    out = _strip_tex(text)
    assert "$" not in out
    assert "MATH" in out


def test_strip_tex_removes_display_math():
    text = "We have \\[ E_2(\\tau) = ... \\] which converges."
    out = _strip_tex(text)
    assert "\\[" not in out and "\\]" not in out


def test_extract_claims_picks_up_conjecture():
    text = "The Birch and Swinnerton-Dyer conjecture predicts that the rank equals the order of vanishing."
    out = _extract_claims_from_text(text)
    assert len(out) >= 1
    assert "conjecture" in out[0].lower()


def test_extract_claims_picks_up_is_defined_as():
    text = "An elliptic curve is defined as a smooth projective curve of genus one with a marked rational point."
    out = _extract_claims_from_text(text)
    assert len(out) >= 1


def test_generator_status_is_active():
    assert E4LMFDBKnowledgeMiningGenerator.status == GeneratorStatus.ACTIVE


def test_generator_emits_records_from_cache(tmp_path):
    cache = tmp_path / "knowls.jsonl"
    _write_cache(cache, [
        {
            "id": "ec.q.bsd_conjecture",
            "title": "Birch and Swinnerton-Dyer conjecture",
            "content": "The conjecture predicts that the rank of an elliptic curve equals the order of vanishing of its L-function at s=1.",
            "category": "ec.q",
        },
        {
            "id": "mf.elliptic.lfunction",
            "title": "L-function of an elliptic curve",
            "content": "The L-function is defined as an Euler product over primes.",
            "category": "mf",
        },
    ])

    g = E4LMFDBKnowledgeMiningGenerator(batch_id="test", cache_path=cache)
    records = []
    while True:
        r = g.next()
        if r is None:
            break
        records.append(r)

    assert len(records) >= 2
    for r in records:
        assert r.generator_id == "e4"
        assert r.claim_kind == ClaimKind.LITERATURE_MINED.value
        assert r.verdict == Verdict.UNVERIFIED.value
        assert "knowl_id" in r.claim_payload


def test_generator_handles_missing_cache(tmp_path):
    g = E4LMFDBKnowledgeMiningGenerator(
        batch_id="test",
        cache_path=tmp_path / "missing.jsonl",
    )
    assert g.next() is None


def test_registry_can_resolve_e4():
    from theseus.registry import get_generator_class

    cls = get_generator_class("e4")
    assert cls is E4LMFDBKnowledgeMiningGenerator
