"""Compositional Depth Specialist — Frame B. PRIMARY: compositional_depth_scaling (multi-hop).
SECONDARY: causal_intervention, temporal_age, temporal_causal_ordering. NCD tiebreaker only."""
import re, zlib
from collections import defaultdict, deque
_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_ALLARB = re.compile(r'[Aa]ll\s+(\w+)\s+are\s+(\w+)')
_NOTALLARB = re.compile(r'[Nn]ot\s+all\s+(\w+)\s+are\s+(\w+)')
_NOARB = re.compile(r'[Nn]o\s+(\w+)\s+are\s+(\w+)')
_QISA = re.compile(r'[Ii]s\s+(?:a[n]?\s+)?(\w+)\s+(?:a[n]?\s+)?(\w+)', re.I)
_QARE = re.compile(r'[Aa]re\s+(?:all\s+)?(\w+)\s+(\w+)', re.I)
_CAUSE = re.compile(r'(\w+)\s+(?:causes?|leads?\s+to|produces?|results?\s+in)\s+(\w+)', re.I)
_ARROW = re.compile(r'(\w+)\s*(?:->|-->|=>|→)\s*(\w+)')
_FORCE = re.compile(r'(?:force|set|clamp|fix|intervene)\s*\(?\s*(\w+)\s*(?:=|to)\s*(\S+)', re.I)
_AGE_REL = re.compile(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)', re.I)
_AGE_MULT = re.compile(r'(\w+)\s+is\s+(twice|half|triple|\d+\s*times)\s+(\w+)[\'\u2019]?s?\s*(?:age)?', re.I)
_AGE_ABS = re.compile(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!er|est)', re.I)
_BEFORE = re.compile(r'(\w[\w\s]*?)\s+(?:happened\s+)?before\s+(\w[\w\s]*?)(?:[.,;]|$)', re.I)
_AFTER = re.compile(r'(\w[\w\s]*?)\s+(?:happened\s+)?after\s+(\w[\w\s]*?)(?:[.,;]|$)', re.I)
_TB = {'p': r'(?:stopped|still|again|already|anymore)', 's': r'(?:every.*?some|all.*?not|not.*?all)',
       'f': r'(?:either.*?or|must\s+be\s+one)', 'v': r'(?:successful|survivors?|winners?|made\s+it)',
       'k': r'(?:already\s+(?:spent|invested|paid)|too\s+late\s+to)'}
_TIERB = {k: re.compile(v, re.I) for k, v in _TB.items()}
def _ns(t): return [float(x) for x in _NUM.findall(t)]
def _h(t, *w): return any(x in t for x in w)
def _stem(w):
    w = w.lower()
    if w.endswith('ies') and len(w)>4: return w[:-3]+'y'
    if w.endswith('ses') or w.endswith('xes') or w.endswith('zes'): return w[:-2]
    if w.endswith('s') and not w.endswith('ss') and len(w)>2: return w[:-1]
    return w

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
    def _bfs(s, g, start, neg, blk, mx=8):
        vis, q = set(), deque([(start, 0)])
        while q:
            nd, d = q.popleft()
            if d > mx: continue
            for nx in g.get(nd, set()):
                if (nd,nx) not in neg and (nd,nx) not in blk and nx not in vis:
                    vis.add(nx); q.append((nx, d+1))
        return vis
    def _compositional_depth(s, p, c):
        g, neg, blk = defaultdict(set), set(), set()
        for a, b in _ALLARB.findall(p): g[_stem(a)].add(_stem(b))
        for a, b in _NOTALLARB.findall(p): neg.add((_stem(a), _stem(b)))
        for a, b in _NOARB.findall(p): blk.add((_stem(a),_stem(b))); blk.add((_stem(b),_stem(a)))
        if not g or sum(len(v) for v in g.values()) < 2: return None
        cl = c.lower()
        cl_stems = set(_stem(w) for w in re.findall(r'\w+', cl))
        qm = _QISA.search(p) or _QARE.search(p)
        if qm:
            src, tgt = _stem(qm.group(1)), _stem(qm.group(2))
            stypes = {src}
            for a in g:
                if src == a or src in g[a]: stypes.add(a)
            for st in stypes:
                if tgt in s._bfs(g, st, neg, blk):
                    if (st, tgt) in blk or (tgt, st) in blk:
                        return 0.90 if _h(cl,'no','false','not','cannot') else 0.12
                    return 0.92 if _h(cl,'yes','true','is a','correct','therefore') else 0.10
            return 0.85 if _h(cl,'no','false','not','cannot') else 0.12
        for nd in g:
            for t in s._bfs(g, nd, neg, blk):
                if nd in cl_stems and t in cl_stems:
                    if _h(cl,'yes','true','is a','correct','therefore'): return 0.90
                    if _h(cl,'no','false','not'): return 0.10
        if re.search(r'all\s+\w+\s+are\s+\w+', cl):
            for a, b in _ALLARB.findall(c):
                sa, sb = _stem(a), _stem(b)
                if sa in g and sb in g.get(sa, set()): return 0.12
        return 0.50
    def _causal_intervention(s, p, c):
        edges = [(a.lower(),b.lower()) for pat in (_CAUSE,_ARROW) for a,b in pat.findall(p)]
        fm = _FORCE.search(p)
        if len(edges)<1 or not fm: return None
        forced, ds, front = fm.group(1).lower(), set(), {fm.group(1).lower()}
        for _ in range(10):
            nxt = set()
            for a, b in edges:
                if a in front and b not in ds: ds.add(b); nxt.add(b)
            if not nxt: break
            front = nxt
        cl = c.lower()
        for d in ds:
            if d in cl:
                if _h(cl,'affected','changes','stops','0','zero','no longer'): return 0.88
                if _h(cl,'unaffected','no effect'): return 0.15
        return 0.50
    def _temporal_age(s, p, c):
        vals = {m.group(1).lower(): float(m.group(2)) for m in _AGE_ABS.finditer(p)}
        cons = []
        for m in _AGE_REL.finditer(p):
            nm, d, dr, rf = m.group(1).lower(), float(m.group(2)), m.group(3).lower(), m.group(4).lower()
            cons.append((nm, 1.0, rf, d if dr=='older' else -d))
        for m in _AGE_MULT.finditer(p):
            nm, mw, rf = m.group(1).lower(), m.group(2).lower(), m.group(3).lower()
            mu = {'twice':2.0,'half':0.5,'triple':3.0}.get(mw)
            if mu is None: mn=_NUM.search(mw); mu=float(mn.group()) if mn else 2.0
            cons.append((nm, mu, rf, 0.0))
        if not cons and not vals: return None
        for _ in range(30):
            ch = False
            for nm, co, rf, off in cons:
                if nm not in vals and rf in vals: vals[nm]=co*vals[rf]+off; ch=True
                elif rf not in vals and nm in vals and co: vals[rf]=(vals[nm]-off)/co; ch=True
            if not ch: break
        cn = _ns(c)
        if not cn or not vals: return None
        best = min((abs(cv-av) for cv in cn for av in vals.values()), default=999)
        return 0.92 if best < 0.5 else 0.15
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
        if re.search(r'all\s+\w+\s+are\s+\w+', pl) and 'are all' in pl:
            return 0.85 if _h(cl,'no','false','not') else 0.15
        if pn and cn and any(abs(a-b)<0.01 for a in pn for b in cn): return 0.65
        return None
    def _score(s, p, c):
        for fn in (s._compositional_depth, s._causal_intervention, s._temporal_age, s._temporal_causal_order):
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
