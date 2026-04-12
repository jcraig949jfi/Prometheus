"""Neural Plasticity Compositional Free-Energy v3.
Neural Plasticity x Compositionality x Free Energy Principle.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """NPCFE v3: structural parsers + hebbian-compositional secondary."""

    def __init__(self):
        self._level = 6

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _hebbian_comp(self, prompt: str, cand: str) -> float:
        """Hebbian co-activation: bigram overlap as compositional synapse."""
        def _bi(s):
            w = s.lower().split()
            return set(zip(w, w[1:])) if len(w) > 1 else set()
        pw = set(re.findall(r'\b\w+\b', prompt.lower()))
        cw = set(re.findall(r'\b\w+\b', cand.lower()))
        w_ov = len(pw & cw) / max(len(pw), 1)
        pb, cb = _bi(prompt), _bi(cand)
        b_ov = len(pb & cb) / max(len(pb), 1) if pb else 0.0
        return 0.5 * w_ov + 0.5 * b_ov

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        hebb = self._hebbian_comp(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * hebb
        else:
            raw = 0.50 * ncd_sim + 0.50 * hebb
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+hebb"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
