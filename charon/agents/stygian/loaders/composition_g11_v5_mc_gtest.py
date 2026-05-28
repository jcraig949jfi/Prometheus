"""Composition loader v5: EREBOS-G11-* Mahler boolean-cube via
G-test + Monte-Carlo permutation null.

Per Erebos v3 Phase 1A ITER-34 + DR batch 2 convergence (calibrated
p-values > asymptotic chi^2 with hardcoded threshold). v2 used
Pearson chi^2 with threshold=10.0; brittle because only ~8
degree_minimum-flagged entries exist across 8 cube cells, and
asymptotic chi^2 is unreliable at those expected counts.

v5 replacement:
- G-test (log-likelihood-ratio) statistic instead of Pearson chi^2.
  Better small-sample behavior; same null hypothesis (independence
  of flag from cube cell).
- Monte-Carlo permutation null: shuffle the degree_minimum flag
  across all catalog entries (preserves marginal totals + cell
  sizes), recompute G, repeat B=2000 times. Empirical p-value =
  fraction of null G values >= observed G.
- Decision rule by calibrated p-value:
  * p_MC < 0.01 -> PROMOTED (substrate-grade structure)
  * 0.01 <= p_MC < 0.05 -> PROMOTED with kp= (none) but seam-flagged
  * p_MC >= 0.05 -> REJECTED kp=flag_distribution_uniform_under_mc_null

Doctrine alignment:
- Layer 1: G-test + permutation null are textbook tools.
- Seam: emits empirical p-value + null G distribution shape
  (not a single ratio), so downstream can re-decide at any
  significance level.
- Layer 2: kill_pattern flag_distribution_uniform_under_mc_null
  distinguishes "structure absent under permutation" from v2's
  "chi^2 below 10" (which was an arbitrary threshold).
"""
from __future__ import annotations

import math
import random
from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    load_non_cyclotomic_mahler_entries,
)


MIN_CELLS_NONEMPTY = 4
N_MC_PERMUTATIONS = 2000
MC_SEED = 23  # reproducibility for substrate-internal runs
ALPHA_PROMOTE = 0.05  # calibrated p-value threshold


def _cube_key(entry: dict) -> tuple[bool, bool, bool]:
    return (
        bool(entry.get("salem_class")),
        bool(entry.get("is_smyth_extremal")),
        int(entry.get("degree", 0)) % 2 == 0,
    )


def _g_statistic(
    cube_total: dict[tuple, int],
    cube_survivors: dict[tuple, int],
    overall_rate: float,
) -> float:
    """G = 2 * sum O * ln(O / E), with O*ln(O/E) := 0 when O=0.
    Skips cells with expected < 1e-9 (degenerate)."""
    g = 0.0
    for key, n_cell in cube_total.items():
        observed = cube_survivors.get(key, 0)
        expected = overall_rate * n_cell
        if expected < 1e-9:
            continue
        if observed <= 0:
            continue  # 0 * log(0/E) = 0 by convention
        g += 2.0 * observed * math.log(observed / expected)
    return g


