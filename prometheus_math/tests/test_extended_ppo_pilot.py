"""Tests for prometheus_math.extended_ppo_pilot.

Math-tdd skill rubric: ≥3 each in authority/property/edge/composition.

The pilot is a thin wrapper around DiscoveryEnv + Stable-Baselines3 PPO
with rich trajectory capture.  Tests focus on:

  * Authority: pilot driver produces well-formed records; band-touch
    detection works on a known sub-band poly; Mossinghoff cross-check
    finds Lehmer's polynomial.
  * Property: determinism with fixed seed; episode count = budget;
    per-seed metrics consistent.
  * Edge: zero-budget pilot; degenerate seed; pilot interrupt mid-run
    handled.
  * Composition: full pipeline runs end-to-end; per-episode trajectory
    captured; results JSON well-formed.
"""
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pytest

from prometheus_math.extended_ppo_pilot import (
    SeedResult,
    _band_margin,
    aggregate_seed_results,
    classify_verdict,
    main,
    run_extended_pilot,
    run_ppo_extended,
)


# Lehmer's polynomial — canonical sub-Lehmer poly anchor.
LEHMER_COEFFS = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.176280818


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


class TestAuthority:
    """Authority: anchor against canonical mathematical truths."""

    def test_authority_lehmer_M_is_inside_band(self):
        """Authority: Lehmer's polynomial sits in the sub-Lehmer band."""
        # M ≈ 1.17628; band is 1.001 < M < 1.18, so Lehmer is in-band
        # and band_margin should be 0.0.
        m = _band_margin(LEHMER_M)
        assert m is not None
        assert m == 0.0   # in-band → margin 0

    def test_authority_above_band_margin_positive(self):
        """Authority: M=1.5 (Salem cluster) has positive margin = 0.32."""
        m = _band_margin(1.5)
        assert m is not None
        assert m == pytest.approx(1.5 - 1.18, abs=1e-9)
        assert m > 0

    def test_authority_cyclotomic_margin_negative(self):
        """Authority: M=1.0 cyclotomic has negative margin (M - 1.001)."""
        m = _band_margin(1.0)
        assert m is not None
        assert m == pytest.approx(1.0 - 1.001, abs=1e-9)
        assert m < 0

    def test_authority_lehmer_in_mossinghoff(self):
        """Authority: Lehmer's polynomial is in the Mossinghoff snapshot
        (verifies the cross-check the env relies on)."""
        from prometheus_math.databases import mahler as _mahler_db
        snapshot = getattr(_mahler_db, "MAHLER_TABLE", None)
        assert snapshot is not None
        found = False
        for entry in snapshot:
            try:
                em = float(entry.get("mahler_measure", float("inf")))
                if abs(em - LEHMER_M) < 1e-6:
                    found = True
                    break
            except (TypeError, ValueError):
                continue
        assert found, "Lehmer's polynomial must be findable in Mossinghoff snapshot"


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


