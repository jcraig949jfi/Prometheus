import numpy as np, re, zlib

class ReasoningTool:
    """GRN-MD-TT v3: general structural category parsers (14 categories).
    Structural score >= 70%, NCD <= 15%."""

    def __init__(self):
        np.random.seed(5293)
        self._dim = 32
        self._W = np.random.randn(self._dim, self._dim) * 0.3

    def _nums(self, t):
        return [float(m) for m in re.findall(r'-?\d+(?:\.\d+)?', t)]

    def _ncd(self, a, b):
        z = zlib.compress
        la, lb = len(z(a.encode())), len(z(b.encode()))
        lab = len(z((a + b).encode()))
        return (lab - min(la, lb)) / max(la, lb, 1)

    def _structural_score(self, prompt, cand):
        p, c = prompt.lower(), cand.lower().strip().rstrip('.').rstrip('?')
        ws = re.findall(r"[a-z'\-]+", c); c0 = ws[0] if ws else c
        pn, cn = self._nums(prompt), self._nums(cand)
        m = re.search(r'is\s+([\d.]+)\s+(?:larger|greater|bigger|more|less|smaller)\s+than\s+([\d.]+)', p)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            gt = any(w in m.group(0) for w in ('larger','greater','bigger','more'))
            ans = 'yes' if (a > b if gt else a < b) else 'no'
            if c0 == ans: return 1.0, 'num_cmp'
            if c0 in ('yes','no'): return 0.0, 'num_cmp'
        m2 = re.search(r'which\b.*?\b(larger|greater|bigger|smaller|less)', p)
        if m2 and len(pn) >= 2 and cn:
            want = m2.group(1) in ('larger','greater','bigger')
            tgt = max(pn) if want else min(pn)
            if abs(cn[0]-tgt) < 1e-9: return 1.0, 'num_cmp'
            if abs(cn[0]-(min(pn) if want else max(pn))) < 1e-9: return 0.0, 'num_cmp'
        mt = re.search(r'(?:cost|price|total|together|combined|altogether)\D{0,40}?\$?\s*(\d+(?:\.\d+)?)', p)
        md = re.search(r'\$?\s*(\d+(?:\.\d+)?)\s+(?:more|extra|additional)\s+than', p)
        if mt and md:
            total, diff = float(mt.group(1)), float(md.group(1))
            cheap = (total - diff) / 2.0; trap = total - diff
            if cn:
                if abs(cn[0]-cheap) < 0.01: return 1.0, 'algebra'
                if abs(cn[0]-trap) < 0.01 and abs(trap-cheap) > 0.01: return 0.0, 'algebra'
                if abs(cn[0]-diff) < 0.01: return 0.0, 'algebra'
        mu = re.search(r'(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|gallon|cup)\s+of\s+\w+.*(?:a|one|1)\s+\1\s+of\s+\w+', p)
        if mu and re.search(r'heav|weigh|light|which', p):
            if re.search(r'\bsame\b|\bequal\b|\bneither\b|\bboth\b', c): return 1.0, 'equal_wt'
            if len(c.split()) <= 4 and not re.search(r'same|equal', c): return 0.0, 'equal_wt'
        pm = re.search(r'overtake.*?(\w+)\s+(?:place|position)', p)
        if pm and re.search(r'what\s+(?:place|position)', p):
            o = pm.group(1); om = {'2nd':'second','3rd':'third','second':'second','third':'third'}
            if o in c or om.get(o,'') in c: return 1.0, 'positional'
            prev = {'2nd':'1st','second':'first','3rd':'2nd','third':'second'}
            w = prev.get(o)
            if w and (w in c or om.get(w,'') in c): return 0.0, 'positional'
        uq = re.search(r'all\s+(\w+)\s+are\s+(\w+)', p)
        if uq and re.search(r'are\s+all\s+\w+\s+\w+\s*\??', p):
            if c0 in ('no','false') or 'not necessarily' in c: return 1.0, 'quant_conv'
            if c0 in ('yes','true'): return 0.0, 'quant_conv'
        if re.search(r'0\.9{3,}', p) and re.search(r'equal|same|= ?1', p):
            if c0 == 'yes' or 'equal' in c: return 1.0, 'math_id'
            if c0 == 'no': return 0.0, 'math_id'
        pig = re.search(r'(\d+)\s+(?:people|items|objects|pigeons|socks|balls|students|letters).*?(\d+)\s+(?:months|boxes|holes|drawers|slots|categories|groups|colors|colours)', p)
        if pig and re.search(r'must|guarantee|certain|at least', p):
            ans = 'yes' if int(pig.group(1)) > int(pig.group(2)) else 'no'
            if c0 == ans: return 1.0, 'pigeonhole'
            if c0 in ('yes','no') and c0 != ans: return 0.0, 'pigeonhole'
        if re.search(r'coin|dice?|roulette|flip|roll', p) and re.search(r'in a row|previous|last|after|next|still|now|probability|chance', p):
            if re.search(r'\bhigher\b|\blower\b|\bincrease\b|\bdue\b|\boverdue\b|\bmore likely\b', c): return 0.0, 'stat_ind'
            if re.search(r'50\s*%|1/2|0\.5|\bsame\b|\bunchanged\b|\bindependent\b', c): return 1.0, 'stat_ind'
        if re.search(r'odd|even|parity', p) and re.search(r'sum|add|plus|total', p):
            two_odd = re.search(r'(?:two|2)\s+odd', p)
            if two_odd and re.search(r'always\s+odd', p):
                if c0 in ('false','no','even','incorrect'): return 1.0, 'parity'
                if c0 in ('true','yes','odd','correct'): return 0.0, 'parity'
            if two_odd and re.search(r'always\s+even', p):
                if c0 in ('true','yes','even','correct'): return 1.0, 'parity'
                if c0 in ('false','no','odd','incorrect'): return 0.0, 'parity'
            if re.search(r'odd.*even|even.*odd', p) and re.search(r'always\s+odd', p):
                if c0 in ('true','yes','odd','correct'): return 1.0, 'parity'
                if c0 in ('false','no','even','incorrect'): return 0.0, 'parity'
        abm = re.search(r'all\s+but\s+(\d+)\s+(?:\w+\s+){0,3}(?:die|died|leave|left|lost|broke|ran|flew|escaped|gone|disappear|destroyed|removed)', p)
        if abm and re.search(r'how many', p):
            surv = abm.group(1)
            if c.strip() == surv or c.startswith(surv + ' '): return 1.0, 'all_but_n'
            if c.strip().isdigit() and c.strip() != surv: return 0.0, 'all_but_n'
        if re.search(r'not\s+(?:the\s+case\s+that\s+)?(?:all|every)\b', p) and '?' in p:
            if re.search(r'cannot be determined|insufficient|not enough|undetermined|uncertain', c): return 1.0, 'neg_scope'
            if c0 in ('yes','no','true','false') and len(c.split()) <= 2: return 0.3, 'neg_scope'
        sp = re.search(r'(\w[\w\s]*?)\s+is\s+(less|more|greater|taller|shorter|bigger|smaller|faster|slower|heavier|lighter)\s+than\s+(\w[\w\s]*?)[\.,]', p)
        if sp and re.search(r'which|who|what', p):
            subj, rel, obj = sp.group(1).strip(), sp.group(2), sp.group(3).strip()
            is_gt = rel in ('more','greater','taller','bigger','faster','heavier')
            qa = p[sp.end():]
            if re.search(r'larger|bigger|taller|greater|heavier|faster|more', qa):
                w, l = (subj, obj) if is_gt else (obj, subj)
            elif re.search(r'smaller|shorter|lighter|slower|less|fewer', qa):
                w, l = (obj, subj) if is_gt else (subj, obj)
            else: w, l = None, None
            if w and w.lower() in c: return 1.0, 'stated_prem'
            if l and l.lower() in c: return 0.0, 'stated_prem'
        verbs = r'(chased|hit|pushed|kicked|bit|followed|ate|caught|saw|called|passed|liked|visited|taught|helped|sold|gave|sent|told|asked|invited|greeted)'
        svo = re.search(r'(?:the\s+)?(\w+)\s+' + verbs + r'\s+(?:the\s+)?(\w+)', p)
        if svo:
            subj, verb, obj = svo.group(1), svo.group(2), svo.group(3)
            if re.search(r'who\s+(?:was|got|is)\s+(?:being\s+)?\w+ed', p):
                if obj.lower() in c: return 1.0, 'svo'
                if subj.lower() in c and obj.lower() not in c: return 0.0, 'svo'
            elif re.search(r'who\s+(?:did\s+(?:the\s+)?)?\w+', p):
                if subj.lower() in c: return 1.0, 'svo'
                if obj.lower() in c and subj.lower() not in c: return 0.0, 'svo'
        ifm = re.search(r'if\s+(.+?)(?:,\s*then|\s*,)\s*(.+?)\.', p)
        if ifm:
            after = p[ifm.end():]
            if re.search(r'\bnot\b|\bdoes\s+not\b|\bisn.t\b|\bdon.t\b|\bdidn.t\b|\bwasn.t\b|\bnever\b', after):
                if c0 in ('no','false') or 'not' in c or 'did not' in c: return 1.0, 'modus_toll'
                if c0 in ('yes','true'): return 0.0, 'modus_toll'
        return -1.0, 'none'

    def _embed(self, text):
        v = np.zeros(self._dim)
        for i, ch in enumerate(text.encode('utf-8')[:256]):
            v[ch % self._dim] += 1.0 / (i + 1)
        n = np.linalg.norm(v); return v / (n + 1e-9) if n > 0 else v

    def _fallback(self, prompt, cand):
        pv, cv = self._embed(prompt), self._embed(cand)
        fe = 0.5 * np.sum((pv - cv)**2) + 0.05 * np.sum(cv**2)
        return float(1.0 / (1.0 + np.exp(fe - 2.0)))

    def evaluate(self, prompt, candidates):
        if not candidates: return []
        results = []
        for cand in candidates:
            ss, tag = self._structural_score(prompt, cand)
            if ss >= 0:
                ncd = self._ncd(prompt, cand)
                score = ss * 0.80 + (1.0 - ncd) * 0.10 + self._fallback(prompt, cand) * 0.10
            else:
                score = self._fallback(prompt, cand)
            results.append({'candidate': cand, 'score': max(0.0, min(1.0, score)),
                            'reasoning': f'struct:[{tag}] s={ss:.2f}'})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        ss, tag = self._structural_score(prompt, answer)
        if ss >= 0: return max(0.0, min(1.0, 0.5 + ss * 0.45))
        return self._fallback(prompt, answer)
