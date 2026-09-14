"""CORONER RUN executor (LAYER: NECROPOLIS VALIDATION).  See CORONER_RUN.md.

Refuses to execute anything that is not an APPROVED plan with an operator
approval record (R-CR-3), refuses any plan carrying a DEAD_BEFORE_RUN
disposition or whose bytes drifted from the fingerprint it was disposed
under (R-CR-2), requires descendants to cite their parent by plan_id AND
hash, re-fingerprints the plan's inputs, and confines writes to the plan's
run directory.  `--dry-run` (the default) checks a plan and prints what
WOULD execute; nothing runs.

    python engine/necropolis/workshop/coroner_run.py coroner_plans/CR-001_pollux_frank004.json
    python engine/necropolis/workshop/coroner_run.py <plan> --execute   # needs APPROVED + operator approval record
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
PLAN_STATUS = {"PROPOSED", "APPROVED", "REJECTED", "EXECUTED"}      # written in the plan file
DISPOSITIONS = {"DEAD_BEFORE_RUN", "SUPERSEDED", "WITHDRAWN"}       # written beside it, never in it
# Names that cannot appear as the authorizing party of an approval record (R-CR-3):
# agents recommend, operators approve.
AGENT_ROLES = {"rhadamanthus", "necromancer", "cleric", "techne", "frankenstein", "coroner", "keeper",
               "hephaestus", "mnemosyne", "daedalus", "aletheia", "nemesis", "pronoia", "coeus", "agent", "claude"}


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


def load_dispositions(plan_dir: Path) -> list[dict]:
    p = plan_dir / "DISPOSITIONS.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def known_plan_hashes(plan_dir: Path) -> dict[str, set[str]]:
    """plan_id -> set of hashes under which that plan is on record (dispositions + freeze records + current bytes)."""
    out: dict[str, set[str]] = {}
    for d in load_dispositions(plan_dir):
        out.setdefault(d["plan_id"], set()).add(d["plan_sha256_lf"])
    for fz in sorted(HERE.glob("FREEZE_*.json")):
        try:
            rec = json.load(open(fz, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for rel, want in rec.get("files", {}).items():
            if rel.startswith("coroner_plans/") and rel.endswith(".json"):
                pid = Path(rel).name.split("_")[0]
                out.setdefault(pid, set()).add(want["sha256_lf"])
    for pf in sorted(plan_dir.glob("CR-*.json")):
        out.setdefault(pf.name.split("_")[0], set()).add(sha256_lf(pf)[0])
    return out


def disposition_for(plan: dict, plan_path: Path) -> tuple[dict | None, list[str]]:
    """The disposition record governing this plan file, plus any identity violations."""
    errs = []
    cur, _ = sha256_lf(plan_path)
    mine = [d for d in load_dispositions(plan_path.parent) if d.get("plan_id") == plan.get("plan_id")]
    for d in mine:
        if d.get("plan_sha256_lf") != cur:
            errs.append(f"plan bytes drifted from disposition {d.get('disposition_id')} (disposed {d.get('plan_sha256_lf', '')[:12]}, "
                        f"now {cur[:12]}): a plan repaired in place has lost its identity (R-CR-2); refile as a descendant")
        if d.get("plan_modified_in_place") is not False:
            errs.append(f"disposition {d.get('disposition_id')} does not assert plan_modified_in_place == false")
    return (mine[-1] if mine else None), errs


def check_plan(plan: dict, plan_path: Path | None = None) -> list[str]:
    """Structural refusals.  Returns a list of reasons; empty means the plan is well-formed."""
    errs = []
    for k in ("plan_id", "question", "target", "target_grave", "invocation", "hitl_status", "inputs", "tools",
              "actions", "controls", "kill_criteria", "expected_outputs", "non_resurrection_argument"):
        if k not in plan:
            errs.append(f"missing field {k}")
    if errs:
        return errs
    if plan["hitl_status"] not in PLAN_STATUS:
        errs.append(f"hitl_status {plan['hitl_status']!r} is not one of {sorted(PLAN_STATUS)} "
                    "(DEAD_BEFORE_RUN lives in DISPOSITIONS.jsonl, never in the plan file)")
    reg = load_registry()
    for tid in plan["tools"]:
        row = reg.get(tid, {})
        st = row.get("necropolis_status")
        adm = row.get("admissibility") or {}
        if st not in RUNNABLE:
            errs.append(f"tool {tid} is {st}; only READY / READY_WITH_CAVEAT may be invoked")
        elif not adm.get("admissible"):
            # the status string is not the authority; the measured ladder is
            errs.append(f"tool {tid} is {st} but not forensically admissible (blocked_by={adm.get('blocked_by')})")
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
    # descendants (CORONER_RUN.md section 7, D4): parent cited by plan_id AND sha256_lf, hash on record
    par = plan.get("parent_plan")
    if par is not None:
        if not isinstance(par, dict) or not par.get("plan_id") or not par.get("sha256_lf"):
            errs.append("parent_plan must be {plan_id, sha256_lf}")
        elif plan_path is not None:
            known = known_plan_hashes(plan_path.parent)
            if par["plan_id"] not in known:
                errs.append(f"parent_plan {par['plan_id']} is not on record in coroner_plans/")
            elif par["sha256_lf"] not in known[par["plan_id"]]:
                errs.append(f"parent_plan {par['plan_id']} hash {par['sha256_lf'][:12]} matches no disposition, freeze record or plan file")
            if par["plan_id"] == plan["plan_id"]:
                errs.append("a descendant must receive a new plan_id (R-CR-2)")
    if plan_path is not None:
        _, derrs = disposition_for(plan, plan_path)
        errs.extend(derrs)
    return errs


def check_approval(plan: dict, plan_path: Path) -> list[str]:
    """R-CR-3: the approval record must exist, bind to these plan bytes, and name an operator, not an agent."""
    errs = []
    appr = plan.get("approval") or {}
    rec = appr.get("record")
    if not rec:
        return ["approval.record missing"]
    rp = REPO / rec
    if not rp.exists():
        rp = plan_path.parent / Path(rec).name
    if not rp.exists():
        return [f"approval.record does not resolve: {rec}"]
    try:
        r = json.loads(rp.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"approval record unreadable: {e}"]
    for k in ("plan_id", "plan_sha256_lf", "authorized_by", "authorization_source", "authorized", "recorded_by"):
        if not r.get(k):
            errs.append(f"approval record missing {k}")
    if errs:
        return errs
    if r["plan_id"] != plan["plan_id"]:
        errs.append(f"approval record is for {r['plan_id']}, not {plan['plan_id']}")
    cur, _ = sha256_lf(plan_path)
    if r["plan_sha256_lf"] != cur:
        errs.append(f"approval binds plan hash {r['plan_sha256_lf'][:12]}, plan is now {cur[:12]}: re-approval required")
    who = str(r["authorized_by"]).strip().lower()
    if any(tok in AGENT_ROLES for tok in who.replace("(", " ").replace(")", " ").replace("/", " ").split()):
        errs.append(f"approval record authorized_by {r['authorized_by']!r} names an agent role; agents may not manufacture execution authority (R-CR-3)")
    return errs


def gate(plan: dict, plan_path: Path) -> list[str]:
    errs = []
    disp, derrs = disposition_for(plan, plan_path)
    errs.extend(derrs)
    if disp is not None and disp.get("disposition") in DISPOSITIONS:
        errs.append(f"plan is disposed {disp['disposition']} ({disp.get('disposition_id')}, ruled_by {disp.get('ruled_by')}); execution refused")
    if plan.get("hitl_status") != "APPROVED":
        errs.append(f"hitl_status is {plan.get('hitl_status')}; execution refused")
    errs.extend(check_approval(plan, plan_path))
    return errs


def execute(plan: dict, plan_path: Path) -> Path:
    run_dir = plan_path.parent / plan["plan_id"] / "runs" / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_dir.mkdir(parents=True, exist_ok=False)
    reg = load_registry()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True).stdout.strip()
    result = {"plan_id": plan["plan_id"], "plan_sha256_lf": sha256_lf(plan_path)[0], "git_head": head, "python": sys.version,
              "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "approval_record": (plan.get("approval") or {}).get("record"),
              "inputs": [{**i, "sha256_lf_at_run": sha256_lf(REPO / i["path"])[0]} for i in plan["inputs"]],
              "tools": {t: {"source_commit": reg[t]["source_commit"], "necropolis_status": reg[t]["necropolis_status"],
                            "admissibility": reg[t].get("admissibility"), "caveat": reg[t].get("caveat")} for t in plan["tools"]},
              "registry_sha256_lf": sha256_lf(HERE / "TOOLS.jsonl")[0],
              "steps": []}
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
    ap.add_argument("--execute", action="store_true", help="execute (requires APPROVED + operator approval record, no disposition)")
    a = ap.parse_args(argv)
    plan_path = Path(a.plan).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errs = check_plan(plan, plan_path)
    for e in errs:
        print("PLAN-ERROR", e)
    if errs:
        return 2
    disp, _ = disposition_for(plan, plan_path)
    print("plan well-formed:", plan["plan_id"], "|", len(plan["actions"]), "actions |", "hitl_status", plan["hitl_status"],
          "| disposition", disp["disposition"] if disp else "none")
    if plan.get("pre_run_findings"):
        print("PRE-RUN FINDINGS present:", len(plan["pre_run_findings"]), "(read before approving)")
    if plan.get("parent_plan"):
        print("descendant of", plan["parent_plan"]["plan_id"], plan["parent_plan"]["sha256_lf"][:12])
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
