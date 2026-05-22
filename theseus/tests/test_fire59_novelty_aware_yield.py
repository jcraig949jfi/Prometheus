"""Fire #59: novelty-aware yield_score tests.

The pre-#59 yield_score was novelty-blind: a generator producing 2M
records of repeat shapes scored higher than one producing 1K records
of novel shapes (because score scaled with info_density × diversity
only). The post-#59 formula folds in `novelty_signatures /
records_emitted`, so the bandit prefers genuinely exploring gens.
"""
from __future__ import annotations

from theseus.bandit.yield_proportional import YieldProportionalBandit
from theseus.scoring.metrics_schema import GeneratorMetrics


def _mk(
    gid: str,
    records: int,
    novel: int,
    info: float = 0.5,
    div: float = 0.5,
    steps: int = 1,
) -> GeneratorMetrics:
    return GeneratorMetrics(
        generator_id=gid,
        records_emitted=records,
        info_density_mean=info,
        diversity_mean=div,
        learner_delta_steps=steps,
        novelty_signatures=novel,
    )


def test_zero_novelty_matches_pre_fire59_formula():
    """Backwards compat: novelty_signatures=0 (default) reproduces
    the pre-#59 base score."""
    m = _mk("a", records=100, novel=0, info=0.5, div=0.5, steps=1)
    # Pre-#59: 0.5 × 0.5 / 1 = 0.25. Post-#59 with novelty=0: 0.25 × 1.0 = 0.25.
    assert abs(m.yield_score - 0.25) < 1e-9


def test_high_novelty_rate_outweighs_low_volume():
    """A small-volume high-novelty gen should score higher than a
    high-volume zero-novelty gen with same density/diversity."""
    high_novelty = _mk("c5", records=100, novel=10)  # 10% novelty rate
    high_volume = _mk("d3", records=1_000_000, novel=0)  # 0% novelty
    # Both have base 0.25. Novelty-aware:
    #   c5: 0.25 × (1 + 10×0.1) = 0.25 × 2 = 0.5
    #   d3: 0.25 × 1 = 0.25
    assert high_novelty.yield_score > high_volume.yield_score


def test_novelty_rate_caps_naturally():
    """A reasonable upper bound: 100% novelty rate gives at most
    11x boost (1 + 10×1.0)."""
    m = _mk("ideal", records=10, novel=10, info=0.5, div=0.5, steps=1)
    # base = 0.25; multiplier = 1 + 10 = 11
    assert abs(m.yield_score - 2.75) < 1e-9


def test_zero_records_does_not_divide_by_zero():
    """records=0 (e.g. errored gen) must not raise."""
    m = _mk("err", records=0, novel=0)
    # Should be 0 (info=0.5, div=0.5, base=0.25 but records=0 → novelty_rate=0)
    assert m.yield_score == 0.25  # base survives


def test_bandit_favors_novelty_aware_high_score():
    """The bandit pulls these scores through select(). High-novelty
    arm should be picked disproportionately."""
    b = YieldProportionalBandit(seed=42, temperature=0.05, ucb_c=0.0)
    explorer = _mk("explorer", records=100, novel=20)  # 20% rate
    volume = _mk("volume", records=1_000_000, novel=0)  # 0% rate
    b.update({"explorer": explorer, "volume": volume})
    # Over many picks, explorer should win majority
    picks = []
    for _ in range(200):
        chosen = b.select(["explorer", "volume"], history={}, n=1)
        picks.extend(chosen)
    explorer_count = picks.count("explorer")
    # With 2x score ratio + temp 0.05, explorer should be picked
    # solidly more than half the time.
    assert explorer_count > 110, f"explorer only picked {explorer_count}/200"


def test_novelty_signatures_serializable_via_dataclass():
    """asdict() must round-trip including novelty_signatures (daemon
    writes it to BATCH_LOG.md and structured journal)."""
    from dataclasses import asdict
    m = _mk("a3", records=2_009_786, novel=147)
    d = asdict(m)
    assert d["novelty_signatures"] == 147
    assert d["records_emitted"] == 2_009_786


# ---------- Fire #60: dup-rate penalty ----------


def _mk_full(
    gid: str,
    records: int,
    novel: int = 0,
    dup_rate: float = 0.0,
    info: float = 0.5,
    div: float = 0.5,
    steps: int = 1,
) -> GeneratorMetrics:
    return GeneratorMetrics(
        generator_id=gid,
        records_emitted=records,
        info_density_mean=info,
        diversity_mean=div,
        learner_delta_steps=steps,
        novelty_signatures=novel,
        dup_rate=dup_rate,
    )


def test_zero_dup_rate_does_not_penalize():
    """dup_rate=0 (default) leaves the Fire #59 score unchanged."""
    m = _mk_full("a", records=100, novel=0, dup_rate=0.0)
    # base = 0.25; novelty=1.0; dup_mult = 1.0
    assert abs(m.yield_score - 0.25) < 1e-9


def test_full_saturation_halves_score():
    """dup_rate=1.0 (fully saturated) → 0.5x multiplier on otherwise
    identical score. Saturated gens still get some exploration."""
    m = _mk_full("d1", records=1807, novel=0, dup_rate=1.0)
    # base = 0.25; novelty=1.0; dup_mult = 0.5 → 0.125
    assert abs(m.yield_score - 0.125) < 1e-9


def test_half_dup_rate_three_quarter_score():
    """50% dup → 0.75 multiplier."""
    m = _mk_full("c3", records=1000, novel=0, dup_rate=0.5)
    # base = 0.25 × 0.75 = 0.1875
    assert abs(m.yield_score - 0.1875) < 1e-9


def test_dup_penalty_caps_at_zero():
    """dup_rate > 1.0 (shouldn't happen but be defensive) doesn't
    yield a negative score."""
    m = _mk_full("bad", records=100, novel=0, dup_rate=3.0)
    assert m.yield_score >= 0.0


def test_novelty_bonus_and_dup_penalty_compose():
    """A gen with both 10% novelty rate AND 50% dup_rate:
       base × (1 + 10×0.1) × (1 - 0.5×0.5) = base × 2 × 0.75 = base × 1.5
    """
    m = _mk_full("explorer_partial_sat", records=100, novel=10, dup_rate=0.5)
    # base = 0.25 → 0.25 × 1.5 = 0.375
    assert abs(m.yield_score - 0.375) < 1e-9


def test_bandit_downweights_saturated_arm():
    """Bandit over 200 picks should favor the unsaturated arm even
    when raw record count is identical."""
    b = YieldProportionalBandit(seed=7, temperature=0.05, ucb_c=0.0)
    fresh = _mk_full("fresh", records=100, dup_rate=0.0)
    sat = _mk_full("sat", records=100, dup_rate=1.0)
    b.update({"fresh": fresh, "sat": sat})
    picks = []
    for _ in range(200):
        picks.extend(b.select(["fresh", "sat"], history={}, n=1))
    assert picks.count("fresh") > 120, (
        f"fresh picked {picks.count('fresh')}/200 — penalty too weak"
    )
