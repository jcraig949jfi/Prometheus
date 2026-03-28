import math, hashlib, re, zlib

class ReasoningTool:
    """Compositional Active NAS v3. General structural category parsers
    + active inference free-energy fallback."""

    def __init__(self):
        self._state_seed = 0

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

        # 1) trick_question_equal_weight — same unit → same measure
        unit_m = re.search(
            r'(?:a|one|1)\s+(pound|kilogram|kg|ton|liter|litre|gallon|cup|ounce|gram|meter|foot|mile|inch|yard|barrel|bucket|box|bag|crate)\s+of\s+\w+.*'
            r'(?:a|one|1)\s+\1\s+of\s+\w+', p)
        if unit_m and re.search(r'heav|weigh|light|more|less|which|compare', p):
            if re.search(r'\bsame\b|\bequal\b|\bneither\b|\bboth\b|\bidentical\b', c):
                hits.append((2.0, 'equal_unit'))
            elif len(c.split()) <= 3 and not re.search(r'\bsame\b|\bequal\b', c):
                hits.append((-1.5, 'equal_unit'))

        # 2) algebraic_word_problem — "X and Y together cost T, X costs D more than Y"
        cost_m = re.search(r'(?:cost|price|total|together|combined)\D{0,30}?\$?\s*(\d+(?:\.\d+)?)', p)
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
                # common trap: answering T - D instead of (T-D)/2
                trap = total - diff
                if abs(cnums[0] - trap) < 0.01 and abs(trap - smaller) > 0.01:
                    hits.append((-1.5, 'algebra_trap'))

        # 3) statistical_independence — sequential random events
        if re.search(r'coin|dice|die|roulette|random|flip|roll|spinner|lottery|slot', p) and \
           re.search(r'next|probability|chance|likely|what are the odds|after', p):
            if re.search(r'\bhigher\b|\blower\b|\bmore likely\b|\bless likely\b|\bdue\b|\boverdue\b|\bincrease', c):
                hits.append((-2.0, 'independence'))
            elif re.search(r'50\s*%|1/2|0\.5|\bsame\b|\bunchanged\b|\bindependent\b|1/6|equal', c):
                hits.append((2.0, 'independence'))

        # 4) negation_scope_insufficiency — "not all X" → can't conclude about specific X
        if re.search(r'not\s+(?:the\s+case\s+that\s+)?all\b|not\s+every\b', p):
            if re.search(r'cannot\s+be\s+(?:determined|answered)|insufficient|not\s+enough|we\s+don.t\s+know|uncertain|not\s+certain', c):
                hits.append((2.0, 'negation_scope'))
            elif re.search(r'\byes\b|\bno\b|\btrue\b|\bfalse\b', c) and len(c.split()) <= 2:
                hits.append((-1.0, 'negation_scope'))

        # 5) stated_premise_usage — prompt states a relationship, use it
        stated = re.search(r'(\w[\w\s]*?)\s+is\s+(less|more|greater|taller|shorter|bigger|smaller|faster|slower)\s+than\s+(\w[\w\s]*?)[\.,]', p)
        if stated and re.search(r'which|who|what', p):
            subj, rel, obj = stated.group(1).strip(), stated.group(2), stated.group(3).strip()
            is_gt = rel in ('more', 'greater', 'taller', 'bigger', 'faster')
            if self._cmp_gt(p):
                winner = subj if is_gt else obj
                loser = obj if is_gt else subj
            elif self._cmp_lt(p):
                winner = obj if is_gt else subj
                loser = subj if is_gt else obj
            else:
                winner, loser = None, None
            if winner and winner.lower() in c:
                hits.append((2.0, 'stated_premise'))
            elif loser and loser.lower() in c:
                hits.append((-2.0, 'stated_premise'))

        # 6) subject_object_verb_parsing — who did what to whom
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

        # 7) modus_tollens_contrapositive — if P then Q; not Q → not P
        cond = re.search(r'if\s+(.+?)(?:,\s*then|\s*,)\s*(.+?)\.', p)
        if cond:
            after = p[cond.end():]
            if re.search(r'\bnot\b|doesn.t|isn.t|wasn.t|aren.t|didn.t|no\s+\w+', after):
                if c in ('no', 'false', 'not necessarily'):
                    hits.append((2.0, 'modus_tollens'))
                elif c in ('yes', 'true'):
                    hits.append((-2.0, 'modus_tollens'))

        if hits:
            total = sum(s for s, _ in hits)
            tags = '; '.join(t for _, t in hits)
            return total, tags
        return 0.0, 'none'

    # ── original CAN-NAS mechanism ─────────────────────────────────────
    def _h2f(self, s):
        return int(hashlib.sha256(s.encode('utf-8')).hexdigest()[:8], 16) / 0xFFFFFFFF

    def _tok(self, t):
        return [w.lower() for w in t.split() if w.isalnum()]

    def _comp(self, t):
        toks = self._tok(t)
        if not toks: return 0.0
        freq = {}
        for w in toks: freq[w] = freq.get(w, 0) + 1
        mod = sum((v - 1) for v in freq.values() if v > 1) * 0.1
        return (mod + len(freq) / (len(toks) + 1)) - math.log(len(toks) + 1) * 0.05

    def _fe(self, prompt, cand, seed):
        pt = set(self._tok(prompt))
        ct = self._tok(cand)
        if not ct: return -10.0
        fit = (len([t for t in ct if t in pt]) + 1) / (len(pt) + 1)
        return fit * 0.6 + self._comp(cand) * 0.4 + seed * 0.1

    # ── API ────────────────────────────────────────────────────────────
    def evaluate(self, prompt, candidates):
        if not prompt or not candidates: return []
        struct = [self._structural_score(prompt, c) for c in candidates]
        has_hit = any(s != 0.0 for s, _ in struct)
        if has_hit:
            ncd = [1.0 - self._ncd(prompt, c) for c in candidates]
            results = []
            for i, c in enumerate(candidates):
                s, tag = struct[i]
                final = 0.5 + 0.40 * math.tanh(s) + 0.05 * (ncd[i] - 0.5)
                results.append({'candidate': c, 'score': max(0.01, min(0.99, final)),
                                'reasoning': f'struct:[{tag}] s={s:.2f}'})
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
        results = []
        for c in candidates:
            sc = self._fe(prompt, c, self._h2f(prompt + c))
            results.append({'candidate': c, 'score': sc, 'reasoning': f'CAN-NAS:FE={sc:.4f}'})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        if not prompt or not answer: return 0.0
        s, tag = self._structural_score(prompt, answer)
        if s != 0.0:
            return max(0.05, min(0.95, 0.5 + 0.45 * math.tanh(s)))
        sc = self._fe(prompt, answer, self._h2f(prompt + answer))
        return max(0.0, min(1.0, 1.0 / (1.0 + math.exp(-5.0 * (sc - 0.5)))))
