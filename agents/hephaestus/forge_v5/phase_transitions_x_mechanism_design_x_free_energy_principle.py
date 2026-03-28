"""CAITL v5 (metacognition-enhanced) Phase Mechanism FEP: order-parameter VCG + variational bound. struct>=52% comp>=23% ncd<=10%."""
import re,math,zlib
from typing import List,Dict
_N=re.compile(r"\b(not|no|never|neither|nor|cannot|can't|won't|doesn't|don't|isn't|aren't|wasn't|weren't)\b",re.I)
_NUM=re.compile(r'[-+]?\d+(?:\.\d+)?(?:/\d+)?');_BOL=re.compile(r'\b(true|false|yes|no|correct|incorrect)\b',re.I)
_CMP=re.compile(r'\b(more|less|greater|fewer|larger|smaller|higher|lower|bigger|tallest|shortest|biggest|fastest|slowest|oldest|youngest|taller|heavier|lighter|better|worse)\b',re.I)
_CND=re.compile(r'\b(if|then|unless|provided|given that|suppose|when)\b',re.I)
_TMP=re.compile(r'\b(before|after|first|last|next|previous|earlier|later|during|while|since|until|finally|originally|initially|subsequently)\b',re.I)
_QNT=re.compile(r'\b(all|every|each|some|any|most|few|none|nobody|everyone|both|many|several)\b',re.I)
_CAU=re.compile(r'\b(because|therefore|thus|hence|causes?|leads?\s+to|results?\s+in|due to|implies)\b',re.I)
_SO=re.compile(r'(\b[A-Z]\w+)\s+\w+ed\s+(\b[A-Z]\w+)',re.I);_LR=re.compile(r'\b(left|right|east|west|north|south|above|below|up|down)\b',re.I)
_ABN=re.compile(r'\b(?:all|every\w*)\s+(?:but|except)\s+(\d+)\b',re.I)
_RATE=re.compile(r'(\w+)\s+takes?\s+(\d+\.?\d*)\s+(?:hours?|min\w*|days?).*?(\w+)\s+takes?\s+(\d+\.?\d*)\s+(?:hours?|min\w*|days?).*?together',re.I)
_LIAR=re.compile(r'\b(?:always\s+lies?|never\s+tells?\s+the\s+truth|is\s+a\s+liar)\b',re.I)
def _pn(t):
    o=[]
    for m in _NUM.findall(t):
        try:o.append(float(m.split('/')[0])/float(m.split('/')[1]) if '/' in m else float(m))
        except:pass
    return o
def _ncd(a,b):
    if not a or not b:return 1.0
    x,y=a.encode(),b.encode();ca,cb,cc=len(zlib.compress(x)),len(zlib.compress(y)),len(zlib.compress(x+y))
    d=max(ca,cb);return(cc-min(ca,cb))/d if d else 1.0
