"""monitor.py — Stagnation detection and early warning for Apollo."""
import numpy as np
from collections import deque


class StagnationMonitor:
    def __init__(self, window=50):
        self.window = window
        self.best_acc_history = deque(maxlen=window*2)
        self.hv_proxy_history = deque(maxlen=window*2)
        self.archive_size_history = deque(maxlen=200)
        self.mutation_accept_history = deque(maxlen=window)

    def update(self, fitness_vectors, archive_size,
               accepted_count=None, total_count=None):
        """Call every generation after selection."""
        # Best accuracy
        arrays = [fv.as_array() for fv in fitness_vectors]
        if arrays:
            best_acc = max(a[0] for a in arrays)
            self.best_acc_history.append(best_acc)

            # Hypervolume proxy: sum of max values per objective across Pareto front
            mat = np.array(arrays)
            hv_proxy = float(np.prod(np.maximum(mat.max(axis=0), 1e-10)))
            self.hv_proxy_history.append(hv_proxy)

        self.archive_size_history.append(archive_size)

        if accepted_count is not None and total_count is not None:
            rate = accepted_count / max(total_count, 1)
            self.mutation_accept_history.append(rate)

    def check_alerts(self, generation):
        """Return list of alert strings. Call every N gens."""
        alerts = []

        # Best accuracy plateau
        if len(self.best_acc_history) >= self.window:
            recent = list(self.best_acc_history)[-self.window:]
            if max(recent) - min(recent) < 0.005:
                alerts.append(
                    f"STAGNATION: best accuracy plateau at {recent[-1]:.3f} "
                    f"for {self.window} gens")

        # Hypervolume stagnation
        if len(self.hv_proxy_history) >= self.window:
            recent = list(self.hv_proxy_history)[-self.window:]
            delta = abs(recent[-1] - recent[0])
            if delta < 0.001:
                alerts.append(
                    f"STAGNATION: hypervolume proxy delta < 0.001 "
                    f"over {self.window} gens")

        # Archive growth stall
        if len(self.archive_size_history) >= 100:
            recent = list(self.archive_size_history)
            growth = recent[-1] - recent[-100]
            if growth < 5:
                alerts.append(
                    f"WARNING: archive grew by only {growth} in last 100 gens")

        # Low mutation acceptance
        if len(self.mutation_accept_history) >= 10:
            recent_rate = np.mean(list(self.mutation_accept_history)[-10:])
            if recent_rate < 0.10:
                alerts.append(
                    f"WARNING: mutation acceptance rate {recent_rate:.1%} < 10%")

        return alerts

    def suggest_intervention(self):
        """Suggest intervention parameters when stagnation detected."""
        alerts = self.check_alerts(0)
        if not alerts:
            return {}

        intervention = {}
        for alert in alerts:
            if "STAGNATION" in alert:
                intervention["inject_random_fraction"] = 0.3
                intervention["temp_boost"] = 0.2
                intervention["novelty_weight_boost"] = 0.5
            elif "acceptance rate" in alert:
                intervention["temp_boost"] = 0.1

        return intervention
