"""Frame E Inference Engine — computation-first + metacognitive confidence tracking.
Every computation module reports (result, parse_confidence). Low parse_confidence
reduces overall score proportionally. 12 computation modules, 26 standard parsers,
Tier B meta-confidence traps. NCD fallback capped at 10%."""
import re, zlib, math, collections, itertools
_NUM = re.compile(r'-?\d+(?:\.\d+)?')
_DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
_DMAP = {d: i for i, d in enumerate(_DAYS)}
_STOP = {'a','i','is','if','in','it','or','of','on','at','to','so','no','do','an','as','am','be'}
_TB = {k: re.compile(v, re.I) for k, v in {'p':r'(?:stopped|still|again|already|anymore)',
    's':r'(?:every.*?some|all.*?not|not.*?all)','f':r'(?:either.*?or|must\s+be\s+one)',
    'v':r'(?:successful|survivors?|winners?|made\s+it)',
    'k':r'(?:already\s+(?:spent|invested|paid)|too\s+late\s+to)'}.items()}
def _ns(t): return [float(x) for x in _NUM.findall(t)]
def _h(t, *ws): return any(w in t.lower() for w in ws)
def _ncd(a, b):
    if not a or not b: return 1.0
    ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
    d = max(ca, cb)
    return (len(zlib.compress((a+" "+b).encode()))-min(ca,cb))/d if d else 1.0

