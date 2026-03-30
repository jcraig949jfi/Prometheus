"""
Plimpton 322 Triples — Babylonian Pythagorean triple generation with regularity constraints

Connects to: [babylonian_sexagesimal, egyptian_fractions, vedic_square]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import gcd

FIELD_NAME = "plimpton322_triples"
OPERATIONS = {}


def _is_regular(n):
    """Check if n is a regular number (factors only 2, 3, 5)."""
    if n <= 0:
        return False
    for p in [2, 3, 5]:
        while n % p == 0:
            n //= p
    return n == 1


def pythagorean_triple_generate(x):
    """Generate Pythagorean triples (a,b,c) with a^2+b^2=c^2 up to limit. Input: scalar. Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    limit = max(5, int(arr[0])) if len(arr) > 0 else 50
    triples = []
    for m in range(2, limit):
        for n in range(1, m):
            if (m - n) % 2 == 0:
                continue
            if gcd(m, n) != 1:
                continue
            a = m * m - n * n
            b = 2 * m * n
            c = m * m + n * n
            if c > limit * limit:
                break
            triples.append([a, b, c])
    if not triples:
        return np.array([[3, 4, 5]], dtype=np.float64)
    return np.array(triples, dtype=np.float64)


OPERATIONS["pythagorean_triple_generate"] = {
    "fn": pythagorean_triple_generate,
    "input_type": "scalar",
    "output_type": "matrix",
    "description": "Generate primitive Pythagorean triples up to a limit"
}


def regular_number_constrained_triples(x):
    """Generate triples where parameters p, q are regular numbers. Input: scalar. Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    limit = max(5, int(arr[0])) if len(arr) > 0 else 100
    # Regular numbers up to limit
    regulars = [n for n in range(1, limit) if _is_regular(n)]
    triples = []
    for i, p in enumerate(regulars):
        for q in regulars[:i]:
            if (p - q) % 2 == 0:
                continue
            if gcd(p, q) != 1:
                continue
            a = p * p - q * q
            b = 2 * p * q
            c = p * p + q * q
            triples.append([a, b, c])
    if not triples:
        return np.array([[3, 4, 5]], dtype=np.float64)
    return np.array(sorted(triples, key=lambda t: t[2]), dtype=np.float64)


OPERATIONS["regular_number_constrained_triples"] = {
    "fn": regular_number_constrained_triples,
    "input_type": "scalar",
    "output_type": "matrix",
    "description": "Pythagorean triples with regular-number parameters (Babylonian style)"
}


def plimpton322_reconstruct(x):
    """Reconstruct the 15 rows of Plimpton 322 tablet. Input: any. Output: matrix."""
    # Known (p, q) pairs that reconstruct the tablet
    # Columns: (p^2/q^2 - q^2/p^2)^2/4, p^2-q^2 (short side/d), p^2+q^2 (diagonal/d), row#
    pq_pairs = [
        (12, 5), (64, 27), (75, 32), (125, 54), (9, 4),
        (20, 9), (54, 25), (32, 15), (25, 12), (81, 40),
        (2, 1), (48, 25), (15, 8), (50, 27), (9, 5)
    ]
    rows = []
    for idx, (p, q) in enumerate(pq_pairs):
        d = 2 * p * q  # common factor
        a = p * p - q * q  # short side (times d)
        c = p * p + q * q  # diagonal (times d)
        # Column 1 of tablet: (c/d)^2 / (a/d)^2 = sec^2(angle)
        sec_sq = (c * c) / (a * a) if a != 0 else 0
        rows.append([sec_sq, a, c, idx + 1])
    return np.array(rows, dtype=np.float64)


OPERATIONS["plimpton322_reconstruct"] = {
    "fn": plimpton322_reconstruct,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Reconstruct the 15 rows of the Plimpton 322 tablet"
}


def triple_parametrize(x):
    """Parametrize triple from (p, q): (p^2-q^2, 2pq, p^2+q^2). Input: array [p, q]. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    p = int(arr[0]) if len(arr) > 0 else 2
    q = int(arr[1]) if len(arr) > 1 else 1
    a = p * p - q * q
    b = 2 * p * q
    c = p * p + q * q
    return np.array([a, b, c], dtype=np.float64)


