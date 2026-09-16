"""Fitness regimes (directive VII). A regime is a cost VECTOR; its name labels the vector,
never an expected mechanism.

    fitness = reward - alpha*ops_per_episode/1000 - beta*persistent_words/64
                     - gamma*(in_reads+out_writes)_per_episode/100 - delta*ticks_late

reward is the fraction of ask events answered EXACTLY. ticks_late is 0 in v0.1.
persistent_words is the Meter's manifest-derived persistent_state_words.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Regime:
    name: str
    alpha: float = 0.0
    beta: float = 0.0
    gamma: float = 0.0
    delta: float = 0.0

    def fitness(self, reward: float, meter: dict, n_episodes: int) -> float:
        n = max(1, n_episodes)
        ops = meter["ops"] / n
        rw = (meter["in_reads"] + meter["out_writes"]) / n
        pw = meter.get("persistent_state_words", 0)
        return reward - self.alpha * ops / 1000.0 - self.beta * pw / 64.0 - self.gamma * rw / 100.0

    def as_dict(self) -> dict:
        return asdict(self)


REGIMES = {
    "E0": Regime("E0"),
    "E1": Regime("E1", alpha=0.02, beta=0.01),
    "E2": Regime("E2", alpha=0.10, beta=0.01),
    "E3": Regime("E3", alpha=0.01, beta=0.10),
}
