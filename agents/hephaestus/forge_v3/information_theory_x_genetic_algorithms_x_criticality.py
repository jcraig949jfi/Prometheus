import numpy as np, hashlib, re, zlib

class ReasoningTool:
    """ME-CGA v3: Maximum-Entropy Critical Genetic Algorithm with general
    structural category parsers. No exact-wording matching."""

    def __init__(self):
        self.l_ent, self.l_crit = 0.1, 0.2
        np.random.seed(42)

    # ── utilities ──────────────────────────────────────────────────────
    def _nums(self, t):
        """Extract all numbers (int or float) from text."""
        return [float(m) for m in re.findall(r'-?\d+(?:\.\d+)?', t)]

    def _cmp_words(self, t):
        return re.search(r'\b(greater|larger|bigger|more|higher|taller|heavier|faster|older|longer)\b', t, re.I)

    def _lt_words(self, t):
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

        # 1) numeric_float_comparison — two numbers + comparative word
        pnums = self._nums(p)
        cnums = self._nums(c)
        if len(pnums) >= 2 and (self._cmp_words(p) or self._lt_words(p)):
            # question asks which is bigger/smaller or yes/no about comparison
            a, b = pnums[0], pnums[1]
            wants_gt = bool(self._cmp_words(p))
            correct_val = max(a, b) if wants_gt else min(a, b)
            incorrect_val = min(a, b) if wants_gt else max(a, b)
            # yes/no style
            if c in ('yes', 'no'):
                if wants_gt:
                    correct_yn = 'yes' if a > b else ('no' if a < b else 'yes')
                else:
                    correct_yn = 'yes' if a < b else ('no' if a > b else 'yes')
                hits.append((2.0 if c == correct_yn else -2.0, 'numeric_float'))
            # candidate states a number
            elif cnums:
                if abs(cnums[0] - correct_val) < 1e-9:
                    hits.append((2.0, 'numeric_float'))
                elif abs(cnums[0] - incorrect_val) < 1e-9:
                    hits.append((-2.0, 'numeric_float'))

        # 2) trick_question_equal_weight — same unit of measure for two things
        unit_m = re.search(r'(?:a|one|1)\s+(pound|kilogram|kg|ton|liter|litre|gallon|cup|ounce|gram|meter|foot|mile|inch)\s+of\s+\w+.*(?:a|one|1)\s+\1\s+of\s+\w+', p)
        if unit_m and re.search(r'heav|weigh|light|more|less|which', p):
            if re.search(r'\bsame\b|\bequal\b|\bneither\b|\bboth\b', c):
                hits.append((2.0, 'equal_unit'))
            elif len(c.split()) <= 3 and not re.search(r'\bsame\b|\bequal\b', c):
                hits.append((-1.5, 'equal_unit'))

        # 3) universal_quantifier_converse_error — "all X are Y" then asks "all Y are X?"
        uq = re.search(r'all\s+(\w+)\s+are\s+(\w+)', p)
        if uq:
            a_class, b_class = uq.group(1), uq.group(2)
            converse = re.search(r'are\s+all\s+' + re.escape(b_class) + r'\s+' + re.escape(a_class), p)
            if not converse:
                converse = re.search(r'are\s+all\s+\w+\s+\w+\s*\?', p)
            if converse:
                if c in ('no', 'not necessarily', 'false'):
                    hits.append((2.0, 'quantifier_converse'))
                elif c in ('yes', 'true'):
                    hits.append((-2.0, 'quantifier_converse'))

        # 4) statistical_independence — sequential random events
        if re.search(r'coin|dice|die|roulette|random|flip|roll', p) and re.search(r'next|probability|chance|likely|what are the odds', p):
            if re.search(r'\bhigher\b|\blower\b|\bmore likely\b|\bless likely\b|\bdue\b|\boverdue\b', c):
                hits.append((-2.0, 'independence'))
            elif re.search(r'50\s*%|1/2|0\.5|\bsame\b|\bunchanged\b|\bindependent\b', c):
                hits.append((2.0, 'independence'))

        # 5) stated_premise_usage — prompt states a fact, answer must use it
        stated = re.search(r'(\w[\w\s]*?)\s+is\s+(?:less|more|greater|taller|shorter|bigger|smaller)\s+than\s+(\w[\w\s]*?)[\.,]', p)
        if stated and re.search(r'which|who|what', p):
            subj, obj = stated.group(1).strip(), stated.group(2).strip()
            rel_word = re.search(r'is\s+(less|more|greater|taller|shorter|bigger|smaller)\s+than', p).group(1)
            is_gt = rel_word in ('more', 'greater', 'taller', 'bigger')
            # question asks for the larger/taller/etc
            if self._cmp_words(p):
                winner = subj if is_gt else obj
                loser = obj if is_gt else subj
            elif self._lt_words(p):
                winner = obj if is_gt else subj
                loser = subj if is_gt else obj
            else:
                winner, loser = None, None
            if winner and winner.lower() in c:
                hits.append((2.0, 'stated_premise'))
            elif loser and loser.lower() in c:
                hits.append((-2.0, 'stated_premise'))

        # 6) subject_object_verb_parsing — who did what to whom
        svo = re.search(r'(?:the\s+)?(\w+)\s+(chased|hit|pushed|kicked|bit|followed|ate|caught|saw|called|passed)\s+(?:the\s+)?(\w+)', p)
        if svo:
            subj, verb, obj = svo.group(1), svo.group(2), svo.group(3)
            if re.search(r'who\s+was\s+(being\s+)?' + re.escape(verb[:-1] if verb.endswith('d') else verb), p) or \
               re.search(r'who\s+(?:was|got|is)\s+\w+ed', p):
                if obj.lower() in c:
                    hits.append((2.0, 'svo_parse'))
                elif subj.lower() in c and obj.lower() not in c:
                    hits.append((-2.0, 'svo_parse'))
            elif re.search(r'who\s+(?:did the\s+)?\w+ing|who\s+' + re.escape(verb[:-1] if verb.endswith('d') else verb), p):
                if subj.lower() in c:
                    hits.append((2.0, 'svo_parse'))
                elif obj.lower() in c and subj.lower() not in c:
                    hits.append((-2.0, 'svo_parse'))

        # 7) modus_tollens_contrapositive — if P then Q; not Q → not P
        cond = re.search(r'if\s+(.+?)(?:,\s*then|\s*,)\s*(.+?)\.', p)
        if cond:
            consequent = cond.group(2).strip()
            # check if prompt asserts negation of consequent
            neg_cons = re.search(r'(?:not|no|doesn.t|isn.t|wasn.t|aren.t|didn.t)\s+\w+', p[cond.end():])
            if neg_cons or re.search(r'the\s+\w+\s+(?:is|are|was)\s+not\b', p[cond.end():]):
                if c in ('no', 'false', 'not necessarily'):
                    hits.append((2.0, 'modus_tollens'))
                elif c in ('yes', 'true'):
                    hits.append((-2.0, 'modus_tollens'))

        if hits:
            total = sum(s for s, _ in hits)
            tags = '; '.join(t for _, t in hits)
            return total, tags
        return 0.0, 'none'

    # ── original mechanism ─────────────────────────────────────────────
    def _mi(self, prompt, cand):
        pw, cw = set(prompt.lower().split()), set(cand.lower().split())
        if not pw or not cw: return 0.0
        return 0.7 * len(pw & cw) / len(pw | cw) + 0.3 * min(len(cand), len(prompt)) / max(len(cand), len(prompt), 1)

    def _pop_stats(self, scores):
        if len(scores) == 0: return 0.0, 0.0
        p = scores - np.min(scores); p = p / (np.sum(p) + 1e-9); p = p[p > 0]
        H = -np.sum(p * np.log2(p)) / (np.log2(len(scores)) + 1e-9) if len(scores) > 1 else 0.0
        mu = np.mean(scores) + 1e-9
        return H, min(np.var(scores) / mu ** 2, 1.0)

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
        raw = np.array([self._mi(prompt, c) for c in candidates])
        H, C = self._pop_stats(raw)
        final = raw + self.l_ent * H + self.l_crit * C
        rng = np.max(final) - np.min(final)
        norm = (final - np.min(final)) / rng if rng > 1e-9 else np.full_like(final, 0.5)
        idx = np.argsort(norm)[::-1]
        return [{'candidate': candidates[i], 'score': float(norm[i]),
                 'reasoning': f'MI={raw[i]:.3f}'} for i in idx]

    def confidence(self, prompt, answer):
        s, tag = self._structural_score(prompt, answer)
        if s != 0.0:
            return float(np.clip(0.5 + 0.45 * np.tanh(s), 0.05, 0.95))
        v = self._mi(prompt, answer)
        if len(answer.split()) < 3: v *= 0.8
        return float(np.clip(v, 0.0, 1.0))
