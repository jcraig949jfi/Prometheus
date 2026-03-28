"""
Library Scanner — Eos module for discovering embeddable mathematical assets.

Scans installed Python packages for callable functions that could be
embedded into the Poros tensor space. No API calls — pure introspection.

Discovers:
  - numpy/scipy/sympy mathematical functions
  - scipy.special (number theory, special functions)
  - scipy.stats distributions
  - scipy.signal processing functions
  - scipy.linalg linear algebra operations
  - Any pip-installed math library

For each discovered function, records:
  - Name and full qualified path
  - Module and package
  - Argument signature (if inspectable)
  - Category (math, linalg, signal, stats, special, number_theory, etc.)
  - Whether it's wrappable (takes numeric input, produces numeric output)

Output: JSON manifest of all discovered functions ready for embedding.
"""

import importlib
import inspect
import json
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

log = logging.getLogger("eos.library_scanner")

# Libraries to scan and their interesting submodules
SCAN_TARGETS = [
    # (package_name, submodules_to_scan, category)
    ("numpy", ["", "linalg", "fft", "polynomial", "random"], "numerical"),
    ("scipy.special", [""], "special_functions"),
    ("scipy.signal", [""], "signal_processing"),
    ("scipy.stats", [""], "statistics"),
    ("scipy.linalg", [""], "linear_algebra"),
    ("scipy.optimize", [""], "optimization"),
    ("scipy.integrate", [""], "integration"),
    ("scipy.interpolate", [""], "interpolation"),
    ("scipy.spatial", [""], "spatial"),
    ("sympy", [""], "symbolic_math"),
    ("sympy.ntheory", [""], "number_theory"),
    ("sympy.combinatorics", [""], "combinatorics"),
    ("math", [""], "stdlib_math"),
    ("cmath", [""], "complex_math"),
    ("statistics", [""], "stdlib_stats"),
    # Optional libraries (may not be installed)
    ("networkx", [""], "graph_theory"),
    ("filterpy.kalman", [""], "estimation"),
    ("galois", [""], "finite_fields"),
    ("tensorly", ["decomposition"], "tensor_methods"),
]


def _is_numeric_callable(obj: Any) -> bool:
    """Check if an object is a callable that likely takes/returns numbers."""
    if not callable(obj):
        return False
    if isinstance(obj, type):
        return False  # Skip classes (we want functions)
    name = getattr(obj, '__name__', '')
    if name.startswith('_'):
        return False
    # Skip known non-numeric
    skip_names = {'print', 'help', 'dir', 'type', 'isinstance', 'issubclass',
                  'getattr', 'setattr', 'hasattr', 'repr', 'str', 'format',
                  'test', 'setup', 'show', 'plot', 'display', 'register'}
    if name.lower() in skip_names:
        return False
    return True


def _get_signature_info(func: Any) -> Dict:
    """Extract parameter information from a function."""
    try:
        sig = inspect.signature(func)
        params = []
        for pname, param in sig.parameters.items():
            if pname in ('self', 'cls'):
                continue
            params.append({
                "name": pname,
                "has_default": param.default is not inspect.Parameter.empty,
                "kind": str(param.kind).split('.')[-1],
            })
        return {"params": params, "n_params": len(params), "inspectable": True}
    except (ValueError, TypeError):
        return {"params": [], "n_params": -1, "inspectable": False}


