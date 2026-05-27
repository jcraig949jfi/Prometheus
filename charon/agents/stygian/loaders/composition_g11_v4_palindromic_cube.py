"""Composition loader v4: EREBOS-G11-* with palindromic-flag cube.

Per pivot/erebos_substrate_finding_iter13_g11_v2_degree_minima_
concentration_2026-05-26.md follow-up #3: test whether palindromicity
(a structural property derivable from coefficients) is the actually-
causal stratifier of degree-minima, vs Salem-class (a catalog flag).

The cube here is (salem_class, is_smyth_extremal, is_palindromic).
The `is_palindromic` flag is computed from the coefficients vector
directly: a polynomial is palindromic iff coeffs == reverse(coeffs).

Substrate observation (preview): in the Mossinghoff catalog,
palindromic and Salem-class are NEARLY EQUIVALENT binary properties.
99.9% of Salem-class entries are palindromic; 98.8% of non-Salem
entries are NOT palindromic. The cube cells therefore collapse to
essentially the same partition as v2's Salem cube — v4's chi^2 result
will be close to v2's, and the substrate observation is that
palindromicity does NOT add independent discriminating power over
Salem-class in this catalog.

If v4 chi^2 is meaningfully larger than v2 chi^2, palindromicity
captures structure Salem-class misses. If v4 ~ v2, the two flags
are catalog-equivalent.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    load_non_cyclotomic_mahler_entries,
)


CHI2_THRESHOLD_V4 = 10.0
MIN_CELLS_NONEMPTY = 4


def _is_palindromic(coeffs: Optional[list]) -> bool:
    """True iff coefficient list reads the same forwards and backwards
    (no leading/trailing zero stripping). False on empty / missing."""
    if not coeffs:
        return False
    return list(coeffs) == list(reversed(coeffs))


def _cube_key(entry: dict) -> tuple[bool, bool, bool]:
    return (
        bool(entry.get("salem_class")),
        bool(entry.get("is_smyth_extremal")),
        _is_palindromic(entry.get("coeffs")),
    )


def _chi_squared(observed: list[float], expected: list[float]) -> float:
    total = 0.0
    for o, e in zip(observed, expected):
        if e < 0.01:
            continue
        total += (o - e) ** 2 / e
    return total


def run_g11_v4_palindromic_cube() -> dict:
    """v4: chi^2 heterogeneity of degree_minima distribution across
    (salem, smyth, palindromic) cube."""
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }

    cube_total: dict[tuple, int] = {}
    cube_degmin: dict[tuple, int] = {}
    # Also track palindromic-vs-salem cross-tab for the equivalence
    # observation
    pal_x_salem: dict[tuple, int] = {}
    for e in entries:
        key = _cube_key(e)
        cube_total[key] = cube_total.get(key, 0) + 1
        if e.get("degree_minimum"):
            cube_degmin[key] = cube_degmin.get(key, 0) + 1
        cross_key = (bool(e.get("salem_class")), key[2])  # (salem, pal)
        pal_x_salem[cross_key] = pal_x_salem.get(cross_key, 0) + 1

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
    total_degmin = sum(cube_degmin.values())
    if total_degmin == 0:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_no_survivors",
            "n_total": total_n,
            "notes": "no degree_minimum-flagged entries in catalog",
        }
    overall_rate = total_degmin / total_n

    observed_counts = []
    expected_counts = []
    cells_report = []
    for key, n_cell in cube_total.items():
        d_cell = cube_degmin.get(key, 0)
        observed_counts.append(d_cell)
        expected_counts.append(overall_rate * n_cell)
        cells_report.append({
            "key": {"salem": key[0], "smyth": key[1], "palindromic": key[2]},
            "n_cell": n_cell,
            "n_degmin": d_cell,
            "degmin_rate": round(d_cell / n_cell, 6) if n_cell else 0.0,
            "expected_degmin": round(overall_rate * n_cell, 4),
        })

    chi2 = _chi_squared(observed_counts, expected_counts)

    # Palindromic-vs-Salem cross-tab for the equivalence observation
    # cells: (salem=False, pal=False), (salem=False, pal=True),
    # (salem=True,  pal=False), (salem=True,  pal=True)
    n_total_x = sum(pal_x_salem.values())
    pal_implies_salem_rate = 0.0
    if n_total_x > 0:
        n_pal_and_salem = pal_x_salem.get((True, True), 0)
        n_pal = pal_x_salem.get((True, True), 0) + pal_x_salem.get((False, True), 0)
        pal_implies_salem_rate = (n_pal_and_salem / n_pal) if n_pal > 0 else 0.0

    if chi2 > CHI2_THRESHOLD_V4:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"v4 chi^2 = {chi2:.2f} > {CHI2_THRESHOLD_V4}; degree-minima "
            f"are NOT uniformly distributed across (salem, smyth, "
            f"palindromic) cube. Palindromic-vs-Salem cross-tab: "
            f"P(salem | palindromic) = {pal_implies_salem_rate:.4f}. "
            f"If this rate is near 1.0, palindromic and Salem are "
            f"catalog-equivalent and v4 essentially re-runs v2's "
            f"finding. If meaningfully different, palindromicity "
            f"adds independent stratification structure."
        )
    else:
        verdict = "REJECTED"
        kp = "out_of_sample_failure"
        notes = (
            f"v4 chi^2 = {chi2:.2f} <= {CHI2_THRESHOLD_V4}; palindromic-"
            f"flag cube does NOT reveal hidden structure. Salem-vs-"
            f"palindromic equivalence: P(salem | palindromic) = "
            f"{pal_implies_salem_rate:.4f}."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "criterion": "palindromic-flag cube + degree_minimum survival",
        "n_total": total_n,
        "n_total_survivors": total_degmin,
        "overall_survival_rate": round(overall_rate, 6),
        "n_nonempty_cells": len(nonempty),
        "chi_squared": round(chi2, 4),
        "chi_squared_threshold": CHI2_THRESHOLD_V4,
        "pal_implies_salem_rate": round(pal_implies_salem_rate, 4),
        "pal_x_salem_crosstab": {
            f"salem={int(k[0])}_pal={int(k[1])}": v
            for k, v in pal_x_salem.items()
        },
        "cells": cells_report,
        "notes": notes,
    }


class G11V4PalindromicCubeLoader:
    plugin_id = "g11_exception_miner"
    composition_id = "g11_v4_palindromic_cube"
    description = (
        "Composition loader v4 for EREBOS-G11-* claims in Mahler "
        "context. Cube = (salem, smyth, palindromic) where "
        "palindromic is derived from coefficients vector. Tests "
        "whether palindromicity adds independent structure over v2's "
        "Salem cube, or is catalog-equivalent to Salem-class."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g11_exception_miner":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        if not ("BL-C-001" in composed_id or "lehmer" in composed_id.lower()
                or "mahler" in composed_id.lower()):
            return False
        return "v4" in composed_id.lower() or "palindromic" in composed_id.lower()

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g11_v4_palindromic_cube()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G11 v4 boolean-cube composition: cube = "
                "(salem, smyth, palindromic); palindromic computed "
                "from coefficients vector directly."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; coefficients-derived "
                "palindromic flag."
            ),
            "result": result,
            "notes": (
                "G11 v4 tests whether palindromicity adds independent "
                "structure to v2's Salem cube; the pal_implies_salem_"
                "rate reports the strength of palindromic-vs-Salem "
                "equivalence in the catalog."
            ),
        }


register(G11V4PalindromicCubeLoader())
