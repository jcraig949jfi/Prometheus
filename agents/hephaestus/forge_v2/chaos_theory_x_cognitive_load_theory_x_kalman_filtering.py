import math, zlib, re
from typing import List, Dict, Any

class ReasoningTool:
    """Chaotic-Kalman Cognitive Load (CKCL) Estimator v2.
    1. Chaos Theory: Logistic map (r=3.9) generates process noise for hypothesis
       exploration/exploitation balance.
    2. Cognitive Load Theory: Intrinsic load (nested clauses, propositions),
       extraneous load (chaos entropy). Miller's threshold triggers chunking.
    3. Kalman Filtering: Full predict-update cycle per candidate. Process noise Q
       from chaos; measurement z from structural + entity scores."""

    def __init__(self):
        self.r = 3.9; self.x0 = 0.5; self.load_thr = 4.0

    def _logistic(self, x): return self.r*x*(1.0-x)
    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca,cb)
        return (cab-min(ca,cb))/mx if mx else 0.0
    def _nums(self, t):
        out = []
        for m in re.findall(r'[-+]?\d*\.?\d+', t):
            try: out.append(float(m))
            except ValueError: pass
        return out
    def _feats(self, text):
        ws = text.lower().split()
        return {'neg':sum(1 for w in ws if w in {'not','no','never','none','neither','cannot'}),
                'comp':sum(1 for w in ws if w in {'more','less','greater','smaller','higher','lower'}),
                'cond':sum(1 for w in ws if w in {'if','unless','provided','when'}),
                'numbers':self._nums(text), 'wc':len(ws)}
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
    def _entities(self, prompt, cand):
        pe = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        ce = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        return len(pe&ce)/len(pe) if pe else 0.0
    def _cog_load(self, text):
        nested = len(re.findall(r',|;|\bwhich\b|\bthat\b|\bwho\b', text))
        props = len(re.split(r'[.!?;]', text)); wc = len(self._words(text))
        return (props+nested)/self.load_thr + max(0.0, wc/20.0-1.0)
    def _kalman(self, pm, pv, z, q, rm=0.1):
        pv2 = pv+q; kg = pv2/(pv2+rm)
        return pm+kg*(z-pm), (1-kg)*pv2, kg
    def _numeric_eval(self, pf, cf, prompt):
        pn, cn = pf['numbers'], cf['numbers']
        if not pn or not cn: return 0.0
        if sorted(pn)==sorted(cn): return 0.5
        pl = prompt.lower()
        if len(pn)==1 and len(cn)==1:
            if any(w in pl for w in ['greater','more','larger']): return 0.4 if cn[0]>pn[0] else 0.05
            if any(w in pl for w in ['less','smaller','fewer']): return 0.4 if cn[0]<pn[0] else 0.05
        return 0.15

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        pf = self._feats(prompt)
        chaos = []; x = self.x0
        for _ in range(len(candidates)): x = self._logistic(x); chaos.append(x)
        p_load = self._cog_load(prompt)
        total_load = p_load + (sum(chaos)/len(chaos))*2.0
        exceeded = total_load > self.load_thr
        results = []
        for i, cand in enumerate(candidates):
            if not cand or not cand.strip():
                results.append({"candidate":cand,"score":0.0,"reasoning":"structural: empty candidate"}); continue
            cf = self._feats(cand)
            num = self._numeric_eval(pf, cf, prompt); mod = self._modus(prompt, cand)
            base = 0.5 + num*0.4 + mod*0.3
            neg_pen = 1.0
            for nt in self._neg_scope(prompt):
                if nt in cand.lower() and not any(n in cand.lower() for n in ['not','no','never']): neg_pen = 0.7
            base *= neg_pen
            q = chaos[i]*(1.0 if not exceeded else 0.1)
            ent = self._entities(prompt, cand)
            ncd = 1.0-self._ncd(prompt.lower(), cand.lower())
            z1 = 0.5*ent + 0.35*min(1.0, num+mod) + 0.15*ncd
            mean, var, kg1 = self._kalman(base, 0.25, z1, q)
            c_load = self._cog_load(cand)
            z2 = max(0.0, 1.0-c_load/(2*self.load_thr))
            mean, var, kg2 = self._kalman(mean, var, z2, q*0.5)
            if not exceeded and mean>0.6: mean += 0.03
            score = max(0.0, min(1.0, mean))
            parts = {'numeric':num,'modus':mod,'entity':ent}
            best = max(parts, key=lambda k: parts[k])
            if parts[best]<0.05 and ncd>0.3: tag = f"fallback:ncd ncd={ncd:.2f}"
            elif best in ('numeric','modus'): tag = f"execution:{best}={parts[best]:.2f}"
            else: tag = f"structural:{best}={parts[best]:.2f}"
            results.append({"candidate":cand,"score":score,
                "reasoning":f"{tag} | kalman={mean:.3f} load={total_load:.2f} chaos={chaos[i]:.3f} kg=[{kg1:.2f},{kg2:.2f}]"})
        results.sort(key=lambda x: x['score'], reverse=True)
        if len(results)>=2:
            t, r = results[0]['score'], results[1]['score']
            if t>0 and abs(t-r)/t<0.05:
                for res in results[:2]: res['reasoning'] += " | metacog: LOW_CONFIDENCE top-2 within 5%"
        if results:
            top = results[0]
            if top['score']>0.7 and 'fallback:ncd' in top['reasoning']:
                top['reasoning'] += " | metacog: high score but NCD-primary, suspect"
            if top['score']<0.15: top['reasoning'] += " | metacog: unable to parse prompt structure"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        if score < 0.15: return 0.0
        for nt in self._neg_scope(prompt):
            if nt in answer.lower() and not any(n in answer.lower() for n in ['not','no','never']):
                return max(0.0, score*0.15)
        return max(0.0, min(1.0, (score-0.15)/0.85))
