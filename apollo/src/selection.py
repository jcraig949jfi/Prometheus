"""
selection.py — NSGA-III with Das-Dennis reference directions for 6 objectives.

Apollo v2c: replaces NSGA-II crowding distance with reference-point niching.
No parsimony tiebreaker (per roadmap P2-4 recommendation).
Backward-compatible function name: nsga2_select (aliased to nsga3_select).
"""

import numpy as np
from itertools import combinations_with_replacement


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


# ── Das-Dennis reference directions ─────────────────────────────────

def _generate_das_dennis(n_objectives, n_partitions):
    """Generate Das-Dennis reference directions on the unit simplex.

    For n_objectives=6, n_partitions=3: C(3+5, 5) = 56 reference points.
    """
    ref_dirs = []
    for combo in combinations_with_replacement(range(n_partitions + 1), n_objectives - 1):
        # Convert combination to direction
        points = [0] + list(combo) + [n_partitions]
        diffs = [points[i + 1] - points[i] for i in range(len(points) - 1)]
        direction = np.array(diffs, dtype=np.float64) / n_partitions
        ref_dirs.append(direction)

    # De-duplicate (combinations_with_replacement can produce duplicates
    # when sorted differently)
    unique = []
    seen = set()
    for d in ref_dirs:
        key = tuple(np.round(d, 8))
        if key not in seen:
            seen.add(key)
            unique.append(d)

    return np.array(unique)


# Pre-compute for 6 objectives, n_partitions=3
_REF_DIRS_6D = None


def _get_ref_dirs():
    """Get cached reference directions."""
    global _REF_DIRS_6D
    if _REF_DIRS_6D is None:
        _REF_DIRS_6D = _generate_das_dennis(6, 3)
    return _REF_DIRS_6D


# ── NSGA-III niching ────────────────────────────────────────────────

def _normalize_objectives(fitness_arrays, front_indices):
    """Normalize objectives to [0, 1] using ideal and nadir points."""
    if not front_indices:
        return []

    arr = np.array([fitness_arrays[i] for i in front_indices])
    ideal = arr.max(axis=0)  # best value per objective (we maximize)
    nadir = arr.min(axis=0)

    ranges = ideal - nadir
    ranges[ranges < 1e-12] = 1e-12  # avoid division by zero

    # Normalize: 0 = nadir, 1 = ideal
    normalized = {}
    for idx in front_indices:
        normalized[idx] = (fitness_arrays[idx] - nadir) / ranges

    return normalized


def _associate_to_reference_points(normalized, ref_dirs):
    """Associate each solution to its nearest reference line.

    Returns:
        associations: dict[idx] -> (ref_point_idx, perpendicular_distance)
    """
    associations = {}
    for idx, norm_vec in normalized.items():
        min_dist = float('inf')
        best_ref = 0
        for r, ref_dir in enumerate(ref_dirs):
            # Perpendicular distance from norm_vec to reference line
            # Project norm_vec onto ref_dir
            ref_norm = ref_dir / (np.linalg.norm(ref_dir) + 1e-12)
            proj_length = np.dot(norm_vec, ref_norm)
            proj = proj_length * ref_norm
            dist = np.linalg.norm(norm_vec - proj)
            if dist < min_dist:
                min_dist = dist
                best_ref = r
        associations[idx] = (best_ref, min_dist)
    return associations


