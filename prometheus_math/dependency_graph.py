"""prometheus_math.dependency_graph — auto-discover inter-module dependencies.

Walks each ``prometheus_math.<modname>`` (and its companion
``techne.lib.<op>``) source file via Python's ``ast`` module and reports
which other ``prometheus_math`` submodules each one depends on.

Used by :func:`prometheus_math.doc.arsenal` to embed a Mermaid diagram of
the dependency structure inside ARSENAL.md.

Why ``ast`` rather than runtime introspection? Lazy imports — half the
optimization backends are only imported inside ``_lp_scipy()`` /
``_mip_scip()`` etc. Runtime introspection would miss them. ``ast``
walks the static text and catches every ``import`` regardless of
where it lives in the function tree.

API
---
``module_imports(modname)``
    Return the set of ``prometheus_math`` submodules that ``modname``
    statically imports (including any imports proxied through
    ``techne.lib.<op>``).

``operation_dependencies(category, op_name)``
    Approximate per-operation dependencies — which other PM operations
    a given function calls. Match-by-name within scope; bonus signal
    for the dependency graph.

``build_dependency_graph()``
    Build the full ``module -> set[module]`` adjacency dict.

``to_mermaid(graph, layout='LR')``
    Render the graph as a Mermaid ``graph LR`` block (text).

``to_dot(graph)``
    Render the graph as a Graphviz DOT block (text).

``cycle_detection(graph)``
    Return a list of cycles (each a list of nodes). Empty iff acyclic.

Forged: 2026-04-25 | project #24 | category A / M
"""
from __future__ import annotations

import ast
import importlib
from pathlib import Path
from typing import Iterable

# The categorical modules of prometheus_math. Kept in sync with
# ``prometheus_math.__init__.__all__``. Used as the canonical node set
# for ``build_dependency_graph()``.
PM_CATEGORIES: tuple[str, ...] = (
    # Calibration drift fix (2026-04-29): expanded from the original 9
    # to include all categorical modules currently exposed by
    # prometheus_math.__init__. The dependency graph walks PM_CATEGORIES
    # to detect inter-module dependencies, and combinatorics/optimization/
    # numerics now have sibling modules (combinatorics_partitions,
    # optimization_qp, numerics_special_*, ...) that the graph must
    # recognize as known PM categories rather than unknown deps.
    "number_theory",
    "elliptic_curves",
    "number_fields",
    "topology",
    "combinatorics",
    "combinatorics_partitions",
    "combinatorics_permutations",
    "combinatorics_posets",
    "optimization",
    "optimization_metaheuristics",
    "optimization_qp",
    "optimization_sdp",
    "optimization_socp",
    "numerics",
    "numerics_special",
    "numerics_special_dilogarithm",
    "numerics_special_eta",
    "numerics_special_hurwitz",
    "numerics_special_q_pochhammer",
    "numerics_special_theta",
    "symbolic",
    "symbolic_tensor_decomp",
    "algebraic_geometry",
    "algebraic_geometry_normal_form",
    "galois",
    "iwasawa",
    "geometry_convex_hull",
    "geometry_delaunay",
    "geometry_voronoi",
    "statistics_distributions",
    "crypto_primitives",
    "crypto_signature_schemes",
    "coding_linear",
    "dynamics_iterated_maps",
    "dynamics_ode_solvers",
    "algebra_lie_algebras",
    "hecke",
    "modular",
    "research",
    "databases",
)


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _pm_root() -> Path:
    """Return the directory that contains prometheus_math/ (i.e. repo root)."""
    return Path(__file__).resolve().parent.parent


def _pm_module_path(modname: str) -> Path:
    """Return the source file for ``prometheus_math.<modname>``.

    Raises FileNotFoundError if the module file does not exist.
    """
    if not modname or not isinstance(modname, str):
        raise ValueError(f"modname must be a non-empty string, got {modname!r}")
    candidate = _pm_root() / "prometheus_math" / f"{modname}.py"
    if not candidate.exists():
        # try as a package
        package = _pm_root() / "prometheus_math" / modname / "__init__.py"
        if package.exists():
            return package
        raise FileNotFoundError(
            f"prometheus_math.{modname} not found at {candidate}"
        )
    return candidate


