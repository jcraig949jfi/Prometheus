"""Fire #59/60/62: yield_score evolution tests.

History:
- Fire #59: novelty rate (novelty_signatures / records) folded in.
  Falsified Fire #61 — the rate was too weak at observed scales
  (35 novel / 1.3M records = boost 1.0003).
- Fire #60: dup-rate penalty (1 - 0.5 × dup_rate). Kept.
- Fire #62: novelty-rate REPLACED with lifetime-saturation premium.
  c5 at 9% sat → 5.55x boost; saturated gens → ~1x. Stable signal.

novelty_signatures field is preserved (informational journal) but
no longer drives the score.
"""
from __future__ import annotations

from theseus.bandit.yield_proportional import YieldProportionalBandit
from theseus.scoring.metrics_schema import GeneratorMetrics


def _mk(
    gid: str,
    records: int = 100,
    novel: int = 0,
    dup_rate: float = 0.0,
    lifetime_sat: float = -1.0,
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
        lifetime_saturation=lifetime_sat,
    )


# ---------- Backwards-compat (default sentinel) ----------


def test_no_lifetime_sat_signal_reproduces_base():
    """Legacy history with lifetime_saturation=-1 (unknown) reproduces
    the pre-#62 base × (1 - 0.5 × dup_rate) score."""
    m = _mk("legacy", dup_rate=0.0, lifetime_sat=-1.0)
    # base = 0.25; exploration_boost = 1.0 (no signal); dup_mult = 1.0
    assert abs(m.yield_score - 0.25) < 1e-9


def test_no_lifetime_sat_still_honors_dup_penalty():
    """dup_rate penalty applies even without lifetime_sat signal."""
    m = _mk("legacy_saturated", dup_rate=1.0, lifetime_sat=-1.0)
    # base = 0.25; exploration_boost = 1.0; dup_mult = 0.5
    assert abs(m.yield_score - 0.125) < 1e-9


# ---------- Fire #62: lifetime-saturation premium ----------


def test_c5_style_explorer_gets_strong_boost():
    """c5 at ~9% lifetime saturation → 1 + 5 × 0.91 = 5.55x boost."""
    m = _mk("c5_like", lifetime_sat=0.09, dup_rate=0.0)
    # base = 0.25; boost = 1 + 5×0.91 = 5.55; dup = 1.0
    expected = 0.25 * (1 + 5 * (1 - 0.09))
    assert abs(m.yield_score - expected) < 1e-9


def test_saturated_gen_gets_minimal_boost():
    """A gen at 100% lifetime sat → 1x boost (no exploration premium)."""
    m = _mk("saturated", lifetime_sat=1.0, dup_rate=0.0)
    # base = 0.25; boost = 1.0
    assert abs(m.yield_score - 0.25) < 1e-9


def test_partially_saturated_gen_gets_moderate_boost():
    """50% sat → 1 + 5 × 0.5 = 3.5x boost."""
    m = _mk("mid_sat", lifetime_sat=0.5)
    expected = 0.25 * 3.5
    assert abs(m.yield_score - expected) < 1e-9


def test_explorer_beats_saturated_by_5x():
    """The whole point of Fire #62: c5-style explorer should score
    much higher than a saturated gen with identical base."""
    explorer = _mk("c5_like", lifetime_sat=0.09, dup_rate=0.0)
    saturated = _mk("saturated", lifetime_sat=1.0, dup_rate=0.0)
    # explorer: 0.25 × 5.55 = 1.39
    # saturated: 0.25 × 1.0 = 0.25
    # ratio ~ 5.55x
    assert explorer.yield_score / saturated.yield_score > 4.0


def test_lifetime_sat_signal_outweighs_per_batch_novelty():
    """Even a gen with high single-batch novelty_signatures should
    yield to a gen with lower-saturation lifetime signal (the
    fundamental change in Fire #62).

    Pre-#62 formula would have favored explorer_burst (10 novel /
    100 records = 10% rate). Post-#62 ignores novelty_signatures
    and uses lifetime_saturation only.
    """
    explorer_burst = _mk("burst", records=100, novel=10, lifetime_sat=1.0)
    explorer_lifetime = _mk("lifetime", records=100, novel=0, lifetime_sat=0.09)
    assert explorer_lifetime.yield_score > explorer_burst.yield_score


# ---------- Fire #60: dup-rate penalty (kept) ----------


def test_zero_dup_rate_does_not_penalize():
    m = _mk("a", dup_rate=0.0)
    assert abs(m.yield_score - 0.25) < 1e-9


def test_full_saturation_halves_score():
    m = _mk("d1", dup_rate=1.0)
    assert abs(m.yield_score - 0.125) < 1e-9


def test_half_dup_rate_three_quarter_score():
    m = _mk("c3", dup_rate=0.5)
    assert abs(m.yield_score - 0.1875) < 1e-9


def test_dup_penalty_caps_at_zero():
    m = _mk("bad", dup_rate=3.0)
    assert m.yield_score >= 0.0


def test_exploration_boost_and_dup_penalty_compose():
    """c5-style: lifetime_sat=0.09 AND dup_rate=0.5:
       base × (1 + 5 × 0.91) × (1 - 0.5 × 0.5)
       = 0.25 × 5.55 × 0.75
       = 1.0406
    """
    m = _mk("partial_sat_explorer", lifetime_sat=0.09, dup_rate=0.5)
    expected = 0.25 * (1 + 5 * 0.91) * 0.75
    assert abs(m.yield_score - expected) < 1e-9


# ---------- Bandit integration ----------


def test_bandit_favors_low_lifetime_sat():
    """Over 200 picks, the low-sat (explorer) arm should dominate."""
    b = YieldProportionalBandit(seed=42, temperature=0.05, ucb_c=0.0)
    explorer = _mk("explorer", lifetime_sat=0.09)
    saturated = _mk("saturated", lifetime_sat=1.0)
    b.update({"explorer": explorer, "saturated": saturated})
    picks = []
    for _ in range(200):
        picks.extend(b.select(["explorer", "saturated"], history={}, n=1))
    assert picks.count("explorer") > 150, (
        f"explorer only picked {picks.count('explorer')}/200 — "
        f"sat-driven boost too weak"
    )


def test_bandit_downweights_dup_saturated_arm():
    """Per-batch dup penalty still works alongside lifetime signal."""
    b = YieldProportionalBandit(seed=7, temperature=0.05, ucb_c=0.0)
    fresh = _mk("fresh", dup_rate=0.0, lifetime_sat=-1.0)
    sat = _mk("sat", dup_rate=1.0, lifetime_sat=-1.0)
    b.update({"fresh": fresh, "sat": sat})
    picks = []
    for _ in range(200):
        picks.extend(b.select(["fresh", "sat"], history={}, n=1))
    assert picks.count("fresh") > 120


# ---------- Serialization ----------


def test_lifetime_saturation_serializable_via_dataclass():
    from dataclasses import asdict
    m = _mk("c5", lifetime_sat=0.091)
    d = asdict(m)
    assert d["lifetime_saturation"] == 0.091
    assert d["records_emitted"] == 100


def test_novelty_signatures_still_preserved_in_journal():
    """novelty_signatures field stays — it's informational journal
    output even though it no longer drives the score."""
    from dataclasses import asdict
    m = _mk("h2", records=1_330_792, novel=35)
    d = asdict(m)
    assert d["novelty_signatures"] == 35
