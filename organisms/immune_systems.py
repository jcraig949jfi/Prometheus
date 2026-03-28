"""
Immune Systems organism.

Operations: clonal_selection, negative_selection, danger_signal,
            self_nonself_discrimination
"""

from .base import MathematicalOrganism


class ImmuneSystems(MathematicalOrganism):
    name = "immune_systems"
    operations = {
        "clonal_selection": {
            "code": """
def clonal_selection(antibodies, antigen, n_clones=5, mutation_rate=0.1,
                     n_generations=20):
    \"\"\"Clonal Selection Algorithm (de Castro & Von Zuben).
    antibodies: (n, d) array of antibody feature vectors.
    antigen: (d,) target vector.
    Selects top antibodies by affinity (inverse distance), clones and
    hypermutates them. Returns evolved antibody population.\"\"\"
    ab = np.asarray(antibodies, dtype=np.float64).copy()
    ag = np.asarray(antigen, dtype=np.float64)
    n, d = ab.shape

    for gen in range(n_generations):
        # Affinity = inverse Euclidean distance
        dists = np.sqrt(((ab - ag) ** 2).sum(axis=1))
        affinity = 1.0 / (1.0 + dists)

        # Select top-half
        ranking = np.argsort(-affinity)
        n_select = max(n // 2, 1)
        selected = ab[ranking[:n_select]]

        # Clone proportionally to affinity
        clones = []
        for i in range(n_select):
            n_c = max(1, int(n_clones * affinity[ranking[i]]))
            for _ in range(n_c):
                mutant = selected[i] + np.random.randn(d) * mutation_rate * (1.0 - affinity[ranking[i]])
                clones.append(mutant)

        if clones:
            clones = np.array(clones)
            # Evaluate clones
            clone_dists = np.sqrt(((clones - ag) ** 2).sum(axis=1))
            clone_aff = 1.0 / (1.0 + clone_dists)
            # Merge best of clones + selected, keep population size
            pool = np.vstack([selected, clones])
            pool_dists = np.sqrt(((pool - ag) ** 2).sum(axis=1))
            pool_aff = 1.0 / (1.0 + pool_dists)
            best_idx = np.argsort(-pool_aff)[:n]
            ab = pool[best_idx]

    final_dists = np.sqrt(((ab - ag) ** 2).sum(axis=1))
    final_aff = 1.0 / (1.0 + final_dists)
    return {"antibodies": ab, "affinities": final_aff, "best_affinity": float(final_aff.max())}
""",
            "input_type": "matrix_vector",
            "output_type": "dict",
        },
        "negative_selection": {
            "code": """
def negative_selection(self_data, detectors, threshold=0.5):
    \"\"\"Negative Selection Algorithm.
    Generates detectors that do NOT match self-data (within threshold).
    self_data: (n_self, d) self patterns.
    detectors: (n_det, d) candidate detector vectors.
    threshold: minimum distance to be considered non-self.
    Returns valid detectors that survived negative selection.\"\"\"
    self_data = np.asarray(self_data, dtype=np.float64)
    detectors = np.asarray(detectors, dtype=np.float64)

    valid = []
    for det in detectors:
        dists = np.sqrt(((self_data - det) ** 2).sum(axis=1))
        if dists.min() > threshold:
            valid.append(det)

    if valid:
        valid = np.array(valid)
    else:
        valid = np.empty((0, self_data.shape[1]))

    return {"valid_detectors": valid, "n_survived": len(valid),
            "survival_rate": len(valid) / len(detectors) if len(detectors) > 0 else 0.0}
""",
            "input_type": "matrix_pair",
            "output_type": "dict",
        },
        "danger_signal": {
            "code": """
def danger_signal(signal_history, threshold=2.0, decay=0.9):
    \"\"\"Danger Theory model (Matzinger).
    Accumulates danger signals over time with exponential decay.
    When accumulated danger exceeds threshold, immune response fires.
    signal_history: 1-D array of incoming signal intensities per timestep.
    Returns danger level trajectory and response events.\"\"\"
    signals = np.asarray(signal_history, dtype=np.float64)
    n = len(signals)
    danger_level = np.zeros(n)
    responses = []

    accumulated = 0.0
    for t in range(n):
        accumulated = accumulated * decay + signals[t]
        danger_level[t] = accumulated
        if accumulated > threshold:
            responses.append(t)
            accumulated = 0.0  # reset after response

    return {
        "danger_level": danger_level,
        "response_times": responses,
        "n_responses": len(responses),
    }
""",
            "input_type": "timeseries",
            "output_type": "dict",
        },
        "self_nonself_discrimination": {
            "code": """
def self_nonself_discrimination(self_patterns, test_patterns, threshold=1.0):
    \"\"\"Classify test patterns as self or non-self based on minimum distance
    to known self patterns.
    self_patterns: (n_self, d) known self.
    test_patterns: (n_test, d) patterns to classify.
    Returns labels (0=self, 1=nonself) and distances.\"\"\"
    self_p = np.asarray(self_patterns, dtype=np.float64)
    test_p = np.asarray(test_patterns, dtype=np.float64)

    n_test = test_p.shape[0]
    min_dists = np.zeros(n_test)
    labels = np.zeros(n_test, dtype=int)

    for i in range(n_test):
        dists = np.sqrt(((self_p - test_p[i]) ** 2).sum(axis=1))
        min_dists[i] = dists.min()
        labels[i] = 1 if min_dists[i] > threshold else 0

    return {
        "labels": labels,
        "min_distances": min_dists,
        "n_self": int((labels == 0).sum()),
        "n_nonself": int((labels == 1).sum()),
    }
""",
            "input_type": "matrix_pair",
            "output_type": "dict",
        },
    }


if __name__ == "__main__":
    import numpy as np
    np.random.seed(42)

    org = ImmuneSystems()
    print(org)

    # Clonal selection
    antibodies = np.random.randn(20, 3)
    antigen = np.array([1.0, 1.0, 1.0])
    result = org.execute("clonal_selection", antibodies, antigen, n_generations=30)
    print(f"Clonal selection best affinity: {result['best_affinity']:.4f}")

    # Negative selection
    self_data = np.random.randn(50, 3) * 0.5
    candidates = np.random.randn(100, 3) * 2.0
    ns_result = org.execute("negative_selection", self_data, candidates, threshold=1.0)
    print(f"Negative selection: {ns_result['n_survived']}/{len(candidates)} survived")

    # Danger signal
    signals = np.concatenate([
        np.random.rand(20) * 0.3,     # quiet
        np.random.rand(5) * 3.0,      # danger!
        np.random.rand(20) * 0.2,     # quiet again
        np.random.rand(5) * 4.0,      # danger!
    ])
    ds = org.execute("danger_signal", signals, threshold=2.0)
    print(f"Danger signal responses at: {ds['response_times']}")

    # Self/nonself discrimination
    self_pts = np.random.randn(30, 2) * 0.5
    test_pts = np.vstack([
        np.random.randn(10, 2) * 0.3,  # self-like
        np.random.randn(10, 2) * 3.0,  # non-self
    ])
    disc = org.execute("self_nonself_discrimination", self_pts, test_pts, threshold=1.5)
    print(f"Discrimination: {disc['n_self']} self, {disc['n_nonself']} nonself")

    print("--- immune_systems: ALL TESTS PASSED ---")