def _niching_select(front_indices, associations, niche_counts, remaining):
    """Select 'remaining' solutions from front using niche-count based selection.

    Prefer solutions associated with reference points that have fewer
    members in already-selected set. Break ties by perpendicular distance.
    """
    selected = []

    # Build ref_point -> [(idx, dist)] mapping for this front
    ref_members = {}
    for idx in front_indices:
        ref_idx, dist = associations[idx]
        ref_members.setdefault(ref_idx, []).append((idx, dist))

    # Sort members of each ref point by distance (closer = better)
    for ref_idx in ref_members:
        ref_members[ref_idx].sort(key=lambda x: x[1])

    available = set(front_indices)

    for _ in range(remaining):
        if not available:
            break

        # Find reference point(s) with minimum niche count
        min_count = float('inf')
        candidate_refs = []
        for ref_idx, members in ref_members.items():
            alive = [(i, d) for i, d in members if i in available]
            if alive:
                count = niche_counts.get(ref_idx, 0)
                if count < min_count:
                    min_count = count
                    candidate_refs = [ref_idx]
                elif count == min_count:
                    candidate_refs.append(ref_idx)

        if not candidate_refs:
            break

        # Pick random reference point among minimum-count ones
        import random
        chosen_ref = random.choice(candidate_refs)

        # Pick the closest solution to this reference line
        alive_members = [(i, d) for i, d in ref_members[chosen_ref]
                         if i in available]
        if not alive_members:
            continue

        chosen_idx = alive_members[0][0]  # closest
        selected.append(chosen_idx)
        available.discard(chosen_idx)
        niche_counts[chosen_ref] = niche_counts.get(chosen_ref, 0) + 1

    return selected


def nsga3_select(organisms, fitness_vectors, target_size,
                 gene_counts=None):
    """NSGA-III selection with reference-point niching.

    Args:
        organisms: list of organisms
        fitness_vectors: list of FitnessVector objects
        target_size: number of organisms to select
        gene_counts: ignored (kept for backward compat, no parsimony tiebreaker)

    Returns:
        list of selected indices
    """
    fitness_arrays = [fv.as_array() for fv in fitness_vectors]
    fronts = non_dominated_sort(fitness_arrays)
    ref_dirs = _get_ref_dirs()

    selected = []
    niche_counts = {}  # ref_point_idx -> count of selected solutions

    # Collect all indices for normalization
    all_indices = [i for front in fronts for i in front]
    normalized = _normalize_objectives(fitness_arrays, all_indices)

    # Associate all solutions to reference points
    associations = _associate_to_reference_points(normalized, ref_dirs)

    for front in fronts:
        if len(selected) + len(front) <= target_size:
            # Entire front fits
            selected.extend(front)
            # Update niche counts
            for idx in front:
                ref_idx = associations[idx][0]
                niche_counts[ref_idx] = niche_counts.get(ref_idx, 0) + 1
        else:
            # Need to pick a subset from this front
            remaining = target_size - len(selected)
            chosen = _niching_select(front, associations, niche_counts,
                                     remaining)
            selected.extend(chosen)
            break

    return selected


# Backward-compatible alias
def nsga2_select(organisms, fitness_vectors, target_size,
                 gene_counts=None):
    """Backward-compatible wrapper — delegates to NSGA-III."""
    return nsga3_select(organisms, fitness_vectors, target_size,
                        gene_counts=gene_counts)


# ── Elites (unchanged) ──────────────────────────────────────────────

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

        f_range = (fitness_arrays[sorted_front[-1]][m] -
                   fitness_arrays[sorted_front[0]][m])
        if f_range < 1e-12:
            continue

        for k in range(1, len(sorted_front) - 1):
            distances[sorted_front[k]] += (
                fitness_arrays[sorted_front[k + 1]][m] -
                fitness_arrays[sorted_front[k - 1]][m]
            ) / f_range

    return distances


def select_elites(fitness_vectors: list, k: int = 5,
                  gene_counts: list = None) -> list:
    """Select top-k elites by Pareto rank then crowding distance."""
    fitness_arrays = [fv.as_array() for fv in fitness_vectors]
    fronts = non_dominated_sort(fitness_arrays)

    candidates = []
    for front in fronts:
        cd = crowding_distance(fitness_arrays, front)
        for idx in front:
            candidates.append(
                (idx, 0 if front == fronts[0] else 1, -cd[idx])
            )
        if len(candidates) >= k:
            break

    candidates.sort(key=lambda x: (x[1], x[2]))
    return [c[0] for c in candidates[:k]]
