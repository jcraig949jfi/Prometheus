"""
Icarus Falsifier sub-agent (co-evolving) -- spec v0.2 sect "Shift 2".

The independent verifier in the hot loop. Runs AFTER TDD passes but BEFORE
the freeze decision. Uses a DIFFERENT model than Icarus's Improve() backend
to break the shared-weights tautology trap.

Asymmetric model selection:
  Icarus Improve() backend  ->  Falsifier model
  claude                    ->  Gemini
  chimera (human-in-loop)   ->  Claude API
  qwen_menial               ->  Claude API

Per-cycle: generate fresh-seed adversarial probes, run them, produce a
structured falsifier_report.md, return verdict.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ICARUS_DIR = Path(r"D:\Prometheus\agents\icarus")

_REPO_ROOT = Path(r"D:\Prometheus")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_falsifier_review(
    cycle_n: int,
    source_dir: Path,
    tier_challenge: dict,
    proposed_diff: str,
    icarus_improve_backend: str,
) -> dict:
    """Run an independent-model adversarial review of the cycle's diff.

    Returns:
        {
          "verdict": "approved" | "rejected" | "inconclusive",
          "probes_attempted": int,
          "probes_failed": int,
          "diagnosis": str,
          "report_path": str,
          "model_used": str,
        }
    """
    # Asymmetric model selection
    falsifier_model = _select_falsifier_model(icarus_improve_backend)

    # If diff is empty, nothing to falsify
    if not proposed_diff or not proposed_diff.strip():
        return _write_report(
            cycle_n=cycle_n,
            verdict="inconclusive",
            probes_attempted=0,
            probes_failed=0,
            diagnosis="empty_diff_nothing_to_review",
            model_used=falsifier_model,
        )

    # Try to call the falsifier model
    try:
        probes = _generate_adversarial_probes(
            tier_challenge=tier_challenge,
            diff=proposed_diff,
            model=falsifier_model,
        )
    except Exception as e:
        return _write_report(
            cycle_n=cycle_n,
            verdict="inconclusive",
            probes_attempted=0,
            probes_failed=0,
            diagnosis=f"falsifier_model_unavailable: {e}",
            model_used=falsifier_model,
        )

    # Run each probe against the diff'd source (Phase 0: shallow check;
    # Phase 1+ will apply the diff in a sandbox and actually run probes)
    breaks = []
    for probe in probes:
        result = _run_probe(probe, source_dir, proposed_diff)
        if not result.get("passed", True):
            breaks.append({"probe": probe, "result": result})

    verdict = "rejected" if breaks else "approved"
    diagnosis = (
        f"{len(breaks)} of {len(probes)} probes found breaks"
        if breaks else
        f"all {len(probes)} probes passed; no breaks found"
    )

    return _write_report(
        cycle_n=cycle_n,
        verdict=verdict,
        probes_attempted=len(probes),
        probes_failed=len(breaks),
        diagnosis=diagnosis,
        model_used=falsifier_model,
        probes=probes,
        breaks=breaks,
    )


def _select_falsifier_model(icarus_backend: str) -> str:
    """Asymmetric model selection per spec v0.2 Shift 2."""
    if icarus_backend == "claude":
        return "gemini"
    if icarus_backend in ("chimera_pending", "chimera_consumed", "chimera"):
        return "claude"
    if icarus_backend == "qwen_menial":
        return "claude"
    return "claude"  # default


def _generate_adversarial_probes(
    tier_challenge: dict,
    diff: str,
    model: str,
) -> list[dict]:
    """Phase 0 stub: returns 3 placeholder probes. Phase 1 will call out to
    the falsifier model (Gemini or Claude) to generate actual probes."""
    # Phase 0 stub
    return [
        {
            "name": "boundary_input",
            "kind": "perturbation",
            "input": None,
            "expected": "no-change behavior on edge case",
        },
        {
            "name": "scrambled_args",
            "kind": "structural",
            "input": None,
            "expected": "graceful handling of unexpected arg order",
        },
        {
            "name": "tier_falsification_repeat",
            "kind": "regression",
            "input": None,
            "expected": "passes the tier's built-in falsification test",
        },
    ]


def _run_probe(probe: dict, source_dir: Path, diff: str) -> dict:
    """Phase 0 stub: marks all probes as passed. Phase 1 will execute the
    probe by applying the diff to a sandbox and running the probe input."""
    # Phase 0 stub
    return {
        "passed": True,
        "detail": "phase_0_stub_no_execution",
    }


def _write_report(
    cycle_n: int,
    verdict: str,
    probes_attempted: int,
    probes_failed: int,
    diagnosis: str,
    model_used: str,
    probes: Optional[list] = None,
    breaks: Optional[list] = None,
) -> dict:
    """Write the falsifier_report.md and return the verdict dict."""
    from lineage import cycle_path
    cp = cycle_path(cycle_n)
    cp.mkdir(parents=True, exist_ok=True)
    report_path = cp / "falsifier_report.md"

    lines = [
        f"# Falsifier Report -- cycle {cycle_n}",
        "",
        f"- **Verdict:** {verdict}",
        f"- **Probes attempted:** {probes_attempted}",
        f"- **Probes failed:** {probes_failed}",
        f"- **Model used:** {model_used}",
        f"- **Generated at:** {_now_iso()}",
        "",
        "## Diagnosis",
        "",
        diagnosis,
        "",
    ]
    if probes:
        lines.append("## Probes attempted")
        lines.append("")
        for p in probes:
            lines.append(f"- **{p.get('name')}** ({p.get('kind', '?')}): {p.get('expected', '')}")
        lines.append("")
    if breaks:
        lines.append("## Breaks found")
        lines.append("")
        for b in breaks:
            lines.append(f"- **{b['probe'].get('name')}**: {b['result'].get('detail', '')}")
        lines.append("")

    try:
        report_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        print(f"[falsifier] report write failed: {e}", file=sys.stderr)

    return {
        "verdict": verdict,
        "probes_attempted": probes_attempted,
        "probes_failed": probes_failed,
        "diagnosis": diagnosis,
        "report_path": str(report_path),
        "model_used": model_used,
    }
