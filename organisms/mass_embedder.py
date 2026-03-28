"""
Mass Embedder — Embed the entire library manifest into the universal vector space.

Reads agents/eos/data/library_manifest.json (2,970 discovered functions),
wraps each as a callable, embeds with universal_embedder.embed(), and stores:
  - Zarr array at organisms/embedded_library.zarr (N x 240 float32)
  - DuckDB table at organisms/library_embeddings.duckdb (metadata + index)

Uses SIGNATURE-DRIVEN wrapping: reads param metadata from manifest to construct
the right wrapper without trial-and-error calls that can hang on C extensions.
"""

import json
import sys
import os
import io
import time
import warnings
import importlib
import traceback
import threading
import numpy as np
from pathlib import Path

# Suppress all warnings globally
warnings.filterwarnings("ignore")
np.seterr(all="ignore")
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Project root
ROOT = Path(__file__).resolve().parent.parent
ORGANISMS = ROOT / "organisms"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ORGANISMS))

from universal_embedder import embed, PROBES

# Constants
MANIFEST_PATH = ROOT / "agents" / "eos" / "data" / "library_manifest.json"
ZARR_PATH = ORGANISMS / "embedded_library.zarr"
DUCKDB_PATH = ORGANISMS / "library_embeddings.duckdb"
CHECKPOINT_PATH = ORGANISMS / "mass_embedder_checkpoint.json"
EMBED_DIM = len(PROBES) * 12  # 20 probes * 12 features = 240
CHECKPOINT_INTERVAL = 500
REPORT_INTERVAL = 100
FLUSH_INTERVAL = 100

# ============================================================
# Blacklist: functions known to crash, hang, or be non-mathematical
# ============================================================
BLACKLIST_NAMES = {
    "numpy.show_config", "numpy.info", "numpy.test",
    "numpy.linalg.test", "numpy.fft.test",
    "numpy.polynomial.test", "numpy.random.test",
    "numpy.lookfor", "numpy.who", "numpy.source",
    "numpy.deprecate", "numpy.deprecate_with_doc",
    "numpy.get_include", "numpy.get_printoptions",
    "numpy.set_printoptions", "numpy.set_string_function",
    "numpy.show_runtime",
    "numpy.random.seed", "numpy.random.get_state", "numpy.random.set_state",
    "sympy.init_printing", "sympy.init_session", "sympy.pprint",
    "sympy.pretty", "sympy.preview", "sympy.doctest",
    # sympy plotting (requires matplotlib, hangs)
    "sympy.plot", "sympy.plot3d", "sympy.plot_implicit",
    "sympy.plot_parametric", "sympy.plot3d_parametric_line",
    "sympy.plot3d_parametric_surface", "sympy.textplot",
    # sympy integral transforms (symbolic integration, very slow)
    "sympy.fourier_transform", "sympy.inverse_fourier_transform",
    "sympy.laplace_transform", "sympy.inverse_laplace_transform",
    "sympy.mellin_transform", "sympy.inverse_mellin_transform",
    "sympy.hankel_transform", "sympy.inverse_hankel_transform",
    "sympy.cosine_transform", "sympy.inverse_cosine_transform",
    "sympy.sine_transform", "sympy.inverse_sine_transform",
    # sympy functions that can hang on numeric input
    "sympy.periodicity", "sympy.is_monotonic", "sympy.is_convex",
    "sympy.is_decreasing", "sympy.is_increasing",
    "sympy.solve", "sympy.dsolve", "sympy.pdsolve",
    "sympy.integrate", "sympy.trigsimp",
    "sympy.simplify", "sympy.nsimplify", "sympy.posify",
    "sympy.series", "sympy.limit", "sympy.limit_seq",
    "sympy.summation", "sympy.product",
    "sympy.reduced", "sympy.groebner",
    "sympy.rsolve", "sympy.rsolve_poly", "sympy.rsolve_ratio",
    "sympy.rsolve_hyper",
    # Known segfault-prone: need very specific tensor shapes
    "numpy.linalg.tensorinv", "numpy.linalg.tensorsolve",
    # scipy linalg segfaulters
    "scipy.linalg.lapack", "scipy.linalg.blas",
    # scipy.special: known to hang/segfault with certain inputs
    # Spheroidal wave functions
    "scipy.special.obl_ang1", "scipy.special.obl_ang1_cv",
    "scipy.special.obl_rad1", "scipy.special.obl_rad1_cv",
    "scipy.special.obl_rad2", "scipy.special.obl_rad2_cv",
    "scipy.special.pro_ang1", "scipy.special.pro_ang1_cv",
    "scipy.special.pro_rad1", "scipy.special.pro_rad1_cv",
    "scipy.special.pro_rad2", "scipy.special.pro_rad2_cv",
    "scipy.special.obl_cv", "scipy.special.pro_cv",
    "scipy.special.obl_cv_seq", "scipy.special.pro_cv_seq",
    # Ellipsoidal harmonics (integration-based, slow)
    "scipy.special.ellip_harm", "scipy.special.ellip_harm_2",
    "scipy.special.ellip_normal",
    # Wright-Bessel (slow convergence)
    "scipy.special.wright_bessel", "scipy.special.log_wright_bessel",
    # Spherical harmonics with complex output + potential segfault
    "scipy.special.sph_harm",
    "scipy.special.sph_harm_y", "scipy.special.sph_harm_y_all",
    "scipy.special.sph_legendre_p", "scipy.special.sph_legendre_p_all",
    "scipy.special.assoc_legendre_p", "scipy.special.assoc_legendre_p_all",
    # Parabolic cylinder functions (segfault-prone)
    "scipy.special.pbdv", "scipy.special.pbvv", "scipy.special.pbwa",
    "scipy.special.pbdv_seq", "scipy.special.pbvv_seq", "scipy.special.pbdn_seq",
    # Mathieu functions (can hang)
    "scipy.special.mathieu_cem", "scipy.special.mathieu_sem",
    "scipy.special.mathieu_modcem1", "scipy.special.mathieu_modcem2",
    "scipy.special.mathieu_modsem1", "scipy.special.mathieu_modsem2",
    # Utility functions
    "scipy.special.seterr", "scipy.special.geterr",
    # Lamé functions
    "scipy.special.lmbda",
    # clpmn/lpmn/lqmn can segfault with wrong m,n
    "scipy.special.clpmn", "scipy.special.lpmn", "scipy.special.lqmn",
}

