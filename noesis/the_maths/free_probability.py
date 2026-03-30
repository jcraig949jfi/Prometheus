"""
Free Probability -- R-transform, S-transform, free convolution, Marchenko-Pastur

Connects to: [random_matrices, operator_algebras, combinatorics, von_neumann_algebras]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "free_probability"
OPERATIONS = {}


def _noncrossing_partitions_count(n):
    """Catalan number C_n = number of noncrossing partitions of [n]."""
    if n <= 0:
        return 1
    # Catalan number via binomial
    c = 1
    for i in range(n):
        c = c * (2 * n - i) // (i + 1)
    return c // (n + 1)


def free_convolution_additive(x):
    """Additive free convolution of two semicircular distributions.
    If X ~ semicircle(0, a) and Y ~ semicircle(0, b) are free,
    then X+Y ~ semicircle(0, sqrt(a^2+b^2)).
    x[0] = radius a, x[1] = radius b. Returns moments of the sum.
    Input: array. Output: array (first 8 moments)."""
    a = abs(x[0]) if len(x) > 0 else 1.0
    b = abs(x[1]) if len(x) > 1 else 1.0
    r = np.sqrt(a**2 + b**2)
    # Moments of semicircle(0, r): m_{2k} = C_k * r^{2k}, m_{2k+1} = 0
    # where C_k is the k-th Catalan number
    moments = np.zeros(8)
    for k in range(8):
        if k % 2 == 0:
            ck = _noncrossing_partitions_count(k // 2)
            moments[k] = ck * r**(k)
        else:
            moments[k] = 0.0
    return moments

OPERATIONS["free_convolution_additive"] = {
    "fn": free_convolution_additive,
    "input_type": "array",
    "output_type": "array",
    "description": "Moments of additive free convolution of two semicircular distributions"
}


def r_transform_semicircle(x):
    """R-transform of the semicircular distribution with variance t.
    R(z) = t*z (linear!). Evaluated at points in x.
    x[0] = variance t, rest = evaluation points.
    Input: array. Output: array."""
    t = abs(x[0]) if len(x) > 0 else 1.0
    z = x[1:] if len(x) > 1 else np.linspace(0.1, 1.0, 5)
    return t * z

OPERATIONS["r_transform_semicircle"] = {
    "fn": r_transform_semicircle,
    "input_type": "array",
    "output_type": "array",
    "description": "R-transform of semicircular distribution (R(z) = t*z)"
}


def s_transform_semicircle(x):
    """S-transform of the semicircular distribution with variance t.
    S(z) = 1 / (t * (1 + z)). Evaluated at points in x.
    x[0] = variance t, rest = evaluation points.
    Input: array. Output: array."""
    t = abs(x[0]) if len(x) > 0 else 1.0
    t = max(t, 1e-10)
    z = x[1:] if len(x) > 1 else np.linspace(0.1, 1.0, 5)
    return 1.0 / (t * (1.0 + z))

OPERATIONS["s_transform_semicircle"] = {
    "fn": s_transform_semicircle,
    "input_type": "array",
    "output_type": "array",
    "description": "S-transform of semicircular distribution"
}


def free_cumulants_from_moments(x):
    """Compute free cumulants from moments using Mobius inversion on
    noncrossing partitions. Uses the moment-cumulant formula:
    m_n = sum over noncrossing partitions pi of prod kappa_{|V|} for V in pi.
    Inverted iteratively.
    Input: array (moments m_1, m_2, ..., m_n). Output: array (free cumulants)."""
    m = x.copy()
    n = len(m)
    kappa = np.zeros(n)
    # Iterative computation using the lattice of noncrossing partitions
    # kappa_1 = m_1
    # kappa_2 = m_2 - m_1^2
    # kappa_3 = m_3 - 3*m_1*m_2 + 2*m_1^3 (for centered: m_3)
    # General: use the recurrence kappa_n = m_n - sum over nontrivial NC partitions
    # Simplified via the R-transform relation
    if n >= 1:
        kappa[0] = m[0]
    if n >= 2:
        kappa[1] = m[1] - m[0]**2
    if n >= 3:
        kappa[2] = m[2] - 3 * m[0] * m[1] + 2 * m[0]**3
    if n >= 4:
        kappa[3] = (m[3] - 4 * m[0] * m[2] - 2 * m[1]**2
                    + 10 * m[0]**2 * m[1] - 5 * m[0]**4)
    # For higher orders, use the general formula with Catalan convolution
    for k in range(4, n):
        # Approximate using Mobius function on NC lattice
        # kappa_k = m_k - sum of products of lower kappas over NC partitions
        # This is a simplified version
        kappa[k] = m[k]
        for j in range(1, k):
            kappa[k] -= _noncrossing_partitions_count(j) * kappa[j-1] * m[k-j-1] if k-j-1 < n else 0
    return kappa

OPERATIONS["free_cumulants_from_moments"] = {
    "fn": free_cumulants_from_moments,
    "input_type": "array",
    "output_type": "array",
    "description": "Free cumulants from moments via noncrossing partition Mobius inversion"
}


def moments_from_free_cumulants(x):
    """Compute moments from free cumulants using the moment-cumulant formula.
    m_n = sum over noncrossing partitions pi of prod kappa_{|V|}.
    Input: array (free cumulants kappa_1, ..., kappa_n). Output: array (moments)."""
    kappa = x.copy()
    n = len(kappa)
    m = np.zeros(n)
    if n >= 1:
        m[0] = kappa[0]
    if n >= 2:
        m[1] = kappa[1] + kappa[0]**2
    if n >= 3:
        m[2] = kappa[2] + 3 * kappa[0] * kappa[1] + kappa[0]**3
    if n >= 4:
        m[3] = (kappa[3] + 4 * kappa[0] * kappa[2] + 2 * kappa[1]**2
                + 6 * kappa[0]**2 * kappa[1] + kappa[0]**4)
    for k in range(4, n):
        m[k] = kappa[k]
        for j in range(1, k):
            m[k] += _noncrossing_partitions_count(j) * kappa[j-1] * m[k-j-1] if k-j-1 < n else 0
    return m

OPERATIONS["moments_from_free_cumulants"] = {
    "fn": moments_from_free_cumulants,
    "input_type": "array",
    "output_type": "array",
    "description": "Moments from free cumulants via noncrossing partition summation"
}


def marchenko_pastur_free(x):
    """Marchenko-Pastur distribution density at points.
    Parameters: ratio gamma = x[0], variance sigma^2 = x[1].
    Density at points x[2:].
    Input: array. Output: array."""
    gamma = abs(x[0]) if len(x) > 0 else 1.0
    gamma = max(gamma, 0.01)
    sigma2 = abs(x[1]) if len(x) > 1 else 1.0
    sigma2 = max(sigma2, 0.01)
    pts = x[2:] if len(x) > 2 else np.linspace(0.01, 4.0, 5)
    lam_minus = sigma2 * (1 - np.sqrt(gamma))**2
    lam_plus = sigma2 * (1 + np.sqrt(gamma))**2
    density = np.zeros_like(pts)
    for i, t in enumerate(pts):
        if lam_minus < t < lam_plus:
            density[i] = np.sqrt((lam_plus - t) * (t - lam_minus)) / (2 * np.pi * gamma * sigma2 * t)
    return density

OPERATIONS["marchenko_pastur_free"] = {
    "fn": marchenko_pastur_free,
    "input_type": "array",
    "output_type": "array",
    "description": "Marchenko-Pastur density at given points"
}


def voiculescu_entropy(x):
    """Voiculescu's free entropy chi for a semicircular variable with variance t.
    chi(semicircle, t) = (1/2) * log(2*pi*e*t).
    x[0] = variance t.
    Input: array. Output: scalar."""
    t = abs(x[0]) if len(x) > 0 else 1.0
    t = max(t, 1e-15)
    return 0.5 * np.log(2 * np.pi * np.e * t)

OPERATIONS["voiculescu_entropy"] = {
    "fn": voiculescu_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Voiculescu free entropy of semicircular distribution"
}


def cauchy_transform(x):
    """Cauchy transform G(z) = integral mu(dt)/(z-t) for semicircular distribution.
    For standard semicircle: G(z) = (z - sqrt(z^2 - 4)) / 2.
    x[0] = radius r, rest = complex evaluation points (real parts).
    Input: array. Output: array."""
    r = abs(x[0]) if len(x) > 0 else 2.0
    r = max(r, 0.01)
    z_real = x[1:] if len(x) > 1 else np.array([3.0, 4.0, 5.0, 6.0])
    # Add small imaginary part to stay off the real axis
    z = z_real + 0.01j
    # G(z) = (z - sqrt(z^2 - r^2)) / (r^2 / 2) -- for semicircle on [-r, r]
    # Standard: G(z) = 2*(z - sqrt(z^2 - r^2)) / r^2
    G = 2 * (z - np.sqrt(z**2 - r**2 + 0j)) / (r**2)
    return np.real(G)

OPERATIONS["cauchy_transform"] = {
    "fn": cauchy_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Cauchy/Stieltjes transform of semicircular distribution"
}


def stieltjes_transform(x):
    """Stieltjes transform m(z) = integral mu(dt)/(t-z) = -G(z) for measure mu.
    For Marchenko-Pastur with gamma=1: m(z) = (1 - z - sqrt((z-1)^2-4z)) / (2z).
    Evaluated at x (real parts, shifted to upper half plane).
    Input: array. Output: array."""
    pts = x if len(x) > 0 else np.array([5.0, 6.0, 7.0])
    z = pts + 0.1j  # upper half plane
    # Marchenko-Pastur gamma=1, sigma=1: support [0, 4]
    # m(z) = (-(z-1) + sqrt((z-1)^2 - 4)) / (2*z) ... using standard form
    # Actually G(z) = (z - 1 - sqrt((z-1)^2 - 4)) / (2*z) picks correct branch
    disc = (z - 1)**2 - 4
    sqrt_disc = np.sqrt(disc + 0j)
    # Choose branch with Im(m) > 0 for z in upper half plane
    m = (-(z - 1) + sqrt_disc) / (2.0)
    # Correct branch: Im(m(z)) should have same sign as Im(z)
    for i in range(len(m)):
        if np.imag(m[i]) * np.imag(z[i]) < 0:
            m[i] = (-(z[i] - 1) - sqrt_disc[i]) / 2.0
    return np.real(m)

OPERATIONS["stieltjes_transform"] = {
    "fn": stieltjes_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Stieltjes transform of Marchenko-Pastur distribution"
}


def free_poisson_moments(x):
    """Moments of the free Poisson (Marchenko-Pastur) distribution.
    m_n = sum_{k=1}^{n} (1/k) * C(n,k) * C(n-1,k-1) * lambda^k.
    These are the Narayana polynomials evaluated at lambda.
    x[0] = lambda (rate parameter), x[1] = number of moments.
    Input: array. Output: array."""
    lam = abs(x[0]) if len(x) > 0 else 1.0
    num = int(x[1]) if len(x) > 1 else min(8, max(len(x), 5))
    num = max(1, min(num, 20))
    from math import comb
    moments = np.zeros(num)
    for n in range(num):
        # m_{n+1} = sum_{k=0}^{n} Narayana(n+1, k+1) * lam^{k+1}
        # Narayana(n, k) = (1/n) * C(n, k) * C(n, k-1)
        nn = n + 1  # 1-based moment index
        s = 0.0
        for k in range(1, nn + 1):
            narayana = comb(nn, k) * comb(nn, k - 1) / nn
            s += narayana * lam**k
        moments[n] = s
    return moments

OPERATIONS["free_poisson_moments"] = {
    "fn": free_poisson_moments,
    "input_type": "array",
    "output_type": "array",
    "description": "Moments of free Poisson distribution via Narayana numbers"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
