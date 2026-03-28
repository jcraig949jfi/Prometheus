"""Temporal Age Specialist — Frame B. PRIMARY: temporal_age_reasoning (equation solving).
SECONDARY: causal_intervention, temporal_causal_ordering, compositional_depth. NCD tiebreaker only."""
import re, zlib
from collections import defaultdict
_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_AGE_REL = re.compile(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)', re.I)
_AGE_MULT = re.compile(r'(\w+)\s+is\s+(twice|half|triple|thrice|\d+\s*times)\s+(?:as\s+old\s+as\s+)?(\w+)[\'\u2019]?s?\s*(?:age)?', re.I)
_AGE_ABS = re.compile(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!er|est)', re.I)
_AGE_SUM = re.compile(r'(?:sum|total|combined)\s+(?:of\s+)?(?:their\s+)?ages?\s+(?:is|=|equals?)\s+(\d+)', re.I)
_AGE_AGO = re.compile(r'(\d+)\s+years?\s+ago,?\s+(\w+)\s+was\s+(\d+)', re.I)
_AGE_HENCE = re.compile(r'in\s+(\d+)\s+years?,?\s+(\w+)\s+will\s+be\s+(\d+)', re.I)
_AGE_RATIO = re.compile(r'ratio\s+of\s+(\w+)[\'\u2019]?s?\s+age\s+to\s+(\w+)[\'\u2019]?s?\s+(?:age\s+)?is\s+(\d+):(\d+)', re.I)
_CAUSE = re.compile(r'(\w+)\s+(?:causes?|leads?\s+to|produces?|results?\s+in)\s+(\w+)', re.I)
_ARROW = re.compile(r'(\w+)\s*(?:->|-->|=>|→)\s*(\w+)')
_FORCE = re.compile(r'(?:force|set|clamp|fix|intervene)\s*\(?\s*(\w+)\s*(?:=|to)\s*(\S+)', re.I)
_ALLARB = re.compile(r'[Aa]ll\s+(\w+)\s+are\s+(\w+)')
_NOTALLARB = re.compile(r'[Nn]ot\s+all\s+(\w+)\s+are\s+(\w+)')
_BEFORE = re.compile(r'(\w[\w\s]*?)\s+(?:happened\s+)?before\s+(\w[\w\s]*?)(?:[.,;]|$)', re.I)
_AFTER = re.compile(r'(\w[\w\s]*?)\s+(?:happened\s+)?after\s+(\w[\w\s]*?)(?:[.,;]|$)', re.I)
_TB = {'p': r'(?:stopped|still|again|already|anymore)', 's': r'(?:every.*?some|all.*?not|not.*?all)',
       'f': r'(?:either.*?or|must\s+be\s+one)', 'v': r'(?:successful|survivors?|winners?|made\s+it)',
       'k': r'(?:already\s+(?:spent|invested|paid)|too\s+late\s+to)'}
_TIERB = {k: re.compile(v, re.I) for k, v in _TB.items()}
def _ns(t): return [float(x) for x in _NUM.findall(t)]
def _h(t, *w): return any(x in t for x in w)

