"""Per-batch record cap + bounded Generator.emitted ring.

Regression test for the 2026-05-20 b3 OOM (28M records, 5 MemoryError
events, OS lockup). Two defenses:

1. `Generator.emitted` is now a bounded deque (maxlen=2000) instead of
   an unbounded list. Generators only .append() to it; nothing reads
   the prior contents. The unbounded list was ~2GB at 28M records.

2. `daemon.run_batch` exits the tick loop once
   `total_records_written >= cfg.PER_BATCH_RECORD_CAP`. The cap is in
   `theseus.config.PER_BATCH_RECORD_CAP` (default 5M).
"""
from __future__ import annotations

from collections import deque

from theseus.generators.base import Generator
from theseus.generators import base as base_mod
from theseus import config as cfg


def test_generator_emitted_is_bounded_deque():
    # Pick any concrete generator. Instantiation gives us the ring.
    from theseus.generators.a1_catalog_cross_product import (
        A1CatalogCrossProductGenerator,
    )

    g = A1CatalogCrossProductGenerator(batch_id="test")
    assert isinstance(g.emitted, deque)
    assert g.emitted.maxlen == base_mod._EMITTED_RING_MAXLEN


def test_emitted_ring_truncates_at_maxlen():
    from theseus.generators.a1_catalog_cross_product import (
        A1CatalogCrossProductGenerator,
    )

    g = A1CatalogCrossProductGenerator(batch_id="test")
    # Stuff in 10x the maxlen; deque should hold only the last maxlen.
    for i in range(base_mod._EMITTED_RING_MAXLEN * 10):
        g.emitted.append(f"r{i}")
    assert len(g.emitted) == base_mod._EMITTED_RING_MAXLEN
    # And it kept the *most recent* additions.
    assert g.emitted[-1] == f"r{base_mod._EMITTED_RING_MAXLEN * 10 - 1}"


def test_per_batch_record_cap_constant_is_present_and_reasonable():
    # Smoke: cap exists, is an int, and is in the expected range.
    assert isinstance(cfg.PER_BATCH_RECORD_CAP, int)
    assert 100_000 < cfg.PER_BATCH_RECORD_CAP <= 100_000_000


def test_daemon_run_batch_respects_record_cap(tmp_path, monkeypatch):
    """Run a short batch with a tiny cap; confirm we stop at the cap."""
    from theseus.daemon import run_batch

    # Force a low cap so we hit it quickly.
    monkeypatch.setattr(cfg, "PER_BATCH_RECORD_CAP", 200)

    bm = run_batch(
        generator_ids=["b3"],
        batch_hours=0.05,  # 3 minutes ceiling, but cap should fire first
        seed=42,
        batch_id="batch-cap-test",
        corpus_dir=tmp_path,
        emit_telemetry=False,
    )
    # Cap should hold up to a small overshoot (one tick per generator
    # past the cap check is OK; with one generator the overshoot is <=1).
    assert bm.total_records <= cfg.PER_BATCH_RECORD_CAP + 5
    assert bm.total_records >= cfg.PER_BATCH_RECORD_CAP - 5


def test_corpus_writer_seen_uses_int_keys(tmp_path):
    """The dedup set now stores ints (digest keys), not full strings."""
    from theseus.emit.corpus_writer import CorpusWriter
    from theseus.emit.record_schema import (
        TheseusRecord,
        ClaimKind,
        Verdict,
    )

    w = CorpusWriter(batch_id="test", corpus_dir=tmp_path)
    rid = TheseusRecord.compute_record_id("claim", "a1")
    r = TheseusRecord(
        record_id=rid,
        generator_id="a1",
        batch_id="batch-test",
        emitted_at="2026-05-21T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={},
        canonical_claim_text="claim",
        verdict=Verdict.UNVERIFIED.value,
    )
    w.write(r)
    # _seen is a set of ints, not strs.
    assert len(w._seen) == 1
    only = next(iter(w._seen))
    assert isinstance(only, int)
