"""A battery of authored defects with ground truth by construction (cycle 057).

Built to answer a question the cycle 055-056 score comparison could not: do targeted READING
and executable PROBING have different POWER, or different DOMAINS?

Each shape appears twice -- once defective, once clean and otherwise identical -- so the clean
halves supply the FALSE-POSITIVE rate cycle 055 could not establish (its negative control
turned out to carry the defect under study).

Ground truth is in `TRUTH` at the bottom. It is authored, not discovered, which is the point:
a probe's verdict can then be scored without appeal to my judgement.
"""
from __future__ import annotations

import math
from typing import Sequence

# ---------------------------------------------------------------- S1 EMPTY-CONFLATION

def s1_defective(scores: Sequence[float], threshold: float) -> float:
    """Fraction of scores at or above threshold."""
    if not scores:
        return 0.0                      # DEFECT: same value as "measured, none passed"
    return sum(1 for s in scores if s >= threshold) / len(scores)


def s1_clean(scores: Sequence[float], threshold: float) -> float | None:
    """Fraction of scores at or above threshold; None when there is nothing to measure."""
    if not scores:
        return None                     # structurally distinct from any legitimate fraction
    return sum(1 for s in scores if s >= threshold) / len(scores)


# ------------------------------------------------------------ S2 UNCONDITIONAL-CONSTANT

def s2_defective(records: Sequence[dict]) -> float:
    """Fraction of records that are unique (1.0 = all unique)."""
    if not records:
        return 1.0
    # DEFECT: placeholder pending a real dedup count -- every path returns the healthy value.
    return 1.0


def s2_clean(records: Sequence[dict]) -> float:
    """Fraction of records that are unique (1.0 = all unique)."""
    if not records:
        return 1.0
    seen = {r.get("id") for r in records}
    return len(seen) / len(records)


# -------------------------------------------------------------- S3 DOC-BEHAVIOUR GAP

def s3_defective(values: Sequence[float]) -> float:
    """Return the MEDIAN of values (0.0 if empty)."""
    if not values:
        return 0.0
    return sum(values) / len(values)    # DEFECT: computes the mean; docstring says median


def s3_clean(values: Sequence[float]) -> float:
    """Return the MEDIAN of values (0.0 if empty)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


# ---------------------------------------------------------------- S4 CONDITION-NUMBER

def s4_defective(a: float, b: float) -> float:
    """Return a - b, the difference of two nearby quantities."""
    # DEFECT: catastrophic cancellation via the algebraically-equal but unstable route.
    return (a * a - b * b) / (a + b) if (a + b) != 0 else 0.0


def s4_clean(a: float, b: float) -> float:
    """Return a - b, the difference of two nearby quantities."""
    return a - b


# --------------------------------------------------------------------- S5 SILENT-NAN

def s5_defective(values: Sequence[float]) -> float:
    """Coefficient of variation: stdev / mean."""
    n = len(values)
    mean = sum(values) / n if n else float("nan")       # DEFECT: unguarded nan propagates
    var = sum((v - mean) ** 2 for v in values) / n if n else float("nan")
    return math.sqrt(var) / mean


def s5_clean(values: Sequence[float]) -> float:
    """Coefficient of variation: stdev / mean. Refuses where it is undefined."""
    n = len(values)
    if n == 0:
        raise ValueError("coefficient of variation is undefined on zero observations")
    mean = sum(values) / n
    if mean == 0:
        raise ValueError("coefficient of variation is undefined when the mean is zero")
    var = sum((v - mean) ** 2 for v in values) / n
    return math.sqrt(var) / mean


TRUTH = {
    "s1_defective": True,  "s1_clean": False,
    "s2_defective": True,  "s2_clean": False,
    "s3_defective": True,  "s3_clean": False,
    "s4_defective": True,  "s4_clean": False,
    "s5_defective": True,  "s5_clean": False,
}
