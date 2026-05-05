"""ergon.learner.stability — perturbation stability check for high-magnitude buckets.

Per pivot/ergon_learner_proposal_v8.md §6.2:

High-magnitude buckets (4 and 5: [10⁹, 10¹²) and [10¹², ∞)) require
perturbation stability before earning full credit:
  - Input jitter test: ε=0.001 across 100 trials, ≥95% same magnitude bucket
  - Half-precision recompute test: same bucket at half precision

Genomes failing the stability check are binned in `out_of_band` cell
instead. F_MAGNITUDE_STABILITY_REJECT runs as a kill-test extension.

At MVP scope this is a stub — it documents the API and runs a no-op
check that always passes. Full implementation requires actual genome
evaluation infrastructure (the BindEvalKernelV2 pipeline that Techne
shipped). v0.5 wires the real check.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ergon.learner.descriptor import (
    OUT_OF_BAND_BUCKET,
    compute_magnitude_bucket,
)
from ergon.learner.genome import Genome


@dataclass
class StabilityCheckResult:
    """Result of running perturbation-stability on a high-magnitude genome.

    passes: True if genome survives both tests
    input_jitter_pass_rate: fraction of jittered trials landing in same bucket
    half_precision_pass: True if half-precision lands in same bucket
    new_magnitude_bucket: where the genome ends up (full bucket if pass;
                          out_of_band if fail)
    """
    passes: bool
    input_jitter_pass_rate: float
    half_precision_pass: bool
    new_magnitude_bucket: int
    metadata: Dict[str, Any] = field(default_factory=dict)


# Per v8 §6.2 thresholds
INPUT_JITTER_EPSILON = 0.001
INPUT_JITTER_N_TRIALS = 100
INPUT_JITTER_PASS_THRESHOLD = 0.95


def perturbation_stability_check(
    genome: Genome,
    nominal_magnitude: float,
    nominal_bucket: int,
    evaluator_fn: Optional[Any] = None,  # callable(perturbed_genome) -> magnitude
) -> StabilityCheckResult:
    """Run input-jitter + half-precision tests on a high-magnitude genome.

    Only applies to magnitude buckets 3 and 4 ([10⁹, 10¹²) and [10¹², ∞)) —
    bucket 4 high-end requires the strictest discipline.

    Buckets 0, 1, 2 are returned with passes=True trivially (low-magnitude
    outputs aren't subject to this discipline).

    At MVP without evaluator_fn: returns passes=True (stub). v0.5 wires
    BindEvalKernelV2 for the real evaluation under perturbation.
    """
    # Trivial pass for low-magnitude buckets
    if nominal_bucket < 3:
        return StabilityCheckResult(
            passes=True,
            input_jitter_pass_rate=1.0,
            half_precision_pass=True,
            new_magnitude_bucket=nominal_bucket,
            metadata={"trivial_pass_low_magnitude": True},
        )

    # MVP stub: no evaluator wired
    if evaluator_fn is None:
        return StabilityCheckResult(
            passes=True,
            input_jitter_pass_rate=1.0,
            half_precision_pass=True,
            new_magnitude_bucket=nominal_bucket,
            metadata={"mvp_stub_pass": True,
                      "warning": "evaluator_fn not provided; stability check is a stub"},
        )

    # v0.5+ implementation path
    n_jitter_pass = 0
    for trial_idx in range(INPUT_JITTER_N_TRIALS):
        try:
            perturbed_mag = evaluator_fn(genome, jitter_epsilon=INPUT_JITTER_EPSILON,
                                         jitter_seed=trial_idx)
            perturbed_bucket = compute_magnitude_bucket(perturbed_mag)
            if perturbed_bucket == nominal_bucket:
                n_jitter_pass += 1
        except Exception:
            # Treat exceptions as failure
            pass
    input_jitter_rate = n_jitter_pass / INPUT_JITTER_N_TRIALS

    try:
        half_precision_mag = evaluator_fn(genome, precision="half")
        half_precision_bucket = compute_magnitude_bucket(half_precision_mag)
        half_precision_passes = (half_precision_bucket == nominal_bucket)
    except Exception:
        half_precision_passes = False

    overall_pass = (
        input_jitter_rate >= INPUT_JITTER_PASS_THRESHOLD
        and half_precision_passes
    )
    new_bucket = nominal_bucket if overall_pass else OUT_OF_BAND_BUCKET

    return StabilityCheckResult(
        passes=overall_pass,
        input_jitter_pass_rate=input_jitter_rate,
        half_precision_pass=half_precision_passes,
        new_magnitude_bucket=new_bucket,
        metadata={
            "n_jitter_trials": INPUT_JITTER_N_TRIALS,
            "jitter_epsilon": INPUT_JITTER_EPSILON,
            "pass_threshold": INPUT_JITTER_PASS_THRESHOLD,
        },
    )
