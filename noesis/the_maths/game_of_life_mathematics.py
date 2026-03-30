"""
Game of Life Mathematics — mathematical properties of Conway's Game of Life

Connects to: [cellular automata, combinatorics, computability theory, dynamical systems, entropy]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "game_of_life_mathematics"
OPERATIONS = {}


def _to_board(x):
    """Convert array to a binary Game of Life board."""
    n = int(np.ceil(np.sqrt(len(x))))
    n = max(n, 3)
    board = np.zeros((n, n), dtype=int)
    flat = (np.abs(x) > np.median(np.abs(x))).astype(int)
    board.flat[:len(flat)] = flat
    return board


def _count_neighbors(board):
    """Count live neighbors for each cell using convolution."""
    rows, cols = board.shape
    counts = np.zeros_like(board)
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            shifted = np.roll(np.roll(board, di, axis=0), dj, axis=1)
            counts += shifted
    return counts


def _step(board):
    """Apply one Game of Life step."""
    neighbors = _count_neighbors(board)
    # Birth: dead cell with exactly 3 neighbors becomes alive
    birth = (board == 0) & (neighbors == 3)
    # Survival: live cell with 2 or 3 neighbors survives
    survive = (board == 1) & ((neighbors == 2) | (neighbors == 3))
    return (birth | survive).astype(int)


def life_step(x):
    """Apply one Game of Life step. Input: array. Output: array."""
    board = _to_board(x)
    result = _step(board)
    return result.flatten()[:len(x)].astype(float)


OPERATIONS["life_step"] = {
    "fn": life_step,
    "input_type": "array",
    "output_type": "array",
    "description": "Applies one step of Conway's Game of Life"
}


def life_evolve(x):
    """Evolve the board for N steps where N = len(x). Return final state.
    Input: array. Output: array."""
    board = _to_board(x)
    steps = min(len(x), 100)
    for _ in range(steps):
        board = _step(board)
    return board.flatten()[:len(x)].astype(float)


OPERATIONS["life_evolve"] = {
    "fn": life_evolve,
    "input_type": "array",
    "output_type": "array",
    "description": "Evolves the Game of Life for N steps and returns final state"
}


def life_population_entropy(x):
    """Compute Shannon entropy of the population time series.
    Input: array. Output: scalar."""
    board = _to_board(x)
    steps = min(len(x) * 10, 200)
    populations = []
    for _ in range(steps):
        populations.append(int(np.sum(board)))
        board = _step(board)
    pops = np.array(populations)
    if np.max(pops) == 0:
        return 0.0
    # Bin the populations and compute entropy
    unique, counts = np.unique(pops, return_counts=True)
    probs = counts / counts.sum()
    entropy = -np.sum(probs * np.log2(probs + 1e-15))
    return float(entropy)


OPERATIONS["life_population_entropy"] = {
    "fn": life_population_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of the population time series during evolution"
}


def life_period_detect(x):
    """Detect the period of a Game of Life pattern. Input: array. Output: scalar (period, 0=none found)."""
    board = _to_board(x)
    max_steps = 300
    # Store hashes of states
    history = {}
    for step in range(max_steps):
        state_hash = board.tobytes()
        if state_hash in history:
            return float(step - history[state_hash])
        history[state_hash] = step
        board = _step(board)
    return 0.0  # No period found within limit


OPERATIONS["life_period_detect"] = {
    "fn": life_period_detect,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Detects the period of a Game of Life pattern (0 if none found)"
}


def life_density_equilibrium(x):
    """Compute the equilibrium density (fraction of live cells) after evolution.
    Input: array. Output: scalar."""
    board = _to_board(x)
    total_cells = board.size
    # Run for a while to reach equilibrium
    densities = []
    for step in range(200):
        board = _step(board)
        if step >= 100:  # Sample last 100 steps
            densities.append(np.sum(board) / total_cells)
    if len(densities) == 0:
        return 0.0
    return float(np.mean(densities))


OPERATIONS["life_density_equilibrium"] = {
    "fn": life_density_equilibrium,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes equilibrium live-cell density after extended evolution"
}


def life_methuselah_score(x):
    """Score a pattern as a methuselah: ratio of total active generations to initial population.
    Input: array. Output: scalar."""
    board = _to_board(x)
    initial_pop = max(int(np.sum(board)), 1)
    max_steps = 500
    active_generations = 0
    prev_board = board.copy()
    for _ in range(max_steps):
        board = _step(board)
        if not np.array_equal(board, prev_board):
            active_generations += 1
        else:
            break
        prev_board = board.copy()
    return float(active_generations) / float(initial_pop)


OPERATIONS["life_methuselah_score"] = {
    "fn": life_methuselah_score,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Scores a pattern as methuselah: active generations / initial population"
}


def life_still_life_test(x):
    """Test if a pattern is a still life (unchanged after one step).
    Input: array. Output: scalar (1=still life, 0=not)."""
    board = _to_board(x)
    next_board = _step(board)
    return 1.0 if np.array_equal(board, next_board) else 0.0


OPERATIONS["life_still_life_test"] = {
    "fn": life_still_life_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tests if a Game of Life pattern is a still life"
}


def life_oscillator_period(x):
    """Find the oscillator period of the pattern (same as period_detect but returns
    the period only if the pattern is purely oscillating, not translating).
    Input: array. Output: scalar."""
    board = _to_board(x)
    original = board.copy()
    max_steps = 300
    for step in range(1, max_steps + 1):
        board = _step(board)
        if np.array_equal(board, original):
            return float(step)
    return 0.0


OPERATIONS["life_oscillator_period"] = {
    "fn": life_oscillator_period,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Finds oscillator period (returns to exact initial state)"
}


def life_spaceship_velocity(x):
    """Detect if a pattern is a spaceship and estimate its velocity (displacement/period).
    Input: array. Output: scalar (speed as cells/generation, 0 if not a spaceship)."""
    board = _to_board(x)
    rows, cols = board.shape
    max_steps = 200
    # Track center of mass
    initial_alive = np.argwhere(board == 1)
    if len(initial_alive) == 0:
        return 0.0
    initial_com = initial_alive.mean(axis=0)
    for step in range(1, max_steps + 1):
        board = _step(board)
        alive = np.argwhere(board == 1)
        if len(alive) == 0:
            return 0.0
        # Check if pattern shape matches original but is displaced
        com = alive.mean(axis=0)
        displacement = np.sqrt(np.sum((com - initial_com) ** 2))
        if displacement > 0.5 and np.sum(board) == np.sum(_to_board(x)):
            # Same population, different position -> possible spaceship
            velocity = displacement / step
            if velocity > 0:
                return float(velocity)
    return 0.0


OPERATIONS["life_spaceship_velocity"] = {
    "fn": life_spaceship_velocity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates spaceship velocity as displacement per generation"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
