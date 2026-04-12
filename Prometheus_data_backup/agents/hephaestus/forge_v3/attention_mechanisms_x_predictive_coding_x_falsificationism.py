"""Structural Falsification Engine v3.
Attention Mechanisms x Predictive Coding x Falsificationism.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """SF-APM v3: structural category parsers + predictive-coding secondary."""

    def __init__(self):
        self._level = 6

    # -- NCD fallback (<=15% weight) ----------------------------------------
    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    # -- Predictive coding secondary (<=15% weight) -------------------------
    def _prediction_error(self, prompt: str, cand: str) -> float:
        """Token-overlap prediction error as secondary signal."""
        pw = set(prompt.lower().split())
        cw = set(cand.lower().split())
        if not pw:
            return 0.5
        return 1.0 - len(pw & cw) / max(len(pw), 1)

    # -- Scoring -----------------------------------------------------------
    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_val = self._ncd(prompt, cand)
        ncd_sim = 1.0 - ncd_val
        pred_err = self._prediction_error(prompt, cand)
        pred_sig = 1.0 - pred_err

        if tags:
            # Structural >= 70%, NCD <= 15%, secondary <= 15%
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * pred_sig
        else:
            raw = 0.50 * ncd_sim + 0.50 * pred_sig
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+pred"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        if tags:
            return float(np.clip(s, 0.05, 0.95))
        return float(np.clip(s, 0.2, 0.7))