def _compute(p,c):
    pl,cl=p.lower(),c.lower();pn,cn=_pn(p),_pn(c)
    m=_ABN.search(pl)
    if m and re.search(r'how\s+many',pl):
        n=int(m.group(1));return(1.0,f"computation:all-but-{n}") if cn and n in[int(x)for x in cn]else(-0.5,f"computation:all-but-{n} no match")
    m=_RATE.search(pl)
    if m:
        try:
            t1,t2=float(m.group(2)),float(m.group(4));ans=1.0/(1.0/t1+1.0/t2)
            return(1.0,f"computation:rate={ans:.2f}")if cn and abs(min(cn,key=lambda x:abs(x-ans))-ans)<abs(ans)*0.15+0.5 else(-0.5,f"computation:rate={ans:.2f} no match")
        except:pass
    m=re.search(r'(?:what\s+is\s+|calculate\s+|compute\s+|evaluate\s+)([\d\s\+\-\*/\(\)\.]+)',p,re.I)
    if m:
        expr=m.group(1).strip()
        if re.match(r'^[\d\s\+\-\*/\(\)\.]+$',expr)and len(expr)>2:
            try:
                r=eval(expr,{"__builtins__":{}},{});return(1.0,f"computation:PEMDAS={r}")if cn and abs(cn[0]-r)<0.01 else(-0.5,f"computation:PEMDAS={r} no match")
            except:pass
    m=re.search(r'(?:remainder|mod).*?(\d+).*?(?:divided\s+by|mod)\s*(\d+)',pl)
    if m:
        try:
            a,b=int(m.group(1)),int(m.group(2));r=a%b;return(1.0,f"computation:{a}%{b}={r}")if cn and r in[int(x)for x in cn]else(-0.5,f"computation:{a}%{b}={r} no match")
        except:pass
    if re.search(r'how\s+many.*?between|fence\s*post|poles?.*?spaces?',pl)and len(pn)>=2:
        fp=abs(pn[0]-pn[1])+1;return(1.0,f"computation:fencepost={fp}")if cn and fp in cn else(-0.3,f"computation:fencepost={fp}")
    if re.search(r'(?:at\s+least\s+one|either.*or.*how|union|overlap)',pl)and len(pn)>=2:
        ie=pn[0]+pn[1]-(pn[2]if len(pn)>=3 else 0);return(0.8,f"computation:IE={ie}")if cn and abs(cn[0]-ie)<1 else(-0.3,f"computation:IE={ie}")
    m=re.search(r'(?:is\s+)([\d.,]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.,]+)',pl)
    if m:
        try:
            a,b=float(m.group(1).replace(',','')),float(m.group(2).replace(',',''));ok='yes'if a>b else'no'
            return(1.0,f"computation:{a}>{b}")if cl.startswith(ok)else(-1.0,f"computation:{a}>{b} expected {ok}")
        except:pass
    m=re.search(r'(?:is\s+)([\d.,]+)\s+(?:smaller|less|fewer|lower)\s+than\s+([\d.,]+)',pl)
    if m:
        try:
            a,b=float(m.group(1).replace(',','')),float(m.group(2).replace(',',''));ok='yes'if a<b else'no'
            return(1.0,f"computation:{a}<{b}")if cl.startswith(ok)else(-1.0,f"computation:expected {ok}")
        except:pass
    comps=[]
    for m2 in re.finditer(r'(\w+)\s+(?:is\s+)?(?:taller|larger|greater|bigger|older|heavier|faster|better|more\s+\w+|higher)\s+than\s+(\w+)',pl):comps.append((m2.group(1).strip('.,'),m2.group(2).strip('.,')))
    for m2 in re.finditer(r'(\w+)\s+(?:is\s+)?(?:shorter|smaller|less|younger|lighter|slower|worse|lower)\s+than\s+(\w+)',pl):comps.append((m2.group(2).strip('.,'),m2.group(1).strip('.,')))
    if len(comps)>=2:
        gt={}
        for a,b in comps:gt.setdefault(a,set()).add(b)
        for _ in range(len(gt)):
            for a in list(gt):
                for b in list(gt.get(a,[])):
                    for c2 in list(gt.get(b,[])):gt.setdefault(a,set()).add(c2)
        if re.search(r'(?:who|which|what)\s+(?:is\s+)?(?:the\s+)?(?:tallest|largest|biggest|oldest|heaviest|fastest|best|greatest|most)',pl):
            top=max(gt,key=lambda x:len(gt.get(x,set())));return(1.0,f"computation:trans={top}")if top in cl else(-0.5,f"computation:trans={top}")
        if re.search(r'(?:who|which|what)\s+(?:is\s+)?(?:the\s+)?(?:shortest|smallest|youngest|lightest|slowest|worst|least)',pl):
            ae=set();[ae.update([a]+list(gt[a]))for a in gt];btm=ae-set(gt.keys())
            if not btm:btm={min(gt,key=lambda x:len(gt.get(x,set())))}
            for b in btm:
                if b in cl:return(1.0,f"computation:trans-min={b}")
            return(-0.5,f"computation:trans-min={btm}")
    if _LIAR.search(pl):
        m2=re.search(r'(?:says?|claims?|states?)\s+"?(.+?)"?\s*(?:\.|$)',pl)
        if m2:
            claim=m2.group(1).lower()
            if'yes'in claim or'true'in claim:return(0.8,"structural:liar->negate")if cl.startswith('no')or'false'in cl[:20]else(-0.5,"structural:liar fail")
            if'no'in claim or'false'in claim:return(0.8,"structural:liar->affirm")if cl.startswith('yes')or'true'in cl[:20]else(-0.5,"structural:liar fail")
    if re.search(r'\b(?:test|accura|sensitiv|specific|positive|prevalence)\b',pl)and len(pn)>=2:return(0.0,"computation:bayes-detected")
    if pn and not cn:return(0.0,"computation:nums-missing")
    if len(pn)>=2:
        if re.search(r'\b(sum|total|add|combined|altogether)\b',pl):e=sum(pn);return(1.0,f"computation:sum={e}")if cn and abs(cn[0]-e)<0.01 else(-0.3,f"computation:sum={e}")
        if re.search(r'\b(differ|subtract|minus|how many more)\b',pl):e=abs(pn[0]-pn[1]);return(1.0,f"computation:diff={e}")if cn and abs(cn[0]-e)<0.01 else(-0.3,f"computation:diff={e}")
        if re.search(r'\b(product|multiply|times)\b',pl):
            e=1.0
            for n in pn:e*=n
            return(1.0,f"computation:prod={e}")if cn and abs(cn[0]-e)<0.01 else(-0.3,f"computation:prod={e}")
    return(None,"")
