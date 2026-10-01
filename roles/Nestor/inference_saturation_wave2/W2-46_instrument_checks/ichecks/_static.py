"""Static-analysis helpers: parse a run script and the LOCAL helper modules it imports, without executing them.

Import resolution mirrors how the campaign scripts build sys.path: a script inserts directories named by string
literals (``HERE.parent / "x_donor_swap"``). So the candidate directories for a module are the script's own
directory plus every indexed directory whose NAME appears as a string literal in the script. Modules that resolve
into ``world_dir`` are the WORLD (world.py, p11.py, z8.py, ...) and are reported separately, never scanned as part
of the experiment's own instrument.
"""
from __future__ import annotations

import ast
import pathlib
import sys
from typing import Dict, Iterable, List, Optional, Set, Tuple

EXCLUDE_PARTS = ("holdout", "nestor_secrets")
STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}


def _excluded(p: pathlib.Path) -> bool:
    s = str(p).replace("\\", "/").lower()
    return any(x in s for x in EXCLUDE_PARTS)


def index_dirs(roots: Iterable[pathlib.Path], depth: int = 2) -> Dict[str, List[pathlib.Path]]:
    """dir name -> paths, for directories up to `depth` levels under each root (holdout/secrets excluded)."""
    out: Dict[str, List[pathlib.Path]] = {}
    for root in roots:
        root = pathlib.Path(root)
        frontier = [root]
        for _ in range(depth):
            nxt = []
            for d in frontier:
                try:
                    kids = [k for k in d.iterdir() if k.is_dir() and not _excluded(k) and k.name != "__pycache__"]
                except OSError:
                    continue
                for k in kids:
                    out.setdefault(k.name, []).append(k)
                nxt.extend(kids)
            frontier = nxt
    return out


def parse(path: pathlib.Path) -> Optional[ast.AST]:
    try:
        return ast.parse(pathlib.Path(path).read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return None


def string_literals(tree: ast.AST) -> Set[str]:
    return {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def imported_names(tree: ast.AST) -> Set[str]:
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            out.add(n.module.split(".")[0])
    return out


def resolve_modules(script: pathlib.Path, roots: Iterable[pathlib.Path], world_dir: Optional[pathlib.Path],
                    max_depth: int = 3, _index=None) -> Dict[str, object]:
    """Resolve the script's local helper modules transitively.

    Returns {"helpers": {name: path}, "world": {name: path}, "unresolved": [names], "trees": {path: ast}}.
    """
    index = _index if _index is not None else index_dirs(roots)
    world_dir = pathlib.Path(world_dir).resolve() if world_dir else None
    helpers: Dict[str, pathlib.Path] = {}
    world: Dict[str, pathlib.Path] = {}
    unresolved: Set[str] = set()
    trees: Dict[pathlib.Path, ast.AST] = {}
    todo: List[Tuple[pathlib.Path, int]] = [(pathlib.Path(script).resolve(), 0)]
    seen: Set[pathlib.Path] = set()
    while todo:
        path, d = todo.pop()
        if path in seen:
            continue
        seen.add(path)
        tree = parse(path)
        if tree is None:
            continue
        trees[path] = tree
        if d >= max_depth:
            continue
        lits = string_literals(tree)
        cands = [path.parent] + [p for name in sorted(lits) for p in index.get(name, [])]
        if world_dir:
            cands.append(world_dir)
        for mod in sorted(imported_names(tree)):
            if mod in STDLIB:
                continue
            hit = None
            if world_dir and (world_dir / (mod + ".py")).is_file():
                cands = [world_dir] + cands          # the canonical world wins over copies elsewhere
            for c in cands:
                f = c / (mod + ".py")
                if f.is_file() and not _excluded(f):
                    hit = f.resolve()
                    break
            if hit is None:
                unresolved.add(mod)
                continue
            if (world_dir and hit.parent == world_dir) or (hit.parent / "world.py").is_file():
                world[mod] = hit                     # any directory holding a world.py is a world, not an instrument
                continue
            if mod not in helpers:
                helpers[mod] = hit
            todo.append((hit, d + 1))
    return {"helpers": helpers, "world": world, "unresolved": sorted(unresolved), "trees": trees}


def assignments(tree: ast.AST) -> Dict[str, List[ast.AST]]:
    """name -> every value expression assigned to it anywhere in the module (scope-insensitive, deliberate)."""
    out: Dict[str, List[ast.AST]] = {}

    def bind(target, value):
        if isinstance(target, ast.Name):
            out.setdefault(target.id, []).append(value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            if isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(target.elts):
                for t, v in zip(target.elts, value.elts):
                    bind(t, v)
            else:
                for t in target.elts:
                    bind(t, value)

    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                bind(t, n.value)
        elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and n.value is not None:
            bind(n.target, n.value)
        elif isinstance(n, ast.For):
            bind(n.target, n.iter)
    return out


def attr_chain(node: ast.AST) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def reachable_code(res: Dict[str, object], script: pathlib.Path) -> List[Tuple[pathlib.Path, ast.AST]]:
    """(path, node) pairs that the script can actually run: the whole script, plus only those top-level functions
    of its local helper modules that are referenced (``helper.func`` / ``from helper import func``) from the script
    or from another reachable function (fixpoint). Module-level code of helpers is NOT included."""
    script = pathlib.Path(script).resolve()
    helpers: Dict[str, pathlib.Path] = res["helpers"]  # type: ignore[assignment]
    trees: Dict[pathlib.Path, ast.AST] = res["trees"]  # type: ignore[assignment]
    funcs: Dict[str, Dict[str, ast.AST]] = {}
    for m, p in helpers.items():
        t = trees.get(p)
        if t is not None:
            funcs[m] = {n.name: n for n in getattr(t, "body", []) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    used: Set[Tuple[str, str]] = set()
    todo: List[Tuple[Optional[str], ast.AST]] = [(None, trees[script])] if script in trees else []
    out: List[Tuple[pathlib.Path, ast.AST]] = [(script, trees[script])] if script in trees else []
    while todo:
        mod, node = todo.pop()
        for n in ast.walk(node):
            hits = []
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in funcs:
                hits.append((n.value.id, n.attr))
            elif isinstance(n, ast.ImportFrom) and n.module in funcs:
                hits.extend((n.module, a.name) for a in n.names)
            elif isinstance(n, ast.Name) and mod is not None and n.id in funcs.get(mod, {}):
                hits.append((mod, n.id))
            for m, f in hits:
                if (m, f) in used or f not in funcs.get(m, {}):
                    continue
                used.add((m, f))
                fn = funcs[m][f]
                out.append((helpers[m], fn))
                todo.append((m, fn))
    return out
