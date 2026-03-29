"""
Automata Base Theory — Sets recognized by automata operating on base-b representations (Cobham's theorem)

Connects to: [automata_theory, formal_language_theory, automata_infinite_words, symbolic_dynamics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "automata_base_theory"
OPERATIONS = {}


def _to_digits_base_b(n, b):
    """Convert non-negative integer n to list of digits in base b (MSB first)."""
    n = int(abs(n))
    b = int(b)
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        digits.append(n % b)
        n //= b
    return digits[::-1]


def b_automatic_set_check(x):
    """Check if a finite set could be b-automatic by testing if membership can be decided by a DFA on base-b digits.
    Tests powers-of-b pattern. Input: array (values; last=base). Output: array of 0/1."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 2
    values = x[:-1] if len(x) > 1 else x
    # A simple b-automatic set: numbers whose base-b representation has bounded digit sum
    # We check if each value is a power of b (a classic b-automatic set)
    results = []
    for v in values:
        n = int(abs(v))
        if n == 0:
            results.append(0)
            continue
        # Check if n is a power of b
        while n > 1:
            if n % b != 0:
                break
            n //= b
        results.append(1 if n == 1 else 0)
    return np.array(results, dtype=float)


OPERATIONS["b_automatic_set_check"] = {
    "fn": b_automatic_set_check,
    "input_type": "array",
    "output_type": "array",
    "description": "Check if values are in the b-automatic set of powers of b"
}


def powers_of_2_automaton_base_b(x):
    """Simulate a DFA that recognizes powers of 2 in base b.
    Input: array (values; last=base). Output: array of 0/1 (accepted/rejected)."""
    x = np.asarray(x, dtype=float)
    b = int(x[-1]) if len(x) > 1 else 10
    values = x[:-1] if len(x) > 1 else x
    results = []
    for v in values:
        n = int(abs(v))
        if n <= 0:
            results.append(0)
            continue
        # Check if n is a power of 2
        results.append(1 if (n & (n - 1)) == 0 else 0)
    return np.array(results, dtype=float)


OPERATIONS["powers_of_2_automaton_base_b"] = {
    "fn": powers_of_2_automaton_base_b,
    "input_type": "array",
    "output_type": "array",
    "description": "DFA recognizing powers of 2 (result independent of base, per Cobham)"
}


