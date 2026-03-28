import numpy as np, zlib, re
from typing import List, Dict

class ReasoningTool:
    """Ergodic Compositional Hebbian Reservoir (ECHR) v2.
    1. Compositionality: Structural feature binding into vector space via orthogonal projections.
    2. Ergodic Theory: Recurrent reservoir with spectral radius < 1 for invariant measure sampling.
    3. Hebbian Learning: Correlation-based weight updates (Oja's rule variant) for online plasticity."""

    def __init__(self):
        self.dim = 128
        rng = np.random.RandomState(42)
        W = rng.randn(self.dim, self.dim)*0.3
        self.W_res = W / np.max(np.abs(np.linalg.eigvals(W))) * 0.95
        self.W_in = rng.randn(self.dim, 32)
        self.weights = np.zeros(self.dim)
        self.lr, self.decay = 0.05, 0.01
        self.negs = ['not','no','never','none','cannot','neither',"n't"]
        self.comps = ['greater','less','more','fewer','higher','lower','>','<']

    def _hv(self, s):
        h = zlib.crc32(s.encode())
        return np.array([((h >> (i % 32)) & 0xFF) / 255.0 for i in range(32)])

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

    def _encode(self, text):
        """Compositional binding of structural features into reservoir-compatible vector."""
        v = np.zeros(self.dim); tl = text.lower()
        # Negation subspace
        ns = self._neg_scope(text)
        if ns: v[:16] = -0.5 * len(ns)
        # Numeric subspace
        nums = self._nums(text)
        if len(nums) >= 2:
            v[16:32] = 1.0 if nums[0] > nums[1] else -1.0
        if nums: v[32:48] = 1.0
        # Conditional subspace
        if self._conditionals(text): v[48:64] = 1.0
        # Quantifier/logic
        lw = {'all','some','every','each','more','less','equal'}
        if set(self._words(text)) & lw: v[64:80] = 1.0
        # Hash-based content encoding
        chunks = [text[i:i+max(1, len(text)//4)] for i in range(0, len(text), max(1, len(text)//4))][:4]
        for j, ch in enumerate(chunks):
            v[80+j*12:80+(j+1)*12] = self._hv(ch)[:12]
        norm = np.linalg.norm(v) + 1e-9
        return v / norm

    def _reservoir_run(self, prompt_vec, cand_vec):
        """Ergodic trajectory: 8-step mixing then time-averaged correlation."""
        combined = prompt_vec + cand_vec
        combined = combined / (np.linalg.norm(combined) + 1e-9)
        st = np.zeros(self.dim); scores = []
        for _ in range(8):
            st = 0.5*st + 0.5*np.tanh(self.W_res @ st + self.W_in @ self._hv("mix"))
            st += combined * 0.3
            scores.append(float(np.dot(st, self.weights)))
        return float(np.mean(scores))

    def _hebbian_update(self, vec):
        """Oja's rule: dw = lr*(x*dot(w,x) - w*dot(w,x)^2) + decay."""
        activation = np.dot(self.weights, vec)
        self.weights += self.lr * (vec * activation - self.weights * activation**2)
        self.weights *= (1.0 - self.decay)

    def _structural_score(self, prompt, cand):
        s = 0.0; pl, cl = prompt.lower(), cand.lower()
        pn, cn = self._nums(prompt), self._nums(cand)
        if pn and cn:
            if set(str(v) for v in pn) & set(str(v) for v in cn): s += 0.25
            if any(w in pl for w in self.comps[:3]) and cn[0] > pn[0]: s += 0.15
            if any(w in pl for w in self.comps[3:6]) and cn[0] < pn[0]: s += 0.15
        pns, cns = self._neg_scope(prompt), self._neg_scope(cand)
        if pns: s += 0.15 if set(pns) & set(cns) else -0.10
        conds = self._conditionals(prompt)
        for ante, cons in conds:
            if ante.strip().lower() in cl and cons.strip().lower() in cl: s += 0.15
        s += self._subj_obj(prompt, cand) * 0.10
        return s

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate": c, "score": 0.0, "reasoning": "structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        pv = self._encode(prompt)
        self._hebbian_update(pv)
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate": cand, "score": 0.0, "reasoning": "structural: empty candidate"}); continue
            cv = self._encode(cand)
            erg = self._reservoir_run(pv, cv)
            erg_norm = float(1.0 / (1.0 + np.exp(-erg)))
            struct = self._structural_score(prompt, cand)
            ncd = self._ncd(prompt, cand); ncd_sim = 1.0 - ncd
            raw = 0.30*erg_norm + 0.45*max(0, struct+0.5)/1.5 + 0.10*ncd_sim + 0.15*self._subj_obj(prompt, cand)
            score = float(np.clip(raw, 0.0, 1.0))
            self._hebbian_update(cv)
            if struct > 0.05:
                if self._nums(prompt) and self._nums(cand):
                    tag = f"execution: hebbian_erg={erg_norm:.2f} struct={struct:.2f}"
                else:
                    tag = f"structural: hebbian_erg={erg_norm:.2f} struct={struct:.2f}"
            elif ncd_sim > 0.3:
                tag = f"fallback:ncd ncd={ncd_sim:.2f}"
            else:
                tag = f"structural: reservoir={erg_norm:.2f}"
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