BLACKLIST_SUBSTRINGS = [
    "show_config", "__test", "print_function",
    "setup_module", "teardown_module",
]


def is_blacklisted(qualified_name, name):
    if qualified_name in BLACKLIST_NAMES:
        return True
    for pat in BLACKLIST_SUBSTRINGS:
        if pat in qualified_name.lower():
            return True
    if name.startswith("__") and name.endswith("__"):
        return True
    # Skip test runners and doctest functions
    if name in ("test", "doctest"):
        return True
    return False


# ============================================================
# Thread-based timeout runner
# ============================================================

def run_with_timeout(fn, args=(), kwargs=None, timeout=10.0):
    """Run fn(*args) in a daemon thread. Returns (ok, result) within timeout."""
    if kwargs is None:
        kwargs = {}
    result_box = {"ok": False, "result": None, "error": None}

    def target():
        try:
            result_box["result"] = fn(*args, **kwargs)
            result_box["ok"] = True
        except Exception as e:
            result_box["error"] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return False, None
    return result_box["ok"], result_box["result"]


# ============================================================
# SIGNATURE-DRIVEN wrapper construction
# ============================================================

def count_required_args(entry):
    """Count the number of required positional arguments from manifest signature."""
    sig = entry.get("signature", {})
    params = sig.get("params", [])
    count = 0
    for p in params:
        kind = p.get("kind", "")
        has_default = p.get("has_default", True)
        name = p.get("name", "")
        # Skip *args, **kwargs, keyword-only with defaults
        if kind in ("VAR_POSITIONAL", "VAR_KEYWORD"):
            continue
        if kind == "KEYWORD_ONLY":
            continue
        if not has_default:
            count += 1
    return count


def build_wrapper(fn, entry):
    """
    Build a single-arg wrapper based on signature metadata.
    Returns (wrapper, wrap_type) or (None, reason).
    """
    qualified_name = entry["qualified_name"]
    module = entry.get("module", "")
    category = entry.get("category", "")
    is_ufunc = entry.get("is_ufunc", False)
    n_required = count_required_args(entry)

    # Not callable?
    if not callable(fn):
        try:
            val = float(fn)
            return (lambda x, v=val: v), "constant"
        except Exception:
            return None, "not_callable"

    # Distribution sub-methods
    if entry.get("_dist_method"):
        return _wrap_dist_method(fn, entry)

    # Probability distributions
    if category == "probability_distribution":
        return _wrap_distribution(fn, entry)

    # sympy: wrap with numeric conversion
    if module.startswith("sympy"):
        return _wrap_sympy(fn, entry, n_required)

    # networkx: wrap with graph objects
    if module == "networkx":
        return _wrap_networkx(fn, entry, n_required)

    # scipy.special: clamp all inputs to safe ranges to avoid C-level hangs
    if module == "scipy.special":
        if is_ufunc:
            return _wrap_special_ufunc(fn, entry, n_required)
        else:
            return _wrap_special_nonufunc(fn, entry, n_required)

    # filterpy: these are typically classes, not simple callables
    if module.startswith("filterpy"):
        return _wrap_filterpy(fn, entry)

    # tensorly: decomposition methods need tensor input
    if module.startswith("tensorly"):
        return _wrap_tensorly(fn, entry)

    # numpy.linalg: needs matrix inputs (scalars cause segfaults)
    if module == "numpy.linalg":
        return _wrap_linalg(fn, entry, n_required)

    # scipy.linalg: also needs matrix inputs
    if module == "scipy.linalg":
        return _wrap_linalg(fn, entry, n_required)

    # numpy.fft: needs array inputs
    if module == "numpy.fft":
        return _wrap_fft(fn, entry, n_required)

    # numpy.random: wrap as generators
    if module == "numpy.random":
        return _wrap_random(fn, entry, n_required)

    # scipy.signal: many need array inputs
    if module == "scipy.signal":
        return _wrap_signal(fn, entry, n_required)

    # scipy.optimize: needs callable + bounds typically
    if module == "scipy.optimize":
        return _wrap_optimize(fn, entry, n_required)

    # scipy.integrate: needs callable typically
    if module == "scipy.integrate":
        return _wrap_integrate(fn, entry, n_required)

    # scipy.interpolate: needs x,y data
    if module == "scipy.interpolate":
        return _wrap_interpolate(fn, entry, n_required)

    # ufuncs: accept element-wise input, clamp to safe range for multi-arg
    if is_ufunc:
        if n_required <= 1:
            def ufunc_w1(x, _f=fn):
                return _f(x)
            return ufunc_w1, "ufunc_1arg"
        elif n_required == 2:
            def ufunc_w2(x, _f=fn):
                a = np.clip(np.asarray(x, dtype=float), -10, 10)
                return _f(a, a)
            return ufunc_w2, "ufunc_2arg"
        elif n_required == 3:
            def ufunc_w3(x, _f=fn):
                a = np.clip(np.asarray(x, dtype=float), -5, 5)
                return _f(a, a, a)
            return ufunc_w3, "ufunc_3arg"
        else:
            def ufunc_wn(x, _f=fn, _n=n_required):
                a = np.clip(np.asarray(x, dtype=float), -5, 5)
                return _f(*([a] * _n))
            return ufunc_wn, f"ufunc_{n_required}arg"

    # General: based on required arg count
    # Ensure array input for multi-arg functions to avoid C segfaults
    if n_required == 0:
        return (lambda x, _f=fn: _f(x)), "passthrough_0"
    elif n_required == 1:
        return (lambda x, _f=fn: _f(x)), "passthrough_1"
    elif n_required == 2:
        # Safe: use np.asarray to ensure proper types
        def wrapper_2(x, _f=fn):
            a = np.asarray(x)
            return _f(a, a)
        return wrapper_2, "fill_2arg"
    elif n_required == 3:
        def wrapper_3(x, _f=fn):
            a = np.asarray(x)
            return _f(a, a, a)
        return wrapper_3, "fill_3arg"
    else:
        def wrapper_n(x, _f=fn, _n=n_required):
            a = np.asarray(x)
            return _f(*([a] * _n))
        return wrapper_n, f"fill_{n_required}arg"


