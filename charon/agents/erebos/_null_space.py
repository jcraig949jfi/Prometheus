"""Null-space detection — third Layer 2 primitive (Phase 1C ITER-42).

Per feedback_failure_signal_vector_field.md:
> "failures emit directional pointers, not pass/fail. Net sum maps
>  a lattice; voids in the lattice ARE the mathematics
>  (vanishing ideals / Morse theory / persistent homology /
>  sheaf cohomology / Yoneda all the same principle)."

And feedback_residue_must_be_navigable_not_logged.md:
> "every reasoning act leaves navigable residue" -- residue
> includes the SHAPE of what's missing.

ITER-42 turns the kill_tensor's empty cells from "no observation"
into "evidence of structure." A void is informative iff the
missing value is COMMON elsewhere in the tensor -- a globally-rare
value being absent from one frame is uninformative; a globally-
common value being absent from a frame is a structural signal.

## What a void is

Given a tensor and a choice of which axes to FIX (the "frame"
axes) vs which axis to SCAN (the candidate axis), a void is:
  - a frame_key F (values along the fixed axes)
  - a candidate value v (along the scan axis)
  - F has populated cells with OTHER candidate values, but the
    specific cell at (F, v) is empty
  - v is populated for OTHER frames in the tensor

The void's score is the global frequency of v -- the fraction of
frames in the tensor where v IS populated. High score means the
missing value is common elsewhere; the void is informative.
Low score means v is rare, so its absence here adds no signal.

## What this primitive is NOT

- NOT a generator. Read-side only.
- NOT a quality filter. A high-score void may be a real structural
  feature OR an artifact of the substrate's sampling. Layer 2
  navigation decides.
- NOT a clustering algorithm. Voids are listed individually; no
  merging.
- NOT a topological invariant. Persistent homology / Morse / sheaf
  framing is the inspiration; this MVP just counts marginal
  absences. Topological structure is for later iterations.

## Storage-backend independence

Takes a KillTensor (ITER-41) instance. The tensor itself is
storage-backend independent; this primitive inherits that.
"""
from __future__ import annotations

from collections import defaultdict
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


@dataclass(frozen=True)
class Void:
    """A structural void in the kill tensor.

    Attributes:
        fix_axes: axes held constant (the frame). Sorted ascending.
        frame_key: values along fix_axes, in the same order.
        scan_axis: the axis being scanned for missing values.
        missing_value: the value that's absent at (frame_key, _).
        score: global frequency of missing_value across all frames
            with the same fix_axes shape. In [0.0, 1.0]; higher
            means more informative.
        n_frames_with_value: count of frames in the tensor where
            missing_value IS populated.
        n_total_frames: count of distinct frames (same fix_axes
            shape) in the tensor.
    """
    fix_axes: tuple[int, ...]
    frame_key: tuple[str, ...]
    scan_axis: int
    missing_value: str
    score: float
    n_frames_with_value: int
    n_total_frames: int

    def axis_name(self) -> str:
        """Human-readable scan axis name."""
        return AXIS_NAMES[self.scan_axis]

    def frame_axis_names(self) -> tuple[str, ...]:
        return tuple(AXIS_NAMES[a] for a in self.fix_axes)


@dataclass(frozen=True)
class NullSpaceResult:
    """Output of a single find_voids call."""
    fix_axes: tuple[int, ...]
    scan_axis: int
    voids: tuple[Void, ...]
    min_score_threshold: float
    n_frames_scanned: int
    n_voids_before_threshold: int
    notes: str = ""

    def top(self, k: int) -> tuple[Void, ...]:
        return self.voids[:k]


def _validate_axes(
    fix_axes: tuple[int, ...]
) -> tuple[tuple[int, ...], int]:
    """Check fix_axes is a 3-subset of {0,1,2,3}; return
    (sorted_fix, scan_axis)."""
    if len(fix_axes) != N_AXES - 1:
        raise ValueError(
            f"find_voids: fix_axes must hold {N_AXES - 1} of {N_AXES} "
            f"axes; got {len(fix_axes)}"
        )
    fix_set = set(fix_axes)
    if any(a < 0 or a >= N_AXES for a in fix_axes):
        raise ValueError(
            f"find_voids: fix_axes values must be in 0..{N_AXES - 1}; "
            f"got {fix_axes}"
        )
    if len(fix_set) != N_AXES - 1:
        raise ValueError(
            f"find_voids: fix_axes has duplicates: {fix_axes}"
        )
    scan_candidates = set(range(N_AXES)) - fix_set
    scan_axis = scan_candidates.pop()
    return tuple(sorted(fix_set)), scan_axis


