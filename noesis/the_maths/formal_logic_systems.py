"""
Formal Logic Systems — Boolean evaluation, modal logic, Gödel numbering, and model checking

Connects to: [proof_complexity, descriptive_complexity, automata_infinite_words]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "formal_logic_systems"
OPERATIONS = {}


def boolean_evaluate(x):
    """Evaluate array as conjunction of boolean values. Input: array. Output: scalar."""
    bits = (x > 0.5).astype(int)
    return float(np.all(bits))


OPERATIONS["boolean_evaluate"] = {
    "fn": boolean_evaluate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Evaluate array as conjunction (AND) of boolean values (>0.5 = True)"
}


def truth_table_generate(x):
    """Generate truth table for n variables (n = len(x), max 8). Input: array. Output: matrix."""
    n = min(len(x), 8)
    rows = 2 ** n
    table = np.zeros((rows, n), dtype=float)
    for i in range(rows):
        for j in range(n):
            table[i, j] = float((i >> (n - 1 - j)) & 1)
    return table


OPERATIONS["truth_table_generate"] = {
    "fn": truth_table_generate,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Generate all 2^n truth assignments for n boolean variables"
}


def kripke_frame_satisfies(x):
    """Check satisfaction in a Kripke frame. Interpret x as adjacency + valuation.
    Builds a small Kripke frame: n worlds, checks if world 0 satisfies 'possibly p'.
    Input: array. Output: scalar (0 or 1)."""
    n = len(x)
    # Build adjacency: world i accesses world (i+1) mod n if x[i] > 0
    # Valuation: p holds at world i if x[i] > 0.5
    valuation = x > 0.5
    # world 0 satisfies 'possibly p' iff some accessible world satisfies p
    # accessible from 0: world 1 (if x[0] > 0), plus self-loop if x[0] > 0.3
    accessible = []
    if n > 1 and x[0] > 0:
        accessible.append(1)
    if x[0] > 0.3:
        accessible.append(0)
    for w in accessible:
        if valuation[w]:
            return 1.0
    return 0.0


OPERATIONS["kripke_frame_satisfies"] = {
    "fn": kripke_frame_satisfies,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if world 0 satisfies 'possibly p' in a Kripke frame derived from input"
}


def modal_necessity(x):
    """Modal necessity (box): true at a world iff p true at ALL accessible worlds.
    Treat array as valuations; necessity holds iff all are true. Input: array. Output: scalar."""
    return float(np.all(x > 0.5))


OPERATIONS["modal_necessity"] = {
    "fn": modal_necessity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Modal necessity operator: 1 iff all values (worlds) satisfy p (>0.5)"
}


def modal_possibility(x):
    """Modal possibility (diamond): true iff p true at SOME accessible world.
    Input: array. Output: scalar."""
    return float(np.any(x > 0.5))


OPERATIONS["modal_possibility"] = {
    "fn": modal_possibility,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Modal possibility operator: 1 iff any value (world) satisfies p (>0.5)"
}


def godel_number_encode(x):
    """Gödel numbering: encode array as product of primes raised to element powers.
    Uses first n primes. Input: array. Output: scalar."""
    # Generate enough primes via simple sieve
    def primes_up_to(limit):
        sieve = np.ones(limit + 1, dtype=bool)
        sieve[0] = sieve[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                sieve[i*i::i] = False
        return np.where(sieve)[0]

    n = len(x)
    ps = primes_up_to(max(100, n * 10))[:n]
    # Use log to avoid overflow: log(product(p_i^x_i)) = sum(x_i * log(p_i))
    vals = np.abs(np.round(x)).astype(int)
    vals = np.clip(vals, 0, 10)
    log_result = np.sum(vals * np.log(ps.astype(float)))
    return float(log_result)


OPERATIONS["godel_number_encode"] = {
    "fn": godel_number_encode,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Gödel encode: return log of product(p_i^x_i) for primes p_i"
}


def godel_number_decode(x):
    """Decode a Gödel number (first element) into prime exponents.
    Input: array (uses x[0]). Output: array of exponents."""
    num = int(abs(round(x[0])))
    if num < 2:
        return np.array([0.0])
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    exponents = []
    for p in primes:
        exp = 0
        while num % p == 0:
            exp += 1
            num //= p
        exponents.append(float(exp))
        if num == 1:
            break
    return np.array(exponents)


OPERATIONS["godel_number_decode"] = {
    "fn": godel_number_decode,
    "input_type": "array",
    "output_type": "array",
    "description": "Decode a Gödel number into its prime factorization exponents"
}


def propositional_resolution(x):
    """Apply resolution to a set of clauses encoded in x.
    Even indices = positive literals, odd = negative. Count resolvable pairs.
    Input: array. Output: scalar (number of resolution steps possible)."""
    n = len(x)
    pos = set()
    neg = set()
    for i in range(n):
        lit = int(round(x[i])) % 16
        if i % 2 == 0:
            pos.add(lit)
        else:
            neg.add(lit)
    resolvents = len(pos & neg)
    return float(resolvents)


OPERATIONS["propositional_resolution"] = {
    "fn": propositional_resolution,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count resolution steps possible between positive and negative literal sets"
}


def first_order_model_check(x):
    """Simple first-order model check: given domain elements x, check if
    a universal property holds (all elements satisfy predicate > mean).
    Input: array. Output: scalar (0 or 1)."""
    mean_val = np.mean(x)
    return float(np.all(x >= mean_val))


OPERATIONS["first_order_model_check"] = {
    "fn": first_order_model_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if universal property 'forall x: x >= mean' holds over domain"
}


def tautology_check(x):
    """Check if a boolean function (given by truth table outputs) is a tautology.
    Input: array of truth values. Output: scalar (1 if tautology, 0 otherwise)."""
    return float(np.all(x > 0.5))


OPERATIONS["tautology_check"] = {
    "fn": tautology_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if all truth values are true (tautology)"
}


def intuitionistic_logic_check(x):
    """Check double negation elimination failure (intuitionistic logic).
    In intuitionistic logic, not-not-p does not imply p.
    Given p-values in x, check how many satisfy p != not-not-p under
    a 3-valued Heyting algebra {0, 0.5, 1}. Input: array. Output: scalar."""
    # Discretize to 3-valued: 0, 0.5, 1
    vals = np.round(x * 2) / 2.0
    vals = np.clip(vals, 0, 1)
    # In Heyting algebra on {0, 0.5, 1}: not(0)=1, not(0.5)=0, not(1)=0
    def heyting_not(v):
        if v <= 0:
            return 1.0
        else:
            return 0.0
    neg = np.vectorize(heyting_not)(vals)
    double_neg = np.vectorize(heyting_not)(neg)
    # Count where double negation != original (DNE fails)
    failures = np.sum(np.abs(double_neg - vals) > 0.01)
    return float(failures)


OPERATIONS["intuitionistic_logic_check"] = {
    "fn": intuitionistic_logic_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count elements where double-negation elimination fails in Heyting algebra"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
