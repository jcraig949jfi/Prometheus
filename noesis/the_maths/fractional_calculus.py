"""
Fractional Calculus — derivatives and integrals of non-integer order

Connects to: [special_functions, differential_equations, operator_theory, spectral_methods]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import gamma

FIELD_NAME = "fractional_calculus"
OPERATIONS = {}


def riemann_liouville_integral(x, alpha=0.5, dt=1.0):
    """Riemann-Liouville fractional integral of order alpha via convolution.
    Input: array. Output: array."""
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        s = 0.0
        for j in range(i + 1):
            weight = ((i - j + 1) * dt) ** (alpha - 1) * dt / gamma(alpha)
            s += weight * x[j]
        result[i] = s
    return result


OPERATIONS["riemann_liouville_integral"] = {
    "fn": riemann_liouville_integral,
    "input_type": "array",
    "output_type": "array",
    "description": "Riemann-Liouville fractional integral of order 0.5"
}


def caputo_derivative(x, alpha=0.5, dt=1.0):
    """Caputo fractional derivative of order alpha (0 < alpha < 1).
    Uses Grunwald-Letnikov weights on finite differences.
    Input: array. Output: array."""
    n = len(x)
    # For 0 < alpha < 1, Caputo = RL integral of order (1-alpha) applied to first derivative
    dx = np.diff(x) / dt
    dx = np.concatenate([[0.0], dx])
    return riemann_liouville_integral(dx, alpha=1.0 - alpha, dt=dt)


OPERATIONS["caputo_derivative"] = {
    "fn": caputo_derivative,
    "input_type": "array",
    "output_type": "array",
    "description": "Caputo fractional derivative of order 0.5"
}


def grunwald_letnikov_derivative(x, alpha=0.5, dt=1.0):
    """Grunwald-Letnikov fractional derivative using binomial-type coefficients.
    Input: array. Output: array."""
    n = len(x)
    # GL coefficients: w_j = (-1)^j * binom(alpha, j)
    weights = np.zeros(n)
    weights[0] = 1.0
    for j in range(1, n):
        weights[j] = weights[j - 1] * (-(alpha - j + 1) / j)
    result = np.zeros(n)
    for i in range(n):
        s = 0.0
        for j in range(i + 1):
            s += weights[j] * x[i - j]
        result[i] = s / (dt ** alpha)
    return result


OPERATIONS["grunwald_letnikov_derivative"] = {
    "fn": grunwald_letnikov_derivative,
    "input_type": "array",
    "output_type": "array",
    "description": "Grunwald-Letnikov fractional derivative of order 0.5"
}


def mittag_leffler_function(x, alpha=1.0, beta=1.0, n_terms=30):
    """Mittag-Leffler function E_{alpha,beta}(x) = sum x^k / Gamma(alpha*k + beta).
    Generalizes the exponential. Input: array. Output: array."""
    result = np.zeros_like(x, dtype=float)
    for k in range(n_terms):
        denom = gamma(alpha * k + beta)
        result += x ** k / denom
    return result


OPERATIONS["mittag_leffler_function"] = {
    "fn": mittag_leffler_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Mittag-Leffler function E_{1,1}(x), generalizes exp(x)"
}


def fractional_laplacian_1d(x, alpha=1.0):
    """Fractional Laplacian (-Delta)^{alpha/2} via Fourier multiplier |k|^alpha.
    Input: array. Output: array."""
    n = len(x)
    freqs = np.fft.fftfreq(n) * 2 * np.pi
    xhat = np.fft.fft(x)
    multiplier = np.abs(freqs) ** alpha
    multiplier[0] = 0.0  # zero mode
    result = np.fft.ifft(multiplier * xhat)
    return np.real(result)


OPERATIONS["fractional_laplacian_1d"] = {
    "fn": fractional_laplacian_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "1D fractional Laplacian via Fourier multiplier"
}


def fractional_diffusion_step(x, alpha=1.5, dt=0.01):
    """One step of fractional diffusion equation du/dt = -(-Delta)^{alpha/2} u.
    Input: array. Output: array."""
    lap = fractional_laplacian_1d(x, alpha=alpha)
    return x - dt * lap


OPERATIONS["fractional_diffusion_step"] = {
    "fn": fractional_diffusion_step,
    "input_type": "array",
    "output_type": "array",
    "description": "Single time step of fractional diffusion"
}


def riesz_derivative(x, alpha=1.5):
    """Riesz fractional derivative: symmetric combination of left/right RL derivatives.
    Computed via Fourier: multiplier = -|k|^alpha. Input: array. Output: array."""
    n = len(x)
    freqs = np.fft.fftfreq(n) * 2 * np.pi
    xhat = np.fft.fft(x)
    multiplier = -(np.abs(freqs) ** alpha)
    multiplier[0] = 0.0
    result = np.fft.ifft(multiplier * xhat)
    return np.real(result)


OPERATIONS["riesz_derivative"] = {
    "fn": riesz_derivative,
    "input_type": "array",
    "output_type": "array",
    "description": "Riesz symmetric fractional derivative"
}


def fractional_taylor_coefficients(x, alpha=0.5, n_terms=5):
    """Fractional Taylor series coefficients for f sampled at x.
    Uses fractional derivatives at x[0]. Input: array. Output: array."""
    # Compute GL fractional derivatives at x[0] for orders k*alpha, k=0..n_terms-1
    coeffs = np.zeros(n_terms)
    for k in range(n_terms):
        order = k * alpha
        if order == 0:
            coeffs[k] = x[0]
        else:
            gld = grunwald_letnikov_derivative(x, alpha=order)
            coeffs[k] = gld[0] / gamma(order * k + 1) if gamma(order * k + 1) != 0 else 0.0
    return coeffs


OPERATIONS["fractional_taylor_coefficients"] = {
    "fn": fractional_taylor_coefficients,
    "input_type": "array",
    "output_type": "array",
    "description": "Coefficients of fractional Taylor expansion"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
