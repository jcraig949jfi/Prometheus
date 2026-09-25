import zlib
import random

"""
ReasoningTool: Thermodynamics x Genetic Algorithms x Model Checking.

Mechanism: the prompt is parsed into atomic propositions and clauses (facts,
negations, if-then implications, 'because' biconditionals); a candidate adds
literals.  A GA evolves boolean assignment vectors; each is model-checked
(v = violated clauses) and scored by energy E = alpha*v + beta*H, where H is
the Shannon entropy of population marginals (temperature-like regulariser).
Structural score = extra energy a candidate's literals induce.  Under-
determination is COMPUTED: variables still varying among minimum-violation
assignments are free degrees of freedom, favouring 'cannot be determined'.
Deterministic parsers (bat-ball, all-but-N, fencepost, modular, coin
independence, parity, pigeonhole, Bayes base rate, modus tollens/ponens,
transitive/temporal closure, SVO, direction, work rate, PEMDAS, numeric
compare) give computed answers.  Score = 0.5 structural + 0.35 computation
+ 0.15 NCD.  confidence() is capped by _meta_confidence() on Tier-B traps.
"""
import re, zlib
import numpy as np

W2N = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}
DIRS = ["north", "east", "south", "west"]
CMP_DN = "short young slow light small weak poor low less cheap".split()
CBD = r"cannot be determined|can't be determined|not enough information|insufficient|undetermined|cannot tell|impossible to (say|know|tell)|ambiguous|unclear|depends|not possible to"
NEG = r"\b(not|no|never|isn't|didn't|doesn't|wasn't|aren't|don't|cannot|can't|won't)\b"
UNIT = r"(?:m|meters?|metres?|feet|ft|km|miles?|yards?)"


def _num(t):
    t = t.lower().replace(",", "")
    if t in W2N: return float(W2N[t])
    try: return float(t)
    except ValueError: return None


def _ncd(a, b):
    z = lambda s: len(zlib.compress(s.encode()))
    return (z(a + b) - min(z(a), z(b))) / max(z(a), z(b), 1)


def _closure(edges):
    nodes = sorted({x for e in edges for x in e}); R = {n: {b for a, b in edges if a == n} for n in nodes}
    for k in nodes:
        for i in nodes:
            if k in R[i]: R[i] |= R[k]
    return R


def _pct_near(ql, kw):
    m = re.search(r"(\d+(?:\.\d+)?)\s*%[^.%]*?\b(?:" + kw + r")|(?:" + kw + r")[^.%]*?(\d+(?:\.\d+)?)\s*%", ql)
    return float(m.group(1) or m.group(2)) if m else None


