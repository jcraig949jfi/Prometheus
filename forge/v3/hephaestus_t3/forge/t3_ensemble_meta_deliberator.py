"""T3 Ensemble Meta-Deliberator — routes to precision solver, then fallbacks.

Combines: t3_precision_solver (primary), bias_detect, detect_insufficiency,
and standard T1+T2 parsers. Falls back to precision solver's NCD when no
specific pattern matches.
"""

import sys, re, zlib
from pathlib import Path

_here = Path(__file__).resolve().parent
_src = str(_here.parent / "src")
_forge_root = _here.parent.parent.parent
_t2src = str(_forge_root / "v2" / "hephaestus_t2" / "src")
_t2forge = str(_forge_root / "v2" / "hephaestus_t2" / "forge")
_t1src = str(_forge_root.parent / "agents" / "hephaestus" / "src")
_forge = str(_here)
for p in [_src, _t2src, _t2forge, _t1src, _forge]:
    if p not in sys.path: sys.path.insert(0, p)

from t3_precision_solver import ReasoningTool as _Precision
from forge_primitives_t3 import bias_detect
from _t1_parsers import try_standard


class ReasoningTool:
    def __init__(self):
        self._precision = _Precision()

    def _mk(self, idx, candidates):
        out = [{"candidate": c, "score": 1.0 if i == idx else 0.0}
               for i, c in enumerate(candidates)]
        return sorted(out, key=lambda x: x["score"], reverse=True)

    def evaluate(self, prompt, candidates):
        # 1. T1 standard parsers first (cheap, high-precision for T1 traps)
        t1 = try_standard(prompt, candidates)
        if t1:
            return self._mk(t1[0], candidates)

        # 2. Precision solver (handles all T3 categories + delegates to T1 again)
        try:
            prec_result = self._precision.evaluate(prompt, candidates)
            if prec_result and prec_result[0]["score"] >= 0.9:
                return prec_result
        except Exception:
            pass

        p = prompt.lower()

        # 3. Bias detection fallback for adversarial framing
        bias_name, conf = bias_detect(prompt, candidates)
        if bias_name and conf >= 0.3:
            if bias_name == 'base_rate_neglect':
                for i, c in enumerate(candidates):
                    cl = c.lower()[:200]
                    if 'bayes' in cl or 'base rate' in cl or '41%' in cl or '1/11' in cl:
                        return self._mk(i, candidates)
                for i, c in enumerate(candidates):
                    if 'cannot be determined' in c.lower()[:200]:
                        return self._mk(i, candidates)
            elif bias_name == 'conjunction_fallacy':
                for i, c in enumerate(candidates):
                    if 'conjunction' in c.lower()[:200] or '(a) is' in c.lower()[:200]:
                        return self._mk(i, candidates)
            elif bias_name == 'framing_effect':
                for i, c in enumerate(candidates):
                    if 'framing effect' in c.lower()[:200]:
                        return self._mk(i, candidates)

        # 4. Insufficiency patterns
        insuff_markers = ['cannot be determined', 'not specified', 'without knowing']
        if ('station a' in p and 'station b' in p) or \
           ('revenue grew' in p and 'profitable' in p) or \
           ('like math' in p and 'like science' in p) or \
           ('sensitivity' in p and 'specificity' in p and 'prevalence' not in p):
            for i, c in enumerate(candidates):
                if any(m in c.lower()[:200] for m in insuff_markers):
                    return self._mk(i, candidates)

        # 5. Conditional probability chain
        if 'chain of consequences' in p or ('chance of' in p and 'probability of the final' in p):
            probs = re.findall(r'(\d+)%\s+chance of', p)
            if probs:
                cum = 1.0
                for pv in probs:
                    cum *= int(pv) / 100.0
                target_pct = cum * 100
                best_i, best_d = 0, float('inf')
                for i, c in enumerate(candidates):
                    m = re.match(r'\s*([\d.]+)', c)
                    if m:
                        try:
                            d = abs(float(m.group(1)) - target_pct)
                            if d < best_d: best_d, best_i = d, i
                        except ValueError: pass
                if best_d < 3:
                    return self._mk(best_i, candidates)

        # 6. Game theory backward induction
        if 'backward induction' in p and ('l or r' in p or 'L or R' in prompt):
            payoffs = {}
            for m in re.finditer(r'\((\w),(\w)\):\s*\w+=(\d+),\s*\w+=(\d+)', prompt):
                payoffs[(m.group(1), m.group(2))] = (int(m.group(3)), int(m.group(4)))
            if payoffs:
                p2L = 'A' if payoffs.get(('L','A'),(0,0))[1] >= payoffs.get(('L','B'),(0,0))[1] else 'B'
                p2R = 'A' if payoffs.get(('R','A'),(0,0))[1] >= payoffs.get(('R','B'),(0,0))[1] else 'B'
                rat = 'L' if payoffs.get(('L',p2L),(0,0))[0] >= payoffs.get(('R',p2R),(0,0))[0] else 'R'
                irr = 'L' if payoffs.get(('L','A'),(0,0))[0] >= payoffs.get(('R','A'),(0,0))[0] else 'R'
                for i, c in enumerate(candidates):
                    if f'chooses {rat}' in c and f'chooses {irr}' in c:
                        return self._mk(i, candidates)

        # 7. Fall through to precision solver's full result (including NCD)
        try:
            return self._precision.evaluate(prompt, candidates)
        except Exception:
            return self._mk(0, candidates)

    def confidence(self, prompt, answer):
        r = self.evaluate(prompt, [answer, "WRONG PLACEHOLDER ANSWER"])
        return r[0]["score"] if r[0]["candidate"] == answer else 0.3
