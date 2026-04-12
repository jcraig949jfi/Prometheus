"""Morphogenetic Predictive Falsification Engine v3.
Morphogenesis x Predictive Coding x Falsificationism.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """MPF v3: structural parsers + morphogenetic-error secondary."""

    def __init__(self):
        self._level = 6

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _morpho_error(self, prompt: str, cand: str) -> float:
        """Prediction error from token-IoU; growth/decay dynamics."""
        pw = set(prompt.lower().split())
        cw = set(cand.lower().split())
        union = pw | cw
        iou = len(pw & cw) / max(len(union), 1)
        error = 1.0 - iou
        # Reaction-diffusion: low error -> growth, high -> decay
        activation = 0.5
        for _ in range(5):
            if error > 0.5:
                activation *= math.exp(-2.0 * error * 0.2)
            else:
                activation += (1.0 - error) * (1.0 - activation) * 0.2
            activation = max(0.0, min(1.0, activation))
        return activation

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        morph = self._morpho_error(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * morph
        else:
            raw = 0.50 * ncd_sim + 0.50 * morph
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+morph"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