class ReasoningTool:
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
    # ==== COMPUTATION MODULES (return (result, parse_confidence) or None) ====
    def _cm_register(s, p):
        pl = p.lower(); pc = 0.95
        m = re.search(r'(?:start|begin|set|let)\s+(?:with\s+)?(?:x\s*=\s*|value\s*(?:=|to|of)\s*|number\s+)(-?\d+(?:\.\d+)?)', pl)
        if not m:
            m = re.search(r'(\w+)\s*=\s*(-?\d+(?:\.\d+)?)', pl)
            if m: reg = float(m.group(2)); pc = 0.85
            else: return None
        else: reg = float(m.group(1))
        ops = re.findall(r'(add|subtract|multiply|divide|triple|double|halve|square|negate)\s+(?:\w+\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)?', pl)
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
            elif op=='negate': reg=-reg
        return (int(reg) if reg==int(reg) else reg, pc)
    def _cm_belief(s, p):
        pl = p.lower()
        puts = re.findall(r'(\w+)\s+(?:puts?|places?|hides?)\s+(?:the\s+)?(\w+)\s+(?:in|on|under|behind|into)\s+(?:the\s+)?(\w+)', pl)
        if not puts: return None
        leaves = re.findall(r'(\w+)\s+(?:leaves?|exits?|goes?\s+(?:out|away))', pl)
        moves = re.findall(r'(\w+)\s+(?:moves?|transfers?|takes?)\s+(?:the\s+)?(\w+)\s+(?:from\s+)?(?:\w+\s+)?(?:to|into)\s+(?:the\s+)?(\w+)', pl)
        beliefs, absent, obj_loc = {}, set(), {}
        for who,obj,loc in puts:
            obj_loc[obj]=loc; beliefs.setdefault(who,{})[obj]=loc
            for a in beliefs:
                if a not in absent: beliefs[a][obj]=loc
        for who in leaves: absent.add(who)
        for who,obj,loc in moves:
            obj_loc[obj]=loc
            for a in beliefs:
                if a not in absent: beliefs.setdefault(a,{})[obj]=loc
        qm = re.search(r'where\s+(?:does|will)\s+(\w+)\s+(?:think|believe|look|expect)', pl)
        if not qm: return None
        ag = qm.group(1)
        if ag in beliefs:
            for obj in obj_loc:
                if obj in beliefs[ag]: return (beliefs[ag][obj], 0.95)
        return None
    def _cm_recursive(s, p):
        pl = p.lower()
        base = re.search(r'f\((\d+)\)\s*=\s*(-?\d+(?:\.\d+)?)', pl)
        rec = re.search(r'f\(n\)\s*=\s*(.+?)(?:\.|,|\s+for|\s+find|\s+what)', pl)
        if not base or not rec: return None
        queries = list(re.finditer(r'f\((\d+)\)', pl))
        find_q = re.search(r'find\s+f\s*\(\s*(\d+)\s*\)', pl)
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
        if r is None: return None
        return (int(r) if isinstance(r, float) and r==int(r) else r, 0.90)
    def _cm_causal(s, p):
        pl = p.lower()
        chains = re.findall(r'(\w[\w\s]*?)\s+(?:causes?|leads?\s+to|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)', p, re.I)
        if not chains: return None
        g = collections.defaultdict(set)
        for a,b in chains: g[a.strip().lower()].add(b.strip().lower())
        if re.search(r'(?:intervene\s+to\s+block|forcibly\s+prevent|block|prevent)\s+\w', p, re.I): return ("stops", 0.90)
        if re.search(r'(?:force|set|clamp|fix)\s*\(?\s*\w+\s*(?:=|to)', p, re.I): return ("stops", 0.85)
        hypo = re.search(r"if\s+(?:the\s+)?(\w[\w\s]*?)\s+had(?:\s+not|n't)\s+happened", pl)
        if hypo:
            removed = hypo.group(1).strip().lower(); affected = set(); q = [removed]
            while q:
                n = q.pop(0)
                for ch in g.get(n, set()):
                    if ch not in affected: affected.add(ch); q.append(ch)
            if affected: return ("would_not_happen", 0.90)
        return None
    def _cm_bayes(s, p):
        pl = p.lower()
        base = re.search(r'(?:base\s+rate|prevalence|prior|probability)\s+(?:is\s+|of\s+)?(\d+(?:\.\d+)?)\s*%?', pl)
        sens = re.search(r'(?:sensitivity|true\s+positive|detection)\s+(?:rate\s+)?(?:is\s+|of\s+)?(\d+(?:\.\d+)?)\s*%?', pl)
        fpr = re.search(r'(?:false\s+positive|specificity)\s+(?:rate\s+)?(?:is\s+|of\s+)?(\d+(?:\.\d+)?)\s*%?', pl)
        if not base or not(sens or fpr): return None
        def _pct(v): x=float(v); return x/100 if x>1 else x
        b = _pct(base.group(1)); sv = _pct(sens.group(1)) if sens else 0.99; f = _pct(fpr.group(1)) if fpr else 0.05
        if 'specificity' in pl and fpr: f = 1.0-f
        denom = sv*b + f*(1-b)
        return (round((sv*b)/denom*100, 1), 0.95 if(sens and fpr) else 0.75) if denom else None
    def _cm_constraint(s, p):
        pl = p.lower()
        chose = re.findall(r'(\w+)\s+chose\s+(?:the\s+)?(\w+)', pl)
        not_chose = re.findall(r"(\w+)\s+(?:didn't|did\s*not|never)\s+cho(?:o?se)\s+(?:the\s+)?(\w+)", pl)
        if not(chose or not_chose): return None
        diff = bool(re.search(r'(?:each|everyone)\s+chose\s+(?:a\s+)?different', pl))
        agents = list(set(a for a,_ in chose+not_chose)); items = list(set(i for _,i in chose+not_chose))
        if len(agents)<2 or len(items)<2: return None
        fixed = dict(chose); excluded = collections.defaultdict(set)
        for a,i in not_chose: excluded[a].add(i)
        free_a = [a for a in agents if a not in fixed]; free_i = [i for i in items if i not in fixed.values()]
        sols = [dict(list(fixed.items())+list(zip(free_a,pm))) for pm in itertools.permutations(free_i, len(free_a))
                if (not diff or len(set(list(fixed.values())+list(pm)))==len(fixed)+len(pm))
                and all(dict(list(fixed.items())+list(zip(free_a,pm))).get(a,'') not in excl for a,excl in excluded.items())]
        if len(sols)==1: return (sols[0], 0.90)
        return ("impossible", 0.90) if not sols else None
    def _cm_arithmetic(s, p):
        pl = p.lower()
        m = re.search(r'start\s+(?:with\s+)?(?:the\s+number\s+)?(-?\d+(?:\.\d+)?)', pl)
        if not m: return None
        val = float(m.group(1)); rest = pl[m.end():]; did = False
        _kw = {'triple':('*',3),'double':('*',2),'halve':('/',2),'square':('**',2),'negate':('*',-1)}
        for st in re.split(r'[.;]\s*', rest):
            st = st.strip()
            if not st: continue
            om = re.search(r'(add|subtract|plus|minus)\s+(-?\d+(?:\.\d+)?)', st)
            if om: val += float(om.group(2))*(1 if om.group(1) in('add','plus') else -1); did=True; continue
            om = re.search(r'(multiply|times)\s+(?:it\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)', st)
            if om: val*=float(om.group(2)); did=True; continue
            om = re.search(r'divide\s+(?:it\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)', st)
            if om and float(om.group(1)): val/=float(om.group(1)); did=True; continue
            for kw,(op,n) in _kw.items():
                if kw in st:
                    val = val**n if op=='**' else val*n if op=='*' else val/n; did=True; break
        if not did: return None
        return (int(val) if val==int(val) else val, 0.92)
    def _cm_info_suff(s, p):
        pl = p.lower()
        if re.search(r'(?:not\s+enough|insufficient|cannot\s+(?:be\s+)?determined?|indeterminate)', pl):
            return ("cannot", 0.85)
        if not re.search(r'(?:what\s+is|find|determine|calculate)', pl): return None
        vs = set(re.findall(r'\b([a-z])\b', pl))-_STOP
        eqs = pl.count('=')+pl.count('equals')+pl.count('is equal')
        if len(vs)>max(eqs,1)+1 and re.search(r'(?:exactly|unique|precise)', pl): return ("cannot", 0.80)
        return None
    def _cm_exception(s, p):
        pl = p.lower()
        defaults = re.findall(r'(?:by\s+default|normally|usually|generally)\s*,?\s*([\w\s]+?)(?:\.|,|$)', pl)
        overrides = re.findall(r'(?:but|except|however|unless)\s+(\w+)\s+(?:is|are|has|gets?|receives?)\s+([\w\s]+?)(?:\.|,|$)', pl)
        if not defaults or not overrides: return None
        rules = dict([(w.lower(),wh.strip()) for w,wh in overrides]+[('_default',defaults[0].strip())])
        qm = re.search(r'(?:what|which|how)\s+(?:does|about|for)\s+(\w+)', pl)
        if qm and rules.get(qm.group(1).lower(), rules.get('_default')): return (rules.get(qm.group(1).lower(), rules['_default']), 0.80)
        return None
    def _cm_consistency(s, p):
        pl = p.lower(); stmts = re.findall(r'(\w+)\s+is\s+(not\s+)?(?:a\s+)?(\w+)', pl)
        if len(stmts)<2: return None
        pos, neg = collections.defaultdict(set), collections.defaultdict(set)
        for subj,negation,pred in stmts: (neg if negation else pos)[subj.lower()].add(pred.lower())
        return ("contradiction", 0.90) if any(pos[k]&neg[k] for k in pos) else None
    def _cm_time_intervals(s, p):
        ranges = re.findall(r'(\d{1,2}:\d{2})\s*(?:-|to)\s*(\d{1,2}:\d{2})', p)
        if len(ranges)<2: return None
        def _tm(t): h,m=t.split(':'); return int(h)*60+int(m)
        ivs = [(_tm(a),_tm(b)) for a,b in ranges]
        has_overlap = any(ivs[i][0]<ivs[j][1] and ivs[j][0]<ivs[i][1] for i in range(len(ivs)) for j in range(i+1,len(ivs)))
        return ("overlap" if has_overlap else "no_overlap", 0.92)
    def _cm_value_prop(s, p):
        pl = p.lower()
        assigns = re.findall(r'(\w+)\s*=\s*(-?\d+(?:\.\d+)?)', pl)
        deps = re.findall(r'(\w+)\s*=\s*(\w+)\s*([\+\-\*/])\s*(-?\d+(?:\.\d+)?)', pl)
        if not assigns and not deps: return None
        vals = {k: float(v) for k, v in assigns}; _op = {'+':lambda a,b:a+b,'-':lambda a,b:a-b,'*':lambda a,b:a*b,'/':lambda a,b:a/b if b else a}
        for _ in range(20):
            ch = False
            for tgt,src,op,num in deps:
                if src in vals and tgt not in vals: vals[tgt]=_op[op](vals[src],float(num)); ch=True
            if not ch: break
        qm = re.search(r'(?:what\s+is|find|value\s+of)\s+(\w+)', pl)
        if qm and qm.group(1) in vals:
            r = vals[qm.group(1)]; return (int(r) if r==int(r) else r, 0.88)
        return None
    # ==== STANDARD PARSERS (Tier 1 — each returns (kind, value, parse_conf) or None) ====
    def _sp(s, p):
        pl = p.lower(); pn = _ns(p)
        m = re.search(r'(?:which\s+is\s+)?(?:larger|greater|bigger|smaller|less).*?(-?\d+\.?\d*)\s+(?:or|and|vs)\s+(-?\d+\.?\d*)', pl)
        if m:
            a,b = float(m.group(1)),float(m.group(2))
            return ('num', min(a,b) if('smaller' in pl or 'less' in pl) else max(a,b), 0.95)
        m = re.search(r'(?:cost|total)s?\s+\$?([\d.]+).*?costs?\s+\$?([\d.]+)\s+more', pl)
        if m: return ('num', (float(m.group(1))-float(m.group(2)))/2, 0.95)
        m = re.search(r'all\s+(?:but|except)\s+(\d+)', pl)
        if m and 'how many' in pl: return ('num', float(m.group(1)), 0.90)
        m = re.search(r'(\d+)\s*(?:fence\s*)?posts?.*?(\d+)\s*(?:meter|feet|ft|m|yard)', pl)
        if m: return ('num', (int(m.group(1))-1)*int(m.group(2)), 0.92)
        m = re.search(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)', pl)
        if m: return ('num', int(m.group(1))%int(m.group(2)), 0.95)
        if re.search(r'coin.*(?:flip|toss)', pl) and re.search(r'(?:next|probability|chance|odds)', pl):
            return ('text', 'independent', 0.92)
        if re.search(r'(?:odd|even)\s*[\+]\s*(?:odd|even)', pl):
            return ('text', 'even' if pl.count('odd')==2 or pl.count('even')==2 else 'odd', 0.95)
        m = re.search(r'(\d+)\s+\w+\s+(?:in|into|among)\s+(\d+)', pl)
        if m and 'at least' in pl: return ('num', math.ceil(int(m.group(1))/int(m.group(2))), 0.90)
        if re.search(r'if\s+\w+.*?then\s+\w+', pl) and re.search(r"(?:not|doesn't|didn't)\s+\w+", pl):
            if re.search(r'therefore|conclude|must\s+be|we\s+(?:can|know)', pl): return ('text','modus_tollens',0.85)
        alls = re.findall(r'all\s+(\w+)\s+are\s+(\w+)', pl)
        if len(alls)>=2:
            g = collections.defaultdict(set)
            for a,b in alls: g[a.lower()].add(b.lower())
            return ('chain', g, 0.88)
        svo = re.search(r'(?:the\s+)?(\w+)\s+(chased|bit|kicked|pushed|pulled|followed|ate|caught)\s+(?:the\s+)?(\w+)', pl)
        if svo and re.search(r'(?:who|what)\s+(?:was|got|did)', pl):
            return ('text', svo.group(3) if('was '+svo.group(2) in pl or 'got '+svo.group(2) in pl) else svo.group(1), 0.90)
        if re.search(r'(?:base\s+rate|prevalence)', pl) and re.search(r'(?:test|positive)', pl):
            return ('text', 'base_rate', 0.80)
        dm = re.findall(r'(?:go|walk|turn|move|head)\s+(north|south|east|west)', pl)
        if len(dm)>=2:
            _dv = {'north':(0,1),'south':(0,-1),'east':(1,0),'west':(-1,0)}
            dx = sum(_dv[d][0] for d in dm); dy = sum(_dv[d][1] for d in dm)
            dirs = (['north'] if dy>0 else ['south'] if dy<0 else [])+(['east'] if dx>0 else ['west'] if dx<0 else [])
            return ('text', '-'.join(dirs) if dirs else 'origin', 0.92)
        if re.search(r'(?:increase|decrease).*?\d+\s*%.*?(?:then|back)', pl): return ('text','not_same',0.90)
        if 'correlat' in pl and re.search(r'(?:cause|causal)', pl): return ('text','no_cause',0.88)
        chain = re.findall(r'(\w[\w\s]*?)\s+(?:leads?\s+to|causes?|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)', p, re.I)
        if chain and re.search(r'(?:intervene|block|prevent|force)', pl): return ('text','stops',0.85)
        mps = re.search(r'on\s+(?:her|his|their|the)\s+(left|right)', pl)
        if mps and re.search(r'opposite\s+side|directly\s+across|faces?\s+\w+\s+from', pl):
            return ('text', 'right' if mps.group(1)=='left' else 'left', 0.90)
        want = re.search(r'wants?\s+\w+\s+to\s+(?:go\s+|pick\s+(?:the\s+)?|take\s+(?:the\s+)?)(\w+)', pl)
        if want and re.search(r'(?:opposite|reliably\s+does\s+the\s+opposite)', pl):
            opp = {'left':'right','right':'left','north':'south','south':'north','east':'west','west':'east','red':'blue','blue':'red','up':'down','down':'up'}
            return ('text', opp.get(want.group(1).lower(), want.group(1).lower()), 0.90)
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
                return ('text', _DAYS[(day+offset)%7].capitalize(), 0.95)
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
            d = t2-t1; return ('text', f"{d//60} hours and {d%60} minutes", 0.95)
        pairs = re.findall(r'(\d{4}):\s*(\d+(?:\.\d+)?)', p)
        if len(pairs)>=3:
            vals = [float(v) for _,v in sorted(pairs)]
            d1 = [vals[i+1]-vals[i] for i in range(len(vals)-1)]
            d2 = [d1[i+1]-d1[i] for i in range(len(d1)-1)]
            if all(d>0 for d in d2): return ('text','Accelerating',0.88)
            if all(d<0 for d in d2): return ('text','Decelerating',0.88)
            if all(abs(d)<0.01 for d in d2): return ('text','Constant',0.88)
            return ('text', 'Accelerating' if sum(d2)/len(d2)>0 else 'Decelerating', 0.75)
        ranges = re.findall(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', p)
        if len(ranges)>=2:
            def to_m(t): h,m=t.split(':'); return int(h)*60+int(m)
            ivs = [(to_m(a),to_m(b)) for a,b in ranges]
            for i in range(len(ivs)):
                for j in range(i+1,len(ivs)):
                    if ivs[i][0]<ivs[j][1] and ivs[j][0]<ivs[i][1]: return ('text','No',0.90)
            return ('text','Yes',0.90)
        age_v = {am.group(1).lower():float(am.group(2)) for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!er)', pl)}
        age_c = [(am.group(1).lower(),float(am.group(2)),am.group(3),am.group(4).lower()) for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)', pl)]
        for am in re.finditer(r'(\w+)\s+is\s+(twice|half|triple|thrice|\d+)\s+(?:times?\s+)?(?:as\s+old\s+as\s+)?(\w+)', pl):
            mw = am.group(2).lower(); mu = {'twice':2,'half':0.5,'triple':3,'thrice':3}.get(mw, None)
            if mu is None:
                try: mu=float(mw)
                except: mu=2
            age_c.append((am.group(1).lower(),mu,'times',am.group(3).lower()))
        if age_v and age_c:
            _ops = {'older':(1,-1),'younger':(-1,1),'times':('*','/')}
            for _ in range(30):
                ch = False
                for nm,v,rel,ref in age_c:
                    if rel in('older','younger'):
                        s1,s2 = _ops[rel]
                        if ref in age_v and nm not in age_v: age_v[nm]=age_v[ref]+s1*v; ch=True
                        if nm in age_v and ref not in age_v: age_v[ref]=age_v[nm]+s2*v; ch=True
                    elif rel=='times':
                        if ref in age_v and nm not in age_v: age_v[nm]=age_v[ref]*v; ch=True
                        if nm in age_v and ref not in age_v and v: age_v[ref]=age_v[nm]/v; ch=True
                if not ch: break
            qm = re.search(r"(?:how\s+old\s+is|what\s+is)\s+(\w+)'?s?\s*(?:age)?", pl)
            if qm and qm.group(1).lower() in age_v: return ('num', age_v[qm.group(1).lower()], 0.90)
            if age_v: return ('num', list(age_v.values())[-1], 0.80)
        befores = re.findall(r'(\w+)\s+(?:happened\s+)?before\s+(\w+)', pl)
        afters = re.findall(r'(\w+)\s+(?:happened\s+)?after\s+(\w+)', pl)
        if befores or afters:
            edges = [(a.lower(),b.lower()) for a,b in befores]+[(b.lower(),a.lower()) for a,b in afters]
            nodes = set(n for e in edges for n in e)
            if edges:
                gr,indeg = collections.defaultdict(set), {n:0 for n in nodes}
                for a,b in edges: gr[a].add(b); indeg[b]+=1
                q = sorted(n for n in nodes if indeg[n]==0); order = []
                while q:
                    n=q.pop(0); order.append(n)
                    for nb in sorted(gr[n]):
                        indeg[nb]-=1
                        if indeg[nb]==0: q.append(nb)
                    q.sort()
                return ('text', ', '.join(w.capitalize() for w in order), 0.88)
        bm = re.search(r'(?:mistakenly\s+believes?|told\s+\w+\s+that)\s+(?:the\s+)?\w[\w\s]*?is\s+(\$?\w[\w\s:]*?)(?:\s*[\.(])', pl)
        if bm: return ('text', bm.group(1).strip(), 0.85)
        if re.search(r'(?:tampered|rigged|loaded|fixed)\s+(?:with\s+)?to\s+always', pl):
            if re.search(r"(?:does\s+not|doesn't|has\s+no\s+idea|not\s+know)", pl):
                if 'die' in pl or 'dice' in pl: return ('text','1/6',0.90)
                if 'coin' in pl: return ('text','1/2',0.90)
                if 'card' in pl: return ('text','1/52',0.90)
        return None
    # ==== MATCHING ENGINE ====
    def _match(s, computed, c):
        cl = c.lower().strip(); cn = _ns(c)
        if isinstance(computed, (int, float)):
            if cn and any(abs(v-computed)<0.5 for v in cn): return 0.95
            st = str(int(computed)) if isinstance(computed,float) and computed==int(computed) else str(computed)
            return 0.95 if st in cl else 0.08
        if isinstance(computed, dict):
            for ag,it in computed.items():
                if ag in cl and it in cl: return 0.95
            return 0.15
        if isinstance(computed, str):
            comp = computed.lower()
            if comp in cl or cl in comp: return 0.95
            _M = {'stops':('stop','unlikely','no longer','cease','would not'),'independent':('1/2','0.5','50','same','independent'),'no_cause':('confound','not necessarily','common cause','no,'),'not_same':('not the same','less','lower','different'),'modus_tollens':('not','cannot','must not'),'base_rate':('low','unlikely','less','rare','small'),'cannot':('cannot','not enough','insufficient','indeterminate'),'would_not_happen':('no','would not',"wouldn't"),'impossible':('impossible','no valid','cannot'),'overlap':('overlap','conflict','no','cannot'),'no_overlap':('yes','compatible','no conflict'),'contradiction':('contradiction','inconsistent','false')}
            if comp in _M and _h(c, *_M[comp]): return 0.95
            if computed=='stops' and _h(c,'still','continue','directly'): return 0.08
            return 0.15
        return 0.50
    def _match_sp(s, sp, c):
        kind, val = sp[0], sp[1]; pc = sp[2] if len(sp)>2 else 0.85
        if kind in('num','text'): return s._match(val, c), pc
        if kind=='chain':
            if _h(c,'yes') and not _h(c,'cannot'): return 0.90, pc
            if _h(c,'no') or _h(c,'cannot'): return 0.08, pc
            return 0.50, pc
        return 0.50, pc
    # ==== SCORING FLOW (parse_confidence scales result) ====
    def _score(s, p, c):
        for fn in [s._cm_register, s._cm_arithmetic, s._cm_belief, s._cm_constraint,
                   s._cm_recursive, s._cm_causal, s._cm_bayes, s._cm_info_suff,
                   s._cm_exception, s._cm_consistency, s._cm_time_intervals, s._cm_value_prop]:
            try: r = fn(p)
            except Exception: continue
            if r is not None:
                result, pc = r; base = s._match(result, c)
                return base*pc + 0.50*(1.0-pc), fn.__name__, pc
        sp = s._sp(p)
        if sp is not None:
            base, pc = s._match_sp(sp, c)
            return base*pc + 0.50*(1.0-pc), 'standard_parser', pc
        ncd = _ncd(p, c)
        return 0.50+(1.0-ncd)*0.08, 'ncd_fallback', 0.50
    def evaluate(s, prompt: str, candidates: list) -> list:
        meta = s._meta(prompt); res = []
        for c in candidates:
            v, tag, pc = s._score(prompt, c)
            res.append({'candidate':c,'score':round(v*(0.88+0.12*meta),4),
                        'reasoning':tag,'meta':round(meta,3),'parse_confidence':round(pc,3)})
        res.sort(key=lambda r: r['score'], reverse=True); return res
    def confidence(s, prompt: str, answer: str) -> float:
        meta = s._meta(prompt)
        if meta<0.30: return meta
        v,_,pc = s._score(prompt, answer); return round(min(meta, v*pc), 4)
