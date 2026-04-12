"""QM x Abductive Reasoning x Criticality. Frame D — Judgment Calibrator.
Superposition scoring, abductive parsimony+coverage, critical threshold detection.
Score: Structural (60%) + Computation (25%) + NCD (15%)."""
import re, math, zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """QM-Abduce-Crit: superposition hypotheses, abductive parsimony, criticality."""
    def __init__(self):
        self._pats = {
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|units)?', re.I),
            'negation': re.compile(r'\b(not|never|no|without|neither|doesn\'t|don\'t|didn\'t)\b', re.I),
        }
        self._presup = [re.compile(r'\b(stopped|quit|ceased|failed)\b.*\b(have you|did you)\b', re.I),
                        re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
                        re.compile(r'\b(?:either)\b.*\b(?:or)\b', re.I)]
        self._fallacy = {
            'presup': re.compile(r'(?:stopped|quit|when did you stop)\b', re.I),
            'scope': re.compile(r'\b(?:every|all|each)\b.*\b(?:some|a|one)\b.*\b(?:not|doesn\'t)\b', re.I),
            'dichot': re.compile(r'\b(?:either|only two|must be one)\b.*\bor\b', re.I),
            'surv': re.compile(r'\b(?:successful|survivors?|winners?)\b.*\b(?:all|every|always)\b', re.I),
            'sunk': re.compile(r'\b(?:already invested|already spent|too far|come this far)\b', re.I),
        }
        self._stops = {'the','is','a','an','and','or','but','in','on','at','to','for','of','it'}

    def _n(self, t): return [float(m) for m in re.findall(r'-?\d+\.?\d*', t)]
    def _w(self, t): return re.findall(r'\b[a-z]+(?:\'[a-z]+)?\b', t.lower())
    def _ncd(self, a, b):
        try:
            ba, bb = a.encode(), b.encode()
            ca, cb, cab = len(zlib.compress(ba)), len(zlib.compress(bb)), len(zlib.compress(ba+bb))
            return (cab - min(ca, cb)) / max(ca, cb, 1)
        except Exception: return 1.0

    def _superpos(self, prompt, candidates):
        n = len(candidates)
        if n == 0: return np.array([])
        pw = set(self._w(prompt)) - self._stops; amps = np.zeros(n)
        for i, c in enumerate(candidates):
            sc = set(self._w(c)) - self._stops
            ov = len(pw & sc) / max(len(pw | sc), 1)
            lp = min(1.0, max(0.2, len(c.split()) / max(len(prompt.split()), 1)))
            amps[i] = math.sqrt(max(0.01, ov * 0.6 + lp * 0.4))
        nm = np.sqrt(np.sum(amps**2))
        return (amps / nm)**2 if nm > 0 else np.ones(n) / n

    def _abductive(self, prompt, cand):
        pw = set(self._w(prompt)) - self._stops; cw = set(self._w(cand)) - self._stops
        cov = len(pw & cw) / max(len(pw), 1)
        par = 1.0 / (1.0 + math.log1p(max(len(cw), 1)))
        return cov * 0.65 + par * 0.35

    def _crit_thresh(self, scores):
        if len(scores) < 2: return 0.5
        s = np.sort(scores)[::-1]; gap = s[0] - s[1]
        mg = float(np.mean(np.diff(s)))
        return float(min(1.0, 0.3 + 0.15 * (gap / (abs(mg) + 1e-9)))) if abs(mg) > 1e-9 else 0.5

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
        if m2 and len(pn) >= 2 and cn:
            wb = m2.group(1) in ('larger','greater','bigger'); tgt = max(pn) if wb else min(pn)
            if abs(cn[0]-tgt) < 1e-9: return 1.0
            if abs(cn[0]-(min(pn) if wb else max(pn))) < 1e-9: return 0.0
        mt = re.search(r'(?:cost|costs?)\s+\$?([\d.]+)\s+(?:total|together|in total|combined)', pl)
        md = re.search(r'costs?\s+\$?([\d.]+)\s+more\s+than', pl)
        if mt and md:
            total, diff = float(mt.group(1)), float(md.group(1)); cheap = (total-diff)/2.0
            if cn:
                if abs(cn[0]-cheap) < 0.01: return 1.0
                if abs(cn[0]-diff) < 0.01: return 0.0
        mu = re.search(r'(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|gallon|cup)\s+of\s+\w+.*(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|gallon|cup)\s+of\s+\w+', pl)
        if mu and mu.group(1)==mu.group(2) and any(w in pl for w in ('heav','weigh','lighter','which')):
            if any(w in cl for w in ('same','equal','neither','both')): return 1.0
            if len(cl) < 30: return 0.0
        m6 = re.search(r'all\s+(\w+)\s+are\s+(\w+)', pl); m7 = re.search(r'are\s+all\s+(\w+)\s+(\w+)', pl)
        if m6 and m7 and m6.group(1) != m7.group(1):
            if cl0 == 'no' or 'not necessarily' in cl: return 1.0
            if cl0 == 'yes': return 0.0
        if re.search(r'0\.9{3,}', pl) and any(w in pl for w in ('equal','= 1','equals','same')):
            if cl0 == 'yes' or 'equal' in cl: return 1.0
            if cl0 == 'no': return 0.0
        if any(w in pl for w in ('coin','die','dice','roulette','flip','roll')):
            if any(w in pl for w in ('in a row','previous','last','after','next','still','now')):
                if 'higher' in cl or 'lower' in cl or 'increase' in cl: return 0.0
                if '50' in cl or '1/2' in cl or '0.5' in cl or 'same' in cl: return 1.0
        m9 = re.search(r'all\s+but\s+(\d+)\s+(?:\w+\s+){0,3}(die|died|leave|left|lost|broke|ran|flew|escaped|gone|disappear)', pl)
        if m9:
            sv = m9.group(1)
            if cl.strip() == sv: return 1.0
            if cl.strip().isdigit() and cl.strip() != sv: return 0.0
        cgt = re.findall(r'(\w+)\s+(?:is\s+)?(?:greater|larger|more|bigger|taller|heavier|higher|faster|older)\s+than\s+(\w+)', pl, re.I)
        if cgt:
            ent = {}
            for a, b in cgt: ent[a.lower()] = ent.get(a.lower(),0)+1; ent.setdefault(b.lower(),0)
            top = max(ent, key=ent.get) if ent else ''
            if top and top in cl: return 1.0
            return 0.3
        ifm = re.search(r'if\s+(.+?)[,.](.+?)\.', pl)
        if ifm:
            after = pl[ifm.end():]
            if re.search(r'\bnot\b|\bdoes\s+not\b|\bisn.t\b|\bdon.t\b', after):
                if cl0 == 'no' or 'therefore not' in cl or 'did not' in cl: return 1.0
                if cl0 == 'yes': return 0.0
        if re.search(r'not\s+(all|every)\s+\w+', pl) and '?' in pl:
            if 'cannot' in cl or 'not enough' in cl or 'cannot be determined' in cl: return 1.0
            if cl in ('yes','no') and len(cl) < 5: return 0.3
        return -1.0

    def _meta_confidence(self, prompt, answer=''):
        pl = prompt.lower()
        for p in self._fallacy.values():
            if p.search(pl): return 0.25
        for p in self._presup:
            if p.search(pl): return 0.25
        if re.search(r'\b(best|worst|favorite|opinion|beautiful|ugly)\b', pl):
            if not re.search(r'\bbest\s+(?:explain|describe|account|represent|fit)', pl): return 0.28
        if len(pl.split()) < 6 and not self._pats['numeric'].search(pl): return 0.20
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates: return []
        mc = self._meta_confidence(prompt); probs = self._superpos(prompt, candidates)
        raw = np.zeros(len(candidates))
        for i, c in enumerate(candidates):
            ss = self._ss(prompt, c); abd = self._abductive(prompt, c)
            ncd_s = (1.0 - self._ncd(prompt.lower(), c.lower())) * 0.15
            raw[i] = (ss * 0.60 + abd * 0.25 + ncd_s) if ss >= 0 else (float(probs[i]) * 0.60 + abd * 0.25 + ncd_s)
        cr = self._crit_thresh(raw)
        results = []
        for i, c in enumerate(candidates):
            s = max(raw[i]*0.8, raw[i]*cr + raw[i]*(1.0-cr)*0.5)
            if mc < 1.0: s = min(s, mc)
            results.append({"candidate": c, "score": float(max(0.0, min(0.95, s))),
                            "reasoning": f"crit={cr:.2f} meta={mc:.2f}"})
        results.sort(key=lambda x: x["score"], reverse=True); return results

    def confidence(self, prompt: str, answer: str) -> float:
        mc = self._meta_confidence(prompt, answer)
        if mc < 0.3: return mc
        ss = self._ss(prompt, answer); abd = self._abductive(prompt, answer)
        ncd_s = (1.0 - self._ncd(prompt.lower(), answer.lower())) * 0.15
        s = (ss*0.60 + abd*0.25 + ncd_s) if ss >= 0 else (0.5*0.60 + abd*0.25 + ncd_s)
        return float(max(0.0, min(0.95, min(s, mc))))
