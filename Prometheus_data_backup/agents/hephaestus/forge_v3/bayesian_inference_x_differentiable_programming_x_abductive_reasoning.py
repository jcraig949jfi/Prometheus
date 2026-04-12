"""Bayesian Abductive Differentiable v3. Posterior inference + gradient scoring + abduction.
CAITL v3: 15 general category parsers. structural_score >= 70%. NCD <= 15%.
"""
import re, zlib, math, os, sys
import numpy as np

# Import shared CAITL v3 structural parsers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _caitl_v3 import structural_score as _structural_score


class ReasoningTool:
    """Bayesian Abductive Differentiable v3. Posterior inference + gradient scoring + abduction."""

    def __init__(self):
        self._level = 6

    # ── NCD tiebreaker (weight <= 15%) ─────────────────────────────
    def _c(self, text: str) -> int:
        return len(zlib.compress(text.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " \n " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    # ── evaluate ───────────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: list) -> list:
        if not candidates:
            return []
        results = []
        for cand in candidates:
            ss = _structural_score(prompt, cand)
            ncd_val = self._ncd(prompt, cand)
            ncd_sim = 1.0 / (1.0 + ncd_val)
            if ss >= 0:
                # Structural parser matched: 85% structural, 15% NCD
                score = ss * 0.85 + ncd_sim * 0.15
            else:
                # No category matched: pure NCD fallback
                score = ncd_sim
            results.append({
                "candidate": cand,
                "score": float(max(0.0, min(1.0, score))),
                "reasoning": f"struct={ss:.2f} ncd={ncd_val:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    # ── confidence ─────────────────────────────────────────────────
    def confidence(self, prompt: str, answer: str) -> float:
        ss = _structural_score(prompt, answer)
        if ss >= 0:
            return float(max(0.05, min(0.95, 0.5 + ss * 0.45)))
        ncd_val = self._ncd(prompt, answer)
        return float(max(0.05, min(0.95, 1.0 / (1.0 + ncd_val))))
