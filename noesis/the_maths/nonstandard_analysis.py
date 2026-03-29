"""
Nonstandard Analysis — hyperreal-inspired computations via finite approximations

Connects to: [real analysis, model theory, ultrafilters, infinitesimal calculus, measure theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "nonstandard_analysis"
OPERATIONS = {}


def infinitesimal_approximation(x):
    """Approximate infinitesimal neighborhood using decreasing epsilon sequence.
    Input: array. Output: array of infinitesimal-scale differences."""
    epsilons = 1.0 / (10.0 ** np.arange(1, len(x) + 1))
    # The "shadow" (standard part) of x + epsilon should be x
    hyperreal_approx = x + epsilons
    return hyperreal_approx - x  # Should recover epsilons


OPERATIONS["infinitesimal_approximation"] = {
    "fn": infinitesimal_approximation,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes infinitesimal neighborhood approximation via decreasing epsilon sequence"
}


def transfer_principle_test(x):
    """Test transfer principle: verify that standard identities hold at hyperreal scale.
    Input: array. Output: scalar (max deviation from identity sin^2 + cos^2 = 1 at micro-scale)."""
    eps = 1e-15
    x_hyper = x * eps
    identity_vals = np.sin(x_hyper)**2 + np.cos(x_hyper)**2
    return float(np.max(np.abs(identity_vals - 1.0)))


OPERATIONS["transfer_principle_test"] = {
    "fn": transfer_principle_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tests transfer principle by verifying trig identity at infinitesimal scale"
}


def nonstandard_hull(x):
    """Compute the nonstandard hull: map near-standard hyperreals to their standard parts.
    Input: array (simulated hyperreals with noise). Output: array (standard parts)."""
    # Add infinitesimal perturbation, then take standard part (rounding to finite precision)
    eps = np.random.default_rng(42).normal(0, 1e-14, size=x.shape)
    hyperreal = x + eps
    # Standard part map: st(x + eps) = x
    standard_part = np.round(hyperreal, decimals=10)
    return standard_part


OPERATIONS["nonstandard_hull"] = {
    "fn": nonstandard_hull,
    "input_type": "array",
    "output_type": "array",
    "description": "Maps hyperreal approximations to their standard parts (nonstandard hull)"
}


def overspill_detection(x):
    """Detect overspill: if a property holds for all standard n, it must hold for some
    nonstandard N. We approximate by finding where a monotone property 'spills over'
    a threshold. Input: array. Output: scalar (overspill index)."""
    # Property: x[i] < threshold. Find where it first fails (overspill point)
    threshold = np.mean(x) + np.std(x)
    cummax = np.maximum.accumulate(x)
    overspill_indices = np.where(cummax > threshold)[0]
    if len(overspill_indices) == 0:
        return float(len(x))
    return float(overspill_indices[0])


OPERATIONS["overspill_detection"] = {
    "fn": overspill_detection,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Detects overspill point where a monotone property exceeds standard bounds"
}


def internal_set_approximation(x):
    """Approximate an internal set via ultrafilter-like majority voting on finite subsets.
    Input: array. Output: array (characteristic function of the 'internal' set)."""
    n = len(x)
    # Simulate internal set membership: element is 'internal' if it appears
    # in the majority of random subsamples (ultrafilter approximation)
    rng = np.random.default_rng(137)
    votes = np.zeros(n)
    num_samples = 50
    for _ in range(num_samples):
        subset = rng.choice(n, size=max(1, n // 2), replace=False)
        votes[subset] += 1
    # Internal if majority vote
    membership = (votes > num_samples / 2).astype(float)
    return membership


OPERATIONS["internal_set_approximation"] = {
    "fn": internal_set_approximation,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximates internal set membership via ultrafilter-like majority voting"
}


def robinson_derivative(x):
    """Compute derivative using Robinson's infinitesimal framework:
    f'(x) = st((f(x+e) - f(x))/e) for infinitesimal e.
    Uses f(x) = x^2 as demonstration. Input: array. Output: array."""
    eps = 1e-12
    f_x = x ** 2
    f_x_eps = (x + eps) ** 2
    # Standard part of the hyperreal quotient
    derivative = (f_x_eps - f_x) / eps
    # st() maps to nearest standard real
    return np.round(derivative, decimals=6)


OPERATIONS["robinson_derivative"] = {
    "fn": robinson_derivative,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes derivative via Robinson's infinitesimal quotient with standard part map"
}


def saturation_test(x):
    """Test countable saturation: check if a decreasing sequence of 'sets' has nonempty
    intersection. Approximate via nested intervals. Input: array. Output: scalar."""
    sorted_x = np.sort(x)
    n = len(sorted_x)
    if n < 2:
        return float(sorted_x[0]) if n == 1 else 0.0
    # Nested intervals [sorted_x[i], sorted_x[n-1-i]]
    left = sorted_x[:n // 2]
    right = sorted_x[n - 1:n - 1 - n // 2:-1]
    # Intersection is nonempty if all left[i] <= right[i]
    valid = left <= right
    if np.all(valid):
        # Return midpoint of tightest interval
        tightest = np.argmin(right - left)
        return float((left[tightest] + right[tightest]) / 2)
    else:
        # Return the index where saturation fails
        return float(-np.argmin(valid) - 1)


OPERATIONS["saturation_test"] = {
    "fn": saturation_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tests countable saturation via nested interval intersection"
}


def loeb_measure_approximation(x):
    """Approximate Loeb measure: convert a finitely-additive hyperreal measure to a
    countably-additive real measure via standard part. Input: array (weights).
    Output: array (Loeb measure on partition)."""
    # Interpret x as unnormalized weights on a hyperfinite partition
    # Hyperfinite counting measure: mu(A) = |A|/N for internal set A
    N = len(x)
    # Internal measure (hyperreal-valued)
    internal_measure = np.abs(x) / np.sum(np.abs(x)) if np.sum(np.abs(x)) > 0 else np.ones(N) / N
    # Loeb measure = standard part of internal measure
    # Add infinitesimal noise, then take st()
    eps_noise = np.random.default_rng(99).normal(0, 1e-15, size=N)
    loeb = np.round(internal_measure + eps_noise, decimals=12)
    # Renormalize to ensure it's a proper probability measure
    loeb = np.abs(loeb)
    loeb = loeb / np.sum(loeb)
    return loeb


OPERATIONS["loeb_measure_approximation"] = {
    "fn": loeb_measure_approximation,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximates Loeb measure via standard part of hyperfinite counting measure"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