def find_voids(
    tensor: KillTensor,
    *,
    fix_axes: tuple[int, ...] = (AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT),
    min_score: float = 0.5,
    sample_limit: int = 200,
) -> NullSpaceResult:
    """Identify voids: empty cells at (frame, value) where the value
    is populated for other frames.

    Args:
        tensor: KillTensor instance.
        fix_axes: 3 of the 4 axes to hold fixed (the frame). Default
            (PLUGIN, DOMAIN, INVARIANT), scanning the KP axis -- the
            most natural framing ("for each generator x domain x
            invariant cell, which kps are missing?").
        min_score: minimum global-frequency threshold to include a
            void in the result. Voids below threshold are counted
            in n_voids_before_threshold but not returned.
        sample_limit: cap on voids returned (sorted by score
            descending). Hard cap to keep results auditable; raise
            if you need more.

    Returns:
        NullSpaceResult.
    """
    fix_axes, scan_axis = _validate_axes(fix_axes)

    # Group populated cells by frame_key -> set of populated scan
    # values
    by_frame: defaultdict[tuple[str, ...], set[str]] = defaultdict(set)
    for cell in tensor.cells:
        frame_key = tuple(cell[a] for a in fix_axes)
        scan_value = cell[scan_axis]
        by_frame[frame_key].add(scan_value)

    n_frames = len(by_frame)
    if n_frames == 0:
        return NullSpaceResult(
            fix_axes=fix_axes,
            scan_axis=scan_axis,
            voids=(),
            min_score_threshold=min_score,
            n_frames_scanned=0,
            n_voids_before_threshold=0,
            notes="tensor has no populated cells",
        )

    # Global value -> count of frames where it is populated.
    # A globally-common value being absent from a frame is the
    # informative case.
    value_to_n_frames: defaultdict[str, int] = defaultdict(int)
    for frame_key, values in by_frame.items():
        for v in values:
            value_to_n_frames[v] += 1

    all_scan_values = set(value_to_n_frames.keys())

    voids: list[Void] = []
    n_below_threshold = 0
    for frame_key, populated_values in by_frame.items():
        missing = all_scan_values - populated_values
        for v in missing:
            n_with_v = value_to_n_frames[v]
            # Score: of the OTHER frames (excluding self), what
            # fraction has v populated?
            # Self is by definition NOT in n_with_v (it's missing),
            # so just n_with_v / (n_frames - 1) for n_frames >= 2.
            # When n_frames == 1, there's only one frame and no
            # comparison possible; score = 0.
            if n_frames <= 1:
                score = 0.0
            else:
                score = n_with_v / (n_frames - 1)
            if score < min_score:
                n_below_threshold += 1
                continue
            voids.append(Void(
                fix_axes=fix_axes,
                frame_key=frame_key,
                scan_axis=scan_axis,
                missing_value=v,
                score=score,
                n_frames_with_value=n_with_v,
                n_total_frames=n_frames,
            ))

    # Sort: score desc, then missing_value asc (stable), then frame_key asc
    voids.sort(key=lambda v: (-v.score, v.missing_value, v.frame_key))
    truncated = len(voids) > sample_limit
    voids_out = voids[:sample_limit]

    notes_parts = [
        f"scanned {n_frames} frames along axis "
        f"{AXIS_NAMES[scan_axis]!r}",
        f"surfaced {len(voids_out)} voids at score >= {min_score}",
        f"({n_below_threshold} below threshold)",
    ]
    if truncated:
        notes_parts.append(
            f"truncated from {len(voids)} -> {sample_limit} by "
            f"sample_limit"
        )

    return NullSpaceResult(
        fix_axes=fix_axes,
        scan_axis=scan_axis,
        voids=tuple(voids_out),
        min_score_threshold=min_score,
        n_frames_scanned=n_frames,
        n_voids_before_threshold=n_below_threshold,
        notes="; ".join(notes_parts),
    )


def find_voids_all_scans(
    tensor: KillTensor,
    *,
    min_score: float = 0.5,
    sample_limit_per_scan: int = 200,
) -> dict[str, NullSpaceResult]:
    """Run find_voids for each possible scan axis.

    Returns a dict keyed by the scan axis name ("plugin", "domain",
    "invariant", "kp"). Useful for one-shot Layer 2 audits.
    """
    results: dict[str, NullSpaceResult] = {}
    for scan_axis in range(N_AXES):
        fix_axes = tuple(a for a in range(N_AXES) if a != scan_axis)
        r = find_voids(
            tensor,
            fix_axes=fix_axes,
            min_score=min_score,
            sample_limit=sample_limit_per_scan,
        )
        results[AXIS_NAMES[scan_axis]] = r
    return results