def run_g11_v5_mc_gtest() -> dict:
    """G-test on degree_minimum distribution across the cube, with
    Monte-Carlo permutation null."""
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }

    # Build per-entry (cube_key, flag) records (no need to retain entry
    # itself for the permutation null; cube_key per entry is what
    # matters).
    records: list[tuple[tuple, bool]] = []
    for e in entries:
        records.append((_cube_key(e), bool(e.get("degree_minimum"))))

    cube_total: dict[tuple, int] = {}
    cube_survivors: dict[tuple, int] = {}
    for key, flag in records:
        cube_total[key] = cube_total.get(key, 0) + 1
        if flag:
            cube_survivors[key] = cube_survivors.get(key, 0) + 1

    nonempty = [k for k, v in cube_total.items() if v]
    if len(nonempty) < MIN_CELLS_NONEMPTY:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_nonempty_cells": len(nonempty),
            "notes": (
                f"only {len(nonempty)}/8 cube cells populated; need "
                f">= {MIN_CELLS_NONEMPTY}"
            ),
        }

    total_n = sum(cube_total.values())
    total_survivors = sum(cube_survivors.values())
    if total_survivors == 0:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_no_survivors",
            "n_total": total_n,
            "n_survivors": 0,
            "notes": "no degree_minimum-flagged entries in catalog",
        }
    overall_rate = total_survivors / total_n

    # Observed G
    g_observed = _g_statistic(cube_total, cube_survivors, overall_rate)

    # Per-cell report
    cells_report = []
    for key in sorted(cube_total.keys()):
        n_cell = cube_total[key]
        d_cell = cube_survivors.get(key, 0)
        cells_report.append({
            "key": {"salem": key[0], "smyth": key[1], "deg_even": key[2]},
            "n_cell": n_cell,
            "n_survivors": d_cell,
            "survivor_rate": (
                round(d_cell / n_cell, 6) if n_cell else 0.0
            ),
            "expected_under_null": round(overall_rate * n_cell, 4),
        })

    # Monte-Carlo permutation null: shuffle the flag across all
    # records (preserves total_survivors + cube_total marginals),
    # recompute G per permutation.
    rng = random.Random(MC_SEED)
    flag_pool: list[bool] = [flag for _, flag in records]
    cube_keys_per_record: list[tuple] = [key for key, _ in records]

    null_g_distribution: list[float] = []
    for _ in range(N_MC_PERMUTATIONS):
        rng.shuffle(flag_pool)
        null_survivors: dict[tuple, int] = {}
        for k, f in zip(cube_keys_per_record, flag_pool):
            if f:
                null_survivors[k] = null_survivors.get(k, 0) + 1
        g_null = _g_statistic(cube_total, null_survivors, overall_rate)
        null_g_distribution.append(g_null)

    # Empirical p-value: fraction of null G >= observed G
    # (one-sided, since we test for excess heterogeneity)
    n_at_or_above = sum(1 for g in null_g_distribution if g >= g_observed)
    p_value_mc = n_at_or_above / N_MC_PERMUTATIONS

    # Quantiles for the seam
    null_sorted = sorted(null_g_distribution)
    def _percentile(p):
        idx = p * (len(null_sorted) - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return null_sorted[lo]
        frac = idx - lo
        return null_sorted[lo] * (1 - frac) + null_sorted[hi] * frac

    null_p50 = _percentile(0.50)
    null_p95 = _percentile(0.95)
    null_p99 = _percentile(0.99)

    if p_value_mc < ALPHA_PROMOTE:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"G-test G = {g_observed:.4f}; Monte-Carlo permutation "
            f"p-value = {p_value_mc:.4f} (over {N_MC_PERMUTATIONS} "
            f"shuffles, null G p95={null_p95:.4f}, p99={null_p99:.4f}). "
            f"Degree-minima are NOT uniformly distributed across "
            f"(salem, smyth, deg_even); G11's hidden-property "
            f"hypothesis is supported with a calibrated p-value "
            f"(no asymptotic-chi^2 assumption)."
        )
    else:
        verdict = "REJECTED"
        kp = "flag_distribution_uniform_under_mc_null"
        notes = (
            f"G-test G = {g_observed:.4f}; Monte-Carlo permutation "
            f"p-value = {p_value_mc:.4f} >= {ALPHA_PROMOTE} (over "
            f"{N_MC_PERMUTATIONS} shuffles, null G p95={null_p95:.4f}, "
            f"p99={null_p99:.4f}). Degree-minima distribution is "
            f"consistent with cube-independent uniform; G11's "
            f"hidden-property hypothesis is not supported at this "
            f"calibration."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "criterion": "degree_minimum flag G-test with MC permutation null",
        "n_total": total_n,
        "n_total_survivors": total_survivors,
        "overall_survival_rate": round(overall_rate, 6),
        "n_nonempty_cells": len(nonempty),
        "g_statistic_observed": round(g_observed, 4),
        "p_value_mc": round(p_value_mc, 4),
        "null_g_p50": round(null_p50, 4),
        "null_g_p95": round(null_p95, 4),
        "null_g_p99": round(null_p99, 4),
        "n_mc_permutations": N_MC_PERMUTATIONS,
        "mc_seed": MC_SEED,
        "alpha_promote": ALPHA_PROMOTE,
        "cells": cells_report,
        "notes": notes,
    }


class G11V5McGtestLoader:
    plugin_id = "g11_exception_miner"
    composition_id = "g11_v5_mc_gtest"
    description = (
        "v5 composition loader: G-test statistic + Monte-Carlo "
        "permutation null on degree_minimum cube distribution. "
        "Replaces v2's Pearson chi^2 + hardcoded threshold with a "
        "calibrated empirical p-value that doesn't rely on asymptotic "
        "chi^2 (essential when expected counts are small)."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g11_exception_miner":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        if not (
            "BL-C-001" in composed_id
            or "lehmer" in composed_id.lower()
            or "mahler" in composed_id.lower()
        ):
            return False
        # v5 fires when the composed_id mentions "v5", "gtest", or "mc"
        lower = composed_id.lower()
        return any(
            marker in lower for marker in ("v5", "gtest", "g_test", "mc_null", "mc_gtest")
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g11_v5_mc_gtest()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G11 v5 boolean-cube composition: G-test "
                f"with Monte-Carlo permutation null (B="
                f"{N_MC_PERMUTATIONS}, alpha={ALPHA_PROMOTE}) on "
                f"degree_minimum distribution across (salem, smyth, "
                f"deg_even) cube. Calibrated p-value, no asymptotic "
                f"chi^2 assumption."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; degree_minimum flag as "
                "survival; (salem, smyth, deg_even) as cube; G-test "
                "+ permutation null."
            ),
            "result": result,
            "notes": (
                "v3 Phase 1A ITER-34 retrofit. Layer 1 upgrade per "
                "DR batch 2 convergence: G-test + MC null replaces "
                "Pearson chi^2 + hardcoded threshold. Sharper G11 "
                "-> calibrated p-value crosses the seam."
            ),
        }


register(G11V5McGtestLoader())
