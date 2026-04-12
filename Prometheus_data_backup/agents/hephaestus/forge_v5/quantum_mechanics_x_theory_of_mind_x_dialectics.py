"""CAITL v5 (metacognition-enhanced) — Quantum ToM Dialectic Reasoner (QTDR).
Constructive computation + structural parsing + epistemic calibration.
struct>=50% comp>=20% ncd<=15%."""
import re, math, zlib
from typing import List, Dict, Tuple, Optional

_N=re.compile(r'\b(not|no|never|neither|nor|cannot|can\'t|won\'t|doesn\'t|don\'t|isn\'t|aren\'t|wasn\'t|weren\'t|nobody|nothing|none)\b',re.I)
_NUM=re.compile(r'[-+]?\d+(?:,\d{3})*(?:\.\d+)?');_FRAC=re.compile(r'(\d+)\s*/\s*(\d+)')
_CMP=re.compile(r'\b(more|less|greater|fewer|larger|smaller|higher|lower|bigger|tallest|shortest|fastest|slowest|oldest|youngest|longest|heaviest|lightest)\b',re.I)
_CND=re.compile(r'\b(if|then|unless|provided|given that|suppose|when)\b',re.I)
_TMP=re.compile(r'\b(before|after|first|last|next|previous|earlier|later|during|while|since|until|finally|then|originally|initially|subsequently)\b',re.I)
_QNT=re.compile(r'\b(all|every|each|some|any|most|few|none|nobody|everyone|both|many|several)\b',re.I)
_BOL=re.compile(r'\b(true|false|yes|no|correct|incorrect)\b',re.I)
_ORD=re.compile(r'(\w+)\s+(?:is\s+)?(?:taller|larger|greater|bigger|older|heavier|faster|better|more\s+\w+|higher)\s+than\s+(\w+)',re.I)
_ORD_R=re.compile(r'(\w+)\s+(?:is\s+)?(?:shorter|smaller|less|younger|lighter|slower|worse|lower)\s+than\s+(\w+)',re.I)

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

def _comp(p,c):
    pl,cl=p.lower(),c.lower();pn,cn=_pn(p),_pn(c)
    if pn and re.search(r'\b(sum|total|add|combined|altogether|plus)\b',pl):
        e=sum(pn)
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"computation:sum={e}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"computation:sum={e}")
        return(0.1,f"computation:sum={e}")
    if pn and re.search(r'\b(differ|subtract|minus|how many more)\b',pl)and len(pn)>=2:
        e=abs(pn[0]-pn[1])
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"computation:diff={e}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"computation:diff={e}")
        return(0.1,f"computation:diff={e}")
    if pn and re.search(r'\b(product|multiply|times)\b',pl)and len(pn)>=2:
        e=1.0
        for n in pn:e*=n
        if cn:best=min(cn,key=lambda x:abs(x-e));return(1.0,f"computation:prod={e}")if abs(best-e)<0.01 else(max(0,1-abs(best-e)/(abs(e)+1)),f"computation:prod={e}")
        return(0.1,f"computation:prod={e}")
    if pn and re.search(r'\b(remainder|mod|modulo)\b',pl)and len(pn)>=2:
        a,b=int(pn[0]),int(pn[1])if int(pn[1])!=0 else 1;e=a%b
        return((1.0,f"computation:mod={e}")if cn and e in[int(x)for x in cn]else(0.2,f"computation:mod={e}"))
    if pn and re.search(r'\bper\b.*\btogether\b|\btakes?\b.*\btogether\b',pl)and len(pn)>=2:
        try:
            t=1.0/sum(1.0/x for x in pn if x>0)
            if cn:best=min(cn,key=lambda x:abs(x-t));return(1.0,f"computation:rate={t:.2f}")if abs(best-t)<0.5 else(0.3,f"computation:rate={t:.2f}")
        except:pass
    if pn and len(pn)>=2 and re.search(r'\b(larg|great|bigg|more|higher)\w*\s+than\b',pl):
        return(0.9,"computation:cmp>")if'yes'in cl or str(max(pn))in cl else(0.2,"computation:cmp>")
    if pn and len(pn)>=2 and re.search(r'\b(small|less|fewer|lower)\w*\s+than\b',pl):
        return(0.9,"computation:cmp<")if'yes'in cl or str(min(pn))in cl else(0.2,"computation:cmp<")
    g=_transitive(p)
    if g:
        if re.search(r'\b(tallest|largest|biggest|oldest|heaviest|fastest|best|greatest|most)\b',pl):
            top=max(g,key=lambda x:len(g.get(x,set())));return(1.0,f"computation:top={top}")if top in cl else(0.2,f"computation:top={top}")
        if re.search(r'\b(shortest|smallest|youngest|lightest|slowest|worst|least)\b',pl):
            ae=set()
            for a in g:ae.add(a);ae.update(g[a])
            bot=ae-set(g.keys())
            for b in bot:
                if b in cl:return(1.0,f"computation:bot={b}")
            return(0.2,f"computation:bot={bot}")
    m=re.search(r'(?:all|every\w*)\s+(?:but|except)\s+(\d+)',pl)
    if m and re.search(r'how\s+many',pl):
        n=m.group(1);return(1.0,f"computation:all_but_{n}")if n in c else(0.2,f"computation:all_but_{n}")
    if not pn:return(0.5,"computation:none")
    return(0.5,"computation:base")

