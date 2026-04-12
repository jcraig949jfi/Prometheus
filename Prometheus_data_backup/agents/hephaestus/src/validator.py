"""Validate extracted Python code for correctness and safety."""

import ast
import importlib
import sys
import tempfile
import types
from pathlib import Path

# Allowed top-level imports: numpy + stdlib
STDLIB_MODULES = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else {
    "abc", "array", "ast", "bisect", "builtins", "collections", "contextlib",
    "copy", "csv", "dataclasses", "datetime", "decimal", "difflib", "enum",
    "fractions", "functools", "hashlib", "heapq", "hmac", "io", "itertools",
    "json", "logging", "math", "operator", "os", "pathlib", "pprint", "random",
    "re", "secrets", "statistics", "string", "struct", "sys", "textwrap",
    "time", "typing", "unittest", "uuid", "warnings",
}
ALLOWED_MODULES = STDLIB_MODULES | {
    "numpy", "np",
    "forge_primitives",       # Frame H primordial-soup primitives
    "sympy", "networkx", "nx", "scipy",  # Frame H external libs
}


def check_syntax(code: str) -> tuple[bool, str]:
    """Check that the code parses as valid Python."""
    try:
        ast.parse(code)
        return True, "ok"
    except SyntaxError as e:
        return False, f"syntax_error: {e.msg} (line {e.lineno})"


def check_imports(code: str) -> tuple[bool, str]:
    """Check that only allowed imports are used."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False, "cannot_parse"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in ALLOWED_MODULES:
                    return False, f"forbidden_import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top = node.module.split(".")[0]
                if top not in ALLOWED_MODULES:
                    return False, f"forbidden_import: {node.module}"
    return True, "ok"


def check_interface(code: str) -> tuple[bool, str]:
    """Check that the code defines a ReasoningTool class with required methods."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False, "cannot_parse"

    classes = [
        node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    ]
    reasoning_tools = [c for c in classes if c.name == "ReasoningTool"]
    if not reasoning_tools:
        return False, "no_ReasoningTool_class"

    cls = reasoning_tools[0]
    method_names = {
        node.name
        for node in ast.walk(cls)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    missing = []
    for required in ("evaluate", "confidence"):
        if required not in method_names:
            missing.append(required)
    if missing:
        return False, f"missing_methods: {', '.join(missing)}"

    return True, "ok"


def check_runtime(code: str) -> tuple[bool, str]:
    """Try to instantiate and call the class with dummy data."""
    # Write to a temp file and import it
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()
        ) as f:
            f.write(code)
            tmp_path = f.name

        spec = importlib.util.spec_from_file_location("_forge_test", tmp_path)
        if spec is None or spec.loader is None:
            return False, "module_spec_failed"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        ToolClass = getattr(mod, "ReasoningTool", None)
        if ToolClass is None:
            return False, "class_not_found_at_runtime"

        tool = ToolClass()

        # Test evaluate()
        result = tool.evaluate("What is 2+2?", ["3", "4", "5"])
        if not isinstance(result, list):
            return False, f"evaluate_bad_return_type: {type(result).__name__}"
        if len(result) == 0:
            return False, "evaluate_returned_empty_list"
        for item in result:
            if not isinstance(item, dict):
                return False, f"evaluate_item_not_dict: {type(item).__name__}"
            if "candidate" not in item or "score" not in item:
                return False, f"evaluate_item_missing_keys: {set(item.keys())}"

        # Test confidence()
        conf = tool.confidence("What is 2+2?", "4")
        if not isinstance(conf, (int, float)):
            return False, f"confidence_bad_return_type: {type(conf).__name__}"
        if not (0.0 <= float(conf) <= 1.0):
            return False, f"confidence_out_of_range: {conf}"

        return True, "ok"

    except Exception as e:
        return False, f"runtime_error: {type(e).__name__}: {e}"
    finally:
        try:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
        # Clean up the module from sys.modules
        sys.modules.pop("_forge_test", None)


def validate(code: str) -> tuple[bool, str]:
    """Run all validation checks. Returns (passed, reason)."""
    for check_fn in (check_syntax, check_imports, check_interface, check_runtime):
        passed, reason = check_fn(code)
        if not passed:
            return False, reason
    return True, "all_checks_passed"
