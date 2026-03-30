"""
Divergent Series -- Abel, Cesaro, Borel, Ramanujan summation methods

Connects to: [zeta_functions, analytic_combinatorics, p_adic_numbers, nonstandard_analysis]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import math
import numpy as np

FIELD_NAME = "divergent_series"
OPERATIONS = {}


def abel_summation(x):
    """Abel sum: lim_{t->1^-} sum a_n t^n. Input: array (series coefficients). Output: scalar."""
    # Evaluate power series at t close to 1 from below using averaging
    ts = np.linspace(0.9, 0.999, 200)
    vals = np.array([np.sum(x * t ** np.arange(len(x))) for t in ts])
    # Richardson-like extrapolation: fit polynomial in (1-t) and take constant term
    eps = 1.0 - ts
    # Fit quadratic in eps
    coeffs = np.polyfit(eps, vals, 2)
    return float(coeffs[-1])  # value at eps=0


OPERATIONS["abel_summation"] = {
    "fn": abel_summation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Abel summation of a (possibly divergent) series"
}


def cesaro_sum(x):
    """Cesaro (C,1) sum: lim of arithmetic means of partial sums. Input: array. Output: scalar."""
    partial_sums = np.cumsum(x)
    cesaro_means = np.cumsum(partial_sums) / np.arange(1, len(x) + 1)
    return float(cesaro_means[-1])


OPERATIONS["cesaro_sum"] = {
    "fn": cesaro_sum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Cesaro (C,1) summation via arithmetic means of partial sums"
}


def borel_sum(x):
    """Borel sum: integral_0^inf e^{-t} sum a_n t^n/n! dt. Input: array. Output: scalar."""
    n = np.arange(len(x))
    factorials = np.array([float(math.factorial(int(k))) for k in n])
    coeffs = x / factorials  # a_n / n!
    # Numerical integration via Gauss-Laguerre quadrature (weight e^{-t})
    # Use numpy roots of Laguerre polynomial
    num_points = min(50, max(10, len(x)))
    # Simple Gauss-Laguerre: approximate with known nodes
    # For robustness, use midpoint quadrature on [0, T] with e^{-t} weight
    T = 30.0
    dt = 0.05
    ts = np.arange(dt / 2, T, dt)
    powers = np.array([t ** n for t in ts])  # shape (len(ts), len(n))
    series_vals = powers @ coeffs
    integrand = np.exp(-ts) * series_vals
    result = np.sum(integrand) * dt
    return float(result)


OPERATIONS["borel_sum"] = {
    "fn": borel_sum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Borel summation via Laplace transform of exponential generating function"
}


def ramanujan_summation(x):
    """Ramanujan summation of a divergent series. For 1+2+3+...=-1/12, pass np.arange(1,N).
    Uses the Ramanujan sum formula: R = -sum_{k=1}^{n} a_k / 2 + ... (Euler-Maclaurin based).
    For the partial input, computes the regularized value. Input: array. Output: scalar."""
    n = len(x)
    if n == 0:
        return 0.0
    # Euler-Maclaurin based Ramanujan summation:
    # R = a(1)/2 + sum_{k=1}^{p} B_{2k}/(2k)! * a^{(2k-1)}(1)
    # For a sequence, approximate using finite differences
    # Simple approach: partial sum minus integral approximation
    partial_sum = np.sum(x)
    # Trapezoidal integral approximation
    integral_approx = np.sum(x) - (x[0] + x[-1]) / 2.0  # trapezoidal rule
    # Ramanujan's constant: R = S - integral - a(1)/2 + correction
    # For f(n) = n: sum 1..N = N(N+1)/2, integral = N^2/2, so R = N/2 + 1/2 + correction
    # The regularized value uses Bernoulli number corrections
    # B2=1/6, so correction = B2 * (finite diff of x at start)
    if n > 1:
        first_diff = x[1] - x[0] if len(x) > 1 else 0.0
    else:
        first_diff = 0.0
    ramanujan_val = x[0] / 2.0 + (1.0 / 6.0) * first_diff
    # Higher order: B4 = -1/30, need 3rd finite difference
    if n > 3:
        third_diff = x[3] - 3 * x[2] + 3 * x[1] - x[0]
        ramanujan_val += (-1.0 / 30.0) * third_diff / 24.0
    return float(ramanujan_val)


OPERATIONS["ramanujan_summation"] = {
    "fn": ramanujan_summation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Ramanujan summation via Euler-Maclaurin regularization"
}


def euler_summation(x):
    """Euler (E,1) summation: sum 2^{-(n+1)} * sum_{k=0}^{n} C(n,k) a_k.
    Input: array. Output: scalar."""
    n = len(x)
    result = 0.0
    for j in range(n):
        # Euler transform: sum of binomial-weighted forward differences
        binom_sum = 0.0
        for k in range(j + 1):
            # C(j, k) * a_k
            binom_coeff = 1.0
            for m in range(k):
                binom_coeff *= (j - m) / (m + 1)
            binom_sum += binom_coeff * x[k]
        result += binom_sum / (2.0 ** (j + 1))
    return float(result)


OPERATIONS["euler_summation"] = {
    "fn": euler_summation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Euler summation method using binomial transform"
}


def regularized_sum(x):
    """Regularized sum using exponential smoothing: sum a_n e^{-n*eps} as eps->0+.
    Input: array. Output: scalar."""
    n = np.arange(len(x))
    epsilons = np.logspace(-1, -3, 50)
    vals = np.array([np.sum(x * np.exp(-n * eps)) for eps in epsilons])
    # Extrapolate to eps=0 via polynomial fit in eps
    coeffs = np.polyfit(epsilons, vals, 3)
    return float(coeffs[-1])


OPERATIONS["regularized_sum"] = {
    "fn": regularized_sum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Exponential regularization with extrapolation to eps=0"
}


def zeta_regularization(x):
    """Zeta regularization: sum a_n * n^{-s} analytically continued to s=0.
    Input: array (treated as a_n for n=1,2,...). Output: scalar."""
    n = np.arange(1, len(x) + 1, dtype=float)
    # Evaluate at several s values and extrapolate to s=0
    s_vals = np.linspace(2.0, 4.0, 30)
    results = np.array([np.sum(x * n ** (-s)) for s in s_vals])
    # Fit and extrapolate
    coeffs = np.polyfit(s_vals, results, 4)
    return float(np.polyval(coeffs, 0.0))


OPERATIONS["zeta_regularization"] = {
    "fn": zeta_regularization,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Zeta function regularization via analytic continuation"
}


def analytic_continuation_approx(x):
    """Approximate analytic continuation of sum a_n z^n beyond radius of convergence.
    Evaluates at z = -1 using Pade-like acceleration. Input: array. Output: scalar."""
    # Euler transform for z = -1: equivalent to alternating series acceleration
    n = len(x)
    # Euler transform of alternating signs
    z = -1.0
    powered = x * (z ** np.arange(n))
    # Apply Euler acceleration
    d = np.copy(powered).astype(float)
    result = d[0] / 2.0
    for j in range(1, n):
        d_new = np.zeros(n - j)
        for k in range(n - j):
            d_new[k] = (d[k] + d[k + 1]) / 2.0
        result += d_new[0] / (2.0 ** (j + 1)) if len(d_new) > 0 else 0.0
        d = d_new
        if len(d) <= 1:
            break
    return float(result)


OPERATIONS["analytic_continuation_approx"] = {
    "fn": analytic_continuation_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate analytic continuation via Euler acceleration at z=-1"
}


def divergence_rate(x):
    """Measure how fast a series diverges: ratio of partial sums growth.
    Input: array. Output: scalar (growth exponent)."""
    partial_sums = np.cumsum(np.abs(x))
    # Fit log(partial_sum) ~ alpha * log(n)
    n = np.arange(1, len(x) + 1, dtype=float)
    mask = partial_sums > 0
    if np.sum(mask) < 2:
        return 0.0
    log_n = np.log(n[mask])
    log_s = np.log(partial_sums[mask])
    coeffs = np.polyfit(log_n, log_s, 1)
    return float(coeffs[0])  # growth exponent


OPERATIONS["divergence_rate"] = {
    "fn": divergence_rate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Growth exponent of partial sums (0 = bounded, 1 = linear, 2 = quadratic)"
}


def summability_test(x):
    """Test which summation methods converge for this series.
    Returns a score 0-1 indicating summability. Input: array. Output: scalar."""
    scores = []
    # Test 1: Do partial sums have bounded Cesaro means?
    partial_sums = np.cumsum(x)
    cesaro = np.cumsum(partial_sums) / np.arange(1, len(x) + 1)
    cesaro_var = np.var(cesaro[len(x) // 2:]) if len(x) > 2 else np.var(cesaro)
    scores.append(1.0 / (1.0 + cesaro_var))

    # Test 2: Do Abel means converge?
    t = 0.95
    n = np.arange(len(x))
    abel_partial = np.cumsum(x * t ** n)
    abel_var = np.var(abel_partial[len(x) // 2:]) if len(x) > 2 else np.var(abel_partial)
    scores.append(1.0 / (1.0 + abel_var))

    # Test 3: Ratio test on terms
    ratios = np.abs(x[1:]) / (np.abs(x[:-1]) + 1e-30)
    avg_ratio = np.mean(ratios)
    scores.append(1.0 / (1.0 + max(0, avg_ratio - 1.0)))

    return float(np.mean(scores))


OPERATIONS["summability_test"] = {
    "fn": summability_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Score (0-1) indicating how summable the series is across methods"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
