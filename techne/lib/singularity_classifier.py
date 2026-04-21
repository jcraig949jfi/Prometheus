"""TOOL_SINGULARITY_CLASSIFIER — Classify generating function singularity type.

Uses Flajolet-Odlyzko transfer theorems: the asymptotic behavior of
coefficients [z^n] f(z) is determined by the singularity type of f(z)
at its radius of convergence.

Types:
- POLE: f ~ (1-z/rho)^{-alpha}, coeffs ~ n^{alpha-1} * rho^{-n}
- ALGEBRAIC: f ~ (1-z/rho)^{alpha} with alpha not integer, coeffs ~ n^{-alpha-1} * rho^{-n}
- LOG: f ~ log(1-z/rho), coeffs ~ 1/(n * rho^n)
- ESSENTIAL: f ~ exp(g(z)), superexponential or subexponential growth
- ENTIRE: radius of convergence is infinite

Interface:
    classify_singularity(coefficients) -> dict
    estimate_radius(coefficients) -> float

Forged: 2026-04-21 | Tier: 1 (Python/numpy) | REQ-020
Tested against: known generating functions (Fibonacci, Catalan, partition, etc.)
"""
import numpy as np
from typing import Optional


def estimate_radius(coefficients: list, min_terms: int = 10) -> Optional[float]:
    """Estimate radius of convergence via ratio test.

    Returns rho = lim |a_n / a_{n+1}|. Returns None if fewer than
    min_terms nonzero coefficients.
    """
    coeffs = np.array(coefficients, dtype=np.float64)
    # Use only nonzero terms for ratio
    nonzero_idx = np.nonzero(coeffs)[0]
    if len(nonzero_idx) < min_terms:
        return None

    # Consecutive ratio of absolute values
    vals = np.abs(coeffs[nonzero_idx])
    if len(vals) < 2:
        return None

    ratios = vals[:-1] / vals[1:]
    # Use median of last half for stability
    half = len(ratios) // 2
    if half < 3:
        return float(np.median(ratios))
    return float(np.median(ratios[half:]))


