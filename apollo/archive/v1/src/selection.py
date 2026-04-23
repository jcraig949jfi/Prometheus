"""
selection.py — NSGA-II with 3 objectives + top-5 elitism + parsimony tiebreaker.
"""

import numpy as np


def _dominates(a: np.ndarray, b: np.ndarray) -> bool:
    """True if a Pareto-dominates b (all >= and at least one >)."""
    return np.all(a >= b) and np.any(a > b)


def non_dominated_sort(fitness_arrays: list) -> list:
    """Returns list of fronts, each front is a list of indices."""
    n = len(fitness_arrays)
    if n == 0:
        return []

    domination_count = [0] * n
    dominated_by = [[] for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            if _dominates(fitness_arrays[i], fitness_arrays[j]):
                dominated_by[i].append(j)
                domination_count[j] += 1
            elif _dominates(fitness_arrays[j], fitness_arrays[i]):
                dominated_by[j].append(i)
                domination_count[i] += 1

    fronts = []
    current_front = [i for i in range(n) if domination_count[i] == 0]

    while current_front:
        fronts.append(current_front)
        next_front = []
        for i in current_front:
            for j in dominated_by[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        current_front = next_front

    return fronts


def crowding_distance(fitness_arrays: list, front: list) -> dict:
    """Compute crowding distance for members of a front."""
    if len(front) <= 2:
        return {idx: float('inf') for idx in front}

    n_obj = len(fitness_arrays[0])
    distances = {idx: 0.0 for idx in front}

    for m in range(n_obj):
        sorted_front = sorted(front, key=lambda i: fitness_arrays[i][m])
        distances[sorted_front[0]] = float('inf')
        distances[sorted_front[-1]] = float('inf')

        f_range = fitness_arrays[sorted_front[-1]][m] - fitness_arrays[sorted_front[0]][m]
        if f_range < 1e-12:
            continue

        for k in range(1, len(sorted_front) - 1):
            distances[sorted_front[k]] += (
                fitness_arrays[sorted_front[k + 1]][m] -
                fitness_arrays[sorted_front[k - 1]][m]
            ) / f_range

    return distances


def nsga2_select(organisms: list, fitness_vectors: list, target_size: int,
                 gene_counts: list = None) -> list:
    """NSGA-II selection. Returns indices of selected organisms."""
    fitness_arrays = [fv.as_array() for fv in fitness_vectors]
    fronts = non_dominated_sort(fitness_arrays)

    selected = []
    for front in fronts:
        if len(selected) + len(front) <= target_size:
            selected.extend(front)
        else:
            remaining = target_size - len(selected)
            cd = crowding_distance(fitness_arrays, front)

            # Parsimony tiebreaker: when crowding distances are similar, prefer fewer genes
            def sort_key(idx):
                gc = gene_counts[idx] if gene_counts else 0
                return (-cd[idx], gc)  # Higher crowding first, fewer genes first

            sorted_front = sorted(front, key=sort_key)
            selected.extend(sorted_front[:remaining])
            break

    return selected


def select_elites(fitness_vectors: list, k: int = 5, gene_counts: list = None) -> list:
    """Select top-k elites by Pareto rank then crowding distance."""
    fitness_arrays = [fv.as_array() for fv in fitness_vectors]
    fronts = non_dominated_sort(fitness_arrays)

    candidates = []
    for front in fronts:
        cd = crowding_distance(fitness_arrays, front)
        for idx in front:
            candidates.append((idx, 0 if front == fronts[0] else 1, -cd[idx]))
        if len(candidates) >= k:
            break

    candidates.sort(key=lambda x: (x[1], x[2]))
    return [c[0] for c in candidates[:k]]
