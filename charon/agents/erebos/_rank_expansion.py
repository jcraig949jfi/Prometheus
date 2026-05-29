"""Rank-expansion test — fourth Layer 2 primitive (Phase 1C ITER-43).

Per feedback_gen_30_wall.md:
> "self-improving agents hit a bounded-menu wall (James's C# agent
>  stalled at gen 30). Don't optimize for deeper menus; design for
>  menu-growth mechanisms (cross-agent borrow, compositional,
>  LLM-authored) or generational handoff."

And tying back to the eligibility gate's CRITERION_ADDS_TENSOR_RANK
(ITER-35): every emission that adds a new (plugin, domain, kp)
triple grows the tensor. This primitive measures that growth rate.

A stalling substrate is a substrate where the tensor is no longer
gaining cells, axes are no longer gaining values, or both. The
bounded-menu wall is visible as a flat snapshot series.

Concrete adjacent signal: Techne is currently sitting at 90
consecutive 0-promoted batches (per repo status 2026-05-29). This
primitive is the kind of detector that would have caught that
plateau formally, with per-axis attribution -- a tool the
substrate can use to ask "WHERE has rank stopped expanding?"
instead of just "is it expanding?"

## Snapshot

A RankSnapshot captures the tensor's structural state at a point
in time: n_populated_cells, axis_cardinalities (4-tuple), density.
Snapshots are frozen + comparable.

## Comparison

compare_snapshots(s1, s2) returns a RankComparison with deltas
per axis + boolean predicates ("did any axis grow", "did
populated cells grow", etc.).

## Stall detection

is_stalled(snapshots, window, ...) walks a list of snapshots and
returns True iff the most recent `window` snapshots show no
growth on any axis above the configured per-axis threshold. The
caller can specify per-axis thresholds because adding a new
plugin (axis 0) is much harder than adding a new invariant
(axis 2). Defaults are conservative.

stalled_axes(...) reports WHICH axes are stalled when the
substrate as a whole has not stalled. Per-axis diagnosis lets
the caller route to whichever axis needs intervention.

## What this primitive is NOT

- NOT a generator. Read-side only.
- NOT a quality filter. A stalled substrate may still be doing
  useful Layer-1 work; rank expansion is one of several
  substrate-internal metrics.
- NOT a time-series database. Snapshots are passed in by the
  caller; this primitive doesn't persist them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from charon.agents.erebos._kill_tensor import (
    AXIS_DOMAIN,
    AXIS_INVARIANT,
    AXIS_KP,
    AXIS_NAMES,
    AXIS_PLUGIN,
    N_AXES,
    KillTensor,
)


# Default per-axis stall thresholds (minimum NEW values per window
# to NOT be considered stalled on that axis). PLUGIN is hardest to
# expand (each plugin must be coded); KP comes from a small
# registry; DOMAIN expands when crossing into new mathematical
# fields; INVARIANT can grow more freely.
DEFAULT_STALL_THRESHOLD_PER_AXIS = {
    AXIS_PLUGIN: 0,     # any plugin addition counts as growth
    AXIS_DOMAIN: 0,
    AXIS_INVARIANT: 1,  # at least one new invariant per window
    AXIS_KP: 0,
}
DEFAULT_STALL_THRESHOLD_POPULATED = 1  # at least 1 new populated cell


@dataclass(frozen=True)
class RankSnapshot:
    """The tensor's structural state at a point in time.

    Attributes:
        timestamp: caller-supplied ordering label. Any sortable
            type works (ISO-8601 string, integer tick number,
            float seconds). The primitive only compares for
            ordering / equality, never parses time.
        n_populated: how many cells have count > 0.
        axis_cardinalities: 4-tuple of distinct value counts per
            axis (plugin, domain, invariant, kp).
        n_total_count: sum of all cell counts (for context, not
            structural).
        density: populated / product_of_cardinalities. None when
            any axis is empty.
    """
    timestamp: object
    n_populated: int
    axis_cardinalities: tuple[int, int, int, int]
    n_total_count: int
    density: Optional[float]

    @classmethod
    def take(cls, tensor: KillTensor, *, timestamp: object) -> "RankSnapshot":
        """Capture a snapshot of the tensor's current rank state."""
        card = tensor.axis_cardinalities()
        product = card[0] * card[1] * card[2] * card[3]
        density = (
            tensor.n_populated_cells() / product if product > 0 else None
        )
        return cls(
            timestamp=timestamp,
            n_populated=tensor.n_populated_cells(),
            axis_cardinalities=card,
            n_total_count=tensor.total_count(),
            density=density,
        )


@dataclass(frozen=True)
class RankComparison:
    """The delta between two snapshots (s2 - s1)."""
    s1_timestamp: object
    s2_timestamp: object
    delta_populated: int
    delta_axis_cardinalities: tuple[int, int, int, int]
    delta_total_count: int

    def any_axis_grew(self) -> bool:
        """True iff at least one axis cardinality strictly increased."""
        return any(d > 0 for d in self.delta_axis_cardinalities)

    def populated_grew(self) -> bool:
        """True iff strictly more populated cells."""
        return self.delta_populated > 0

    def growing(self) -> bool:
        """Either axis or populated growth counts as growth."""
        return self.any_axis_grew() or self.populated_grew()


