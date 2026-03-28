"""Chaos Theory x Error Correcting Codes x Type Theory. Frame C: Dynamics Tracker.
Chaotic perturbation testing (score stability under noise), Hamming-distance redundancy
across multiple independent scoring channels, type-checking prompt structure.
Score: computation(45%) + structural(35%) + NCD tiebreaker(20% max)."""
import re, math, zlib, numpy as np
from typing import List, Dict
_N=re.compile(r"[-+]?\d*\.?\d+"); _D=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']; _C=['north','east','south','west']
def _n(t): return [float(m) for m in _N.findall(t)]
def _h(t,*w): l=t.lower(); return any(x in l for x in w)
def _f(t): m=re.match(r'\s*([a-z]+)',t.lower()); return m.group(1) if m else ''

class ReasoningTool:
    def _perturbation_stability(self,p,c,base):
        if base is None: return 0.5
        ws=c.split()
        if len(ws)<2: return 0.8
        scores=[base]
        s1,_=self._s(p,' '.join(ws[:-1]));scores.append(s1 if s1 is not None else .5)
        s2,_=self._s(p,ws[0]+' '+c);scores.append(s2 if s2 is not None else .5)
        s3,_=self._s(p,c.swapcase());scores.append(s3 if s3 is not None else .5)
        return 1.0-min(max(scores)-min(scores),1.0)

    def _ecc_hamming(self,p,c):
        pl,cl=p.lower(),c.lower();pw=set(re.findall(r'\b[a-z]{3,}\b',pl));cw=set(re.findall(r'\b[a-z]{3,}\b',cl))
        ch1=1 if len(pw&cw)/max(len(pw),1)>.15 else 0
        ents=set(re.findall(r'\b[A-Z][a-z]+\b',p));ch2=1 if any(e.lower() in cl for e in ents) else 0
        pn,cn=_n(p),_n(c);ch3=1 if(pn and cn and any(abs(a-b)<.5 for a in pn for b in cn))else 0
        ch4=1 if 1<=len(c.split())<=50 else 0;ch5=1 if self._type_check(p,c)<.1 else 0
        bits=[ch1,ch2,ch3,ch4,ch5];hw=sum(bits);conf=hw/len(bits)
        if hw>=4: conf=min(conf*1.1,1.0)
        return conf,bits

    def _type_check(self,p,c):
        pl,fw=p.lower(),_f(c); pen=0.0
        if _h(pl,'how many','how old','how far','how long') and not _n(c): pen+=.15
        if re.search(r'^(is|are|was|were|do|does|did|can|could|will|would|should)\s',pl) and fw not in('yes','no','true','false','it','the','not','neither'): pen+=.1
        if _h(pl,'who ') and not re.search(r'[A-Z][a-z]',c) and not _h(c,'no one','nobody','everyone','the'): pen+=.08
        return min(pen,.3)

    def _s(self,p,c):
        ns=_n(p);pl=p.lower();cn=_n(c);cl=c.lower();fw=_f(c)
        if _h(p,'which is','greater','larger','smaller','less than','more than','bigger') and len(ns)>=2 and cn:
            t=max(ns) if _h(p,'great','larg','big','more') else min(ns); return(0.9 if abs(cn[0]-t)<1e-9 else 0.1),'numeric'
        if _h(p,'cost','total','together') and _h(p,'more than') and len(ns)>=2:
            a=(ns[0]-ns[1])/2
            if cn: return(0.92 if abs(cn[0]-a)<.01 else(0.1 if abs(cn[0]-ns[1])<.01 else 0.3)),'bat_ball'
        if _h(p,'all but','all except') and len(ns)>=2: return(0.9 if cn and abs(cn[0]-int(min(ns)))<.5 else 0.15),'all_but'
        pr=re.findall(r'(\w+)\s+is\s+(?:taller|faster|older|bigger|heavier|stronger|shorter|slower)\s+than\s+(\w+)',pl)
        if len(pr)>=2:
            g={}
            for a,b in pr: g.setdefault(a,set()).add(b)
            ch=True
            while ch:
                ch=False
                for a in list(g):
                    for b in list(g.get(a,[])):
                        for bb in list(g.get(b,[])):
                            if bb not in g.get(a,set()): g.setdefault(a,set()).add(bb);ch=True
            an=set();[an.update([a]+list(v)) for a,v in g.items()]
            for a in an:
                if a in cl and not any(a in g.get(x,set()) for x in an if x!=a):
                    if _h(p,'tallest','fastest','oldest','biggest','heaviest','strongest'): return 0.88,'trans'
            return 0.3,'trans'
        m=re.search(r'if\s+(.+?)\s*,?\s*then\s+(.+?)\.',pl)
        if m and _h(p,'not','no ','never',"don't","doesn't"):
            if _h(c,'not') or fw=='no': return 0.85,'mt'
            if fw in('yes','true'): return 0.1,'mt'
        if re.search(r'not\s+all\s+\w+\s+are',pl):
            if _h(c,'cannot determine','insufficient','not enough','uncertain'): return 0.88,'neg'
            if fw in('yes','no','true','false'): return 0.15,'neg'
        sm=re.search(r'(\w+)\s+(gave|told|sent|passed|handed)\s+(?:\w+\s+)?(?:to\s+)?(\w+)',pl)
        if sm and _h(p,'who'):
            if _h(p,'who '+sm.group(2),'who gave','who told') and sm.group(1) in cl: return 0.88,'svo'
            if _h(p,'receive','got','to whom') and sm.group(3) in cl: return 0.88,'svo'
        if _h(p,'preva','base rate','1 in','sensitivity') and len(ns)>=2:
            pv=min(ns)/100 if min(ns)>1 else min(ns)
            if pv>.5: pv=.01
            se=max(x for x in ns if x<=100)/100;po=(se*pv)/(se*pv+(1-se)*(1-pv)) if(se*pv+(1-se)*(1-pv))>0 else .5
            if cn:
                cp=cn[0]/100 if cn[0]>1 else cn[0]
                if abs(cp-po)<.15: return 0.8,'bayes'
            if _h(c,'low','unlikely') and po<.3: return 0.75,'bayes'
        be=re.findall(r'(\w+)\s+(?:before|earlier than|prior to)\s+(\w+)',pl);af=re.findall(r'(\w+)\s+(?:after|later than|following)\s+(\w+)',pl)
        ed=[(a,b) for a,b in be]+[(b,a) for a,b in af]
        if ed:
            nd=set();[nd.update([a,b]) for a,b in ed];ig={x:0 for x in nd};aj={x:[] for x in nd}
            for a,b in ed: aj[a].append(b);ig[b]+=1
            q=sorted(x for x in nd if ig[x]==0);od=[]
            while q:
                x=q.pop(0);od.append(x)
                for nb in aj[x]: ig[nb]-=1;(q.append(nb) if ig[nb]==0 else None)
                q.sort()
            tg=od[0] if _h(p,'first','earliest') else(od[-1] if _h(p,'last','latest') else None)
            if tg and tg in cl: return 0.9,'topo'
            if tg: return 0.2,'topo'
        rl=re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)',pl);st=re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+old',pl)
        if rl:
            kn={x:int(a) for x,a in st}
            for _ in range(10):
                for a,d,r2,b in rl:
                    d2=int(d)
                    if b in kn and a not in kn: kn[a]=kn[b]+d2 if r2=='older' else kn[b]-d2
                    if a in kn and b not in kn: kn[b]=kn[a]-d2 if r2=='older' else kn[a]+d2
            tg=re.search(r'how old (?:is|was) (\w+)',pl)
            if tg and tg.group(1) in kn: return(0.92 if cn and abs(cn[0]-kn[tg.group(1)])<.5 else 0.1),'age'
        if _h(p,'same time','simultaneous','parallel','together','at once'):
            ts=[int(x) for x in re.findall(r'(\d+)\s*(?:min|hour|second|minute)',pl)]
            if ts:
                a2=max(ts) if _h(p,'total','all done','finish') else min(ts)
                if cn and abs(cn[0]-a2)<.5: return 0.88,'conc'
        fm=re.search(r'fac(?:e|ing)\s+(north|south|east|west)',pl)
        if fm:
            ix=_C.index(fm.group(1))
            for t in re.findall(r'turn\s+(left|right)',pl): ix=(ix+1)%4 if t=='right' else(ix-1)%4
            return(0.9 if _C[ix] in cl else 0.1),'dir'
        if _h(p,'facing','across','opposite') and _h(p,'left','right'):
            if re.search(r'(?:raise|lift|hold)s?\s+(?:his|her|their)?\s*left',pl) and 'right' in cl: return 0.88,'lr'
            if re.search(r'(?:raise|lift|hold)s?\s+(?:his|her|their)?\s*right',pl) and 'left' in cl: return 0.88,'lr'
        if _h(p,'fence','post','tree','pole','plant','along') and len(ns)>=2:
            ln,sp=max(ns),min(ns)
            if sp>0 and cn and abs(cn[0]-(ln/sp+1))<.5: return 0.9,'fence'
        if _h(p,"o'clock",'clock','hour','modulo') and len(ns)>=2:
            a2=((int(ns[0])+int(ns[1])-1)%12)+1
            if cn and abs(cn[0]-a2)<.5: return 0.9,'mod'
        if _h(p,'coin','flip','toss') and _h(p,'independent','next flip','fair') and _h(c,'50','1/2','0.5','half'): return 0.9,'coin'
        if _h(p,'guarantee','worst case','minimum number','sock','drawer') and len(ns)>=2:
            if cn and abs(cn[0]-(int(max(ns))+1))<.5: return 0.88,'pig'
        if _h(p,'odd','even','parity'):
            ni=[int(x) for x in re.findall(r'\b(\d+)\b',p)]
            if ni:
                v=ni[-1] if len(ni)==1 else sum(ni)
                if v%2==0 and _h(c,'even'): return 0.85,'par'
                if v%2==1 and _h(c,'odd'): return 0.85,'par'
        if _h(p,'yesterday','tomorrow','day after','day before'):
            dm=re.search(r'today is (\w+day)',pl)
            if dm:
                ix=next((i for i,d in enumerate(_D) if d==dm.group(1)),-1)
                if ix>=0:
                    of=len(re.findall(r'tomorrow|day after',pl))-len(re.findall(r'yesterday|day before',pl))
                    if _D[(ix+of)%7] in cl: return 0.9,'day'
                    return 0.15,'day'
        ti=re.findall(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',pl)
        if len(ti)>=4 and _h(p,'conflict','overlap','both','attend'):
            def tm(h,mi,ap): h=int(h);mi=int(mi) if mi else 0;h+=(12 if ap=='pm' and h!=12 else(-12 if ap=='am' and h==12 else 0));return h*60+mi
            rg=[]
            for i in range(0,len(ti)-1,2): s2,e2=tm(*ti[i]),tm(*ti[i+1]);rg.append((s2,e2+1440*(e2<s2)))
            ov=len(rg)>=2 and rg[0][0]<rg[1][1] and rg[1][0]<rg[0][1]
            if ov and _h(c,'yes','conflict','cannot'): return 0.88,'sched'
            if not ov and _h(c,'no','can'): return 0.88,'sched'
            return 0.15,'sched'
        return None,'none'

    def _meta_confidence(self,prompt,answer=''):
        pl=prompt.lower()
        if re.search(r'(stopped|quit)\s.*\b(have you|did you)',pl): return 0.2
        if re.search(r'\b(best|worst|favorite|opinion|beautiful)\b',pl): return 0.25
        if re.search(r'not\s+all\b',pl) and not _h(pl,'how many'): return 0.28
        if re.search(r'\b(ambiguous|vague|unclear|trick)\b',pl): return 0.22
        return 1.0

    def _ncd(self,a,b):
        try:
            ba,bb=a.encode(),b.encode();ca,cb,cab=len(zlib.compress(ba)),len(zlib.compress(bb)),len(zlib.compress(ba+bb))
            return(cab-min(ca,cb))/max(ca,cb,1)
        except: return 1.0

    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates: return []
        meta=self._meta_confidence(prompt);results=[]
        for cand in candidates:
            cs,sn=self._s(prompt,cand);tp=self._type_check(prompt,cand)
            nc=(1.0-self._ncd(prompt,cand))*.2;ecc,bits=self._ecc_hamming(prompt,cand)
            stab=self._perturbation_stability(prompt,cand,cs)
            if cs is not None: raw=cs*.45+ecc*.35+nc;raw=raw*(.7+.3*stab)
            else: raw=ecc*.55+nc+.1
            score=raw-tp
            results.append({'candidate':cand,'score':float(np.clip(min(score,meta),0,1)),'reasoning':f'comp:{sn} ecc:{ecc:.2f} stab:{stab:.2f} b:{"".join(str(b) for b in bits)}'})
        results.sort(key=lambda x:x['score'],reverse=True);return results

    def confidence(self,prompt:str,answer:str)->float:
        meta=self._meta_confidence(prompt,answer)
        if meta<0.3: return meta
        r=self.evaluate(prompt,[answer]);return float(np.clip(min(r[0]['score'],meta),0,1)) if r else 0.3
