"""Final Gap Closer — 5 uncovered categories + full standard battery + Tier B meta.
Gaps: causal_intervention, compositional_depth_scaling, temporal_age_reasoning,
temporal_causal_ordering, tom_strategic_deception. numpy+stdlib only."""
import re, math, zlib
from collections import defaultdict

_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_FORCE = re.compile(r'(?:force|set|clamp|fix|intervene).*?(\w+)\s*=\s*(\S+)', re.I)
_CHAIN = re.compile(r'(\w+)\s*[→\->]+\s*', re.I)
_ALLARB = re.compile(r'[Aa]ll\s+(\w+)\s+are\s+(\w+)', re.I)
_ISA = re.compile(r'(\w+)\s+is\s+(?:a[n]?\s+)?(\w+)', re.I)
_AGE_REL = re.compile(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)', re.I)
_AGE_MULT = re.compile(r'(\w+)\s+is\s+(twice|half|triple|\d+\s*times)\s+(\w+)[\'\u2019]?s?\s+age', re.I)
_AGE_ABS = re.compile(r'(\w+)\s+is\s+(\d+)', re.I)
_BEFORE = re.compile(r'[Bb]efore\s+(?:that\s+|the\s+)?(.+?)(?:[.,;]|$)')
_AFTER = re.compile(r'[Aa]fter\s+(?:that\s+|the\s+)?(.+?)(?:[.,;]|$)')
_OPPOSITE = re.compile(r'(?:opposite|contrary|reverse|negat)', re.I)
_WANTS = re.compile(r'(\w+)\s+wants?\s+(\w+)\s+to\s+(?:go\s+)?(\w+)', re.I)
_SAYS = re.compile(r'[Ww]hat\s+should\s+(\w+)\s+say', re.I)
_BAT = re.compile(r'(\w+)\s+and\s+(?:a\s+)?(\w+)\s+(?:cost|total)\s+([\d.]+).*?(\w+)\s+costs?\s+([\d.]+)\s+more', re.I)
_ALLBUT = re.compile(r'[Aa]ll\s+(?:but|except)\s+(\d+)', re.I)
_FENCE = re.compile(r'(\d+)\s*(?:fence\s*)?posts?\s.*?(\d+)\s*(?:meter|feet|ft|m|yard)', re.I)
_MOD = re.compile(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)', re.I)
_COINS = re.compile(r'(?:coin|flip|toss)', re.I)
_PARITY = re.compile(r'(?:odd|even)\s*(?:\+|plus|and|times|\*|minus|-)\s*(?:odd|even)', re.I)
_PIGEON = re.compile(r'(\d+)\s*(?:items?|objects?|pigeons?|people|balls?).*?(\d+)\s*(?:boxes|holes?|slots?|containers?)', re.I)
_PCT = re.compile(r'(?:increase|decrease|raise|lower|drop|rise).*?(\d+)\s*%', re.I)
_BASERATE = re.compile(r'(?:prevalence|base\s*rate|prior|(\d+)\s*(?:in|out\s*of)\s*(\d+))', re.I)
_SVO = re.compile(r'[Tt]he\s+(\w+)\s+(chased|bit|hit|pushed|pulled|caught|ate|saw|followed)\s+the\s+(\w+)', re.I)
_DIR = re.compile(r'(north|south|east|west|left|right|up|down)', re.I)
_NEG = re.compile(r'\b(?:not|no|never|neither|nor)\b', re.I)
_COND = re.compile(r'[Ii]f\s+(.+?),?\s+then\s+(.+?)(?:[.,;]|$)')
_COMP = re.compile(r'(\w+)\s+(?:is|are)\s+(?:larger|greater|bigger|more|taller|heavier|faster|older|higher)\s+than\s+(\w+)', re.I)
_TB = {'presup': r'(?:stopped|still|again|already|anymore)', 'scope': r'(?:every.*?some|all.*?not|not.*?all)',
       'fdichotomy': r'(?:either.*?or|must\s+be\s+one)', 'survivor': r'(?:successful|survivors?|winners?|made\s+it)',
       'sunk': r'(?:already\s+(?:spent|invested|paid)|too\s+late\s+to)'}
_TIERB = {k: re.compile(v, re.I) for k, v in _TB.items()}

def _has(t, *ws): return any(w in t for w in ws)

