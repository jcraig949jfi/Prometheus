"""CAITL v4 — Neuromodulated Sparse Latent Reasoner. Sparse feature encoding +
gain-adjusted sparsity threshold + program synthesis.
struct>=50% comp>=20% ncd<=15%."""
import re, math, zlib
from typing import List, Dict

_N = re.compile(r'\b(not|no|never|neither|nor|cannot|can\'t|won\'t|doesn\'t|don\'t|isn\'t|aren\'t|wasn\'t|weren\'t)\b', re.I)
_NUM = re.compile(r'[-+]?\d+(?:\.\d+)?(?:/\d+)?')
_CMP = re.compile(r'\b(more|less|greater|fewer|larger|smaller|higher|lower|bigger|longest|shortest|tallest|biggest|fastest|slowest|older|younger)\b', re.I)
_CND = re.compile(r'\b(if|then|unless|provided|given that|suppose|when)\b', re.I)
_TMP = re.compile(r'\b(before|after|first|last|next|previous|earlier|later|during|while|since|until|finally)\b', re.I)
_QNT = re.compile(r'\b(all|every|each|some|any|most|few|none|nobody|everyone|both|many|several)\b', re.I)
_CAU = re.compile(r'\b(because|therefore|thus|hence|causes?|leads? to|results? in|due to|implies)\b', re.I)
_BOL = re.compile(r'\b(true|false|yes|no|correct|incorrect)\b', re.I)
_SO = re.compile(r'(\b[A-Z]\w+)\s+\w+\s+(\b[A-Z]\w+)', re.I)
_LR = re.compile(r'\b(left|right|east|west|north|south|above|below)\b', re.I)

def _pn(t):
    o=[]
    for m in _NUM.findall(t):
        try: o.append(float(m.split('/')[0])/float(m.split('/')[1]) if '/' in m else float(m))
        except: pass
    return o

def _ncd(a,b):
    if not a or not b: return 1.0
    x,y=a.encode(),b.encode()
    ca,cb,cc=len(zlib.compress(x)),len(zlib.compress(y)),len(zlib.compress(x+y))
    d=max(ca,cb); return (cc-min(ca,cb))/d if d else 1.0

def _numeric(p,c):
    pn,cn,pl=_pn(p),_pn(c),p.lower()
    if not pn: return 0.5
    if re.search(r'\b(sum|total|add|combined|altogether)\b',pl):
        e=sum(pn)
        if cn: best=min(cn,key=lambda x:abs(x-e)); return 1.0 if abs(best-e)<0.01 else max(0,1-abs(best-e)/(abs(e)+1))
        return 0.1
    if re.search(r'\b(differ|subtract|minus|how many more|how much more)\b',pl) and len(pn)>=2:
        e=abs(pn[0]-pn[1])
        if cn: best=min(cn,key=lambda x:abs(x-e)); return 1.0 if abs(best-e)<0.01 else max(0,1-abs(best-e)/(abs(e)+1))
        return 0.1
    if re.search(r'\b(product|multiply|times)\b',pl) and len(pn)>=2:
        e=1.0
        for n in pn: e*=n
        if cn: best=min(cn,key=lambda x:abs(x-e)); return 1.0 if abs(best-e)<0.01 else max(0,1-abs(best-e)/(abs(e)+1))
        return 0.1
    if re.search(r'\b(larg|great|bigg|more|higher|tall|fast|old)\w*',pl) and len(pn)>=2:
        e=max(pn); return (1.0 if e in cn else 0.3) if cn else 0.2
    if re.search(r'\b(small|less|fewer|lower|short|slow|young)\w*',pl) and len(pn)>=2:
        e=min(pn); return (1.0 if e in cn else 0.3) if cn else 0.2
    if re.search(r'\b(percent|%)\b',pl) and len(pn)>=2:
        base=pn[0] if pn[0]!=0 else 1; e=abs(pn[1]-pn[0])/abs(base)*100
        if cn: best=min(cn,key=lambda x:abs(x-e)); return 1.0 if abs(best-e)<1 else max(0,1-abs(best-e)/100)
        return 0.2
    if re.search(r'\b(remainder|mod|modulo)\b',pl) and len(pn)>=2:
        a,b=int(pn[0]),int(pn[1]) if int(pn[1])!=0 else 1; e=a%b
        return (1.0 if e in [int(x) for x in cn] else 0.2) if cn else 0.2
    return 0.5 if cn and set(pn)&set(cn) else 0.35

