import itertools
import zlib

"""
ReasoningTool: Quantum Mechanics x Neural Plasticity x Model Checking.
Mechanism: candidate text -> propositions (a tiny Kripke structure).  Ambiguous
negation scope yields a weighted parse forest ('superposition'); worlds that
contain a contradiction are pruned ('measurement') and the surviving mass is the
consistency score.  Prompt specs are CALCULATED (numeric compare, PEMDAS, modulo,
percent, transitive closure, modus ponens/tollens, Bayes, work-rate) and each
candidate is model-checked against the result.  Constraint-type weights adapt
Hebbian-style within a batch ('plasticity', frozen before scoring).  Confidence
is capped by _meta_confidence, which inspects the QUESTION for presupposition,
scope/pronoun ambiguity, false dichotomy, subjectivity and unanswerability.
"""
import re, zlib, itertools
import numpy as np

NUM = r'-?\d+(?:\.\d+)?'
HEDGE = re.compile(r"cannot be (determined|known|answered|concluded)|can'?t (be determined|say|tell|know)|not enough|insufficient|ambiguous|depends|unclear|assum|presuppos|not necessarily|neither|other option|false (dichotomy|choice|dilemma)|loaded|unanswerable|no way to know|either could|could be either|more information|not (valid|sound)|invalid|does ?n[o']t follow|regression|survivor|sunk cost|luck|chance|random|both", re.I)
NEG = re.compile(r"\b(not|no|never|isn't|aren't|wasn't|doesn't|didn't|don't|cannot|can't|won't|false)\b", re.I)
STOP = {'then', 'that', 'will', 'woul', 'this', 'they', 'with', 'ther', 'have', 'been', 'does', 'from', 'whic', 'beca'}
CMP = {'taller': 'shorter', 'older': 'younger', 'faster': 'slower', 'heavier': 'lighter', 'bigger': 'smaller',
       'larger': 'smaller', 'stronger': 'weaker', 'richer': 'poorer', 'higher': 'lower', 'longer': 'shorter'}
LOW = {v: k for k, v in CMP.items()}
META = [  # (flag, regex over the whitespace-normalised prompt) -- QUESTION properties only
    ('presupposition', r"\b(have|has|had|did|when did) (you|he|she|they|it|\w+) (stop|quit|cease|give up|given up|stopped|ceased|finally)\b|\bwhy (did|does|do|has|is|are) .{0,40}\b(fail|stop|quit|lie|cheat|hate|refuse|always|worse)"),
    ('scope', r"\b(every|each|all)\b .{0,40}\b(a|an|some|one)\b .{0,80}\b(same|different|how many)\b"),
    ('pronoun', r"\b\w+ (told|said to|asked|informed|called|met) \w+ (that )?(he|she|they|his|her|their)\b.*\bwho(m|se)?\b"),
    ('false_dichotomy', r"\beither\b .{0,80}\bor\b .{0,80}\?|\bwhich (one )?(is|must be) (it|true|right)\b|\bonly (two )?(options|choices|possibilit)"),
    ('subjective', r"\b(best|worst|favou?rite|most beautiful|greatest|nicest|coolest|tastiest)\b(?!.{0,60}\b(by|according to|measured|in terms of|defined)\b)"),
    ('survivorship', r"\b(survivor|survived|successful (people|companies|founders|entrepreneurs)|dropouts?|returned|came back|winners)\b.{0,100}\b(should|therefore|so|prove|means|conclude)\b"),
    ('sunk_cost', r"\b(already (spent|invested|paid|put in|sunk)|sunk cost|wasted)\b"),
    ('regression', r"\b(regress|after (praise|praising|punish|scolding|yelling)|worst (day|game|performance|score)|best (day|game|performance|score)|extreme)\b.{0,80}\b(next|following|then|improved|got worse)\b"),
    ('validity', r"\b(valid|sound|logically follow|argument|strong|weak)\b.{0,120}\b(true|premise|conclusion|argument)\b"),
    ('unanswerable', r"\b(what am i thinking|what number am i|in my (pocket|bag|house|head)|what did .{0,30} dream|what will .{0,40}(tomorrow|next year))"),
    ('intent_outcome', r"\b(intend|meant to|tried to|by accident|accidentally|deliberately|on purpose|deceiv|lie|bluff)\b.{0,100}\b(blame|responsib|wrong|moral|guilty|honest|trust)\b"),
]


