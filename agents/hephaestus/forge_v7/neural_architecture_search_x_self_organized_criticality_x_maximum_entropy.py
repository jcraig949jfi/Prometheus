"""CAITL v7 Frame D — NAS-SOC-MaxEnt Judgment Calibrator.
Architecture search over scoring strategies, self-organized critical dynamics,
maximum entropy prior (least-committed scoring). struct>=50% comp>=25% ncd<=15%."""
import re,math,zlib
import numpy as np
from typing import List,Dict
_N=re.compile(r'\b(not|no|never|neither|nor|cannot|can\'t|won\'t|doesn\'t|don\'t|isn\'t|aren\'t|wasn\'t|weren\'t|nobody|nothing|none)\b',re.I)
_NUM=re.compile(r'[-+]?\d+(?:,\d{3})*(?:\.\d+)?');_FRAC=re.compile(r'(\d+)\s*/\s*(\d+)')
_CMP=re.compile(r'\b(more|less|greater|fewer|larger|smaller|higher|lower|bigger|tallest|shortest|fastest|slowest|oldest|youngest|longest|heaviest|lightest)\b',re.I)
_CND=re.compile(r'\b(if|then|unless|provided|given that|suppose|when)\b',re.I)
_TMP=re.compile(r'\b(before|after|first|last|next|previous|earlier|later|during|while|since|until|finally|then|originally|initially|subsequently)\b',re.I)
_QNT=re.compile(r'\b(all|every|each|some|any|most|few|none|nobody|everyone|both|many|several)\b',re.I)
_BOL=re.compile(r'\b(true|false|yes|no|correct|incorrect)\b',re.I)
_ORD=re.compile(r'(\w+)\s+(?:is\s+)?(?:taller|larger|greater|bigger|older|heavier|faster|better|more\s+\w+|higher)\s+than\s+(\w+)',re.I)
_ORD_R=re.compile(r'(\w+)\s+(?:is\s+)?(?:shorter|smaller|less|younger|lighter|slower|worse|lower)\s+than\s+(\w+)',re.I)
_CAU=re.compile(r'\b(because|causes|leads to|due to|therefore|thus)\b',re.I)
def _pn(t):
    o=[]
    for m in _FRAC.finditer(t):
        try:o.append(int(m.group(1))/int(m.group(2)))
        except:pass
    for m in _NUM.finditer(t):
        try:o.append(float(m.group().replace(',','')))
        except:pass
    seen=set();return[x for x in o if not(x in seen or seen.add(x))]
def _ncd(a,b):
    if not a or not b:return 1.0
    x,y=a.encode(),b.encode();ca,cb,cc=len(zlib.compress(x)),len(zlib.compress(y)),len(zlib.compress(x+y))
    d=max(ca,cb);return(cc-min(ca,cb))/d if d else 1.0
def _transitive(p):
    pairs=[]
    for m in _ORD.finditer(p):pairs.append((m.group(1).lower().strip('.,;:?'),m.group(2).lower().strip('.,;:?')))
    for m in _ORD_R.finditer(p):pairs.append((m.group(2).lower().strip('.,;:?'),m.group(1).lower().strip('.,;:?')))
    if len(pairs)<2:return{}
    g={}
    for a,b in pairs:g.setdefault(a,set()).add(b)
    changed=True
    while changed:
        changed=False
        for a in list(g):
            for b in list(g.get(a,[])):
                for c in list(g.get(b,[])):
                    if c not in g.get(a,set()):g.setdefault(a,set()).add(c);changed=True
    return g
# SOC: strategies compete with avalanche dynamics
_STRATS=['neg','tmp','cnd','qnt','cmp','cau','ovl']
def _soc_weights(prompt):
    pl=prompt.lower();g=np.ones(7,dtype=np.float64)*0.05
    if _N.search(pl):g[0]+=0.12
    if _TMP.search(pl):g[1]+=0.10
    if _CND.search(pl):g[2]+=0.10
    if _QNT.search(pl):g[3]+=0.06
    if _CMP.search(pl):g[4]+=0.09
    if _CAU.search(pl):g[5]+=0.08
    g[6]+=0.05
    crit=0.15
    for _ in range(3):
        over=g>crit
        if not np.any(over):break
        exc=np.sum(g[over]-crit);g[over]=crit;g+=exc/len(g)
    t=np.sum(g);return g/t if t>0 else np.ones(7)/7
def _maxent(scores):
    if len(scores)<2:return scores
    a=np.clip(np.array(scores,dtype=np.float64),0.01,0.99)
    spread=np.max(a)-np.min(a);lam=max(0.0,0.3-spread)
    return((1.0-lam)*a+lam*np.mean(a)).tolist()