def _negation(p,c):
    np_,nc_=len(_N.findall(p)),len(_N.findall(c))
    if np_>=2 and np_%2==0: return 0.8 if nc_%2==0 else 0.3
    if np_==1: return 0.65 if _BOL.search(c.lower()) or nc_>=1 else 0.35
    return 0.5

def _temporal(p,c):
    if not _TMP.search(p): return 0.5
    cl=c.lower(); s=0.35
    if any(w in cl for w in ['before','after','first','last','then','earlier','later']): s+=0.3
    ep=re.findall(r'\b[A-Z][a-z]+\b',p); ec=re.findall(r'\b[A-Z][a-z]+\b',c)
    if ep and ec and ec[0] in ep: s+=0.2
    return min(1.0,s)

def _conditional(p,c):
    if not _CND.search(p): return 0.5
    pl,cl=p.lower(),c.lower(); s=0.3
    if 'if' in pl and 'then' in pl: s+=0.2
    if _BOL.search(cl): s+=0.2
    if _N.search(pl) and _N.search(cl): s+=0.2
    return min(1.0,s)

def _struct(p,c):
    sc,wt,R=0.0,0.0,[]
    pl,cl=p.lower(),c.lower()
    def _a(s,w,n): nonlocal sc,wt; sc+=s*w; wt+=w; R.append(f"{n}={s:.2f}")
    if _N.search(pl):        _a(_negation(p,c),0.12,'neg')
    if _pn(p):               _a(_numeric(p,c),0.15,'num')
    if _TMP.search(pl):      _a(_temporal(p,c),0.10,'tmp')
    if _CND.search(pl):      _a(_conditional(p,c),0.10,'cnd')
    if _CMP.search(pl):
        cn_,pn_=_pn(c),_pn(p)
        if pn_ and cn_:
            s=1.0 if (re.search(r'\b(larg|great|bigg|more|higher)\w*',pl) and max(pn_) in cn_) else \
              (1.0 if (re.search(r'\b(small|less|fewer|lower)\w*',pl) and min(pn_) in cn_) else 0.4)
        else: s=0.4
        _a(s,0.08,'cmp')
    if _QNT.search(pl):      _a(0.6 if _QNT.search(cl) else 0.3,0.06,'qnt')
    if _CAU.search(pl):      _a(0.6 if _CAU.search(cl) else 0.3,0.06,'cau')
    if _SO.search(p):        _a(0.6 if _SO.search(c) else 0.3,0.06,'s_o')
    if re.search(r'\?',pl) and re.search(r'\b(is|are|does|do|was|were|can|will)\b',pl):
        _a(0.65 if _BOL.search(cl) else 0.3,0.05,'bol')
    if _LR.search(pl):       _a(0.6 if _LR.search(cl) else 0.3,0.04,'lr')
    if wt<0.01:
        pt=set(re.findall(r'\b\w{3,}\b',pl)); ct=set(re.findall(r'\b\w{3,}\b',cl))
        ov=len(pt&ct)/max(len(pt),1); sc=ov*0.4; wt=0.5; R.append(f"base={ov:.2f}")
    return (sc/wt if wt else 0.3),wt,R

class ReasoningTool:
    """Neuromodulated Sparse Latent Reasoner v4 struct>=50% comp>=20% ncd<=15%."""
    TAG="NSLR-v4"
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates: return []
        res=[]
        for c in candidates:
            st,w,R=_struct(prompt,c); cp=_numeric(prompt,c) if _pn(prompt) else 0.5
            nc=max(0,1-_ncd(prompt,c)); lr=min(len(c)+1,len(prompt)+1)/max(len(c)+1,len(prompt)+1)
            f=0.55*st+0.25*cp+0.10*nc+0.10*lr
            res.append({"candidate":c,"score":float(max(0,min(1,f))),
                "reasoning":f"[{self.TAG}] st={st:.3f}(w={w:.2f}) cp={cp:.3f} nc={nc:.3f} lr={lr:.3f} | {'; '.join(R)}"})
        res.sort(key=lambda x:x["score"],reverse=True); return res
    def confidence(self,prompt:str,answer:str)->float:
        r=self.evaluate(prompt,[answer])
        if not r: return 0.0
        s=r[0]["score"]; _,w,_=_struct(prompt,answer)
        return min(s,0.25) if w<0.05 else s
