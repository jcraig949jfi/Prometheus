"""Capability registry for prometheus_math.

Detects available backends at import time. The capability matrix is
queryable at runtime via `installed()`, and feeds into ARSENAL.md
generation in `doc.py`.

Each backend has a name, an import probe, and a category. Probes are
cheap (just `importlib.util.find_spec` or a quick `import`); they do not
load heavy modules.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Backend:
    name: str
    kind: str  # "python", "binary"
    category: str
    import_name: Optional[str] = None  # for python backends
    binary_name: Optional[str] = None  # for native binaries
    description: str = ""
    available: bool = field(default=False, init=False)
    version: Optional[str] = field(default=None, init=False)
    error: Optional[str] = field(default=None, init=False)


_BACKENDS: list[Backend] = [
    # CAS
    Backend("sympy", "python", "CAS", import_name="sympy",
            description="Pure-Python symbolic computation"),
    Backend("sage", "python", "CAS", import_name="sage",
            description="SageMath meta-CAS (heavy install)"),
    # Number theory
    Backend("cypari", "python", "NT", import_name="cypari",
            description="PARI/GP via cypari (number theory)"),
    Backend("flint", "python", "NT", import_name="flint",
            description="python-flint (fast NT primitives)"),
    Backend("gmpy2", "python", "NUM", import_name="gmpy2",
            description="GMP/MPFR/MPC arbitrary precision"),
    # Numerics
    Backend("numpy", "python", "NUM", import_name="numpy",
            description="Array computing"),
    Backend("scipy", "python", "NUM", import_name="scipy",
            description="Scientific algorithms"),
    Backend("mpmath", "python", "NUM", import_name="mpmath",
            description="Arbitrary-precision floats"),
    # Topology
    Backend("snappy", "python", "TOP", import_name="snappy",
            description="3-manifolds, hyperbolic geometry"),
    Backend("knot_floer_homology", "python", "TOP",
            import_name="knot_floer_homology",
            description="Heegaard Floer knot homology"),
    Backend("gudhi", "python", "TOP", import_name="gudhi",
            description="Persistent homology, TDA"),
    Backend("ripser", "python", "TOP", import_name="ripser",
            description="Fast Vietoris-Rips persistence"),
    Backend("persim", "python", "TOP", import_name="persim",
            description="Persistence images, distances"),
    # Combinatorics
    Backend("networkx", "python", "COMB", import_name="networkx",
            description="Graph theory"),
    Backend("chipfiring", "python", "COMB", import_name="chipfiring",
            description="Chip-firing, Baker-Norine rank"),
    Backend("galois", "python", "COMB", import_name="galois",
            description="GF(p^n) arithmetic, error-correcting codes"),
    # SAT / SMT
    Backend("z3", "python", "SAT", import_name="z3",
            description="Z3 SMT solver"),
    Backend("pysat", "python", "SAT", import_name="pysat",
            description="PySAT (Glucose, MiniSat-class)"),
    # Optimization
    Backend("pyscipopt", "python", "OPT", import_name="pyscipopt",
            description="SCIP MIP/LP"),
    Backend("ortools", "python", "OPT", import_name="ortools",
            description="Google OR-Tools / CP-SAT"),
    Backend("highspy", "python", "OPT", import_name="highspy",
            description="HiGHS LP/MIP"),
    Backend("pulp", "python", "OPT", import_name="pulp",
            description="PuLP modeling layer"),
    Backend("cvxpy", "python", "OPT", import_name="cvxpy",
            description="Convex optimization"),
    # ML
    Backend("torch", "python", "AI", import_name="torch",
            description="PyTorch"),
    # Native binaries we'd dispatch to via subprocess
    Backend("gap", "binary", "GT", binary_name="gap",
            description="GAP (groups, representations)"),
    Backend("macaulay2", "binary", "AG", binary_name="M2",
            description="Macaulay2 (commutative algebra)"),
    Backend("singular", "binary", "AG", binary_name="Singular",
            description="Singular (polynomial rings)"),
    Backend("julia", "binary", "lang", binary_name="julia",
            description="Julia (gateway to OSCAR/Hecke/Nemo)"),
    Backend("lean", "binary", "PA", binary_name="lean",
            description="Lean 4 theorem prover"),
    Backend("R", "binary", "stats", binary_name="Rscript",
            description="R statistics environment"),
]


def _probe_python(b: Backend) -> None:
    spec = importlib.util.find_spec(b.import_name)
    if spec is None:
        b.available = False
        b.error = "not installed"
        return
    try:
        # Light probe — just attribute lookup
        import importlib as _il
        m = _il.import_module(b.import_name)
        b.available = True
        b.version = getattr(m, "__version__", None) or getattr(m, "VERSION", None)
        if b.version is None:
            b.version = "?"
    except Exception as e:
        b.available = False
        b.error = f"import failed: {type(e).__name__}: {e}"


def _probe_binary(b: Backend) -> None:
    path = shutil.which(b.binary_name)
    if path is None:
        b.available = False
        b.error = "binary not on PATH"
        return
    b.available = True
    # Try a --version probe; some binaries don't support it
    try:
        out = subprocess.run([b.binary_name, "--version"],
                             capture_output=True, text=True, timeout=5)
        v = (out.stdout or out.stderr).splitlines()[0].strip()[:80]
        b.version = v if v else "installed"
    except Exception:
        b.version = "installed"


def _probe_all() -> None:
    for b in _BACKENDS:
        try:
            if b.kind == "python":
                _probe_python(b)
            elif b.kind == "binary":
                _probe_binary(b)
        except Exception as e:
            b.available = False
            b.error = f"probe error: {e}"


_probe_all()


def installed() -> dict[str, dict]:
    """Return a dict of backend_name -> {available, version, kind, category, description, error}."""
    return {
        b.name: {
            "available": b.available,
            "version": b.version,
            "kind": b.kind,
            "category": b.category,
            "description": b.description,
            "error": b.error,
        }
        for b in _BACKENDS
    }


def is_available(name: str) -> bool:
    """True iff backend `name` is available."""
    for b in _BACKENDS:
        if b.name == name:
            return b.available
    return False


def by_category(cat: str) -> list[Backend]:
    """All backends in category `cat`."""
    return [b for b in _BACKENDS if b.category == cat]


def all_backends() -> list[Backend]:
    return list(_BACKENDS)


def summary() -> str:
    """One-line status summary."""
    n_avail = sum(1 for b in _BACKENDS if b.available)
    n_total = len(_BACKENDS)
    cats = sorted({b.category for b in _BACKENDS if b.available})
    return f"{n_avail}/{n_total} backends available across {len(cats)} categories: {', '.join(cats)}"
