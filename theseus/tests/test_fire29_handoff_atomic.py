"""Tests for Fire #29 atomic-write + partition handoff protocol."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.handoff.ergon_handoff import (
    export_for_ergon,
    INBOX_SUBDIR,
    CONSUMED_SUBDIR,
    REJECTED_SUBDIR,
)


@pytest.fixture
def synthetic_corpus(tmp_path: Path) -> Path:
    """Make a small corpus with high-weight SHADOW records."""
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
                "relation": "equal_mod_2",
                "catalog_a": "knot",
                "object_a": f"k{i}",
                "invariant_a": "signature",
                "value_a": 2,
                "catalog_b": "ec",
                "object_b": f"e{i}",
                "invariant_b": "rank",
                "value_b": 4,
                "holds": True,
            },
            canonical_claim_text=f"r{i} claim",
            verdict=Verdict.SHADOW_CATALOG.value,
        )
        records.append(r)
    with (corpus_dir / "batch-synthetic.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(r.to_jsonl() + "\n")
    return corpus_dir


def test_partitions_created_on_emission(synthetic_corpus, tmp_path):
    out = tmp_path / "outbox"
    export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    assert (out / INBOX_SUBDIR).is_dir()
    assert (out / CONSUMED_SUBDIR).is_dir()
    assert (out / REJECTED_SUBDIR).is_dir()


def test_three_files_per_bundle(synthetic_corpus, tmp_path):
    out = tmp_path / "outbox"
    stats = export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    md = Path(stats["markdown_path"])
    jsonl = Path(stats["jsonl_path"])
    complete = Path(stats["complete_marker"])
    assert md.exists() and md.suffix == ".md"
    assert jsonl.exists() and jsonl.suffix == ".jsonl"
    assert complete.exists() and complete.suffix == ".complete"
    # All three share the same base name
    assert md.stem == jsonl.stem == complete.stem


def test_complete_sentinel_is_zero_byte(synthetic_corpus, tmp_path):
    out = tmp_path / "outbox"
    stats = export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    complete = Path(stats["complete_marker"])
    assert complete.read_bytes() == b""


def test_no_tmp_files_left_after_emission(synthetic_corpus, tmp_path):
    out = tmp_path / "outbox"
    export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    tmp_files = list((out / INBOX_SUBDIR).glob("*.tmp"))
    assert tmp_files == [], f"left-over tmp files: {tmp_files}"


def test_bundle_lands_in_inbox(synthetic_corpus, tmp_path):
    out = tmp_path / "outbox"
    stats = export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    md = Path(stats["markdown_path"])
    assert md.parent.name == INBOX_SUBDIR


def test_jsonl_record_count_matches_emitted(synthetic_corpus, tmp_path):
    out = tmp_path / "outbox"
    stats = export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    n = stats["n_emitted"]
    jsonl = Path(stats["jsonl_path"])
    lines = jsonl.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == n
    for line in lines:
        rec = json.loads(line)
        assert rec["block_type"] == "training_anchor"


def test_two_consecutive_emissions_distinct_timestamps(synthetic_corpus, tmp_path):
    """Bundles share filename pattern but timestamps differ enough that
    consecutive emissions don't collide."""
    out = tmp_path / "outbox"
    import time
    s1 = export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    time.sleep(1.1)  # ensure timestamp tick
    s2 = export_for_ergon(
        corpus_dir=synthetic_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=5,
    )
    assert s1["markdown_path"] != s2["markdown_path"]
