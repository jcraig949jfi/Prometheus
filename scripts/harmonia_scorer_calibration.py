"""
Harmonia scorer calibration watchdog.

Daily watchdog that exercises each Harmonia child-agent's auto-promotion
pipeline against a fixed calibration set of positive and negative anchors.
On drift -- a positive anchor that fails to auto-promote OR a negative
anchor that *does* auto-promote -- the watchdog calls
`pipeline.quiesce(reason)` and emits a `scorer_self_quiesce` event so the
conductor reviews before any further promotion runs.

Spec: D:\\Prometheus\\harmonia\\agents\\AUTOPROMOTION_TARGETS.md (Phase 0
tool #3 of 4). Locked interface: D:\\Prometheus\\harmonia\\agents\\_scorer.py.

Per-pipeline anchor files live at:
    D:\\Prometheus\\harmonia\\agents\\<name>\\state\\calibration_positive.json
    D:\\Prometheus\\harmonia\\agents\\<name>\\state\\calibration_negative.json

Each is a list[CalibrationCase] of the form:

    {
      "name": "anchor_F001_passes_with_score_above_2",
      "candidate": { /* the candidate dict the pipeline's scorer expects */ },
      "expected_auto_promote": true,
      "rationale": "F001 modularity should pass Iris's symbol candidate check"
    }

A pipeline that does not exist yet (no `_pipeline.py` under the agent dir)
is reported as `pipeline_status: not_yet_built` and skipped without error
-- Phase 0 ships the foundation; pipeline subclasses land in Phase 1+.

CLI:
    python D:\\Prometheus\\scripts\\harmonia_scorer_calibration.py
    python D:\\Prometheus\\scripts\\harmonia_scorer_calibration.py --json
    python D:\\Prometheus\\scripts\\harmonia_scorer_calibration.py --pipeline iris
    python D:\\Prometheus\\scripts\\harmonia_scorer_calibration.py --dry-run
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Locked-interface import -- fail fast with a clear message if unavailable.
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from harmonia.agents._scorer import (  # type: ignore
        HarmoniaScorer,
        CandidateVerdict,
        AGENTS_DIR,
        EVENTS_JSONL,
        emit_event,
        EVENT_CALIBRATION_RUN,
    )
except Exception as e:  # pragma: no cover -- import-time failure path
    sys.stderr.write(
        "[harmonia_scorer_calibration] FATAL: failed to import the locked "
        "scorer interface from D:\\Prometheus\\harmonia\\agents\\_scorer.py: "
        f"{e}\n"
    )
    raise SystemExit(2)


AGENT_NAMES = ("phylax", "sophia", "iris", "argos", "telos")


# ---------------------------------------------------------------------------
# Per-pipeline calibration-case dataclass
# ---------------------------------------------------------------------------

@dataclass
class CalibrationCase:
    """One anchor in the calibration set.

    See module docstring for the on-disk JSON shape under
    D:\\Prometheus\\harmonia\\agents\\<name>\\state\\calibration_*.json.
    """
    name: str
    candidate: dict
    expected_auto_promote: bool
    rationale: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "CalibrationCase":
        return cls(
            name=str(d.get("name", "<unnamed>")),
            candidate=dict(d.get("candidate") or {}),
            expected_auto_promote=bool(d.get("expected_auto_promote", False)),
            rationale=str(d.get("rationale", "")),
        )


@dataclass
class PipelineReport:
    """Per-pipeline result row for the watchdog markdown report."""
    pipeline: str
    pipeline_status: str  # "ran" | "not_yet_built" | "load_error" | "empty"
    anchors_tested: int = 0
    positives_correct: int = 0
    positives_total: int = 0
    negatives_correct: int = 0
    negatives_total: int = 0
    failures: list[dict] = field(default_factory=list)
    quiesced: bool = False
    error: Optional[str] = None

    @property
    def overall_pass(self) -> bool:
        if self.pipeline_status != "ran":
            # Non-ran statuses do not fail the watchdog; they're reported.
            return True
        return not self.failures


# ---------------------------------------------------------------------------
# Pipeline discovery
# ---------------------------------------------------------------------------

def _pipeline_path(agent_name: str) -> Path:
    return AGENTS_DIR / agent_name / "_pipeline.py"


def _load_pipeline_class(agent_name: str):
    """Import `harmonia/agents/<name>/_pipeline.py` and return its `Pipeline`
    class iff that class subclasses `HarmoniaScorer`. Returns None if the
    file does not exist (Phase 0 normal state). Raises on import errors
    so the watchdog can report them as `load_error`.
    """
    path = _pipeline_path(agent_name)
    if not path.exists():
        return None
    mod_name = f"_harmonia_calib_{agent_name}"
    spec = importlib.util.spec_from_file_location(mod_name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(
            f"could not build import spec for {path}"
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    cls = getattr(module, "Pipeline", None)
    if cls is None:
        raise AttributeError(
            f"{path} does not expose a `Pipeline` class"
        )
    if not (isinstance(cls, type) and issubclass(cls, HarmoniaScorer)):
        raise TypeError(
            f"{path}:Pipeline does not subclass HarmoniaScorer"
        )
    return cls


# ---------------------------------------------------------------------------
# Anchor file loading
# ---------------------------------------------------------------------------

def _anchor_path(agent_name: str, polarity: str) -> Path:
    return AGENTS_DIR / agent_name / "state" / f"calibration_{polarity}.json"


def _load_anchors(agent_name: str, polarity: str) -> tuple[list[CalibrationCase], Optional[str]]:
    """Load positive or negative anchors. Returns (cases, error). If the
    file does not exist, returns ([], None) (empty is normal). If the file
    exists but is malformed, returns ([], error_message).
    """
    p = _anchor_path(agent_name, polarity)
    if not p.exists():
        return [], None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return [], f"json parse error at {p}: {e}"
    if not isinstance(data, list):
        return [], f"expected list at {p}, got {type(data).__name__}"
    cases: list[CalibrationCase] = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            return [], f"entry {i} in {p} is not a dict"
        try:
            cases.append(CalibrationCase.from_dict(entry))
        except Exception as e:
            return [], f"entry {i} in {p} malformed: {e}"
    return cases, None


def _build_calibration_set(agent_name: str) -> tuple[list[CalibrationCase], list[CalibrationCase], list[str]]:
    """Return (positives, negatives, load_errors)."""
    errors: list[str] = []
    pos, err = _load_anchors(agent_name, "positive")
    if err:
        errors.append(err)
    neg, err = _load_anchors(agent_name, "negative")
    if err:
        errors.append(err)
    # Enforce expected polarity at the case level; warn (but don't crash)
    # if an anchor file mislabels polarity.
    for c in pos:
        if not c.expected_auto_promote:
            errors.append(
                f"positive-anchor file lists case '{c.name}' with "
                f"expected_auto_promote=False; ignoring polarity mismatch"
            )
    for c in neg:
        if c.expected_auto_promote:
            errors.append(
                f"negative-anchor file lists case '{c.name}' with "
                f"expected_auto_promote=True; ignoring polarity mismatch"
            )
    return pos, neg, errors


# ---------------------------------------------------------------------------
# Per-case evaluation
# ---------------------------------------------------------------------------

def _evaluate_case(pipeline: HarmoniaScorer, case: CalibrationCase) -> tuple[bool, Optional[str]]:
    """Run one case through `pipeline.evaluate_batch([case.candidate], k=1)`.

    Returns (passed, failure_description). `passed` is True iff the
    observed auto_promote matches `case.expected_auto_promote`.
    """
    try:
        verdicts: list[CandidateVerdict] = pipeline.evaluate_batch(
            [case.candidate], k=1
        )
    except Exception as e:
        return False, f"evaluate_batch raised: {e!r}"

    # auto_promote is True iff the candidate appears in the returned
    # promote-eligible verdicts AND has auto_promote=True. evaluate_batch
    # only returns promote-eligible verdicts, so any returned verdict for
    # our candidate implies promotion. An empty result means rejected.
    observed_promote = False
    for v in verdicts:
        if v.candidate is case.candidate and v.auto_promote:
            observed_promote = True
            break

    if observed_promote == case.expected_auto_promote:
        return True, None

    expected_str = "auto_promote" if case.expected_auto_promote else "reject"
    observed_str = "auto_promote" if observed_promote else "reject"
    return False, (
        f"anchor '{case.name}': expected {expected_str}, observed "
        f"{observed_str} (rationale: {case.rationale or 'n/a'})"
    )


def _run_pipeline(agent_name: str, dry_run: bool) -> PipelineReport:
    """Run the calibration set for one pipeline. Always produces a
    PipelineReport; never raises (errors are reported in the row)."""
    report = PipelineReport(pipeline=agent_name, pipeline_status="ran")

    # --- discover the pipeline class
    try:
        cls = _load_pipeline_class(agent_name)
    except Exception as e:
        report.pipeline_status = "load_error"
        report.error = f"{type(e).__name__}: {e}"
        emit_event(
            EVENT_CALIBRATION_RUN,
            {
                "pipeline": agent_name,
                "pipeline_status": "load_error",
                "anchors_tested": 0,
                "positives_correct": 0,
                "negatives_correct": 0,
                "failures": [report.error],
                "quiesced": False,
                "dry_run": dry_run,
            },
            agent=agent_name,
        )
        return report

    if cls is None:
        report.pipeline_status = "not_yet_built"
        emit_event(
            EVENT_CALIBRATION_RUN,
            {
                "pipeline": agent_name,
                "pipeline_status": "not_yet_built",
                "anchors_tested": 0,
                "positives_correct": 0,
                "negatives_correct": 0,
                "failures": [],
                "quiesced": False,
                "dry_run": dry_run,
            },
            agent=agent_name,
        )
        return report

    # --- instantiate the pipeline
    try:
        pipeline = cls()
    except Exception as e:
        report.pipeline_status = "load_error"
        report.error = f"instantiation failed: {type(e).__name__}: {e}"
        emit_event(
            EVENT_CALIBRATION_RUN,
            {
                "pipeline": agent_name,
                "pipeline_status": "load_error",
                "anchors_tested": 0,
                "positives_correct": 0,
                "negatives_correct": 0,
                "failures": [report.error],
                "quiesced": False,
                "dry_run": dry_run,
            },
            agent=agent_name,
        )
        return report

    # --- load anchors
    positives, negatives, anchor_errors = _build_calibration_set(agent_name)
    for ae in anchor_errors:
        report.failures.append({"kind": "anchor_load_warning", "detail": ae})

    if not positives and not negatives:
        report.pipeline_status = "empty"
        emit_event(
            EVENT_CALIBRATION_RUN,
            {
                "pipeline": agent_name,
                "pipeline_status": "empty",
                "anchors_tested": 0,
                "positives_correct": 0,
                "negatives_correct": 0,
                "failures": [],
                "quiesced": False,
                "dry_run": dry_run,
                "note": "calibration_set_empty -- no anchor files at "
                        f"D:\\Prometheus\\harmonia\\agents\\{agent_name}\\state\\",
            },
            agent=agent_name,
        )
        return report

    # --- run positives
    report.positives_total = len(positives)
    for case in positives:
        passed, failure = _evaluate_case(pipeline, case)
        if passed:
            report.positives_correct += 1
        else:
            report.failures.append({
                "kind": "positive_anchor_failed",
                "case": case.name,
                "detail": failure or "",
            })

    # --- run negatives
    report.negatives_total = len(negatives)
    for case in negatives:
        passed, failure = _evaluate_case(pipeline, case)
        if passed:
            report.negatives_correct += 1
        else:
            report.failures.append({
                "kind": "negative_anchor_failed",
                "case": case.name,
                "detail": failure or "",
            })

    report.anchors_tested = report.positives_total + report.negatives_total

    # --- quiesce on any drift
    if report.failures and not dry_run:
        try:
            reason = (
                f"calibration drift: {len(report.failures)} anchor(s) failed. "
                f"First failure: {report.failures[0].get('detail', '')[:200]}"
            )
            pipeline.quiesce(reason=reason)
            report.quiesced = True
        except Exception as e:
            report.failures.append({
                "kind": "quiesce_error",
                "detail": f"{type(e).__name__}: {e}",
            })

    # --- emit one calibration_run event per pipeline
    emit_event(
        EVENT_CALIBRATION_RUN,
        {
            "pipeline": agent_name,
            "pipeline_status": report.pipeline_status,
            "anchors_tested": report.anchors_tested,
            "positives_correct": report.positives_correct,
            "positives_total": report.positives_total,
            "negatives_correct": report.negatives_correct,
            "negatives_total": report.negatives_total,
            "failures": report.failures,
            "quiesced": report.quiesced,
            "dry_run": dry_run,
            "pass": not report.failures,
        },
        agent=agent_name,
    )

    return report


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _markdown_report(reports: list[PipelineReport], dry_run: bool) -> str:
    lines: list[str] = []
    lines.append("# Harmonia scorer calibration -- watchdog report")
    lines.append("")
    lines.append(
        f"Mode: {'DRY-RUN (no quiesce flags written)' if dry_run else 'live'}"
    )
    lines.append(
        "Spec: D:\\Prometheus\\harmonia\\agents\\AUTOPROMOTION_TARGETS.md"
    )
    lines.append(
        "Interface: D:\\Prometheus\\harmonia\\agents\\_scorer.py"
    )
    lines.append("")
    lines.append(
        "| pipeline | status | anchors | pos | neg | failures | quiesced |"
    )
    lines.append(
        "|---|---|---|---|---|---|---|"
    )
    any_fail = False
    for r in reports:
        if r.pipeline_status == "ran" and r.failures:
            any_fail = True
        pos = f"{r.positives_correct}/{r.positives_total}"
        neg = f"{r.negatives_correct}/{r.negatives_total}"
        n_fail = sum(
            1 for f in r.failures
            if f.get("kind") in ("positive_anchor_failed", "negative_anchor_failed")
        )
        lines.append(
            f"| {r.pipeline} | {r.pipeline_status} | {r.anchors_tested} | "
            f"{pos} | {neg} | {n_fail} | {r.quiesced} |"
        )
    lines.append("")
    lines.append(
        f"**Overall:** {'FAIL -- one or more pipelines quiesced' if any_fail else 'PASS'}"
    )
    lines.append("")
    # Failure detail
    for r in reports:
        if not r.failures and r.pipeline_status in ("ran", "empty", "not_yet_built"):
            continue
        lines.append(f"### {r.pipeline} ({r.pipeline_status})")
        if r.error:
            lines.append(f"- error: `{r.error}`")
        for f in r.failures:
            lines.append(
                f"- {f.get('kind', '?')}: {f.get('case', '')} -- {f.get('detail', '')}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _json_report(reports: list[PipelineReport], dry_run: bool) -> str:
    overall_pass = all(r.overall_pass for r in reports)
    payload = {
        "spec": "D:\\Prometheus\\harmonia\\agents\\AUTOPROMOTION_TARGETS.md",
        "interface": "D:\\Prometheus\\harmonia\\agents\\_scorer.py",
        "dry_run": dry_run,
        "overall_pass": overall_pass,
        "pipelines": [
            {
                "pipeline": r.pipeline,
                "pipeline_status": r.pipeline_status,
                "anchors_tested": r.anchors_tested,
                "positives_correct": r.positives_correct,
                "positives_total": r.positives_total,
                "negatives_correct": r.negatives_correct,
                "negatives_total": r.negatives_total,
                "failures": r.failures,
                "quiesced": r.quiesced,
                "error": r.error,
            }
            for r in reports
        ],
    }
    return json.dumps(payload, indent=2, default=str)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Harmonia scorer calibration watchdog. Runs each pipeline's "
            "anchor set; quiesces drifters."
        )
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit JSON instead of markdown (for CI / cron consumers)",
    )
    parser.add_argument(
        "--pipeline",
        choices=AGENT_NAMES,
        help="restrict to a single pipeline",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="do not write quiesce flags; just report",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    targets = (args.pipeline,) if args.pipeline else AGENT_NAMES

    reports: list[PipelineReport] = []
    for name in targets:
        try:
            reports.append(_run_pipeline(name, dry_run=args.dry_run))
        except Exception as e:  # pragma: no cover -- defensive
            tb = traceback.format_exc()
            sys.stderr.write(
                f"[harmonia_scorer_calibration] unexpected error for "
                f"pipeline '{name}': {e}\n{tb}\n"
            )
            reports.append(PipelineReport(
                pipeline=name,
                pipeline_status="load_error",
                error=f"unexpected: {type(e).__name__}: {e}",
            ))

    if args.json:
        sys.stdout.write(_json_report(reports, dry_run=args.dry_run) + "\n")
    else:
        sys.stdout.write(_markdown_report(reports, dry_run=args.dry_run))

    # Exit-code: 0 if all reports pass or are non-ran statuses; 1 if any
    # pipeline that actually ran failed its anchors.
    any_ran_failure = any(
        r.pipeline_status == "ran" and r.failures for r in reports
    )
    return 1 if any_ran_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
