"""
Library Wrapper — Auto-wrap discovered library functions as MathematicalOrganism operations.

Reads the Eos library manifest (2,970 functions from numpy, scipy, networkx, etc.),
introspects signatures, maps to semantic types, tests each on standard probes,
and generates organism files for all viable functions.

This bridges the circularity gap: the tensor needs density (more organisms) to
beat random search, and this script turns 2,970 cataloged functions into
hundreds of new operations without manual encoding.

Usage:
    python library_wrapper.py --source numpy --test --save
    python library_wrapper.py --source scipy.linalg --test --save
    python library_wrapper.py --source all --test --save --report
"""

import argparse
import importlib
import json
import os
import sys
import time
import traceback
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

warnings.filterwarnings("ignore")
np.seterr(all="ignore")

ROOT = Path(__file__).resolve().parent.parent
ORGANISMS_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "agents" / "eos" / "data" / "library_manifest.json"
GENERATED_DIR = ORGANISMS_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT))

# ============================================================
# Blacklist — functions known to hang, crash, or be useless
# ============================================================

BLACKLIST_NAMES = {
    # numpy: non-mathematical, utility, or dangerous
    "numpy.array", "numpy.asarray", "numpy.asanyarray", "numpy.ascontiguousarray",
    "numpy.asfortranarray", "numpy.asmatrix", "numpy.array2string",
    "numpy.array_repr", "numpy.array_str", "numpy.base_repr", "numpy.binary_repr",
    "numpy.bmat", "numpy.block", "numpy.copy", "numpy.empty_like",
    "numpy.frombuffer", "numpy.fromfile", "numpy.fromfunction", "numpy.fromiter",
    "numpy.fromstring", "numpy.full_like", "numpy.identity", "numpy.load",
    "numpy.loadtxt", "numpy.ones_like", "numpy.save", "numpy.savetxt",
    "numpy.savez", "numpy.savez_compressed", "numpy.zeros_like",
    "numpy.set_printoptions", "numpy.get_printoptions",
    "numpy.show_config", "numpy.info", "numpy.test", "numpy.lookfor",
    "numpy.who", "numpy.source", "numpy.deprecate", "numpy.deprecate_with_doc",
    "numpy.show_runtime",
    "numpy.random.seed", "numpy.random.get_state", "numpy.random.set_state",
    "numpy.linalg.tensorinv", "numpy.linalg.tensorsolve",
    # scipy dangerous
    "scipy.linalg.lapack", "scipy.linalg.blas",
    # math: non-wrappable
    "math.factorial",  # huge outputs on large integers
}

BLACKLIST_SUBSTRINGS = [
    "show_config", "__test", "print_function", "setup_module", "teardown_module",
    "_internal", "_core", "arrayprint", "getlimits", "machar",
]

# ============================================================
# Semantic Type Inference
# ============================================================

# Map function name patterns to semantic output types
OUTPUT_TYPE_RULES = {
    # Scalar outputs
    "det": "scalar", "norm": "scalar", "trace": "scalar", "rank": "scalar",
    "cond": "scalar", "max": "scalar", "min": "scalar", "sum": "scalar",
    "mean": "scalar", "std": "scalar", "var": "scalar", "median": "scalar",
    "prod": "scalar", "ptp": "scalar", "count": "scalar",
    # Integer outputs
    "argmax": "integer", "argmin": "integer", "count_nonzero": "integer",
    "bincount": "array",
    # Array outputs
    "sort": "array", "argsort": "array", "cumsum": "array", "cumprod": "array",
    "diff": "array", "gradient": "array", "convolve": "array",
    "correlate": "array", "histogram": "array",
    "fft": "array", "ifft": "array", "rfft": "array", "irfft": "array",
    "fftfreq": "array", "rfftfreq": "array",
    "eigenvalue": "array", "eigvals": "array",
    "singular": "array", "svdvals": "array",
    # Matrix outputs
    "inv": "matrix", "pinv": "matrix", "cholesky": "matrix",
    "qr": "matrix", "lu": "matrix", "schur": "matrix",
    "hessenberg": "matrix", "expm": "matrix", "logm": "matrix",
    "sqrtm": "matrix", "funm": "matrix",
}

