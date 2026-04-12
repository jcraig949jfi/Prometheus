"""Frame E Hybrid Engine — computation-first + standard parsers + meta-confidence.
Layer 1: 8 computation modules (Tier 2). Layer 2: 26+ standard parsers (Tier 1).
Layer 3: Tier B meta-confidence traps. NCD fallback capped at 10%."""
import re, zlib, math
from collections import defaultdict
from itertools import permutations
_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
_DMAP = {d: i for i, d in enumerate(_DAYS)}
_TB = {k: re.compile(v, re.I) for k, v in {
    'p': r'(?:stopped|still|again|already|anymore)', 's': r'(?:every.*?some|all.*?not|not.*?all)',
    'f': r'(?:either.*?or|must\s+be\s+one)', 'v': r'(?:successful|survivors?|winners?|made\s+it)',
    'k': r'(?:already\s+(?:spent|invested|paid)|too\s+late\s+to)'}.items()}
def _ns(t): return [float(x) for x in _NUM.findall(t)]
def _h(t, *ws): return any(w in t.lower() for w in ws)

class ReasoningTool:
    def _ncd(s, a, b):
        if not a or not b: return 1.0
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        d = max(ca, cb)
        return (len(zlib.compress((a+" "+b).encode()))-min(ca,cb))/d if d else 1.0
    def _meta(s, p):
        pl = p.lower()
        if re.search(r'\b(?:have|has)\s+\w+\s+(?:stopped|quit|given\s+up)', pl): return 0.20
        if re.search(r'\bevery\b.*\b(?:a|some)\b.*\?', pl): return 0.20
        if re.search(r'already\s+(?:spent|invested|paid)', pl): return 0.20
        if re.search(r'non-?refundable', pl): return 0.20
        if re.search(r'either.*?or|must\s+be\s+one', pl) and len(pl.split())>15: return 0.25
        if re.search(r'(?:successful|survivors?).*(?:sample|study)', pl): return 0.20
        n = sum(1 for v in _TB.values() if v.search(pl))
        return max(0.20, 1.0-0.15*n) if n else 1.0
    # ==== LAYER 1: COMPUTATION MODULES ====
    def _cm_register(s, p):
        pl = p.lower()
        m = re.search(r'(?:start|begin|set|let)\s+(?:with\s+)?(?:x\s*=\s*|value\s*(?:=|to|of)\s*|number\s+)(-?\d+(?:\.\d+)?)', pl)
        if not m:
            m = re.search(r'(\w+)\s*=\s*(-?\d+(?:\.\d+)?)', pl)
            if m: reg = float(m.group(2))
            else: return None
        else: reg = float(m.group(1))
        ops = re.findall(r'(add|subtract|multiply|divide|triple|double|halve|square)\s+(?:\w+\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)?', pl)
        if not ops: return None
        for op, val in ops:
            v = float(val) if val else 0
            if op=='add': reg+=v
            elif op=='subtract': reg-=v
            elif op=='multiply': reg*=v
            elif op=='divide' and v: reg/=v
            elif op=='triple': reg*=3
            elif op=='double': reg*=2
            elif op=='halve': reg/=2
            elif op=='square': reg**=2
        return int(reg) if reg==int(reg) else reg
    def _cm_seq_arith(s, p):
        pl = p.lower()
        m = re.search(r'start\s+(?:with\s+)?(?:the\s+number\s+)?(-?\d+(?:\.\d+)?)', pl)
        if not m: return None
        val = float(m.group(1)); rest = pl[m.end():]; did = False
        for st in re.split(r'[.;]\s*', rest):
            st = st.strip()
            if not st: continue
            om = re.search(r'(add|subtract|plus|minus)\s+(-?\d+(?:\.\d+)?)', st)
            if om: val = val+(float(om.group(2)) if om.group(1) in('add','plus') else -float(om.group(2))); did=True; continue
            om = re.search(r'(multiply|times)\s+(?:it\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)', st)
            if om: val*=float(om.group(2)); did=True; continue
            om = re.search(r'divide\s+(?:it\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)', st)
            if om and float(om.group(1)): val/=float(om.group(1)); did=True; continue
            if 'triple' in st: val*=3; did=True
            elif 'double' in st: val*=2; did=True
            elif 'halve' in st: val/=2; did=True
            elif 'square' in st: val**=2; did=True
            elif 'negate' in st: val=-val; did=True
        if not did: return None
        return int(val) if val==int(val) else val
    def _cm_belief(s, p):
        pl = p.lower()
        puts = re.findall(r'(\w+)\s+(?:puts?|places?|hides?)\s+(?:the\s+)?(\w+)\s+(?:in|on|under|behind|into)\s+(?:the\s+)?(\w+)', pl)
        leaves = re.findall(r'(\w+)\s+(?:leaves?|exits?|goes?\s+(?:out|away))', pl)
        moves = re.findall(r'(\w+)\s+(?:moves?|transfers?|takes?)\s+(?:the\s+)?(\w+)\s+(?:from\s+)?(?:\w+\s+)?(?:to|into)\s+(?:the\s+)?(\w+)', pl)
        if not puts: return None
        beliefs, absent, obj_loc = {}, set(), {}
        for who, obj, loc in puts:
            obj_loc[obj] = loc; beliefs.setdefault(who, {})[obj] = loc
            for a in beliefs:
                if a not in absent: beliefs[a][obj] = loc
        for who in leaves: absent.add(who)
        for who, obj, loc in moves:
            obj_loc[obj] = loc
            for a in beliefs:
                if a not in absent: beliefs.setdefault(a, {})[obj] = loc
        qm = re.search(r'where\s+(?:does|will)\s+(\w+)\s+(?:think|believe|look|expect)', pl)
        if qm:
            ag = qm.group(1)
            for obj in obj_loc:
                if ag in beliefs and obj in beliefs[ag]: return beliefs[ag][obj]
        return None
    def _cm_constraint(s, p):
        pl = p.lower()
        chose = re.findall(r'(\w+)\s+chose\s+(?:the\s+)?(\w+)', pl)
        not_chose = re.findall(r"(\w+)\s+(?:didn't|did\s*not|never)\s+cho(?:o?se)\s+(?:the\s+)?(\w+)", pl)
        diff = bool(re.search(r'(?:each|everyone)\s+chose\s+(?:a\s+)?different', pl))
        if not(chose or not_chose): return None
        agents = list(set(a for a,_ in chose+not_chose)); items = list(set(i for _,i in chose+not_chose))
        if len(agents)<2 or len(items)<2: return None
        fixed = {a:i for a,i in chose}; excluded = defaultdict(set)
        for a,i in not_chose: excluded[a].add(i)
        free_a = [a for a in agents if a not in fixed]; free_i = [i for i in items if i not in fixed.values()]
        sols = []
        for perm in permutations(free_i, len(free_a)):
            assign = dict(fixed); assign.update(zip(free_a, perm))
            if diff and len(set(assign.values()))!=len(assign): continue
            if all(assign.get(a,'') not in excl for a,excl in excluded.items()): sols.append(dict(assign))
        if len(sols)==1: return sols[0]
        return "impossible" if not sols else None
    def _cm_recursive(s, p):
        pl = p.lower()
        base = re.search(r'f\((\d+)\)\s*=\s*(-?\d+(?:\.\d+)?)', pl)
        rec = re.search(r'f\(n\)\s*=\s*(.+?)(?:\.|,|\s+for)', pl)
        # Find the LAST f(N) or "find f(N)" as the query
        queries = list(re.finditer(r'f\((\d+)\)', pl))
        find_q = re.search(r'find\s+f\s*\(\s*(\d+)\s*\)', pl)
        if not base or not rec: return None
        if find_q: qn = int(find_q.group(1))
        elif len(queries)>=2: qn = int(queries[-1].group(1))
        else: return None
        n0, v0 = int(base.group(1)), float(base.group(2)); expr = rec.group(1).strip()
        memo = {n0: v0}
        try:
            for i in range(n0+1, qn+1):
                val = expr.replace('f(n-1)', str(memo[i-1])).replace('f(n - 1)', str(memo[i-1]))
                val = val.replace('n', str(i)); memo[i] = eval(val, {"__builtins__": {}})
        except Exception: return None
        r = memo.get(qn)
        return int(r) if r is not None and isinstance(r, float) and r==int(r) else r
    def _cm_counterfactual(s, p):
        pl = p.lower()
        chains = re.findall(r'(\w[\w\s]*?)\s+(?:causes?|leads?\s+to|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)', pl)
        hypo = re.search(r"if\s+(?:the\s+)?(\w[\w\s]*?)\s+had(?:\s+not|n't)\s+happened", pl)
        if not chains or not hypo: return None
        removed = hypo.group(1).strip().lower(); g = defaultdict(set)
        for a,b in chains: g[a.strip().lower()].add(b.strip().lower())
        affected, q = set(), [removed]
        while q:
            n = q.pop(0)
            for ch in g.get(n, set()):
                if ch not in affected: affected.add(ch); q.append(ch)
        if affected: return "would_not_happen"
        return None
    def _cm_bayesian(s, p):
        pl = p.lower()
        base = re.search(r'(?:base\s+rate|prevalence|prior|probability)\s+(?:is\s+|of\s+)?(\d+(?:\.\d+)?)\s*%?', pl)
        sens = re.search(r'(?:sensitivity|true\s+positive|detection)\s+(?:rate\s+)?(?:is\s+|of\s+)?(\d+(?:\.\d+)?)\s*%?', pl)
        fpr = re.search(r'(?:false\s+positive|specificity)\s+(?:rate\s+)?(?:is\s+|of\s+)?(\d+(?:\.\d+)?)\s*%?', pl)
        if not base or not(sens or fpr): return None
        b = float(base.group(1)); b = b/100 if b>1 else b
        sv = float(sens.group(1)) if sens else 0.99; sv = sv/100 if sv>1 else sv
        f = float(fpr.group(1)) if fpr else 0.05; f = f/100 if f>1 else f
        if 'specificity' in pl and fpr: f = 1.0-f
        denom = sv*b + f*(1-b)
        if denom==0: return None
        return round((sv*b)/denom*100, 1)
    def _cm_info_suff(s, p):
        pl = p.lower()
        if re.search(r'(?:not\s+enough|insufficient|cannot\s+(?:be\s+)?determined?|indeterminate)', pl): return "cannot"
        if not re.search(r'(?:what\s+is|find|determine|calculate)', pl): return None
        vs = set(re.findall(r'\b([a-z])\b', pl))-{'a','i','is','if','in','it','or','of','on','at','to','so','no','do','an','as','am','be'}
        eqs = pl.count('=')+pl.count('equals')+pl.count('is equal')
        if len(vs)>max(eqs,1)+1 and re.search(r'(?:exactly|unique|precise)', pl): return "cannot"
        return None
    # ==== LAYER 2: STANDARD PARSERS ====
    def _sp(s, p):
        pl = p.lower(); pn = _ns(p)
        m = re.search(r'(?:which\s+is\s+)?(?:larger|greater|bigger|smaller|less).*?(-?\d+\.?\d*)\s+(?:or|and|vs)\s+(-?\d+\.?\d*)', pl)
        if m:
            a,b = float(m.group(1)),float(m.group(2))
            return ('num', min(a,b)) if('smaller' in pl or 'less' in pl) else ('num', max(a,b))
        m = re.search(r'(?:cost|total)s?\s+\$?([\d.]+).*?costs?\s+\$?([\d.]+)\s+more', pl)
        if m: return ('num', (float(m.group(1))-float(m.group(2)))/2)
        m = re.search(r'all\s+(?:but|except)\s+(\d+)', pl)
        if m and 'how many' in pl: return ('num', float(m.group(1)))
        m = re.search(r'(\d+)\s*(?:fence\s*)?posts?.*?(\d+)\s*(?:meter|feet|ft|m|yard)', pl)
        if m: return ('num', (int(m.group(1))-1)*int(m.group(2)))
        m = re.search(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)', pl)
        if m: return ('num', int(m.group(1))%int(m.group(2)))
        if re.search(r'coin.*(?:flip|toss)', pl) and re.search(r'(?:next|probability|chance|odds)', pl):
            return ('text', 'independent')
        if re.search(r'(?:odd|even)\s*[\+]\s*(?:odd|even)', pl):
            if pl.count('odd')==2 or pl.count('even')==2: return ('text', 'even')
            return ('text', 'odd')
        m = re.search(r'(\d+)\s+\w+\s+(?:in|into|among)\s+(\d+)', pl)
        if m and 'at least' in pl: return ('num', math.ceil(int(m.group(1))/int(m.group(2))))
        if re.search(r'if\s+\w+.*?then\s+\w+', pl) and re.search(r"(?:not|doesn't|didn't)\s+\w+", pl):
            if re.search(r'therefore|conclude|must\s+be|we\s+(?:can|know)', pl): return ('text', 'modus_tollens')
        alls = re.findall(r'all\s+(\w+)\s+are\s+(\w+)', pl)
        if len(alls)>=2:
            g = defaultdict(set)
            for a,b in alls: g[a.lower()].add(b.lower())
            return ('chain', g)
        svo = re.search(r'(?:the\s+)?(\w+)\s+(chased|bit|kicked|pushed|pulled|followed|ate|caught)\s+(?:the\s+)?(\w+)', pl)
        if svo and re.search(r'(?:who|what)\s+(?:was|got|did)', pl):
            return ('text', svo.group(3) if('was '+svo.group(2) in pl or 'got '+svo.group(2) in pl) else svo.group(1))
        if re.search(r'(?:base\s+rate|prevalence)', pl) and re.search(r'(?:test|positive)', pl): return ('text', 'base_rate')
        befores = re.findall(r'(\w+)\s+(?:happened\s+)?before\s+(\w+)', pl)
        afters = re.findall(r'(\w+)\s+(?:happened\s+)?after\s+(\w+)', pl)
        preceded = re.findall(r'(\w+)\s+preceded\s+(\w+)', pl)
        if befores or afters or preceded:
            edges, nodes = [], set()
            for a,b in befores: edges.append((a.lower(),b.lower())); nodes|={a.lower(),b.lower()}
            for a,b in afters: edges.append((b.lower(),a.lower())); nodes|={a.lower(),b.lower()}
            for a,b in preceded: edges.append((a.lower(),b.lower())); nodes|={a.lower(),b.lower()}
            if edges:
                gr,indeg = defaultdict(set), defaultdict(int)
                for a,b in edges: gr[a].add(b); indeg.setdefault(b,0); indeg.setdefault(a,0)
                for a,b in edges: indeg[b]+=1
                q = sorted([n for n in nodes if indeg[n]==0]); order = []
                while q:
                    n=q.pop(0); order.append(n)
                    for nb in sorted(gr[n]):
                        indeg[nb]-=1
                        if indeg[nb]==0: q.append(nb)
                    q.sort()
                return ('text', ', '.join(w.capitalize() for w in order))
        dm = re.findall(r'(?:go|walk|turn|move|head)\s+(north|south|east|west)', pl)
        if len(dm)>=2:
            dx=dy=0
            for d in dm:
                if d=='north': dy+=1
                elif d=='south': dy-=1
                elif d=='east': dx+=1
                elif d=='west': dx-=1
            dirs = []
            if dy>0: dirs.append('north')
            elif dy<0: dirs.append('south')
            if dx>0: dirs.append('east')
            elif dx<0: dirs.append('west')
            return ('text', '-'.join(dirs) if dirs else 'origin')
        if re.search(r'(?:increase|decrease).*?\d+\s*%.*?(?:then|back)', pl): return ('text', 'not_same')
        if 'correlat' in pl and re.search(r'(?:cause|causal)', pl): return ('text', 'no_cause')
        chain = re.findall(r'(\w[\w\s]*?)\s+(?:leads?\s+to|causes?|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)', p, re.I)
        if chain and re.search(r'(?:intervene|block|prevent|force)', pl): return ('text', 'stops')
        mps = re.search(r'on\s+(?:her|his|their|the)\s+(left|right)', pl)
        if mps and re.search(r'opposite\s+side|directly\s+across|faces?\s+\w+\s+from', pl):
            return ('text', 'right' if mps.group(1)=='left' else 'left')
        want = re.search(r'wants?\s+\w+\s+to\s+(?:go\s+|pick\s+(?:the\s+)?|take\s+(?:the\s+)?)(\w+)', pl)
        if want and re.search(r'(?:opposite|reliably\s+does\s+the\s+opposite)', pl):
            opp = {'left':'right','right':'left','north':'south','south':'north','east':'west','west':'east','red':'blue','blue':'red','up':'down','down':'up'}
            return ('text', opp.get(want.group(1).lower(), want.group(1).lower()))
        bm = re.search(r'(?:mistakenly\s+believes?|told\s+\w+\s+that)\s+(?:the\s+)?\w[\w\s]*?is\s+(\$?\w[\w\s:]*?)(?:\s*[\.(])', pl)
        if bm: return ('text', bm.group(1).strip())
        day_m = re.search(r'today\s+is\s+(\w+)', pl)
        if day_m:
            day = _DMAP.get(day_m.group(1).lower())
            if day is not None:
                offset = 0
                for t in re.findall(r'(?:day\s+before|day\s+after|yesterday|tomorrow)', pl[day_m.end():]):
                    offset += -1 if t in('yesterday','day before') else 1
                nm = re.search(r'(\d+)\s+days?\s+(?:from\s+now|later|ahead|after)', pl)
                if nm: offset += int(nm.group(1))
                nm = re.search(r'(\d+)\s+days?\s+(?:ago|before|earlier)', pl)
                if nm: offset -= int(nm.group(1))
                return ('text', _DAYS[(day+offset)%7].capitalize())
        tm = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm).*?(\d{1,2}):(\d{2})\s*(am|pm)', pl)
        if tm:
            h1,m1,ap1 = int(tm.group(1)),int(tm.group(2)),tm.group(3)
            h2,m2,ap2 = int(tm.group(4)),int(tm.group(5)),tm.group(6)
            if ap1=='pm' and h1!=12: h1+=12
            elif ap1=='am' and h1==12: h1=0
            if ap2=='pm' and h2!=12: h2+=12
            elif ap2=='am' and h2==12: h2=0
            t1,t2 = h1*60+m1, h2*60+m2
            if t2<=t1: t2+=1440
            d = t2-t1; return ('text', f"{d//60} hours and {d%60} minutes")
        pairs = re.findall(r'(\d{4}):\s*(\d+(?:\.\d+)?)', p)
        if len(pairs)>=3:
            vals = [float(v) for _,v in sorted(pairs)]
            d1 = [vals[i+1]-vals[i] for i in range(len(vals)-1)]
            d2 = [d1[i+1]-d1[i] for i in range(len(d1)-1)]
            if all(d>0 for d in d2): return ('text', 'Accelerating')
            if all(d<0 for d in d2): return ('text', 'Decelerating')
            if all(abs(d)<0.01 for d in d2): return ('text', 'Constant')
            return ('text', 'Accelerating' if sum(d2)/len(d2)>0 else 'Decelerating')
        ranges = re.findall(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', p)
        if len(ranges)>=2:
            def to_m(t): h,m=t.split(':'); return int(h)*60+int(m)
            ivs = [(to_m(a),to_m(b)) for a,b in ranges]
            for i in range(len(ivs)):
                for j in range(i+1,len(ivs)):
                    if ivs[i][0]<ivs[j][1] and ivs[j][0]<ivs[i][1]: return ('text','No')
            return ('text','Yes')
        age_v = {}
        for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!er)', pl): age_v[am.group(1).lower()]=float(am.group(2))
        age_c = []
        for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)', pl):
            age_c.append((am.group(1).lower(),float(am.group(2)),am.group(3),am.group(4).lower()))
        for am in re.finditer(r'(\w+)\s+is\s+(twice|half|triple|thrice|\d+)\s+(?:times?\s+)?(?:as\s+old\s+as\s+)?(\w+)', pl):
            mw = am.group(2).lower(); mu = {'twice':2,'half':0.5,'triple':3,'thrice':3}.get(mw)
            if mu is None:
                try: mu=float(mw)
                except: mu=2
            age_c.append((am.group(1).lower(),mu,'times',am.group(3).lower()))
        if age_v and age_c:
            for _ in range(30):
                ch = False
                for nm,v,rel,ref in age_c:
                    if rel=='older':
                        if ref in age_v and nm not in age_v: age_v[nm]=age_v[ref]+v; ch=True
                        if nm in age_v and ref not in age_v: age_v[ref]=age_v[nm]-v; ch=True
                    elif rel=='younger':
                        if ref in age_v and nm not in age_v: age_v[nm]=age_v[ref]-v; ch=True
                        if nm in age_v and ref not in age_v: age_v[ref]=age_v[nm]+v; ch=True
                    elif rel=='times':
                        if ref in age_v and nm not in age_v: age_v[nm]=age_v[ref]*v; ch=True
                        if nm in age_v and ref not in age_v and v: age_v[ref]=age_v[nm]/v; ch=True
                if not ch: break
            qm = re.search(r"(?:how\s+old\s+is|what\s+is)\s+(\w+)'?s?\s*(?:age)?", pl)
            if qm and qm.group(1).lower() in age_v: return ('num', age_v[qm.group(1).lower()])
            if age_v: return ('num', list(age_v.values())[-1])
        return None
    # ==== MATCHING ENGINE ====
    def _match(s, computed, c):
        cl = c.lower().strip(); cn = _ns(c)
        if isinstance(computed, (int, float)):
            if cn and any(abs(v-computed)<0.5 for v in cn): return 0.95
            st = str(int(computed)) if isinstance(computed,float) and computed==int(computed) else str(computed)
            if st in cl: return 0.95
            return 0.08
        if isinstance(computed, dict):
            for ag,it in computed.items():
                if ag in cl and it in cl: return 0.95
            return 0.15
        if isinstance(computed, str):
            comp = computed.lower()
            if comp in cl or cl in comp: return 0.95
            M = {'stops':('stop','unlikely','no longer','cease','would not'),
                 'independent':('1/2','0.5','50','same','independent'),
                 'no_cause':('confound','not necessarily','common cause','no,'),
                 'not_same':('not the same','less','lower','different'),
                 'modus_tollens':('not','cannot','must not'),
                 'base_rate':('low','unlikely','less','rare','small'),
                 'cannot':('cannot','not enough','insufficient','indeterminate'),
                 'would_not_happen':('no','would not',"wouldn't"),
                 'impossible':('impossible','no valid','cannot')}
            if comp in M and _h(c, *M[comp]): return 0.95
            if computed=='stops' and _h(c,'still','continue','directly'): return 0.08
            return 0.15
        if isinstance(computed, tuple):
            if computed[0] in('num','text'): return s._match(computed[1], c)
            if computed[0]=='chain':
                if _h(c,'yes') and not _h(c,'cannot'): return 0.90
                if _h(c,'no') or _h(c,'cannot'): return 0.08
                return 0.50
        return 0.50
    # ==== SCORING FLOW ====
    def _score(s, p, c):
        for fn in [s._cm_register, s._cm_seq_arith, s._cm_belief, s._cm_constraint,
                   s._cm_recursive, s._cm_counterfactual, s._cm_bayesian, s._cm_info_suff]:
            try: r = fn(p)
            except Exception: continue
            if r is not None: return s._match(r, c), fn.__name__
        sp = s._sp(p)
        if sp is not None:
            sc = s._match(sp, c)
            return (0.90 if sc>=0.90 else 0.12 if sc<=0.15 else sc), 'standard_parser'
        ncd = s._ncd(p, c)
        return 0.50+(1.0-ncd)*0.08, 'ncd_fallback'
    def evaluate(s, prompt: str, candidates: list) -> list:
        meta = s._meta(prompt); res = []
        for c in candidates:
            v, tag = s._score(prompt, c)
            res.append({'candidate':c,'score':round(v*(0.88+0.12*meta),4),'reasoning':tag,'meta':round(meta,3)})
        res.sort(key=lambda r: r['score'], reverse=True); return res
    def confidence(s, prompt: str, answer: str) -> float:
        meta = s._meta(prompt)
        if meta<0.30: return meta
        v,_ = s._score(prompt, answer); return round(min(meta, v), 4)
