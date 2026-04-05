"""
selection.py — NSGA-III with 6 objectives + reference-point niching.

Replaces NSGA-II crowding-distance selection with NSGA-III Das-Dennis
reference-point niching for better diversity in high-dimensional
objective spaces (6D).
"""

import itertools
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


# ── NSGA-III Reference Point Infrastructure ─────────────────────────


def _generate_reference_directions(n_obj=6, n_partitions=3):
    """Das-Dennis method: generate simplex lattice points that sum to 1.

    For n_obj=6, n_partitions=3 this gives C(8,5) = 56 reference points.
    """
    # Generate all combinations of non-negative integers that sum to n_partitions
    # using stars-and-bars via itertools
    ref_dirs = []
    for combo in itertools.combinations(
        range(n_partitions + n_obj - 1), n_obj - 1
    ):
        # Convert combination to partition sizes
        point = []
        prev = -1
        for c in combo:
            point.append(c - prev - 1)
            prev = c
        point.append(n_partitions + n_obj - 2 - prev)
        ref_dirs.append([p / n_partitions for p in point])

    return np.array(ref_dirs)


def _normalize_fitness(fitness_arrays, front_indices):
    """Normalize fitness values to [0, 1] using ideal and nadir points.

    Since all objectives are maximized, ideal = max per objective,
    nadir = min per objective across the population.
    """
    all_indices = []
    for front in front_indices:
        all_indices.extend(front)

    if not all_indices:
        return np.array([]), np.array([]), np.array([])

    mat = np.array([fitness_arrays[i] for i in all_indices])

    # Ideal point: best (max) per objective across population
    ideal = mat.max(axis=0)
    # Nadir point: worst (min) per objective across population
    nadir = mat.min(axis=0)

    # Avoid division by zero
    denom = ideal - nadir
    denom[denom < 1e-12] = 1e-12

    # Normalize so that ideal maps to 1 and nadir maps to 0
    normalized = {}
    for idx in all_indices:
        normalized[idx] = (fitness_arrays[idx] - nadir) / denom

    return normalized, ideal, nadir


def _associate_to_reference_points(normalized_fitness, ref_dirs, indices):
    """For each solution, find the reference line with minimum perpendicular distance.

    Returns:
        association_map: dict mapping ref_point_index -> list of solution indices
        perp_distances: dict mapping solution_index -> perpendicular distance
        closest_ref: dict mapping solution_index -> ref_point_index
    """
    association_map = {j: [] for j in range(len(ref_dirs))}
    perp_distances = {}
    closest_ref = {}

    for idx in indices:
        if idx not in normalized_fitness:
            continue
        point = normalized_fitness[idx]

        min_dist = float('inf')
        min_ref = 0

        for j, ref in enumerate(ref_dirs):
            # Perpendicular distance from point to reference line (origin -> ref)
            # Project point onto the reference direction
            ref_norm = ref / (np.linalg.norm(ref) + 1e-12)
            proj_scalar = np.dot(point, ref_norm)
            proj = proj_scalar * ref_norm
            perp_dist = np.linalg.norm(point - proj)

            if perp_dist < min_dist:
                min_dist = perp_dist
                min_ref = j

        association_map[min_ref].append(idx)
        perp_distances[idx] = min_dist
        closest_ref[idx] = min_ref

    return association_map, perp_distances, closest_ref


# ── Legacy crowding distance (kept for backward compat) ─────────────


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


# ── NSGA-III Selection ───────────────────────────────────────────────


# Module-level cached reference directions
_REF_DIRS_CACHE = {}


def _get_ref_dirs(n_obj=6, n_partitions=3):
    """Get or create cached reference directions."""
    key = (n_obj, n_partitions)
    if key not in _REF_DIRS_CACHE:
        _REF_DIRS_CACHE[key] = _generate_reference_directions(n_obj, n_partitions)
    return _REF_DIRS_CACHE[key]


