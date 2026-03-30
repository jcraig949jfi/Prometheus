"""
Modular Forms — q-expansions, Eisenstein series, Dedekind eta

Connects to: [number_theory, algebraic_geometry, elliptic_curves, representation_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "modular_forms"
OPERATIONS = {}


def _sigma_k(n, k):
    """Sum of k-th powers of divisors of n."""
    if n <= 0:
        return 0
    total = 0
    for d in range(1, n + 1):
        if n % d == 0:
            total += d ** k
    return total


def eisenstein_series_e4(x):
    """q-expansion coefficients of the Eisenstein series E_4(tau).
    E_4 = 1 + 240 * sum_{n>=1} sigma_3(n) * q^n.
    Returns first N coefficients where N = len(x). Input: array. Output: array."""
    N = len(x)
    coeffs = np.zeros(N)
    coeffs[0] = 1.0
    for n in range(1, N):
        coeffs[n] = 240.0 * _sigma_k(n, 3)
    return coeffs


OPERATIONS["eisenstein_series_e4"] = {
    "fn": eisenstein_series_e4,
    "input_type": "array",
    "output_type": "array",
    "description": "q-expansion coefficients of Eisenstein series E_4: 1 + 240*sum(sigma_3(n)*q^n)"
}


def eisenstein_series_e6(x):
    """q-expansion coefficients of the Eisenstein series E_6(tau).
    E_6 = 1 - 504 * sum_{n>=1} sigma_5(n) * q^n.
    Returns first N coefficients where N = len(x). Input: array. Output: array."""
    N = len(x)
    coeffs = np.zeros(N)
    coeffs[0] = 1.0
    for n in range(1, N):
        coeffs[n] = -504.0 * _sigma_k(n, 5)
    return coeffs


OPERATIONS["eisenstein_series_e6"] = {
    "fn": eisenstein_series_e6,
    "input_type": "array",
    "output_type": "array",
    "description": "q-expansion coefficients of Eisenstein series E_6: 1 - 504*sum(sigma_5(n)*q^n)"
}


def dedekind_eta_approx(x):
    """Approximate |eta(tau)| for tau = i*y where y = x[0] (must be > 0).
    eta(tau) = q^{1/24} * prod_{n>=1}(1 - q^n), q = exp(2*pi*i*tau).
    For tau = iy, q = exp(-2*pi*y) is real. Input: array. Output: scalar."""
    y = abs(float(x[0]))
    if y < 0.01:
        y = 0.01
    q = np.exp(-2.0 * np.pi * y)
    # q^{1/24}
    result = q ** (1.0 / 24.0)
    # Product (1 - q^n) for n = 1 to 50
    for n in range(1, 51):
        qn = q ** n
        if qn < 1e-15:
            break
        result *= (1.0 - qn)
    return float(result)


OPERATIONS["dedekind_eta_approx"] = {
    "fn": dedekind_eta_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate |eta(iy)| for the Dedekind eta function at tau=iy"
}


def ramanujan_tau(x):
    """Compute Ramanujan tau function values tau(1)..tau(N) where N = len(x).
    tau(n) is the coefficient of q^n in q*prod_{n>=1}(1-q^n)^24 = Delta(tau).
    Uses the identity Delta = (E_4^3 - E_6^2)/1728. Input: array. Output: array."""
    N = len(x)
    # Compute E_4 and E_6 coefficients up to order N
    e4 = np.zeros(N)
    e6 = np.zeros(N)
    e4[0] = 1.0
    e6[0] = 1.0
    for n in range(1, N):
        e4[n] = 240.0 * _sigma_k(n, 3)
        e6[n] = -504.0 * _sigma_k(n, 5)

    # E_4^3 via repeated polynomial multiplication (truncated)
    e4_sq = np.zeros(N)
    for i in range(N):
        for j in range(N - i):
            e4_sq[i + j] += e4[i] * e4[j]
    e4_cu = np.zeros(N)
    for i in range(N):
        for j in range(N - i):
            e4_cu[i + j] += e4_sq[i] * e4[j]

    # E_6^2
    e6_sq = np.zeros(N)
    for i in range(N):
        for j in range(N - i):
            e6_sq[i + j] += e6[i] * e6[j]

    # Delta = (E_4^3 - E_6^2) / 1728
    delta = (e4_cu - e6_sq) / 1728.0
    # tau(n) = delta[n] for n >= 1 (delta[0] should be 0)
    return delta


OPERATIONS["ramanujan_tau"] = {
    "fn": ramanujan_tau,
    "input_type": "array",
    "output_type": "array",
    "description": "Ramanujan tau function: coefficients of the modular discriminant Delta"
}


def j_invariant_approx(x):
    """Approximate the j-invariant j(tau) for tau = i*y where y = x[0].
    j = 1728 * E_4^3 / (E_4^3 - E_6^2) = E_4^3 / Delta.
    For tau = iy with large y, j ~ 1/q + 744 + ... where q = e^{-2*pi*y}.
    Input: array. Output: scalar."""
    y = abs(float(x[0]))
    if y < 0.01:
        y = 0.01
    q = np.exp(-2.0 * np.pi * y)
    # j(tau) = 1/q + 744 + 196884*q + 21493760*q^2 + ...
    if q < 1e-15:
        return float(1.0 / max(q, 1e-300))
    j = 1.0 / q + 744.0 + 196884.0 * q + 21493760.0 * q ** 2
    return float(j)


OPERATIONS["j_invariant_approx"] = {
    "fn": j_invariant_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate j-invariant j(iy) using q-expansion"
}


def theta_function(x):
    """Jacobi theta function theta_3(0, q) = 1 + 2*sum_{n>=1} q^{n^2}.
    Uses q = exp(-pi * x[0]). Input: array. Output: scalar."""
    y = abs(float(x[0]))
    if y < 0.01:
        y = 0.01
    q = np.exp(-np.pi * y)
    result = 1.0
    for n in range(1, 30):
        term = q ** (n * n)
        if term < 1e-15:
            break
        result += 2.0 * term
    return float(result)


OPERATIONS["theta_function"] = {
    "fn": theta_function,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Jacobi theta_3(0, q) with q = exp(-pi*x[0])"
}


def modular_discriminant(x):
    """Compute modular discriminant Delta(tau) = eta(tau)^24 at tau = i*y.
    Uses the product formula. Input: array. Output: scalar."""
    y = abs(float(x[0]))
    if y < 0.01:
        y = 0.01
    q = np.exp(-2.0 * np.pi * y)
    # Delta = q * prod(1-q^n)^24
    result = q
    for n in range(1, 51):
        qn = q ** n
        if qn < 1e-15:
            break
        result *= (1.0 - qn) ** 24
    return float(result)


OPERATIONS["modular_discriminant"] = {
    "fn": modular_discriminant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Modular discriminant Delta(iy) = eta(iy)^24 via product formula"
}


def q_expansion_coefficients(x):
    """Compute q-expansion coefficients of eta(tau)^k where k = int(x[0]).
    eta^k = q^{k/24} * prod(1-q^n)^k. Returns coefficients of q^{k/24+j}.
    Limited to first 10 terms. Input: array. Output: array."""
    k = int(round(x[0]))
    N = 10
    # Expand prod(1-q^n)^k as a power series, truncated to N terms
    # Start with [1, 0, 0, ...]
    coeffs = np.zeros(N)
    coeffs[0] = 1.0
    # Multiply by (1 - q^n)^k for n = 1, 2, ...
    for n in range(1, N):
        # (1 - q^n)^k via binomial, applied to the coefficient array
        # Multiply coefficient array by (1 - q^n)^k
        for _ in range(abs(k)):
            sign = -1.0 if k > 0 else 1.0
            new_coeffs = coeffs.copy()
            if n < N:
                new_coeffs[n:] += sign * coeffs[:N - n]
            coeffs = new_coeffs
    return coeffs


OPERATIONS["q_expansion_coefficients"] = {
    "fn": q_expansion_coefficients,
    "input_type": "array",
    "output_type": "array",
    "description": "q-expansion coefficients of eta(tau)^k where k = int(x[0])"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
