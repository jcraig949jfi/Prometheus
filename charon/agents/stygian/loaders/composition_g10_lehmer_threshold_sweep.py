"""Composition loader: EREBOS-G10-* (Boundary) on Lehmer-context
parents.

Per the G10 plugin spec: takes a claim that shows strange
heteroskedasticity (variance changes over scale) and predicts
SMOOTH degradation across a threshold sweep. This loader runs the
sweep on the Mossinghoff catalog: survival fraction at M_threshold
values from M_Lehmer up to UPPER_BOUND, and checks whether the
degradation is smooth (G10's prediction) or has a cliff (boundary
is sharp, not smooth — kill_pattern = sharp_boundary_detected).

Concrete measurement:
- Sweep thresholds: M_Lehmer, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45,
  1.50.
- At each threshold, compute survival_fraction(values >= threshold)
  over the Mossinghoff non-cyclotomic catalog.
- Compute first-differences across consecutive thresholds.
- Smoothness metric = max(abs(first_differences)) /
  mean(abs(first_differences)). Smooth degradation has ratio close
  to 1 (uniform drop); a cliff has ratio >> 1.

Decision rule:
- smoothness_ratio <= SMOOTH_THRESHOLD: smooth degradation confirmed
  -> PROMOTED (G10's hypothesis survives).
- smoothness_ratio > SMOOTH_THRESHOLD: a sharp cliff exists in the
  sweep -> REJECTED with kill_pattern = sharp_boundary_detected
  (G10 mis-modeled the boundary shape).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
    survival_fraction,
)


# Threshold sweep range (anchored at M_Lehmer, walked upward to 1.50)
SWEEP_THRESHOLDS = [
    M_LEHMER, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50,
]
# Max-to-mean ratio of first differences above which we call it a
# cliff rather than smooth degradation. Empirically chosen at 3x.
SMOOTH_THRESHOLD = 3.0
MIN_SAMPLE_SIZE = 100


def _first_differences(values: list[float]) -> list[float]:
    return [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]


def _smoothness_ratio(diffs: list[float]) -> float:
    if not diffs:
        return 0.0
    mean = sum(diffs) / len(diffs)
    if mean == 0:
        return 0.0
    return max(diffs) / mean


def run_g10_lehmer_threshold_sweep() -> dict:
    """Sweep thresholds; measure smoothness vs cliff."""
    entries = load_non_cyclotomic_mahler_entries()
    values = [float(e["mahler_measure"]) for e in entries]
    if len(values) < MIN_SAMPLE_SIZE:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_sample": len(values),
            "notes": (
                f"Mossinghoff catalog too small (n={len(values)} < "
                f"{MIN_SAMPLE_SIZE})"
            ),
        }
    survivals = [survival_fraction(values, t) for t in SWEEP_THRESHOLDS]
    diffs = _first_differences(survivals)
    ratio = _smoothness_ratio(diffs)

    if ratio <= SMOOTH_THRESHOLD:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"Smoothness ratio = {ratio:.3f} <= {SMOOTH_THRESHOLD}; "
            f"survival degrades smoothly across the threshold sweep "
            f"({SWEEP_THRESHOLDS}). G10's smooth-degradation "
            f"hypothesis is consistent with the Mossinghoff data."
        )
    else:
        verdict = "REJECTED"
        kp = "sharp_boundary_detected"
        notes = (
            f"Smoothness ratio = {ratio:.3f} > {SMOOTH_THRESHOLD}; "
            f"a sharp drop dominates the sweep (max diff "
            f"{max(diffs):.4f} vs mean {sum(diffs)/len(diffs):.4f}). "
            f"G10 mis-modeled the boundary as smooth; there's a cliff "
            f"in the threshold response."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "sweep_thresholds": [round(t, 4) for t in SWEEP_THRESHOLDS],
        "survival_fractions": [round(s, 4) for s in survivals],
        "first_differences": [round(d, 4) for d in diffs],
        "smoothness_ratio": round(ratio, 4),
        "smoothness_threshold": SMOOTH_THRESHOLD,
        "n_sample": len(values),
        "notes": notes,
    }


class G10LehmerThresholdSweepLoader:
    plugin_id = "g10_boundary"
    composition_id = "g10_lehmer_threshold_sweep"
    description = (
        "Composition loader for EREBOS-G10-* claims whose parent is "
        "BL-C-001 Lehmer. Sweeps survival fraction across M_Lehmer "
        "-> 1.50; measures max/mean of first-differences; "
        "PROMOTED if smooth, REJECTED with sharp_boundary_detected "
        "if a cliff dominates."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g10_boundary":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        return (
            "BL-C-001" in composed_id
            or "lehmer" in composed_id.lower()
            or "lehmer" in rationale
            or "mahler" in rationale
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g10_lehmer_threshold_sweep()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G10 threshold-sweep composition: survival "
                f"fraction is measured at {len(SWEEP_THRESHOLDS)} "
                f"thresholds from M_Lehmer to 1.50; smoothness vs "
                f"cliff is the test."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; multi-threshold sweep."
            ),
            "result": result,
            "notes": (
                "G10 graduates to empirical instrument for Lehmer-"
                "context emissions via the threshold-sweep + "
                "first-difference smoothness ratio."
            ),
        }


register(G10LehmerThresholdSweepLoader())
