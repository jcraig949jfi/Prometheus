"""Tests for CorpusWriter."""
from __future__ import annotations

import json

import pytest

from theseus.emit.corpus_writer import CorpusWriter
from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict


def _make_record(text: str, gid: str = "a1") -> TheseusRecord:
    rid = TheseusRecord.compute_record_id(text, gid)
    return TheseusRecord(
        record_id=rid,
        generator_id=gid,
        batch_id="batch-test",
        emitted_at="2026-05-18T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={},
        canonical_claim_text=text,
        verdict=Verdict.UNVERIFIED.value,
    )


def test_writer_dedups_within_batch(tmp_path):
    w = CorpusWriter(batch_id="b1", corpus_dir=tmp_path)
    r1 = _make_record("same claim")
    r2 = _make_record("same claim")
    assert w.write(r1) is True
    assert w.write(r2) is False
    assert w.records_written == 1
    assert w.duplicates_skipped == 1


def test_writer_appends_jsonl(tmp_path):
    w = CorpusWriter(batch_id="b2", corpus_dir=tmp_path)
    w.write(_make_record("claim 1"))
    w.write(_make_record("claim 2"))
    assert w.records_written == 2
    lines = (tmp_path / "b2.jsonl").read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    parsed = [json.loads(l) for l in lines]
    assert {p["canonical_claim_text"] for p in parsed} == {"claim 1", "claim 2"}


def test_write_many_returns_count(tmp_path):
    w = CorpusWriter(batch_id="b3", corpus_dir=tmp_path)
    rs = [_make_record(f"claim {i}") for i in range(5)]
    n = w.write_many(rs + [rs[0]])  # one duplicate
    assert n == 5
