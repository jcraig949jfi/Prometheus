"""Selection discipline — forbid arbitrary-scalar candidate selection.

Per Erebos v3 + DR amendment §3.1 (DR Anti-Pattern A: Arbitrary-scalar
selection across G06, G09, G10, G11, G16, G18). A substrate-level
module every loader's `build_battery_input()` must call when selecting
from a candidate set with cardinality > 1.

The module forbids lexicographically-first, modal, random, or
aggregate-scalar selection without an explicit declared selection
metric. Loaders that pick without declaring raise
ArbitraryScalarSelectionError.

Reading: `pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md` §3.1
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class SelectionMetric(Enum):
    """Declared metric a loader uses to select from a candidate set."""
    DISTANCE_MINIMIZING = "distance_minimizing"
    POSTERIOR_MAXIMIZING = "posterior_maximizing"
    ATTRIBUTION_RANKED = "attribution_ranked"
    PERCENTILE_BASED = "percentile_based"
    EXHAUSTIVE = "exhaustive"  # all candidates kept; no single selection


class ArbitraryScalarSelectionError(Exception):
    """Raised when a loader picks first / random / argmax-scalar without
    declaring its metric, OR when the declared metric is incompatible
    with the candidate data type."""


# Registry of valid (data_type, metric) pairs. Updated as new data
# types and metrics earn their place via per-plugin v3 review.
_VALID_METRIC_PAIRS: dict[str, set[SelectionMetric]] = {
    "persistence_diagram": {SelectionMetric.DISTANCE_MINIMIZING},
    "survival_curve": {
        SelectionMetric.POSTERIOR_MAXIMIZING,
        SelectionMetric.PERCENTILE_BASED,
    },
    "feature_vector": {
        SelectionMetric.ATTRIBUTION_RANKED,
        SelectionMetric.DISTANCE_MINIMIZING,
    },
    "kill_pattern_set": {
        SelectionMetric.DISTANCE_MINIMIZING,
        SelectionMetric.EXHAUSTIVE,
    },
    "ledger_row_set": {
        SelectionMetric.POSTERIOR_MAXIMIZING,
        SelectionMetric.EXHAUSTIVE,
    },
    "polynomial_coeffs": {
        SelectionMetric.DISTANCE_MINIMIZING,
        SelectionMetric.ATTRIBUTION_RANKED,
    },
    "scalar_axis_value": {
        SelectionMetric.PERCENTILE_BASED,
        SelectionMetric.POSTERIOR_MAXIMIZING,
    },
}


def validate_metric_for_data_type(
    metric: SelectionMetric, data_type: str
) -> bool:
    """Per the (data_type, valid_metric) registry. E.g.,
    persistence_diagram accepts DISTANCE_MINIMIZING via Wasserstein
    but not POSTERIOR_MAXIMIZING."""
    valid_set = _VALID_METRIC_PAIRS.get(data_type)
    if valid_set is None:
        return False
    return metric in valid_set


def disciplined_select(
    candidates: list[Any],
    metric: Optional[SelectionMetric],
    metric_callable: Optional[Callable[[Any], float]],
    *,
    data_type: str,
    selection_provenance: Optional[dict] = None,
) -> tuple[Any, dict]:
    """Select one candidate from > 1; record the chosen-and-rejected list.

    Raises ArbitraryScalarSelectionError if metric is None, metric_callable
    is None, or the metric is incompatible with the data type.

    Returns (chosen_candidate, provenance_dict). The provenance dict
    includes: chosen_score, rejected_scores, metric, data_type, and
    any caller-supplied selection_provenance.

    Convention: metric_callable returns a SCORE per candidate. For
    DISTANCE_MINIMIZING and PERCENTILE_BASED (where "closer / nearer
    target" wins), the SMALLEST score wins. For POSTERIOR_MAXIMIZING
    and ATTRIBUTION_RANKED, the LARGEST score wins. For EXHAUSTIVE,
    metric_callable is ignored and a list-of-all-candidates is
    returned wrapped in a single-element tuple.
    """
    if not candidates:
        raise ArbitraryScalarSelectionError(
            "disciplined_select called with empty candidates list"
        )

    # Single candidate: pass-through with no metric check (no selection
    # is happening). Still records provenance for audit.
    if len(candidates) == 1:
        provenance = dict(selection_provenance or {})
        provenance.update({
            "chosen_score": None,
            "rejected_scores": [],
            "metric": metric.value if metric else "n/a_single_candidate",
            "data_type": data_type,
            "single_candidate_passthrough": True,
        })
        return candidates[0], provenance

    if metric is None:
        raise ArbitraryScalarSelectionError(
            f"disciplined_select called with {len(candidates)} candidates "
            f"but no SelectionMetric declared. Declare one of "
            f"{[m.value for m in SelectionMetric]} or document why "
            f"EXHAUSTIVE."
        )

    if metric != SelectionMetric.EXHAUSTIVE and metric_callable is None:
        raise ArbitraryScalarSelectionError(
            f"disciplined_select called with metric={metric.value} but no "
            f"metric_callable. Provide a per-candidate scoring function."
        )

    if not validate_metric_for_data_type(metric, data_type):
        raise ArbitraryScalarSelectionError(
            f"disciplined_select: metric {metric.value} is not valid "
            f"for data_type {data_type!r}. Valid metrics for this "
            f"data_type: "
            f"{[m.value for m in _VALID_METRIC_PAIRS.get(data_type, set())]}"
        )

    # Exhaustive: return all candidates wrapped in a list (caller
    # consumes the list rather than picking one).
    if metric == SelectionMetric.EXHAUSTIVE:
        provenance = dict(selection_provenance or {})
        provenance.update({
            "chosen_score": None,
            "rejected_scores": [],
            "metric": metric.value,
            "data_type": data_type,
            "exhaustive_mode": True,
            "n_candidates": len(candidates),
        })
        return list(candidates), provenance

    # Score every candidate; validate finiteness.
    scored: list[tuple[Any, float]] = []
    for c in candidates:
        score = metric_callable(c)
        if not isinstance(score, (int, float)) or not math.isfinite(score):
            raise ArbitraryScalarSelectionError(
                f"metric_callable returned non-finite score {score!r} "
                f"for candidate {c!r}"
            )
        scored.append((c, float(score)))

    # Pick winner per metric semantics.
    smallest_wins = metric in (
        SelectionMetric.DISTANCE_MINIMIZING,
        SelectionMetric.PERCENTILE_BASED,
    )
    scored.sort(key=lambda pair: pair[1], reverse=not smallest_wins)
    chosen, chosen_score = scored[0]
    rejected_scores = [score for _, score in scored[1:]]

    provenance = dict(selection_provenance or {})
    provenance.update({
        "chosen_score": chosen_score,
        "rejected_scores": rejected_scores,
        "metric": metric.value,
        "data_type": data_type,
        "n_candidates": len(candidates),
        "smallest_wins": smallest_wins,
    })
    return chosen, provenance


def register_metric_pair(
    data_type: str, metric: SelectionMetric
) -> None:
    """Extend the (data_type, valid_metric) registry. Used by plugin
    authors who introduce a new data type."""
    if data_type not in _VALID_METRIC_PAIRS:
        _VALID_METRIC_PAIRS[data_type] = set()
    _VALID_METRIC_PAIRS[data_type].add(metric)


def known_data_types() -> list[str]:
    """Return the sorted list of data types registered."""
    return sorted(_VALID_METRIC_PAIRS.keys())