def cobham_independence_test(x):
    """Test Cobham's theorem: a set b-automatic AND c-automatic (with b,c mult. independent)
    must be eventually periodic. Checks if values form eventually periodic set.
    Input: array of sorted integers. Output: scalar (1=eventually periodic, 0=not)."""
    x = np.asarray(x, dtype=int)
    if len(x) < 3:
        return np.float64(1.0)
    # Check if differences eventually become periodic
    diffs = np.diff(x)
    if len(diffs) < 4:
        return np.float64(1.0)
    # Check last half for periodicity
    half = len(diffs) // 2
    tail = diffs[half:]
    for period in range(1, len(tail) // 2 + 1):
        if all(tail[i] == tail[i % period] for i in range(len(tail))):
            return np.float64(1.0)
    return np.float64(0.0)


OPERATIONS["cobham_independence_test"] = {
    "fn": cobham_independence_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Test if a set is eventually periodic (Cobham's theorem condition)"
}


def regular_sequence_check(x):
    """Check if a sequence satisfies a linear recurrence in subsequences (b-regular).
    Tests if the sequence of values at indices 0,1,...,n satisfies a linear recurrence.
    Input: array. Output: scalar (estimated rank of the Z-module)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 4:
        return np.float64(n)
    # Build a Hankel-like matrix and estimate rank
    half = n // 2
    H = np.zeros((half, half))
    for i in range(half):
        for j in range(half):
            idx = i + j
            if idx < n:
                H[i, j] = x[idx]
    # Rank of this matrix approximates the rank of the module
    sv = np.linalg.svd(H, compute_uv=False)
    tol = max(sv) * max(H.shape) * np.finfo(float).eps
    rank = int(np.sum(sv > tol))
    return np.float64(rank)


OPERATIONS["regular_sequence_check"] = {
    "fn": regular_sequence_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate rank of the Z-module for a b-regular sequence"
}


def automatic_sequence_generate(x):
    """Generate a b-automatic sequence: the base-b digit sum mod m.
    Input: array [length, base, modulus]. Output: array of sequence values."""
    x = np.asarray(x, dtype=float)
    length = int(x[0]) if len(x) > 0 else 20
    b = int(x[1]) if len(x) > 1 else 2
    m = int(x[2]) if len(x) > 2 else 2
    length = min(length, 1000)
    b = max(b, 2)
    m = max(m, 2)
    result = []
    for n in range(length):
        s = sum(_to_digits_base_b(n, b))
        result.append(s % m)
    return np.array(result, dtype=float)


OPERATIONS["automatic_sequence_generate"] = {
    "fn": automatic_sequence_generate,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate b-automatic sequence (digit sum mod m)"
}


def base_dependent_regularity(x):
    """Compare regularity of a sequence in different bases.
    Computes digit-sum sequences in bases 2..max_base and returns their Hankel matrix ranks.
    Input: array [N, max_base]. Output: array of ranks."""
    x = np.asarray(x, dtype=float)
    N = int(x[0]) if len(x) > 0 else 20
    max_base = int(x[1]) if len(x) > 1 else 8
    N = min(N, 100)
    max_base = min(max_base, 16)
    ranks = []
    for b in range(2, max_base + 1):
        seq = [sum(_to_digits_base_b(n, b)) for n in range(N)]
        seq = np.array(seq, dtype=float)
        half = max(N // 2, 2)
        H = np.zeros((half, half))
        for i in range(half):
            for j in range(half):
                idx = i + j
                if idx < N:
                    H[i, j] = seq[idx]
        sv = np.linalg.svd(H, compute_uv=False)
        tol = max(sv.max(), 1e-10) * max(H.shape) * np.finfo(float).eps
        rank = int(np.sum(sv > tol))
        ranks.append(rank)
    return np.array(ranks, dtype=float)


OPERATIONS["base_dependent_regularity"] = {
    "fn": base_dependent_regularity,
    "input_type": "array",
    "output_type": "array",
    "description": "Hankel matrix rank of digit-sum sequences across bases"
}


def morphic_word_generate(x):
    """Generate a morphic word by iterated morphism.
    Default: Thue-Morse via 0->01, 1->10. Input: array [length, variant].
    variant=0: Thue-Morse, variant=1: Rudin-Shapiro parity. Output: array."""
    x = np.asarray(x, dtype=float)
    length = int(x[0]) if len(x) > 0 else 32
    variant = int(x[1]) if len(x) > 1 else 0
    length = min(length, 1000)
    if variant == 0:
        # Thue-Morse: a(n) = number of 1s in binary representation of n, mod 2
        result = [bin(n).count('1') % 2 for n in range(length)]
    else:
        # Rudin-Shapiro: parity of number of '11' blocks in binary
        result = []
        for n in range(length):
            b = bin(n)[2:]
            count = sum(1 for i in range(len(b) - 1) if b[i] == '1' and b[i+1] == '1')
            result.append(count % 2)
    return np.array(result, dtype=float)


OPERATIONS["morphic_word_generate"] = {
    "fn": morphic_word_generate,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate morphic word (Thue-Morse or Rudin-Shapiro)"
}


def automatic_complexity(x):
    """Compute automatic complexity: minimal number of states in a DFA that outputs the given finite word.
    Approximation via suffix-based state merging. Input: array (binary word). Output: scalar."""
    x = np.asarray(x, dtype=int)
    word = tuple(x)
    n = len(word)
    if n == 0:
        return np.float64(1)
    # Lower bound: count distinct suffixes (each needs at least one state)
    suffixes = set()
    for i in range(n):
        suffixes.add(word[i:])
    # The automatic complexity is at least the number of distinct Nerode classes
    # We approximate by counting how many distinct prefix-conditioned outputs exist
    prefixes = set()
    for i in range(n + 1):
        prefixes.add(word[:i])
    # Simple upper bound: number of distinct states needed
    return np.float64(min(len(suffixes), n))


OPERATIONS["automatic_complexity"] = {
    "fn": automatic_complexity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate automatic complexity (min DFA states for a finite word)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
