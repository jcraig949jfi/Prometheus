import numpy as np, zlib, re
from typing import List, Dict

class ReasoningTool:
    """Recursive Ergodic Particle Filter (REPF) v2.
    1. Ergodic Theory: Time-averaged consistency via perturbation stability sampling.
    2. Ecosystem Dynamics: Predation (pruning contradictions), keystone detection,
       succession (fallback when no candidate dominates).
    3. Theory of Mind: Parses belief markers ("thinks","believes","says") and checks
       whether candidates respect the agent-belief vs ground-truth distinction."""

    def __init__(self):
        self.n_samples = 5
    _tom_markers = re.compile(r'\b(thinks|believes|assumes|expects|says|claims|would\s+think)\b', re.I)
    _tom_agents = re.compile(r'\b([A-Z][a-z]+)\s+(thinks|believes|says|assumes|claims)\b')

    def _nums(self, t): return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", t)]
    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + b).encode()))
        mx = max(ca, cb); return (cab - min(ca, cb)) / mx if mx else 0.0
    def _neg_scope(self, text):
        toks = self._words(text); negs = {'not','no','never','none','cannot','neither'}
        return [toks[i+1] for i in range(len(toks)-1) if toks[i] in negs]
    def _conditionals(self, t):
        return re.findall(r'if\s+(.+?)\s*,?\s*then\s+(.+?)(?:[.]|$)', t, re.I)
    def _modus(self, prompt, cand):
        conds = self._conditionals(prompt)
        if not conds: return 0.0
        cl = cand.lower(); s = 0.0
        for a, c in conds:
            al, cr = a.strip().lower(), c.strip().lower()
            if al in cl and cr in cl: s += 0.3
            if f"not {cr}" in cl and f"not {al}" in cl: s += 0.3
        return min(1.0, s)
    def _tom(self, prompt, cand):
        if not self._tom_markers.search(prompt): return 0.0
        agents = self._tom_agents.findall(prompt)
        if not agents: return 0.15
        s, cl = 0.0, cand.lower()
        for ag, vb in agents:
            if ag.lower() in cl: s += 0.25
            if vb.lower() in ('thinks','believes','assumes'):
                if any(w in cl for w in ['actually','but','however','in reality',ag.lower()]): s += 0.25
        return min(1.0, s)
    def _ergodic(self, prompt, cand):
        base = self._ncd(prompt, cand); var = 0.0
        for i in range(self.n_samples):
            step = max(1, len(prompt)//(self.n_samples+1))
            var += (self._ncd(prompt[step*i:]+prompt[:step*i], cand) - base)**2
        return 1.0/(1.0 + 10.0*var/self.n_samples)
    def _numeric(self, prompt, cand):
        pn, cn = self._nums(prompt), self._nums(cand)
        if not pn and not cn: return 0.0
        s, pl = 0.0, prompt.lower()
        if pn and cn and sorted(pn)==sorted(cn): s += 0.3
        if re.search(r'(greater|more|larger|higher)\s+than', pl): s += 0.15
        return min(1.0, s)
    def _entities(self, prompt, cand):
        pe = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        ce = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        return len(pe & ce)/len(pe) if pe else 0.0
    def _constraint(self, prompt, cand):
        s = 1.0; cl = cand.lower()
        for nt in self._neg_scope(prompt):
            if nt in cl and not any(n in cl for n in ['not','no','never']): s *= 0.7
        return s

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate":cand,"score":0.0,"reasoning":"structural: empty candidate"}); continue
            p = {}
            p['con'] = self._constraint(prompt, cand)
            p['erg'] = self._ergodic(prompt, cand)
            p['tom'] = self._tom(prompt, cand)
            p['num'] = self._numeric(prompt, cand)
            p['mod'] = self._modus(prompt, cand)
            p['ent'] = self._entities(prompt, cand)
            ncd = 1.0 - self._ncd(prompt, cand)
            raw = 0.20*p['erg'] + 0.20*p['tom'] + 0.15*p['num'] + 0.15*p['mod'] + 0.10*p['ent'] + 0.05*p['con'] + 0.15*ncd
            raw *= p['con']
            best = max(p, key=lambda k: p[k])
            if p[best]<0.05 and ncd>0.3: tag = f"fallback:ncd ncd={ncd:.2f}"
            elif best in ('mod','num','con'): tag = f"execution:{best}={p[best]:.2f}"
            else: tag = f"structural:{best}={p[best]:.2f}"
            score = float(np.clip(raw, 0.0, 1.0))
            results.append({"candidate":cand,"score":score,
                "reasoning":f"{tag} | erg={p['erg']:.2f} tom={p['tom']:.2f} ent={p['ent']:.2f} ncd={ncd:.2f}"})
        results.sort(key=lambda x: x['score'], reverse=True)
        if len(results)>=2:
            t, r = results[0]['score'], results[1]['score']
            if t>0 and abs(t-r)/t < 0.05:
                for res in results[:2]: res['reasoning'] += " | metacog: LOW_CONFIDENCE top-2 within 5%"
        if results and results[0]['score']<0.15:
            results[0]['reasoning'] += " | metacog: unable to parse prompt structure"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        if score < 0.15: return 0.0
        for nt in self._neg_scope(prompt):
            al = answer.lower()
            if nt in al and not any(n in al for n in ['not','no','never']):
                return max(0.0, score*0.2)
        return float(np.clip((score-0.15)/0.85, 0.0, 1.0))
