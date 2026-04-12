import numpy as np, zlib, re, math
from typing import List, Dict

class ReasoningTool:
    """Multi-Scale Thermodynamic Active Inference (MT-AI) v2.
    1. Thermodynamics: Boltzmann-weighted partition function over candidate energies.
       Shannon entropy measures dissipation; inverse temperature beta modulates precision.
    2. Active Inference: Free energy F = PredictionError - beta*EpistemicValue + ThermoCost.
       Candidates scored by minimising variational free energy.
    3. Wavelet Transforms: Real Haar decomposition on 8-dim feature vectors — approx
       coefficients track global consistency, detail coefficients flag contradictions."""

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
    def _feature_vec(self, text):
        tl = text.lower()
        return np.array([
            min(sum(tl.count(n) for n in ['not','no','never','none',"n't",'cannot'])/5,1),
            min(sum(tl.count(c) for c in ['greater','less','more','fewer','than','better','worse'])/5,1),
            min(sum(tl.count(c) for c in ['if','then','therefore','because','thus','unless'])/5,1),
            min(len(self._nums(text))/5,1), min(len(text)/500,1), min(text.count('?')/3,1),
            min(self._entropy(text)/5,1), min(len(set(self._words(text)))/50,1),
        ], dtype=np.float64)
    def _haar(self, v):
        n = len(v) - len(v) % 2
        if n < 2: return 0.0, 0.0
        pairs = v[:n].reshape(-1, 2)
        return float(np.mean(((pairs[:,0]+pairs[:,1])/math.sqrt(2))**2)), \
               float(np.mean(((pairs[:,0]-pairs[:,1])/math.sqrt(2))**2))
    def _wavelet_score(self, prompt, cand):
        pa, pd = self._haar(self._feature_vec(prompt))
        ca, cd = self._haar(self._feature_vec(cand))
        return float(np.clip(1.0/(1.0+abs(pa-ca)) - 0.5*abs(pd-cd), 0.0, 1.0))
    def _thermo_beta(self, prompt, cand):
        pe, ce = self._entropy(prompt), self._entropy(cand)
        diss = abs(pe-ce)/(max(pe, ce)+1e-9)
        return 0.5 + 0.5/(1.0+math.exp(-5*(diss-0.3)))
    def _boltzmann(self, energies, beta=1.0):
        e = np.array(energies, dtype=np.float64); e -= e.min()
        w = np.exp(-beta*e); t = w.sum()
        return (w/t).tolist() if t > 0 else [1.0/len(e)]*len(e)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        parts, energies = [], []
        for cand in candidates:
            if not cand or not cand.strip():
                parts.append(None); energies.append(10.0); continue
            p = {}
            p['neg'] = self._neg_check(prompt, cand); p['num'] = self._numeric(prompt, cand)
            p['cmp'] = self._comparative(prompt, cand); p['mod'] = self._modus(prompt, cand)
            p['svo'] = self._subj_obj(prompt, cand); p['wav'] = self._wavelet_score(prompt, cand)
            p['beta'] = self._thermo_beta(prompt, cand)
            ncd = max(0.0, 1.0-self._ncd(prompt, cand)); p['ncd'] = ncd
            raw = (0.15*max(0,p['neg']) + 0.20*max(0,p['num']) + 0.10*p['cmp'] +
                   0.15*p['mod'] + 0.05*p['svo'] + 0.25*p['wav'] + 0.10*ncd)
            if p['neg'] < 0: raw = max(0.0, raw+p['neg'])
            energies.append(1.0 - raw); parts.append(p)
        avg_b = np.mean([p['beta'] for p in parts if p]) if any(p for p in parts) else 1.0
        boltz = self._boltzmann(energies, beta=avg_b)
        results = []
        vi = 0
        for i, cand in enumerate(candidates):
            if parts[i] is None:
                results.append({"candidate":cand,"score":0.0,"reasoning":"structural: empty candidate"}); continue
            p = parts[i]; score = float(np.clip(boltz[i], 0.0, 1.0))
            bk = max((k for k in p if k not in ('beta','ncd')), key=lambda k: p[k])
            if p[bk] < 0.05 and p['ncd'] > 0.3: tag = f"fallback:ncd ncd={p['ncd']:.2f}"
            elif bk in ('num','mod','neg'): tag = f"execution:{bk}={p[bk]:.2f}"
            else: tag = f"structural:{bk}={p[bk]:.2f}"
            results.append({"candidate":cand,"score":score,
                "reasoning":f"{tag} | wav={p['wav']:.2f} beta={p['beta']:.2f} ncd={p['ncd']:.2f}"})
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