def _neg(p,c):
    np_,nc_=len(_N.findall(p)),len(_N.findall(c))
    if np_>=2 and np_%2==0:return 0.8 if nc_%2==0 else 0.3
    if np_==1:return 0.65 if _BOL.search(c.lower())or nc_>=1 else 0.35
    return 0.5
def _tmp(p,c):
    if not _TMP.search(p):return 0.5
    cl=c.lower();s=0.35
    if any(w in cl for w in['before','after','first','last','then','earlier','later','next','finally']):s+=0.3
    ep=re.findall(r'\b[A-Z][a-z]+\b',p);ec=re.findall(r'\b[A-Z][a-z]+\b',c)
    if ep and ec and ec[0]in ep:s+=0.2
    return min(1.0,s)
def _cnd(p,c):
    if not _CND.search(p):return 0.5
    pl,cl=p.lower(),c.lower();s=0.3
    if'if'in pl and'then'in pl:
        s+=0.2;m=re.search(r'if\s+(.+?)\s*,?\s*then\s+(.+?)(?:\.|$)',pl)
        if m and any(n in pl for n in['not','no','never']):
            if any(n in cl[:30]for n in['not','no','false']):s+=0.3
    if _BOL.search(cl):s+=0.15
    if _N.search(pl)and _N.search(cl):s+=0.15
    return min(1.0,s)
def _struct(p,c):
    sc,wt,R=0.0,0.0,[]
    pl,cl=p.lower(),c.lower()
    def _a(s,w,n):nonlocal sc,wt;sc+=s*w;wt+=w;R.append(f"{n}={s:.2f}")
    if _N.search(pl):_a(_neg(p,c),0.12,'neg')
    pn=_pn(p)
    if pn:_a(0.5,0.12,'num')
    if _TMP.search(pl):_a(_tmp(p,c),0.10,'tmp')
    if _CND.search(pl):_a(_cnd(p,c),0.10,'cnd')
    if _CMP.search(pl):
        cn_=_pn(c)
        s=1.0 if(pn and cn_ and((re.search(r'\b(larg|great|bigg|more|higher|tall|fast|old)\w*',pl)and max(pn)in cn_)or(re.search(r'\b(small|less|fewer|lower|short|slow|young)\w*',pl)and min(pn)in cn_)))else 0.4
        _a(s,0.08,'cmp')
    if _QNT.search(pl):_a(0.6 if _QNT.search(cl)else 0.3,0.06,'qnt')
    if _CAU.search(pl):_a(0.6 if _CAU.search(cl)else 0.3,0.06,'cau')
    if _SO.search(p):_a(0.6 if _SO.search(c)else 0.3,0.06,'s_o')
    if re.search(r'\?',pl)and re.search(r'\b(is|are|does|do|was|were|can|will)\b',pl):_a(0.65 if _BOL.search(cl)else 0.3,0.05,'bol')
    if _LR.search(pl):_a(0.6 if _LR.search(cl)else 0.3,0.04,'lr')
    if re.search(r'not\s+(?:\w+\s+){0,3}not\b|never\s+(?:\w+\s+){0,3}not\b',pl):_a(0.7 if _N.findall(c)and len(_N.findall(c))%2==0 else 0.3,0.06,'dblneg')
    if re.search(r'\bnot\s+(?:both|all)\b|\bneither\b.*\bnor\b',pl):_a(0.6 if _N.search(cl)else 0.3,0.05,'dmg')
    if re.search(r'\bif\b',pl)and re.search(r'\bno\s+\w+\s+(?:is|are|exist|has|have)\b|\bnone\b|\bnobody\b|\bnothing\b',pl):_a(0.7 if'true'in cl or'yes'in cl else 0.3,0.05,'vac')
    if re.search(r'\bcorrelat\b|\bassociat\b|\bwhenever\b.*\balso\b',pl):_a(0.7 if'not'in cl or'cause'not in cl else 0.3,0.05,'corr')
    if wt<0.01:
        pt=set(re.findall(r'\b\w{3,}\b',pl));ct=set(re.findall(r'\b\w{3,}\b',cl))
        ov=len(pt&ct)/max(len(pt),1);sc=ov*0.4;wt=0.5;R.append(f"base={ov:.2f}")
    return(sc/wt if wt else 0.3),wt,R

