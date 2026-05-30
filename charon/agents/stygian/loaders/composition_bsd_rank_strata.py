"""Composition loader: BSD rank-stratified regulator scaling (ITER-61).

Second BSD-domain Layer-1 detector. For curves stratified by rank
(0, 1, 2, 3+), fit log(regulator) vs log(conductor) via bootstrap
CI on the slope. Per Lang's conjecture, regulator should scale
weakly with conductor (positive but small slope).

The output is per-rank-stratum; each stratum is its own emission.
Provides BSD-domain ledger rows with KP variation across strata.
"""
from __future__ import annotations

import math

from charon.agents.stygian.loaders._bootstrap_ci import bootstrap_ci
from charon.agents.stygian.loaders._bsd_helpers import (
    MIN_BSD_SAMPLE_SIZE,
    get_conductor,
    get_rank,
    get_regulator,
    load_bsd_entries,
)
from charon.agents.stygian.loaders._composition import register


N_BOOTSTRAP = 1000
CONFIDENCE_LEVEL = 0.95
SEED = 1101


def _log_log_slope(points):
    if len(points) < 3:
        return None
    xs = [math.log(c) for c, _ in points if c > 0]
    ys = [math.log(r) for _, r in points if r > 0]
    if len(xs) != len(ys) or len(xs) < 3:
        # fall back to coupled filter
        coupled = [(math.log(c), math.log(r)) for c, r in points
                    if c > 0 and r > 0]
        if len(coupled) < 3:
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


def run_bsd_rank_stratum(rank_filter: int) -> dict:
    """Run scaling test on the rank-`rank_filter` stratum
    (rank_filter=0/1/2; rank_filter=3 means rank>=3)."""
    entries = load_bsd_entries()
    if len(entries) < MIN_BSD_SAMPLE_SIZE:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "bsd_composition_data_load_failed",
            "n_entries": len(entries),
            "stratum": f"rank={rank_filter}",
        }
    if rank_filter < 3:
        in_stratum = [e for e in entries if get_rank(e) == rank_filter]
    else:
        in_stratum = [e for e in entries if (get_rank(e) or 0) >= 3]
    points = [
        (get_conductor(e), get_regulator(e))
        for e in in_stratum
        if get_conductor(e) is not None and get_regulator(e) is not None
        and get_regulator(e) > 0
    ]
    if len(points) < MIN_BSD_SAMPLE_SIZE:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "bsd_rank_stratum_too_small",
            "n_stratum_entries": len(in_stratum),
            "n_valid_points": len(points),
            "stratum": f"rank={rank_filter}",
        }
    ci = bootstrap_ci(
        data=points,
        statistic_fn=_log_log_slope,
        n_resamples=N_BOOTSTRAP,
        confidence_level=CONFIDENCE_LEVEL,
        seed=SEED + rank_filter,
    )
    if ci.statistic_observed is None or ci.ci_lower is None:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "bsd_rank_stratum_slope_fit_failed",
            "stratum": f"rank={rank_filter}",
        }
    slope = ci.statistic_observed
    lo, hi = ci.ci_lower, ci.ci_upper

    # Decision by CI position
    if lo > 0:
        verdict = "PROMOTED"
        kp = f"bsd_regulator_grows_with_conductor_rank{rank_filter}"
        notes = (
            f"Positive scaling: rank={rank_filter} stratum slope = "
            f"{slope:.4f}, CI = [{lo:.4f}, {hi:.4f}] entirely above 0."
        )
    elif hi < 0:
        verdict = "REJECTED"
        kp = f"bsd_regulator_shrinks_with_conductor_rank{rank_filter}"
        notes = (
            f"Negative scaling (Lang violated?): rank={rank_filter} "
            f"slope = {slope:.4f}, CI = [{lo:.4f}, {hi:.4f}] entirely "
            f"below 0."
        )
    else:
        verdict = "REJECTED"
        kp = f"bsd_regulator_independent_of_conductor_rank{rank_filter}"
        notes = (
            f"CI straddles zero: rank={rank_filter} slope = "
            f"{slope:.4f}, CI = [{lo:.4f}, {hi:.4f}]; insufficient "
            f"evidence regulator scales with conductor in this stratum."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_stratum_entries": len(in_stratum),
        "n_valid_points": len(points),
        "stratum": f"rank={rank_filter}",
        "slope_observed": round(slope, 4),
        "ci_lower": round(lo, 4) if lo is not None else None,
        "ci_upper": round(hi, 4) if hi is not None else None,
        "n_bootstrap": ci.n_resamples,
        "notes": notes,
    }


class BSDRankStratumLoader:
    plugin_id = "g23_asymptotic_limit"  # reuse asymptotic semantics
    composition_id = "bsd_rank_stratified_regulator_scaling"
    description = (
        "BSD rank-stratified regulator scaling Layer-1 detector. "
        "Bootstrap CI on log-log slope per stratum."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g23_asymptotic_limit":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        return (
            "bsd" in composed_id.lower()
            and "rank" in composed_id.lower()
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        # Default: rank=0 stratum
        result = run_bsd_rank_stratum(0)
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": queue_payload.get("erebos_composed_id", "?"),
            "claim": (
                "BSD rank-stratified Layer-1 detector: bootstrap CI "
                "on log-log slope of regulator vs conductor."
            ),
            "data_source": "prometheus_math.databases.bsd_rich",
            "domain": "BSD",
            "result": result,
        }


register(BSDRankStratumLoader())