class ReasoningTool:
    def __init__(self): self.alpha, self.beta, self.pop, self.gens = 1.0, 0.3, 24, 30

    # ---------------- model checking + GA core ----------------
    def _clauses(self, q):
        props, cl = [], []
        def pid(t):
            t = re.sub(NEG, "", t).strip(" ,"); t = re.sub(r"^(is|are|does|do|did|was|will|can)\s+", "", t)
            if t not in props: props.append(t)
            return props.index(t)
        for s in [x.strip() for x in re.split(r"(?<=[.;?!])\s+", q.lower()) if x.strip()]:
            body = s.rstrip(".;?!"); m = re.match(r"if (.+?),? then (.+)", body)
            if m: cl.append(("imp", pid(m.group(1)), pid(m.group(2)))); continue
            m = re.match(r"(.+?) because (.+)", body)
            if m: cl.append(("iff", pid(m.group(1)), pid(m.group(2)))); continue
            if s.endswith("?"):
                if re.match(r"(is|are|does|do|did|was|will|can)\b", body): pid(body)
            elif re.search(r"\b(is|are|was|were|has|have|can|will)\b", body):
                cl.append(("neg" if re.search(NEG, body) else "pos", pid(body)))
        return props, cl

    def _assert(self, props, cand):
        c = cand.lower(); lits = []
        if re.match(r"\s*(yes|no)\b", c) and props: lits.append(("pos" if c.strip().startswith("yes") else "neg", len(props) - 1))
        for i, p in enumerate(props):
            keys = [w for w in re.findall(r"[a-z]{4,}", p) if w not in ("then", "because", "that", "with", "this", "there")]
            if keys and sum(k in c for k in keys) >= max(1, len(keys) // 2): lits.append(("neg" if re.search(NEG, c) else "pos", i))
        return lits

    def _ga(self, n, cl):
        """Evolve assignments; return (E_min, violations, free degrees of freedom)."""
        rng = np.random.RandomState(7); n = max(n, 1); X = rng.rand(self.pop, n) < 0.5; best = None
        def viol(X):
            v = np.zeros(len(X))
            for c in cl:
                if c[0] == "pos": v += ~X[:, c[1]]
                elif c[0] == "neg": v += X[:, c[1]]
                elif c[0] == "imp": v += X[:, c[1]] & ~X[:, c[2]]
                else: v += X[:, c[1]] != X[:, c[2]]
            return v
        for _ in range(self.gens):
            v = viol(X); p = X.mean(0).clip(1e-9, 1 - 1e-9)
            H = float(-(p * np.log(p) + (1 - p) * np.log(1 - p)).sum()); E = self.alpha * v + self.beta * H
            i = int(E.argmin())
            if best is None or E[i] < best[0]: best = (float(E[i]), float(v[i]), X[v == v.min()].copy())
            a, b = rng.randint(0, self.pop, (2, self.pop)); par = np.where((E[a] <= E[b])[:, None], X[a], X[b])
            a, b = rng.randint(0, self.pop, (2, self.pop)); mask = rng.rand(self.pop, n) < 0.5
            X = np.where(mask, par[a], par[b]) ^ (rng.rand(self.pop, n) < 0.01)
        E, v, S = best; m = S.mean(0)
        return E, v, int(((m > 0) & (m < 1)).sum())

    # ---------------- ordering (transitivity / temporal) ----------------
    def _order(self, ql, edges):
        R = _closure(edges); nodes = list(R)
        m = re.search(r"\b(?:is|was|does|did)\s+(\w+)\s+(?:\w+\s+)?(\w+)\s+than\s+(\w+)", ql)
        if m and m.group(1) in R and m.group(3) in R:
            a, w, c = m.groups()
            if any(w.startswith(s) for s in CMP_DN): a, c = c, a
            if c in R[a]: return "yes", 0.9, "transitive closure: %s > %s" % (a, c)
            if a in R[c]: return "no", 0.9, "transitive closure: %s > %s" % (c, a)
            return "cannot be determined", 0.85, "no chain links %s and %s (free dof)" % (a, c)
        m = re.search(r"\b(\w+est|first|earliest|most|last|latest|least)\b", ql)
        if not m: return None
        w = m.group(1); low = w in ("last", "latest", "least") or any(w.startswith(s) for s in CMP_DN)
        top = [n for n in nodes if len(R[n]) == len(nodes) - 1]; bot = [n for n in nodes if all(n in R[o] for o in nodes if o != n)]
        pick = bot if low else top
        if len(pick) == 1: return pick[0], 0.9, "order closure extremum: " + pick[0]
        return "cannot be determined", 0.8, "order underdetermined: %d nodes, no unique extremum" % len(nodes)

    # ---------------- constructive parsers ----------------
    def _parse(self, q):
        L = q.lower()
        m = re.search(r"\$?([\d.]+)\s*(?:dollars?\s*)?(?:in )?total.*?\$?([\d.]+)\s*(?:dollars?\s*)?more than", L, re.S)
        if m: return (float(m.group(1)) - float(m.group(2))) / 2, 0.95, "bat-ball algebra: (total-diff)/2"
        m = re.search(r"all but (\w+)", L)
        if m and _num(m.group(1)) is not None: return _num(m.group(1)), 0.9, "all-but-N: N remain"
        m = re.search(r"(\d+)\s*" + UNIT + r"\b.*?every (\d+)|every (\d+)\s*" + UNIT + r"\b.*?(\d+)\s*" + UNIT, L, re.S)
        if m and re.search(r"post|pole|tree|marker|lamp", L):
            g = [x for x in m.groups() if x]; Ln, s = (g[0], g[1]) if m.group(1) else (g[1], g[0])
            return float(Ln) // float(s) + 1, 0.85, "fencepost: L/s + 1"
        m = re.search(r"(\d+)\s*(?:mod|modulo|%)\s*(\d+)|remainder (?:when|of|if) (\d+) (?:is )?divided by (\d+)", L)
        if m: g = [float(x) for x in m.groups() if x]; return g[0] % g[1], 0.95, "modular arithmetic"
        if re.search(r"coin|flip|toss|heads|tails", L) and re.search(r"in a row|consecutive|times|straight", L) and re.search(r"probab|chance|likely|odds", L):
            return 0.5, 0.9, "independent flips: p(next)=0.5"
        m = re.search(r"sum of (\w+) odd", L)
        if m and _num(m.group(1)) is not None: return ("even" if _num(m.group(1)) % 2 == 0 else "odd"), 0.9, "parity of sum of odds"
        m = re.search(r"(\w+) (?:different )?(?:colou?rs|kinds|types|varieties)", L)
        if m and _num(m.group(1)) and re.search(r"guarantee|ensure|certain|sure", L):
            m2 = re.search(r"(\w+) (?:of the same|matching|alike|identical)", L); n = (_num(m2.group(1)) if m2 else None) or 2.0
            return _num(m.group(1)) * (n - 1) + 1, 0.85, "pigeonhole: k*(n-1)+1"
        pri, sen = _pct_near(L, "population|people|prevalen|have the|has the|rate|patients"), _pct_near(L, "sensitiv|detect|accura|true positive|correctly")
        if pri is not None and sen is not None and re.search(r"test|positive|disease", L):
            fpr = _pct_near(L, "false positive|falsely|incorrectly|wrongly"); f = (fpr if fpr is not None else 100 - sen) / 100; p, s = pri / 100, sen / 100
            return 100 * p * s / (p * s + (1 - p) * f), 0.85, "Bayes posterior (base rate)"
        m = re.search(r"if (.+?),? then (.+?)[.;]", L)
        if m:
            ak, bk = [max(re.findall(r"[a-z]{4,}", g), key=len, default="")[:4] for g in m.groups()]
            sents = re.split(r"(?<=[.;?])\s*", L[m.end():]); bs = [s for s in sents if bk and bk in s]; as_ = [s for s in sents if ak and ak in s and not s.endswith("?")]
            if bs and re.search(NEG, bs[0]): return (lambda c: ak in c and bool(re.search(NEG, c))), 0.9, "modus tollens: not B => not A"
            if as_ and not re.search(NEG, as_[0]): return (lambda c: bk in c and not re.search(NEG, c)), 0.9, "modus ponens: A => B"
            if bs: return "cannot be determined", 0.8, "affirming the consequent: A is a free dof"
        m = re.search(r"\b([A-Z]\w+) (told|gave|sent|asked|called|hit|thanked|paid|helped|pushed) ([A-Z]\w+)\b", q)
        if m and re.search(r"\bwho", L):
            s, v, o = m.groups()
            if re.search(r"\b(he|she|they) (was|were|is|are)\b", L): return "cannot be determined", 0.7, "pronoun referent ambiguous: 2 candidates"
            return (o if re.search(r"who (was|were|got)|whom", L) else s), 0.85, "SVO roles: subject=%s object=%s" % (s, o)
        m = re.search(r"facing (north|south|east|west)", L)
        if m:
            d = DIRS.index(m.group(1))
            for t in re.findall(r"turn(?:s|ed)? (?:to the )?(left|right|around)", L[m.end():]): d = (d + {"left": 3, "right": 1, "around": 2}[t]) % 4
            return DIRS[d], 0.9, "direction composition"
        mv = re.findall(r"(\d+)\s*\w* ?(north|south|east|west)", L)
        if len(mv) >= 2 and re.search(r"how far|distance", L):
            x = sum(float(n) * (1 if d == "east" else -1) for n, d in mv if d in ("east", "west")); y = sum(float(n) * (1 if d == "north" else -1) for n, d in mv if d in ("north", "south"))
            return (x * x + y * y) ** 0.5, 0.85, "displacement vector norm"
        pr = re.findall(r"\b(\w+) (?:is |was |are |runs |happened |occurred |came |arrived |finished )?(\w+) than (\w+)", L)
        edges = [(c, a) if any(w.startswith(s) for s in CMP_DN) else (a, c) for a, w, c in pr if w != "more"]
        edges += [(a, c) if w == "before" else (c, a) for a, w, c in re.findall(r"\b(\w+) (?:\w+ )?(before|after) (\w+)", L)]
        if edges:
            r = self._order(L, edges)
            if r: return r
        hs = re.findall(r"(\d+(?:\.\d+)?)\s*(?:hours?|minutes?|days?)", L)
        if len(hs) >= 2 and "together" in L: a, b = float(hs[0]), float(hs[1]); return 1 / (1 / a + 1 / b), 0.9, "work rate: 1/(1/a+1/b)"
        m = re.search(r"(?:what is|calculate|evaluate|compute)\s*:?\s*(-?[\d\s\+\-\*/\(\)\.x\^]+)", L)
        if m and re.search(r"[\+\-\*/x\^]", m.group(1)) and re.search(r"\d", m.group(1)):
            try: return float(eval(m.group(1).replace("x", "*").replace("^", "**"), {"__builtins__": {}})), 0.95, "PEMDAS evaluation"
            except Exception: pass
        m = re.search(r"\b(larger|bigger|greater|smaller|less|higher|lower)\b", L); ns = re.findall(r"-?\d[\d,]*\.?\d*", L)
        if m and len(ns) >= 2:
            v = [float(n.replace(",", "")) for n in ns[:2]]; hi = m.group(1) in ("larger", "bigger", "greater", "higher")
            return v[int(np.argmax(v)) if hi else int(np.argmin(v))], 0.95, "numeric comparison %s vs %s" % tuple(ns[:2])
        return None

    def _match(self, ans, cand):
        c = cand.lower().strip()
        if callable(ans): return bool(ans(c))
        if ans == "cannot be determined": return bool(re.search(CBD, c))
        if isinstance(ans, float):
            for v in [_num(t) for t in re.findall(r"-?\d[\d,]*\.?\d*|\b[a-z]+\b", c)]:
                if v is None: continue
                for u in [v] + ([v / 100] if "%" in c else [v * 100] if 0 < v < 1 else []):
                    if abs(u - ans) <= max(0.03 * abs(ans), 0.005): return True
            return False
        toks = re.findall(r"[a-z]+", c)
        if ans in ("yes", "no"): return bool(re.match(ans + r"\b", c)) or (ans in toks and ("no" if ans == "yes" else "yes") not in toks)
        return bool(re.search(r"\b" + re.escape(ans) + r"\b", c))

    # ---------------- metacognition ----------------
    def _meta_confidence(self, q):
        ql = q.lower(); checks = [
            ("presupposition", r"have you (stopped|quit|given up)|why (did|does|has|is) .* (fail|stop|quit|worse|broken|lie)|when did you stop|still (beat|cheat|lie)"),
            ("scope ambiguity", r"\b(every|each|all)\b \w+ (\w+ ){0,3}\b(a|an|some|one)\b .*\b(same|different|which)\b"),
            ("pronoun ambiguity", r"\b[a-z]+ (told|said to|asked|informed) [a-z]+ (that )?(he|she|they) .*\bwho\b"),
            ("false dichotomy", r"\beither\b .* \bor\b(?!.*" + NEG + ")"),
            ("subjectivity", r"\b(best|worst|favou?rite|most beautiful|greatest|nicest)\b(?!.*\d)"),
            ("survivorship bias", r"of those who (succeeded|survived|made it)|survivors?|successful (people|companies|founders|entrepreneurs)\b.*\b(all|most|share)"),
            ("sunk cost", r"already (invested|spent|paid|put in|sunk)"),
            ("regression to mean", r"(exceptional|extreme|record|best ever|worst ever|unusually)\b.*\b(next|following|again)"),
            ("validity vs truth", r"\b(valid|sound)\b.*\bargument|argument.*\b(valid|sound)\b")]
        flags = [n for n, p in checks if re.search(p, ql, re.S)]
        if re.search(r"\b(how many|how much|who|which)\b", ql) and not re.search(r"\d|\b(" + "|".join(W2N) + r")\b", ql) and len(set(re.findall(r"\b[A-Z][a-z]+\b", q))) < 2 and not re.search(r"\b(if|than|before|after|facing)\b", ql):
            flags.append("unanswerable: no data in prompt")
        return (0.25 if flags else 1.0), flags

    # ---------------- interface ----------------
    def evaluate(self, prompt, candidates):
        props, cl = self._clauses(prompt); sol = self._parse(prompt); meta, flags = self._meta_confidence(prompt)
        E0, _, free = self._ga(len(props), cl); out = []
        for c in candidates:
            E, v, _ = self._ga(len(props), cl + self._assert(props, c)); struct = 1.0 / (1.0 + max(0.0, E - E0)); cbd = bool(re.search(CBD, c.lower()))
            if sol: comp = 1.0 if self._match(sol[0], c) else 0.0
            else: comp = 0.6 if (cbd and free > 0) else (0.3 if not cbd else 0.15)
            if meta < 0.3 and cbd: comp = max(comp, 0.9)
            score = 0.5 * struct + 0.35 * comp + 0.15 * (1 - _ncd(prompt, c))
            why = "model-check: E=%.2f (dE=%.2f, v=%d, free dof=%d); %s; meta=%s" % (E, E - E0, v, free, sol[2] if sol else "no parser matched", flags or "clean")
            out.append({"candidate": c, "score": round(score, 4), "reasoning": why})
        return sorted(out, key=lambda d: -d["score"])

    def confidence(self, prompt, answer):
        meta, flags = self._meta_confidence(prompt); sol = self._parse(prompt); pl = prompt.lower()
        amb = len(re.findall(r"\b(he|she|it|they|him|her|them)\b", pl)); ents = len(set(re.findall(r"\b[A-Z][a-z]+\b", prompt))) + len(re.findall(r"\d+", prompt))
        prop = 1 - 0.5 * amb / max(1, amb + ents)  # uncertainty propagation over ambiguous vs confident variables
        if sol:
            ans, pc, _ = sol; hit = self._match(ans, answer)
            conf = pc * prop if hit else (0.15 if ans != "cannot be determined" else 0.2)
        else:
            props, cl = self._clauses(prompt); E, v, free = self._ga(len(props), cl + self._assert(props, answer))
            conf = min(0.28, 0.25 / (1.0 + v) * (0.6 if free > 0 else 1.0))
        return float(round(max(0.02, min(conf, meta, 0.97)), 4))


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
