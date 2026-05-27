"""Stygian executor -- bridges attack_plan to v10 battery execution.

Reads a problem dict (BL-C-* or HECATE-*), looks up its loader, runs
the battery, and emits a kill_ledger row in Theseus's schema so
Hecate's gradient-archaeology pipeline consumes it without changes.

Per pivot/stygian_executor_scoping_2026-05-21.md MVP1.

Hard stops (NOT negotiated):
- v10 battery FROZEN; this module is read-only consumer of
  cartography/shared/scripts/battery_unified.py.
- No --writeable; no multiprocessing scaling; no LoRA.

Currently shipped:
- BL-C-001 (Lehmer) loader registered; full executor path lit.
- HECATE-* problems short-circuit with verdict="UNVERIFIED" and
  kill_pattern="stygian_hecate_meta_test_not_yet_implemented".
- Other BL-C-* problems (002-010) short-circuit with
  verdict="UNVERIFIED" and kill_pattern="stygian_no_loader_registered".

The short-circuit rows still emit to kill_ledger so Hecate sees the
attempted attacks even when execution is deferred. SELF_AUDIT_NULL
discipline per Stygian CHARTER -- silent ticks are forbidden.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from charon.agents.stygian.loaders import get_loader
from harmonia.agents._base import REPO_ROOT

# Make cartography/shared/scripts importable for the battery
_BATTERY_DIR = REPO_ROOT / "cartography" / "shared" / "scripts"
if str(_BATTERY_DIR) not in sys.path:
    sys.path.insert(0, str(_BATTERY_DIR))

KILL_LEDGER_PATH = (
    REPO_ROOT / "charon" / "agents" / "stygian" / "state" / "kill_ledger.jsonl"
)

# Per-tick wall-clock budget for battery execution. Battery itself
# enforces no timeout internally; if a single problem exceeds this
# budget Stygian still emits a row (with kill_pattern recording the
# overrun) and the executor returns. MVP1 budget; raise once async
# state machine ships in MVP2.
BATTERY_TIMEOUT_SEC = 60.0


def _json_safe(o):
    """Coerce numpy scalars/arrays + other non-JSON types to native Python.
    Used as `default=` for json.dumps so battery results (which can
    include np.bool_, np.int64, np.ndarray) serialize cleanly."""
    try:
        import numpy as np  # type: ignore
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.ndarray,)):
            return o.tolist()
    except Exception:
        pass
    # Pythonic fallbacks
    if isinstance(o, (set, frozenset)):
        return list(o)
    return str(o)


def _record_id(payload: dict) -> str:
    """Content-addressed record id matching Theseus's hashing convention.

    Theseus uses sha256 of canonical-claim-text + emitted_at + a salt;
    we use sha256 of the JSON payload sorted-keys for determinism.
    """
    blob = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, default=_json_safe
    ).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _emit_kill_ledger_row(row: dict) -> Path:
    """Append a kill_ledger row to Stygian's local ledger file. The shape
    matches Theseus's batch records so Hecate's gradient-archaeology
    consumer reads both ledgers identically."""
    KILL_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with KILL_LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=_json_safe) + "\n")
    return KILL_LEDGER_PATH


def _classify_verdict_to_pattern(
    overall: dict, tests: dict
) -> tuple[str, Optional[str]]:
    """Map the battery's overall classification to (verdict, kill_pattern).

    verdict matches Theseus's vocabulary: PROMOTED, REJECTED, UNVERIFIED.
    kill_pattern is None on PROMOTED, otherwise a specific failure-mode
    string suitable for Hecate's clustering.
    """
    overall_verdict = (overall or {}).get("verdict", "UNKNOWN")
    if overall_verdict in ("PASS", "PROMOTED", "SURVIVES"):
        return "PROMOTED", None
    if overall_verdict in ("FAIL", "KILLED", "REJECTED"):
        # Identify the FIRST failing sub-test for the kill_pattern label;
        # additional failures stay in the kill_vector blob.
        for tname in sorted(tests.keys()):
            tdict = tests.get(tname) or {}
            tv = tdict.get("verdict", "")
            if tv in ("FAIL", "KILLED", "REJECTED"):
                return "REJECTED", f"stygian_{tname.lower()}_failed"
        return "REJECTED", "stygian_battery_failed_unidentified_test"
    return "UNVERIFIED", f"stygian_battery_verdict_{overall_verdict.lower()}"


def execute_attack(problem: dict, attack_plan_path: Optional[str] = None) -> dict:
    """Execute the v10 battery against a problem; emit a kill_ledger row.

    Returns a stats dict for Stygian.run_tick to merge:
      {executor_invoked, battery_mode, battery_verdict, battery_elapsed_sec,
       kill_ledger_row_id, executor_skip_reason}
    """
    problem_id = problem.get("id", "UNKNOWN")
    stats: dict[str, Any] = {
        "executor_invoked": True,
        "battery_mode": None,
        "battery_verdict": None,
        "battery_elapsed_sec": None,
        "kill_ledger_row_id": None,
        "executor_skip_reason": None,
    }

    # ---- HECATE-* meta-test: deferred (per scoping doc) -------------
    if problem_id.startswith("HECATE-"):
        return _emit_short_circuit_row(
            problem=problem,
            attack_plan_path=attack_plan_path,
            kill_pattern="stygian_hecate_meta_test_not_yet_implemented",
            reason="hecate_meta_test_deferred_to_mvp2",
            stats=stats,
        )

    # ---- EREBOS-* composed-claim validation -------------------------
    # v0.10 SPIKE (task #37): composition-aware loaders. Protocol in
    # charon/agents/stygian/loaders/_composition.py + concrete loaders
    # registered via @register decorator. If a loader is registered
    # for THIS specific Erebos composition payload, run it; otherwise
    # fall through to short-circuit (UNVERIFIED row so Hecate still
    # sees the composer's contribution to the ledger).
    if problem_id.startswith("EREBOS-"):
        try:
            # Force-import the composition loader module(s) to trigger
            # @register side-effects. Add new composition loaders here
            # as they ship.
            import charon.agents.stygian.loaders.composition_g02_lehmer_salem  # noqa: F401
            import charon.agents.stygian.loaders.composition_g09_lehmer_ablation  # noqa: F401
            import charon.agents.stygian.loaders.composition_g25_lehmer_degenerate  # noqa: F401
            import charon.agents.stygian.loaders.composition_g02_g04_lehmer_tightened  # noqa: F401
            import charon.agents.stygian.loaders.composition_g02_g04_lehmer_band_high  # noqa: F401
            import charon.agents.stygian.loaders.composition_g02_lehmer_smyth  # noqa: F401
            import charon.agents.stygian.loaders.composition_g02_lehmer_degree_parity  # noqa: F401
            import charon.agents.stygian.loaders.composition_g03_lehmer_neighborhood  # noqa: F401
            import charon.agents.stygian.loaders.composition_g10_lehmer_threshold_sweep  # noqa: F401
            import charon.agents.stygian.loaders.composition_g16_lehmer_extremum  # noqa: F401
            import charon.agents.stygian.loaders.composition_g18_lehmer_degree_band  # noqa: F401
            import charon.agents.stygian.loaders.composition_g19_ledger_transitivity  # noqa: F401
            import charon.agents.stygian.loaders.composition_g24_lehmer_x_flip  # noqa: F401
            from charon.agents.stygian.loaders._composition import find_loader
        except Exception as e:
            return _emit_short_circuit_row(
                problem=problem,
                attack_plan_path=attack_plan_path,
                kill_pattern="stygian_erebos_composition_import_failed",
                reason=f"composition_loader_module_import: {e}",
                stats=stats,
            )
        queue_payload = problem.get("_queue_payload", {}) or {}
        loader = find_loader(queue_payload)
        if loader is None:
            return _emit_short_circuit_row(
                problem=problem,
                attack_plan_path=attack_plan_path,
                kill_pattern="stygian_erebos_composed_loader_pending",
                reason="no_composition_loader_for_this_erebos_payload",
                stats=stats,
            )
        # Composition loader exists -- run it end-to-end
        return _execute_composition_attack(
            problem=problem,
            attack_plan_path=attack_plan_path,
            loader=loader,
            queue_payload=queue_payload,
            stats=stats,
        )

    # ---- POLLUX-* survivor validation: deferred ---------------------
    # Pollux fed a PROMOTED pair into the queue (survived mean-spacing
    # normalization). The right v10 attack is to load the same pair's
    # values and run test_distribution / test_correlation on them. A
    # dedicated loader belongs in loaders/pollux_survivor.py; for now
    # we emit a typed UNVERIFIED row so Pollux's contribution to the
    # ledger is visible and Hecate sees a 'stygian saw pollux's pair'
    # entry.
    if problem_id.startswith("POLLUX-"):
        return _emit_short_circuit_row(
            problem=problem,
            attack_plan_path=attack_plan_path,
            kill_pattern="stygian_pollux_survivor_loader_pending",
            reason="pollux_survivor_loader_not_yet_implemented",
            stats=stats,
        )

    # ---- BL-C-* with no loader: short-circuit -----------------------
    loader = get_loader(problem_id)
    if loader is None:
        return _emit_short_circuit_row(
            problem=problem,
            attack_plan_path=attack_plan_path,
            kill_pattern="stygian_no_loader_registered",
            reason=f"no_loader_for_{problem_id}",
            stats=stats,
        )

    # ---- Load battery inputs ---------------------------------------
    try:
        loader_result = loader()
    except Exception as e:
        return _emit_short_circuit_row(
            problem=problem,
            attack_plan_path=attack_plan_path,
            kill_pattern="stygian_loader_failed",
            reason=f"loader_exception: {e}",
            stats=stats,
        )

    mode = loader_result.get("mode")
    stats["battery_mode"] = mode

    # ---- Invoke UnifiedBattery -------------------------------------
    t0 = time.time()
    try:
        from battery_unified import UnifiedBattery  # type: ignore
        ub = UnifiedBattery()
        finding_id = f"stygian_{problem_id}_{uuid.uuid4().hex[:8]}"
        if mode == "distribution":
            battery_result = ub.test_distribution(
                finding_id=finding_id,
                claim=loader_result["claim"],
                values=loader_result.get("values"),
                predicted_value=loader_result.get("predicted_value"),
                data_source=loader_result.get("data_source", ""),
                domain_is_multiplicative=loader_result.get(
                    "domain_is_multiplicative", False
                ),
                synthetic_generator=loader_result.get("synthetic_generator"),
                group_labels=loader_result.get("group_labels"),
                confound_values=loader_result.get("confound_values"),
                X_for_regression=loader_result.get("X_for_regression"),
                Y_for_regression=loader_result.get("Y_for_regression"),
                notes=loader_result.get("notes", ""),
            )
        elif mode == "correlation":
            battery_result = ub.test_correlation(
                finding_id=finding_id,
                claim=loader_result["claim"],
                values_a=loader_result.get("values_a"),
                values_b=loader_result.get("values_b"),
                data_source=loader_result.get("data_source", ""),
                confounds=loader_result.get("confounds"),
                dose_levels=loader_result.get("dose_levels"),
                dose_labels=loader_result.get("dose_labels"),
                subgroups=loader_result.get("subgroups"),
                n_hypotheses_tested=loader_result.get("n_hypotheses_tested", 3),
                index_values=loader_result.get("index_values"),
                notes=loader_result.get("notes", ""),
            )
        else:
            return _emit_short_circuit_row(
                problem=problem,
                attack_plan_path=attack_plan_path,
                kill_pattern="stygian_loader_invalid_mode",
                reason=f"loader_returned_unknown_mode: {mode}",
                stats=stats,
            )
    except Exception as e:
        return _emit_short_circuit_row(
            problem=problem,
            attack_plan_path=attack_plan_path,
            kill_pattern="stygian_battery_exception",
            reason=f"battery_exception: {e}",
            stats=stats,
        )
    elapsed = time.time() - t0
    stats["battery_elapsed_sec"] = round(elapsed, 3)

    # ---- Convert to kill_ledger row (Theseus shape) ----------------
    overall = battery_result.get("overall", {}) or {}
    tests = battery_result.get("tests", {}) or {}
    verdict, kill_pattern = _classify_verdict_to_pattern(overall, tests)
    stats["battery_verdict"] = verdict

    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "problem_id": problem_id,
        "claim": loader_result["claim"],
        "battery_finding_id": finding_id,
        "emitted_at": now_iso,
        "tests": tests,
        "overall": overall,
    }
    record_id = _record_id(payload)
    row = {
        # Theseus-compatible fields (so Hecate consumes uniformly)
        "batch_id": f"stygian-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "record_id": record_id,
        "canonical_claim_text": loader_result["claim"],
        "claim_kind": "stygian_battery_attack",
        "claim_payload": {
            "problem_id": problem_id,
            "problem_name": problem.get("name"),
            "hardness": problem.get("hardness"),
            "domain": problem.get("domain"),
            "mode": mode,
        },
        "convergence_status": "exact" if verdict == "PROMOTED" else "approximate",
        "diversity_score": None,
        "emitted_at": now_iso,
        "extras": {
            "battery_elapsed_sec": stats["battery_elapsed_sec"],
            "n_samples": battery_result.get("n_samples"),
            "tier": overall.get("tier"),
            "attack_plan_path": attack_plan_path,
            "queue_row_id": problem.get("_queue_row_id"),
            "queue_source": problem.get("_queue_source"),
        },
        "generator_id": "stygian",  # new operator-class for Hecate's MI
        "info_density": None,
        "kill_pattern": kill_pattern,
        "kill_vector": {
            "battery_finding_id": finding_id,
            "overall": overall,
            "tests": tests,
            "predicted_value": loader_result.get("predicted_value"),
            "notes": loader_result.get("notes", ""),
        },
        "method": "v10_battery",
        "novelty_estimate": None,
        "parent_record_id": None,
        "precision_dps": None,
        "sigma_claim_id": None,
        "sigma_symbol_ref": None,
        "step_trace": None,
        "training_weight": None,
        "verdict": verdict,
    }
    _emit_kill_ledger_row(row)
    stats["kill_ledger_row_id"] = record_id
    return stats


def _execute_composition_attack(
    problem: dict,
    attack_plan_path: Optional[str],
    loader,
    queue_payload: dict,
    stats: dict,
) -> dict:
    """Run a composition-aware loader end-to-end; emit a kill_ledger
    row with the loader's verdict. Per v0.10 SPIKE (task #37); first
    EREBOS-* row to get a REAL battery verdict instead of short-
    circuit short_circuit."""
    stats["executor_invoked"] = True
    stats["battery_mode"] = "composition"
    stats["composition_loader_id"] = getattr(loader, "composition_id", "?")
    t0 = time.time()
    try:
        result_dict = loader.build_battery_input(queue_payload)
    except Exception as e:
        return _emit_short_circuit_row(
            problem=problem,
            attack_plan_path=attack_plan_path,
            kill_pattern="stygian_composition_loader_exception",
            reason=f"composition_loader_exception: {e}",
            stats=stats,
        )
    elapsed = time.time() - t0
    stats["battery_elapsed_sec"] = round(elapsed, 3)

    result = result_dict.get("result", {}) or {}
    verdict = result.get("verdict", "UNVERIFIED")
    kill_pattern = result.get("kill_pattern")
    stats["battery_verdict"] = verdict
    if kill_pattern:
        stats["battery_kill_pattern"] = kill_pattern

    now_iso = datetime.now(timezone.utc).isoformat()
    composed_id = result_dict.get("composed_id", problem.get("id", "?"))
    payload_hash_input = {
        "composed_id": composed_id,
        "loader_id": loader.composition_id,
        "verdict": verdict,
        "result": result,
        "emitted_at": now_iso,
    }
    record_id = _record_id(payload_hash_input)
    row = {
        "batch_id": f"stygian-comp-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "record_id": record_id,
        "canonical_claim_text": result_dict.get("claim", "")[:500],
        "claim_kind": "stygian_composition_attack",
        "claim_payload": {
            "problem_id": problem.get("id"),
            "composed_id": composed_id,
            "composition_loader_id": loader.composition_id,
            "data_source": result_dict.get("data_source", ""),
        },
        "convergence_status": "composition_validated",
        "diversity_score": None,
        "emitted_at": now_iso,
        "extras": {
            "attack_plan_path": attack_plan_path,
            "queue_row_id": problem.get("_queue_row_id"),
            "queue_source": problem.get("_queue_source"),
            "composition_result": result,
            "notes": result_dict.get("notes", ""),
            "battery_elapsed_sec": stats["battery_elapsed_sec"],
        },
        "generator_id": "stygian",
        "info_density": None,
        "kill_pattern": kill_pattern,  # None on PROMOTED, else the failure mode
        "kill_vector": {
            "loader_id": loader.composition_id,
            "verdict": verdict,
            "result": result,
        },
        "method": f"composition_{loader.composition_id}",
        "novelty_estimate": None,
        "parent_record_id": queue_payload.get("erebos_ledger_row_id"),
        "precision_dps": 4,
        "sigma_claim_id": None,
        "sigma_symbol_ref": None,
        "step_trace": None,
        "training_weight": None,
        "verdict": verdict,
    }
    _emit_kill_ledger_row(row)
    stats["kill_ledger_row_id"] = record_id
    return stats


def _emit_short_circuit_row(
    problem: dict,
    attack_plan_path: Optional[str],
    kill_pattern: str,
    reason: str,
    stats: dict,
) -> dict:
    """Emit an UNVERIFIED kill_ledger row when execution is skipped.

    Per SELF_AUDIT_NULL discipline: silent ticks are forbidden. Even a
    deferred-execution path produces a typed substrate row Hecate can
    see.
    """
    stats["executor_skip_reason"] = reason
    stats["battery_verdict"] = "UNVERIFIED"
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "problem_id": problem.get("id"),
        "kill_pattern": kill_pattern,
        "reason": reason,
        "emitted_at": now_iso,
    }
    record_id = _record_id(payload)
    row = {
        "batch_id": f"stygian-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "record_id": record_id,
        "canonical_claim_text": f"Stygian attempted attack on {problem.get('id')}; execution skipped ({reason})",
        "claim_kind": "stygian_battery_attack",
        "claim_payload": {
            "problem_id": problem.get("id"),
            "problem_name": problem.get("name"),
            "skip_reason": reason,
        },
        "convergence_status": "skipped",
        "diversity_score": None,
        "emitted_at": now_iso,
        "extras": {
            "attack_plan_path": attack_plan_path,
            "queue_row_id": problem.get("_queue_row_id"),
            "queue_source": problem.get("_queue_source"),
        },
        "generator_id": "stygian",
        "info_density": None,
        "kill_pattern": kill_pattern,
        "kill_vector": None,
        "method": "stygian_short_circuit",
        "novelty_estimate": None,
        "parent_record_id": None,
        "precision_dps": None,
        "sigma_claim_id": None,
        "sigma_symbol_ref": None,
        "step_trace": None,
        "training_weight": None,
        "verdict": "UNVERIFIED",
    }
    _emit_kill_ledger_row(row)
    stats["kill_ledger_row_id"] = record_id
    return stats
