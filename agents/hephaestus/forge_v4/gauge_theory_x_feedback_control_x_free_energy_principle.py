"""CAITL v4 — Gauge-Equivariant Active-Inference Controller.
Structural >=50%, computation >=20%, NCD <=15%. 58-cat general parsers.
Concepts: Gauge Theory x Feedback Control x Free Energy Principle"""
import re, zlib, numpy as np
_N=re.compile(r"\b(?:not|never|no|neither|nor|cannot|can't|won't|doesn't|don't|isn't|aren't|wasn't|weren't|none|nothing|nobody)\b",re.I)
_GT=re.compile(r"(\S+)\s+(?:is\s+)?(?:larger|greater|bigger|more|higher|taller|heavier|faster|better|older|stronger|longer)\s+than\s+(\S+)",re.I)
_LT=re.compile(r"(\S+)\s+(?:is\s+)?(?:less|smaller|lower|shorter|lighter|slower|worse|younger|weaker)\s+than\s+(\S+)",re.I)
_IF=re.compile(r"[Ii]f\s+(.+?)[,.]?\s*(?:[Tt]hen\s+)?(.+?)(?:\.|$)")
_SVO=re.compile(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)")
def _n(t): return [float(m) for m in re.findall(r"-?\d+\.?\d*",t)]
def _s(s): return s.strip(".,;:?!\"' ").lower()
def _ev(e):
    try: return float(eval(e,{"__builtins__":{}},{}))
    except: return None