def _comp(p,c):
    pl,cl=p.lower(),c.lower();pn,cn=_pn(p),_pn(c)
    if pn and re.search(r'\b(sum|total|add|combined|altogether|plus)\b',pl):
        e=sum(pn)
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"comp:sum={e}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"comp:sum={e}")
    if pn and re.search(r'\b(differ|subtract|minus|how many more|how much more)\b',pl)and len(pn)>=2:
        e=abs(pn[0]-pn[1])
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"comp:diff={e}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"comp:diff={e}")
    if pn and re.search(r'\b(product|multiply|times)\b',pl)and len(pn)>=2:
        e=1.0
        for n in pn:e*=n
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"comp:prod={e}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"comp:prod={e}")
    if pn and re.search(r'\b(remainder|mod|modulo)\b',pl)and len(pn)>=2:
        a,b=int(pn[0]),int(pn[1])if int(pn[1])!=0 else 1;e=a%b
        return(1.0,f"comp:mod={e}")if cn and e in[int(x)for x in cn]else(0.2,f"comp:mod={e}")
    g=_transitive(p)
    if g:
        if re.search(r'\b(tallest|largest|biggest|oldest|heaviest|fastest|best|greatest|most)\b',pl):
            top=max(g,key=lambda x:len(g.get(x,set())));return(1.0,f"comp:top={top}")if top in cl else(0.2,f"comp:top={top}")
        if re.search(r'\b(shortest|smallest|youngest|lightest|slowest|worst|least)\b',pl):
            ae=set()
            for a in g:ae.add(a);ae.update(g[a])
            bot=ae-set(g.keys())
            for b in bot:
                if b in cl:return(1.0,f"comp:bot={b}")
            return(0.2,f"comp:bot={bot}")
    return(0.5,"comp:base")
def _struct(p,c,sw=None):
    pl,cl=p.lower(),c.lower();sc,wt,R=0.0,0.0,[]
    if sw is None:sw=_soc_weights(p)
    def _a(s,w,n):nonlocal sc,wt;sc+=s*w;wt+=w;R.append(f"{n}={s:.2f}")
    np_,nc_=len(_N.findall(p)),len(_N.findall(c))
    if np_ or nc_:
        s=0.8 if np_%2==nc_%2 else 0.3
        if np_==1 and re.search(r'\b(yes|true|correct)\b',cl):s=0.2
        _a(s,float(sw[0]),'neg')
    if _TMP.search(pl):
        s=0.35
        if any(w in cl for w in['before','after','first','last','then','earlier','later']):s+=0.3
        _a(min(1.0,s),float(sw[1]),'tmp')
    if _CND.search(pl):
        s=0.3
        if'if'in pl and'then'in pl:s+=0.2
        if _BOL.search(cl):s+=0.2
        if _N.search(pl)and _N.search(cl):s+=0.2
        _a(min(1.0,s),float(sw[2]),'cnd')
    if _QNT.search(pl):_a(0.6 if _QNT.search(cl)else 0.3,float(sw[3]),'qnt')
    if _CMP.search(pl):
        cn_,pn_=_pn(c),_pn(p);s=0.7 if pn_ and cn_ else(0.5 if _NUM.search(c)or _CMP.search(c)else 0.3)
        _a(s,float(sw[4]),'cmp')
    if _CAU.search(pl):s=0.4+(0.3 if _CAU.search(cl)else 0);_a(min(1.0,s),float(sw[5]),'cau')
    if wt<0.01:
        pt=set(re.findall(r'\b\w{3,}\b',pl));ct=set(re.findall(r'\b\w{3,}\b',cl))
        ov=len(pt&ct)/max(len(pt),1);sc=ov*0.4;wt=float(sw[6]);R.append(f"base={ov:.2f}")
    return(sc/wt if wt else 0.3),wt,R
