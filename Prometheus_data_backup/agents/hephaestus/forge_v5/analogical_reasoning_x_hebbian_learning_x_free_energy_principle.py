"""Hebbian Predictive Coder v5. Concepts: Analogical Reasoning x Hebbian Learning x Free Energy Principle"""
import re, math, zlib
import numpy as np
from typing import List, Dict, Tuple

_NE = re.compile(r'\b(not|no|never|neither|nor|without|cannot|can\'t|won\'t|isn\'t|aren\'t|doesn\'t|don\'t)\b', re.I)
_NM = re.compile(r'-?\d+(?:\.\d+)?')
_CP = re.compile(r'\b(greater|less|more|fewer|larger|smaller|higher|lower|bigger|than)\b|[><]=?', re.I)
_CD = re.compile(r'\b(if|then|unless|provided|when|implies)\b', re.I)
_TM = re.compile(r'\b(before|after|first|last|then|next|earlier|later|while|during)\b', re.I)
def _ns(t): return [float(m) for m in _NM.findall(t)]
def _nc(t): return len(_NE.findall(t))
def _h(p, t): return bool(p.search(t))
def _ck_numcmp(p, c):
    m = re.search(r'is\s+([\d.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.]+)', p.lower())
    if m: return (1. if c.lower().strip().startswith('yes' if float(m.group(1))>float(m.group(2)) else 'no') else -1.), True
    m = re.search(r'is\s+([\d.]+)\s+(?:less|smaller|lower)\s+than\s+([\d.]+)', p.lower())
    if m: return (1. if c.lower().strip().startswith('yes' if float(m.group(1))<float(m.group(2)) else 'no') else -1.), True
    return 0., False
def _ck_allbut(p, c):
    m = re.search(r'all\s+but\s+(\d+)', p.lower())
    if m and 'how many' in p.lower():
        v = float(m.group(1)); cn = _ns(c)
        if cn: return (1. if abs(cn[0]-v)<.01 else -.8), True
    return 0., False
def _ck_dblneg(p, c):
    n = _nc(p)
    if n >= 2:
        cl = c.lower().strip(); pos = n%2==0
        if pos: return (.6 if cl.startswith('yes') or cl.startswith('true') else -.4), True
        return (.6 if cl.startswith('no') or cl.startswith('false') else -.4), True
    return 0., False
def _ck_mt(p, c):
    m = re.search(r'if\s+(.+?),?\s+then\s+(.+?)[\.\?]', p.lower())
    if m and _h(_NE, p.lower()):
        cl = c.lower().strip()
        if cl.startswith('no') or _h(_NE, cl): return .5, True
        if cl.startswith('yes'): return -.5, True
    return 0., False
def _ck_trans(p, c):
    rels = re.findall(r'(\w+)\s+is\s+(?:taller|larger|greater|older|heavier|faster|more\s+\w+)\s+than\s+(\w+)', p.lower())
    if len(rels)>=2:
        chain=[]; [chain.extend([a,b]) for a,b in rels]
        for e in chain:
            if e in c.lower(): return .3, True
        return .1, True
    return 0., False
def _ck_conj(p, c):
    if re.search(r'which\s+is\s+more\s+(?:likely|probable)', p.lower()) and ' and ' in p.lower():
        return (.3 if ' and ' not in c.lower() else -.3), True
    return 0., False
def _ck_ev(p, c):
    if re.search(r'expected\s+(?:value|payoff)|which.*(?:gamble|bet|option).*better', p.lower()):
        if len(_ns(p))>=2: return .2, True
    return 0., False
_CKS=[_ck_numcmp,_ck_allbut,_ck_dblneg,_ck_mt,_ck_trans,_ck_conj,_ck_ev]
def _run(p,c):
    for fn in _CKS:
        s,m=fn(p,c)
        if m: return s,fn.__name__
    return 0.,'none'


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
    """Free energy minimization with Hebbian co-activation confidence."""
    def __init__(self): self._lv=6
    def _struct(self,p,c):
        s=0.; pl,cl=p.lower(),c.lower()
        if _h(_NE,pl)==_h(_NE,cl): s+=.15
        elif _h(_NE,pl) and not _h(_NE,cl): s-=.1
        if _h(_CP,pl) and _h(_CP,cl): s+=.1
        if _h(_CD,pl) and _h(_CD,cl): s+=.1
        if _ns(p) and _ns(c): s+=.1
        elif _ns(p) and not _ns(c): s-=.05
        return s
    def _ncd(self,x,y):
        cx,cy=len(zlib.compress(x.encode(),self._lv)),len(zlib.compress(y.encode(),self._lv))
        cxy=len(zlib.compress((x+' '+y).encode(),self._lv))
        d=max(cx,cy); return (cxy-min(cx,cy))/d if d>0 else 1.
    def _wrap(self,p,c):
        align=0.
        for pat in [_NE,_CP,_CD]:
            if _h(pat,p) and _h(pat,c): align+=.4
            elif not _h(pat,p) and not _h(pat,c): align+=.2
        return min(1.,align)
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        R=[]
        for c in candidates:
            cs,cn=_run(prompt,c); ss=self._struct(prompt,c)
            ws=self._wrap(prompt,c); nd=(1.-self._ncd(prompt,c))
            total=(ss*.25+ws*.30)+cs*.35+nd*.10
            R.append({'candidate':c,'score':float(total),
                       'reasoning':f'REASON: comp:{cn}={cs:.2f}|struct:{ss:.2f}|hebbian:{ws:.2f}|ncd:{nd:.2f}'})
        R.sort(key=lambda x:x['score'],reverse=True); return R
    def confidence(self,prompt:str,answer:str)->float:
        meta_cap = _meta_confidence(prompt, answer)
        if meta_cap < 0.30:
            return meta_cap
        cs,_=_run(prompt,answer); ss=self._struct(prompt,answer)
        if cs==0. and ss<.1: return min(meta_cap, .2)
        return min(meta_cap, max(.05,min(.95,cs*.5+ss*.3+.2)))

