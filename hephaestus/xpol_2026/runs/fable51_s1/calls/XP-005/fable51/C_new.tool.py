import zlib

"""
ReasoningTool: Tensor Decomposition x Feedback Control x Nash Equilibrium.
(1) Constructive solvers COMPUTE answers: PEMDAS, modular, Bayes posterior, expected
value, rate/work, speed/distance, age, numeric compare, schedule overlap, temporal order.
(2) Prompt + candidates are parsed into atomic claims (subj, rel, obj, polarity) and
placed in a 3-mode tensor T[claim_i, claim_j, slice] (entails/contradicts/order-chain/
causal-chain). Constraint propagation (transitive closure of ground claims, modus
ponens/tollens, polarity clash) fills implied entries. Tucker/HOSVD low-rank
reconstruction leaves a residual on claims that do not fit the dominant logical
structure; a PI feedback loop reweights slices from that residual with an
oscillation (gain) guard. (3) Candidates are players in a best-response game:
payoff = ground agreement - residual - clashes with other high-weight candidates;
the logit fixed point gives scores. NCD is a 10% tiebreak only.
_meta_confidence() caps confidence from QUESTION properties, not answer score.
"""
import re, zlib
import numpy as np

NUM = r'-?\d+(?:\.\d+)?'
NEG = re.compile(r"\b(not|no|never|cannot|isn't|aren't|doesn't|don't|didn't|won't|wasn't)\b")
STOP = re.compile(r'\b(the|a|an|that|this|then|it|very|also|will|would|does|do)\b')
PATS = [
    (r'(.+?)\s+(?:is|are|was|were)\s+(?:greater|larger|bigger|more|higher|older|taller|faster|heavier)\s+than\s+(.+)', 'gt'),
    (r'(.+?)\s+(?:is|are|was|were)\s+(?:less|smaller|lower|fewer|younger|shorter|slower|lighter)\s+than\s+(.+)', 'lt'),
    (r'(.+?)\s+(?:\w+\s+)?(?:before|precedes|earlier than)\s+(.+)', 'before'),
    (r'(.+?)\s+(?:\w+\s+)?(?:after|follows|later than)\s+(.+)', 'after'),
    (r'(.+?)\s+(?:causes?|leads? to|results? in|triggers?|implies)\s+(.+)', 'causes'),
    (r'(?:if|whenever)\s+(.+?),?\s+then\s+(.+)', 'causes'),
    (r'(.+?)\s+(?:is|are|equals?|=)\s+(.+)', 'eq'),
]
FLIP = {'lt': 'gt', 'after': 'before'}
META = [  # (question-property pattern, confidence cap)
    (r'\b(have|has|had|did) (you|he|she|they|we) (stopped|quit|ceased|given up|stop)\b', 0.15),
    (r'\bwhy (did|does|do|has|have|is|was) .*\b(fail|stop|quit|cheat|lie|lied|failed|stopped|wrong)', 0.2),
    (r'\b(every|each|all)\b.*\b(a|an)\b.*\b(same|different)\b', 0.25),
    (r'\b(told|said to|asked|informed) \w+ (that )?(he|she|they)\b.*\b(who|whom)\b', 0.2),
    (r'\beither\b .+ \bor\b', 0.25),
    (r'\b(best|worst|favou?rite|greatest|most (beautiful|important|interesting))\b', 0.25),
    (r'\b(sunk cost|already (spent|invested|paid)|survivor|survived|surviving|regress|streak)\b', 0.3),
    (r'\b(valid|sound|logically follow|strong argument|weak argument|good argument)\b', 0.3),
    (r'\b(cannot be determined|not enough information|insufficient|unknowable)\b', 0.2),
]


