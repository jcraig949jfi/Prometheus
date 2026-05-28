"""Composition loader v2: EREBOS-G23-* Lehmer degree-decay with
nonparametric bootstrap CI on the log-log slope.

Per Erebos v3 Phase 1A ITER-33 + DR batch 2 convergence (graded
confidence > single point estimate). Replaces v1's hard-tolerance
slope band [-1.5, -0.5] with a bootstrap CI on the slope estimate,
then decides based on CI OVERLAP with the canonical hypothesis
bands rather than a single point estimate.

The brittleness fixed:
- v1 returned PROMOTED iff slope in [-1.5, -0.5]. A single outlier
  degree could flip the verdict.
- v1 emitted a single scalar; nothing about uncertainty crossed
  the seam.
- v1's tolerance band was arbitrarily +/- 0.5 around -1.0; not
  justified by data.

The replacement:
- B=2000 nonparametric bootstrap on the (deg, error) pairs.
- 95% percentile CI on the slope.
- Decision rule (DR-convergent):
  * CI wholly inside [-1.5, -0.5]  -> PROMOTED (decay ~ 1/N
    with high confidence).
  * CI wholly above -0.5           -> REJECTED, kp =
    error_term_does_not_decay_bootstrap.
  * CI wholly below -1.5           -> REJECTED, kp =
    decay_faster_than_1_over_N_bootstrap.
  * CI straddles either boundary   -> UNCERTAIN, kp =
    decay_slope_ci_straddles_boundary.

Doctrine alignment:
- Layer 1: standard nonparametric bootstrap.
- Seam: emits CI band + bootstrap fractions (P(slope < -0.5),
  P(slope < -1.5)) — graded confidence into the kill_ledger.
- Layer 2: kill_pattern `decay_slope_ci_straddles_boundary`
  distinguishes uncertainty-driven non-promotion from a hard
  empirical kill; routes differently.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from charon.agents.stygian.loaders._bootstrap_ci import (
    BootstrapCIResult,
    bootstrap_ci,
)
from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
)


EPSILON = 1e-9
MIN_DEGREES_NEEDED = 5
N_BOOTSTRAP = 2000
CONFIDENCE_LEVEL = 0.95
BOOTSTRAP_SEED = 17  # reproducibility for substrate-internal runs

# Canonical hypothesis bands (slope thresholds in log-log space)
SLOPE_UPPER_BOUND = -0.5   # above -> "no decay"
SLOPE_LOWER_BOUND = -1.5   # below -> "faster than 1/N"
SLOPE_TARGET = -1.0        # canonical O(1/N)


def _log_log_slope(points: Sequence[tuple[int, float]]) -> Optional[float]:
    """OLS slope of log(error) vs log(degree). None on degenerate input."""
    if len(points) < 2:
        return None
    xs = [math.log(d) for d, _ in points]
    ys = [math.log(err) for _, err in points if err > 0]
    if len(ys) != len(xs):  # filter dropped some
        # Recompute coupled pairs
        coupled = [(math.log(d), math.log(e)) for d, e in points if e > 0]
        if len(coupled) < 2:
            return None
        xs = [x for x, _ in coupled]
        ys = [y for _, y in coupled]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return num / den


def _classify_ci(ci: BootstrapCIResult) -> tuple[str, Optional[str], str]:
    """Return (verdict, kill_pattern, decision_note) from CI bounds."""
    if ci.ci_lower is None or ci.ci_upper is None:
        return (
            "UNVERIFIED",
            "stygian_composition_fit_failed",
            "bootstrap produced no valid slope estimates",
        )

    lo, hi = ci.ci_lower, ci.ci_upper

    if lo >= SLOPE_LOWER_BOUND and hi <= SLOPE_UPPER_BOUND:
        return (
            "PROMOTED",
            None,
            f"95% bootstrap CI [{lo:.3f}, {hi:.3f}] entirely inside "
            f"[{SLOPE_LOWER_BOUND}, {SLOPE_UPPER_BOUND}]: O(1/N) decay "
            f"hypothesis empirically supported with bootstrap confidence."
        )
    elif lo > SLOPE_UPPER_BOUND:
        return (
            "REJECTED",
            "error_term_does_not_decay_bootstrap",
            f"95% bootstrap CI [{lo:.3f}, {hi:.3f}] entirely ABOVE "
            f"{SLOPE_UPPER_BOUND}: error does not decay with degree; "
            f"G23's asymptotic hypothesis falsified by bootstrap."
        )
    elif hi < SLOPE_LOWER_BOUND:
        return (
            "REJECTED",
            "decay_faster_than_1_over_N_bootstrap",
            f"95% bootstrap CI [{lo:.3f}, {hi:.3f}] entirely BELOW "
            f"{SLOPE_LOWER_BOUND}: decay is faster than O(1/N); "
            f"G23's specific 1/N hypothesis falsified but a stronger "
            f"law exists."
        )
    else:
        # Straddles either boundary
        return (
            "UNCERTAIN",
            "decay_slope_ci_straddles_boundary",
            f"95% bootstrap CI [{lo:.3f}, {hi:.3f}] straddles the "
            f"canonical band [{SLOPE_LOWER_BOUND}, {SLOPE_UPPER_BOUND}]; "
            f"sample insufficient to commit to a verdict. P(slope > "
            f"{SLOPE_UPPER_BOUND}) = {ci.fraction_above(SLOPE_UPPER_BOUND):.3f}; "
            f"P(slope < {SLOPE_LOWER_BOUND}) = "
            f"{ci.fraction_below(SLOPE_LOWER_BOUND):.3f}."
        )


def run_g23_lehmer_degree_decay_bootstrap() -> dict:
    """Per-degree M_min, bootstrap-CI on log-log slope, decide."""
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }

    by_degree: dict[int, float] = {}
    for e in entries:
        deg = e.get("degree")
        m = float(e.get("mahler_measure", 0.0))
        if deg is None or m <= 1.0 + EPSILON:
            continue
        if deg not in by_degree or m < by_degree[deg]:
            by_degree[deg] = m

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
                f"only {len(points)} degrees with M_min > M_Lehmer "
                f"by more than EPSILON; need >= {MIN_DEGREES_NEEDED}"
            ),
        }

    ci = bootstrap_ci(
        data=points,
        statistic_fn=_log_log_slope,
        n_resamples=N_BOOTSTRAP,
        confidence_level=CONFIDENCE_LEVEL,
        seed=BOOTSTRAP_SEED,
    )

    verdict, kp, decision_note = _classify_ci(ci)

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_points": len(points),
        "n_degrees_total": len(by_degree),
        "slope_observed": (
            round(ci.statistic_observed, 4)
            if ci.statistic_observed is not None else None
        ),
        "slope_ci_lower": (
            round(ci.ci_lower, 4) if ci.ci_lower is not None else None
        ),
        "slope_ci_upper": (
            round(ci.ci_upper, 4) if ci.ci_upper is not None else None
        ),
        "confidence_level": CONFIDENCE_LEVEL,
        "n_bootstrap_resamples": ci.n_resamples,
        "fraction_above_no_decay_bound": round(
            ci.fraction_above(SLOPE_UPPER_BOUND), 4
        ),
        "fraction_below_faster_bound": round(
            ci.fraction_below(SLOPE_LOWER_BOUND), 4
        ),
        "ci_covers_canonical_target": ci.covers(SLOPE_TARGET),
        "slope_target": SLOPE_TARGET,
        "slope_upper_bound": SLOPE_UPPER_BOUND,
        "slope_lower_bound": SLOPE_LOWER_BOUND,
        "points_head": [(d, round(e, 6)) for d, e in points[:10]],
        "bootstrap_seed": BOOTSTRAP_SEED,
        "notes": decision_note,
    }


class G23LehmerDegreeDecayBootstrapLoader:
    plugin_id = "g23_asymptotic_limit"
    composition_id = "g23_lehmer_degree_decay_bootstrap"
    description = (
        "v2 composition loader: nonparametric bootstrap CI on the "
        "log-log slope of (M_min(N) - M_Lehmer) vs N. Replaces v1's "
        "hard-tolerance slope band with graded-confidence CI overlap "
        "decision rule; surfaces uncertainty into the seam."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g23_asymptotic_limit":
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
        is_bootstrap_variant = (
            "bootstrap" in composed_id.lower()
            or "ci" in composed_id.lower().split("_")
            or "v2" in composed_id.lower()
        )
        return is_lehmer and is_bootstrap_variant

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g23_lehmer_degree_decay_bootstrap()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G23 asymptotic composition: nonparametric "
                f"bootstrap CI on log-log slope of (M_min(N) - "
                f"M_Lehmer) vs N; B={N_BOOTSTRAP}; CI overlap with "
                f"[{SLOPE_LOWER_BOUND}, {SLOPE_UPPER_BOUND}] band "
                f"decides verdict."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; per-degree minimum M; "
                "log-log linear regression with nonparametric "
                "bootstrap CI."
            ),
            "result": result,
            "notes": (
                "v3 Phase 1A ITER-33 retrofit. Layer 1 upgrade per "
                "DR batch 2 convergence: bootstrap CI replaces hard "
                "tolerance bands. Sharper G23 -> graded confidence "
                "crosses the seam."
            ),
        }


register(G23LehmerDegreeDecayBootstrapLoader())