class ReasoningTool:
    def _ncd(s, a, b):
        if not a or not b: return 1.0
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        d = max(ca, cb)
        return (len(zlib.compress((a+" "+b).encode())) - min(ca, cb)) / d if d else 1.0
    def _meta_confidence(s, p, a=""):
        pl = p.lower()
        if re.search(r'\b(?:have|has)\s+\w+\s+(?:stopped|quit|given up)', pl): return 0.20
        if re.search(r'\bevery\b.*\b(?:a|some)\b.*\?', pl): return 0.20
        if re.search(r'already\s+(?:spent|invested|paid)', pl): return 0.20
        if re.search(r'either.*?or|must\s+be\s+one', pl) and len(pl.split()) > 15: return 0.25
        if re.search(r'(?:successful|survivors?).*(?:sample|study)', pl): return 0.20
        if re.search(r'scored?\s+\d+.*then\s+\d+.*(?:worse|better)', pl): return 0.22
        if re.search(r'non-?refundable', pl): return 0.20
        n = sum(1 for v in _TIERB.values() if v.search(pl))
        return max(0.20, 1.0 - 0.15*n) if n else 1.0
    def _temporal_age(s, p, c):
        vals = {m.group(1).lower(): float(m.group(2)) for m in _AGE_ABS.finditer(p)}
        cons = []  # (name, coeff, ref, offset) meaning name = coeff*ref + offset
        for m in _AGE_REL.finditer(p):
            nm, d, dr, rf = m.group(1).lower(), float(m.group(2)), m.group(3).lower(), m.group(4).lower()
            cons.append((nm, 1.0, rf, d if dr=='older' else -d))
        for m in _AGE_MULT.finditer(p):
            nm, mw, rf = m.group(1).lower(), m.group(2).lower(), m.group(3).lower()
            mu = {'twice':2.0,'half':0.5,'triple':3.0,'thrice':3.0}.get(mw)
            if mu is None: mn=_NUM.search(mw); mu=float(mn.group()) if mn else 2.0
            cons.append((nm, mu, rf, 0.0))
        for m in _AGE_AGO.finditer(p): vals[m.group(2).lower()] = float(m.group(3)) + int(m.group(1))
        for m in _AGE_HENCE.finditer(p): vals[m.group(2).lower()] = float(m.group(3)) - int(m.group(1))
        for m in _AGE_RATIO.finditer(p):
            n1, n2, r1, r2 = m.group(1).lower(), m.group(2).lower(), float(m.group(3)), float(m.group(4))
            if n2 in vals: vals[n1] = vals[n2]*r1/r2
            elif n1 in vals and r1: vals[n2] = vals[n1]*r2/r1
            else: cons.append((n1, r1/r2, n2, 0.0))
        sm = _AGE_SUM.search(p)
        if sm and cons and not vals:
            total = float(sm.group(1))
            names = list(set(x for c_ in cons for x in (c_[0], c_[2])))
            if len(names) == 2:
                a_, b_ = names[0], names[1]
                for cn in cons:
                    if cn[0]==a_ and cn[2]==b_:
                        vals[b_] = (total-cn[3])/(cn[1]+1); vals[a_] = cn[1]*vals[b_]+cn[3]; break
                    elif cn[0]==b_ and cn[2]==a_:
                        vals[a_] = (total-cn[3])/(cn[1]+1); vals[b_] = cn[1]*vals[a_]+cn[3]; break
        if not cons and not vals: return None
        for _ in range(30):
            ch = False
            for nm, co, rf, off in cons:
                if nm not in vals and rf in vals: vals[nm] = co*vals[rf]+off; ch=True
                elif rf not in vals and nm in vals and co: vals[rf] = (vals[nm]-off)/co; ch=True
            if not ch: break
        cn = _ns(c)
        if not cn or not vals: return None
        best = min((abs(cv-av) for cv in cn for av in vals.values()), default=999)
        return 0.93 if best < 0.5 else 0.15
    def _causal_intervention(s, p, c):
        edges = [(a.lower(),b.lower()) for pat in (_CAUSE,_ARROW) for a,b in pat.findall(p)]
        fm = _FORCE.search(p)
        if len(edges)<1 or not fm: return None
        forced = fm.group(1).lower()
        downstream, front = set(), {forced}
        for _ in range(10):
            nxt = set()
            for a, b in edges:
                if a in front and b not in downstream: downstream.add(b); nxt.add(b)
            if not nxt: break
            front = nxt
        cl = c.lower()
        for d in downstream:
            if d in cl:
                if _h(cl, 'affected','changes','stops','0','zero','no longer'): return 0.88
                if _h(cl, 'unaffected','no effect'): return 0.15
        return 0.50
    def _temporal_causal_order(s, p, c):
        bef, aft = _BEFORE.findall(p), _AFTER.findall(p)
        if not bef and not aft: return None
        order, events = defaultdict(set), set()
        for a, b in bef: a,b=a.strip().lower(),b.strip().lower(); order[a].add(b); events|={a,b}
        for a, b in aft: a,b=a.strip().lower(),b.strip().lower(); order[b].add(a); events|={a,b}
        if not events: return None
        pl, cl = p.lower(), c.lower()
        roots = events - set(b for vs in order.values() for b in vs)
        leaves = events - set(order.keys())
        if _h(pl,'earliest','first'):
            return 0.88 if any(any(w in cl for w in r.split()[:3]) for r in roots) else 0.25
        if _h(pl,'latest','last','most recent'):
            return 0.88 if any(any(w in cl for w in l.split()[:3]) for l in leaves) else 0.25
        return 0.50
    def _compositional_depth(s, p, c):
        links, negs = _ALLARB.findall(p), _NOTALLARB.findall(p)
        if len(links)<2: return None
        g, broken = defaultdict(set), set()
        for a, b in links: g[a.lower()].add(b.lower())
        for a, b in negs: broken.add((a.lower(), b.lower()))
        def reach(nd, d=0):
            if d>8: return set()
            r = set()
            for n in g.get(nd, set()):
                if (nd,n) not in broken: r.add(n); r|=reach(n,d+1)
            return r
        cl = c.lower()
        for nd in g:
            for t in reach(nd):
                if nd in cl and t in cl:
                    if _h(cl,'yes','true','is a','correct'): return 0.88
                    if _h(cl,'no','false','not'): return 0.12
        return 0.50
    def _std(s, p, c):
        pl, cl, cn, pn = p.lower(), c.lower(), _ns(c), _ns(p)
        m = re.search(r'cost\s+\$?([\d.]+).*?costs?\s+\$?([\d.]+)\s+more', pl)
        if m: v=(float(m.group(1))-float(m.group(2)))/2; return 0.92 if cn and abs(cn[0]-v)<0.01 else 0.15
        if re.search(r'coin.*(?:flip|toss)', pl): return 0.88 if _h(cl,'50','1/2','same','independent') else 0.15
        m = re.search(r'all\s+but\s+(\d+)', pl)
        if m and 'how many' in pl: return 0.90 if cn and abs(cn[0]-float(m.group(1)))<0.5 else 0.15
        m = re.search(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)', pl)
        if m: v=int(m.group(1))%int(m.group(2)); return 0.90 if cn and abs(cn[0]-v)<0.01 else 0.15
        if 'correlat' in pl and 'cause' in pl: return 0.85 if _h(cl,'no','not') else 0.15
        if pn and cn and any(abs(a-b)<0.01 for a in pn for b in cn): return 0.65
        return None
    def _score(s, p, c):
        for fn in (s._temporal_age, s._causal_intervention, s._temporal_causal_order, s._compositional_depth):
            v = fn(p, c)
            if v is not None: return v, fn.__name__
        v = s._std(p, c)
        if v is not None: return v, 'standard'
        return 0.50 + (1.0-s._ncd(p,c))*0.08, 'ncd_fallback'
    def evaluate(s, prompt: str, candidates: list) -> list:
        meta = s._meta_confidence(prompt); res = []
        for c in candidates:
            v, tag = s._score(prompt, c)
            res.append({'candidate':c, 'score':round(v*(0.88+0.12*meta),4), 'reasoning':tag, 'meta':round(meta,3)})
        res.sort(key=lambda r: r['score'], reverse=True); return res
    def confidence(s, prompt: str, answer: str) -> float:
        meta = s._meta_confidence(prompt, answer)
        if meta < 0.30: return meta
        v, _ = s._score(prompt, answer); return round(min(meta, v), 4)
