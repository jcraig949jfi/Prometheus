"""Composition loader: EREBOS-G03-* (Failure-Neighborhood) on
Lehmer-context parents.

Per pivot/erebos_g03_failure_neighborhood_research_2026-05-26.md +
the G03 plugin's Tier B feasibility note. The plugin weakens an
arithmetic operator one rank down the ladder; this loader tests
the weakened claim on the Mossinghoff catalog and measures whether
the weakened form is empirically meaningful (a real constraint) or
trivially satisfied (boundary_collapse).

Concrete Lehmer-context test (v0.14 MVP):
- Original parent claim form: "M(P) = M_Lehmer" or "M(P) >= M_Lehmer"
  (strict equality / strict inequality).
- Weakened form: "M(P) within tolerance epsilon of M_Lehmer" (epsilon-
  band substitution).
- Measurement: fraction of Mossinghoff non-cyclotomic entries with
  M in [M_Lehmer - epsilon, M_Lehmer + epsilon] for epsilon =
  EPSILON_BAND.

Decision rule:
- If trivial_fraction >= TRIVIAL_THRESHOLD (e.g., >= 0.95): the
  weakened form catches essentially every polynomial -> kill_pattern =
  boundary_collapse (G03's weakening was too permissive; the new
  predicate is vacuous).
- If trivial_fraction in (NEGLIGIBLE_THRESHOLD, TRIVIAL_THRESHOLD):
  the weakened form is a real constraint that catches a measurable
  fraction -> PROMOTED (G03's weakening yields a non-trivial
  predicate worth investigating further).
- If trivial_fraction <= NEGLIGIBLE_THRESHOLD: the band is so narrow
  it catches almost nothing -> REJECTED with kill_pattern =
  weakening_too_strict (the relaxation didn't relax enough; G03's
  one-step weakening was insufficient).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
)


EPSILON_BAND = 0.05  # epsilon for the weakened "M within epsilon of M_Lehmer" form
TRIVIAL_THRESHOLD = 0.95
NEGLIGIBLE_THRESHOLD = 0.02
MIN_SAMPLE_SIZE = 100


def _fraction_in_band(values: list[float], lo: float, hi: float) -> float:
    if not values:
        return 0.0
    return sum(1 for v in values if lo <= v <= hi) / len(values)


def run_g03_lehmer_neighborhood() -> dict:
    """Test the epsilon-band weakening on the Mossinghoff catalog.
    Returns the result dict the executor consumes."""
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
    lo = M_LEHMER - EPSILON_BAND
    hi = M_LEHMER + EPSILON_BAND
    trivial_fraction = _fraction_in_band(values, lo, hi)

    if trivial_fraction >= TRIVIAL_THRESHOLD:
        verdict = "REJECTED"
        kp = "boundary_collapse"
        notes = (
            f"fraction in epsilon-band [{lo:.4f}, {hi:.4f}] = "
            f"{trivial_fraction:.4f} >= {TRIVIAL_THRESHOLD}; G03's "
            f"weakening was too permissive (the new predicate is "
            f"essentially universal). kill_pattern=boundary_collapse."
        )
    elif trivial_fraction <= NEGLIGIBLE_THRESHOLD:
        verdict = "REJECTED"
        kp = "weakening_too_strict"
        notes = (
            f"fraction in epsilon-band [{lo:.4f}, {hi:.4f}] = "
            f"{trivial_fraction:.4f} <= {NEGLIGIBLE_THRESHOLD}; G03's "
            f"one-step weakening still catches almost nothing. The "
            f"original was rejected because it was a near-tautology "
            f"of impossibility, not because of operator strictness."
        )
    else:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"fraction in epsilon-band [{lo:.4f}, {hi:.4f}] = "
            f"{trivial_fraction:.4f}, in non-trivial range "
            f"({NEGLIGIBLE_THRESHOLD}, {TRIVIAL_THRESHOLD}); G03's "
            f"weakening produced an empirically meaningful predicate. "
            f"Worth investigating which Mossinghoff entries land in "
            f"the band and what structural property they share."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "epsilon_band": EPSILON_BAND,
        "band_lo": round(lo, 6),
        "band_hi": round(hi, 6),
        "trivial_fraction": round(trivial_fraction, 4),
        "trivial_threshold": TRIVIAL_THRESHOLD,
        "negligible_threshold": NEGLIGIBLE_THRESHOLD,
        "n_sample": len(values),
        "notes": notes,
    }


class G03LehmerNeighborhoodLoader:
    plugin_id = "g03_failure_neighborhood"
    composition_id = "g03_lehmer_neighborhood"
    description = (
        "Composition loader for EREBOS-G03-* claims whose parent "
        "is BL-C-001 Lehmer. Tests the epsilon-band weakening: "
        "fraction of Mossinghoff entries with M in [M_Lehmer +/- "
        "EPSILON_BAND] -> boundary_collapse vs PROMOTED vs "
        "weakening_too_strict."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g03_failure_neighborhood":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        # Match Lehmer-context emissions via composed_id or rationale
        return (
            "BL-C-001" in composed_id
            or "lehmer" in composed_id.lower()
            or "lehmer" in rationale
            or "mahler" in rationale
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g03_lehmer_neighborhood()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G03 neighborhood composition: weaken Lehmer-"
                f"context arithmetic predicate to epsilon-band "
                f"(M within +/-{EPSILON_BAND} of M_Lehmer); measure "
                f"whether the weakened form is trivial / non-trivial / "
                f"still-empty on the Mossinghoff catalog."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; epsilon-band sweep around "
                "M_Lehmer."
            ),
            "result": result,
            "notes": (
                "G03 graduates to empirical instrument for Lehmer-"
                "context emissions. Other domains' G03 emissions stay "
                "unfalsifiable until per-domain weakening tests ship."
            ),
        }


register(G03LehmerNeighborhoodLoader())
