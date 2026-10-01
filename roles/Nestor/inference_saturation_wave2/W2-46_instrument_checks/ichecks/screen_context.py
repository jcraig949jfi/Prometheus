"""Class (a): screen context != world context.

Incidents: N11 and N13 (zero-register "competent" counts read as the world's copiers), W2-26 (founder called
"register-robust" from BANK and ZERO contexts, while self-carried in-world contexts convert some side-1 genomes at
side 0: 0.91-1.0 vs 0.13-0.18 under ZERO), W2-34 (C-A3's post-takeover "collapse" read from a zero-register
screen), W2-38 (0008 checkpoint 900: zero screen 1/64, carried contexts 30/64).

The world carries registers: ``world.Runner._pair_interact`` loads ``ctx.regs, ctx.fz, ctx.fc = org.regs, ...``
before each slice and stores them back afterwards (world.py:804/812), and the world's own P-11 assay runs on the
actual pre-interaction state ``st0`` (world.py:793-794, 850). A screen that calls the P-11 assay / interact with
``st_a = st_b = (None, 0, 0)`` (or constant synthetic registers) measures a different context.

STATIC. Parses the run script and its local helper modules (the world's own modules are excluded), finds every
call that passes ``st_a`` / ``st_b`` (and every call that forwards a captured world kwargs dict unchanged), and
classifies each context expression:

    CARRIED    the expression reads ``.regs`` of a live organism, or forwards the world's captured kwargs
    ZERO       a constant ``(None, 0, 0)``-style state
    SYNTHETIC  constant or generated registers that are not any organism's carried state
    UNKNOWN    an unresolvable name (e.g. a function parameter)

Verdicts
    CONTEXT_MISMATCH  the world carries registers and every screen context found is ZERO / SYNTHETIC
    OK                at least one screen context is CARRIED (details list mixed designs), or the world resets
    NOT_VERIFIED      no screen call found, a context is UNKNOWN with none CARRIED, or the world's carry rule
                      could not be read

A CONTEXT_MISMATCH is a flag on the INSTRUMENT, not a verdict on the claim: a script whose question is explicitly
"does this genome copy from fresh registers?" uses a zero context correctly; any reading of that screen as in-world
competence or persistence is what the flag guards.
"""
from __future__ import annotations

import ast
import pathlib
from typing import Dict, List, Optional, Set

from . import CheckResult, NOT_VERIFIED, OK
from ._static import assignments, attr_chain, imported_names, parse, reachable_code, resolve_modules

NAME = "screen_context"
ST_KEYS = ("st_a", "st_b")


def world_carries_registers(world_py: pathlib.Path) -> Optional[bool]:
    """True if the world stores ctx.regs back into the organism and never resets .regs outside __init__."""
    tree = parse(world_py)
    if tree is None:
        return None
    carried = reset = False
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        for n in ast.walk(fn):
            if not isinstance(n, ast.Assign):
                continue
            tgts = []
            for t in n.targets:
                tgts.extend(t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t])
            vals = n.value.elts if isinstance(n.value, (ast.Tuple, ast.List)) else [n.value]
            for i, t in enumerate(tgts):
                if not (isinstance(t, ast.Attribute) and t.attr == "regs"):
                    continue
                owner = attr_chain(t.value)
                v = vals[i] if i < len(vals) else n.value
                if owner != "ctx" and isinstance(v, ast.Attribute) and v.attr == "regs" and attr_chain(v.value) == "ctx":
                    carried = True
                if isinstance(v, ast.Constant) and v.value is None and fn.name != "__init__" and owner != "ctx":
                    reset = True
    if not carried and not reset:
        return None
    return carried and not reset


class _Classifier:
    def __init__(self, tree: ast.AST):
        self.assign = assignments(tree)
        self.modules = imported_names(tree) | {"random", "math", "hashlib", "bytes", "list", "range", "tuple", "len"}

    def kinds(self, node: ast.AST, depth: int = 0, seen: Optional[Set[str]] = None) -> Set[str]:
        seen = set() if seen is None else seen
        if depth > 40 or node is None:
            return {"UNKNOWN"}
        k: Set[str] = set()
        if isinstance(node, ast.Attribute):
            if node.attr == "regs":
                return {"CARRIED"}
            return self.kinds(node.value, depth + 1, seen) if not isinstance(node.value, ast.Name) or \
                node.value.id not in self.modules else set()
        if isinstance(node, ast.Constant):
            return {"ZERO"} if node.value in (None, 0, False) else {"SYNTHETIC"}
        if isinstance(node, ast.Name):
            if node.id in self.modules or node.id in ("True", "False", "None"):
                return set()
            if node.id in seen:
                return set()
            vals = self.assign.get(node.id)
            if not vals:
                return {"UNKNOWN"}
            seen = seen | {node.id}
            for v in vals:
                k |= self.kinds(v, depth + 1, seen)
            return k
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            for e in node.elts:
                k |= self.kinds(e, depth + 1, seen)
            return k
        if isinstance(node, ast.Dict):
            for e in node.values:
                k |= self.kinds(e, depth + 1, seen)
            return k
        if isinstance(node, ast.IfExp):
            return self.kinds(node.body, depth + 1, seen) | self.kinds(node.orelse, depth + 1, seen)
        if isinstance(node, ast.Subscript):
            return self.kinds(node.value, depth + 1, seen)
        if isinstance(node, (ast.BinOp,)):
            return self.kinds(node.left, depth + 1, seen) | self.kinds(node.right, depth + 1, seen)
        if isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.SetComp)):
            return self.kinds(node.elt, depth + 1, seen) or {"SYNTHETIC"}
        if isinstance(node, ast.Call):
            for a in node.args:
                k |= self.kinds(a, depth + 1, seen)
            for kw in node.keywords:
                k |= self.kinds(kw.value, depth + 1, seen)
            if isinstance(node.func, ast.Attribute):
                k |= self.kinds(node.func.value, depth + 1, seen)
            return k or {"SYNTHETIC"}
        return {"UNKNOWN"}


