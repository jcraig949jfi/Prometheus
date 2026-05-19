"""Tests for Fire #33 — falsify-phase opening + quota.

Validates:
  - REJECTED records' v_mult was boosted (specific=1.0, generic=0.6)
  - export_for_ergon's default verdict_filter now includes REJECTED
  - falsify_share quota guarantees the negative-example floor
  - falsify_share=0 disables the floor (legacy behavior)
"""
from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

import pytest

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.handoff.ergon_handoff import (
    INBOX_SUBDIR,
    DEFAULT_FALSIFY_SHARE,
    export_for_ergon,
)
from theseus.scoring.training_weight import (
    training_weight,
    _verdict_multiplier,
)


def _record(rid: str, verdict: str, kill_pattern: str = None,
            relation: str = "equal_mod_2") -> TheseusRecord:
    return TheseusRecord(
        record_id=rid,
        generator_id="d1",
        batch_id="b",
        emitted_at="2026-05-19T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={
            "relation": relation, "catalog_a": "knot",
            "object_a": f"k{rid}", "invariant_a": "signature",
            "value_a": 2, "catalog_b": "ec",
            "object_b": f"e{rid}", "invariant_b": "rank",
            "value_b": 4, "holds": (verdict == Verdict.SHADOW_CATALOG.value),
        },
        canonical_claim_text=f"{rid} claim",
        verdict=verdict,
        kill_pattern=kill_pattern,
    )


def test_rejected_specific_v_mult_boosted():
    """Fire #33: specific kills now at parity with SHADOW (1.0)."""
    r = _record("r", Verdict.REJECTED.value,
                kill_pattern="F1_triggered_violated")
    assert _verdict_multiplier(r) == 1.0


def test_rejected_generic_v_mult_boosted():
    """Fire #33: generic kills boosted from 0.4 to 0.6."""
    r = _record("r", Verdict.REJECTED.value,
                kill_pattern="some_generic_kill")
    assert _verdict_multiplier(r) == 0.6


def test_specific_kill_still_outranks_generic():
    """Ordering preserved from Fire #15."""
    specific = _record("s", Verdict.REJECTED.value,
                       kill_pattern="F1_triggered_violated")
    generic = _record("g", Verdict.REJECTED.value,
                      kill_pattern="some_generic_kill")
    assert training_weight(specific) > training_weight(generic)


def test_rejected_at_parity_with_shadow_for_specific_kills():
    """A specific kill on the same relation now scores equal to a SHADOW."""
    shadow = _record("s", Verdict.SHADOW_CATALOG.value)
    rejected_specific = _record("r", Verdict.REJECTED.value,
                                kill_pattern="F1_triggered_violated")
    # Same base, same v_mult (1.0 now), same triangulation → equal weight
    assert training_weight(shadow) == training_weight(rejected_specific)


def _build_mixed_corpus(corpus_dir: Path, n_shadow: int = 50,
                       n_rejected: int = 50) -> None:
    """Make a corpus with mixed verdicts so the quota has room to work."""
    records = []
    for i in range(n_shadow):
        records.append(_record(f"s{i}", Verdict.SHADOW_CATALOG.value))
    for i in range(n_rejected):
        records.append(_record(f"r{i}", Verdict.REJECTED.value,
                               kill_pattern="F1_triggered_violated"))
    with (corpus_dir / "batch.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(r.to_jsonl() + "\n")


def test_falsify_share_enforced_at_default_20_pct(tmp_path):
    """20% of a 50-record bundle should be REJECTED, regardless of ranking."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _build_mixed_corpus(corpus)
    out = tmp_path / "outbox"
    result = export_for_ergon(
        corpus_dir=corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=50,
        falsify_share=0.20,
    )
    jsonl_path = Path(result["jsonl_path"])
    verdicts = Counter()
    with jsonl_path.open(encoding="utf-8") as f:
        for ln in f:
            rec = json.loads(ln)
            # Pre-parsed jsonl carries source_record info; verdict isn't
            # in the anchor block but the underlying record id starts
            # with 's' or 'r' from our fixture.
            src = rec.get("source_record_id", "")
            if src.startswith("r"):
                verdicts["REJECTED"] += 1
            elif src.startswith("s"):
                verdicts["SHADOW_CATALOG"] += 1
    # 50 records × 0.20 = 10 REJECTED guaranteed
    assert verdicts["REJECTED"] == 10
    assert verdicts["SHADOW_CATALOG"] == 40


def test_falsify_share_zero_disables_floor(tmp_path):
    """falsify_share=0 returns to weight-only ranking; REJECTED records
    only land if they organically beat SHADOW."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _build_mixed_corpus(corpus, n_shadow=50, n_rejected=50)
    out = tmp_path / "outbox"
    result = export_for_ergon(
        corpus_dir=corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=50,
        falsify_share=0.0,
    )
    # With our fixture, SHADOW and REJECTED-specific score identically.
    # Without a quota, sort stability picks earliest-iterated; that's
    # corpus-walk-order dependent. We just assert the bundle filled.
    jsonl_path = Path(result["jsonl_path"])
    n = sum(1 for _ in jsonl_path.open(encoding="utf-8"))
    assert n == 50


def test_rejected_verdict_in_default_filter(tmp_path):
    """Fire #33: REJECTED records must appear in bundles by default,
    even when the caller doesn't pass falsify_share explicitly."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _build_mixed_corpus(corpus, n_shadow=10, n_rejected=10)
    out = tmp_path / "outbox"
    result = export_for_ergon(
        corpus_dir=corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=20,
        # NB: falsify_share omitted → uses DEFAULT_FALSIFY_SHARE
    )
    jsonl_path = Path(result["jsonl_path"])
    n_rej = 0
    with jsonl_path.open(encoding="utf-8") as f:
        for ln in f:
            rec = json.loads(ln)
            if rec.get("source_record_id", "").startswith("r"):
                n_rej += 1
    # Default falsify_share=0.20 → at least 4 of 20
    assert n_rej >= 4


def test_falsify_pool_smaller_than_quota(tmp_path):
    """If corpus has fewer REJECTED records than the quota wants,
    we take all available and fill the rest from non-REJECTED."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _build_mixed_corpus(corpus, n_shadow=50, n_rejected=3)
    out = tmp_path / "outbox"
    result = export_for_ergon(
        corpus_dir=corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=50,
        falsify_share=0.20,  # wants 10 but only 3 available
    )
    jsonl_path = Path(result["jsonl_path"])
    n_rej = 0
    n_total = 0
    with jsonl_path.open(encoding="utf-8") as f:
        for ln in f:
            rec = json.loads(ln)
            n_total += 1
            if rec.get("source_record_id", "").startswith("r"):
                n_rej += 1
    assert n_total == 50  # bundle still full
    assert n_rej == 3  # took everything we had
