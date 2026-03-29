"""
p-adic Physics — p-adic string theory and adelic amplitudes

Connects to: [tropical_qft, feynman_diagram_algebra, tqft]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import gamma as gamma_fn

FIELD_NAME = "p_adic_physics"
OPERATIONS = {}


def freund_witten_amplitude(s, p=2):
    """Freund-Witten p-adic string amplitude (4-tachyon).
    A_p(s,t) propto integral |x|_p^{s-1} |1-x|_p^{t-1} dx
    For the p-adic Gel'fand-Graev beta function:
    B_p(a,b) = (1 - p^{a-1})*(1 - p^{b-1}) / (1 - p^{a+b-1}) when Re(a),Re(b) > 0.
    Here we compute B_p(s, 1-s) as function of s (Mandelstam variable).
    Input: s array (Mandelstam s values). Output: amplitude array."""
    s = np.asarray(s, dtype=float)
    # B_p(a, b) = (1 - p^{a-1})*(1 - p^{b-1}) / (1 - p^{a+b-2})
    # With a = -s (tachyon kinematics shifted), b = -t = s-1 (for 4pt at fixed sum)
    a = s
    b = 1.0 - s  # simple parametrization
    num = (1.0 - p**(a - 1.0)) * (1.0 - p**(b - 1.0))
    den = 1.0 - p**(a + b - 2.0)
    # Avoid division by zero
    den = np.where(np.abs(den) < 1e-15, 1e-15, den)
    return num / den

OPERATIONS["freund_witten_amplitude"] = {
    "fn": freund_witten_amplitude,
    "input_type": "array",
    "output_type": "array",
    "description": "Freund-Witten p-adic string amplitude"
}


def p_adic_string_amplitude(k_sq, p=2):
    """p-adic open string tachyon amplitude: A = p^{-k^2/2} (tree-level propagator).
    The p-adic string action gives amplitudes as powers of p.
    Input: k_sq array (momentum squared). Output: amplitude array."""
    k_sq = np.asarray(k_sq, dtype=float)
    return p ** (-k_sq / 2.0)

OPERATIONS["p_adic_string_amplitude"] = {
    "fn": p_adic_string_amplitude,
    "input_type": "array",
    "output_type": "array",
    "description": "p-adic string tachyon amplitude"
}


def adelic_product_formula(s, primes=None):
    """Adelic product formula: product over all places (real + p-adic) gives 1.
    Gamma_R(s) * prod_p Gamma_p(s) = 1 for the adelic Tate gamma.
    Gamma_p(s) = 1/(1 - p^{-s}).
    Compute the partial product: prod_{p in primes} 1/(1-p^{-s}).
    This equals the partial Euler product of the Riemann zeta function.
    Input: s array. Output: partial product array."""
    s = np.asarray(s, dtype=float)
    if primes is None:
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    result = np.ones_like(s)
    for p in primes:
        result *= 1.0 / (1.0 - p ** (-s))
    return result

OPERATIONS["adelic_product_formula"] = {
    "fn": adelic_product_formula,
    "input_type": "array",
    "output_type": "array",
    "description": "Adelic product (partial Euler product of zeta)"
}


def bruhat_tits_tree_distance(a, b, p=2):
    """Distance on the Bruhat-Tits tree of Q_p.
    For integers a, b: d(a,b) = v_p(a-b) where v_p is the p-adic valuation.
    v_p(n) = max power of p dividing n; distance = 2*v_p(a-b) + |log_p|a-b||.
    Simplified: d = -log_p(|a-b|_p) = v_p(a-b).
    Input: a array, b (use a, b=0 for simplicity). Output: distance array."""
    a = np.asarray(a, dtype=float)
    b = 0.0
    diff = np.abs(a - b)
    # p-adic valuation: highest power of p dividing diff
    val = np.zeros_like(diff)
    for i, d in enumerate(diff.flat):
        d_int = int(round(d))
        if d_int == 0:
            val.flat[i] = np.inf
            continue
        v = 0
        while d_int % p == 0 and d_int > 0:
            d_int //= p
            v += 1
        val.flat[i] = float(v)
    return val

OPERATIONS["bruhat_tits_tree_distance"] = {
    "fn": lambda x: bruhat_tits_tree_distance(x, 0.0),
    "input_type": "array",
    "output_type": "array",
    "description": "Bruhat-Tits tree distance (p-adic valuation)"
}


def p_adic_path_integral_tree(phi_boundary, p=2):
    """p-adic path integral on the Bruhat-Tits tree.
    The free field on the tree has action S = sum_{edges} (phi_i - phi_j)^2.
    On-shell: phi at each vertex is the average of its p+1 neighbors (harmonic).
    For boundary values: the bulk solution minimizes action.
    The action on-shell = sum of (boundary differences)^2 * weight.
    Input: phi_boundary array (boundary field values). Output: action scalar."""
    phi = np.asarray(phi_boundary, dtype=float)
    n = len(phi)
    # Action for free field on tree: sum over edges of (phi_i - phi_j)^2
    # For boundary-to-boundary propagator on the tree:
    # S ~ sum_{i<j} |phi_i - phi_j|^2 * p^{-d(i,j)} where d = tree distance
    S = 0.0
    for i in range(n):
        for j in range(i+1, n):
            # Tree distance: use p-adic-like weighting
            d_ij = abs(i - j)
            weight = p ** (-d_ij)
            S += (phi[i] - phi[j])**2 * weight
    return np.float64(S)

OPERATIONS["p_adic_path_integral_tree"] = {
    "fn": p_adic_path_integral_tree,
    "input_type": "array",
    "output_type": "scalar",
    "description": "p-adic path integral action on Bruhat-Tits tree"
}


def veneziano_amplitude(s, t=None):
    """Veneziano amplitude: A(s,t) = Gamma(-s)*Gamma(-t)/Gamma(-s-t)
    = B(-s, -t) (Euler beta function).
    For real s with t = -(s+1) (simple parametrization):
    Input: s array. Output: amplitude array."""
    s = np.asarray(s, dtype=float)
    if t is None:
        t = -(s + 1.0)
    # B(-s, -t) = Gamma(-s)*Gamma(-t)/Gamma(-s-t)
    # Use log-gamma for numerical stability
    from math import lgamma
    result = np.zeros_like(s)
    for i, (si, ti) in enumerate(zip(s.flat, t.flat)):
        try:
            log_A = lgamma(-si) + lgamma(-ti) - lgamma(-si - ti)
            result.flat[i] = np.exp(log_A)
        except (ValueError, OverflowError):
            result.flat[i] = np.nan
    return result

OPERATIONS["veneziano_amplitude"] = {
    "fn": lambda x: veneziano_amplitude(-x - 0.1, -0.5 * np.ones_like(x)),
    "input_type": "array",
    "output_type": "array",
    "description": "Veneziano amplitude B(-s,-t)"
}


def p_adic_propagator(x, m_sq=1.0, p=2):
    """p-adic propagator: G_p(x) = |x|_p^{s-1} / (|x|_p^s + m^2) in momentum space.
    Simplified: in position space on Z_p, G(n) ~ p^{-v_p(n)} / m^2 for massive field.
    Input: x array (positions as integers). Output: propagator array."""
    x = np.asarray(x, dtype=float)
    # Compute p-adic norm |x|_p = p^{-v_p(x)}
    norm_p = np.zeros_like(x)
    for i, xi in enumerate(x.flat):
        xi_int = int(round(xi))
        if xi_int == 0:
            norm_p.flat[i] = 0.0
            continue
        v = 0
        temp = abs(xi_int)
        while temp % p == 0 and temp > 0:
            temp //= p
            v += 1
        norm_p.flat[i] = p ** (-v)
    # Propagator ~ |x|_p / (1 + m^2 * |x|_p)
    G = norm_p / (1.0 + m_sq * norm_p + 1e-30)
    return G

OPERATIONS["p_adic_propagator"] = {
    "fn": p_adic_propagator,
    "input_type": "array",
    "output_type": "array",
    "description": "p-adic field propagator"
}


def p_adic_partition_function(beta, p=2, n_terms=20):
    """p-adic partition function: Z_p(beta) = sum_{n=0}^{inf} p^{-beta*n}.
    This is a geometric series: Z = 1/(1 - p^{-beta}) for beta > 0.
    Input: beta array. Output: Z array."""
    beta = np.asarray(beta, dtype=float)
    Z = 1.0 / (1.0 - p ** (-beta))
    return Z

OPERATIONS["p_adic_partition_function"] = {
    "fn": p_adic_partition_function,
    "input_type": "array",
    "output_type": "array",
    "description": "p-adic partition function (geometric series)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
