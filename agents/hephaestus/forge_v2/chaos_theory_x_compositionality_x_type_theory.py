import re, zlib
from typing import List, Dict

class ReasoningTool:
    """Chaotic Compositional Type-Driven Reasoning Tool v2.
    1. Chaos Theory: Logistic-map perturbation breaks ties between structurally
       similar but logically distinct candidates (Lyapunov divergence).
    2. Compositionality: Score is composed from independent sub-scores (type-match,
       numeric, modus, entity, NCD) each computed and weighted separately.
    3. Type Theory: Prompt and candidate get a type signature of logical features.
       Well-typed candidates satisfy the prompt's structural demands."""

    def __init__(self):
        self.r = 3.9; self.chaos_steps = 100

    def _logistic(self, x): return self.r*x*(1.0-x)
    def _chaos(self, seed, idx):
        x = (abs(hash(seed)+idx)%10000)/10000.0+0.001; x = min(x, 0.999)
        for _ in range(self.chaos_steps): x = self._logistic(x)
        return (x-0.5)*0.06
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca, cb)
        return (cab-min(ca,cb))/mx if mx else 0.0
    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _type_sig(self, text):
        tl = text.lower()
        return {'neg':bool(re.search(r'\b(no|not|never|none|cannot|impossible)\b',tl)),
                'comp':bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b',tl)),
                'cond':bool(re.search(r'\b(if|then|unless|provided|when)\b',tl)),
                'num':bool(re.search(r'\d+',text)), 'wc':len(text.split())}
    def _type_match(self, ps, cs):
        s = 0.0
        if ps['neg']: s += 0.25 if cs['neg'] else -0.1
        if ps['cond']: s += 0.2 if cs['cond'] else 0.0
        if ps['num']: s += 0.2 if cs['num'] else -0.05
        if ps['comp']: s += 0.15 if cs['comp'] else 0.0
        return s
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
    def _numeric(self, prompt, cand):
        pn = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', prompt)]
        cn = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', cand)]
        if not pn or not cn: return 0.0
        if sorted(pn)==sorted(cn): return 0.4
        pl = prompt.lower()
        if any(w in pl for w in ['greater','more','larger']): return 0.3 if cn[0]>pn[0] else 0.05
        if any(w in pl for w in ['less','smaller','fewer']): return 0.3 if cn[0]<pn[0] else 0.05
        if len(set(cn)-set(pn))>2: return 0.05
        return 0.15
    def _entities(self, prompt, cand):
        pe = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        ce = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        return len(pe&ce)/len(pe) if pe else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        ps = self._type_sig(prompt); results = []
        for i, cand in enumerate(candidates):
            if not cand or not cand.strip():
                results.append({"candidate":cand,"score":0.0,"reasoning":"structural: empty candidate"}); continue
            cs = self._type_sig(cand)
            tm = self._type_match(ps, cs); num = self._numeric(prompt, cand)
            mod = self._modus(prompt, cand); ent = self._entities(prompt, cand)
            ncd = 1.0-self._ncd(prompt, cand)
            chaos = self._chaos(prompt+str(i), i)
            if tm > 0.3: chaos *= 0.2
            neg_pen = 1.0; cl = cand.lower()
            for nt in self._neg_scope(prompt):
                if nt in cl and not any(n in cl for n in ['not','no','never','none']): neg_pen = 0.7
            raw = (0.25*max(0.0,tm) + 0.20*num + 0.15*mod + 0.10*ent + 0.15*ncd + chaos)*neg_pen + 0.15
            score = max(0.0, min(1.0, raw))
            parts = {'type_match':tm,'numeric':num,'modus':mod,'entity':ent}
            best = max(parts, key=lambda k: parts[k])
            if parts[best]<0.05 and ncd>0.3: tag = f"fallback:ncd ncd={ncd:.2f}"
            elif best in ('numeric','modus'): tag = f"execution:{best}={parts[best]:.2f}"
            else: tag = f"structural:{best}={parts[best]:.2f}"
            results.append({"candidate":cand,"score":score,
                "reasoning":f"{tag} | type={tm:.2f} num={num:.2f} mod={mod:.2f} ent={ent:.2f} chaos={chaos:.4f}"})
        results.sort(key=lambda x: x['score'], reverse=True)
        if len(results)>=2:
            t, r = results[0]['score'], results[1]['score']
            if t>0 and abs(t-r)/t<0.05:
                for res in results[:2]: res['reasoning'] += " | metacog: LOW_CONFIDENCE top-2 within 5%"
        if results and results[0]['score']<0.18:
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
            if nt in al and not any(n in al for n in ['not','no','never']): return max(0.0, score*0.15)
        return max(0.0, min(1.0, (score-0.15)/0.85))
