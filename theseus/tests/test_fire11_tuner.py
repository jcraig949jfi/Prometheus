"""Tests for the optimization module: spaces, overrides, TunerLite."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.optimization.spaces import GENERATOR_SPACES
from theseus.optimization.config_overrides import (
    load_overrides,
    save_overrides,
    update_overrides_for,
    get_overrides_for,
)
from theseus.optimization.bayes_tuner import TunerLite, _score_generator_with_params


def test_spaces_defined_for_tunable_generators():
    """Sanity: every space has enumerable values."""
    for gid, space in GENERATOR_SPACES.items():
        assert isinstance(space, dict)
        for param, values in space.items():
            assert isinstance(values, list)
            assert len(values) >= 2


def test_overrides_roundtrip(tmp_path, monkeypatch):
    """Read/write cycle for the overrides JSON."""
    from theseus.optimization import config_overrides as co
    overrides_path = tmp_path / "tuned.json"
    monkeypatch.setattr(co, "OVERRIDES_PATH", overrides_path)

    assert co.load_overrides() == {}
    co.save_overrides({"a4": {"sample_size": 50}})
    assert co.load_overrides() == {"a4": {"sample_size": 50}}
    assert co.get_overrides_for("a4") == {"sample_size": 50}
    assert co.get_overrides_for("missing") == {}


def test_overrides_update_merges(tmp_path, monkeypatch):
    from theseus.optimization import config_overrides as co
    overrides_path = tmp_path / "tuned.json"
    monkeypatch.setattr(co, "OVERRIDES_PATH", overrides_path)

    co.save_overrides({"a4": {"sample_size": 50}})
    co.update_overrides_for("a5", {"KS_GOOD": 0.25})
    loaded = co.load_overrides()
    assert loaded["a4"] == {"sample_size": 50}
    assert loaded["a5"] == {"KS_GOOD": 0.25}


def test_score_generator_with_params_a4_small():
    """Sanity: scoring A4 with a small sample_size completes."""
    score, n_records = _score_generator_with_params(
        "a4",
        params={"sample_size": 15, "STRONG_R2": 0.7, "WEAK_R2": 0.3},
        n_records=10,
        seed=0,
    )
    assert n_records > 0
    assert 0.0 <= score <= 1.0


def test_tuner_random_completes_small_study():
    tuner = TunerLite(seed=42)
    result = tuner.run_study(
        generator_id="a4",
        n_trials=3,
        n_records_per_trial=10,
        mode="random",
    )
    assert result.n_trials == 3
    assert len(result.trials) == 3
    assert result.best_score >= 0.0
    assert "sample_size" in result.best_params


def test_tuner_invalid_generator_raises():
    tuner = TunerLite(seed=0)
    with pytest.raises(KeyError):
        tuner.run_study(generator_id="zzz_nonexistent", n_trials=1)