def _sympy_call_with_timeout(fn, args, timeout=2.0):
    """Call a sympy function with a thread timeout to avoid hanging."""
    ok, result = run_with_timeout(fn, args, timeout=timeout)
    if ok:
        if hasattr(result, 'evalf'):
            try:
                return float(result.evalf())
            except Exception:
                return 0.0
        if hasattr(result, '__float__'):
            try:
                return float(result)
            except Exception:
                return 0.0
        return result
    raise TimeoutError("sympy call timed out")


def _wrap_sympy(fn, entry, n_required):
    """Wrap sympy function with per-call timeout."""
    if not callable(fn):
        try:
            val = float(fn)
            return (lambda x, v=val: v), "sympy_constant"
        except Exception:
            return None, "sympy_not_callable"

    if n_required == 0:
        def wrapper(x, _f=fn):
            val = float(x) if not isinstance(x, np.ndarray) else float(np.mean(x))
            return _sympy_call_with_timeout(_f, (val,))
        return wrapper, "sympy_0"
    elif n_required == 1:
        def wrapper(x, _f=fn):
            val = float(x) if not isinstance(x, np.ndarray) else float(np.mean(x))
            try:
                return _sympy_call_with_timeout(_f, (val,))
            except (TypeError, ValueError):
                return _sympy_call_with_timeout(_f, (max(1, int(abs(val))),))
        return wrapper, "sympy_1"
    elif n_required == 2:
        def wrapper(x, _f=fn):
            val = float(x) if not isinstance(x, np.ndarray) else float(np.mean(x))
            try:
                return _sympy_call_with_timeout(_f, (val, val))
            except (TypeError, ValueError):
                iv = max(1, int(abs(val)))
                return _sympy_call_with_timeout(_f, (iv, iv))
        return wrapper, "sympy_2"
    else:
        def wrapper(x, _f=fn, _n=n_required):
            val = float(x) if not isinstance(x, np.ndarray) else float(np.mean(x))
            try:
                return _sympy_call_with_timeout(_f, tuple([val] * _n))
            except (TypeError, ValueError):
                iv = max(1, int(abs(val)))
                return _sympy_call_with_timeout(_f, tuple([iv] * _n))
        return wrapper, f"sympy_{n_required}"


def _wrap_networkx(fn, entry, n_required):
    """Wrap networkx functions using pre-built graph objects."""
    try:
        import networkx as nx
    except ImportError:
        return None, "nx_import_fail"

    G = nx.complete_graph(5)
    nx.set_edge_attributes(G, 1.0, "weight")

    name = entry["name"]
    sig = entry.get("signature", {})
    params = sig.get("params", [])
    param_names = [p.get("name", "") for p in params]

    # Graph generators: take int n, return a graph
    # Detect by name patterns
    gen_patterns = ["_graph", "complete_", "cycle_", "path_", "star_",
                    "wheel_", "grid_", "random_", "barabasi_", "erdos_",
                    "watts_", "petersen_", "tutte_"]
    if any(pat in name.lower() for pat in gen_patterns) and n_required >= 1:
        def wrapper(x, _f=fn):
            n = max(2, min(20, int(abs(float(np.mean(np.asarray(x).flatten()))))))
            return _f(n)
        return wrapper, "nx_generator"

    # Functions that take a graph as first arg
    if n_required >= 1 and len(param_names) >= 1:
        first_param = param_names[0].lower()
        if first_param in ("g", "graph", "nbunch1"):
            if n_required == 1:
                return (lambda x, _f=fn, _G=G: _f(_G)), "nx_graph"
            elif n_required == 2:
                # (G, node) or (G, source)
                return (lambda x, _f=fn, _G=G: _f(_G, 0)), "nx_graph_node"
            elif n_required == 3:
                return (lambda x, _f=fn, _G=G: _f(_G, 0, 4)), "nx_graph_st"
            else:
                return (lambda x, _f=fn, _G=G: _f(_G, *([0] * (n_required - 1)))), f"nx_graph_{n_required}"

    # Fallback: try just passing a number
    if n_required <= 1:
        def wrapper(x, _f=fn):
            return _f(x)
        return wrapper, "nx_scalar"

    return None, "nx_unwrappable"


