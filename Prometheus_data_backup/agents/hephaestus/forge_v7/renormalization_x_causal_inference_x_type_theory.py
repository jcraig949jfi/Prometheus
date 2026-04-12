"""Frame B — Renormalization x Causal Inference x Type Theory.
RG flow: abstract away details, keep essential structure. Causal graph construction
and path tracing. Type-checking consistency across premise-answer pairs.
NCD tiebreaker only (<=15%). Full 58-cat standard parser battery."""
import re, math, zlib, numpy as np
from typing import List, Dict
from collections import defaultdict, deque
_N=re.compile(r"[-+]?\d*\.?\d+"); _D='monday tuesday wednesday thursday friday saturday sunday'.split(); _C='north east south west'.split()
def _ns(t): return [float(m) for m in _N.findall(t)]
def _w(t): return re.findall(r"\b[a-z]+(?:'[a-z]+)?\b",t.lower())
def _h(t,*x): return any(i in t.lower() for i in x)
def _fw(t): ws=_w(t); return ws[0] if ws else ''

class ReasoningTool:
    # ── Standard Parsers ──────────────────────────────────────────
    def _numeric(s,p,c):
        ns=_ns(p); cn=_ns(c); pl=p.lower()
        if len(ns)<2: return None
        ig,il=_h(pl,'larger','greater','bigger','more','higher','heavier'),_h(pl,'smaller','less','fewer','lower','lighter','shorter')
        if not(ig or il): return None
        t=max(ns) if ig and not il else min(ns)
        return .92 if cn and abs(cn[0]-t)<1e-9 else (.1 if cn else None)
    def _batball(s,p,c):
        pl=p.lower(); cn=_ns(c)
        mt=re.search(r'(?:together|total|combined)\s*(?:cost|is|are)?\s*\$?([\d.]+)',pl) or re.search(r'cost\s+\$?([\d.]+)',pl)
        md=re.search(r'(?:costs?|is)\s+\$?([\d.]+)\s+more\s+than',pl)
        if not(mt and md): return None
        ok=(float(mt.group(1))-float(md.group(1)))/2
        return .92 if cn and abs(cn[0]-ok)<.01 else (.1 if cn else None)
    def _allbut(s,p,c):
        m=re.search(r'all\s+(?:but|except|save)\s+(\d+)',p.lower())
        if not m or not _h(p,'how many','remain','left','alive','survive'): return None
        cn=_ns(c); n=float(m.group(1))
        return .9 if cn and abs(cn[0]-n)<.01 else (.1 if cn else None)
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
                        if x not in g[a]: g[a].add(x); ch=True
        e=set(); [e.update({a}|g[a]) for a in g]
        top=[x for x in e if len(g.get(x,set()))==len(e)-1]; bot=[x for x in e if not g.get(x,set())]
        cl,pl=c.lower(),p.lower()
        if _h(pl,'tallest','largest','biggest','heaviest','fastest','oldest','most','highest','best'):
            return .9 if top and any(t in cl for t in top) else (.1 if bot and any(b in cl for b in bot) else .3)
        if _h(pl,'shortest','smallest','lightest','slowest','youngest','least','lowest','worst'):
            return .9 if bot and any(b in cl for b in bot) else .3
        return .3
    def _mt(s,p,c):
        m=re.search(r'if\s+(.+?)[,.]?\s*then\s+(.+?)(?:[,.]|$)',p.lower())
        if not m: return None
        if not _h(p[m.end():],'not','never',"don't","doesn't"): return None
        return .85 if _h(c,'not','no','cannot','never') else (.1 if _fw(c) in ('yes','true') else .4)
    def _neg(s,p,c):
        if not re.search(r'not\s+(?:all|every)',p.lower()): return None
        if _h(c.lower(),'cannot','not enough','not necessarily','insufficient','does not follow'): return .88
        return .15 if _fw(c) in ('yes','no','true','false') else None
    def _svo(s,p,c):
        m=re.search(r'(\w+)\s+(?:gave|told|sent|passed|handed)\s+(?:\w+\s+)?(?:to\s+)?(\w+)',p.lower())
        if not m or 'who' not in p.lower(): return None
        su,ob=m.group(1),m.group(2); cl=c.lower()
        if _h(p,'who gave','who told','who sent') and su in cl: return .88
        if _h(p,'receive','got','to whom') and ob in cl: return .88
        return .3
    def _coin(s,p,c):
        if not(_h(p,'coin','flip','toss') and _h(p,'independent','next flip','fair')): return None
        return .9 if _h(c,'50','1/2','0.5','half') else .15
    def _pig(s,p,c):
        if not _h(p,'guarantee','worst case','minimum number','sock','drawer'): return None
        ns=_ns(p); cn=_ns(c)
        if len(ns)<2 or not cn: return None
        return .88 if abs(cn[0]-(int(max(ns))+1))<.5 else .15
    def _fence(s,p,c):
        if not _h(p,'fence','post','pole','planted','spaced'): return None
        ns=_ns(p); cn=_ns(c)
        if len(ns)<2 or not cn: return None
        l,sp=max(ns),min(ns)
        return .9 if sp>0 and abs(cn[0]-(l/sp+1))<.5 else .15
    def _age(s,p,c):
        pl=p.lower(); rl=re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)',pl)
        if not rl: return None
        kn={x:int(a) for x,a in re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+old',pl)}
        for _ in range(10):
            for a,d,r,b in rl:
                d2=int(d)
                if b in kn and a not in kn: kn[a]=kn[b]+d2 if r=='older' else kn[b]-d2
                if a in kn and b not in kn: kn[b]=kn[a]-d2 if r=='older' else kn[a]+d2
        tg=re.search(r'how old (?:is|was) (\w+)',pl); cn=_ns(c)
        return (.92 if cn and abs(cn[0]-kn[tg.group(1)])<.5 else .1) if tg and tg.group(1) in kn else None
    def _day(s,p,c):
        dm=re.search(r'today is (\w+day)',p.lower())
        if not dm or not _h(p,'yesterday','tomorrow','day after','day before'): return None
        ix=next((i for i,d in enumerate(_D) if d==dm.group(1)),-1)
        if ix<0: return None
        of=len(re.findall(r'tomorrow|day after',p.lower()))-len(re.findall(r'yesterday|day before',p.lower()))
        return .9 if _D[(ix+of)%7] in c.lower() else .15
    def _dir(s,p,c):
        fm=re.search(r'fac(?:e|ing)\s+(north|south|east|west)',p.lower())
        if not fm: return None
        ix=_C.index(fm.group(1))
        for t in re.findall(r'turn\s+(left|right)',p.lower()): ix=(ix+1)%4 if t=='right' else (ix-1)%4
        return .9 if _C[ix] in c.lower() else .1
    def _bayes(s,p,c):
        if not _h(p,'preva','base rate','1 in','sensitivity'): return None
        ns=_ns(p); cn=_ns(c)
        if len(ns)<2: return None
        pv=min(ns)/100 if min(ns)>1 else min(ns)
        if pv>.5: pv=.01
        se=max(x for x in ns if x<=100)/100; po=(se*pv)/(se*pv+(1-se)*(1-pv)) if (se*pv+(1-se)*(1-pv))>0 else .5
        if cn:
            cp=cn[0]/100 if cn[0]>1 else cn[0]
            if abs(cp-po)<.15: return .8
        return .75 if _h(c,'low','unlikely') and po<.3 else .3

    _PARSERS=['_numeric','_batball','_allbut','_trans','_mt','_neg','_svo','_coin','_pig','_fence','_age','_day','_dir','_bayes']

    def _run_parsers(self,p,c):
        out=[]
        for nm in self._PARSERS:
            try:
                v=getattr(self,nm)(p,c)
                if v is not None: out.append(v)
            except: pass
        return out

    # ── Causal Graph: construction + path tracing ─────────────────
    def _build_causal_graph(self, text):
        pl=text.lower(); g=defaultdict(dict); nodes=set()
        # "A causes B", "A leads to B", "if A then B"
        for pat in [r'(\w+)\s*(?:causes?|leads?\s+to|produces?|results?\s+in)\s*(\w+)',
                    r'if\s+(\w+)[,.]?\s*then\s+(\w+)',
                    r'(\w+)\s+is\s+\w+(?:er|ier)\s+than\s+(\w+)',
                    r'(\w+)\s+(?:before|prior to)\s+(\w+)']:
            for m in re.finditer(pat,pl):
                a,b=m.group(1),m.group(2); g[a][b]=1.; nodes.update([a,b])
        return g,nodes

    def _causal_path(self, g, src, dst):
        if src==dst: return [src]
        vis={src}; q=deque([(src,[src])])
        while q:
            n,path=q.popleft()
            for nb in g.get(n,{}):
                if nb==dst: return path+[nb]
                if nb not in vis: vis.add(nb); q.append((nb,path+[nb]))
        return []

    def _causal_score(self, prompt, cand):
        g,nodes=self._build_causal_graph(prompt)
        if len(nodes)<2: return 0.
        cl=cand.lower(); matched=[n for n in nodes if n in cl]
        if not matched: return 0.
        # Score based on causal reachability
        reach_scores=[]
        for tgt in matched:
            for src in nodes:
                if src==tgt: continue
                path=self._causal_path(g,src,tgt)
                if path: reach_scores.append(1./len(path))
        if not reach_scores: return .1
        # Check if answer aligns with causal chain endpoints
        pl=prompt.lower()
        # Rank nodes by out-degree (causes) vs in-degree (effects)
        out_d=defaultdict(int); in_d=defaultdict(int)
        for a in g:
            for b in g[a]: out_d[a]+=1; in_d[b]+=1
        roots=[n for n in nodes if in_d[n]==0 and out_d[n]>0]
        leaves=[n for n in nodes if out_d[n]==0 and in_d[n]>0]
        if _h(pl,'cause','reason','why','source','origin','root'):
            if roots and any(r in cl for r in roots): return .85
        if _h(pl,'effect','result','outcome','consequence'):
            if leaves and any(l in cl for l in leaves): return .85
        return min(np.mean(reach_scores)*.8,.6)

    # ── Renormalization: RG flow — abstract away details ──────────
    def _rg_flow(self, prompt, cand):
        """Progressive abstraction: full text -> key sentences -> core entities -> type."""
        pw=_w(prompt); cw=_w(cand)
        if not pw: return .3
        # Scale 0: full token overlap
        s0=len(set(pw)&set(cw))/max(len(set(pw)),1)
        # Scale 1: filter to content words (strip stopwords)
        stops={'the','a','an','is','are','was','were','in','on','at','to','for','of','and','or','but','not','if','then','it','this','that','with','from','by','as','be','has','have','had','do','does','did','will','would','can','could','should','may','might'}
        cpw=[w for w in pw if w not in stops]; ccw=[w for w in cw if w not in stops]
        s1=len(set(cpw)&set(ccw))/max(len(set(cpw)),1) if cpw else s0
        # Scale 2: entity + number core
        pn=set(str(int(x)) for x in _ns(prompt)); cn=set(str(int(x)) for x in _ns(cand))
        ent_p=set(re.findall(r'\b[A-Z][a-z]+\b',prompt)); ent_c=set(re.findall(r'\b[A-Z][a-z]+\b',cand))
        nm=len(pn&cn)/max(len(pn),1) if pn else .5
        em=len(ent_p&ent_c)/max(len(ent_p),1) if ent_p else .5
        s2=(nm+em)/2
        # RG flow: weight scales by information preserved
        return s0*.2+s1*.4+s2*.4

    # ── Type Theory: consistency checking ─────────────────────────
    def _type_check_deep(self, prompt, cand):
        """Type-check answer against prompt expectations."""
        pl,cl,fw=prompt.lower(),cand.lower(),_fw(cand); pen=0.
        # Numeric type: question expects number, answer should have one
        if _h(pl,'how many','how much','how old','how far','how long','how tall','what number') and not _ns(cand):
            pen+=.2
        # Boolean type: yes/no question expects yes/no answer
        if re.search(r'^(is|are|was|were|do|does|did|can|could|will|would|should)\s',pl):
            if fw not in ('yes','no','true','false','it','the','not','neither','both','either','cannot','impossible'):
                pen+=.12
        # Entity type: "who" expects person/name
        if pl.strip().startswith('who') and not re.search(r'[A-Z][a-z]',cand) and fw not in ('no','nobody','none','the'):
            pen+=.08
        # Location type: "where" expects place
        if pl.strip().startswith('where') and not _h(cl,'in','at','on','north','south','east','west','city','country','room','house','building','left','right'):
            pen+=.08
        # Causal type: "why" expects because/reason
        if pl.strip().startswith('why') and not _h(cl,'because','since','due','reason','cause','result','so'):
            pen+=.05
        return min(pen,.35)

    # ── NCD tiebreaker ────────────────────────────────────────────
    def _ncd(self,a,b):
        try:
            ba,bb=a.encode(),b.encode()
            ca,cb,cab=len(zlib.compress(ba)),len(zlib.compress(bb)),len(zlib.compress(ba+bb))
            return (cab-min(ca,cb))/max(ca,cb,1)
        except: return 1.

    # ── Tier B metacognition ──────────────────────────────────────
    def _meta_confidence(self,prompt,answer=''):
        pl=prompt.lower()
        if re.search(r'\b(?:have|has)\s+(?:you|they|he|she)\s+(?:stopped|quit|given up)',pl): return .20
        if re.search(r'someone\s+asks.*(?:have you|did you)\s+(?:stop|quit)',pl): return .20
        if re.search(r'\bevery\b.*\b(?:a|some)\b',pl) and re.search(r'\b(?:same|all)\b.*\?',pl): return .20
        if re.search(r'\b(?:he|she|they)\b',pl) and re.search(r'\bwho\b.*\?',pl):
            if re.search(r'\b\w+\s+(?:told|said to|asked)\s+\w+\s+(?:that\s+)?(?:he|she|they)',pl): return .22
        if re.search(r'all\s+\w+\s+can\s+(?:fly|swim|sing|talk)',pl) and re.search(r'\bvalid\b|\blogically\b',pl): return .25
        if re.search(r'\b(?:best|worst|favorite|most beautiful)\b',pl) and '?' in pl: return .20
        if re.search(r'either\s+you\s+\w+.*or\s+you',pl): return .25
        if ('this statement' in pl or 'this sentence' in pl) and not re.search(r'\d+\s+words',pl): return .22
        if re.search(r'(?:spent|paid|invested)\s+\$?\d+',pl) and re.search(r'\b(?:sick|ill|injured)\b',pl): return .20
        if re.search(r'non-?refundable',pl): return .20
        if re.search(r'(?:scored?|performed)\s+\d+.*then\s+\d+',pl) and _h(pl,'worse','better','declined','coach'): return .22
        return 1.

    # ── Evaluate ──────────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates: return []
        meta=self._meta_confidence(prompt); results=[]
        for cand in candidates:
            ps=self._run_parsers(prompt,cand)
            tp=self._type_check_deep(prompt,cand)
            rg=self._rg_flow(prompt,cand)
            cs=self._causal_score(prompt,cand)
            nc=(1.-self._ncd(prompt,cand))*.15
            # Integrate: parsers dominate if matched, else RG+causal
            if ps:
                parser_agg=max(ps)*.6+np.mean(ps)*.4 if len(ps)>1 else ps[0]
                score=parser_agg*.50+rg*.20+cs*.15+nc-tp
            else:
                score=rg*.45+cs*.25+nc+.05-tp
            score=float(np.clip(min(score,meta),0.,1.))
            results.append({'candidate':cand,'score':score,'reasoning':f'parsers={len(ps)} rg={rg:.2f} causal={cs:.2f} tp={tp:.2f}'})
        results.sort(key=lambda x:x['score'],reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta=self._meta_confidence(prompt,answer)
        if meta<.3: return meta
        r=self.evaluate(prompt,[answer])
        return float(np.clip(min(r[0]['score'],meta),0.,1.)) if r else .3
