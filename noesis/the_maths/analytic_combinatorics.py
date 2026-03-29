"""
Analytic Combinatorics — singularity analysis, transfer theorems, asymptotic enumeration

Connects to: [complex_analysis, generating_functions, asymptotic_analysis, combinatorics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "analytic_combinatorics"
OPERATIONS = {}


def singularity_type_classify(x):
    """Classify singularity type from Taylor coefficients.
    If a_n ~ C * rho^{-n} * n^{-alpha}, then:
      alpha > 0 => algebraic singularity
      alpha = 0 => simple pole
      alpha < 0 => essential singularity (or none)
    Input: array of Taylor coefficients a_0, a_1, ..., a_n. Output: array [rho, alpha].
    """
    n = len(x)
    if n < 4:
        return np.array([1.0, 0.0])
    # Estimate growth rate rho^{-1} from ratio of consecutive terms
    ratios = []
    for i in range(1, n):
        if abs(x[i - 1]) > 1e-12:
            ratios.append(abs(x[i] / x[i - 1]))
    if not ratios:
        return np.array([1.0, 0.0])
    rho_inv = np.median(ratios[-max(3, len(ratios) // 2):])
    rho = 1.0 / rho_inv if rho_inv > 1e-12 else np.inf

    # Estimate alpha from a_n * rho^n ~ C * n^{-alpha}
    indices = np.arange(1, n)
    scaled = np.abs(x[1:]) * rho**indices
    log_scaled = np.log(scaled + 1e-300)
    log_n = np.log(indices)
    # Linear regression: log(a_n * rho^n) ~ -alpha * log(n) + const
    if len(log_n) >= 3:
        valid = np.isfinite(log_scaled) & np.isfinite(log_n)
        if valid.sum() >= 2:
            coeffs = np.polyfit(log_n[valid], log_scaled[valid], 1)
            alpha = -coeffs[0]
        else:
            alpha = 0.0
    else:
        alpha = 0.0

    return np.array([rho, alpha])


OPERATIONS["singularity_type_classify"] = {
    "fn": singularity_type_classify,
    "input_type": "array",
    "output_type": "array",
    "description": "Classify singularity type [rho, alpha] from Taylor coefficients"
}


def darboux_asymptotic(x):
    """Darboux's method: estimate [n]f from singularity at rho with exponent alpha.
    a_n ~ (C / Gamma(alpha)) * rho^{-n} * n^{alpha-1}.
    Input: array [rho, alpha, C, n]. Output: scalar (estimated coefficient).
    """
    if len(x) < 4:
        return np.float64(0.0)
    rho, alpha, C, n_val = x[0], x[1], x[2], max(x[3], 1)
    from math import gamma as gamma_fn
    try:
        g = gamma_fn(alpha) if alpha > 0 else 1.0
    except (ValueError, OverflowError):
        g = 1.0
    result = (C / g) * rho**(-n_val) * n_val**(alpha - 1)
    return np.float64(result)


OPERATIONS["darboux_asymptotic"] = {
    "fn": darboux_asymptotic,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Darboux asymptotic estimate of n-th coefficient from singularity parameters"
}


def algebraic_singularity_coeffs(x):
    """Coefficients from an algebraic singularity f(z) ~ (1 - z/rho)^{-alpha}.
    [z^n] ~ rho^{-n} * n^{alpha-1} / Gamma(alpha).
    Input: array [rho, alpha]. Output: array of first 10 estimated coefficients.
    """
    if len(x) < 2:
        return np.ones(10)
    rho, alpha = x[0], x[1]
    from math import gamma as gamma_fn
    try:
        g = gamma_fn(alpha) if alpha > 0 else 1.0
    except (ValueError, OverflowError):
        g = 1.0
    ns = np.arange(1, 11)
    coeffs = (1.0 / (rho**ns)) * ns**(alpha - 1) / g
    return coeffs


OPERATIONS["algebraic_singularity_coeffs"] = {
    "fn": algebraic_singularity_coeffs,
    "input_type": "array",
    "output_type": "array",
    "description": "First 10 asymptotic coefficients from algebraic singularity (rho, alpha)"
}


def meromorphic_residue(x):
    """Estimate residue at a simple pole from Taylor coefficients.
    If f has a simple pole at z=rho, then a_n ~ Res * rho^{-(n+1)}.
    So Res ~ a_n * rho^{n+1}. We estimate rho from ratios and compute Res.
    Input: array of Taylor coefficients. Output: scalar (estimated residue).
    """
    n = len(x)
    if n < 3:
        return np.float64(x[-1] if len(x) > 0 else 0.0)
    ratios = []
    for i in range(1, n):
        if abs(x[i - 1]) > 1e-12:
            ratios.append(abs(x[i] / x[i - 1]))
    if not ratios:
        return np.float64(0.0)
    rho_inv = np.median(ratios[-3:])
    rho = 1.0 / rho_inv if rho_inv > 1e-12 else 1.0
    # Residue estimate from last coefficient
    last_n = n - 1
    residue = x[last_n] * rho**(last_n + 1)
    return np.float64(residue)


OPERATIONS["meromorphic_residue"] = {
    "fn": meromorphic_residue,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate residue at dominant pole from Taylor coefficients"
}


def exponential_growth_rate(x):
    """Exponential growth rate mu of a sequence: a_n ~ mu^n.
    Estimated as the geometric mean of ratios a_{n+1}/a_n.
    Input: array of sequence values. Output: scalar.
    """
    ratios = []
    for i in range(1, len(x)):
        if abs(x[i - 1]) > 1e-12:
            ratios.append(abs(x[i] / x[i - 1]))
    if not ratios:
        return np.float64(1.0)
    return np.float64(np.exp(np.mean(np.log(np.array(ratios) + 1e-300))))


OPERATIONS["exponential_growth_rate"] = {
    "fn": exponential_growth_rate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Exponential growth rate of a sequence from ratio estimates"
}


def subexponential_factor(x):
    """Estimate subexponential factor: a_n / mu^n ~ C * n^alpha.
    Input: array of sequence values. Output: array [C, alpha].
    """
    n = len(x)
    if n < 3:
        return np.array([1.0, 0.0])
    # Get mu
    ratios = []
    for i in range(1, n):
        if abs(x[i - 1]) > 1e-12:
            ratios.append(abs(x[i] / x[i - 1]))
    if not ratios:
        return np.array([1.0, 0.0])
    mu = np.exp(np.mean(np.log(np.array(ratios) + 1e-300)))

    # Detrend: b_n = a_n / mu^n
    indices = np.arange(n)
    b = np.abs(x) / (mu**indices + 1e-300)
    # Fit log(b_n) ~ alpha*log(n) + log(C) for n >= 1
    valid = (indices >= 1) & (b > 1e-300)
    if valid.sum() < 2:
        return np.array([1.0, 0.0])
    log_b = np.log(b[valid])
    log_n = np.log(indices[valid].astype(float))
    coeffs = np.polyfit(log_n, log_b, 1)
    alpha = coeffs[0]
    C = np.exp(coeffs[1])
    return np.array([C, alpha])


OPERATIONS["subexponential_factor"] = {
    "fn": subexponential_factor,
    "input_type": "array",
    "output_type": "array",
    "description": "Subexponential factor [C, alpha] where a_n ~ C * mu^n * n^alpha"
}


def generating_function_radius(x):
    """Radius of convergence of a power series from its coefficients.
    R = 1 / limsup |a_n|^{1/n}.
    Input: array of Taylor coefficients. Output: scalar.
    """
    n = len(x)
    if n < 2:
        return np.float64(np.inf)
    indices = np.arange(1, n)
    roots = np.abs(x[1:])**(1.0 / indices)
    # limsup approximated by max of last few values
    tail = roots[max(0, len(roots) - 3):]
    limsup = np.max(tail) if len(tail) > 0 else 1.0
    if limsup < 1e-12:
        return np.float64(np.inf)
    return np.float64(1.0 / limsup)


OPERATIONS["generating_function_radius"] = {
    "fn": generating_function_radius,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Radius of convergence from Taylor coefficients via root test"
}


def saddle_point_estimate(x):
    """Saddle-point estimate for [z^n] e^{f(z)} where f(z) = sum a_k z^k.
    Input: array of coefficients [a_1, a_2, ...]. Output: scalar.
    Uses the approximation: find z_0 such that z_0 f'(z_0) = n, then
    [z^n] ~ e^{f(z_0)} / (z_0^n * sqrt(2*pi*z_0^2 f''(z_0))).
    Here n = len(x).
    """
    n = len(x)
    if n < 2:
        return np.float64(1.0)
    # Treat x as coefficients of f(z) = sum_{k=1}^{n} x[k-1] * z^k
    # Saddle point: z * f'(z) = n => sum k*x[k-1]*z^k = n
    # Try Newton's method starting from z=1
    target = float(n)
    z = 1.0
    for _ in range(50):
        ks = np.arange(1, n + 1, dtype=float)
        fz = np.sum(x * z**ks)
        fpz = np.sum(ks * x * z**(ks - 1))
        zfpz = z * fpz
        if abs(zfpz) < 1e-300:
            break
        # Newton step on g(z) = z*f'(z) - n = 0
        # g'(z) = f'(z) + z*f''(z)
        fppz = np.sum(ks * (ks - 1) * x * z**(ks - 2))
        gpz = fpz + z * fppz
        if abs(gpz) < 1e-300:
            break
        z = z - (zfpz - target) / gpz
        z = max(z, 1e-6)

    ks = np.arange(1, n + 1, dtype=float)
    fz = np.sum(x * z**ks)
    fppz = np.sum(ks * (ks - 1) * x * z**(ks - 2))
    variance = z**2 * fppz
    if variance <= 0:
        variance = 1.0
    estimate = np.exp(fz) / (z**n * np.sqrt(2 * np.pi * variance))
    return np.float64(np.clip(estimate, -1e100, 1e100))


OPERATIONS["saddle_point_estimate"] = {
    "fn": saddle_point_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Saddle-point estimate of n-th coefficient of exp(f(z))"
}


def hayman_admissible_check(x):
    """Check if a power series appears Hayman-admissible (variance grows).
    A function f(z) = sum a_n z^n is H-admissible if the saddle-point variance
    b(r) = r*d/dr(r*f'(r)/f(r)) -> infinity as r -> R.
    Input: array of coefficients. Output: integer (1=likely admissible, 0=not).
    """
    n = len(x)
    if n < 4:
        return np.int64(0)
    # Check if partial sums of |a_n| * r^n have growing variance-like quantity
    # Evaluate at a few radii
    variances = []
    for r in [0.5, 0.8, 0.95]:
        ks = np.arange(n, dtype=float)
        weights = np.abs(x) * r**ks
        total = weights.sum()
        if total < 1e-12:
            variances.append(0.0)
            continue
        p = weights / total
        mean_k = np.sum(ks * p)
        var_k = np.sum((ks - mean_k)**2 * p)
        variances.append(var_k)
    # Admissible if variance is increasing with r
    if len(variances) >= 3 and variances[-1] > variances[0] + 0.1:
        return np.int64(1)
    return np.int64(0)


OPERATIONS["hayman_admissible_check"] = {
    "fn": hayman_admissible_check,
    "input_type": "array",
    "output_type": "integer",
    "description": "Check if power series appears Hayman-admissible (growing saddle-point variance)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
