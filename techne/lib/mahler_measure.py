"""TOOL_MAHLER_MEASURE — Mahler measure of a polynomial.

The Mahler measure M(p) of a polynomial p(x) = a_n * prod(x - alpha_i) is:
    M(p) = |a_n| * prod(max(1, |alpha_i|))

Equivalently: exp(integral_0^1 log|p(e^{2*pi*i*t})| dt)

For integer polynomials, M(p) >= 1, and Lehmer's conjecture asserts
M(p) > 1.17628... for any non-cyclotomic polynomial with M(p) > 1.

Interface:
    mahler_measure(coefficients) -> float
    is_cyclotomic(coefficients) -> bool
    log_mahler_measure(coefficients) -> float

Forged: 2026-04-21 | Tier: 1 (Python/numpy) | REQ-001
Tested against: Mossinghoff's list of known small Mahler measures
"""
import numpy as np


def mahler_measure(coefficients: list) -> float:
    """Compute the Mahler measure of a polynomial from its coefficients.

    Parameters
    ----------
    coefficients : list of int or float
        Polynomial coefficients in descending degree order: [a_n, ..., a_1, a_0]
        (numpy convention). For ascending order, reverse first.

    Returns
    -------
    float
        The Mahler measure M(p). Always >= 0. Returns |a_0| if degree 0.

    Raises
    ------
    ValueError
        If coefficients is empty or all zeros.
    """
    coeffs = np.array(coefficients, dtype=np.complex128)
    # Strip leading zeros
    nonzero = np.nonzero(coeffs)[0]
    if len(nonzero) == 0:
        raise ValueError("Zero polynomial has no Mahler measure")
    coeffs = coeffs[nonzero[0]:]

    if len(coeffs) == 1:
        return abs(float(coeffs[0]))

    roots = np.roots(coeffs)
    leading = abs(coeffs[0])
    return float(leading * np.prod(np.maximum(1.0, np.abs(roots))))


def log_mahler_measure(coefficients: list) -> float:
    """Compute log(M(p)), the logarithmic Mahler measure.

    This is the more natural quantity for theoretical work:
    m(p) = log(M(p)) = log|a_n| + sum(max(0, log|alpha_i|))
    """
    m = mahler_measure(coefficients)
    if m <= 0:
        return float('-inf')
    return float(np.log(m))


def is_cyclotomic(coefficients: list, tol: float = 1e-10) -> bool:
    """Test whether a polynomial is cyclotomic (all roots on unit circle).

    Cyclotomic polynomials have M(p) = 1 exactly. This is a numerical
    test with tolerance `tol` on root moduli.

    Returns False for constant polynomials.
    """
    coeffs = np.array(coefficients, dtype=np.complex128)
    nonzero = np.nonzero(coeffs)[0]
    if len(nonzero) == 0 or len(coeffs) <= 1:
        return False
    coeffs = coeffs[nonzero[0]:]
    if len(coeffs) <= 1:
        return False

    roots = np.roots(coeffs)
    return bool(np.all(np.abs(np.abs(roots) - 1.0) < tol))


if __name__ == "__main__":
    # Quick smoke test with known values
    # x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1 (Lehmer's polynomial)
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    m = mahler_measure(lehmer)
    print(f"Lehmer polynomial M(p) = {m:.10f}")
    print(f"  Expected:             1.1762808183...")
    print(f"  Cyclotomic: {is_cyclotomic(lehmer)}")

    # Cyclotomic: x^4 + x^3 + x^2 + x + 1 = Phi_5
    phi5 = [1, 1, 1, 1, 1]
    print(f"\nPhi_5 M(p) = {mahler_measure(phi5):.10f}")
    print(f"  Expected: 1.0000000000")
    print(f"  Cyclotomic: {is_cyclotomic(phi5)}")

    # x^2 - x - 1 (golden ratio polynomial)
    golden = [1, -1, -1]
    print(f"\nGolden ratio poly M(p) = {mahler_measure(golden):.10f}")
    print(f"  Expected:              1.6180339887...")
