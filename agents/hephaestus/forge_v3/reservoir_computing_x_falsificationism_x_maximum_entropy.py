"""Maximum-Entropy Reservoir Falsifier v3.
Reservoir Computing x Falsificationism x Maximum Entropy.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """MERF v3: structural parsers + reservoir-hash secondary."""

    def __init__(self):
        self._level = 6
        np.random.seed(42)
        self._W = np.random.randn(32, 16) * 0.3

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _reservoir_sim(self, prompt: str, cand: str) -> float:
        """Hash-based reservoir similarity."""
        def _vec(s):
            v = np.zeros(16)
            for i, ch in enumerate(s.encode()[:64]):
                v[i % 16] += ch / 255.0
            return np.tanh(self._W @ v)
        pv, cv = _vec(prompt), _vec(cand)
        dot = np.dot(pv, cv)
        n = (np.linalg.norm(pv) * np.linalg.norm(cv))
        return (dot / n + 1.0) / 2.0 if n > 0 else 0.5

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        res = self._reservoir_sim(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * res
        else:
            raw = 0.50 * ncd_sim + 0.50 * res
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+reservoir"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
