"""Code-lineage audit: which families share implementation?

A family's lineage = the transitive closure of repository modules its source
imports, excluding a whitelist of modules that carry signatures only
(contract.py) or no physics. Two families that share any non-whitelisted module
are merged into one evaluator lineage (union-find). Law support is counted in
lineages, never in families, and held-out folds are lineages.

This detects SHARED CODE. It cannot detect shared IDEAS (the same author writing
the same physics twice); that conflict of interest is declared in the prereg.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Iterable, List, Set

REPO = Path(__file__).resolve().parents[2]
SIGNATURE_ONLY = {"prometheus.cosmos.contract", "prometheus", "prometheus.cosmos"}
THIRD_PARTY_OK = {"numpy", "math", "typing", "__future__", "dataclasses", "itertools", "functools"}


def _module_file(mod: str) -> Path | None:
    p = REPO.joinpath(*mod.split("."))
    if p.with_suffix(".py").exists():
        return p.with_suffix(".py")
    if (p / "__init__.py").exists():
        return p / "__init__.py"
    return None


def imports_of(path: Path) -> Set[str]:
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    out: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.add(node.module)
            for a in node.names:
                if _module_file(node.module + "." + a.name):
                    out.add(node.module + "." + a.name)
    return out


def closure(path: Path) -> Set[str]:
    """Repository modules reachable from `path` (excluding signature-only modules)."""
    seen: Set[str] = set()
    stack = [m for m in imports_of(path)]
    while stack:
        m = stack.pop()
        if m in seen or m in SIGNATURE_ONLY:
            continue
        f = _module_file(m)
        if f is None:
            continue  # stdlib / third party
        seen.add(m)
        stack.extend(imports_of(f))
    return seen


def foreign_imports(path: Path) -> Set[str]:
    """Top-level non-repo imports that are not on the allowed list (a family must stay small)."""
    out = set()
    for m in imports_of(path):
        top = m.split(".")[0]
        if _module_file(m) is None and top not in THIRD_PARTY_OK:
            out.add(m)
    return out


def lineages(family_files: Dict[str, Iterable[str]]) -> Dict[str, str]:
    """family -> lineage id (sorted '+'-joined member names of its union-find class)."""
    names = sorted(family_files)
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    deps = {}
    for n in names:
        d: Set[str] = set()
        for f in family_files[n]:
            d |= closure(REPO / f)
        deps[n] = d
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if deps[a] & deps[b]:
                parent[find(a)] = find(b)
    groups: Dict[str, List[str]] = {}
    for n in names:
        groups.setdefault(find(n), []).append(n)
    return {n: "+".join(sorted(groups[find(n)])) for n in names}
