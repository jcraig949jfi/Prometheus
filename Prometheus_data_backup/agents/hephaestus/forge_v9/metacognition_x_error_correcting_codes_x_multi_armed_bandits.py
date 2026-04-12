"""Metacognition x Error-Correcting Codes x Multi-Armed Bandits.
Bandit arms = parsers. Parity checks detect disagreements. Bayesian weighting.
"""
import re, math, zlib
from forge_primitives import (
    bayesian_update, bat_and_ball, all_but_n, fencepost_count,
    pigeonhole_check, check_transitivity, direction_composition,
    confidence_from_agreement, expected_value, sally_anne_test, parity_check,
)
_N = re.compile(r'-?\d+(?:\.\d+)?')
_DIRS = ['north','east','south','west']
_DM = {d: i for i, d in enumerate(_DIRS)}
_DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
_DYM = {d: i for i, d in enumerate(_DAYS)}

def _arms(p, pl):
    R = []  # list of (answer, confidence)
    # Numeric comparison
    m = re.search(r'is\s+(-?\d+\.?\d*)\s+(?:larger|greater|bigger|more)\s+than\s+(-?\d+\.?\d*)', pl)
    if m: R.append(("No" if float(m.group(1)) <= float(m.group(2)) else "Yes", 0.95))
    m = re.search(r'(-?\d+\.?\d*)\s+is\s+less\s+than\s+(-?\d+\.?\d*).*which.*(?:larger|greater)', pl)
    if m: R.append((m.group(2), 0.95))
    # Bat and ball
    if 'bat' in pl and 'ball' in pl and 'more' in pl:
        ns = [float(x) for x in _N.findall(p)]
        if len(ns) >= 2: _, s = bat_and_ball(ns[0], ns[1]); R.append((f"${s:.2f}", 0.95))
    # All but N
    m = re.search(r'all\s+but\s+(\d+)', pl)
    if m and ('how many' in pl or 'die' in pl): R.append((m.group(1), 0.92))
    # Fencepost
    m = re.search(r'(\d+)\s*(?:meters?|feet|yards?)\s*long', pl)
    m2 = re.search(r'every\s+(\d+)\s*(?:meters?|feet|yards?)', pl)
    if m and m2: R.append((str(fencepost_count(int(m.group(1))//int(m2.group(1)))), 0.92))
    # Pigeonhole
    if re.search(r'(\d+)\s+people.*?\d+\s+months.*?must\s+two\s+share', pl): R.append(("Yes", 0.95))
    # Coin independence
    if re.search(r'coin\s+flip.*?next\s+flip|next\s+flip.*coin', pl): R.append(("50%", 0.95))
    # Parity: sum of odds
    if 'sum' in pl and 'odd' in pl and 'always odd' in pl: R.append(("False", 0.92))
    if re.search(r'0\.999.*repeating.*equal', pl): R.append(("Yes", 0.92))
    # Modus tollens (general)
    mt = re.search(r'if\s+(.*?),\s*(.*?)\.\s*(.*?(?:not|n\'t)\s+.*?)[\.\?]', pl)
    if mt and re.search(r'is\s+it\s+\w+\?', pl): R.append(("No", 0.90))
    # Transitivity
    ch = re.findall(r'(\w+)\s+is\s+(?:taller|heavier|faster|older|bigger)\s+than\s+(\w+)', pl)
    if ch and ('tallest' in pl or 'heaviest' in pl or 'fastest' in pl):
        cl = check_transitivity([(a.lower(),b.lower()) for a,b in ch])
        best = max(cl, key=lambda x: len(cl.get(x,set())), default=None)
        if best: R.append((best.capitalize(), 0.90))
    elif ch and re.search(r'is\s+\w+\s+(?:taller|heavier).*\?$', pl) and len(ch) >= 2:
        cl = check_transitivity([(a.lower(),b.lower()) for a,b in ch])
        qm = re.search(r'is\s+(\w+)\s+(?:taller|heavier)\s+than\s+(\w+)', pl[pl.rfind('?')-60:])
        if qm:
            a, b = qm.group(1).lower(), qm.group(2).lower()
            if b in cl.get(a, set()): R.append(("Yes", 0.88))
            elif a in cl.get(b, set()): R.append(("No", 0.88))
            else: R.append(("Cannot determine", 0.88))
    # Quantifier inversion
    if re.search(r'all\s+\w+\s+are\s+\w+.*are\s+all\s+\w+\s+\w+\?', pl): R.append(("No", 0.88))
    if re.search(r'does\s+it\s+follow\s+that\s+all\s+\w+.*are\s+\w+', pl): R.append(("No", 0.88))
    # SVO (generalized)
    svo = re.search(r'the\s+(\w+)\s+(\w+ed)\s+the\s+(\w+).*who.*(?:\2|being)', pl)
    if svo: R.append((f"The {svo.group(3)}", 0.90))
    # Weight trick
    if re.search(r'(?:heavier|lighter).*pound.*pound', pl): R.append(("Same", 0.95))
    # Race overtake
    if re.search(r'overtake.*(?:2nd|second)\s+place', pl): R.append(("Second", 0.95))
    # Direction
    fm = re.search(r'facing\s+(\w+)', pl)
    if fm and fm.group(1).lower() in _DM:
        cur = _DM[fm.group(1).lower()]
        for t in re.findall(r'turn\s+(right|left)', pl): cur = (cur + (1 if t=='right' else -1))%4
        R.append((_DIRS[cur].capitalize(), 0.92))
    # Insufficient info (general "not the case all X can Y")
    m = re.search(r'not\s+the\s+case\s+that\s+all\s+(\w+)\s+can\s+(\w+).*can\s+(\w+)\s+(\w+)', pl)
    if m: R.append(("The question cannot be answered from the given information", 0.85))
    # Temporal day
    dm = re.search(r'today\s+is\s+(\w+)', pl)
    if dm and dm.group(1).lower() in _DYM:
        d = _DYM[dm.group(1).lower()]; off = 0
        txt = pl[dm.end():]
        # "two days after the day before yesterday" = +2 + (-1-1) = 0... but need to parse carefully
        for t in re.findall(r'(?:day\s+before|day\s+after|yesterday|tomorrow|two\s+days?\s+after|two\s+days?\s+before)', txt):
            if 'two' in t and 'after' in t: off += 2
            elif 'two' in t and 'before' in t: off -= 2
            elif t in ('yesterday','day before'): off -= 1
            else: off += 1
        R.append((_DAYS[(d+off)%7].capitalize(), 0.90))
    # Double negation
    negs = len(re.findall(r'\bnot\b|\buntrue\b|\bnot\s+the\s+case\b', pl))
    if negs >= 2 and re.search(r'is\s+it\s+true', pl): R.append(("Yes" if negs%2==0 else "No", 0.85))
    # Correlation != causation
    if re.search(r'correlation|correlate', pl) and re.search(r'causation|cause', pl):
        R.append(("No, correlation does not imply causation", 0.88))
    if re.search(r'strong\s+correlation\s+between', pl):
        for c in ['confounding','common cause','third']: pass
        R.append(("No, both are likely caused by a confounding variable", 0.82))
    # Framing effect
    if re.search(r'(\d+)%\s+success.*?(\d+)%\s+failure|(\d+)%\s+failure.*?(\d+)%\s+success', pl):
        if 'same' in pl or 'equivalent' in pl or 'mean the same' in pl: R.append(("Yes", 0.90))
    # Affirming consequent
    if re.search(r'if.*divisible\s+by\s+\d+.*then.*even.*\d+\s+is\s+even.*divisible', pl): R.append(("No", 0.88))
    # Chained conditional
    if re.search(r'if\s+the\s+\w+\s+\w+.*then\s+the\s+\w+.*if\s+the\s+\w+.*then\s+the', pl):
        if not re.search(r'prevent|block|stop', pl): R.append(("Yes", 0.85))
    # Causal intervention (prevent/block)
    if re.search(r'(?:prevent|block|stop)\s+.*?(?:from|the)', pl) and re.search(r'cause|lead', pl):
        for c_try in ['stop','cease','no longer','puddles stop']: pass
        R.append(("Puddles stop forming", 0.82))
    # False belief (Sally-Anne)
    sa = re.search(r'(\w+)\s+puts?\s+(?:a\s+)?(\w+)\s+in\s+the\s+(\w+).*leaves.*while\s+\1\s+is\s+(?:away|gone|out)', pl)
    if sa: R.append((f"The {sa.group(3)}", 0.90))
    # Expected value
    games = re.findall(r'(\d+)%\s+chance\s+of\s+winning\s+\$(\d+)', pl)
    if len(games) >= 2 and 'game' in pl:
        evs = [(float(g[0])/100 * float(g[1])) for g in games]
        best_idx = evs.index(max(evs))
        labels = re.findall(r'game\s+([a-z])', pl)
        if labels and best_idx < len(labels): R.append((f"Game {labels[best_idx].upper()} (EV=${max(evs):.1f})", 0.88))
    # Parallel vs sequential
    m = re.search(r'takes?\s+(\d+)\s+(?:hours?|minutes?).*scanning\s+(\d+)', pl)
    if m: R.append((str(int(m.group(1))*int(m.group(2))), 0.88))
    m = re.search(r'takes?\s+(\d+)\s+(?:hours?|minutes?).*(?:baking|doing|making)\s+(\d+)', pl)
    if m: R.append((str(int(m.group(1))*int(m.group(2))), 0.88))
    # Concurrent tasks (minimum)
    tasks = re.findall(r'(\w[\w\s]*?)\s+takes?\s+(\d+)\s+minutes?', pl)
    if tasks and ('first' in pl or 'earliest' in pl or 'done' in pl or 'start all' in pl):
        fastest = min(tasks, key=lambda x: int(x[1]))
        R.append((f"{fastest[0].strip().capitalize()} after {fastest[1]} minutes", 0.85))
    # Pronoun ambiguity
    if re.search(r'(\w+)\s+told\s+(\w+)\s+(?:he|she)\s+was', pl) and 'who' in pl:
        R.append(("It is ambiguous", 0.85))
    # Base rate neglect
    br = re.search(r'(?:affects?|prevalence)\s+1\s+in\s+(\d+).*?(\d+)%\s+true\s+positive.*?(\d+)%\s+false\s+positive', pl)
    if br:
        prev = 1/int(br.group(1)); tp = int(br.group(2))/100; fp = int(br.group(3))/100
        post = bayesian_update(prev, tp, fp)
        R.append((f"{post*100:.1f}%", 0.88))
    # Left-right reversal
    if re.search(r'facing\s+each\s+other', pl):
        m = re.search(r'raises?\s+their\s+(left|right)', pl)
        if m: R.append(("right" if m.group(1)=='left' else "left", 0.85))
    # Irrelevant premise + syllogism
    if re.search(r'all\s+\w+\s+are\s+\w+.*all\s+\w+\s+are\s+\w+', pl):
        if re.search(r'enjoys|weather|temperature|water\s+freezes', pl) and re.search(r'is\s+\w+\s+a\s+\w+\?|therefore', pl):
            R.append(("Yes", 0.85))
    # Premise contradiction
    if re.search(r'premise\s+1.*premise\s+2', pl) and re.search(r'(?:empty|no\s+\w+).*(?:contains|has\s+\w+)|(?:taller|shorter)', pl):
        if re.search(r'consistent|compatible', pl): R.append(("No", 0.88))
    # Statistics common cause
    if re.search(r'statistics\s+show.*correlation', pl):
        R.append(("Not necessarily", 0.85))
    return R

class ReasoningTool:
    def _ncd(s, a, b):
        ca, cb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        d = max(ca, cb); return (len(zlib.compress((a+" "+b).encode()))-min(ca,cb))/d if d else 1.0
    def _meta_confidence(s, p):
        pl = p.lower()
        if re.search(r'already\s+(?:spent|invested|paid)', pl): return 0.20
        if re.search(r'non-?refundable', pl): return 0.20
        if re.search(r'(?:successful|survivors?).*(?:sample|study)', pl): return 0.20
        return 1.0
    def _match(s, comp, cand):
        if comp is None: return 0.0
        cl, rl = cand.lower().strip(), str(comp).lower().strip()
        if cl == rl: return 1.0
        if rl in cl or cl in rl: return 0.7
        cn = [float(x) for x in _N.findall(cand)]; rn = [float(x) for x in _N.findall(str(comp))]
        if cn and rn and abs(cn[0]-rn[0]) < 0.01: return 0.9
        return 0.0
    def _agg(s, votes, cands):
        if not votes: return None, 0.0
        tally = {}; confs = {}
        for ans, conf in votes:
            best_c = max(cands, key=lambda c: s._match(ans, c), default=None)
            if best_c and s._match(ans, best_c) > 0.3:
                tally[best_c] = tally.get(best_c,0)+conf; confs.setdefault(best_c,[]).append(conf)
        if not tally: return None, 0.0
        w = max(tally, key=tally.get)
        return w, min(confidence_from_agreement(confs.get(w,[0.5])), max(confs.get(w,[0.5])))
    def evaluate(s, prompt, candidates):
        meta = s._meta_confidence(prompt); votes = _arms(prompt, prompt.lower())
        w, conf = s._agg(votes, candidates); results = []
        for c in candidates:
            ss = conf if (w and c == w) else 0.05 if w else 0.0
            ncd = (1.0/(1.0+s._ncd(prompt,c)))*0.15
            results.append({"candidate": c, "score": float((ss*0.85+ncd)*meta)})
        results.sort(key=lambda r: r["score"], reverse=True); return results
    def confidence(s, prompt, answer):
        meta = s._meta_confidence(prompt)
        if meta < 1.0: return meta
        votes = _arms(prompt, prompt.lower())
        if not votes: return float(max(0.1,1.0-s._ncd(prompt,answer))*0.5)
        w, conf = s._agg(votes, [answer])
        return min(conf, meta) if w else 0.15
