"""Causal Intervention Specialist — Frame B. PRIMARY: causal_intervention (graph mutilation).
SECONDARY: temporal_age, temporal_causal_ordering, compositional_depth. NCD tiebreaker only."""
import re, zlib
from collections import defaultdict
_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_CAUSE = re.compile(r'(\w+)\s+(?:causes?|leads?\s+to|produces?|results?\s+in|triggers?)\s+(\w+)', re.I)
_ARROW = re.compile(r'(\w+)\s*(?:->|-->|=>|→)\s*(\w+)')
_IFT = re.compile(r'if\s+(\w+),?\s*(?:then\s+)?(\w+)\s+(?:will|would|happens?)', re.I)
_FORCE = re.compile(r'(?:force|set|clamp|fix|intervene\s+on|do)\s*\(?\s*(\w+)\s*(?:=|to)\s*(\S+)', re.I)
_FORCE2 = re.compile(r'(?:we|you)\s+(?:force|set|clamp|fix)\s+(\w+)\s+(?:=|to)\s+(\S+)', re.I)
_DSTREAM = re.compile(r'(?:what\s+happens?\s+to|effect\s+on|impact\s+on)\s+(\w+)', re.I)
_ALLARB = re.compile(r'[Aa]ll\s+(\w+)\s+are\s+(\w+)')
_NOTALLARB = re.compile(r'[Nn]ot\s+all\s+(\w+)\s+are\s+(\w+)')
_AGE_REL = re.compile(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)', re.I)
_AGE_MULT = re.compile(r'(\w+)\s+is\s+(twice|half|triple|\d+\s*times)\s+(\w+)[\'\u2019]?s?\s+age', re.I)
_AGE_ABS = re.compile(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!er|est)', re.I)
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
    def _reach(s, edges, start, mx=10):
        reached, front = set(), {start}
        for _ in range(mx):
            nxt = set()
            for a, b in edges:
                if a in front and b not in reached: reached.add(b); nxt.add(b)
            if not nxt: break
            front = nxt
        return reached
    def _causal_intervention(s, p, c):
        edges = []
        for pat in (_CAUSE, _ARROW, _IFT): edges += [(a.lower(), b.lower()) for a, b in pat.findall(p)]
        if not edges: return None
        fm = _FORCE.search(p) or _FORCE2.search(p)
        if not fm:
            m2 = re.search(r'if\s+(?:we\s+)?(?:force|set|clamp)\s+(\w+)\s*(?:=|to)\s*(\S+)', p, re.I)
            if m2: fm = m2
        if not fm: return None
        fv, fval = fm.group(1).lower(), fm.group(2).lower().rstrip('.,;?!')
        mutilated = [(a, b) for a, b in edges if b != fv]
        downstream = s._reach(edges, fv)
        dm, cl = _DSTREAM.search(p), c.lower()
        if dm:
            tgt = dm.group(1).lower()
            if tgt in downstream:
                roots = set(a for a, b in mutilated) - set(b for a, b in mutilated)
                still = any(tgt in s._reach(mutilated, r) for r in roots)
                if fval in ('0', 'zero', 'false', 'off', 'null'):
                    if _h(cl, 'no effect', 'unaffected', 'unchanged'): return 0.15 if not still else 0.5
                    if _h(cl, 'affected', 'changes', 'disrupted', '0', 'zero', 'stops', 'no longer'): return 0.90
                    return 0.45
                return 0.85 if _h(cl, 'affected', 'changes', 'determined') else 0.40
        for d in downstream:
            if d in cl:
                if _h(cl, 'affected', 'changes', 'disrupted', 'stops', '0', 'zero'): return 0.85
                if _h(cl, 'unaffected', 'no effect'): return 0.15
                return 0.60
        return 0.50
    def _temporal_age(s, p, c):
        vals = {m.group(1).lower(): float(m.group(2)) for m in _AGE_ABS.finditer(p)}
        rels = []
        for m in _AGE_REL.finditer(p):
            rels.append((m.group(1).lower(), float(m.group(2)), m.group(3).lower(), m.group(4).lower()))
        for m in _AGE_MULT.finditer(p):
            mw = m.group(2).lower()
            mu = {'twice':2,'half':0.5,'triple':3}.get(mw)
            if mu is None: mn = _NUM.search(mw); mu = float(mn.group()) if mn else 2
            rels.append((m.group(1).lower(), mu, 'times', m.group(3).lower()))
        if not rels and not vals: return None
        for _ in range(20):
            ch = False
            for r in rels:
                if r[0] not in vals:
                    if r[2]=='older' and r[3] in vals: vals[r[0]]=vals[r[3]]+r[1]; ch=True
                    elif r[2]=='younger' and r[3] in vals: vals[r[0]]=vals[r[3]]-r[1]; ch=True
                    elif r[2]=='times' and r[3] in vals: vals[r[0]]=vals[r[3]]*r[1]; ch=True
                if r[3] not in vals and r[0] in vals:
                    if r[2]=='older': vals[r[3]]=vals[r[0]]-r[1]; ch=True
                    elif r[2]=='younger': vals[r[3]]=vals[r[0]]+r[1]; ch=True
                    elif r[2]=='times' and r[1]!=0: vals[r[3]]=vals[r[0]]/r[1]; ch=True
            if not ch: break
        cn = _ns(c)
        if not cn or not vals: return None
        best = min((abs(cv-tv) for cv in cn for tv in vals.values()), default=999)
        return 0.92 if best < 0.5 else 0.18
    def _temporal_causal_order(s, p, c):
        bef, aft = _BEFORE.findall(p), _AFTER.findall(p)
        if not bef and not aft: return None
        order, events = defaultdict(set), set()
        for a, b in bef:
            a, b = a.strip().lower(), b.strip().lower(); order[a].add(b); events |= {a, b}
        for a, b in aft:
            a, b = a.strip().lower(), b.strip().lower(); order[b].add(a); events |= {a, b}
        if not events: return None
        pl, cl = p.lower(), c.lower()
        roots = events - set(b for vs in order.values() for b in vs)
        leaves = events - set(order.keys())
        if _h(pl, 'earliest', 'first'):
            return 0.88 if any(any(w in cl for w in r.split()[:3]) for r in roots) else 0.25
        if _h(pl, 'latest', 'last', 'most recent'):
            return 0.88 if any(any(w in cl for w in l.split()[:3]) for l in leaves) else 0.25
        return 0.50
    def _compositional_depth(s, p, c):
        links, negs = _ALLARB.findall(p), _NOTALLARB.findall(p)
        if len(links) < 2: return None
        g, broken = defaultdict(set), set()
        for a, b in links: g[a.lower()].add(b.lower())
        for a, b in negs: broken.add((a.lower(), b.lower()))
        def reach(node, d=0):
            if d > 8: return set()
            r = set()
            for n in g.get(node, set()):
                if (node, n) not in broken: r.add(n); r |= reach(n, d+1)
            return r
        cl = c.lower()
        for nd in g:
            for t in reach(nd):
                if nd in cl and t in cl:
                    if _h(cl, 'yes', 'true', 'is a', 'correct'): return 0.88
                    if _h(cl, 'no', 'false', 'not'): return 0.12
        for a, b in broken:
            if a in cl and b in cl:
                if _h(cl, 'no', 'false', 'not'): return 0.88
                if _h(cl, 'yes', 'true'): return 0.12
        return 0.50
    def _std(s, p, c):
        pl, cl, cn, pn = p.lower(), c.lower(), _ns(c), _ns(p)
        m = re.search(r'cost\s+\$?([\d.]+).*?costs?\s+\$?([\d.]+)\s+more', pl)
        if m:
            v = (float(m.group(1))-float(m.group(2)))/2
            return 0.92 if cn and abs(cn[0]-v)<0.01 else 0.15
        if re.search(r'coin.*(?:flip|toss)', pl):
            return 0.88 if _h(cl, '50', '1/2', 'same', 'independent') else 0.15
        m = re.search(r'all\s+but\s+(\d+)', pl)
        if m and 'how many' in pl: return 0.90 if cn and abs(cn[0]-float(m.group(1)))<0.5 else 0.15
        m = re.search(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)', pl)
        if m: v=int(m.group(1))%int(m.group(2)); return 0.90 if cn and abs(cn[0]-v)<0.01 else 0.15
        if re.search(r'increases?\s+by\s+\d+%.*decreases?\s+by', pl):
            return 0.82 if _h(cl, 'lower', 'less', 'not the same', 'different') else 0.15
        if 'correlat' in pl and 'cause' in pl: return 0.85 if _h(cl, 'no', 'not') else 0.15
        if pn and cn and any(abs(a-b)<0.01 for a in pn for b in cn): return 0.65
        return None
    def _score(s, p, c):
        for fn in (s._causal_intervention, s._temporal_age, s._temporal_causal_order, s._compositional_depth):
            v = fn(p, c)
            if v is not None: return v, fn.__name__
        v = s._std(p, c)
        if v is not None: return v, 'standard'
        return 0.50 + (1.0-s._ncd(p, c))*0.08, 'ncd_fallback'
    def evaluate(s, prompt: str, candidates: list) -> list:
        meta = s._meta_confidence(prompt); res = []
        for c in candidates:
            v, tag = s._score(prompt, c)
            res.append({'candidate': c, 'score': round(v*(0.88+0.12*meta), 4), 'reasoning': tag, 'meta': round(meta, 3)})
        res.sort(key=lambda r: r['score'], reverse=True); return res
    def confidence(s, prompt: str, answer: str) -> float:
        meta = s._meta_confidence(prompt, answer)
        if meta < 0.30: return meta
        v, _ = s._score(prompt, answer); return round(min(meta, v), 4)
