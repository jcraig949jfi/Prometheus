"""Chaotic Kolmogorov Free-Energy Engine v3.
Chaos Theory x Kolmogorov Complexity x Free Energy Principle.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """CKFE v3: structural parsers + chaos-Kolmogorov secondary."""

    def __init__(self):
        self._level = 6
        self._r = 3.9

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _chaos_kolm(self, prompt: str, cand: str) -> float:
        """Logistic chaos seeded by compression ratio."""
        cp = self._c(prompt)
        cc = self._c(cand)
        ratio = cc / max(cp, 1)
        x = max(0.01, min(0.99, ratio))
        for _ in range(6):
            x = self._r * x * (1.0 - x)
        # Blend with Occam: prefer concise
        occam = max(0.0, 1.0 - abs(ratio - 0.4) * 2.0)
        return 0.5 * x + 0.5 * occam

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        ck = self._chaos_kolm(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * ck
        else:
            raw = 0.55 * ncd_sim + 0.45 * ck
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+ck"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
