"""Tests for sigma_kernel.coordinate_chart and the Lehmer chart.

Joint sprint sync points S5/T4-T5. See
``pivot/techne_ergon_joint_sprint_2026-05-05.md`` and substrate v2.3
§6.1.

Aim: 12-18 tests across:
* CanonicalizationProtocol shape + decidability validation
* ChartRegistry register / lookup / by_id / round-trip
* Lehmer canonicalize correctness (reflection invariance)
* Lehmer metric properties (symmetry, identity)
* Lehmer admissible_region (rejects non-palindromic / wrong-degree /
  out-of-band coefficients)
* Hot-swap awareness (integration with canonicalizer_observability)
* Chart_id round-trip via the substrate-level singleton registry
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import pytest

from prometheus_math.canonicalizer_observability import (
    HOT_SWAP_THRESHOLD,
    CanonicalizerObserver,
)
from sigma_kernel.coordinate_chart import (
    DEFAULT_REGISTRY,
    REGISTERED_CANONICALIZER_IMPLS,
    VALID_DECIDABILITY,
    CanonicalizationProtocol,
    ChartLookupError,
    ChartRegistrationError,
    ChartRegistry,
    CoordinateChart,
    get_chart,
    lookup_chart,
    register_chart,
)
# Importing this submodule registers the Lehmer chart against
# DEFAULT_REGISTRY at import time. We import the chart object too so
# tests that need direct access don't have to look it up by id.
from sigma_kernel.coordinate_charts.lehmer import (
    LEHMER_DEG14_PM5_PALINDROMIC,
    _lehmer_admissible,
    _lehmer_canonicalize,
    _lehmer_distance,
)


# ---------------------------------------------------------------------------
# CanonicalizationProtocol
# ---------------------------------------------------------------------------


class TestCanonicalizationProtocol:
    def test_basic_construction(self):
        proto = CanonicalizationProtocol(
            impl="group_quotient",
            decidability_status="decidable",
            choice_dependencies=("ordering",),
            version="1.0.0",
        )
        assert proto.impl == "group_quotient"
        assert proto.decidability_status == "decidable"
        assert proto.choice_dependencies == ("ordering",)
        assert proto.version == "1.0.0"
        assert proto.canonicalize is None

    def test_decidability_status_validates(self):
        # Valid values pass
        for s in VALID_DECIDABILITY:
            CanonicalizationProtocol(
                impl="stub",
                decidability_status=s,  # type: ignore[arg-type]
                choice_dependencies=(),
                version="0.1.0",
            )
        # Invalid value rejected
        with pytest.raises(ValueError, match="decidability_status"):
            CanonicalizationProtocol(
                impl="stub",
                decidability_status="maybe",  # type: ignore[arg-type]
                choice_dependencies=(),
                version="0.1.0",
            )

    def test_all_known_canonicalizer_impls_loadable(self):
        """Hard requirement: all 6-8 known canonicalizer impls
        (group_quotient, partition_refinement, ideal_reduction,
        variety_fingerprint, cohomological_functor, reflection_quotient,
        plus stub) must be loadable as CanonicalizationProtocol values."""
        for impl in REGISTERED_CANONICALIZER_IMPLS:
            proto = CanonicalizationProtocol(
                impl=impl,
                decidability_status="decidable",
                choice_dependencies=(),
                version="1.0.0",
            )
            assert proto.impl == impl
        # Specifically named impls per the spec
        for required in (
            "group_quotient",
            "partition_refinement",
            "ideal_reduction",
            "variety_fingerprint",
            "cohomological_functor",
            "reflection_quotient",
            "stub",
        ):
            assert required in REGISTERED_CANONICALIZER_IMPLS, (
                f"required canonicalizer impl {required!r} missing from "
                f"REGISTERED_CANONICALIZER_IMPLS"
            )

    def test_apply_calls_bound_canonicalizer(self):
        proto = CanonicalizationProtocol(
            impl="stub",
            decidability_status="decidable",
            choice_dependencies=(),
            version="1.0.0",
            canonicalize=lambda x: tuple(sorted(x)),
        )
        assert proto.apply((3, 1, 2)) == (1, 2, 3)

    def test_apply_without_impl_raises(self):
        proto = CanonicalizationProtocol(
            impl="stub",
            decidability_status="decidable",
            choice_dependencies=(),
            version="1.0.0",
        )
        with pytest.raises(NotImplementedError):
            proto.apply((1, 2, 3))


# ---------------------------------------------------------------------------
# CoordinateChart.__post_init__ validation
# ---------------------------------------------------------------------------


class TestCoordinateChartValidation:
    """Validators in CoordinateChart.__post_init__. Substrate-tester ST002
    surfaced the empty-domain asymmetry vs region_key (2026-05-06)."""

    def _minimal_proto(self) -> CanonicalizationProtocol:
        return CanonicalizationProtocol(
            impl="stub",
            decidability_status="decidable",
            choice_dependencies=(),
            version="1.0.0",
        )

    def _minimal_chart_kwargs(self, **overrides):
        kwargs = dict(
            domain="test",
            region_key="r1",
            coordinate_system=("x",),
            canonicalization=self._minimal_proto(),
            metric=lambda a, b: 0.0,
            metric_id="trivial",
            equivalence_relations=(),
            admissible_region=lambda p: True,
            valid_operations=(),
        )
        kwargs.update(overrides)
        return kwargs

    def test_coordinate_chart_rejects_empty_domain(self):
        """ST002: domain='' must raise ValueError; previously accepted silently
        producing chart_id ':<region_key>' with downstream _split_chart_id corruption."""
        with pytest.raises(ValueError, match="domain must be a colon-free non-empty string"):
            CoordinateChart(**self._minimal_chart_kwargs(domain=""))

    def test_coordinate_chart_rejects_non_string_domain(self):
        with pytest.raises(ValueError, match="domain must be a colon-free non-empty string"):
            CoordinateChart(**self._minimal_chart_kwargs(domain=123))

    def test_coordinate_chart_rejects_colon_in_domain(self):
        with pytest.raises(ValueError, match="domain must be a colon-free non-empty string"):
            CoordinateChart(**self._minimal_chart_kwargs(domain="a:b"))

    def test_coordinate_chart_accepts_valid_domain(self):
        """Sanity check: a normal domain string still constructs successfully."""
        chart = CoordinateChart(**self._minimal_chart_kwargs(domain="lehmer"))
        assert chart.domain == "lehmer"
        assert chart.chart_id == "lehmer:r1"


# ---------------------------------------------------------------------------
# ChartRegistry
# ---------------------------------------------------------------------------


def _make_dummy_chart(domain: str = "test", region_key: str = "r1") -> CoordinateChart:
    return CoordinateChart(
        domain=domain,
        region_key=region_key,
        coordinate_system=("x", "y"),
        canonicalization=CanonicalizationProtocol(
            impl="stub",
            decidability_status="decidable",
            choice_dependencies=(),
            version="0.1.0",
            canonicalize=lambda p: tuple(p),
        ),
        metric=lambda a, b: math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))),
        metric_id="L2",
        equivalence_relations=(),
        admissible_region=lambda p: True,
        valid_operations=("identity",),
    )


class TestChartRegistry:
    def test_register_and_lookup_round_trip(self):
        reg = ChartRegistry()
        chart = _make_dummy_chart("d", "r")
        reg.register(chart)
        assert reg.lookup("d", "r") is chart
        assert reg.by_id("d:r") is chart
        assert "d:r" in reg
        assert len(reg) == 1
        assert reg.all() == [chart]
        assert reg.ids() == ["d:r"]

    def test_lookup_missing_returns_none(self):
        reg = ChartRegistry()
        assert reg.lookup("nope", "nada") is None
        assert reg.by_id("nope:nada") is None

    def test_require_raises_when_missing(self):
        reg = ChartRegistry()
        with pytest.raises(ChartLookupError):
            reg.require("nope:nada")

    def test_duplicate_registration_raises_without_replace(self):
        reg = ChartRegistry()
        chart = _make_dummy_chart("d", "r")
        reg.register(chart)
        with pytest.raises(ChartRegistrationError):
            reg.register(chart)

    def test_duplicate_registration_with_replace_succeeds(self):
        reg = ChartRegistry()
        c1 = _make_dummy_chart("d", "r")
        c2 = _make_dummy_chart("d", "r")
        reg.register(c1)
        reg.register(c2, replace=True)
        # The second registration won; ensure we got c2 not c1.
        assert reg.by_id("d:r") is c2


# ---------------------------------------------------------------------------
# Lehmer chart — canonicalization, metric, admissibility
# ---------------------------------------------------------------------------


class TestLehmerCanonicalization:
    def test_canonicalizes_polynomial_and_reflection_to_same(self):
        """Spec: canonicalize a polynomial + its x→-x reflection to the
        same value."""
        # Pick a non-symmetric half so the reflection is genuinely
        # different. (1, 1, ...) reflected becomes (1, -1, 1, -1, ...).
        original = (1, 1, 2, -1, 0, 3, -2, 1)
        # x → -x flips signs of odd-index coefficients
        reflected = (1, -1, 2, 1, 0, -3, -2, -1)
        c1 = _lehmer_canonicalize(original)
        c2 = _lehmer_canonicalize(reflected)
        assert c1 == c2, (
            f"canonicalize(orig)={c1}, canonicalize(refl)={c2}; should be equal"
        )

    def test_canonicalize_idempotent(self):
        v = (1, -2, 3, 0, -1, 2, -3, 1)
        c = _lehmer_canonicalize(v)
        assert _lehmer_canonicalize(c) == c

    def test_canonicalize_picks_lex_min(self):
        # Construct a half-vector whose reflection is lex-smaller and
        # check we pick the reflection.
        # original starts with positive c1; reflection flips c1 to
        # negative, which is lex-smaller (since c0 stays the same).
        original = (3, 2, 0, 0, 0, 0, 0, 0)
        reflected = (3, -2, 0, 0, 0, 0, 0, 0)
        canon = _lehmer_canonicalize(original)
        assert canon == reflected
        assert canon < original

    def test_metric_symmetric(self):
        """Spec: chart's metric is symmetric: d(a, b) == d(b, a)."""
        a = (1, 0, -1, 2, 0, 1, 0, 1)
        b = (1, 1, 0, -1, 0, 0, 2, 1)
        assert _lehmer_distance(a, b) == _lehmer_distance(b, a)

    def test_metric_zero_for_canonicalized_equal(self):
        """Spec: chart's metric returns 0 for canonicalized-equal inputs."""
        original = (1, 2, 0, -1, 0, 1, 3, 1)
        reflected = (1, -2, 0, 1, 0, -1, 3, -1)
        # original and reflected are the SAME canonical object
        assert _lehmer_canonicalize(original) == _lehmer_canonicalize(reflected)
        assert _lehmer_distance(original, reflected) == 0.0
        assert _lehmer_distance(original, original) == 0.0

    def test_metric_positive_for_distinct_points(self):
        a = (1, 0, 0, 0, 0, 0, 0, 0)
        b = (1, 0, 0, 0, 0, 0, 0, 1)
        # These are not in the same equivalence class (reflection of b
        # would flip odd-index entries; b's only nonzero off c0 is c7
        # which is even-indexed so unchanged). Distance should be 1.
        assert _lehmer_distance(a, b) == 1.0


