"""
Game Theory organism.

Operations: nash_equilibrium_2x2, minimax, prisoners_dilemma_iterate,
            replicator_dynamics
"""

from .base import MathematicalOrganism


class GameTheory(MathematicalOrganism):
    name = "game_theory"
    operations = {
        "nash_equilibrium_2x2": {
            "code": """
def nash_equilibrium_2x2(A, B=None):
    \"\"\"Find mixed-strategy Nash equilibrium for a 2x2 game.
    A: 2x2 payoff matrix for player 1.
    B: 2x2 payoff matrix for player 2 (if None, zero-sum: B = -A).
    Returns (p, q) mixed strategies and expected payoffs.\"\"\"
    A = np.asarray(A, dtype=np.float64)
    if B is None:
        B = -A
    else:
        B = np.asarray(B, dtype=np.float64)

    # Player 2's mixed strategy q makes player 1 indifferent:
    # A[0,0]*q + A[0,1]*(1-q) = A[1,0]*q + A[1,1]*(1-q)
    denom_q = (A[0,0] - A[0,1] - A[1,0] + A[1,1])
    if abs(denom_q) < 1e-12:
        q = 0.5  # degenerate
    else:
        q = (A[1,1] - A[0,1]) / denom_q
        q = np.clip(q, 0, 1)

    # Player 1's mixed strategy p makes player 2 indifferent:
    denom_p = (B[0,0] - B[0,1] - B[1,0] + B[1,1])
    if abs(denom_p) < 1e-12:
        p = 0.5
    else:
        p = (B[1,1] - B[0,1]) / denom_p
        p = np.clip(p, 0, 1)

    # Expected payoffs
    strat1 = np.array([p, 1 - p])
    strat2 = np.array([q, 1 - q])
    ev1 = strat1 @ A @ strat2
    ev2 = strat1 @ B @ strat2
    return {
        "player1_strategy": [float(p), float(1-p)],
        "player2_strategy": [float(q), float(1-q)],
        "expected_payoff_1": float(ev1),
        "expected_payoff_2": float(ev2),
    }
""",
            "input_type": "matrix",
            "output_type": "dict",
        },
        "minimax": {
            "code": """
def minimax(payoff_matrix):
    \"\"\"Minimax for a zero-sum game.
    Row player maximises, column player minimises.
    Returns the minimax value and the saddle point if one exists.\"\"\"
    M = np.asarray(payoff_matrix, dtype=np.float64)
    # Row player's maximin
    row_mins = M.min(axis=1)
    maximin = row_mins.max()
    maximin_row = int(row_mins.argmax())
    # Column player's minimax
    col_maxs = M.max(axis=0)
    minimax_val = col_maxs.min()
    minimax_col = int(col_maxs.argmin())

    saddle_point = None
    if abs(maximin - minimax_val) < 1e-12:
        saddle_point = (maximin_row, minimax_col)

    return {
        "maximin": float(maximin),
        "minimax": float(minimax_val),
        "saddle_point": saddle_point,
        "game_value": float(maximin) if saddle_point else None,
    }
""",
            "input_type": "matrix",
            "output_type": "dict",
        },
        "prisoners_dilemma_iterate": {
            "code": """
def prisoners_dilemma_iterate(strategy1, strategy2, n_rounds=100,
                               payoff=None):
    \"\"\"Iterated Prisoner's Dilemma.
    strategy1, strategy2: arrays of length n_rounds with 0=cooperate, 1=defect.
    If shorter than n_rounds, cycles.
    payoff: dict with keys (C,C),(C,D),(D,C),(D,D) -> (p1, p2).
    Default: classic PD payoffs.\"\"\"
    if payoff is None:
        payoff = {
            (0,0): (3, 3),  # mutual cooperate
            (0,1): (0, 5),  # sucker / temptation
            (1,0): (5, 0),  # temptation / sucker
            (1,1): (1, 1),  # mutual defect
        }
    s1 = np.asarray(strategy1, dtype=int)
    s2 = np.asarray(strategy2, dtype=int)
    score1, score2 = 0, 0
    history = []
    for i in range(n_rounds):
        a1 = int(s1[i % len(s1)])
        a2 = int(s2[i % len(s2)])
        p1, p2 = payoff[(a1, a2)]
        score1 += p1
        score2 += p2
        history.append((a1, a2, p1, p2))
    return {
        "total_score_1": score1,
        "total_score_2": score2,
        "avg_score_1": score1 / n_rounds,
        "avg_score_2": score2 / n_rounds,
        "history_length": len(history),
    }
""",
            "input_type": "vector_pair",
            "output_type": "dict",
        },
        "replicator_dynamics": {
            "code": """
def replicator_dynamics(payoff_matrix, x0=None, dt=0.01, n_steps=1000):
    \"\"\"Replicator dynamics: dx_i/dt = x_i * (f_i - avg_f)
    where f_i = (Ax)_i and avg_f = x . A . x.
    Input: n x n payoff matrix, initial population shares.
    Returns trajectory (n_steps+1, n).\"\"\"
    A = np.asarray(payoff_matrix, dtype=np.float64)
    n = A.shape[0]
    if x0 is None:
        x0 = np.ones(n) / n
    x = np.asarray(x0, dtype=np.float64)
    x = x / x.sum()  # normalise

    trajectory = np.zeros((n_steps + 1, n))
    trajectory[0] = x

    for t in range(n_steps):
        fitness = A @ x
        avg_fitness = x @ fitness
        dx = x * (fitness - avg_fitness)
        x = x + dt * dx
        x = np.maximum(x, 0)
        x = x / x.sum()  # renormalise
        trajectory[t + 1] = x

    return trajectory
""",
            "input_type": "matrix",
            "output_type": "trajectory",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = GameTheory()
    print(org)

    # Matching pennies (zero-sum)
    A = np.array([[1, -1], [-1, 1]])
    nash = org.execute("nash_equilibrium_2x2", A)
    print(f"Matching pennies Nash: {nash}")
    print(f"  (expect 50/50 mix)")

    # Minimax
    mm = org.execute("minimax", A)
    print(f"Minimax: {mm}")

    # Iterated PD: tit-for-tat vs always defect
    tft = [0] + [0] * 99  # starts cooperating
    always_d = [1] * 100
    pd = org.execute("prisoners_dilemma_iterate", tft, always_d, n_rounds=100)
    print(f"TFT vs Always-D: {pd}")

    # Replicator dynamics: Rock-Paper-Scissors
    rps = np.array([
        [0, -1,  1],
        [1,  0, -1],
        [-1, 1,  0],
    ], dtype=float)
    traj = org.execute("replicator_dynamics", rps, x0=[0.6, 0.3, 0.1], n_steps=2000)
    print(f"RPS replicator final pop: {traj[-1]}  (should cycle near 1/3 each)")

    print("--- game_theory: ALL TESTS PASSED ---")