class ReasoningTool:
    def __init__(self, rank=3, kp=0.5, ki=0.1, iters=8):
        self.rank, self.kp, self.ki, self.iters = rank, kp, ki, iters

    # ---------------- claim parsing + propagation ----------------
    @staticmethod
    def _norm(s):
        return ' '.join(STOP.sub(' ', re.sub(r'[^a-z0-9 .]', ' ', s.lower())).split())

    def _claims(self, text):
        out = set()
        for sent in re.split(r'[.;!?\n]|\b(?:but|while|and|so)\b', text.lower()):
            pol = 0 if NEG.search(sent) else 1
            sent = NEG.sub(' ', sent).strip()
            for pat, rel in PATS:
                m = re.match(pat, sent)
                if not m: continue
                a, b = self._norm(m.group(1)), self._norm(m.group(2))
                if a and b and len(a) < 40 and len(b) < 40:
                    if rel in FLIP: a, b, rel = b, a, FLIP[rel]
                    out.add((a, rel, b, pol))
                break
        return out

    @staticmethod
    def _closure(claims):
        C = {}
        for a, r, b, p in claims:
            if p and r != 'eq': C.setdefault(r, set()).add((a, b))
        for E in C.values():
            new = {1}
            while new:
                new = {(a, d) for (a, b) in E for (c, d) in E if b == c} - E; E |= new
        return C

    def _tensor(self, allc, C):
        n = len(allc); T = np.zeros((n, n, 4))
        for i, (a, r, b, p) in enumerate(allc):
            E = C.get(r, set()); reach = lambda x, y: x == y or (x, y) in E
            for j, (c, s, d, q) in enumerate(allc):
                if r != s: continue
                if i == j: T[i, j, 0] = 1; continue
                if r == 'eq':
                    if (a, b) == (c, d) and p != q: T[i, j, 1] = 1
                    elif a == c and b != d and p and q and re.fullmatch(NUM, b) and re.fullmatch(NUM, d): T[i, j, 1] = 1
                elif p and q and reach(b, c) and reach(d, a): T[i, j, 1] = 1       # cycle => contradiction
                elif (p, q) == (0, 1) and reach(a, c) and reach(d, b): T[i, j, 1] = 1   # modus tollens
                elif (p, q) == (1, 0) and reach(c, a) and reach(b, d): T[i, j, 1] = 1
                elif p and q and reach(c, a) and reach(b, d): T[i, j, 0] = 1           # i entails j
                elif p and q and b == c: T[i, j, 2 if r != 'causes' else 3] = 1        # chain (modus ponens)
        return T

    # ---------------- tensor decomposition + PI feedback ----------------
    def _hosvd(self, T):
        R = T
        for m in range(3):
            M = np.moveaxis(T, m, 0).reshape(T.shape[m], -1)
            U = np.linalg.svd(M, full_matrices=False)[0][:, :self.rank]
            R = np.moveaxis(np.tensordot(U.dot(U.T), np.moveaxis(R, m, 0), axes=1), 0, m)
        return R

    def _feedback(self, T):
        w, cum, prev, osc, res = np.ones(4), np.zeros(4), np.zeros(4), 0, np.zeros(T.shape[0])
        for _ in range(self.iters):
            Tw = T * w; D = np.abs(Tw - self._hosvd(Tw))
            e = D.sum(axis=(0, 1)); e = e / max(e.sum(), 1e-9) - 0.25       # signed slice error
            cum += e; step = self.kp * e + self.ki * cum
            osc += int(np.any(step * prev < -1e-9)); prev = step             # Nyquist-like guard
            w = np.clip(w + step, 0.2, 3.0)
            new = D.sum(axis=(1, 2)) / w.sum()
            done = osc >= 3 or np.abs(new - res).max() < 1e-4; res = new
            if done: break
        return res, osc >= 3

    # ---------------- Nash best-response over candidates ----------------
    @staticmethod
    def _nash(G, K, R):
        q = np.ones(len(G)) / len(G); pay = G
        for _ in range(100):
            pay = G - 0.5 * R - K.dot(q)
            z = np.exp(4 * (pay - pay.max())); q2 = z / z.sum()
            if np.abs(q2 - q).max() < 1e-6: q = q2; break
            q = q2
        return pay, q

    def _analyze(self, prompt, cands):
        ground = self._claims(re.sub(r'[^.!?]*\?', ' ', prompt))
        csets = [self._claims(c) for c in cands]
        allc = sorted(ground.union(*csets)); idx = {c: i for i, c in enumerate(allc)}
        m = len(cands); G, Rm, K = np.zeros(m), np.zeros(m), np.zeros((m, m))
        if not allc: return G, G, np.ones(m) / m, False, len(ground)
        T = self._tensor(allc, self._closure(ground))
        res, unstable = self._feedback(T); gi = [idx[c] for c in ground]
        for x, cs in enumerate(csets):
            ii = [idx[c] for c in cs]
            if not ii: continue
            ent = sum(T[gi][:, i, 0].max() for i in ii) if gi else 0
            con = sum(max(T[i, gi, 1].max(), T[gi, i, 1].max()) for i in ii) if gi else 0
            G[x] = (ent - 2 * con) / len(ii); Rm[x] = res[ii].mean()
            for y, ds in enumerate(csets):
                if y != x and ds: K[x, y] = T[np.ix_(ii, [idx[c] for c in ds], [1])].sum() / len(ii)
        pay, q = self._nash(G, K, Rm)
        return G, pay, q, unstable, len(ground)

    # ---------------- constructive computation ----------------
    def _compute(self, prompt):
        p = ' '.join(prompt.lower().replace(',', '').split())
        nums = [float(x) for x in re.findall(NUM, p)]
        pct = [float(x) / 100 for x in re.findall(r'(' + NUM + r')\s*(?:%|percent)', p)]
        m = re.search(r'(?:what is|calculate|evaluate|compute|solve)\s*:?\s*([\d\s+\-*/().^x]+?)\s*(?:\?|$)', p)
        if m and re.search(r'[+\-*/^x]', m.group(1)) and re.search(r'\d', m.group(1)):
            try: return [float(eval(m.group(1).replace('^', '**').replace('x', '*'), {'__builtins__': {}}, {}))]
            except Exception: pass
        m = re.search(r'remainder when (' + NUM + r') is divided by (' + NUM + ')|(' + NUM + r') mod(?:ulo)? (' + NUM + ')', p)
        if m: g = [x for x in m.groups() if x]; return [float(g[0]) % float(g[1])]
        if len(pct) >= 3 and re.search(r'\b(test|positive|detect|screen)', p):
            fp = re.search(r'false[ -]positive[^%\d]*(' + NUM + r')\s*(?:%|percent)', p)
            pri, sen, fpr = pct[0], pct[1], (float(fp.group(1)) / 100 if fp else pct[2])
            post = pri * sen / max(pri * sen + (1 - pri) * fpr, 1e-12); return [post * 100, post]
        ev = re.findall(r'(' + NUM + r')\s*(?:%|percent)\s*(?:chance|probability)[^.;]*?\b(win|gain|earn|receive|get|lose|loss|pay)\w*[^.;\d]*\$?(' + NUM + ')', p)
        if len(ev) >= 2: return [sum(float(a) / 100 * float(v) * (-1 if w in ('lose', 'loss', 'pay') else 1) for a, w, v in ev)]
        t = re.findall(r'in (' + NUM + r') (?:hours?|minutes?|days?)', p)
        if len(t) >= 2 and 'together' in p: x, y = float(t[0]), float(t[1]); return [x * y / (x + y)]
        sp = re.search(r'(' + NUM + r')\s*(?:mph|km/h|kph|miles per hour|km per hour)', p)
        if sp:
            s = float(sp.group(1)); hrs = re.search(r'(?:for|in) (' + NUM + r') hours?', p)
            dist = re.search(r'(' + NUM + r')\s*(?:miles|km|kilometers)', p)
            if hrs and re.search(r'how far|distance', p): return [s * float(hrs.group(1))]
            if dist and re.search(r'how long|how many hours', p): return [float(dist.group(1)) / s]
        ag = re.search(r'(\w+) is (' + NUM + r') years (older|younger) than (\w+)', p)
        if ag and re.search(ag.group(4) + r' is (' + NUM + ')', p):
            base = float(re.search(ag.group(4) + r' is (' + NUM + ')', p).group(1)) + float(ag.group(2)) * (1 if ag.group(3) == 'older' else -1)
            fut = re.search(r'in (' + NUM + r') years', p); return [base + float(fut.group(1))] if fut else [base]
        cm = re.search(r'\bis (' + NUM + r') (greater|bigger|larger|more|higher|less|smaller|lower) than (' + NUM + ')', p)
        if cm: x, y = float(cm.group(1)), float(cm.group(3)); return [x > y if cm.group(2) in ('greater', 'bigger', 'larger', 'more', 'higher') else x < y]
        if re.search(r'\b(bigger|larger|greater|smaller|less|lower|higher)\b', p) and '?' in p and len(nums) == 2:
            return [max(nums) if re.search(r'\b(bigger|larger|greater|higher|more)\b', p) else min(nums)]
        sched = re.findall(r'(\d{1,2})(?::(\d\d))?\s*(am|pm)?\s*(?:to|-|until|till)\s*(\d{1,2})(?::(\d\d))?\s*(am|pm)?', p)
        if len(sched) >= 2 and re.search(r'conflict|overlap|both|same time', p):
            tm = lambda h, mi, ap: int(h) % 12 + (12 if ap == 'pm' else 0) + int(mi or 0) / 60
            iv = [(tm(a, b, c or f), tm(d, e, f or c)) for a, b, c, d, e, f in sched[:2]]
            return [max(iv[0][0], iv[1][0]) < min(iv[0][1], iv[1][1])]
        if re.search(r'\b(first|earliest|last|latest)\b', p) and '?' in p:
            E = self._closure(self._claims(re.sub(r'[^.!?]*\?', ' ', prompt))).get('before')
            if E:
                heads, tails = {a for a, b in E}, {b for a, b in E}
                pick = heads - tails if re.search(r'first|earliest', p) else tails - heads
                if len(pick) == 1: return [pick.pop()]
        return None

    @staticmethod
    def _match(targets, cand):
        c = cand.lower(); t0 = targets[0]
        if isinstance(t0, bool):
            yes = bool(re.search(r'\b(yes|true|correct|conflict|overlap|clash)', c)) and not NEG.search(c)
            return 1.0 if yes == t0 else 0.0
        if isinstance(t0, str): return 1.0 if t0 in c else 0.0
        vals = [float(x) for x in re.findall(NUM, c.replace(',', ''))]
        return 1.0 if any(abs(v - t) <= max(0.02 * abs(t), 0.011) for v in vals for t in targets) else 0.0

    @staticmethod
    def _ncd(a, b):
        za, zb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        return (len(zlib.compress((a + b).encode())) - min(za, zb)) / max(za, zb, 1)

    # ---------------- public interface ----------------
    def evaluate(self, prompt, candidates):
        if not candidates: return []
        targets = self._compute(prompt)
        G, pay, q, unstable, _ = self._analyze(prompt, candidates)
        span = max(pay.max() - pay.min(), 1e-9); out = []
        for i, c in enumerate(candidates):
            comp = self._match(targets, c) if targets else 0.5
            struct = 0.6 * (pay[i] - pay.min()) / span + 0.4 * q[i] / max(q.max(), 1e-9)
            ncd = 1.0 - self._ncd(prompt, c)
            score = 0.40 * comp + 0.50 * struct + 0.10 * ncd   # computation 40 / structural 50 / NCD 10
            why = 'computed=%s match=%.0f; ground=%.2f payoff=%.2f eq_weight=%.2f%s' % (
                'none' if not targets else str(targets[0])[:12], comp, G[i], pay[i], q[i], ' [oscillating]' if unstable else '')
            out.append({'candidate': c, 'score': round(float(score), 4), 'reasoning': why})
        return sorted(out, key=lambda d: -d['score'])

    def _meta_confidence(self, prompt):
        p = ' '.join(prompt.lower().split()); cap = 1.0
        for pat, c in META:
            if re.search(pat, p): cap = min(cap, c)
        if re.search(r'\b(how (many|much|old|long|far)|what is|which)\b', p) and not re.search(NUM, p) \
                and not self._claims(re.sub(r'[^.!?]*\?', ' ', prompt)):
            cap = min(cap, 0.25)   # asks for a quantity/selection but supplies no data
        return cap

    def confidence(self, prompt, answer):
        cap = self._meta_confidence(prompt); targets = self._compute(prompt)
        if targets is not None: return float(min(0.9 if self._match(targets, answer) else 0.08, cap))
        G, _, _, unstable, n_ground = self._analyze(prompt, [answer])
        if n_ground == 0 or not self._claims(answer): return float(min(0.25, cap))
        return float(min(max(0.4 + 0.3 * np.tanh(G[0]) - (0.1 if unstable else 0.0), 0.05), 0.7, cap))


# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence


# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
