"""
Voting Theory -- Shapley-Shubik, Banzhaf, Kemeny, Condorcet, Arrow's impossibility

Connects to: [combinatorial_species, lattice_theory, game_of_life_mathematics, nim_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from itertools import permutations

FIELD_NAME = "voting_theory"
OPERATIONS = {}


def _build_preference_matrix(x):
    """Build pairwise preference matrix from flat input.
    Treats x as flattened preference profile: n_voters x n_candidates."""
    n = len(x)
    # Guess candidates = min(n, 5), voters = n // candidates
    n_cand = min(5, n)
    n_voters = max(1, n // n_cand)
    prefs = np.zeros((n_voters, n_cand))
    for i in range(n_voters):
        for j in range(n_cand):
            idx = i * n_cand + j
            prefs[i, j] = x[idx] if idx < n else 0
    # Pairwise matrix: P[i,j] = number of voters preferring i to j
    P = np.zeros((n_cand, n_cand))
    for v in range(n_voters):
        ranking = np.argsort(-prefs[v])  # higher value = more preferred
        for i in range(n_cand):
            for j in range(i + 1, n_cand):
                P[ranking[i], ranking[j]] += 1
                # If tie, split
    return P, n_cand, n_voters


def shapley_shubik_index(x):
    """Shapley-Shubik power index for a weighted voting game.
    Treats x as weights; quota = sum/2 + 1. Input: array. Output: array."""
    weights = np.abs(x)
    n = len(weights)
    quota = np.sum(weights) / 2.0 + 1.0
    ssi = np.zeros(n)
    # For small n, enumerate all permutations
    if n <= 8:
        count = 0
        for perm in permutations(range(n)):
            running = 0.0
            for i, p in enumerate(perm):
                running += weights[p]
                if running >= quota:
                    ssi[p] += 1
                    break
            count += 1
        ssi /= count
    else:
        # Monte Carlo approximation
        rng = np.random.RandomState(42)
        n_samples = 10000
        for _ in range(n_samples):
            perm = rng.permutation(n)
            running = 0.0
            for p in perm:
                running += weights[p]
                if running >= quota:
                    ssi[p] += 1
                    break
        ssi /= n_samples
    return ssi


OPERATIONS["shapley_shubik_index"] = {
    "fn": shapley_shubik_index,
    "input_type": "array",
    "output_type": "array",
    "description": "Shapley-Shubik power index for weighted voting game"
}


def banzhaf_index(x):
    """Banzhaf power index. Treats x as weights; quota = sum/2 + 1.
    Input: array. Output: array."""
    weights = np.abs(x)
    n = len(weights)
    quota = np.sum(weights) / 2.0 + 1.0
    banzhaf = np.zeros(n)
    # Enumerate all 2^n coalitions for small n
    if n <= 20:
        for mask in range(1, 1 << n):
            total = sum(weights[i] for i in range(n) if mask & (1 << i))
            if total >= quota:
                for i in range(n):
                    if mask & (1 << i):
                        if total - weights[i] < quota:
                            banzhaf[i] += 1
    total_swings = np.sum(banzhaf)
    if total_swings > 0:
        banzhaf /= total_swings
    return banzhaf


OPERATIONS["banzhaf_index"] = {
    "fn": banzhaf_index,
    "input_type": "array",
    "output_type": "array",
    "description": "Banzhaf power index (normalized) for weighted voting game"
}


def condorcet_winner(x):
    """Find Condorcet winner if exists. Input: array (pref profile). Output: scalar (winner index or -1)."""
    P, n_cand, _ = _build_preference_matrix(x)
    n_voters_total = np.max(P + P.T)
    for i in range(n_cand):
        wins_all = True
        for j in range(n_cand):
            if i != j and P[i, j] <= P[j, i]:
                wins_all = False
                break
        if wins_all:
            return float(i)
    return -1.0


OPERATIONS["condorcet_winner"] = {
    "fn": condorcet_winner,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Condorcet winner index (-1 if none exists)"
}


def borda_count(x):
    """Borda count scores. Input: array (preference values per candidate). Output: array."""
    P, n_cand, n_voters = _build_preference_matrix(x)
    # Borda: each pairwise win gives 1 point
    scores = np.sum(P, axis=1)
    return scores


OPERATIONS["borda_count"] = {
    "fn": borda_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Borda count scores from pairwise preference matrix"
}


def kemeny_ranking_score(x):
    """Kemeny score of the identity ranking (sum of agreements with pairwise preferences).
    Input: array. Output: scalar."""
    P, n_cand, _ = _build_preference_matrix(x)
    # Score of ranking 0 < 1 < 2 < ... (identity)
    score = 0.0
    for i in range(n_cand):
        for j in range(i + 1, n_cand):
            score += P[i, j]
    return float(score)


OPERATIONS["kemeny_ranking_score"] = {
    "fn": kemeny_ranking_score,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Kemeny score of the natural ranking"
}


def plurality_winner(x):
    """Plurality winner: candidate with most first-place votes.
    Input: array (treated as first-choice votes). Output: scalar."""
    n_cand = min(5, len(x))
    votes = np.zeros(n_cand)
    for v in x:
        idx = int(np.round(v)) % n_cand
        votes[idx] += 1
    return float(np.argmax(votes))


OPERATIONS["plurality_winner"] = {
    "fn": plurality_winner,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Plurality winner (most first-place votes)"
}


def copeland_score(x):
    """Copeland scores: +1 for each pairwise win, -1 for loss. Input: array. Output: array."""
    P, n_cand, _ = _build_preference_matrix(x)
    scores = np.zeros(n_cand)
    for i in range(n_cand):
        for j in range(n_cand):
            if i != j:
                if P[i, j] > P[j, i]:
                    scores[i] += 1
                elif P[i, j] < P[j, i]:
                    scores[i] -= 1
    return scores


OPERATIONS["copeland_score"] = {
    "fn": copeland_score,
    "input_type": "array",
    "output_type": "array",
    "description": "Copeland pairwise comparison scores"
}


def minimax_winner(x):
    """Minimax (Simpson) winner: minimize worst pairwise defeat. Input: array. Output: scalar."""
    P, n_cand, _ = _build_preference_matrix(x)
    worst_defeat = np.full(n_cand, -np.inf)
    for i in range(n_cand):
        for j in range(n_cand):
            if i != j:
                defeat_margin = P[j, i] - P[i, j]
                worst_defeat[i] = max(worst_defeat[i], defeat_margin)
    return float(np.argmin(worst_defeat))


OPERATIONS["minimax_winner"] = {
    "fn": minimax_winner,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Minimax (Simpson) winner minimizing worst pairwise defeat"
}


def arrow_impossibility_dimension(x):
    """Dimension of the space of social welfare functions satisfying IIA and Pareto.
    For n voters and k alternatives, Arrow says dim=n (dictatorships only).
    Input: array (first elem = n_voters, second = n_candidates). Output: scalar."""
    n_voters = max(1, int(np.round(x[0]))) if len(x) > 0 else 3
    n_cand = max(2, int(np.round(x[1]))) if len(x) > 1 else 3
    if n_cand >= 3:
        # Arrow's theorem: only dictatorships satisfy both conditions
        return float(n_voters)  # dimension = number of possible dictators
    else:
        # With 2 candidates, majority rule works
        return float(2 ** n_voters - 1)  # all monotone functions


OPERATIONS["arrow_impossibility_dimension"] = {
    "fn": arrow_impossibility_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of social welfare functions satisfying Arrow's conditions"
}


def voting_power_concentration(x):
    """Gini coefficient of voting power (Banzhaf). Input: array. Output: scalar."""
    bi = banzhaf_index(x)
    n = len(bi)
    if n <= 1 or np.sum(bi) == 0:
        return 0.0
    sorted_bi = np.sort(bi)
    cumulative = np.cumsum(sorted_bi)
    total = cumulative[-1]
    if total == 0:
        return 0.0
    # Gini = 1 - 2 * area under Lorenz curve
    lorenz = cumulative / total
    area = np.sum(lorenz) / n
    return float(1.0 - 2.0 * area + 1.0 / n)


OPERATIONS["voting_power_concentration"] = {
    "fn": voting_power_concentration,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Gini coefficient of Banzhaf voting power distribution"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