OPERATIONS["triple_parametrize"] = {
    "fn": triple_parametrize,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate Pythagorean triple from parameters (p, q)"
}


def gap_analysis(x):
    """Find which primitive triples the regular-number method misses up to limit. Input: scalar. Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    limit = max(10, int(arr[0])) if len(arr) > 0 else 100
    # All primitive triples
    all_triples = set()
    for m in range(2, limit):
        for n in range(1, m):
            if (m - n) % 2 == 0 or gcd(m, n) != 1:
                continue
            a = m * m - n * n
            b = 2 * m * n
            c = m * m + n * n
            if c > limit * 10:
                break
            all_triples.add((min(a, b), max(a, b), c))
    # Regular-constrained triples
    regulars = [n for n in range(1, limit) if _is_regular(n)]
    reg_triples = set()
    for i, p in enumerate(regulars):
        for q in regulars[:i]:
            if (p - q) % 2 == 0 or gcd(p, q) != 1:
                continue
            a = p * p - q * q
            b = 2 * p * q
            c = p * p + q * q
            reg_triples.add((min(a, b), max(a, b), c))
    missed = sorted(all_triples - reg_triples, key=lambda t: t[2])
    if not missed:
        return np.array([[0, 0, 0]], dtype=np.float64)
    return np.array(missed[:20], dtype=np.float64)


OPERATIONS["gap_analysis"] = {
    "fn": gap_analysis,
    "input_type": "scalar",
    "output_type": "matrix",
    "description": "Find primitive triples not reachable by regular-number parametrization"
}


def triple_regularity_score(x):
    """Score how 'regular' a Pythagorean triple is (factors 2,3,5 content). Input: array [a,b,c]. Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    total_score = 0.0
    for val in arr:
        n = int(abs(val))
        if n == 0:
            continue
        original = n
        for p in [2, 3, 5]:
            while n % p == 0:
                n //= p
        # Score: fraction of the number that was regular factors
        total_score += 1.0 - (np.log(max(n, 1)) / np.log(max(original, 2)))
    return float(total_score / max(len(arr), 1))


OPERATIONS["triple_regularity_score"] = {
    "fn": triple_regularity_score,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Score regularity (2,3,5 factor content) of triple elements"
}


def secant_squared_column(x):
    """Compute sec^2(angle) = (c/a)^2 for Plimpton 322 interpretation. Input: array [a, c]. Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    a = arr[0] if len(arr) > 0 else 3.0
    c = arr[1] if len(arr) > 1 else 5.0
    if a == 0:
        return np.inf
    return float((c / a) ** 2)


OPERATIONS["secant_squared_column"] = {
    "fn": secant_squared_column,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Compute sec^2 column value (Plimpton 322 Column I interpretation)"
}


def tablet_angle_range(x):
    """Compute the angle range (in degrees) covered by Plimpton 322 rows. Input: any. Output: array.
    Returns [min_angle, max_angle] from the reconstructed tablet."""
    tablet = plimpton322_reconstruct(x)
    angles = []
    for row in tablet:
        sec_sq = row[0]
        if sec_sq > 0:
            cos_sq = 1.0 / sec_sq
            if 0 <= cos_sq <= 1:
                angle = np.degrees(np.arccos(np.sqrt(cos_sq)))
                angles.append(angle)
    if not angles:
        return np.array([0.0, 0.0])
    return np.array([min(angles), max(angles)])


OPERATIONS["tablet_angle_range"] = {
    "fn": tablet_angle_range,
    "input_type": "array",
    "output_type": "array",
    "description": "Angle range (degrees) spanned by Plimpton 322 tablet rows"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
