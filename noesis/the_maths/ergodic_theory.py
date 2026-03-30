"""
Ergodic Theory — Birkhoff averages, mixing coefficients, entropy rate

Connects to: [dynamical_systems, information_theory, measure_theory, probability_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "ergodic_theory"
OPERATIONS = {}


def birkhoff_average(x):
    """Compute Birkhoff time average of an observable along an orbit.
    Input: array (orbit values). Output: scalar."""
    return np.mean(x)


OPERATIONS["birkhoff_average"] = {
    "fn": birkhoff_average,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Birkhoff ergodic average of observable values along an orbit"
}


def time_average(x):
    """Cumulative time average (running mean) of an orbit.
    Input: array. Output: array."""
    return np.cumsum(x) / np.arange(1, len(x) + 1)


OPERATIONS["time_average"] = {
    "fn": time_average,
    "input_type": "array",
    "output_type": "array",
    "description": "Running time average showing convergence of Birkhoff average"
}


def space_average(x):
    """Space (ensemble) average — weighted mean using invariant measure estimate.
    For ergodic systems this equals the time average. Input: array. Output: scalar."""
    # Estimate invariant density via histogram, then compute weighted average
    n_bins = max(5, len(x) // 5)
    counts, bin_edges = np.histogram(x, bins=n_bins, density=True)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    bin_width = bin_edges[1] - bin_edges[0]
    # Space average = integral of x * rho(x) dx
    return float(np.sum(bin_centers * counts * bin_width))


OPERATIONS["space_average"] = {
    "fn": space_average,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Space average using estimated invariant measure density"
}


def mixing_coefficient(x):
    """Estimate mixing coefficient via autocorrelation decay rate.
    Input: array (time series). Output: scalar (decay rate)."""
    x_centered = x - np.mean(x)
    var = np.var(x)
    if var < 1e-15:
        return 0.0
    n = len(x_centered)
    max_lag = min(n // 2, 50)
    autocorr = np.array([
        np.mean(x_centered[:n - lag] * x_centered[lag:]) / var
        for lag in range(1, max_lag + 1)
    ])
    # Find decay rate by fitting log of absolute autocorrelation
    abs_ac = np.abs(autocorr)
    valid = abs_ac > 1e-10
    if np.sum(valid) < 2:
        return float('inf')  # Very fast mixing
    lags = np.arange(1, max_lag + 1)[valid]
    log_ac = np.log(abs_ac[valid])
    # Linear fit: log|C(lag)| ~ -alpha * lag
    coeffs = np.polyfit(lags, log_ac, 1)
    return float(-coeffs[0])


OPERATIONS["mixing_coefficient"] = {
    "fn": mixing_coefficient,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Autocorrelation decay rate estimating mixing strength"
}


def ergodic_decomposition_entropy(x):
    """Entropy of the ergodic decomposition estimated from orbit data.
    Input: array. Output: scalar."""
    # Partition orbit into bins and compute entropy of visit frequencies
    n_bins = max(5, int(np.sqrt(len(x))))
    counts, _ = np.histogram(x, bins=n_bins)
    probs = counts / np.sum(counts)
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs)))


OPERATIONS["ergodic_decomposition_entropy"] = {
    "fn": ergodic_decomposition_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of the ergodic decomposition visit distribution"
}


def recurrence_time(x):
    """Estimate mean recurrence time to initial region.
    Input: array (orbit). Output: scalar."""
    if len(x) < 2:
        return 1.0
    # Define "initial region" as within epsilon of x[0]
    epsilon = (np.max(x) - np.min(x)) * 0.1 + 1e-15
    recurrences = np.where(np.abs(x[1:] - x[0]) < epsilon)[0] + 1
    if len(recurrences) == 0:
        return float(len(x))
    # Mean first-return times
    diffs = np.diff(np.concatenate([[0], recurrences]))
    return float(np.mean(diffs))


OPERATIONS["recurrence_time"] = {
    "fn": recurrence_time,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Mean Poincare recurrence time to initial region"
}


def poincare_recurrence_estimate(x):
    """Estimate Poincare recurrence time distribution.
    Input: array (orbit). Output: array (recurrence times)."""
    if len(x) < 3:
        return np.array([1.0])
    epsilon = (np.max(x) - np.min(x)) * 0.1 + 1e-15
    # For each point, find next recurrence
    recurrence_times = []
    for i in range(len(x) - 1):
        hits = np.where(np.abs(x[i + 1:] - x[i]) < epsilon)[0]
        if len(hits) > 0:
            recurrence_times.append(hits[0] + 1)
    if len(recurrence_times) == 0:
        return np.array([float(len(x))])
    return np.array(recurrence_times, dtype=float)


OPERATIONS["poincare_recurrence_estimate"] = {
    "fn": poincare_recurrence_estimate,
    "input_type": "array",
    "output_type": "array",
    "description": "Distribution of Poincare recurrence times across the orbit"
}


def kolmogorov_sinai_entropy_approx(x):
    """Approximate Kolmogorov-Sinai entropy via correlation integral method.
    Input: array (time series). Output: scalar."""
    n = len(x)
    if n < 10:
        return 0.0
    # Embedding dimension 2
    m = 2
    embedded = np.array([x[i:i + m] for i in range(n - m)])
    n_pts = len(embedded)
    # Compute correlation integrals at two scales
    epsilons = []
    C_eps = []
    data_range = np.max(x) - np.min(x) + 1e-15
    for scale in [0.1, 0.2]:
        eps = data_range * scale
        dists = np.abs(embedded[:, None, :] - embedded[None, :, :]).max(axis=2)
        count = np.sum(dists < eps) - n_pts  # exclude self-pairs
        C_eps.append(count / (n_pts * (n_pts - 1)))
        epsilons.append(eps)
    C_eps = np.array(C_eps)
    epsilons = np.array(epsilons)
    valid = C_eps > 1e-15
    if np.sum(valid) < 2:
        return 0.0
    # h_KS ~ log(C(eps1)/C(eps2)) / (eps difference) in correlation dimension approach
    h = (np.log(C_eps[1]) - np.log(C_eps[0])) / (np.log(epsilons[1]) - np.log(epsilons[0]))
    return float(max(0.0, h))


OPERATIONS["kolmogorov_sinai_entropy_approx"] = {
    "fn": kolmogorov_sinai_entropy_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate KS entropy via correlation integral scaling"
}


def rotation_ergodic_average(x):
    """Ergodic average for irrational rotation on the circle.
    Treats x as angles (mod 2pi) and computes average of cos(x).
    Input: array (angles). Output: scalar."""
    return float(np.mean(np.cos(x)))


OPERATIONS["rotation_ergodic_average"] = {
    "fn": rotation_ergodic_average,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Ergodic average of cosine observable for circle rotation"
}


def gauss_map_invariant_density(x):
    """Evaluate the Gauss map invariant density rho(x) = 1/(ln2 * (1+x)).
    Input: array (points in (0,1]). Output: array (density values)."""
    x_safe = np.clip(x, 1e-15, None)
    return 1.0 / (np.log(2) * (1.0 + x_safe))


OPERATIONS["gauss_map_invariant_density"] = {
    "fn": gauss_map_invariant_density,
    "input_type": "array",
    "output_type": "array",
    "description": "Invariant density of the Gauss map (continued fraction map)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
