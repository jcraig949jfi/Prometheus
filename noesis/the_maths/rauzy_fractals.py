"""
Rauzy Fractals — Beta-expansions, Rauzy fractal boundaries, Pisot numbers

Connects to: [symbolic_dynamics, fractal_dimensions, dynamical_systems, quasicrystal_mathematics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "rauzy_fractals"
OPERATIONS = {}


def beta_expansion(x):
    """Compute greedy beta-expansion of a number.
    Input: array [number, beta, num_digits]. Output: array of digits."""
    x = np.asarray(x, dtype=float)
    number = abs(x[0]) if len(x) > 0 else 1.0
    beta = x[1] if len(x) > 1 else (1 + np.sqrt(5)) / 2  # golden ratio
    num_digits = int(x[2]) if len(x) > 2 else 30
    num_digits = min(num_digits, 500)
    if beta <= 1.0:
        return np.zeros(num_digits)
    digits = []
    val = number
    for _ in range(num_digits):
        d = int(val)
        if d >= int(np.ceil(beta)):
            d = int(np.ceil(beta)) - 1
        digits.append(d)
        val = val * beta - d * beta  # wrong, should be:
        # Actually: greedy algorithm: d_i = floor(r_{i-1} * beta), r_i = r_{i-1} * beta - d_i
        pass
    # Redo properly
    digits = []
    r = number
    for _ in range(num_digits):
        d = int(r)
        d = min(d, int(np.ceil(beta)) - 1)
        digits.append(d)
        r = r * beta - d
        if r < 1e-15:
            r = 0.0
    return np.array(digits, dtype=float)


OPERATIONS["beta_expansion"] = {
    "fn": beta_expansion,
    "input_type": "array",
    "output_type": "array",
    "description": "Greedy beta-expansion of a number"
}


def is_pisot_number(x):
    """Check if a value is close to a Pisot number (algebraic integer > 1 whose conjugates
    all have absolute value < 1). Tests common Pisot numbers.
    Input: array. Output: array of 0/1."""
    x = np.asarray(x, dtype=float)
    # Known Pisot numbers
    golden = (1 + np.sqrt(5)) / 2  # ~1.618
    plastic = 1.3247179572  # real root of x^3 = x + 1
    tribonacci = 1.8392867552  # real root of x^3 = x^2 + x + 1
    silver = 1 + np.sqrt(2)  # ~2.414
    known_pisot = [golden, plastic, tribonacci, silver, 2.0]
    results = []
    tol = 1e-4
    for v in x:
        is_pisot = any(abs(v - p) < tol for p in known_pisot)
        # Also check: integer values > 1 are trivially Pisot
        if v > 1 and abs(v - round(v)) < tol and round(v) >= 2:
            is_pisot = True
        results.append(1.0 if is_pisot else 0.0)
    return np.array(results, dtype=float)


OPERATIONS["is_pisot_number"] = {
    "fn": is_pisot_number,
    "input_type": "array",
    "output_type": "array",
    "description": "Check if values are close to known Pisot numbers"
}


def rauzy_fractal_boundary_points(x):
    """Generate boundary points of the Rauzy fractal for the tribonacci substitution.
    Uses the projection of the stepped surface onto the contracting plane.
    Input: array [num_iterations]. Output: flattened array of (x, y) coordinates."""
    x = np.asarray(x, dtype=float)
    n_iter = int(x[0]) if len(x) > 0 else 8
    n_iter = min(n_iter, 14)
    # Tribonacci substitution: 1->12, 2->13, 3->1
    # Generate the word by iteration
    word = [1]
    for _ in range(n_iter):
        new_word = []
        for c in word:
            if c == 1:
                new_word.extend([1, 2])
            elif c == 2:
                new_word.extend([1, 3])
            else:
                new_word.append(1)
        word = new_word
        if len(word) > 5000:
            word = word[:5000]
            break
    # Tribonacci constant
    t = 1.8392867552141612
    # Companion matrix eigenvalues give projection
    # The contracting eigenvalues are complex conjugates with |lambda| < 1
    # lambda = alpha (where alpha^3 = alpha^2 + alpha + 1)
    # Contracting eigenvalue: compute from characteristic polynomial x^3 - x^2 - x - 1
    roots = np.roots([1, -1, -1, -1])
    # Find contracting (|root| < 1) complex root
    contracting = [r for r in roots if abs(r) < 1 and np.iscomplex(r)]
    if contracting:
        lam = contracting[0]
    else:
        lam = complex(-0.4196 + 0.6063j)
    # Project: point n maps to sum_{k=0}^{n-1} e_{word[k]} * lam^k
    # where e_1, e_2, e_3 are basis vectors projected onto contracting plane
    e = {1: 1.0, 2: lam, 3: lam ** 2}
    points = []
    z = complex(0)
    power = complex(1)
    for i, c in enumerate(word[:min(len(word), 2000)]):
        z += e[c] * power
        power *= lam
        if i % 5 == 0:  # subsample for output size
            points.append(z.real)
            points.append(z.imag)
    return np.array(points, dtype=float)


OPERATIONS["rauzy_fractal_boundary_points"] = {
    "fn": rauzy_fractal_boundary_points,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate Rauzy fractal points via tribonacci substitution projection"
}


def tribonacci_substitution_iterate(x):
    """Iterate the tribonacci substitution 1->12, 2->13, 3->1.
    Input: array [num_iterations]. Output: array encoding the word."""
    x = np.asarray(x, dtype=float)
    n_iter = int(x[0]) if len(x) > 0 else 6
    n_iter = min(n_iter, 15)
    word = [1]
    for _ in range(n_iter):
        new_word = []
        for c in word:
            if c == 1:
                new_word.extend([1, 2])
            elif c == 2:
                new_word.extend([1, 3])
            else:
                new_word.append(1)
        word = new_word
        if len(word) > 5000:
            word = word[:5000]
            break
    return np.array(word, dtype=float)


OPERATIONS["tribonacci_substitution_iterate"] = {
    "fn": tribonacci_substitution_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "Iterate tribonacci substitution 1->12, 2->13, 3->1"
}


def rauzy_fractal_dimension_estimate(x):
    """Estimate the Hausdorff dimension of the Rauzy fractal boundary.
    Uses box-counting on the projected points.
    Input: array [num_iterations]. Output: scalar (estimated dimension)."""
    x = np.asarray(x, dtype=float)
    n_iter = int(x[0]) if len(x) > 0 else 10
    n_iter = min(n_iter, 13)
    # Generate points
    word = [1]
    for _ in range(n_iter):
        new_word = []
        for c in word:
            if c == 1:
                new_word.extend([1, 2])
            elif c == 2:
                new_word.extend([1, 3])
            else:
                new_word.append(1)
        word = new_word
        if len(word) > 5000:
            word = word[:5000]
            break
    roots = np.roots([1, -1, -1, -1])
    contracting = [r for r in roots if abs(r) < 1 and np.iscomplex(r)]
    lam = contracting[0] if contracting else complex(-0.4196 + 0.6063j)
    e = {1: 1.0, 2: lam, 3: lam ** 2}
    points_x, points_y = [], []
    z = complex(0)
    power = complex(1)
    for c in word:
        z += e[c] * power
        power *= lam
        points_x.append(z.real)
        points_y.append(z.imag)
    points_x = np.array(points_x)
    points_y = np.array(points_y)
    # Box counting
    dims = []
    for grid_size in [0.1, 0.05, 0.02, 0.01]:
        bx = ((points_x - points_x.min()) / grid_size).astype(int)
        by = ((points_y - points_y.min()) / grid_size).astype(int)
        boxes = len(set(zip(bx, by)))
        dims.append((np.log(boxes), -np.log(grid_size)))
    dims = np.array(dims)
    if len(dims) > 1:
        # Linear regression for dimension
        slope = np.polyfit(dims[:, 1], dims[:, 0], 1)[0]
    else:
        slope = 2.0
    return np.float64(slope)


OPERATIONS["rauzy_fractal_dimension_estimate"] = {
    "fn": rauzy_fractal_dimension_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate Hausdorff dimension of Rauzy fractal boundary via box-counting"
}


def beta_transformation_orbit(x):
    """Compute orbit of x under the beta-transformation T(x) = beta*x mod 1.
    Input: array [x0, beta, num_steps]. Output: array of orbit values."""
    x = np.asarray(x, dtype=float)
    x0 = x[0] if len(x) > 0 else 0.5
    beta = x[1] if len(x) > 1 else (1 + np.sqrt(5)) / 2
    steps = int(x[2]) if len(x) > 2 else 50
    steps = min(steps, 1000)
    orbit = [x0 % 1.0]
    for _ in range(steps - 1):
        orbit.append((beta * orbit[-1]) % 1.0)
    return np.array(orbit, dtype=float)


OPERATIONS["beta_transformation_orbit"] = {
    "fn": beta_transformation_orbit,
    "input_type": "array",
    "output_type": "array",
    "description": "Orbit under beta-transformation T(x) = beta*x mod 1"
}


def beta_expansion_periodic_check(x):
    """Check if the beta-expansion of 1 is eventually periodic (finite or periodic).
    This is equivalent to beta being a Parry number.
    Input: array [beta, max_digits]. Output: scalar (period length, 0 if not found)."""
    x = np.asarray(x, dtype=float)
    beta = x[0] if len(x) > 0 else (1 + np.sqrt(5)) / 2
    max_digits = int(x[1]) if len(x) > 1 else 100
    max_digits = min(max_digits, 500)
    if beta <= 1.0:
        return np.float64(0)
    # Compute T^n(1) orbit and look for periodicity
    orbit = []
    val = 1.0
    for _ in range(max_digits):
        val = (beta * val) % 1.0
        # Check if val is close to a previous value
        for j, prev in enumerate(orbit):
            if abs(val - prev) < 1e-10:
                return np.float64(len(orbit) - j)
        orbit.append(val)
        if val < 1e-12:
            return np.float64(0)  # finite expansion (period 0)
    return np.float64(-1)  # no period found


OPERATIONS["beta_expansion_periodic_check"] = {
    "fn": beta_expansion_periodic_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if beta-expansion of 1 is eventually periodic (Parry number)"
}


def tiling_self_similarity_factor(x):
    """Compute the self-similarity factor for a substitution tiling.
    For tribonacci, this is the tribonacci constant ~1.839.
    Input: array [variant] (0=tribonacci, 1=fibonacci). Output: scalar."""
    x = np.asarray(x, dtype=float)
    variant = int(x[0]) if len(x) > 0 else 0
    if variant == 1:
        # Fibonacci: x^2 - x - 1 = 0
        return np.float64((1 + np.sqrt(5)) / 2)
    else:
        # Tribonacci: x^3 - x^2 - x - 1 = 0
        roots = np.roots([1, -1, -1, -1])
        real_root = max(r.real for r in roots if abs(r.imag) < 1e-10)
        return np.float64(real_root)


OPERATIONS["tiling_self_similarity_factor"] = {
    "fn": tiling_self_similarity_factor,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Self-similarity factor for substitution tiling"
}


def pisot_eigenvalue_check(x):
    """Given a substitution matrix, check if the dominant eigenvalue is a Pisot number.
    Input: array (flattened n x n matrix, first element = n). Output: array [dominant_eigenvalue, is_pisot, spectral_gap]."""
    x = np.asarray(x, dtype=float)
    n = int(x[0]) if len(x) > 0 else 3
    n = min(n, 10)
    if len(x) >= 1 + n * n:
        M = x[1:1 + n * n].reshape(n, n)
    else:
        # Default: tribonacci substitution matrix
        M = np.array([[1, 1, 1],
                       [1, 0, 0],
                       [0, 1, 0]], dtype=float)
    eigenvalues = np.linalg.eigvals(M)
    # Sort by absolute value descending
    idx = np.argsort(-np.abs(eigenvalues))
    eigenvalues = eigenvalues[idx]
    dominant = np.abs(eigenvalues[0])
    # Check Pisot: dominant > 1, all others < 1
    is_pisot = 1.0 if (dominant > 1.0 and all(np.abs(eigenvalues[1:]) < 1.0)) else 0.0
    spectral_gap = dominant - np.abs(eigenvalues[1]) if len(eigenvalues) > 1 else dominant
    return np.array([dominant, is_pisot, spectral_gap], dtype=float)


OPERATIONS["pisot_eigenvalue_check"] = {
    "fn": pisot_eigenvalue_check,
    "input_type": "array",
    "output_type": "array",
    "description": "Check if substitution matrix has Pisot dominant eigenvalue"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