class TestLehmerAdmissibility:
    def test_rejects_wrong_length(self):
        # Length 5 is neither 8 (half) nor 15 (full)
        assert _lehmer_admissible((1, 2, 3, 4, 5)) is False
        # Length 0
        assert _lehmer_admissible(()) is False

    def test_rejects_out_of_band_coefficient(self):
        # Coefficient bound is ±5
        assert _lehmer_admissible((1, 0, 0, 0, 0, 0, 0, 6)) is False
        assert _lehmer_admissible((1, 0, 0, -7, 0, 0, 0, 0)) is False

    def test_rejects_zero_leading_coefficient(self):
        # c0 == 0 means not actually degree 14
        assert _lehmer_admissible((0, 1, 0, 0, 0, 0, 0, 0)) is False

    def test_rejects_non_palindromic_full_vector(self):
        # 15-element vector that isn't palindromic
        full = [1, 2, 3, 4, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0]
        # full[0]=1 vs full[14]=0 -> not palindromic
        assert _lehmer_admissible(full) is False

    def test_accepts_valid_half_vector(self):
        assert _lehmer_admissible((1, 2, 3, -1, 0, 1, -2, 1)) is True
        assert _lehmer_admissible((1, 0, 0, 0, 0, 0, 0, 0)) is True

    def test_accepts_valid_full_palindrome(self):
        # Palindromic 15-coefficient vector with all entries in [-5, 5]
        # and c0 != 0
        full = (1, 2, 0, -1, 3, 0, -2, 1, -2, 0, 3, -1, 0, 2, 1)
        assert _lehmer_admissible(full) is True


