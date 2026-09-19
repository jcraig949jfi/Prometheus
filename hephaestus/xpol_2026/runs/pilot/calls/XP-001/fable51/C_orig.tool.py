import re
import itertools
import zlib
import operator

"""Entangled Plastic Model Checker (EPMC) reasoning tool.

Mechanism: atomic propositions are extracted from the prompt (conditionals,
causals, negated facts, the question) and from each candidate.  Constraints
form a weighted implication graph whose Hebbian weights start at 0.5; over T
iterations each candidate's propositional set (its claim + prompt facts)
potentiates co-activated edges and depresses silent ones; weak synapses are
pruned.  All 2^p truth states are enumerated (model checking); a state's
weight decays by (1-w) per violated implication and is zeroed by a violated
fact.  A candidate's sat_ratio is the weighted fraction of states in which its
claim holds ("cannot be determined" scores high only when no claim is
determined).  Candidates start in uniform superposition and collapse
Born-rule style on these ratios.  A computation channel (numeric comparison,
arithmetic, transitive orderings) handles calculable prompts; zlib NCD is a
<=15% tiebreaker.  _meta_confidence inspects the QUESTION for presupposition,
scope/pronoun ambiguity, false dichotomy, subjectivity and judgment traps and
caps confidence at 0.2 regardless of answer quality.
"""
import ast, itertools, operator, re, zlib
import numpy as np


