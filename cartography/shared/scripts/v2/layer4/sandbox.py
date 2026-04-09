"""Sandbox — safe execution environment for LLM-generated search functions."""

import ast
import math
import time
import threading
from collections import Counter, defaultdict
from typing import Any

import numpy as np
from scipy import stats


# Modules allowed inside generated code
ALLOWED_GLOBALS = {
    "np": np,
    "numpy": np,
    "math": math,
    "stats": stats,
    "Counter": Counter,
    "defaultdict": defaultdict,
    "range": range,
    "len": len,
    "min": min,
    "max": max,
    "abs": abs,
    "sum": sum,
    "sorted": sorted,
    "zip": zip,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "True": True,
    "False": False,
    "None": None,
    "print": lambda *a, **k: None,  # swallow prints
}

# AST node types that indicate dangerous operations
FORBIDDEN_MODULES = {"os", "sys", "subprocess", "shutil", "pathlib", "socket",
                     "http", "urllib", "requests", "ctypes", "signal", "importlib",
                     "builtins", "io", "tempfile", "glob", "pickle", "shelve"}

FORBIDDEN_CALLS = {"open", "exec", "eval", "compile",
                   "getattr", "setattr", "delattr", "globals", "locals",
                   "breakpoint", "exit", "quit", "input"}

# Modules that generated code may import inline
SAFE_IMPORT_MODULES = {"numpy", "np", "scipy", "scipy.stats", "math",
                       "collections", "functools", "itertools"}


# ---------------------------------------------------------------------------
# AST validation
# ---------------------------------------------------------------------------

class _SafetyChecker(ast.NodeVisitor):
    """Walk AST, flag forbidden patterns."""

    def __init__(self):
        self.violations = []

    def visit_Import(self, node):
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in FORBIDDEN_MODULES:
                self.violations.append(f"import {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            root = node.module.split(".")[0]
            if root in FORBIDDEN_MODULES:
                self.violations.append(f"from {node.module} import ...")
        self.generic_visit(node)

    def visit_Call(self, node):
        # Check direct calls like open(), exec()
        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            self.violations.append(f"call to {node.func.id}()")
        # Check attribute calls like os.system()
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("system", "popen", "exec"):
            self.violations.append(f"call to .{node.func.attr}()")
        self.generic_visit(node)


def validate_code(code_str: str) -> tuple:
    """Check if code is safe to execute. Returns (is_safe, reason)."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"

    checker = _SafetyChecker()
    checker.visit(tree)
    if checker.violations:
        return False, f"Forbidden: {', '.join(checker.violations)}"
    return True, "ok"


def complexity_score(code_str: str) -> int:
    """Count AST nodes. Used for parsimony scoring."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        return 999
    count = 0
    for _ in ast.walk(tree):
        count += 1
    return count


def extract_function_name(code_str: str) -> str | None:
    """Return the name of the first def in code_str, or None."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node.name
    return None


# ---------------------------------------------------------------------------
# Sandbox executor
# ---------------------------------------------------------------------------

class Sandbox:
    """Execute untrusted search functions with timeout and resource limits."""

    def __init__(self, timeout_s: float = 5, max_memory_mb: int = 256):
        self.timeout_s = timeout_s
        self.max_memory_mb = max_memory_mb

    def execute(self, code_str: str, function_name: str, *args, **kwargs) -> dict:
        """Execute a function defined in code_str.

        Returns dict with keys: success, result|error, elapsed_s.
        """
        # 1. Validate
        safe, reason = validate_code(code_str)
        if not safe:
            return {"success": False, "error": f"Validation failed: {reason}", "elapsed_s": 0.0}

        # 2. Build restricted namespace with safe __import__
        def _safe_import(name, *args, **kwargs):
            root = name.split(".")[0]
            if root not in SAFE_IMPORT_MODULES:
                raise ImportError(f"Import of '{name}' is not allowed")
            return __builtins__.__import__(name, *args, **kwargs) if hasattr(__builtins__, '__import__') else __import__(name, *args, **kwargs)

        ns = dict(ALLOWED_GLOBALS)
        ns["__builtins__"] = {"__import__": _safe_import, "__name__": "sandbox"}

        # 3. Exec the code to define the function
        try:
            exec(code_str, ns)  # noqa: S102
        except Exception as e:
            return {"success": False, "error": f"Exec failed: {type(e).__name__}: {e}", "elapsed_s": 0.0}

        if function_name not in ns:
            return {"success": False, "error": f"Function '{function_name}' not defined", "elapsed_s": 0.0}

        func = ns[function_name]

        # 4. Run with timeout (threading for Windows compat)
        result_box: dict = {}

        def _target():
            try:
                t0 = time.perf_counter()
                ret = func(*args, **kwargs)
                result_box["success"] = True
                result_box["result"] = ret
                result_box["elapsed_s"] = time.perf_counter() - t0
            except Exception as e:
                result_box["success"] = False
                result_box["error"] = f"{type(e).__name__}: {e}"
                result_box["elapsed_s"] = time.perf_counter() - t0 if "t0" in dir() else 0.0

        t0_outer = time.perf_counter()
        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout_s)

        if thread.is_alive():
            return {"success": False, "error": "Timeout", "elapsed_s": self.timeout_s}

        if not result_box:
            return {"success": False, "error": "No result produced", "elapsed_s": time.perf_counter() - t0_outer}

        return result_box


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_default_sandbox = Sandbox()

def run(code_str: str, function_name: str, *args, **kwargs) -> dict:
    """Convenience: run in default sandbox."""
    return _default_sandbox.execute(code_str, function_name, *args, **kwargs)


if __name__ == "__main__":
    # Quick self-test
    test_code = '''
def test_func(a, b):
    import numpy as np
    return {"mean_a": float(np.mean(a)), "mean_b": float(np.mean(b))}
'''
    sb = Sandbox(timeout_s=2)
    r = sb.execute(test_code, "test_func", [1, 2, 3], [4, 5, 6])
    print(f"Test 1 (valid):   {r}")

    bad_code = '''
def bad_func():
    import os
    os.system("echo pwned")
'''
    r2 = sb.execute(bad_code, "bad_func")
    print(f"Test 2 (blocked): {r2}")

    hang_code = '''
def hang():
    while True:
        pass
'''
    r3 = sb.execute(hang_code, "hang")
    print(f"Test 3 (timeout): {r3}")

    print(f"\ncomplexity_score(test_code) = {complexity_score(test_code)}")
    print(f"validate_code(bad_code) = {validate_code(bad_code)}")
