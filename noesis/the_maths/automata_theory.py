"""
Automata Theory — DFA minimization, NFA→DFA conversion, regular expression matching

Connects to: [graph_theory, linear_algebra, information_theory, lambda_calculus]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "automata_theory"
OPERATIONS = {}


def dfa_accepts_string(x):
    """Simulate a DFA on an input string encoded as array of state indices.
    Uses array as transition sequence through states. The DFA has n states
    (n = len(x)), transitions are determined by values mod n.
    Input: array. Output: integer (1 if accepts, 0 if rejects)."""
    n = len(x)
    if n == 0:
        return 0
    # Build a simple DFA: states 0..n-1, accepting state = last state
    # Transitions: from state s, input x[i] -> state int(x[i]) % n
    state = 0
    for val in x:
        state = int(abs(val)) % n
    # Accept if we end in the last state
    return int(state == n - 1)


OPERATIONS["dfa_accepts_string"] = {
    "fn": dfa_accepts_string,
    "input_type": "array",
    "output_type": "integer",
    "description": "Simulates a DFA on input array as transition sequence, returns 1 if accepting"
}


def dfa_minimize_partition(x):
    """Compute partition refinement for DFA minimization.
    Given array representing state outputs, returns number of distinguishable
    equivalence classes (Myhill-Nerode classes).
    Input: array. Output: integer."""
    # Distinct values in the array represent distinct equivalence classes
    # This is the core of Hopcroft's partition refinement
    unique_vals = np.unique(np.round(x, decimals=6))
    return int(len(unique_vals))


OPERATIONS["dfa_minimize_partition"] = {
    "fn": dfa_minimize_partition,
    "input_type": "array",
    "output_type": "integer",
    "description": "Counts distinguishable state classes via partition refinement"
}


def nfa_epsilon_closure(x):
    """Compute epsilon closure from adjacency-like representation.
    Treats array as adjacency flags for epsilon transitions from state 0.
    Returns array of reachable states (1 = reachable, 0 = not).
    Input: array. Output: array."""
    n = len(x)
    # Build epsilon transition: state i has epsilon to state (i+1) % n if x[i] > 0
    reachable = np.zeros(n)
    reachable[0] = 1.0
    # BFS/fixed-point for epsilon closure
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if reachable[i] == 1.0 and x[i] > 0:
                target = (i + 1) % n
                if reachable[target] == 0.0:
                    reachable[target] = 1.0
                    changed = True
    return reachable


OPERATIONS["nfa_epsilon_closure"] = {
    "fn": nfa_epsilon_closure,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes epsilon closure of state 0 given epsilon-transition flags"
}


def regular_language_pumping(x):
    """Estimate the pumping length for a regular language.
    For a DFA with n states, the pumping length is at most n.
    Input: array (representing states). Output: integer."""
    return int(len(x))


OPERATIONS["regular_language_pumping"] = {
    "fn": regular_language_pumping,
    "input_type": "array",
    "output_type": "integer",
    "description": "Returns the pumping length bound (number of states) for a regular language"
}


def state_reachability_matrix(x):
    """Build state reachability matrix from array.
    Constructs a transition graph and computes transitive closure.
    Input: array. Output: matrix."""
    n = len(x)
    # Build adjacency: state i -> state int(|x[i]|) % n
    adj = np.zeros((n, n))
    for i in range(n):
        target = int(abs(x[i])) % n
        adj[i, target] = 1.0
    # Transitive closure via Warshall's algorithm
    reach = adj.copy()
    for i in range(n):
        reach[i, i] = 1.0  # self-reachable
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i, k] and reach[k, j]:
                    reach[i, j] = 1.0
    return reach


OPERATIONS["state_reachability_matrix"] = {
    "fn": state_reachability_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Computes transitive closure reachability matrix for automaton states"
}


def transition_matrix_power(x):
    """Raise the transition matrix to the power len(x).
    Builds a stochastic transition matrix from the array, then computes
    its n-th power to find n-step transition probabilities.
    Input: array. Output: matrix."""
    n = len(x)
    # Build stochastic matrix: row i has weight at column int(|x[i]|) % n
    T = np.zeros((n, n))
    for i in range(n):
        target = int(abs(x[i])) % n
        T[i, target] = 1.0
    # Raise to power n
    result = np.linalg.matrix_power(T.astype(int), n).astype(float)
    return result


OPERATIONS["transition_matrix_power"] = {
    "fn": transition_matrix_power,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Computes n-step transition matrix by raising transition matrix to n-th power"
}


def automaton_entropy(x):
    """Compute the topological entropy of the automaton.
    Entropy = log of the spectral radius of the adjacency matrix.
    Input: array. Output: scalar."""
    n = len(x)
    # Build adjacency matrix
    adj = np.zeros((n, n))
    for i in range(n):
        target = int(abs(x[i])) % n
        adj[i, target] = 1.0
    eigenvalues = np.abs(np.linalg.eigvals(adj))
    spectral_radius = np.max(eigenvalues)
    if spectral_radius <= 0:
        return 0.0
    return float(np.log(spectral_radius))


OPERATIONS["automaton_entropy"] = {
    "fn": automaton_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes topological entropy as log of spectral radius of adjacency matrix"
}


def dfa_complement_accepts(x):
    """Check if the complement DFA accepts the input.
    The complement DFA accepts iff the original rejects.
    Input: array. Output: integer."""
    return 1 - dfa_accepts_string(x)


OPERATIONS["dfa_complement_accepts"] = {
    "fn": dfa_complement_accepts,
    "input_type": "array",
    "output_type": "integer",
    "description": "Returns 1 if the complement DFA accepts (original rejects)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
