"""Execution Evaluator v3 -- grounds reasoning in computed behavior.
Proof Theory x Constraint Satisfaction x Normalized Compression Distance.
Category-driven structural parsers (>=70%), NCD tiebreaker (<=15%).
"""
import re, zlib, math
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _caitl_parsers import run_all_parsers, _nums

class ReasoningTool:
    """ExecEval v3: structural parsers primary + arithmetic execution secondary."""

    def __init__(self):
        self._level = 6

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    def _try_arithmetic(self, prompt: str, cand: str) -> float:
        """Try to compute simple arithmetic from prompt and validate candidate."""
        pl = prompt.lower()
        # Simple expression: "What is A + B?" or "A * B = ?"
        m = re.search(r"what\s+is\s+([\d.]+)\s*([+\-*/])\s*([\d.]+)", pl)
        if m:
            a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
            ops = {'+': a+b, '-': a-b, '*': a*b, '/': a/b if b != 0 else float('inf')}
            correct = ops.get(op)
            if correct is not None:
                cn = _nums(cand)
                if cn and abs(cn[0] - correct) < 0.01:
                    return 1.0
                if cn:
                    return -1.0
        return 0.0  # no arithmetic detected

    def _score(self, prompt: str, cand: str) -> tuple:
        struct_score, tags = run_all_parsers(prompt, cand)
        ncd_sim = 1.0 - self._ncd(prompt, cand)
        arith = self._try_arithmetic(prompt, cand)

        if tags:
            # If arithmetic also fires, blend
            if arith != 0.0:
                raw = 0.55 * ((struct_score + 1.0) / 2.0) + 0.30 * ((arith + 1.0) / 2.0) + 0.15 * ncd_sim
            else:
                raw = 0.70 * ((struct_score + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * 0.5
        else:
            if arith != 0.0:
                raw = 0.70 * ((arith + 1.0) / 2.0) + 0.15 * ncd_sim + 0.15 * 0.5
            else:
                raw = 0.85 * ncd_sim + 0.15 * 0.5
        return max(0.0, min(1.0, raw)), tags + ([f"arith={arith:+.1f}"] if arith != 0 else [])

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        results = []
        for cand in candidates:
            s, tags = self._score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(s),
                "reasoning": "; ".join(tags) if tags else "fallback:ncd"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        s, tags = self._score(prompt, answer)
        if any("arith=+1" in t for t in tags):
            return 0.95
        if any("arith=-1" in t for t in tags):
            return 0.05
        return float(np.clip(s, 0.05 if tags else 0.2, 0.95 if tags else 0.7))