def _struct(p,c):
    pl,cl=p.lower(),c.lower();sc,wt,R=0.0,0.0,[]
    def _a(s,w,n):nonlocal sc,wt;sc+=s*w;wt+=w;R.append(f"{n}={s:.2f}")
    np_,nc_=len(_N.findall(p)),len(_N.findall(c))
    if np_ or nc_:
        s=0.8 if np_%2==nc_%2 else 0.3
        if np_==1 and re.search(r'\b(yes|true|correct)\b',cl):s=0.2
        _a(s,0.12,'neg')
    if _TMP.search(pl):
        s=0.35
        if any(w in cl for w in['before','after','first','last','then','earlier','later']):s+=0.3
        ep=re.findall(r'\b[A-Z][a-z]+\b',p);ec=re.findall(r'\b[A-Z][a-z]+\b',c)
        if ep and ec and ec[0]in ep:s+=0.2
        _a(min(1.0,s),0.10,'tmp')
    if _CND.search(pl):
        s=0.3
        if'if'in pl and'then'in pl:s+=0.2
        if _BOL.search(cl):s+=0.2
        if _N.search(pl)and _N.search(cl):s+=0.2
        _a(min(1.0,s),0.10,'cnd')
    if _QNT.search(pl):_a(0.6 if _QNT.search(cl)else 0.3,0.06,'qnt')
    if _CMP.search(pl):
        cn_,pn_=_pn(c),_pn(p)
        s=0.7 if pn_ and cn_ else(0.5 if _NUM.search(c)or _CMP.search(c)else 0.3)
        _a(s,0.08,'cmp')
    if re.search(r'\?',pl)and re.search(r'\b(is|are|does|do|was|were|can|will|has|have)\b',pl):
        _a(0.65 if _BOL.search(cl)else 0.3,0.05,'bol')
    if re.search(r'(\b[A-Z]\w+)\s+\w+ed\s+(\b[A-Z]\w+)',p):
        _a(0.6 if re.search(r'(\b[A-Z]\w+)\s+\w+ed\s+(\b[A-Z]\w+)',c)else 0.3,0.06,'s_o')
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
    """Quantum ToM Dialectic Reasoner v4. struct>=50% comp>=20% ncd<=15%."""
    TAG="QTDR-v4"
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates:return[]
        res=[]
        for c in candidates:
            st,w,R=_struct(prompt,c);cs,cr=_comp(prompt,c);nc=max(0,1-_ncd(prompt,c))
            f=0.55*st+0.25*cs+0.10*nc+0.10*0.5
            res.append({"candidate":c,"score":float(max(0,min(1,f))),"reasoning":f"[{self.TAG}] st={st:.3f}(w={w:.2f}) cp={cs:.3f} nc={nc:.3f} | {cr} | {'; '.join(R)}"})
        res.sort(key=lambda x:x["score"],reverse=True);return res
    def confidence(self,prompt:str,answer:str)->float:
        meta_cap = _meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        r=self.evaluate(prompt,[answer])
        if not r:return 0.0
        s=r[0]["score"];_,w,_=_struct(prompt,answer)
        if w<0.05:return min(s,0.25)
        return min(meta_cap, min(0.9,s)if _pn(prompt)and _pn(answer)else min(0.7,s))