def _wrap_special_ufunc(fn, entry, n_required):
    """Wrap scipy.special ufuncs with clamped inputs to prevent C-level hangs."""
    if n_required <= 1:
        def wrapper(x, _f=fn):
            a = np.clip(np.asarray(x, dtype=float), -20, 20)
            return _f(a)
        return wrapper, "special_ufunc_1"
    elif n_required == 2:
        def wrapper(x, _f=fn):
            a = np.clip(np.asarray(x, dtype=float), -5, 5)
            return _f(a, a)
        return wrapper, "special_ufunc_2"
    elif n_required == 3:
        def wrapper(x, _f=fn):
            a = np.clip(np.asarray(x, dtype=float), -3, 3)
            return _f(a, a, a)
        return wrapper, "special_ufunc_3"
    elif n_required == 4:
        def wrapper(x, _f=fn):
            a = np.clip(np.asarray(x, dtype=float), -2, 2)
            return _f(a, a, a, a)
        return wrapper, "special_ufunc_4"
    else:
        def wrapper(x, _f=fn, _n=n_required):
            a = np.clip(np.asarray(x, dtype=float), -2, 2)
            return _f(*([a] * _n))
        return wrapper, f"special_ufunc_{n_required}"


def _wrap_special_nonufunc(fn, entry, n_required):
    """Wrap non-ufunc scipy.special functions that need integer order params."""
    sig = entry.get("signature", {})
    params = sig.get("params", [])
    req_params = [p for p in params
                  if not p.get("has_default", True)
                  and p.get("kind", "") not in ("VAR_POSITIONAL", "VAR_KEYWORD", "KEYWORD_ONLY")]
    param_names = [p["name"] for p in req_params]

    # Classify each required param as "int-like" or "float-like"
    int_param_names = {"n", "nt", "m", "k"}
    # Note: N, K, p excluded - these are often float in scipy.special

    def make_arg(param_name, x_val):
        """Create appropriate arg for a parameter based on its name."""
        pn = param_name.lower()
        if pn in int_param_names:
            return max(1, min(8, int(abs(x_val))))
        else:
            # Clamp floats to safe range for special functions
            return float(np.clip(x_val, -5, 5))

    if n_required == 1:
        pname = param_names[0] if param_names else "x"
        if pname.lower() in int_param_names:
            def wrapper(x, _f=fn):
                val = float(np.mean(np.asarray(x).flatten())) if isinstance(x, np.ndarray) else float(x)
                return _f(max(1, min(8, int(abs(val)))))
            return wrapper, "special_int1"
        else:
            def wrapper(x, _f=fn):
                return _f(np.clip(np.asarray(x, dtype=float), -20, 20))
            return wrapper, "special_float1"
    elif n_required == 2:
        def wrapper(x, _f=fn, _pnames=param_names):
            val = float(np.mean(np.asarray(x).flatten())) if isinstance(x, np.ndarray) else float(x)
            a0 = make_arg(_pnames[0], val) if len(_pnames) > 0 else float(np.clip(val, -5, 5))
            a1 = make_arg(_pnames[1], val) if len(_pnames) > 1 else float(np.clip(val, -5, 5))
            return _f(a0, a1)
        return wrapper, "special_2"
    elif n_required == 3:
        def wrapper(x, _f=fn, _pnames=param_names):
            val = float(np.mean(np.asarray(x).flatten())) if isinstance(x, np.ndarray) else float(x)
            args = [make_arg(_pnames[i], val) if i < len(_pnames) else float(np.clip(val, -3, 3))
                    for i in range(3)]
            return _f(*args)
        return wrapper, "special_3"
    else:
        def wrapper(x, _f=fn, _pnames=param_names, _n=n_required):
            val = float(np.mean(np.asarray(x).flatten())) if isinstance(x, np.ndarray) else float(x)
            args = [make_arg(_pnames[i], val) if i < len(_pnames) else float(np.clip(val, -2, 2))
                    for i in range(_n)]
            return _f(*args)
        return wrapper, f"special_{n_required}"


