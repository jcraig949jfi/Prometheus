"""Execute one candidate implementation for a wall in a subprocess and emit JSON.

    python -m hephaestus.src.run_candidate <wall_id> <candidate.py> <out.json>

The candidate must define `op_<wall_id>(state)`. Static gate first (AST allowlist), then the
wall's harness (train/holdout metrics, boundary false-commit, input mutants). Never trusts
the candidate's explanation; only its executed behaviour.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ALLOWED_MODULES = {"re", "math", "itertools", "collections", "functools", "string", "typing",
                   "dataclasses", "forge_primitives", "blackboard"}
FORBIDDEN_NAMES = {"exec", "eval", "open", "compile", "__import__", "globals", "locals",
                   "getattr", "setattr", "delattr", "input", "breakpoint", "exit", "quit"}
FORBIDDEN_ATTRS = {"system", "popen", "spawn", "fork", "remove", "unlink", "rmdir", "socket"}


def static_gate(src: str) -> list[str]:
    problems: list[str] = []
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED_MODULES:
                    problems.append(f"import not allowed: {a.name}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_MODULES:
                problems.append(f"import not allowed: from {node.module}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            problems.append(f"forbidden name: {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRS:
            problems.append(f"forbidden attribute: .{node.attr}")
    if "def op_" not in src:
        problems.append("no `def op_<wall>` found")
    return problems


def main() -> int:
    wall_id, cand_path, out_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    src = cand_path.read_text(encoding="utf-8")
    result: dict = {"wall": wall_id, "candidate": str(cand_path), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    gate = static_gate(src)
    result["static_gate"] = gate
    if gate:
        result["verdict"] = "STATIC_REJECT"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 0
    wall = importlib.import_module(f"hephaestus.src.wall_{wall_id}")
    spec = importlib.util.spec_from_file_location("candidate_mod", cand_path)
    mod = importlib.util.module_from_spec(spec)
    for p in (ROOT / "apollo" / "src", ROOT / "agents" / "hephaestus" / "src"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception as e:  # noqa: BLE001
        result["verdict"] = "IMPORT_ERROR"
        result["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 0
    op = getattr(mod, f"op_{wall_id}", None)
    if op is None:
        result["verdict"] = "NO_OP_FUNCTION"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 0
    ex = wall.build_examples()
    train, hold = wall.split(ex)
    tr = wall.evaluate(op, train)
    ho = wall.evaluate(op, hold)
    mut = wall.input_mutants(op, ex)
    result.update({"train": tr["metrics"], "holdout": ho["metrics"], "input_mutants": mut,
                   "holdout_records": ho["records"]})
    m = ho["metrics"]
    mut_ok = all(v["passed"] == v["of"] for v in mut.values())
    iv = sum(1 for r in ho["records"] if (r.get("error") or "").startswith("InterfaceViolation"))
    if iv == len(hold):
        result["verdict"] = "INTERFACE_VIOLATION"
        result["failure_families"] = ["returns_value_instead_of_state"]
    elif m["errors"] == len(hold):
        result["verdict"] = "RUNTIME_ERROR_ALL"
        result["failure_families"] = ["runtime_error:" + (ho["records"][0].get("error") or "")[:60]]
    elif m["accuracy_decidable"] >= 0.95 and m["boundary_false_commit_rate"] == 0 and mut_ok:
        result["verdict"] = "PASS_DEV"
    else:
        fams = []
        if m["accuracy_decidable"] < 0.5:
            fams.append("below_chance_or_abstaining")
        if m["boundary_false_commit_rate"] > 0:
            fams.append("commits_without_information")
        if mut["emptiness_removed_should_not_commit_yes"]["passed"] < mut["emptiness_removed_should_not_commit_yes"]["of"]:
            fams.append("keys_on_claim_form_not_domain_emptiness")
        if mut["every_to_some_should_flip_to_no"]["passed"] < mut["every_to_some_should_flip_to_no"]["of"]:
            fams.append("quantifier_blind")
        if mut["candidate_order_invariance"]["passed"] < mut["candidate_order_invariance"]["of"]:
            fams.append("candidate_order_dependent")
        if mut["no_to_exactly_zero_same_answer"]["passed"] < mut["no_to_exactly_zero_same_answer"]["of"]:
            fams.append("surface_form_of_emptiness")
        low = [k for k, v in m["by_kind"].items() if v < 0.5]
        if low:
            fams.append("weak_kinds:" + ",".join(low))
        if m["errors"]:
            fams.append(f"runtime_errors:{m['errors']}")
        result["verdict"] = "FAIL_DEV"
        result["failure_families"] = fams or ["near_miss_below_threshold"]
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
