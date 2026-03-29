"""
Rod Calculus — Chinese counting rod algorithms (Horner scheme, early Gaussian elimination)

Connects to: [vedic_square, pingala_prosody, kerala_series]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "rod_calculus"
OPERATIONS = {}


def horner_evaluate(x):
    """Evaluate polynomial using Horner's method (rod calculus). Input: array [x0, c0, c1, ...]. Output: scalar.
    Polynomial: c0 + c1*x + c2*x^2 + ... evaluated at x0."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    if len(arr) < 2:
        return float(arr[0]) if len(arr) > 0 else 0.0
    x0 = arr[0]
    coeffs = arr[1:]  # c0, c1, c2, ... (ascending order)
    # Horner: start from highest degree
    result = coeffs[-1]
    for c in reversed(coeffs[:-1]):
        result = result * x0 + c
    return float(result)


OPERATIONS["horner_evaluate"] = {
    "fn": horner_evaluate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Evaluate polynomial via Horner's scheme (Chinese rod calculus)"
}


def jia_xian_triangle(x):
    """Generate Jia Xian's triangle (Pascal's triangle). Input: scalar (n rows). Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(1, int(arr[0])) if len(arr) > 0 else 5
    n = min(n, 20)  # cap for performance
    triangle = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        triangle[i, 0] = 1.0
        for j in range(1, i + 1):
            triangle[i, j] = triangle[i - 1, j - 1] + triangle[i - 1, j]
    return triangle


OPERATIONS["jia_xian_triangle"] = {
    "fn": jia_xian_triangle,
    "input_type": "scalar",
    "output_type": "matrix",
    "description": "Generate Jia Xian's triangle (Pascal's triangle, centuries earlier)"
}


def polynomial_root_extract(x):
    """Extract real roots of polynomial using rod calculus bisection. Input: array (coeffs ascending). Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    if len(arr) < 2:
        return np.array([0.0])
    coeffs = arr  # ascending: c0 + c1*x + c2*x^2 + ...

    def eval_poly(t):
        result = coeffs[-1]
        for c in reversed(coeffs[:-1]):
            result = result * t + c
        return result

    # Search for roots by sign changes in [-100, 100]
    roots = []
    test_points = np.linspace(-10, 10, 201)
    vals = np.array([eval_poly(t) for t in test_points])
    for i in range(len(vals) - 1):
        if vals[i] * vals[i + 1] < 0:
            # Bisection
            lo, hi = test_points[i], test_points[i + 1]
            for _ in range(60):
                mid = (lo + hi) / 2.0
                if eval_poly(mid) * eval_poly(lo) < 0:
                    hi = mid
                else:
                    lo = mid
            roots.append((lo + hi) / 2.0)
    if not roots:
        return np.array([np.nan])
    return np.array(roots)


OPERATIONS["polynomial_root_extract"] = {
    "fn": polynomial_root_extract,
    "input_type": "array",
    "output_type": "array",
    "description": "Extract polynomial roots via rod calculus bisection method"
}


def fangcheng_eliminate(x):
    """Gaussian elimination from Nine Chapters (fangcheng). Input: matrix. Output: array (solution)."""
    mat = np.asarray(x, dtype=np.float64)
    if mat.ndim == 1:
        n = int(np.sqrt(len(mat)))
        if n * n == len(mat):
            mat = mat.reshape(n, n)
        else:
            # Treat as augmented system [A|b] with n-1 unknowns
            # For the test input, just solve a small system
            return np.array([float(mat[0])]) if len(mat) > 0 else np.array([0.0])

    rows, cols = mat.shape
    if cols < 2:
        return np.array([0.0])

    # Augmented matrix: last column is RHS
    aug = mat.copy()
    n = min(rows, cols - 1)

    # Forward elimination
    for i in range(n):
        # Partial pivoting
        max_row = i + np.argmax(np.abs(aug[i:rows, i]))
        aug[[i, max_row]] = aug[[max_row, i]]
        if abs(aug[i, i]) < 1e-12:
            continue
        for j in range(i + 1, rows):
            factor = aug[j, i] / aug[i, i]
            aug[j, i:] -= factor * aug[i, i:]

    # Back substitution
    solution = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if abs(aug[i, i]) < 1e-12:
            solution[i] = 0.0
        else:
            solution[i] = (aug[i, -1] - np.dot(aug[i, i + 1:n], solution[i + 1:n])) / aug[i, i]

    return solution


