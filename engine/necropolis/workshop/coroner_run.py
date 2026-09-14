"""CORONER RUN executor (LAYER: NECROPOLIS VALIDATION).  See CORONER_RUN.md.

Refuses to execute anything that is not an APPROVED plan with an approval
record, re-fingerprints the plan's inputs, and confines writes to the
plan's run directory.  `--dry-run` (the default) checks a plan and prints
what WOULD execute; nothing runs.

    python engine/necropolis/workshop/coroner_run.py coroner_plans/CR-001_pollux_frank004.json
    python engine/necropolis/workshop/coroner_run.py <plan> --execute   # needs hitl_status APPROVED + approval file
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MAY = {f"M{i}" for i in range(1, 11)}
RUNNABLE = {"READY", "READY_WITH_CAVEAT"}


def sha256_lf(path: Path) -> tuple[str, int]:
    b = path.read_bytes()
    if b"\0" not in b[:4096]:
        b = b.replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest(), len(b)


def load_registry() -> dict[str, dict]:
    p = HERE / "TOOLS.jsonl"
    if not p.exists():
        return {}
    return {r["tool_id"]: r for r in (json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip())}


def check_plan(plan: dict) -> list[str]:
    """Structural refusals.  Returns a list of reasons; empty means the plan is well-formed."""
    errs = []
    for k in ("plan_id", "question", "target", "target_grave", "invocation", "hitl_status", "inputs", "tools",
              "actions", "controls", "kill_criteria", "expected_outputs", "non_resurrection_argument"):
        if k not in plan:
            errs.append(f"missing field {k}")
    if errs:
        return errs
    reg = load_registry()
    for tid in plan["tools"]:
        st = reg.get(tid, {}).get("necropolis_status")
        if st not in RUNNABLE:
            errs.append(f"tool {tid} is {st}; only READY / READY_WITH_CAVEAT may be invoked")
    for a in plan["actions"]:
        if a.get("may") not in MAY:
            errs.append(f"action {a.get('step')} names no MAY clause (got {a.get('may')!r})")
        if a.get("tool_id") and a["tool_id"] not in plan["tools"]:
            errs.append(f"action {a.get('step')} uses undeclared tool {a['tool_id']}")
        w = a.get("writes")
        if w and not str(w).startswith("<run_dir>"):
            errs.append(f"action {a.get('step')} writes outside <run_dir>: {w}")
    for inp in plan["inputs"]:
        p = REPO / inp["path"]
        if not p.exists():
            errs.append(f"input missing: {inp['path']}")
            continue
        h, n = sha256_lf(p)
        if inp.get("sha256_lf") and inp["sha256_lf"] != h:
            errs.append(f"input fingerprint mismatch: {inp['path']} (plan {inp['sha256_lf'][:12]}, now {h[:12]})")
    nra = plan["non_resurrection_argument"]
    if isinstance(nra, dict):
        for x in (f"X{i}" for i in range(1, 9)):
            if x not in nra:
                errs.append(f"non_resurrection_argument does not address {x}")
    return errs


def gate(plan: dict, plan_path: Path) -> list[str]:
    errs = []
    if plan.get("hitl_status") != "APPROVED":
        errs.append(f"hitl_status is {plan.get('hitl_status')}; execution refused")
    appr = plan.get("approval") or {}
    rec = appr.get("record")
    if not rec or not (REPO / rec).exists():
        errs.append("approval.record missing or does not resolve")
    return errs


def execute(plan: dict, plan_path: Path) -> Path:
    run_dir = plan_path.parent / plan["plan_id"] / "runs" / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_dir.mkdir(parents=True, exist_ok=False)
    reg = load_registry()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True).stdout.strip()
    result = {"plan_id": plan["plan_id"], "git_head": head, "python": sys.version, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "inputs": [{**i, "sha256_lf_at_run": sha256_lf(REPO / i["path"])[0]} for i in plan["inputs"]],
              "tools": {t: reg[t]["source_commit"] for t in plan["tools"]}, "steps": []}
    sys.path.insert(0, str(REPO))
    for a in plan["actions"]:
        step = {"step": a["step"], "may": a["may"], "tool_id": a.get("tool_id")}
        t0 = time.time()
        try:
            mod = importlib.import_module(a["module"])
            fn = getattr(mod, a["function"])
            kwargs = dict(a.get("kwargs", {}))
            for k, v in list(kwargs.items()):
                if isinstance(v, str) and v.startswith("<run_dir>"):
                    kwargs[k] = str(run_dir / v[len("<run_dir>/"):])
            out = fn(**kwargs)
            step["ok"] = True
            step["output"] = out if isinstance(out, (dict, list, str, int, float, bool, type(None))) else repr(out)[:2000]
        except Exception as e:  # noqa: BLE001
            step["ok"] = False
            step["error"] = repr(e)[:500]
        step["seconds"] = round(time.time() - t0, 2)
        result["steps"].append(step)
        (run_dir / "RESULT.json").write_text(json.dumps(result, indent=1, default=str), encoding="utf-8", newline="\n")
    result["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (run_dir / "RESULT.json").write_text(json.dumps(result, indent=1, default=str), encoding="utf-8", newline="\n")
    return run_dir


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--execute", action="store_true", help="execute (requires APPROVED + approval record)")
    a = ap.parse_args(argv)
    plan_path = Path(a.plan).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errs = check_plan(plan)
    for e in errs:
        print("PLAN-ERROR", e)
    if errs:
        return 2
    print("plan well-formed:", plan["plan_id"], "|", len(plan["actions"]), "actions |", "hitl_status", plan["hitl_status"])
    if plan.get("pre_run_findings"):
        print("PRE-RUN FINDINGS present:", len(plan["pre_run_findings"]), "(read before approving)")
    if not a.execute:
        for act in plan["actions"]:
            print("  would run", act["step"], act["may"], act.get("tool_id"), act.get("module"), act.get("function"))
        return 0
    g = gate(plan, plan_path)
    for e in g:
        print("GATE-REFUSED", e)
    if g:
        return 3
    run_dir = execute(plan, plan_path)
    print("run dir", run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
