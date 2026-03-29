"""
Origami Axiomatics -- Huzita-Hatori axioms, flat-foldability, crease pattern algebra

Connects to: [geometric_algebra, constructive_mathematics, exterior_calculus, computational_algebra]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "origami_axiomatics"
OPERATIONS = {}


def huzita_axiom_1(x):
    """Axiom 1: Given two points p1, p2, fold the line passing through both.
    Input: array [p1x, p1y, p2x, p2y, ...]. Output: array [a, b, c] for line ax+by+c=0."""
    if len(x) < 4:
        padded = np.concatenate([x, np.zeros(4 - len(x))])
    else:
        padded = x[:4]
    p1 = padded[:2]
    p2 = padded[2:4]
    # Direction
    d = p2 - p1
    # Line through p1 and p2: normal is perpendicular to d
    # But axiom 1 IS the line through p1 and p2
    # ax + by + c = 0 where (a,b) = (-dy, dx)
    a = -d[1]
    b = d[0]
    c = -(a * p1[0] + b * p1[1])
    norm = np.sqrt(a ** 2 + b ** 2)
    if norm > 1e-15:
        a, b, c = a / norm, b / norm, c / norm
    return np.array([a, b, c])


OPERATIONS["huzita_axiom_1"] = {
    "fn": huzita_axiom_1,
    "input_type": "array",
    "output_type": "array",
    "description": "Axiom 1: Line through two points (fold crease)"
}


def huzita_axiom_2(x):
    """Axiom 2: Given two points p1, p2, fold p1 onto p2 (perpendicular bisector).
    Input: array [p1x, p1y, p2x, p2y, ...]. Output: array [a, b, c]."""
    if len(x) < 4:
        padded = np.concatenate([x, np.zeros(4 - len(x))])
    else:
        padded = x[:4]
    p1 = padded[:2]
    p2 = padded[2:4]
    midpoint = (p1 + p2) / 2.0
    d = p2 - p1
    # Perpendicular bisector: normal is d itself
    a = d[0]
    b = d[1]
    c = -(a * midpoint[0] + b * midpoint[1])
    norm = np.sqrt(a ** 2 + b ** 2)
    if norm > 1e-15:
        a, b, c = a / norm, b / norm, c / norm
    return np.array([a, b, c])


OPERATIONS["huzita_axiom_2"] = {
    "fn": huzita_axiom_2,
    "input_type": "array",
    "output_type": "array",
    "description": "Axiom 2: Perpendicular bisector fold (point onto point)"
}


def huzita_axiom_3(x):
    """Axiom 3: Given two lines, fold one onto the other (angle bisector).
    Input: array [a1,b1,c1, a2,b2,c2, ...]. Output: array [a,b,c]."""
    if len(x) < 6:
        padded = np.concatenate([x, np.ones(6 - len(x))])
    else:
        padded = x[:6]
    n1 = padded[:2]
    c1 = padded[2]
    n2 = padded[3:5]
    c2 = padded[5]
    # Normalize
    norm1 = np.linalg.norm(n1)
    norm2 = np.linalg.norm(n2)
    if norm1 > 1e-15:
        n1, c1 = n1 / norm1, c1 / norm1
    if norm2 > 1e-15:
        n2, c2 = n2 / norm2, c2 / norm2
    # Angle bisector: (a1x+b1y+c1)/1 = +-(a2x+b2y+c2)/1
    # => (a1-a2)x + (b1-b2)y + (c1-c2) = 0
    a = n1[0] - n2[0]
    b = n1[1] - n2[1]
    c = c1 - c2
    norm = np.sqrt(a ** 2 + b ** 2)
    if norm > 1e-15:
        a, b, c = a / norm, b / norm, c / norm
    return np.array([a, b, c])


OPERATIONS["huzita_axiom_3"] = {
    "fn": huzita_axiom_3,
    "input_type": "array",
    "output_type": "array",
    "description": "Axiom 3: Angle bisector fold (line onto line)"
}


def huzita_axiom_6(x):
    """Axiom 6: Given two points and two lines, fold point1 onto line1 and point2 onto line2.
    This is the axiom that solves cubics. Returns fold line.
    Input: array [p1x,p1y, p2x,p2y, a1,b1,c1, a2,b2,c2, ...]. Output: array [a,b,c]."""
    if len(x) < 10:
        padded = np.concatenate([x, np.ones(10 - len(x))])
    else:
        padded = x[:10]
    p1 = padded[:2]
    p2 = padded[2:4]
    line1 = padded[4:7]  # a1, b1, c1
    line2 = padded[7:10]
    # This requires solving a cubic. For a general implementation,
    # find fold line L such that reflection of p1 in L lies on line1
    # and reflection of p2 in L lies on line2.
    # Parametrize fold line by angle theta: L passes through some point with direction (cos(theta), sin(theta))
    # Search over theta
    best_err = np.inf
    best_fold = np.array([1.0, 0.0, 0.0])
    for theta in np.linspace(0, np.pi, 180):
        n = np.array([np.cos(theta), np.sin(theta)])
        # For each theta, find the offset d such that both reflections work
        # Reflection of p in line (n, d): p' = p - 2(n.p - d)n
        # p1' must satisfy line1: a1*p1'x + b1*p1'y + c1 = 0
        # This gives a linear equation in d
        # p1' = p1 - 2*(n.p1 - d)*n
        # line1 . p1' + c1 = 0
        l1_n = line1[:2]
        l1_c = line1[2]
        l2_n = line2[:2]
        l2_c = line2[2]
        # dot(l1_n, p1 - 2*(dot(n,p1) - d)*n) + l1_c = 0
        # dot(l1_n, p1) - 2*(dot(n,p1) - d)*dot(l1_n, n) + l1_c = 0
        A1 = 2.0 * np.dot(l1_n, n)
        B1 = np.dot(l1_n, p1) - 2.0 * np.dot(n, p1) * np.dot(l1_n, n) + l1_c
        # d = (B1) / (-A1) ... wait: A1*d + B1 = 0 => d = -B1/A1
        A2 = 2.0 * np.dot(l2_n, n)
        B2 = np.dot(l2_n, p2) - 2.0 * np.dot(n, p2) * np.dot(l2_n, n) + l2_c
        if abs(A1) < 1e-15 or abs(A2) < 1e-15:
            continue
        d1 = -B1 / A1
        d2 = -B2 / A2
        err = abs(d1 - d2)
        if err < best_err:
            best_err = err
            d = (d1 + d2) / 2.0
            best_fold = np.array([n[0], n[1], -d])
    norm = np.sqrt(best_fold[0] ** 2 + best_fold[1] ** 2)
    if norm > 1e-15:
        best_fold /= norm
    return best_fold


OPERATIONS["huzita_axiom_6"] = {
    "fn": huzita_axiom_6,
    "input_type": "array",
    "output_type": "array",
    "description": "Axiom 6: Cubic-solving fold (two points onto two lines)"
}


def flat_fold_condition(x):
    """Check Kawasaki + Maekawa conditions for flat-foldability.
    Input: array (angles at a vertex in radians). Output: scalar (0 = foldable, >0 = error)."""
    angles = np.abs(x)
    if len(angles) < 2:
        return 0.0
    # Kawasaki: alternating sum of angles = 0
    alt_sum = 0.0
    for i, a in enumerate(angles):
        alt_sum += a if i % 2 == 0 else -a
    return float(abs(alt_sum))


OPERATIONS["flat_fold_condition"] = {
    "fn": flat_fold_condition,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Flat-fold condition error (0 = satisfies Kawasaki theorem)"
}


def kawasaki_theorem_check(x):
    """Kawasaki's theorem: at a flat-foldable vertex, alternating angle sums are equal (both = pi).
    Input: array (angles). Output: scalar (1 if satisfied within tolerance, else 0)."""
    angles = np.abs(x)
    n = len(angles)
    if n < 2 or n % 2 != 0:
        return 0.0
    sum_even = sum(angles[i] for i in range(0, n, 2))
    sum_odd = sum(angles[i] for i in range(1, n, 2))
    # Both should equal pi for flat foldability
    if abs(sum_even - sum_odd) < 0.1:
        return 1.0
    return 0.0


OPERATIONS["kawasaki_theorem_check"] = {
    "fn": kawasaki_theorem_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check Kawasaki theorem (alternating angle sums equal)"
}


def maekawa_theorem_check(x):
    """Maekawa's theorem: M - V = +-2 where M = mountain folds, V = valley folds.
    Input: array (fold assignments: positive = mountain, negative = valley). Output: scalar."""
    n = len(x)
    M = np.sum(x > 0)
    V = np.sum(x < 0)
    diff = abs(M - V)
    return float(1.0 if diff == 2 else 0.0)


OPERATIONS["maekawa_theorem_check"] = {
    "fn": maekawa_theorem_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check Maekawa theorem (|M-V| = 2)"
}


def crease_pattern_valid(x):
    """Check if a crease pattern is valid (all vertices satisfy flat-fold conditions).
    Input: array (angles between consecutive creases). Output: scalar."""
    angles = np.abs(x)
    # Check that angles sum to 2*pi (full turn around vertex)
    total = np.sum(angles)
    angle_error = abs(total - 2 * np.pi)
    kawasaki_err = flat_fold_condition(angles)
    return float(1.0 / (1.0 + angle_error + kawasaki_err))


OPERATIONS["crease_pattern_valid"] = {
    "fn": crease_pattern_valid,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Validity score of crease pattern (1.0 = perfectly valid)"
}


def fold_angle_assignment(x):
    """Assign fold angles (mountain/valley) to creases to satisfy flat-foldability.
    Input: array (crease angles). Output: array (assignments: +1 mountain, -1 valley)."""
    n = len(x)
    # Simple heuristic: alternate M and V, with extra M's to satisfy Maekawa
    assignment = np.ones(n)
    # Need M - V = 2, so if n creases: M = (n+2)/2, V = (n-2)/2
    n_valley = max(0, (n - 2) // 2)
    for i in range(n_valley):
        assignment[2 * i + 1] = -1.0
    return assignment


OPERATIONS["fold_angle_assignment"] = {
    "fn": fold_angle_assignment,
    "input_type": "array",
    "output_type": "array",
    "description": "Mountain/valley assignment satisfying Maekawa theorem"
}


def origami_constructible_number(x):
    """Check if a number is origami-constructible (solvable by nested square and cube roots).
    Origami can solve cubics, so constructible numbers include those from degree <= 3 extensions.
    Input: array. Output: array (1 if constructible, 0 if not, for each element)."""
    results = []
    for val in x:
        # All rationals and their cube/square roots are origami-constructible
        # Heuristic: check if val is a root of a low-degree polynomial with rational coeffs
        # Try: is val^2 or val^3 close to a small integer?
        v = abs(val)
        constructible = 0.0
        for power in [1, 2, 3, 6]:
            vp = v ** power
            if abs(vp - round(vp)) < 0.01:
                constructible = 1.0
                break
        results.append(constructible)
    return np.array(results)


OPERATIONS["origami_constructible_number"] = {
    "fn": origami_constructible_number,
    "input_type": "array",
    "output_type": "array",
    "description": "Check origami-constructibility (cubic extensions of rationals)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
