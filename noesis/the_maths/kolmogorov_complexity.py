"""
Kolmogorov Complexity — compression ratio, LZ complexity, entropy rate estimation

Connects to: [information_theory, algorithmic_randomness, data_compression]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
import zlib

FIELD_NAME = "kolmogorov_complexity"
OPERATIONS = {}


def lz_complexity(x):
    """Lempel-Ziv complexity (number of distinct substrings in LZ decomposition). Input: array. Output: integer."""
    # Convert array to binary string
    vals = np.asarray(x, dtype=np.float64)
    binary = ''.join('1' if v > np.median(vals) else '0' for v in vals.ravel())
    if len(binary) == 0:
        return 0
    # LZ76 complexity
    n = len(binary)
    i = 0
    c = 1
    l = 1
    while l + i < n:
        # Check if binary[i:i+l] has been seen in binary[0:i+l-1]
        substring = binary[i:i + l]
        if substring in binary[0:i + l - 1]:
            l += 1
        else:
            c += 1
            i += l
            l = 1
    return int(c)


OPERATIONS["lz_complexity"] = {
    "fn": lz_complexity,
    "input_type": "array",
    "output_type": "integer",
    "description": "Lempel-Ziv complexity of binarized sequence"
}


def compression_ratio(x):
    """Ratio of compressed to original size (proxy for Kolmogorov complexity). Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    raw = vals.tobytes()
    if len(raw) == 0:
        return 1.0
    compressed = zlib.compress(raw)
    return float(len(compressed) / len(raw))


OPERATIONS["compression_ratio"] = {
    "fn": compression_ratio,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Compression ratio via zlib as Kolmogorov complexity proxy"
}


def entropy_rate_estimate(x):
    """Estimate entropy rate from sequence via block entropy differences. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    # Quantize to symbols
    n_bins = min(10, len(vals))
    if n_bins < 2 or len(vals) < 4:
        return 0.0
    bins = np.linspace(vals.min() - 1e-10, vals.max() + 1e-10, n_bins + 1)
    symbols = np.digitize(vals, bins) - 1
    symbols = np.clip(symbols, 0, n_bins - 1)

    def _block_entropy(seq, block_size):
        from collections import Counter
        blocks = [tuple(seq[i:i + block_size]) for i in range(len(seq) - block_size + 1)]
        counts = Counter(blocks)
        total = sum(counts.values())
        probs = np.array(list(counts.values()), dtype=np.float64) / total
        return -np.sum(probs * np.log2(probs))

    # h = H(L) - H(L-1) approximates entropy rate
    if len(symbols) < 3:
        return 0.0
    h1 = _block_entropy(symbols, 1)
    h2 = _block_entropy(symbols, 2)
    return float(h2 - h1)


OPERATIONS["entropy_rate_estimate"] = {
    "fn": entropy_rate_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Entropy rate estimate via block entropy differences"
}


def normalized_compression_distance(x):
    """NCD between first and second half of array. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    mid = len(vals) // 2
    if mid == 0:
        return 0.0
    a = vals[:mid].tobytes()
    b = vals[mid:].tobytes()
    ab = vals.tobytes()
    ca = len(zlib.compress(a))
    cb = len(zlib.compress(b))
    cab = len(zlib.compress(ab))
    # NCD(a,b) = (C(ab) - min(C(a), C(b))) / max(C(a), C(b))
    denom = max(ca, cb)
    if denom == 0:
        return 0.0
    return float((cab - min(ca, cb)) / denom)


OPERATIONS["normalized_compression_distance"] = {
    "fn": normalized_compression_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Normalized compression distance between array halves"
}


def block_entropy(x):
    """Block entropy H(L) for block sizes 1..min(4, len). Input: array. Output: array."""
    vals = np.asarray(x, dtype=np.float64)
    n_bins = min(10, len(vals))
    if n_bins < 2:
        return np.array([0.0])
    bins = np.linspace(vals.min() - 1e-10, vals.max() + 1e-10, n_bins + 1)
    symbols = np.digitize(vals, bins) - 1
    symbols = np.clip(symbols, 0, n_bins - 1)

    from collections import Counter
    max_block = min(4, len(symbols))
    entropies = []
    for L in range(1, max_block + 1):
        blocks = [tuple(symbols[i:i + L]) for i in range(len(symbols) - L + 1)]
        counts = Counter(blocks)
        total = sum(counts.values())
        probs = np.array(list(counts.values()), dtype=np.float64) / total
        entropies.append(-np.sum(probs * np.log2(probs)))
    return np.array(entropies)


