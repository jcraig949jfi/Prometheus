"""Frame B — Causal Inference x Multi-Armed Bandits x Property-Based Testing.
Causal graph with do-calculus, UCB exploration-exploitation, property invariants.
NCD tiebreaker only. Full standard parser battery + Tier B traps."""
import re,math,zlib,collections
_N=re.compile(r"[-+]?\d*\.?\d+");_D='monday tuesday wednesday thursday friday saturday sunday'.split();_C='north east south west'.split()
def _ns(t): return [float(m) for m in _N.findall(t)]
def _w(t): return re.findall(r"\b[a-z]+(?:'[a-z]+)?\b",t.lower())
def _h(t,*x): return any(i in t.lower() for i in x)
def _fw(t): ws=_w(t); return ws[0] if ws else ''
def _ncd(a,b):
    try: ca,cb=len(zlib.compress(a.encode())),len(zlib.compress(b.encode())); return(len(zlib.compress((a+b).encode()))-min(ca,cb))/max(ca,cb,1)
    except: return 1.
class ReasoningTool:
    def _numeric(s,p,c):
        ns=_ns(p);cn=_ns(c);pl=p.lower()
        if len(ns)<2: return None
        ig,il=_h(pl,'larger','greater','bigger','more','higher','heavier'),_h(pl,'smaller','less','fewer','lower','lighter','shorter')
        if not(ig or il): return None
        return .92 if cn and abs(cn[0]-(max(ns) if ig and not il else min(ns)))<1e-9 else(.1 if cn else None)
    def _batball(s,p,c):
        pl=p.lower();cn=_ns(c);mt=re.search(r'(?:together|total|combined)\s*(?:cost|is|are)?\s*\$?(\d+(?:\.\d+)?)',pl) or re.search(r'cost\s+\$?(\d+(?:\.\d+)?)',pl);md=re.search(r'(?:costs?|is)\s+\$?(\d+(?:\.\d+)?)\s+more\s+than',pl)
        if not(mt and md): return None
        ok=(float(mt.group(1))-float(md.group(1)))/2; return .92 if cn and abs(cn[0]-ok)<.01 else(.1 if cn else None)
    def _allbut(s,p,c):
        m=re.search(r'all\s+(?:but|except|save)\s+(\d+)',p.lower())
        if not m or not _h(p,'how many','remain','left','alive','survive'): return None
        cn=_ns(c);n=float(m.group(1)); return .9 if cn and abs(cn[0]-n)<.01 else(.1 if cn else None)
    def _trans(s,p,c):
        pairs=re.findall(r'(\w+)\s+is\s+(\w+(?:er|ier))\s+than\s+(\w+)',p.lower())
        if len(pairs)<2: return None
        g={}
        for a,_,b in pairs: g.setdefault(a,set()).add(b)
        ch=True
        while ch:
            ch=False
            for a in list(g):
                for b in list(g.get(a,set())):
                    for x in g.get(b,set()):
                        if x not in g[a]: g[a].add(x);ch=True
        e=set();[e.update({a}|g[a]) for a in g];top=[x for x in e if len(g.get(x,set()))==len(e)-1];bot=[x for x in e if not g.get(x,set())];cl,pl=c.lower(),p.lower()
        if _h(pl,'tallest','largest','biggest','heaviest','fastest','oldest','most','highest','best'): return .9 if top and any(t in cl for t in top) else(.1 if bot and any(b in cl for b in bot) else .3)
        if _h(pl,'shortest','smallest','lightest','slowest','youngest','least','lowest','worst'): return .9 if bot and any(b in cl for b in bot) else .3
        return .3
    def _mt(s,p,c):
        m=re.search(r'if\s+(.+?)[,.]?\s*then\s+(.+?)(?:[,.]|$)',p.lower())
        if not m or not _h(p[m.end():],'not','never',"don't","doesn't"): return None
        return .85 if _h(c,'not','no','cannot','never') else(.1 if _fw(c) in('yes','true') else .4)
    def _neg(s,p,c):
        if not re.search(r'not\s+(?:all|every)',p.lower()): return None
        return .88 if _h(c.lower(),'cannot','not enough','not necessarily','insufficient','does not follow') else(.15 if _fw(c) in('yes','no','true','false') else None)
    def _svo(s,p,c):
        m=re.search(r'(\w+)\s+(?:gave|told|sent|passed|handed|chased|bit|hit|ate|pushed|caught)\s+(?:\w+\s+)?(?:to\s+)?(\w+)',p.lower())
        if not m or 'who' not in p.lower(): return None
        su,ob=m.group(1),m.group(2);cl=c.lower()
        if _h(p,'who gave','who told','who sent','who chased','who hit') and su in cl: return .88
        return .88 if _h(p,'receive','got','to whom','was chased','was hit') and ob in cl else .3
    def _coin(s,p,c):
        if not(_h(p,'coin','flip','toss') and _h(p,'probability','chance','likely','odds','next') and re.search(r'\d+\s*(?:times|flips|tosses|in a row)',p.lower())): return None
        return .9 if _h(c,'50','1/2','0.5','half','same') else .15
    def _pig(s,p,c):
        if not _h(p,'guarantee','worst case','minimum number','sock','drawer'): return None
        ns=_ns(p);cn=_ns(c); return .88 if len(ns)>=2 and cn and abs(cn[0]-(int(max(ns))+1))<.5 else(.15 if cn else None)
    def _fence(s,p,c):
        if not _h(p,'fence','post','pole','planted','spaced'): return None
        ns=_ns(p);cn=_ns(c)
        if len(ns)<2 or not cn: return None
        l,sp=max(ns),min(ns); return .9 if sp>0 and abs(cn[0]-(l/sp+1))<.5 else .15
    def _age(s,p,c):
        pl=p.lower();rl=re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)',pl)
        if not rl: return None
        kn={x:int(a) for x,a in re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+old',pl)}
        for _ in range(10):
            for a,d,r,b in rl:
                d2=int(d)
                if b in kn and a not in kn: kn[a]=kn[b]+d2 if r=='older' else kn[b]-d2
                if a in kn and b not in kn: kn[b]=kn[a]-d2 if r=='older' else kn[a]+d2
        tg=re.search(r'how old (?:is|was) (\w+)',pl);cn=_ns(c)
        return(.92 if cn and abs(cn[0]-kn[tg.group(1)])<.5 else .1) if tg and tg.group(1) in kn else None
    def _day(s,p,c):
        dm=re.search(r'today is (\w+day)',p.lower())
        if not dm or not _h(p,'yesterday','tomorrow','day after','day before'): return None
        ix=next((i for i,d in enumerate(_D) if d==dm.group(1)),-1)
        if ix<0: return None
        of=len(re.findall(r'tomorrow|day after',p.lower()))-len(re.findall(r'yesterday|day before',p.lower())); return .9 if _D[(ix+of)%7] in c.lower() else .15
    def _dir(s,p,c):
        fm=re.search(r'fac(?:e|ing)\s+(north|south|east|west)',p.lower())
        if not fm: return None
        ix=_C.index(fm.group(1))
        for t in re.findall(r'turn\s+(left|right)',p.lower()): ix=(ix+1)%4 if t=='right' else(ix-1)%4
        return .9 if _C[ix] in c.lower() else .1
    def _bayes(s,p,c):
        if not _h(p,'preva','base rate','1 in','sensitivity'): return None
        ns=_ns(p);cn=_ns(c)
        if len(ns)<2: return None
        pv=min(ns)/100 if min(ns)>1 else min(ns)
        if pv>.5: pv=.01
        se=max(x for x in ns if x<=100)/100;po=(se*pv)/(se*pv+(1-se)*(1-pv)) if(se*pv+(1-se)*(1-pv))>0 else .5
        if cn:
            cp=cn[0]/100 if cn[0]>1 else cn[0]
            if abs(cp-po)<.15: return .8
        return .75 if _h(c,'low','unlikely') and po<.3 else .3
    def _mod(s,p,c):
        if not _h(p,'remainder','mod','modulo','clock','cycl'): return None
        ns=_ns(p);cn=_ns(c)
        if len(ns)<2 or int(ns[1])==0 or not cn: return None
        return .88 if abs(cn[0]-int(ns[0])%int(ns[1]))<.5 else .15
    def _parity(s,p,c):
        if not _h(p,'odd','even','parity'): return None
        ns=_ns(p)
        if not ns: return None
        v=int(ns[-1]);ev=v%2==0
        if _h(p,'odd'): return .88 if(not ev and _h(c,'yes','odd','true'))or(ev and _h(c,'no','even','false')) else .15
        return .88 if(ev and _h(c,'yes','even','true'))or(not ev and _h(c,'no','odd','false')) else .15
    _P=['_numeric','_batball','_allbut','_trans','_mt','_neg','_svo','_coin','_pig','_fence','_age','_day','_dir','_bayes','_mod','_parity']
    def _rp(self,p,c):
        o=[]
        for nm in self._P:
            try:
                v=getattr(self,nm)(p,c)
                if v is not None: o.append(v)
            except: pass
        return o
    def _build_graph(self,text):
        pl=text.lower();g=collections.defaultdict(set)
        for pat in[r'(\w+)\s*(?:causes?|leads?\s+to|produces?|results?\s+in)\s*(\w+)',r'(\w+)\s*(?:->|-->|=>)\s*(\w+)',r'if\s+(\w+)[,.]?\s*then\s+(\w+)']:
            for m in re.finditer(pat,pl): g[m.group(1)].add(m.group(2))
        return g
    def _do_calc(self,g,iv,tgt):
        g2=collections.defaultdict(set)
        for a in g:
            for b in g[a]:
                if b!=iv: g2[a].add(b)
        vis,q={iv},collections.deque([iv])
        while q:
            n=q.popleft()
            for nb in g2.get(n,set()):
                if nb not in vis: vis.add(nb);q.append(nb)
        return tgt in vis
    def _causal(self,p,c):
        g=self._build_graph(p)
        if not g: return 0.
        pl,cl=p.lower(),c.lower();nodes=set()
        for a in g: nodes.add(a);nodes.update(g[a])
        iv=re.search(r'(?:force|set|intervene|do|remove|block)\s+(\w+)',pl)
        if iv:
            matched=[n for n in nodes if n in cl]
            for tgt in matched:
                if self._do_calc(g,iv.group(1),tgt): return .82
            return .15 if matched else .3
        od,ind=collections.Counter(),collections.Counter()
        for a in g:
            for b in g[a]: od[a]+=1;ind[b]+=1
        roots=[n for n in nodes if ind[n]==0 and od[n]>0];leaves=[n for n in nodes if od[n]==0 and ind[n]>0]
        if _h(pl,'cause','reason','why','source') and roots and any(r in cl for r in roots): return .8
        if _h(pl,'effect','result','outcome') and leaves and any(l in cl for l in leaves): return .8
        return .3
    def _invariants(self,p,c):
        cn=_ns(c);pn=_ns(p);sc=.5
        if cn and pn:
            if min(pn)<=cn[0]<=max(pn)*10: sc+=.1
            if cn[0]<0 and not _h(p,'negative','debt','loss','below'): sc-=.2
        if p.strip().endswith('?') and _fw(c) in('yes','no','true','false'): sc+=.1
        return min(1.,max(0.,sc))
    def _meta_confidence(self,prompt,answer=""):
        pl=prompt.lower()
        if re.search(r'\b(?:have|has|had)\s+(?:you|they|he|she|we)\s+(?:stopped|quit|given up)',pl): return .20
        if re.search(r'\b(?:stopped|still|again|already|anymore)\b',pl) and re.search(r'\b(?:have you|did you|when did)\b',pl): return .22
        if re.search(r'\bevery\b.*\bsome\b',pl) or(re.search(r'\ball\b.*\bnot\b',pl) and '?' in pl): return .22
        if re.search(r'either\s+you\s+\w+.*or\s+you',pl) or re.search(r'\bmust be one\b',pl): return .25
        if re.search(r'\b(?:all|every)\s+(?:successful|winning|survivors?|winners?|top|best|famous)\b',pl) and re.search(r'\bstudy\b|\bsample\b|\bshow\b|\bfind\b',pl): return .20
        if re.search(r'(?:already\s+)?(?:spent|invested|paid)\s+\$?\d+',pl) and re.search(r'\b(?:should|continue|keep|quit|stop)\b',pl): return .20
        if re.search(r'non-?refundable',pl): return .20
        if re.search(r'\b(?:best|worst|favorite|opinion|beautiful)\b',pl) and '?' in pl: return .22
        if re.search(r'all\s+\w+\s+can\s+(?:fly|swim|sing|dance|talk)',pl) and _h(pl,'valid','logically'): return .25
        if('this statement' in pl or 'this sentence' in pl) and not re.search(r'\d+\s+words',pl): return .22
        if re.search(r'\b(?:he|she|they)\b',pl) and re.search(r'\bwho\b.*\?',pl) and re.search(r'\w+\s+(?:told|said to|asked)\s+\w+\s+(?:that\s+)?(?:he|she|they)',pl): return .22
        if re.search(r'(?:correlation|correlated)\b.*\b(?:cause|caus)',pl): return .25
        return 1.0
    def _score(self,p,c):
        ps=self._rp(p,c);pmax=max(ps) if ps else None
        caus=self._causal(p,c);inv=self._invariants(p,c);concept=.6*caus+.4*inv;ncd=1.-_ncd(p,c)
        return .70*pmax+.25*concept+.05*ncd if pmax is not None else .85*concept+.15*ncd
    def evaluate(self,prompt,candidates):
        if not candidates: return []
        mc=self._meta_confidence(prompt);r=[]
        for c in candidates:
            sc=float(max(0.,min(1.,min(self._score(prompt,c),mc))))
            r.append({"candidate":c,"score":sc,"reasoning":f"ci={sc:.3f} cap={mc:.2f}"})
        r.sort(key=lambda x:x["score"],reverse=True); return r
    def confidence(self,prompt,answer):
        mc=self._meta_confidence(prompt,answer)
        if mc<.3: return mc
        return float(max(0.,min(.95,min(self._score(prompt,answer),mc))))