@dataclass(frozen=True)
class StallReport:
    """Output of is_stalled / stalled_axes."""
    is_stalled: bool
    window_size: int
    n_snapshots_examined: int
    stalled_axes: tuple[int, ...]   # axes that did NOT grow above threshold
    growing_axes: tuple[int, ...]    # axes that DID grow above threshold
    populated_growth: int            # total populated-cell growth over window
    populated_growth_threshold: int  # the threshold used
    per_axis_growth: tuple[int, int, int, int]  # delta per axis over window
    per_axis_thresholds: tuple[int, int, int, int]
    notes: str = ""


def compare_snapshots(s1: RankSnapshot, s2: RankSnapshot) -> RankComparison:
    """Return (s2 - s1) delta across all rank measures."""
    return RankComparison(
        s1_timestamp=s1.timestamp,
        s2_timestamp=s2.timestamp,
        delta_populated=s2.n_populated - s1.n_populated,
        delta_axis_cardinalities=tuple(
            s2.axis_cardinalities[i] - s1.axis_cardinalities[i]
            for i in range(N_AXES)
        ),  # type: ignore[arg-type]
        delta_total_count=s2.n_total_count - s1.n_total_count,
    )


def _resolve_thresholds(
    threshold_per_axis: Optional[dict[int, int]],
    threshold_populated: Optional[int],
) -> tuple[tuple[int, int, int, int], int]:
    per_axis_dict = dict(DEFAULT_STALL_THRESHOLD_PER_AXIS)
    if threshold_per_axis is not None:
        per_axis_dict.update(threshold_per_axis)
    per_axis = tuple(per_axis_dict[i] for i in range(N_AXES))  # type: ignore[assignment]
    pop = (
        DEFAULT_STALL_THRESHOLD_POPULATED
        if threshold_populated is None
        else threshold_populated
    )
    return per_axis, pop  # type: ignore[return-value]


def is_stalled(
    snapshots: list[RankSnapshot],
    *,
    window: int = 5,
    threshold_per_axis: Optional[dict[int, int]] = None,
    threshold_populated: Optional[int] = None,
) -> StallReport:
    """Detect whether rank has stopped expanding over the last
    `window` snapshots.

    Algorithm:
      1. Take the LAST `window` snapshots (or all of them if
         fewer exist; reports n_snapshots_examined).
      2. Compute delta between first and last in the window
         (per axis + populated).
      3. An axis is "stalled" iff delta_axis < threshold_per_axis.
      4. The substrate is "stalled" iff ALL four axes are stalled
         AND populated growth < threshold_populated.
      5. Diagnose by listing the stalled vs growing axes.
    """
    per_axis_thresh, pop_thresh = _resolve_thresholds(
        threshold_per_axis, threshold_populated
    )
    if len(snapshots) < 2:
        return StallReport(
            is_stalled=False,
            window_size=window,
            n_snapshots_examined=len(snapshots),
            stalled_axes=(),
            growing_axes=tuple(range(N_AXES)),
            populated_growth=0,
            populated_growth_threshold=pop_thresh,
            per_axis_growth=(0, 0, 0, 0),
            per_axis_thresholds=per_axis_thresh,
            notes=(
                "fewer than 2 snapshots; cannot evaluate stall "
                f"(have {len(snapshots)})"
            ),
        )
    window_snapshots = snapshots[-window:]
    n_examined = len(window_snapshots)
    first, last = window_snapshots[0], window_snapshots[-1]
    cmp = compare_snapshots(first, last)

    growing: list[int] = []
    stalled: list[int] = []
    for axis in range(N_AXES):
        delta = cmp.delta_axis_cardinalities[axis]
        if delta > per_axis_thresh[axis]:
            growing.append(axis)
        else:
            stalled.append(axis)

    populated_growing = cmp.delta_populated > pop_thresh

    substrate_stalled = (not growing) and (not populated_growing)

    notes_parts = [
        f"examined {n_examined} snapshots over window={window}",
        (
            f"populated delta = {cmp.delta_populated} "
            f"(threshold > {pop_thresh})"
        ),
        f"axis deltas = {cmp.delta_axis_cardinalities}",
    ]
    if substrate_stalled:
        notes_parts.append(
            "STALLED: bounded-menu wall candidate -- all axes flat"
        )
    elif stalled:
        notes_parts.append(
            f"partial stall on axes "
            f"{tuple(AXIS_NAMES[a] for a in stalled)}"
        )

    return StallReport(
        is_stalled=substrate_stalled,
        window_size=window,
        n_snapshots_examined=n_examined,
        stalled_axes=tuple(stalled),
        growing_axes=tuple(growing),
        populated_growth=cmp.delta_populated,
        populated_growth_threshold=pop_thresh,
        per_axis_growth=cmp.delta_axis_cardinalities,
        per_axis_thresholds=per_axis_thresh,
        notes="; ".join(notes_parts),
    )


def consecutive_zero_growth_run(
    snapshots: list[RankSnapshot],
) -> int:
    """Return the length of the longest TRAILING run of snapshots
    with no populated-cell growth.

    Mirrors Techne's "N consecutive 0-promoted" metric in commit
    messages -- a useful coarse plateau indicator. A run of 0
    means the most recent snapshot DID gain populated cells.
    """
    if len(snapshots) < 2:
        return 0
    run = 0
    for i in range(len(snapshots) - 1, 0, -1):
        if snapshots[i].n_populated <= snapshots[i - 1].n_populated:
            run += 1
        else:
            break
    return run
