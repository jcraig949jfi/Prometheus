"""
Symbolic Dynamics — shift spaces, sofic shifts, entropy of symbolic systems

Connects to: [dynamical_systems, ergodic_theory, automata_theory, information_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "symbolic_dynamics"
OPERATIONS = {}


def shift_map(x):
    """Apply the left shift map sigma: (x_0, x_1, x_2, ...) -> (x_1, x_2, ...).
    Input: array. Output: array (one element shorter, or rotated).
    """
    if len(x) <= 1:
        return x.copy()
    return x[1:]


OPERATIONS["shift_map"] = {
    "fn": shift_map,
    "input_type": "array",
    "output_type": "array",
    "description": "Left shift map on a symbolic sequence"
}


def topological_entropy_matrix(x):
    """Topological entropy of a shift of finite type defined by a transition matrix.
    Input: array of length n^2, reshaped as n x n adjacency matrix. Output: scalar.
    Entropy = log(spectral_radius(A)).
    """
    n = int(np.round(np.sqrt(len(x))))
    if n < 1:
        return np.float64(0.0)
    A = x[:n*n].reshape(n, n)
    eigenvalues = np.abs(np.linalg.eigvals(A))
    spectral_radius = np.max(eigenvalues) if len(eigenvalues) > 0 else 1.0
    if spectral_radius <= 0:
        return np.float64(0.0)
    return np.float64(np.log(spectral_radius))


OPERATIONS["topological_entropy_matrix"] = {
    "fn": topological_entropy_matrix,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Topological entropy of a shift of finite type (log of spectral radius)"
}


def sofic_shift_entropy(x):
    """Entropy of a sofic shift given by a labeled graph adjacency matrix.
    Same computation as SFT entropy: h = log(spectral_radius).
    Input: array reshaped as matrix. Output: scalar.
    """
    n = int(np.round(np.sqrt(len(x))))
    if n < 1:
        return np.float64(0.0)
    A = np.abs(x[:n*n].reshape(n, n))
    # For sofic shifts, entropy is still log of spectral radius of the adjacency matrix
    eigenvalues = np.abs(np.linalg.eigvals(A))
    rho = np.max(eigenvalues) if len(eigenvalues) > 0 else 1.0
    if rho <= 0:
        return np.float64(0.0)
    return np.float64(np.log(rho))


OPERATIONS["sofic_shift_entropy"] = {
    "fn": sofic_shift_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Entropy of a sofic shift (log spectral radius of presentation matrix)"
}


def forbidden_words_entropy(x):
    """Approximate entropy of a shift space with forbidden words.
    Input: array treated as a binary sequence (threshold at 0.5). Output: scalar.
    Estimates entropy from empirical block frequencies.
    """
    seq = (x > np.median(x)).astype(int)
    n = len(seq)
    if n < 2:
        return np.float64(0.0)
    # Count block frequencies of length 1 and 2
    freq1 = {}
    freq2 = {}
    for i in range(n):
        w = seq[i]
        freq1[w] = freq1.get(w, 0) + 1
    for i in range(n - 1):
        w = (seq[i], seq[i + 1])
        freq2[w] = freq2.get(w, 0) + 1
    # Entropy rate ~ H(block2) - H(block1) per symbol
    h1 = 0.0
    total1 = sum(freq1.values())
    for c in freq1.values():
        p = c / total1
        if p > 0:
            h1 -= p * np.log(p)
    h2 = 0.0
    total2 = sum(freq2.values())
    for c in freq2.values():
        p = c / total2
        if p > 0:
            h2 -= p * np.log(p)
    return np.float64(h2)


OPERATIONS["forbidden_words_entropy"] = {
    "fn": forbidden_words_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Empirical entropy estimate of a binary symbolic sequence"
}


def golden_mean_shift_matrix(x):
    """Transition matrix for the golden mean shift (no consecutive 1s).
    Input: array (unused, but length determines alphabet hint). Output: matrix.
    Alphabet {0,1}, forbidden word '11'. Transition matrix:
    From 0: can go to 0 or 1. From 1: can only go to 0.
    """
    # The golden mean shift transition matrix
    A = np.array([[1.0, 1.0],
                  [1.0, 0.0]])
    return A


OPERATIONS["golden_mean_shift_matrix"] = {
    "fn": golden_mean_shift_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Transition matrix for the golden mean shift (no consecutive 1s)"
}


def word_complexity_function(x):
    """Word complexity function p(n): number of distinct words of length n in a sequence.
    Input: array treated as symbolic sequence (rounded to integers mod 3). Output: array.
    Returns p(1), p(2), ..., p(min(len/2, 8)).
    """
    seq = np.round(np.abs(x)).astype(int) % 3
    n = len(seq)
    max_len = min(n // 2, 8) if n >= 2 else 1
    complexity = []
    for w_len in range(1, max_len + 1):
        words = set()
        for i in range(n - w_len + 1):
            words.add(tuple(seq[i:i + w_len]))
        complexity.append(len(words))
    return np.array(complexity, dtype=float)


OPERATIONS["word_complexity_function"] = {
    "fn": word_complexity_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Word complexity function p(n) counting distinct subwords of each length"
}


def substitution_system_iterate(x):
    """Apply a simple substitution rule and return the resulting sequence.
    Rule: 0 -> 01, 1 -> 0 (Fibonacci/golden mean substitution).
    Input: array (binarized). Output: array (one iteration of substitution).
    """
    seq = (x > np.median(x)).astype(int)
    result = []
    for s in seq:
        if s == 0:
            result.extend([0, 1])
        else:
            result.extend([0])
    return np.array(result, dtype=float)


OPERATIONS["substitution_system_iterate"] = {
    "fn": substitution_system_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "One iteration of the Fibonacci substitution (0->01, 1->0)"
}


def symbolic_sequence_entropy(x):
    """Shannon entropy of the empirical symbol distribution.
    Input: array (rounded to symbols). Output: scalar.
    """
    symbols = np.round(x).astype(int)
    unique, counts = np.unique(symbols, return_counts=True)
    p = counts / counts.sum()
    return np.float64(-np.sum(p * np.log(p + 1e-300)))


OPERATIONS["symbolic_sequence_entropy"] = {
    "fn": symbolic_sequence_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of the empirical symbol distribution"
}


def recurrence_plot_matrix(x):
    """Recurrence plot: R[i,j] = 1 if |x_i - x_j| < epsilon, else 0.
    Input: array. Output: matrix.
    Epsilon is set to 20% of the data range.
    """
    eps = 0.2 * (np.max(x) - np.min(x)) + 1e-12
    D = np.abs(x[:, None] - x[None, :])
    return (D < eps).astype(float)


OPERATIONS["recurrence_plot_matrix"] = {
    "fn": recurrence_plot_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Binary recurrence plot matrix with threshold at 20% of data range"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
