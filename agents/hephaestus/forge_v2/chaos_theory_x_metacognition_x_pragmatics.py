import numpy as np, zlib, re
from typing import List, Dict

class ReasoningTool:
    """Pragmatic Chaotic Meta-Reservoir (PCMR) v2.
    1. Chaos Theory: Deterministic ESN reservoir; state divergence detects mismatch.
    2. Metacognition: Prediction-error monitoring + reflection pass on top candidate.
    3. Pragmatics (Gricean): Quantity, Relation, Manner, Quality maxims scored."""

    def __init__(self):
        rng = np.random.RandomState(42)
        self.rs, self.ins, self.leak = 64, 32, 0.5
        self.W_in = rng.randn(self.rs, self.ins)
        W = rng.randn(self.rs, self.rs)*0.3
        self.W_res = W/np.max(np.abs(np.linalg.eigvals(W)))*1.1
        self.connectors = ['therefore','thus','hence','because','if','then','so','but','however']
        self.negs = ['not','no','never','none','cannot','neither']

    def _hv(self, s):
        h = zlib.crc32(s.encode())
        return np.array([((h>>(i%32))&0xFF)/255.0 for i in range(self.ins)])
    def _reservoir(self, text):
        st = np.zeros(self.rs); cs = max(1, len(text)//10)
        for ch in [text[i:i+cs] for i in range(0,len(text),cs)][:10]:
            st = (1-self.leak)*st + self.leak*np.tanh(self.W_in@self._hv(ch) + self.W_res@st)
        return st
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca,cb)
        return (cab-min(ca,cb))/mx if mx else 0.0
    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _neg_scope(self, text):
        toks = self._words(text); ns = set(self.negs)
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
        pn = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', prompt)]
        cn = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', cand)]
        if not pn or not cn: return 0.0
        if sorted(pn)==sorted(cn): return 0.4
        pl = prompt.lower()
        if any(w in pl for w in ['greater','more','larger']) and cn[0]>pn[0]: return 0.3
        if any(w in pl for w in ['less','smaller','fewer']) and cn[0]<pn[0]: return 0.3
        return 0.1
    def _pragmatic(self, prompt, cand):
        pw, cw = self._words(prompt), self._words(cand)
        pn, cn = self._neg_scope(prompt), self._neg_scope(cand); s = 0.0
        pe = set(re.findall(r'\b[A-Z][a-z]{2,}\b', prompt))
        ce = set(re.findall(r'\b[A-Z][a-z]{2,}\b', cand))
        if pe: s += 0.15*len(pe&ce)/len(pe)
        if set(pn)==set(cn): s += 0.1
        if any(c in cand.lower() for c in self.connectors): s += 0.1
        if len(cw)<3 and len(pw)>5: s -= 0.15
        if re.search(r'\d', prompt) and re.search(r'\d', cand): s += 0.1
        return s
    def _meta(self, prompt, cand):
        err = np.linalg.norm(self._reservoir(prompt)-self._reservoir(cand))
        return (1.0-min(1.0, err/15.0))*0.3

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate":cand,"score":0.0,"reasoning":"structural: empty candidate"}); continue
            ncd = 1.0-self._ncd(prompt, cand)
            prag = self._pragmatic(prompt, cand)
            meta = self._meta(prompt, cand)
            num = self._numeric(prompt, cand)
            mod = self._modus(prompt, cand)
            raw = 0.15*ncd + 0.25*prag + 0.20*meta + 0.20*num + 0.20*mod
            parts = {'pragmatics':prag,'metacog':meta,'numeric':num,'modus':mod}
            best = max(parts, key=lambda k: parts[k])
            if parts[best]<0.05 and ncd>0.3: tag = f"fallback:ncd ncd={ncd:.2f}"
            elif best in ('numeric','modus'): tag = f"execution:{best}={parts[best]:.2f}"
            else: tag = f"structural:{best}={parts[best]:.2f}"
            score = float(np.clip(raw, 0.0, 1.0))
            results.append({"candidate":cand,"score":score,
                "reasoning":f"{tag} | prag={prag:.2f} meta={meta:.2f} num={num:.2f} ncd={ncd:.2f}"})
        results.sort(key=lambda x: x['score'], reverse=True)
        if len(results)>=2:
            t, r = results[0]['score'], results[1]['score']
            if t>0 and abs(t-r)/t<0.05:
                for res in results[:2]: res['reasoning'] += " | metacog: LOW_CONFIDENCE top-2 within 5%"
        if results:
            top = results[0]
            neg_p, neg_c = self._neg_scope(prompt), self._neg_scope(top['candidate'])
            if neg_p and not neg_c and top['score']>0.4:
                top['reasoning'] += " | metacog: prompt has negation, candidate does not"
            if top['score']<0.12: top['reasoning'] += " | metacog: unable to parse prompt structure"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not prompt or not answer: return 0.0
        res = self.evaluate(prompt, [answer])
        if not res: return 0.0
        score = res[0]['score']
        if score < 0.12: return 0.0
        for nt in self._neg_scope(prompt):
            al = answer.lower()
            if nt in al and not any(n in al for n in self.negs): return max(0.0, score*0.15)
        return float(np.clip((score-0.12)/0.88, 0.0, 1.0))
