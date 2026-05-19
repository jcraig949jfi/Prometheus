"""Tests for corpus_files helpers and handoff_daemon (Fire #32).

Validates:
  - iter_batch_paths returns both .jsonl and .jsonl.gz, sorted, no annotated
  - open_batch transparently handles both
  - find_compactable_batches respects age + already-compacted siblings
  - compress_batch is atomic (tmp → final, old .jsonl removed)
  - episode composer + ergon_handoff still work on a mixed corpus
"""
from __future__ import annotations

import gzip
import json
import os
import time
from pathlib import Path

import pytest

from theseus.emit.corpus_files import (
    iter_batch_paths,
    open_batch,
    iter_batch_lines,
)
from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.handoff.handoff_daemon import (
    find_compactable_batches,
    compress_batch,
    run_cycle,
)
from theseus.handoff.episodes import assign_episodes


def _write_batch(path: Path, n: int = 3) -> None:
    """Write n minimal valid records as JSONL."""
    with path.open("w", encoding="utf-8") as f:
        for i in range(n):
            r = TheseusRecord(
                record_id=f"{path.stem}-r{i}",
                generator_id="a1",
                batch_id=path.stem,
                emitted_at="2026-05-19T00:00:00Z",
                claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
                claim_payload={
                    "relation": "equal", "catalog_a": "knot",
                    "object_a": f"k{i}", "invariant_a": "signature",
                    "value_a": 1, "catalog_b": "ec",
                    "object_b": f"e{i}", "invariant_b": "rank",
                    "value_b": 1, "holds": True,
                },
                canonical_claim_text=f"claim {i}",
                verdict=Verdict.SHADOW_CATALOG.value,
            )
            f.write(r.to_jsonl() + "\n")


def test_iter_batch_paths_mixed(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    p_plain = corpus / "batch-A.jsonl"
    p_gz = corpus / "batch-B.jsonl.gz"
    p_annot = corpus / "batch-C.annotated.jsonl"
    _write_batch(p_plain, 2)
    with gzip.open(p_gz, "wt", encoding="utf-8") as f:
        f.write('{"hello": "gz"}\n')
    p_annot.write_text("{}\n", encoding="utf-8")
    paths = iter_batch_paths(corpus)
    names = [p.name for p in paths]
    assert "batch-A.jsonl" in names
    assert "batch-B.jsonl.gz" in names
    assert "batch-C.annotated.jsonl" not in names
    # Sorted by name → batch-A before batch-B
    assert names.index("batch-A.jsonl") < names.index("batch-B.jsonl.gz")


def test_open_batch_transparent_for_gz(tmp_path):
    p = tmp_path / "data.jsonl.gz"
    with gzip.open(p, "wt", encoding="utf-8") as f:
        f.write("line1\nline2\n")
    with open_batch(p) as f:
        lines = [ln.rstrip() for ln in f]
    assert lines == ["line1", "line2"]


def test_iter_batch_lines_skips_blanks(tmp_path):
    p = tmp_path / "data.jsonl"
    p.write_text("a\n\nb\n\n\nc\n", encoding="utf-8")
    assert list(iter_batch_lines(p)) == ["a", "b", "c"]


def test_iter_batch_paths_empty_dir(tmp_path):
    """Empty corpus dir → empty list, no exception."""
    empty = tmp_path / "empty"
    empty.mkdir()
    assert iter_batch_paths(empty) == []
    # Nonexistent dir also returns []
    assert iter_batch_paths(tmp_path / "ghost") == []


def test_find_compactable_skips_recent_and_already_compacted(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    fresh = corpus / "fresh.jsonl"
    old = corpus / "old.jsonl"
    already = corpus / "already.jsonl"
    already_gz = corpus / "already.jsonl.gz"
    _write_batch(fresh)
    _write_batch(old)
    _write_batch(already)
    already_gz.write_bytes(b"\x1f\x8b\x08\x00")  # dummy gzip header
    # Backdate `old` and `already` to 1 hour ago
    one_hour_ago = time.time() - 3600
    os.utime(old, (one_hour_ago, one_hour_ago))
    os.utime(already, (one_hour_ago, one_hour_ago))
    targets = find_compactable_batches(corpus, older_than_minutes=15)
    target_names = [p.name for p in targets]
    assert "fresh.jsonl" not in target_names           # too recent
    assert "already.jsonl" not in target_names         # already has .gz sibling
    assert "old.jsonl" in target_names                 # eligible


def test_compress_batch_is_atomic_and_size_reduces(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    p = corpus / "compactme.jsonl"
    _write_batch(p, n=100)  # more rows → real compression ratio
    before_size = p.stat().st_size
    bytes_before, bytes_after = compress_batch(p)
    assert bytes_before == before_size
    assert bytes_after < bytes_before  # JSONL compresses
    assert not p.exists()
    assert (corpus / "compactme.jsonl.gz").exists()
    # No leftover tmp file
    assert not (corpus / "compactme.jsonl.gz.tmp").exists()
    # Content survives round-trip
    paths = iter_batch_paths(corpus)
    assert len(paths) == 1 and paths[0].suffix == ".gz"
    with open_batch(paths[0]) as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    assert len(rows) == 100
    assert rows[0]["generator_id"] == "a1"


def test_episode_composer_works_on_gz_corpus(tmp_path):
    """assign_episodes must read compressed batches transparently."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    plain = corpus / "b1.jsonl"
    _write_batch(plain, n=5)
    # Compress half the corpus
    p2 = corpus / "b2.jsonl"
    _write_batch(p2, n=5)
    compress_batch(p2)
    # Episodes still assignable
    record_to_episode, episode_meta = assign_episodes(corpus)
    assert len(record_to_episode) == 10  # 5 from plain + 5 from gz


def test_run_cycle_emits_and_compacts(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    # One old batch eligible for compaction, one fresh
    old = corpus / "batch-old.jsonl"
    fresh = corpus / "batch-fresh.jsonl"
    _write_batch(old, n=20)
    _write_batch(fresh, n=20)
    one_hour_ago = time.time() - 3600
    os.utime(old, (one_hour_ago, one_hour_ago))
    outbox = tmp_path / "outbox"
    inbox = outbox / "inbox"
    summary = run_cycle(
        emit_max_records=10,
        emit_weight_threshold=0.0,
        compact_after_minutes=15,
        corpus_dir=corpus,
        inbox_dir=inbox,
    )
    # Emit produced a bundle
    assert summary["emit"]["ok"] is True
    assert summary["emit"]["records"] > 0
    # Compaction got the old batch only
    assert summary["compaction"]["n_batches"] == 1
    assert (corpus / "batch-old.jsonl.gz").exists()
    assert not (corpus / "batch-old.jsonl").exists()
    assert (corpus / "batch-fresh.jsonl").exists()
    # Inbox got the bundle
    assert len(list(inbox.glob("*.complete"))) == 1
