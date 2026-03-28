"""Thermodynamic Maximum-Entropy Free-Energy Engine v3.
Thermodynamics x Free Energy Principle x Maximum Entropy.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """TMEFE v3: structural parsers + max-entropy free-energy secondary."""

    def __init__(self):
        self._level = 6
        self._beta = 1.5

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _maxent_fe(self, prompt: str, cand: str) -> float:
        """Free energy = surprise - entropy.  Normalised to [0,1]."""
        surprise = self._ncd(prompt, cand)
        cw = set(re.findall(r'\b\w+\b', cand.lower()))
        n = max(len(cw), 1)
        entropy_proxy = math.log(n + 1) / math.log(50)  # normalised
        fe = surprise - entropy_proxy / self._beta
        return max(0.0, 1.0 / (1.0 + math.exp(fe * 3)))

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        mfe = self._maxent_fe(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * mfe
        else:
            raw = 0.50 * ncd_sim + 0.50 * mfe
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+maxent"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
