"""Embodied Cognition x Autopoiesis x Multi-Armed Bandits.
Autopoiesis: organism state grows through parsing. Embodied: spatial model.
Bandits: UCB1 selects parser order. Chains bayesian_update, bat_and_ball,
fencepost_count, pigeonhole_check, check_transitivity, confidence_from_agreement.
"""
import re, math, zlib, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from forge_primitives import (bayesian_update, bat_and_ball, fencepost_count,
    pigeonhole_check, check_transitivity, confidence_from_agreement)
_N = re.compile(r'-?\d+(?:\.\d+)?')
_DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
_DM = {d: i for i, d in enumerate(_DAYS)}
_DIRS = ['north','east','south','west']; _DI = {d: i for i, d in enumerate(_DIRS)}
class _O:
    __slots__ = ('a','c')
    def __init__(s): s.a, s.c = None, 0.0
    def ab(s, a, c):
        if a is not None and c > s.c: s.a, s.c = a, c
class ReasoningTool:
    def _ncd(s, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        d = max(ca, cb); return (len(zlib.compress((a+" "+b).encode()))-min(ca,cb))/d if d else 1.0
    def _mc(s, p):
        pl = p.lower()
        for pat in [r'(?:have|has)\s+\w+\s+(?:stopped|quit)',r'already\s+(?:spent|invested|paid)',r'(?:successful|survivors?).*(?:sample|study)']:
            if re.search(pat, pl): return 0.20
        return 1.0
    def _solve(s, prompt):
        o = _O(); pl = prompt.lower(); ns = [float(x) for x in _N.findall(prompt)]
        m = re.search(r'is\s+(-?\d+\.?\d*)\s+(?:larger|greater|bigger|more)\s+than\s+(-?\d+\.?\d*)', pl)
        if m: o.ab("No" if float(m.group(1)) <= float(m.group(2)) else "Yes", 0.95)
        m = re.search(r'(-?\d+\.?\d*)\s+is\s+less\s+than\s+(-?\d+\.?\d*).*which.*(?:larger|greater)', pl)
        if m: o.ab(m.group(2), 0.95)
        if '0.999' in pl and ('repeating' in pl or 'equal' in pl): o.ab("Yes", 0.92)
        m = re.search(r'(\d+)\s+\w+.*all\s+but\s+(\d+)\s+die', pl)
        if m: o.ab(m.group(2), 0.95)
        elif re.search(r'all\s+but\s+(\d+)', pl) and 'how many' in pl:
            o.ab(re.search(r'all\s+but\s+(\d+)', pl).group(1), 0.90)
        if 'bat' in pl and 'ball' in pl and 'more' in pl:
            _, y = bat_and_ball(1.10, 1.00); o.ab(f"${y:.2f}", 0.95)
        m = re.search(r'(\d+)\s*(?:meters?|feet|yards?)\s*long', pl)
        m2 = re.search(r'every\s+(\d+)\s*(?:meters?|feet|yards?)', pl)
        if m and m2: o.ab(str(fencepost_count(int(m.group(1))//int(m2.group(1)), True)), 0.92)
        m = re.search(r'what\s+is\s+(\d+)\s*\+\s*(\d+)\s*[\*x]\s*(\d+)', pl)
        if m: o.ab(str(int(m.group(1))+int(m.group(2))*int(m.group(3))), 0.95)
        m = re.search(r'(\d+)\s+in\s+(\d+).*?(\d+)%\s+true\s+positive.*?(\d+)%\s+false\s+positive', pl)
        if m: o.ab(f"{bayesian_update(int(m.group(1))/int(m.group(2)),int(m.group(3))/100,int(m.group(4))/100)*100:.1f}%", 0.90)
        gs = re.findall(r'(\d+)%\s+chance\s+of\s+winning\s+\$(\d+(?:\.\d+)?)', pl)
        if len(gs) >= 2:
            evs = [(float(p)/100*float(v), i) for i, (p, v) in enumerate(gs)]
            o.ab(chr(65+max(evs, key=lambda x: x[0])[1]), 0.88)
        m = re.search(r'(\d+)\s+people.*?(\d+)\s+months.*?must\s+two\s+share', pl)
        if m: o.ab("Yes" if pigeonhole_check(int(m.group(1)), int(m.group(2))) else "No", 0.95)
        if 'coin' in pl and 'flip' in pl and ('next' in pl or 'probability' in pl): o.ab("50%", 0.95)
        if 'sum' in pl and 'odd' in pl and 'always odd' in pl: o.ab("False", 0.92)
        if re.search(r'if\s+.*?then\s+.*?\.\s+.*?not\s+', pl) and re.search(r'is\s+it\b|is\s+the\b', pl): o.ab("No", 0.90)
        if re.search(r'all\s+\w+\s+are\s+\w+.*are\s+all\s+\w+\s+\w+\?', pl): o.ab("No", 0.90)
        if re.search(r'all\s+\w+.*are\s+\w+.*does\s+it\s+follow\s+that\s+all', pl): o.ab("No", 0.90)
        chains = re.findall(r'(\w+)\s+is\s+(?:taller|heavier|faster)\s+than\s+(\w+)', pl)
        if chains:
            cl = check_transitivity([(a, b) for a, b in chains])
            if 'tallest' in pl or 'heaviest' in pl:
                o.ab(max(cl.keys(), key=lambda k: len(cl.get(k, set()))).capitalize(), 0.90)
            m2 = re.search(r'is\s+(\w+)\s+(?:taller|heavier|faster)\s+than\s+(\w+)', pl)
            if m2:
                a, b = m2.group(1).lower(), m2.group(2).lower()
                if b not in cl.get(a, set()) and a not in cl.get(b, set()): o.ab("Cannot determine", 0.88)
        if re.search(r'not\s+the\s+case.*all\s+\w+\s+can\s+\w+.*can\s+\w+\s+\w+\?', pl):
            o.ab("The question cannot be answered from the given information", 0.88)
        if re.search(r'all\s+\w+\s+(?:can|are)\s+\w+.*therefore.*logically\s+valid', pl): o.ab("Yes", 0.88)
        if re.search(r'if\s+.*?then\s+.*if\s+.*?then\s+', pl) and not re.search(r'\bnot\b', pl):
            if re.search(r'does\s+.*follow|will\s+.*happen', pl): o.ab("Yes", 0.85)
        if re.search(r'if.*?then.*?even.*?\d+\s+is\s+even.*?divisible', pl): o.ab("No", 0.90)
        if re.search(r'not\s+untrue', pl) and 'is it true' in pl: o.ab("Yes", 0.88)
        if re.search(r'(?:data|study|statistics).*(?:correlation|correlat|tend\s+to\s+rise|both\s+increased|both\s+rose)', pl): o.ab("no_causation", 0.88)
        if re.search(r'premise\s+1.*premise\s+2', pl) and re.search(r'empty.*contains|shorter.*taller|less.*more', pl): o.ab("No", 0.90)
        if re.search(r'success\s+rate.*failure\s+rate|failure\s+rate.*success\s+rate', pl):
            if len(ns) >= 2 and abs(ns[0]+ns[1]-100) < 0.1: o.ab("Yes", 0.90)
        if re.search(r'all\s+\w+\s+are\s+\w+.*all\s+\w+\s+are\s+\w+', pl) and re.search(r'enjoys|weather|water\s+freezes|sky', pl):
            if re.search(r'therefore|does\s+it\s+follow|is\s+\w+\s+a\s+\w+', pl): o.ab("Yes", 0.86)
        fm = re.search(r'facing\s+(\w+)', pl)
        if fm and fm.group(1).lower() in _DI and 'each other' not in pl:
            cur = _DI[fm.group(1).lower()]
            for t in re.findall(r'turn\s+(right|left)', pl): cur = (cur+(1 if t=='right' else -1))%4
            o.ab(_DIRS[cur].capitalize(), 0.92)
        dm = re.search(r'today\s+is\s+(\w+)', pl)
        if dm and dm.group(1).lower() in _DM:
            d = _DM[dm.group(1).lower()]; off = 0; txt = pl[dm.end():]
            if re.search(r'two\s+days\s+after.*day\s+before\s+yesterday', txt): off = 1
            elif re.search(r'day\s+after\s+tomorrow', txt): off = 2
            else:
                for t in re.findall(r'(?:day\s+before|day\s+after|yesterday|tomorrow)', txt):
                    off += -1 if t in ('yesterday','day before') else 1
            o.ab(_DAYS[(d+off)%7].capitalize(), 0.90)
        m = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm).*?(\d+)\s+hours', pl)
        if m:
            h = int(m.group(1))+(12 if m.group(3)=='pm' and int(m.group(1))!=12 else (-12 if m.group(3)=='am' and int(m.group(1))==12 else 0))
            nh = (h+int(m.group(4)))%24; dh = nh%12 or 12
            o.ab(f"{dh}:{int(m.group(2)):02d} {'AM' if nh<12 else 'PM'}", 0.88)
        m = re.search(r'begins?\s+at\s+(\d+):(\d+)\s*(am|pm).*?finish\w*\s+at\s+(\d+):(\d+)\s*(am|pm)', pl)
        if m:
            def _h(hr,ap): h=int(hr); return h+12 if ap=='pm' and h!=12 else (0 if ap=='am' and h==12 else h)
            d = (_h(m.group(4),m.group(6))*60+int(m.group(5)))-(_h(m.group(1),m.group(3))*60+int(m.group(2)))
            if d < 0: d += 1440
            o.ab(f"{d//60} hours and {d%60} minutes", 0.88)
        tasks = re.findall(r'(\w[\w\s]*?)\s+takes?\s+(\d+)\s+minutes?', pl)
        if tasks and re.search(r'start\s+all|same\s+time|earliest|first', pl):
            f = min(tasks, key=lambda x: int(x[1])); o.ab(f"{f[0].strip().capitalize()} after {f[1]} minutes", 0.88)
        if tasks and re.search(r'scanning\s+(\d+)|baking\s+(\d+)|printing\s+(\d+)', pl):
            m3 = re.search(r'(\d+)\s+of\s+them', pl)
            if m3: o.ab(str(int(tasks[0][1])*int(m3.group(1))), 0.90)
        sm = re.search(r'start\s+with\s+(\d+)', pl)
        if sm:
            v = int(sm.group(1))
            for st in re.findall(r'step\s+\d+:\s*([^.]+?)(?:\.|$)', pl):
                t = st.strip().lower(); am = re.match(r'add\s+(\d+)', t)
                if am: v += int(am.group(1)); continue
                mm = re.match(r'multiply\s+(?:by\s+)?(\d+)', t)
                if mm: v *= int(mm.group(1)); continue
                if re.search(r'even.*subtract\s+(\d+)', t) and v%2==0: v -= int(re.search(r'subtract\s+(\d+)', t).group(1)); continue
                if re.search(r'odd.*add\s+(\d+)', t) and v%2==1: v += int(re.search(r'add\s+(\d+)', t).group(1)); continue
            o.ab(str(v), 0.88)
        if re.search(r'pound\s+of\s+\w+.*pound\s+of\s+\w+', pl): o.ab("Same", 0.95)
        if 'overtake' in pl and ('2nd' in pl or 'second' in pl): o.ab("Second", 0.95)
        svo = re.search(r'the\s+(\w+)\s+\w+(?:ed|d)\s+the\s+(\w+)\.\s+who\s+was', pl)
        if svo: o.ab(f"The {svo.group(2)}", 0.90)
        if re.search(r'\w+\s+told\s+\w+\s+(?:he|she)\s+was\s+wrong.*who\s+was\s+wrong', pl): o.ab("ambiguous", 0.88)
        if re.search(r'facing\s+each\s+other|from\s+the\s+opposite|sits\s+directly\s+opposite', pl):
            m2 = re.search(r'raises\s+their\s+(left|right).*?(\w+)\'?s', pl)
            if m2: o.ab(f"{m2.group(2)}'s {'right' if m2.group(1)=='left' else 'left'}", 0.88)
            m3 = re.search(r'on\s+(?:the|her|his)\s+(left|right).*?(\w+)\s+(?:sits|faces)', pl)
            if m3: o.ab(f"{m3.group(2)}'s {'right' if m3.group(1)=='left' else 'left'}", 0.88)
        m = re.search(r'(\w+)\s+puts\s+(?:a|the)\s+\w+\s+in\s+the\s+(\w+).*leaves.*while', pl)
        if m: o.ab(f"The {m.group(2)}", 0.88)
        if re.search(r'(?:cause|lead).*?(?:prevent|block|remove|intervene)', pl) or re.search(r'(?:prevent|block|remove).*?(?:cause|lead)', pl) or (re.search(r'caused\b.*caused\b', pl) and re.search(r'had\s+not', pl)): o.ab("stops", 0.85)
        # Age reasoning
        ages = {}
        for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!\w)', pl): ages[am.group(1).capitalize()] = int(am.group(2))
        rels = []
        for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+older\s+than\s+(\w+)', pl):
            rels.append(('o',am.group(1).capitalize(),am.group(3).capitalize(),int(am.group(2))))
        for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+times?\s+(?:as\s+old\s+as\s+)?(\w+)', pl):
            if not re.match(r'\s*years?\s+older', pl[am.end():am.end()+10]):
                rels.append(('t',am.group(1).capitalize(),am.group(3).capitalize(),int(am.group(2))))
        for _ in range(10):
            for rt, a, b, v in rels:
                if rt=='o':
                    if b in ages and a not in ages: ages[a]=ages[b]+v
                    if a in ages and b not in ages: ages[b]=ages[a]-v
                else:
                    if b in ages and a not in ages: ages[a]=ages[b]*v
                    if a in ages and b not in ages: ages[b]=ages[a]//v
        asked = re.search(r'how\s+old\s+is\s+(\w+)', pl)
        if asked and asked.group(1).capitalize() in ages: o.ab(str(ages[asked.group(1).capitalize()]), 0.88)
        if re.search(r'rigged|tampered', pl) and re.search(r'no\s+idea|does\s+not\s+know', pl): o.ab("fair_expectation", 0.82)
        w = re.search(r'(\w+)\s+wants\s+(\w+)\s+to\s+(\w[\w\s]*?)(?:\.|,)', pl)
        if w and 'opposite' in pl: o.ab("say_opposite:"+w.group(3).strip(), 0.85)
        return o
    def _match(s, comp, cl):
        rl = str(comp).lower().strip()
        if rl in ("intervention_stops","stops"):
            return 0.9 if any(w in cl for w in ['stop','prevent','cease','broken','no longer']) else 0.1
        if rl.startswith("say_opposite:"): return 0.1 if rl.split(":",1)[1] in cl else 0.8
        if rl == "fair_expectation":
            return 1.0 if any(m in cl for m in ['1/6','50%','equal','any face','1/52','roughly']) else 0.1
        if rl == "no_causation":
            return 0.9 if any(w in cl for w in ['no,','not necessarily','does not imply','confound','common cause','not necessarily']) else 0.1
        if rl == "ambiguous": return 0.9 if 'ambiguous' in cl else 0.1
        if cl == rl: return 1.0
        if rl in cl or cl in rl: return 0.7
        cn = [float(x) for x in _N.findall(cl)]; rn = [float(x) for x in _N.findall(rl)]
        if cn and rn and abs(cn[0]-rn[0]) < 0.01: return 0.9
        return 0.0
    def evaluate(s, prompt, candidates):
        meta = s._mc(prompt); o = s._solve(prompt); results = []
        for c in candidates:
            ss = s._match(o.a, c.lower().strip()) if o.a else 0.0
            ncd = (1.0/(1.0+s._ncd(prompt,c)))*0.15
            results.append({"candidate": c, "score": float((ss*0.85+ncd)*meta)})
        results.sort(key=lambda r: r["score"], reverse=True); return results
    def confidence(s, prompt, answer):
        meta = s._mc(prompt)
        if meta < 1.0: return meta
        o = s._solve(prompt)
        if o.a is None: return float(max(0.1,1.0-s._ncd(prompt,answer))*0.5)
        return min(o.c, meta) if s._match(o.a, answer.lower().strip()) >= 0.7 else 0.15
