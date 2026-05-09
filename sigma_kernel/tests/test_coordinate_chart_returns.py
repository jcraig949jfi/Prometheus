"""Return-value coverage for sigma_kernel.coordinate_chart.

Closes ST-fire63-001 part 2: substrate-tester fire #63 Lane 16
mutation testing on sigma_kernel/coordinate_chart.py surfaced 6
genuine return-value gaps (lines 185, 273, 283, 287, 303, 308) on
the substrate v2.3 §6.2 P0 primitive bundling CanonicalizationProtocol
+ CoordinateChart.

**Sister files (same return-value pattern):**
  - test_method_spec_factory_returns.py (fire #51)
  - test_exclusion_certificate_returns.py (fire #54)
  - test_triangulation_protocol_returns.py (fire #55)
  - test_sigma_kernel_core_returns.py (fire #62)

**Source ticket:** T-2026-05-09-ST-fire64-001 (Techne; closes ST-fire63-001).
"""
from __future__ import annotations

import pytest

from sigma_kernel.coordinate_chart import (
    CanonicalizationProtocol,
    ChartRegistry,
    CoordinateChart,
    _split_chart_id,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _identity_canonicalization() -> CanonicalizationProtocol:
    return CanonicalizationProtocol(
        impl="identity",
        decidability_status="decidable",
        choice_dependencies=(),
        version="1.0.0",
        canonicalize=lambda p: p,
    )


def _make_chart(domain: str = "test_domain", region_key: str = "test_region") -> CoordinateChart:
    return CoordinateChart(
        domain=domain,
        region_key=region_key,
        coordinate_system=("x", "y"),
        canonicalization=_identity_canonicalization(),
        metric=lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1]),
        metric_id="manhattan_test",
        equivalence_relations=(),
        admissible_region=lambda p: True,
        valid_operations=(),
    )


# ---------------------------------------------------------------------------
# Line 185: CanonicalizationProtocol.apply()
# ---------------------------------------------------------------------------


class TestCanonicalizationProtocolApply:
    """Catches `return self.canonicalize(point)` -> `return None`."""

    def test_apply_returns_non_None_for_identity(self):
        proto = _identity_canonicalization()
        result = proto.apply((3, 5))
        assert result is not None
        assert result == (3, 5)

    def test_apply_returns_canonicalized_value(self):
        """A non-identity canonicalizer (sort tuple) must return the
        canonicalized form."""
        sort_canonical = CanonicalizationProtocol(
            impl="sort",
            decidability_status="decidable",
            choice_dependencies=(),
            version="1.0.0",
            canonicalize=lambda p: tuple(sorted(p)),
        )
        result = sort_canonical.apply((5, 3, 1))
        assert result == (1, 3, 5)

    def test_apply_unbound_raises(self):
        """Registry-only entry (canonicalize=None) must raise on apply()."""
        proto = CanonicalizationProtocol(
            impl="x",
            decidability_status="decidable",
            choice_dependencies=(),
            version="1.0.0",
            canonicalize=None,
        )
        with pytest.raises(NotImplementedError):
            proto.apply((1, 2))


# ---------------------------------------------------------------------------
# Line 273: CoordinateChart.canonicalize() delegate
# ---------------------------------------------------------------------------


class TestCoordinateChartCanonicalize:
    """Catches `return self.canonicalization.apply(point)` -> `return None`."""

    def test_canonicalize_returns_non_None(self):
        chart = _make_chart()
        result = chart.canonicalize((3, 5))
        assert result is not None

    def test_canonicalize_delegates_to_protocol(self):
        sort_chart = CoordinateChart(
            domain="d", region_key="r",
            coordinate_system=("x", "y", "z"),
            canonicalization=CanonicalizationProtocol(
                impl="sort",
                decidability_status="decidable",
                choice_dependencies=(),
                version="1.0.0",
                canonicalize=lambda p: tuple(sorted(p)),
            ),
            metric=lambda a, b: 0.0,
            metric_id="zero_test",
            equivalence_relations=(),
            admissible_region=lambda p: True,
            valid_operations=(),
        )
        assert sort_chart.canonicalize((5, 3, 1)) == (1, 3, 5)


# ---------------------------------------------------------------------------
# Line 283: CoordinateChart.distance()
# ---------------------------------------------------------------------------


class TestCoordinateChartDistance:
    """Catches `return float(self.metric(ca, cb))` -> `return None`."""

    def test_distance_returns_non_None(self):
        chart = _make_chart()
        result = chart.distance((1, 2), (4, 6))
        assert result is not None

    def test_distance_returns_float(self):
        chart = _make_chart()
        result = chart.distance((1, 2), (4, 6))
        assert isinstance(result, float)

    def test_distance_value(self):
        """Manhattan distance: |1-4| + |2-6| = 3 + 4 = 7.0."""
        chart = _make_chart()
        assert chart.distance((1, 2), (4, 6)) == 7.0

    def test_distance_self_zero(self):
        chart = _make_chart()
        assert chart.distance((1, 2), (1, 2)) == 0.0


# ---------------------------------------------------------------------------
# Line 287: CoordinateChart.admits()
# ---------------------------------------------------------------------------


class TestCoordinateChartAdmits:
    """Catches `return bool(self.admissible_region(point))` -> `return None`."""

    def test_admits_returns_non_None(self):
        chart = _make_chart()
        result = chart.admits((1, 2))
        assert result is not None

    def test_admits_returns_bool(self):
        chart = _make_chart()
        assert isinstance(chart.admits((1, 2)), bool)

    def test_admits_true_for_inside(self):
        chart = _make_chart()
        assert chart.admits((1, 2)) is True

    def test_admits_false_for_outside(self):
        outside_chart = CoordinateChart(
            domain="d", region_key="r",
            coordinate_system=("x", "y"),
            canonicalization=_identity_canonicalization(),
            metric=lambda a, b: 0.0,
            metric_id="zero_test",
            equivalence_relations=(),
            admissible_region=lambda p: p[0] >= 0,  # only non-negative x
            valid_operations=(),
        )
        assert outside_chart.admits((-1, 0)) is False
        assert outside_chart.admits((1, 0)) is True


# ---------------------------------------------------------------------------
# Lines 303, 308: _split_chart_id()
# ---------------------------------------------------------------------------


class TestSplitChartId:
    """Catches:
      - line 303: `chart_id.split(":", 1)` maxsplit `1 → 2`
      - line 308: `return domain, region_key` -> `return None`"""

    def test_split_returns_non_None(self):
        result = _split_chart_id("lehmer:deg14:pm5:palindromic")
        assert result is not None

    def test_split_returns_tuple_of_two_strings(self):
        result = _split_chart_id("lehmer:deg14:pm5:palindromic")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(x, str) for x in result)

    def test_split_first_colon_only(self):
        """maxsplit=1: region_key must keep the rest of the colons."""
        domain, region_key = _split_chart_id("lehmer:deg14:pm5:palindromic")
        assert domain == "lehmer"
        assert region_key == "deg14:pm5:palindromic"

    def test_split_simple_case(self):
        domain, region_key = _split_chart_id("a:b")
        assert domain == "a"
        assert region_key == "b"

    def test_split_empty_domain_raises(self):
        with pytest.raises(ValueError):
            _split_chart_id(":x")

    def test_split_empty_region_key_raises(self):
        with pytest.raises(ValueError):
            _split_chart_id("x:")

    def test_split_no_colon_raises(self):
        with pytest.raises(ValueError):
            _split_chart_id("nocolon")

    def test_split_non_string_raises(self):
        with pytest.raises(ValueError):
            _split_chart_id(12345)  # type: ignore
