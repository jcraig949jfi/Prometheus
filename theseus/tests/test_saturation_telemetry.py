"""Saturation telemetry: per-generator dup_rate in BatchMetrics.

Closes the one-way reporting gap with Penelope (Ergon's ingester),
which reports 90% duplicates downstream. The CorpusWriter now tracks
per-gen dup vs unique counts in-batch; daemon folds dup_rate into
each GeneratorMetrics so journal/dashboard/bandit-history see it.

Per persona_seed_prompts_2026-05-21.md Techne idea #4:
"Theseus saturation telemetry. Penelope's 90% duplicate rate is a
saturation signal. Add a 'primitive coverage' metric... fire a
'kernel saturated, expand vocabulary' anomaly."
"""
from __future__ import annotations

from theseus.emit.corpus_writer import CorpusWriter
from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict


def _mk(text: str, gid: str = "a1") -> TheseusRecord:
    rid = TheseusRecord.compute_record_id(text, gid)
    return TheseusRecord(
        record_id=rid,
        generator_id=gid,
        batch_id="t",
        emitted_at="2026-05-22T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={},
        canonical_claim_text=text,
        verdict=Verdict.UNVERIFIED.value,
    )


def test_dup_rate_zero_when_no_duplicates(tmp_path):
    w = CorpusWriter(batch_id="b", corpus_dir=tmp_path)
    for i in range(5):
        w.write(_mk(f"claim {i}", "a1"))
    rates = w.dup_rate_by_gen()
    assert rates["a1"] == 0.0


def test_dup_rate_one_when_all_duplicates(tmp_path):
    w = CorpusWriter(batch_id="b", corpus_dir=tmp_path)
    w.write(_mk("same", "a1"))
    for _ in range(9):
        w.write(_mk("same", "a1"))
    rates = w.dup_rate_by_gen()
    # 1 unique + 9 dups → 9/10 = 0.9
    assert abs(rates["a1"] - 0.9) < 1e-9


def test_dup_rate_per_gen_separation(tmp_path):
    w = CorpusWriter(batch_id="b", corpus_dir=tmp_path)
    # a1: 5 unique, 0 dups
    for i in range(5):
        w.write(_mk(f"a-claim-{i}", "a1"))
    # b5: 1 unique, 4 dups
    w.write(_mk("b-claim", "b5"))
    for _ in range(4):
        w.write(_mk("b-claim", "b5"))
    rates = w.dup_rate_by_gen()
    assert rates["a1"] == 0.0
    assert abs(rates["b5"] - 0.8) < 1e-9


def test_dup_rate_excludes_unfired_gens(tmp_path):
    w = CorpusWriter(batch_id="b", corpus_dir=tmp_path)
    w.write(_mk("x", "a1"))
    rates = w.dup_rate_by_gen()
    assert "b5" not in rates


def test_writer_tracks_unique_and_dup_separately(tmp_path):
    w = CorpusWriter(batch_id="b", corpus_dir=tmp_path)
    w.write(_mk("u1", "a1"))
    w.write(_mk("u1", "a1"))  # dup
    w.write(_mk("u2", "a1"))
    assert w.unique_by_gen["a1"] == 2
    assert w.duplicates_by_gen["a1"] == 1


def test_generator_metrics_dup_rate_default_zero():
    """Backwards-compat: existing records without dup_rate read as 0."""
    from theseus.scoring.metrics_schema import GeneratorMetrics
    m = GeneratorMetrics(generator_id="a1")
    assert m.dup_rate == 0.0


def test_run_batch_populates_dup_rate(tmp_path, monkeypatch):
    """End-to-end: run_batch's BatchMetrics carries per-gen dup_rate."""
    from theseus.daemon import run_batch
    from theseus import config as cfg

    monkeypatch.setattr(cfg, "JOURNAL_DIR", tmp_path / "journal")
    monkeypatch.setattr(
        cfg, "BATCH_LOG_PATH", tmp_path / "journal" / "BATCH_LOG.md"
    )
    monkeypatch.setattr(
        cfg, "BATCHES_JSONL_PATH", tmp_path / "journal" / "batches.jsonl"
    )
    monkeypatch.setattr(cfg, "PER_BATCH_RECORD_CAP", 200)

    bm = run_batch(
        generator_ids=["b3"],
        batch_hours=0.001,
        seed=0,
        corpus_dir=tmp_path,
        emit_telemetry=False,
    )
    # b3 in the metrics
    assert "b3" in bm.per_generator
    m = bm.per_generator["b3"]
    # dup_rate is a real float in [0, 1]
    assert 0.0 <= m.dup_rate <= 1.0
