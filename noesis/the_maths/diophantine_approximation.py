"""
Diophantine Approximation — Liouville's theorem, irrationality measure, three-distance theorem

Connects to: [number_theory, continued_fractions, ergodic_theory, dynamical_systems]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "diophantine_approximation"
OPERATIONS = {}


def best_rational_approximation(x):
    """Find best rational approximation p/q for each element via continued fractions.
    Input: array. Output: matrix (each row is [p, q])."""
    results = []
    max_iter = 30
    for val in np.asarray(x).ravel():
        # Continued fraction convergents
        a = float(val)
        p_prev, p_curr = 0, 1
        q_prev, q_curr = 1, 0
        best_p, best_q = round(a), 1
        for _ in range(max_iter):
            ai = int(np.floor(a))
            p_prev, p_curr = p_curr, ai * p_curr + p_prev
            q_prev, q_curr = q_curr, ai * q_curr + q_prev
            if q_curr > 1000:
                break
            best_p, best_q = p_curr, q_curr
            frac = a - ai
            if abs(frac) < 1e-12:
                break
            a = 1.0 / frac
        results.append([best_p, best_q])
    return np.array(results, dtype=np.float64)


OPERATIONS["best_rational_approximation"] = {
    "fn": best_rational_approximation,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Best rational approximation p/q via continued fraction convergents"
}


def irrationality_measure_estimate(x):
    """Estimate irrationality measure mu by checking |x - p/q| vs 1/q^mu.
    Input: array. Output: array."""
    results = []
    for val in np.asarray(x).ravel():
        # Check convergents and estimate mu from |val - p/q| ~ 1/q^mu
        a = float(val)
        p_prev, p_curr = 0, 1
        q_prev, q_curr = 1, 0
        mus = []
        orig_a = a
        for _ in range(40):
            ai = int(np.floor(a))
            p_prev, p_curr = p_curr, ai * p_curr + p_prev
            q_prev, q_curr = q_curr, ai * q_curr + q_prev
            if q_curr > 1:
                err = abs(orig_a - p_curr / q_curr)
                if err > 1e-15:
                    mu_est = -np.log(err) / np.log(q_curr)
                    mus.append(mu_est)
            frac = a - ai
            if abs(frac) < 1e-14:
                break
            a = 1.0 / frac
        results.append(max(mus) if mus else 2.0)
    return np.array(results)


OPERATIONS["irrationality_measure_estimate"] = {
    "fn": irrationality_measure_estimate,
    "input_type": "array",
    "output_type": "array",
    "description": "Estimate irrationality measure from continued fraction convergents"
}


def three_distance_gaps(x):
    """Compute the three-distance (Steinhaus) theorem gaps for n*alpha mod 1.
    Input: array (first element = alpha, rest = n values). Output: array of gap counts."""
    arr = np.asarray(x).ravel()
    alpha = arr[0]
    results = []
    for n_val in arr[1:]:
        n = max(int(n_val), 2)
        points = np.sort(np.mod(np.arange(1, n + 1) * alpha, 1.0))
        points = np.concatenate(([0.0], points, [1.0]))
        gaps = np.diff(points)
        # Round to group distinct gap lengths
        unique_gaps = np.unique(np.round(gaps, decimals=10))
        results.append(len(unique_gaps))
    return np.array(results, dtype=np.float64)


OPERATIONS["three_distance_gaps"] = {
    "fn": three_distance_gaps,
    "input_type": "array",
    "output_type": "array",
    "description": "Count distinct gap lengths in n*alpha mod 1 (Steinhaus/three-distance theorem)"
}


def liouville_number_approx(x):
    """Compute partial sums of the Liouville constant L = sum(10^{-k!}).
    Input: array (number of terms for each element). Output: array."""
    results = []
    for val in np.asarray(x).ravel():
        n = max(int(val), 1)
        n = min(n, 20)  # avoid overflow
        s = 0.0
        for k in range(1, n + 1):
            factorial_k = 1
            for j in range(1, k + 1):
                factorial_k *= j
            s += 10.0 ** (-factorial_k)
        results.append(s)
    return np.array(results)


OPERATIONS["liouville_number_approx"] = {
    "fn": liouville_number_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Partial sums of Liouville constant sum(10^{-k!})"
}


def markov_spectrum_first(x):
    """Return the first few Markov constants sqrt(9 - 4/m_i^2) / m_i.
    Input: array (number of constants per element). Output: array."""
    # Markov numbers: 1, 2, 5, 13, 29, 34, 89, 169, 194, ...
    markov_numbers = [1, 2, 5, 13, 29, 34, 89, 169, 194, 233, 433, 610, 985]
    results = []
    for val in np.asarray(x).ravel():
        n = max(int(val), 1)
        n = min(n, len(markov_numbers))
        # Lagrange spectrum values: sqrt(9 - 4/m^2) for Markov number m
        vals = [np.sqrt(9.0 - 4.0 / (m * m)) for m in markov_numbers[:n]]
        results.extend(vals)
    return np.array(results)


OPERATIONS["markov_spectrum_first"] = {
    "fn": markov_spectrum_first,
    "input_type": "array",
    "output_type": "array",
    "description": "First entries of the Markov spectrum sqrt(9 - 4/m^2)"
}


def hurwitz_constant_check(x):
    """Check Hurwitz's theorem: for each irrational x, there exist infinitely many
    p/q with |x - p/q| < 1/(sqrt(5)*q^2). Returns the minimum ratio found.
    Input: array. Output: array."""
    results = []
    for val in np.asarray(x).ravel():
        a = float(val)
        p_prev, p_curr = 0, 1
        q_prev, q_curr = 1, 0
        min_ratio = float('inf')
        orig_a = a
        for _ in range(50):
            ai = int(np.floor(a))
            p_prev, p_curr = p_curr, ai * p_curr + p_prev
            q_prev, q_curr = q_curr, ai * q_curr + q_prev
            if q_curr > 0:
                err = abs(orig_a - p_curr / q_curr)
                ratio = err * np.sqrt(5) * q_curr * q_curr
                if ratio < min_ratio:
                    min_ratio = ratio
            frac = a - ai
            if abs(frac) < 1e-14:
                break
            a = 1.0 / frac
        results.append(min_ratio)
    return np.array(results)


OPERATIONS["hurwitz_constant_check"] = {
    "fn": hurwitz_constant_check,
    "input_type": "array",
    "output_type": "array",
    "description": "Minimum of |x - p/q| * sqrt(5) * q^2 over convergents (Hurwitz theorem check)"
}


def badly_approximable_test(x):
    """Test if numbers are badly approximable by checking if continued fraction
    partial quotients are bounded. Returns max partial quotient found.
    Input: array. Output: array."""
    results = []
    for val in np.asarray(x).ravel():
        a = float(val)
        max_pq = 0
        for _ in range(60):
            ai = int(np.floor(a))
            if ai > max_pq:
                max_pq = ai
            frac = a - ai
            if abs(frac) < 1e-14:
                break
            a = 1.0 / frac
            if a > 1e12:
                break
        results.append(float(max_pq))
    return np.array(results)


OPERATIONS["badly_approximable_test"] = {
    "fn": badly_approximable_test,
    "input_type": "array",
    "output_type": "array",
    "description": "Max partial quotient in CF expansion (bounded => badly approximable)"
}


def discrepancy_sequence(x):
    """Compute star discrepancy D*_N of the sequence {n*alpha mod 1} for each alpha.
    Input: array (alphas). Output: array (discrepancies for N=100)."""
    N = 100
    results = []
    for alpha in np.asarray(x).ravel():
        points = np.sort(np.mod(np.arange(1, N + 1) * alpha, 1.0))
        # D*_N = sup |F_N(x) - x|
        ivals = np.arange(1, N + 1) / N
        disc = max(np.max(np.abs(ivals - points)),
                    np.max(np.abs((ivals - 1.0 / N) - points)))
        results.append(disc)
    return np.array(results)


OPERATIONS["discrepancy_sequence"] = {
    "fn": discrepancy_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "Star discrepancy of {n*alpha mod 1} sequence for N=100"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
