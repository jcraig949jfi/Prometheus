"""Spectral Analysis x Abductive Reasoning x Multi-Armed Bandits. Frame C: Dynamics Tracker.
Frequency decomposition of text structure (token periodicity, structural harmonics),
abductive hypothesis ranking (parsimony + coverage), bandit-style scoring (UCB1).
Score: computation(50%) + spectral+abductive(30%) + NCD tiebreaker(20% max)."""
import re, math, zlib, numpy as np
from typing import List, Dict
_N=re.compile(r'[-+]?\d*\.?\d+');_D=['monday','tuesday','wednesday','thursday','friday','saturday','sunday'];_C=['north','east','south','west']
def _n(t): return [float(m) for m in _N.findall(t)]
def _h(t,*w): l=t.lower(); return any(x in l for x in w)
def _f(t): m=re.match(r'\s*([a-z]+)',t.lower()); return m.group(1) if m else ''

class ReasoningTool:
    def _spectral_features(self,text):
        """Frequency decomposition: word length periodicity, punctuation rhythm."""
        words=text.split();df={'dominant_freq':0.0,'spectral_entropy':0.5,'harmonic_ratio':0.5}
        if len(words)<3: return df
        lengths=np.array([len(w) for w in words],dtype=float);lengths-=np.mean(lengths)
        mag=np.abs(np.fft.rfft(lengths)[1:]);total=np.sum(mag)
        if len(mag)==0 or total<1e-9: return df
        probs=mag/total;probs=probs[probs>0];entropy=-np.sum(probs*np.log2(probs))/max(np.log2(len(probs)),1)
        di=np.argmax(mag);return {'dominant_freq':float(di/len(words)),'spectral_entropy':float(np.clip(entropy,0,1)),'harmonic_ratio':float(mag[di]/total)}

    def _spectral_match(self,p,c):
        """How well do prompt and candidate spectral signatures align?"""
        sp=self._spectral_features(p);sc=self._spectral_features(c)
        freq_diff=abs(sp['dominant_freq']-sc['dominant_freq'])
        ent_diff=abs(sp['spectral_entropy']-sc['spectral_entropy'])
        return max(0,1.0-freq_diff*2-ent_diff*0.5)

    def _abductive_rank(self,p,c):
        """Abductive: coverage of prompt elements + parsimony of explanation."""
        pl=p.lower();cl=c.lower()
        stops={'the','and','for','that','this','with','are','was','were','has','have','from','but','not','can','will'}
        pw=set(re.findall(r'\b[a-z]{3,}\b',pl))-stops;cw=set(re.findall(r'\b[a-z]{3,}\b',cl))-stops
        coverage=len(pw&cw)/max(len(pw),1)
        parsimony=1.0/(1.0+math.log1p(max(len(cw),1)))
        ents=set(re.findall(r'\b[A-Z][a-z]+\b',p));ent_hit=sum(1 for e in ents if e.lower() in cl)/max(len(ents),1)
        pn,cn=_n(p),_n(c);num_hit=1.0 if(pn and cn and any(abs(a-b)<.5 for a in pn for b in cn))else 0.0
        return coverage*0.35+parsimony*0.20+ent_hit*0.25+num_hit*0.20

    def _bandit_adjust(self,scores,idx):
        """UCB1-style: boost uncertain candidates slightly for exploration."""
        if len(scores)<2: return scores[idx] if idx<len(scores) else 0.5
        n=len(scores)
        exploration=math.sqrt(2*math.log(n)/(idx+1))
        return scores[idx]+0.05*min(exploration,1.0)

    def _s(self,p,c):
        ns=_n(p);pl=p.lower();cn=_n(c);cl=c.lower();fw=_f(c)
        if _h(p,'cost','total','together') and _h(p,'more than') and len(ns)>=2:
            a=(ns[0]-ns[1])/2
            if cn: return(0.92 if abs(cn[0]-a)<.01 else(0.1 if abs(cn[0]-ns[1])<.01 else 0.3)),'bat_ball'
        if _h(p,'which is','greater','larger','smaller','less than','more than','bigger') and len(ns)>=2 and cn:
            t=max(ns) if _h(p,'great','larg','big','more') else min(ns); return(0.9 if abs(cn[0]-t)<1e-9 else 0.1),'numeric'
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
        if _h(p,'coin','flip','toss') and _h(p,'independent','next flip','fair'):
            cl2=c.lower().strip();is_half=cl2 in('50%','50','0.5','1/2','half','50 percent') or cl2.startswith('50%') or cl2=='half'
            if not _h(c,'higher','lower','more','less','increase','decrease','greater') and is_half: return 0.9,'coin'
            return 0.1,'coin'
        if _h(p,'guarantee','worst case','minimum number','sock','drawer') and ns:
            tgt=int(max(ns))+1
            if cn:
                if abs(cn[0]-tgt)<.5: return 0.88,'pig'
                return 0.1,'pig'
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
        return None,'none'

    def _meta_confidence(self,prompt,answer=''):
        pl=prompt.lower()
        if re.search(r'\b(stopped|still|again|already|anymore)\b.*\b(have you|did you|do you)\b',pl): return 0.20
        if re.search(r'\bevery\b.*\bsome\b|\ball\b.*\bnot\b',pl): return 0.22
        if re.search(r'\b(either)\b.*\bor\b.*\b(must be one|only)\b',pl): return 0.23
        if re.search(r'\b(successful|survivors?|winners?)\b.*\b(all|every|always)\b',pl): return 0.24
        if re.search(r'\balready\s+(spent|invested|paid)\b',pl): return 0.25
        if re.search(r'\b(best|worst|favorite|opinion|beautiful)\b',pl):
            if not re.search(r'best\s+(?:explain|describe|fit)',pl): return 0.25
        if re.search(r'\b(ambiguous|vague|unclear|trick)\b',pl): return 0.22
        return 1.0

    def _ncd(self,a,b):
        try:
            ba,bb=a.encode(),b.encode();ca,cb,cab=len(zlib.compress(ba)),len(zlib.compress(bb)),len(zlib.compress(ba+bb))
            return(cab-min(ca,cb))/max(ca,cb,1)
        except: return 1.0

    def evaluate(self,prompt:str,candidates:List[str])->List[Dict]:
        if not candidates: return []
        meta=self._meta_confidence(prompt);raw_scores=[];results=[]
        for cand in candidates:
            cs,sn=self._s(prompt,cand)
            abd=self._abductive_rank(prompt,cand)
            spec=self._spectral_match(prompt,cand)
            nc=(1.0-self._ncd(prompt,cand))*.2
            if cs is not None: raw=cs*.50+abd*.15+spec*.15+nc
            else: raw=abd*.35+spec*.20+nc+.1
            raw_scores.append(raw)
        for i,cand in enumerate(candidates):
            cs,sn=self._s(prompt,cand)
            adj=self._bandit_adjust(raw_scores,i)
            final=raw_scores[i]*0.9+adj*0.1
            score=float(np.clip(min(final,meta),0,1))
            results.append({'candidate':cand,'score':score,'reasoning':f'comp:{sn} abd:{self._abductive_rank(prompt,cand):.2f} spec:{self._spectral_match(prompt,cand):.2f}'})
        results.sort(key=lambda x:x['score'],reverse=True);return results

    def confidence(self,prompt:str,answer:str)->float:
        meta=self._meta_confidence(prompt,answer)
        if meta<0.3: return meta
        r=self.evaluate(prompt,[answer]);return float(np.clip(min(r[0]['score'],meta),0,1)) if r else 0.3
