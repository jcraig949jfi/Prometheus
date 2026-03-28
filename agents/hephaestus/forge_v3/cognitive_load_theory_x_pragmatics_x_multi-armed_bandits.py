"""Pragmatic Cognitive-Load-Aware Bandit v3.
Cognitive Load Theory x Pragmatics x Multi-Armed Bandits.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

_STOP = {'the','a','an','and','or','but','in','on','at','to','for','of','with',
         'is','are','was','were','be','been','that','this','it','as'}

class ReasoningTool:
    """PC-MAB v3: structural parsers + pragmatic-load secondary."""

    def __init__(self):
        self._level = 6

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _pragmatic_load(self, prompt: str, cand: str) -> float:
        """Gricean relevance: content-word overlap minus extraneous penalty."""
        pw = set(re.findall(r'\b\w+\b', prompt.lower())) - _STOP
        cw = set(re.findall(r'\b\w+\b', cand.lower())) - _STOP
        if not pw:
            return 0.5
        rel = len(pw & cw) / len(pw)
        extra = min(0.3, len(cw - pw) * 0.03)
        return max(0.0, min(1.0, rel - extra))

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        prag = self._pragmatic_load(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * prag
        else:
            raw = 0.50 * ncd_sim + 0.50 * prag
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+prag"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
