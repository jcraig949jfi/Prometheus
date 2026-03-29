"""
Causal Set Theory — Spacetime as discrete poset with causal order

Connects to: [pseudo_riemannian, spin_foam, noncommutative_geometry_connes]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "causal_set_theory"
OPERATIONS = {}


def poisson_sprinkling(x):
    """Generate a Poisson sprinkling of points in a causal diamond.
    Input: array where x[0]=density parameter. Output: array of sprinkled point coordinates (1D times).
    Uses density * len(x) as the expected number of points."""
    density = max(x[0], 1.0)
    n_points = int(density * len(x))
    np.random.seed(42)
    points = np.sort(np.random.uniform(0, 1, n_points))
    return points


OPERATIONS["poisson_sprinkling"] = {
    "fn": poisson_sprinkling,
    "input_type": "array",
    "output_type": "array",
    "description": "Poisson sprinkling of points in a 1D causal interval"
}


def causal_matrix_construct(x):
    """Construct causal matrix C_{ij} = 1 if x_i < x_j (causal relation in 1D).
    Input: array of event times. Output: array (flattened causal matrix)."""
    n = len(x)
    C = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if x[i] < x[j]:
                C[i, j] = 1.0
    return C.flatten()


OPERATIONS["causal_matrix_construct"] = {
    "fn": causal_matrix_construct,
    "input_type": "array",
    "output_type": "array",
    "description": "Construct causal order matrix from event times"
}


def benincasa_dowker_action(x):
    """Compute the Benincasa-Dowker action for a causal set.
    Input: array of event times (sorted). Output: scalar action.
    S_BD = N - (2/sqrt(6)) * sum of causal interval counts.
    Simplified 2D version: S = N - alpha * sum_{i<j} (n_ij choose 0) where n_ij = elements between i,j."""
    n = len(x)
    sorted_x = np.sort(x)
    # Count causal intervals: number of elements between each pair
    action = float(n)
    alpha = 2.0 / np.sqrt(6.0)
    for i in range(n):
        for j in range(i + 1, n):
            # Number of points strictly between i and j in causal order
            n_between = j - i - 1
            # BD action correction: (-1)^0 * C(n_between, 0) = 1 for links,
            # (-1)^1 * C(n_between, 1) for 2-chains, etc. (truncated at order 3 for 2D)
            correction = 1.0
            if n_between >= 1:
                correction -= n_between
            if n_between >= 2:
                correction += n_between * (n_between - 1) / 2.0
            if n_between >= 3:
                correction -= n_between * (n_between - 1) * (n_between - 2) / 6.0
            action -= alpha * correction
    return np.float64(action)


OPERATIONS["benincasa_dowker_action"] = {
    "fn": benincasa_dowker_action,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Benincasa-Dowker action for a 1D causal set"
}


def dimension_estimate_myrheim_meyer(x):
    """Estimate dimension using Myrheim-Meyer method: d from <f> = C_d / 2^d.
    Input: array of event times. Output: scalar estimated dimension.
    f = fraction of causally related pairs. For 1D, f ~ 1/2 -> d ~ 1."""
    n = len(x)
    if n < 2:
        return np.float64(1.0)
    # Count causally related pairs (i < j in time order)
    sorted_x = np.sort(x)
    total_pairs = n * (n - 1) / 2.0
    # In 1D all pairs are causally related after sorting
    # For a sprinkling in d-dim Alexandrov set: <r> = (Gamma(d+1)Gamma(d/2))/(4*Gamma(3d/2))
    # Ordering fraction r for a random sprinkling in d-dim flat spacetime
    # r_d = d! * Gamma(d/2) / (4 * Gamma(3d/2))
    # For general input, compute ordering fraction
    causal_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            if x[j] > x[i]:
                causal_pairs += 1
    r = causal_pairs / total_pairs if total_pairs > 0 else 0.5
    # Invert r_d relation numerically (search over d from 1 to 10)
    from scipy.special import gamma as gammafn
    best_d = 1.0
    best_err = float('inf')
    for d_test in np.linspace(0.5, 10.0, 100):
        try:
            r_theory = (gammafn(d_test + 1) * gammafn(d_test / 2.0)) / (4.0 * gammafn(3 * d_test / 2.0))
            err = abs(r - r_theory)
            if err < best_err:
                best_err = err
                best_d = d_test
        except Exception:
            continue
    return np.float64(best_d)


OPERATIONS["dimension_estimate_myrheim_meyer"] = {
    "fn": dimension_estimate_myrheim_meyer,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Myrheim-Meyer dimension estimator from ordering fraction"
}


def longest_chain_length(x):
    """Find the longest chain (totally ordered subset) in the causal set.
    Input: array of event times. Output: scalar length of longest chain.
    In 1D with distinct times, this is just n."""
    sorted_x = np.sort(x)
    # In 1D, longest chain = number of distinct elements
    unique = np.unique(sorted_x)
    return np.float64(len(unique))


OPERATIONS["longest_chain_length"] = {
    "fn": longest_chain_length,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Length of the longest causal chain in the set"
}


def causal_interval_count(x):
    """Count number of elements in each causal interval [x_i, x_j].
    Input: array of event times. Output: array of interval sizes for consecutive pairs."""
    sorted_x = np.sort(x)
    n = len(sorted_x)
    intervals = np.zeros(max(n - 1, 1))
    for i in range(n - 1):
        # Count points between consecutive events
        count = 0
        for k in range(n):
            if sorted_x[i] < sorted_x[k] < sorted_x[i + 1]:
                count += 1
        intervals[i] = count
    return intervals


OPERATIONS["causal_interval_count"] = {
    "fn": causal_interval_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Count elements in each consecutive causal interval"
}


def d_alembertian_causal_set(x):
    """Discrete d'Alembertian operator on a causal set in 1D.
    Input: array of field values at causal set points. Output: array of d'Alembertian applied.
    Uses the Sorkin prescription: Box phi(x) ~ sum of coefficients * phi at neighbors."""
    n = len(x)
    result = np.zeros(n)
    # 1D causal set d'Alembertian approximation (second derivative)
    if n >= 3:
        for i in range(1, n - 1):
            result[i] = x[i + 1] - 2 * x[i] + x[i - 1]
    # Boundary: forward/backward difference
    if n >= 2:
        result[0] = x[1] - x[0]
        result[-1] = x[-1] - x[-2]
    return result


OPERATIONS["d_alembertian_causal_set"] = {
    "fn": d_alembertian_causal_set,
    "input_type": "array",
    "output_type": "array",
    "description": "Discrete d'Alembertian on a 1D causal set (Sorkin prescription)"
}


def causal_set_geodesic_distance(x):
    """Estimate geodesic distance in a causal set.
    Input: array of event times. Output: scalar (longest chain length * fundamental length).
    In causal set theory, geodesic distance ~ longest chain * l_fundamental."""
    sorted_x = np.sort(x)
    n = len(sorted_x)
    if n < 2:
        return np.float64(0.0)
    # Geodesic distance estimate: longest chain * (V/N)^{1/d}
    # For 1D: total range * correction
    chain_length = n  # In 1D, all points form the chain
    volume = sorted_x[-1] - sorted_x[0]
    l_fund = volume / n  # fundamental length scale
    distance = chain_length * l_fund
    return np.float64(distance)


OPERATIONS["causal_set_geodesic_distance"] = {
    "fn": causal_set_geodesic_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Geodesic distance estimate from longest chain and fundamental length"
}


def sprinkling_density(x):
    """Compute the sprinkling density (points per unit volume) of a causal set.
    Input: array of event positions. Output: scalar density."""
    n = len(x)
    if n < 2:
        return np.float64(float(n))
    volume = np.max(x) - np.min(x)
    if volume < 1e-15:
        return np.float64(float(n))
    density = n / volume
    return np.float64(density)


OPERATIONS["sprinkling_density"] = {
    "fn": sprinkling_density,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Compute sprinkling density N/V of the causal set"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
