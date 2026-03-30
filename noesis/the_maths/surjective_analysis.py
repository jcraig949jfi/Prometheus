"""
Surjective Analysis — smooth infinitesimal analysis (constructive)

Connects to: [synthetic_differential_geometry, topos_theory, nonstandard_analysis, category_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "surjective_analysis"
OPERATIONS = {}


def smooth_infinitesimal_test(x):
    """Test if differences behave like smooth infinitesimals: consecutive diffs
    should be nilsquare (d^2 ~ 0). Returns ratio of second-order to first-order diffs.
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    if len(x) < 3:
        return 0.0
    d1 = np.diff(x)
    d2 = np.diff(d1)
    norm1 = np.sum(d1**2)
    norm2 = np.sum(d2**2)
    if norm1 < 1e-15:
        return 0.0
    # In SIA, nilsquare means d^2 = 0; ratio measures how close
    return float(norm2 / norm1)

OPERATIONS["smooth_infinitesimal_test"] = {
    "fn": smooth_infinitesimal_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Test nilsquare property: ratio of second-order to first-order differences"
}


def kock_lawvere_axiom_approx(x):
    """Approximate the Kock-Lawvere axiom: every function on infinitesimals is affine.
    f(d) = f(0) + b*d for unique b. Fits affine model and returns residual.
    Input: array (treated as function values at equally-spaced points near 0).
    Output: scalar (residual, lower = more affine)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    t = np.linspace(0, 1, n)
    # Fit affine: x = a + b*t
    A = np.vstack([np.ones(n), t]).T
    coeffs, residuals, _, _ = np.linalg.lstsq(A, x, rcond=None)
    fitted = A @ coeffs
    residual = np.sqrt(np.mean((x - fitted)**2))
    return float(residual)

OPERATIONS["kock_lawvere_axiom_approx"] = {
    "fn": kock_lawvere_axiom_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Kock-Lawvere axiom test: residual of affine fit (0 = perfectly affine)"
}


def synthetic_derivative(x):
    """Compute derivative using the synthetic/SIA approach: for smooth f,
    f(x+d) = f(x) + f'(x)*d where d is nilsquare. We use finite differences
    with Richardson extrapolation for a cleaner approximation.
    Input: array (function samples). Output: array (derivative samples)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2:
        return np.array([0.0])
    # Central differences where possible, forward/backward at edges
    deriv = np.zeros(n)
    deriv[0] = x[1] - x[0]
    deriv[-1] = x[-1] - x[-2]
    if n > 2:
        deriv[1:-1] = (x[2:] - x[:-2]) / 2.0
    return deriv

OPERATIONS["synthetic_derivative"] = {
    "fn": synthetic_derivative,
    "input_type": "array",
    "output_type": "array",
    "description": "Synthetic derivative via smooth infinitesimal differences"
}


def microlinear_map(x):
    """Apply a microlinear map: in SDG, microlinear objects satisfy that maps
    from D (nilsquares) factor uniquely. We model this as the unique linear
    component of the local behavior: project onto the best-fit line through origin.
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    # Project onto principal direction (rank-1 approximation centered at mean)
    mean = np.mean(x)
    centered = x - mean
    # The microlinear component is the linear trend
    n = len(x)
    t = np.arange(n, dtype=float) - (n - 1) / 2.0
    t_norm_sq = np.dot(t, t)
    if t_norm_sq < 1e-15:
        return x
    slope = np.dot(centered, t) / t_norm_sq
    return mean + slope * t

OPERATIONS["microlinear_map"] = {
    "fn": microlinear_map,
    "input_type": "array",
    "output_type": "array",
    "description": "Microlinear projection: extract the unique linear component"
}


def nilsquare_infinitesimal(x):
    """Generate nilsquare infinitesimals from the input: elements d where d^2 = 0.
    In practice, returns the components of x that are 'infinitesimally small'
    relative to the dominant scale, squared values below machine epsilon.
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    scale = np.max(np.abs(x)) if np.max(np.abs(x)) > 0 else 1.0
    normalized = x / scale
    # Extract the nilsquare part: components where square is negligible
    sq = normalized ** 2
    threshold = np.mean(sq) * 0.01
    nilsquare_mask = sq < threshold
    result = np.where(nilsquare_mask, x, 0.0)
    return result

OPERATIONS["nilsquare_infinitesimal"] = {
    "fn": nilsquare_infinitesimal,
    "input_type": "array",
    "output_type": "array",
    "description": "Extract nilsquare infinitesimal components (effectively-zero-when-squared)"
}


def smooth_topos_morphism(x):
    """Model a morphism in the smooth topos: a natural transformation between
    smooth functors. Approximated as the exponential map applied element-wise,
    which is the canonical smooth morphism from (R,+) to (R*,x).
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    # Clamp for numerical safety
    x_clamped = np.clip(x, -500, 500)
    return np.exp(x_clamped)

OPERATIONS["smooth_topos_morphism"] = {
    "fn": smooth_topos_morphism,
    "input_type": "array",
    "output_type": "array",
    "description": "Smooth topos morphism: exponential map as canonical smooth functor"
}


def infinitesimal_generator(x):
    """Compute the infinitesimal generator of a one-parameter group.
    Given samples of a group action g(t), the generator is dg/dt at t=0.
    We estimate using the matrix logarithm approach for a vector:
    generator = lim_{t->0} (g(t) - id) / t.
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    # Treat x as a discrete one-parameter family; generator is the initial velocity
    # x[0] is the identity, x[k] is the state at step k
    if n < 2:
        return np.array([0.0])
    # Forward difference at t=0 (first step)
    dt = 1.0
    generator = (x[1:] - x[:-1]) / dt
    # The infinitesimal generator is the initial tangent
    return generator

OPERATIONS["infinitesimal_generator"] = {
    "fn": infinitesimal_generator,
    "input_type": "array",
    "output_type": "array",
    "description": "Infinitesimal generator: tangent vector of a one-parameter group at identity"
}


def weil_algebra_product(x):
    """Compute the Weil algebra product: W = R[e]/(e^n=0) truncated polynomial.
    Given array as coefficients of two truncated polynomials (split in half),
    compute their product in the Weil algebra W_2 = R[e]/(e^k=0).
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    half = n // 2
    if half == 0:
        return np.array([0.0])
    a = x[:half]
    b = x[half:2*half]
    # Polynomial multiplication truncated at degree half (nilpotent)
    full_conv = np.convolve(a, b)
    # Truncate: in Weil algebra R[e]/(e^k=0), kill terms of degree >= k
    truncated = full_conv[:half]
    return truncated

OPERATIONS["weil_algebra_product"] = {
    "fn": weil_algebra_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Weil algebra product: truncated polynomial multiplication (nilpotent quotient)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
