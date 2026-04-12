import numpy as np, zlib, re
from typing import List, Dict

class ReasoningTool:
    """Chaotic Dialectical Adaptive Controller (CDAC) v2.
    1. Chaos Theory: Discrete Lorenz map generates perturbation signal for robustness.
    2. Dialectics: Thesis/antithesis/synthesis scoring with explicit triad weights.
    3. Feedback Control: PID controller with Lyapunov-inspired gain scheduling."""

    def __init__(self):
        self.x, self.y, self.z = 0.1, 0.1, 0.1
        self.dt, self.rho, self.sigma, self.beta = 0.01, 28.0, 10.0, 8.0/3.0
        self.integral, self.prev_err = 0.0, 0.0
        self.negs = ['not','no','never','none','cannot','neither',"n't"]
        self.comps = ['greater','less','more','fewer','higher','lower','>','<']

    def _lorenz(self):
        dx = self.sigma*(self.y-self.x)*self.dt
        dy = (self.x*(self.rho-self.z)-self.y)*self.dt
        dz = (self.x*self.y-self.beta*self.z)*self.dt
        self.x += dx; self.y += dy; self.z += dz
        return float(np.tanh(self.z/10.0))

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
        return (cab-min(ca, cb))/mx if mx else 0.0
    def _subj_obj(self, prompt, cand):
        pe = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        ce = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        return len(pe & ce)/max(len(pe), 1) if pe else 0.0

    def _thesis(self, prompt, cand):
        s = 0.0; pl, cl = prompt.lower(), cand.lower()
        pn, cn = self._nums(prompt), self._nums(cand)
        if pn and cn:
            if set(str(v) for v in pn) & set(str(v) for v in cn): s += 0.25
            if any(w in pl for w in ['greater','more','larger']) and cn and pn and cn[0]>pn[0]: s += 0.15
            if any(w in pl for w in ['less','smaller','fewer']) and cn and pn and cn[0]<pn[0]: s += 0.15
        pns, cns = self._neg_scope(prompt), self._neg_scope(cand)
        if pns:
            s += 0.15 if set(pns) & set(cns) else -0.10
        conds = self._conditionals(prompt)
        for ante, cons in conds:
            al, cr = ante.strip().lower(), cons.strip().lower()
            if al in cl and cr in cl: s += 0.15
            if f"not {cr}" in cl and f"not {al}" in cl: s += 0.15
        s += self._subj_obj(prompt, cand) * 0.10
        return s

    def _antithesis(self, thesis_score, prompt, cand):
        chaos = self._lorenz()
        return thesis_score + chaos * 0.3 * (1.0 - abs(thesis_score))

    def _synthesis(self, thesis, antithesis):
        """PID controller merging thesis and antithesis; returns (score, instability)."""
        err = thesis - antithesis
        self.integral += err * self.dt
        deriv = err - self.prev_err
        if abs(err) > abs(self.prev_err)*1.1:
            kp, ki, kd = 0.5, 0.1, 0.8
        else:
            kp, ki, kd = 0.6, 0.2, 0.1
        correction = kp*err + ki*self.integral + kd*deriv
        self.prev_err = err
        return float(np.clip(thesis + correction, 0.0, 1.0)), abs(err)

    def _dialectic_score(self, thesis, antithesis, synthesis):
        """Explicit triad: thesis contribution, antithetical tension, synthesis resolution."""
        return 0.4*thesis + 0.2*max(0, 1.0-abs(thesis-antithesis)) + 0.4*synthesis

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        self.x, self.y, self.z = 0.1, 0.1, 0.1
        self.integral, self.prev_err = 0.0, 0.0
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural: empty candidate"}); continue
            th = self._thesis(prompt, cand)
            an = self._antithesis(th, prompt, cand)
            sy, instab = self._synthesis(th, an)
            dial = self._dialectic_score(max(0, th), an, sy)
            ncd = self._ncd(prompt, cand)
            ncd_contrib = (1.0-ncd)*0.15
            raw = dial*0.85 + ncd_contrib
            score = float(np.clip(raw, 0.0, 1.0))
            if dial < 0.05 and ncd_contrib > 0.05:
                tag = f"fallback:ncd ncd={1-ncd:.2f}"
            elif self._nums(prompt) and self._nums(cand):
                tag = f"execution: numeric thesis={th:.2f} synth={sy:.2f}"
            else:
                tag = f"structural: dialectic thesis={th:.2f} antith_delta={instab:.2f} synth={sy:.2f}"
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
        return float(np.clip(adj / max(1.0-baseline, 0.01), 0.0, 1.0))
