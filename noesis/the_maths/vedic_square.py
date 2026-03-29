"""
Vedic Square — Digital root multiplication tables and Z9 structure

Connects to: [pingala_prosody, rod_calculus, egyptian_fractions]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "vedic_square"
OPERATIONS = {}


def _digital_root(n):
    """Compute digital root of integer n (repeatedly sum digits until single digit)."""
    n = int(abs(n))
    if n == 0:
        return 0
    return 1 + (n - 1) % 9


def vedic_square_generate(x):
    """Generate the 9x9 Vedic square (digital root multiplication table). Input: any. Output: matrix."""
    square = np.zeros((9, 9), dtype=np.float64)
    for i in range(9):
        for j in range(9):
            square[i, j] = _digital_root((i + 1) * (j + 1))
    return square


OPERATIONS["vedic_square_generate"] = {
    "fn": vedic_square_generate,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Generate the 9x9 Vedic square (digital root multiplication table)"
}


def digital_root_multiply(x):
    """Digital root of products of consecutive pairs in array. Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for i in range(0, len(arr) - 1, 2):
        results.append(float(_digital_root(int(arr[i]) * int(arr[i + 1]))))
    if not results:
        results.append(float(_digital_root(int(arr[0]))))
    return np.array(results)


OPERATIONS["digital_root_multiply"] = {
    "fn": digital_root_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Digital root of pairwise products"
}


def z9_cayley_table(x):
    """Cayley table for Z/9Z multiplication. Input: any. Output: matrix."""
    table = np.zeros((9, 9), dtype=np.float64)
    for i in range(9):
        for j in range(9):
            table[i, j] = (i * j) % 9
    return table


OPERATIONS["z9_cayley_table"] = {
    "fn": z9_cayley_table,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Cayley (multiplication) table for Z/9Z"
}


def detect_nilpotent_base(x):
    """Find nilpotent elements in Z/nZ (elements where a^k = 0 mod n). Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for val in arr:
        n = max(2, int(abs(val)))
        nilpotents = []
        for a in range(n):
            power = a
            is_nilp = False
            for _ in range(n):
                power = (power * a) % n
                if power == 0:
                    is_nilp = True
                    break
            if is_nilp and a != 0:
                nilpotents.append(a)
        results.append(float(len(nilpotents)))
    return np.array(results)


OPERATIONS["detect_nilpotent_base"] = {
    "fn": detect_nilpotent_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Count nilpotent elements in Z/nZ for each n"
}


def detect_idempotent_base(x):
    """Find idempotent elements in Z/nZ (a^2 = a mod n). Input: array. Output: array."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    results = []
    for val in arr:
        n = max(2, int(abs(val)))
        idempotents = []
        for a in range(n):
            if (a * a) % n == a:
                idempotents.append(a)
        results.append(float(len(idempotents)))
    return np.array(results)


OPERATIONS["detect_idempotent_base"] = {
    "fn": detect_idempotent_base,
    "input_type": "array",
    "output_type": "array",
    "description": "Count idempotent elements (a^2=a) in Z/nZ for each n"
}


def vedic_square_symmetry(x):
    """Analyze symmetry properties of the Vedic square. Input: any. Output: array.
    Returns [is_symmetric, trace, num_distinct_values, determinant_mod9]."""
    vs = vedic_square_generate(x)
    is_sym = 1.0 if np.allclose(vs, vs.T) else 0.0
    trace = float(np.trace(vs))
    distinct = float(len(np.unique(vs)))
    # Determinant mod 9
    det = float(round(np.linalg.det(vs)) % 9)
    return np.array([is_sym, trace, distinct, det])


OPERATIONS["vedic_square_symmetry"] = {
    "fn": vedic_square_symmetry,
    "input_type": "array",
    "output_type": "array",
    "description": "Symmetry analysis of the Vedic square"
}


def latin_square_from_vedic(x):
    """Extract a Latin square pattern from the Vedic square by row permutation. Input: any. Output: matrix."""
    vs = vedic_square_generate(x)
    # The Vedic square rows 1-9 each contain all digits 1-9 when row index is coprime to 9
    # Rows for indices 1, 2, 4, 5, 7, 8 (coprime to 9) form Latin-like rectangles
    coprime_rows = [i for i in range(9) if np.gcd(i + 1, 9) == 1]
    if len(coprime_rows) >= 6:
        sub = vs[coprime_rows[:6], :]
        return sub
    return vs


OPERATIONS["latin_square_from_vedic"] = {
    "fn": latin_square_from_vedic,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Extract Latin square pattern from Vedic square (coprime rows)"
}


def magic_square_connection(x):
    """Compute digital root of a magic square to show Vedic structure. Input: scalar (n). Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(3, int(arr[0])) if len(arr) > 0 else 3
    n = min(n, 9)
    # Generate a magic square using Siamese method for odd n
    if n % 2 == 0:
        n = 3  # fallback to odd
    magic = np.zeros((n, n), dtype=np.int64)
    i, j = 0, n // 2
    for num in range(1, n * n + 1):
        magic[i, j] = num
        ni, nj = (i - 1) % n, (j + 1) % n
        if magic[ni, nj] != 0:
            ni = (i + 1) % n
            nj = j
        i, j = ni, nj
    # Apply digital root to each element
    result = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            result[i, j] = _digital_root(magic[i, j])
    return result


OPERATIONS["magic_square_connection"] = {
    "fn": magic_square_connection,
    "input_type": "scalar",
    "output_type": "matrix",
    "description": "Digital root structure of a magic square"
}


def base_b_vedic_square(x):
    """Generate Vedic square in arbitrary base b. Input: array [b]. Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    b = max(2, int(arr[0])) if len(arr) > 0 else 10
    b = min(b, 20)
    size = b - 1
    square = np.zeros((size, size), dtype=np.float64)
    for i in range(size):
        for j in range(size):
            prod = (i + 1) * (j + 1)
            # Digital root in base b
            if prod == 0:
                dr = 0
            else:
                dr = 1 + (prod - 1) % (b - 1)
            square[i, j] = dr
    return square


OPERATIONS["base_b_vedic_square"] = {
    "fn": base_b_vedic_square,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Vedic square generalized to arbitrary base b"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
