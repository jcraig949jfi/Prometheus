"""
Ordinal Arithmetic — transfinite ordinal operations via finite approximations

Connects to: [set theory, proof theory, computability, well-orderings, cardinal arithmetic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "ordinal_arithmetic"
OPERATIONS = {}


def ordinal_add(x):
    """Ordinal addition (finite approximation). For transfinite ordinals, addition is
    NOT commutative: omega + 1 != 1 + omega. We represent ordinals as arrays of
    Cantor normal form coefficients. Input: array (split in half: a + b).
    Output: array (CNF of sum)."""
    n = len(x) // 2
    if n == 0:
        return x.copy()
    a = np.abs(x[:n])
    b = np.abs(x[n:2 * n])
    # Ordinal addition: omega^a1*c1 + ... + omega^b1*d1 + ...
    # In CNF, a + b = b if b has a term with exponent >= max exponent of a
    # For finite ordinals (exponent 0), addition is just regular addition
    # We simulate: concatenate and merge terms with same exponent
    # Treat index as exponent (higher index = higher power of omega)
    result = np.zeros(n)
    # b's highest terms dominate a's lower terms (ordinal absorption)
    max_b_exp = 0
    for i in range(n - 1, -1, -1):
        if b[i] > 0:
            max_b_exp = i
            break
    # Terms of a with exponent > max_b_exp survive; others are absorbed
    for i in range(n):
        if i > max_b_exp:
            result[i] = a[i]  # Higher terms from a survive
        else:
            result[i] = b[i]  # Lower terms replaced by b
    # The highest surviving a-terms plus all of b
    for i in range(max_b_exp + 1, n):
        result[i] += a[i]
    return result


OPERATIONS["ordinal_add"] = {
    "fn": ordinal_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Ordinal addition respecting non-commutativity and absorption"
}


def ordinal_multiply(x):
    """Ordinal multiplication (finite approximation). omega * 2 = omega + omega,
    but 2 * omega = omega. Input: array (split in half: a * b).
    Output: array (CNF of product)."""
    n = len(x) // 2
    if n == 0:
        return x.copy()
    a = np.abs(x[:n])
    b = np.abs(x[n:2 * n])
    # For CNF terms: (omega^alpha * m) * (omega^beta * n) = omega^(alpha+beta) * (m*n if beta=0, else n)
    # Simplified: multiply the "ordinal magnitudes"
    result = np.zeros(n)
    # Find highest nonzero exponent in each
    max_a = max((i for i in range(n) if a[i] > 0), default=0)
    max_b = max((i for i in range(n) if b[i] > 0), default=0)
    # Product exponent = max_a + max_b (ordinal exponent addition)
    prod_exp = min(max_a + max_b, n - 1)
    # Coefficient: if b has transfinite part (max_b > 0), a's coefficient is absorbed
    if max_b > 0:
        result[prod_exp] = b[max_b]
    else:
        result[prod_exp] = a[max_a] * b[0]
    return result


OPERATIONS["ordinal_multiply"] = {
    "fn": ordinal_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Ordinal multiplication with absorption (non-commutative)"
}


def ordinal_exponentiate(x):
    """Ordinal exponentiation (finite approximation). omega^omega, omega^(omega^omega), etc.
    Input: array [base_exp, power_exp] as CNF exponents. Output: array (CNF of result)."""
    n = len(x)
    base_exp = int(np.abs(x[0])) if n > 0 else 1
    power_exp = int(np.abs(x[1])) if n > 1 else 1
    base_exp = min(base_exp, 10)
    power_exp = min(power_exp, 10)
    # omega^(omega^a) raised to omega^b = omega^(omega^a * omega^b) = omega^(omega^(a+b)) if a,b > 0
    # For finite base n: n^omega = omega
    # For omega^alpha base: (omega^alpha)^beta = omega^(alpha * beta)
    result = np.zeros(n)
    result_exp = min(base_exp * max(power_exp, 1), n - 1)
    result[result_exp] = 1.0
    return result


OPERATIONS["ordinal_exponentiate"] = {
    "fn": ordinal_exponentiate,
    "input_type": "array",
    "output_type": "array",
    "description": "Ordinal exponentiation using CNF exponent multiplication"
}


def cantor_normal_form(x):
    """Convert a 'number' to Cantor Normal Form representation.
    Every ordinal alpha = omega^{beta_1}*c_1 + omega^{beta_2}*c_2 + ... where beta_1 > beta_2 > ...
    For finite numbers, CNF is just the number itself (omega^0 * n).
    Input: array (treated as mixed-radix number). Output: array (CNF coefficients)."""
    # Use the array values as coefficients in a base-omega expansion
    # Normalize: each position i represents omega^i coefficient
    n = len(x)
    cnf = np.abs(x).copy()
    # "Carry" operation: if coefficient >= omega (we use 10 as finite omega),
    # carry to next position
    omega_approx = 10
    for i in range(n - 1):
        if cnf[i] >= omega_approx:
            carry = int(cnf[i]) // omega_approx
            cnf[i] = cnf[i] % omega_approx
            cnf[i + 1] += carry
    return cnf


OPERATIONS["cantor_normal_form"] = {
    "fn": cantor_normal_form,
    "input_type": "array",
    "output_type": "array",
    "description": "Converts array to Cantor Normal Form with base-omega carries"
}


def epsilon_naught_approx(x):
    """Approximate epsilon_0, the smallest ordinal where omega^epsilon = epsilon.
    Build the sequence: a_0=1, a_{n+1} = omega^{a_n}. This converges to epsilon_0.
    Input: array (number of iterations from each starting point). Output: array."""
    n = len(x)
    results = np.zeros(n)
    for i in range(n):
        steps = min(int(np.abs(x[i])) + 1, 20)
        # Iterate a_{n+1} = omega^{a_n} using finite omega approximation
        # In log scale: log(a_{n+1}) = a_n * log(omega)
        omega = 10.0  # Finite stand-in
        val = 1.0
        for _ in range(steps):
            val = omega ** min(val, 15)  # Cap to prevent overflow
            if val > 1e15:
                val = 1e15
                break
        results[i] = np.log10(val)  # Return in log scale
    return results


OPERATIONS["epsilon_naught_approx"] = {
    "fn": epsilon_naught_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximates epsilon_0 via iterated exponentiation tower"
}


def ordinal_successor(x):
    """Compute the successor ordinal for each element. S(alpha) = alpha + 1.
    In CNF, this adds 1 to the omega^0 coefficient.
    Input: array (CNF coefficients). Output: array."""
    result = np.abs(x).copy()
    # Successor adds 1 to the omega^0 term
    result[0] = result[0] + 1
    return result


OPERATIONS["ordinal_successor"] = {
    "fn": ordinal_successor,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes successor ordinal by incrementing the omega^0 coefficient"
}


def veblen_function(x):
    """Approximate the Veblen function phi_alpha(beta).
    phi_0(beta) = omega^beta, phi_1(beta) = epsilon_beta,
    phi_2(beta) = the beta-th critical point of phi_1, etc.
    Input: array [alpha, beta, ...extra ignored]. Output: array."""
    n = len(x)
    alpha = int(np.abs(x[0])) if n > 0 else 0
    beta = int(np.abs(x[1])) if n > 1 else 0
    alpha = min(alpha, 5)
    beta = min(beta, 10)

    result = np.zeros(n)
    if alpha == 0:
        # phi_0(beta) = omega^beta, represented as CNF with 1 at position beta
        pos = min(beta, n - 1)
        result[pos] = 1.0
    elif alpha == 1:
        # phi_1(beta) = epsilon_beta. Approximate as iterated tower height
        # Track in pure log-log scale to avoid overflow entirely
        # height = number of times we can take log10 before reaching < 1
        tower_height = float(beta + 5)
        result[0] = tower_height
    else:
        # Higher Veblen functions: even faster growing
        # Represent as tower height * alpha
        tower_height = float(alpha * (beta + 1))
        result[0] = tower_height
    return result


OPERATIONS["veblen_function"] = {
    "fn": veblen_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximates Veblen hierarchy phi_alpha(beta) in log-scale"
}


def goodstein_sequence_step(x):
    """Compute one step of the Goodstein sequence.
    Goodstein's theorem: every Goodstein sequence terminates (unprovable in PA!).
    Step: write n in hereditary base b, bump base to b+1, subtract 1.
    Input: array [n, base]. Output: array [new_n, new_base]."""
    n_val = int(np.abs(x[0])) if len(x) > 0 else 4
    base = int(np.abs(x[1])) if len(x) > 1 else 2
    base = max(base, 2)
    n_val = min(n_val, 10000)  # Cap for performance

    # Write n in hereditary base-b representation
    # Then replace b with b+1 and subtract 1
    def hereditary_represent(n, b):
        """Represent n in hereditary base b: returns list of (coeff, exponent) pairs."""
        if n == 0:
            return []
        if n < b:
            return [(n, 0)]
        digits = []
        power = 0
        temp = n
        while temp > 0:
            digit = temp % b
            if digit > 0:
                digits.append((digit, power))
            temp //= b
            power += 1
        return digits

    def hereditary_eval(digits, b):
        """Evaluate hereditary base-b representation in base b."""
        total = 0
        for coeff, exp in digits:
            total += coeff * (b ** exp)
        return total

    representation = hereditary_represent(n_val, base)
    # Bump base: replace b with b+1
    new_val = hereditary_eval(representation, base + 1) - 1
    new_val = max(new_val, 0)

    result = np.zeros(len(x))
    result[0] = float(new_val)
    if len(x) > 1:
        result[1] = float(base + 1)
    # Fill rest with sequence info
    for i in range(2, len(x)):
        result[i] = x[i]
    return result


OPERATIONS["goodstein_sequence_step"] = {
    "fn": goodstein_sequence_step,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes one Goodstein sequence step (hereditary base change minus 1)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
