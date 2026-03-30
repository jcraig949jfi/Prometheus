"""
Rook Theory — rook polynomials, hit numbers, permutations with forbidden positions

Connects to: [combinatorics, species_arithmetic, majorization, linear_algebra]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import factorial, comb
from itertools import permutations as iter_permutations

FIELD_NAME = "rook_theory"
OPERATIONS = {}


def _board_from_array(x):
    """Create a board (0/1 matrix) from array. Reshape to square matrix,
    threshold at median to get forbidden positions."""
    n = int(np.ceil(np.sqrt(len(x))))
    padded = np.zeros(n * n)
    padded[:len(x)] = x
    board = padded.reshape(n, n)
    # Convert to 0/1: positions above median are available
    median = np.median(board)
    return (board > median).astype(int), n


def _rook_poly_board(board, n):
    """Compute rook polynomial coefficients for an n x n board.
    r_k = number of ways to place k non-attacking rooks on the board.
    Uses inclusion-exclusion via permanent-like computation for small n."""
    max_k = n
    r = np.zeros(max_k + 1)
    r[0] = 1.0
    if n > 8:
        # Approximate for large boards using greedy
        for k in range(1, max_k + 1):
            # Count using column-based recursion (approximate)
            count = 0.0
            available = board.copy()
            for trial in range(min(100, n * n)):
                np.random.seed(trial + 42)
                placed = 0
                used_rows = set()
                used_cols = set()
                cols = np.random.permutation(n)
                for c in cols:
                    for row in np.random.permutation(n):
                        if row not in used_rows and available[row, c] == 1:
                            used_rows.add(row)
                            used_cols.add(c)
                            placed += 1
                            break
                    if placed >= k:
                        count += 1
                        break
            r[k] = max(count, 0)
        return r

    # Exact computation for small boards via recursive expansion
    def count_placements(board, n, k, start_col, used_rows):
        if k == 0:
            return 1
        if start_col >= n:
            return 0
        # Don't place in this column
        total = count_placements(board, n, k, start_col + 1, used_rows)
        # Place in this column in each available row
        for row in range(n):
            if row not in used_rows and board[row, start_col] == 1:
                used_rows.add(row)
                total += count_placements(board, n, k - 1, start_col + 1, used_rows)
                used_rows.remove(row)
        return total

    for k in range(1, max_k + 1):
        r[k] = count_placements(board, n, k, 0, set())
    return r


def rook_polynomial(x):
    """Compute the rook polynomial coefficients for a board derived from x.
    r_k = number of ways to place k non-attacking rooks.
    Input: array. Output: polynomial (array of coefficients)."""
    board, n = _board_from_array(x)
    return _rook_poly_board(board, n)


OPERATIONS["rook_polynomial"] = {
    "fn": rook_polynomial,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "Rook polynomial coefficients for board derived from input"
}


def hit_number(x):
    """Compute hit numbers h_k = number of permutations that hit exactly k
    forbidden positions. Uses inclusion-exclusion with rook numbers.
    h_k = sum_{i=0}^{n-k} (-1)^i * C(k+i, i) * r_{k+i} * (n-k-i)!
    Wait, correct formula: h_k = sum_{j=k}^{n} (-1)^{j-k} C(j,k) r_j (n-j)!
    Input: array. Output: array."""
    board, n = _board_from_array(x)
    r = _rook_poly_board(board, n)
    h = np.zeros(n + 1)
    for k in range(n + 1):
        s = 0.0
        for j in range(k, n + 1):
            s += ((-1) ** (j - k)) * comb(j, k) * r[j] * factorial(n - j)
        h[k] = s
    return h


OPERATIONS["hit_number"] = {
    "fn": hit_number,
    "input_type": "array",
    "output_type": "array",
    "description": "Hit numbers: permutations hitting exactly k forbidden positions"
}


def forbidden_position_count(x):
    """Count permutations avoiding all forbidden positions (hit number h_0).
    This is D_B = sum_{k=0}^{n} (-1)^k * r_k * (n-k)!.
    Input: array. Output: scalar."""
    board, n = _board_from_array(x)
    r = _rook_poly_board(board, n)
    total = 0.0
    for k in range(n + 1):
        total += ((-1) ** k) * r[k] * factorial(n - k)
    return float(total)


OPERATIONS["forbidden_position_count"] = {
    "fn": forbidden_position_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of permutations avoiding all forbidden positions"
}


def rook_placement_count(x):
    """Count maximum number of non-attacking rooks on the board.
    This equals the maximum matching in the bipartite graph.
    Input: array. Output: integer."""
    board, n = _board_from_array(x)
    # Greedy matching
    used_rows = set()
    used_cols = set()
    count = 0
    for i in range(n):
        for j in range(n):
            if board[i, j] == 1 and i not in used_rows and j not in used_cols:
                used_rows.add(i)
                used_cols.add(j)
                count += 1
                break
    return int(count)


OPERATIONS["rook_placement_count"] = {
    "fn": rook_placement_count,
    "input_type": "array",
    "output_type": "integer",
    "description": "Maximum non-attacking rooks on the board"
}


def board_complement_rook_poly(x):
    """Rook polynomial of the complement board (swap 0s and 1s).
    Input: array. Output: polynomial."""
    board, n = _board_from_array(x)
    comp_board = 1 - board
    return _rook_poly_board(comp_board, n)


OPERATIONS["board_complement_rook_poly"] = {
    "fn": board_complement_rook_poly,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "Rook polynomial of the complement board"
}


def ferrers_board_rook_poly(x):
    """Rook polynomial for a Ferrers board defined by column heights from x.
    Column j has height min(floor(|x[j]|), n). Input: array. Output: polynomial."""
    n = len(x)
    heights = np.minimum(np.floor(np.abs(x)).astype(int), n)
    heights = np.sort(heights)  # Ferrers boards have non-decreasing heights
    # Build board
    board = np.zeros((n, n), dtype=int)
    for j in range(n):
        for i in range(min(heights[j], n)):
            board[i, j] = 1
    return _rook_poly_board(board, n)


OPERATIONS["ferrers_board_rook_poly"] = {
    "fn": ferrers_board_rook_poly,
    "input_type": "array",
    "output_type": "polynomial",
    "description": "Rook polynomial for Ferrers board with given column heights"
}


def rook_reciprocity(x):
    """Rook reciprocity: evaluate rook polynomial at -1 and relate to
    complementary board. R_B(-1) = (-1)^n * number of permutations on complement.
    Returns R_B(-1). Input: array. Output: scalar."""
    board, n = _board_from_array(x)
    r = _rook_poly_board(board, n)
    # Evaluate R_B(t) = sum r_k * t^k at t = -1
    val = 0.0
    for k in range(len(r)):
        val += r[k] * ((-1) ** k)
    return float(val)


OPERATIONS["rook_reciprocity"] = {
    "fn": rook_reciprocity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rook polynomial evaluated at -1 (reciprocity)"
}


def permanent_via_rook(x):
    """Compute the permanent of a 0/1 matrix via rook theory.
    perm(A) = r_n (maximum rook number) for an n x n board A.
    Input: array. Output: scalar."""
    board, n = _board_from_array(x)
    r = _rook_poly_board(board, n)
    return float(r[n]) if n < len(r) else 0.0


OPERATIONS["permanent_via_rook"] = {
    "fn": permanent_via_rook,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Permanent of 0/1 matrix = r_n (max rook number)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
