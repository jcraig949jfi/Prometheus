import numpy as np, zlib, re, math
from typing import List, Dict

class ReasoningTool:
    """Renormalized Chaotic Reservoir with Cognitive Load Gating (RC-CLG) v2.
    1. Chaos Theory: Sparse recurrent reservoir at edge-of-chaos (spectral radius~1.05).
       Input tokens drive chaotic trajectories; similar semantics yield nearby states.
    2. Cognitive Load Theory: Germane-load gating filters noise — complex prompts that get
       trivial answers are penalised via intrinsic-load mismatch.
    3. Renormalization: Multi-scale coarse-graining at 3 pool sizes (2,4,8) detects
       scale-invariant patterns. Low cross-scale variance = structurally coherent."""

    def __init__(self):
        self.n_res = 32; rng = np.random.RandomState(42)
        W = rng.randn(self.n_res, self.n_res) * (rng.rand(self.n_res, self.n_res) < 0.15)
        eig = np.max(np.abs(np.linalg.eigvals(W)))
        self.W = W / eig * 1.05 if eig > 0 else W
        self.inp_w = rng.randn(self.n_res) * 0.3

    def _nums(self, t): return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", t)]
    def _words(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _ncd(self, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a+b).encode())); mx = max(ca, cb)
        return (cab - min(ca, cb)) / mx if mx else 0.0
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

    def _trajectory(self, text, steps=20):
        state = np.zeros(self.n_res)
        history = []
        for ch in text[:steps*2]:
            state = np.tanh(self.W @ state + self.inp_w*(ord(ch)/256.0))
            history.append(state.copy())
        return np.array(history) if history else np.zeros((1, self.n_res))
    def _renorm(self, traj):
        sums = []
        for pool in [2, 4, 8]:
            n = len(traj) - len(traj) % pool
            if n < pool: sums.append(np.mean(traj, axis=0)); continue
            sums.append(traj[:n].reshape(-1, pool, self.n_res).mean(axis=1).mean(axis=0))
        return np.stack(sums)
    def _chaos_score(self, prompt, cand):
        pt, ct = self._renorm(self._trajectory(prompt)), self._renorm(self._trajectory(cand))
        dists = [float(np.linalg.norm(pt[i]-ct[i])) for i in range(min(len(pt),len(ct)))]
        sim = 1.0/(1.0+np.mean(dists)); inv = 1.0/(1.0+np.var(dists)*10)
        return float(np.clip(0.6*sim + 0.4*inv, 0.0, 1.0))
    def _cog_load(self, prompt, cand):
        ps = len(self._neg_scope(prompt))+len(self._conditionals(prompt))+min(len(self._nums(prompt)),3)
        cs = len(self._neg_scope(cand))+len(self._conditionals(cand))+min(len(self._nums(cand)),3)
        return 0.6 if ps > 3 and cs == 0 else 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not prompt or not prompt.strip():
            return [{"candidate":c,"score":0.0,"reasoning":"structural: empty prompt"} for c in (candidates or [])]
        if not candidates: return []
        results = []
        for cand in candidates:
            if not cand or not cand.strip():
                results.append({"candidate":cand,"score":0.0,"reasoning":"structural: empty candidate"}); continue
            p = {}
            p['neg'] = self._neg_check(prompt, cand); p['num'] = self._numeric(prompt, cand)
            p['cmp'] = self._comparative(prompt, cand); p['mod'] = self._modus(prompt, cand)
            p['svo'] = self._subj_obj(prompt, cand); p['res'] = self._chaos_score(prompt, cand)
            cog = self._cog_load(prompt, cand)
            ncd = max(0.0, 1.0-self._ncd(prompt, cand))
            raw = (0.15*max(0,p['neg']) + 0.20*max(0,p['num']) + 0.10*p['cmp'] +
                   0.15*p['mod'] + 0.05*p['svo'] + 0.25*p['res'] + 0.10*ncd) * cog
            if p['neg'] < 0: raw = max(0.0, raw+p['neg'])
            bk = max(p, key=lambda k: p[k])
            if p[bk] < 0.05 and ncd > 0.3: tag = f"fallback:ncd ncd={ncd:.2f}"
            elif bk in ('num','mod','neg'): tag = f"execution:{bk}={p[bk]:.2f}"
            else: tag = f"structural:{bk}={p[bk]:.2f}"
            score = float(np.clip(raw, 0.0, 1.0))
            results.append({"candidate":cand,"score":score,
                "reasoning":f"{tag} | res={p['res']:.2f} cog={cog:.2f} ncd={ncd:.2f}"})
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
