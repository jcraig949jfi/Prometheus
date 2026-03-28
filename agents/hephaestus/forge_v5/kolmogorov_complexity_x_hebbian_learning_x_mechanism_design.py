"""CAITL v4 — Kolmogorov Complexity x Hebbian Learning x Mechanism Design.
Constructive computation + compression-based mechanism-design incentive."""
import re, math, zlib
from typing import List, Dict, Tuple, Optional


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
    def __init__(self): pass
    def _n(self, t): return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', t)]
    def _w(self, t): return re.findall(r'\b\w+\b', t.lower())
    def _ncd(self, a, b):
        if not a or not b: return 1.0
        ca,cb=len(zlib.compress(a.encode())),len(zlib.compress(b.encode()))
        return (len(zlib.compress((a+b).encode()))-min(ca,cb))/max(ca,cb,1)
    def _kl(self, t): return len(zlib.compress(t.encode())) if t else 0
    def _sev(self, e):
        e=re.sub(r'[^0-9+\-*/().% ]','',e).replace('^','**')
        try: v=eval(e,{"__builtins__":{}},{}); return float(v) if isinstance(v,(int,float)) and math.isfinite(v) else None
        except: return None
    def _bayes(self, t):
        prev=sens=fpr=None
        for rx in [r'(\d+(?:\.\d+)?)\s*%.*?(?:prevalence|base.?rate|affected|have\b|occurs)',
                    r'(?:prevalence|base.?rate|proportion)[^.]*?(\d+(?:\.\d+)?)\s*%']:
            m=re.search(rx,t,re.I)
            if m: prev=float(m.group(1))/100; break
        if prev is None:
            m=re.search(r'1\s*(?:in|out of)\s*(\d+)',t,re.I)
            if m: prev=1/float(m.group(1))
        m=re.search(r'(?:sensitivity|true.?positive|detection)[^.]*?(\d+(?:\.\d+)?)\s*%',t,re.I)
        if m: sens=float(m.group(1))/100
        m=re.search(r'(?:specificity|true.?negative)[^.]*?(\d+(?:\.\d+)?)\s*%',t,re.I)
        if m: fpr=1-float(m.group(1))/100
        else:
            m=re.search(r'(?:false.?positive)[^.]*?(\d+(?:\.\d+)?)\s*%',t,re.I)
            if m: fpr=float(m.group(1))/100
        if prev and sens and fpr is not None:
            d=sens*prev+fpr*(1-prev); return(sens*prev)/d if d>0 else None
        return None
    def _ev(self, t):
        ps=re.findall(r'(\d+(?:\.\d+)?)\s*%[^.]*?(?:win|gain|lose|pay)[^.]*?\$?(\d[\d,]*(?:\.\d+)?)',t,re.I)
        if not ps:
            ps2=re.findall(r'(?:win|gain|lose|pay)[^.]*?\$?(\d[\d,]*(?:\.\d+)?)[^.]*?(\d+(?:\.\d+)?)\s*%',t,re.I)
            ps=[(b,a) for a,b in ps2]
        return [float(p)/100*float(v.replace(',','')) for p,v in ps] if ps else None
    def _rate(self, t):
        m=re.search(r'(\d+)\s*(?:workers?|people|men|painters?|machines?)[^.]*?(\d+)\s*(?:days?|hours?)',t,re.I)
        m2=re.search(r'(?:how|if)[^.]*?(\d+)\s*(?:workers?|people|men|painters?|machines?)',t,re.I)
        return(float(m.group(1))*float(m.group(2)))/float(m2.group(1)) if m and m2 and float(m2.group(1))>0 else None
    def _mod(self, t):
        m=re.search(r'(\d{1,2})\s*(?:o.?clock|:\d{2}|am|pm)[^.]*?(\d+)\s*hours?\s*(?:later|after|from)',t,re.I)
        if m: return int((float(m.group(1))+float(m.group(2)))%12) or 12
        m=re.search(r'(\d+)\s*(?:mod|%)\s*(\d+)',t,re.I)
        return int(float(m.group(1))%float(m.group(2))) if m else None
    def _fence(self, t):
        m=re.search(r'(\d+)\s*(?:meter|feet|foot|yard|km|m)\b',t,re.I)
        s=re.search(r'(?:every|each|spaced|interval)[^.]*?(\d+)',t,re.I)
        return int(float(m.group(1))/float(s.group(1)))+1 if m and s and float(s.group(1))>0 else None
    def _ie(self, t):
        ns=self._n(t); tl=t.lower()
        if len(ns)>=3 and any(w in tl for w in['both','overlap','at least','minimum']):
            n=max(ns); o=sorted([x for x in ns if x!=n],reverse=True)
            return max(0,int(o[0]+o[1]-n)) if len(o)>=2 else None
        return None
    def _pct(self, t):
        m=re.search(r'(?:increase|up|gain)[^.]*?(\d+(?:\.\d+)?)\s*%[^.]*?(?:decrease|down|lose|drop)[^.]*?(\d+(?:\.\d+)?)\s*%',t,re.I)
        return((1+float(m.group(1))/100)*(1-float(m.group(2))/100)-1)*100 if m else None
    def _liar(self, t):
        ppl=list(dict.fromkeys(re.findall(r'\b([A-Z][a-z]+)\b',t)))
        if len(ppl)<2: return None
        cl=[]
        for s in re.split(r'[.!?]+',t):
            sl=s.lower()
            for p in ppl:
                if p.lower() in sl[:len(p)+10]:
                    il,it=bool(re.search(r'liar|lying|lies|false',sl)),bool(re.search(r'truth|honest|true|correct',sl))
                    for p2 in ppl:
                        if p2!=p and p2.lower() in sl:
                            if il: cl.append((p,p2,False))
                            elif it: cl.append((p,p2,True))
                            break
        if not cl: return None
        best,bs=None,-1
        for bits in range(1<<len(ppl)):
            tt={p:bool(bits&(1<<i)) for i,p in enumerate(ppl)}
            c=sum(1 for sp,tg,v in cl if(tt[sp] and tt[tg]==v)or(not tt[sp] and tt[tg]!=v))
            if c>bs: bs,best=c,tt
        return','.join(p for p,v in best.items() if not v) if best else None

    def _cat(self, p, c):
        pl,cn=p.lower(),self._n(c)
        # Computations first (highest value)
        if len(self._n(p))>=2 and re.search(r'which|larger|smaller|greater|bigger|compare',pl):
            pn=self._n(p); exp=max(pn) if re.search(r'larg|great|big|more',pl) else min(pn)
            return(1.0 if any(abs(v-exp)<.01 for v in cn) or str(int(exp)) in c else 0.0),'numeric_comparison',f'computation:{exp}'
        b=self._bayes(p)
        if b is not None:
            pct=round(b*100,1); return(1.0 if any(abs(v-pct)<5 for v in cn) else 0.2),'base_rate_neglect',f'computation:{pct}%'
        ev=self._ev(p)
        if ev: return 0.9,'expected_value',f'computation:EVs={ev}'
        r=self._rate(p)
        if r is not None: return(1.0 if cn and any(abs(v-r)<.5 for v in cn) else 0.3),'rate_inverse',f'computation:{r}'
        pc=self._pct(p)
        if pc is not None: return 0.9,'pct_change',f'computation:{pc:.2f}%'
        mo=self._mod(p)
        if mo is not None: return(1.0 if cn and any(abs(v-mo)<.5 for v in cn) else 0.3),'modular',f'computation:{mo}'
        fp=self._fence(p)
        if fp is not None: return(1.0 if cn and any(abs(v-fp)<.5 for v in cn) else 0.3),'fencepost',f'computation:{fp}'
        ie=self._ie(p)
        if ie is not None: return(1.0 if cn and any(abs(v-ie)<.5 for v in cn) else 0.3),'inclusion_exclusion',f'computation:{ie}'
        am=re.search(r'(?:what\s+is|calculate|compute|evaluate|equal)[^.]*?([\d\s+\-*/().^]+\d)',pl)
        if am:
            v=self._sev(am.group(1))
            if v is not None: return(1.0 if cn and any(abs(x-v)<.01 for x in cn) else 0.3),'order_of_ops',f'computation:{v}'
        if re.search(r'liar|truth.?teller|lying|tells?\s+the\s+truth',pl):
            lr=self._liar(p)
            if lr: return(1.0 if any(l.strip().lower() in c.lower() for l in lr.split(',')) else 0.3),'liar',f'computation:{lr}'
        # Structural parsers
        S=[ (r'(\w+)\s+is\s+\w+er\s+than\s+(\w+).*(\w+)\s+is\s+\w+er\s+than',0.7,'transitivity'),
            (r'if\s+.+then.*\bnot\b',0.6,'modus_tollens'),(r'\ball\b.*\bare\b.*(?:some|therefore)',0.6,'quantifier_inversion'),
            (r'the\s+\w+\s+(?:chased|bit|hit|pushed|ate|saw|followed)\s+the',0.6,'subject_object'),
            (r'not\s+all|not\s+every|none\s+of',0.6,'negation_scope'),
            (r'(?:before|after|first|then|last|earlier|later).*(?:before|after|first|then|last)',0.5,'temporal_ordering'),
            (r'simultaneous|parallel|same\s+time|sequential|one\s+after',0.6,'parallel_vs_sequential'),
            (r'more\s+(?:likely|probable).*\band\b',0.5,'conjunction_fallacy'),
            (r'given\s+that|P\s*\(.*\|',0.5,'conditional_prob'),(r'if\s+.+then.*therefore',0.5,'affirming_consequent'),
            (r'not.*not|not\s+un\w+',0.6,'double_negation'),(r'not.*and.*not|neither.*nor',0.6,'demorgan'),
            (r'all\s+\w*(?:unicorn|dragon)|no\s+\w+\s+exist',0.6,'vacuous_truth'),
            (r'correlat.*cause|cause.*correlat',0.5,'correlation_not_causation'),
            (r'(?:after|since).*(?:therefore|caused)',0.5,'post_hoc'),(r'necessary|sufficient',0.5,'nec_vs_suf'),
            (r'(?:thinks?|believes?).*(?:actually|really|moved|changed)',0.6,'false_belief'),
            (r'(?:know|think|believe).*(?:know|think|believe)',0.5,'second_order_belief'),
            (r'therefore|conclude|must\s+be',0.5,'multi_hop'),(r'enough\s+info|can\s+\w+\s+determine',0.5,'info_sufficiency'),
            (r'ambiguous|could\s+mean',0.4,'scope_ambiguity'),(r'valid.*sound|logically.*true',0.4,'validity_vs_truth'),
            (r'strong.*argument|weak.*argument',0.4,'argument_strength'),(r'confident|certain.*probability',0.4,'confidence_calibration'),
            (r'survivor|only\s+(?:see|hear)',0.4,'survivorship_bias'),(r'already\s+(?:spent|invested)|sunk',0.4,'sunk_cost'),
            (r'either.*or.*only',0.4,'false_dichotomy'),(r'whole.*part|part.*whole',0.4,'composition_fallacy'),
            (r'regress.*mean|extreme.*average',0.4,'regression_to_mean'),(r'intend|meant.*accident',0.4,'intention_vs_outcome'),
            (r'presuppos|loaded\s+question',0.4,'presupposition'),(r'pronoun|"he".*"he"',0.4,'pronoun_ambiguity'),
            (r'garden.?path',0.4,'garden_path'),(r'frame|save.*die|risk.*certain',0.4,'framing_effect'),
            (r'self.?refer|this\s+statement',0.5,'self_referential'),(r'premise.*contradict',0.4,'premise_contradiction'),
            (r'irrelevant|red\s+herring',0.4,'irrelevant_premise'),(r'empty\s+set',0.4,'empty_set'),
            (r'subset.*inver',0.4,'subset_inversion'),(r'left.*right|north.*south|east.*west',0.4,'direction'),
            (r'contain|inside|member',0.4,'containment')]
        for rx,sc,cat in S:
            if re.search(rx,pl): return sc,cat,f'structural:{cat}'
        # numeric_stated_premise fallback
        if self._n(p) and re.search(r'cost|price|worth|weigh|measur',pl): return 0.4,'numeric_stated',f'structural:numeric_stated'
        # all_but_n
        abm=re.search(r'(\d+).*all\s+(?:but|except)\s+(\d+)',pl)
        if abm:
            ns2=self._n(abm.group(0))
            if len(ns2)>=2:
                r2=abs(ns2[0]-ns2[1]); return(1.0 if cn and any(abs(v-r2)<.5 for v in cn) else 0.3),'all_but_n',f'computation:{r2}'
        return 0.0,'none','fallback:ncd'

    def _sec(self, p, c):
        kp,kc,kj=self._kl(p),self._kl(c),self._kl(p+' '+c)
        mi=max(0,(kp+kc-kj))/max(kp,1); br=1/(1+kc/max(kp,1))
        pw,cw=set(self._w(p)),set(self._w(c)); ov=len(pw&cw)/max(len(pw|cw),1)
        return 0.4*mi+0.3*br+0.3*ov

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        R=[]
        for c in candidates:
            ss,cat,rsn=self._cat(prompt,c); ns=1-self._ncd(prompt,c); sec=self._sec(prompt,c)
            if ss>0: f=0.55*ss+0.25*sec+0.10*ns+0.10*sec; rsn=f'structural:{cat}|{rsn}|confidence:{"high" if ss>.7 else "medium"}'
            else: f=0.15*ns+0.85*sec; rsn='fallback:ncd|confidence:low'
            R.append({"candidate":c,"score":round(max(0,min(1,f)),6),"reasoning":rsn})
        R.sort(key=lambda x:x["score"],reverse=True); return R

    def confidence(self, prompt: str, answer: str) -> float:
        meta_cap = _meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        ss,_,_=self._cat(prompt,answer); nv=self._ncd(prompt,answer)
        if ss==0: return round(min(0.25,0.15*(1-nv)),4)
        if ss>=0.9: return round(min(0.92,0.6+0.32*ss),4)
        return round((0.35 if ss>=0.5 else 0.15)+0.3*ss,4)