# ---------------------------------------------------------------------------
# Singleton registry + chart_id round-trip
# ---------------------------------------------------------------------------


class TestSingletonRegistration:
    def test_lehmer_chart_lookup_by_chart_id(self):
        """Spec: chart can be looked up by chart_id
        ``"lehmer:deg14:pm5:palindromic"``."""
        chart = get_chart("lehmer:deg14:pm5:palindromic")
        assert chart is not None
        assert chart is LEHMER_DEG14_PM5_PALINDROMIC
        assert chart.domain == "lehmer"
        assert chart.region_key == "deg14:pm5:palindromic"
        assert chart.metric_id == "L2"
        assert chart.canonicalization.impl == "reflection_quotient"
        assert chart.canonicalization.decidability_status == "decidable"

    def test_lehmer_chart_lookup_by_domain_region(self):
        chart = lookup_chart("lehmer", "deg14:pm5:palindromic")
        assert chart is LEHMER_DEG14_PM5_PALINDROMIC

    def test_chart_id_property_round_trip(self):
        chart = LEHMER_DEG14_PM5_PALINDROMIC
        assert chart.chart_id == "lehmer:deg14:pm5:palindromic"
        # Round-trip through the registry
        assert get_chart(chart.chart_id) is chart

    def test_chart_distance_canonicalizes_inputs(self):
        """CoordinateChart.distance should canonicalize before
        applying the metric, so reflected inputs yield distance 0."""
        chart = LEHMER_DEG14_PM5_PALINDROMIC
        a = (1, 1, 2, -1, 0, 3, -2, 1)
        a_refl = (1, -1, 2, 1, 0, -3, -2, -1)
        assert chart.distance(a, a_refl) == 0.0

    def test_chart_admits_predicate(self):
        chart = LEHMER_DEG14_PM5_PALINDROMIC
        assert chart.admits((1, 0, 0, 0, 0, 0, 0, 0)) is True
        assert chart.admits((0, 0, 0, 0, 0, 0, 0, 1)) is False  # c0 == 0
        assert chart.admits((1, 0, 0, 0, 0, 0, 0, 99)) is False  # out of band


