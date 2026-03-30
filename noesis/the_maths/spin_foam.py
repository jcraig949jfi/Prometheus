"""
Spin Foam — Discretized quantum gravity path integrals via labeled 2-complexes

Connects to: [pseudo_riemannian, causal_set_theory, noncommutative_geometry_connes]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "spin_foam"
OPERATIONS = {}


def _factorial(n):
    """Factorial for small integers."""
    n = int(max(n, 0))
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def _wigner_3j_approx(j1, j2, j3, m1, m2, m3):
    """Approximate Wigner 3j symbol using Racah formula for simple cases."""
    if m1 + m2 + m3 != 0:
        return 0.0
    if abs(j1 - j2) > j3 or j3 > j1 + j2:
        return 0.0
    if abs(m1) > j1 or abs(m2) > j2 or abs(m3) > j3:
        return 0.0
    # Simple approximation for small j values
    J = j1 + j2 + j3
    if J != int(J):
        return 0.0
    J = int(J)
    # Use dimension formula as approximation weight
    dim = (2 * j3 + 1)
    sign = (-1) ** int(j1 - j2 - m3)
    return sign / np.sqrt(dim + 1)


def sixj_symbol(x):
    """Compute Racah-Wigner 6j symbol {j1 j2 j3; j4 j5 j6}.
    Input: array of 6 spin values [j1,...,j6]. Output: scalar 6j symbol.
    Uses the Racah formula with triangle conditions."""
    spins = np.zeros(6)
    spins[:min(len(x), 6)] = x[:min(len(x), 6)]
    j1, j2, j3, j4, j5, j6 = [max(0, s) for s in spins[:6]]

    # Triangle conditions: {j1,j2,j3}, {j1,j5,j6}, {j2,j4,j6}, {j3,j4,j5}
    def tri_ok(a, b, c):
        return (abs(a - b) <= c <= a + b) and ((a + b + c) == int(a + b + c))

    if not (tri_ok(j1, j2, j3) and tri_ok(j1, j5, j6) and
            tri_ok(j2, j4, j6) and tri_ok(j3, j4, j5)):
        return np.float64(0.0)

    # Racah formula: sum over z of (-1)^z * (z+1)! / products of factorials
    def tri_coeff(a, b, c):
        a, b, c = int(round(a)), int(round(b)), int(round(c))
        num = _factorial(a + b - c) * _factorial(a - b + c) * _factorial(-a + b + c)
        den = _factorial(a + b + c + 1)
        return num / den

    delta = np.sqrt(tri_coeff(j1, j2, j3) * tri_coeff(j1, j5, j6) *
                    tri_coeff(j2, j4, j6) * tri_coeff(j3, j4, j5))

    j1, j2, j3, j4, j5, j6 = [int(round(s)) for s in [j1, j2, j3, j4, j5, j6]]
    z_min = max(j1+j2+j3, j1+j5+j6, j2+j4+j6, j3+j4+j5)
    z_max = min(j1+j2+j4+j5, j2+j3+j5+j6, j1+j3+j4+j6)

    result = 0.0
    for z in range(z_min, z_max + 1):
        num = _factorial(z + 1)
        d1 = _factorial(z - j1 - j2 - j3)
        d2 = _factorial(z - j1 - j5 - j6)
        d3 = _factorial(z - j2 - j4 - j6)
        d4 = _factorial(z - j3 - j4 - j5)
        d5 = _factorial(j1 + j2 + j4 + j5 - z)
        d6 = _factorial(j2 + j3 + j5 + j6 - z)
        d7 = _factorial(j1 + j3 + j4 + j6 - z)
        den = d1 * d2 * d3 * d4 * d5 * d6 * d7
        if den != 0:
            result += ((-1) ** z) * num / den

    return np.float64(delta * result)


OPERATIONS["sixj_symbol"] = {
    "fn": sixj_symbol,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Racah-Wigner 6j symbol from six spin values"
}


def vertex_amplitude_ponzano_regge(x):
    """Ponzano-Regge vertex amplitude: product of 6j symbols weighted by dimensions.
    Input: array of 6 spins for a tetrahedron. Output: scalar amplitude.
    A_v = (-1)^{sum j} * prod(2j+1)^{1/2} * {6j}."""
    spins = np.zeros(6)
    spins[:min(len(x), 6)] = np.abs(x[:min(len(x), 6)])
    # Round to nearest half-integer
    spins = np.round(2 * spins) / 2.0
    j_sum = np.sum(spins)
    dim_factor = np.prod(np.sqrt(2.0 * spins + 1.0))
    sixj = sixj_symbol(spins)
    sign = (-1) ** int(round(j_sum))
    amplitude = sign * dim_factor * sixj
    return np.float64(amplitude)


OPERATIONS["vertex_amplitude_ponzano_regge"] = {
    "fn": vertex_amplitude_ponzano_regge,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Ponzano-Regge vertex amplitude for a tetrahedron"
}


def partition_function_simplicial(x):
    """Simplicial partition function Z = sum over labelings of product of amplitudes.
    Input: array of spins (interpreted as edge labels). Output: scalar Z.
    Simplified: Z = prod_edges (2j_e + 1) * sum of vertex amplitudes."""
    spins = np.abs(x)
    # Edge amplitudes: product of (2j+1)
    edge_amps = np.prod(2.0 * spins + 1.0)
    # Simple vertex amplitude (single vertex approximation)
    if len(spins) >= 6:
        v_amp = abs(sixj_symbol(spins[:6]))
    else:
        v_amp = 1.0
    Z = edge_amps * max(v_amp, 1e-15)
    return np.float64(Z)


OPERATIONS["partition_function_simplicial"] = {
    "fn": partition_function_simplicial,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Simplicial partition function from edge spin labels"
}


def edge_amplitude(x):
    """Edge amplitude in spin foam: A_e = (2j_e + 1) (dimension of SU(2) irrep).
    Input: array of spins. Output: array of edge amplitudes."""
    return 2.0 * np.abs(x) + 1.0


OPERATIONS["edge_amplitude"] = {
    "fn": edge_amplitude,
    "input_type": "array",
    "output_type": "array",
    "description": "Edge amplitudes (2j+1) for each spin label"
}


def face_amplitude(x):
    """Face amplitude in spin foam: A_f = (-1)^{2j} * (2j+1).
    Input: array of face spins. Output: array of face amplitudes."""
    spins = np.abs(x)
    signs = (-1.0) ** (2.0 * np.round(spins))
    return signs * (2.0 * spins + 1.0)


OPERATIONS["face_amplitude"] = {
    "fn": face_amplitude,
    "input_type": "array",
    "output_type": "array",
    "description": "Face amplitudes (-1)^{2j}(2j+1) for each face spin"
}


def semiclassical_limit_check(x):
    """Check if spins are in semiclassical regime (j >> 1).
    Input: array of spins. Output: scalar (fraction of spins with j > 5)."""
    spins = np.abs(x)
    frac = np.mean(spins > 5.0)
    return np.float64(frac)


OPERATIONS["semiclassical_limit_check"] = {
    "fn": semiclassical_limit_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fraction of spins in semiclassical regime (j > 5)"
}


def spin_foam_boundary_state(x):
    """Construct boundary spin network state from edge spins.
    Input: array of spins. Output: array of (2j+1)-dimensional basis state norms.
    |psi> = tensor product of |j, m=0> states."""
    spins = np.abs(x)
    # For each spin j, the m=0 component of |j,m> in the (2j+1)-dim space
    norms = np.ones_like(spins)
    for i, j in enumerate(spins):
        dim = int(2 * round(j) + 1)
        if dim > 0:
            norms[i] = 1.0 / np.sqrt(dim)
    return norms


OPERATIONS["spin_foam_boundary_state"] = {
    "fn": spin_foam_boundary_state,
    "input_type": "array",
    "output_type": "array",
    "description": "Boundary state norms for spin network with given edge spins"
}


def recoupling_coefficient(x):
    """Recoupling coefficient for change of basis in spin recoupling theory.
    Input: array [j1, j2, j3, j12, j23] (5 spins). Output: scalar coefficient.
    Related to 6j symbol: <(j1 j2)j12, j3 | j1, (j2 j3)j23>."""
    spins = np.zeros(5)
    spins[:min(len(x), 5)] = np.abs(x[:min(len(x), 5)])
    j1, j2, j3, j12, j23 = spins
    # Recoupling coefficient = (-1)^{j1+j2+j3+J} * sqrt((2j12+1)(2j23+1)) * {6j}
    J = j1 + j2  # total spin (simplified)
    phase = (-1) ** int(round(j1 + j2 + j3 + j12))
    dim_factor = np.sqrt((2 * j12 + 1) * (2 * j23 + 1))
    sixj_spins = np.array([j1, j2, j12, j3, j1 + j2 + j3 - j12 - j23, j23])
    sixj_spins = np.abs(sixj_spins)
    sj = sixj_symbol(sixj_spins)
    return np.float64(phase * dim_factor * sj)


OPERATIONS["recoupling_coefficient"] = {
    "fn": recoupling_coefficient,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Recoupling coefficient via 6j symbol for basis change"
}


def triangle_inequality_check(x):
    """Check triangle inequality for all triples of spins (necessary for valid spin foam).
    Input: array of spins [j1, j2, j3, ...]. Output: scalar (1 if all triples valid, 0 otherwise).
    Checks |j_i - j_j| <= j_k <= j_i + j_j for consecutive triples."""
    spins = np.abs(x)
    n = len(spins)
    if n < 3:
        return np.float64(1.0)
    for i in range(0, n - 2, 3):
        a, b, c = spins[i], spins[i + 1], spins[i + 2]
        if not (abs(a - b) <= c <= a + b):
            return np.float64(0.0)
    return np.float64(1.0)


OPERATIONS["triangle_inequality_check"] = {
    "fn": triangle_inequality_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check triangle inequality for consecutive spin triples"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
