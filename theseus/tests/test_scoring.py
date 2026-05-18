"""Tests for scoring (yield_tracker, info_density, diversity)."""
from __future__ import annotations

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.scoring.info_density import info_density_score
from theseus.scoring.diversity import diversity_score
from theseus.scoring.yield_tracker import YieldTracker


def _make(verdict: str, kp: str | None = None, text: str = "x") -> TheseusRecord:
    return TheseusRecord(
        record_id=TheseusRecord.compute_record_id(text, "g"),
        generator_id="g",
        batch_id="b",
        emitted_at="2026-05-18T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={},
        canonical_claim_text=text,
        verdict=verdict,
        kill_pattern=kp,
    )


def test_info_density_specific_kill_higher_than_generic():
    specific = _make(Verdict.REJECTED.value, "F1_triggered_band_violation")
    generic = _make(Verdict.REJECTED.value, None)
    assert info_density_score(specific) > info_density_score(generic)


def test_info_density_promoted_high():
    promoted = _make(Verdict.PROMOTED.value)
    assert info_density_score(promoted) > 0.9


def test_info_density_unverified_low():
    unv = _make(Verdict.UNVERIFIED.value)
    assert info_density_score(unv) < 0.3


def test_diversity_empty_recent_returns_one():
    r = _make(Verdict.UNVERIFIED.value, text="alpha beta gamma")
    assert diversity_score(r, []) == 1.0


def test_diversity_identical_returns_zero():
    r = _make(Verdict.UNVERIFIED.value, text="alpha beta gamma")
    r2 = _make(Verdict.UNVERIFIED.value, text="alpha beta gamma")
    assert diversity_score(r, [r2]) == 0.0


def test_diversity_disjoint_returns_one():
    r = _make(Verdict.UNVERIFIED.value, text="alpha beta gamma")
    r2 = _make(Verdict.UNVERIFIED.value, text="delta epsilon zeta")
    assert diversity_score(r, [r2]) == 1.0


def test_yield_tracker_accumulates():
    yt = YieldTracker()
    yt.start_generator("g")
    for v in [Verdict.REJECTED.value, Verdict.SHADOW_CATALOG.value, Verdict.UNVERIFIED.value]:
        yt.record_emission(_make(v, text=v))
    yt.stop_generator("g")
    final = yt.finalize()
    m = final["g"]
    assert m.records_emitted == 3
    assert m.kills == 1
    assert m.confirmations == 1
    assert m.inconclusive == 0
    assert 0.0 < m.info_density_mean < 1.0
