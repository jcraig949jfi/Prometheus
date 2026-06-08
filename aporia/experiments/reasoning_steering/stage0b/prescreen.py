"""Signal pre-screen (Stage 0b) — a FAST curl measure, gating the expensive H-R1 run.

KEY CORRECTION (validated 2026-06-08 on real data): pairwise anti-correlation does NOT
predict non-transitivity. The g2c criteria had min pairwise Spearman -0.80 and 34
anti-correlated pairs yet H-R1 was NULL -- because two evaluators trading off is still
WEIGHTABLE (a scalar combination orders the states). Curl requires CYCLIC, non-weightable
inconsistency (a>b>c>a) among >=3 evaluators, which pairwise stats cannot see. So the
only valid cheap screen is the curl itself at low sample count.

This screen computes the observed non_gradient_mass + a SMALL column-shuffle null
(~10x cheaper than the full run) and PASSes only if the observed curl beats it at a
lenient alpha. The pairwise-correlation summary is still reported as a DIAGNOSTIC --
explicitly NOT the gate (it gives false positives; see g2c).
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np
from scipy.stats import spearmanr

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0b.flow import relational_flow
from aporia.experiments.reasoning_steering.stage0b.relational_nulls import run_relational_null

__all__ = ["ScreenResult", "signal_screen", "MIN_VARYING_EVALUATORS", "SCREEN_ALPHA"]

MIN_VARYING_EVALUATORS = 3
SCREEN_ALPHA = 0.2          # lenient: a screen, not the final test
TRADEOFF_CORR = -0.1


@dataclass(frozen=True)
class ScreenResult:
    n_states: int
    n_varying: int
    observed_non_gradient_mass: float
    quick_null_mean: float
    quick_pvalue: float
    # pairwise-correlation DIAGNOSTIC (reported, NOT the gate -- does not predict curl):
    mean_corr: float
    min_corr: float
    n_negative_pairs: int
    predicted_signal: str       # "worth_running" | "unlikely"
    verdict: str                # "PASS" | "FAIL_NO_CURL" | "FAIL_TOO_FEW"


def _corr_diagnostic(vectors, varying):
    corrs = []
    for a, b in combinations(varying, 2):
        idx = [i for i, v in enumerate(vectors) if a in v and b in v]
        rho = spearmanr([vectors[i][a] for i in idx], [vectors[i][b] for i in idx]).statistic
        if rho is not None and np.isfinite(rho):
            corrs.append(float(rho))
    c = np.array(corrs) if corrs else np.array([0.0])
    return float(np.mean(c)), float(np.min(c)), int(np.sum(c < TRADEOFF_CORR))


def signal_screen(records, quick_null: int = 60, seed: int = 0) -> ScreenResult:
    """Fast curl screen: PASS iff observed non_gradient_mass beats a small column-shuffle
    null at SCREEN_ALPHA. ~10x cheaper than the full H-R1 run; same (curl) quantity."""
    vectors = [r["margins"] for r in records]
    n_states = len(vectors)
    if n_states < 3:
        raise ValueError("need >= 3 states")
    names = sorted(set().union(*[set(v) for v in vectors]))
    varying = [k for k in names if len({round(v[k], 9) for v in vectors if k in v}) >= 2]
    n_varying = len(varying)

    mean_c, min_c, n_neg = _corr_diagnostic(vectors, varying) if n_varying >= 2 else (0.0, 0.0, 0)
    base = dict(n_states=n_states, n_varying=n_varying, mean_corr=mean_c,
                min_corr=min_c, n_negative_pairs=n_neg)

    if n_varying < MIN_VARYING_EVALUATORS:
        return ScreenResult(**base, observed_non_gradient_mass=0.0, quick_null_mean=0.0,
                            quick_pvalue=1.0, predicted_signal="unlikely", verdict="FAIL_TOO_FEW")

    G, flow = relational_flow(vectors)
    observed = hodge_decompose(G, flow).non_gradient_mass
    res = run_relational_null(records, "falsifier_column_shuffle", n_samples=quick_null, seed=seed)
    beats = observed > res.null_mean and res.pvalue < SCREEN_ALPHA
    return ScreenResult(
        **base, observed_non_gradient_mass=observed, quick_null_mean=res.null_mean,
        quick_pvalue=res.pvalue,
        predicted_signal="worth_running" if beats else "unlikely",
        verdict="PASS" if beats else "FAIL_NO_CURL",
    )
