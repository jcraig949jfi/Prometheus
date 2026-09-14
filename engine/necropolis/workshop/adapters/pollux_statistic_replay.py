"""Replay of the Pollux verdict statistic on caller-supplied values (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: charon/agents/pollux/daemon.py -- _spearman,
_mean_spacing_normalize, _classify, CORR_SIGNIFICANT, CORR_FLIPPED_DELTA, and
the run_tick construction ``sorted(a)[:n], sorted(b)[:n]``.  Those functions
are imported and called UNCHANGED.  The construction is re-stated here line
for line from run_tick because run_tick itself loads subsets, writes an
artifact and appends a kill_ledger row, none of which a coroner may do.

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::pollux_pipeline.*
and ::adapters_pollux_replay.*

What this adapter does NOT do: it does not repair the statistic.  The
``historical`` block is what the daemon computed; the ``diagnostics`` block is
the instrument-null reading of the same construction.  If the two disagree
about whether a verdict means anything, that disagreement IS the finding.

Reads: two lists of floats.  Writes: nothing.  Never loads a Mahler subset;
the caller passes values (a coroner plan names where they come from).
"""
from __future__ import annotations

import importlib
from typing import Optional, Sequence

from . import instrument_null as _inull


def _daemon():
    return importlib.import_module("charon.agents.pollux.daemon")


def historical_statistic(a_vals: Sequence[float], b_vals: Sequence[float]) -> dict:
    """Exactly the numbers run_tick would have produced for these two value lists."""
    D = _daemon()
    a_vals, b_vals = list(a_vals), list(b_vals)
    n = min(len(a_vals), len(b_vals))
    a_paired = sorted(a_vals)[:n]
    b_paired = sorted(b_vals)[:n]
    corr_raw = D._spearman(a_paired, b_paired)
    a_norm = D._mean_spacing_normalize(a_paired)
    b_norm = D._mean_spacing_normalize(b_paired)
    n_norm = min(len(a_norm), len(b_norm))
    corr_norm = D._spearman(a_norm[:n_norm], b_norm[:n_norm]) if n_norm >= 10 else None
    kp = D._classify(corr_raw, corr_norm)
    verdict = ("PROMOTED" if kp == "pollux_correlation_survives_normalization"
               else "REJECTED" if kp in ("pollux_sign_flips_under_normalization",
                                         "pollux_no_correlation_observed")
               else "UNVERIFIED")
    return {
        "n_paired": n,
        "corr_raw": round(corr_raw, 4) if corr_raw is not None else None,
        "corr_norm": round(corr_norm, 4) if corr_norm is not None else None,
        "kill_pattern": kp,
        "verdict": verdict,
        "thresholds": {"CORR_SIGNIFICANT": D.CORR_SIGNIFICANT, "CORR_FLIPPED_DELTA": D.CORR_FLIPPED_DELTA},
        "construction": "sorted(a)[:n], sorted(b)[:n]; spearman; mean-spacing-normalise each; spearman of gap series",
    }


def _corr_norm_stat(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    D = _daemon()
    n = min(len(a), len(b))
    an = D._mean_spacing_normalize(sorted(a)[:n])
    bn = D._mean_spacing_normalize(sorted(b)[:n])
    m = min(len(an), len(bn))
    return D._spearman(an[:m], bn[:m]) if m >= 10 else None


def _corr_raw_stat(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    D = _daemon()
    n = min(len(a), len(b))
    return D._spearman(sorted(a)[:n], sorted(b)[:n])


def replay(a_vals: Sequence[float], b_vals: Sequence[float], *, n_draws: int = 200, seed: int = 0) -> dict:
    """Historical numbers beside the instrument-null reading of the same construction."""
    hist = historical_statistic(a_vals, b_vals)
    diag_raw = _inull.instrument_null(_corr_raw_stat, a_vals, b_vals, n_draws=n_draws, seed=seed)
    diag_norm = _inull.instrument_null(_corr_norm_stat, a_vals, b_vals, n_draws=n_draws, seed=seed)
    return {
        "historical": hist,
        "diagnostics": {"corr_raw": diag_raw, "corr_norm": diag_norm},
        "reading": (
            "corr_raw is computed on two sorted series and is 1.0 by construction whenever it is defined; "
            "corr_norm is read against shuffled and independent draws above. A PROMOTED verdict is "
            "evidence about the pair only if diagnostics.corr_norm.verdict is RESPONSIVE AND "
            "independent.frac_ge_observed is small; the daemon never checked either."),
    }