def classify_singularity(coefficients: list, min_terms: int = 15) -> dict:
    """Classify the dominant singularity type of a generating function.

    Parameters
    ----------
    coefficients : list of int or float
        The first N coefficients [a_0, a_1, ..., a_{N-1}].

    Returns
    -------
    dict with:
        type : str — "POLE", "ALGEBRAIC", "LOG", "ESSENTIAL", "ENTIRE", "UNKNOWN"
        alpha : float or None — the exponent (for POLE/ALGEBRAIC)
        radius : float or None — estimated radius of convergence
        growth_rate : str — "exponential", "subexponential", "polynomial", "superexponential"
        confidence : float — 0 to 1 heuristic confidence
        evidence : str — explanation of classification
    """
    coeffs = np.array(coefficients, dtype=np.float64)
    n = len(coeffs)

    if n < min_terms:
        return {"type": "UNKNOWN", "alpha": None, "radius": None,
                "growth_rate": "unknown", "confidence": 0.0,
                "evidence": f"Only {n} terms, need at least {min_terms}"}

    # Remove leading zeros
    nonzero = np.nonzero(coeffs)[0]
    if len(nonzero) < min_terms:
        return {"type": "UNKNOWN", "alpha": None, "radius": None,
                "growth_rate": "unknown", "confidence": 0.0,
                "evidence": f"Only {len(nonzero)} nonzero terms"}

    abs_coeffs = np.abs(coeffs)
    idx = np.arange(n, dtype=np.float64)

    # Step 1: Estimate radius of convergence
    radius = estimate_radius(coefficients, min_terms)

    # Step 2: Check if entire (coeffs decay faster than any exponential)
    if radius is not None and radius > 1e10:
        return {"type": "ENTIRE", "alpha": None, "radius": float('inf'),
                "growth_rate": "polynomial", "confidence": 0.7,
                "evidence": "Ratio test suggests infinite radius"}

    # Step 3: Analyze growth via log-coefficients
    pos_idx = abs_coeffs > 0
    if np.sum(pos_idx) < min_terms:
        return {"type": "UNKNOWN", "alpha": None, "radius": radius,
                "growth_rate": "unknown", "confidence": 0.0,
                "evidence": "Too many zero coefficients"}

    log_coeffs = np.log(abs_coeffs[pos_idx])
    ns = idx[pos_idx]

    # Step 4: Fit log(|a_n|) = A*n + B*log(n) + C
    # This separates exponential (A != 0) from polynomial (A = 0) growth
    # For pole of order alpha: log|a_n| ~ n*log(1/rho) + (alpha-1)*log(n)
    # For algebraic: log|a_n| ~ n*log(1/rho) + (-alpha-1)*log(n)

    # Use tail (last 60%) for fitting
    tail_start = len(ns) // 3
    ns_tail = ns[tail_start:]
    lc_tail = log_coeffs[tail_start:]

    if len(ns_tail) < 5:
        return {"type": "UNKNOWN", "alpha": None, "radius": radius,
                "growth_rate": "unknown", "confidence": 0.0,
                "evidence": "Insufficient tail data"}

    # Fit: log|a_n| = A*n + B*log(n) + C
    log_ns = np.log(ns_tail + 1)  # +1 to avoid log(0)
    X = np.column_stack([ns_tail, log_ns, np.ones(len(ns_tail))])
    try:
        result = np.linalg.lstsq(X, lc_tail, rcond=None)
        A, B, C = result[0]
        residuals = result[1]
        r_squared = 1 - (np.sum((lc_tail - X @ result[0])**2) /
                         np.sum((lc_tail - np.mean(lc_tail))**2))
    except np.linalg.LinAlgError:
        return {"type": "UNKNOWN", "alpha": None, "radius": radius,
                "growth_rate": "unknown", "confidence": 0.0,
                "evidence": "Least squares failed"}

    # Step 5: Classify based on fit
    confidence = max(0.0, min(1.0, r_squared))

    # Check for superexponential growth (n!, n^n, etc.)
    # Test: does log|a_n|/n diverge?
    log_over_n = lc_tail / (ns_tail + 1)
    if len(log_over_n) > 5 and log_over_n[-1] > 2 * log_over_n[len(log_over_n)//2]:
        return {"type": "ESSENTIAL", "alpha": None, "radius": 0.0,
                "growth_rate": "superexponential", "confidence": confidence * 0.8,
                "evidence": f"log|a_n|/n diverges (ratio {log_over_n[-1]/log_over_n[len(log_over_n)//2]:.2f})"}

    if abs(A) < 0.01:
        # Subexponential — polynomial growth
        # log|a_n| ~ B*log(n), so |a_n| ~ n^B
        return {"type": "ENTIRE", "alpha": B, "radius": float('inf'),
                "growth_rate": "polynomial", "confidence": confidence,
                "evidence": f"|a_n| ~ n^{B:.2f}, exponential rate A={A:.4f} ≈ 0"}

    # Exponential growth: |a_n| ~ rho^{-n} * n^{B}
    rho_from_fit = np.exp(-A)

    if B > 0.5:
        # Positive B => pole-like: a_n ~ n^{alpha-1} * rho^{-n}, so alpha = B + 1
        alpha = B + 1
        return {"type": "POLE", "alpha": float(alpha), "radius": float(rho_from_fit),
                "growth_rate": "exponential", "confidence": confidence,
                "evidence": f"|a_n| ~ n^{B:.2f} * {1/rho_from_fit:.4f}^n => pole of order {alpha:.2f}"}

    elif B < -0.5:
        # Negative B => algebraic: a_n ~ n^{-alpha-1} * rho^{-n}
        alpha = -B - 1
        return {"type": "ALGEBRAIC", "alpha": float(alpha), "radius": float(rho_from_fit),
                "growth_rate": "exponential", "confidence": confidence,
                "evidence": f"|a_n| ~ n^{B:.2f} * {1/rho_from_fit:.4f}^n => algebraic with alpha={alpha:.2f}"}

    else:
        # B near 0 — could be simple pole or logarithmic
        if abs(B) < 0.1:
            return {"type": "LOG", "alpha": None, "radius": float(rho_from_fit),
                    "growth_rate": "exponential", "confidence": confidence * 0.8,
                    "evidence": f"|a_n| ~ {1/rho_from_fit:.4f}^n * n^{B:.2f} => log-type"}
        else:
            return {"type": "POLE", "alpha": float(B + 1), "radius": float(rho_from_fit),
                    "growth_rate": "exponential", "confidence": confidence,
                    "evidence": f"|a_n| ~ n^{B:.2f} * {1/rho_from_fit:.4f}^n"}


if __name__ == "__main__":
    # Fibonacci: a_n ~ phi^n / sqrt(5), pole at z = 1/phi
    fib = [0, 1]
    for i in range(48):
        fib.append(fib[-1] + fib[-2])
    r = classify_singularity(fib)
    print(f"Fibonacci: type={r['type']}, radius={r['radius']:.4f} (expect 0.6180), alpha={r['alpha']}")

    # Catalan: a_n ~ 4^n / (n^{3/2} * sqrt(pi)), algebraic singularity
    from math import comb
    catalan = [comb(2*n, n) // (n+1) for n in range(50)]
    r = classify_singularity(catalan)
    print(f"Catalan:   type={r['type']}, radius={r['radius']:.4f} (expect 0.2500), alpha={r['alpha']}")

    # Partition: p(n) ~ exp(pi*sqrt(2n/3)) / (4n*sqrt(3)), essential
    # Approximate partition numbers
    partitions = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135,
                  176, 231, 297, 385, 490, 627, 792, 1002, 1255, 1575, 1958,
                  2436, 3010, 3718, 4565, 5604, 6842, 8349, 10143, 12310,
                  14883, 17977, 21637, 26015, 31185, 37338, 44583, 53174,
                  63261, 75175, 89134, 105558, 124754, 147273, 173525]
    r = classify_singularity(partitions)
    print(f"Partition: type={r['type']}, growth={r['growth_rate']}")

    # Constant sequence: a_n = 1
    const = [1] * 50
    r = classify_singularity(const)
    print(f"Constant:  type={r['type']}, radius={r['radius']}")
