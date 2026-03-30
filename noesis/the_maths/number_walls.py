"""
Number Walls — number wall construction and zero patterns

Connects to: [combinatorics, linear_recurrences, p_adic_numbers, fractal_geometry]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

A number wall is a 2D array built from a sequence using the cross rule:
W(n,k) * W(n-2,k) = W(n-1,k-1) * W(n-1,k+1) - W(n-1,k)^2
"""

import numpy as np

FIELD_NAME = "number_walls"
OPERATIONS = {}


def number_wall_compute(x, n_rows=6):
    """Build a number wall from sequence x. Row -1 is all zeros, row 0 is all ones,
    row 1 is the sequence, further rows via the cross rule.
    Input: array. Output: array (flattened wall)."""
    seq = x
    m = len(seq)
    width = m + 2 * n_rows  # extra padding
    # Rows indexed 0..n_rows-1 internally; row 0 = all 1s, row 1 = sequence
    wall = np.zeros((n_rows + 2, width))
    # Row -1 (index 0): all zeros
    wall[0, :] = 0.0
    # Row 0 (index 1): all ones
    wall[1, :] = 1.0
    # Row 1 (index 2): the sequence centered
    offset = n_rows
    for i in range(m):
        wall[2, offset + i] = seq[i]
    # Fill remaining rows using the cross rule
    for r in range(3, n_rows + 2):
        for k in range(1, width - 1):
            denom = wall[r - 2, k]
            if abs(denom) > 1e-15:
                wall[r, k] = (wall[r - 1, k - 1] * wall[r - 1, k + 1] - wall[r - 1, k] ** 2) / denom
            else:
                wall[r, k] = 0.0
    # Return the central portion
    result = wall[2:, offset:offset + m]
    return result.flatten()


OPERATIONS["number_wall_compute"] = {
    "fn": number_wall_compute,
    "input_type": "array",
    "output_type": "array",
    "description": "Build number wall from a sequence via the cross rule"
}


def number_wall_zero_window(x):
    """Count zero entries in the number wall (zero windows correspond to
    linear recurrences in the original sequence).
    Input: array. Output: scalar."""
    wall = number_wall_compute(x)
    return float(np.sum(np.abs(wall) < 1e-12))


OPERATIONS["number_wall_zero_window"] = {
    "fn": number_wall_zero_window,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count zeros in the number wall (detects linear recurrences)"
}


def number_wall_frame(x):
    """Extract the 'frame' around zero windows — the nonzero border entries
    adjacent to zeros. Input: array. Output: array."""
    wall_flat = number_wall_compute(x)
    m = len(x)
    n_rows = len(wall_flat) // m if m > 0 else 1
    wall = wall_flat.reshape(n_rows, m)
    frame_entries = []
    for i in range(n_rows):
        for j in range(m):
            if abs(wall[i, j]) > 1e-12:
                # Check if adjacent to a zero
                neighbors = []
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n_rows and 0 <= nj < m:
                        neighbors.append(wall[ni, nj])
                if any(abs(n) < 1e-12 for n in neighbors):
                    frame_entries.append(wall[i, j])
    return np.array(frame_entries) if frame_entries else np.array([0.0])


OPERATIONS["number_wall_frame"] = {
    "fn": number_wall_frame,
    "input_type": "array",
    "output_type": "array",
    "description": "Nonzero frame entries bordering zero windows"
}


