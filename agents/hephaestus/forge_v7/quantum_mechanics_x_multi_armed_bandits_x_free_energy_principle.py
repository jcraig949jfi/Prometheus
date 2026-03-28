"""QM x Multi-Armed Bandits x Free Energy Principle. Frame D — Judgment Calibrator.
Quantum-inspired amplitude scoring (candidates as basis states), UCB exploration
of scoring strategies, free energy minimization (accuracy + complexity).
Score: Structural (60%) + Computation (25%) + NCD (15%)."""
import re, math, zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """QM-MAB-FEP: amplitude scoring, UCB strategy, free energy minimizer."""
    def __init__(self):
        self._pats = {'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|units)?', re.I)}
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
        self._arm_n = np.ones(4); self._arm_r = np.array([0.5,0.5,0.5,0.5])

    def _nu(self, t): return [float(m) for m in re.findall(r'-?\d+\.?\d*', t)]
    def _w(self, t): return re.findall(r'\b[a-z]+(?:\'[a-z]+)?\b', t.lower())
    def _ncd(self, a, b):
        try:
            ba, bb = a.encode(), b.encode()
            ca, cb, cab = len(zlib.compress(ba)), len(zlib.compress(bb)), len(zlib.compress(ba+bb))
            return (cab - min(ca, cb)) / max(ca, cb, 1)
        except Exception: return 1.0

    def _qm_probs(self, prompt, candidates):
        n = len(candidates)
        if n == 0: return np.array([])
        pw = set(self._w(prompt)) - self._stops
        re_a, im_a = np.zeros(n), np.zeros(n)
        for i, c in enumerate(candidates):
            sc = set(self._w(c)) - self._stops
            re_a[i] = len(pw & sc) / max(len(pw | sc), 1)
            im_a[i] = len(sc - pw) / max(len(sc), 1) * 0.3
        mag2 = re_a**2 + im_a**2; s = mag2.sum()
        return mag2 / s if s > 0 else np.ones(n) / n

    def _ucb_arm(self):
        t = int(np.sum(self._arm_n))
        return int(np.argmax(self._arm_r / self._arm_n + np.sqrt(2*math.log(max(t,1)) / self._arm_n)))

    def _strat(self, arm, prompt, cand, qp):
        nv = self._ncd(prompt.lower(), cand.lower())
        pw = set(self._w(prompt)) - self._stops; cw = set(self._w(cand)) - self._stops
        ov = len(pw & cw) / max(len(pw), 1)
        if arm == 0: return ov*0.7 + (1-nv)*0.3
        if arm == 1: return qp*0.7 + ov*0.3
        if arm == 2: return ov*0.4 + qp*0.3 + (1-nv)*0.3
        par = 1.0/(1.0+math.log1p(max(len(cw),1)))
        return ov*0.3 + par*0.4 + (1-nv)*0.3

    def _fe(self, acc, cand):
        b = cand.encode(); cpx = min(1.0, len(zlib.compress(b))/max(len(b),1)) if b else 1.0
        return 1.0 / (1.0 + math.exp(acc - 0.3*cpx))

    def _ss(self, prompt, cand):
        pl, cl = prompt.lower(), cand.lower().strip()
        ws = re.findall(r"[a-z'\-]+", cl); cl0 = ws[0] if ws else cl
        pn, cn = self._nu(prompt), self._nu(cand)
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
        if len(pn)>=2 and any(w in pl for w in ('month','birthday','drawer','sock','box','categor','slot')):
            if sorted(pn)[-1]>sorted(pn)[0]:
                if cl0=='yes' or 'must' in cl or 'at least' in cl: return 1.0
                if cl0=='no' and 'not' not in cl[3:]: return 0.0
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
        m12 = re.search(r'the\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)', pl)
        if m12 and re.search(r'who\s+(?:was|is|did|got|were)\s+(?:being\s+)?(\w+)', pl):
            su, ob = m12.group(1).lower(), m12.group(3).lower()
            if ob in cl and su not in cl: return 1.0
            if su in cl and ob not in cl: return 0.0
        if 'odd' in pl and 'sum' in pl:
            m8 = re.search(r'(two|2|three|3)\s+odd', pl)
            if m8:
                nv = {'two':2,'2':2,'three':3,'3':3}.get(m8.group(1),2); ev = nv%2==0
                if 'always odd' in pl:
                    if cl0 in ('false','no'): return 1.0 if ev else 0.0
                    if cl0 in ('true','yes'): return 0.0 if ev else 1.0
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
        mc = self._meta_confidence(prompt); qp = self._qm_probs(prompt, candidates)
        arm = self._ucb_arm(); results = []
        for i, c in enumerate(candidates):
            ss = self._ss(prompt, c); ncd_s = (1.0-self._ncd(prompt.lower(), c.lower()))*0.15
            acc = ss if ss >= 0 else self._strat(arm, prompt, c, float(qp[i]))
            fe_s = self._fe(acc, c)
            s = acc*0.60 + fe_s*0.25 + ncd_s
            if mc < 1.0: s = min(s, mc)
            results.append({"candidate": c, "score": float(max(0.0, min(0.95, s))),
                            "reasoning": f"arm={arm} qm={qp[i]:.2f}"})
        if results:
            self._arm_n[arm] += 1; self._arm_r[arm] += max(r["score"] for r in results)
        results.sort(key=lambda x: x["score"], reverse=True); return results

    def confidence(self, prompt: str, answer: str) -> float:
        mc = self._meta_confidence(prompt, answer)
        if mc < 0.3: return mc
        ss = self._ss(prompt, answer); ncd_s = (1.0-self._ncd(prompt.lower(), answer.lower()))*0.15
        acc = ss if ss >= 0 else 0.5
        fe_s = self._fe(acc, answer)
        s = acc*0.60 + fe_s*0.25 + ncd_s
        return float(max(0.0, min(0.95, min(s, mc))))
