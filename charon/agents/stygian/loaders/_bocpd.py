"""Bayesian Online Change-Point Detection (Adams-MacKay 2007).

Per Erebos v3 Phase 1A ITER-32 + DR batch 2 convergence
(`aporia/docs/erebos_v3_dr_synthesis_batch2_g06_g12.md`). Used by
G10 boundary loader to replace the max/mean smoothness-ratio
statistic with a posterior-probability-based change-point detector.

The Adams-MacKay BOCPD computes p(r_t | y_{1:t}) — the posterior
probability that the current run length is r_t, given observations
so far. Change points are detected where the run-length posterior
RESETS (mass concentrates at r_t = 0).

This implementation uses a constant hazard function H(r) = 1/lambda
(geometric prior on run length) and a Normal-Inverse-Gamma conjugate
prior on the observation distribution. No external dependency.

Reference: Adams & MacKay (2007), "Bayesian Online Changepoint
Detection," arXiv:0710.3742. Subsequent improvements: Knoblauch &
Damoulas (2018) on hyperparameter learning; Saatci et al. (2010) on
non-conjugate priors. v0 implementation uses the canonical conjugate
form for tractability.

Doctrine alignment (Erebos Doctrine v1.0):
- Layer 1 statistical method. Endorsed.
- Output is a posterior distribution (changepoint probability per
  timestep), not a scalar — naturally crosses the seam as a curve.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BOCPDResult:
    """Result of a BOCPD scan over an observation sequence."""
    n_observations: int
    changepoint_probabilities: list[float]  # P(changepoint at t) per t
    most_likely_changepoint_t: Optional[int]
    most_likely_changepoint_value: Optional[float]  # parameter value at change
    max_posterior: float
    hazard_rate: float
    notes: str


def _student_t_pdf(
    x: float, df: float, loc: float, scale: float
) -> float:
    """Student-t PDF, used for the conjugate-prior predictive."""
    if scale <= 0 or df <= 0:
        return 0.0
    z = (x - loc) / scale
    # log-PDF for numerical stability
    log_coeff = (
        math.lgamma((df + 1) / 2.0)
        - math.lgamma(df / 2.0)
        - 0.5 * math.log(df * math.pi)
        - math.log(scale)
    )
    log_kernel = -((df + 1) / 2.0) * math.log(1.0 + (z * z) / df)
    return math.exp(log_coeff + log_kernel)


def detect_changepoints(
    observations: list[float],
    *,
    hazard_rate: float = 0.05,
    prior_mean: Optional[float] = None,
    prior_kappa: float = 1.0,
    prior_alpha: float = 1.0,
    prior_beta: Optional[float] = None,
) -> BOCPDResult:
    """Run Adams-MacKay BOCPD on a 1D observation sequence.

    Parameters
    ----------
    observations : list[float]
        Sequence to scan.
    hazard_rate : float
        Constant hazard 1/lambda; expected run length between changes
        is 1/hazard_rate. Default 0.05 = expected 20 steps between
        changes (reasonable for boundary-detection on threshold sweeps).
    prior_mean, prior_kappa, prior_alpha, prior_beta : Normal-Inverse-
        Gamma hyperparameters. Defaults derived from data if None.

    Returns
    -------
    BOCPDResult with per-timestep changepoint posterior and the
    most-likely changepoint location.
    """
    n = len(observations)
    if n < 2:
        return BOCPDResult(
            n_observations=n,
            changepoint_probabilities=[0.0] * n,
            most_likely_changepoint_t=None,
            most_likely_changepoint_value=None,
            max_posterior=0.0,
            hazard_rate=hazard_rate,
            notes="insufficient observations (need >= 2)",
        )

    # Data-driven default priors
    if prior_mean is None:
        prior_mean = sum(observations) / n
    if prior_beta is None:
        # variance prior centered at observed variance
        mean = prior_mean
        var = sum((x - mean) ** 2 for x in observations) / max(n - 1, 1)
        prior_beta = max(var * 0.5, 1e-6)

    # Run-length posterior r_t can range 0..t. Maintained as a list.
    # P(r_t = r | y_{1:t}) where r is index.
    run_length_posterior: list[float] = [1.0]  # at t=0, r=0 with prob 1

    # Sufficient statistics for the conjugate posterior at each run
    # length. Each entry: (n_obs, mean_estimate, sum_sq_dev, kappa)
    stats: list[tuple[int, float, float, float]] = [
        (0, prior_mean, 0.0, prior_kappa),
    ]

    changepoint_probabilities: list[float] = [0.0]

    for t in range(n):
        y = observations[t]

        # Predictive probability for each run length, per Murphy 2007
        # "Conjugate Bayesian analysis of the Gaussian distribution"
        # eq. 100. NIG posterior (mu_n, kappa_n, alpha_n, beta_n) gives
        # predictive y ~ t_{2*alpha_n}(mu_n, scale_sq) with
        # scale_sq = beta_n * (kappa_n + 1) / (kappa_n * alpha_n).
        # The predictive's LOCATION is the posterior mean mu_n, not
        # the running mean_r. Bug fix from initial implementation
        # where loc was set to mean_r and scale was wrongly computed.
        pred_probs: list[float] = []
        for (n_r, mean_r, ssd_r, kappa_r) in stats:
            kappa_n = kappa_r + n_r
            alpha_n = prior_alpha + n_r / 2.0
            if n_r > 0:
                mu_n = (kappa_r * prior_mean + n_r * mean_r) / kappa_n
                beta_n = prior_beta + ssd_r / 2.0 + (
                    (kappa_r * n_r * (mean_r - prior_mean) ** 2)
                    / (2.0 * kappa_n)
                )
            else:
                mu_n = prior_mean
                beta_n = prior_beta
            df = 2 * alpha_n
            loc = mu_n
            scale_sq = beta_n * (kappa_n + 1) / (kappa_n * alpha_n)
            scale = math.sqrt(max(scale_sq, 1e-12))
            pred_probs.append(_student_t_pdf(y, df, loc, scale))

        # Growth probabilities (run length continues)
        growth_probs = [
            run_length_posterior[i] * pred_probs[i] * (1.0 - hazard_rate)
            for i in range(len(run_length_posterior))
        ]
        # Changepoint probability (run length resets to 0)
        cp_prob = sum(
            run_length_posterior[i] * pred_probs[i] * hazard_rate
            for i in range(len(run_length_posterior))
        )

        new_posterior = [cp_prob] + growth_probs
        total = sum(new_posterior)
        if total > 0:
            new_posterior = [p / total for p in new_posterior]
        run_length_posterior = new_posterior

        # Changepoint signal under Adams-MacKay: the MODE of the
        # run-length posterior shifts. We track the run-length MODE
        # per timestep; a changepoint corresponds to the mode
        # RESETTING (dropping sharply to a small value). P(r_t = 0)
        # itself = hazard rate after normalization (proven algebraic
        # identity); the diagnostic is the mode's drop, not its
        # absolute value.
        # We store the EXPECTED RUN LENGTH as the "non-stationarity
        # signal": low values = recent changepoint suspected.
        # changepoint_probability_at_t = 1 / (1 + E[run_length])
        # so that fresh changes give probability near 1.
        expected_run_length = sum(
            r * p for r, p in enumerate(new_posterior)
        )
        cp_signal = 1.0 / (1.0 + expected_run_length)
        changepoint_probabilities.append(cp_signal)

        # Update sufficient statistics
        new_stats: list[tuple[int, float, float, float]] = [
            (0, prior_mean, 0.0, prior_kappa),
        ]
        for (n_r, mean_r, ssd_r, kappa_r) in stats:
            new_n = n_r + 1
            new_mean = (n_r * mean_r + y) / new_n
            new_ssd = ssd_r + (y - mean_r) * (y - new_mean)
            new_stats.append((new_n, new_mean, new_ssd, kappa_r))
        stats = new_stats

    # Trim leading zero (initial state)
    cp_per_t = changepoint_probabilities[1:]
    if not cp_per_t:
        return BOCPDResult(
            n_observations=n,
            changepoint_probabilities=[0.0] * n,
            most_likely_changepoint_t=None,
            most_likely_changepoint_value=None,
            max_posterior=0.0,
            hazard_rate=hazard_rate,
            notes="no posterior values computed",
        )

    max_post = max(cp_per_t)
    # Exclude the t=0 trivial point (which always shows P=1 as the
    # initial "everything just started" event); locate the strongest
    # interior change.
    interior = cp_per_t[1:] if len(cp_per_t) > 1 else []
    if interior:
        most_likely_t = interior.index(max(interior)) + 1
        most_likely_val = observations[most_likely_t]
    else:
        most_likely_t = None
        most_likely_val = None

    return BOCPDResult(
        n_observations=n,
        changepoint_probabilities=cp_per_t,
        most_likely_changepoint_t=most_likely_t,
        most_likely_changepoint_value=most_likely_val,
        max_posterior=max_post,
        hazard_rate=hazard_rate,
        notes=(
            f"BOCPD over n={n} observations, hazard={hazard_rate}, "
            f"max interior posterior = {max(interior):.4f} at t="
            f"{most_likely_t}"
            if interior else
            f"BOCPD over n={n}, no interior changepoint detected"
        ),
    )
