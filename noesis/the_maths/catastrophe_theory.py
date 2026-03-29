"""
Catastrophe Theory — Thom's classification of elementary catastrophes

Connects to: [singularity theory, bifurcation theory, topology, dynamical systems, morphogenesis]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "catastrophe_theory"
OPERATIONS = {}


def fold_catastrophe(x):
    """Evaluate the fold catastrophe normal form V(x) = x^3 + ax.
    The fold is the simplest catastrophe (A_2, codimension 1).
    Input: array (first element = control param a, rest = state values).
    Output: array (potential values)."""
    a = x[0]
    states = x[1:] if len(x) > 1 else x
    # V(s) = s^3 + a*s
    potential = states ** 3 + a * states
    return potential


OPERATIONS["fold_catastrophe"] = {
    "fn": fold_catastrophe,
    "input_type": "array",
    "output_type": "array",
    "description": "Evaluates fold catastrophe potential V(x) = x^3 + ax"
}


def cusp_catastrophe(x):
    """Evaluate the cusp catastrophe normal form V(x) = x^4 + ax^2 + bx.
    The cusp (A_3) has codimension 2 and exhibits hysteresis.
    Input: array (first two = control params a,b; rest = state values).
    Output: array (potential values)."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 0.0
    states = x[2:] if len(x) > 2 else x
    potential = states ** 4 + a * states ** 2 + b * states
    return potential


OPERATIONS["cusp_catastrophe"] = {
    "fn": cusp_catastrophe,
    "input_type": "array",
    "output_type": "array",
    "description": "Evaluates cusp catastrophe potential V(x) = x^4 + ax^2 + bx"
}


def swallowtail_catastrophe(x):
    """Evaluate the swallowtail catastrophe V(x) = x^5 + ax^3 + bx^2 + cx.
    A_4, codimension 3. Input: array (first 3 = controls; rest = states).
    Output: array."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 0.0
    c = x[2] if len(x) > 2 else 0.0
    states = x[3:] if len(x) > 3 else x
    potential = states ** 5 + a * states ** 3 + b * states ** 2 + c * states
    return potential


OPERATIONS["swallowtail_catastrophe"] = {
    "fn": swallowtail_catastrophe,
    "input_type": "array",
    "output_type": "array",
    "description": "Evaluates swallowtail catastrophe V(x) = x^5 + ax^3 + bx^2 + cx"
}


def butterfly_catastrophe(x):
    """Evaluate the butterfly catastrophe V(x) = x^6 + ax^4 + bx^3 + cx^2 + dx.
    A_5, codimension 4. Input: array (first 4 = controls; rest = states).
    Output: array."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 0.0
    c = x[2] if len(x) > 2 else 0.0
    d = x[3] if len(x) > 3 else 0.0
    states = x[4:] if len(x) > 4 else x
    potential = states ** 6 + a * states ** 4 + b * states ** 3 + c * states ** 2 + d * states
    return potential


OPERATIONS["butterfly_catastrophe"] = {
    "fn": butterfly_catastrophe,
    "input_type": "array",
    "output_type": "array",
    "description": "Evaluates butterfly catastrophe V(x) = x^6 + ax^4 + bx^3 + cx^2 + dx"
}


def catastrophe_bifurcation_set(x):
    """Compute the bifurcation set for the cusp catastrophe.
    The bifurcation set is where V'(x)=0 and V''(x)=0 simultaneously.
    For V = x^4 + ax^2 + bx: 8a^3 + 27b^2 = 0.
    Input: array (treated as 'a' values). Output: array (corresponding 'b' values on bifurcation set)."""
    a_vals = x
    # From discriminant: 8a^3 + 27b^2 = 0 => b = +/- sqrt(-8a^3/27)
    # Only real when a <= 0
    b_vals = np.zeros_like(a_vals)
    mask = a_vals <= 0
    b_vals[mask] = np.sqrt(-8.0 * a_vals[mask] ** 3 / 27.0)
    # For a > 0, no real bifurcation: set to 0
    return b_vals


OPERATIONS["catastrophe_bifurcation_set"] = {
    "fn": catastrophe_bifurcation_set,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes cusp catastrophe bifurcation set from discriminant 8a^3+27b^2=0"
}


def catastrophe_stability_boundary(x):
    """Find stability boundary: where the second derivative of the potential changes sign.
    For fold: V''(s) = 6s + 2a... but simplify to cusp: V''=12x^2+2a.
    Stability lost when V'' = 0. Input: array (a values). Output: array (critical x values)."""
    a_vals = x
    # For cusp V = x^4 + ax^2 + bx, V''(x) = 12x^2 + 2a = 0
    # x = +/- sqrt(-a/6), only real for a < 0
    results = np.zeros_like(a_vals)
    mask = a_vals < 0
    results[mask] = np.sqrt(-a_vals[mask] / 6.0)
    return results


OPERATIONS["catastrophe_stability_boundary"] = {
    "fn": catastrophe_stability_boundary,
    "input_type": "array",
    "output_type": "array",
    "description": "Finds where second derivative vanishes (stability boundary for cusp)"
}


def potential_critical_points(x):
    """Find critical points of the cusp potential V(x) = x^4 + ax^2 + bx.
    V'(x) = 4x^3 + 2ax + b = 0. Solved numerically.
    Input: array [a, b]. Output: array (real roots)."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 0.0
    # Solve 4x^3 + 2ax + b = 0
    coeffs = [4.0, 0.0, 2.0 * a, b]
    roots = np.roots(coeffs)
    # Return only real roots
    real_roots = roots[np.abs(roots.imag) < 1e-10].real
    if len(real_roots) == 0:
        return np.array([0.0])
    return np.sort(real_roots)


OPERATIONS["potential_critical_points"] = {
    "fn": potential_critical_points,
    "input_type": "array",
    "output_type": "array",
    "description": "Finds critical points of cusp potential by solving V'(x)=0"
}


def maxwell_set_cusp(x):
    """Compute Maxwell set for cusp catastrophe: where two minima have equal potential.
    For V = x^4 + ax^2 + bx, the Maxwell set is b=0 for a<0.
    Input: array (a values). Output: array (b values on Maxwell set)."""
    # The Maxwell set of the cusp is the curve where two distinct minima have
    # the same potential value. By symmetry of V = x^4 + ax^2, this is b = 0.
    # For a < 0 there are two minima; for a >= 0 only one minimum.
    b_maxwell = np.zeros_like(x)
    # Maxwell set is b = 0 for a < 0; undefined otherwise
    # Return 0 for a < 0 (on set), NaN for a >= 0 (not applicable)
    b_maxwell[x >= 0] = np.nan
    return b_maxwell


OPERATIONS["maxwell_set_cusp"] = {
    "fn": maxwell_set_cusp,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Maxwell set for cusp catastrophe (equal-potential minima locus)"
}


def catastrophe_germ_codimension(x):
    """Compute the codimension (number of control parameters) for A_k singularities.
    For A_k: V = x^{k+1}, codimension = k-1.
    Input: array (k values). Output: array (codimensions)."""
    k_vals = np.maximum(np.round(np.abs(x)), 2).astype(int)
    codimensions = (k_vals - 1).astype(float)
    return codimensions


OPERATIONS["catastrophe_germ_codimension"] = {
    "fn": catastrophe_germ_codimension,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes codimension of A_k singularity germs (codim = k-1)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
