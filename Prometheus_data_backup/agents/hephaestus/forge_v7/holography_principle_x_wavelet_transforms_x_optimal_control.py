"""Frame C — Holography Principle x Wavelet Transforms x Optimal Control. Holographic boundary
encoding, Haar wavelet multi-resolution analysis, LQR-like optimal control scoring."""
import re, math, zlib, numpy as np
_N=re.compile(r"[-+]?\d*\.?\d+")
def _ns(t): return [float(m) for m in _N.findall(t)]
def _w(t): return re.findall(r"\b[a-z]+(?:'[a-z]+)?\b",t.lower())
def _h(t,*x): return any(i in t.lower() for i in x)
def _af(t): return (_w(t) or [""])[0] in ("yes","true","correct","right")
def _dn(t): return (_w(t) or [""])[0] in ("no","false","incorrect","wrong","not")
def _ncd(p,c):
    try: b1,b2=p.encode(),c.encode(); c1,c2,c12=len(zlib.compress(b1)),len(zlib.compress(b2)),len(zlib.compress(b1+b2)); return (c12-min(c1,c2))/max(c1,c2,1)
    except: return 1.
class ReasoningTool:
    def __init__(s):
        np.random.seed(91); s._bp=np.random.randn(16,64); s._bp/=np.linalg.norm(s._bp,axis=1,keepdims=True)+1e-9
    def _run(s,fns,p,c):
        t,n=0.,0
        for f in fns:
            try:
                sc,m=f(p,c)
                if m: t+=sc; n+=1
            except: pass
        return (t/n if n else 0.),n
    def _embed(s,t):
        v=np.zeros(64)
        for i,ch in enumerate(t): v[ord(ch)%64]+=1./(i+1)
        v/=np.linalg.norm(v)+1e-9; return v
    def _holo(s,p,c):
        pb,cb=s._bp@s._embed(p),s._bp@s._embed(c)
        pb/=np.linalg.norm(pb)+1e-9; cb/=np.linalg.norm(cb)+1e-9
        sim=np.dot(pb,cb)
        pe=-np.sum(np.abs(pb)*np.log(np.abs(pb)+1e-9)); ce=-np.sum(np.abs(cb)*np.log(np.abs(cb)+1e-9))
        return 0.6*sim+0.4*min(ce,pe)/(max(ce,pe)+1e-9)
    def _wavelet(s,p,c):
        cs=np.array([ord(ch)%128 for ch in (p+' '+c)[:128]],dtype=float); cs/=np.max(np.abs(cs))+1e-9
        n=len(cs)-(len(cs)%2); s_=cs[:n]
        a1,d1=(s_[::2]+s_[1::2])/1.414,(s_[::2]-s_[1::2])/1.414
        n2=len(a1)-(len(a1)%2); a1_=a1[:n2]
        a2,d2=(a1_[::2]+a1_[1::2])/1.414,(a1_[::2]-a1_[1::2])/1.414
        ef,em,ec=np.sum(d1**2)/(len(d1)+1e-9),np.sum(d2**2)/(len(d2)+1e-9),np.sum(a2**2)/(len(a2)+1e-9)
        tot=ef+em+ec+1e-9; overlap=len(set(_w(p))&set(_w(c)))/(len(set(_w(p))|set(_w(c)))+1e-9)
        return 0.4*overlap+0.3*(1.-np.std([ef/tot,em/tot,ec/tot]))+0.3*(ec/tot)
    def _ctrl(s,p,c):
        err=s._embed(c)-s._embed(p); J=0.5*np.dot(err,err)+0.1*max(0.,len(c.split())/(len(p.split())+1e-9)-1.)**2
        return 1./(1.+math.exp(3.*(J-0.5)))
    def _numeric(s,p,c):
        ns=_ns(p); pl,cl=p.lower(),c.lower()
        if len(ns)<2: return 0.,False
        ig,il=_h(pl,"larger","greater","bigger","more","higher","heavier"),_h(pl,"smaller","less","fewer","lower","lighter","shorter")
        if not(ig or il): return 0.,False
        a,b=ns[0],ns[1]; cn=_ns(c)
        if ig and not il: ok=a>b
        elif il and not ig: ok=a<b
        else: v=max(a,b) if ig else min(a,b); return (1. if cn and abs(cn[0]-v)<1e-9 else 0.),True
        if _af(cl): return (1. if ok else -1.),True
        if _dn(cl): return (1. if not ok else -1.),True
        if cn:
            v=max(a,b) if ig else min(a,b)
            if abs(cn[0]-v)<1e-9: return 1.,True
            if abs(cn[0]-(a+b-v))<1e-9: return -1.,True
        return 0.,True
    def _trans(s,p,c):
        pairs=re.findall(r"(\w+)\s+is\s+(\w+(?:er|ier))\s+than\s+(\w+)",p.lower())
        if len(pairs)<2: return 0.,False
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
        if _h(pl,"tallest","largest","biggest","heaviest","fastest","oldest","most","highest","best"):
            if top and any(t in cl for t in top): return 1.,True
            if bot and any(b in cl for b in bot): return -1.,True
        if _h(pl,"shortest","smallest","lightest","slowest","youngest","least","lowest","worst"):
            if bot and any(b in cl for b in bot): return 1.,True
        return 0.,True
    def _mt(s,p,c):
        m=re.search(r"if\s+(.+?)[,.]?\s*then\s+(.+?)(?:[,.]|$)",p.lower())
        if not m: return 0.,False
        cw=set(_w(m.group(2))); rw=_w(p.lower()[m.end():])
        if not any(rw[i] in("not","no","never","doesn","didn") and set(rw[i:i+5])&cw for i in range(len(rw))) and not _h(p.lower()[m.end():],"not","never"): return 0.,False
        if _dn(c) or _h(c.lower(),"not","cannot"): return 1.,True
        return (-1.,True) if _af(c) else (0.,True)
    def _bb(s,p,c):
        pl=p.lower(); mt=re.search(r"(?:together|total|combined)\s*(?:cost|is|are)?\s*\$?([\d.]+)",pl) or re.search(r"cost\s+\$?([\d.]+)",pl)
        md=re.search(r"(?:costs?|is)\s+\$?([\d.]+)\s+more\s+than",pl)
        if not(mt and md): return 0.,False
        ok=(float(mt.group(1))-float(md.group(1)))/2; cn=_ns(c)
        return ((1. if abs(cn[0]-ok)<.01 else -1.),True) if cn else (0.,True)
    def _abn(s,p,c):
        m=re.search(r"all\s+(?:but|except|save)\s+(\d+)",p.lower())
        if not m or not _h(p,"how many","remain","left","alive","survive"): return 0.,False
        cn=_ns(c); n=float(m.group(1))
        return ((1. if abs(cn[0]-n)<.01 else -.8),True) if cn else (0.,True)
    def _neg(s,p,c):
        if not re.search(r"not\s+(?:all|every|each)",p.lower()) or not _h(p,"?","can we","does","is it","conclude","mean"): return 0.,False
        if _h(c.lower(),"cannot","not enough","not necessarily","insufficient","does not follow"): return 1.,True
        return (-1.,True) if _af(c) or _h(c.lower(),"none","all are") else (0.,True)
    def _svo(s,p,c):
        m=re.search(r"(?:the\s+)?(\w+)\s+(?:\w+ed|\w+s|ate|hit|saw|bit|chased|caught|pushed)\s+(?:the\s+)?(\w+)",p.lower())
        if not m or not re.search(r"who\s+(?:was|were|got)\s+\w+(?:ed|en)",p.lower()): return 0.,False
        su,ob=m.group(1).lower(),m.group(2).lower(); cl=c.lower()
        if ob in cl and su not in cl: return 1.,True
        return (-1.,True) if su in cl and ob not in cl else (0.,True)
    def _br(s,p,c):
        pl=p.lower()
        if not _h(pl,"coin","flip","toss","dice","die","roll") or not(re.search(r"\d+\s*(?:times|flips|tosses|rolls|in a row)",pl) and _h(pl,"probability","chance","likely","odds","next")): return 0.,False
        if _h(pl,"coin"):
            if _h(c.lower(),"50","1/2","half","0.5","same"): return 1.,True
            if _h(c.lower(),"higher","lower","more likely","less likely"): return -1.,True
        return 0.,True
    def _temp(s,p,c):
        pl=p.lower(); am=re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)',pl)
        if am and 'how old' in pl:
            kn={nm:int(a) for nm,a,_,_ in re.findall(r'(\w+)\s+is\s+(\d+)(?!\s+years)',pl)}
            for a,d,r,b in am:
                for _ in range(5):
                    if a in kn and b not in kn: kn[b]=kn[a]+(-int(d) if r=='older' else int(d))
                    if b in kn and a not in kn: kn[a]=kn[b]+(int(d) if r=='older' else -int(d))
            tm=re.search(r'how old is (\w+)',pl)
            if tm and tm.group(1) in kn: return (1. if str(kn[tm.group(1)]) in c else -.5),True
        if re.search(r'face\s+(north|south|east|west)',pl) and 'turn' in pl:
            d=['north','east','south','west']; fm=re.search(r'face\s+(north|south|east|west)',pl)
            if fm:
                i=d.index(fm.group(1))
                for t in re.findall(r'turn\s+(left|right)',pl): i=(i+(1 if t=='right' else -1))%4
                return (1. if d[i] in c.lower() else -.5),True
        return 0.,False
    def _causal(s,p,c):
        ch=re.findall(r'(\w+)\s*(?:causes|leads to|->)\s*(\w+)',p.lower())
        if not ch: return 0.,False
        fm=re.search(r'(?:force|set|remove)\s+(\w+)',p.lower())
        if fm:
            ds,fr=set(),{fm.group(1).lower()}
            while fr:
                nf=set()
                for a,b in ch:
                    if a.lower() in fr: ds.add(b.lower()); nf.add(b.lower())
                fr=nf-ds
            if any(d in c.lower() for d in ds): return 1.,True
        return 0.,True
    def _tom(s,p,c):
        pl=p.lower()
        if re.search(r"doesn.t know",pl) and re.search(r'what does \w+ (?:think|believe)',pl) and _h(pl,'rigged','loaded','biased'):
            return (1. if _h(c.lower(),'50','fair','equal') else -.5),True
        if _h(pl,'opposite','contrary') and re.search(r'should \w+ say',pl):
            wm=re.search(r'wants? \w+ to (?:go )?(left|right|stay|leave)',pl)
            if wm: return (1. if {'left':'right','right':'left','stay':'leave','leave':'stay'}.get(wm.group(1),'') in c.lower() else -.5),True
        return 0.,False
    def _fp(s,p,c):
        if not _h(p,"fence","post","pole","planted","spaced"): return 0.,False
        ns=_ns(p)
        if len(ns)<2: return 0.,False
        l,sp=max(ns[0],ns[1]),min(ns[0],ns[1])
        if sp<=0: return 0.,False
        ok=int(l/sp)+1; cn=_ns(c)
        return ((1. if abs(cn[0]-ok)<.5 else -1. if abs(cn[0]-(ok-1))<.5 else 0.),True) if cn else (0.,True)
    def _mod(s,p,c):
        if not _h(p,"remainder","mod","modulo","clock","cycl"): return 0.,False
        ns=_ns(p)
        if len(ns)<2 or int(ns[1])==0: return 0.,False
        cn=_ns(c)
        return ((1. if abs(cn[0]-int(ns[0])%int(ns[1]))<.5 else -.5),True) if cn else (0.,True)
    def _s1(s,p,c): return s._run([s._numeric,s._trans,s._mt,s._bb,s._abn,s._neg,s._svo,s._br,s._temp,s._causal,s._tom,s._fp,s._mod],p,c)
    def _compose(s,p,c):
        s1,n1=s._s1(p,c); ho,wv,ct=s._holo(p,c),s._wavelet(p,c),s._ctrl(p,c)
        bl=0.55*s1+0.15*ho+0.15*wv+0.15*ct if n1>0 else 0.30*ho+0.35*wv+0.35*ct
        return max(0.,min(1.,bl)),n1,ct
    def _meta_confidence(s,prompt,answer=""):
        pl=prompt.lower()
        if re.search(r'\b(stopped|quit|ceased)\b.*\b(have you|did you)\b',pl): return .25
        if re.search(r'\b(best|worst|favorite|opinion|beautiful)\b',pl): return .30
        if re.search(r'\bwhy\s+(did|does|is)\b',pl) and not _h(pl,"because","since"): return .35
        if "who" in pl and re.search(r'\b(he|she|they)\b',pl) and _h(pl,"told","said"): return .30
        if len(_ns(prompt))+len(re.findall(r'\b(?:if|all|not|every)\b',pl))==0 and len(prompt.split())<8: return .20
        return 1.
    def evaluate(s,prompt,candidates):
        if not candidates: return []
        mc=s._meta_confidence(prompt); r=[]
        for c in candidates:
            sc,n1,ct=s._compose(prompt,c); sc=float(max(0.,min(1.,min(sc,mc))))
            r.append({"candidate":c,"score":sc,"reasoning":f"S1={n1} ctrl={ct:.2f} cap={mc:.2f}"})
        r.sort(key=lambda x:x["score"],reverse=True); return r
    def confidence(s,prompt,answer):
        mc=s._meta_confidence(prompt,answer)
        if mc<.3: return mc
        sc,_,_=s._compose(prompt,answer); return float(max(0.,min(.95,min(sc,mc))))