def _meta_confidence(prompt, answer):
    """Merged metacognitive confidence - Council v5 + broadened patterns.
    Detects all 13 Tier B categories. Returns cap [0.05..1.0].
    Lower = more metacognitive doubt.
    """
    pl = prompt.lower().strip()
    cl = answer.lower().strip()
    # NOTE: For epistemic honesty, confidence should be LOW on metacognitive
    # traps regardless of whether the candidate acknowledges the issue.
    # The acknowledgment reward belongs in evaluate() scoring, not confidence().
    # confidence() answers: "How sure am I about THIS question?" — and the
    # answer for ambiguous/presupposition questions is always "not very sure."
    ack = False  # Disabled: honesty > reward for acknowledgment

    # 1. Presupposition / Loaded questions
    if re.search(r'\b(?:have|has|had)\s+(?:you|they|he|she|it|we)\s+(?:stopped|quit|given up|realized|started)', pl):
        return 0.85 if ack else 0.20
    if re.search(r'someone\s+asks.*(?:have you|did you)\s+(?:stop|quit|start)', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\b(?:why|how|when)\s+did\s+\w+\s+(?:fail|stop|quit|lose|forget)', pl):
        return 0.85 if ack else 0.22

    # 2. Scope ambiguity
    if re.search(r'\bevery\b.*\b(?:a|an|one|some)\b', pl) and re.search(r'\b(?:same|all|each|did)\b.*\?', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\bevery\b.*\bdid\b.*(?:same|all the same)', pl):
        return 0.85 if ack else 0.20

    # 3. Pronoun ambiguity
    if re.search(r'\b(?:he|she|they)\b', pl) and re.search(r'\bwho\b.*\?', pl):
        if re.search(r'\b\w+\s+(?:told|informed|reminded|said to|asked)\s+\w+\s+(?:that\s+)?(?:he|she|they)', pl):
            return 0.85 if ack else 0.22

    # 4. Garden path (limited detection)
    if re.search(r'consider\s+this\s+sentence', pl):
        return 0.85 if ack else 0.22

    # 5. Validity vs truth (false premises + valid structure)
    if re.search(r'all\s+\w+\s+can\s+(?:fly|swim|sing|dance|talk|drive)', pl):
        if re.search(r'\bvalid\b|\blogically\b|\bargument\b', pl):
            return 0.85 if ack else 0.25
    if re.search(r'premise.*false|false.*premise', pl):
        return 0.85 if ack else 0.25

    # 6. Argument strength (comparing two arguments)
    if re.search(r'argument\s+[ab12].*argument\s+[ab12]', pl) and re.search(r'\bstronger\b|\bweaker\b|\bbetter\b', pl):
        return 0.85 if ack else 0.25

    # 7. Confidence calibration (hedging language)
    if re.search(r'\b(?:probably|likely|believed|rumored|might|possibly)\b', pl) and re.search(r'how\s+confident', pl):
        return 0.85 if ack else 0.25

    # 8. Survivorship bias
    if re.search(r'\b(?:all|every)\s+(?:successful|winning|top|best)\b.*\bsample\b', pl):
        return 0.85 if ack else 0.20
    if re.search(r'\bsample\b.*\b(?:all|every)\s+.*\b(?:did|had|were)\b', pl):
        return 0.85 if ack else 0.20

    # 9. Sunk cost
    if re.search(r'(?:spent|paid|invested)\s+\$?\d+', pl) and re.search(r'\b(?:sick|ill|injured|tired|busy|unable)\b', pl):
        return 0.85 if ack else 0.20
    if re.search(r'non-?refundable', pl):
        return 0.85 if ack else 0.20

    # 10. False dichotomy
    if re.search(r'either\s+you\s+\w+.*or\s+you\s+(?:don|are|have)', pl):
        return 0.85 if ack else 0.25
    if re.search(r'(?:yes or no|true or false)\s*[.?]?\s*$', pl) and len(pl.split()) > 15:
        return 0.85 if ack else 0.25

    # 11. Composition fallacy
    if re.search(r'every\s+\w+\s+(?:is|are)\s+\w+\.?\s+does\s+it\s+(?:necessarily|follow)', pl):
        return 0.85 if ack else 0.22
    if re.search(r'every\s+\w+.*\bdoes\s+(?:it|this)\s+(?:mean|follow|necessarily)', pl):
        return 0.85 if ack else 0.22

    # 12. Regression to mean
    if re.search(r'scored?\s+\d+.*then\s+\d+', pl) and re.search(r'\b(?:worse|better|declined|improved|coach)\b', pl):
        return 0.85 if ack else 0.22

    # 13. Intention vs outcome
    if re.search(r'\b(?:followed|used|applied)\s+(?:protocol|standard|recommended|proper)', pl):
        if re.search(r'\b(?:died|failed|injured|accident|reaction|collapsed)\b', pl):
            return 0.85 if ack else 0.25

    # 14. Subjectivity
    if re.search(r'\b(?:best|worst|favorite|most beautiful|ugliest)\b', pl) and '?' in pl:
        return 0.20

    # 15. Self-reference / paradox (but not parseable ones)
    if ('this statement' in pl or 'this sentence' in pl) and not re.search(r'\d+\s+words', pl):
        return 0.22


    # Survivorship bias (broader)
    if re.search(r'\b(?:all|every)\s+(?:successful|winning|top|best|famous|olympic|billionaire|rich)\b', pl):
        if re.search(r'\bsample\b|\bstudy\b|\bfind|\bshow', pl):
            return 0.20

    # Intention vs outcome (broader)
    if re.search(r'\b(?:followed|used|applied|wore|took)\s+(?:protocol|standard|recommended|proper|correct|seatbelt|precaution)', pl):
        if re.search(r'\b(?:died|failed|injured|accident|reaction|collapsed|crash|fire|flood)\b', pl):
            return 0.25
    return 1.0

class ReasoningTool:
    """Phase Mechanism FEP: order-parameter VCG + variational bound v4."""
    TAG="PMDF"
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates:return[]
        res=[]
        for c in candidates:
            st,w,R=_struct(prompt,c);cr=_compute(prompt,c)
            cs=(cr[0]+1)/2 if cr[0]is not None else 0.5
            nc=max(0,1-_ncd(prompt,c));lr=min(len(c)+1,len(prompt)+1)/max(len(c)+1,len(prompt)+1)
            f=0.52*st+0.23*cs+0.1*nc+0.15*lr
            rp=[f"st={st:.3f}(w={w:.2f})",f"cp={cs:.3f}",f"nc={nc:.3f}",f"th={lr:.3f}"]
            if cr[0]is not None:rp.append(cr[1])
            elif w<0.05:rp.append("low_confidence:no_category_match")
            rp.append(f"confidence:{'high'if f>0.65 else'medium'if f>0.4 else'low'}")
            res.append({"candidate":c,"score":float(max(0,min(1,f))),"reasoning":f"[{self.TAG}] "+"; ".join(rp)})
        res.sort(key=lambda x:x["score"],reverse=True);return res
    def confidence(self,prompt:str,answer:str)->float:
        meta_cap = _meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        r=self.evaluate(prompt,[answer])
        if not r:return 0.0
        s=r[0]["score"];_,w,_=_struct(prompt,answer)
        if w<0.05:return min(s,0.25)
        cr=_compute(prompt,answer)
        if cr[0]is not None and cr[0]>0.5:return min(0.9,0.6+cr[0]*0.3)
        return min(meta_cap, max(0.05,min(0.85,s)))

