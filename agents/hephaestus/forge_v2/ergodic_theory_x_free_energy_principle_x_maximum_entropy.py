import numpy as np, zlib, re, math
from typing import List, Dict

class ReasoningTool:
    """Ergodic Variational Free-Energy Inference Engine (EVFE) v2.
    1. Ergodic Theory: Metropolis-Hastings MCMC through candidate space. Time-averaged
       visit frequencies converge to posterior (ergodic theorem).
    2. Free Energy Principle: Energy = structural mismatch + bounded NCD. Boltzmann
       exp(-E) converts to probabilities; variational free energy minimised.
    3. Maximum Entropy: MaxEnt prior via exponential weighting of structural constraints.
       Least-biased distribution consistent with negation/numeric/conditional rules."""

    def __init__(self): self.rng = np.random.default_rng(seed=42)
    def _nums(self, t): return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", t)]
    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca, cb)
        return (cab - min(ca, cb)) / mx if mx else 0.0
    def _entropy(self, text):
        if not text: return 0.0
        freq = {}
        for c in text: freq[c] = freq.get(c, 0) + 1
        n = len(text); return -sum((v/n)*math.log2(v/n) for v in freq.values())
    def _neg_scope(self, text):
        toks = self._words(text); negs = {'not','no','never','none','cannot','neither'}
        return [toks[i+1] for i in range(len(toks)-1) if toks[i] in negs]
    def _neg_check(self, prompt, cand):
        ns = self._neg_scope(prompt)
        if not ns: return 0.0
        cl = cand.lower()
        bad = sum(1 for w in ns if w in cl and not any(n+' '+w in cl for n in ['not','no','never']))
        return -0.3*bad if bad else 0.2
    def _numeric(self, prompt, cand):
        pn, cn = self._nums(prompt), self._nums(cand)
        if not pn: return 0.0
        s, pl = 0.0, prompt.lower()
        if cn:
            if set(round(x,8) for x in pn) & set(round(x,8) for x in cn): s += 0.2
            if len(pn) >= 2 and cn:
                if re.search(r'(greater|more|larger)\b', pl) and cn[0] > min(pn): s += 0.15
                if re.search(r'(less|fewer|smaller)\b', pl) and cn[0] < max(pn): s += 0.15
        elif pn: s -= 0.1
        return float(np.clip(s, -0.5, 1.0))
    def _comparative(self, prompt, cand):
        m = re.search(r'(\w+)\s+(?:is|are|was)\s+(more|less|greater|smaller|taller|shorter|better|worse)\s+than\s+(\w+)', prompt, re.I)
        if not m: return 0.0
        subj, obj_ = m.group(1).lower(), m.group(3).lower(); cl = cand.lower()
        return 0.25 if (subj in cl and obj_ in cl) else (0.1 if subj in cl else 0.0)
    def _conditionals(self, t):
        return re.findall(r'if\s+(.+?)\s*,?\s*then\s+(.+?)(?:[.]|$)', t, re.I)
    def _modus(self, prompt, cand):
        conds = self._conditionals(prompt)
        if not conds: return 0.0
        cl, s = cand.lower(), 0.0
        for ant, con in conds:
            al, cr = ant.strip().lower(), con.strip().lower()
            if al in cl and cr in cl: s += 0.3
            if f"not {cr}" in cl and f"not {al}" in cl: s += 0.3
        return min(1.0, s)
    def _subj_obj(self, prompt, cand):
        m = re.search(r'(\b[A-Z][a-z]+)\s+\w+(?:ed|s)?\s+(?:the\s+|a\s+)?(\b[A-Z][a-z]+|\b\w+)', prompt)
        if not m: return 0.0
        s, o = m.group(1).lower(), m.group(2).lower(); cl = cand.lower()
        return 0.2 if (s in cl and o in cl) else (0.1 if s in cl or o in cl else 0.0)

    def _maxent_energy(self, prompt, cand):
        energy = 0.0
        neg = self._neg_check(prompt, cand)
        if neg < 0: energy += 2.0 * abs(neg)
        num = self._numeric(prompt, cand)
        if num < 0: energy += 1.5
        elif self._nums(prompt) and not self._nums(cand): energy += 1.0
        if self._conditionals(prompt) and self._modus(prompt, cand) == 0: energy += 0.5
        energy += min(self._ncd(prompt, cand) * 0.5, 0.75)  # NCD capped
        return energy
    def _ergodic_sample(self, prompt, candidates, steps=60):
        if len(candidates) <= 1: return [1.0]*len(candidates)
        energies = np.array([self._maxent_energy(prompt, c) for c in candidates])
        energies -= energies.min()
        visits = np.zeros(len(candidates)); cur = int(self.rng.integers(0, len(candidates)))
        for _ in range(steps):
            visits[cur] += 1
            prop = int(self.rng.integers(0, len(candidates)))
            if prop == cur: continue
            de = energies[prop] - energies[cur]
            if de < 0 or self.rng.random() < math.exp(-de): cur = prop
        t = visits.sum()
        return (visits/t).tolist() if t > 0 else [1.0/len(candidates)]*len(candidates)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        valid = [(i, c) for i, c in enumerate(candidates) if c and c.strip()]
        if not valid:
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty candidate"} for c in candidates]
        erg = self._ergodic_sample(prompt, [c for _, c in valid])
        results, vi = [], 0
        for i, cand in enumerate(candidates):
            if not cand or not cand.strip():
                results.append({"candidate":cand,"score":0.0,"reasoning":"structural: empty candidate"}); continue
            p = {}
            p['neg'] = self._neg_check(prompt, cand); p['num'] = self._numeric(prompt, cand)
            p['cmp'] = self._comparative(prompt, cand); p['mod'] = self._modus(prompt, cand)
            p['svo'] = self._subj_obj(prompt, cand)
            ncd = max(0.0, 1.0-self._ncd(prompt, cand)); p['ncd'] = ncd
            score = float(np.clip(erg[vi], 0.0, 1.0)); vi += 1
            bk = max((k for k in p if k != 'ncd'), key=lambda k: p[k])
            if p[bk] < 0.05 and ncd > 0.3: tag = f"fallback:ncd ncd={ncd:.2f}"
            elif bk in ('num','mod','neg'): tag = f"execution:{bk}={p[bk]:.2f}"
            else: tag = f"structural:{bk}={p[bk]:.2f}"
            e = self._maxent_energy(prompt, cand)
            results.append({"candidate":cand,"score":score,
                "reasoning":f"{tag} | energy={e:.2f} ergodic={score:.3f} ncd={ncd:.2f}"})
        results.sort(key=lambda x: x['score'], reverse=True)
        if len(results) >= 2:
            t, r = results[0]['score'], results[1]['score']
            if t > 0 and abs(t-r)/t < 0.05:
                for res in results[:2]: res['reasoning'] += " | metacog: LOW_CONFIDENCE top-2 within 5%"
        if results and results[0]['score'] < 0.15:
            results[0]['reasoning'] += " | metacog: unable to parse prompt structure"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        null_avg = float(np.mean([self.evaluate(prompt,[n])[0]['score'] for n in ["Yes","No","Unknown"]]))
        if score <= null_avg: return 0.0
        for nt in self._neg_scope(prompt):
            al = answer.lower()
            if nt in al and not any(n+' '+nt in al for n in ['not','no','never']):
                return max(0.0, score*0.1)
        return float(np.clip((score-null_avg)/(1.0-null_avg+1e-9), 0.0, 1.0))
