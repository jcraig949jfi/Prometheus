"""YieldProportionalBandit — softmax-over-yield sampling with UCB exploration.

GFlowNet-spirit alternative to epsilon-greedy. Where epsilon-greedy
splits between exploit-best (greedy) and explore-uniform (random),
yield-proportional samples *each* selection with probability proportional
to `exp(yield_score / temperature)`. This produces diverse high-reward
samples without an explicit explore/exploit dichotomy — the same property
GFlowNets target via flow-conservation training.

Plus a UCB-style exploration bonus: generators with low fire counts get
a one-time boost proportional to `sqrt(log(total_fires) / n_fires)`.
After enough fires, the UCB term decays and pure yield-proportional
sampling dominates.

For Theseus's 40-generator categorical space this is the right level of
sophistication. Full GFlowNet (torchgfn) is overkill at this scale and
adds heavy PyTorch dependencies; the upgrade path is documented for
future scaling.
"""
from __future__ import annotations

import math
import random
from typing import Dict, List, Optional

from theseus.bandit.base import Bandit
from theseus.scoring.metrics_schema import GeneratorMetrics


class YieldProportionalBandit(Bandit):
    """Yield-proportional bandit with UCB exploration bonus.

    Parameters:
      temperature: softmax temperature. Lower → greedier (concentrated on
                   top-yield); higher → more uniform. 0.01 is the default
                   for the yield_score's natural [0, 0.01] scale.
      ucb_c:       UCB exploration coefficient. 0 disables exploration.
                   1.0 is the canonical value.
      seed:        RNG seed.
    """

    def __init__(
        self,
        temperature: float = 0.005,
        ucb_c: float = 1.0,
        seed: Optional[int] = None,
    ) -> None:
        self.temperature = temperature
        self.ucb_c = ucb_c
        self._rng = random.Random(seed)
        self._history: Dict[str, List[float]] = {}

    def select(
        self,
        available: List[str],
        history: Dict[str, List[GeneratorMetrics]],
        n: int = 5,
    ) -> List[str]:
        if len(available) <= n:
            return list(available)

        # Ingest any new history from caller
        for gid, ms in history.items():
            self._history.setdefault(gid, [])
            seen = len(self._history[gid])
            for m in ms[seen:]:
                self._history[gid].append(m.yield_score)

        # Compute mean yield per generator (0 if never fired)
        means: Dict[str, float] = {}
        fires: Dict[str, int] = {}
        for gid in available:
            ys = self._history.get(gid, [])
            means[gid] = sum(ys) / len(ys) if ys else 0.0
            fires[gid] = len(ys)

        # UCB exploration bonus
        total_fires = sum(fires.values())
        log_total = math.log(max(total_fires, 1)) if total_fires > 0 else 0.0
        scores: Dict[str, float] = {}
        for gid in available:
            n_g = fires[gid]
            if n_g == 0:
                ucb = self.ucb_c * 0.05  # initial exploration weight for never-fired
            elif self.ucb_c > 0 and log_total > 0:
                ucb = self.ucb_c * math.sqrt(log_total / n_g) * 0.001
            else:
                ucb = 0.0
            scores[gid] = means[gid] + ucb

        # Softmax with temperature
        T = max(self.temperature, 1e-6)
        max_score = max(scores.values())
        exps = {gid: math.exp((s - max_score) / T) for gid, s in scores.items()}
        total = sum(exps.values())
        if total <= 0:
            # Degenerate (all zero) — fall back to uniform
            return self._rng.sample(available, n)
        probs = {gid: e / total for gid, e in exps.items()}

        # Sample without replacement (sequential proportional draws)
        picked: List[str] = []
        remaining = list(available)
        remaining_probs = dict(probs)
        for _ in range(n):
            if not remaining:
                break
            total_r = sum(remaining_probs[g] for g in remaining)
            if total_r <= 0:
                # Fall back to uniform on the remainder
                pick = self._rng.choice(remaining)
            else:
                r = self._rng.random() * total_r
                cum = 0.0
                pick = remaining[-1]
                for g in remaining:
                    cum += remaining_probs[g]
                    if cum >= r:
                        pick = g
                        break
            picked.append(pick)
            remaining.remove(pick)

        return picked

    def update(self, batch_metrics: Dict[str, GeneratorMetrics]) -> None:
        for gid, m in batch_metrics.items():
            self._history.setdefault(gid, []).append(m.yield_score)
