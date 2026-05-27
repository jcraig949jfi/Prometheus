"""Composition loader: EREBOS-G23-* (Asymptotic Limit) on Lehmer-
context parents.

Per the G23 plugin spec: hypothesizes error / failure rate scales
as O(1/N) where N is object complexity. For Lehmer-context, the
natural complexity is polynomial degree N, and the natural "error"
is the gap between the smallest known Mahler measure at degree N
and M_Lehmer (which is the conjectured floor).

Concrete test (v0.16 MVP):
- For each degree N in the catalog, compute M_min(N) = smallest M
  among non-cyclotomic entries of that degree.
- Define error(N) = M_min(N) - M_Lehmer.
- Fit log(error+EPSILON) vs log(N) by linear regression; extract
  slope.
- If slope ≈ -1 (within DECAY_SLOPE_TOLERANCE of -1.0), error decays
  as O(1/N) -> PROMOTED.
- If slope ≈ 0 or positive (no decay or growth), error does not
  decay -> REJECTED with kill_pattern = error_term_does_not_decay.
- If slope is steep-negative (much faster than 1/N), it's not the
  hypothesized 1/N -> REJECTED with kill_pattern = decay_faster_than_1_over_N
  (we observe convergence but at a different rate).
"""
from __future__ import annotations

import math
from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
)


EPSILON = 1e-9  # to handle zero-error degenerate degrees
# Slope tolerance for "≈ -1" classification
DECAY_SLOPE_TOLERANCE = 0.5  # slope in [-1.5, -0.5] counts as O(1/N)
MIN_DEGREES_NEEDED = 5  # need at least this many degrees with M_min > M_Lehmer to fit


def _linear_regression(xs: list[float], ys: list[float]) -> Optional[dict]:
    """OLS slope + intercept; returns None on degenerate input."""
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    slope = num / den
    intercept = my - slope * mx
    # R^2
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    return {"slope": slope, "intercept": intercept, "r_squared": r_squared, "n": n}


def run_g23_lehmer_degree_decay() -> dict:
    """Compute per-degree M_min, fit log(error) vs log(N), classify."""
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }

    # Compute per-degree minimum M
    by_degree: dict[int, float] = {}
    for e in entries:
        deg = e.get("degree")
        m = float(e.get("mahler_measure", 0.0))
        if deg is None or m <= 1.0 + EPSILON:
            continue
        if deg not in by_degree or m < by_degree[deg]:
            by_degree[deg] = m

    # Filter to degrees with positive error (M_min > M_Lehmer)
    points: list[tuple[int, float]] = []
    for deg, m_min in by_degree.items():
        err = m_min - M_LEHMER
        if err > EPSILON:
            points.append((deg, err))
    points.sort()

    if len(points) < MIN_DEGREES_NEEDED:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_degrees_total": len(by_degree),
            "n_degrees_with_positive_error": len(points),
            "notes": (
                f"only {len(points)} degrees have M_min > M_Lehmer "
                f"by more than EPSILON; need >= {MIN_DEGREES_NEEDED} "
                f"for slope fit"
            ),
        }

    # Log-log fit
    xs = [math.log(d) for d, _ in points]
    ys = [math.log(err) for _, err in points]
    fit = _linear_regression(xs, ys)
    if fit is None:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_fit_failed",
            "n_points": len(points),
            "notes": "log-log regression degenerate (zero variance)",
        }

    slope = fit["slope"]
    r2 = fit["r_squared"]

    # Classify
    if abs(slope - (-1.0)) <= DECAY_SLOPE_TOLERANCE:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"Slope = {slope:.4f} (in [-1.5, -0.5]), R^2 = {r2:.4f}. "
            f"Error decays approximately as O(1/N) where N is "
            f"polynomial degree; G23's asymptotic hypothesis is "
            f"empirically consistent with the Mossinghoff per-degree "
            f"minimum-Mahler curve."
        )
    elif slope > -0.5:
        verdict = "REJECTED"
        kp = "error_term_does_not_decay"
        notes = (
            f"Slope = {slope:.4f} > -0.5 (R^2 = {r2:.4f}); error does "
            f"NOT decay as O(1/N). G23's asymptotic hypothesis is "
            f"falsified -- per-degree minimum-Mahler error stays "
            f"roughly constant (or grows) with degree."
        )
    else:
        # slope < -1.5: decay is faster than 1/N
        verdict = "REJECTED"
        kp = "decay_faster_than_1_over_N"
        notes = (
            f"Slope = {slope:.4f} < -1.5 (R^2 = {r2:.4f}); error "
            f"decays FASTER than O(1/N). G23's specific 1/N "
            f"hypothesis is wrong, but a stronger decay law exists "
            f"-- worth investigating the actual exponent."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_points": len(points),
        "n_degrees_total": len(by_degree),
        "slope": round(slope, 4),
        "intercept": round(fit["intercept"], 4),
        "r_squared": round(r2, 4),
        "decay_slope_tolerance": DECAY_SLOPE_TOLERANCE,
        "points_head": [(d, round(e, 6)) for d, e in points[:10]],
        "notes": notes,
    }


class G23LehmerDegreeDecayLoader:
    plugin_id = "g23_asymptotic_limit"
    composition_id = "g23_lehmer_degree_decay"
    description = (
        "Composition loader for EREBOS-G23-* claims in Lehmer context. "
        "Per-degree M_min(N) curve, log-log fit of (M_min - M_Lehmer) "
        "vs N; slope classifies decay law: ≈ -1 -> O(1/N) hypothesis "
        "confirmed; ≈ 0 -> error_term_does_not_decay; steep-negative "
        "-> decay_faster_than_1_over_N."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g23_asymptotic_limit":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        return (
            "BL-C-001" in composed_id
            or "lehmer" in composed_id.lower()
            or "mahler" in composed_id.lower()
            or "lehmer" in rationale
            or "mahler" in rationale
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g23_lehmer_degree_decay()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G23 asymptotic composition: log-log fit of "
                "(M_min(N) - M_Lehmer) vs polynomial degree N, "
                "across Mossinghoff non-cyclotomic catalog. Slope ≈ "
                "-1 confirms O(1/N) decay hypothesis."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; per-degree minimum M; "
                "log-log linear regression."
            ),
            "result": result,
            "notes": (
                "G23 graduates to empirical instrument for Lehmer-"
                "context emissions via the degree-decay law fit."
            ),
        }


register(G23LehmerDegreeDecayLoader())
