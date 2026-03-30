"""
Idempotent Analysis — max-plus and idempotent mathematics beyond tropical

Connects to: [tropical_geometry, optimization, mathematical_morphology, dynamic_programming]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "idempotent_analysis"
OPERATIONS = {}

# Max-plus algebra: a ⊕ b = max(a, b), a ⊗ b = a + b
# Min-plus algebra: a ⊕ b = min(a, b), a ⊗ b = a + b
# Identity for ⊕ is -inf (max-plus) or +inf (min-plus)
# Identity for ⊗ is 0


def idempotent_semiring_add(x):
    """Max-plus addition (idempotent): a ⊕ b = max(a, b).
    For arrays, computes pairwise ⊕ between first and second halves.
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = len(x) // 2
    if n == 0:
        return x.copy()
    a = x[:n]
    b = x[n:2*n]
    return np.maximum(a, b)

OPERATIONS["idempotent_semiring_add"] = {
    "fn": idempotent_semiring_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Max-plus addition: a ⊕ b = max(a, b) elementwise"
}


def idempotent_semiring_multiply(x):
    """Max-plus multiplication: a ⊗ b = a + b.
    For arrays, computes pairwise ⊗ between first and second halves.
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = len(x) // 2
    if n == 0:
        return x.copy()
    a = x[:n]
    b = x[n:2*n]
    return a + b

OPERATIONS["idempotent_semiring_multiply"] = {
    "fn": idempotent_semiring_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Max-plus multiplication: a ⊗ b = a + b elementwise"
}


def bellman_equation_iterate(x):
    """One iteration of Bellman's equation in max-plus algebra:
    V_new[i] = max_j(R[i,j] + gamma * V[j]).
    Input: array treated as flattened [reward_matrix | value_vector].
    Output: array (updated value vector)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    # Try to split into square matrix + vector
    # n = k^2 + k => k = (-1 + sqrt(1 + 4n)) / 2
    k = int((-1 + np.sqrt(1 + 4 * n)) / 2)
    if k < 1:
        return x.copy()
    k = min(k, int(np.sqrt(n)))
    if k * k + k > n:
        k = max(1, k - 1)

    R = x[:k*k].reshape(k, k)
    V = x[k*k:k*k+k] if k*k+k <= n else np.zeros(k)
    gamma = 0.9  # Discount factor

    # Bellman update in max-plus: V_new[i] = max_j(R[i,j] + gamma * V[j])
    V_new = np.max(R + gamma * V[np.newaxis, :], axis=1)
    return V_new

OPERATIONS["bellman_equation_iterate"] = {
    "fn": bellman_equation_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "Bellman equation iteration in max-plus algebra with discount"
}


def maslov_dequantization(x):
    """Maslov dequantization: lim_{h->0} h * log(sum(exp(x_i / h))).
    As h -> 0+, this converges to max(x_i). We compute for several h values
    to show the dequantization process.
    Input: array. Output: array (results for decreasing h)."""
    x = np.asarray(x, dtype=float)
    h_values = np.array([10.0, 1.0, 0.1, 0.01, 0.001])
    results = np.zeros(len(h_values))
    for i, h in enumerate(h_values):
        # h * log(sum(exp(x / h))) with numerical stability
        shifted = x / h - np.max(x / h)
        results[i] = h * (np.log(np.sum(np.exp(shifted))) + np.max(x / h))
    return results

OPERATIONS["maslov_dequantization"] = {
    "fn": maslov_dequantization,
    "input_type": "array",
    "output_type": "array",
    "description": "Maslov dequantization: h*log(sum(exp(x/h))) converging to max(x)"
}


