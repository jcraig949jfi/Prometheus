"""
Juggling Mathematics -- Siteswap notation, state transition graphs, orbit enumeration

Connects to: [combinatorial_species, automata_theory, symbolic_dynamics, finite_fields]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "juggling_mathematics"
OPERATIONS = {}


def siteswap_valid(x):
    """Check if a siteswap pattern is valid (no two balls land at the same time).
    Input: array (throw heights as integers). Output: scalar (1 valid, 0 invalid)."""
    throws = np.round(np.abs(x)).astype(int)
    n = len(throws)
    if n == 0:
        return 1.0
    # A siteswap is valid iff {(i + t_i) mod n : i=0..n-1} is a permutation of {0..n-1}
    landing_times = set()
    for i in range(n):
        landing = (i + throws[i]) % n
        if landing in landing_times:
            return 0.0
        landing_times.add(landing)
    return 1.0


OPERATIONS["siteswap_valid"] = {
    "fn": siteswap_valid,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if siteswap pattern is valid (landing permutation test)"
}


def siteswap_period(x):
    """Period of the siteswap pattern. Input: array. Output: scalar."""
    return float(len(x))


OPERATIONS["siteswap_period"] = {
    "fn": siteswap_period,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Period (length) of the siteswap pattern"
}


def siteswap_num_balls(x):
    """Number of balls in a siteswap: average of throw heights.
    Input: array. Output: scalar."""
    throws = np.round(np.abs(x)).astype(int)
    if len(throws) == 0:
        return 0.0
    return float(np.mean(throws))


OPERATIONS["siteswap_num_balls"] = {
    "fn": siteswap_num_balls,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of balls = average throw height"
}


def siteswap_state_vector(x):
    """Compute the juggling state (landing schedule) from a siteswap.
    Input: array. Output: array (binary state vector)."""
    throws = np.round(np.abs(x)).astype(int)
    n = len(throws)
    if n == 0:
        return np.array([0.0])
    max_height = max(int(np.max(throws)), n)
    state = np.zeros(max_height + 1)
    # Simulate the pattern: after one full period, what's the landing schedule?
    for i in range(n):
        t = throws[i]
        if t > 0:
            landing = (i + t)
            if landing < len(state):
                state[landing] = 1.0
    # The state is the landing schedule relative to current beat
    # Return the first n+max_throw positions
    return state[:max(n, int(np.max(throws)) + 1)]


OPERATIONS["siteswap_state_vector"] = {
    "fn": siteswap_state_vector,
    "input_type": "array",
    "output_type": "array",
    "description": "Juggling state vector (landing schedule)"
}


def siteswap_transition_matrix(x):
    """Build transition matrix for siteswap states.
    For b balls and max throw h, states are binary vectors of length h with b ones.
    Returns flattened transition matrix for small cases. Input: array. Output: array."""
    throws = np.round(np.abs(x)).astype(int)
    b = int(np.round(np.mean(throws))) if len(throws) > 0 else 3
    b = min(b, 5)  # cap for efficiency
    h = min(int(np.max(throws)) if len(throws) > 0 else 5, 6)
    if h < b:
        h = b + 1
    # Enumerate all valid states: binary vectors of length h with exactly b ones
    from itertools import combinations
    states = []
    for combo in combinations(range(h), b):
        state = [0] * h
        for c in combo:
            state[c] = 1
        states.append(tuple(state))
    n_states = len(states)
    if n_states == 0 or n_states > 100:
        return np.array([float(n_states)])
    state_idx = {s: i for i, s in enumerate(states)}
    T = np.zeros((n_states, n_states))
    for s, idx in state_idx.items():
        # Current state: if s[0]=1, we must throw; the throw height determines next state
        if s[0] == 1:
            for throw_h in range(1, h + 1):
                # After throwing with height throw_h:
                # shift state left by 1, set position throw_h-1 to 1
                new_state = list(s[1:]) + [0]
                if throw_h - 1 < len(new_state) and new_state[throw_h - 1] == 0:
                    new_state[throw_h - 1] = 1
                    ns = tuple(new_state)
                    if ns in state_idx:
                        T[idx, state_idx[ns]] = 1.0
        else:
            # No ball to throw: just shift (throw height 0)
            new_state = list(s[1:]) + [0]
            ns = tuple(new_state)
            if ns in state_idx:
                T[idx, state_idx[ns]] = 1.0
    return T.ravel()


OPERATIONS["siteswap_transition_matrix"] = {
    "fn": siteswap_transition_matrix,
    "input_type": "array",
    "output_type": "array",
    "description": "State transition matrix for siteswap juggling automaton"
}


def siteswap_orbit_count(x):
    """Count the number of distinct siteswap orbits (necklaces) for given parameters.
    Input: array (first elem = balls, second = max_throw, third = period).
    Output: scalar."""
    b = max(1, int(np.round(x[0]))) if len(x) > 0 else 3
    max_t = max(b, int(np.round(x[1]))) if len(x) > 1 else 5
    period = max(1, int(np.round(x[2]))) if len(x) > 2 else 3
    # Count valid siteswaps of given period with b balls and max throw max_t
    # Enumerate and check (only for small parameters)
    if max_t ** period > 50000:
        # Too large, use approximation: roughly max_t^period / period * (b/max_t) like
        approx = (max_t ** period) / period
        return float(approx)
    count = 0
    throws_range = range(max_t + 1)

    def enumerate_ss(prefix, remaining):
        nonlocal count
        if remaining == 0:
            arr = np.array(prefix)
            if np.mean(arr) == b:
                if siteswap_valid(arr) == 1.0:
                    count += 1
            return
        for t in throws_range:
            enumerate_ss(prefix + [t], remaining - 1)

    enumerate_ss([], period)
    # Divide by period for necklace equivalence
    return float(count / period) if period > 0 else 0.0


OPERATIONS["siteswap_orbit_count"] = {
    "fn": siteswap_orbit_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count distinct siteswap orbits (necklace equivalence classes)"
}


def vanilla_siteswap_enumerate(x):
    """Enumerate vanilla siteswaps (no multiplex) with given average.
    Input: array (first = num_balls, second = period). Output: array (count per max_throw)."""
    b = max(1, int(np.round(x[0]))) if len(x) > 0 else 3
    period = max(1, min(4, int(np.round(x[1])))) if len(x) > 1 else 3
    results = []
    for max_t in range(b, min(b + 5, 10)):
        count = 0
        # Enumerate siteswaps of this period
        def count_valid(prefix, rem, target_sum):
            nonlocal count
            if rem == 0:
                if sum(prefix) == target_sum:
                    arr = np.array(prefix)
                    if siteswap_valid(arr) == 1.0:
                        count += 1
                return
            for t in range(max_t + 1):
                if sum(prefix) + t + rem - 1 > target_sum:
                    continue  # prune
                count_valid(prefix + [t], rem - 1, target_sum)

        target = b * period
        if max_t ** period <= 100000:
            count_valid([], period, target)
        results.append(float(count))
    return np.array(results) if results else np.array([0.0])


OPERATIONS["vanilla_siteswap_enumerate"] = {
    "fn": vanilla_siteswap_enumerate,
    "input_type": "array",
    "output_type": "array",
    "description": "Count vanilla siteswaps per max throw height"
}


def siteswap_ground_state(x):
    """Ground state for b balls: the state [1,1,...,1,0,0,...0] with b ones.
    Input: array (first elem = b). Output: array."""
    b = max(1, int(np.round(x[0]))) if len(x) > 0 else 3
    h = max(b + 2, int(np.round(x[1]))) if len(x) > 1 else b + 3
    state = np.zeros(h)
    state[:b] = 1.0
    return state


OPERATIONS["siteswap_ground_state"] = {
    "fn": siteswap_ground_state,
    "input_type": "array",
    "output_type": "array",
    "description": "Ground state for b-ball juggling"
}


def siteswap_excited_state(x):
    """Check if a siteswap is an excited state (not the ground state).
    Input: array (siteswap throws). Output: scalar (1 if excited, 0 if ground)."""
    throws = np.round(np.abs(x)).astype(int)
    if len(throws) == 0:
        return 0.0
    b = int(np.round(np.mean(throws)))
    # Ground state siteswap for b balls is just [b] (constant throw)
    # A pattern is excited if it visits a state other than the ground state
    state = siteswap_state_vector(throws)
    ground = np.zeros_like(state)
    if b <= len(ground):
        ground[:b] = 1.0
    # Check if state differs from ground
    if np.array_equal(state[:min(len(state), len(ground))],
                      ground[:min(len(state), len(ground))]):
        return 0.0
    return 1.0


OPERATIONS["siteswap_excited_state"] = {
    "fn": siteswap_excited_state,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if siteswap visits an excited (non-ground) state"
}


def multiplex_throw_count(x):
    """Count how many throws in the pattern would require multiplex (>1 ball thrown simultaneously).
    For vanilla siteswaps this should be 0. Input: array. Output: scalar."""
    throws = np.round(np.abs(x)).astype(int)
    n = len(throws)
    if n == 0:
        return 0.0
    # Simulate and check if any beat requires throwing more than one ball
    max_height = max(int(np.max(throws)), n) + n
    schedule = np.zeros(max_height + n)
    # Run two periods to stabilize
    multiplex_count = 0
    for period in range(2):
        for i in range(n):
            beat = period * n + i
            if schedule[beat] > 1:
                multiplex_count += 1
            t = throws[i]
            if t > 0 and beat + t < len(schedule):
                schedule[beat + t] += 1
    return float(multiplex_count)


OPERATIONS["multiplex_throw_count"] = {
    "fn": multiplex_throw_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of beats requiring multiplex throws"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
