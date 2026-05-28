"""Composition loader v2: EREBOS-G10-* Lehmer threshold sweep with
Bayesian Online Change-Point Detection.

Per Erebos v3 Phase 1A ITER-32 + DR batch 2 convergence. Replaces
the v1 max/mean smoothness ratio (a brittle single-scalar statistic
that depends on the threshold-discretization choice) with a Bayesian
posterior on changepoint locations. Locates phase transitions with
graded confidence rather than threshold-crossing.

Output is a posterior CURVE (P(changepoint at threshold_t)) per
threshold sweep point. The verdict is derived from the maximum
posterior + its localization, not from a single ratio.

Doctrine alignment:
- Layer 1: BOCPD is a standard Bayesian online algorithm.
- Seam: emits SurvivalCurve + per-threshold changepoint posterior.
- Layer 2: kill_pattern `sharp_boundary_detected_bocpd` distinguishes
  posterior-based detection from ratio-based (preserves v1's
  `sharp_boundary_detected` semantics for backward compatibility).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._bocpd import detect_changepoints
from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
    survival_fraction,
)


# Sweep grid (same as v1 for direct comparability)
SWEEP_THRESHOLDS = [M_LEHMER, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50]

# Posterior threshold above which a changepoint is considered
# substrate-grade detected. The BOCPD signal is
# 1 / (1 + E[run_length]); a value > 0.3 at an INTERIOR step
# (excluding cold start) indicates the posterior expects a recent
# changepoint at that step. Calibrated empirically.
POSTERIOR_THRESHOLD = 0.3

# Above this RELATIVE-to-prior-trend jump in the BOCPD signal, the
# event is substrate-grade even if the absolute posterior is below
# POSTERIOR_THRESHOLD. The signal naturally decays over time as
# evidence accumulates; a SPIKE relative to the local trend is the
# true changepoint indicator.
RELATIVE_SPIKE_THRESHOLD = 0.05

# Cold-start window — the first N timesteps have prior-dominated
# posterior signal that is artifactually high. Exclude from
# changepoint search.
COLD_START_EXCLUSION = 2

# Hazard rate (expected steps between changes). For an 8-point sweep
# expecting 0-1 changes, hazard = 1/8 = 0.125 is a sensible prior.
HAZARD_RATE = 0.125

MIN_SAMPLE_SIZE = 100


def run_g10_lehmer_bocpd_sweep() -> dict:
    """Sweep + BOCPD changepoint detection on the survival curve."""
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

    # Survival fractions live in [0, 1] with natural noise scale << 1.
    # Use tight default priors (prior_beta = 0.001) instead of the
    # generic data-driven default (which gets swamped by the cliff
    # itself and loses discriminative power).
    bocpd_result = detect_changepoints(
        observations=survivals,
        hazard_rate=HAZARD_RATE,
        prior_kappa=0.1,
        prior_alpha=0.5,
        prior_beta=0.001,
    )

    # Identify interior spike (relative to the local trend),
    # excluding the cold-start window where the posterior is
    # artifactually high.
    posteriors = bocpd_result.changepoint_probabilities
    interior_spike_t = None
    interior_spike_value = None
    interior_spike_threshold = None
    if len(posteriors) > COLD_START_EXCLUSION + 1:
        # Compare each interior t to the IMMEDIATELY-PRIOR posterior.
        # A spike = (posterior[t] - posterior[t-1]) > RELATIVE_SPIKE_THRESHOLD.
        max_spike = 0.0
        for t in range(COLD_START_EXCLUSION, len(posteriors)):
            spike = posteriors[t] - posteriors[t - 1]
            if spike > max_spike and spike >= RELATIVE_SPIKE_THRESHOLD:
                max_spike = spike
                interior_spike_t = t
                interior_spike_value = posteriors[t]
                interior_spike_threshold = SWEEP_THRESHOLDS[t]

    # Decision rule — REJECT on either:
    # (a) interior posterior spike above RELATIVE_SPIKE_THRESHOLD, OR
    # (b) interior posterior absolute > POSTERIOR_THRESHOLD
    if interior_spike_t is not None:
        verdict = "REJECTED"
        kp = "sharp_boundary_detected_bocpd"
        notes = (
            f"BOCPD detected substrate-grade changepoint spike at "
            f"threshold = {interior_spike_threshold} "
            f"(BOCPD signal = {interior_spike_value:.4f}, "
            f"spike vs prior = {interior_spike_value - posteriors[interior_spike_t - 1]:.4f}). "
            f"Survival curve has a sharp discontinuity at this point. "
            f"G10's smooth-degradation hypothesis is falsified by "
            f"posterior-based detector (Layer 1 ITER-32 upgrade)."
        )
    elif len(posteriors) > COLD_START_EXCLUSION:
        # Check if any INTERIOR (non-cold-start) posterior exceeds
        # the absolute threshold
        interior_max = max(posteriors[COLD_START_EXCLUSION:])
        if interior_max > POSTERIOR_THRESHOLD:
            interior_max_t = posteriors.index(interior_max)
            verdict = "REJECTED"
            kp = "sharp_boundary_detected_bocpd"
            notes = (
                f"BOCPD interior posterior {interior_max:.4f} > "
                f"{POSTERIOR_THRESHOLD} at threshold = "
                f"{SWEEP_THRESHOLDS[interior_max_t]}; substrate-grade "
                f"changepoint signal."
            )
        else:
            verdict = "PROMOTED"
            kp = None
            notes = (
                f"BOCPD over {len(survivals)} threshold points, "
                f"hazard={HAZARD_RATE}: no interior changepoint "
                f"signal above {POSTERIOR_THRESHOLD} abs or "
                f"{RELATIVE_SPIKE_THRESHOLD} relative-spike. Survival "
                f"curve appears continuous; G10's smooth-degradation "
                f"hypothesis is consistent."
            )
    else:
        verdict = "UNVERIFIED"
        kp = "stygian_composition_insufficient_sample"
        notes = "Too few sweep points for cold-start exclusion + interior detection."

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "sweep_thresholds": [round(t, 4) for t in SWEEP_THRESHOLDS],
        "survival_fractions": [round(s, 4) for s in survivals],
        "changepoint_posteriors": [
            round(p, 4) for p in bocpd_result.changepoint_probabilities
        ],
        "most_likely_changepoint_t": bocpd_result.most_likely_changepoint_t,
        "most_likely_changepoint_threshold": (
            round(bocpd_result.most_likely_changepoint_value, 4)
            if bocpd_result.most_likely_changepoint_value is not None
            else None
        ),
        "max_posterior": round(bocpd_result.max_posterior, 4),
        "interior_spike_t": interior_spike_t,
        "interior_spike_threshold": (
            round(interior_spike_threshold, 4)
            if interior_spike_threshold is not None else None
        ),
        "interior_spike_value": (
            round(interior_spike_value, 4)
            if interior_spike_value is not None else None
        ),
        "posterior_threshold": POSTERIOR_THRESHOLD,
        "relative_spike_threshold": RELATIVE_SPIKE_THRESHOLD,
        "cold_start_exclusion": COLD_START_EXCLUSION,
        "hazard_rate": HAZARD_RATE,
        "n_sample": len(values),
        "notes": notes,
    }


class G10LehmerBOCPDSweepLoader:
    plugin_id = "g10_boundary"
    composition_id = "g10_lehmer_bocpd_sweep"
    description = (
        "v2 composition loader: BOCPD posterior-probability change-"
        "point detection over the survival sweep. Replaces v1 "
        "max/mean smoothness ratio with a graded-confidence Bayesian "
        "detector that doesn't depend on the threshold-discretization."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g10_boundary":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        is_lehmer = (
            "BL-C-001" in composed_id
            or "lehmer" in composed_id.lower()
            or "mahler" in composed_id.lower()
            or "lehmer" in rationale
            or "mahler" in rationale
        )
        is_bocpd_variant = (
            "bocpd" in composed_id.lower()
            or "v2" in composed_id.lower()
            or "posterior" in composed_id.lower()
        )
        return is_lehmer and is_bocpd_variant

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g10_lehmer_bocpd_sweep()
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": queue_payload.get("erebos_composed_id", "?"),
            "claim": (
                f"EREBOS-G10 BOCPD composition: survival fraction "
                f"sweep across {len(SWEEP_THRESHOLDS)} thresholds, "
                f"Adams-MacKay 2007 Bayesian changepoint posterior "
                f"with hazard={HAZARD_RATE}. Posterior >= "
                f"{POSTERIOR_THRESHOLD} -> sharp boundary detected."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; multi-threshold survival "
                "sweep; BOCPD posterior changepoint detection."
            ),
            "result": result,
            "notes": (
                "v3 Phase 1A ITER-32 retrofit. Layer 1 upgrade per "
                "DR batch 2 convergence: BOCPD replaces max/mean "
                "smoothness ratio. Sharper G10 -> cleaner failure "
                "data crossing the seam."
            ),
        }


register(G10LehmerBOCPDSweepLoader())