# Map function name patterns to semantic input types
INPUT_TYPE_RULES = {
    "det": "matrix", "inv": "matrix", "pinv": "matrix", "norm": "array",
    "cholesky": "matrix", "eig": "matrix", "svd": "matrix",
    "qr": "matrix", "lu": "matrix", "schur": "matrix",
    "solve": "matrix", "lstsq": "matrix",
    "fft": "array", "ifft": "array", "rfft": "array", "irfft": "array",
    "convolve": "array", "correlate": "array",
    "sort": "array", "argsort": "array", "cumsum": "array",
    "diff": "array", "gradient": "array",
    "histogram": "array", "bincount": "array",
    "arange": "integer", "linspace": "scalar",
}


def infer_semantic_type(func_name: str, param_name: str, is_output: bool,
                        category: str, tags: List[str]) -> str:
    """Infer semantic type from function name, param name, and metadata."""
    name_lower = func_name.lower().split(".")[-1]
    param_lower = param_name.lower()

    rules = OUTPUT_TYPE_RULES if is_output else INPUT_TYPE_RULES
    for pattern, stype in rules.items():
        if pattern in name_lower:
            return stype

    # Infer from category
    if category == "linear_algebra":
        return "matrix" if "matrix" in param_lower or "a" == param_lower else "array"
    if category == "signal_processing":
        return "array"
    if category == "statistics":
        return "array"
    if category == "special_functions":
        return "scalar"
    if category == "number_theory":
        return "integer"

    # Infer from param name
    if param_lower in ("x", "a", "data", "arr", "values"):
        return "array"
    if param_lower in ("n", "k", "m", "order", "size"):
        return "integer"

    # Default based on whether the function is a ufunc
    return "array"


