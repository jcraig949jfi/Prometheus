"""Lint for functions that return a verdict literal unconditionally (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: none.  AST scan for the Noesis shape: a function
whose every return statement returns the same constant drawn from a verdict
vocabulary (PASS, PROMOTED, SURVIVES, True, ...) and that never raises.  Such
a function cannot have produced evidence, whatever its docstring says.

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_verdict_lint.*

Reads: python source files.  Writes: nothing.
"""
from __future__ import annotations

import ast
from pathlib import Path

VERDICT_WORDS = {"PASS", "PASSED", "FAIL", "PROMOTED", "REJECTED", "SURVIVES", "KILLED", "VALIDATED", "OK", "GREEN",
                 "ACCEPT", "ACCEPTED", "TRUE", "VERIFIED", "REPRODUCED", "CONFIRMED", "HEALTHY", "ALIVE", "PRODUCTIVE",
                 "SUCCESS"}


def _const_str(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return node.value
        if node.value is True:
            return "TRUE"
        return None
    if isinstance(node, ast.Dict):
        for k, v in zip(node.keys, node.values):
            if (isinstance(k, ast.Constant) and k.value in ("verdict", "status", "result", "ok", "passed")
                    and isinstance(v, ast.Constant)):
                return "TRUE" if v.value is True else str(v.value)
    return None


def lint_source(src: str, relpath: str = "<src>") -> list:
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [{"file": relpath, "line": e.lineno, "kind": "SYNTAX_ERROR", "detail": str(e)[:120]}]
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        rets = [n for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None]
        raises = [n for n in ast.walk(fn) if isinstance(n, ast.Raise)]
        if not rets:
            continue
        lits = [_const_str(r.value) for r in rets]
        if (all(v is not None for v in lits) and len(set(lits)) == 1
                and lits[0].upper() in VERDICT_WORDS and not raises):
            out.append({"file": relpath, "line": fn.lineno, "function": fn.name, "kind": "UNCONDITIONAL_VERDICT",
                        "literal": lits[0], "n_returns": len(rets)})
    return out


def lint_paths(paths, repo: Path) -> dict:
    findings = []
    n = 0
    for p in paths:
        p = Path(p)
        files = [f for f in p.rglob("*.py") if "__pycache__" not in f.parts] if p.is_dir() else [p]
        for f in files:
            n += 1
            try:
                rel = f.resolve().relative_to(Path(repo).resolve()).as_posix()
            except ValueError:
                rel = str(f)
            findings += lint_source(f.read_text(encoding="utf-8", errors="replace"), rel)
    return {"files_scanned": n, "n_findings": len(findings), "findings": findings,
            "forbidden_inference": "a flagged function is one that CANNOT discriminate; an unflagged one is "
                                   "not thereby shown to discriminate (data-dependent verdicts need a control run)."}
