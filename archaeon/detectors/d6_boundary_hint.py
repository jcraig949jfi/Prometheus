"""D6 BOUNDARY / TRANSITION HINT.

Adjacent or nearby parameter settings show substantially different behaviour,
suggesting an unresolved boundary.

Grain: an ADJACENT PAIR of coordinate bins along ONE axis. Rows are binned on
the axis, bins sorted, and each consecutive pair examined.

Three conditions, all required:

  ADJACENCY  gap <= d6_max_gap in normalized units. A large step across a
             large gap is just the metric varying with the parameter.
  SALIENCE   |difference| >= d6_min_jump_sd pooled SDs, so the step beats the
             local scatter. The pooled SD comes from the two bins themselves,
             not from a global SD that a strong trend would inflate.
  LOCALITY   the step exceeds the axis's own MEDIAN adjacent step by
             d6_min_trend_ratio.

LOCALITY is the condition the v0 build lacked, and it is the one that carries
the detector's meaning. Salience alone cannot tell a boundary from a smooth
trend: on a gradient every adjacent pair is a large step relative to local
scatter, so v0 fired on 83% of gradual-trend corpora carrying the same
end-to-end change as a planted step. A BOUNDARY is a step that is large
COMPARED TO THE OTHER STEPS on the same axis; a trend is one where every step
is the same size. The median is used rather than the mean so that the boundary
step, which is one of the steps being summarised, does not inflate the
baseline it is being judged against.

An axis with fewer than d6_min_steps_for_trend steps has no usable median and
is reported NOT ELIGIBLE rather than judged without the comparison.

This detector needs coordinates. Without them "adjacent parameter settings" has
no referent and eligibility is zero.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, List, Tuple

from .base import (DetectorResult, Eligibility, Signal, INTENT_REFINE_BOUNDARY,
                   mean, median, variance, clamp01)

NAME = "BOUNDARY_TRANSITION_HINT"
VERSION = "d6.v1"
UNIT = "adjacent coordinate-bin pair on one axis"

# Binning resolution along an axis. Finer than d5's cell bin because a boundary
# is looked for BETWEEN bins, so the bin must be smaller than the gap the
# detector is willing to call adjacent.
BIN_WIDTH = 0.02


def detect(corpus, dcfg) -> DetectorResult:
    rows = corpus.rows
    axes = list(corpus.chart.coord_fields)

    if not axes:
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT,
            blocked_reason=("chart declares no coordinate axes, so 'adjacent "
                            "parameter settings' has no referent"),
            detail={"chart": corpus.chart.name}))

    scales = corpus.coord_scales()
    live_axes = [a for a in axes
                 if a in scales and scales[a]["span"] > 0]
    if not live_axes:
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT,
            blocked_reason=("every coordinate axis is degenerate (zero span) "
                            "in this corpus, so no two settings are distinct"),
            detail={"axes": axes,
                    "spans": {a: scales.get(a, {}).get("span") for a in axes}}))

    total_units = 0
    eligible_units = 0
    signals: List[Signal] = []
    per_axis: Dict[str, Dict[str, int]] = {}

    for axis in live_axes:
        bins: Dict[float, List] = defaultdict(list)
        for r in rows:
            nc = corpus.normalized_coords(r, scales)
            if axis not in nc:
                continue
            bins[round(nc[axis] / BIN_WIDTH) * BIN_WIDTH].append(r)

        ordered = sorted(bins)
        total_units += max(len(ordered) - 1, 0)
        ok = [b for b in ordered if len(bins[b]) >= dcfg.d6_min_n_side]
        pairs = [(ordered[i], ordered[i + 1]) for i in range(len(ordered) - 1)
                 if len(bins[ordered[i]]) >= dcfg.d6_min_n_side
                 and len(bins[ordered[i + 1]]) >= dcfg.d6_min_n_side
                 and (ordered[i + 1] - ordered[i]) <= dcfg.d6_max_gap]

        # The axis's own step profile: |mean(b_{i+1}) - mean(b_i)| over every
        # eligible adjacent pair. Its MEDIAN is the trend baseline.
        steps = [abs(mean([r.metric for r in bins[b2]])
                     - mean([r.metric for r in bins[b1]]))
                 for b1, b2 in pairs]
        has_trend_baseline = len(steps) >= dcfg.d6_min_steps_for_trend
        median_step = median(steps) if has_trend_baseline else None

        per_axis[axis] = {"bins": len(ordered), "bins_supported": len(ok),
                          "adjacent_pairs": len(pairs),
                          "steps_available": len(steps),
                          "median_adjacent_step": median_step,
                          "trend_baseline": ("AVAILABLE" if has_trend_baseline
                                             else "TOO_FEW_STEPS")}
        if not has_trend_baseline:
            # No usable trend baseline -> this axis contributes no eligible
            # units. Judging a step without it cannot distinguish a boundary
            # from a gradient, which is the whole question.
            continue
        eligible_units += len(pairs)

        for b1, b2 in pairs:
            v1 = [r.metric for r in bins[b1]]
            v2 = [r.metric for r in bins[b2]]
            n1, n2 = len(v1), len(v2)
            # pooled SD of the two sides
            pooled_var = (((n1 - 1) * variance(v1) + (n2 - 1) * variance(v2))
                          / max(n1 + n2 - 2, 1))
            pooled_sd = math.sqrt(pooled_var)
            if pooled_sd <= 0:
                continue
            jump = mean(v2) - mean(v1)
            jump_sd = abs(jump) / pooled_sd
            gap = b2 - b1
            if jump_sd < dcfg.d6_min_jump_sd:
                continue
            # LOCALITY: is this step unusual FOR THIS AXIS?
            if median_step <= 0:
                # A perfectly flat axis with one step: the ratio is unbounded
                # but meaningless, since a zero median means fewer than half
                # the steps moved at all. Require the salience test only.
                trend_ratio = float("inf")
            else:
                trend_ratio = abs(jump) / median_step
            if trend_ratio < dcfg.d6_min_trend_ratio:
                continue

            signals.append(Signal(
                detector=NAME, detector_version=VERSION,
                intent=INTENT_REFINE_BOUNDARY,
                regions=tuple(sorted({r.region for r in bins[b1]} |
                                     {r.region for r in bins[b2]})),
                players=(),
                values={"axis": axis,
                        "bin_low": b1, "bin_high": b2,
                        "coordinate_gap": gap,
                        "mean_low": mean(v1), "mean_high": mean(v2),
                        "jump": jump, "jump_sd_units": jump_sd,
                        "median_adjacent_step_on_axis": median_step,
                        "trend_ratio": trend_ratio,
                        "steps_on_axis": len(steps),
                        "pooled_sd": pooled_sd,
                        "n_low": n1, "n_high": n2,
                        "axis_scale": dict(scales[axis])},
                thresholds={"d6_max_gap": dcfg.d6_max_gap,
                            "d6_min_jump_sd": dcfg.d6_min_jump_sd,
                            "d6_min_trend_ratio": dcfg.d6_min_trend_ratio,
                            "d6_min_n_side": dcfg.d6_min_n_side,
                            "d6_min_steps_for_trend":
                                dcfg.d6_min_steps_for_trend,
                            "bin_width": BIN_WIDTH},
                support_n=n1 + n2,
                effect_norm=clamp01(jump_sd / 6.0),
                # Bisect: the boundary, if there is one, lies between the bins.
                target_coords={axis: 0.5 * (b1 + b2)},
                evidence_rows=tuple(r.anchor_ref()
                                    for r in (bins[b1][:32] + bins[b2][:32])),
            ))

    if eligible_units == 0:
        return DetectorResult(Eligibility(
            NAME, 0, total_units, UNIT,
            blocked_reason=("no axis supplies both adjacent bin pairs (bins "
                            "supported by d6_min_n_side={} rows and within "
                            "d6_max_gap={}) AND at least d6_min_steps_for_trend"
                            "={} steps to form the trend baseline a boundary "
                            "must be judged against"
                            .format(dcfg.d6_min_n_side, dcfg.d6_max_gap,
                                    dcfg.d6_min_steps_for_trend)),
            detail={"per_axis": per_axis, "bin_width": BIN_WIDTH}))

    return DetectorResult(
        Eligibility(NAME, eligible_units, total_units, UNIT,
                    detail={"per_axis": per_axis, "bin_width": BIN_WIDTH}),
        tuple(signals))
