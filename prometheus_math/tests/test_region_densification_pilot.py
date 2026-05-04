"""Tests for prometheus_math.region_densification_pilot.

Math-tdd skill rubric: ≥3 each in authority/property/edge/composition.

The densification pilot reuses ``native_kill_vector_pilot``'s emission
infrastructure but parameterizes the region cell.  Tests focus on:

  * Authority: the 4 region cells run; per-region records are well-formed;
    KillVector emission works in all 4 cells.
  * Property: determinism with fixed seed; episode count per cell = 1K;
    region metadata correctly tagged on each record.
  * Edge: degenerate region (degree=10 ±3 → smaller search space);
    zero-budget cell handled; mismatched config caught.
  * Composition: pilot → analysis → coverage update end-to-end;
    navigator now has 6 regions; per-region recommendations are well-formed.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path

import numpy as np
import pytest

from prometheus_math.kill_vector import KillVector
from prometheus_math.region_densification_pilot import (
    CELL_ALGORITHM_RUNNERS,
    DEFAULT_REGION_CELLS,
    RegionCell,
    compare_with_baseline,
    main,
    per_region_operator_margins,
    run_densification,
    _run_ga_elitist_cell,
    _run_random_uniform_cell,
    _run_reinforce_cell,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


class TestAuthority:
    """Authority: pilot covers all 4 region cells; records are well-formed;
    KillVector emission works in all 4 cells."""

    def test_authority_default_cells_match_spec(self):
        """Authority: the 4 default cells exactly match the spec's
        densification target (deg10 ±5, deg12 ±5, deg10 ±3, deg14 ±3,
        all reward_shape=step)."""
        cell_ids = sorted(c.cell_id for c in DEFAULT_REGION_CELLS)
        assert cell_ids == sorted([
            "deg10_w5_step",
            "deg12_w5_step",
            "deg10_w3_step",
            "deg14_w3_step",
        ])
        for c in DEFAULT_REGION_CELLS:
            assert c.reward_shape == "step"
            assert c.alphabet_width in (3, 5)
            assert c.degree in (10, 12, 14)
            assert c.alphabet_size == 2 * c.alphabet_width + 1

    def test_authority_pilot_covers_all_4_cells_with_records(self):
        """Authority: a tiny end-to-end run produces records for every
        (cell × algorithm × seed) tuple, with per-cell summary present."""
        r = run_densification(
            cells=DEFAULT_REGION_CELLS,
            n_episodes_per_cell=2,
            seeds=(0,),
            algorithms=("random_uniform",),  # Just one algo for speed
            progress=False,
        )
        # 4 cells × 1 algo × 1 seed = 4 cell-summary entries
        assert len(r["cell_summary"]) == 4
        # Total episodes = 4 cells × 1 algo × 1 seed × 2 episodes = 8
        assert r["total_episodes"] == 8
        # Every cell has at least 1 episode
        cell_ids_seen = {info["cell_id"] for info in r["cell_summary"].values()}
        assert cell_ids_seen == {
            "deg10_w5_step", "deg12_w5_step",
            "deg10_w3_step", "deg14_w3_step",
        }

    def test_authority_kill_vector_emission_works_in_all_4_cells(self):
        """Authority: every cell produces episodes whose kill_vector is
        a valid KillVector dict with components in [1, 12]."""
        for cell in DEFAULT_REGION_CELLS:
            eps = _run_random_uniform_cell(cell, n_episodes=2, seed=0)
            assert len(eps) == 2, (
                f"cell {cell.cell_id} produced {len(eps)} eps, expected 2"
            )
            for e in eps:
                kv_dict = e.kill_vector_dict
                assert kv_dict is not None
                assert "components" in kv_dict
                comps = kv_dict["components"]
                assert 1 <= len(comps) <= 12
                # KillVector should be reconstructable.
                kv = KillVector.from_dict(kv_dict)
                assert kv.region_meta.get("degree") == cell.degree
                assert kv.region_meta.get("alphabet_width") == cell.alphabet_width


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


class TestProperty:
    """Property: determinism with fixed seed; episode count per cell = 1K;
    region metadata correctly tagged on each record."""

    def test_property_determinism_with_fixed_seed(self):
        """Property: same seed → same coefficients across runs (within
        a single cell)."""
        cell = RegionCell(degree=10, alphabet_width=3, reward_shape="step")
        r1 = _run_random_uniform_cell(cell, n_episodes=4, seed=7)
        r2 = _run_random_uniform_cell(cell, n_episodes=4, seed=7)
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a.coeffs == b.coeffs
            if math.isfinite(a.mahler_measure) and math.isfinite(b.mahler_measure):
                assert abs(a.mahler_measure - b.mahler_measure) < 1e-9

    def test_property_episode_count_matches_request(self):
        """Property: requesting N episodes per (cell, algo, seed)
        produces exactly N records per (cell, algo, seed)."""
        n = 3
        r = run_densification(
            cells=(RegionCell(degree=10, alphabet_width=3, reward_shape="step"),),
            n_episodes_per_cell=n,
            seeds=(0, 1),
            algorithms=("random_uniform",),
            progress=False,
        )
        # 1 cell × 1 algo × 2 seeds × 3 eps = 6 total
        assert r["total_episodes"] == 6
        for key, info in r["cell_summary"].items():
            assert info["n_episodes"] == n

    def test_property_region_metadata_correctly_tagged(self):
        """Property: each episode's kill_vector has region_meta that
        matches the cell it came from."""
        cell = RegionCell(degree=12, alphabet_width=5, reward_shape="step")
        eps = _run_random_uniform_cell(cell, n_episodes=4, seed=1)
        for e in eps:
            kv_dict = e.kill_vector_dict
            meta = kv_dict.get("region_meta") or {}
            assert meta.get("degree") == 12
            assert meta.get("alphabet_width") == 5
            assert meta.get("reward_shape") == "step"
            assert meta.get("env") == "DiscoveryEnv"

    def test_property_v2_region_meta_uses_v2_env(self):
        """Property: GA_elitist V2 records carry env=DiscoveryEnvV2 in
        region_meta — this is what makes the navigator key them as
        a separate region from V1 random/REINFORCE/PPO."""
        cell = RegionCell(degree=10, alphabet_width=3, reward_shape="step")
        eps = _run_ga_elitist_cell(cell, n_episodes=2, seed=0)
        assert len(eps) == 2
        for e in eps:
            meta = e.kill_vector_dict.get("region_meta") or {}
            assert meta.get("env") == "DiscoveryEnvV2"
            assert meta.get("degree") == 10
            assert meta.get("alphabet_width") == 3


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


class TestEdge:
    """Edge: degenerate region (degree=10 ±3); zero-budget cell;
    mismatched config caught."""

    def test_edge_smallest_search_space_degree10_w3(self):
        """Edge: deg10 ±3 has the smallest search space (7^6 = 117K).
        Pilot must run to completion without errors and produce valid
        records."""
        cell = RegionCell(degree=10, alphabet_width=3, reward_shape="step")
        eps = _run_random_uniform_cell(cell, n_episodes=5, seed=0)
        assert len(eps) == 5
        for e in eps:
            assert all(-3 <= c <= 3 for c in e.coeffs), (
                f"coefficient outside ±3: {e.coeffs}"
            )

    def test_edge_zero_episode_budget(self):
        """Edge: n_episodes_per_cell=0 yields empty episode list and
        zero-cell summary entries (all marked skipped=True)."""
        r = run_densification(
            cells=(RegionCell(degree=10, alphabet_width=3, reward_shape="step"),),
            n_episodes_per_cell=0,
            seeds=(0,),
            algorithms=("random_uniform",),
            progress=False,
        )
        assert r["total_episodes"] == 0
        for info in r["cell_summary"].values():
            assert info["n_episodes"] == 0

    def test_edge_unknown_algorithm_raises(self):
        """Edge: passing an unknown algorithm name raises ValueError
        rather than silently skipping (config-mismatch catch)."""
        cell = RegionCell(degree=10, alphabet_width=3, reward_shape="step")
        with pytest.raises(ValueError, match="unknown algorithm"):
            run_densification(
                cells=(cell,),
                n_episodes_per_cell=1,
                seeds=(0,),
                algorithms=("does_not_exist",),
                progress=False,
            )

    def test_edge_alphabet_width_3_yields_alphabet_size_7(self):
        """Edge: alphabet_width=3 yields a 7-element coefficient
        alphabet ([-3..3]); navigator's region_id must reflect this."""
        cell = RegionCell(degree=14, alphabet_width=3, reward_shape="step")
        assert cell.alphabet == (-3, -2, -1, 0, 1, 2, 3)
        assert cell.alphabet_size == 7
        # Region meta carries this through.
        meta = cell.region_meta_v1()
        assert meta["alphabet_width"] == 3
        assert meta["alphabet_size"] == 7


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


