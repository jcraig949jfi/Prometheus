import re, zlib
import numpy as np
from typing import List, Dict

class ReasoningTool:
    """Chaos-Neuromodulated Cognitive Load Evaluator v2.
    1. Chaos Theory: Lyapunov stability via logistic-map perturbation of influence graph.
    2. Cognitive Load Theory: Intrinsic (nested clauses), extraneous (complexity w/o payoff),
       germane (useful features). Miller's k=7 chunking.
    3. Neuromodulation: Dopamine/serotonin gain vectors modulate influence matrix."""

    def __init__(self):
        self.k = 7; self.steps = 20; self.eps = 1e-3
        self.pos = {'correct','true','yes','good','valid','increase','gain','success','right'}
        self.neg = {'false','no','bad','invalid','decrease','loss','fail','error','wrong'}
        self.pats = {
            'neg':re.compile(r'\b(not|no|never|neither|nor|cannot)\b',re.I),
            'comp':re.compile(r'\b(more than|less than|greater|smaller|higher|lower)\b',re.I),
            'cond':re.compile(r'\b(if|then|unless|otherwise|provided)\b',re.I),
            'caus':re.compile(r'\b(because|leads to|results in|causes|due to)\b',re.I),
            'num':re.compile(r'[-+]?\d*\.?\d+')}
    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _props(self, t):
        ss = re.split(r'[.!?;]', t); return [s.strip() for s in ss if s.strip()] or [t]
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca,cb)
        return (cab-min(ca,cb))/mx if mx else 0.0
    def _neg_scope(self, text):
        toks = self._words(text); ns = {'not','no','never','none','cannot','neither'}
        return [toks[i+1] for i in range(len(toks)-1) if toks[i] in ns]
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
    def _numeric(self, prompt, cand):
        pn = [float(x) for x in self.pats['num'].findall(prompt)]
        cn = [float(x) for x in self.pats['num'].findall(cand)]
        if not pn or not cn: return 0.0
        if sorted(pn)==sorted(cn): return 0.4
        pl = prompt.lower()
        if any(w in pl for w in ['greater','more','larger']): return 0.3 if cn[0]>pn[0] else 0.05
        if any(w in pl for w in ['less','smaller','fewer']): return 0.3 if cn[0]<pn[0] else 0.05
        return 0.1
    def _entities(self, prompt, cand):
        pe = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        ce = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        return len(pe&ce)/len(pe) if pe else 0.0
    def _cog_load(self, text):
        nested = len(re.findall(r',|;|\bwhich\b|\bthat\b|\bwho\b', text))
        n_props = len(self._props(text)); wc = len(self._words(text))
        sf = sum(1 for p in self.pats.values() if p.search(text))
        intr = min(1.0, (n_props+nested)/(2*self.k))
        extr = min(1.0, max(0.0, (wc/self.k - sf)/10.0))
        germ = min(1.0, sf/5.0)
        return {'i':intr, 'e':extr, 'g':germ}
    def _influence(self, props):
        n = len(props)
        if n == 0: return np.zeros((0,0))
        W = np.zeros((n,n)); gd, gs = np.ones(n), np.ones(n)
        for i, p in enumerate(props):
            toks = set(self._words(p))
            gd[i] = 1+0.2*(1.0 if toks&self.pos else 0.0)
            gs[i] = 1-0.15*(1.0 if toks&self.neg else 0.0)
            for j in range(n):
                if i==j: W[i,j]=1.0; continue
                s = 0.0
                if self.pats['cond'].search(p) and j>i: s += 0.8
                if self.pats['comp'].search(p) and j>i: s += 0.5
                if self.pats['caus'].search(p) and j>i: s += 0.7
                W[i,j] = min(1.0, s)
        return np.diag(gd*gs)@W
    def _stability(self, text):
        props = self._props(text); W = self._influence(props); n = W.shape[0]
        if n == 0: return 0.0
        if n > self.k:
            top = np.argsort(np.sum(np.abs(W),axis=1))[-self.k:]; W = W[np.ix_(top,top)]; n = self.k
        rs = np.sum(np.abs(W),axis=1,keepdims=True); rs[rs==0]=1; Wn = W/rs
        x0 = np.ones(n)*0.5; b = np.ones(n)*0.1; xp = x0.copy()
        rng = np.random.RandomState(7); xp[rng.randint(n)] += self.eps
        lyap, cnt, xc, xpc = 0.0, 0, x0, xp
        sig = lambda z: 1.0/(1.0+np.exp(-np.clip(z,-500,500)))
        for _ in range(self.steps):
            xn, xpn = sig(Wn@xc+b), sig(Wn@xpc+b)
            dt, dn = np.linalg.norm(xc-xpc), np.linalg.norm(xn-xpn)
            if dt>1e-10: lyap += np.log((dn+1e-10)/(dt+1e-10)); cnt += 1
            xc, xpc = xn, xpn
        return float(np.clip(-lyap/cnt, 0, 1)) if cnt else 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate":cand,"score":0.0,"reasoning":"structural: empty candidate"}); continue
            stab = self._stability(cand); ld = self._cog_load(cand)
            num = self._numeric(prompt, cand); mod = self._modus(prompt, cand)
            ent = self._entities(prompt, cand); ncd = 1.0-self._ncd(prompt, cand)
            lf = max(0.5, 1.0 - ld['e']*0.3 + ld['g']*0.2)
            neg_pen = 1.0
            for nt in self._neg_scope(prompt):
                if nt in cand.lower() and not any(n in cand.lower() for n in ['not','no','never']): neg_pen = 0.7
            raw = (0.25*stab + 0.20*num + 0.15*mod + 0.10*ent + 0.15*ncd)*lf*neg_pen
            score = float(np.clip(raw, 0.0, 1.0))
            parts = {'stability':stab,'numeric':num,'modus':mod,'entity':ent}
            best = max(parts, key=lambda k: parts[k])
            if parts[best]<0.05 and ncd>0.3: tag = f"fallback:ncd ncd={ncd:.2f}"
            elif best in ('numeric','modus'): tag = f"execution:{best}={parts[best]:.2f}"
            else: tag = f"structural:{best}={parts[best]:.2f}"
            results.append({"candidate":cand,"score":score,
                "reasoning":f"{tag} | stab={stab:.2f} lf={lf:.2f} num={num:.2f} mod={mod:.2f} ncd={ncd:.2f}"})
        results.sort(key=lambda x: x['score'], reverse=True)
        if len(results)>=2:
            t, r = results[0]['score'], results[1]['score']
            if t>0 and abs(t-r)/t<0.05:
                for res in results[:2]: res['reasoning'] += " | metacog: LOW_CONFIDENCE top-2 within 5%"
        if results and results[0]['score']<0.12:
            results[0]['reasoning'] += " | metacog: unable to parse prompt structure"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        if score < 0.12: return 0.0
        for nt in self._neg_scope(prompt):
            if nt in answer.lower() and not any(n in answer.lower() for n in ['not','no','never']):
                return max(0.0, score*0.15)
        return float(np.clip((score-0.12)/0.88, 0.0, 1.0))
