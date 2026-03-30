"""
Automata on Infinite Words — Büchi automata, Muller automata, omega-regular languages, parity games

Connects to: [formal_logic_systems, descriptive_complexity, reversible_computing]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "automata_infinite_words"
OPERATIONS = {}


def buchi_acceptance_check(x):
    """Check Büchi acceptance: does the input (as an ultimately periodic word)
    visit an accepting state infinitely often?
    Treat states as rounded values mod n_states; accepting state = 0.
    Input: array (word). Output: scalar (0 or 1)."""
    n_states = max(int(np.max(np.abs(x))) + 1, 2)
    states = np.round(np.abs(x)).astype(int) % n_states
    # Accepting state = 0. Check if 0 appears in the periodic part (second half).
    half = len(states) // 2
    periodic_part = states[half:]
    return float(0 in periodic_part)


OPERATIONS["buchi_acceptance_check"] = {
    "fn": buchi_acceptance_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Büchi acceptance: does accepting state appear in periodic part of word"
}


def buchi_emptiness_check(x):
    """Check Büchi automaton emptiness via cycle detection.
    Build a small automaton from x: n states, transition i->j if x[i] encodes j.
    Non-empty iff there's a reachable cycle through an accepting state.
    Input: array. Output: scalar (1 if non-empty, 0 if empty)."""
    n = len(x)
    if n == 0:
        return 0.0
    # Transition: state i goes to state round(abs(x[i])) mod n
    trans = np.round(np.abs(x)).astype(int) % n
    # Accepting state = 0
    # Check if state 0 is on a reachable cycle from state 0
    visited = set()
    current = 0
    for _ in range(2 * n):
        if current in visited and current == 0:
            return 1.0
        visited.add(current)
        current = trans[current]
    if current == 0:
        return 1.0
    return 0.0


OPERATIONS["buchi_emptiness_check"] = {
    "fn": buchi_emptiness_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Büchi emptiness: 1 if accepting state is on a reachable cycle, 0 if empty"
}


def muller_to_buchi_states(x):
    """Convert Muller automaton to Büchi: estimate state blowup.
    Safra's construction: Muller with n states -> Büchi with O(n! * 2^n) states.
    Return log2 of estimated Büchi state count. Input: array (n = len = #states). Output: scalar."""
    n = len(x)
    # Safra's determinization: O((2n)^n) states
    # log2((2n)^n) = n * log2(2n)
    if n <= 0:
        return 0.0
    log_states = n * np.log2(2 * n)
    return float(log_states)


OPERATIONS["muller_to_buchi_states"] = {
    "fn": muller_to_buchi_states,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Log2 of state count for Muller-to-Büchi via Safra construction"
}


def omega_regular_complement_size(x):
    """Estimate complement automaton size for omega-regular language.
    Complementation of nondeterministic Büchi: O((0.76n)^n) states (Schewe tight bound).
    Return log2. Input: array (n = len = #states). Output: scalar."""
    n = max(len(x), 1)
    # Schewe's tight bound: (0.76n)^n
    log_complement = n * np.log2(0.76 * n) if n > 1 else 1.0
    return float(max(log_complement, 0.0))


OPERATIONS["omega_regular_complement_size"] = {
    "fn": omega_regular_complement_size,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Log2 of complemented Büchi automaton size (Schewe bound)"
}


def parity_game_solve(x):
    """Solve a parity game: determine winner for each node.
    Encode: x[i] = priority of node i; edges: i -> (i+1) mod n.
    Player 0 wins if min infinitely-visited priority is even.
    On a cycle, all are visited; winner = parity of min priority.
    Input: array. Output: array (0 = player 0 wins, 1 = player 1 wins)."""
    priorities = np.round(np.abs(x)).astype(int)
    min_priority = np.min(priorities)
    # On a single cycle, winner everywhere is determined by min priority parity
    winner = float(min_priority % 2)
    return np.full(len(x), winner)


OPERATIONS["parity_game_solve"] = {
    "fn": parity_game_solve,
    "input_type": "array",
    "output_type": "array",
    "description": "Solve parity game on cycle graph: winner by min priority parity"
}


def rabin_chain_index(x):
    """Compute the Rabin chain index (number of Rabin pairs needed).
    For a parity condition with priorities 0..k, the Rabin index is ceil(k/2).
    Input: array (priorities). Output: scalar."""
    k = int(np.max(np.round(np.abs(x))))
    index = (k + 1) // 2  # ceil(k/2) for 0-indexed priorities
    return float(max(index, 1))


OPERATIONS["rabin_chain_index"] = {
    "fn": rabin_chain_index,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rabin chain index: ceil(max_priority / 2)"
}


def buchi_intersection_product(x):
    """Compute product automaton size for Büchi intersection.
    Intersection of two Büchi automata with n1, n2 states: product has O(n1 * n2 * 2) states
    (extra factor 2 for acceptance tracking). Split x in half for two automata sizes.
    Input: array. Output: scalar."""
    n = len(x)
    n1 = max(n // 2, 1)
    n2 = max(n - n1, 1)
    product_size = n1 * n2 * 2  # factor 2 for Büchi acceptance counter
    return float(product_size)


OPERATIONS["buchi_intersection_product"] = {
    "fn": buchi_intersection_product,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Product automaton state count for Büchi intersection"
}


def ultimately_periodic_check(x):
    """Check if array represents an ultimately periodic word.
    Find shortest period p in the second half of x.
    Input: array. Output: scalar (period length, 0 if not periodic)."""
    n = len(x)
    if n < 2:
        return float(n)
    half = n // 2
    tail = x[half:]
    m = len(tail)
    for p in range(1, m // 2 + 1):
        is_periodic = True
        for i in range(p, m):
            if abs(tail[i] - tail[i % p]) > 1e-10:
                is_periodic = False
                break
        if is_periodic:
            return float(p)
    return 0.0  # Not periodic


OPERATIONS["ultimately_periodic_check"] = {
    "fn": ultimately_periodic_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Find shortest period in the tail of the word (0 if not periodic)"
}


def omega_word_prefix_period(x):
    """Decompose an ultimately periodic omega-word into prefix length and period length.
    Returns array [prefix_len, period_len].
    Input: array. Output: array."""
    n = len(x)
    # Try each possible prefix/period split
    for prefix_len in range(0, n // 2):
        tail = x[prefix_len:]
        m = len(tail)
        for p in range(1, m // 2 + 1):
            is_periodic = True
            for i in range(p, m):
                if abs(tail[i] - tail[i % p]) > 1e-10:
                    is_periodic = False
                    break
            if is_periodic:
                return np.array([float(prefix_len), float(p)])
    return np.array([float(n), 0.0])  # No periodicity found


OPERATIONS["omega_word_prefix_period"] = {
    "fn": omega_word_prefix_period,
    "input_type": "array",
    "output_type": "array",
    "description": "Decompose word into (prefix_length, period_length)"
}


def zielonka_tree_depth(x):
    """Compute Zielonka tree depth for a Muller acceptance condition.
    The Zielonka tree alternates between accepting and rejecting levels.
    Depth ~ number of distinct priorities. Input: array (priorities). Output: scalar."""
    priorities = np.unique(np.round(np.abs(x)).astype(int))
    return float(len(priorities))


OPERATIONS["zielonka_tree_depth"] = {
    "fn": zielonka_tree_depth,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Zielonka tree depth: number of distinct priority levels"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