def _categorize_function(name: str, module: str, docstring: str) -> List[str]:
    """Assign categories based on name and docstring."""
    tags = []
    name_lower = name.lower()
    doc_lower = (docstring or "").lower()[:500]

    # Math categories
    if any(k in name_lower for k in ['prime', 'factor', 'divis', 'totient', 'mobius', 'gcd', 'lcm']):
        tags.append('number_theory')
    if any(k in name_lower for k in ['bessel', 'airy', 'gamma', 'zeta', 'beta', 'erf', 'legendre']):
        tags.append('special_function')
    if any(k in name_lower for k in ['bernoulli', 'euler', 'fibonacci', 'catalan', 'stirling']):
        tags.append('combinatorial')
    if any(k in name_lower for k in ['fft', 'ifft', 'rfft', 'spectrum', 'freq']):
        tags.append('fourier')
    if any(k in name_lower for k in ['filter', 'convolve', 'correlate', 'window', 'hilbert']):
        tags.append('signal')
    if any(k in name_lower for k in ['eig', 'svd', 'det', 'inv', 'norm', 'rank', 'trace', 'cholesky', 'qr', 'lu']):
        tags.append('linear_algebra')
    if any(k in name_lower for k in ['sort', 'search', 'argmin', 'argmax', 'partition', 'unique']):
        tags.append('algorithm')
    if any(k in name_lower for k in ['random', 'rand', 'uniform', 'normal', 'poisson', 'binomial']):
        tags.append('random')
    if any(k in name_lower for k in ['optim', 'minimize', 'root', 'solve', 'fit']):
        tags.append('optimization')
    if any(k in name_lower for k in ['integrate', 'quad', 'trapz', 'simpson']):
        tags.append('integration')
    if any(k in name_lower for k in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs', 'ceil', 'floor']):
        tags.append('elementary')
    if any(k in name_lower for k in ['matrix', 'array', 'tensor', 'sparse']):
        tags.append('data_structure')
    if any(k in name_lower for k in ['entropy', 'mutual', 'kl_div', 'cross_entropy']):
        tags.append('information_theory')

    # From docstring
    if 'probability' in doc_lower or 'distribution' in doc_lower:
        tags.append('probability')
    if 'topology' in doc_lower or 'homolog' in doc_lower:
        tags.append('topology')
    if 'chaos' in doc_lower or 'lyapunov' in doc_lower or 'bifurcation' in doc_lower:
        tags.append('chaos')

    if not tags:
        tags.append('uncategorized')
    return tags


def scan_module(package_name: str, submodule: str, category: str) -> List[Dict]:
    """Scan a module for embeddable functions."""
    full_name = f"{package_name}.{submodule}" if submodule else package_name
    discoveries = []

    try:
        mod = importlib.import_module(full_name)
    except ImportError:
        return []

    for attr_name in dir(mod):
        if attr_name.startswith('_'):
            continue

        try:
            obj = getattr(mod, attr_name)
        except Exception:
            continue

        if not _is_numeric_callable(obj):
            continue

        docstring = inspect.getdoc(obj) or ""
        sig_info = _get_signature_info(obj)
        tags = _categorize_function(attr_name, full_name, docstring)

        discovery = {
            "name": attr_name,
            "qualified_name": f"{full_name}.{attr_name}",
            "module": full_name,
            "package": package_name,
            "category": category,
            "tags": tags,
            "signature": sig_info,
            "docstring_preview": docstring[:200] if docstring else "",
            "is_ufunc": isinstance(obj, np.ufunc),
        }
        discoveries.append(discovery)

    return discoveries


def scan_scipy_distributions() -> List[Dict]:
    """Special handling for scipy.stats distributions — each is an object, not a function."""
    import scipy.stats as stats
    discoveries = []

    for name in dir(stats):
        obj = getattr(stats, name, None)
        if obj is None:
            continue
        # Check if it's a distribution (has pdf or pmf method)
        if hasattr(obj, 'pdf') or hasattr(obj, 'pmf'):
            kind = 'continuous' if hasattr(obj, 'pdf') else 'discrete'
            discoveries.append({
                "name": name,
                "qualified_name": f"scipy.stats.{name}",
                "module": "scipy.stats",
                "package": "scipy",
                "category": "probability_distribution",
                "tags": ["probability", "distribution", kind],
                "signature": {"params": [{"name": "x"}, {"name": "loc"}, {"name": "scale"}],
                              "n_params": 3, "inspectable": True},
                "docstring_preview": (inspect.getdoc(obj) or "")[:200],
                "is_ufunc": False,
                "distribution_type": kind,
                "embeddable_as": [
                    f"{name}.pdf" if kind == 'continuous' else f"{name}.pmf",
                    f"{name}.cdf",
                    f"{name}.entropy",
                    f"{name}.mean",
                    f"{name}.var",
                ],
            })

    return discoveries


def full_scan() -> Dict:
    """Scan all configured libraries and return a complete manifest."""
    all_discoveries = []
    scan_results = {}

    for package, submodules, category in SCAN_TARGETS:
        for sub in submodules:
            full = f"{package}.{sub}" if sub else package
            try:
                items = scan_module(package, sub, category)
                all_discoveries.extend(items)
                scan_results[full] = {"count": len(items), "status": "ok"}
            except Exception as e:
                scan_results[full] = {"count": 0, "status": f"error: {e}"}

    # Add scipy distributions specially
    try:
        dist_items = scan_scipy_distributions()
        all_discoveries.extend(dist_items)
        scan_results["scipy.stats.distributions"] = {"count": len(dist_items), "status": "ok"}
    except Exception as e:
        scan_results["scipy.stats.distributions"] = {"count": 0, "status": f"error: {e}"}

    # Deduplicate by qualified_name
    seen = set()
    unique = []
    for d in all_discoveries:
        qn = d["qualified_name"]
        if qn not in seen:
            seen.add(qn)
            unique.append(d)

    manifest = {
        "scan_timestamp": datetime.now().isoformat(),
        "total_discovered": len(unique),
        "by_category": {},
        "by_package": {},
        "scan_results": scan_results,
        "discoveries": unique,
    }

    # Summarize by category
    for d in unique:
        cat = d["category"]
        manifest["by_category"][cat] = manifest["by_category"].get(cat, 0) + 1
        pkg = d["package"]
        manifest["by_package"][pkg] = manifest["by_package"].get(pkg, 0) + 1

    return manifest


def save_manifest(manifest: Dict, output_path: str = None) -> str:
    """Save the discovery manifest to JSON."""
    if output_path is None:
        output_path = str(Path(__file__).resolve().parent.parent / "data" / "library_manifest.json")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("  EOS LIBRARY SCANNER")
    print("  Discovering embeddable mathematical assets")
    print("=" * 60)
    print()

    manifest = full_scan()

    print(f"Total discovered: {manifest['total_discovered']} functions")
    print()
    print("By category:")
    for cat, count in sorted(manifest["by_category"].items(), key=lambda x: -x[1]):
        print(f"  {cat:30s}: {count:4d}")
    print()
    print("By package:")
    for pkg, count in sorted(manifest["by_package"].items(), key=lambda x: -x[1]):
        print(f"  {pkg:30s}: {count:4d}")
    print()

    path = save_manifest(manifest)
    print(f"Manifest saved: {path}")
    print()

    # Show some interesting finds
    print("Sample discoveries (number theory):")
    nt = [d for d in manifest["discoveries"] if "number_theory" in d["tags"]]
    for d in nt[:10]:
        print(f"  {d['qualified_name']:50s} tags={d['tags']}")

    print()
    print("Sample discoveries (special functions):")
    sf = [d for d in manifest["discoveries"] if "special_function" in d["tags"]]
    for d in sf[:10]:
        print(f"  {d['qualified_name']:50s} tags={d['tags']}")
