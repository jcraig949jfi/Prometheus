"""Tests for YieldProportionalBandit (GFlowNet-spirit)."""
from __future__ import annotations

import pytest

from theseus.bandit.yield_proportional import YieldProportionalBandit
from theseus.scoring.metrics_schema import GeneratorMetrics


def _make_m(gid: str, info: float, div: float, steps: int = 1) -> GeneratorMetrics:
    return GeneratorMetrics(
        generator_id=gid,
        records_emitted=100,
        info_density_mean=info,
        diversity_mean=div,
        learner_delta_steps=steps,
    )


def test_select_returns_n_when_more_available():
    b = YieldProportionalBandit(seed=0)
    chosen = b.select(["a", "b", "c", "d", "e", "f"], history={}, n=3)
    assert len(chosen) == 3
    assert len(set(chosen)) == 3  # no duplicates


def test_select_returns_all_when_fewer_available():
    b = YieldProportionalBandit(seed=0)
    chosen = b.select(["a", "b"], history={}, n=5)
    assert set(chosen) == {"a", "b"}


def test_high_yield_picked_more_often():
    """Over many selections, the high-yield generator should be picked
    more often than the low-yield one."""
    b = YieldProportionalBandit(seed=0, temperature=0.002, ucb_c=0.0)
    # Pre-load history: a is high-yield, b is low
    b.update({
        "a": _make_m("a", info=0.9, div=0.9, steps=1),
        "b": _make_m("b", info=0.1, div=0.1, steps=10),
    })

    a_count = 0
    b_count = 0
    for _ in range(200):
        # n=1: pure proportional sampling
        b2 = YieldProportionalBandit(seed=None, temperature=0.002, ucb_c=0.0)
        b2._history = {k: list(v) for k, v in b._history.items()}
        b2._rng.seed(_ + 1)  # different seed each call
        choice = b2.select(["a", "b"], history={}, n=1)
        if choice == ["a"]:
            a_count += 1
        else:
            b_count += 1
    assert a_count > b_count * 5  # at temperature=0.002, a should dominate


def test_never_fired_get_exploration_bonus():
    """Generators with 0 history get some non-zero probability."""
    b = YieldProportionalBandit(seed=0, temperature=0.005, ucb_c=1.0)
    # a has high yield, b/c never fired
    b.update({"a": _make_m("a", info=0.9, div=0.9, steps=1)})
    picks = set()
    for _ in range(50):
        b._rng.seed(_)
        chosen = b.select(["a", "b", "c"], history={}, n=2)
        picks.update(chosen)
    assert "b" in picks or "c" in picks  # at least one never-fired got picked


def test_update_records_yield():
    b = YieldProportionalBandit(seed=0)
    m = _make_m("a", info=0.7, div=0.5, steps=2)
    b.update({"a": m})
    assert "a" in b._history
    assert len(b._history["a"]) == 1


def test_temperature_concentration():
    """Lower temperature → more concentration on top-yield."""
    history = {
        "a": _make_m("a", info=0.9, div=0.9, steps=1),
        "b": _make_m("b", info=0.5, div=0.5, steps=1),
        "c": _make_m("c", info=0.1, div=0.1, steps=1),
    }

    # High temperature: closer to uniform
    high_T = YieldProportionalBandit(seed=0, temperature=1.0, ucb_c=0.0)
    high_T.update(history)
    high_T_picks = []
    for i in range(100):
        high_T._rng.seed(i)
        high_T_picks.append(high_T.select(["a", "b", "c"], history={}, n=1)[0])
    high_T_a_rate = high_T_picks.count("a") / len(high_T_picks)

    # Low temperature: concentrated
    low_T = YieldProportionalBandit(seed=0, temperature=0.001, ucb_c=0.0)
    low_T.update(history)
    low_T_picks = []
    for i in range(100):
        low_T._rng.seed(i)
        low_T_picks.append(low_T.select(["a", "b", "c"], history={}, n=1)[0])
    low_T_a_rate = low_T_picks.count("a") / len(low_T_picks)

    assert low_T_a_rate > high_T_a_rate  # lower T = more concentrated on a


def test_select_no_duplicates():
    b = YieldProportionalBandit(seed=0, temperature=0.001, ucb_c=0.0)
    b.update({
        "a": _make_m("a", info=0.9, div=0.9, steps=1),
        "b": _make_m("b", info=0.1, div=0.1, steps=10),
        "c": _make_m("c", info=0.1, div=0.1, steps=10),
    })
    for _ in range(50):
        chosen = b.select(["a", "b", "c"], history={}, n=2)
        assert len(set(chosen)) == 2
