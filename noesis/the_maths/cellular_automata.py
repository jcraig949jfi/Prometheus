"""
Cellular Automata — all 256 elementary rules, Wolfram classification, entropy of orbits

Connects to: [dynamical_systems, computation_theory, information_theory, statistical_mechanics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "cellular_automata"
OPERATIONS = {}


def _apply_rule(state, rule_number):
    """Apply an elementary cellular automaton rule to a binary state array.
    rule_number: 0-255 integer specifying the Wolfram rule.
    Returns the next generation."""
    rule_number = int(rule_number) % 256
    n = len(state)
    new_state = np.zeros(n, dtype=float)
    for i in range(n):
        left = int(state[(i - 1) % n])
        center = int(state[i])
        right = int(state[(i + 1) % n])
        neighborhood = (left << 2) | (center << 1) | right  # 0-7
        new_state[i] = float((rule_number >> neighborhood) & 1)
    return new_state


def _evolve(state, rule_number, steps):
    """Evolve a CA for the given number of steps. Returns all generations as rows."""
    history = [state.copy()]
    current = state.copy()
    for _ in range(steps):
        current = _apply_rule(current, rule_number)
        history.append(current.copy())
    return np.array(history)


def elementary_rule_step(x):
    """Apply one step of an elementary CA rule. x[0] is the rule number (0-255),
    remaining elements are the binary state (thresholded at 0.5).
    Input: array. Output: array."""
    rule_number = int(x[0]) % 256
    state = (x[1:] >= 0.5).astype(float)
    if len(state) == 0:
        return np.array([0.0])
    return _apply_rule(state, rule_number)


OPERATIONS["elementary_rule_step"] = {
    "fn": elementary_rule_step,
    "input_type": "array",
    "output_type": "array",
    "description": "One step of elementary CA: x[0]=rule, x[1:]=state"
}


def elementary_rule_evolve(x):
    """Evolve an elementary CA for multiple steps. x[0] = rule number,
    x[1] = number of steps, x[2:] = initial state (binary, thresholded at 0.5).
    Returns flattened spacetime diagram (rows = generations).
    Input: array. Output: array."""
    rule_number = int(x[0]) % 256
    steps = max(1, int(x[1])) if len(x) > 1 else 5
    state = (x[2:] >= 0.5).astype(float) if len(x) > 2 else np.zeros(1)
    if len(state) == 0:
        state = np.array([1.0])
    history = _evolve(state, rule_number, steps)
    return history.flatten()


OPERATIONS["elementary_rule_evolve"] = {
    "fn": elementary_rule_evolve,
    "input_type": "array",
    "output_type": "array",
    "description": "Evolve elementary CA: x[0]=rule, x[1]=steps, x[2:]=state"
}


def rule_entropy(x):
    """Compute the Shannon entropy of a CA spacetime diagram.
    x[0] = rule number, x[1:] = initial state. Evolves for 20 steps
    and computes entropy of the density time series.
    Input: array. Output: scalar."""
    rule_number = int(x[0]) % 256
    state = (x[1:] >= 0.5).astype(float) if len(x) > 1 else np.array([1.0])
    if len(state) == 0:
        state = np.array([1.0])
    steps = 20
    history = _evolve(state, rule_number, steps)
    # Compute column-wise density as a time series
    densities = np.mean(history, axis=1)
    # Bin the densities for entropy computation
    counts = np.histogram(densities, bins=10, range=(0, 1))[0]
    counts = counts[counts > 0]
    probs = counts / counts.sum()
    entropy = -np.sum(probs * np.log2(probs))
    return float(entropy)


OPERATIONS["rule_entropy"] = {
    "fn": rule_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of CA density evolution over 20 steps"
}


def rule_density_evolution(x):
    """Track density (fraction of 1s) over time for a CA rule.
    x[0] = rule number, x[1:] = initial state. Evolves for len(x)-1 steps
    or 10 steps, whichever is smaller.
    Input: array. Output: array (density at each time step)."""
    rule_number = int(x[0]) % 256
    state = (x[1:] >= 0.5).astype(float) if len(x) > 1 else np.array([1.0])
    if len(state) == 0:
        state = np.array([1.0])
    steps = min(max(len(x) - 1, 5), 30)
    history = _evolve(state, rule_number, steps)
    return np.mean(history, axis=1)


OPERATIONS["rule_density_evolution"] = {
    "fn": rule_density_evolution,
    "input_type": "array",
    "output_type": "array",
    "description": "Density (fraction of 1s) over time for CA rule"
}


def rule_classification_heuristic(x):
    """Heuristic Wolfram classification of a CA rule (1-4).
    Class 1: fixed point, Class 2: periodic, Class 3: chaotic, Class 4: complex.
    x[0] = rule number. Uses entropy and density variance as heuristics.
    Input: array. Output: scalar (1, 2, 3, or 4)."""
    rule_number = int(x[0]) % 256
    # Known classifications for some rules
    known_class1 = {0, 8, 32, 40, 128, 136, 160, 168}  # all die / uniform
    known_class2 = {1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 13, 14, 15, 23, 24,
                    25, 26, 27, 28, 29, 33, 34, 35, 36, 37, 38, 42, 44,
                    46, 50, 51, 56, 57, 58, 62, 72, 73, 76, 77, 78, 94,
                    104, 108, 130, 132, 134, 138, 140, 142, 152, 154,
                    156, 162, 164, 170, 172, 178, 184, 200, 204, 232}
    known_class3 = {18, 22, 30, 45, 60, 90, 105, 122, 126, 146, 150, 182}
    known_class4 = {54, 106, 110}

    if rule_number in known_class1:
        return 1.0
    if rule_number in known_class4:
        return 4.0
    if rule_number in known_class3:
        return 3.0
    if rule_number in known_class2:
        return 2.0

    # Heuristic: evolve from random initial state and measure entropy
    size = 51
    np.random.seed(rule_number)
    state = (np.random.random(size) >= 0.5).astype(float)
    steps = 50
    history = _evolve(state, rule_number, steps)
    densities = np.mean(history, axis=1)

    # Check if it dies (class 1)
    if densities[-1] == 0.0 or densities[-1] == 1.0:
        late_var = np.var(densities[-10:])
        if late_var < 1e-10:
            return 1.0

    # Check periodicity (class 2)
    late_states = history[-10:]
    for period in range(1, 6):
        if np.array_equal(late_states[-1], late_states[-1 - period]):
            return 2.0

    # Entropy-based: high entropy = class 3, medium = class 4
    counts = np.histogram(densities, bins=10, range=(0, 1))[0]
    counts = counts[counts > 0]
    probs = counts / counts.sum()
    entropy = -np.sum(probs * np.log2(probs))

    if entropy > 2.5:
        return 3.0
    elif entropy > 1.5:
        return 4.0
    else:
        return 2.0


OPERATIONS["rule_classification_heuristic"] = {
    "fn": rule_classification_heuristic,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Heuristic Wolfram class (1-4) for CA rule x[0]"
}


def rule_langton_parameter(x):
    """Compute Langton's lambda parameter for a CA rule.
    lambda = (K^N - n_quiescent) / K^N where K=2 states, N=3 neighborhood size.
    For elementary CA: lambda = (number of 1s in rule binary) / 8.
    x[0] = rule number.
    Input: array. Output: scalar."""
    rule_number = int(x[0]) % 256
    # Count number of 1-bits in the 8-bit rule
    ones = bin(rule_number).count('1')
    return float(ones / 8.0)


OPERATIONS["rule_langton_parameter"] = {
    "fn": rule_langton_parameter,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Langton's lambda parameter: fraction of non-quiescent transitions"
}


def rule_lyapunov_exponent(x):
    """Estimate the Lyapunov exponent of a CA rule by measuring sensitivity
    to initial conditions. Flip one bit and measure Hamming distance divergence.
    x[0] = rule number, x[1:] = initial state.
    Input: array. Output: scalar."""
    rule_number = int(x[0]) % 256
    state = (x[1:] >= 0.5).astype(float) if len(x) > 1 else np.array([1.0])
    if len(state) < 3:
        state = np.zeros(21)
        state[10] = 1.0

    # Perturbed state: flip middle bit
    perturbed = state.copy()
    mid = len(state) // 2
    perturbed[mid] = 1.0 - perturbed[mid]

    steps = 20
    dists = []
    s1, s2 = state.copy(), perturbed.copy()
    for _ in range(steps):
        s1 = _apply_rule(s1, rule_number)
        s2 = _apply_rule(s2, rule_number)
        hamming = np.sum(np.abs(s1 - s2))
        dists.append(max(hamming, 1e-15))

    # Lyapunov exponent ~ average log growth rate of perturbation
    log_dists = np.log(np.array(dists))
    if len(log_dists) > 1:
        # Linear fit to log(distance) vs time
        times = np.arange(1, steps + 1, dtype=float)
        coeffs = np.polyfit(times, log_dists, 1)
        return float(coeffs[0])  # slope = Lyapunov exponent
    return 0.0


OPERATIONS["rule_lyapunov_exponent"] = {
    "fn": rule_lyapunov_exponent,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimated Lyapunov exponent from bit-flip perturbation"
}


def rule_spatial_entropy(x):
    """Compute spatial entropy of a CA state after evolution.
    x[0] = rule number, x[1:] = initial state. Evolves 20 steps,
    then measures entropy of block patterns of length 3 in the final state.
    Input: array. Output: scalar."""
    rule_number = int(x[0]) % 256
    state = (x[1:] >= 0.5).astype(float) if len(x) > 1 else np.array([1.0])
    if len(state) < 5:
        state = np.zeros(31)
        state[15] = 1.0

    steps = 20
    current = state.copy()
    for _ in range(steps):
        current = _apply_rule(current, rule_number)

    # Count all 3-cell blocks (8 possible patterns)
    n = len(current)
    if n < 3:
        return 0.0
    block_counts = np.zeros(8)
    for i in range(n):
        block = (int(current[(i - 1) % n]) << 2 |
                 int(current[i]) << 1 |
                 int(current[(i + 1) % n]))
        block_counts[block] += 1

    total = block_counts.sum()
    if total == 0:
        return 0.0
    probs = block_counts[block_counts > 0] / total
    entropy = -np.sum(probs * np.log2(probs))
    return float(entropy)


OPERATIONS["rule_spatial_entropy"] = {
    "fn": rule_spatial_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Spatial entropy of 3-cell blocks after 20 evolution steps"
}


def rule_30_random_column(x):
    """Extract the center column from Rule 30 evolution as a pseudo-random
    bit sequence. x[0] = number of bits to generate (capped at 100),
    starting from a single seed cell.
    Input: array. Output: array (binary sequence)."""
    n_bits = min(100, max(1, int(x[0])))
    # State wide enough to avoid boundary effects
    width = 2 * n_bits + 3
    state = np.zeros(width)
    state[width // 2] = 1.0

    center_bits = [state[width // 2]]
    for _ in range(n_bits - 1):
        state = _apply_rule(state, 30)
        center_bits.append(state[width // 2])

    return np.array(center_bits)


OPERATIONS["rule_30_random_column"] = {
    "fn": rule_30_random_column,
    "input_type": "array",
    "output_type": "array",
    "description": "Center column of Rule 30 as pseudo-random bit sequence"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
