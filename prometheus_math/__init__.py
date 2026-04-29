"""Prometheus Math — unified API over the mathematical-software arsenal.

A single import for Prometheus researchers. Every supported mathematical
operation has one canonical entry point, with backend dispatch to the
fastest available implementation.

Usage:

    import prometheus_math as pm

    pm.number_theory.class_number('x^2+5')              # 2
    pm.elliptic_curves.analytic_sha([0,-1,1,-10,-20])    # {'rounded': 1, ...}
    pm.topology.hyperbolic_volume('4_1')                 # 2.0298832...
    pm.optimization.solve_mip(c, A_ub, b_ub)             # via SCIP/OR-Tools/HiGHS
    pm.numerics.zeta(0.5 + 14.13j, prec=50)              # mpmath

    pm.registry.installed()    # capability matrix
    pm.doc.arsenal()           # write/refresh ARSENAL.md

Design:
- Categorical modules expose the API surface ("number_theory.class_number").
- Backends in prometheus_math.backends/ are thin adapters around each tool.
- registry.py scans for installed backends at import; capability matrix
  is available at runtime.
- ARSENAL.md is auto-generated from the registry.

See also:
- techne/ARSENAL_ROADMAP.md for the long-term target list.
- prometheus_math/ARSENAL.md for the researcher-facing API reference.
"""

__version__ = "0.1.0"

from . import registry  # noqa: F401 — populates capability matrix at import
from . import (  # noqa: F401
    number_theory,
    elliptic_curves,
    number_fields,
    topology,
    combinatorics,
    optimization,
    numerics,
    symbolic,
    algebraic_geometry,
    algebraic_geometry_normal_form,
    galois,
    iwasawa,
)
from . import numerics_special_hurwitz  # noqa: F401
from . import numerics_special  # noqa: F401  -- facade namespace
from . import combinatorics_partitions  # noqa: F401  -- partitions / Young tableaux
from . import combinatorics_permutations  # noqa: F401  -- permutations / Bruhat
from . import combinatorics_posets  # noqa: F401  -- finite posets / lattices
from . import geometry_convex_hull  # noqa: F401  -- convex hulls (qhull)
from . import geometry_delaunay  # noqa: F401  -- Delaunay triangulation (qhull)
from . import doc  # noqa: F401

# Optional SDP module (cvxpy-backed). Skip silently if cvxpy missing.
try:
    from . import optimization_sdp  # noqa: F401
    _HAS_OPT_SDP = True
except Exception:  # pragma: no cover
    _HAS_OPT_SDP = False

# Optional QP module (cvxpy- or scipy-backed). Skip silently if both missing.
try:
    from . import optimization_qp  # noqa: F401
    _HAS_OPT_QP = True
except Exception:  # pragma: no cover
    _HAS_OPT_QP = False

# Optional SOCP module (cvxpy-backed). Skip silently if cvxpy missing.
try:
    from . import optimization_socp  # noqa: F401
    _HAS_OPT_SOCP = True
except Exception:  # pragma: no cover
    _HAS_OPT_SOCP = False

# Optional metaheuristics module (CMA-ES via cma, GA via deap, simulated
# annealing via scipy, PSO native). Module imports cleanly even without the
# optional backends; individual entry points raise ImportError on call.
try:
    from . import optimization_metaheuristics  # noqa: F401
    _HAS_OPT_METAHEURISTICS = True
except Exception:  # pragma: no cover
    _HAS_OPT_METAHEURISTICS = False

# Optional submodule: tensor decompositions (CP, Tucker, TT) via tensorly.
try:
    from . import symbolic_tensor_decomp  # noqa: F401
    _HAS_SYMBOLIC_TENSOR_DECOMP = True
except Exception:  # pragma: no cover
    _HAS_SYMBOLIC_TENSOR_DECOMP = False

# viz: notebook-ready knot/link diagram rendering. Optional in the
# sense that it depends on matplotlib + snappy; protect the rest of pm
# from import errors if either is missing.
try:
    from . import viz  # noqa: F401
    _HAS_VIZ = True
except Exception:  # pragma: no cover
    _HAS_VIZ = False

# Optional research-thread subpackage (may fail to import if a sibling
# module is being edited; don't crash the rest of pm if so).
try:
    from . import research  # noqa: F401
    _HAS_RESEARCH = True
except Exception:  # pragma: no cover
    _HAS_RESEARCH = False

# hecke imports cypari + LMFDB; protect the rest of pm from import errors.
try:
    from . import hecke  # noqa: F401
    _HAS_HECKE = True
except Exception:  # pragma: no cover
    _HAS_HECKE = False

# recipes: end-to-end recipe galleries (persistent homology, ...).  Optional
# because some galleries depend on heavy backends (gudhi, ripser, ...).
try:
    from . import recipes  # noqa: F401
    _HAS_RECIPES = True
except Exception:  # pragma: no cover
    _HAS_RECIPES = False

# modular imports cypari + LMFDB; protect the rest of pm from import errors.
try:
    from . import modular  # noqa: F401
    _HAS_MODULAR = True
except Exception:  # pragma: no cover
    _HAS_MODULAR = False

__all__ = [
    "registry",
    "doc",
    "number_theory",
    "elliptic_curves",
    "number_fields",
    "topology",
    "combinatorics",
    "optimization",
    "numerics",
    "numerics_special",
    "numerics_special_hurwitz",
    "symbolic",
    "algebraic_geometry",
    "algebraic_geometry_normal_form",
    "galois",
    "iwasawa",
    "geometry_convex_hull",
    "geometry_delaunay",
]
if _HAS_RESEARCH:
    __all__.append("research")
if _HAS_HECKE:
    __all__.append("hecke")
if _HAS_MODULAR:
    __all__.append("modular")
if _HAS_VIZ:
    __all__.append("viz")
if _HAS_RECIPES:
    __all__.append("recipes")
if _HAS_SYMBOLIC_TENSOR_DECOMP:
    __all__.append("symbolic_tensor_decomp")
if _HAS_OPT_SDP:
    __all__.append("optimization_sdp")
if _HAS_OPT_QP:
    __all__.append("optimization_qp")
if _HAS_OPT_SOCP:
    __all__.append("optimization_socp")
if _HAS_OPT_METAHEURISTICS:
    __all__.append("optimization_metaheuristics")
