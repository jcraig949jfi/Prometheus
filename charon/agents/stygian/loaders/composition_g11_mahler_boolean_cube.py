"""Composition loader: EREBOS-G11-* (Exception-Miner) on Mahler
boolean cube.

Per the G11 plugin spec: hunts the "hidden property H" that
distinguishes a high-kill-cohort's survivors. For Mahler context,
the natural cube is three binary flags on each Mossinghoff entry:
- salem_class           (from catalog)
- is_smyth_extremal     (from catalog)
- degree_is_even        (from the entry's degree)

2^3 = 8 cells. For each cell, count entries and compute survival
fraction at M < SURVIVAL_THRESHOLD (members of the Salem-cluster
bulk count as "survivors"). Chi-squared-style heterogeneity test
on cell-level survival rates discriminates:

- High heterogeneity (chi^2 > CHI2_THRESHOLD): the cube reveals
  cell-level structure -> the survivor population is NOT uniformly
  distributed -> G11's "hidden property H exists" hypothesis is
  empirically supported -> PROMOTED.

- Low heterogeneity (chi^2 <= CHI2_THRESHOLD): the cube does NOT
  reveal hidden structure -> G11 was wrong on this candidate set
  -> REJECTED with kill_pattern = out_of_sample_failure (matches
  plugin's expected_kill_pattern).

We use a heuristic chi^2 threshold rather than a formal p-value
to avoid mishandling sparse cells (chi^2 assumes >=5 expected
per cell; sparse Mahler cells violate this).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    load_non_cyclotomic_mahler_entries,
)


SURVIVAL_THRESHOLD = 1.30  # "survivor" = entry with M < 1.30 (Salem bulk)
CHI2_THRESHOLD = 50.0      # heterogeneity threshold; calibrated empirically
MIN_CELLS_NONEMPTY = 4     # need at least this many non-empty cells to test


def _cube_key(entry: dict) -> tuple[bool, bool, bool]:
    """Boolean cube coordinates: (salem_class, smyth_extremal, deg_even)."""
    return (
        bool(entry.get("salem_class")),
        bool(entry.get("is_smyth_extremal")),
        int(entry.get("degree", 0)) % 2 == 0,
    )


def _chi_squared(observed: list[float], expected: list[float]) -> float:
    """Sum of (O - E)^2 / E across cells. Skip cells with E < 1 to
    avoid degenerate division."""
    total = 0.0
    for o, e in zip(observed, expected):
        if e < 1.0:
            continue
        total += (o - e) ** 2 / e
    return total


def run_g11_mahler_boolean_cube() -> dict:
    """Compute the 2^3 boolean cube + chi^2 heterogeneity score."""
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }

    # Group by cube cell
    cube: dict[tuple, list[float]] = {}
    for e in entries:
        key = _cube_key(e)
        m = float(e.get("mahler_measure", 0.0))
        cube.setdefault(key, []).append(m)

    nonempty = [k for k, v in cube.items() if v]
    if len(nonempty) < MIN_CELLS_NONEMPTY:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_nonempty_cells": len(nonempty),
            "min_cells_needed": MIN_CELLS_NONEMPTY,
            "notes": (
                f"only {len(nonempty)}/8 cube cells populated; need "
                f">= {MIN_CELLS_NONEMPTY} for heterogeneity test"
            ),
        }

    # Total survivor fraction (overall)
    total_n = sum(len(v) for v in cube.values())
    total_survivors = sum(1 for v in cube.values() for m in v if m < SURVIVAL_THRESHOLD)
    overall_rate = total_survivors / total_n if total_n else 0.0

    # Per-cell survival rate + expected-under-null counts
    cells_report = []
    observed_counts = []
    expected_counts = []
    for key, ms in cube.items():
        n_cell = len(ms)
        if n_cell == 0:
            continue
        survivors = sum(1 for m in ms if m < SURVIVAL_THRESHOLD)
        cell_rate = survivors / n_cell
        observed_counts.append(survivors)
        expected_counts.append(overall_rate * n_cell)
        cells_report.append({
            "key": {"salem": key[0], "smyth": key[1], "deg_even": key[2]},
            "n_cell": n_cell,
            "n_survivors": survivors,
            "survival_rate": round(cell_rate, 4),
        })

    chi2 = _chi_squared(observed_counts, expected_counts)

    if chi2 > CHI2_THRESHOLD:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"Cube heterogeneity chi^2 = {chi2:.2f} > {CHI2_THRESHOLD}; "
            f"survivor population is NOT uniformly distributed across "
            f"the (salem, smyth, deg_even) cube. G11's 'hidden "
            f"property H' hypothesis is empirically supported -- the "
            f"binary flags meaningfully stratify Salem-bulk membership."
        )
    else:
        verdict = "REJECTED"
        kp = "out_of_sample_failure"
        notes = (
            f"Cube heterogeneity chi^2 = {chi2:.2f} <= {CHI2_THRESHOLD}; "
            f"survivor distribution is approximately uniform across "
            f"the (salem, smyth, deg_even) cube. G11's hidden-property "
            f"hypothesis on this candidate set is falsified."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_total": total_n,
        "n_total_survivors": total_survivors,
        "overall_survival_rate": round(overall_rate, 4),
        "survival_threshold_M": SURVIVAL_THRESHOLD,
        "n_nonempty_cells": len(nonempty),
        "chi_squared": round(chi2, 4),
        "chi_squared_threshold": CHI2_THRESHOLD,
        "cells": cells_report,
        "notes": notes,
    }


class G11MahlerBooleanCubeLoader:
    plugin_id = "g11_exception_miner"
    composition_id = "g11_mahler_boolean_cube"
    description = (
        "Composition loader for EREBOS-G11-* claims in Mahler context. "
        "Stratifies Mossinghoff catalog by 3 binary flags "
        "(salem_class, is_smyth_extremal, degree_is_even); chi^2 "
        "heterogeneity score on survival rates discriminates PROMOTED "
        "(hidden property exists) vs REJECTED out_of_sample_failure."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g11_exception_miner":
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
        result = run_g11_mahler_boolean_cube()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G11 boolean-cube composition: stratify "
                "Mossinghoff catalog by 3 binary flags; chi^2 "
                "heterogeneity score discriminates hidden-property "
                "presence vs absence."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; (salem_class, is_smyth_"
                "extremal, deg_even) cube."
            ),
            "result": result,
            "notes": (
                "G11 graduates to empirical instrument for Mahler-"
                "context emissions via boolean-cube stratification."
            ),
        }


register(G11MahlerBooleanCubeLoader())
