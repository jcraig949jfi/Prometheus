import zlib
import operator

"""
ReasoningTool: sparse predicate coding + variational free-energy scoring.

Mechanism.  A dictionary of regex atoms (CMP comparatives/orderings, COND
if-then, NEG, NUM) parses the prompt into a fact set that is closed under
transitivity (Floyd-Warshall on a boolean matrix), modus ponens / tollens
over conditionals, and arithmetic (PEMDAS, percent, modulo, Bayes, rate/work).
This closure P* is the generative model.  Each candidate is encoded as a
sparse atom vector and scored by free energy
    F = accuracy (contradictions/omissions vs P*) + lambda * unsupported atoms
      + small NCD tiebreak;   score = -F.
Judgment layer: _meta_confidence classifies the QUESTION (presupposition,
scope/pronoun ambiguity, false dichotomy, subjectivity, unanswerability) and
caps confidence at 0.25; hedging candidates are rewarded only when the
question itself is defective.  The NAS component degenerates to a memoised
parse cache plus a fixed, offline-searched config.
"""
import re, ast, zlib, operator
import numpy as np

NUM = r"-?\d+(?:\.\d+)?"
GT = r"taller|older|bigger|larger|faster|heavier|greater|higher|longer|stronger|richer|more|better"
LT = r"shorter|smaller|younger|slower|lighter|lower|weaker|poorer|less|worse"
SUP_HI = r"tallest|oldest|biggest|largest|fastest|heaviest|greatest|highest|longest|strongest|richest|most|first|earliest"
SUP_LO = r"shortest|smallest|youngest|slowest|lightest|lowest|weakest|poorest|least|last|latest"
HEDGE = (r"cannot be determined|can't be determined|cannot be concluded|not enough|insufficient|ambiguous|depends|"
         r"unclear|neither|false (dilemma|dichotomy)|presuppos|loaded|other option|\bboth\b|unknown|no way to know|"
         r"impossible to (say|know|tell)|not necessarily|does not follow|doesn't follow|does not (prove|mean|imply)|"
         r"doesn't (prove|mean|imply)|survivorship|sunk cost|irrelevant|regression|regress|luck|coincidence|"
         r"premise|conclusion|need more|more information|which one|could be either|not specified")
STOP = set("the a an is are was were it then if that this will be does do did not no never has have had to of in and "
           "or so he she they gets get goes go there their his her its".split())
META = [
    (r"\b(have|has|had|did|do|does|will) (you|he|she|they|it|we|people|[a-z]+) (finally |ever |really )?"
     r"(stop|stopped|quit|cease|ceased|give up|given up|still|continue)\b", "presupposition"),
    (r"\bwhy (did|does|do|has|have|is|are|was|were) [^.?]*\b(fail|stop|quit|cheat|lie|refuse|hate|steal|always|never)",
     "presupposition"),
    (r"\b(still|anymore|any more|no longer)\b[^.?]*\?", "presupposition"),
    (r"\b(every|each|all)\b [^.?]*\b(a|an|one|some)\b.*\b(same|different|how many|single|one particular)", "scope"),
    (r"survivorship|survived|survivors|successful (people|companies|founders|traders|investors)|sunk cost|"
     r"already (spent|invested|paid|put in)|regression to the mean|regress|revert|\bvalid\b|\bsound\b|"
     r"stronger argument|weaker argument|persuasive|convincing|intend|meant to|on purpose|deceiv|bluff|\blied?\b|"
     r"\blying\b|mislead|strateg", "unanswerable"),
]