def _wrap_linalg(fn, entry, n_required):
    """Wrap numpy.linalg / scipy.linalg functions with safe matrix inputs."""
    name = entry["name"]

    # Functions that take a single matrix
    single_matrix = ["det", "eig", "eigh", "eigvals", "eigvalsh", "inv",
                     "cholesky", "matrix_rank", "norm", "qr", "svd", "svdvals",
                     "slogdet", "pinv", "matrix_norm", "matrix_transpose",
                     "trace", "expm", "logm", "sqrtm", "cosm", "sinm",
                     "tanhm", "sinhm", "coshm", "signm", "funm",
                     "schur", "hessenberg", "lu", "polar"]
    if name in single_matrix or n_required <= 1:
        def wrapper(x, _f=fn):
            # Convert input to a proper matrix
            a = np.asarray(x, dtype=float)
            if a.ndim < 2:
                if a.size == 1:
                    a = np.array([[float(a.flat[0])]])
                else:
                    n = int(np.sqrt(a.size))
                    if n * n == a.size:
                        a = a[:n*n].reshape(n, n)
                    else:
                        a = np.diag(a.flatten()[:min(5, a.size)])
            return _f(a)
        return wrapper, "linalg_matrix"

    # Functions that take (A, b) — solvers
    solvers = ["solve", "lstsq", "solve_triangular", "solve_banded",
               "solve_sylvester", "cho_solve", "lu_solve"]
    if name in solvers:
        def wrapper(x, _f=fn):
            a = np.asarray(x, dtype=float)
            if a.ndim < 2:
                if a.size == 1:
                    A = np.array([[float(a.flat[0]) + 1.0]])
                    b = np.array([float(a.flat[0])])
                else:
                    n = min(a.size, 5)
                    A = np.diag(a.flatten()[:n]) + np.eye(n)
                    b = a.flatten()[:n]
            else:
                A = a + np.eye(a.shape[0]) * 0.1
                b = a[:, 0]
            return _f(A, b)
        return wrapper, "linalg_solve"

    # Functions that take two matrices
    two_matrix = ["matmul", "multi_dot", "outer", "vecdot", "tensordot",
                  "kron", "block_diag"]
    if name in two_matrix:
        def wrapper(x, _f=fn):
            a = np.asarray(x, dtype=float)
            if a.ndim < 2:
                a = np.diag(a.flatten()[:min(5, max(a.size, 1))])
            if name == "multi_dot":
                return _f([a, a])
            return _f(a, a)
        return wrapper, "linalg_2mat"

    # matrix_power needs (matrix, n)
    if name == "matrix_power":
        def wrapper(x, _f=fn):
            a = np.asarray(x, dtype=float)
            if a.ndim < 2:
                a = np.diag(a.flatten()[:min(5, max(a.size, 1))])
            return _f(a, 2)
        return wrapper, "linalg_power"

    # vector_norm
    if name == "vector_norm":
        def wrapper(x, _f=fn):
            return _f(np.asarray(x, dtype=float).flatten())
        return wrapper, "linalg_vecnorm"

    # Default: pass as matrix
    def wrapper(x, _f=fn):
        a = np.asarray(x, dtype=float)
        if a.ndim < 2:
            a = np.diag(a.flatten()[:min(5, max(a.size, 1))])
        return _f(a)
    return wrapper, "linalg_default"


def _wrap_fft(fn, entry, n_required):
    """Wrap numpy.fft functions."""
    name = entry["name"]
    # fftfreq/rfftfreq take an integer n
    if "freq" in name:
        def wrapper(x, _f=fn):
            n = max(2, int(abs(float(np.mean(np.asarray(x).flatten())))))
            return _f(n)
        return wrapper, "fft_freq"
    # fftshift/ifftshift just rearrange
    if "shift" in name:
        return (lambda x, _f=fn: _f(np.asarray(x, dtype=float).flatten())), "fft_shift"
    # All others: pass array
    def wrapper(x, _f=fn):
        a = np.asarray(x, dtype=float)
        if a.ndim == 0:
            a = np.array([float(a)])
        return _f(a.flatten())
    return wrapper, "fft_array"


def _wrap_random(fn, entry, n_required):
    """Wrap numpy.random generators."""
    name = entry["name"]
    # Most random functions take a size parameter
    if n_required == 0:
        def wrapper(x, _f=fn):
            return _f()
        return wrapper, "random_0"
    elif n_required == 1:
        def wrapper(x, _f=fn):
            # Might need int (size) or might need shape param
            try:
                return _f(int(abs(float(np.mean(np.asarray(x).flatten())))) + 1)
            except Exception:
                return _f(x)
        return wrapper, "random_1"
    else:
        return None, "random_unwrappable"


def _wrap_signal(fn, entry, n_required):
    """Wrap scipy.signal functions."""
    name = entry["name"]
    if n_required <= 1:
        def wrapper(x, _f=fn):
            a = np.asarray(x, dtype=float)
            if a.ndim == 0:
                a = np.array([float(a)] * 10)
            return _f(a.flatten())
        return wrapper, "signal_1"
    elif n_required == 2:
        def wrapper(x, _f=fn):
            a = np.asarray(x, dtype=float).flatten()
            if a.size < 2:
                a = np.array([float(a.flat[0])] * 10)
            return _f(a, a)
        return wrapper, "signal_2"
    else:
        def wrapper(x, _f=fn, _n=n_required):
            a = np.asarray(x, dtype=float).flatten()
            if a.size < 2:
                a = np.array([float(a.flat[0])] * 10)
            return _f(*([a] * _n))
        return wrapper, f"signal_{n_required}"


