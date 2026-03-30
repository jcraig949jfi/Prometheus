"""
Formal Language Theory — Chomsky hierarchy and language complexity

Connects to: [automata_theory, information_theory, combinatorics, computability]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

We interpret input arrays as encoding grammars or automata:
array values define transition weights or production sizes.
"""

import numpy as np

FIELD_NAME = "formal_language_theory"
OPERATIONS = {}


def chomsky_normal_form_size(x):
    """Estimate the CNF grammar size from a grammar encoded as production weights.
    CNF conversion can at most square the number of productions.
    Input: array (production weights). Output: scalar."""
    n = len(x)
    # Original productions: each x[i] > 0 means a production of 'length' x[i]
    # CNF requires rules of form A -> BC or A -> a
    # A production of length k requires k-1 new binary rules
    total_cnf = 0
    for val in x:
        k = max(1, int(abs(val)))
        if k <= 2:
            total_cnf += 1
        else:
            total_cnf += (k - 1)  # chain of binary rules
    return float(total_cnf)


OPERATIONS["chomsky_normal_form_size"] = {
    "fn": chomsky_normal_form_size,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of CNF productions after Chomsky normalization"
}


def cyk_parse_count(x):
    """CYK parse table fill count for a string of length n with k nonterminals.
    The table has O(n^2 * k) cells, each requiring O(n) work.
    Interpret x as nonterminal weights. Input: array. Output: scalar."""
    n = len(x)
    # Simulate CYK: n = string length, k = number of nonterminals (from array)
    k = max(1, int(np.sum(np.abs(x) > 0.5)))
    # Table entries: n*(n+1)/2 substrings, each with k nonterminals
    # For each cell of span s, we try s-1 split points with k^2 rule combinations
    total_ops = 0
    for s in range(1, n + 1):  # span length
        num_substrings = n - s + 1
        splits = max(1, s - 1)
        total_ops += num_substrings * splits * k
    return float(total_ops)


OPERATIONS["cyk_parse_count"] = {
    "fn": cyk_parse_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "CYK parsing operation count for given grammar size"
}


def language_entropy_rate(x):
    """Entropy rate of a language defined by transition probabilities.
    Interpret x as a stochastic process: normalize to probability, compute
    Shannon entropy rate. Input: array. Output: scalar."""
    # Treat x as emission probabilities of a unigram model
    probs = np.abs(x) + 1e-10
    probs = probs / np.sum(probs)
    # Shannon entropy
    entropy = -np.sum(probs * np.log2(probs))
    return float(entropy)


OPERATIONS["language_entropy_rate"] = {
    "fn": language_entropy_rate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy rate of the language model"
}


def pumping_length_estimate(x):
    """Estimate the pumping length for a regular language defined by a DFA.
    The pumping length equals the number of states in the minimal DFA.
    Interpret x as state weights; states with weight > threshold are reachable.
    Input: array. Output: scalar."""
    # Number of "active" states = pumping length
    threshold = np.mean(np.abs(x)) * 0.5
    n_states = int(np.sum(np.abs(x) > threshold))
    return float(max(1, n_states))


OPERATIONS["pumping_length_estimate"] = {
    "fn": pumping_length_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Pumping length estimate (min DFA states)"
}


def star_height(x):
    """Estimate the star height of a regular expression.
    Star height = max nesting depth of Kleene stars.
    We interpret x as a hierarchy of operations and compute nesting depth.
    Input: array. Output: scalar."""
    n = len(x)
    # Model: values above threshold indicate a Kleene star application
    # Star height = longest chain of nested star operations
    threshold = np.median(np.abs(x))
    # Build a nesting structure
    depth = 0
    max_depth = 0
    for val in x:
        if abs(val) > threshold:
            depth += 1
            max_depth = max(max_depth, depth)
        else:
            depth = max(0, depth - 1)
    return float(max(1, max_depth))


OPERATIONS["star_height"] = {
    "fn": star_height,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Star height (max Kleene star nesting depth)"
}


def growth_rate_language(x):
    """Growth rate of a language: the number of strings of length n grows as lambda^n.
    Lambda is the spectral radius of the adjacency/transition matrix.
    Input: array (transition weights). Output: scalar."""
    n = int(np.ceil(np.sqrt(len(x))))
    mat = np.zeros((n, n))
    for i in range(min(len(x), n * n)):
        mat[i // n, i % n] = abs(x[i])
    # Growth rate = spectral radius
    eigenvalues = np.linalg.eigvals(mat)
    spectral_radius = np.max(np.abs(eigenvalues))
    return float(spectral_radius)


OPERATIONS["growth_rate_language"] = {
    "fn": growth_rate_language,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Growth rate (spectral radius of transition matrix)"
}


def ambiguity_degree(x):
    """Degree of ambiguity: max number of distinct parse trees for any string.
    For a grammar with k rules of arity encoded by x, estimate the max
    ambiguity via the self-convolution of production weights.
    Input: array. Output: scalar."""
    n = len(x)
    # Self-convolution measures how many ways to combine productions
    conv = np.convolve(np.abs(x), np.abs(x), mode='full')
    # Ambiguity ~ max of the convolution normalized by mean
    mean_val = np.mean(conv) if np.mean(conv) > 0 else 1.0
    max_ambiguity = np.max(conv) / mean_val
    return float(max_ambiguity)


OPERATIONS["ambiguity_degree"] = {
    "fn": ambiguity_degree,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimated degree of ambiguity of the grammar"
}


def parikh_image(x):
    """Parikh image: map a string to its letter-frequency vector.
    For alphabet of size k, count occurrences of each symbol.
    We interpret x as a sequence of symbol indices. Input: array. Output: array."""
    # Discretize to symbols
    symbols = np.round(np.abs(x)).astype(int)
    max_sym = max(1, np.max(symbols))
    counts = np.zeros(max_sym + 1)
    for s in symbols:
        counts[s] += 1
    return counts


OPERATIONS["parikh_image"] = {
    "fn": parikh_image,
    "input_type": "array",
    "output_type": "array",
    "description": "Parikh image (letter frequency vector) of symbol sequence"
}


def shuffle_product_size(x):
    """Size of the shuffle product of two languages.
    shuffle(u, v) interleaves characters. |shuffle(u,v)| = C(|u|+|v|, |u|).
    Split x into two halves and compute the shuffle product cardinality.
    Input: array. Output: scalar."""
    mid = len(x) // 2
    a = mid  # length of first string
    b = len(x) - mid  # length of second string
    # |shuffle| = C(a+b, a) = (a+b)! / (a! * b!)
    from math import comb
    result = comb(a + b, a)
    return float(result)


OPERATIONS["shuffle_product_size"] = {
    "fn": shuffle_product_size,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Cardinality of shuffle product of two languages"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
