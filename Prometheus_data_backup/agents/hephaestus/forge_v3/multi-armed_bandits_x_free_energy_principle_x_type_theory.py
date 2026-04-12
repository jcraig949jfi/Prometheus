"""Variational Bandit Type-Checker v3.
Multi-Armed Bandits x Free Energy Principle x Type Theory.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """VBTC v3: structural parsers + free-energy secondary."""

    def __init__(self):
        self._level = 6

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _free_energy(self, prompt: str, cand: str) -> float:
        """Inverse free energy: lower surprise = higher score."""
        surprise = self._ncd(prompt, cand)
        pw = set(re.findall(r'\b\w+\b', prompt.lower()))
        cw = set(re.findall(r'\b\w+\b', cand.lower()))
        type_pen = 0.0
        negs_p = pw & {'not','no','never','none','cannot'}
        if negs_p and not (cw & {'not','no','never','none','cannot','false'}):
            if cw & {'yes','true','correct'}:
                type_pen = 0.3
        return max(0.0, 1.0 - surprise - type_pen)

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        fe = self._free_energy(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * fe
        else:
            raw = 0.50 * ncd_sim + 0.50 * fe
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+fe"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
