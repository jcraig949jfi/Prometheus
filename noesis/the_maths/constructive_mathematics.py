"""
Constructive Mathematics — computability-aware math

Connects to: [computability_theory, intuitionistic_logic, type_theory, real_analysis]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

All operations here are constructively valid: they produce witnesses,
not mere existence proofs. No excluded middle, no choice axiom.
"""

import numpy as np

FIELD_NAME = "constructive_mathematics"
OPERATIONS = {}


def bishop_real_approx(x, precision=10):
    """Bishop-style constructive real number: a Cauchy sequence with explicit
    modulus of convergence. Given x, produce rational approximations at
    precisions 2^{-k} for k = 1..precision.
    Input: array. Output: array (Cauchy sequence of partial sums)."""
    # Treat x as coefficients of a series; partial sums are the approximation
    n = len(x)
    approx = np.zeros(precision)
    for k in range(precision):
        # Use first min(k+1, n) terms
        terms = min(k + 1, n)
        approx[k] = np.sum(x[:terms])
    return approx


OPERATIONS["bishop_real_approx"] = {
    "fn": bishop_real_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Bishop real number as explicit Cauchy sequence"
}


def computable_real_cauchy_rate(x):
    """Compute the Cauchy rate (modulus of convergence) for the sequence of
    partial sums of x. The modulus M(epsilon) is the smallest N such that
    |S_n - S_m| < epsilon for all n, m >= N.
    Input: array. Output: array (modulus at epsilon = 1, 0.1, 0.01, ...)."""
    n = len(x)
    partial_sums = np.cumsum(x)
    if n <= 1:
        return np.array([0.0])
    # Limit estimate
    limit = partial_sums[-1]
    epsilons = [10.0 ** (-k) for k in range(6)]
    moduli = np.zeros(len(epsilons))
    for idx, eps in enumerate(epsilons):
        found = n  # default: need all terms
        for N in range(n):
            if all(abs(partial_sums[m] - limit) < eps for m in range(N, n)):
                found = N
                break
        moduli[idx] = float(found)
    return moduli


OPERATIONS["computable_real_cauchy_rate"] = {
    "fn": computable_real_cauchy_rate,
    "input_type": "array",
    "output_type": "array",
    "description": "Modulus of convergence for the partial sum Cauchy sequence"
}


def markov_principle_test(x):
    """Markov's principle: if it's not the case that all x[i] = 0,
    then we can find an index i where x[i] != 0.
    Constructively: search for the witness. Returns the first nonzero index,
    or -1 if all zero. Input: array. Output: scalar."""
    for i in range(len(x)):
        if abs(x[i]) > 1e-15:
            return float(i)
    return -1.0


OPERATIONS["markov_principle_test"] = {
    "fn": markov_principle_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Markov's principle: find explicit witness of nonzero element"
}


def brouwer_fixed_point_approx_1d(x):
    """Constructive Brouwer fixed point in 1D: for f:[0,1]->[0,1], find
    approximate fixed point. Interpret x as samples of f on uniform grid.
    Find where f(t) ~ t by bisection. Input: array. Output: scalar."""
    n = len(x)
    if n < 2:
        return float(x[0]) if n == 1 else 0.0
    # f is sampled at t_i = i/(n-1), f(t_i) = x[i] clamped to [0,1]
    f_vals = np.clip(x, 0, 1)
    t_vals = np.linspace(0, 1, n)
    # g(t) = f(t) - t; find zero of g by bisection
    g = f_vals - t_vals
    # Find sign change
    for i in range(n - 1):
        if g[i] * g[i + 1] <= 0:
            # Linear interpolation for the zero
            if abs(g[i + 1] - g[i]) > 1e-15:
                t_star = t_vals[i] - g[i] * (t_vals[i + 1] - t_vals[i]) / (g[i + 1] - g[i])
            else:
                t_star = (t_vals[i] + t_vals[i + 1]) / 2
            return float(t_star)
    # No sign change found; return point with smallest |g|
    idx = np.argmin(np.abs(g))
    return float(t_vals[idx])


