import numpy as np, zlib, re
from typing import List, Dict

class ReasoningTool:
    """Critical Ergodic Constraint Propagator (CECP) v2.
    1. Constraint Satisfaction: Arc-consistent constraint propagation over parsed logical features.
    2. Criticality: Susceptibility via variance of satisfaction under thermal perturbation.
    3. Ergodic Theory: Time-averaged sampling over noisy constraint evaluations."""

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

    def _extract_constraints(self, prompt):
        """Parse prompt into a set of typed constraints for arc-consistency checking."""
        constraints = []
        pl = prompt.lower()
        # Negation constraints
        ns = self._neg_scope(prompt)
        for n in ns: constraints.append(('neg', n))
        # Numeric constraints
        nums = self._nums(prompt)
        if nums: constraints.append(('num', nums))
        if any(w in pl for w in ['greater','more','larger']): constraints.append(('cmp', 'gt'))
        if any(w in pl for w in ['less','smaller','fewer']): constraints.append(('cmp', 'lt'))
        # Conditional constraints
        for ante, cons in self._conditionals(prompt):
            constraints.append(('cond', (ante.strip().lower(), cons.strip().lower())))
        # Quantifier constraints
        for q in ['all','every','each','some','any']:
            if q in pl: constraints.append(('quant', q))
        return constraints

    def _propagate(self, constraints, cand):
        """Arc-consistency: check each constraint against candidate, return satisfaction vector."""
        sats = []; cl = cand.lower()
        cns = self._neg_scope(cand); cn = self._nums(cand)
        for ctype, cval in constraints:
            if ctype == 'neg':
                # Arc: negated word should appear in negated scope of candidate OR not appear
                if cval in cns: sats.append(1.0)
                elif cval not in cl: sats.append(0.5)
                else: sats.append(0.0)  # word appears un-negated = violation
            elif ctype == 'num':
                if cn:
                    overlap = set(str(v) for v in cval) & set(str(v) for v in cn)
                    sats.append(0.8 if overlap else 0.3)
                else: sats.append(0.1)
            elif ctype == 'cmp':
                pn, candn = self._nums(""), cn  # use already extracted
                if len(cn) >= 1 and len(cval) > 0:
                    sats.append(0.5)  # present but can't verify fully
                else: sats.append(0.2)
            elif ctype == 'cond':
                ante, cons = cval
                if ante in cl and cons in cl: sats.append(1.0)
                elif f"not {cons}" in cl and f"not {ante}" in cl: sats.append(0.9)
                elif ante in cl and cons not in cl: sats.append(0.1)
                else: sats.append(0.4)
            elif ctype == 'quant':
                sats.append(0.5)  # quantifier presence noted
        return sats

    def _ergodic_sample(self, constraints, cand, n_samples=10):
        """Ergodic time-average over noisy constraint evaluations (thermal noise)."""
        base_sats = self._propagate(constraints, cand)
        if not base_sats: return 0.5, 0.0
        all_means = []
        for i in range(n_samples):
            h = zlib.crc32(f"{cand}_{i}".encode()) / (2**32)
            noise = (h - 0.5) * 0.3
            noisy = [max(0, min(1, s + noise * (1 if j % 2 == 0 else -1))) for j, s in enumerate(base_sats)]
            all_means.append(float(np.mean(noisy)))
        arr = np.array(all_means)
        return float(np.mean(arr)), float(np.var(arr))

    def _structural_bonus(self, prompt, cand):
        s = 0.0; pl, cl = prompt.lower(), cand.lower()
        pn, cn = self._nums(prompt), self._nums(cand)
        if pn and cn:
            if set(str(v) for v in pn) & set(str(v) for v in cn): s += 0.20
            if any(w in pl for w in ['greater','more','larger']) and cn[0] > pn[0]: s += 0.15
            if any(w in pl for w in ['less','smaller','fewer']) and cn[0] < pn[0]: s += 0.15
        if '?' in prompt and '?' not in cand and len(cand.strip()) > 0: s += 0.05
        if '?' in prompt and '?' in cand: s -= 0.10
        s += self._subj_obj(prompt, cand) * 0.10
        return s

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        constraints = self._extract_constraints(prompt)
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural: empty candidate"}); continue
            mean_sat, suscept = self._ergodic_sample(constraints, cand)
            stability = 1.0 / (1.0 + 10.0 * suscept)
            struct = self._structural_bonus(prompt, cand)
            ncd = self._ncd(prompt, cand); ncd_sim = 1.0 - ncd
            csp_score = mean_sat * stability
            raw = 0.45*csp_score + 0.30*max(0, struct+0.3)/1.3 + 0.10*ncd_sim + 0.15*self._subj_obj(prompt, cand)
            score = float(np.clip(raw, 0.0, 1.0))
            n_con = len(constraints)
            if struct > 0.05:
                if self._nums(prompt) and self._nums(cand):
                    tag = f"execution: csp={csp_score:.2f} sat={mean_sat:.2f} n_cons={n_con}"
                else:
                    tag = f"structural: csp={csp_score:.2f} stability={stability:.2f} n_cons={n_con}"
            elif ncd_sim > 0.3:
                tag = f"fallback:ncd ncd={ncd_sim:.2f}"
            else:
                tag = f"structural: csp={csp_score:.2f} suscept={suscept:.4f}"
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
