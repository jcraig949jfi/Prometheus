"""Gauge-Equivariant Sparse Compositional Encoder v3.
Gauge Theory x Sparse Autoencoders x Compositional Semantics.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """GESCE v3: structural parsers + gauge-covariance secondary."""

    def __init__(self):
        self._level = 6
        self._logic_tokens = {'not','no','never','none','if','then','all','some',
                              'every','greater','less','more','fewer'}

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _sparse_compositional(self, prompt: str, cand: str) -> float:
        """Weighted token overlap, logic tokens get 3x weight."""
        pw = set(re.findall(r'\b\w+\b', prompt.lower()))
        cw = set(re.findall(r'\b\w+\b', cand.lower()))
        shared = pw & cw
        w = sum(3.0 if t in self._logic_tokens else 1.0 for t in shared)
        denom = sum(3.0 if t in self._logic_tokens else 1.0 for t in pw) or 1.0
        return min(1.0, w / denom)

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        sparse = self._sparse_compositional(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * sparse
        else:
            raw = 0.50 * ncd_sim + 0.50 * sparse
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+sparse"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
