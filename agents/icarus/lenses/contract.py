"""
Contract Lens -- deterministic, non-LLM contract checker.

Per the 2026-05-28 review: pull one non-LLM lens forward from v3. The
Generator cannot model or game a deterministic checker the way it can game
an LLM evaluator, so this lens is a Goodhart-resistant evaluation channel.

It compares the candidate reasoner (cycle_N/code, diff already applied)
against the last-stable reasoner along structural contract axes:
  - cardinality preservation: does a list-returning method still return a
    list of the expected length? (this catches Cycle 14's apply_batch
    silently dropping entries)
  - type stability: does a method return the same type for the same input?
  - exception contract: does a method raise where it previously returned,
    or return where it previously raised?

Emits a machine-readable contract_report consumed by the panel + taxonomy.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from lenses._base import Lens, LensReport, CycleContext, SCORING_AXES


# Canonical probe battery for the arithmetic-reasoner domain. Each entry is
# (method_name, args_tuple). We run these against BOTH stable and candidate.
# apply_batch probes deliberately include distractor steps to surface
# cardinality changes.
_CONTRACT_PROBES = [
    ("apply", ({"op": "add", "a": 2, "b": 3},)),
    ("apply", ({"op": "mul", "a": 4, "b": 5},)),
    ("apply", ({"op": "sub", "a": 9, "b": 2},)),
    ("apply", ({"op": "add", "x": 7, "y": 1},)),       # renamed keys (R1)
    ("apply", ({},)),                                    # empty -> should be None
    ("apply", (None,)),                                  # non-dict -> None
    ("apply_batch", ([{"op": "add", "a": 1, "b": 2},
                       {"op": "mul", "a": 3, "b": 4},
                       {"op": "sub", "a": 9, "b": 5}],)),  # cardinality=3
    ("apply_batch", ([{"op": "add", "a": 1, "b": 2},
                       {"op": "distractor", "note": "ignore"},
                       {"op": "mul", "a": 3, "b": 4}],)),   # distractor in middle
    ("apply_batch", ([],)),                              # empty list
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_contract_check(candidate_dir: Path, stable_dir: Path) -> dict:
    """Compare candidate vs stable reasoner along contract axes.

    Returns a machine-readable contract_report:
      {
        "contract_violation": bool,
        "violation_subclass": str | None,
        "violations": [ {probe, axis, stable, candidate, detail} ],
        "probes_run": int,
        "methods_checked": [str],
        "note": str,
      }
    """
    if not candidate_dir.exists():
        return _empty_report("candidate_missing")
    if not stable_dir.exists():
        # No baseline to compare against (e.g., bootstrap). Self-consistency only.
        return _self_consistency_only(candidate_dir)

    violations = []
    methods_checked = set()
    probes_run = 0

    for method, args in _CONTRACT_PROBES:
        stable_res = _invoke(stable_dir, method, args)
        cand_res = _invoke(candidate_dir, method, args)
        # If the method doesn't exist in stable, it's new -- no contract to break
        if stable_res.get("missing_method"):
            continue
        # If it doesn't exist in candidate but did in stable -> removed method
        if cand_res.get("missing_method"):
            violations.append({
                "probe": f"{method}{_short(args)}",
                "axis": "method_removed",
                "stable": "present", "candidate": "absent",
                "detail": f"method '{method}' present in stable, removed in candidate",
            })
            methods_checked.add(method)
            continue

        methods_checked.add(method)
        probes_run += 1

        # Axis 1: cardinality preservation (list-returning methods)
        if stable_res.get("ok") and cand_res.get("ok"):
            s_val, c_val = stable_res.get("result"), cand_res.get("result")
            s_is_list = stable_res.get("is_list")
            c_is_list = cand_res.get("is_list")
            if s_is_list and c_is_list:
                if stable_res.get("length") != cand_res.get("length"):
                    violations.append({
                        "probe": f"{method}{_short(args)}",
                        "axis": "cardinality",
                        "stable": stable_res.get("length"),
                        "candidate": cand_res.get("length"),
                        "detail": (
                            f"{method} returned list of len {stable_res.get('length')} "
                            f"on stable but len {cand_res.get('length')} on candidate "
                            f"for same input -- alignment/cardinality contract break"
                        ),
                    })
            # Axis 2: type stability (scalar methods)
            elif not s_is_list and not c_is_list:
                if stable_res.get("rtype") != cand_res.get("rtype"):
                    # Allow None<->None; flag genuine type drift
                    if not (s_val is None and c_val is None):
                        violations.append({
                            "probe": f"{method}{_short(args)}",
                            "axis": "type_stability",
                            "stable": stable_res.get("rtype"),
                            "candidate": cand_res.get("rtype"),
                            "detail": (
                                f"{method} returned {stable_res.get('rtype')} on stable "
                                f"but {cand_res.get('rtype')} on candidate"
                            ),
                        })

        # Axis 3: exception contract
        s_raised = not stable_res.get("ok") and not stable_res.get("missing_method")
        c_raised = not cand_res.get("ok") and not cand_res.get("missing_method")
        if s_raised != c_raised:
            violations.append({
                "probe": f"{method}{_short(args)}",
                "axis": "exception_contract",
                "stable": "raised" if s_raised else "returned",
                "candidate": "raised" if c_raised else "returned",
                "detail": (
                    f"{method} exception behavior changed: "
                    f"stable {'raised' if s_raised else 'returned'}, "
                    f"candidate {'raised' if c_raised else 'returned'}"
                ),
            })

    violation = len(violations) > 0
    subclass = None
    if violation:
        # Pick the most severe subclass present
        axes_present = {v["axis"] for v in violations}
        if "cardinality" in axes_present:
            subclass = "input_output_alignment_lost"
        elif "method_removed" in axes_present:
            subclass = "input_output_alignment_lost"
        elif "exception_contract" in axes_present:
            subclass = "exception_contract_changed"
        elif "type_stability" in axes_present:
            subclass = "type_instability"

    return {
        "contract_violation": violation,
        "violation_subclass": subclass,
        "violations": violations,
        "probes_run": probes_run,
        "methods_checked": sorted(methods_checked),
        "note": "ok",
    }


def _self_consistency_only(candidate_dir: Path) -> dict:
    """When there's no stable baseline, just check the candidate doesn't
    crash on the probe battery + apply_batch preserves cardinality vs input."""
    violations = []
    for method, args in _CONTRACT_PROBES:
        res = _invoke(candidate_dir, method, args)
        if res.get("missing_method"):
            continue
        # apply_batch should return a list whose length matches the input list
        if method == "apply_batch" and res.get("ok") and res.get("is_list"):
            input_len = len(args[0]) if args and isinstance(args[0], list) else None
            if input_len is not None and res.get("length") != input_len:
                violations.append({
                    "probe": f"{method}{_short(args)}",
                    "axis": "cardinality",
                    "stable": input_len,
                    "candidate": res.get("length"),
                    "detail": (
                        f"apply_batch returned len {res.get('length')} for input "
                        f"of len {input_len} -- cardinality not preserved"
                    ),
                })
    violation = len(violations) > 0
    return {
        "contract_violation": violation,
        "violation_subclass": "input_output_alignment_lost" if violation else None,
        "violations": violations,
        "probes_run": len(_CONTRACT_PROBES),
        "methods_checked": [],
        "note": "self_consistency_only_no_stable_baseline",
    }


def _empty_report(note: str) -> dict:
    return {
        "contract_violation": False, "violation_subclass": None,
        "violations": [], "probes_run": 0, "methods_checked": [], "note": note,
    }


def _short(args) -> str:
    s = repr(args)
    return s if len(s) < 50 else s[:47] + "...)"


def _invoke(source_dir: Path, method: str, args: tuple) -> dict:
    """Subprocess-isolated call of Reasoner.<method>(*args). Returns a
    structural summary: ok, result, rtype, is_list, length, error,
    missing_method."""
    runner = (
        f"import json, sys\n"
        f"sys.path.insert(0, r'{source_dir}')\n"
        f"try:\n"
        f"    from reasoner import Reasoner\n"
        f"    r = Reasoner()\n"
        f"    if not hasattr(r, {method!r}):\n"
        f"        print(json.dumps({{'missing_method': True}})); sys.exit(0)\n"
        f"    fn = getattr(r, {method!r})\n"
        f"    out = fn(*{args!r})\n"
        f"    is_list = isinstance(out, (list, tuple))\n"
        f"    print(json.dumps({{\n"
        f"        'ok': True,\n"
        f"        'rtype': type(out).__name__,\n"
        f"        'is_list': is_list,\n"
        f"        'length': (len(out) if is_list else None),\n"
        f"        'result': (out if (out is None or isinstance(out, (int,float,str,bool))) else str(out)),\n"
        f"    }}, default=str))\n"
        f"except Exception as e:\n"
        f"    print(json.dumps({{'ok': False, 'error': str(e), 'error_type': type(e).__name__}}))\n"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", runner],
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode != 0:
            return {"ok": False, "error": proc.stderr[:200], "error_type": "subprocess_error"}
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception as e:
        return {"ok": False, "error": str(e), "error_type": "runner_error"}


class ContractLens(Lens):
    """Deterministic contract lens. Wraps run_contract_check in a LensReport
    so it integrates with the panel, and exposes the raw contract_report via
    suggested_actions[0] for the taxonomy + Integrator."""
    name = "contract"
    model_preference = "deterministic"  # no LLM

    def observe(self, ctx: CycleContext) -> LensReport:
        stable_dir = _stable_code_dir(ctx)
        report = run_contract_check(ctx.source_dir, stable_dir)

        violation = report.get("contract_violation", False)
        n_viol = len(report.get("violations", []))

        # Axes: a contract violation tanks regression_risk + evidence_quality.
        axes = {a: 0.7 for a in SCORING_AXES}
        if violation:
            axes["regression_risk"] = 0.05   # 1=LOW risk; violation = HIGH risk
            axes["evidence_quality"] = 0.2
            axes["structural_simplicity"] = 0.4
        confidence = 1.0  # deterministic; we are certain of what we measured

        observations = [f"contract_violation={violation}",
                        f"probes_run={report.get('probes_run')}",
                        f"methods_checked={report.get('methods_checked')}"]
        for v in report.get("violations", [])[:4]:
            observations.append(f"VIOLATION[{v['axis']}]: {v['detail'][:160]}")

        summary = (
            f"Deterministic contract check: {n_viol} violation(s) across "
            f"{report.get('probes_run')} probes. "
            + ("CONTRACT BREAK DETECTED." if violation else "No contract breaks.")
        )

        return LensReport(
            lens_name=self.name,
            model_used="deterministic",
            cycle_n=ctx.cycle_n,
            ts=_now_iso(),
            qualitative_summary=summary,
            axes=axes,
            confidence=confidence,
            key_observations=observations[:8],
            minority_position=(
                report["violations"][0]["detail"] if violation else None
            ),
            suggested_actions=[json.dumps(report, default=str)],
            tokens_used=0,
            cost_estimate_usd=0.0,
        )


def _stable_code_dir(ctx: CycleContext) -> Path:
    """Locate the last-stable cycle's code/ dir for comparison."""
    cycles_dir = Path(r"D:\Prometheus\agents\icarus\cycles")
    stable_id = ctx.last_stable_id
    p = cycles_dir / f"cycle_{stable_id}" / "code"
    return p
