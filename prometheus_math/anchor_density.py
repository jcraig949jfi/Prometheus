"""Calibration anchor density measurement primitive.

Per inbox ticket T-2026-05-07-T036 (P1-high, Aporia 2026-05-07): per
HARD-4 (calibration anchors are load-bearing infrastructure), each
registered :class:`sigma_kernel.coordinate_chart.CoordinateChart` should
report its calibration anchor count + density. Substrate-Tester's
representation-pressure lane uses this to flag under-anchored regions.

Anchor-to-chart mapping
-----------------------
The calibration anchor schema (``aporia/calibration/battery_calibration.jsonl``)
carries free-text ``structural_signature`` + ``tag_set`` fields, not a
``chart_id`` field. This audit uses the conservative-permissive heuristic:

  * An anchor is **mapped to** a chart iff *any* of: chart's ``domain``
    appears as a substring of the anchor's ``structural_signature``,
    OR chart's ``domain`` appears in the anchor's ``tag_set``,
    OR chart's ``region_key`` first segment appears in either field.

This is deliberately permissive because the substrate's anchor schema
predates the CoordinateChart registry (2026-04-26 vs 2026-05-05); a
future ticket should add an explicit ``chart_id`` field to the anchor
schema (Aporia coordination ticket noted in the rendered report when
the heuristic-mismatch case arises).

Density definition
------------------
True volume normalization (volume of admissible region) is chart-specific
and not generally computable. This audit reports two metrics:

  * ``count`` — raw matched-anchor count
  * ``per_axis_density`` — count / max(1, len(coordinate_system))

Under-anchored = ``count == 0`` OR ``per_axis_density < threshold``.

Default threshold: 0.1 anchors/axis (per HARD-4 conservative reading;
zero-anchor charts always flag).

NO contract change to CoordinateChart, ChartRegistry, or any sigma_kernel
module — this module is purely additive and reads via the public
``all_charts()`` API plus direct JSONL load of the anchor file.

CLI
---
::

    python -m prometheus_math.anchor_density [--anchor-store PATH]
        [--threshold 0.1] [--out PATH]

Outputs:
  * Markdown report at ``--out`` (default
    ``prometheus_math/ANCHOR_DENSITY_REPORT.md``)
  * Returns dict ``{chart_id -> ChartAnchorMetrics}`` for programmatic use.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


DEFAULT_ANCHOR_STORE: Path = (
    Path(__file__).resolve().parent.parent / "aporia" / "calibration" /
    "battery_calibration.jsonl"
)
"""Default path to the calibration anchor JSONL store."""


DEFAULT_UNDER_ANCHORED_THRESHOLD: float = 0.1
"""Anchors-per-axis below this threshold (or count==0) flags the chart
as under-anchored. Conservative default per HARD-4 calibration-density
emphasis; zero-anchor charts always flag regardless of threshold."""


DEFAULT_REPORT_PATH: Path = (
    Path(__file__).resolve().parent / "ANCHOR_DENSITY_REPORT.md"
)


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CalibrationAnchor:
    """One anchor record loaded from the JSONL store. Free-form fields
    are kept for diagnostics; the matching logic uses only the named
    fields below."""

    anchor_id: str
    label: str
    structural_signature: str
    tag_set: Tuple[str, ...]
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CalibrationAnchor":
        return cls(
            anchor_id=str(d.get("anchor_id", "")),
            label=str(d.get("label", "")),
            structural_signature=str(d.get("structural_signature", "")),
            tag_set=tuple(str(t) for t in (d.get("tag_set") or [])),
            raw=dict(d),
        )


@dataclass(frozen=True)
class ChartAnchorMetrics:
    """Per-chart anchor density metrics."""

    chart_id: str
    domain: str
    region_key: str
    n_axes: int
    matched_anchor_ids: Tuple[str, ...]
    count: int
    per_axis_density: float
    under_anchored: bool


@dataclass(frozen=True)
class AnchorDensityReport:
    """Aggregate report across all registered charts."""

    n_charts_audited: int
    n_anchors_loaded: int
    threshold: float
    chart_metrics: Tuple[ChartAnchorMetrics, ...]
    under_anchored_chart_ids: Tuple[str, ...]
    n_anchors_unmatched: int
    unmatched_anchor_ids: Tuple[str, ...]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_anchors(store_path: Path) -> List[CalibrationAnchor]:
    """Load CalibrationAnchors from the JSONL store. Returns empty list
    if the file doesn't exist (treat absent store as zero anchors).
    Raises ValueError on malformed JSON within an existing file."""
    if not store_path.exists():
        return []
    out: List[CalibrationAnchor] = []
    with open(store_path, encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"malformed JSON in anchor store {store_path} at line {i}: {e}"
                ) from e
            if not isinstance(d, dict):
                raise ValueError(
                    f"anchor at {store_path}:{i} is not a JSON object; "
                    f"got {type(d).__name__}"
                )
            out.append(CalibrationAnchor.from_dict(d))
    return out


# ---------------------------------------------------------------------------
# Anchor-to-chart matching
# ---------------------------------------------------------------------------


def anchor_matches_chart(
    anchor: CalibrationAnchor,
    chart_domain: str,
    chart_region_key: str,
) -> bool:
    """Conservative-permissive match: anchor matches chart iff chart's
    domain or region_key first-segment appears in the anchor's
    structural_signature OR tag_set.

    Both arguments are passed as separate strings (not the chart object)
    to keep the matching logic pure / easy to test in isolation.
    """
    if not chart_domain:
        return False
    region_first_segment = chart_region_key.split(":", 1)[0] if chart_region_key else ""
    sig_lower = anchor.structural_signature.lower()
    tags_lower = {t.lower() for t in anchor.tag_set}
    domain_lower = chart_domain.lower()
    region_lower = region_first_segment.lower()
    if domain_lower and (domain_lower in sig_lower or domain_lower in tags_lower):
        return True
    if region_lower and (region_lower in sig_lower or region_lower in tags_lower):
        return True
    return False


# ---------------------------------------------------------------------------
# Core measurement
# ---------------------------------------------------------------------------


def measure_chart_anchor_density(
    chart: Any,  # CoordinateChart, but kept generic for testability
    anchors: Sequence[CalibrationAnchor],
    *,
    threshold: float = DEFAULT_UNDER_ANCHORED_THRESHOLD,
) -> ChartAnchorMetrics:
    """Measure anchor count + density for a single chart."""
    matched_ids: List[str] = []
    for a in anchors:
        if anchor_matches_chart(a, chart.domain, chart.region_key):
            matched_ids.append(a.anchor_id)
    n_axes = len(chart.coordinate_system) if chart.coordinate_system else 0
    density = len(matched_ids) / max(1, n_axes)
    under = (len(matched_ids) == 0) or (density < threshold)
    return ChartAnchorMetrics(
        chart_id=chart.chart_id,
        domain=chart.domain,
        region_key=chart.region_key,
        n_axes=n_axes,
        matched_anchor_ids=tuple(matched_ids),
        count=len(matched_ids),
        per_axis_density=density,
        under_anchored=under,
    )


def measure_all_chart_density(
    charts: Sequence[Any],  # Sequence[CoordinateChart]
    anchors: Sequence[CalibrationAnchor],
    *,
    threshold: float = DEFAULT_UNDER_ANCHORED_THRESHOLD,
) -> AnchorDensityReport:
    """Measure anchor density across a sequence of charts."""
    chart_metrics: List[ChartAnchorMetrics] = []
    matched_anchor_ids: set = set()
    for chart in charts:
        metrics = measure_chart_anchor_density(chart, anchors, threshold=threshold)
        chart_metrics.append(metrics)
        matched_anchor_ids.update(metrics.matched_anchor_ids)

    all_anchor_ids = {a.anchor_id for a in anchors}
    unmatched_ids = tuple(sorted(all_anchor_ids - matched_anchor_ids))
    under_ids = tuple(m.chart_id for m in chart_metrics if m.under_anchored)

    return AnchorDensityReport(
        n_charts_audited=len(chart_metrics),
        n_anchors_loaded=len(anchors),
        threshold=threshold,
        chart_metrics=tuple(chart_metrics),
        under_anchored_chart_ids=under_ids,
        n_anchors_unmatched=len(unmatched_ids),
        unmatched_anchor_ids=unmatched_ids,
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_report(report: AnchorDensityReport) -> str:
    lines: List[str] = []
    lines.append("# Calibration Anchor Density Report")
    lines.append("")
    lines.append(
        f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}_"
    )
    lines.append(
        "_Per inbox ticket T-2026-05-07-T036 "
        "(prometheus_math/anchor_density.py)_"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Charts audited:** {report.n_charts_audited}")
    lines.append(f"- **Anchors loaded:** {report.n_anchors_loaded}")
    lines.append(f"- **Under-anchored threshold (per-axis):** {report.threshold:.3f}")
    lines.append(f"- **Under-anchored charts:** {len(report.under_anchored_chart_ids)}")
    lines.append(f"- **Unmatched anchors (in store but not mapped to any chart):** {report.n_anchors_unmatched}")
    lines.append("")

    if report.n_charts_audited == 0:
        lines.append("## Result: No Registered Charts")
        lines.append("")
        lines.append(
            "No CoordinateCharts are currently registered against "
            "DEFAULT_REGISTRY. Audit cannot proceed without registered "
            "charts. (Did you forget to import "
            "`sigma_kernel.coordinate_charts` at startup? Chart "
            "registration is import-time-side-effect.)"
        )
        lines.append("")
        return "\n".join(lines)

    lines.append("## Per-Chart Metrics")
    lines.append("")
    lines.append(
        "| chart_id | domain | region_key | axes | anchors | density (per-axis) | flag |"
    )
    lines.append("|---|---|---|---:|---:|---:|---|")
    for m in report.chart_metrics:
        flag = "UNDER" if m.under_anchored else ""
        lines.append(
            f"| `{m.chart_id}` | `{m.domain}` | `{m.region_key}` | "
            f"{m.n_axes} | {m.count} | {m.per_axis_density:.3f} | {flag} |"
        )
    lines.append("")

    if report.under_anchored_chart_ids:
        lines.append("## Under-Anchored Charts (Substrate Finding)")
        lines.append("")
        lines.append(
            f"**{len(report.under_anchored_chart_ids)} chart(s) are "
            f"under-anchored** (count == 0 OR per-axis density < "
            f"{report.threshold:.3f}). Per HARD-4, calibration anchors "
            "are load-bearing infrastructure; under-anchored regions are "
            "epistemically blind. Recommend Aporia + Mnemosyne sourcing "
            "calibration anchors for these regions:"
        )
        lines.append("")
        for cid in report.under_anchored_chart_ids:
            lines.append(f"- `{cid}`")
        lines.append("")

    if report.n_anchors_unmatched > 0:
        lines.append("## Unmatched Anchors (Substrate Finding)")
        lines.append("")
        lines.append(
            f"**{report.n_anchors_unmatched} anchor(s) in the store do "
            "not match any registered chart** under the conservative-"
            "permissive heuristic (chart's domain or region_key first "
            "segment appears in the anchor's structural_signature or "
            "tag_set). Either: (a) the anchor schema needs an explicit "
            "`chart_id` field; or (b) the relevant chart isn't yet "
            "registered. Sample unmatched anchor ids:"
        )
        lines.append("")
        for aid in report.unmatched_anchor_ids[:20]:
            lines.append(f"- `{aid}`")
        if len(report.unmatched_anchor_ids) > 20:
            lines.append(
                f"- _...and {len(report.unmatched_anchor_ids) - 20} more_"
            )
        lines.append("")

    lines.append("## Caveats")
    lines.append("")
    lines.append(
        "1. **Conservative-permissive matching.** This audit uses substring "
        "matching on free-text fields because the anchor schema lacks an "
        "explicit `chart_id` field. False positives (anchor mapped to a "
        "chart it shouldn't be) and false negatives (anchor missed by "
        "matching) are both possible. Recommend Aporia file a follow-up "
        "ticket to add `chart_id` to the calibration anchor schema."
    )
    lines.append(
        "2. **Per-axis density is a proxy.** True volume normalization "
        "(volume of admissible region) is chart-specific and not generally "
        "computable. The per-axis-density metric is a comparable proxy "
        "across charts; a future Aporia ticket can extend with chart-"
        "specific volume estimators where they exist."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m prometheus_math.anchor_density",
        description=(
            "Measure calibration anchor density per registered "
            "CoordinateChart (T-2026-05-07-T036)."
        ),
    )
    parser.add_argument(
        "--anchor-store", type=Path, default=DEFAULT_ANCHOR_STORE,
        help=f"Path to anchor JSONL store. Default: {DEFAULT_ANCHOR_STORE.name}",
    )
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_UNDER_ANCHORED_THRESHOLD,
        help=(
            f"Per-axis density threshold for under-anchored flag. "
            f"Default: {DEFAULT_UNDER_ANCHORED_THRESHOLD}."
        ),
    )
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_REPORT_PATH,
        help=f"Markdown report output path. Default: {DEFAULT_REPORT_PATH.name}",
    )
    args = parser.parse_args(argv)

    # Trigger chart registration side-effects.
    import sigma_kernel.coordinate_charts  # noqa: F401
    from sigma_kernel.coordinate_chart import all_charts

    charts = all_charts()
    print(f"[anchor-density] {len(charts)} registered chart(s)", file=sys.stderr)

    anchors = load_anchors(args.anchor_store)
    print(
        f"[anchor-density] loaded {len(anchors)} anchor(s) from {args.anchor_store}",
        file=sys.stderr,
    )

    report = measure_all_chart_density(
        charts, anchors, threshold=args.threshold,
    )
    print(
        f"[anchor-density] under-anchored: {len(report.under_anchored_chart_ids)}, "
        f"unmatched: {report.n_anchors_unmatched}",
        file=sys.stderr,
    )

    md = render_report(report)
    args.out.write_text(md, encoding="utf-8")
    print(f"[anchor-density] report written: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "DEFAULT_ANCHOR_STORE",
    "DEFAULT_UNDER_ANCHORED_THRESHOLD",
    "DEFAULT_REPORT_PATH",
    "CalibrationAnchor",
    "ChartAnchorMetrics",
    "AnchorDensityReport",
    "load_anchors",
    "anchor_matches_chart",
    "measure_chart_anchor_density",
    "measure_all_chart_density",
    "render_report",
    "main",
]