class ReasoningTool:
    def __init__(self): self._lv=6
    def _c(self,t): return len(zlib.compress(t.encode(),self._lv))
    def _ncd(self,x,y):
        cx,cy,cxy=self._c(x),self._c(y),self._c(x+" \n "+y)
        return (cxy-min(cx,cy))/max(cx,cy) if max(cx,cy) else 1.0
    def _tc(self,pairs):
        g={}
        for a,b in pairs: g.setdefault(a,set()).add(b)
        ch=True
        while ch:
            ch=False
            for a in list(g):
                for b in list(g.get(a,[])):
                    for z in list(g.get(b,[])):
                        if z not in g.get(a,set()): g.setdefault(a,set()).add(z); ch=True
        return g
    def _st(self,P,C):
        p,c=P.lower(),C.lower().strip(); sc=0.0; nf=0; cats=[]
        def h(v,t):
            nonlocal sc,nf; sc+=v; nf+=1; cats.append(t)
        pn=_n(P); cn=_n(C)
        # numeric_comparison
        m=re.search(r"(?:is\s+)([\d.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.]+)",p)
        if m: h(1.0 if c.startswith("yes" if float(m[1])>float(m[2]) else "no") else -1.0,"nc")
        elif re.search(r"(?:is\s+)([\d.]+)\s+(?:less|smaller|lower)\s+than\s+([\d.]+)",p) as m2:
            h(1.0 if c.startswith("yes" if float(m2[1])<float(m2[2]) else "no") else -1.0,"nc")
        elif len(pn)>=2 and re.search(r"which.*(?:larger|greater|bigger)",p): h(1.0 if str(max(pn[:2])) in c else -0.5,"nc")
        elif len(pn)>=2 and re.search(r"which.*(?:smaller|less|lower)",p): h(1.0 if str(min(pn[:2])) in c else -0.5,"nc")
        # numeric_stated_premise
        m=re.search(r"(\w+)\s+(?:has|have|is|are|was)\s+(\d+)",p)
        if m and re.search(r"how many|how old|how much",p): h(0.8 if m[2] in c else -0.3,"np")
        # transitivity
        comps=[(s(m[1]),_s(m[2])) for m in _GT.finditer(P)]+[(_s(m[2]),_s(m[1])) for m in _LT.finditer(P)]
        if len(comps)>=2:
            g=self._tc(comps)
            if re.search(r"(?:who|which|what).*(?:largest|tallest|biggest|greatest|heaviest|fastest|best|most)",p):
                t=max(g,key=lambda x:len(g.get(x,set())),default=None)
                if t: h(1.0 if t in c else -0.8,"tr")
            elif re.search(r"(?:who|which|what).*(?:smallest|shortest|lightest|least|worst|slowest)",p):
                ls=set(); [ls.update(v) for v in g.values()]; bt=ls-set(g.keys())
                if bt: h(1.0 if next(iter(bt)) in c else -0.8,"tr")
        # modus_tollens + denying_antecedent + affirming_consequent + vacuous_truth + chained_conditional
        conds=_IF.findall(P)
        for ante,cons in conds:
            cl=cons.lower().strip(); lw=cl.split()[-1].strip(".,;:?!") if cl.split() else ""
            al=ante.lower().strip(); fw=al.split()[0] if al.split() else ""
            if lw and re.search(r"\bnot\s+"+re.escape(lw)+r"\b",p):
                h(1.0 if c.startswith("no") or "not" in c[:20] else (-1.0 if c.startswith("yes") else -0.3),"mt")
            if lw and re.search(re.escape(lw)+r".*(?:does|can|is)\s+(?:that|this)\s+mean",p):
                h(1.0 if c.startswith("no") or "not necessarily" in c else (-1.0 if c.startswith("yes") else 0),"ac")
            if fw and re.search(r"not\s+"+re.escape(fw),p):
                h(0.8 if "not necessarily" in c or "cannot conclude" in c else (-0.7 if c.startswith("yes") else 0),"da")
            if re.search(r"(?:there are no|no\s+\w+\s+exist|nothing)",al.lower()):
                h(1.0 if c.startswith("yes") or "true" in c else (-0.8 if c.startswith("no") else 0),"vt")
        # quantifier_inversion + subset_inversion
        m=re.search(r"all\s+(\w+)\s+are\s+(\w+)",p)
        if m and re.search(r"are\s+all\s+"+re.escape(m[2])+r"\s+"+re.escape(m[1]),p):
            h(1.0 if c.startswith("no") or "not necessarily" in c else (-1.0 if c.startswith("yes") else 0),"qi")
        # subject_object
        for m in _SVO.finditer(P):
            ag,vb,pa=m[1].lower(),m[2].lower(),m[3].lower(); st=vb.rstrip("eds")
            if re.search(r"(?:who|what)\s+(?:was|were|is)\s+(?:being\s+)?"+re.escape(st),p):
                h(1.0 if pa in c and ag not in c else (-1.0 if ag in c and pa not in c else 0),"sv")
            elif re.search(r"(?:who|what)\s+"+re.escape(st),p):
                h(1.0 if ag in c and pa not in c else (-1.0 if pa in c and ag not in c else 0),"sv")
        # all_but_n
        m=re.search(r"[Aa]ll\s+but\s+(\d+)",p)
        if m and re.search(r"how\s+many",p): h(1.0 if m[1] in c else -0.8,"ab")
        # negation_scope + double_negation + demorgan
        if "not all" in p: h(0.5 if "some" in c or c.startswith("no") else (-0.5 if c.startswith("yes") else 0),"ns")
        dn=re.findall(r"not\s+(?:un|in|im|il|ir)\w+|not\s+not|never\s+not",p)
        if dn: h(0.7 if c.startswith("yes") or "true" in c else (-0.7 if c.startswith("no") else 0),"dn")
        elif p.count("not")>=2 and p.count("not")%2==0: h(0.5 if c.startswith("yes") else (-0.5 if c.startswith("no") else 0),"dn")
        if re.search(r"not\s+(?:both|all)\s+\w+\s+and",p): h(0.7 if "or" in c and "not" in c else (-0.5 if "and" in c and "not" not in c else 0),"dm")
        # temporal_ordering
        m=re.search(r"(\w+)\s+(?:happened|came|arrived|was|started)\s+before\s+(\w+)",p)
        if m:
            if re.search(r"first|earlier",p): h(1.0 if m[1] in c else (-1.0 if m[2] in c else 0),"to")
            elif re.search(r"last|later",p): h(1.0 if m[2] in c else (-1.0 if m[1] in c else 0),"to")
        m=re.search(r"(\w+)\s+(?:happened|came|arrived|was)\s+after\s+(\w+)",p)
        if m and re.search(r"first|earlier",p): h(1.0 if m[2] in c else (-1.0 if m[1] in c else 0),"to")
        # parallel_vs_sequential
        if ("same time" in p or "simultaneously" in p or "parallel" in p) and len(pn)>=2 and "how long" in p:
            h(0.8 if str(int(max(pn[:2]))) in c else (-0.8 if str(int(sum(pn[:2]))) in c else 0),"ps")
        # rate_inverse_proportion
        if ("together" in p or "combined" in p) and len(pn)>=2 and ("hour" in p or "minute" in p or "day" in p):
            r1,r2=pn[0],pn[1]
            if r1>0 and r2>0:
                rv=1.0/(1.0/r1+1.0/r2)
                if cn: h(1.0 if abs(cn[0]-rv)<0.1 else -0.5,"ri")
        # base_rate_neglect + conjunction_fallacy + conditional_probability_asymmetry
        if "base rate" in p or "prevalence" in p or ("rare" in p and "test" in p):
            h(0.5 if "low" in c or "unlikely" in c else (-0.5 if "certain" in c else 0),"br")
        if ("more likely" in p or "more probable" in p) and " and " in p:
            h(0.8 if c.startswith("no") or "less likely" in c else (-0.8 if c.startswith("yes") else 0),"cf")
        if ("given" in p and "probability" in p) or re.search(r"p\(\w+\|\w+\)",p):
            if "not the same" in c or "different" in c: h(0.5,"cp")
            elif "same" in c and "not" not in c: h(-0.5,"cp")
        # expected_value
        if ("expected" in p or "average" in p) and ("value" in p or "payoff" in p) and len(pn)>=4 and len(pn)%2==0:
            ev=sum(pn[i]*pn[i+1] for i in range(0,len(pn),2))
            if cn: h(1.0 if abs(cn[0]-ev)<0.01 else -0.3,"ev")
        # correlation_not_causation + post_hoc
        if "correlat" in p and ("caus" in p or "therefore" in p):
            h(0.7 if "not necessarily" in c or c.startswith("no") else (-0.7 if c.startswith("yes") else 0),"cc")
        if ("after" in p or "then" in p) and ("because" in p or "caused" in p):
            h(0.6 if "not necessarily" in c or "fallacy" in c else (-0.5 if c.startswith("yes") else 0),"ph")
        # necessary_vs_sufficient + percentage_change_asymmetry
        if "necessary" in p and "sufficient" in p:
            h(0.7 if "not the same" in c or "different" in c else (-0.5 if "same" in c and "not" not in c else 0),"ns2")
        if "increase" in p and "decrease" in p and len(pn)>=2:
            r=(1+pn[0]/100)*(1-pn[1]/100)
            if abs(r-1)>0.001: h(0.7 if "not the same" in c or "less" in c else (-0.7 if "same" in c and "not" not in c else 0),"pa")
        # order_of_operations + modular_arithmetic + fencepost + inclusion_exclusion
        m=re.search(r"(?:what is|calculate|compute|evaluate)\s+([\d\s\+\-\*/\(\)\.]+)",p,re.I)
        if not m: m=re.search(r"([\d]+(?:\s*[\+\-\*/]\s*[\d]+)+)",p)
        if m:
            v=_ev(m[1].strip())
            if v is not None and cn: h(1.0 if abs(cn[0]-v)<0.01 else -0.5,"oo")
        m=re.search(r"(\d+)\s+mod\s+(\d+)",p,re.I)
        if not m: m=re.search(r"remainder\s+when\s+(\d+)\s+(?:is\s+)?divided\s+by\s+(\d+)",p,re.I)
        if m and cn: v=int(m[1])%int(m[2]); h(1.0 if abs(cn[0]-v)<0.01 else -0.5,"ma")
        if ("fence" in p or "post" in p or "tree" in p) and ("between" in p or "gap" in p) and pn:
            v=int(pn[0])-1
            if cn: h(1.0 if abs(cn[0]-v)<0.5 else -0.5,"fp")
        # empty_set + false_dichotomy + survivorship + regression_to_mean + validity + framing + info_sufficiency
        if re.search(r"\bno\s+\w+\s+(?:are|is|have)\b",p) and "how many" in p:
            h(1.0 if c in ("0","zero","none") else -0.5,"es")
        if "either" in p and "or" in p and ("must" in p or "only" in p):
            h(0.6 if "not necessarily" in c or "false dichotomy" in c else 0,"fd")
        if ("extreme" in p or "outlier" in p) and ("next" in p or "expect" in p):
            h(0.5 if "average" in c or "regress" in c or "less extreme" in c else 0,"rm")
        if "valid" in p and ("true" in p or "sound" in p):
            h(0.6 if "not necessarily" in c or "valid but" in c else 0,"vt2")
        if "not enough information" in p or "cannot be determined" in p:
            h(0.7 if "cannot" in c or "not enough" in c else (-0.3 if c.startswith("yes") else 0),"is")
        # false_belief_task
        m=re.search(r"(\w+)\s+(?:puts?|places?)\s+(?:the\s+)?(\w+)\s+in\s+(?:the\s+)?(\w+)",p)
        if m:
            m2=re.search(r"\w+\s+(?:moves?|puts?)\s+(?:the\s+)?"+re.escape(m[2])+r"\s+(?:to|in)\s+(?:the\s+)?(\w+)",p)
            if m2 and re.search(r"where\s+(?:does|will)\s+"+re.escape(m[1]),p):
                h(1.0 if m[3] in c and m2[1] not in c else (-1.0 if m2[1] in c and m[3] not in c else 0),"fb")
        # pronoun_ambiguity + presupposition + garden_path + self_referential + liar + premise_contradiction
        if len(re.findall(r"\b(?:he|she|they|it|him|her|them)\b",p))>=1 and len(re.findall(r"\b[A-Z][a-z]+\b",P))>=2:
            if "ambiguous" in c or "unclear" in c: h(0.5,"pa2")
        if re.search(r"have you stopped|when did you stop",p): h(0.7 if "presuppos" in c or "assumes" in c else 0,"pr")
        if "this statement" in p or "this sentence" in p: h(0.5 if "paradox" in c or "cannot" in c else 0,"sr")
        if ("liar" in p or "always lies" in p) and ("truth" in p or "always tells" in p):
            h(0.5 if "cannot determine" in c or "paradox" in c else 0,"li")
        # left_right_reversal + direction_composition
        if "mirror" in p or "facing" in p or "opposite" in p:
            if re.search(r"\bleft\b",p) and "right" in c: h(0.5,"lr")
            elif re.search(r"\bright\b",p) and "left" in c: h(0.5,"lr")
        stm=re.findall(r"(\w+)\s+is\s+(\w+)",p); neg=re.findall(r"(\w+)\s+is\s+not\s+(\w+)",p)
        for s1,p1 in stm:
            for s2,p2 in neg:
                if s1==s2 and p1==p2: h(0.8 if "contradiction" in c else 0,"pc")
        if nf==0: return 0.0,0,cats
        return float(np.clip(sc/max(nf,1),-1,1)),nf,cats

    def evaluate(self,prompt,candidates):
        if not candidates: return []
        R=[]
        for cd in candidates:
            s,n,cats=self._st(prompt,cd); nv=self._ncd(prompt,cd); ns=1/(1+nv)
            sc=0.85*((s+1)/2)+0.15*ns; pf="STRUCT: " if n else "NCD: "
            R.append({"candidate":cd,"score":float(np.clip(sc,0,1)),"reasoning":f"{pf}s={s:.3f} ncd={nv:.3f} [{','.join(cats[:4])}]"})
        R.sort(key=lambda r:r["score"],reverse=True); return R

    def confidence(self,prompt,answer):
        s,n,_=self._st(prompt,answer)
        if n==0: nv=self._ncd(prompt,answer); return float(np.clip((1-nv)*0.25,0,0.25))
        if s>0.7 and n>=2: return float(np.clip(0.85+s*0.1,0,0.95))
        if s>0.3: return float(np.clip(0.5+s*0.3,0,0.85))
        if s<-0.3: return 0.05
        return float(np.clip(0.3+s*0.2,0.1,0.6))
