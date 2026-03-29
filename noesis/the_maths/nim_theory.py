"""
Nim Theory — Sprague-Grundy values, nimbers, combinatorial game evaluation

Connects to: [game_theory, combinatorics, binary_arithmetic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "nim_theory"
OPERATIONS = {}


def nim_value(x):
    """Nim-value (XOR of heap sizes). Input: array. Output: scalar."""
    heaps = np.asarray(np.abs(x), dtype=np.int64)
    result = 0
    for h in heaps.ravel():
        result ^= int(h)
    return int(result)


OPERATIONS["nim_value"] = {
    "fn": nim_value,
    "input_type": "array",
    "output_type": "integer",
    "description": "Nim-value of position (XOR of heap sizes)"
}


def sprague_grundy(x):
    """Compute Sprague-Grundy values for subtraction game with moves in x[1:], positions 0..x[0]. Input: array. Output: array."""
    n = int(x[0])
    moves = set(int(m) for m in x[1:] if m > 0)
    if not moves:
        moves = {1, 2, 3}
    sg = np.zeros(n + 1, dtype=np.int64)
    for pos in range(1, n + 1):
        reachable = set()
        for m in moves:
            if pos >= m:
                reachable.add(int(sg[pos - m]))
        # Minimum excludant
        mex = 0
        while mex in reachable:
            mex += 1
        sg[pos] = mex
    return sg


OPERATIONS["sprague_grundy"] = {
    "fn": sprague_grundy,
    "input_type": "array",
    "output_type": "array",
    "description": "Sprague-Grundy values for subtraction game"
}


def nimber_add(x):
    """Nimber addition (XOR) of pairs. x treated as pairs [a0,b0,a1,b1,...]. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    flat = vals.ravel()
    if len(flat) % 2 != 0:
        flat = np.append(flat, 0)
    results = []
    for i in range(0, len(flat), 2):
        results.append(int(flat[i]) ^ int(flat[i + 1]))
    return np.array(results, dtype=np.int64)


OPERATIONS["nimber_add"] = {
    "fn": nimber_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Nimber (XOR) addition of pairs"
}


def nimber_multiply(x):
    """Nimber multiplication of two values x[0]*x[1]. Input: array. Output: integer."""
    a = int(abs(x[0]))
    b = int(abs(x[1]))

    def _nim_mult(a, b):
        if a <= 1 or b <= 1:
            return a * b
        # Find highest power of 2 in bit length
        a_bits = a.bit_length() - 1
        b_bits = b.bit_length() - 1
        # Use recursive definition based on Fermat 2-powers
        # For small values, compute directly via table
        if a < 4 and b < 4:
            # Nimber multiplication table for {0,1,2,3}
            table = [[0, 0, 0, 0],
                     [0, 1, 2, 3],
                     [0, 2, 3, 1],
                     [0, 3, 1, 2]]
            return table[a][b]
        # General case: decompose and recurse
        # Find D = highest Fermat 2-power <= max(a,b)
        D_exp = 1
        while (1 << (1 << D_exp)) <= max(a, b):
            D_exp += 1
        D_exp -= 1
        D = 1 << (1 << D_exp)  # 2^(2^D_exp)

        ah, al = a >> (1 << D_exp), a & (D - 1)
        bh, bl = b >> (1 << D_exp), b & (D - 1)

        c = _nim_mult(ah, bh)
        d = _nim_mult(al, bl)
        e = _nim_mult(ah ^ al, bh ^ bl)
        f = _nim_mult(c, D >> 1)  # c * (D/2) in nimber arithmetic

        return ((e ^ d) << (1 << D_exp)) ^ (f ^ d)

    return int(_nim_mult(a, b))


OPERATIONS["nimber_multiply"] = {
    "fn": nimber_multiply,
    "input_type": "array",
    "output_type": "integer",
    "description": "Nimber multiplication of two values"
}


def mex_function(x):
    """Minimum excludant of the set of values in x. Input: array. Output: integer."""
    vals = set(int(abs(v)) for v in x)
    mex = 0
    while mex in vals:
        mex += 1
    return int(mex)


OPERATIONS["mex_function"] = {
    "fn": mex_function,
    "input_type": "array",
    "output_type": "integer",
    "description": "Minimum excludant (mex) of a set of non-negative integers"
}


def game_sum_value(x):
    """Nim-value of game sum (XOR of individual Grundy values). Input: array. Output: integer."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    result = 0
    for v in vals.ravel():
        result ^= int(v)
    return int(result)


OPERATIONS["game_sum_value"] = {
    "fn": game_sum_value,
    "input_type": "array",
    "output_type": "integer",
    "description": "Game sum value (XOR of component Grundy values)"
}


def wythoff_position(x):
    """Check if (a, b) is a cold position in Wythoff's game. x=[a, b]. Input: array. Output: integer."""
    a = int(abs(x[0]))
    b = int(abs(x[1]))
    if a > b:
        a, b = b, a
    # Cold positions are (floor(n*phi), floor(n*phi^2)) for n=0,1,2,...
    phi = (1 + np.sqrt(5)) / 2
    # Check if a = floor(n*phi) and b = floor(n*phi^2) for some n
    # Equivalently, n = floor(a/phi) or n = a (approximately)
    n_candidate = int(round(a / phi))
    for n in range(max(0, n_candidate - 2), n_candidate + 3):
        an = int(np.floor(n * phi))
        bn = int(np.floor(n * phi * phi))
        if an == a and bn == b:
            return 1  # Cold (P-position)
    return 0  # Hot (N-position)


OPERATIONS["wythoff_position"] = {
    "fn": wythoff_position,
    "input_type": "array",
    "output_type": "integer",
    "description": "1 if (a,b) is a P-position in Wythoff's game, 0 otherwise"
}


def fibonacci_nim_optimal(x):
    """Optimal move in Fibonacci Nim. Heap size = x[0]. Returns stones to take. Input: array. Output: integer."""
    n = int(abs(x[0]))
    if n == 0:
        return 0
    # Zeckendorf representation: take the smallest Fibonacci number in decomposition
    fibs = [1, 2]
    while fibs[-1] < n:
        fibs.append(fibs[-1] + fibs[-2])
    # Find Zeckendorf representation
    remaining = n
    smallest_fib = n
    for f in reversed(fibs):
        if f <= remaining:
            remaining -= f
            smallest_fib = f
            if remaining == 0:
                break
    return int(smallest_fib)


OPERATIONS["fibonacci_nim_optimal"] = {
    "fn": fibonacci_nim_optimal,
    "input_type": "array",
    "output_type": "integer",
    "description": "Optimal move in Fibonacci Nim (smallest Zeckendorf component)"
}


def cold_game_temperature(x):
    """Estimate combinatorial game temperature from Grundy values. Input: array. Output: scalar."""
    vals = np.asarray(np.abs(x), dtype=np.float64)
    # Temperature is roughly the largest move advantage
    # For nim-like games, temperature ~ max(grundy values) / 2
    if len(vals) == 0:
        return 0.0
    return float(np.max(vals) / 2.0)


OPERATIONS["cold_game_temperature"] = {
    "fn": cold_game_temperature,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate game temperature from Grundy values"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