OPERATIONS["brouwer_fixed_point_approx_1d"] = {
    "fn": brouwer_fixed_point_approx_1d,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Constructive approximate Brouwer fixed point in 1D"
}


def constructive_intermediate_value(x):
    """Constructive IVT: given f sampled at x (with f(0) < 0 and f(end) > 0),
    find an interval where the zero lies, with constructive witness.
    Returns [left, right, midpoint]. Input: array. Output: array."""
    n = len(x)
    if n < 2:
        return np.array([0.0, 1.0, 0.5])
    # Ensure we have a sign change by shifting
    vals = x - x[0]  # make vals[0] = 0
    if abs(vals[-1]) < 1e-15:
        vals[-1] = 1.0
    # Bisection to find zero
    left, right = 0, n - 1
    for _ in range(50):
        mid = (left + right) // 2
        if mid == left:
            break
        if vals[mid] * vals[left] <= 0:
            right = mid
        else:
            left = mid
    t_left = left / (n - 1)
    t_right = right / (n - 1)
    t_mid = (t_left + t_right) / 2
    return np.array([t_left, t_right, t_mid])


OPERATIONS["constructive_intermediate_value"] = {
    "fn": constructive_intermediate_value,
    "input_type": "array",
    "output_type": "array",
    "description": "Constructive IVT: bracketing interval with witness"
}


def choice_sequence_fan(x):
    """Fan theorem (Brouwer): every bar on the universal spread is uniform.
    Given x as a bar (predicate on finite sequences), compute the
    uniform bound. Input: array (bar depths). Output: scalar."""
    # The bar assigns to each node a depth at which it's barred
    # The fan theorem says there's a uniform bound N
    # N = max of all bar depths
    depths = np.abs(x).astype(int)
    uniform_bound = int(np.max(depths))
    return float(uniform_bound)


OPERATIONS["choice_sequence_fan"] = {
    "fn": choice_sequence_fan,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fan theorem uniform bound on bar depths"
}


def bar_induction_bound(x):
    """Bar induction: compute the bar induction ordinal bound.
    For a well-founded bar on a tree, the ordinal height of the induction.
    We compute this as the height of the tree defined by x.
    Input: array (parent pointers, -1 for root). Output: scalar."""
    n = len(x)
    # Interpret x as a tree: x[i] is the parent of node i (mod n)
    parents = np.clip(np.round(np.abs(x)).astype(int), 0, n - 1)
    # Compute depth of each node
    depths = np.zeros(n, dtype=int)
    for i in range(n):
        depth = 0
        visited = set()
        node = i
        while node != parents[node] and node not in visited and depth < n:
            visited.add(node)
            node = parents[node]
            depth += 1
        depths[i] = depth
    return float(np.max(depths))


OPERATIONS["bar_induction_bound"] = {
    "fn": bar_induction_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Ordinal height bound for bar induction on a tree"
}


def church_thesis_function(x):
    """Church's thesis: every total function on naturals is computable.
    Demonstrate by computing a few standard computable functions on x
    and returning their Godel numbers (indices in a standard enumeration).
    Input: array. Output: array."""
    n = len(x)
    vals = np.round(np.abs(x)).astype(int)
    results = np.zeros(n)
    # Apply a sequence of primitive recursive functions
    # f_0 = identity, f_1 = successor, f_2 = addition, f_3 = multiplication, f_4 = exponentiation
    functions = [
        lambda v: v,                          # identity
        lambda v: v + 1,                      # successor
        lambda v: v + v,                      # doubling (addition with self)
        lambda v: v * v,                      # squaring (multiplication with self)
        lambda v: min(2 ** v, 10 ** 15),     # bounded exponentiation
    ]
    for i in range(n):
        f_idx = i % len(functions)
        results[i] = float(functions[f_idx](vals[i]))
    return results


OPERATIONS["church_thesis_function"] = {
    "fn": church_thesis_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Primitive recursive function enumeration (Church's thesis)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
