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
    result["dev_set_version"] = getattr(wall, "DEV_SET_VERSION", 1)
    mut_ok = all(v["passed"] == v["of"] for v in mut.values())
    # ── Mechanism coverage (Addendum 1, Q3). A candidate may declare
    #      ABLATIONS = {"component name": {"module_attr": replacement, ...}, ...}
    #    Each ablation is applied in turn and the holdout delta measured. A component whose
    #    ablation changes nothing is UNTESTED by this dev set (decorative until proven otherwise).
    coverage = None
    abl = getattr(mod, "ABLATIONS", None)
    # Addendum 3 (Q6): self-declared ablations are hints, not the obligation set. The harness derives
    # a minimum obligation set from externally visible components: every module-level function other
    # than the entry op is stubbed to return None; every module-level list/tuple constant is emptied.
    auto = {}
    import types as _types
    for name, val in vars(mod).items():
        if name.startswith("__") or name == f"op_{wall_id}":
            continue
        if isinstance(val, _types.FunctionType) and val.__module__ == mod.__name__:
            auto[f"auto:fn:{name}"] = {name: (lambda *a, **k: None)}
        elif isinstance(val, (list, tuple)) and val and not isinstance(val, str):
            auto[f"auto:const:{name}"] = {name: type(val)()}
    merged = dict(auto)
    if isinstance(abl, dict):
        merged.update({f"declared:{k}": v for k, v in abl.items()})
    result["harness_authorship"] = "AUTHOR-ADVERSARIAL (dev set and harness authored by the forge seat; not independent)"
    if merged:
        coverage = {}
        for cname, patch in merged.items():
            saved = {k: getattr(mod, k, None) for k in patch}
            try:
                for k, v in patch.items():
                    setattr(mod, k, v)
                acc = wall.evaluate(op, hold)["metrics"]["accuracy_decidable"]
            except Exception as e:  # noqa: BLE001
                acc = None; coverage[cname] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}
            finally:
                for k, v in saved.items():
                    setattr(mod, k, v)
            if acc is not None:
                coverage[cname] = {"delta_acc": round(acc - m["accuracy_decidable"], 4)}
        result["mechanism_coverage"] = coverage
    untested = [c for c, v in (coverage or {}).items() if v.get("delta_acc") == 0.0]
    iv = sum(1 for r in ho["records"] if (r.get("error") or "").startswith("InterfaceViolation"))
    if iv == len(hold):
        result["verdict"] = "INTERFACE_VIOLATION"
        result["failure_families"] = ["returns_value_instead_of_state"]
    elif m["errors"] == len(hold):
        result["verdict"] = "RUNTIME_ERROR_ALL"
        result["failure_families"] = ["runtime_error:" + (ho["records"][0].get("error") or "")[:60]]
    elif m["accuracy_decidable"] >= 0.95 and m["boundary_false_commit_rate"] == 0 and mut_ok:
        if coverage is None:
            result["verdict"] = "PASS_DEV_UNVERIFIED_COVERAGE"     # no ABLATIONS declared
        elif untested:
            result["verdict"] = "PASS_DEV_WITH_UNTESTED_COMPONENT"
            result["untested_components"] = untested
        else:
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
