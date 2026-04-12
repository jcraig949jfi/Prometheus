"""
monitor.py — Stagnation Monitor for Apollo v2c.

Tracks hypervolume proxy, accuracy plateau, archive growth, and
mutation acceptance rate. Fires alerts when stagnation detected.
"""

import numpy as np


def _hypervolume_proxy(fitness_vectors, ref_point=None):
    """Compute a hypervolume proxy (sum of dominated hypervolume slices).

    True hypervolume is expensive for 6D. This proxy uses the sum of
    per-objective contributions above the reference point, weighted by
    Pareto rank. Not exact HV but correlates well for stagnation detection.
    """
    if not fitness_vectors:
        return 0.0

    arrays = [fv.as_array() for fv in fitness_vectors]
    if ref_point is None:
        ref_point = np.zeros(len(arrays[0]))

    # Simple proxy: sum of (value - ref) for all non-dominated solutions
    total = 0.0
    for arr in arrays:
        contributions = np.maximum(arr - ref_point, 0.0)
        total += float(np.prod(contributions + 1e-10))  # pseudo-volume

    return total


class StagnationMonitor:
    """Monitors evolution progress and fires alerts on stagnation.

    Tracks:
    - Hypervolume proxy over time
    - Best accuracy plateau
    - Archive growth rate
    - Mutation acceptance rate
    """

    def __init__(self, window=50):
        self.window = window
        self.hv_history = []
        self.accuracy_history = []
        self.archive_growth_history = []
        self.mutation_accept_history = []
        self.neutral_mutation_ratio = []

    def update(self, fitness_vectors, archive_size, accepted, total,
               neutral_count=0):
        """Record metrics for this generation.

        Args:
            fitness_vectors: list of FitnessVector for current population
            archive_size: current novelty archive size
            accepted: number of offspring that survived selection
            total: total offspring generated
            neutral_count: mutations that didn't change fitness
        """
        # 1. Hypervolume proxy
        hv = _hypervolume_proxy(fitness_vectors)
        self.hv_history.append(hv)

        # 2. Best accuracy
        if fitness_vectors:
            best_acc = max(fv.accuracy_margin for fv in fitness_vectors)
        else:
            best_acc = 0.0
        self.accuracy_history.append(best_acc)

        # 3. Archive growth
        self.archive_growth_history.append(archive_size)

        # 4. Mutation acceptance rate
        self.mutation_accept_history.append(
            accepted / max(total, 1)
        )

        # 5. Neutral mutation ratio
        self.neutral_mutation_ratio.append(
            neutral_count / max(total, 1)
        )

    def check_alerts(self, generation):
        """Check for stagnation conditions.

        Returns:
            list of alert strings (empty if no issues)
        """
        alerts = []

        # Hypervolume stagnation
        if len(self.hv_history) >= self.window:
            delta = self.hv_history[-1] - self.hv_history[-self.window]
            if abs(delta) < 0.001:
                alerts.append(
                    f"STAGNATION: HV delta < 0.001 over {self.window} gens "
                    f"(gen {generation})"
                )

        # Accuracy plateau
        if len(self.accuracy_history) >= self.window:
            recent = self.accuracy_history[-self.window:]
            if max(recent) - min(recent) < 0.005:
                alerts.append(
                    f"PLATEAU: Accuracy range < 0.005 over {self.window} gens"
                )

        # Low mutation acceptance
        if self.mutation_accept_history:
            if self.mutation_accept_history[-1] < 0.10:
                alerts.append(
                    "WARNING: Mutation acceptance rate < 10%"
                )

        # Archive growth stalled
        if len(self.archive_growth_history) >= 100:
            growth = (self.archive_growth_history[-1] -
                      self.archive_growth_history[-100])
            if growth < 5:
                alerts.append(
                    "WARNING: Archive growth < 5 entries in 100 gens"
                )

        # Neutral mutation dominance
        if self.neutral_mutation_ratio:
            if self.neutral_mutation_ratio[-1] > 0.8:
                alerts.append(
                    "WARNING: >80% neutral mutations — plateau drift"
                )

        return alerts

    def should_intervene(self, generation):
        """Check if intervention is needed (restart, temp boost, etc.)."""
        alerts = self.check_alerts(generation)
        return any("STAGNATION" in a for a in alerts)

    def get_stats(self):
        """Return current monitor stats for logging."""
        stats = {}
        if self.hv_history:
            stats["hv_current"] = self.hv_history[-1]
            if len(self.hv_history) >= self.window:
                stats["hv_delta"] = (self.hv_history[-1] -
                                     self.hv_history[-self.window])
        if self.accuracy_history:
            stats["best_accuracy"] = self.accuracy_history[-1]
        if self.mutation_accept_history:
            stats["accept_rate"] = self.mutation_accept_history[-1]
        if self.archive_growth_history:
            stats["archive_size"] = self.archive_growth_history[-1]
        return stats