class ReasoningTool:
    def _ncd(self, x, y):
        cx, cy = len(zlib.compress(x.encode())), len(zlib.compress(y.encode()))
        cxy = len(zlib.compress((x + " " + y).encode()))
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d else 1.0

    def _ns(self, t): return [float(x) for x in _NUM.findall(t)]

    def _causal_intervention(self, p, c):
        chains, fm = _CHAIN.findall(p), _FORCE.search(p + " " + c)
        if not chains or not fm: return None
        forced, ds, found = fm.group(1).lower(), [], False
        for n in chains:
            if found: ds.append(n.lower())
            if n.lower() == forced: found = True
        if not ds: return None
        cl = c.lower()
        if any(d in cl for d in ds):
            return 0.8 if _has(cl, 'affected', 'changes', 'disrupted', '0', 'zero', 'stops') else 0.4
        return 0.3

    def _compositional_depth(self, p, c):
        links, isa = _ALLARB.findall(p), _ISA.findall(p)
        if len(links) < 2 and len(isa) < 2: return None
        g = defaultdict(set)
        for a, b in links: g[a.lower()].add(b.lower())
        for a, b in isa:
            if a.lower() != b.lower(): g[a.lower()].add(b.lower())
        def reach(s, d=0):
            if d > 8: return set()
            r = set()
            for n in g.get(s, set()): r.add(n); r |= reach(n, d+1)
            return r
        cl = c.lower()
        for s in g:
            for t in reach(s):
                if s in cl and t in cl:
                    if _has(cl, 'yes', 'true', 'is a', 'is an', 'correct'): return 0.85
                    if _has(cl, 'no', 'false', 'not'): return 0.15
        return 0.5

    def _temporal_age(self, p, c):
        vals = {m.group(1).lower(): float(m.group(2)) for m in _AGE_ABS.finditer(p)}
        rels = []
        for m in _AGE_REL.finditer(p):
            rels.append((m.group(1).lower(), float(m.group(2)), m.group(3).lower(), m.group(4).lower()))
        for m in _AGE_MULT.finditer(p):
            mw = m.group(2).lower()
            mu = {'twice': 2, 'half': 0.5, 'triple': 3}.get(mw)
            if mu is None:
                mn = _NUM.search(mw); mu = float(mn.group()) if mn else 2
            rels.append((m.group(1).lower(), mu, 'times', m.group(3).lower()))
        if not rels: return None
        ch = True
        while ch:
            ch = False
            for r in rels:
                if r[0] in vals: continue
                if r[2] == 'older' and r[3] in vals: vals[r[0]] = vals[r[3]] + r[1]; ch = True
                elif r[2] == 'younger' and r[3] in vals: vals[r[0]] = vals[r[3]] - r[1]; ch = True
                elif r[2] == 'times' and r[3] in vals: vals[r[0]] = vals[r[3]] * r[1]; ch = True
        cn = self._ns(c)
        if not cn or not vals: return None
        tv = list(vals.values())[-1]
        return 0.9 if abs(min(cn, key=lambda x: abs(x - tv)) - tv) < 0.01 else 0.2

    def _temporal_causal_order(self, p, c):
        sents = [s.strip() for s in re.split(r'[.!?]+', p) if s.strip()]
        if len(sents) < 2: return None
        bf, af = _BEFORE.findall(p), _AFTER.findall(p)
        if not bf and not af: return None
        ordered = list(reversed(sents))
        cl, pl = c.lower(), p.lower()
        if 'earliest' in pl or 'first' in pl:
            return 0.85 if any(w in cl for w in ordered[0][:30].lower().split()[:3]) else 0.3
        if 'latest' in pl or 'last' in pl or 'most recent' in pl:
            return 0.85 if any(w in cl for w in ordered[-1][:30].lower().split()[:3]) else 0.3
        return 0.5

    def _tom_strategic(self, p, c):
        if not _OPPOSITE.search(p): return None
        wm, sm = _WANTS.search(p), _SAYS.search(p)
        if not wm or not sm: return None
        desired = wm.group(3).lower()
        opp = {'left':'right','right':'left','up':'down','down':'up','north':'south',
               'south':'north','east':'west','west':'east','yes':'no','no':'yes',
               'go':'stay','stay':'go','true':'false','false':'true'}
        say = opp.get(desired, desired); cl = c.lower()
        return 0.9 if say in cl else (0.15 if desired in cl else 0.4)

    def _std(self, p, c):
        pl, cl = p.lower(), c.lower()
        bm = _BAT.search(p)
        if bm:
            ans = (float(bm.group(3)) - float(bm.group(5))) / 2; cn = self._ns(c)
            if cn: return 0.9 if abs(cn[0] - ans) < 0.01 else 0.15
        abm = _ALLBUT.search(p)
        if abm:
            ne = int(abm.group(1)); cn = self._ns(c)
            if cn: return 0.85 if abs(cn[0] - ne) < 0.5 else 0.2
        fm = _FENCE.search(p)
        if fm:
            ln = (int(fm.group(1)) - 1) * int(fm.group(2)); cn = self._ns(c)
            if cn: return 0.9 if abs(cn[0] - ln) < 0.5 else 0.2
        mm = _MOD.search(p)
        if mm:
            ans = int(mm.group(1)) % int(mm.group(2)); cn = self._ns(c)
            if cn: return 0.9 if abs(cn[0] - ans) < 0.01 else 0.2
        if _COINS.search(p):
            if _has(cl, '1/2', '0.5', '50%', 'same', 'independent'): return 0.85
            if _has(cl, 'due', 'overdue', 'more likely'): return 0.15
        if _PARITY.search(p):
            if 'odd' in pl and 'odd' in pl:
                if 'even' in pl: return 0.9 if 'odd' in cl else 0.15
                return 0.9 if 'even' in cl else 0.15
            if 'even' in pl: return 0.9 if 'even' in cl else 0.15
            return 0.9 if 'odd' in cl else 0.15
        pm = _PIGEON.search(p)
        if pm:
            it, bx = int(pm.group(1)), int(pm.group(2))
            if it > bx:
                cn = self._ns(c)
                if cn: return 0.85 if cn[0] >= math.ceil(it / bx) else 0.2
        if _PCT.search(p) and ('then' in pl or 'back' in pl):
            if _has(cl, 'not the same', 'less', 'lower', 'different', 'net'): return 0.8
            if _has(cl, 'same', 'original', 'equal'): return 0.15
        brm = _BASERATE.search(p)
        if brm and brm.group(1):
            if float(brm.group(1)) / float(brm.group(2)) < 0.05:
                if _has(cl, 'low', 'unlikely', 'rare', 'small'): return 0.8
                if _has(cl, 'high', 'likely', 'certain'): return 0.15
        comps = _COMP.findall(p)
        if len(comps) >= 2:
            ch = {a.lower(): b.lower() for a, b in comps}
            if any(w in cl for w in ch): return 0.7
        cm = _COND.search(p)
        if cm and _NEG.search(p): return 0.7 if _has(cl, 'not', 'false') else 0.4
        svo = _SVO.search(p)
        if svo:
            ag, pt = svo.group(1).lower(), svo.group(3).lower()
            if ag in cl and pt in cl: return 0.8 if cl.find(ag) < cl.find(pt) else 0.3
        dirs = _DIR.findall(p)
        if len(dirs) >= 2: return 0.6
        if 'all' in pl and 'are' in pl:
            alm = _ALLARB.findall(p)
            if alm and f'all {alm[0][1].lower()} are {alm[0][0].lower()}' in cl: return 0.15
        pn, cn = self._ns(p), self._ns(c)
        if pn and cn and any(abs(a - b) < 0.01 for a in pn for b in cn): return 0.7
        if _has(pl, 'assume', 'given that', 'suppose'): return 0.6
        return None

    def _meta(self, p):
        n = sum(1 for v in _TIERB.values() if v.search(p))
        return max(0.25, 1.0 - 0.12 * n) if n else 1.0

    def _score(self, p, c):
        for fn in (self._causal_intervention, self._compositional_depth,
                   self._temporal_age, self._temporal_causal_order, self._tom_strategic):
            s = fn(p, c)
            if s is not None: return s, fn.__name__
        s = self._std(p, c)
        if s is not None: return s, 'standard'
        return 0.5 + (1.0 - self._ncd(p, c)) * 0.1, 'ncd_fallback'

    def evaluate(self, prompt: str, candidates: list) -> list:
        m = self._meta(prompt); res = []
        for c in candidates:
            s, tag = self._score(prompt, c)
            res.append({'candidate': c, 'score': round(s * (0.9 + 0.1 * m), 4), 'reasoning': tag, 'meta': round(m, 3)})
        res.sort(key=lambda r: r['score'], reverse=True)
        return res

    def confidence(self, prompt: str, answer: str) -> float:
        s, _ = self._score(prompt, answer)
        return round(s * self._meta(prompt), 4)
