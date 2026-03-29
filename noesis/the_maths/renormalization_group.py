"""
Renormalization Group — Block spin transforms, decimation on lattices, scale-dependent coupling constants

Connects to: [sheaves_on_graphs, discrete_morse_theory, convex_geometry]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "renormalization_group"
OPERATIONS = {}


def block_spin_transform_1d(x):
    """Block spin transformation: coarse-grain a 1D spin chain by averaging blocks of 2.
    Input: array (spin configuration). Output: array (coarse-grained spins)."""
    n = len(x)
    n_blocks = n // 2
    if n_blocks == 0:
        return x.copy()
    blocked = np.zeros(n_blocks)
    for i in range(n_blocks):
        blocked[i] = np.sign(x[2 * i] + x[2 * i + 1])
        if blocked[i] == 0:
            blocked[i] = x[2 * i]  # tie-break
    return blocked


OPERATIONS["block_spin_transform_1d"] = {
    "fn": block_spin_transform_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "Coarse-grains a 1D spin chain by majority-rule block spin transform"
}


def decimation_1d(x):
    """Decimation RG: keep every other spin, integrate out the rest.
    For 1D Ising with coupling K, the decimated coupling K' satisfies
    tanh(K') = tanh(K)^2. Here we apply to actual spin values.
    Input: array. Output: array (decimated spins)."""
    # Keep every other spin (odd-indexed sites)
    return x[::2].copy()


OPERATIONS["decimation_1d"] = {
    "fn": decimation_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "Decimation RG: keeps every other site in a 1D lattice"
}


def renormalization_flow_step(x):
    """One step of RG flow for 1D Ising coupling constants.
    Given couplings K (array), compute K' where tanh(K') = tanh(K)^2.
    Input: array (coupling constants). Output: array (renormalized couplings)."""
    # RG recursion for 1D Ising: tanh(K') = tanh(K)^2
    t = np.tanh(x)
    t_sq = t ** 2
    # Clip to avoid arctanh domain issues
    t_sq = np.clip(t_sq, -1 + 1e-15, 1 - 1e-15)
    K_prime = np.arctanh(t_sq)
    return K_prime


OPERATIONS["renormalization_flow_step"] = {
    "fn": renormalization_flow_step,
    "input_type": "array",
    "output_type": "array",
    "description": "One RG flow step for 1D Ising: tanh(K') = tanh(K)^2"
}


def critical_exponent_estimate(x):
    """Estimate the correlation length critical exponent nu from RG flow.
    nu = ln(b) / ln(lambda) where b=2 (block size) and lambda = dK'/dK at fixed point.
    For 1D Ising: K*=0 (trivial), lambda = 0, so nu -> infinity (no phase transition).
    We compute the linearized RG at the given coupling values.
    Input: array. Output: array (estimated nu for each coupling)."""
    # dK'/dK = d/dK arctanh(tanh(K)^2) = 2*tanh(K)/cosh(K)^2 / (1 - tanh(K)^4)
    t = np.tanh(x)
    cosh_sq = np.cosh(x) ** 2
    denom = 1.0 - t ** 4 + 1e-15
    dKprime_dK = 2.0 * t / (cosh_sq * denom + 1e-15)
    # nu = ln(2) / ln|lambda| where lambda = dK'/dK
    lam = np.abs(dKprime_dK) + 1e-15
    nu = np.log(2.0) / (np.abs(np.log(lam)) + 1e-15)
    return nu


OPERATIONS["critical_exponent_estimate"] = {
    "fn": critical_exponent_estimate,
    "input_type": "array",
    "output_type": "array",
    "description": "Estimates correlation length exponent nu from linearized RG flow"
}


def scaling_dimension(x):
    """Compute scaling dimensions from eigenvalues of the linearized RG transformation.
    Delta = d - ln(lambda)/ln(b) where d=1, b=2.
    Input: array (coupling constants). Output: array."""
    d = 1.0
    b = 2.0
    t = np.tanh(x)
    cosh_sq = np.cosh(x) ** 2
    denom = 1.0 - t ** 4 + 1e-15
    lam = 2.0 * t / (cosh_sq * denom + 1e-15)
    lam = np.abs(lam) + 1e-15
    delta = d - np.log(lam) / np.log(b)
    return delta


OPERATIONS["scaling_dimension"] = {
    "fn": scaling_dimension,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes scaling dimensions from linearized RG eigenvalues"
}


def beta_function_discrete(x):
    """Discrete beta function: beta(K) = K' - K, the change in coupling under one RG step.
    Input: array. Output: array."""
    K_prime = renormalization_flow_step(x)
    beta = K_prime - x
    return beta


OPERATIONS["beta_function_discrete"] = {
    "fn": beta_function_discrete,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes discrete beta function beta(K) = K' - K"
}


def fixed_point_rg(x):
    """Find fixed points of the RG flow by iterating until convergence.
    Returns the fixed-point coupling values. Input: array. Output: array."""
    K = x.copy()
    for _ in range(200):
        K_new = renormalization_flow_step(K)
        if np.max(np.abs(K_new - K)) < 1e-12:
            break
        K = K_new
    return K


OPERATIONS["fixed_point_rg"] = {
    "fn": fixed_point_rg,
    "input_type": "array",
    "output_type": "array",
    "description": "Finds RG fixed points by iterating the flow to convergence"
}


def correlation_length_scaling(x):
    """Compute how correlation length scales under RG.
    xi' = xi / b. After n steps, xi_n = xi_0 / b^n.
    Returns xi at each RG step (up to 10 steps).
    Input: array (initial correlation lengths). Output: matrix."""
    b = 2.0
    n_steps = 10
    n = len(x)
    xi = np.abs(x) + 1e-10
    result = np.zeros((n_steps, n))
    for step in range(n_steps):
        result[step] = xi
        xi = xi / b
    return result


OPERATIONS["correlation_length_scaling"] = {
    "fn": correlation_length_scaling,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Tracks correlation length scaling xi' = xi/b under RG steps"
}


def universality_class_indicator(x):
    """Classify the universality class by analyzing the RG flow behavior.
    Returns indicators: [flow_to_zero, flow_to_inf, oscillating, fixed_point_value].
    For 1D Ising, all couplings flow to 0 (high-T fixed point).
    Input: array. Output: array."""
    K = x.copy()
    K_final = fixed_point_rg(K)
    # Classify behavior
    flow_to_zero = float(np.mean(np.abs(K_final) < 1e-6))
    flow_to_inf = float(np.mean(np.abs(K_final) > 100))
    # Check for oscillation
    K1 = renormalization_flow_step(x)
    K2 = renormalization_flow_step(K1)
    oscillating = float(np.mean(np.abs(K2 - x) < np.abs(K1 - x)))
    fp_value = float(np.mean(K_final))
    return np.array([flow_to_zero, flow_to_inf, oscillating, fp_value])


OPERATIONS["universality_class_indicator"] = {
    "fn": universality_class_indicator,
    "input_type": "array",
    "output_type": "array",
    "description": "Classifies universality class from RG flow behavior"
}


def kadanoff_block_transform(x):
    """Kadanoff block spin transformation with weighted averaging.
    Block size b=2, new spin = tanh(sum of spins in block / T).
    Uses T = mean(|x|) + 0.1 as effective temperature.
    Input: array. Output: array."""
    n = len(x)
    n_blocks = n // 2
    if n_blocks == 0:
        return x.copy()
    T = np.mean(np.abs(x)) + 0.1
    blocked = np.zeros(n_blocks)
    for i in range(n_blocks):
        block_sum = x[2 * i] + x[2 * i + 1]
        blocked[i] = np.tanh(block_sum / T)
    return blocked


OPERATIONS["kadanoff_block_transform"] = {
    "fn": kadanoff_block_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Kadanoff block spin transform with thermal weighting"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
