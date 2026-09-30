"""Execute subject-written code (step functions, invariant expressions,
symmetry maps) safely: AST whitelist, no imports, no dunder or unlisted
attributes, no builtins beyond a small pure set, run in a subprocess with a
timeout. A rejected or crashing program yields None, never an exception in
the scorer.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys

SAFE_CALLS = {"range", "len", "sum", "min", "max", "abs", "list", "tuple", "sorted",
              "enumerate", "zip", "int", "all", "any", "dict", "set", "reversed",
              "divmod", "pow", "bool", "map", "filter", "step", "g", "q"}
SAFE_ATTRS = {"append", "index", "count", "copy", "pop", "insert", "extend", "get",
              "items", "keys", "values", "add", "update", "setdefault"}
OK_NODES = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Return, ast.Assign,
            ast.AugAssign, ast.AnnAssign, ast.For, ast.While, ast.If, ast.Break, ast.Continue,
            ast.Pass, ast.Expr, ast.Compare, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Call,
            ast.Subscript, ast.Slice, ast.Name, ast.Load, ast.Store, ast.Del, ast.Constant,
            ast.List, ast.Tuple, ast.Dict, ast.Set, ast.ListComp, ast.SetComp, ast.DictComp,
            ast.GeneratorExp, ast.comprehension, ast.IfExp, ast.Attribute, ast.Lambda,
            ast.operator, ast.cmpop, ast.boolop, ast.unaryop, ast.Starred, ast.keyword,
            ast.Expression)


def check(src: str) -> str | None:
    """Return None if the source is acceptable, else the reason."""
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return f"syntax: {e.msg}"
    for node in ast.walk(tree):
        if not isinstance(node, OK_NODES):
            return f"node {type(node).__name__}"
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            return "dunder name"
        if isinstance(node, ast.Attribute) and (node.attr.startswith("_") or node.attr not in SAFE_ATTRS):
            return f"attribute {node.attr}"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id not in SAFE_CALLS and not _defined(tree, node.func.id):
                return f"call {node.func.id}"
    return None


def _defined(tree, name):
    return any(isinstance(n, ast.FunctionDef) and n.name == name for n in ast.walk(tree))


_RUNNER = r'''
import json, sys
B = {k: __builtins__[k] if isinstance(__builtins__, dict) else getattr(__builtins__, k)
     for k in ("range","len","sum","min","max","abs","list","tuple","sorted","enumerate",
               "zip","int","all","any","dict","set","reversed","divmod","pow","bool","map",
               "filter","True","False","None")}
job = json.loads(sys.stdin.read())
env = {"__builtins__": B}
out = []
try:
    exec(compile(job["src"], "<subject>", "exec"), env)
    fn = env.get(job["fn"])
except Exception as e:
    print(json.dumps({"error": "load: " + type(e).__name__})); sys.exit(0)
if fn is None:
    print(json.dumps({"error": "no function " + job["fn"]})); sys.exit(0)
for s in job["inputs"]:
    try:
        r = fn(list(s))
        if isinstance(r, (list, tuple)):
            r = [int(v) for v in r]
        elif isinstance(r, bool):
            r = int(r)
        elif isinstance(r, (int, float)):
            r = int(r)
        else:
            r = None
    except Exception:
        r = None
    out.append(r)
print(json.dumps({"out": out}))
'''


def run(src: str, fn: str, inputs, timeout: int = 30):
    """Apply subject function `fn` to each input; list of results (None on
    failure), or {'error': reason}."""
    why = check(src)
    if why:
        return {"error": "rejected: " + why}
    try:
        p = subprocess.run([sys.executable, "-I", "-c", _RUNNER],
                           input=json.dumps({"src": src, "fn": fn, "inputs": [list(s) for s in inputs]}),
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    try:
        res = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"error": "no output"}
    return res.get("out", {"error": res.get("error", "unknown")}) if "out" in res else {"error": res.get("error")}


def expr_to_fn(expr: str, name: str = "q") -> str:
    """Wrap a one-line expression in s into a function definition."""
    return f"def {name}(s):\n    return {expr}\n"


def code_length(src: str) -> int:
    """Description length: characters of the source without comments and
    blank lines, whitespace runs collapsed."""
    lines = []
    for line in src.splitlines():
        line = line.split("#", 1)[0].rstrip()
        if line.strip():
            lines.append(" ".join(line.split()))
    return len("\n".join(lines))
