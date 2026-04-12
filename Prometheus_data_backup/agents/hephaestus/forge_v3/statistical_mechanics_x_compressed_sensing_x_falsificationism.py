"""Statistical Mechanics Compressed Sensing Falsifier v3.
Statistical Mechanics x Compressed Sensing x Falsificationism.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """SMCSF v3: structural parsers + compressed-sensing secondary."""

    def __init__(self):
        self._level = 6

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _compressed_match(self, prompt: str, cand: str) -> float:
        """Sparse keyword matching weighted by information content."""
        pw = re.findall(r'\b\w+\b', prompt.lower())
        cw = set(re.findall(r'\b\w+\b', cand.lower()))
        if not pw:
            return 0.5
        # IDF-like weighting: rarer words in prompt are more informative
        freq = {}
        for w in pw:
            freq[w] = freq.get(w, 0) + 1
        total_w = 0.0
        match_w = 0.0
        for w, cnt in freq.items():
            weight = 1.0 / cnt  # inverse frequency
            total_w += weight
            if w in cw:
                match_w += weight
        return match_w / total_w if total_w > 0 else 0.5

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        cs = self._compressed_match(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * cs
        else:
            raw = 0.50 * ncd_sim + 0.50 * cs
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+cs"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
