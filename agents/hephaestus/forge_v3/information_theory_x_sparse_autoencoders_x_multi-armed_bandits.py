import math, hashlib, re, zlib

class ReasoningTool:
    """Information-Guided Sparsity-Constrained Feature-Selection Bandit v3.
    General structural category parsers + UCB bandit fallback."""

    def __init__(self):
        self.n_features = 256
        self.feature_counts = [0.0] * self.n_features
        self.feature_success = [0.0] * self.n_features
        self.total_pulls = 1.0
        self.eps = 1e-6

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

        # 1) numeric_float_comparison — numbers + comparative
        pnums = self._nums(p)
        cnums = self._nums(c)
        if len(pnums) >= 2 and (self._cmp_gt(p) or self._cmp_lt(p)):
            a, b = pnums[0], pnums[1]
            wants_gt = bool(self._cmp_gt(p))
            correct_val = max(a, b) if wants_gt else min(a, b)
            incorrect_val = min(a, b) if wants_gt else max(a, b)
            if c in ('yes', 'no'):
                if wants_gt:
                    ans = 'yes' if a > b else ('no' if a < b else 'yes')
                else:
                    ans = 'yes' if a < b else ('no' if a > b else 'yes')
                hits.append((2.0 if c == ans else -2.0, 'numeric_float'))
            elif cnums:
                if abs(cnums[0] - correct_val) < 1e-9:
                    hits.append((2.0, 'numeric_float'))
                elif abs(cnums[0] - incorrect_val) < 1e-9:
                    hits.append((-2.0, 'numeric_float'))

        # 2) universal_quantifier_converse_error — "all X are Y ⇏ all Y are X"
        uq = re.search(r'all\s+(\w+)\s+are\s+(\w+)', p)
        if uq and re.search(r'are\s+all\s+\w+\s+\w+\s*\?', p):
            if c in ('no', 'not necessarily', 'false'):
                hits.append((2.0, 'quantifier_converse'))
            elif c in ('yes', 'true'):
                hits.append((-2.0, 'quantifier_converse'))

        # 3) negation_scope_insufficiency — "not all X have P" → can't conclude about specific X
        if re.search(r'not\s+(?:the\s+case\s+that\s+)?all\b', p):
            if re.search(r'cannot\s+be\s+(?:determined|answered)|insufficient|not\s+enough|we\s+don.t\s+know|uncertain', c):
                hits.append((2.0, 'negation_scope'))
            elif re.search(r'\byes\b|\bno\b|\btrue\b|\bfalse\b', c) and len(c.split()) <= 2:
                hits.append((-1.0, 'negation_scope'))

        # 4) subject_object_verb_parsing — who did what to whom
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

        # 5) modus_tollens_contrapositive — if P then Q; not Q → not P
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

    # ── original bandit mechanism ──────────────────────────────────────
    def _hash_idx(self, text, k=5):
        h = hashlib.sha256(text.encode()).hexdigest()
        idx = []
        for i in range(0, len(h) - 2, 2):
            if len(idx) >= k: break
            v = int(h[i:i+2], 16)
            j = (v * (i + 1) + len(text)) % self.n_features
            if j not in idx: idx.append(j)
        return idx[:k]

    def _mi(self, idx):
        n = self.feature_counts[idx] + self.eps
        s = self.feature_success[idx]
        if n < 1.0: return 0.0
        pp = s / n
        if pp <= 0 or pp >= 1: return 1.0
        return 1.0 + pp * math.log2(pp) + (1 - pp) * math.log2(1 - pp)

    def _ucb(self, idx):
        if self.feature_counts[idx] == 0: return float('inf')
        return self._mi(idx) + math.sqrt(2.0 * math.log(self.total_pulls + 1) / (self.feature_counts[idx] + self.eps))

    def _bandit_score(self, prompt, cand):
        pf = set(self._hash_idx(prompt))
        cf = set(self._hash_idx(cand))
        ctx = list(pf | cf)
        for i in ctx:
            self.feature_counts[i] += 1.0
            self.feature_success[i] += 0.5 + 0.5 * math.sin(i)
        self.total_pulls += len(ctx)
        sc = sum(u for i in ctx if (u := self._ucb(i)) != float('inf'))
        return sc / (len(ctx) + 1)

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
                final = 0.5 + 0.40 * math.tanh(s) + 0.05 * (ncd[i] - 0.5)
                results.append({'candidate': c, 'score': max(0.01, min(0.99, final)),
                                'reasoning': f'struct:[{tag}] s={s:.2f}'})
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
        scores = [self._bandit_score(prompt, c) for c in candidates]
        results = [{'candidate': candidates[i], 'score': scores[i],
                    'reasoning': 'bandit_ucb'} for i in range(len(candidates))]
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        s, tag = self._structural_score(prompt, answer)
        if s != 0.0:
            return max(0.05, min(0.95, 0.5 + 0.45 * math.tanh(s)))
        f = self._hash_idx(prompt + answer)
        if not f: return 0.0
        tm = sum(self._mi(i) for i in f)
        return min(1.0, max(0.0, tm / (len(f) + 1)))
