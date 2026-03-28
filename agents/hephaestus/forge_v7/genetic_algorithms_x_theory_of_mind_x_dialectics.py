"""GA x Theory of Mind x Dialectics. Frame D — Judgment Calibrator.
GA-based feature evolution (mutate weights, select fittest), ToM agent modeling
(false belief, knowledge attribution, perspective), dialectical scoring.
Score: Structural (60%) + Computation (25%) + NCD (15%)."""
import re, math, zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """GA-ToM-Dialectic: evolve weights, model agents, synthesize."""
    def __init__(self):
        self._pats = {'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|units)?', re.I),
                      'belief': re.compile(r'\b(thinks?|believes?|expects?|assumes?|knows?)\b', re.I)}
        self._presup = [re.compile(r'\b(stopped|quit|ceased|failed)\b.*\b(have you|did you)\b', re.I),
                        re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
                        re.compile(r'\b(?:either)\b.*\b(?:or)\b', re.I)]
        self._fallacy = {
            'presup': re.compile(r'(?:stopped|quit|when did you stop)\b', re.I),
            'scope': re.compile(r'\b(?:every|all|each)\b.*\b(?:some|a|one)\b.*\b(?:not|doesn\'t)\b', re.I),
            'dichot': re.compile(r'\b(?:either|only two|must be one)\b.*\bor\b', re.I),
            'surv': re.compile(r'\b(?:successful|survivors?|winners?)\b.*\b(?:all|every|always)\b', re.I),
            'sunk': re.compile(r'\b(?:already invested|already spent|too far|come this far)\b', re.I)}
        self._stops = {'the','is','a','an','and','or','but','in','on','at','to','for','of','it'}
        self.rng = np.random.RandomState(42)

    def _n(self, t): return [float(m) for m in re.findall(r'-?\d+\.?\d*', t)]
    def _w(self, t): return re.findall(r'\b[a-z]+(?:\'[a-z]+)?\b', t.lower())
    def _ncd(self, a, b):
        try:
            ba, bb = a.encode(), b.encode()
            ca, cb, cab = len(zlib.compress(ba)), len(zlib.compress(bb)), len(zlib.compress(ba+bb))
            return (cab - min(ca, cb)) / max(ca, cb, 1)
        except Exception: return 1.0

    def _evolve(self, feat, n_gen=8, pop=16):
        nf = feat.shape[1] if feat.ndim > 1 else 1
        if nf == 0: return np.ones(1)
        P = self.rng.rand(pop, nf)
        for _ in range(n_gen):
            sc = feat @ P.T; fit = np.var(sc, axis=0) + 1e-9
            idx = np.argsort(fit)[::-1]; surv = P[idx[:pop//2]]
            kids = []
            for j in range(0, len(surv)-1, 2):
                cx = self.rng.randint(1, nf) if nf > 1 else 1
                kids.append(np.concatenate([surv[j,:cx], surv[j+1,cx:]]))
                kids.append(np.concatenate([surv[j+1,:cx], surv[j,cx:]]))
            for c in kids:
                if self.rng.rand() < 0.3: c[self.rng.randint(nf)] = max(0, c[self.rng.randint(nf)] + self.rng.randn()*0.2)
            P = np.vstack([surv, np.array(kids[:pop-len(surv)])]) if kids else surv
        sc = feat @ P.T; return P[np.argmax(np.var(sc, axis=0))]

    def _tom_solve(self, prompt, candidates):
        pl = prompt.lower()
        # false belief
        put = re.search(r'(\w+)\s+(?:puts?|places?|leaves?)\s+(?:the\s+)?(\w+)\s+(?:in|on|under|behind)\s+(?:the\s+)?(\w+)', pl)
        mv = re.search(r'(?:moves?|transfers?|takes?)\s+(?:the\s+)?(\w+)\s+(?:to|into|in|under|behind)\s+(?:the\s+)?(\w+)', pl)
        lv = re.search(r'(\w+)\s+(?:leaves?|goes?\s+(?:out|away)|exits?|walks?\s+away)', pl)
        lk = re.search(r'where\s+(?:will|does|would)\s+(\w+)\s+(?:look|search|expect|think)', pl)
        if put and mv and lv and lk:
            for c in candidates:
                if put.group(3) in c.lower(): return c, 0.88
        # knowledge attribution
        if re.search(r"(?:doesn't|does not|don't|do not)\s+know", pl) and re.search(r'what\s+(?:does|would|will)\s+\w+\s+(?:think|believe|expect|guess|predict)', pl):
            if re.search(r'(?:rigged|loaded|biased|unfair|weighted|trick)', pl):
                for c in candidates:
                    if any(w in c.lower() for w in ('fair','equal','50','even','normal','unbiased')): return c, 0.85
        # perspective
        see = re.search(r'(\w+)\s+(?:sees?|witnesses?|observes?)\s+(.*?)(?:\.|,)', pl)
        ns = re.search(r'(\w+)\s+(?:does not|doesn\'t)\s+(?:see|witness|observe|know)', pl)
        if see and ns:
            ask = re.search(r'what\s+(?:does|would|will)\s+(\w+)\s+(?:think|believe|expect)', pl)
            if ask and ask.group(1).lower() == ns.group(1).lower():
                for c in candidates:
                    if any(w in c.lower() for w in ('original','initial','default','still','same')): return c, 0.82
        return None, 0

    def _dialectic(self, prompt, candidates):
        pl = prompt.lower(); pw = set(self._w(pl)) - self._stops
        has_contra = any(w in pl for w in ('but','however','although'))
        scores = np.zeros(len(candidates))
        for i, c in enumerate(candidates):
            sc = set(self._w(c)) - self._stops
            thesis = len(pw & sc) / max(len(pw), 1)
            anti = 0.3 if has_contra and any(w in c.lower() for w in ('both','however','but','yet')) else 0.0
            synth = 0.3 if any(w in c.lower() for w in ('therefore','thus','hence','because','since')) else 0.0
            scores[i] = thesis*0.5 + anti*0.2 + synth*0.3
        return scores

    def _ss(self, prompt, cand):
        pl, cl = prompt.lower(), cand.lower().strip()
        ws = re.findall(r"[a-z'\-]+", cl); cl0 = ws[0] if ws else cl
        pn, cn = self._n(prompt), self._n(cand)
        m = re.search(r'is\s+([\.\d]+)\s+(?:larger|greater|bigger|more|less|smaller)\s+than\s+([\.\d]+)', pl)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            big = any(w in m.group(0) for w in ('larger','greater','bigger','more'))
            ans = 'yes' if ((a>b) if big else (a<b)) else 'no'
            if cl0 == ans: return 1.0
            if cl0 in ('yes','no') and cl0 != ans: return 0.0
        m2 = re.search(r'which\b.*?\b(larger|greater|bigger|smaller|less)', pl)
        if m2 and len(pn)>=2 and cn:
            wb = m2.group(1) in ('larger','greater','bigger'); tgt = max(pn) if wb else min(pn)
            if abs(cn[0]-tgt)<1e-9: return 1.0
        mt = re.search(r'(?:cost|costs?)\s+\$?([\d.]+)\s+(?:total|together|in total|combined)', pl)
        md = re.search(r'costs?\s+\$?([\d.]+)\s+more\s+than', pl)
        if mt and md:
            total, diff = float(mt.group(1)), float(md.group(1)); cheap = (total-diff)/2.0
            if cn and abs(cn[0]-cheap)<0.01: return 1.0
            if cn and abs(cn[0]-diff)<0.01: return 0.0
        mu = re.search(r'(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|gallon|cup)\s+of\s+\w+.*(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|gallon|cup)\s+of\s+\w+', pl)
        if mu and mu.group(1)==mu.group(2) and any(w in pl for w in ('heav','weigh','lighter','which')):
            if any(w in cl for w in ('same','equal','neither','both')): return 1.0
            if len(cl)<30: return 0.0
        m6 = re.search(r'all\s+(\w+)\s+are\s+(\w+)', pl); m7 = re.search(r'are\s+all\s+(\w+)\s+(\w+)', pl)
        if m6 and m7 and m6.group(1)!=m7.group(1):
            if cl0=='no' or 'not necessarily' in cl: return 1.0
            if cl0=='yes': return 0.0
        if re.search(r'0\.9{3,}', pl) and any(w in pl for w in ('equal','= 1','equals','same')):
            if cl0=='yes' or 'equal' in cl: return 1.0
            if cl0=='no': return 0.0
        if any(w in pl for w in ('coin','die','dice','roulette','flip','roll')):
            if any(w in pl for w in ('in a row','previous','last','after','next','still','now')):
                if 'higher' in cl or 'lower' in cl or 'increase' in cl: return 0.0
                if '50' in cl or '1/2' in cl or '0.5' in cl or 'same' in cl: return 1.0
        m9 = re.search(r'all\s+but\s+(\d+)\s+(?:\w+\s+){0,3}(die|died|leave|left|lost|broke|ran|flew|escaped|gone|disappear)', pl)
        if m9:
            if cl.strip()==m9.group(1): return 1.0
            if cl.strip().isdigit() and cl.strip()!=m9.group(1): return 0.0
        cgt = re.findall(r'(\w+)\s+(?:is\s+)?(?:greater|larger|more|bigger|taller|heavier|higher|faster|older)\s+than\s+(\w+)', pl, re.I)
        if cgt:
            ent = {}
            for a, b in cgt: ent[a.lower()] = ent.get(a.lower(),0)+1; ent.setdefault(b.lower(),0)
            top = max(ent, key=ent.get) if ent else ''
            if top and top in cl: return 1.0
            return 0.3
        ifm = re.search(r'if\s+(.+?)[,.](.+?)\.', pl)
        if ifm and re.search(r'\bnot\b|\bdoes\s+not\b|\bisn.t\b|\bdon.t\b', pl[ifm.end():]):
            if cl0=='no' or 'therefore not' in cl or 'did not' in cl: return 1.0
            if cl0=='yes': return 0.0
        if re.search(r'not\s+(all|every)\s+\w+', pl) and '?' in pl:
            if 'cannot' in cl or 'not enough' in cl or 'cannot be determined' in cl: return 1.0
        return -1.0

    def _meta_confidence(self, prompt, answer=''):
        pl = prompt.lower()
        for p in self._fallacy.values():
            if p.search(pl): return 0.25
        for p in self._presup:
            if p.search(pl): return 0.25
        if re.search(r'\b(best|worst|favorite|opinion|beautiful|ugly)\b', pl):
            if not re.search(r'\bbest\s+(?:explain|describe|account|represent|fit)', pl): return 0.28
        if len(pl.split())<6 and not self._pats['numeric'].search(pl): return 0.20
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates: return []
        best, ts = self._tom_solve(prompt, candidates)
        if best and ts > 0.5:
            r = [{"candidate": c, "score": float(ts) if c==best else float(max(0.05,1.0-ts)),
                  "reasoning": "tom_solver"} for c in candidates]
            r.sort(key=lambda x: x["score"], reverse=True); return r
        mc = self._meta_confidence(prompt); dial = self._dialectic(prompt, candidates)
        n = len(candidates); feat = np.zeros((n, 4))
        ss_v = []
        for i, c in enumerate(candidates):
            ss = self._ss(prompt, c); ncd_v = self._ncd(prompt.lower(), c.lower())
            pw = set(self._w(prompt)) - self._stops; cw = set(self._w(c)) - self._stops
            feat[i] = [max(0, ss), dial[i], 1.0-ncd_v, len(pw&cw)/max(len(pw),1)]
            ss_v.append(ss)
        wt = self._evolve(feat); ev = feat @ wt
        if ev.max() > ev.min(): ev = (ev-ev.min())/(ev.max()-ev.min())
        else: ev = np.full(n, 0.5)
        results = []
        for i, c in enumerate(candidates):
            ncd_s = (1.0-self._ncd(prompt.lower(), c.lower()))*0.15
            s = (ss_v[i]*0.60 + float(ev[i])*0.25 + ncd_s) if ss_v[i]>=0 else (float(ev[i])*0.60 + float(dial[i])*0.25 + ncd_s)
            if mc < 1.0: s = min(s, mc)
            results.append({"candidate": c, "score": float(max(0.0, min(0.95, s))),
                            "reasoning": f"ga={ev[i]:.2f} dial={dial[i]:.2f}"})
        results.sort(key=lambda x: x["score"], reverse=True); return results

    def confidence(self, prompt: str, answer: str) -> float:
        mc = self._meta_confidence(prompt, answer)
        if mc < 0.3: return mc
        ss = self._ss(prompt, answer); ncd_s = (1.0-self._ncd(prompt.lower(), answer.lower()))*0.15
        dial = self._dialectic(prompt, [answer])
        s = (ss*0.60 + float(dial[0])*0.25 + ncd_s) if ss>=0 else (0.5*0.60 + float(dial[0])*0.25 + ncd_s)
        return float(max(0.0, min(0.95, min(s, mc))))