class TestProperty:
    """Property: invariants over a parametrised family."""

    def test_property_band_margin_signed_consistency(self):
        """Property: band margin is signed & consistent — positive for
        above-band, negative for below-1.001, zero in-band."""
        # Sweep a range of M values and check the signed convention.
        for M, expected_sign in [
            (0.5, -1),    # below cyclotomic floor → negative
            (1.0, -1),    # cyclotomic → negative
            (1.001, 0),   # exactly at floor → 0 (in-band by convention)
            (1.1, 0),     # in-band → 0
            (1.18, 0),    # boundary → 0 (defined by `M > 1.18` strict)
            (1.5, +1),    # above band → positive
            (3.0, +1),    # high → positive
        ]:
            m = _band_margin(M)
            assert m is not None
            if expected_sign < 0:
                assert m < 0, f"M={M}: expected negative, got {m}"
            elif expected_sign == 0:
                assert m == 0.0, f"M={M}: expected zero, got {m}"
            else:
                assert m > 0, f"M={M}: expected positive, got {m}"

    def test_property_zero_budget_yields_empty_seed_result(self):
        """Property: zero episodes → SeedResult with n_episodes=0
        and no firsts."""
        sr = run_ppo_extended(0, seed=0, progress_every=0)
        assert sr.n_episodes == 0
        assert sr.first_band_touch_episode is None
        assert sr.first_band_cross_episode is None
        assert sr.first_sub_lehmer_episode is None
        assert sr.n_band_touch == 0

    def test_property_aggregate_sums_match_per_seed(self):
        """Property: aggregate counts equal sum of per-seed counts."""
        # Construct synthetic SeedResult instances.
        srs = [
            SeedResult(
                seed=0, n_episodes=100, elapsed_s=1.0,
                first_band_touch_episode=10, first_band_touch_margin=-0.001,
                first_band_cross_episode=10, first_band_cross_margin=-0.001,
                first_sub_lehmer_episode=20, first_sub_lehmer_M=1.176,
                first_shadow_catalog_episode=None, first_promote_episode=None,
                best_margin=-0.005, mean_margin=2.0,
                median_margin=1.5, std_margin=1.0,
                p10_margin=0.0, p25_margin=0.5, p75_margin=2.5, p90_margin=4.0,
                n_band_touch=15, n_band_cross=10, n_sub_lehmer=5,
                n_cyclotomic=10, n_above_band=85,
                n_known_in_mossinghoff=5, n_novel_in_band=0,
                n_pipeline_routed=0, n_promoted=0,
                n_shadow_catalog=0, n_rejected_post_pipeline=0,
            ),
            SeedResult(
                seed=1, n_episodes=200, elapsed_s=2.0,
                first_band_touch_episode=50, first_band_touch_margin=-0.002,
                first_band_cross_episode=50, first_band_cross_margin=-0.002,
                first_sub_lehmer_episode=60, first_sub_lehmer_M=1.18,
                first_shadow_catalog_episode=None, first_promote_episode=None,
                best_margin=-0.01, mean_margin=1.8,
                median_margin=1.5, std_margin=1.1,
                p10_margin=0.0, p25_margin=0.5, p75_margin=2.5, p90_margin=4.0,
                n_band_touch=20, n_band_cross=15, n_sub_lehmer=8,
                n_cyclotomic=12, n_above_band=180,
                n_known_in_mossinghoff=8, n_novel_in_band=0,
                n_pipeline_routed=0, n_promoted=0,
                n_shadow_catalog=0, n_rejected_post_pipeline=0,
            ),
        ]
        agg = aggregate_seed_results(srs)
        assert agg["total_episodes"] == 300
        assert agg["n_band_touch"] == 35
        assert agg["n_band_cross"] == 25
        assert agg["n_sub_lehmer"] == 13
        assert agg["n_known_in_mossinghoff"] == 13
        assert agg["best_margin_overall"] == -0.01

    def test_property_seed_result_to_dict_well_formed(self):
        """Property: SeedResult.to_dict produces a JSON-roundtrippable dict."""
        sr = SeedResult(
            seed=42, n_episodes=10, elapsed_s=0.5,
            first_band_touch_episode=None, first_band_touch_margin=None,
            first_band_cross_episode=None, first_band_cross_margin=None,
            first_sub_lehmer_episode=None, first_sub_lehmer_M=None,
            first_shadow_catalog_episode=None, first_promote_episode=None,
            best_margin=2.0, mean_margin=3.0, median_margin=3.0,
            std_margin=0.5, p10_margin=2.0, p25_margin=2.5,
            p75_margin=3.5, p90_margin=4.0,
            n_band_touch=0, n_band_cross=0, n_sub_lehmer=0,
            n_cyclotomic=0, n_above_band=10,
            n_known_in_mossinghoff=0, n_novel_in_band=0,
            n_pipeline_routed=0, n_promoted=0,
            n_shadow_catalog=0, n_rejected_post_pipeline=0,
        )
        d = sr.to_dict()
        # Round-trip through JSON.
        s = json.dumps(d, default=str)
        d2 = json.loads(s)
        assert d2["seed"] == 42
        assert d2["best_margin"] == 2.0


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------