OPERATIONS["block_entropy"] = {
    "fn": block_entropy,
    "input_type": "array",
    "output_type": "array",
    "description": "Block entropy H(L) for increasing block sizes"
}


def conditional_entropy_estimate(x):
    """Estimate H(X_n | X_{n-1}) from sequence. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    n_bins = min(10, len(vals))
    if n_bins < 2 or len(vals) < 3:
        return 0.0
    bins = np.linspace(vals.min() - 1e-10, vals.max() + 1e-10, n_bins + 1)
    symbols = np.digitize(vals, bins) - 1
    symbols = np.clip(symbols, 0, n_bins - 1)

    from collections import Counter
    # H(X_n | X_{n-1}) = H(X_n, X_{n-1}) - H(X_{n-1})
    pairs = [tuple(symbols[i:i + 2]) for i in range(len(symbols) - 1)]
    singles = [s for s in symbols[:-1]]

    pair_counts = Counter(pairs)
    single_counts = Counter(singles)

    total_p = sum(pair_counts.values())
    total_s = sum(single_counts.values())

    h_pair = -sum((c / total_p) * np.log2(c / total_p) for c in pair_counts.values())
    h_single = -sum((c / total_s) * np.log2(c / total_s) for c in single_counts.values())

    return float(h_pair - h_single)


OPERATIONS["conditional_entropy_estimate"] = {
    "fn": conditional_entropy_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Conditional entropy H(X_n | X_{n-1}) estimate"
}


def effective_measure_complexity(x):
    """Effective measure complexity: sum of (h_L - h_inf) over block sizes. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    n_bins = min(10, len(vals))
    if n_bins < 2 or len(vals) < 5:
        return 0.0
    bins = np.linspace(vals.min() - 1e-10, vals.max() + 1e-10, n_bins + 1)
    symbols = np.digitize(vals, bins) - 1
    symbols = np.clip(symbols, 0, n_bins - 1)

    from collections import Counter
    max_block = min(4, len(symbols))
    entropies = []
    for L in range(1, max_block + 1):
        blocks = [tuple(symbols[i:i + L]) for i in range(len(symbols) - L + 1)]
        counts = Counter(blocks)
        total = sum(counts.values())
        probs = np.array(list(counts.values()), dtype=np.float64) / total
        entropies.append(-np.sum(probs * np.log2(probs)))

    # h_L = H(L) - H(L-1), entropy rate estimates
    h_rates = [entropies[0]]
    for i in range(1, len(entropies)):
        h_rates.append(entropies[i] - entropies[i - 1])

    if len(h_rates) < 2:
        return 0.0
    h_inf = h_rates[-1]
    emc = sum(h - h_inf for h in h_rates[:-1])
    return float(max(emc, 0.0))


OPERATIONS["effective_measure_complexity"] = {
    "fn": effective_measure_complexity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Effective measure complexity (excess entropy rate sum)"
}


def excess_entropy(x):
    """Excess entropy E = lim_{L->inf} [H(L) - L*h]. Input: array. Output: scalar."""
    vals = np.asarray(x, dtype=np.float64)
    n_bins = min(10, len(vals))
    if n_bins < 2 or len(vals) < 5:
        return 0.0
    bins = np.linspace(vals.min() - 1e-10, vals.max() + 1e-10, n_bins + 1)
    symbols = np.digitize(vals, bins) - 1
    symbols = np.clip(symbols, 0, n_bins - 1)

    from collections import Counter
    max_block = min(4, len(symbols))
    entropies = []
    for L in range(1, max_block + 1):
        blocks = [tuple(symbols[i:i + L]) for i in range(len(symbols) - L + 1)]
        counts = Counter(blocks)
        total = sum(counts.values())
        probs = np.array(list(counts.values()), dtype=np.float64) / total
        entropies.append(-np.sum(probs * np.log2(probs)))

    if len(entropies) < 2:
        return 0.0
    # Estimate h from last two block entropies
    h_est = entropies[-1] - entropies[-2]
    # Excess entropy E ~ H(L) - L*h for largest L
    L = len(entropies)
    E = entropies[-1] - L * h_est
    return float(max(E, 0.0))


OPERATIONS["excess_entropy"] = {
    "fn": excess_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Excess entropy (total memory in process)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
