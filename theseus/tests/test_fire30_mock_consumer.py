"""Tests for the mock consumer (reference implementation of the
Theseus → Ergon handoff contract)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.handoff.ergon_handoff import (
    INBOX_SUBDIR,
    CONSUMED_SUBDIR,
    REJECTED_SUBDIR,
    export_for_ergon,
)
from theseus.handoff.mock_consumer import (
    discover_ready_bundles,
    validate_bundle,
    consume_bundle,
    consume_inbox,
)


@pytest.fixture
def synthetic_corpus(tmp_path: Path) -> Path:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    records = []
    for i in range(5):
        r = TheseusRecord(
            record_id=f"r{i}",
            generator_id="a1",
            batch_id="b1",
            emitted_at="2026-05-18T00:00:00Z",
            claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
            claim_payload={
                "relation": "equal_mod_2", "catalog_a": "knot",
                "object_a": f"k{i}", "invariant_a": "signature",
                "value_a": 2, "catalog_b": "ec",
                "object_b": f"e{i}", "invariant_b": "rank",
                "value_b": 4, "holds": True,
            },
            canonical_claim_text=f"r{i} claim",
            verdict=Verdict.SHADOW_CATALOG.value,
        )
        records.append(r)
    with (corpus_dir / "batch.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(r.to_jsonl() + "\n")
    return corpus_dir


@pytest.fixture
def primed_outbox(synthetic_corpus, tmp_path) -> Path:
    out = tmp_path / "outbox"
    export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    return out


def test_discover_finds_ready_bundle(primed_outbox):
    bundles = discover_ready_bundles(primed_outbox / INBOX_SUBDIR)
    assert len(bundles) == 1
    assert bundles[0].suffix == ".complete"


def test_discover_skips_bundle_without_complete(primed_outbox, tmp_path):
    # Drop the .complete sentinel to simulate mid-write state
    inbox = primed_outbox / INBOX_SUBDIR
    complete = next(inbox.glob("*.complete"))
    complete.unlink()
    bundles = discover_ready_bundles(inbox)
    assert bundles == []


def test_validate_bundle_ok(primed_outbox):
    jsonl = next((primed_outbox / INBOX_SUBDIR).glob("*.jsonl"))
    ok, msg = validate_bundle(jsonl)
    assert ok is True
    assert "5 records" in msg


def test_validate_bundle_rejects_missing_payload(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text(
        '{"block_type": "training_anchor"}\n', encoding="utf-8"
    )
    ok, msg = validate_bundle(bad)
    assert ok is False
    assert "missing payload" in msg


def test_consume_moves_bundle_to_consumed(primed_outbox):
    results = consume_inbox(
        primed_outbox / INBOX_SUBDIR,
        primed_outbox / CONSUMED_SUBDIR,
        primed_outbox / REJECTED_SUBDIR,
        dry_run=False,
    )
    assert len(results) == 1
    assert results[0]["moved"] is True
    assert results[0]["moved_to"] == CONSUMED_SUBDIR
    # Inbox now empty (no .complete)
    assert list((primed_outbox / INBOX_SUBDIR).glob("*.complete")) == []
    # Consumed has the 3 files
    consumed_files = list((primed_outbox / CONSUMED_SUBDIR).iterdir())
    assert len(consumed_files) == 3
    extensions = sorted(f.suffix for f in consumed_files)
    assert extensions == [".complete", ".jsonl", ".md"]


def test_consume_dry_run_does_not_move(primed_outbox):
    results = consume_inbox(
        primed_outbox / INBOX_SUBDIR,
        primed_outbox / CONSUMED_SUBDIR,
        primed_outbox / REJECTED_SUBDIR,
        dry_run=True,
    )
    assert results[0]["moved"] is False
    # Inbox still has all 3 files
    inbox_files = sorted(f.name for f in (primed_outbox / INBOX_SUBDIR).iterdir())
    assert any(f.endswith(".complete") for f in inbox_files)


def test_consume_idempotent_on_empty_inbox(tmp_path):
    out = tmp_path / "outbox"
    (out / INBOX_SUBDIR).mkdir(parents=True)
    (out / CONSUMED_SUBDIR).mkdir(parents=True)
    (out / REJECTED_SUBDIR).mkdir(parents=True)
    results = consume_inbox(
        out / INBOX_SUBDIR,
        out / CONSUMED_SUBDIR,
        out / REJECTED_SUBDIR,
    )
    assert results == []


def test_consume_skips_tmp_files(primed_outbox):
    # Drop a fake .tmp file in inbox; consumer should ignore it
    inbox = primed_outbox / INBOX_SUBDIR
    (inbox / "leftover.md.tmp").write_text("orphan", encoding="utf-8")
    bundles = discover_ready_bundles(inbox)
    # Still finds the real bundle
    assert len(bundles) == 1
    # And the tmp file is still there (not consumed)
    assert (inbox / "leftover.md.tmp").exists()


def test_rejected_bundle_routes_to_rejected(primed_outbox):
    # Corrupt the JSONL to fail validation
    jsonl = next((primed_outbox / INBOX_SUBDIR).glob("*.jsonl"))
    jsonl.write_text(
        '{"block_type": "training_anchor"}\n', encoding="utf-8"
    )
    results = consume_inbox(
        primed_outbox / INBOX_SUBDIR,
        primed_outbox / CONSUMED_SUBDIR,
        primed_outbox / REJECTED_SUBDIR,
    )
    assert results[0]["moved"] is True
    assert results[0]["moved_to"] == REJECTED_SUBDIR
    # All 3 files end up in rejected/
    rejected_files = list((primed_outbox / REJECTED_SUBDIR).iterdir())
    assert len(rejected_files) == 3
