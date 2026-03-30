"""
Combinatorial Game Theory Extended -- Hackenbush, domineering, temperature theory, thermography

Connects to: [nim_theory, surreal_numbers, lattice_theory, ordinal_arithmetic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "combinatorial_game_theory_extended"
OPERATIONS = {}


def _parse_game(x):
    """Interpret array as a game {L | R} where L = left options, R = right options.
    First half = left option values, second half = right option values."""
    n = len(x)
    half = n // 2
    left = np.sort(x[:half])[::-1] if half > 0 else np.array([])
    right = np.sort(x[half:]) if n - half > 0 else np.array([])
    return left, right


def game_value_compute(x):
    """Compute the value of a combinatorial game {L|R}.
    Uses simplicity rule: value is simplest number between max(L) and min(R).
    Input: array. Output: scalar."""
    left, right = _parse_game(x)
    if len(left) == 0 and len(right) == 0:
        return 0.0  # {|} = 0
    if len(left) == 0:
        # {|R} = min(R) - 1 approximately (if R are integers)
        return float(min(right) - 1)
    if len(right) == 0:
        # {L|} = max(L) + 1
        return float(max(left) + 1)
    L_max = max(left)
    R_min = min(right)
    if L_max >= R_min:
        # Fuzzy or confused: this is a hot game
        return float((L_max + R_min) / 2.0)
    # Find simplest number strictly between L_max and R_min
    # Simplest = smallest denominator (dyadic rational)
    for denom in [1, 2, 4, 8, 16, 32, 64]:
        for num in range(int(np.floor(L_max * denom)), int(np.ceil(R_min * denom)) + 1):
            val = num / denom
            if L_max < val < R_min:
                return float(val)
    return float((L_max + R_min) / 2.0)


OPERATIONS["game_value_compute"] = {
    "fn": game_value_compute,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Game value via simplicity rule"
}


def game_temperature(x):
    """Temperature of a game: measures how much the game value changes per move.
    temp(G) = (Left incentive + Right incentive) / 2.
    Input: array. Output: scalar."""
    left, right = _parse_game(x)
    if len(left) == 0 or len(right) == 0:
        return 0.0
    game_val = game_value_compute(x)
    # Left incentive: max over left options of (option_value - game_value)
    left_inc = max(left) - game_val
    # Right incentive: max over right options of (game_value - option_value)
    right_inc = game_val - min(right)
    temp = max(0, (left_inc + right_inc) / 2.0)
    return float(temp)


OPERATIONS["game_temperature"] = {
    "fn": game_temperature,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Temperature of a combinatorial game"
}


def game_mean(x):
    """Mean value of a game: the value as temperature approaches 0.
    For a hot game {a|b}, mean = (a+b)/2. Input: array. Output: scalar."""
    left, right = _parse_game(x)
    if len(left) == 0 and len(right) == 0:
        return 0.0
    if len(left) == 0:
        return float(np.mean(right))
    if len(right) == 0:
        return float(np.mean(left))
    return float((max(left) + min(right)) / 2.0)


OPERATIONS["game_mean"] = {
    "fn": game_mean,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Mean value of a combinatorial game"
}


def game_fuzzy_check(x):
    """Check if game is fuzzy (incomparable with 0): first player wins.
    G is fuzzy if Left can win going first AND Right can win going first.
    Input: array. Output: scalar (1 fuzzy, 0 not)."""
    left, right = _parse_game(x)
    if len(left) == 0 and len(right) == 0:
        return 0.0  # Zero game, second player wins
    # G > 0: Left wins regardless who moves first
    # G < 0: Right wins regardless
    # G = 0: Second player wins
    # G || 0: First player wins (fuzzy)
    val = game_value_compute(x)
    if len(left) > 0 and len(right) > 0:
        if max(left) > 0 and min(right) < 0:
            # Both players have winning moves going first => fuzzy
            return 1.0
    # Check if value suggests fuzziness
    if len(left) > 0 and len(right) > 0 and max(left) >= min(right):
        return 1.0
    return 0.0


OPERATIONS["game_fuzzy_check"] = {
    "fn": game_fuzzy_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if game is fuzzy (first player wins)"
}


def nimber_game_sum(x):
    """Nim-value sum (XOR) of nimbers. Input: array (nim values). Output: scalar."""
    nim_vals = np.round(np.abs(x)).astype(int)
    result = 0
    for v in nim_vals:
        result ^= v
    return float(result)


OPERATIONS["nimber_game_sum"] = {
    "fn": nimber_game_sum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Nim-value (Sprague-Grundy) sum via XOR"
}


def hackenbush_value(x):
    """Value of a Hackenbush string: Blue edges = +1, Red = -1.
    Treats positive values as Blue, negative as Red. Input: array. Output: scalar."""
    # A Hackenbush string of alternating colors has value that depends on the sequence
    # Simple case: stack of same-color edges
    blue = np.sum(x > 0)
    red = np.sum(x < 0)
    if blue == 0 and red == 0:
        return 0.0
    # For a simple stack from ground: value = sum of +1/-1 for each edge color
    # More precisely: value as a game
    # Stack of n blue = n, stack of n red = -n
    # Mixed stack: binary fraction representation
    n = len(x)
    val = 0.0
    sign = 1.0
    for i in range(n):
        if i == 0:
            val = 1.0 if x[i] > 0 else -1.0
            sign = 1.0 if x[i] > 0 else -1.0
        else:
            current_sign = 1.0 if x[i] > 0 else -1.0
            if current_sign == sign:
                val += current_sign * (1.0 / (2 ** i))
            else:
                val += current_sign * (1.0 / (2 ** i))
                sign = current_sign
    return float(val)


OPERATIONS["hackenbush_value"] = {
    "fn": hackenbush_value,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Value of a Hackenbush string (Blue/Red stack)"
}


def domineering_value_small(x):
    """Compute Domineering game value on a small board.
    Input: array (flattened board, 0=empty, 1=occupied). Output: scalar."""
    n = len(x)
    cols = int(np.ceil(np.sqrt(n)))
    rows = max(1, n // cols)
    board = np.zeros(rows * cols)
    board[:min(n, rows * cols)] = x[:min(n, rows * cols)]
    board = (board > np.median(board)).astype(int).reshape(rows, cols)
    # Count available moves for Vertical (Left) and Horizontal (Right)
    left_moves = 0  # vertical dominoes
    right_moves = 0  # horizontal dominoes
    for r in range(rows - 1):
        for c in range(cols):
            if board[r, c] == 0 and board[r + 1, c] == 0:
                left_moves += 1
    for r in range(rows):
        for c in range(cols - 1):
            if board[r, c] == 0 and board[r, c + 1] == 0:
                right_moves += 1
    # Approximate game value: difference in mobility
    return float(left_moves - right_moves)


OPERATIONS["domineering_value_small"] = {
    "fn": domineering_value_small,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate Domineering game value (mobility difference)"
}


def thermograph_left_wall(x):
    """Left wall of thermograph: game value as seen by Left at various temperatures.
    Input: array (game encoding). Output: array (values at temperatures 0,0.5,1,1.5,...)."""
    left, right = _parse_game(x)
    mean = game_mean(x)
    temp = game_temperature(x)
    # Left wall: starts at max(left options), decreases linearly to mean at t=temp
    temps = np.arange(0, max(temp + 1, 3), 0.5)
    wall = []
    for t in temps:
        if t >= temp:
            wall.append(mean)
        else:
            if len(left) > 0:
                wall.append(max(left) - t)
            else:
                wall.append(mean)
    return np.array(wall)


OPERATIONS["thermograph_left_wall"] = {
    "fn": thermograph_left_wall,
    "input_type": "array",
    "output_type": "array",
    "description": "Left wall of thermograph at various temperatures"
}


def thermograph_right_wall(x):
    """Right wall of thermograph. Input: array. Output: array."""
    left, right = _parse_game(x)
    mean = game_mean(x)
    temp = game_temperature(x)
    temps = np.arange(0, max(temp + 1, 3), 0.5)
    wall = []
    for t in temps:
        if t >= temp:
            wall.append(mean)
        else:
            if len(right) > 0:
                wall.append(min(right) + t)
            else:
                wall.append(mean)
    return np.array(wall)


OPERATIONS["thermograph_right_wall"] = {
    "fn": thermograph_right_wall,
    "input_type": "array",
    "output_type": "array",
    "description": "Right wall of thermograph at various temperatures"
}


def game_outcome_class(x):
    """Determine outcome class: 0=zero (2nd player wins), 1=positive (Left wins),
    -1=negative (Right wins), 2=fuzzy (1st player wins).
    Input: array. Output: scalar."""
    left, right = _parse_game(x)
    val = game_value_compute(x)
    is_fuzzy = game_fuzzy_check(x)
    if is_fuzzy > 0.5:
        return 2.0
    if abs(val) < 1e-10:
        return 0.0
    if val > 0:
        return 1.0
    return -1.0


OPERATIONS["game_outcome_class"] = {
    "fn": game_outcome_class,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Outcome class: 0=zero, 1=positive, -1=negative, 2=fuzzy"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