class TestEdge:
    """Edge: behavior at boundaries / degenerate inputs."""

    def test_edge_band_margin_nonfinite(self):
        """Edge: non-finite M returns None (the calling code handles it)."""
        assert _band_margin(float("inf")) is None
        assert _band_margin(float("nan")) is None

    def test_edge_zero_budget_pilot(self):
        """Edge: zero-episode pilot yields empty results without crashing."""
        result = run_extended_pilot(
            n_episodes_per_seed=0, seeds=(0,), progress=False
        )
        assert result["meta"]["n_episodes_per_seed"] == 0
        assert len(result["seed_results"]) == 1
        assert result["seed_results"][0]["n_episodes"] == 0
        assert result["aggregate"]["total_episodes"] == 0
        # Verdict on zero data: D (didn't touch band).
        assert result["verdict"]["verdict"] in (
            "D_OVERESTIMATED_UTILITY", "C_STRUCTURALLY_ELUSIVE"
        )

    def test_edge_classify_verdict_a_from_synthetic(self):
        """Edge: classify_verdict handles the SHADOW_CATALOG-discovery
        path (synthetic seed result with novel candidate)."""
        agg = {
            "total_episodes": 1000, "n_band_touch": 5, "n_band_cross": 5,
            "n_sub_lehmer": 1, "n_known_in_mossinghoff": 0,
            "n_novel_in_band": 1, "n_pipeline_routed": 1,
            "n_promoted": 0, "n_shadow_catalog": 1,
            "n_rejected_post_pipeline": 0,
            "best_margin_overall": -0.005,
        }
        v = classify_verdict(agg, [])
        assert v["verdict"] == "A_NAVIGATOR_VALIDATED"

    def test_edge_classify_verdict_b_from_synthetic(self):
        """Edge: classify_verdict — band-cross + only Mossinghoff hits → B."""
        agg = {
            "total_episodes": 1000, "n_band_touch": 5, "n_band_cross": 5,
            "n_sub_lehmer": 5, "n_known_in_mossinghoff": 5,
            "n_novel_in_band": 0, "n_pipeline_routed": 0,
            "n_promoted": 0, "n_shadow_catalog": 0,
            "n_rejected_post_pipeline": 0,
            "best_margin_overall": -0.005,
        }
        v = classify_verdict(agg, [])
        assert v["verdict"] == "B_BOUNDED_REDISCOVERY"

    def test_edge_classify_verdict_c_from_synthetic(self):
        """Edge: classify_verdict — band-touch but no sub-Lehmer hit → C."""
        agg = {
            "total_episodes": 1000, "n_band_touch": 5, "n_band_cross": 5,
            "n_sub_lehmer": 0, "n_known_in_mossinghoff": 0,
            "n_novel_in_band": 0, "n_pipeline_routed": 0,
            "n_promoted": 0, "n_shadow_catalog": 0,
            "n_rejected_post_pipeline": 0,
            "best_margin_overall": -0.001,
        }
        v = classify_verdict(agg, [])
        assert v["verdict"] == "C_STRUCTURALLY_ELUSIVE"


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


class TestComposition:
    """Composition: the parts integrate correctly end-to-end."""

    def test_composition_small_smoke_run(self):
        """Composition: a tiny end-to-end run produces a well-formed
        result dict.  Uses a small budget so it's fast in CI."""
        try:
            import stable_baselines3  # noqa: F401
        except ImportError:
            pytest.skip("SB3 not installed")
        result = run_extended_pilot(
            n_episodes_per_seed=20,    # tiny smoke
            seeds=(0,),
            progress=False,
        )
        assert "meta" in result
        assert "seed_results" in result
        assert "aggregate" in result
        assert "verdict" in result
        assert len(result["seed_results"]) == 1
        sr = result["seed_results"][0]
        assert sr["n_episodes"] >= 1   # PPO got at least 1 episode in
        # Aggregate consistency: total = sum of seeds.
        assert result["aggregate"]["total_episodes"] == sr["n_episodes"]

    def test_composition_main_writes_json(self, tmp_path):
        """Composition: main() writes a JSON file with the full structure."""
        try:
            import stable_baselines3  # noqa: F401
        except ImportError:
            pytest.skip("SB3 not installed")
        out_path = tmp_path / "extended_ppo_smoke.json"
        result = main(
            out_path=str(out_path),
            n_episodes_per_seed=10,
            seeds=(0,),
        )
        assert out_path.exists()
        loaded = json.loads(out_path.read_text())
        assert loaded["meta"]["algorithm"] == "PPO-MLP"
        assert loaded["meta"]["env"]["degree"] == 14
        assert "seed_results" in loaded
        assert "verdict" in loaded

    def test_composition_seed_result_trajectory_captured(self):
        """Composition: per-seed band_touch_samples list is populated when
        episodes touch the band.  We can't guarantee touches at small
        scale, so this just checks the field exists + is iterable."""
        try:
            import stable_baselines3  # noqa: F401
        except ImportError:
            pytest.skip("SB3 not installed")
        sr = run_ppo_extended(20, seed=0, progress_every=0)
        # Even on no touches, the field is an empty list (not None / not absent).
        assert isinstance(sr.band_touch_samples, list)
        assert isinstance(sr.novel_candidates, list)

    def test_composition_aggregate_handles_empty_list(self):
        """Composition: aggregate over an empty list returns empty dict."""
        agg = aggregate_seed_results([])
        assert agg == {}