def nsga3_select(organisms: list, fitness_vectors: list, target_size: int,
                 gene_counts: list = None) -> list:
    """NSGA-III selection with reference-point niching.

    Returns indices of selected organisms.
    """
    fitness_arrays = [fv.as_array() for fv in fitness_vectors]
    fronts = non_dominated_sort(fitness_arrays)

    if not fronts:
        return []

    n_obj = len(fitness_arrays[0])
    ref_dirs = _get_ref_dirs(n_obj)

    # Fill selected from complete fronts
    selected = []
    last_front_idx = -1

    for fi, front in enumerate(fronts):
        if len(selected) + len(front) <= target_size:
            selected.extend(front)
            last_front_idx = fi
        else:
            last_front_idx = fi
            break
    else:
        # All fronts fit
        return selected[:target_size]

    if len(selected) >= target_size:
        return selected[:target_size]

    # Need to partially include the last front
    remaining_needed = target_size - len(selected)
    last_front = fronts[last_front_idx]

    # Normalize fitness across all fronts up to and including last_front
    included_fronts = fronts[:last_front_idx + 1]
    normalized, ideal, nadir = _normalize_fitness(fitness_arrays, included_fronts)

    if not normalized:
        # Fallback: just take first remaining_needed from last front
        selected.extend(last_front[:remaining_needed])
        return selected

    # Associate already-selected solutions to reference points
    already_selected_set = set(selected)
    assoc_selected, perp_sel, closest_sel = _associate_to_reference_points(
        normalized, ref_dirs, list(already_selected_set)
    )

    # Associate last-front solutions to reference points
    assoc_last, perp_last, closest_last = _associate_to_reference_points(
        normalized, ref_dirs, last_front
    )

    # Count how many already-selected solutions per reference point
    rho = {}  # niche count
    for j in range(len(ref_dirs)):
        rho[j] = len(assoc_selected[j])

    # Niching procedure: pick from least-populated reference points
    last_front_remaining = set(last_front)
    chosen_from_last = []

    while len(chosen_from_last) < remaining_needed and last_front_remaining:
        # Find minimum niche count among ref points that have candidates in last front
        ref_with_candidates = []
        for j in range(len(ref_dirs)):
            candidates_j = [idx for idx in assoc_last[j] if idx in last_front_remaining]
            if candidates_j:
                ref_with_candidates.append((rho[j], j, candidates_j))

        if not ref_with_candidates:
            break

        min_count = min(r[0] for r in ref_with_candidates)
        # All ref points with minimum niche count
        min_refs = [(j, cands) for (cnt, j, cands) in ref_with_candidates if cnt == min_count]

        # Pick one reference point randomly from the tied set
        j_pick, cands = min_refs[np.random.randint(len(min_refs))]

        # Pick the candidate with smallest perpendicular distance
        best_idx = min(cands, key=lambda idx: perp_last.get(idx, float('inf')))

        chosen_from_last.append(best_idx)
        last_front_remaining.discard(best_idx)
        rho[j_pick] += 1

        # Remove from association map to avoid re-picking
        if best_idx in assoc_last[j_pick]:
            assoc_last[j_pick].remove(best_idx)

    selected.extend(chosen_from_last)
    return selected[:target_size]


def select_elites(fitness_vectors: list, k: int = 5, gene_counts: list = None) -> list:
    """Select top-k elites by Pareto rank then reference-point diversity."""
    fitness_arrays = [fv.as_array() for fv in fitness_vectors]
    fronts = non_dominated_sort(fitness_arrays)

    if not fronts:
        return []

    n_obj = len(fitness_arrays[0]) if fitness_arrays else 6
    ref_dirs = _get_ref_dirs(n_obj)

    # Normalize across all fronts
    normalized, ideal, nadir = _normalize_fitness(fitness_arrays, fronts)

    if not normalized:
        # Fallback
        return list(range(min(k, len(fitness_arrays))))

    # Collect candidates front by front
    candidates = []
    for fi, front in enumerate(fronts):
        for idx in front:
            candidates.append((idx, fi))
        if len(candidates) >= k:
            break

    if len(candidates) <= k:
        return [c[0] for c in candidates]

    # All candidates from front 0
    front0 = [c[0] for c in candidates if c[1] == 0]

    if len(front0) >= k:
        # Need to select k from front 0 using reference-point diversity
        assoc, perp, closest = _associate_to_reference_points(
            normalized, ref_dirs, front0
        )

        selected_elites = []
        remaining = set(front0)
        rho = {j: 0 for j in range(len(ref_dirs))}

        while len(selected_elites) < k and remaining:
            ref_with_candidates = []
            for j in range(len(ref_dirs)):
                cands = [idx for idx in assoc[j] if idx in remaining]
                if cands:
                    ref_with_candidates.append((rho[j], j, cands))

            if not ref_with_candidates:
                break

            min_count = min(r[0] for r in ref_with_candidates)
            min_refs = [(j, cands) for (cnt, j, cands) in ref_with_candidates if cnt == min_count]

            j_pick, cands = min_refs[np.random.randint(len(min_refs))]
            best_idx = min(cands, key=lambda idx: perp.get(idx, float('inf')))

            selected_elites.append(best_idx)
            remaining.discard(best_idx)
            rho[j_pick] += 1
            if best_idx in assoc[j_pick]:
                assoc[j_pick].remove(best_idx)

        return selected_elites[:k]
    else:
        # Take all of front 0, fill from subsequent fronts
        selected_elites = list(front0)
        remaining_needed = k - len(selected_elites)

        later_candidates = [c[0] for c in candidates if c[1] > 0]

        # Use reference-point niching for the remaining
        assoc_sel, _, _ = _associate_to_reference_points(
            normalized, ref_dirs, selected_elites
        )
        rho = {j: len(assoc_sel[j]) for j in range(len(ref_dirs))}

        assoc_later, perp_later, _ = _associate_to_reference_points(
            normalized, ref_dirs, later_candidates
        )

        remaining = set(later_candidates)

        while len(selected_elites) < k and remaining:
            ref_with_candidates = []
            for j in range(len(ref_dirs)):
                cands = [idx for idx in assoc_later[j] if idx in remaining]
                if cands:
                    ref_with_candidates.append((rho[j], j, cands))

            if not ref_with_candidates:
                break

            min_count = min(r[0] for r in ref_with_candidates)
            min_refs = [(j, cands) for (cnt, j, cands) in ref_with_candidates if cnt == min_count]

            j_pick, cands = min_refs[np.random.randint(len(min_refs))]
            best_idx = min(cands, key=lambda idx: perp_later.get(idx, float('inf')))

            selected_elites.append(best_idx)
            remaining.discard(best_idx)
            rho[j_pick] += 1
            if best_idx in assoc_later[j_pick]:
                assoc_later[j_pick].remove(best_idx)

        return selected_elites[:k]


# ── Backward compatibility ───────────────────────────────────────────

# Alias: nsga2_select points to nsga3_select for drop-in replacement
nsga2_select = nsga3_select