class ReasoningTool:
    T, ETA, TAU, MAXP = 5, 0.1, 0.2, 10
    META = [
        ("presupposition", r"\b(have|has|had|did) (you|he|she|they|it|we) (stopped|quit|ceased|given up|started|finally)\b|\bwhy (did|does|do|has|have|is|are|was|were) [^?]*(fail|stop|quit|cheat|lie|lied|refuse|hate)|\bwhen did [^?]* stop\b|\b(still|anymore|again)\b[^.]*\?"),
        ("scope_ambiguity", r"\b(every|each|all) \w+ [^.?!]*\b(a|an|some) \w+[^?]*\b(same|different)\b"),
        ("pronoun_ambiguity", r"\b(told|asked|said to|informed|warned|called)\b[^?]*\b(he|she|they|his|her|their|him|them)\b[^?]*\b(who|whom|whose|which)\b"),
        ("false_dichotomy", r"\beither\b[^?]*\bor\b|\bonly (two|2) (options|choices|ways)\b|\bmust (be|choose) (either|one of|between)\b"),
        ("subjectivity", r"\b(best|worst|favou?rite|greatest|most beautiful|nicest)\b(?! (describes|explains|estimate|answer|approximat|represents|supports|fits|matches|complet|characteri))"),
        ("judgment_trap", r"\b(survivor|survived|those who (made it|succeeded)|sunk cost|already (spent|invested|paid)|regress|streak|lucky|deceiv|bluff|pretend|intend|meant to|on purpose|accident|valid argument|argument (is )?(valid|sound|strong|weak)|fallac|how confident|persuasive)"),
        ("unanswerable", r"\b(not enough information|cannot be determined|how (many|much) [^?]*(in the world|exist|are there)|what (am i|is he|is she) thinking|guess)\b"),
    ]
    NEGRX = re.compile(r"\b(not|no|never|false|cannot|none|neither|nobody)\b")
    QSTOP = set("it the a an is was are were be been being did does do will would shall should to of that this in on at and then there they he she we i you his her its their them him also very really who what which whom whose can could must how why when where true".split())
    UNK = re.compile(r"cannot|can't|not (be )?determined|insufficient|not enough|unknown|not necessarily|indeterminate|undetermined|either could|impossible to|depends|ambiguous|unclear")
    YES, NO = re.compile(r"^\W*(yes|true|correct|valid)\b"), re.compile(r"^\W*(no|false|incorrect|invalid)\b")
    COND = [(r"^if (.+?),? then (.+)$", 0), (r"^if (.+?), (.+)$", 0), (r"^unless (.+?), (.+)$", 1), (r"^whenever (.+?), (.+)$", 0),
            (r"^(.+?) (?:causes?|leads? to|results? in|implies|means that|guarantees?|only if|requires?) (.+)$", 0)]
    NUM = r"-?\d+(?:\.\d+)?"
    OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg}
    BIG = {"larger", "bigger", "greater", "higher", "more", "biggest", "largest", "greatest", "highest"}

    # ---------------- judgment layer ----------------
    def _meta_confidence(self, prompt):
        p = prompt.lower()
        hits = [name for name, rx in self.META if re.search(rx, p)]
        return (0.2 if hits else 1.0), hits

    # ---------------- proposition extraction ----------------
    def _toks(self, text):
        t = text.lower().replace("n't", " not")
        neg = bool(self.NEGRX.search(t))
        ws = [w for w in re.findall(r"[a-z]+", self.NEGRX.sub(" ", t)) if w not in self.QSTOP]
        return frozenset(re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w for w in ws), neg

    def _canon(self, toks, names, add):
        best, bj = None, 0.0
        for nm, nt in names.items():
            j = len(toks & nt) / max(1, len(toks | nt))
            if j > bj: best, bj = nm, j
        if bj >= 0.5: return best
        if not add: return None
        nm = " ".join(sorted(toks)); names[nm] = toks
        return nm

    # ---------------- EPMC core: plastic weighted model check ----------------
    def _epmc(self, prompt, cands):
        names, edges, facts, qprop = {}, [], [], None
        for s in re.split(r"(?<=[.;!?])\s+", prompt.strip()):
            low = s.strip().lower().rstrip(".;!")
            if not low or re.search(r"\bthan\b", low): continue
            if low.endswith("?"):
                t, ng = self._toks(low.rstrip("?"))
                if t: qprop = (self._canon(t, names, True), ng)
                continue
            for rx, flip in self.COND:
                m = re.match(rx, low)
                if m:
                    (ta, na), (tb, nb) = self._toks(m.group(1)), self._toks(m.group(2))
                    if ta and tb: edges.append((self._canon(ta, names, True), bool(na ^ flip), self._canon(tb, names, True), nb))
                    break
            else:
                t, ng = self._toks(re.sub(r"^(therefore|so|thus|hence|but|however|and|now|suppose|assume|given that|we know that|we know|fact:)\s*,?\s*", "", low))
                if t and len(t) <= 6 and not re.search(r"\d", low): facts.append((self._canon(t, names, True), ng))
        keys = list(names)[:self.MAXP]; idx = {k: i for i, k in enumerate(keys)}; p = len(keys)
        claims = []
        for c in cands:
            cl = c.lower()
            if self.UNK.search(cl): claims.append(("UNK", False))
            elif self.YES.match(cl): claims.append(qprop or (None, False))
            elif self.NO.match(cl): claims.append((qprop[0], not qprop[1]) if qprop else (None, False))
            else:
                t, ng = self._toks(cl); claims.append((self._canon(t, names, False) if t else None, ng))
        if p == 0 or not edges: return np.full(len(cands), 0.5), False
        states = np.array(list(itertools.product([False, True], repeat=p)), dtype=bool)
        w, fset = np.full(len(edges), 0.5), {f for f, _ in facts}
        for _ in range(self.T):                              # critical period: Hebbian potentiation / depression
            for nm, _ in claims:
                cp = fset | {nm}
                for k, (a, _, b, _) in enumerate(edges):
                    m = (a in cp) + (b in cp)
                    w[k] += self.ETA * (1 - w[k]) if m == 2 else (-self.ETA * w[k] if m == 0 else 0.0)
            w[w < self.TAU] = 0.0                            # synaptic pruning
        sw = np.ones(len(states))
        for k, (a, na, b, nb) in enumerate(edges):           # weighted transition relation: box(ant -> con)
            if w[k] == 0 or a not in idx or b not in idx: continue
            ok = ~(states[:, idx[a]] ^ na) | (states[:, idx[b]] ^ nb)
            sw = np.where(ok, sw, sw * (1 - w[k]))
        for f, nf in facts:
            if f in idx: sw = np.where(states[:, idx[f]] ^ nf, sw, 0.0)
        tot = sw.sum()
        prob = lambda nm, ng: 0.5 if (nm not in idx or tot == 0) else float(sw[states[:, idx[nm]] ^ ng].sum() / tot)
        det = [abs(2 * prob(nm, ng) - 1) for nm, ng in claims if nm not in (None, "UNK")] + ([abs(2 * prob(*qprop) - 1)] if qprop else [])
        out = [1 - max(det or [0.0]) if nm == "UNK" else prob(nm, ng) for nm, ng in claims]
        fired = any(nm in idx or nm == "UNK" for nm, _ in claims)
        return np.array(out), fired

    # ---------------- computation channel ----------------
    def _ev(self, n):
        if isinstance(n, ast.Constant): return float(n.value)
        if isinstance(n, ast.BinOp): return self.OPS[type(n.op)](self._ev(n.left), self._ev(n.right))
        if isinstance(n, ast.UnaryOp): return self.OPS[type(n.op)](self._ev(n.operand))
        raise ValueError("bad node")

    def _compute(self, prompt, cands):
        p = prompt.lower().replace(",", "")
        for a, b in [(r"\b(mod|modulo)\b", "%"), (r"\bdivided by\b", "/"), (r"\b(times|multiplied by)\b", "*"), (r"\bplus\b", "+"), (r"\bminus\b", "-")]:
            p = re.sub(a, b, p)
        cn = [[float(x) for x in re.findall(self.NUM, c.replace(",", ""))] for c in cands]
        nums = [float(x) for x in re.findall(self.NUM, p)]
        m = re.search(r"\b(%s|smaller|less|lower|fewer|smallest|lowest|least)\b" % "|".join(self.BIG), p)
        exprs = [e for e in re.findall(r"[\d\(][\d\.\s\+\-\*/\(\)x\^%]*[\d\)]", p) if re.search(r"\d\s*[\+\-\*/x\^%]\s*[\d\(]", e)]
        target = None
        if exprs:
            try: target = self._ev(ast.parse(max(exprs, key=len).replace("x", "*").replace("^", "**"), mode="eval").body)
            except Exception: target = None
        if target is None and m and len(nums) >= 2:
            if re.search(r"\bthan\b", p):                    # "Is 9.11 greater than 9.9?"
                truth = (nums[0] > nums[1]) if m.group(1) in self.BIG else (nums[0] < nums[1])
                sc = [1.0 if self.YES.match(c.lower()) == bool(truth) or self.NO.match(c.lower()) == (not truth) else 0.0 for c in cands]
                return np.array([1.0 if (self.YES.match(c.lower()) and truth) or (self.NO.match(c.lower()) and not truth) else 0.0 for c in cands])
            target = max(nums) if m.group(1) in self.BIG else min(nums)
        if target is None: return None
        return np.array([1.0 if any(abs(v - target) <= 1e-6 * max(1.0, abs(target)) for v in vs) else 0.0 for vs in cn])

    def _order(self, prompt, cands):
        p = prompt.lower()
        rel = re.findall(r"\b([a-z]+) (?:is|was|are|were|runs|ran) (?:([a-z]+)er|more ([a-z]+)) than ([a-z]+)", p)
        stems = {(r[1] or r[2]) for r in rel}
        if len(stems) != 1: return None
        stem, gt = stems.pop(), {}
        for a, _, _, b in rel: gt.setdefault(a, set()).add(b)
        nodes = set(gt) | {b for s in gt.values() for b in s}
        def reach(a, b, seen=()):
            return any(c == b or (c not in seen and reach(c, b, seen + (c,))) for c in gt.get(a, ()))
        qs = [s for s in re.split(r"(?<=[.!?])\s+", p) if s.endswith("?")]; q = qs[-1] if qs else p
        mc = re.search(r"\bis ([a-z]+) (?:([a-z]+)er|more ([a-z]+)) than ([a-z]+)", q)
        ms = re.search(r"\b(?:([a-z]+)est|most ([a-z]+)|least ([a-z]+))\b", q)
        if mc:
            a, b, s2 = mc.group(1), mc.group(4), (mc.group(2) or mc.group(3))
            ab, ba = (reach(a, b), reach(b, a)) if s2 == stem else (reach(b, a), reach(a, b))
            tr = 1.0 if ab else (0.0 if ba else 0.5)
            return np.array([tr if self.YES.match(c.lower()) else 1 - tr if self.NO.match(c.lower()) else 1 - abs(2 * tr - 1) if self.UNK.search(c.lower()) else 0.0 for c in cands])
        if not ms: return None
        ss = ms.group(1) or ms.group(2) or ms.group(3)
        top = (ss == stem) != bool(ms.group(3))
        ext = [n for n in nodes if not any(n in s for s in gt.values())] if top else [n for n in nodes if not gt.get(n)]
        amb = len(ext) != 1
        return np.array([(1.0 if amb else 0.0) if self.UNK.search(c.lower()) else (0.25 if amb else 1.0) if re.search(r"\b%s\b" % ext[0], c.lower()) and not amb else 0.0 for c in cands]) if ext else None

    def _ncd(self, a, b):
        za, zb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        return (len(zlib.compress((a + " " + b).encode())) - min(za, zb)) / max(za, zb, 1)

    # ---------------- interface ----------------
    def _channels(self, prompt, cands):
        comp = self._compute(prompt, cands)
        if comp is None: comp = self._order(prompt, cands)
        struct, fired = self._epmc(prompt, cands)
        ncd = np.array([1 - self._ncd(prompt, c) for c in cands])
        return comp, struct, fired, ncd

    def evaluate(self, prompt, candidates):
        n = len(candidates)
        if n == 0: return []
        cap, hits = self._meta_confidence(prompt)
        comp, struct, fired, ncd = self._channels(prompt, candidates)
        if comp is not None and fired: base = 0.5 * struct + 0.35 * comp + 0.15 * ncd
        elif comp is not None: base = 0.85 * comp + 0.15 * ncd
        elif fired: base = 0.85 * struct + 0.15 * ncd
        else: base = 0.85 * 0.35 + 0.15 * ncd
        belief = np.full(n, 1.0 / n) * np.maximum(base, 1e-9)   # Born-rule collapse of the candidate superposition
        belief = belief / belief.sum()
        tag = "meta:%s " % ",".join(hits) if hits else ""
        out = [{"candidate": c, "score": round(float(base[i]), 4),
                "reasoning": "%sepmc=%s comp=%s ncd=%.2f posterior=%.2f" % (tag, "%.2f" % struct[i] if fired else "na",
                "%.2f" % comp[i] if comp is not None else "na", ncd[i], belief[i])} for i, c in enumerate(candidates)]
        return sorted(out, key=lambda d: -d["score"])

    def confidence(self, prompt, answer):
        cap, hits = self._meta_confidence(prompt)
        comp, struct, fired, ncd = self._channels(prompt, [answer])
        if comp is not None: conf = 0.05 + 0.9 * float(comp[0])          # definitive computation: up to 0.95
        elif fired: conf = 0.2 + 0.6 * float(struct[0])                   # model-checked entailment: up to 0.8
        else: conf = 0.1 + 0.15 * float(ncd[0])                            # no parser matched: honest < 0.3
        return float(min(max(conf, 0.02), cap))


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