def _collapse(kinds: Set[str]) -> str:
    if "CARRIED" in kinds:
        return "CARRIED"
    if "UNKNOWN" in kinds:
        return "UNKNOWN"
    if "SYNTHETIC" in kinds:
        return "SYNTHETIC"
    return "ZERO"


def _is_assay_func(func: ast.AST, cl: _Classifier) -> bool:
    chain = attr_chain(func)
    if chain.endswith(("assay", "interact")):
        return True
    if isinstance(func, ast.Name):
        for v in cl.assign.get(func.id, []):
            if attr_chain(v).endswith(("p11.assay", "p11.interact")):
                return True
    return False


def screen_contexts(tree: ast.AST, path: str, scan: Optional[ast.AST] = None) -> List[Dict]:
    """Contexts passed by calls inside `scan` (default: the whole module); names resolve against the whole `tree`."""
    cl = _Classifier(tree)
    wrapper_kw = {n.args.kwarg.arg for n in ast.walk(tree)
                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and n.args.kwarg}
    out = []
    for n in ast.walk(scan if scan is not None else tree):
        if not isinstance(n, ast.Call):
            continue
        kws = {k.arg: k.value for k in n.keywords if k.arg in ST_KEYS}
        if kws:
            for key, v in kws.items():
                kinds = cl.kinds(v)
                out.append({"file": path, "line": n.lineno, "arg": key, "kind": _collapse(kinds),
                            "raw": sorted(kinds)})
            continue
        star = [k.value for k in n.keywords if k.arg is None]
        if star and _is_assay_func(n.func, cl):
            fwd = star[0]
            overrides = isinstance(fwd, ast.Call) and any(k.arg in ST_KEYS for k in fwd.keywords)
            if isinstance(fwd, ast.Name) and fwd.id in wrapper_kw:
                continue                     # a wrapper forwarding its own **kwargs: the world's call, not a screen
            if not overrides and (isinstance(fwd, ast.Name) or (isinstance(fwd, ast.Call) and attr_chain(fwd.func) == "dict")):
                out.append({"file": path, "line": n.lineno, "arg": "**kw", "kind": "CARRIED",
                            "raw": ["FORWARDED_WORLD_KWARGS"]})
    return out


def check_screen_context(script: pathlib.Path, world_dir: pathlib.Path, roots, _index=None) -> CheckResult:
    world_py = pathlib.Path(world_dir) / "world.py"
    carries = world_carries_registers(world_py)
    if carries is None:
        return CheckResult(NAME, NOT_VERIFIED, "could not read the world's register carry rule from %s" % world_py)
    res = resolve_modules(script, roots, world_dir, _index=_index)
    ctxs: List[Dict] = []
    for path, node in reachable_code(res, script):
        ctxs.extend(screen_contexts(res["trees"][path], str(path), node))
    kinds = sorted({c["kind"] for c in ctxs})
    details = {"world_carries_registers": carries, "contexts": ctxs, "kinds": kinds,
               "helpers": {k: str(v) for k, v in res["helpers"].items()}, "unresolved_imports": res["unresolved"]}
    if not carries:
        return CheckResult(NAME, OK, "the world resets registers: a zero context is the world's context", details)
    if not ctxs:
        return CheckResult(NAME, NOT_VERIFIED, "no screen call (st_a/st_b or forwarded world kwargs) found in the "
                           "script or in the helper functions it reaches", details)
    if "CARRIED" in kinds:
        mixed = [k for k in kinds if k != "CARRIED"]
        return CheckResult(NAME, OK, "a carried-register context is screened" +
                           (" (alongside %s: a deliberate comparison?)" % "/".join(mixed) if mixed else ""), details)
    if "UNKNOWN" in kinds:
        return CheckResult(NAME, NOT_VERIFIED, "a screen context could not be resolved and none is carried", details)
    return CheckResult(NAME, "CONTEXT_MISMATCH",
                       "every screen context is %s while the world carries registers: read this screen as "
                       "fresh-context competence only, never as in-world competence" % "/".join(kinds),
                       details, [c for c in ctxs])
