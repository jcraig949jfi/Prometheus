"""Tests for TheseusRecord schema."""
from __future__ import annotations

import json

import pytest

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict


def _make_record(text: str = "claim text", gid: str = "a1") -> TheseusRecord:
    rid = TheseusRecord.compute_record_id(text, gid)
    return TheseusRecord(
        record_id=rid,
        generator_id=gid,
        batch_id="batch-test",
        emitted_at="2026-05-18T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={"x": 1},
        canonical_claim_text=text,
        verdict=Verdict.UNVERIFIED.value,
    )


def test_record_id_is_content_addressed():
    a = TheseusRecord.compute_record_id("foo", "a1")
    b = TheseusRecord.compute_record_id("foo", "a1")
    assert a == b


def test_record_id_differs_by_generator():
    a = TheseusRecord.compute_record_id("foo", "a1")
    b = TheseusRecord.compute_record_id("foo", "c1")
    assert a != b


def test_record_id_differs_by_text():
    a = TheseusRecord.compute_record_id("foo", "a1")
    b = TheseusRecord.compute_record_id("bar", "a1")
    assert a != b


def test_jsonl_roundtrips():
    r = _make_record()
    line = r.to_jsonl()
    parsed = json.loads(line)
    assert parsed["record_id"] == r.record_id
    assert parsed["generator_id"] == r.generator_id
    assert parsed["claim_payload"] == {"x": 1}


def test_claim_kind_values_are_strings():
    for ck in ClaimKind:
        assert isinstance(ck.value, str)


def test_verdict_values_are_strings():
    for v in Verdict:
        assert isinstance(v.value, str)
