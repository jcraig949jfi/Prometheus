"""Algorithm-library landscape — the operation graph of math code (sympy).

Node:  "algolib:<name>"   (a sympy function/class)
Verb:  "calls"            (function A's source calls B)

The verb here is genuinely operational (feedback_verbs_over_nouns): edges are
"this operation invokes that operation," not "these names co-occur."
"""
from __future__ import annotations

import ast
import inspect
from collections import Counter


_SEED_MODULES = [
    "sympy", "sympy.simplify", "sympy.ntheory", "sympy.polys", "sympy.solvers",
    "sympy.matrices", "sympy.functions", "sympy.combinatorics", "sympy.series",
]


class AlgolibLandscape:
    name = "algolib"

    def __init__(self):
        self._obj: dict[str, object] = {}    # name -> callable
        self._src: dict[str, str] = {}       # name -> source (cached)
        self._reffreq: Counter = Counter()
        self._ok = False
        try:
            import importlib
            for modname in _SEED_MODULES:
                try:
                    mod = importlib.import_module(modname)
                except Exception:
                    continue
                for nm in dir(mod):
                    if nm.startswith("_"):
                        continue
                    obj = getattr(mod, nm, None)
                    if callable(obj) and nm not in self._obj:
                        self._obj[nm] = obj
            self._ok = len(self._obj) > 50
        except Exception:
            self._ok = False

    def available(self) -> bool:
        return self._ok

    def _source(self, name: str):
        if name in self._src:
            return self._src[name]
        obj = self._obj.get(name)
        if obj is None:
            return None
        try:
            src = inspect.getsource(obj)
        except Exception:
            src = ""
        self._src[name] = src
        return src

    def seeds(self, rng, k: int = 4) -> list[str]:
        names = list(self._obj.keys())
        if not names:
            return []
        return [f"algolib:{rng.choice(names)}" for _ in range(min(k, len(names)))]

    @staticmethod
    def _called_names(src: str) -> list[str]:
        out = []
        try:
            tree = ast.parse(src)
        except Exception:
            return out
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name):
                    out.append(f.id)
                elif isinstance(f, ast.Attribute):
                    out.append(f.attr)
        return out

    def expand(self, node: str, rng, ruleset) -> list:
        if not node.startswith("algolib:"):
            return []
        name = node.split(":", 1)[1]
        src = self._source(name)
        if not src:
            return []
        maxf = max(self._reffreq.values()) if self._reffreq else 1
        out, seen = [], set()
        for callee in self._called_names(src):
            if callee == name or callee in seen or len(callee) <= 2:
                continue
            # resolve callee to a known sympy object; discover new ones lazily
            if callee not in self._obj:
                import sympy
                obj = getattr(sympy, callee, None)
                if callable(obj):
                    self._obj[callee] = obj
                else:
                    continue
            seen.add(callee)
            self._reffreq[callee] += 1
            null_p = min(0.99, self._reffreq.get(callee, 1) / maxf)
            out.append((f"algolib:{callee}", "calls", null_p))
        return out