def _wrap_optimize(fn, entry, n_required):
    """Wrap scipy.optimize functions."""
    name = entry["name"]
    # Most optimizers need a callable + initial guess
    # We embed a simple quadratic optimization
    if n_required <= 2:
        def wrapper(x, _f=fn):
            val = float(np.mean(np.asarray(x).flatten()))
            try:
                return _f(lambda t: (t - val) ** 2, val)
            except Exception:
                return _f(val)
        return wrapper, "optimize_func"
    return None, "optimize_unwrappable"


def _wrap_integrate(fn, entry, n_required):
    """Wrap scipy.integrate functions."""
    if n_required <= 2:
        def wrapper(x, _f=fn):
            val = float(np.mean(np.asarray(x).flatten()))
            try:
                return _f(lambda t: np.sin(t * val), 0, 1)
            except Exception:
                return _f(val)
        return wrapper, "integrate_func"
    return None, "integrate_unwrappable"


def _wrap_interpolate(fn, entry, n_required):
    """Wrap scipy.interpolate functions."""
    xdata = np.linspace(0, 1, 10)
    ydata = np.sin(xdata * 3)
    if n_required <= 2:
        def wrapper(x, _f=fn):
            try:
                interp = _f(xdata, ydata)
                val = float(np.mean(np.asarray(x).flatten()))
                val = np.clip(val, 0, 1)  # keep in domain
                return interp(val)
            except Exception:
                return _f(x)
        return wrapper, "interpolate_xy"
    return None, "interpolate_unwrappable"


def _wrap_distribution(fn, entry):
    """Wrap scipy.stats distribution."""
    # Try to get the pdf method via different instantiation strategies
    for method_name in ["pdf", "pmf", "cdf"]:
        for args in [(), (0, 1), (0.5,), (1,), (2, 0.5)]:
            try:
                dist = fn(*args)
                method = getattr(dist, method_name, None)
                if method is not None:
                    def wrapper(x, _m=method):
                        return _m(float(x) if not isinstance(x, np.ndarray) else x)
                    # Quick test
                    test_ok, _ = run_with_timeout(wrapper, (2.5,), timeout=2.0)
                    if test_ok:
                        return wrapper, f"dist_{method_name}"
            except Exception:
                continue

    # Try Binomial-like
    try:
        dist = fn(n=10, p=0.5)
        for method_name in ["pmf", "pdf", "cdf"]:
            method = getattr(dist, method_name, None)
            if method:
                def wrapper(x, _m=method):
                    return _m(float(x) if not isinstance(x, np.ndarray) else x)
                return wrapper, f"dist_{method_name}"
    except Exception:
        pass

    return None, "dist_unwrappable"


def _wrap_dist_method(fn, entry):
    """Wrap a distribution sub-method (pdf, cdf, entropy, mean, var)."""
    method_name = entry["_dist_method"]

    for args in [(), (0, 1), (0.5,), (1,), (2, 0.5)]:
        try:
            dist = fn(*args)
            method = getattr(dist, method_name, None)
            if method is None:
                continue
            if method_name in ("entropy", "mean", "var"):
                def wrapper(x, _m=method):
                    return float(_m())
                test_ok, _ = run_with_timeout(wrapper, (2.5,), timeout=2.0)
                if test_ok:
                    return wrapper, f"dist_{method_name}"
            else:
                def wrapper(x, _m=method):
                    return _m(float(x) if not isinstance(x, np.ndarray) else x)
                test_ok, _ = run_with_timeout(wrapper, (2.5,), timeout=2.0)
                if test_ok:
                    return wrapper, f"dist_{method_name}"
        except Exception:
            continue

    # Binomial-like
    try:
        dist = fn(n=10, p=0.5)
        method = getattr(dist, method_name, None)
        if method:
            if method_name in ("entropy", "mean", "var"):
                return (lambda x, _m=method: float(_m())), f"dist_{method_name}"
            else:
                return (lambda x, _m=method: _m(float(x) if not isinstance(x, np.ndarray) else x)), f"dist_{method_name}"
    except Exception:
        pass

    return None, "dist_method_unwrappable"


def _wrap_filterpy(fn, entry):
    """Wrap filterpy objects. Most are classes, not callables in the math sense."""
    return None, "filterpy_skip"


def _wrap_tensorly(fn, entry):
    """Wrap tensorly decomposition functions."""
    # These typically take a tensor and return decomposed components
    def wrapper(x, _f=fn):
        t = np.random.randn(4, 4, 4).astype(np.float64)
        return _f(t)
    return wrapper, "tensorly_tensor"


# ============================================================
# Import
# ============================================================

def import_function(entry):
    """Import a function given its manifest entry."""
    module_name = entry["module"]
    fn_name = entry["name"]
    try:
        mod = importlib.import_module(module_name)
        return getattr(mod, fn_name, None)
    except Exception:
        pass
    qualified_name = entry["qualified_name"]
    try:
        parts = qualified_name.rsplit(".", 1)
        if len(parts) == 2:
            mod = importlib.import_module(parts[0])
            return getattr(mod, parts[1], None)
    except Exception:
        pass
    return None


# ============================================================
# Storage
# ============================================================

