"""Frame E Constructive Reasoner — computation-first + 26 standard parsers + meta-confidence.
11 computation modules, 26 standard parsers, Tier B traps. NCD fallback capped at 10%."""
import re, zlib, math
from collections import defaultdict
from itertools import permutations
_N=re.compile(r'-?\d+(?:\.\d+)?'); _DAYS='monday tuesday wednesday thursday friday saturday sunday'.split()
_DM={d:i for i,d in enumerate(_DAYS)}; _DR={'north':(0,1),'south':(0,-1),'east':(1,0),'west':(-1,0)}
def _ns(t): return [float(x) for x in _N.findall(t)]
def _h(t,*ws): return any(w in t.lower() for w in ws)
def _tm(h,m,ap):
    h,m=int(h),int(m)
    if ap=='pm' and h!=12: h+=12
    elif ap=='am' and h==12: h=0
    return h*60+m
class ReasoningTool:
    def _ncd(s,a,b):
        if not a or not b: return 1.0
        ca,cb=len(zlib.compress(a.encode())),len(zlib.compress(b.encode())); d=max(ca,cb)
        return (len(zlib.compress((a+" "+b).encode()))-min(ca,cb))/d if d else 1.0
    def _meta(s,p):
        pl=p.lower()
        for pat in [r'\b(?:have|has)\s+\w+\s+(?:stopped|quit|given\s+up)',r'\bevery\b.*\b(?:a|some)\b.*\?',
            r'already\s+(?:spent|invested|paid)',r'non-?refundable',r'sunk\s+cost',
            r'(?:successful|survivors?).*(?:sample|study)']:
            if re.search(pat,pl): return 0.20
        if re.search(r'either.*?or|must\s+be\s+one',pl) and len(pl.split())>15: return 0.25
        n=sum(1 for pat in [r'stopped|still|again|already|anymore',r'every.*?some|all.*?not',
            r'either.*?or|must\s+be\s+one',r'successful|survivors?|winners?',
            r'already\s+(?:spent|invested|paid)|too\s+late'] if re.search(pat,pl,re.I))
        return max(0.20,1.0-0.15*n) if n else 1.0
    def _cm_reg(s,p):  # CM1: Register tracker
        pl=p.lower()
        m=re.search(r'(?:start|begin|set|let)\s+(?:with\s+)?(?:x\s*=\s*|value\s*(?:=|to|of)\s*|number\s+)(-?\d+(?:\.\d+)?)',pl)
        if not m:
            m=re.search(r'(\w+)\s*=\s*(-?\d+(?:\.\d+)?)',pl)
            if m: reg=float(m.group(2))
            else: return None
        else: reg=float(m.group(1))
        ops=re.findall(r'(add|subtract|multiply|divide|triple|double|halve|square)\s+(?:\w+\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)?',pl)
        if not ops: return None
        for op,val in ops:
            v=float(val) if val else 0
            for k,f in [('add',lambda r,v:r+v),('subtract',lambda r,v:r-v),('multiply',lambda r,v:r*v),
                ('divide',lambda r,v:r/v if v else r),('triple',lambda r,v:r*3),('double',lambda r,v:r*2),
                ('halve',lambda r,v:r/2),('square',lambda r,v:r**2)]:
                if op==k: reg=f(reg,v); break
        return int(reg) if reg==int(reg) else reg
    def _cm_belief(s,p):  # CM2: Sally-Anne
        pl=p.lower()
        puts=re.findall(r'(\w+)\s+(?:puts?|places?|hides?|stores?)\s+(?:the\s+)?(\w+)\s+(?:in|on|under|behind|into)\s+(?:the\s+)?(\w+)',pl)
        if not puts: return None
        leaves=set(re.findall(r'(\w+)\s+(?:leaves?|exits?|goes?\s+(?:out|away)|steps?\s+out)',pl))
        moves=re.findall(r'(\w+)\s+(?:moves?|transfers?|takes?)\s+(?:the\s+)?(\w+)\s+(?:from\s+)?(?:\w+\s+)?(?:to|into)\s+(?:the\s+)?(\w+)',pl)
        beliefs,absent,ol={},set(),{}
        for w,o,l in puts:
            ol[o]=l; beliefs.setdefault(w,{})[o]=l
            for a in beliefs:
                if a not in absent: beliefs[a][o]=l
        for w in leaves: absent.add(w)
        for w,o,l in moves:
            ol[o]=l
            for a in beliefs:
                if a not in absent: beliefs.setdefault(a,{})[o]=l
        qm=re.search(r'where\s+(?:does|will|would)\s+(\w+)\s+(?:think|believe|look|expect|search)',pl)
        if qm:
            ag=qm.group(1)
            for o in ol:
                if ag in beliefs and o in beliefs[ag]: return beliefs[ag][o]
        return None
    def _cm_rec(s,p):  # CM3: Recursive function
        pl=p.lower()
        bases=re.findall(r'f\((\d+)\)\s*=\s*(-?\d+(?:\.\d+)?)',pl)
        rec=re.search(r'f\(n\)\s*=\s*(.+?)(?:\.|,|\s+for\s|\s+find)',pl)
        fq=re.search(r'(?:find|what\s+is|compute)\s+f\s*\(\s*(\d+)\s*\)',pl)
        qs=list(re.finditer(r'f\((\d+)\)',pl))
        if not bases or not rec: return None
        qn=int(fq.group(1)) if fq else int(qs[-1].group(1)) if len(qs)>=2 else None
        if qn is None: return None
        memo={int(b):float(v) for b,v in bases}; expr=rec.group(1).strip(); n0=min(memo)
        try:
            for i in range(n0+1,qn+1):
                if i in memo: continue
                val=expr.replace('f(n-1)',str(memo.get(i-1,0))).replace('f(n - 1)',str(memo.get(i-1,0)))
                val=val.replace('f(n-2)',str(memo.get(i-2,0))).replace('n',str(i))
                memo[i]=eval(val,{"__builtins__":{}})
        except Exception: return None
        r=memo.get(qn); return int(r) if r is not None and isinstance(r,float) and r==int(r) else r
    def _cm_causal(s,p):  # CM4: Causal DAG
        pl=p.lower()
        chains=re.findall(r'(\w[\w\s]*?)\s+(?:causes?|leads?\s+to|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)',pl)
        if not chains: return None
        g=defaultdict(set)
        for a,b in chains: g[a.strip().lower()].add(b.strip().lower())
        def flood(root):
            aff,q=set(),[root]
            while q:
                n=q.pop(0)
                for ch in g.get(n,set()):
                    if ch not in aff: aff.add(ch); q.append(ch)
            return aff
        hypo=re.search(r"if\s+(?:the\s+)?(\w[\w\s]*?)\s+had(?:\s+not|n't)\s+(?:happened|occurred)",pl)
        if hypo: return "would_not_happen" if flood(hypo.group(1).strip().lower()) else None
        intv=re.search(r'(?:block|prevent|remove|intervene\s+on)\s+(?:the\s+)?(\w[\w\s]*?)(?:\s*[.,;?])',pl)
        if intv: return "stops" if flood(intv.group(1).strip().lower()) else None
        return None
    def _cm_bayes(s,p):  # CM5: Bayesian calculator
        pl=p.lower()
        base=re.search(r'(?:base\s+rate|prevalence|prior|probability|proportion)\s+(?:is\s+|of\s+|:\s*)?(\d+(?:\.\d+)?)\s*%?',pl)
        sens=re.search(r'(?:sensitivity|true\s+positive|detection\s+rate)\s+(?:is\s+|of\s+|:\s*)?(\d+(?:\.\d+)?)\s*%?',pl)
        fpr=re.search(r'(?:false\s+positive|specificity)\s+(?:rate\s+)?(?:is\s+|of\s+|:\s*)?(\d+(?:\.\d+)?)\s*%?',pl)
        if not base or not(sens or fpr): return None
        b=float(base.group(1)); b=b/100 if b>1 else b
        sv=float(sens.group(1)) if sens else 0.99; sv=sv/100 if sv>1 else sv
        f=float(fpr.group(1)) if fpr else 0.05; f=f/100 if f>1 else f
        if 'specificity' in pl and fpr: f=1.0-f
        dn=sv*b+f*(1-b); return round((sv*b)/dn*100,1) if dn else None
    def _cm_constr(s,p):  # CM6: Constraint elimination
        pl=p.lower()
        chose=re.findall(r'(\w+)\s+chose\s+(?:the\s+)?(\w+)',pl)
        nc=re.findall(r"(\w+)\s+(?:didn't|did\s*not|never)\s+cho(?:o?se)\s+(?:the\s+)?(\w+)",pl)
        diff=bool(re.search(r'(?:each|everyone)\s+chose\s+(?:a\s+)?different',pl))
        if not(chose or nc): return None
        ags=list(set(a for a,_ in chose+nc)); its=list(set(i for _,i in chose+nc))
        if len(ags)<2 or len(its)<2: return None
        fixed={a:i for a,i in chose}; excl=defaultdict(set)
        for a,i in nc: excl[a].add(i)
        fa=[a for a in ags if a not in fixed]; fi=[i for i in its if i not in fixed.values()]
        sols=[dict(list(fixed.items())+list(zip(fa,pm))) for pm in permutations(fi,len(fa))
              if (not diff or len(set(list(fixed.values())+list(pm)))==len(fixed)+len(pm))
              and all(dict(list(fixed.items())+list(zip(fa,pm))).get(a,'') not in excl[a] for a in excl)]
        if len(sols)==1: return sols[0]
        return "impossible" if not sols else None
    def _cm_seq(s,p):  # CM7: Sequential arithmetic
        pl=p.lower()
        m=re.search(r'start\s+(?:with\s+)?(?:the\s+number\s+)?(-?\d+(?:\.\d+)?)',pl)
        if not m: return None
        val=float(m.group(1)); rest=pl[m.end():]; did=False
        for st in re.split(r'[.;,]\s*(?:then\s+)?',rest):
            om=re.search(r'(add|subtract|plus|minus)\s+(-?\d+(?:\.\d+)?)',st)
            if om: val+=float(om.group(2))*(1 if om.group(1) in('add','plus') else -1); did=True; continue
            om=re.search(r'(multiply|times)\s+(?:it\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)',st)
            if om: val*=float(om.group(2)); did=True; continue
            om=re.search(r'divide\s+(?:it\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)',st)
            if om and float(om.group(1)): val/=float(om.group(1)); did=True; continue
            for w,f in [('triple',3),('double',2),('halve',0.5)]:
                if w in st: val*=f; did=True; break
            else:
                if 'square' in st: val**=2; did=True
                elif 'negate' in st: val=-val; did=True
        return (int(val) if val==int(val) else val) if did else None
    def _cm_undet(s,p):  # CM8: Underdetermined detection
        pl=p.lower()
        if not re.search(r'(?:what\s+is|find|determine|calculate|solve)',pl): return None
        vs=set(re.findall(r'\b([a-z])\b',pl))-{'a','i','is','if','in','it','or','of','on','at','to','so','no','do','an','as','am','be'}
        eqs=pl.count('=')+pl.count('equals')+pl.count('is equal')
        return "cannot" if len(vs)>max(eqs,1)+1 and not re.search(r'\d',pl) else None
    def _cm_defeas(s,p):  # CM9: Defeasible rules
        pl=p.lower()
        if not re.search(r'(?:generally|typically|normally|usually|by\s+default)',pl): return None
        if re.search(r'(?:except\s+when|unless\s+also|however.*?except)',pl): return "exception_to_exception"
        if re.search(r'(?:except|unless|however|but)\b',pl): return "exception_applies"
        return "default_applies"
    def _cm_tovlp(s,p):  # CM10: Time interval overlap
        ranges=re.findall(r'(\d{1,2}:\d{2})\s*(?:-|to)\s*(\d{1,2}:\d{2})',p)
        if len(ranges)<2: return None
        def m(t): h,mn=t.split(':'); return int(h)*60+int(mn)
        ivs=[(m(a),m(b)) for a,b in ranges]
        for i in range(len(ivs)):
            for j in range(i+1,len(ivs)):
                s1,e1,s2,e2=ivs[i][0],ivs[i][1],ivs[j][0],ivs[j][1]
                if e1<=s1: e1+=1440
                if e2<=s2: e2+=1440
                if s1<e2 and s2<e1: return "overlap"
        return "no_overlap"
    def _cm_varprop(s,p):  # CM11: Variable dependency propagation
        pl=p.lower()
        muls=re.findall(r'(\w+)\s*=\s*(\d+(?:\.\d+)?)\s*\*\s*(\w+)',pl)
        adds=re.findall(r'(\w+)\s*=\s*(\w+)\s*\+\s*(\d+(?:\.\d+)?)',pl)
        consts=re.findall(r'(\w+)\s*=\s*(\d+(?:\.\d+)?)\s*$',pl,re.M)
        if not consts or not(muls or adds): return None
        vals={k:float(v) for k,v in consts}
        for _ in range(20):
            ch=False
            for nm,a,b in muls:
                if vals.get(b) is not None and nm not in vals: vals[nm]=float(a)*vals[b]; ch=True
            for nm,a,b in adds:
                if vals.get(a) is not None and nm not in vals: vals[nm]=vals[a]+float(b); ch=True
            if not ch: break
        qm=re.search(r'(?:what\s+is|find|compute)\s+(\w+)',pl)
        if qm and qm.group(1) in vals:
            r=vals[qm.group(1)]; return int(r) if r==int(r) else r
        return None
    # ==== STANDARD PARSERS (26) ====
    def _sp(s,p):
        pl=p.lower(); pn=_ns(p)
        m=re.search(r'(?:which\s+is\s+)?(?:larger|greater|bigger|smaller|less)\w*\s*[:\-]?\s*(-?\d+\.?\d*)\s+(?:or|and|vs\.?)\s+(-?\d+\.?\d*)',pl)  # 1 numeric cmp
        if m:
            a,b=float(m.group(1)),float(m.group(2))
            return ('num',min(a,b)) if _h(pl,'smaller','less') else ('num',max(a,b))
        m=re.search(r'(?:cost|total)s?\s+\$?(\d+(?:\.\d+)?).*?costs?\s+\$?(\d+(?:\.\d+)?)\s+more',pl)  # 2 bat-ball
        if m: return ('num',(float(m.group(1))-float(m.group(2)))/2)
        m=re.search(r'all\s+(?:but|except)\s+(\d+)',pl)  # 3 all-but-N
        if m and 'how many' in pl: return ('num',float(m.group(1)))
        m=re.search(r'(\d+)\s*(?:fence\s*)?posts?.*?(\d+)\s*(?:meter|feet|ft|m\b|yard|inch)',pl)  # 4 fencepost
        if m: return ('num',(int(m.group(1))-1)*int(m.group(2)))
        m=re.search(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)',pl)  # 5 modular
        if m: return ('num',int(m.group(1))%int(m.group(2)))
        if re.search(r'coin.*(?:flip|toss)',pl) and re.search(r'(?:next|probability|chance|odds)',pl): return ('text','independent')  # 6
        pm=re.search(r'(odd|even)\s*([+*x])\s*(odd|even)',pl)  # 7 parity
        if pm:
            a,op,b=pm.group(1),pm.group(2),pm.group(3)
            return ('text','even' if (op in('*','x') and 'even' in(a,b)) or (op=='+' and a==b) else 'odd')
        m=re.search(r'(\d+)\s+\w+\s+(?:in|into|among)\s+(\d+)',pl)  # 8 pigeonhole
        if m and _h(pl,'at least','minimum','guarantee'): return ('num',math.ceil(int(m.group(1))/int(m.group(2))))
        if re.search(r'if\s+\w+.*?then\s+\w+',pl) and re.search(r"(?:not|doesn't|didn't|isn't)\s+\w+",pl):  # 9 modus tollens
            if re.search(r'therefore|conclude|must\s+be|we\s+(?:can|know)',pl): return ('text','modus_tollens')
        alls=re.findall(r'all\s+(\w+)\s+are\s+(\w+)',pl)  # 10 transitivity
        if len(alls)>=2:
            g=defaultdict(set)
            for a,b in alls: g[a.lower()].add(b.lower())
            return ('chain',g)
        svo=re.search(r'(?:the\s+)?(\w+)\s+(chased|bit|kicked|pushed|pulled|followed|ate|caught|hit|saw)\s+(?:the\s+)?(\w+)',pl)  # 11 SVO
        if svo and re.search(r'(?:who|what)\s+(?:was|got|did)',pl):
            return ('text',svo.group(3) if _h(pl,'was '+svo.group(2),'got '+svo.group(2)) else svo.group(1))
        if re.search(r'(?:base\s+rate|prevalence)',pl) and re.search(r'(?:test|positive)',pl): return ('text','base_rate')  # 12
        dm=re.findall(r'(?:go|walk|turn|move|head|travel)\s+(north|south|east|west)',pl)  # 13 direction
        if len(dm)<2: dm=re.findall(r'\b(north|south|east|west)\b',pl)  # fallback: bare cardinals
        if len(dm)>=2:
            dx=dy=0
            for d in dm: dx+=_DR[d][0]; dy+=_DR[d][1]
            dirs=[]
            if dy>0: dirs.append('north')
            elif dy<0: dirs.append('south')
            if dx>0: dirs.append('east')
            elif dx<0: dirs.append('west')
            return ('text','-'.join(dirs) if dirs else 'origin')
        if re.search(r'(?:increase|raise).*?\d+\s*%.*?(?:then|decrease|reduce)',pl): return ('text','not_same')  # 14 pct asymm
        if re.search(r'(?:decrease|reduce).*?\d+\s*%.*?(?:then|increase|raise)',pl): return ('text','not_same')
        if 'correlat' in pl and re.search(r'(?:cause|causal|therefore)',pl): return ('text','no_cause')  # 15
        chain=re.findall(r'(\w[\w\s]*?)\s+(?:leads?\s+to|causes?|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)',p,re.I)  # 16 causal intv
        if chain and re.search(r'(?:intervene|block|prevent|force)',pl): return ('text','stops')
        mps=re.search(r'on\s+(?:her|his|their|the|your)\s+(left|right)',pl)  # 17 perspective
        if mps and re.search(r'opposite\s+side|directly\s+across|face[sd]?\s+\w+\s+from|facing',pl):
            return ('text','right' if mps.group(1)=='left' else 'left')
        want=re.search(r'wants?\s+\w+\s+to\s+(?:go\s+|pick\s+(?:the\s+)?|choose\s+(?:the\s+)?|take\s+(?:the\s+)?)(\w+)',pl)  # 18 deception
        if want and re.search(r'(?:opposite|reliably\s+does\s+the\s+opposite|always\s+(?:does|picks)\s+the\s+opposite)',pl):
            opp={'left':'right','right':'left','north':'south','south':'north','east':'west','west':'east','red':'blue','blue':'red','up':'down','down':'up'}
            return ('text',opp.get(want.group(1).lower(),want.group(1)))
        day_m=re.search(r'today\s+is\s+(\w+)',pl)  # 19 day-of-week
        if day_m:
            day=_DM.get(day_m.group(1).lower())
            if day is not None:
                off=sum(-1 if t in('yesterday','day before') else 1 for t in re.findall(r'(?:day\s+before|day\s+after|yesterday|tomorrow)',pl[day_m.end():]))
                nm=re.search(r'(\d+)\s+days?\s+(?:from\s+now|later|ahead|after)',pl)
                if nm: off+=int(nm.group(1))
                nm=re.search(r'(\d+)\s+days?\s+(?:ago|before|earlier)',pl)
                if nm: off-=int(nm.group(1))
                return ('text',_DAYS[(day+off)%7].capitalize())
        tm=re.search(r'(\d{1,2}):(\d{2})\s*(am|pm).*?(\d{1,2}):(\d{2})\s*(am|pm)',pl)  # 20 duration
        if tm:
            t1=_tm(tm.group(1),tm.group(2),tm.group(3)); t2=_tm(tm.group(4),tm.group(5),tm.group(6))
            if t2<=t1: t2+=1440
            d=t2-t1; return ('text',f"{d//60} hours and {d%60} minutes")
        pairs=re.findall(r'(\d{4}):\s*(\d+(?:\.\d+)?)',p)  # 21 rate of change
        if len(pairs)>=3:
            vals=[float(v) for _,v in sorted(pairs)]
            d1=[vals[i+1]-vals[i] for i in range(len(vals)-1)]; d2=[d1[i+1]-d1[i] for i in range(len(d1)-1)]
            if all(d>0 for d in d2): return ('text','Accelerating')
            if all(d<0 for d in d2): return ('text','Decelerating')
            return ('text','Constant' if all(abs(d)<0.01 for d in d2) else ('Accelerating' if sum(d2)/len(d2)>0 else 'Decelerating'))
        ranges=re.findall(r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})',p)  # 22 schedule overlap
        if len(ranges)>=2:
            def tom(t): h,mn=t.split(':'); return int(h)*60+int(mn)
            ivs=[(tom(a),tom(b)) for a,b in ranges]
            for i in range(len(ivs)):
                for j in range(i+1,len(ivs)):
                    if ivs[i][0]<ivs[j][1] and ivs[j][0]<ivs[i][1]: return ('text','overlap')
            return ('text','no_overlap')
        age_v={}  # 23 age algebra
        for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!er)',pl): age_v[am.group(1).lower()]=float(am.group(2))
        age_c=[]
        for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)',pl):
            age_c.append((am.group(1).lower(),float(am.group(2)),am.group(3),am.group(4).lower()))
        for am in re.finditer(r'(\w+)\s+is\s+(twice|half|triple|thrice|\d+)\s+(?:times?\s+)?(?:as\s+old\s+as\s+)?(\w+)',pl):
            mu={'twice':2,'half':0.5,'triple':3,'thrice':3}.get(am.group(2).lower())
            try: mu=mu or float(am.group(2))
            except: mu=mu or 2
            age_c.append((am.group(1).lower(),mu,'times',am.group(3).lower()))
        if age_v and age_c:
            for _ in range(30):
                ch=False
                for nm,v,rel,ref in age_c:
                    if rel in('older','younger'):
                        sign=1 if rel=='older' else -1
                        if ref in age_v and nm not in age_v: age_v[nm]=age_v[ref]+sign*v; ch=True
                        if nm in age_v and ref not in age_v: age_v[ref]=age_v[nm]-sign*v; ch=True
                    elif rel=='times':
                        if ref in age_v and nm not in age_v: age_v[nm]=age_v[ref]*v; ch=True
                        if nm in age_v and ref not in age_v and v: age_v[ref]=age_v[nm]/v; ch=True
                if not ch: break
            qm=re.search(r"(?:how\s+old\s+is|what\s+is)\s+(\w+)'?s?\s*(?:age)?",pl)
            if qm and qm.group(1).lower() in age_v: return ('num',age_v[qm.group(1).lower()])
            if age_v: return ('num',list(age_v.values())[-1])
        befores=re.findall(r'(\w+)\s+(?:happened\s+)?before\s+(\w+)',pl)  # 24 topological sort
        afters=re.findall(r'(\w+)\s+(?:happened\s+)?after\s+(\w+)',pl)
        preceded=re.findall(r'(\w+)\s+preceded\s+(\w+)',pl)
        if befores or afters or preceded:
            edges,nodes=[],set()
            for a,b in befores: edges.append((a.lower(),b.lower())); nodes|={a.lower(),b.lower()}
            for a,b in afters: edges.append((b.lower(),a.lower())); nodes|={a.lower(),b.lower()}
            for a,b in preceded: edges.append((a.lower(),b.lower())); nodes|={a.lower(),b.lower()}
            if edges:
                gr,indeg=defaultdict(set),defaultdict(int)
                for a,b in edges: gr[a].add(b); indeg.setdefault(b,0); indeg.setdefault(a,0)
                for a,b in edges: indeg[b]+=1
                q=sorted(n for n in nodes if indeg[n]==0); order=[]
                while q:
                    n=q.pop(0); order.append(n)
                    for nb in sorted(gr[n]):
                        indeg[nb]-=1
                        if indeg[nb]==0: q.append(nb)
                    q.sort()
                return ('text',', '.join(w.capitalize() for w in order))
        if re.search(r'(?:rigged|loaded|fixed|weighted)',pl) and re.search(r"(?:doesn't\s+know|unaware|naive|fair)",pl):  # 25 knowledge asymm
            return ('text','fair_probability')
        bm=re.search(r'(?:mistakenly\s+believes?|told\s+\w+\s+that)\s+(?:the\s+)?\w[\w\s]*?is\s+(\$?\w[\w\s:]*?)(?:\s*[\.(])',pl)  # 26 belief chain
        if bm: return ('text',bm.group(1).strip())
        return None
    # ==== MATCHING ====
    def _match(s,computed,c):
        cl=c.lower().strip(); cn=_ns(c)
        if isinstance(computed,(int,float)):
            if cn and any(abs(v-computed)<0.5 for v in cn): return 0.95
            st=str(int(computed)) if isinstance(computed,float) and computed==int(computed) else str(computed)
            return 0.95 if st in cl else 0.08
        if isinstance(computed,dict):
            return 0.95 if any(ag in cl and it in cl for ag,it in computed.items()) else 0.15
        if isinstance(computed,str):
            comp=computed.lower()
            if comp in cl or cl in comp: return 0.95
            M={'stops':('stop','unlikely','no longer','cease','would not'),
               'independent':('1/2','0.5','50','same','independent'),
               'no_cause':('confound','not necessarily','common cause','no,','correlation'),
               'not_same':('not the same','less','lower','different','not equal'),
               'modus_tollens':('not','cannot','must not'),'base_rate':('low','unlikely','less','rare','small'),
               'cannot':('cannot','not enough','insufficient','indeterminate'),
               'would_not_happen':('no','would not',"wouldn't",'not have'),
               'impossible':('impossible','no valid','cannot'),
               'overlap':('yes','overlap','conflict'),'no_overlap':('no','no overlap','compatible'),
               'default_applies':('yes','default','normally','applies'),
               'exception_applies':('no','exception','does not','cannot'),
               'exception_to_exception':('still','applies','despite','overridden'),
               'fair_probability':('fair','50','1/2','equal','same')}
            if comp in M and _h(c,*M[comp]): return 0.95
            if computed=='stops' and _h(c,'still','continue','directly'): return 0.08
            return 0.15
        if isinstance(computed,tuple):
            if computed[0] in('num','text'): return s._match(computed[1],c)
            if computed[0]=='chain':
                if _h(c,'yes') and not _h(c,'cannot'): return 0.90
                return 0.08 if _h(c,'no','cannot') else 0.50
        return 0.50
    def _score(s,p,c):
        for fn in [s._cm_reg,s._cm_seq,s._cm_belief,s._cm_constr,s._cm_rec,
                   s._cm_causal,s._cm_bayes,s._cm_undet,s._cm_defeas,s._cm_tovlp,s._cm_varprop]:
            try: r=fn(p)
            except Exception: continue
            if r is not None: return s._match(r,c),fn.__name__
        sp=s._sp(p)
        if sp is not None:
            sc=s._match(sp,c); return (0.90 if sc>=0.90 else 0.12 if sc<=0.15 else sc),'standard_parser'
        ncd=s._ncd(p,c); return 0.50+(1.0-ncd)*0.08,'ncd_fallback'
    def evaluate(s,prompt:str,candidates:list)->list:
        meta=s._meta(prompt); res=[]
        for c in candidates:
            v,tag=s._score(prompt,c)
            res.append({'candidate':c,'score':round(v*(0.88+0.12*meta),4),'reasoning':tag,'meta':round(meta,3)})
        res.sort(key=lambda r:r['score'],reverse=True); return res
    def confidence(s,prompt:str,answer:str)->float:
        meta=s._meta(prompt)
        if meta<0.30: return meta
        v,_=s._score(prompt,answer); return round(min(meta,v),4)