def somos_sequence(x):
    """Somos-k sequence starting from initial values x.
    Somos-k: a(n)*a(n-k) = sum of products a(n-i)*a(n-k+i) for i=1..k//2.
    Input: array (initial values, length = k). Output: array (extended sequence)."""
    k = len(x)
    n_extend = max(10, 2 * k)
    a = list(x)
    for n in range(k, k + n_extend):
        num = 0.0
        for i in range(1, k // 2 + 1):
            num += a[n - i] * a[n - k + i]
        denom = a[n - k]
        if abs(denom) > 1e-15:
            a.append(num / denom)
        else:
            a.append(0.0)
    return np.array(a)


OPERATIONS["somos_sequence"] = {
    "fn": somos_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate Somos-k sequence from initial values"
}


def number_wall_determinant(x):
    """The number wall entry at position (n, k) equals the Toeplitz determinant
    det(a_{k-i+j})_{i,j=0}^{n-1}. Compute these for the first few orders.
    Input: array. Output: array (determinants for orders 1..len(x))."""
    n = len(x)
    dets = []
    for order in range(1, n + 1):
        # Build Toeplitz-like matrix
        mat = np.zeros((order, order))
        for i in range(order):
            for j in range(order):
                idx = j - i
                if 0 <= idx < n:
                    mat[i, j] = x[idx]
                elif -n < idx < 0:
                    mat[i, j] = x[-idx] if -idx < n else 0.0
        dets.append(np.linalg.det(mat))
    return np.array(dets)


OPERATIONS["number_wall_determinant"] = {
    "fn": number_wall_determinant,
    "input_type": "array",
    "output_type": "array",
    "description": "Toeplitz determinants underlying the number wall"
}


def zero_pattern_fractal_dimension(x):
    """Estimate the fractal (box-counting) dimension of the zero pattern
    in the number wall. Input: array. Output: scalar."""
    wall_flat = number_wall_compute(x, n_rows=8)
    m = len(x)
    n_rows = len(wall_flat) // m if m > 0 else 1
    if n_rows < 2 or m < 2:
        return 0.0
    wall = wall_flat.reshape(n_rows, m)
    zeros = (np.abs(wall) < 1e-12).astype(float)
    total_zeros = np.sum(zeros)
    if total_zeros == 0:
        return 0.0
    # Box counting at different scales
    counts = []
    scales = []
    for box_size in [1, 2, 4]:
        if box_size > min(n_rows, m):
            continue
        count = 0
        for i in range(0, n_rows, box_size):
            for j in range(0, m, box_size):
                block = zeros[i:i + box_size, j:j + box_size]
                if np.any(block > 0):
                    count += 1
        if count > 0:
            counts.append(np.log(count))
            scales.append(np.log(1.0 / box_size))
    if len(counts) < 2:
        return 1.0
    # Linear regression for dimension
    coeffs = np.polyfit(scales, counts, 1)
    return float(max(0.0, min(2.0, coeffs[0])))


OPERATIONS["zero_pattern_fractal_dimension"] = {
    "fn": zero_pattern_fractal_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Box-counting fractal dimension of zero pattern"
}


def number_wall_recurrence(x):
    """Detect the minimal linear recurrence satisfied by the sequence
    using the number wall (row where zeros appear).
    Input: array. Output: array (recurrence coefficients)."""
    wall_flat = number_wall_compute(x, n_rows=min(len(x), 8))
    m = len(x)
    n_rows = len(wall_flat) // m if m > 0 else 1
    wall = wall_flat.reshape(n_rows, m)
    # Find first row that is all-zero in center
    for r in range(n_rows):
        center = wall[r, m // 4: 3 * m // 4]
        if np.all(np.abs(center) < 1e-10) and r > 0:
            # The recurrence order is r-1
            order = r
            # Solve for coefficients using least squares
            if order < m:
                A_mat = np.zeros((m - order, order))
                b_vec = np.zeros(m - order)
                for i in range(m - order):
                    for j in range(order):
                        A_mat[i, j] = x[i + j]
                    b_vec[i] = x[i + order]
                try:
                    coeffs, _, _, _ = np.linalg.lstsq(A_mat, b_vec, rcond=None)
                    return coeffs
                except np.linalg.LinAlgError:
                    pass
    # No recurrence found; return trivial
    return np.array([1.0])


OPERATIONS["number_wall_recurrence"] = {
    "fn": number_wall_recurrence,
    "input_type": "array",
    "output_type": "array",
    "description": "Detect minimal linear recurrence from number wall"
}


def dodgson_condensation(x):
    """Dodgson condensation (Lewis Carroll's method) for computing determinants.
    Builds successive condensed matrices. Input: array. Output: scalar."""
    n = int(np.round(np.sqrt(len(x))))
    if n * n > len(x):
        n = int(np.floor(np.sqrt(len(x))))
    A = x[:n * n].reshape(n, n).astype(float)
    if n <= 1:
        return float(A[0, 0]) if n == 1 else 0.0
    # Dodgson condensation
    prev_prev = None
    prev = A.copy()
    for step in range(n - 1):
        rows, cols = prev.shape
        new_rows, new_cols = rows - 1, cols - 1
        if new_rows <= 0 or new_cols <= 0:
            break
        current = np.zeros((new_rows, new_cols))
        for i in range(new_rows):
            for j in range(new_cols):
                det2x2 = prev[i, j] * prev[i + 1, j + 1] - prev[i, j + 1] * prev[i + 1, j]
                if prev_prev is not None and i < prev_prev.shape[0] and j < prev_prev.shape[1]:
                    denom = prev_prev[i, j]
                    if abs(denom) > 1e-15:
                        current[i, j] = det2x2 / denom
                    else:
                        current[i, j] = det2x2
                else:
                    current[i, j] = det2x2
        prev_prev = prev
        prev = current
    return float(prev[0, 0]) if prev.size > 0 else 0.0


OPERATIONS["dodgson_condensation"] = {
    "fn": dodgson_condensation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Determinant via Dodgson condensation (Lewis Carroll's identity)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