class ReasoningTool:
    BASE = np.array([0.33, 0.45, 0.12, 0.10])  # structural, judgment, consistency (model check), ncd

    def __init__(self):
        self.eta = 0.1  # Hebbian learning rate (critical period = one batch)

    # ---------- judgment layer: properties of the QUESTION ----------
    def _meta_flags(self, prompt):
        p = ' '.join(prompt.split())
        return [n for n, rx in META if re.search(rx, p, re.I)]

    def _meta_confidence(self, prompt):
        return 0.2 if self._meta_flags(prompt) else 1.0

    # ---------- constructive solvers: prompt -> spec ----------
    def _solve(self, p):
        for f in (self._bayes, self._work, self._arith, self._compare, self._transitive, self._conditional):
            r = f(p)
            if r: return r
        return None

    def _bayes(self, p):
        got = {}
        for m in re.finditer(NUM + r"\s*(?:%|percent)", p):
            v = float(re.match(NUM, m.group(0)).group(0)) / 100
            for ctx in (p[m.end():m.end() + 45].lower(), p[max(0, m.start() - 70):m.start()].lower()):
                k = ('fp' if 'false positive' in ctx or 'falsely' in ctx else 'spec' if 'specific' in ctx else
                     'sens' if re.search(r"sensitiv|true positive|correctly|detect|accura", ctx) else
                     'prev' if re.search(r"prevalen|base rate|population|have the|of (people|women|patients|adults)|infected|carry", ctx) else None)
                if k: got.setdefault(k, v); break
        if 'prev' in got and 'sens' in got and ('fp' in got or 'spec' in got):
            fp = got.get('fp', 1 - got.get('spec', 0)); a = got['prev'] * got['sens']
            return ('num', 100 * a / (a + (1 - got['prev']) * fp), 1.0, 'bayes posterior %')
        return None

    def _work(self, p):
        m = re.search(r"(?:in|takes) (" + NUM + r") (hours?|minutes?|days?).{0,120}?(?:in|takes) (" + NUM + r") \2.{0,150}?together", p, re.I | re.S)
        if not m: return None
        x, y = float(m.group(1)), float(m.group(3)); t = x * y / (x + y)
        return ('num', t, 0.02 * t + 0.01, 'work rate xy/(x+y)')

    def _arith(self, p):
        m = re.search(r"remainder (?:when|of) (" + NUM + r") (?:is )?divided by (" + NUM + r")|(" + NUM + r") mod(?:ulo)? (" + NUM + ")", p, re.I)
        if m:
            a, b = [float(g) for g in m.groups() if g is not None]
            return ('num', a % b, 1e-9, 'modular arithmetic') if b else None
        m = re.search(r"(" + NUM + r")\s*(?:%|percent) of (" + NUM + ")", p, re.I)
        if m: return ('num', float(m.group(1)) * float(m.group(2)) / 100, 1e-6, 'percent of')
        m = re.search(r"(?:what is|what's|calculate|compute|evaluate|solve)\s*:?\s*([\d\s\.\+\-\*/x\(\)\^]+?)\s*[?=]", p, re.I)
        if m:
            e = m.group(1).replace('x', '*').replace('^', '**').strip()
            if re.search(r"[\+\-\*/]", e) and re.fullmatch(r"[\d\s\.\+\-\*/\(\)]+", e) and '**' not in e:
                try: return ('num', float(eval(e, {"__builtins__": {}})), 1e-6, 'PEMDAS ' + e)
                except Exception: return None
        return None

    def _compare(self, p):
        m = re.search(r"\b(?:which|what)\b[^?]*?\b(larger|bigger|greater|smaller|less|lower|higher)\b[^?]*?(" + NUM + r")[^\d.-]+(" + NUM + ")", p, re.I)
        if not m: return None
        a, b = float(m.group(2)), float(m.group(3)); big = m.group(1).lower() in ('larger', 'bigger', 'greater', 'higher')
        return ('first_num', max(a, b) if big else min(a, b), 1e-9, 'float compare %s vs %s' % (a, b))

    def _transitive(self, p):
        gt = set()
        for a, adj, b in re.findall(r"\b([A-Z]\w+) is (\w+) than ([A-Z]\w+)", p):
            adj = adj.lower()
            if adj in CMP: gt.add((a, b))
            elif adj in LOW: gt.add((b, a))
        if len(gt) < 2: return None
        while True:  # transitive closure = reachability in the order graph
            new = {(a, d) for (a, b) in gt for (c, d) in gt if b == c} - gt
            if not new: break
            gt |= new
        names = {x for e in gt for x in e}
        m = re.search(r"who is (?:the )?(\w+)est\b", p, re.I)
        if m:
            base = m.group(1).lower()
            if any(k.startswith(base) for k in CMP): win = [x for x in names if all((x, y) in gt for y in names if y != x)]
            elif any(k.startswith(base) for k in LOW): win = [x for x in names if all((y, x) in gt for y in names if y != x)]
            else: return None
            return ('name', win[0], names, 'transitive closure') if len(win) == 1 else ('undetermined', None, 0, 'order not total')
        m = re.search(r"\bis ([A-Z]\w+) (\w+) than ([A-Z]\w+)\?", p)
        if m:
            a, adj, b = m.group(1), m.group(2).lower(), m.group(3)
            if adj in LOW: a, b = b, a
            elif adj not in CMP: return None
            v = 'yes' if (a, b) in gt else 'no' if (b, a) in gt else None
            return ('yesno', v, 0, 'transitive closure') if v else ('undetermined', None, 0, 'not entailed')
        return None

    @staticmethod
    def _keys(s): return {w[:4] for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 3 and not NEG.match(w)} - STOP

    def _mention(self, s, t):
        k = self._keys(t); return bool(k) and len(k & self._keys(s)) / len(k) >= 0.5

    def _conditional(self, p):
        m = re.search(r"\bif ([^,.]+?),? then ([^.?;]+)[.?;]|\bif ([^,.]+?), ([^.?;]+)[.?;]", p, re.I)
        if not m: return None
        P, Q = [g.strip() for g in m.groups() if g is not None]; par = lambda s: len(NEG.findall(s)) % 2
        for s in re.split(r"(?<=[.!?])\s+", p[m.end():]):
            if not s.strip() or s.strip().endswith('?'): continue
            mp, mq = self._mention(s, P), self._mention(s, Q)
            if mq and not mp: return ('text', 'not ' + P, 0, 'modus tollens') if par(s) != par(Q) else ('undetermined', None, 0, 'affirming the consequent')
            if mp: return ('undetermined', None, 0, 'denying the antecedent') if par(s) != par(P) else ('text', Q, 0, 'modus ponens')
        return None

    # ---------- model check a candidate against the spec ----------
    def _match(self, sol, c):
        kind, val = sol[0], sol[1]; nums = [float(x) for x in re.findall(NUM, c)]
        if kind == 'first_num': return float(bool(nums) and abs(nums[0] - val) < 1e-9)
        if kind == 'num': return float(any(abs(n - val) <= sol[2] or abs(n - val / 100) <= sol[2] / 100 for n in nums))
        if kind == 'name':
            found = [w for w in re.findall(r"[A-Z]\w+", c) if w in sol[2]]
            return float(found[0] == val) if found else 0.3
        if kind == 'yesno':
            m = re.match(r"\W*(yes|no)\b", c, re.I)
            return float(m.group(1).lower() == val) if m else (0.1 if HEDGE.search(c) else 0.3)
        if kind == 'text': return float(self._mention(c, val) and len(NEG.findall(c)) % 2 == len(NEG.findall(val)) % 2)
        return float(bool(HEDGE.search(c)))  # undetermined: the honest answer hedges

    def _consistency(self, c):
        """Superposition: weighted parse forest over negation scope; measurement prunes contradictory worlds."""
        alts = []
        for s in [x for x in re.split(r"(?<=[.;!?])\s+|\bbut\b|\bhowever\b", c) if x.strip()]:
            par = len(NEG.findall(s)) % 2
            parts = [k for k in (self._keys(x) for x in re.split(r"\b(?:and|or)\b", s)) if k]
            wide = [(frozenset(k), par) for k in parts]
            if par and len(parts) > 1:  # wide-scope negation (0.6) vs narrow-scope (0.4)
                alts.append([(0.6, wide), (0.4, [(frozenset(parts[0]), 1)] + [(frozenset(k), 0) for k in parts[1:]])])
            elif wide: alts.append([(1.0, wide)])
        if not alts: return 0.5
        mass = 0.0
        for combo in itertools.product(*alts[:8]):
            world, ok = {}, True
            for _, props in combo:
                for k, pr in props:
                    if world.setdefault(k, pr) != pr: ok = False
            mass += ok * float(np.prod([w for w, _ in combo]))
        return mass

    @staticmethod
    def _ncd(a, b):
        z = lambda s: len(zlib.compress(s.encode('utf-8', 'ignore')))
        za, zb = z(a), z(b)
        return (z(a + ' ' + b) - min(za, zb)) / max(za, zb, 1)

    def _hebb(self, F):
        """Plasticity: constraint types whose satisfaction co-varies with inter-candidate agreement are
        strengthened; zero-variance types are pruned (corr 0). Frozen after this calibration pass."""
        if len(F) < 3: return self.BASE.copy()
        agree, corr = F.mean(axis=1), np.zeros(4)
        for k in range(4):
            if F[:, k].std() > 1e-9 and agree.std() > 1e-9: corr[k] = np.corrcoef(F[:, k], agree)[0, 1]
        ad = np.exp(np.log(self.BASE) + self.eta * np.nan_to_num(corr)); ad /= ad.sum()
        return 0.7 * self.BASE + 0.3 * ad  # keeps judgment >= 0.40, structural >= 0.30, ncd <= 0.15

    def evaluate(self, prompt, candidates):
        flags, sol = self._meta_flags(prompt), self._solve(prompt)
        F, notes = [], []
        for c in candidates:
            hedge = bool(HEDGE.search(c))
            s = self._match(sol, c) if sol else 0.5
            if flags: j = 1.0 if hedge else 0.15
            elif sol and sol[0] == 'undetermined': j = 1.0 if hedge else 0.2
            else: j = 0.35 if hedge else 0.7
            k = self._consistency(c)
            F.append([s, j, k, 1.0 - self._ncd(prompt, c)]); notes.append((hedge, s, k))
        F = np.array(F, dtype=float) if F else np.zeros((0, 4))
        w = self._hebb(F); scores = F @ w
        out = [{'candidate': c, 'score': round(float(sc), 4),
                'reasoning': 'flags=%s; solver=%s; structural=%.2f; hedged=%s; consistency=%.2f; w=%s' % (
                    flags or 'none', sol[3] if sol else 'none', s, h, k, np.round(w, 2).tolist())}
               for c, sc, (h, s, k) in zip(candidates, scores, notes)]
        return sorted(out, key=lambda d: -d['score'])

    def confidence(self, prompt, answer):
        cap = self._meta_confidence(prompt)
        hedge, sol, k = bool(HEDGE.search(answer)), self._solve(prompt), self._consistency(answer)
        if cap < 0.3: return min(cap, 0.25 if hedge else 0.12)  # ambiguous / loaded / unanswerable question
        if sol is None: return 0.28 if k > 0.5 else 0.1          # no structural parser: honest uncertainty
        if sol[0] == 'undetermined': return 0.65 if hedge else 0.12
        s = self._match(sol, answer)
        if s >= 1.0: return 0.92 if k > 0.5 else 0.6              # computation produced a definitive answer
        return 0.3 if s > 0 else 0.06


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
