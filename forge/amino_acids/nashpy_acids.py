"""Amino acids decomposed from nashpy (v0.0.43) — 2-player game theory.

Each function is 5-20 lines, performs one atomic reasoning operation,
and wraps a specific nashpy capability that T1 primitives lack.
"""
from forge.amino_acids.registry import amino_acid


@amino_acid(
    id="nash_find_equilibria",
    source="nashpy",
    reasoning_type="game_theoretic",
    description="Compute all Nash equilibria of a 2-player game"
)
def find_equilibria(payoff_a, payoff_b):
    """Compute Nash equilibria via support enumeration.
    
    Args:
        payoff_a: 2D list — row player's payoff matrix
        payoff_b: 2D list — column player's payoff matrix
    Returns:
        list of (strategy_p1, strategy_p2) tuples, each a numpy array of probabilities
    """
    import nashpy as nash
    import numpy as np
    game = nash.Game(np.array(payoff_a), np.array(payoff_b))
    return [(eq[0].tolist(), eq[1].tolist()) for eq in game.support_enumeration()]


@amino_acid(
    id="nash_is_dominated",
    source="nashpy",
    reasoning_type="game_theoretic",
    description="Check if a strategy is strictly dominated by another strategy"
)
def is_dominated(payoff_matrix, strategy_idx, player_is_row=True):
    """Check if strategy at strategy_idx is strictly dominated.
    
    A strategy is dominated if another strategy gives strictly higher payoff
    against every opponent strategy.
    
    Args:
        payoff_matrix: 2D list of payoffs for the player
        strategy_idx: index of the strategy to check
        player_is_row: True if checking row player strategies
    Returns:
        dict with 'dominated' (bool), 'dominator' (index of dominating strategy or None)
    """
    import numpy as np
    m = np.array(payoff_matrix)
    if not player_is_row:
        m = m.T
    target = m[strategy_idx]
    for i in range(m.shape[0]):
        if i != strategy_idx and np.all(m[i] > target):
            return {"dominated": True, "dominator": i}
    return {"dominated": False, "dominator": None}


@amino_acid(
    id="nash_best_response",
    source="nashpy",
    reasoning_type="game_theoretic",
    description="Compute the best response strategy to an opponent's mixed strategy"
)
def best_response(payoff_matrix, opponent_strategy, player_is_row=True):
    """Compute best response to opponent's mixed strategy.
    
    Args:
        payoff_matrix: 2D list of payoffs
        opponent_strategy: list of probabilities (opponent's mixed strategy)
        player_is_row: True if this player is the row player
    Returns:
        dict with 'best_action' (int), 'expected_payoff' (float), 'all_payoffs' (list)
    """
    import numpy as np
    m = np.array(payoff_matrix)
    opp = np.array(opponent_strategy)
    if player_is_row:
        expected = m @ opp
    else:
        expected = m.T @ opp
    best = int(np.argmax(expected))
    return {"best_action": best, "expected_payoff": float(expected[best]),
            "all_payoffs": expected.tolist()}


@amino_acid(
    id="nash_find_dominant_strategy",
    source="nashpy",
    reasoning_type="game_theoretic",
    description="Find a strictly dominant strategy if one exists"
)
def find_dominant_strategy(payoff_matrix, player_is_row=True):
    """Find a strategy that dominates ALL others.
    
    Returns:
        int index of dominant strategy, or None if no dominant strategy exists
    """
    import numpy as np
    m = np.array(payoff_matrix)
    if not player_is_row:
        m = m.T
    n = m.shape[0]
    for i in range(n):
        dominates_all = True
        for j in range(n):
            if i != j and not np.all(m[i] > m[j]):
                dominates_all = False
                break
        if dominates_all:
            return i
    return None


@amino_acid(
    id="nash_compute_minimax",
    source="nashpy",
    reasoning_type="game_theoretic",
    description="Compute the minimax value and strategy for a zero-sum game"
)
def compute_minimax(payoff_matrix):
    """Compute minimax strategy for the row player in a zero-sum game.
    
    Returns:
        dict with 'value' (float), 'row_strategy' (list), 'col_strategy' (list)
    """
    import nashpy as nash
    import numpy as np
    m = np.array(payoff_matrix)
    game = nash.Game(m, -m)  # zero-sum
    eqs = list(game.support_enumeration())
    if eqs:
        row_s, col_s = eqs[0]
        value = float(row_s @ m @ col_s)
        return {"value": value, "row_strategy": row_s.tolist(), "col_strategy": col_s.tolist()}
    return None


@amino_acid(
    id="nash_expected_payoff",
    source="nashpy",
    reasoning_type="game_theoretic",
    description="Compute expected payoffs for both players under given mixed strategies"
)
def expected_payoff(payoff_a, payoff_b, strategy_a, strategy_b):
    """Compute expected payoff for each player under mixed strategy profiles.
    
    Returns:
        dict with 'payoff_a' (float), 'payoff_b' (float)
    """
    import numpy as np
    a, b = np.array(payoff_a), np.array(payoff_b)
    sa, sb = np.array(strategy_a), np.array(strategy_b)
    return {
        "payoff_a": float(sa @ a @ sb),
        "payoff_b": float(sa @ b @ sb),
    }