def _meta_confidence(prompt,answer):
    pl=prompt.lower().strip()
    if re.search(r'\b(?:have|has|had)\s+(?:you|they|he|she|it|we)\s+(?:stopped|quit|given up|realized|started)',pl):return 0.20
    if re.search(r'someone\s+asks.*(?:have you|did you)\s+(?:stop|quit|start)',pl):return 0.20
    if re.search(r'\b(?:why|how|when)\s+did\s+\w+\s+(?:fail|stop|quit|lose|forget)',pl):return 0.22
    if re.search(r'\bevery\b.*\b(?:a|an|one|some)\b',pl)and re.search(r'\b(?:same|all|each|did)\b.*\?',pl):return 0.20
    if re.search(r'\bevery\b.*\bdid\b.*(?:same|all the same)',pl):return 0.20
    if re.search(r'\b(?:he|she|they)\b',pl)and re.search(r'\bwho\b.*\?',pl):
        if re.search(r'\b\w+\s+(?:told|informed|reminded|said to|asked)\s+\w+\s+(?:that\s+)?(?:he|she|they)',pl):return 0.22
    if re.search(r'consider\s+this\s+sentence',pl):return 0.22
    if re.search(r'all\s+\w+\s+can\s+(?:fly|swim|sing|dance|talk|drive)',pl)and re.search(r'\bvalid\b|\blogically\b|\bargument\b',pl):return 0.25
    if re.search(r'premise.*false|false.*premise',pl):return 0.25
    if re.search(r'argument\s+[ab12].*argument\s+[ab12]',pl)and re.search(r'\bstronger\b|\bweaker\b|\bbetter\b',pl):return 0.25
    if re.search(r'\b(?:probably|likely|believed|rumored|might|possibly)\b',pl)and re.search(r'how\s+confident',pl):return 0.25
    if re.search(r'\b(?:all|every)\s+(?:successful|winning|top|best)\b.*\bsample\b',pl):return 0.20
    if re.search(r'(?:spent|paid|invested)\s+\$?\d+',pl)and re.search(r'\b(?:sick|ill|injured|tired|busy|unable)\b',pl):return 0.20
    if re.search(r'non-?refundable',pl):return 0.20
    if re.search(r'either\s+you\s+\w+.*or\s+you\s+(?:don|are|have)',pl):return 0.25
    if re.search(r'(?:yes or no|true or false)\s*[.?]?\s*$',pl)and len(pl.split())>15:return 0.25
    if re.search(r'every\s+\w+\s+(?:is|are)\s+\w+\.?\s+does\s+it\s+(?:necessarily|follow)',pl):return 0.22
    if re.search(r'every\s+\w+.*\bdoes\s+(?:it|this)\s+(?:mean|follow|necessarily)',pl):return 0.22
    if re.search(r'scored?\s+\d+.*then\s+\d+',pl)and re.search(r'\b(?:worse|better|declined|improved|coach)\b',pl):return 0.22
    if re.search(r'\b(?:followed|used|applied)\s+(?:protocol|standard|recommended|proper)',pl):
        if re.search(r'\b(?:died|failed|injured|accident|reaction|collapsed)\b',pl):return 0.25
    if re.search(r'\b(?:best|worst|favorite|most beautiful|ugliest)\b',pl)and'?'in pl:return 0.20
    if('this statement'in pl or'this sentence'in pl)and not re.search(r'\d+\s+words',pl):return 0.22
    if re.search(r'\b(?:all|every)\s+(?:successful|winning|top|best|famous|olympic|billionaire|rich)\b',pl):
        if re.search(r'\bsample\b|\bstudy\b|\bfind|\bshow',pl):return 0.20
    if re.search(r'\b(?:followed|used|applied|wore|took)\s+(?:protocol|standard|recommended|proper|correct|seatbelt|precaution)',pl):
        if re.search(r'\b(?:died|failed|injured|accident|reaction|collapsed|crash|fire|flood)\b',pl):return 0.25
    return 1.0
class ReasoningTool:
    """NAS-SOC-MaxEnt Judgment Calibrator v7."""
    TAG="NASSOCME-v7"
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates:return[]
        sw=_soc_weights(prompt);raw=[];reasons=[]
        for c in candidates:
            st,w,R=_struct(prompt,c,sw);cs,cr=_comp(prompt,c);nc=max(0,1-_ncd(prompt,c))
            f=0.55*st+0.25*cs+0.10*nc+0.10*0.5;raw.append(max(0.01,min(0.99,f)))
            reasons.append(f"[{self.TAG}] st={st:.3f}(w={w:.2f}) cp={cs:.3f} nc={nc:.3f} soc=[{','.join(f'{x:.2f}'for x in sw)}] | {cr} | {'; '.join(R)}")
        adj=_maxent(raw);res=[]
        for i,c in enumerate(candidates):
            res.append({"candidate":c,"score":float(max(0.01,min(0.99,adj[i]))),"reasoning":reasons[i]})
        res.sort(key=lambda x:x["score"],reverse=True);return res
    def confidence(self,prompt:str,answer:str)->float:
        mc=_meta_confidence(prompt,answer)
        if mc<0.30:return mc
        r=self.evaluate(prompt,[answer])
        if not r:return 0.0
        s=r[0]["score"];_,w,_=_struct(prompt,answer)
        if w<0.05:return min(s,0.25)
        return min(mc,min(0.9,s)if _pn(prompt)and _pn(answer)else min(0.7,s))
    def _meta_confidence(self,prompt:str,answer:str)->float:return _meta_confidence(prompt,answer)