# ---------------------------------------------------------------------------
# Hot-swap awareness (integration with canonicalizer_observability)
# ---------------------------------------------------------------------------


class TestHotSwapAwareness:
    def test_hot_swap_pending_false_on_empty_log(self, tmp_path: Path):
        """No observations logged → no hot-swap."""
        log_path = tmp_path / "obs.jsonl"
        # Don't create the file; empty / nonexistent should be False
        reg = ChartRegistry()
        assert reg.hot_swap_pending(log_path=log_path) is False

    def test_hot_swap_pending_true_when_threshold_crossed(self, tmp_path: Path):
        """Spec: when canonicalizer_observed_distribution >= 0.70 for a
        single canonicalizer, ChartRegistry exposes a hot_swap_pending
        flag (integrate with prometheus_math.canonicalizer_observability)."""
        log_path = tmp_path / "obs.jsonl"
        observer = CanonicalizerObserver(log_path=log_path)
        # 8 of 10 events = 80% on variety_fingerprint, above 70%
        for i in range(8):
            observer.observe("variety_fingerprint", claim_id=f"c{i}")
        for i in range(2):
            observer.observe("group_quotient", claim_id=f"d{i}")

        reg = ChartRegistry()
        assert reg.hot_swap_pending(log_path=log_path) is True
        status = reg.hot_swap_status(log_path=log_path)
        assert status["pending"] is True
        assert status["dominant"][0] == "variety_fingerprint"
        assert status["dominant"][1] >= HOT_SWAP_THRESHOLD
        # Distribution should be approximately {variety_fingerprint:0.8,
        # group_quotient:0.2}
        assert status["distribution"]["variety_fingerprint"] == pytest.approx(0.8)
        assert status["distribution"]["group_quotient"] == pytest.approx(0.2)

    def test_hot_swap_pending_false_below_threshold(self, tmp_path: Path):
        """At 60% (< 70%), hot-swap should NOT be pending."""
        log_path = tmp_path / "obs.jsonl"
        observer = CanonicalizerObserver(log_path=log_path)
        for i in range(6):
            observer.observe("variety_fingerprint", claim_id=f"c{i}")
        for i in range(4):
            observer.observe("group_quotient", claim_id=f"d{i}")
        reg = ChartRegistry()
        assert reg.hot_swap_pending(log_path=log_path) is False