class TestComposition:
    """Composition: pilot → analysis → coverage update end-to-end;
    navigator gets new regions; per-region recommendations well-formed."""

    def test_composition_pilot_to_per_region_margins(self):
        """Composition: pilot output flows into per_region_operator_margins
        and yields a well-formed dict keyed by region_id."""
        r = run_densification(
            cells=(
                RegionCell(degree=10, alphabet_width=3, reward_shape="step"),
                RegionCell(degree=12, alphabet_width=5, reward_shape="step"),
            ),
            n_episodes_per_cell=3,
            seeds=(0,),
            algorithms=("random_uniform",),
            progress=False,
        )
        margins = per_region_operator_margins(r)
        # 2 cells × 1 algo (V1 only) = 2 region keys
        assert len(margins) == 2
        for region_id, info in margins.items():
            assert "operators" in info
            assert "top_operator" in info
            assert "ranking" in info
            for op_name, op_info in info["operators"].items():
                assert op_info["n_episodes"] >= 1
                assert "mean_magnitude" in op_info
                assert "ci_low" in op_info
                assert "ci_high" in op_info

    def test_composition_pilot_to_navigator_coverage(self):
        """Composition: writing the densification JSON makes the
        navigator pick up the new regions in margin mode.

        Uses a temporary base_dir so we don't pollute the real artifacts.
        """
        from prometheus_math.kill_vector_navigator import KillVectorNavigator

        with tempfile.TemporaryDirectory() as td:
            r = run_densification(
                cells=(
                    RegionCell(degree=10, alphabet_width=3, reward_shape="step"),
                ),
                n_episodes_per_cell=2,
                seeds=(0,),
                algorithms=("random_uniform",),
                progress=False,
            )
            # Persist as the densification JSON in the temp dir.
            out_path = os.path.join(td, "_region_densification_pilot.json")
            with open(out_path, "w") as f:
                json.dump({"pilot": r}, f, default=str)

            nav = KillVectorNavigator.from_data(base_dir=td)
            summary = nav.summary()
            # Should pick up the densification region.
            region_ids = [row["region"] for row in summary["regions"]]
            assert "DiscoveryEnv|deg10|w3|step" in region_ids
            # That region has margin data.
            for row in summary["regions"]:
                if row["region"] == "DiscoveryEnv|deg10|w3|step":
                    assert "margin" in row["modes"]

    def test_composition_navigator_recommendation_well_formed(self):
        """Composition: navigator.recommend on a densification region
        returns OperatorRecommendation dataclass instances with finite
        mean & CI bounds."""
        from prometheus_math.kill_vector_navigator import (
            KillVectorNavigator, OperatorRecommendation,
        )

        with tempfile.TemporaryDirectory() as td:
            r = run_densification(
                cells=(
                    RegionCell(degree=10, alphabet_width=3, reward_shape="step"),
                ),
                n_episodes_per_cell=10,
                seeds=(0, 1),
                algorithms=("random_uniform",),
                progress=False,
            )
            out_path = os.path.join(td, "_region_densification_pilot.json")
            with open(out_path, "w") as f:
                json.dump({"pilot": r}, f, default=str)
            nav = KillVectorNavigator.from_data(base_dir=td)
            recs = nav.recommend(
                "DiscoveryEnv|deg10|w3|step",
                mode="margin",
                top_k=10,
                min_episodes=1,  # 20 eps total, allow inclusion
            )
            assert len(recs) >= 1
            for rec in recs:
                assert isinstance(rec, OperatorRecommendation)
                assert math.isfinite(rec.expected_magnitude)
                assert rec.ci_low <= rec.expected_magnitude <= rec.ci_high
                assert rec.mode == "margin"

    def test_composition_baseline_comparison_returns_verdict(self):
        """Composition: compare_with_baseline runs end-to-end and
        returns a verdict letter from {A, B, C} along with the per-
        region top operator dict."""
        r = run_densification(
            cells=(
                RegionCell(degree=10, alphabet_width=3, reward_shape="step"),
                RegionCell(degree=12, alphabet_width=5, reward_shape="step"),
            ),
            n_episodes_per_cell=4,
            seeds=(0,),
            algorithms=("random_uniform", "reinforce_linear"),
            progress=False,
        )
        margins = per_region_operator_margins(r)
        comparison = compare_with_baseline(margins, baseline_pilot_path=None)
        assert comparison["verdict"] in ("A", "B", "C")
        assert isinstance(comparison["verdict_text"], str)
        assert "densification_top_per_region" in comparison
        assert isinstance(comparison["n_distinct_top_operators"], int)