class ReasoningTool:
    def __init__(self):
        self.cfg = {"lam": 0.3, "ncd_w": 0.12, "tol": 0.02}   # offline-searched config (the "NAS" result)
        self.cache = {}                                         # weight sharing = memoised parse

    @staticmethod
    def _sents(t):
        return [s.strip() for s in re.split(r"(?<=[.!?;])\s+|\n", t) if s.strip()]

    @staticmethod
    def _words(s):
        return {re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w for w in re.findall(r"[a-z]+", s)} - STOP

    @staticmethod
    def _ov(a, b):
        return len(a & b) >= max(1, -(-len(b) // 2))

    def _close(self, a, b):
        return abs(a - b) <= self.cfg["tol"] * max(1.0, abs(b))

    @staticmethod
    def _ncd(a, b):
        za, zb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        return (len(zlib.compress((a + b).encode())) - min(za, zb)) / max(za, zb, 1)

    @staticmethod
    def _arith(expr):
        ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
               ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}
        def ev(n):
            if isinstance(n, ast.Constant): return float(n.value)
            if isinstance(n, ast.BinOp): return ops[type(n.op)](ev(n.left), ev(n.right))
            if isinstance(n, ast.UnaryOp): return ops[type(n.op)](ev(n.operand))
            raise ValueError("bad node")
        try:
            return ev(ast.parse(re.sub(r"\bx\b", "*", expr).replace("^", "**").strip(), mode="eval").body)
        except Exception:
            return None

    def _parse(self, text):
        if text in self.cache: return self.cache[text]
        low = text.lower(); F = {"cmp": [], "cond": [], "neg": [], "pos": [], "names": set()}
        for a, w, b in re.findall(r"\b([a-z]+) (?:is|was|are|were|runs|ran) (?:much |slightly |a bit )?(%s|%s) than ([a-z]+)"
                                  % (GT, LT), low):
            F["cmp"].append((a, b) if re.fullmatch(GT, w) else (b, a))
        for a, w, b in re.findall(r"\b([a-z]+) (?:came|arrived|finished|was born|left|happened|occurred|comes|goes|is) "
                                  r"(?:just |right )?(before|after) ([a-z]+)", low):
            F["cmp"].append((a, b) if w == "before" else (b, a))
        for a, b in F["cmp"]: F["names"].update([a, b])
        for p, q in re.findall(r"\bif (.+?)(?:, then|,| then) (.+?)(?:[.?;]|$)", low):
            F["cond"].append((self._words(p), self._words(q)))
        for s in self._sents(low):
            if s.startswith("if") or "?" in s: continue
            F["neg" if re.search(r"\b(not|no|never|none|neither|nobody|nothing)\b|n't", s) else "pos"].append(self._words(s))
        self.cache[text] = F; return F

    def _solve(self, text, F):
        low = text.lower().replace(",", ""); S = {}; sents = self._sents(low)
        qs = [s for s in sents if "?" in s]; q = qs[-1] if qs else (sents[-1] if sents else "")
        nums = [float(x) for x in re.findall(NUM, low)]
        pct = [float(x) / 100 for x in re.findall(r"(%s)\s*(?:%%|percent)" % NUM, low)]
        m = re.search(r"(%s)\s*(?:%%|percent) of (%s)" % (NUM, NUM), low)
        m2 = re.search(r"(?:remainder|left over) when (\d+) is divided by (\d+)|(\d+) mod(?:ulo)? (\d+)", low)
        m3 = re.search(r"in (%s) (?:hours?|minutes?|days?).*?in (%s) (?:hours?|minutes?|days?).*?together" % (NUM, NUM), low)
        m4 = re.search(r"[\d(][\d.\s()]*(?:[+\-*/^]|\bx\b)[\d.\s+\-*/^()x]*[\d)]", low)
        m5 = re.search(r"\b(%s|%s)\b" % (GT, LT), q)
        if m: S["num"] = float(m.group(1)) / 100 * float(m.group(2))
        elif m2:
            a, b = [g for g in m2.groups() if g]; S["num"] = int(a) % int(b)
        elif len(pct) >= 3 and re.search(r"false positive|test", low) and re.search(r"prevalence|base rate|population|actually|really", low):
            p, s, f = pct[:3]; post = p * s / (p * s + (1 - p) * f); S["num"], S["alt"] = post * 100, post
        elif m3:
            a, b = float(m3.group(1)), float(m3.group(2)); S["num"] = a * b / (a + b)
        elif m4 and re.search(r"what is|calculate|compute|evaluate|equals|=\s*\?|result|value of", low) \
                and self._arith(m4.group(0)) is not None:
            S["num"] = self._arith(m4.group(0))
        elif m5 and len(nums) >= 2 and not F["cmp"]:
            S["num"] = max(nums[-2:]) if re.fullmatch(GT, m5.group(1)) else min(nums[-2:])
        names = sorted(F["names"])
        if names:  # transitive closure over CMP/ORD atoms
            idx = {x: i for i, x in enumerate(names)}; n = len(names); R = np.zeros((n, n), bool)
            for a, b in F["cmp"]: R[idx[a], idx[b]] = True
            for k in range(n): R |= R[:, k:k + 1] & R[k:k + 1, :]
            S["reach"], S["idx"] = R, idx
            hi, lo = re.search(r"\b(%s)\b" % SUP_HI, q), re.search(r"\b(%s)\b" % SUP_LO, q)
            if hi or lo:
                w = [x for x in names if (R[idx[x]] if hi else R[:, idx[x]]).sum() == n - 1]
                if len(w) == 1: S["name"] = w[0]
                else: S["undet"] = True
            mq = re.search(r"\b(?:is|was) ([a-z]+) (%s|%s) than ([a-z]+)" % (GT, LT), q)
            if mq and mq.group(1) in idx and mq.group(3) in idx:
                a, b = (idx[mq.group(1)], idx[mq.group(3)]) if re.fullmatch(GT, mq.group(2)) else (idx[mq.group(3)], idx[mq.group(1)])
                if R[a, b]: S["polarity"] = "yes"
                elif R[b, a]: S["polarity"] = "no"
                else: S["undet"] = True
        qw = self._words(q)
        for p, c in F["cond"]:  # modus tollens / ponens; affirming consequent + denying antecedent -> undetermined
            negq, negp = any(self._ov(s, c) for s in F["neg"]), any(self._ov(s, p) for s in F["neg"])
            posp, posq = any(self._ov(s, p) for s in F["pos"]), any(self._ov(s, c) for s in F["pos"])
            if negq and self._ov(qw, p): S["polarity"] = "no"
            elif posp and self._ov(qw, c): S["polarity"] = "yes"
            elif (posq and self._ov(qw, p)) or (negp and self._ov(qw, c)): S["undet"] = True
        return S

    def _F(self, prompt, cand, F, S, tags):
        c = cand.lower().replace(",", ""); Fc = self._parse(cand); det = any(k in S for k in ("num", "name", "polarity"))
        cn = [float(x) for x in re.findall(NUM, c)]; hedge = bool(re.search(HEDGE, c))
        err, grd, atoms = 0.0, 0, len(cn) + len(Fc["cmp"])
        if "num" in S:
            if any(self._close(v, S["num"]) or self._close(v, S.get("alt", S["num"])) for v in cn): grd += 1
            else: err += 2.0
        if "name" in S:
            if re.search(r"\b%s\b" % S["name"], c): grd += 1
            else: err += 2.0
        if "polarity" in S:
            pc = None if hedge else ("no" if re.search(r"^\W*(no|false|incorrect)\b|\bnot\b|n't|\bcannot\b|\bnever\b", c) else "yes")
            if pc == S["polarity"]: grd += 1
            else: err += 1.0 if pc is None else 2.0
        if "undet" in S:
            if hedge: grd += 1
            else: err += 2.0
        elif hedge and det: err += 1.0
        if tags: err += -1.5 if hedge else 1.0          # judgment term: defective question rewards hedging
        for a, b in Fc["cmp"]:
            if "idx" in S and a in S["idx"] and b in S["idx"]:
                if S["reach"][S["idx"][a], S["idx"][b]]: grd += 1
                elif S["reach"][S["idx"][b], S["idx"][a]]: err += 1.5
        comp = self.cfg["lam"] * max(0, atoms - grd)     # KL-to-prior: unsupported atoms
        return err + comp + self.cfg["ncd_w"] * self._ncd(prompt, cand)

    def _meta_tags(self, prompt):
        low = prompt.lower(); F = self._parse(prompt); nn = len(re.findall(NUM, low))
        tags = [t for rx, t in META if re.search(rx, low, re.S)]
        if re.search(r"\beither\b[^.?]*\bor\b", low) and not re.search(r"\bnot\b|n't|\bno\b", low): tags.append("false_dichotomy")
        if re.search(r"\b(told|said to|asked|informed|reminded|thanked|called|warned) \w+ (that )?(he|she|they|his|her|their)\b", low) \
                and re.search(r"\bwho(m|se)?\b", low): tags.append("pronoun")
        if re.search(r"\b(best|worst|favou?rite|greatest|most beautiful|nicest|coolest|prettiest|tastiest|most interesting)\b", low) \
                and not F["cmp"] and nn < 2: tags.append("subjectivity")
        if re.search(r"\bhow (many|much|old|tall|far|long|heavy)\b", low) and nn == 0: tags.append("unanswerable")
        return sorted(set(tags))

    def _meta_confidence(self, prompt):
        return 0.25 if self._meta_tags(prompt) else 1.0

    def evaluate(self, prompt, candidates):
        F = self._parse(prompt); S = self._solve(prompt, F); tags = self._meta_tags(prompt)
        info = {k: v for k, v in S.items() if k not in ("reach", "idx")}; out = []
        for cand in candidates:
            f = self._F(prompt, cand, F, S, tags)
            out.append({"candidate": cand, "score": round(-f, 4),
                        "reasoning": "solved=%s meta=%s free_energy=%.3f" % (info, tags, f)})
        return sorted(out, key=lambda d: -d["score"])

    def confidence(self, prompt, answer):
        F = self._parse(prompt); S = self._solve(prompt, F); tags = self._meta_tags(prompt)
        f = max(self._F(prompt, answer, F, S, tags), 0.0)
        det = any(k in S for k in ("num", "name", "polarity", "undet"))
        base = (0.88 if det else 0.28) * float(np.exp(-f))   # no parser fired -> stays below 0.3
        return float(np.clip(min(base, self._meta_confidence(prompt)), 0.02, 0.9))


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
