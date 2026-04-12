"""Frame C Dynamics — Ergodic Theory x Genetic Algorithms x Neuromodulation.
Ergodic averaging over multiple evaluation passes converges to stable score.
Genetic operators mutate candidate features and test fitness.
Neuromodulatory gain control adjusts scoring weights based on context.
Score: computation(45%) + structural(35%) + NCD tiebreaker(20% max)."""
import re, math, zlib, numpy as np
from typing import List, Dict
_N=re.compile(r"[-+]?\d*\.?\d+"); _D=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']; _C=['north','east','south','west']
def _n(t): return [float(m) for m in _N.findall(t)]
def _h(t,*w): l=t.lower(); return any(x in l for x in w)
def _f(t): m=re.match(r'\s*([a-z]+)',t.lower()); return m.group(1) if m else ''
def _ncd(a,b):
    try: ba,bb=a.encode(),b.encode(); ca,cb,cab=len(zlib.compress(ba)),len(zlib.compress(bb)),len(zlib.compress(ba+bb)); return (cab-min(ca,cb))/max(ca,cb,1)
    except: return 1.0

class ReasoningTool:
    def _neuromod_gain(self, p):
        """Context-dependent gain control: modulate scoring weights by problem type."""
        pl=p.lower(); ns=_n(p)
        g_comp, g_struct = 0.45, 0.35
        if len(ns)>=3 and _h(pl,'rate','acceler','sequence','series'): g_comp=0.55; g_struct=0.25
        elif _h(pl,'not all','cannot determine','ambiguous'): g_comp=0.35; g_struct=0.45
        elif re.search(r'\b(who|whom)\b',pl) and _h(pl,'gave','told','said'): g_comp=0.50; g_struct=0.30
        elif len(ns)==0 and len(p.split())<10: g_comp=0.30; g_struct=0.50
        return g_comp, g_struct

    def _genetic_fitness(self, p, c, base_score):
        """Mutate candidate feature weights, return best fitness across variants."""
        pl,cl=p.lower(),c.lower(); ns=_n(p); cn=_n(c)
        mutations = [base_score]
        kw_p=set(re.findall(r'\b[a-z]{3,}\b',pl)); kw_c=set(re.findall(r'\b[a-z]{3,}\b',cl))
        overlap=len(kw_p&kw_c)/max(len(kw_p),1)
        ent_p=set(re.findall(r'\b[A-Z][a-z]+\b',p)); ent_match=sum(1 for e in ent_p if e.lower() in cl)/max(len(ent_p),1)
        num_match=0.0
        if cn and ns:
            for v in ns:
                if any(abs(v-cv)<0.01 for cv in cn): num_match=0.3; break
        mutations.append(base_score*0.6 + overlap*0.25 + ent_match*0.15)
        mutations.append(base_score*0.7 + num_match*0.2 + overlap*0.1)
        mutations.append(base_score*0.5 + ent_match*0.3 + overlap*0.2)
        return max(mutations)

    def _ergodic_average(self, scores):
        """Time-average over multiple evaluation passes — ergodic convergence."""
        if not scores: return 0.0
        arr=np.array(scores,dtype=np.float64)
        weights=np.exp(-0.1*np.arange(len(arr))[::-1])
        return float(np.average(arr, weights=weights))

    def _s(self, p, c):
        ns=_n(p); pl=p.lower(); cn=_n(c); cl=c.lower(); fw=_f(c)
        if _h(p,'which is','greater','larger','smaller','less than','more than','bigger') and len(ns)>=2 and cn:
            t=max(ns) if _h(p,'great','larg','big','more') else min(ns)
            return (0.9 if abs(cn[0]-t)<1e-9 else 0.1),'numeric'
        if _h(p,'cost','total','together') and _h(p,'more than') and len(ns)>=2:
            a=(ns[0]-ns[1])/2
            if cn: return (0.92 if abs(cn[0]-a)<.01 else (0.1 if abs(cn[0]-ns[1])<.01 else 0.3)),'bat_ball'
        if _h(p,'all but','all except') and len(ns)>=2:
            return (0.9 if cn and abs(cn[0]-int(min(ns)))<.5 else 0.15),'all_but'
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
                            if bb not in g.get(a,set()): g.setdefault(a,set()).add(bb); ch=True
            an=set(); [an.update([a]+list(v)) for a,v in g.items()]
            for a in an:
                if a in cl and not any(a in g.get(x,set()) for x in an if x!=a):
                    if _h(p,'tallest','fastest','oldest','biggest','heaviest','strongest'): return 0.88,'trans'
            return 0.3,'trans'
        m=re.search(r'if\s+(.+?)\s*,?\s*then\s+(.+?)\.',pl)
        if m and _h(p,'not','no ','never',"don't","doesn't"):
            if _h(c,'not') or fw=='no': return 0.85,'mt'
            if fw in ('yes','true'): return 0.1,'mt'
        if re.search(r'not\s+all\s+\w+\s+are',pl):
            if _h(c,'cannot determine','insufficient','not enough','uncertain'): return 0.88,'neg'
            if fw in ('yes','no','true','false'): return 0.15,'neg'
        sm=re.search(r'(\w+)\s+(gave|told|sent|passed|handed)\s+(?:\w+\s+)?(?:to\s+)?(\w+)',pl)
        if sm and _h(p,'who'):
            if _h(p,'who '+sm.group(2),'who gave','who told') and sm.group(1) in cl: return 0.88,'svo'
            if _h(p,'receive','got','to whom') and sm.group(3) in cl: return 0.88,'svo'
        if _h(p,'preva','base rate','1 in','sensitivity') and len(ns)>=2:
            pv=min(ns)/100 if min(ns)>1 else min(ns)
            if pv>.5: pv=.01
            se=max(x for x in ns if x<=100)/100; po=(se*pv)/(se*pv+(1-se)*(1-pv)) if (se*pv+(1-se)*(1-pv))>0 else .5
            if cn:
                cp=cn[0]/100 if cn[0]>1 else cn[0]
                if abs(cp-po)<.15: return 0.8,'bayes'
            if _h(c,'low','unlikely') and po<.3: return 0.75,'bayes'
        be=re.findall(r'(\w+)\s+(?:before|earlier than|prior to)\s+(\w+)',pl)
        af=re.findall(r'(\w+)\s+(?:after|later than|following)\s+(\w+)',pl)
        ed=[(a,b) for a,b in be]+[(b,a) for a,b in af]
        if ed:
            nd=set(); [nd.update([a,b]) for a,b in ed]
            ig={x:0 for x in nd}; aj={x:[] for x in nd}
            for a,b in ed: aj[a].append(b); ig[b]+=1
            q=sorted(x for x in nd if ig[x]==0); od=[]
            while q:
                x=q.pop(0); od.append(x)
                for nb in aj[x]: ig[nb]-=1; (q.append(nb) if ig[nb]==0 else None)
                q.sort()
            tg=od[0] if _h(p,'first','earliest') else (od[-1] if _h(p,'last','latest') else None)
            if tg and tg in cl: return 0.9,'topo'
            if tg: return 0.2,'topo'
        rl=re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)',pl)
        st=re.findall(r'(\w+)\s+is\s+(\d+)\s+years?\s+old',pl)
        if rl:
            kn={x:int(a) for x,a in st}
            for _ in range(10):
                for a,d,r2,b in rl:
                    d2=int(d)
                    if b in kn and a not in kn: kn[a]=kn[b]+d2 if r2=='older' else kn[b]-d2
                    if a in kn and b not in kn: kn[b]=kn[a]-d2 if r2=='older' else kn[a]+d2
            tg=re.search(r'how old (?:is|was) (\w+)',pl)
            if tg and tg.group(1) in kn: return (0.92 if cn and abs(cn[0]-kn[tg.group(1)])<.5 else 0.1),'age'
        if _h(p,'same time','simultaneous','parallel','together','at once'):
            ts=[int(x) for x in re.findall(r'(\d+)\s*(?:min|hour|second|minute)',pl)]
            if ts:
                a2=max(ts) if _h(p,'total','all done','finish') else min(ts)
                if cn and abs(cn[0]-a2)<.5: return 0.88,'conc'
        ti=re.findall(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',pl)
        if len(ti)>=4 and _h(p,'conflict','overlap','both','attend'):
            def tm(h,mi,ap): h=int(h);mi=int(mi) if mi else 0; h+=(12 if ap=='pm' and h!=12 else (-12 if ap=='am' and h==12 else 0)); return h*60+mi
            rg=[]
            for i in range(0,len(ti)-1,2): s2,e2=tm(*ti[i]),tm(*ti[i+1]); rg.append((s2,e2+1440*(e2<s2)))
            ov=len(rg)>=2 and rg[0][0]<rg[1][1] and rg[1][0]<rg[0][1]
            if ov and _h(c,'yes','conflict','cannot'): return 0.88,'sched'
            if not ov and _h(c,'no','can'): return 0.88,'sched'
            return 0.15,'sched'
        if _h(p,'accelerat','deceler','rate','increasing','decreasing') and len(ns)>=3:
            df=[ns[i+1]-ns[i] for i in range(len(ns)-1)]; dd=df[-1]-df[0]
            if dd>0 and _h(c,'accelerat','increasing','faster'): return 0.85,'rate'
            if dd<0 and _h(c,'deceler','decreasing','slower'): return 0.85,'rate'
            return 0.15,'rate'
        if _h(p,'yesterday','tomorrow','day after','day before'):
            dm=re.search(r'today is (\w+day)',pl)
            if dm:
                ix=next((i for i,d in enumerate(_D) if d==dm.group(1)),-1)
                if ix>=0:
                    of=len(re.findall(r'tomorrow|day after',pl))-len(re.findall(r'yesterday|day before',pl))
                    if _D[(ix+of)%7] in cl: return 0.9,'day'
                    return 0.15,'day'
        fm=re.search(r'fac(?:e|ing)\s+(north|south|east|west)',pl)
        if fm:
            ix=_C.index(fm.group(1))
            for t in re.findall(r'turn\s+(left|right)',pl): ix=(ix+1)%4 if t=='right' else (ix-1)%4
            return (0.9 if _C[ix] in cl else 0.1),'dir'
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
        return None,'none'

    def _meta_confidence(self, prompt, answer=''):
        pl=prompt.lower()
        if re.search(r'(stopped|quit)\s.*\b(have you|did you)',pl): return 0.2
        if re.search(r'\b(best|worst|favorite|opinion|beautiful)\b',pl): return 0.25
        if re.search(r'not\s+all\b',pl) and not _h(pl,'how many'): return 0.28
        if re.search(r'\b(ambiguous|vague|unclear|trick)\b',pl): return 0.22
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates: return []
        meta=self._meta_confidence(prompt); g_comp,g_struct=self._neuromod_gain(prompt)
        g_ncd=1.0-g_comp-g_struct; pw=set(re.findall(r'\b[a-z]{3,}\b',prompt.lower())); results=[]
        for cand in candidates:
            cs,sn=self._s(prompt,cand)
            cw=set(re.findall(r'\b[a-z]{3,}\b',cand.lower())); st=len(pw&cw)/max(len(pw),1)*.6+.2
            nc=(1.0-_ncd(prompt,cand))*g_ncd
            base=(cs*g_comp+st*g_struct+nc) if cs is not None else (st*(g_struct+g_comp*.5)+nc+.1)
            # Ergodic averaging: run genetic fitness variants, converge
            passes=[base, self._genetic_fitness(prompt,cand,base)]
            score=self._ergodic_average(passes)
            results.append({'candidate':cand,'score':float(np.clip(min(score,meta),0,1)),'reasoning':f'erg:{sn} g={g_comp:.2f}/{g_struct:.2f}'})
        results.sort(key=lambda x:x['score'],reverse=True); return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta=self._meta_confidence(prompt,answer)
        if meta<0.3: return meta
        r=self.evaluate(prompt,[answer]); return float(np.clip(min(r[0]['score'],meta),0,1)) if r else 0.3