def legendre_fenchel_transform(x):
    """Legendre-Fenchel (convex conjugate) transform: f*(p) = sup_x(p*x - f(x)).
    This is the idempotent Fourier transform in max-plus algebra.
    Given f sampled at x_i, compute f* at the same points as p values.
    Input: array (function values). Output: array (conjugate values)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    # x_i = sample points (0, 1, ..., n-1), f(x_i) = x[i]
    x_pts = np.arange(n, dtype=float)
    p_pts = np.linspace(-2, 2, n)  # Dual variable range

    f_star = np.zeros(n)
    for i, p in enumerate(p_pts):
        # f*(p) = max_j(p * x_pts[j] - x[j])
        f_star[i] = np.max(p * x_pts - x)
    return f_star

OPERATIONS["legendre_fenchel_transform"] = {
    "fn": legendre_fenchel_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Legendre-Fenchel transform: idempotent Fourier in max-plus algebra"
}


def morphological_dilation(x):
    """Mathematical morphology dilation: (f ⊕ g)(x) = max_{y}(f(y) + g(x-y)).
    This is convolution in max-plus algebra. Uses a parabolic structuring element.
    Input: array (signal f). Output: array (dilated signal)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    # Structuring element: inverted parabola
    radius = min(n // 2, 5)
    se = np.zeros(2 * radius + 1)
    for i in range(len(se)):
        se[i] = -(i - radius) ** 2 / max(radius, 1)

    # Max-plus convolution
    result = np.full(n, -np.inf)
    for i in range(n):
        for j in range(len(se)):
            idx = i - j + radius
            if 0 <= idx < n:
                result[i] = max(result[i], x[idx] + se[j])
    return result

OPERATIONS["morphological_dilation"] = {
    "fn": morphological_dilation,
    "input_type": "array",
    "output_type": "array",
    "description": "Morphological dilation: max-plus convolution with parabolic element"
}


def morphological_erosion(x):
    """Mathematical morphology erosion: (f ⊖ g)(x) = min_{y}(f(y) - g(y-x)).
    Dual of dilation in min-plus algebra.
    Input: array (signal f). Output: array (eroded signal)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    radius = min(n // 2, 5)
    se = np.zeros(2 * radius + 1)
    for i in range(len(se)):
        se[i] = -(i - radius) ** 2 / max(radius, 1)

    # Min-plus: erosion is infimal convolution of f with reflected -g
    result = np.full(n, np.inf)
    for i in range(n):
        for j in range(len(se)):
            idx = i + j - radius
            if 0 <= idx < n:
                result[i] = min(result[i], x[idx] - se[j])
    return result

OPERATIONS["morphological_erosion"] = {
    "fn": morphological_erosion,
    "input_type": "array",
    "output_type": "array",
    "description": "Morphological erosion: min-plus dual of dilation"
}


def idempotent_measure(x):
    """Maslov measure (idempotent probability): replace integration with supremum
    and multiplication with addition. The idempotent measure of a set is
    sup of the density. Returns the idempotent "integral" = max(x) and
    the idempotent "expectation" = argmax(x) (normalized).
    Input: array. Output: array [max_val, argmax_normalized]."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    max_val = np.max(x)
    argmax = float(np.argmax(x)) / max(n - 1, 1)
    return np.array([max_val, argmax])

OPERATIONS["idempotent_measure"] = {
    "fn": idempotent_measure,
    "input_type": "array",
    "output_type": "array",
    "description": "Maslov idempotent measure: (supremum, normalized argmax)"
}


def viterbi_semiring_product(x):
    """Viterbi semiring (max, *) product: used in HMM decoding.
    a ⊕ b = max(a, b), a ⊗ b = a * b (for probabilities).
    Given transition probs (first half) and emission probs (second half),
    compute Viterbi step: max over previous states of (trans * emission).
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    x = np.clip(x, 0, None)  # Probabilities are non-negative
    n = len(x) // 2
    if n == 0:
        return x.copy()
    trans = x[:n]
    emission = x[n:2*n]
    # Normalize to [0,1] range for probability interpretation
    t_sum = np.sum(trans)
    e_sum = np.sum(emission)
    if t_sum > 0:
        trans = trans / t_sum
    if e_sum > 0:
        emission = emission / e_sum
    # Viterbi: for each state, max over incoming transitions * emission
    # Simple model: each state receives from all others
    viterbi = np.max(trans) * emission  # Best incoming * local emission
    return viterbi

OPERATIONS["viterbi_semiring_product"] = {
    "fn": viterbi_semiring_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Viterbi semiring step: max(trans) * emission for HMM decoding"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