def _techne_lib_path(op_name: str) -> Path | None:
    """Return the source file for ``techne.lib.<op_name>``, or None if absent."""
    candidate = _pm_root() / "techne" / "lib" / f"{op_name}.py"
    return candidate if candidate.exists() else None


# ---------------------------------------------------------------------------
# AST walking
# ---------------------------------------------------------------------------

def _ast_imports(source: str) -> list[tuple[str, list[str]]]:
    """Parse ``source`` and return (module, imported_names) pairs.

    For ``import a.b`` -> ('a.b', []).
    For ``from a.b import c, d`` -> ('a.b', ['c', 'd']).
    """
    tree = ast.parse(source)
    out: list[tuple[str, list[str]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((alias.name, []))
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            names = [alias.name for alias in node.names]
            out.append((node.module, names))
    return out


def _imported_techne_ops(modname: str) -> set[str]:
    """Return the set of techne.lib op-names that ``modname`` imports.

    A categorical module like ``elliptic_curves`` typically contains
    ``from techne.lib.regulator import ...``; this returns
    ``{"regulator"}``.
    """
    path = _pm_module_path(modname)
    src = path.read_text(encoding="utf-8")
    ops = set()
    for module, _names in _ast_imports(src):
        if module.startswith("techne.lib."):
            tail = module[len("techne.lib."):]
            head = tail.split(".", 1)[0]
            if head:
                ops.add(head)
    return ops


def _techne_op_to_pm_module() -> dict[str, str]:
    """Map each techne.lib op-name -> the pm.<module> that owns it.

    Built by scanning every PM categorical module's import graph. If two
    PM modules pull from the same op, the first one wins (the name is
    canonical to its first export site).
    """
    mapping: dict[str, str] = {}
    for cat in PM_CATEGORIES:
        try:
            ops = _imported_techne_ops(cat)
        except (FileNotFoundError, OSError, SyntaxError):
            continue
        for op in ops:
            mapping.setdefault(op, cat)
    return mapping


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def module_imports(modname: str) -> set[str]:
    """Return PM submodules that ``modname`` depends on.

    Static (ast-based) walk of the source file. Picks up:
      - direct ``from prometheus_math.X import ...``
      - indirect deps via ``from techne.lib.<op> import ...`` resolved
        through the ``op -> pm.<category>`` map.

    Self-dependencies are removed. Standard-library and third-party
    imports are excluded.

    Parameters
    ----------
    modname : str
        e.g. "elliptic_curves" or "number_theory".

    Returns
    -------
    set[str] of PM module short names.

    Raises
    ------
    ValueError on empty/invalid modname.
    FileNotFoundError if the module's source can't be located.
    """
    if not modname or not isinstance(modname, str):
        raise ValueError(f"modname must be a non-empty string, got {modname!r}")
    path = _pm_module_path(modname)
    src = path.read_text(encoding="utf-8")
    op_map = _techne_op_to_pm_module()

    deps: set[str] = set()

    # 1) Direct prometheus_math.X imports
    for module, _names in _ast_imports(src):
        if module.startswith("prometheus_math."):
            tail = module[len("prometheus_math."):]
            head = tail.split(".", 1)[0]
            if head and head != modname:
                deps.add(head)
        # 2) Relative imports `from .X import ...` are normalised by
        # ast.ImportFrom: ImportFrom node has `module='X'` and a
        # nonzero `level`. Walk again to catch level>0 cases.

    # Re-scan with level tracking for relative imports (`from .registry`)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level and node.level > 0:
            mod = node.module or ""
            head = mod.split(".", 1)[0] if mod else ""
            if head and head != modname and head in PM_CATEGORIES:
                deps.add(head)

    # 3) Indirect via techne.lib.<op>
    techne_ops = _imported_techne_ops(modname)
    for op in techne_ops:
        owner = op_map.get(op)
        if owner and owner != modname:
            deps.add(owner)
        # Also follow op -> op imports inside techne.lib (e.g.
        # analytic_sha imports regulator -> exposes the
        # elliptic_curves <- elliptic_curves self-edge that we drop).
        op_path = _techne_lib_path(op)
        if op_path is None:
            continue
        try:
            op_src = op_path.read_text(encoding="utf-8")
        except OSError:
            continue
        for sub_mod, _names in _ast_imports(op_src):
            # Catch "from .regulator import ..." inside techne.lib
            if sub_mod.startswith("."):
                # Relative import within techne.lib
                rel = sub_mod.lstrip(".")
                head = rel.split(".", 1)[0]
                owner2 = op_map.get(head)
                if owner2 and owner2 != modname:
                    deps.add(owner2)
            elif sub_mod.startswith("techne.lib."):
                tail = sub_mod[len("techne.lib."):]
                head = tail.split(".", 1)[0]
                owner2 = op_map.get(head)
                if owner2 and owner2 != modname:
                    deps.add(owner2)

    deps.discard(modname)
    return deps


def operation_dependencies(category: str, op_name: str) -> set[str]:
    """Approximate per-operation dependencies.

    Walks the source file of the techne.lib op (if it exists) and
    extracts the names of other PM-known operations called inside the
    function body of ``op_name``. Match-by-name within scope.

    Returns the set of PM op names referenced.

    Parameters
    ----------
    category : str
        PM categorical module (e.g. "elliptic_curves"). Used only as
        a sanity-check that the op belongs to that category.
    op_name : str
        Name of the operation (e.g. "analytic_sha").

    Notes
    -----
    Approximate: a name match within the function body counts as a
    dependency, even if it's a local binding shadowing a PM op. The
    bonus signal is fine for the graph; for hard correctness use
    ``module_imports``.
    """
    if not category or not op_name:
        raise ValueError("category and op_name must be non-empty strings")
    if category not in PM_CATEGORIES:
        # Soft-fail: still try to resolve, but warn caller via empty result
        pass
    op_path = _techne_lib_path(op_name)
    if op_path is None:
        return set()
    src = op_path.read_text(encoding="utf-8")

    # Collect known PM op names from every category's __all__
    known_ops: set[str] = set()
    for cat in PM_CATEGORIES:
        try:
            mod = importlib.import_module(f"prometheus_math.{cat}")
            for name in getattr(mod, "__all__", []) or []:
                known_ops.add(name)
        except Exception:
            continue

    tree = ast.parse(src)

    # Build module-level alias map: local_name -> pm_op_name. Catches
    # `from .regulator import regulator as _regulator` (alias _regulator
    # tracks back to the pm op `regulator`).
    alias_map: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                bound_name = alias.asname or alias.name
                # Two flavours:
                #   from .regulator import regulator as _regulator
                #     -> mod=='regulator' (relative), alias.name='regulator'
                #     -> bound_name='_regulator'
                #   from techne.lib.regulator import regulator
                #     -> mod=='techne.lib.regulator'
                head = ""
                if node.level and node.level > 0 and mod:
                    head = mod.split(".", 1)[0]
                elif mod.startswith("techne.lib."):
                    head = mod[len("techne.lib."):].split(".", 1)[0]
                elif mod.startswith("prometheus_math."):
                    head = mod[len("prometheus_math."):].split(".", 1)[0]
                # Both the imported name and the head module name are
                # candidate PM op names.
                for cand in (alias.name, head):
                    if cand and cand in known_ops:
                        alias_map[bound_name] = cand
                        break

    deps: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name != op_name:
            continue
        # Walk inside this function's body
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                if sub.id in known_ops and sub.id != op_name:
                    deps.add(sub.id)
                elif sub.id in alias_map and alias_map[sub.id] != op_name:
                    deps.add(alias_map[sub.id])
            elif isinstance(sub, ast.Attribute) and isinstance(sub.attr, str):
                if sub.attr in known_ops and sub.attr != op_name:
                    deps.add(sub.attr)
        break
    return deps


def build_dependency_graph() -> dict[str, set[str]]:
    """Return ``{pm_module: set_of_pm_modules_it_depends_on}``.

    The keys are exactly ``PM_CATEGORIES``. Modules with no detectable
    dependencies map to an empty set. Self-loops are not produced.
    """
    graph: dict[str, set[str]] = {}
    for cat in PM_CATEGORIES:
        try:
            graph[cat] = module_imports(cat)
        except FileNotFoundError:
            graph[cat] = set()
    return graph


def to_mermaid(graph: dict[str, set[str]], layout: str = "LR") -> str:
    """Render ``graph`` as a Mermaid block.

    Parameters
    ----------
    graph : dict[str, set[str]]
    layout : str
        ``LR`` (left-to-right) or ``TB`` (top-to-bottom). Mermaid also
        accepts ``RL`` and ``BT``. Anything else raises ValueError.

    Output is a triple-backtick fenced block ready to drop into
    Markdown.
    """
    if layout not in ("LR", "RL", "TB", "BT"):
        raise ValueError(f"layout must be one of LR/RL/TB/BT, got {layout!r}")
    lines = ["```mermaid", f"graph {layout}"]
    nodes = sorted(graph.keys())
    # Declare nodes first (gives them stable, readable labels even when
    # they have no edges).
    for n in nodes:
        # Sanitize node id for Mermaid (no dots, dashes ok). Our names
        # are already safe but be defensive.
        safe = n.replace(".", "_")
        lines.append(f"  {safe}[{n}]")
    # Edges
    for src in nodes:
        for dst in sorted(graph.get(src, ())):
            ssrc = src.replace(".", "_")
            sdst = dst.replace(".", "_")
            lines.append(f"  {ssrc} --> {sdst}")
    lines.append("```")
    return "\n".join(lines)


def to_dot(graph: dict[str, set[str]]) -> str:
    """Render ``graph`` in Graphviz DOT format."""
    lines = ["digraph prometheus_math {", "  rankdir=LR;"]
    for n in sorted(graph.keys()):
        lines.append(f'  "{n}";')
    for src in sorted(graph.keys()):
        for dst in sorted(graph.get(src, ())):
            lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    return "\n".join(lines)


def cycle_detection(graph: dict[str, set[str]]) -> list[list[str]]:
    """Return a list of cycles in ``graph``. Empty list iff acyclic.

    Uses Tarjan's strongly-connected-components algorithm. Each SCC of
    size > 1 is reported as a single cycle (the nodes of the SCC, sorted).
    Self-loops (size-1 SCCs with a self-edge) are also reported.
    """
    # Tarjan's SCC
    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    sccs: list[list[str]] = []

    def strongconnect(v: str) -> None:
        indices[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)
        for w in graph.get(v, ()):
            if w not in indices:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], indices[w])
        if lowlinks[v] == indices[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp.append(w)
                if w == v:
                    break
            sccs.append(comp)

    for v in graph:
        if v not in indices:
            strongconnect(v)

    cycles: list[list[str]] = []
    for comp in sccs:
        if len(comp) > 1:
            cycles.append(sorted(comp))
        elif len(comp) == 1:
            v = comp[0]
            if v in graph.get(v, set()):
                cycles.append([v])
    return cycles


def composition_opportunities(
    graph: dict[str, set[str]] | None = None,
) -> list[tuple[str, str]]:
    """Pairs of PM modules that aren't yet composed but plausibly could be.

    Heuristic: a pair (A, B) is reported when:
      - A and B are in PM_CATEGORIES,
      - neither A->B nor B->A is in the graph,
      - A != B,
      - and at least one is in the "Tier 1" mathematical core
        (number_theory / elliptic_curves / number_fields / topology).

    Output is sorted lexicographically by (A, B).
    """
    if graph is None:
        graph = build_dependency_graph()
    core = {"number_theory", "elliptic_curves", "number_fields", "topology"}
    pairs: list[tuple[str, str]] = []
    cats = sorted(PM_CATEGORIES)
    for i, a in enumerate(cats):
        for b in cats[i + 1:]:
            if a == b:
                continue
            if b in graph.get(a, set()):
                continue
            if a in graph.get(b, set()):
                continue
            if a in core or b in core:
                pairs.append((a, b))
    return pairs


__all__ = [
    "PM_CATEGORIES",
    "module_imports",
    "operation_dependencies",
    "build_dependency_graph",
    "to_mermaid",
    "to_dot",
    "cycle_detection",
    "composition_opportunities",
]
