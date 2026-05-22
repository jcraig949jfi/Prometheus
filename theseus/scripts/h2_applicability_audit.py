"""h2 applicability audit per advisory board (Fire #51).

Pre-registered falsifiable test:
  Construct synthetic (xs, ys) datasets at KNOWN r² levels via
  y = m*x + Gaussian noise, vary noise scale. Pass through h2's
  exact verdict-mapping (_polyfit_r2 + _r2_to_verdict). At each
  ground-truth r² level, tally what verdict h2 assigns.

Pre-registered threshold:
  If h2 REJECTS (=KILL) synthetic data with true r² ≥ 0.9 at >20%
  of trials, h2 is calibrated too narrow and its 99.99%-kill-rate
  on cross-catalog samples reflects calibration, not falsification.

Note on h2's actual structure: h2 takes A4-INCONCLUSIVE parents
with (knot_invariant, ec_invariant) payloads, then INDEPENDENTLY
samples knots and ECs from the catalogs and runs polyfit on the
resulting (knot.ki, ec.ei) pairs. Independent sampling means the
cross-catalog signal is structurally noise — the 99.99% kill rate
reflects this null distribution measurement, not substrate
falsification of specific claims.

This audit tests the orthogonal question: GIVEN a polynomial
relationship exists, does h2 correctly confirm it?
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

from theseus.config import THESEUS_ROOT
from theseus.emit.record_schema import Verdict
from theseus.generators.a4_symbolic_regression import (
    _polyfit_r2,
    STRONG_R2,
    WEAK_R2,
)


def _r2_to_verdict(r2: float) -> str:
    """Replicates h2's verdict mapping exactly."""
    if r2 >= STRONG_R2:
        return Verdict.SHADOW_CATALOG.value
    if r2 >= WEAK_R2:
        return Verdict.INCONCLUSIVE.value
    return Verdict.REJECTED.value


def _synthesize_dataset(
    n: int,
    true_r2: float,
    degree: int,
    seed: int,
) -> Tuple[List[float], List[float]]:
    """Build (xs, ys) where polynomial fit at given degree achieves
    approximately the target r².

    Construction: y = polynomial(x) + Gaussian noise with σ tuned so
    that the resulting r² matches target. Uses iterative noise-scale
    adjustment.
    """
    rng = random.Random(seed)
    xs = [float(rng.uniform(-10, 10)) for _ in range(n)]
    # Polynomial: linear or quadratic depending on degree
    if degree == 1:
        signal = [2.0 * x + 1.0 for x in xs]
    elif degree == 2:
        signal = [x * x + 2.0 * x + 1.0 for x in xs]
    else:
        signal = [x ** 3 - x for x in xs]

    # Noise scale calibration via the relationship:
    #   r² ≈ var(signal) / (var(signal) + var(noise))
    # So var(noise) ≈ var(signal) * (1 - r²) / r²
    mean_signal = sum(signal) / len(signal)
    var_signal = sum((s - mean_signal) ** 2 for s in signal) / len(signal)
    if true_r2 <= 0.001:
        noise_var = var_signal * 1000.0
    elif true_r2 >= 0.999:
        noise_var = 1e-9
    else:
        noise_var = var_signal * (1.0 - true_r2) / true_r2
    noise_sigma = noise_var ** 0.5

    ys = [s + rng.gauss(0.0, noise_sigma) for s in signal]
    return xs, ys


def audit_at_r2(
    target_r2: float,
    n_trials: int = 100,
    sample_size: int = 50,
    degree: int = 2,
    seed_base: int = 0,
) -> Dict[str, int]:
    """For n_trials synthetic datasets at target_r2, tally h2 verdicts."""
    verdicts: Dict[str, int] = {
        Verdict.SHADOW_CATALOG.value: 0,
        Verdict.INCONCLUSIVE.value: 0,
        Verdict.REJECTED.value: 0,
    }
    observed_r2s: List[float] = []
    for i in range(n_trials):
        xs, ys = _synthesize_dataset(sample_size, target_r2, degree, seed_base + i)
        _, observed_r2 = _polyfit_r2(xs, ys, degree)
        observed_r2s.append(observed_r2)
        verdict = _r2_to_verdict(observed_r2)
        verdicts[verdict] += 1
    mean_observed = sum(observed_r2s) / len(observed_r2s) if observed_r2s else 0
    return {
        "target_r2": target_r2,
        "n_trials": n_trials,
        "mean_observed_r2": round(mean_observed, 4),
        "verdicts": verdicts,
        "kill_rate": verdicts[Verdict.REJECTED.value] / n_trials,
        "confirm_rate": verdicts[Verdict.SHADOW_CATALOG.value] / n_trials,
    }


def run_audit(
    n_trials_per_level: int = 100,
    sample_size: int = 50,
    degree: int = 2,
    output_path: Path = None,
) -> Dict:
    """Audit h2 verdict calibration across r² levels."""
    levels = (0.99, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.01)
    per_level = []
    for r2 in levels:
        result = audit_at_r2(
            target_r2=r2,
            n_trials=n_trials_per_level,
            sample_size=sample_size,
            degree=degree,
            seed_base=int(r2 * 10000),
        )
        per_level.append(result)

    # Pre-registered evaluation
    high_r2_results = [r for r in per_level if r["target_r2"] >= 0.9]
    high_r2_kill_rate = (
        sum(r["kill_rate"] for r in high_r2_results) / len(high_r2_results)
    )
    too_narrow = high_r2_kill_rate > 0.20

    summary = {
        "audit_date": datetime.now(timezone.utc).isoformat(),
        "n_trials_per_level": n_trials_per_level,
        "sample_size": sample_size,
        "degree": degree,
        "strong_r2_threshold": STRONG_R2,
        "weak_r2_threshold": WEAK_R2,
        "per_level": per_level,
        "high_r2_mean_kill_rate": round(high_r2_kill_rate, 4),
        "pre_registered_threshold": 0.20,
        "verdict": (
            "h2_TOO_NARROW" if too_narrow
            else "h2_CALIBRATED_OK"
        ),
        "interpretation": (
            "h2 KILLS synthetic data with true r² ≥ 0.9 at "
            f"{high_r2_kill_rate*100:.1f}% — exceeds 20% threshold. "
            "h2's verdict mapping is too strict; high observed kill "
            "rate on cross-catalog samples reflects calibration, not "
            "substrate-meaningful falsification."
        ) if too_narrow else (
            "h2 correctly preserves (does not KILL) synthetic data "
            f"with true r² ≥ 0.9; mean kill rate {high_r2_kill_rate*100:.1f}% "
            "is within the 20% pre-registered threshold. h2's high kill "
            "rate on cross-catalog samples is substrate-meaningful (the "
            "random independent sampling of knots and ECs produces "
            "polynomial-fit-rejecting data, which is the correct verdict)."
        ),
    }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.h2_applicability_audit")
    p.add_argument("--n-trials", type=int, default=100,
                   help="Trials per r² level.")
    p.add_argument("--sample-size", type=int, default=50,
                   help="Per-trial sample size (matches h2 mid-method).")
    p.add_argument("--degree", type=int, default=2,
                   help="Polynomial degree (matches h2 mid-method).")
    p.add_argument("--output", type=Path, default=None,
                   help="Write summary JSON to path.")
    args = p.parse_args()

    summary = run_audit(
        n_trials_per_level=args.n_trials,
        sample_size=args.sample_size,
        degree=args.degree,
        output_path=args.output,
    )
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