def init_zarr(path, n_total):
    import zarr
    group = zarr.open_group(str(path), mode="w")
    group.create_array("addresses", shape=(n_total, EMBED_DIM),
                       chunks=(min(500, n_total), EMBED_DIM),
                       dtype=np.float32, fill_value=0.0)
    group.create_array("success_rates", shape=(n_total,),
                       chunks=(min(500, n_total),),
                       dtype=np.float32, fill_value=0.0)
    group.create_array("norms", shape=(n_total,),
                       chunks=(min(500, n_total),),
                       dtype=np.float32, fill_value=0.0)
    return group


def open_zarr(path):
    import zarr
    return zarr.open_group(str(path), mode="r+")


def init_duckdb(path):
    import duckdb
    conn = duckdb.connect(str(path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            idx INTEGER PRIMARY KEY,
            name VARCHAR, qualified_name VARCHAR, module VARCHAR,
            package VARCHAR, category VARCHAR, tags VARCHAR,
            wrap_type VARCHAR, success_rate FLOAT, address_norm FLOAT,
            embed_time_ms FLOAT, n_probes_success INTEGER,
            n_probes_error INTEGER, status VARCHAR, error_message VARCHAR
        )
    """)
    conn.execute("DELETE FROM embeddings")
    conn.commit()
    return conn


def _flush_db(db, rows):
    if not rows:
        return
    try:
        db.executemany("""
            INSERT OR REPLACE INTO embeddings
            (idx, name, qualified_name, module, package, category, tags,
             wrap_type, success_rate, address_norm, embed_time_ms,
             n_probes_success, n_probes_error, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        db.commit()
    except Exception as e:
        print(f"  [WARN] DuckDB batch error: {e}")
        for row in rows:
            try:
                db.execute("""
                    INSERT OR REPLACE INTO embeddings
                    (idx, name, qualified_name, module, package, category, tags,
                     wrap_type, success_rate, address_norm, embed_time_ms,
                     n_probes_success, n_probes_error, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, row)
            except Exception:
                pass
        db.commit()


def save_checkpoint(idx, stats):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump({"last_completed_idx": idx, "stats": stats,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}, f, indent=2)


def make_row(idx, name, qn, module, package, category, tags, wrap_type,
             sr, norm, time_ms, ns, ne, status, err=""):
    return (idx, name, qn, module, package, category, tags, wrap_type,
            float(sr), float(norm), float(time_ms), int(ns), int(ne), status, err)


# ============================================================
# Safe embed with thread timeout
# ============================================================

def safe_embed(wrapper, timeout=15.0):
    """Embed with thread-based timeout. Returns result dict or None."""
    ok, result = run_with_timeout(embed, (wrapper, 2.0), timeout=timeout)
    if ok and isinstance(result, dict) and "address" in result:
        return result
    return None


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 70)
    print("MASS EMBEDDER — Embedding the Library of Alexandria")
    print("=" * 70)
    print()

    # Load manifest
    print("[1/5] Loading manifest...")
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    discoveries = manifest["discoveries"]
    print(f"  {len(discoveries)} functions discovered")
    print()

    # Build work list (expanding distributions)
    print("[2/5] Building work list...")
    work_items = []
    for entry in discoveries:
        if entry.get("category") == "probability_distribution" and entry.get("embeddable_as"):
            for sub_name in entry["embeddable_as"]:
                sub_entry = dict(entry)
                method = sub_name.split(".")[-1]
                sub_entry["name"] = sub_name
                sub_entry["qualified_name"] = f"{entry['qualified_name']}.{method}"
                sub_entry["_dist_method"] = method
                sub_entry["_dist_base_name"] = entry["name"]
                work_items.append(sub_entry)
        else:
            work_items.append(entry)

    n_total = len(work_items)
    print(f"  {n_total} items after distribution expansion")
    print()

    # Initialize storage
    print("[3/5] Initializing storage...")
    zarr_group = init_zarr(ZARR_PATH, n_total)
    db = init_duckdb(DUCKDB_PATH)
    print(f"  Zarr: {ZARR_PATH} ({n_total} x {EMBED_DIM})")
    print(f"  DuckDB: {DUCKDB_PATH}")
    print()

    stats = {"embedded": 0, "skipped": 0, "errors": 0,
             "unwrappable": 0, "blacklisted": 0, "timeout": 0}

    print("[4/5] Embedding functions...")
    print(f"  Embed dimension: {EMBED_DIM}")
    print()

    t_start = time.time()
    batch_rows = []

    for idx in range(n_total):
        entry = work_items[idx]
        name = entry["name"]
        qualified_name = entry["qualified_name"]
        module = entry["module"]
        package = entry.get("package", module)
        category = entry.get("category", "unknown")
        tags = ",".join(entry.get("tags", []))

        # Progress report
        if idx > 0 and idx % REPORT_INTERVAL == 0:
            elapsed = time.time() - t_start
            rate = idx / max(elapsed, 0.01)
            remaining = (n_total - idx) / max(rate, 0.01)
            print(f"  [{idx:4d}/{n_total}] ok={stats['embedded']} "
                  f"err={stats['errors']} unwrap={stats['unwrappable']} "
                  f"tmo={stats['timeout']} skip={stats['blacklisted']} "
                  f"({rate:.1f}/s, ~{remaining:.0f}s left)")
            sys.stdout.flush()

        # Flush periodically
        if idx > 0 and idx % FLUSH_INTERVAL == 0:
            _flush_db(db, batch_rows)
            batch_rows = []
            if idx % CHECKPOINT_INTERVAL == 0:
                save_checkpoint(idx, stats)

        # Blacklist check
        if is_blacklisted(qualified_name, name):
            stats["blacklisted"] += 1
            batch_rows.append(make_row(idx, name, qualified_name, module, package,
                                       category, tags, "blacklisted",
                                       0, 0, 0, 0, 0, "skipped", "blacklisted"))
            continue

        # Import
        try:
            fn = import_function(entry)
        except Exception:
            fn = None
        if fn is None:
            stats["errors"] += 1
            batch_rows.append(make_row(idx, name, qualified_name, module, package,
                                       category, tags, "import_failed",
                                       0, 0, 0, 0, 0, "error", "import failed"))
            continue

        # Build wrapper using signature metadata
        try:
            wrapper, wrap_type = build_wrapper(fn, entry)
        except Exception as e:
            wrapper, wrap_type = None, f"wrap_error:{type(e).__name__}"

        if wrapper is None:
            stats["unwrappable"] += 1
            batch_rows.append(make_row(idx, name, qualified_name, module, package,
                                       category, tags, wrap_type,
                                       0, 0, 0, 0, 0, "unwrappable"))
            continue

        # Embed with timeout
        t0 = time.perf_counter()
        result = safe_embed(wrapper, timeout=15.0)
        embed_time = (time.perf_counter() - t0) * 1000

        if result is None:
            if embed_time > 14000:  # hit the timeout
                stats["timeout"] += 1
                batch_rows.append(make_row(idx, name, qualified_name, module, package,
                                           category, tags, wrap_type,
                                           0, 0, embed_time, 0, 0, "timeout", "embed timed out"))
            else:
                stats["errors"] += 1
                batch_rows.append(make_row(idx, name, qualified_name, module, package,
                                           category, tags, wrap_type,
                                           0, 0, embed_time, 0, 0, "embed_error", "safe_embed None"))
            continue

        address = result["address"]
        meta = result["meta"]

        # Store in Zarr
        try:
            zarr_group["addresses"][idx] = address
            zarr_group["success_rates"][idx] = meta["success_rate"]
            zarr_group["norms"][idx] = meta["address_norm"]
        except Exception as e:
            stats["errors"] += 1
            batch_rows.append(make_row(idx, name, qualified_name, module, package,
                                       category, tags, wrap_type,
                                       meta["success_rate"], meta["address_norm"],
                                       embed_time, meta["n_success"], meta["n_error"],
                                       "zarr_error", str(e)[:150]))
            continue

        batch_rows.append(make_row(idx, name, qualified_name, module, package,
                                   category, tags, wrap_type,
                                   meta["success_rate"], meta["address_norm"],
                                   embed_time, meta["n_success"], meta["n_error"],
                                   "ok"))
        stats["embedded"] += 1

    # Final flush
    _flush_db(db, batch_rows)
    save_checkpoint(n_total - 1, stats)

    elapsed_total = time.time() - t_start

    # Summary
    print()
    print("=" * 70)
    print("[5/5] EMBEDDING COMPLETE")
    print("=" * 70)
    print(f"  Total items:     {n_total}")
    print(f"  Embedded:        {stats['embedded']}")
    print(f"  Unwrappable:     {stats['unwrappable']}")
    print(f"  Errors:          {stats['errors']}")
    print(f"  Timeouts:        {stats['timeout']}")
    print(f"  Blacklisted:     {stats['blacklisted']}")
    print(f"  Time:            {elapsed_total:.1f}s ({elapsed_total/60:.1f}m)")
    if elapsed_total > 0:
        print(f"  Rate:            {stats['embedded'] / elapsed_total:.1f} embeddings/s")
    print()

    # Breakdowns
    print("  BY CATEGORY:")
    try:
        for row in db.execute("""
            SELECT category, COUNT(*) t,
                   SUM(CASE WHEN status='ok' THEN 1 ELSE 0 END) ok,
                   ROUND(AVG(CASE WHEN status='ok' THEN success_rate END), 3) sr
            FROM embeddings GROUP BY category ORDER BY ok DESC
        """).fetchall():
            sr = f"{row[3]:.1%}" if row[3] is not None else "n/a"
            print(f"    {row[0]:30s}: {row[1]:4d} total, {row[2]:4d} ok, sr={sr}")
    except Exception as e:
        print(f"    (error: {e})")

    print()
    print("  BY WRAP TYPE (embedded):")
    try:
        for row in db.execute("""
            SELECT wrap_type, COUNT(*) n FROM embeddings
            WHERE status='ok' GROUP BY wrap_type ORDER BY n DESC
        """).fetchall():
            print(f"    {row[0]:25s}: {row[1]:4d}")
    except Exception as e:
        print(f"    (error: {e})")

    print()
    print("  BY STATUS:")
    try:
        for row in db.execute("""
            SELECT status, COUNT(*) n FROM embeddings GROUP BY status ORDER BY n DESC
        """).fetchall():
            print(f"    {row[0]:20s}: {row[1]:4d}")
    except Exception as e:
        print(f"    (error: {e})")

    print()
    print(f"  Zarr: {ZARR_PATH}")
    print(f"  DuckDB: {DUCKDB_PATH}")
    print()

    db.close()
    return stats


if __name__ == "__main__":
    main()
