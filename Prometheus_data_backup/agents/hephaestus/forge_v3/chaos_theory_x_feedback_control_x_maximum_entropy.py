"""Maximum-Entropy Adaptive Chaos Feedback v3.
Chaos Theory x Feedback Control x Maximum Entropy.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """MEACF v3: structural parsers + logistic-map entropy secondary."""

    def __init__(self):
        self._chaos_r = 3.9
        self._level = 6

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _chaos_secondary(self, prompt: str, cand: str) -> float:
        """Logistic-map seeded by token overlap ratio."""
        pw = set(prompt.lower().split())
        cw = set(cand.lower().split())
        overlap = len(pw & cw) / max(len(pw | cw), 1)
        x = max(0.01, min(0.99, overlap))
        for _ in range(5):
            x = self._chaos_r * x * (1.0 - x)
        return x

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        chaos = self._chaos_secondary(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * chaos
        else:
            raw = 0.55 * ncd_sim + 0.45 * chaos
        return max(0.0, min(1.0, raw)), tags

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        results = []
        for cand in candidates:
            s, tags = self._score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(s),
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+chaos"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
