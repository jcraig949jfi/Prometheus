"""Hyperparameter spaces per generator.

Each space is a dict of param_name → list-of-candidate-values.
Lists must be enumerable (no continuous spaces in v0.1 random-search;
Optuna swap-in will support continuous suggest_float / suggest_int).
"""
from __future__ import annotations

from typing import Any, Dict, List


GENERATOR_SPACES: Dict[str, Dict[str, List[Any]]] = {
    "a4": {
        # Sample size: smaller = faster but noisier R²
        "sample_size": [15, 25, 40, 60, 100],
        # Strong R² threshold: lower → more SHADOW emissions but more false positives
        "STRONG_R2": [0.5, 0.6, 0.7, 0.8, 0.9],
        # Weak R² threshold: lower → more INCONCLUSIVE bin
        "WEAK_R2": [0.1, 0.2, 0.3, 0.4],
    },
    "a5": {
        "sample_size": [15, 25, 40, 60, 100],
        "KS_GOOD": [0.15, 0.2, 0.25, 0.3, 0.4],
        "KS_WEAK": [0.4, 0.5, 0.6, 0.7],
    },
    "a2": {
        "sample_size": [20, 30, 50, 80, 120],
        "SIGNIFICANT_R": [0.05, 0.1, 0.15, 0.2, 0.3],
    },
    "h1": {
        "hunt_budget": [10, 20, 30, 50, 80],
    },
    "d3": {
        "n_branches": [3, 5, 7, 10],
    },
}
