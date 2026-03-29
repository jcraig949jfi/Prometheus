"""
Coding Theory — Hamming codes, Reed-Solomon, BCH, syndrome decoding

Connects to: [linear_algebra, finite_fields, information_theory, combinatorics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "coding_theory"
OPERATIONS = {}


def _hamming_G():
    """Generator matrix for Hamming(7,4) code."""
    return np.array([
        [1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 1],
        [0, 0, 1, 0, 0, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
    ], dtype=np.int64)


def _hamming_H():
    """Parity check matrix for Hamming(7,4) code."""
    return np.array([
        [1, 1, 0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 1],
    ], dtype=np.int64)


def hamming_encode_7_4(x):
    """Encode 4-bit message words using Hamming(7,4) code.
    Input: array (length 4, binary). Output: array (length 7)."""
    msg = np.asarray(x).ravel()[:4].astype(np.int64) % 2
    if len(msg) < 4:
        msg = np.pad(msg, (0, 4 - len(msg)))
    G = _hamming_G()
    codeword = (msg @ G) % 2
    return codeword.astype(np.float64)


OPERATIONS["hamming_encode_7_4"] = {
    "fn": hamming_encode_7_4,
    "input_type": "array",
    "output_type": "array",
    "description": "Encode a 4-bit message using Hamming(7,4) systematic code"
}


def hamming_decode_7_4(x):
    """Decode a 7-bit received word using Hamming(7,4) with single-error correction.
    Input: array (length 7, binary). Output: array (length 4, decoded message)."""
    received = np.asarray(x).ravel()[:7].astype(np.int64) % 2
    if len(received) < 7:
        received = np.pad(received, (0, 7 - len(received)))
    H = _hamming_H()
    syndrome = (H @ received) % 2
    # Syndrome as binary number indicates error position
    error_pos = int(syndrome[0] * 4 + syndrome[1] * 2 + syndrome[2])
    corrected = received.copy()
    if error_pos > 0:
        # Columns of H are binary representations of 1..7
        # Find which column matches the syndrome
        for i in range(7):
            if np.array_equal(H[:, i] % 2, syndrome % 2):
                corrected[i] ^= 1
                break
    # Extract message bits (systematic: first 4 bits)
    return corrected[:4].astype(np.float64)


OPERATIONS["hamming_decode_7_4"] = {
    "fn": hamming_decode_7_4,
    "input_type": "array",
    "output_type": "array",
    "description": "Decode Hamming(7,4) codeword with single-error correction"
}


def hamming_distance(x):
    """Compute pairwise Hamming distances between binary vectors.
    Input: matrix (rows are binary vectors). Output: matrix."""
    M = np.asarray(x)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    M = M.astype(np.int64) % 2
    n = M.shape[0]
    dist = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            d = np.sum(M[i] != M[j])
            dist[i, j] = d
            dist[j, i] = d
    return dist


OPERATIONS["hamming_distance"] = {
    "fn": hamming_distance,
    "input_type": "matrix",
    "output_type": "matrix",
    "description": "Pairwise Hamming distances between binary vectors"
}


def minimum_distance_brute(x):
    """Find minimum Hamming distance of a code (given as matrix of codewords).
    Input: matrix (rows are codewords). Output: scalar."""
    M = np.asarray(x)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    M = M.astype(np.int64) % 2
    n = M.shape[0]
    if n < 2:
        return np.float64(0.0)
    min_d = M.shape[1] + 1
    for i in range(n):
        for j in range(i + 1, n):
            d = int(np.sum(M[i] != M[j]))
            if d < min_d:
                min_d = d
    return np.float64(min_d)


OPERATIONS["minimum_distance_brute"] = {
    "fn": minimum_distance_brute,
    "input_type": "matrix",
    "output_type": "scalar",
    "description": "Minimum Hamming distance of a code by brute force"
}


def singleton_bound(x):
    """Singleton bound: maximum codewords A(n,d) <= q^(n-d+1) for q-ary code.
    Input: array [n, d, q]. Output: scalar."""
    arr = np.asarray(x).ravel()
    n = int(arr[0]) if len(arr) > 0 else 7
    d = int(arr[1]) if len(arr) > 1 else 3
    q = int(arr[2]) if len(arr) > 2 else 2
    return np.float64(q ** (n - d + 1))


OPERATIONS["singleton_bound"] = {
    "fn": singleton_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Singleton bound A(n,d) <= q^(n-d+1)"
}


def plotkin_bound(x):
    """Plotkin bound: for binary code with d even and n < 2d, A(n,d) <= 2*d / (2*d - n).
    Input: array [n, d]. Output: scalar."""
    arr = np.asarray(x).ravel()
    n = int(arr[0]) if len(arr) > 0 else 7
    d = int(arr[1]) if len(arr) > 1 else 3
    if 2 * d <= n:
        # Plotkin bound for d even: A(n,d) <= 2 * floor(d / (2d - n))
        # General: if d is even, A(n,d) <= 2d
        return np.float64(2.0 * d)
    else:
        denom = 2 * d - n
        if denom <= 0:
            return np.float64(float('inf'))
        return np.float64(np.floor(2.0 * d / denom))


OPERATIONS["plotkin_bound"] = {
    "fn": plotkin_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Plotkin bound on maximum code size"
}


def gilbert_varshamov_bound(x):
    """Gilbert-Varshamov bound: binary [n,k,d] code exists if 2^(n-k) > sum_{i=0}^{d-2} C(n-1,i).
    Input: array [n, d]. Output: scalar (minimum k satisfying bound)."""
    from math import comb
    arr = np.asarray(x).ravel()
    n = int(arr[0]) if len(arr) > 0 else 7
    d = int(arr[1]) if len(arr) > 1 else 3
    # Sum of C(n-1, i) for i = 0..d-2
    vol = sum(comb(n - 1, i) for i in range(d - 1))
    # Need 2^(n-k) > vol => n - k > log2(vol) => k < n - log2(vol)
    if vol > 0:
        k = int(np.floor(n - np.log2(vol)))
    else:
        k = n
    return np.float64(max(k, 1))


OPERATIONS["gilbert_varshamov_bound"] = {
    "fn": gilbert_varshamov_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Gilbert-Varshamov lower bound on achievable dimension k for [n,k,d] code"
}


def syndrome_compute(x):
    """Compute syndrome H*r^T for Hamming(7,4).
    Input: array (length 7 received word). Output: array (syndrome)."""
    received = np.asarray(x).ravel()[:7].astype(np.int64) % 2
    if len(received) < 7:
        received = np.pad(received, (0, 7 - len(received)))
    H = _hamming_H()
    syndrome = (H @ received) % 2
    return syndrome.astype(np.float64)


OPERATIONS["syndrome_compute"] = {
    "fn": syndrome_compute,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute syndrome of received word for Hamming(7,4)"
}


def parity_check_matrix_hamming(x):
    """Return the parity check matrix for Hamming(2^r - 1, 2^r - 1 - r).
    Input: array (first element = r). Output: matrix."""
    r = max(int(np.asarray(x).ravel()[0]), 2)
    r = min(r, 10)  # Reasonable limit
    n = 2 ** r - 1
    # Columns are binary representations of 1..n
    H = np.zeros((r, n), dtype=np.float64)
    for j in range(1, n + 1):
        for i in range(r):
            H[r - 1 - i, j - 1] = (j >> i) & 1
    return H


OPERATIONS["parity_check_matrix_hamming"] = {
    "fn": parity_check_matrix_hamming,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Parity check matrix for Hamming(2^r - 1, 2^r - 1 - r) code"
}


def repetition_code_decode(x):
    """Decode a repetition code by majority vote.
    Input: array (binary received word). Output: scalar (decoded bit)."""
    bits = np.asarray(x).ravel().astype(np.int64) % 2
    ones = np.sum(bits)
    return np.float64(1.0 if ones > len(bits) / 2 else 0.0)


OPERATIONS["repetition_code_decode"] = {
    "fn": repetition_code_decode,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Decode repetition code by majority vote"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
