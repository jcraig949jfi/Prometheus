"""Tests for prometheus_math.anchor_density (T-2026-05-07-T036)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pytest

from prometheus_math.anchor_density import (
    DEFAULT_UNDER_ANCHORED_THRESHOLD,
    AnchorDensityReport,
    CalibrationAnchor,
    ChartAnchorMetrics,
    anchor_matches_chart,
    load_anchors,
    measure_all_chart_density,
    measure_chart_anchor_density,
    render_report,
)


# ---------------------------------------------------------------------------
# Test-local fake chart (avoids importing the real CoordinateChart so tests
# stay decoupled from chart-registration import side effects)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _FakeChart:
    domain: str
    region_key: str
    coordinate_system: Tuple[str, ...]

    @property
    def chart_id(self) -> str:
        return f"{self.domain}:{self.region_key}"


def _anchor(
    *,
    anchor_id: str = "CAL-test",
    structural_signature: str = "",
    tag_set: Tuple[str, ...] = (),
    label: str = "true_positive",
) -> CalibrationAnchor:
    return CalibrationAnchor(
        anchor_id=anchor_id,
        label=label,
        structural_signature=structural_signature,
        tag_set=tag_set,
        raw={"anchor_id": anchor_id, "label": label},
    )


# ---------------------------------------------------------------------------
# load_anchors
# ---------------------------------------------------------------------------


class TestLoadAnchors:
    def test_load_anchors_from_well_formed_jsonl(self, tmp_path: Path):
        store = tmp_path / "anchors.jsonl"
        store.write_text(
            json.dumps({
                "anchor_id": "CAL-A",
                "label": "true_positive",
                "structural_signature": "lehmer:deg14:exhaustive",
                "tag_set": ["number_theory", "lehmer"],
            }) + "\n" + json.dumps({
                "anchor_id": "CAL-B",
                "label": "true_negative",
                "structural_signature": "narrative:popular_press",
                "tag_set": ["narrative"],
            }) + "\n",
            encoding="utf-8",
        )
        anchors = load_anchors(store)
        assert len(anchors) == 2
        assert anchors[0].anchor_id == "CAL-A"
        assert anchors[0].tag_set == ("number_theory", "lehmer")
        assert anchors[1].label == "true_negative"

    def test_load_returns_empty_list_when_file_missing(self, tmp_path: Path):
        absent = tmp_path / "does_not_exist.jsonl"
        assert load_anchors(absent) == []

    def test_load_skips_blank_lines(self, tmp_path: Path):
        store = tmp_path / "withblank.jsonl"
        store.write_text(
            json.dumps({"anchor_id": "X", "label": "l", "structural_signature": "", "tag_set": []})
            + "\n\n  \n\n",
            encoding="utf-8",
        )
        assert len(load_anchors(store)) == 1

    def test_load_raises_on_malformed_json(self, tmp_path: Path):
        store = tmp_path / "bad.jsonl"
        store.write_text("not json\n", encoding="utf-8")
        with pytest.raises(ValueError, match="malformed JSON"):
            load_anchors(store)

    def test_load_raises_on_non_object_line(self, tmp_path: Path):
        store = tmp_path / "list.jsonl"
        store.write_text(json.dumps(["not", "an", "object"]) + "\n", encoding="utf-8")
        with pytest.raises(ValueError, match="not a JSON object"):
            load_anchors(store)


# ---------------------------------------------------------------------------
# anchor_matches_chart
# ---------------------------------------------------------------------------


class TestAnchorMatchesChart:
    def test_domain_in_structural_signature_matches(self):
        a = _anchor(structural_signature="lehmer:deg14:exhaustive")
        assert anchor_matches_chart(a, "lehmer", "deg14:pm5:palindromic") is True

    def test_domain_in_tag_set_matches(self):
        a = _anchor(tag_set=("lehmer", "polynomials"))
        assert anchor_matches_chart(a, "lehmer", "deg14:pm5:palindromic") is True

    def test_region_key_first_segment_in_signature_matches(self):
        a = _anchor(structural_signature="something:deg14:other")
        # chart's domain is "foo" (no match) but region_key starts with "deg14"
        assert anchor_matches_chart(a, "foo", "deg14:pm5:palindromic") is True

    def test_no_match_returns_false(self):
        a = _anchor(
            structural_signature="narrative:popular_press",
            tag_set=("narrative",),
        )
        assert anchor_matches_chart(a, "lehmer", "deg14:pm5:palindromic") is False

    def test_empty_chart_domain_returns_false(self):
        a = _anchor(structural_signature="lehmer:deg14")
        assert anchor_matches_chart(a, "", "deg14:pm5") is False

    def test_case_insensitive_match(self):
        a = _anchor(structural_signature="LEHMER:DEG14")
        assert anchor_matches_chart(a, "lehmer", "deg14:pm5") is True

    def test_tag_set_uses_exact_match_not_substring(self):
        """tag_set membership is exact (tags are identifier-like). A
        substring match in a tag does NOT count — only an exact tag
        equal to the chart domain (or region first segment) matches.
        Intentional asymmetry vs structural_signature substring match."""
        a = _anchor(tag_set=("foo_lehmer_bar",))
        assert anchor_matches_chart(a, "lehmer", "deg14:pm5") is False
        # An exact-equal tag does match.
        a_exact = _anchor(tag_set=("lehmer",))
        assert anchor_matches_chart(a_exact, "lehmer", "deg14:pm5") is True


# ---------------------------------------------------------------------------
# measure_chart_anchor_density
# ---------------------------------------------------------------------------


class TestMeasureChartAnchorDensity:
    def test_zero_anchors_yields_under_anchored(self):
        chart = _FakeChart("lehmer", "deg14:pm5", ("c0", "c1"))
        m = measure_chart_anchor_density(chart, [])
        assert m.count == 0
        assert m.under_anchored is True
        assert m.matched_anchor_ids == ()

    def test_matching_anchor_counted(self):
        chart = _FakeChart("lehmer", "deg14:pm5", ("c0",) * 8)
        anchors = [_anchor(anchor_id="A", structural_signature="lehmer:deg14")]
        m = measure_chart_anchor_density(chart, anchors)
        assert m.count == 1
        assert m.matched_anchor_ids == ("A",)
        assert m.per_axis_density == 1 / 8
        # density 0.125 > default threshold 0.1 -> not under-anchored
        assert m.under_anchored is False

    def test_density_below_threshold_flags(self):
        chart = _FakeChart("lehmer", "deg14:pm5", ("c0",) * 100)
        anchors = [_anchor(anchor_id="A", structural_signature="lehmer:deg14")]
        m = measure_chart_anchor_density(chart, anchors, threshold=0.1)
        # 1 / 100 = 0.01 < 0.1 -> under-anchored
        assert m.under_anchored is True

    def test_density_above_threshold_clears(self):
        chart = _FakeChart("lehmer", "deg14:pm5", ("c0", "c1"))
        anchors = [
            _anchor(anchor_id=f"A{i}", structural_signature="lehmer")
            for i in range(5)
        ]
        m = measure_chart_anchor_density(chart, anchors, threshold=0.5)
        assert m.count == 5
        assert m.per_axis_density == 2.5
        assert m.under_anchored is False

    def test_zero_axes_falls_back_to_count_density(self):
        chart = _FakeChart("lehmer", "deg14", ())
        anchors = [_anchor(anchor_id="A", structural_signature="lehmer")]
        m = measure_chart_anchor_density(chart, anchors)
        assert m.n_axes == 0
        # max(1, 0) = 1 in denominator -> density == count
        assert m.per_axis_density == 1.0


# ---------------------------------------------------------------------------
# measure_all_chart_density
# ---------------------------------------------------------------------------


class TestMeasureAllChartDensity:
    def test_unmatched_anchors_surfaced(self):
        chart = _FakeChart("lehmer", "deg14", ("c0",))
        anchors = [
            _anchor(anchor_id="MATCHED", structural_signature="lehmer:deg14"),
            _anchor(anchor_id="UNMATCHED", structural_signature="other:foo"),
        ]
        report = measure_all_chart_density([chart], anchors)
        assert report.n_anchors_loaded == 2
        assert report.n_anchors_unmatched == 1
        assert report.unmatched_anchor_ids == ("UNMATCHED",)

    def test_under_anchored_chart_ids_collected(self):
        chart_a = _FakeChart("alpha", "r1", ("c0", "c1"))
        chart_b = _FakeChart("beta", "r1", ("c0",))
        anchors = [
            _anchor(anchor_id="A", structural_signature="alpha"),
            _anchor(anchor_id="B", structural_signature="alpha"),
        ]
        report = measure_all_chart_density([chart_a, chart_b], anchors, threshold=0.5)
        # alpha gets 2 / 2 = 1.0 (above 0.5 -> not flagged)
        # beta gets 0 -> flagged
        assert "alpha:r1" not in report.under_anchored_chart_ids
        assert "beta:r1" in report.under_anchored_chart_ids

    def test_no_charts_yields_empty_report(self):
        report = measure_all_chart_density([], [_anchor(anchor_id="X")])
        assert report.n_charts_audited == 0
        assert report.chart_metrics == ()
        # Anchor unmatched (no charts to match against)
        assert report.n_anchors_unmatched == 1


# ---------------------------------------------------------------------------
# render_report
# ---------------------------------------------------------------------------


class TestRenderReport:
    def test_no_charts_renders_no_charts_message(self):
        report = AnchorDensityReport(
            n_charts_audited=0, n_anchors_loaded=0,
            threshold=0.1, chart_metrics=(),
            under_anchored_chart_ids=(), n_anchors_unmatched=0,
            unmatched_anchor_ids=(),
        )
        md = render_report(report)
        assert "No Registered Charts" in md
        assert "import" in md.lower()

    def test_populated_report_renders_table_and_flags(self):
        chart = _FakeChart("lehmer", "deg14:pm5", ("c0", "c1"))
        anchors = [_anchor(anchor_id="A", structural_signature="lehmer")]
        report = measure_all_chart_density([chart], anchors, threshold=2.0)
        # density 0.5 < 2.0 -> under-anchored
        md = render_report(report)
        assert "Per-Chart Metrics" in md
        assert "lehmer:deg14:pm5" in md
        assert "UNDER" in md
        assert "Under-Anchored Charts" in md

    def test_unmatched_anchors_section_renders(self):
        report = AnchorDensityReport(
            n_charts_audited=1, n_anchors_loaded=2,
            threshold=0.1,
            chart_metrics=(
                ChartAnchorMetrics(
                    chart_id="x:y", domain="x", region_key="y",
                    n_axes=1, matched_anchor_ids=(),
                    count=0, per_axis_density=0.0,
                    under_anchored=True,
                ),
            ),
            under_anchored_chart_ids=("x:y",),
            n_anchors_unmatched=2,
            unmatched_anchor_ids=("CAL-1", "CAL-2"),
        )
        md = render_report(report)
        assert "Unmatched Anchors" in md
        assert "CAL-1" in md
        assert "CAL-2" in md


# ---------------------------------------------------------------------------
# Integration: real registry + real anchor store
# ---------------------------------------------------------------------------


class TestIntegrationRealSubstrate:
    def test_runs_against_real_substrate_without_error(self, tmp_path: Path):
        """Smoke-test: importing real charts + loading the real anchor
        store + measuring density runs cleanly. Substrate finding is
        expected (current state has 0-anchor charts) but the test must
        not throw."""
        # Avoid the real default store by passing an empty store; this
        # decouples the integration test from the actual anchor file's
        # state at any given commit.
        store = tmp_path / "empty.jsonl"
        store.write_text("", encoding="utf-8")
        anchors = load_anchors(store)
        # Trigger registration of real charts
        import sigma_kernel.coordinate_charts  # noqa: F401
        from sigma_kernel.coordinate_chart import all_charts
        charts = all_charts()
        assert len(charts) >= 1  # at least lehmer must be registered
        report = measure_all_chart_density(charts, anchors)
        # All charts should be flagged under-anchored (zero anchors loaded)
        assert len(report.under_anchored_chart_ids) == len(charts)
        md = render_report(report)
        assert "Calibration Anchor Density Report" in md
