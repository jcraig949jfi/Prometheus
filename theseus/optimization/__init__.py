"""Theseus optimization — Bayesian-flavored hyperparameter tuning for generators.

v0.1: random-search + best-tracking with adaptive narrowing.
Architecture is Optuna-compatible; Optuna can swap in cleanly in Tier 2
by replacing TunerLite.run_study() with optuna.create_study().
"""
from theseus.optimization.bayes_tuner import TunerLite, TunerResult
from theseus.optimization.config_overrides import (
    load_overrides,
    save_overrides,
    OVERRIDES_PATH,
)
from theseus.optimization.spaces import GENERATOR_SPACES

__all__ = [
    "TunerLite",
    "TunerResult",
    "load_overrides",
    "save_overrides",
    "OVERRIDES_PATH",
    "GENERATOR_SPACES",
]