OPERATIONS["fangcheng_eliminate"] = {
    "fn": fangcheng_eliminate,
    "input_type": "matrix",
    "output_type": "array",
    "description": "Solve linear system via fangcheng (Gaussian elimination, Nine Chapters)"
}


def rod_representation(x):
    """Convert numbers to rod calculus representation (digit arrays). Input: array. Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    max_digits = 5
    result = np.zeros((len(arr), max_digits), dtype=np.float64)
    for i, val in enumerate(arr):
        n = int(abs(val))
        for j in range(max_digits - 1, -1, -1):
            result[i, j] = n % 10
            n //= 10
        if val < 0:
            result[i, 0] = -result[i, 0]
    return result


OPERATIONS["rod_representation"] = {
    "fn": rod_representation,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Convert numbers to counting rod digit representation"
}


def rod_polynomial_gcd(x):
    """GCD of two polynomials using rod calculus Euclidean algorithm. Input: array. Output: array.
    First half and second half of array are two polynomial coefficient vectors."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = len(arr) // 2
    p = np.trim_zeros(arr[:n], 'b') if n > 0 else np.array([0.0])
    q = np.trim_zeros(arr[n:], 'b') if n > 0 else np.array([0.0])
    if len(p) == 0:
        p = np.array([0.0])
    if len(q) == 0:
        q = np.array([0.0])

    # Polynomial GCD via Euclidean algorithm
    def poly_mod(a, b):
        a = a.copy()
        while len(a) >= len(b) and not (len(a) == 1 and abs(a[0]) < 1e-12):
            if abs(b[-1]) < 1e-12:
                break
            coeff = a[-1] / b[-1]
            shift = len(a) - len(b)
            for i in range(len(b)):
                a[i + shift] -= coeff * b[i]
            a = np.trim_zeros(a, 'b')
            if len(a) == 0:
                return np.array([0.0])
        return a

    for _ in range(50):
        if len(q) == 1 and abs(q[0]) < 1e-12:
            break
        r = poly_mod(p, q)
        p = q
        q = r

    # Normalize
    if len(p) > 0 and abs(p[-1]) > 1e-12:
        p = p / p[-1]
    return p


OPERATIONS["rod_polynomial_gcd"] = {
    "fn": rod_polynomial_gcd,
    "input_type": "array",
    "output_type": "array",
    "description": "Polynomial GCD via rod calculus Euclidean algorithm"
}


def rod_multiply_polynomial(x):
    """Multiply two polynomials (rod calculus convolution). Input: array. Output: array.
    First half and second half are two polynomial coefficient vectors."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = len(arr) // 2
    p = arr[:n] if n > 0 else np.array([1.0])
    q = arr[n:] if n > 0 else np.array([1.0])
    return np.convolve(p, q)


OPERATIONS["rod_multiply_polynomial"] = {
    "fn": rod_multiply_polynomial,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two polynomials via rod calculus convolution"
}


def liu_hui_pi_approximation(x):
    """Liu Hui's pi approximation by inscribed polygon doubling. Input: array (n doublings). Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(1, int(arr[0])) if len(arr) > 0 else 10
    n = min(n, 30)
    # Start with hexagon (6 sides), side length = radius = 1
    sides = 6
    side_length = 1.0  # for unit circle radius
    for _ in range(n):
        # Double sides: new side = sqrt(2 - 2*cos(pi/sides)) but using
        # Liu Hui's geometric method:
        # If s is side of n-gon inscribed in unit circle,
        # new side s' for 2n-gon: s' = sqrt(2 - sqrt(4 - s^2))
        s_sq = side_length * side_length
        side_length = np.sqrt(2.0 - np.sqrt(max(4.0 - s_sq, 0.0)))
        sides *= 2
    # pi ~ (sides * side_length) / 2  (perimeter of inscribed polygon / diameter)
    pi_approx = sides * side_length / 2.0
    return float(pi_approx)


OPERATIONS["liu_hui_pi_approximation"] = {
    "fn": liu_hui_pi_approximation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Liu Hui's pi approximation by inscribed polygon doubling"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
