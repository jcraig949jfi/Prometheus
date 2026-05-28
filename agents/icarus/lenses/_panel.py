"""
Icarus lens panel orchestrator.

Runs lenses in topological order:
  Phase A (parallel):   Diagnostician + Historian
  Phase B:              Generator  (sees A's outputs)
  --- infra ---
  Phase C:              Apply diff (patcher)
  Phase D:              TDD        (tdd_runner)
  --- back to lenses ---
  Phase E:              Skeptic    (sees applied code + TDD)
  Phase F:              Integrator (synthesizes everything)

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ICARUS_DIR = Path(r"D:\Prometheus\agents\icarus")

_REPO_ROOT = Path(r"D:\Prometheus")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(ICARUS_DIR) not in sys.path:
    sys.path.insert(0, str(ICARUS_DIR))

from lenses._base import (
    Lens, LensReport, CycleContext, SCORING_AXES,
    write_lens_report, axes_summary, lens_agreement_patterns,
)
from lenses.diagnostician import DiagnosticianLens
from lenses.historian import HistorianLens
from lenses.generator import GeneratorLens
from lenses.skeptic import SkepticLens
from lenses.integrator import IntegratorLens
from lenses.contract import ContractLens


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_lens_panel(
    ctx: CycleContext,
    cycle_dir: Path,
    apply_fn,           # patcher.apply_diff
    tdd_fn,             # tdd_runner.run_all_tests
    emit_event_fn=None,
) -> dict:
    """Execute all lenses + infrastructure phases. Returns:
        {
          "decision": "mark_stable" | "park",
          "load_bearing_lens": str,
          "rationale": str,
          "lens_reports": dict[str, LensReport],
          "axes_summary": dict,
          "agreement_patterns": dict,
          "apply_result": dict,
          "tdd_result": dict,
        }
    """
    lens_reports: dict[str, LensReport] = {}

    # ---- Phase A: Diagnostician + Historian in parallel -----------------
    _emit(emit_event_fn, "phase_a_start", ctx.cycle_n, {})
    with ThreadPoolExecutor(max_workers=2) as ex:
        fut_diag = ex.submit(_safe_observe, DiagnosticianLens(), ctx)
        fut_hist = ex.submit(_safe_observe, HistorianLens(), ctx)
        diag_report = fut_diag.result(timeout=120)
        hist_report = fut_hist.result(timeout=120)
    ctx.diagnostician_report = diag_report
    ctx.historian_report = hist_report
    lens_reports["diagnostician"] = diag_report
    lens_reports["historian"] = hist_report
    write_lens_report(diag_report, cycle_dir)
    write_lens_report(hist_report, cycle_dir)
    _emit(emit_event_fn, "phase_a_complete", ctx.cycle_n, {
        "diag_confidence": diag_report.confidence,
        "hist_confidence": hist_report.confidence,
    })

    # ---- Phase B: Generator (informed by A) -----------------------------
    _emit(emit_event_fn, "phase_b_start", ctx.cycle_n, {})
    gen_report = _safe_observe(GeneratorLens(), ctx)
    ctx.generator_report = gen_report
    lens_reports["generator"] = gen_report
    write_lens_report(gen_report, cycle_dir)
    # Extract proposed diff from generator
    ctx.proposed_diff = (gen_report.suggested_actions[0]
                         if gen_report.suggested_actions else "")
    _emit(emit_event_fn, "phase_b_complete", ctx.cycle_n, {
        "diff_lines": len((ctx.proposed_diff or "").splitlines()),
        "gen_confidence": gen_report.confidence,
    })

    # ---- Phase C: apply diff --------------------------------------------
    apply_result = {"applied": False, "reason": "no_diff", "files_changed": []}
    if ctx.proposed_diff and ctx.proposed_diff.strip():
        apply_result = apply_fn(ctx.proposed_diff, ctx.source_dir)
    ctx.apply_result = apply_result
    ctx.diff_applied = bool(apply_result.get("applied"))
    _emit(emit_event_fn, "phase_c_complete", ctx.cycle_n, {
        "applied": ctx.diff_applied,
        "reason": apply_result.get("reason"),
    })

    # ---- Phase D: TDD ---------------------------------------------------
    if ctx.diff_applied or not (ctx.proposed_diff or "").strip():
        tdd_result = tdd_fn(
            source_dir=ctx.source_dir,
            cycle_n=ctx.cycle_n,
            tier_target=ctx.tier_target,
        )
    else:
        tdd_result = {
            "all_passed": False,
            "per_source": {},
            "note": "diff_apply_failed_skipping_tdd",
            "regression_clean": False,
        }
    ctx.tdd_result = tdd_result
    _emit(emit_event_fn, "phase_d_complete", ctx.cycle_n, {
        "all_passed": tdd_result.get("all_passed"),
    })

    # ---- Phase D.5: Contract Lens (deterministic, runs whenever a diff applied) ----
    if ctx.diff_applied:
        contract_lens_report = _safe_observe(ContractLens(), ctx)
        # The raw machine-readable report is in suggested_actions[0]
        try:
            import json as _json
            ctx.contract_report = _json.loads(contract_lens_report.suggested_actions[0])
        except Exception:
            ctx.contract_report = None
    else:
        contract_lens_report = LensReport(
            lens_name="contract", model_used="deterministic",
            cycle_n=ctx.cycle_n, ts=_now_iso(),
            qualitative_summary="Contract check skipped: no diff applied.",
            axes={a: 0.5 for a in SCORING_AXES}, confidence=1.0,
        )
        ctx.contract_report = None
    ctx.contract_lens_report = contract_lens_report
    lens_reports["contract"] = contract_lens_report
    write_lens_report(contract_lens_report, cycle_dir)
    _emit(emit_event_fn, "phase_d5_complete", ctx.cycle_n, {
        "contract_violation": (ctx.contract_report or {}).get("contract_violation"),
    })

    # ---- Phase E: Skeptic (only if there's something to be skeptical about) ----
    if ctx.diff_applied:
        skeptic_report = _safe_observe(SkepticLens(), ctx)
    else:
        skeptic_report = LensReport(
            lens_name="skeptic",
            model_used="n/a_no_applied_diff",
            cycle_n=ctx.cycle_n,
            ts=_now_iso(),
            qualitative_summary=(
                "Skeptic skipped: no diff was applied (apply failed or empty). "
                "No applied code to be skeptical about."
            ),
            axes={"tier_proximity": 0.0, "novelty": 0.0,
                  "regression_risk": 0.0, "structural_simplicity": 0.0,
                  "evidence_quality": 0.0},
            confidence=1.0,  # confident the skip is correct
        )
    ctx.skeptic_report = skeptic_report
    lens_reports["skeptic"] = skeptic_report
    write_lens_report(skeptic_report, cycle_dir)
    _emit(emit_event_fn, "phase_e_complete", ctx.cycle_n, {
        "skeptic_confidence": skeptic_report.confidence,
        "minority": skeptic_report.minority_position is not None,
    })

    # ---- Phase F: Integrator (synthesis) --------------------------------
    integ_report = _safe_observe(IntegratorLens(), ctx)
    ctx.integrator_report = integ_report
    lens_reports["integrator"] = integ_report
    write_lens_report(integ_report, cycle_dir)

    # Decision emerges from Integrator's load-bearing citation.
    # We require the Integrator to specify in suggested_actions:
    #   suggested_actions[0] = "mark_stable" or "park"
    #   suggested_actions[1] = which lens it weighted highest
    #   suggested_actions[2..] = additional rationale
    decision = "park"  # default
    load_bearing = "integrator"
    rationale = integ_report.qualitative_summary[:300]
    if integ_report.suggested_actions:
        first = integ_report.suggested_actions[0].strip().lower()
        if first in ("mark_stable", "promote", "stable"):
            decision = "mark_stable"
        elif first in ("park", "reject", "regress"):
            decision = "park"
        if len(integ_report.suggested_actions) > 1:
            load_bearing = integ_report.suggested_actions[1]

    # Hard guards: even if Integrator says stable, override if any of:
    if decision == "mark_stable":
        if not ctx.diff_applied:
            decision = "park"
            rationale = "[guard] integrator said stable but diff did not apply"
        elif not tdd_result.get("all_passed"):
            decision = "park"
            rationale = "[guard] integrator said stable but TDD failed"

    summary = axes_summary(list(lens_reports.values()))
    agreement = lens_agreement_patterns(list(lens_reports.values()))

    return {
        "decision": decision,
        "load_bearing_lens": load_bearing,
        "rationale": rationale,
        "lens_reports": {name: r.to_dict() for name, r in lens_reports.items()},
        "axes_summary": summary,
        "agreement_patterns": agreement,
        "apply_result": apply_result,
        "tdd_result": tdd_result,
    }


def _safe_observe(lens: Lens, ctx: CycleContext) -> LensReport:
    """Call lens.observe with belt-and-suspenders error handling.
    A lens that raises is replaced with an error-typed LensReport so the
    panel can continue. Per James's principle: a parked cycle is still a
    multi-perspective observation."""
    try:
        report = lens.observe(ctx)
        if not isinstance(report, LensReport):
            return LensReport.empty_with_error(
                lens_name=lens.name, cycle_n=ctx.cycle_n,
                error=f"lens returned {type(report).__name__}, expected LensReport",
            )
        return report
    except Exception as e:
        return LensReport.empty_with_error(
            lens_name=lens.name, cycle_n=ctx.cycle_n,
            error=f"{type(e).__name__}: {e}",
        )


def _emit(emit_event_fn, name: str, cycle_n: int, payload: dict) -> None:
    """Per-phase telemetry. Suppressed in current version because the shared
    Harmonia emit_event helper rejects unknown event classes -- per-phase
    detail already lives in the cycle's log.jsonl + per-lens reports."""
    return
