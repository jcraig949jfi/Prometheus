"""Gene Regulatory Mechanism Checker v3.
Gene Regulatory Networks x Mechanism Design x Model Checking.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """GRMC v3: structural parsers + regulatory-network secondary."""

    def __init__(self):
        self._level = 6

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _regulatory_check(self, prompt: str, cand: str) -> float:
        """Activation/inhibition network: logic-keyword consistency."""
        pw = set(re.findall(r'\b\w+\b', prompt.lower()))
        cw = set(re.findall(r'\b\w+\b', cand.lower()))
        # Activators: affirmative logic keywords
        act = {'yes','true','correct','is','are','all','every'}
        # Inhibitors: negative logic keywords
        inh = {'not','no','never','none','cannot','false'}
        p_act = bool(pw & act)
        p_inh = bool(pw & inh)
        c_act = bool(cw & act)
        c_inh = bool(cw & inh)
        score = len(pw & cw) / max(len(pw), 1)
        # Mismatch penalty
        if p_inh and c_act and not c_inh:
            score *= 0.6
        if p_act and not p_inh and c_inh:
            score *= 0.8
        return min(1.0, score)

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        reg = self._regulatory_check(prompt, cand)

        if tags:
            raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * reg
        else:
            raw = 0.50 * ncd_sim + 0.50 * reg
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
                "reasoning": "; ".join(tags) if tags else "fallback:ncd+reg"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
