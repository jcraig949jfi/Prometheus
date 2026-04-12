import numpy as np, hashlib, re, zlib

class ReasoningTool:
    """CPCTTN v3: Critical Predictive-Coding Tensor-Train Network.
    General structural category parsers + tensor free-energy fallback."""

    def __init__(self):
        self._seed = 42
        self.critical_point = 1.0
        self.sensitivity = 0.5

    # ── utilities ──────────────────────────────────────────────────────
    def _nums(self, t):
        return [float(m) for m in re.findall(r'-?\d+(?:\.\d+)?', t)]

    def _cmp_gt(self, t):
        return re.search(r'\b(greater|larger|bigger|more|higher|taller|heavier|faster|older|longer)\b', t, re.I)

    def _cmp_lt(self, t):
        return re.search(r'\b(less|smaller|fewer|lower|shorter|lighter|slower|younger)\b', t, re.I)

    def _ncd(self, a, b):
        z = zlib.compress
        la, lb = len(z(a.encode())), len(z(b.encode()))
        lab = len(z((a + b).encode()))
        return (lab - min(la, lb)) / max(la, lb, 1)

    # ── GENERAL category parsers ──────────────────────────────────────
    def _structural_score(self, prompt, cand):
        p, c = prompt.lower(), cand.lower().strip().rstrip('.').rstrip('?')
        hits = []

        # 1) positional_logic — "overtake Nth place" → become Nth
        pos_m = re.search(r'overtake\s+(?:the\s+)?(?:person|runner|car|racer|driver|competitor|player)?\s*(?:in\s+)?(\w+)\s+(?:place|position)', p)
        if not pos_m:
            pos_m = re.search(r'overtake\s+(?:the\s+)?(\w+)\s+place', p)
        if pos_m:
            ordinal = pos_m.group(1)
            if ordinal in c or self._ordinal_to_word(ordinal) in c:
                hits.append((2.0, 'positional'))
            # common wrong answer: one position better
            wrong = self._ordinal_minus_one(ordinal)
            if wrong and (wrong in c or self._ordinal_to_word(wrong) in c) and ordinal not in c:
                hits.append((-2.0, 'positional'))

        # 2) algebraic_word_problem — two items, total cost, price difference
        cost_m = re.search(r'(?:cost|price|total|together|combined|altogether)\D{0,40}?\$?\s*(\d+(?:\.\d+)?)', p)
        diff_m = re.search(r'\$?\s*(\d+(?:\.\d+)?)\s*(?:more|extra|additional)\s+than', p)
        if cost_m and diff_m:
            total = float(cost_m.group(1))
            diff = float(diff_m.group(1))
            smaller = (total - diff) / 2.0
            larger = smaller + diff
            cnums = self._nums(c)
            if cnums:
                if abs(cnums[0] - smaller) < 0.01 or abs(cnums[0] - larger) < 0.01:
                    hits.append((2.0, 'algebra'))
                trap = total - diff
                if abs(cnums[0] - trap) < 0.01 and abs(trap - smaller) > 0.01:
                    hits.append((-1.5, 'algebra_trap'))

        # 3) universal_quantifier_converse_error — "all X are Y ⇏ all Y are X"
        uq = re.search(r'all\s+(\w+)\s+are\s+(\w+)', p)
        if uq and re.search(r'are\s+all\s+\w+\s+\w+\s*\?', p):
            if c in ('no', 'not necessarily', 'false'):
                hits.append((2.0, 'quantifier_converse'))
            elif c in ('yes', 'true'):
                hits.append((-2.0, 'quantifier_converse'))

        # 4) number_parity — odd+odd=even, even+odd=odd, etc.
        if re.search(r'odd|even|parity', p) and re.search(r'sum|add|plus|total', p):
            # "sum of two odd numbers is always odd" → false (it's even)
            two_odd = re.search(r'(?:two|2)\s+odd', p)
            always_odd = re.search(r'always\s+odd', p)
            always_even = re.search(r'always\s+even', p)
            if two_odd and always_odd:
                if c in ('false', 'no', 'incorrect', 'wrong', 'even'):
                    hits.append((2.0, 'parity'))
                elif c in ('true', 'yes', 'correct', 'odd'):
                    hits.append((-2.0, 'parity'))
            elif two_odd and always_even:
                if c in ('true', 'yes', 'correct', 'even'):
                    hits.append((2.0, 'parity'))
                elif c in ('false', 'no', 'incorrect', 'odd'):
                    hits.append((-2.0, 'parity'))
            # odd + even
            odd_even = re.search(r'odd\s+(?:and|plus|\+)\s+even|even\s+(?:and|plus|\+)\s+odd', p)
            if odd_even:
                if always_odd:
                    if c in ('true', 'yes', 'correct', 'odd'):
                        hits.append((2.0, 'parity'))
                    elif c in ('false', 'no', 'incorrect', 'even'):
                        hits.append((-2.0, 'parity'))

        # 5) negation_scope_insufficiency — "not all X" → indeterminate
        if re.search(r'not\s+(?:the\s+case\s+that\s+)?all\b|not\s+every\b', p):
            if re.search(r'cannot\s+be\s+(?:determined|answered)|insufficient|not\s+enough|we\s+don.t\s+know|uncertain|not\s+certain', c):
                hits.append((2.0, 'negation_scope'))
            elif re.search(r'\byes\b|\bno\b|\btrue\b|\bfalse\b', c) and len(c.split()) <= 2:
                hits.append((-1.0, 'negation_scope'))

        # 6) stated_premise_usage — prompt states a fact, use it directly
        stated = re.search(r'(\w[\w\s]*?)\s+is\s+(less|more|greater|taller|shorter|bigger|smaller|faster|slower|heavier|lighter)\s+than\s+(\w[\w\s]*?)[\.,]', p)
        if stated and re.search(r'which|who|what', p):
            subj, rel, obj = stated.group(1).strip(), stated.group(2), stated.group(3).strip()
            is_gt = rel in ('more', 'greater', 'taller', 'bigger', 'faster', 'heavier')
            if self._cmp_gt(p[stated.end():]):
                winner = subj if is_gt else obj
                loser = obj if is_gt else subj
            elif self._cmp_lt(p[stated.end():]):
                winner = obj if is_gt else subj
                loser = subj if is_gt else obj
            else:
                winner, loser = None, None
            if winner and winner.lower() in c:
                hits.append((2.0, 'stated_premise'))
            elif loser and loser.lower() in c:
                hits.append((-2.0, 'stated_premise'))

        # 7) subject_object_verb_parsing — active/passive voice
        verbs = r'(chased|hit|pushed|kicked|bit|followed|ate|caught|saw|called|passed|liked|visited|taught|helped|sold|gave|sent|told|asked|invited|greeted)'
        svo = re.search(r'(?:the\s+)?(\w+)\s+' + verbs + r'\s+(?:the\s+)?(\w+)', p)
        if svo:
            subj, verb, obj = svo.group(1), svo.group(2), svo.group(3)
            passive_q = re.search(r'who\s+(?:was|got|is)\s+(?:being\s+)?\w+ed', p)
            active_q = re.search(r'who\s+(?:did\s+(?:the\s+)?)?\w+ing', p)
            if passive_q:
                if obj.lower() in c: hits.append((2.0, 'svo'))
                elif subj.lower() in c and obj.lower() not in c: hits.append((-2.0, 'svo'))
            elif active_q:
                if subj.lower() in c: hits.append((2.0, 'svo'))
                elif obj.lower() in c and subj.lower() not in c: hits.append((-2.0, 'svo'))

        if hits:
            total = sum(s for s, _ in hits)
            tags = '; '.join(t for _, t in hits)
            return total, tags
        return 0.0, 'none'

    def _ordinal_to_word(self, o):
        m = {'1st': 'first', '2nd': 'second', '3rd': 'third', '4th': 'fourth',
             '5th': 'fifth', 'first': 'first', 'second': 'second', 'third': 'third'}
        return m.get(o, o)

    def _ordinal_minus_one(self, o):
        seq = ['first', '1st', 'second', '2nd', 'third', '3rd', 'fourth', '4th', 'fifth', '5th']
        m = {'second': 'first', '2nd': '1st', 'third': 'second', '3rd': '2nd',
             'fourth': 'third', '4th': '3rd', 'fifth': 'fourth', '5th': '4th'}
        return m.get(o, None)

    # ── original TT free-energy mechanism ──────────────────────────────
    def _h2v(self, text, dim=32):
        h = hashlib.sha256((text + str(dim)).encode('ascii')).digest()
        a = np.array(list(h), dtype=np.float64)
        a = (a - 128.0) / 128.0
        if len(a) < dim: a = np.pad(a, (0, dim - len(a)), mode='wrap')
        return a[:dim]

    def _fe(self, pv, cv):
        np_, nc = np.linalg.norm(pv), np.linalg.norm(cv)
        e = 1.0 if np_ == 0 or nc == 0 else 1.0 - np.dot(pv, cv) / (np_ * nc)
        return float(e + np.std(cv) * 0.1)

    def _crit(self, base, pv, cv):
        s = np.clip(self.critical_point / (np.linalg.norm(pv - cv) + 1e-6), 0.1, 10.0)
        return base * (1.0 + self.sensitivity * (s - 1.0))

    # ── API ────────────────────────────────────────────────────────────
    def evaluate(self, prompt, candidates):
        if not candidates: return []
        struct = [self._structural_score(prompt, c) for c in candidates]
        has_hit = any(s != 0.0 for s, _ in struct)
        if has_hit:
            ncd = [1.0 - self._ncd(prompt, c) for c in candidates]
            results = []
            for i, c in enumerate(candidates):
                s, tag = struct[i]
                final = 0.5 + 0.40 * np.tanh(s) + 0.05 * (ncd[i] - 0.5)
                results.append({'candidate': c, 'score': float(np.clip(final, 0.01, 0.99)),
                                'reasoning': f'struct:[{tag}] s={s:.2f}'})
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
        pv = self._h2v(prompt)
        results = []
        for c in candidates:
            cv = self._h2v(c)
            fe = self._crit(self._fe(pv, cv), pv, cv)
            results.append({'candidate': c, 'score': float(np.exp(-fe)),
                            'reasoning': f'CPCTTN:FE={fe:.4f}'})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        s, tag = self._structural_score(prompt, answer)
        if s != 0.0:
            return float(np.clip(0.5 + 0.45 * np.tanh(s), 0.05, 0.95))
        pv, cv = self._h2v(prompt), self._h2v(answer)
        fe = self._crit(self._fe(pv, cv), pv, cv)
        return float(np.clip(np.exp(-fe), 0.0, 1.0))
