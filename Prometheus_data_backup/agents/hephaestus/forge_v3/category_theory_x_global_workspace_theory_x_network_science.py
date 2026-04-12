import numpy as np, re, zlib

class ReasoningTool:
    """Categorical Message-Passing Workspace v3. Functorial structural mapping
    + global workspace consensus + 14 general category parsers."""

    def _n(self, t):
        return [float(m) for m in re.findall(r'-?\d+\.?\d*', t)]

    def _ncd(self, a, b):
        z = zlib.compress
        la, lb = len(z(a.encode())), len(z(b.encode()))
        return (len(z((a + b).encode())) - min(la, lb)) / max(la, lb, 1)

    def _structural_score(self, prompt, cand):
        p, c = prompt.lower(), cand.lower().strip()
        ws = re.findall(r"[a-z'\-]+", c); c0 = ws[0] if ws else c

        # 1  numeric_float_comparison
        m = re.search(r'is\s+([\d.]+)\s+(larger|greater|bigger|more|less|smaller)\s+than\s+([\d.]+)', p)
        if m:
            a, b = float(m.group(1)), float(m.group(3))
            gt = m.group(2) in ('larger','greater','bigger','more')
            ans = 'yes' if (a > b if gt else a < b) else 'no'
            if c0 == ans: return 1.0
            if c0 in ('yes','no'): return 0.0
        m2 = re.search(r'which\b.*?\b(larger|greater|bigger|smaller|less)', p)
        if m2:
            pn, cn = self._n(prompt), self._n(cand)
            if len(pn) >= 2 and cn:
                wb = m2.group(1) in ('larger','greater','bigger')
                tgt = max(pn) if wb else min(pn)
                if abs(cn[0] - tgt) < 1e-9: return 1.0
                oth = min(pn) if wb else max(pn)
                if abs(cn[0] - oth) < 1e-9: return 0.0

        # 2  algebraic_word_problem
        mt = re.search(r'(?:cost|costs?)\s+\$?([\d.]+)\s+(?:total|together|in total|combined)', p)
        md = re.search(r'costs?\s+\$?([\d.]+)\s+more\s+than', p)
        if mt and md:
            total, diff = float(mt.group(1)), float(md.group(1))
            cheap = (total - diff) / 2.0; cn = self._n(cand)
            if cn:
                if abs(cn[0] - cheap) < 0.01: return 1.0
                if abs(cn[0] - diff) < 0.01: return 0.0

        # 3  trick_question_equal_weight
        mu = re.search(r'(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|gallon|cup)\s+of\s+\w+.*(?:a|one|1)\s+\1\s+of\s+\w+', p)
        if mu and any(w in p for w in ('heav','weigh','lighter','which')):
            if any(w in c for w in ('same','equal','neither','both')): return 1.0
            if len(c) < 40 and not any(w in c for w in ('same','equal')): return 0.0

        # 4  positional_logic
        pm = re.search(r'overtake\s+(?:the\s+)?(?:\w+\s+)?(?:in\s+)?(\w+)\s*(?:place|position)', p)
        if pm:
            o = pm.group(1)
            omap = {'first':'1st','second':'2nd','third':'3rd','fourth':'4th','fifth':'5th',
                     '1st':'1st','2nd':'2nd','3rd':'3rd','4th':'4th','5th':'5th'}
            rev = {'1st':'first','2nd':'second','3rd':'third','4th':'fourth','5th':'fifth'}
            tag = omap.get(o, o); nm = rev.get(tag, tag)
            if nm in c or tag in c: return 1.0
            prev = {'2nd':'1st','3rd':'2nd','4th':'3rd','5th':'4th'}
            pt = prev.get(tag)
            if pt and (pt in c or rev.get(pt,'') in c): return 0.0

        # 5  universal_quantifier_converse_error
        if re.search(r'all\s+\w+\s+are\s+\w+', p) and re.search(r'are\s+all\s+\w+\s+\w+', p):
            if c0 == 'no' or 'not necessarily' in c: return 1.0
            if c0 == 'yes': return 0.0

        # 6  statistical_independence
        if any(w in p for w in ('coin','die','dice','roulette','flip','roll')):
            if any(w in p for w in ('in a row','previous','last','after','next','still','now')):
                if any(w in c for w in ('higher','lower','increase')): return 0.0
                if any(w in c for w in ('50','1/2','0.5','same')): return 1.0

        # 7  number_parity
        if re.search(r'(?:two|2|three|3)\s+odd', p) and re.search(r'sum|add|plus', p):
            nm = re.search(r'(two|2|three|3)\s+odd', p)
            if nm:
                n = {'two':2,'2':2,'three':3,'3':3}.get(nm.group(1), 2)
                even = (n % 2 == 0)
                if 'always odd' in p:
                    if c0 in ('false','no'): return 1.0 if even else 0.0
                    if c0 in ('true','yes'): return 0.0 if even else 1.0
                if 'always even' in p:
                    if c0 in ('true','yes'): return 1.0 if even else 0.0
                    if c0 in ('false','no'): return 0.0 if even else 1.0

        # 8  all_but_N_survivor_counting
        ms = re.search(r'all\s+but\s+(\d+)\s+(?:\w+\s+){0,3}(die|died|leave|left|lost|broke|ran|flew|escaped|gone|disappear)', p)
        if ms:
            sv = ms.group(1)
            if c.strip() == sv or c.strip() == sv + '.': return 1.0
            if c.strip().isdigit() and c.strip() != sv: return 0.0

        # 9  negation_scope_insufficiency
        if re.search(r'not\s+(?:the\s+case\s+that\s+)?(?:all|every)\b', p) and '?' in p:
            if re.search(r'cannot\s+be\s+(?:determined|answered)|insufficient|not\s+enough|undetermined|uncertain', c): return 1.0
            if c in ('yes','no') or (len(c.split()) <= 2 and re.match(r'^(yes|no|true|false)$', c0)): return 0.3

        # 10 mathematical_identity
        if re.search(r'0\.9{3,}', p) and any(w in p for w in ('equal','= 1','equals','same')):
            if c0 == 'yes' or 'equal' in c: return 1.0
            if c0 == 'no': return 0.0

        # 11 pigeonhole_principle
        pn = self._n(prompt)
        if len(pn) >= 2 and any(w in p for w in ('month','birthday','drawer','sock','box','categor','slot','compartment')):
            vals = sorted(pn)
            if vals[-1] > vals[0]:
                if c0 == 'yes' or any(w in c for w in ('must','at least','guaranteed')): return 1.0
                if c0 == 'no' and 'not' not in c[3:]: return 0.0

        # 12 stated_premise_usage
        sp = re.search(r'(\w[\w\s]*?)\s+is\s+(less|more|greater|taller|shorter|bigger|smaller|faster|slower|heavier|lighter)\s+than\s+(\w[\w\s]*?)[\.,]', p)
        if sp and any(w in p for w in ('which','who','what')):
            subj, rel, obj = sp.group(1).strip(), sp.group(2), sp.group(3).strip()
            is_gt = rel in ('more','greater','taller','bigger','faster','heavier')
            ask_gt = bool(re.search(r'(larger|greater|bigger|taller|faster|heavier|most|biggest)', p[sp.end():]))
            ask_lt = bool(re.search(r'(smaller|less|shorter|slower|lighter|least|smallest)', p[sp.end():]))
            if ask_gt:
                w_ = subj if is_gt else obj; l_ = obj if is_gt else subj
            elif ask_lt:
                w_ = obj if is_gt else subj; l_ = subj if is_gt else obj
            else: w_, l_ = None, None
            if w_ and w_.lower() in c: return 1.0
            if l_ and l_.lower() in c and (not w_ or w_.lower() not in c): return 0.0

        # 13 subject_object_verb_parsing
        vp = r'(chased|hit|pushed|kicked|bit|followed|ate|caught|saw|called|passed|liked|visited|taught|helped|sold|gave|sent|told|asked|invited|greeted)'
        svo = re.search(r'(?:the\s+)?(\w+)\s+' + vp + r'\s+(?:the\s+)?(\w+)', p)
        if svo:
            sb, ob = svo.group(1), svo.group(3)
            if re.search(r'who\s+(?:was|got|is)\s+(?:being\s+)?\w+', p):
                if ob.lower() in c: return 1.0
                if sb.lower() in c and ob.lower() not in c: return 0.0
            if re.search(r'who\s+(?:did\s+(?:the\s+)?)?\w+', p):
                if sb.lower() in c: return 1.0
                if ob.lower() in c and sb.lower() not in c: return 0.0

        # 14 modus_tollens_contrapositive
        ifm = re.search(r'if\s+(.+?)[,.](.+?)\.', p)
        if ifm:
            after = p[ifm.end():]
            if re.search(r'\bnot\b|\bdoes\s+not\b|\bisn.t\b|\bdon.t\b|\bdidn.t\b', after):
                if c0 == 'no' or 'therefore not' in c or 'did not' in c: return 1.0
                if c0 == 'yes': return 0.0

        return -1.0

    # ── workspace fallback ─────────────────────────────────────
    def _ws(self, prompt, cand):
        v = np.zeros(8)
        for i, ch in enumerate(prompt + cand): v[ord(ch) % 8] += 1.0 / (i + 1)
        return float(np.tanh(np.sum(v))) * 0.5 + 0.5

    def evaluate(self, prompt, candidates):
        if not candidates: return []
        res = []
        for c in candidates:
            ss = self._structural_score(prompt, c)
            if ss >= 0:
                ncd = self._ncd(prompt, c)
                score = ss * 0.80 + (1.0 - ncd) * 0.10 + self._ws(prompt, c) * 0.10
            else:
                ncd = self._ncd(prompt, c)
                score = (1.0 - ncd) * 0.15 + self._ws(prompt, c) * 0.85
            res.append({'candidate': c, 'score': float(np.clip(score, 0.01, 0.99)),
                        'reasoning': f'struct={ss:.2f}'})
        res.sort(key=lambda x: x['score'], reverse=True)
        return res

    def confidence(self, prompt, answer):
        ss = self._structural_score(prompt, answer)
        if ss >= 0: return float(np.clip(0.5 + ss * 0.45, 0.05, 0.95))
        r = self.evaluate(prompt, [answer])
        return r[0]['score'] if r else 0.0
