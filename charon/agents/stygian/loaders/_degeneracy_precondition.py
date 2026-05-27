"""Degeneracy precondition — pre-flight gate on (data, inquiry) pairs.

Per Erebos v3 + DR amendment §3.3 (DR Anti-Pattern C: triviality /
degeneracy not gated upstream). A module each loader's applicable()
must consult before returning True. Rejects emissions where the
(data, inquiry) pair makes the loader's test mathematically vacuous.

The G11 v1 Salem-cluster tautology — where 99% of catalog was one
class so the chi² test was structurally guaranteed to fire — would
have been caught here pre-firing. The G25 v1 "any non-empty subset
passes" pathology and G24 v1 "catalog passes by construction" both
would have been gated.

Three orthogonal degeneracy axes:
  1. Effective sample size (Kish formula on weights)
  2. Feature entropy (Shannon, in bits)
  3. Tail concentration index (max class fraction)

Reading: pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md §3.3
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# Default thresholds. Loaders can override per-call.
DEFAULT_THRESHOLD_N_EFFECTIVE = 30
DEFAULT_THRESHOLD_ENTROPY_BITS = 0.5
DEFAULT_THRESHOLD_TAIL_INDEX = 0.95


@dataclass(frozen=True)
class DegeneracyReport:
    """Structured report on whether (data, inquiry) is degenerate."""
    is_degenerate: bool
    n_effective: int
    feature_entropy_bits: float
    tail_concentration_index: float
    reason: Optional[str] = None
    threshold_n_effective: int = DEFAULT_THRESHOLD_N_EFFECTIVE
    threshold_entropy_bits: float = DEFAULT_THRESHOLD_ENTROPY_BITS
    threshold_tail_index: float = DEFAULT_THRESHOLD_TAIL_INDEX

    def to_payload_dict(self) -> dict:
        """Serializable form for inclusion in BatteryLoaderResult."""
        return {
            "is_degenerate": self.is_degenerate,
            "n_effective": self.n_effective,
            "feature_entropy_bits": round(self.feature_entropy_bits, 4),
            "tail_concentration_index": round(self.tail_concentration_index, 4),
            "reason": self.reason,
            "thresholds": {
                "n_effective": self.threshold_n_effective,
                "entropy_bits": self.threshold_entropy_bits,
                "tail_index": self.threshold_tail_index,
            },
        }


class DegenerateInputError(Exception):
    """Raised when a loader fires on degenerate input."""


# --------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------

def kish_effective_n(weights: list[float]) -> int:
    """Kish formula: n_effective = (sum w)^2 / sum w^2.

    For uniform weights, returns N exactly. For concentrated weights
    (e.g., one weight >> others), drops below N.
    """
    if not weights:
        return 0
    s = sum(weights)
    s2 = sum(w * w for w in weights)
    if s2 == 0:
        return 0
    return int((s * s) / s2)


def entropy_bits(distribution: list[float]) -> float:
    """Shannon entropy in bits. Input is treated as unnormalized;
    we normalize internally."""
    if not distribution:
        return 0.0
    total = sum(distribution)
    if total <= 0:
        return 0.0
    h = 0.0
    for w in distribution:
        if w <= 0:
            continue
        p = w / total
        h -= p * math.log2(p)
    return h


def tail_concentration_index(distribution: list[float]) -> float:
    """Max class fraction = max(d) / sum(d). 1.0 means everything in
    one class (fully concentrated); 1/N means uniform."""
    if not distribution:
        return 0.0
    total = sum(distribution)
    if total <= 0:
        return 0.0
    return max(distribution) / total


# --------------------------------------------------------------------
# Report computation + gate
# --------------------------------------------------------------------

def degeneracy_report(
    data: Any,
    inquiry: dict,
    *,
    feature_extractor: Callable[[Any], list[float]],
    threshold_n_effective: int = DEFAULT_THRESHOLD_N_EFFECTIVE,
    threshold_entropy_bits: float = DEFAULT_THRESHOLD_ENTROPY_BITS,
    threshold_tail_index: float = DEFAULT_THRESHOLD_TAIL_INDEX,
    weights: Optional[list[float]] = None,
) -> DegeneracyReport:
    """Compute degeneracy report for a (data, inquiry) pair.

    Parameters:
    - data: the catalog or row-set the loader plans to test on
    - inquiry: dict describing what the loader plans to test
              (e.g., {"test": "binary_split", "binary_field": "salem_class"})
    - feature_extractor: function that takes data and returns the
              test-relevant feature distribution as a list of counts
              (e.g., for a binary split, returns [n_true, n_false])
    - weights: optional per-data-point weights (defaults to uniform)
    - thresholds: per-call overrides for the 3 degeneracy axes

    Returns DegeneracyReport with is_degenerate=True if ANY axis fails.
    """
    distribution = feature_extractor(data)
    if not distribution:
        return DegeneracyReport(
            is_degenerate=True,
            n_effective=0,
            feature_entropy_bits=0.0,
            tail_concentration_index=0.0,
            reason="empty_feature_distribution",
            threshold_n_effective=threshold_n_effective,
            threshold_entropy_bits=threshold_entropy_bits,
            threshold_tail_index=threshold_tail_index,
        )

    if weights is None:
        # Default: uniform weights of size = total item count.
        # Kish formula on uniform weights returns N exactly.
        n_eff = int(sum(distribution))
    else:
        n_eff = kish_effective_n(weights)
    h = entropy_bits(distribution)
    tail = tail_concentration_index(distribution)

    reasons = []
    if n_eff < threshold_n_effective:
        reasons.append(
            f"n_effective={n_eff} < {threshold_n_effective}"
        )
    if h < threshold_entropy_bits:
        reasons.append(
            f"entropy_bits={h:.4f} < {threshold_entropy_bits}"
        )
    if tail > threshold_tail_index:
        reasons.append(
            f"tail_concentration_index={tail:.4f} > {threshold_tail_index}"
        )

    is_degen = len(reasons) > 0
    reason = "; ".join(reasons) if reasons else None

    return DegeneracyReport(
        is_degenerate=is_degen,
        n_effective=n_eff,
        feature_entropy_bits=h,
        tail_concentration_index=tail,
        reason=reason,
        threshold_n_effective=threshold_n_effective,
        threshold_entropy_bits=threshold_entropy_bits,
        threshold_tail_index=threshold_tail_index,
    )


def gate(report: DegeneracyReport) -> None:
    """Raise DegenerateInputError if report.is_degenerate."""
    if report.is_degenerate:
        raise DegenerateInputError(
            f"Degenerate (data, inquiry): {report.reason}. "
            f"n_effective={report.n_effective} "
            f"(threshold {report.threshold_n_effective}), "
            f"entropy_bits={report.feature_entropy_bits:.4f} "
            f"(threshold {report.threshold_entropy_bits}), "
            f"tail_index={report.tail_concentration_index:.4f} "
            f"(threshold {report.threshold_tail_index})."
        )
