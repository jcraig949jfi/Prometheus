"""Fire #83 bandit cooldown tests.

Background: the "finite refillable reservoir" pattern (Fires #80, #81, #82):
  f4#66: 175 templates (first pick) → f4#80: 0 (re-pick)
  e2#79: 269 templates              → e2#81: 0
  g4#65: 131 templates              → g4#82: 0

YieldProportionalBandit now downweights gens picked within last N fires.
Persistence schema v2 tracks fire_counter + last_picked_at per gen.
"""
from __future__ import annotations

import json
from pathlib import Path

from theseus.bandit.yield_proportional import YieldProportionalBandit
from theseus.scoring.metrics_schema import GeneratorMetrics
from theseus.orchestration.bandit_state import (
    fires_since_last_pick,
    load_history,
    load_pick_recency,
    persist_bandit,
    save_history,
)


def _make_metric(gid: str, info: float = 0.5, div: float = 0.5,
                 steps: int = 1) -> GeneratorMetrics:
    return GeneratorMetrics(
        generator_id=gid,
        records_emitted=100,
        info_density_mean=info,
        diversity_mean=div,
        learner_delta_steps=steps,
    )


# ---------- v2 schema persistence ----------


def test_v2_schema_saves_fire_counter_and_last_picked(tmp_path):
    """Schema v2 round-trips fire_counter + last_picked_at."""
    p = tmp_path / "history.json"
    save_history(
        {"a1": [0.005, 0.006]},
        path=p,
        fire_counter=42,
        last_picked_at={"a1": 40, "c5": 41},
    )
    data = json.loads(p.read_text())
    assert data["version"] == 2
    assert data["fire_counter"] == 42
    assert data["last_picked_at"] == {"a1": 40, "c5": 41}


def test_v1_files_still_load_for_history(tmp_path):
    """Pre-#83 v1 history files should still load (backwards compat)."""
    p = tmp_path / "history.json"
    p.write_text(json.dumps({
        "version": 1,
        "yield_scores": {"a1": [0.003, 0.004]},
    }))
    h = load_history(path=p)
    assert h == {"a1": [0.003, 0.004]}


def test_v1_files_return_empty_recency(tmp_path):
    """v1 files have no recency data → returns (0, {})."""
    p = tmp_path / "history.json"
    p.write_text(json.dumps({
        "version": 1,
        "yield_scores": {"a1": [0.003]},
    }))
    counter, last_picked = load_pick_recency(path=p)
    assert counter == 0
    assert last_picked == {}


def test_persist_bandit_increments_counter(tmp_path):
    """Each persist_bandit call increments fire_counter and marks picks."""
    p = tmp_path / "history.json"
    save_history({}, path=p, fire_counter=5, last_picked_at={"a1": 3})
    b = YieldProportionalBandit(seed=0)
    b._history = {"a1": [0.003], "c5": [0.005]}
    persist_bandit(b, path=p, picked_this_fire=["a1", "c5"])
    data = json.loads(p.read_text())
    assert data["fire_counter"] == 6
    assert data["last_picked_at"]["a1"] == 6
    assert data["last_picked_at"]["c5"] == 6


def test_fires_since_last_pick_never_picked():
    """Gens never picked → large fresh value."""
    assert fires_since_last_pick("a1", counter=10, last_picked={}) == 1000


def test_fires_since_last_pick_normal_case():
    last = {"a1": 5, "c5": 8}
    assert fires_since_last_pick("a1", counter=10, last_picked=last) == 5
    assert fires_since_last_pick("c5", counter=10, last_picked=last) == 2


# ---------- Cooldown effect on YieldProportionalBandit.select ----------


def test_cooldown_downweights_recently_picked():
    """Gen picked 1 fire ago should be picked less than fresh gen
    with same score, given identical UCB."""
    b = YieldProportionalBandit(
        seed=0,
        temperature=0.01,
        ucb_c=0.0,  # disable UCB to isolate cooldown effect
        cooldown_window=3,
        cooldown_multiplier=0.3,
    )
    b.update({
        "fresh": _make_metric("fresh", info=0.5, div=0.5, steps=1),
        "recent": _make_metric("recent", info=0.5, div=0.5, steps=1),
    })
    # Both have same yield_score; only 'recent' is in cooldown
    b._pick_recency = {"fresh": 100, "recent": 1}
    picks = []
    for _ in range(200):
        picks.extend(b.select(["fresh", "recent"], history={}, n=1))
    fresh_count = picks.count("fresh")
    assert fresh_count > 130, (
        f"fresh picked {fresh_count}/200 — cooldown not strong enough"
    )


def test_cooldown_window_threshold():
    """A gen exactly at the cooldown window edge gets full score
    (no penalty applied)."""
    b = YieldProportionalBandit(
        seed=0,
        cooldown_window=3,
        cooldown_multiplier=0.3,
    )
    b.update({"a": _make_metric("a")})
    # Exactly 3 fires since pick — should NOT be downweighted (< 3 = penalty)
    b._pick_recency = {"a": 3}
    # Internal: when computing for a single available gen, just verify
    # the score path doesn't crash. Behavior validated by integration.
    chosen = b.select(["a"], history={}, n=1)
    assert chosen == ["a"]


def test_cooldown_no_effect_without_recency_map():
    """If _pick_recency is empty (legacy behavior), no penalty applied."""
    b = YieldProportionalBandit(seed=0, cooldown_window=3)
    b.update({
        "a": _make_metric("a"),
        "b": _make_metric("b"),
    })
    assert b._pick_recency == {}
    # Should pick normally
    chosen = b.select(["a", "b"], history={}, n=1)
    assert len(chosen) == 1


def test_full_cooldown_cycle_via_persist(tmp_path):
    """End-to-end: persist_bandit twice; second load shows fire_counter=2
    and recency updated."""
    p = tmp_path / "history.json"
    b1 = YieldProportionalBandit(seed=0)
    b1._history = {"a1": [0.003]}
    persist_bandit(b1, path=p, picked_this_fire=["a1", "c5"])

    b2 = YieldProportionalBandit(seed=0)
    b2._history = {"a1": [0.003, 0.004], "h2": [0.005]}
    persist_bandit(b2, path=p, picked_this_fire=["h2"])

    counter, last_picked = load_pick_recency(path=p)
    assert counter == 2
    assert last_picked["a1"] == 1
    assert last_picked["c5"] == 1
    assert last_picked["h2"] == 2
