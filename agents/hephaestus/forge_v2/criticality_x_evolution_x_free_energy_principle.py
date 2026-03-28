import numpy as np, zlib, re
from typing import List, Dict

class ReasoningTool:
    """Critical Evolutionary Free-Energy Reasoner (CEFER) v2.
    1. Criticality: Susceptibility via perturbation variance near phase transition.
    2. Evolution: NEAT-like parsimony pressure penalizes over-complexity (Occam's razor).
    3. Free Energy Principle: VFE = prediction_error + complexity_cost, minimized."""

    def __init__(self):
        self.negs = ['not','no','never','none','cannot','neither',"n't"]
        self.comps = ['greater','less','more','fewer','higher','lower','>','<']

    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _nums(self, t): return [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', t)]
    def _neg_scope(self, text):
        toks = self._words(text); ns = set(self.negs)
        return [toks[i+1] for i in range(len(toks)-1) if toks[i] in ns]
    def _conditionals(self, t):
        return re.findall(r'if\s+(.+?)\s*,?\s*then\s+(.+?)(?:[.]|$)', t, re.I)
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca, cb)
        return (cab - min(ca, cb)) / mx if mx else 0.0
    def _subj_obj(self, prompt, cand):
        pe = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        ce = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        return len(pe & ce) / max(len(pe), 1) if pe else 0.0

    def _susceptibility(self, prompt, cand):
        """Criticality: variance of NCD under micro-perturbations."""
        base = self._ncd(prompt, cand)
        diffs = []
        for i in range(4):
            if len(cand) > 1:
                p = cand[:-(i+1)] + chr(ord('a') + i)
            else:
                p = cand + chr(ord('a') + i)
            diffs.append(abs(self._ncd(prompt, p) - base))
        return float(np.mean(diffs)) + 1e-6

    def _free_energy(self, prompt, cand):
        """VFE = prediction_error (NCD) + complexity_cost (length penalty)."""
        pred_err = self._ncd(prompt, cand)
        comp_cost = abs(len(cand) - len(prompt)) / (len(prompt) + 1)
        return pred_err + 0.5 * comp_cost

    def _evolution_fitness(self, prompt, cand):
        """Parsimony-weighted structural fitness."""
        s = 0.0; pl, cl = prompt.lower(), cand.lower()
        pn, cn = self._nums(prompt), self._nums(cand)
        if pn and cn:
            if set(str(v) for v in pn) & set(str(v) for v in cn): s += 0.30
            if any(w in pl for w in ['greater','more','larger']) and cn[0] > pn[0]: s += 0.20
            if any(w in pl for w in ['less','smaller','fewer']) and cn[0] < pn[0]: s += 0.20
        elif pn and not cn:
            if any(w in pl for w in self.comps): s -= 0.20
        pns, cns = self._neg_scope(prompt), self._neg_scope(cand)
        if pns:
            s += 0.15 if set(pns) & set(cns) else -0.15
        conds = self._conditionals(prompt)
        for ante, cons in conds:
            al, cr = ante.strip().lower(), cons.strip().lower()
            if al in cl and cr in cl: s += 0.15
            if f"not {cr}" in cl and f"not {al}" in cl: s += 0.15
        # Question-answer alignment
        if '?' in prompt and '?' not in cand and len(cand.strip()) > 0: s += 0.05
        if '?' in prompt and '?' in cand: s -= 0.10
        s += self._subj_obj(prompt, cand) * 0.10
        # Parsimony: slight penalty for excessive length
        if len(cand) > len(prompt) * 3: s -= 0.10
        return s

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural: empty candidate"}); continue
            fe = self._free_energy(prompt, cand)
            susc = self._susceptibility(prompt, cand)
            evo = self._evolution_fitness(prompt, cand)
            ncd = self._ncd(prompt, cand); ncd_sim = 1.0 - ncd
            # Score: (susceptibility * fitness) / free_energy, mapped via sigmoid
            fe_inv = 1.0 / (fe + 0.1)
            raw_signal = susc * max(0, evo + 0.5) * fe_inv
            sig_score = float(1.0 / (1.0 + np.exp(-raw_signal + 1.5)))
            # Blend with NCD (capped at 15%)
            raw = 0.85 * sig_score + 0.15 * ncd_sim
            score = float(np.clip(raw, 0.0, 1.0))
            if evo > 0.05:
                if self._nums(prompt) and self._nums(cand):
                    tag = f"execution: FE={fe:.2f} crit={susc:.3f} evo={evo:.2f}"
                else:
                    tag = f"structural: FE={fe:.2f} crit={susc:.3f} evo={evo:.2f}"
            elif ncd_sim > 0.3:
                tag = f"fallback:ncd ncd={ncd_sim:.2f}"
            else:
                tag = f"structural: FE={fe:.2f} crit={susc:.3f}"
            results.append({"candidate": cand, "score": score, "reasoning": tag})
        results.sort(key=lambda x: x['score'], reverse=True)
        # Metacognitive reflection
        if len(results) >= 2:
            t, r = results[0]['score'], results[1]['score']
            if t > 0 and abs(t-r)/t < 0.05:
                for res in results[:2]: res['reasoning'] += " | metacog: LOW_CONFIDENCE top-2 within 5%"
        if results:
            top = results[0]
            pns = self._neg_scope(prompt)
            if pns and not self._neg_scope(top['candidate']) and top['score'] > 0.3:
                top['reasoning'] += " | metacog: prompt negation not reflected"
            if top['score'] < 0.10:
                top['reasoning'] += " | metacog: unable to parse prompt structure"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        null = self.evaluate(prompt, [""])
        baseline = null[0]['score'] if null else 0.0
        adj = max(0.0, score - baseline)
        return float(np.clip(adj / max(1.0 - baseline, 0.01), 0.0, 1.0))
