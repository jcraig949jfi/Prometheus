"""Thermodynamic Predictive Coder v4. Concepts: Thermodynamics x Neural Plasticity x FEP"""
import re, math, zlib
import numpy as np
from typing import List, Dict, Tuple
_NE=re.compile(r'\b(not|no|never|neither|nor|without|cannot|can\'t|won\'t|isn\'t|aren\'t|doesn\'t|don\'t)\b',re.I)
_NM=re.compile(r'-?\d+(?:\.\d+)?'); _CP=re.compile(r'\b(greater|less|more|fewer|larger|smaller|higher|lower|bigger|than)\b|[><]=?',re.I)
_CD=re.compile(r'\b(if|then|unless|provided|when|implies)\b',re.I); _TM=re.compile(r'\b(before|after|first|last|then|next|earlier|later|while|during)\b',re.I)
def _ns(t): return [float(m) for m in _NM.findall(t)]
def _nc(t): return len(_NE.findall(t))
def _h(p,t): return bool(p.search(t))
def _ck_numcmp(p,c):
    m=re.search(r'is\s+([\d.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.]+)',p.lower())
    if m: return (1. if c.lower().strip().startswith('yes' if float(m.group(1))>float(m.group(2)) else 'no') else -1.),True
    m=re.search(r'is\s+([\d.]+)\s+(?:less|smaller|lower)\s+than\s+([\d.]+)',p.lower())
    if m: return (1. if c.lower().strip().startswith('yes' if float(m.group(1))<float(m.group(2)) else 'no') else -1.),True
    return 0.,False
def _ck_allbut(p,c):
    m=re.search(r'all\s+but\s+(\d+)',p.lower())
    if m and 'how many' in p.lower():
        v=float(m.group(1)); cn=_ns(c)
        if cn: return (1. if abs(cn[0]-v)<.01 else -.8),True
    return 0.,False
def _ck_dblneg(p,c):
    n=_nc(p)
    if n>=2:
        cl=c.lower().strip(); pos=n%2==0
        if pos: return (.6 if cl.startswith('yes') or cl.startswith('true') else -.4),True
        return (.6 if cl.startswith('no') or cl.startswith('false') else -.4),True
    return 0.,False
def _ck_mt(p,c):
    m=re.search(r'if\s+(.+?),?\s+then\s+(.+?)[\.\?]',p.lower())
    if m and _h(_NE,p.lower()):
        cl=c.lower().strip()
        if cl.startswith('no') or _h(_NE,cl): return .5,True
        if cl.startswith('yes'): return -.5,True
    return 0.,False
def _ck_trans(p,c):
    rels=re.findall(r'(\w+)\s+is\s+(?:taller|larger|greater|older|heavier|faster|more\s+\w+)\s+than\s+(\w+)',p.lower())
    if len(rels)>=2:
        chain=[]; [chain.extend([a,b]) for a,b in rels]
        for e in chain:
            if e in c.lower(): return .3,True
        return .1,True
    return 0.,False
def _ck_conj(p,c):
    if re.search(r'which\s+is\s+more\s+(?:likely|probable)',p.lower()) and ' and ' in p.lower():
        return (.3 if ' and ' not in c.lower() else -.3),True
    return 0.,False
def _ck_ev(p,c):
    if re.search(r'expected\s+(?:value|payoff)|which.*(?:gamble|bet|option).*better',p.lower()):
        if len(_ns(p))>=2: return .2,True
    return 0.,False
_CKS=[_ck_numcmp,_ck_allbut,_ck_dblneg,_ck_mt,_ck_trans,_ck_conj,_ck_ev]
def _run(p,c):
    for fn in _CKS:
        s,m=fn(p,c)
        if m: return s,fn.__name__
    return 0.,'none'

class ReasoningTool:
    """NCD on structural features as prediction error proxy."""
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
        pf=' '.join(w for w in p.lower().split() if _NE.search(w) or _CP.search(w) or _NM.search(w))
        cf=' '.join(w for w in c.lower().split() if _NE.search(w) or _CP.search(w) or _NM.search(w))
        if not pf: pf=p
        if not cf: cf=c
        return 1.-self._ncd(pf,cf)
    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        R=[]
        for c in candidates:
            cs,cn=_run(prompt,c); ss=self._struct(prompt,c)
            ws=self._wrap(prompt,c); nd=(1.-self._ncd(prompt,c))
            total=(ss*.25+ws*.30)+cs*.35+nd*.10
            R.append({'candidate':c,'score':float(total),
                       'reasoning':f'REASON: comp:{cn}={cs:.2f}|struct:{ss:.2f}|thermo:{ws:.2f}|ncd:{nd:.2f}'})
        R.sort(key=lambda x:x['score'],reverse=True); return R
    def confidence(self,prompt:str,answer:str)->float:
        cs,_=_run(prompt,answer); ss=self._struct(prompt,answer)
        if cs==0. and ss<.1: return .2
        return max(.05,min(.95,cs*.5+ss*.3+.2))
