"""Tests for epsilon-greedy bandit."""
from __future__ import annotations

from theseus.bandit.epsilon_greedy import EpsilonGreedyBandit
from theseus.scoring.metrics_schema import GeneratorMetrics


def test_select_returns_n_when_more_available():
    b = EpsilonGreedyBandit(epsilon=0.0, seed=0)
    chosen = b.select(["a1", "b5", "c1", "d1", "e1", "f1"], history={}, n=3)
    assert len(chosen) == 3
    assert all(c in {"a1", "b5", "c1", "d1", "e1", "f1"} for c in chosen)


def test_select_returns_all_when_fewer_available():
    b = EpsilonGreedyBandit(epsilon=0.0, seed=0)
    chosen = b.select(["a1", "b5"], history={}, n=5)
    assert set(chosen) == {"a1", "b5"}


def test_update_records_yield():
    b = EpsilonGreedyBandit(epsilon=0.0, seed=0)
    m = GeneratorMetrics(
        generator_id="a1",
        records_emitted=10,
        info_density_mean=0.7,
        diversity_mean=0.5,
        learner_delta_steps=2,
    )
    b.update({"a1": m})
    assert "a1" in b._history
    assert len(b._history["a1"]) == 1


def test_high_yield_generator_gets_picked_in_exploitation():
    b = EpsilonGreedyBandit(epsilon=0.0, seed=0)
    # Seed history: a1 high yield, b5 low yield
    high = GeneratorMetrics(
        generator_id="a1", records_emitted=10,
        info_density_mean=0.9, diversity_mean=0.9, learner_delta_steps=1,
    )
    low = GeneratorMetrics(
        generator_id="b5", records_emitted=10,
        info_density_mean=0.1, diversity_mean=0.1, learner_delta_steps=10,
    )
    b.update({"a1": high, "b5": low})
    chosen = b.select(["a1", "b5"], history={}, n=1)
    # epsilon=0, so pure exploit; a1 has higher yield_score
    assert chosen == ["a1"]