def infer_input_output_types(discovery: Dict) -> Tuple[str, str]:
    """Infer semantic input and output types for a function."""
    name = discovery["qualified_name"]
    category = discovery.get("category", "")
    tags = discovery.get("tags", [])
    params = discovery.get("signature", {}).get("params", [])

    required = [p for p in params
                if not p.get("has_default", True)
                and p.get("kind", "") in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")]

    if not required:
        return "scalar", "array"  # 0-param: probably a generator

    # Use first required param for input type
    input_type = infer_semantic_type(name, required[0]["name"], False, category, tags)

    # Output type from function name patterns
    output_type = infer_semantic_type(name, "output", True, category, tags)

    return input_type, output_type


# ============================================================
# Test Probes
# ============================================================

SCALAR_PROBES = [0.5, 1.0, 2.0, 3.14159, 7.0, 42.0]
INTEGER_PROBES = [2, 5, 7, 10, 20, 50]
ARRAY_PROBES = [
    np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
    np.linspace(0, 1, 20),
    np.random.RandomState(42).randn(10),
    np.arange(1, 11, dtype=float),
]
MATRIX_PROBES = [
    np.eye(5),
    np.random.RandomState(42).randn(5, 5),
    np.array([[1, 2], [3, 4]], dtype=float),
]

TYPE_TO_PROBES = {
    "scalar": SCALAR_PROBES,
    "integer": INTEGER_PROBES,
    "array": ARRAY_PROBES,
    "matrix": MATRIX_PROBES,
}


def test_function(func, input_type: str, timeout: float = 2.0) -> Dict:
    """
    Test a function with standard probes in a subprocess to isolate segfaults.
    Returns test results.
    """
    import subprocess, tempfile, textwrap

    probes_map = {
        "scalar": "[0.5, 1.0, 2.0, 3.14159, 7.0, 42.0]",
        "integer": "[2, 5, 7, 10, 20, 50]",
        "array": "[np.array([1.0,2.0,3.0,4.0,5.0]), np.linspace(0,1,20), np.arange(1,11,dtype=float)]",
        "matrix": "[np.eye(5), np.array([[1,2],[3,4]],dtype=float)]",
    }
    probes_str = probes_map.get(input_type, probes_map["scalar"])
    n_probes = {"scalar": 6, "integer": 6, "array": 3, "matrix": 2}.get(input_type, 6)

    # Get the qualified name from the function
    mod_name = func.__module__ if hasattr(func, "__module__") else ""
    func_name = func.__name__ if hasattr(func, "__name__") else ""
    qname = f"{mod_name}.{func_name}" if mod_name else func_name

    # Build a test script that runs in a subprocess
    script = textwrap.dedent(f'''
        import numpy as np, json, warnings, sys
        warnings.filterwarnings("ignore")
        np.seterr(all="ignore")
        try:
            parts = "{qname}".rsplit(".", 1)
            mod = __import__(parts[0], fromlist=[parts[1]])
            func = getattr(mod, parts[1])
        except Exception as e:
            print(json.dumps({{"successes":0,"failures":1,"total":1,"success_rate":0,"output_types":[],"errors":[str(e)[:100]]}}))
            sys.exit(0)
        probes = {probes_str}
        successes = 0
        failures = 0
        outputs = []
        errors = []
        for probe in probes:
            try:
                result = func(probe)
                if result is None:
                    failures += 1; continue
                if isinstance(result, (np.ndarray, np.generic)):
                    if np.any(np.isnan(result)) or np.any(np.isinf(result)):
                        failures += 1; continue
                    if isinstance(result, np.ndarray) and result.size > 100000:
                        failures += 1; continue
                if isinstance(result, (tuple, list)):
                    result = result[0] if result else None
                    if result is None:
                        failures += 1; continue
                successes += 1
                outputs.append(type(result).__name__)
            except Exception as e:
                failures += 1
                errors.append(str(e)[:100])
        print(json.dumps({{"successes":successes,"failures":failures,"total":len(probes),
            "success_rate":successes/len(probes) if probes else 0,
            "output_types":outputs,"errors":errors[:3]}}))
    ''').strip()

    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=timeout + 2,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.returncode != 0 or not result.stdout.strip():
            return {"successes": 0, "failures": n_probes, "total": n_probes,
                    "success_rate": 0, "output_types": [], "errors": ["subprocess crashed"]}
        return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return {"successes": 0, "failures": n_probes, "total": n_probes,
                "success_rate": 0, "output_types": [], "errors": ["timeout or parse error"]}


def infer_output_type_from_tests(test_results: Dict, default: str) -> str:
    """Refine output type based on actual test outputs."""
    output_types = test_results.get("output_types", [])
    if not output_types:
        return default

    from collections import Counter
    type_counts = Counter(output_types)
    most_common = type_counts.most_common(1)[0][0]

    type_map = {
        "float64": "scalar", "float32": "scalar", "float": "scalar",
        "int64": "integer", "int32": "integer", "int": "integer",
        "complex128": "scalar", "complex64": "scalar",
        "ndarray": "array",
        "bool_": "scalar", "bool": "scalar",
        "tuple": "array",  # Often (values, counts) etc.
    }
    return type_map.get(most_common, default)


# ============================================================
# Wrapping
# ============================================================

def wrap_function(discovery: Dict) -> Optional[Dict]:
    """
    Attempt to wrap a library function as an organism operation.
    Returns operation dict or None if wrapping fails.
    """
    qname = discovery["qualified_name"]

    # Blacklist check
    if qname in BLACKLIST_NAMES:
        return None
    for sub in BLACKLIST_SUBSTRINGS:
        if sub in qname:
            return None

    # Check it has exactly 1 required param
    params = discovery.get("signature", {}).get("params", [])
    required = [p for p in params
                if not p.get("has_default", True)
                and p.get("kind", "") in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")]
    if len(required) != 1:
        return None

    # Try to import
    try:
        parts = qname.rsplit(".", 1)
        if len(parts) != 2:
            return None
        mod_path, func_name = parts
        mod = importlib.import_module(mod_path)
        func = getattr(mod, func_name)
        if not callable(func):
            return None
    except Exception:
        return None

    # Infer types
    input_type, output_type = infer_input_output_types(discovery)

    # Test
    test_results = test_function(func, input_type)
    if test_results["success_rate"] < 0.5:
        # Try with scalar inputs as fallback
        test_results2 = test_function(func, "scalar")
        if test_results2["success_rate"] > test_results["success_rate"]:
            input_type = "scalar"
            test_results = test_results2

    if test_results["success_rate"] < 0.5:
        return None

    # Refine output type from actual test results
    output_type = infer_output_type_from_tests(test_results, output_type)

    # Build the operation code string
    code = f'def {func_name}(x):\n'
    code += f'    import {mod_path}\n'
    code += f'    result = {mod_path}.{func_name}(x)\n'
    code += f'    if isinstance(result, tuple):\n'
    code += f'        result = result[0]\n'
    code += f'    return result\n'

    return {
        "name": func_name,
        "qualified_name": qname,
        "code": code,
        "input_type": input_type,
        "output_type": output_type,
        "category": discovery.get("category", ""),
        "tags": discovery.get("tags", []),
        "test_success_rate": test_results["success_rate"],
        "is_ufunc": discovery.get("is_ufunc", False),
    }


def wrap_package(discoveries: List[Dict], package: str) -> List[Dict]:
    """Wrap all viable functions from a package."""
    pkg_funcs = [d for d in discoveries if d.get("package", "") == package]
    results = []
    for d in pkg_funcs:
        wrapped = wrap_function(d)
        if wrapped:
            results.append(wrapped)
    return results


# ============================================================
# Organism Generation
# ============================================================

def generate_organism_file(package: str, operations: List[Dict], output_dir: Path) -> str:
    """Generate a MathematicalOrganism Python file from wrapped operations."""
    # Clean package name for use as organism name
    org_name = package.replace(".", "_").replace("-", "_").lower()

    lines = [
        f'"""Auto-generated organism wrapping {len(operations)} functions from {package}."""',
        '',
        'import numpy as np',
        'from organisms.base import MathematicalOrganism',
        '',
        '',
        f'class {org_name.title().replace("_", "")}Organism(MathematicalOrganism):',
        f'    name = "{org_name}"',
        '    operations = {',
    ]

    for op in operations:
        code_escaped = op["code"].replace("\\", "\\\\").replace('"', '\\"')
        code_lines = op["code"].split("\n")
        code_str = "\\n".join(code_lines)

        lines.append(f'        "{op["name"]}": {{')
        lines.append(f'            "code": "{code_str}",')
        lines.append(f'            "input_type": "{op["input_type"]}",')
        lines.append(f'            "output_type": "{op["output_type"]}",')
        lines.append(f'        }},')

    lines.append('    }')
    lines.append('')

    file_path = output_dir / f"{org_name}.py"
    with open(file_path, "w") as f:
        f.write("\n".join(lines))

    return str(file_path)


def generate_init_file(organisms: Dict[str, List[Dict]], output_dir: Path) -> str:
    """Generate __init__.py that imports all generated organisms."""
    lines = ['"""Auto-generated organisms from library wrapping."""', '']

    all_classes = []
    for package, ops in organisms.items():
        org_name = package.replace(".", "_").replace("-", "_").lower()
        class_name = f'{org_name.title().replace("_", "")}Organism'
        lines.append(f'from .{org_name} import {class_name}')
        all_classes.append(class_name)

    lines.append('')
    lines.append(f'ALL_GENERATED = [{", ".join(all_classes)}]')
    lines.append('')

    file_path = output_dir / "__init__.py"
    with open(file_path, "w") as f:
        f.write("\n".join(lines))

    return str(file_path)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Library Wrapper — Auto-generate organisms")
    parser.add_argument("--source", type=str, default="numpy",
                        help="Package to wrap: numpy, scipy.linalg, scipy.signal, scipy.stats, "
                             "scipy.special, math, or 'all' for all packages")
    parser.add_argument("--test", action="store_true", help="Test each function before wrapping")
    parser.add_argument("--save", action="store_true", help="Save generated organism files")
    parser.add_argument("--report", action="store_true", help="Print detailed report")
    parser.add_argument("--min-success", type=float, default=0.5,
                        help="Minimum test success rate to include (default: 0.5)")
    args = parser.parse_args()

    print("=" * 70)
    print("  LIBRARY WRAPPER — Auto-wrapping functions as organisms")
    print("=" * 70)
    print()

    # Load manifest
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    discoveries = manifest["discoveries"]
    print(f"  Manifest: {len(discoveries)} functions discovered")

    # Select packages
    if args.source == "all":
        packages = ["numpy", "numpy.linalg", "numpy.fft", "numpy.random",
                     "scipy.linalg", "scipy.signal", "scipy.stats", "scipy.special",
                     "math", "cmath", "statistics"]
    else:
        packages = [args.source]

    # Wrap each package
    all_results: Dict[str, List[Dict]] = {}
    total_wrapped = 0
    total_tested = 0

    for package in packages:
        pkg_funcs = [d for d in discoveries if d.get("package", "") == package]
        print(f"\n  {package}: {len(pkg_funcs)} functions in manifest...")

        wrapped = wrap_package(discoveries, package)
        total_tested += len(pkg_funcs)
        total_wrapped += len(wrapped)

        if wrapped:
            all_results[package] = wrapped
            # Type distribution
            from collections import Counter
            in_types = Counter(op["input_type"] for op in wrapped)
            out_types = Counter(op["output_type"] for op in wrapped)
            print(f"    Wrapped: {len(wrapped)} operations")
            print(f"    Input types:  {dict(in_types)}")
            print(f"    Output types: {dict(out_types)}")
            if args.report:
                for op in wrapped[:5]:
                    print(f"      {op['qualified_name']:50s} {op['input_type']:10s} -> {op['output_type']:10s} "
                          f"(success: {op['test_success_rate']:.0%})")
                if len(wrapped) > 5:
                    print(f"      ... and {len(wrapped) - 5} more")
        else:
            print(f"    No viable functions")

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Packages processed: {len(packages)}")
    print(f"  Functions tested:   {total_tested}")
    print(f"  Operations wrapped: {total_wrapped}")
    print(f"  New organisms:      {len(all_results)}")

    if args.save and all_results:
        print(f"\n  Saving to {GENERATED_DIR}/...")
        for package, ops in all_results.items():
            path = generate_organism_file(package, ops, GENERATED_DIR)
            print(f"    {path} ({len(ops)} operations)")

        init_path = generate_init_file(all_results, GENERATED_DIR)
        print(f"    {init_path}")

        # Also save a manifest of what was wrapped
        wrap_manifest = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_operations": total_wrapped,
            "packages": {pkg: len(ops) for pkg, ops in all_results.items()},
            "operations": {
                pkg: [{"name": op["name"], "qualified_name": op["qualified_name"],
                       "input_type": op["input_type"], "output_type": op["output_type"],
                       "test_success_rate": op["test_success_rate"]}
                      for op in ops]
                for pkg, ops in all_results.items()
            },
        }
        manifest_path = GENERATED_DIR / "wrap_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(wrap_manifest, f, indent=2)
        print(f"    {manifest_path}")

    print()


if __name__ == "__main__":
    main()
