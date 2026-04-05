"""
aos.py — Adaptive Operator Selection for Apollo v2c.

Multi-armed bandit with exponential moving average rewards.
Replaces fixed mutation rates with learned operator probabilities.
"""

import random
import numpy as np
from logger import log_debug


class AdaptiveOperatorSelector:
    """Multi-armed bandit over mutation operators.

    Uses exponential moving average to track operator rewards,
    with a minimum probability floor to prevent operator starvation.
    """

    def __init__(self, operators=None, alpha=0.3, p_min=0.05):
        """
        Args:
            operators: list of operator names
            alpha: EMA learning rate (higher = more reactive)
            p_min: minimum probability per operator
        """
        self.operators = operators or ['route', 'parameter', 'wiring', 'swap']
        self.alpha = alpha
        self.p_min = p_min
        self.rewards = {op: 0.0 for op in self.operators}
        self.counts = {op: 0 for op in self.operators}
        self.probs = {op: 1.0 / len(self.operators) for op in self.operators}

    @staticmethod
    def compute_reward(child_fitness, parent_fitness, generation,
                       accuracy_only_until=300):
        """Compute AOS reward. Early gens: accuracy-only. Later: Pareto."""
        if generation < accuracy_only_until:
            # Simple: did raw accuracy improve?
            child_acc = child_fitness.raw_accuracy if hasattr(child_fitness, 'raw_accuracy') else 0
            parent_acc = parent_fitness.raw_accuracy if hasattr(parent_fitness, 'raw_accuracy') else 0
            return 1.0 if child_acc > parent_acc else 0.0
        else:
            # Full Pareto: child dominates parent on any objective
            child_arr = child_fitness.as_array()
            parent_arr = parent_fitness.as_array()
            if np.all(child_arr >= parent_arr) and np.any(child_arr > parent_arr):
                return 1.0
            return 0.0

    def select(self):
        """Select an operator based on current probability distribution."""
        ops = list(self.probs.keys())
        return random.choices(ops, weights=[self.probs[o] for o in ops])[0]

    def update(self, operator, reward):
        """Update operator reward estimate.

        Args:
            operator: operator name
            reward: 1.0 if offspring Pareto-improves, 0.0 otherwise
        """
        if operator not in self.operators:
            return

        self.counts[operator] += 1
        # Exponential moving average
        self.rewards[operator] += (reward - self.rewards[operator]) * self.alpha

        # Recompute probabilities
        total = sum(max(r, 0) for r in self.rewards.values())
        n = len(self.operators)

        if total > 0:
            for op in self.operators:
                raw = max(self.rewards[op], 0) / total
                self.probs[op] = self.p_min + raw * (1 - n * self.p_min)
        # else keep uniform

        log_debug(
            f"AOS update: {operator} reward={reward:.2f} | probs={self.get_probabilities()}",
            stage="aos",
            data={
                "operator": operator,
                "reward": reward,
                "probabilities": self.get_probabilities(),
                "counts": dict(self.counts),
            }
        )

    def get_probabilities(self):
        """Return current operator probability distribution."""
        return dict(self.probs)

    def get_stats(self):
        """Return full stats for logging."""
        return {
            "probabilities": dict(self.probs),
            "rewards": dict(self.rewards),
            "counts": dict(self.counts),
        }

    def reset(self):
        """Reset to uniform distribution."""
        n = len(self.operators)
        self.rewards = {op: 0.0 for op in self.operators}
        self.counts = {op: 0 for op in self.operators}
        self.probs = {op: 1.0 / n for op in self.operators}
