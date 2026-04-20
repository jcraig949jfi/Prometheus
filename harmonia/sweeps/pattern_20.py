"""
Pattern 20 — Pooled-vs-Stratified Artifact Detection.

Diagnostic bullets (from pattern_library.md Pattern 20):
- pooled statistic without stratification or preprocessing variant
- pooled number is clean (monotone, single-signed, high R2, low p)
- no >=1 stratification AND >=1 preprocessing applied
- no sample-size replication at 2x scale

Anchor cases: F010 (pooled 0.40 -> bigsample 0.11, decon stable at 0.27),
              F011 (pooled 40% -> unfolded 38%), F013 (pooled slope halved),
              F015 (pooled -0.60 vs per-k range [-0.13, -0.49]).

Automated sweep input: a SIGNATURE dict carrying `pooled_stat` and optionally
`stratified_stats` (dict of stratum -> stat). If the caller has not run any
stratification, the sweep WARNs with a re-audit suggestion; if stratified
stats are present, computes divergence ratio and sign-agreement.

Rules:
  pooled_vs_stratified_ratio > 1.2          -> WARN
  sign discordant                           -> BLOCK
  stratum sample sizes < 100 per stratum    -> FLAG_INCONCLUSIVE (WARN)
  no stratified data provided               -> WARN (re-audit requested)
  ratio <= 1.2 and sign uniform             -> CLEAR
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Mapping, Sequence


@dataclass
class StratifiedStat:
    stratum: str
    value: float
    n: int


@dataclass
class Pattern20Check:
    """Input for the pooled-vs-stratified sweep.

    Fields:
      pooled_value: the headline pooled statistic (slope, rho, variance, ...)
      pooled_n: sample size behind the pooled value
      stratified: per-stratum values; keyed by stratum label
      min_stratum_n: smaller strata trigger FLAG_INCONCLUSIVE
      ratio_warn_threshold: pooled/max_stratum or pooled/mean_stratum ratio
    """
    pooled_value: Optional[float]
    pooled_n: Optional[int] = None
    stratified: Sequence[StratifiedStat] = field(default_factory=list)
    min_stratum_n: int = 100
    ratio_warn_threshold: float = 1.2
    label: str = "pooled_stat"


@dataclass
class Pattern20Result:
    verdict: str
    rationale: str
    ratio: Optional[float] = None
    sign_agreement: Optional[bool] = None
    small_n_strata: Sequence[str] = field(default_factory=list)


def sweep(check: Pattern20Check) -> Pattern20Result:
    if check.pooled_value is None:
        return Pattern20Result(
            verdict="CLEAR",
            rationale="no pooled stat supplied; Pattern 20 not applicable",
        )

    if not check.stratified:
        return Pattern20Result(
            verdict="WARN",
            rationale=(
                f"pooled {check.label}={check.pooled_value:.4g} has no "
                "stratified companion; re-audit with >=1 stratification "
                "(conductor_decile, rank, num_bad_primes, ...) before any "
                "promotion"
            ),
        )

    # Small-n flag
    small = [s.stratum for s in check.stratified if s.n < check.min_stratum_n]

    # Sign agreement
    pooled_sign = _sign(check.pooled_value)
    stratum_signs = [_sign(s.value) for s in check.stratified]
    # Exclude strata with ~zero stat from sign check
    non_zero_signs = [s for s in stratum_signs if s != 0]
    sign_uniform = (len(set(non_zero_signs)) <= 1) if non_zero_signs else True
    sign_matches_pooled = all(
        s == 0 or s == pooled_sign for s in stratum_signs
    ) if pooled_sign != 0 else True

    # Ratio: pooled value vs mean absolute stratum value
    mean_abs_stratum = _mean([abs(s.value) for s in check.stratified])
    if mean_abs_stratum == 0:
        ratio = float("inf") if check.pooled_value != 0 else 1.0
    else:
        ratio = abs(check.pooled_value) / mean_abs_stratum

    # Decision tree
    if not sign_uniform or not sign_matches_pooled:
        return Pattern20Result(
            verdict="BLOCK",
            rationale=(
                f"pooled {check.label}={check.pooled_value:.4g} has "
                f"sign-discordance with per-stratum values "
                f"({[f'{s.stratum}:{s.value:.3g}' for s in check.stratified]}); "
                "pooled number is a projection artifact"
            ),
            ratio=ratio,
            sign_agreement=False,
            small_n_strata=small,
        )

    if ratio > check.ratio_warn_threshold:
        verdict = "BLOCK" if ratio > 2.0 else "WARN"
        return Pattern20Result(
            verdict=verdict,
            rationale=(
                f"pooled/mean_stratum ratio {ratio:.3f} exceeds "
                f"threshold {check.ratio_warn_threshold} (pooled="
                f"{check.pooled_value:.4g}, mean|stratum|={mean_abs_stratum:.4g}); "
                "pooled magnitude is a mixture-of-strata artifact"
            ),
            ratio=ratio,
            sign_agreement=True,
            small_n_strata=small,
        )

    if small:
        return Pattern20Result(
            verdict="WARN",
            rationale=(
                f"pooled {check.label} clean vs strata but strata {small} "
                f"have n<{check.min_stratum_n}; FLAG_INCONCLUSIVE"
            ),
            ratio=ratio,
            sign_agreement=True,
            small_n_strata=small,
        )

    return Pattern20Result(
        verdict="CLEAR",
        rationale=(
            f"pooled {check.label}={check.pooled_value:.4g} consistent "
            f"with per-stratum panel (ratio={ratio:.3f}, sign uniform)"
        ),
        ratio=ratio,
        sign_agreement=True,
    )


def _sign(v: float) -> int:
    if v > 1e-12:
        return 1
    if v < -1e-12:
        return -1
    return 0


def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0
