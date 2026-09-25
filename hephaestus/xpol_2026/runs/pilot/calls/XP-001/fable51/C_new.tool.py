import zlib

"""ReasoningTool: bounded model checker over a packed-ambiguity proposition
lattice with Hebbian edge reweighting.

Mechanism: (1) regex-extract propositions from the prompt (order relations,
conditionals / universals, negated facts, numeric slots) and claims from each
candidate; (2) expand a depth-bounded closure: transitivity over orderings,
modus ponens / modus tollens with subset-unification over conditionals, direct
arithmetic (PEMDAS, modular, percent, work-rate, Bayes) on numeric slots;
(3) "measure" every claim against the closure -> verified / refuted (hard
penalty) / unresolved, with an entropy penalty for spans no constraint
disambiguates (pronouns); (4) a Hebbian co-occurrence matrix over claim
predicates across the candidate set is a tie-breaker prior; (5) confidence is
driven by QUESTION properties: _meta_confidence caps it on presupposition,
scope / pronoun ambiguity, false dichotomy, subjectivity, judgment traps and
unanswerability.  Score = 0.50 structural + 0.25 computation + 0.10 Hebbian
+ 0.15 NCD - mu * entropy.
"""
import re, zlib, ast, operator as op
import numpy as np

GT = set("taller older bigger larger greater heavier faster higher longer more stronger richer wider better above after later".split())
LT = set("shorter younger smaller less lighter slower lower fewer weaker poorer narrower worse below before earlier".split())
MINW = set("shortest youngest smallest least lightest slowest lowest fewest weakest poorest worst first earliest".split())
STOP = set("the a an is are was were than and that this of to in on if then it he she they them we you i his her their be been do does did can could will would must may might true false follow conclude whether so therefore".split())
NEG = r"\b(not|no|never|cannot|isn't|doesn't|didn't|won't|aren't|don't)\b|n't\b"
NUM = r"-?\d+(?:\.\d+)?"
OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg}
META = [
    ("presupposition", r"\b(have|has|had|did) \w+ (stopped|quit|given up|ceased|finally|still)\b|\bwhy (did|does|do|is|are|has|have)\b[^?]*\b(fail|stop|quit|refuse|hate|lie|cheat|always|never)\b|\bhow many times\b|\bstill\b[^.]*\?", re.I),
    ("scope ambiguity", r"\b(every|each|all)\b[^.?]{1,60}\b(a|an|one)\b[^?]*\b(same|different|how many)\b", re.I),
    ("pronoun ambiguity", r"\b[A-Z][a-z]+\b[^.?]*\b(told|said to|asked|called|met|thanked|saw|warned|hit|visited|gave)\b[^.?]*\b[A-Z][a-z]+\b[^.?]*\b(he|she|him|her|his|they|their)\b[\s\S]*\b(who|whom|whose)\b", 0),
    ("false dichotomy", r"\beither\b[^?]*\bor\b|\bonly (two|2) (options|choices|ways)|\bmust (choose|pick)\b|\bif (you'?re|you are) not\b", re.I),
    ("subjectivity", r"\b(best|worst|favou?rite|most (beautiful|interesting|important|fun))\b(?! (answer|estimate|approximation))|\b(should|ought to)\b", re.I),
    ("judgment trap", r"\b(sunk cost|already (spent|invested|paid)|regress(ion)? to|survivor(ship)?|came back|returned (planes|ships)|argument (is )?(strong|weak|persuasive|convincing)|strongest|weakest|persuasive|intend(ed|s|ing)?|intention|deceiv|bluff|lying|strateg|how (sure|certain|confident))\b|\bvalid\b[^?]*\b(true|sound)\b|\b(true|sound)\b[^?]*\bvalid", re.I),
    ("unanswerable", r"\b(cannot be determined|not enough information|insufficient|what (is|was) (my|his|her|their) (name|age|favorite|birthday)|how (old|tall) (am|is) (i|my))\b", re.I),
]


class ReasoningTool:
    def __init__(self, lam=0.5, mu=0.05):
        self.lam, self.mu = lam, mu

    # ---------------- question-level judgment ----------------
    def _meta_confidence(self, prompt):
        hits = [n for n, rx, fl in META if re.search(rx, prompt, fl)]
        if "subjectivity" in hits and self._orders(prompt): hits.remove("subjectivity")
        sents = self._sents(prompt)
        body = " ".join(s for s in sents if not s.endswith("?")); q = " ".join(s for s in sents if s.endswith("?"))
        if q and body:
            if re.search(r"how (many|much|old|tall|far|long)", q, re.I) and not re.search(r"\d", body) and not self._orders(body): hits.append("unanswerable")
            if any(n not in body for n in re.findall(r"\b[A-Z][a-z]+\b", q)[1:]): hits.append("unanswerable")
        hits = sorted(set(hits))
        return (0.22 if hits else 1.0), hits

    # ---------------- parsing ----------------
    @staticmethod
    def _sents(t): return [s.strip() for s in re.split(r"(?<=[.;?!])\s+", t.strip()) if s.strip()]

    @staticmethod
    def _key(s):
        return frozenset(w[:-1] if len(w) > 3 and w.endswith("s") else w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP)

    def _prop(self, s):
        neg = re.search(NEG, s.lower()) is not None
        k = self._key(re.sub(NEG, " ", s.lower()))
        return (k, not neg) if k else None

    def _orders(self, text):  # (a, b) means a > b (bigger / later)
        out = []
        for a, mid, w, b in re.findall(r"\b([A-Z][a-z]+)\b([^.,;?]{0,25}?)\b(\w+ than|before|after)\s+(?:the )?([A-Z][a-z]+)\b", text):
            w = w.split()[0]
            rel = ">" if (w in GT or (w.endswith("er") and w not in LT) or " more " in mid) else "<"
            if w in LT or " less " in mid or " fewer " in mid: rel = "<"
            out.append((a, b) if rel == ">" else (b, a))
        return out

    @staticmethod
    def _super(q):
        m = re.search(r"\b(\w+est|most|least|first|last)\b", q.lower())
        if not m: return None
        w = m.group(1)
        return "min" if (w in MINW) else "max"

    def _rules_facts(self, sents):
        rules, facts, q = [], set(), ""
        for s in sents:
            if s.endswith("?"): q = s; continue
            m = (re.match(r"(?i)if (.+?),? then (.+)", s) or re.match(r"(?i)if (.+?), (.+)", s) or re.match(r"(?i)(?:all|every) (\w+) (?:are|is) (.+)", s))
            if m:
                p, c = self._prop(m.group(1)), self._prop(m.group(2))
                if p and c: rules.append((p, c))
            elif len(s.split()) <= 14:
                p = self._prop(s)
                if p: facts.add(p)
        return rules, facts, q

    # ---------------- bounded closure (Kripke expansion) ----------------
    @staticmethod
    def _closure(edges, depth=6):
        gt = {}
        for a, b in edges: gt.setdefault(a, set()).add(b)
        for _ in range(depth):
            new = False
            for a in list(gt):
                for b in list(gt[a]):
                    for c in gt.get(b, ()):
                        if c not in gt[a]: gt[a].add(c); new = True
            if not new: break
        return gt

    @staticmethod
    def _derive(rules, facts, depth=5):
        D = set(facts)
        for _ in range(depth):
            new = set()
            for (pk, pp), (ck, cp) in rules:
                for fk, fp in D:
                    if pk <= fk and fp == pp: new.add((frozenset((fk - pk) | ck), cp))          # modus ponens
                    if ck <= fk and fp != cp: new.add((frozenset((fk - ck) | pk), not pp))      # modus tollens
            if new <= D: break
            D |= new
        return D

    @staticmethod
    def _status(p, D):  # +1 derivable, -1 refuted, 0 open
        k, pol = p; res = 0
        for dk, dp in D:
            if k == dk or (min(len(k), len(dk)) >= 2 and (k <= dk or dk <= k)):
                if dp != pol: return -1
                res = 1
        return res

    # ---------------- computation ----------------
    def _ev(self, n):
        if isinstance(n, ast.Expression): return self._ev(n.body)
        if isinstance(n, ast.Constant): return float(n.value)
        if isinstance(n, ast.BinOp): return OPS[type(n.op)](self._ev(n.left), self._ev(n.right))
        if isinstance(n, ast.UnaryOp): return OPS[type(n.op)](self._ev(n.operand))
        raise ValueError("bad node")

    def _compute(self, prompt):
        t = prompt.lower().replace(",", "")
        nums = [float(x) for x in re.findall(NUM, t)]
        pct = [float(x) / 100 for x in re.findall(r"(\d+(?:\.\d+)?)\s*(?:%|percent)", t)]
        m = re.search(r"(%s)\s*(?:%%|percent) of (%s)" % (NUM, NUM), t)
        if m: return float(m.group(1)) / 100 * float(m.group(2)), "percent-of"
        m = re.search(r"remainder (?:when|of) (\d+) (?:is )?divided by (\d+)|(\d+)\s*(?:mod|modulo)\s*(\d+)", t)
        if m: g = [x for x in m.groups() if x]; return float(int(g[0]) % int(g[1])), "modular"
        m = re.search(r"(%s) (?:is )?(greater|larger|bigger|more|less|smaller|lower|higher) than (%s)" % (NUM, NUM), t)
        if m:
            a, b = float(m.group(1)), float(m.group(3))
            return float(a > b if m.group(2) in ("greater", "larger", "bigger", "more", "higher") else a < b), "numcmp"
        if len(pct) >= 3 and re.search(r"false positive|sensitivity|prevalence|base rate|prior", t):
            p, s, f = pct[:3]; return p * s / (p * s + (1 - p) * f + 1e-12), "bayes"
        if re.search(r"together|combined|both", t) and re.search(r"\b(hours?|minutes?|days?)\b", t) and len(nums) >= 2 and nums[0] > 0 and nums[1] > 0:
            return 1 / (1 / nums[0] + 1 / nums[1]), "work-rate"
        e = t
        for w, s in (("plus", "+"), ("minus", "-"), ("multiplied by", "*"), ("times", "*"), ("divided by", "/"), ("^", "**")): e = e.replace(w, s)
        e = re.sub(r"(?<=\d)\s*x\s*(?=\d)", "*", e)
        m = re.search(r"\(?-?\d[\d\.]*\)?(?:\s*(?:\*\*|[\+\-\*/%])\s*\(?-?\d[\d\.]*\)?)+", e)
        if m:
            try: return float(self._ev(ast.parse(m.group(0).strip(), mode="eval"))), "arithmetic"
            except Exception: pass
        m = re.search(r"\b(larger|bigger|greater|higher|more|largest|biggest|greatest|max\w*|smaller|less|lower|smallest|least|fewer|min\w*)\b", t)
        if m and len(nums) >= 2 and not self._orders(prompt):
            return (max(nums) if m.group(1)[:3] in ("lar", "big", "gre", "hig", "mor", "max") else min(nums)), "compare"
        return None

    @staticmethod
    def _comp_match(comp, cand):
        if not comp: return 0.5
        val, kind = comp; cl = cand.lower().strip()
        if kind == "numcmp":
            yes, no = re.match(r"(yes|true|correct)\b", cl), re.match(r"(no|false|incorrect)\b", cl)
            return 0.5 if not (yes or no) else (1.0 if bool(val) == bool(yes) else 0.0)
        cn = [float(x) for x in re.findall(NUM, cl.replace(",", ""))]
        if not cn: return 0.5
        alts = (val, val * 100, val / 100) if kind in ("bayes", "percent-of") else (val,)
        tol = 1e-6 if kind == "compare" else 0.01
        return 1.0 if any(abs(c - a) <= tol * max(1.0, abs(a)) for c in cn for a in alts) else 0.0

    # ---------------- measurement of claims ----------------
    def _claims(self, cand, qprop, qord, sup, gt, D):
        v = r = u = 0; tags = []; cl = cand.lower().strip()
        yes, no = re.match(r"(yes|true|correct|valid)\b", cl), re.match(r"(no|false|incorrect|invalid)\b", cl)
        und = re.search(r"cannot|can't|not enough|insufficient|undetermined|not necessarily|neither|unknown|no conclusion|not follow|impossible to", cl)
        def tally(s, mode):  # s: derivability; mode: +1 asserts, -1 denies, 0 says open
            nonlocal v, r, u
            if mode == 0: v, r = (v + 1, r) if s == 0 else (v, r + 1)
            elif s == 0: u += 1
            elif s == mode: v += 1
            else: r += 1
        def ostat(a, b): return 1 if b in gt.get(a, ()) else (-1 if a in gt.get(b, ()) else 0)
        for s in ([self._status(qprop, D)] if qprop else []) + ([ostat(*qord[0])] if qord else []):
            if und: tally(s, 0); tags.append("undet")
            elif yes: tally(s, 1); tags.append("yes")
            elif no: tally(s, -1); tags.append("no")
        for a, b in self._orders(cand): tally(ostat(a, b), 1); tags.append("gt")
        if sup and gt:
            nodes = set(gt) | {x for ss in gt.values() for x in ss}
            for n in re.findall(r"\b[A-Z][a-z]+\b", cand):
                if n not in nodes: continue
                above = {x for x in nodes if n in gt.get(x, ())}; below = gt.get(n, set())
                dom, beat = (below, above) if sup == "max" else (above, below)
                tally(1 if dom >= nodes - {n} else (-1 if beat else 0), 1); tags.append("sup")
        if D and not (yes or no or und):
            for s_ in self._sents(cand):
                p = self._prop(s_)
                if p and len(p[0]) >= 2: tally(self._status(p, D), 1); tags.append("prop")
        return v, r, u, tags

    @staticmethod
    def _ncd(a, b):
        za, zb = len(zlib.compress(a.encode())), len(zlib.compress(b.encode()))
        return (len(zlib.compress((a + " " + b).encode())) - min(za, zb)) / max(za, zb, 1)

    def _run(self, prompt, cands):
        sents = self._sents(prompt); rules, facts, q = self._rules_facts(sents)
        D = self._derive(rules, facts) if rules else set()
        gt = self._closure(self._orders(prompt)); comp = self._compute(prompt)
        qprop = self._prop(q) if (q and rules) else None; qord = self._orders(q) if q else []; sup = self._super(q) if q else None
        names = set(re.findall(r"(?<=[a-z,] )[A-Z][a-z]+\b", prompt))
        rows = []
        for c in cands:
            v, r, u, tg = self._claims(c, qprop, qord, sup, gt, D)
            ent = len(re.findall(r"\b(he|she|they|him|her|it)\b", c.lower())) * (float(np.log2(len(names))) if len(names) > 1 else 0.0)
            rows.append((c, v, r, u, tg, self._comp_match(comp, c), ent))
        tags = sorted({t for row in rows for t in row[4]}); ix = {t: i for i, t in enumerate(tags)}
        W = np.zeros((len(tags), len(tags)))  # Hebbian co-occurrence prior
        for c, v, r, u, tg, cm, ent in rows:
            s = 0.1 if v > r else (-0.1 if r else 0.0)
            for a in tg:
                for b in tg: W[ix[a], ix[b]] += s
        W[np.abs(W) < 0.05] = 0.0
        out = []
        for c, v, r, u, tg, cm, ent in rows:
            struct = v / (v + r + self.lam * u) if (v + r + u) else 0.5
            if r: struct *= 0.2
            h = 0.5 + float(np.clip(np.mean([W[ix[a], ix[b]] for a in tg for b in tg]) if tg else 0.0, -0.5, 0.5))
            n = self._ncd(prompt, c)
            score = 0.50 * struct + 0.25 * cm + 0.10 * h + 0.15 * (1 - n) - self.mu * ent
            kind = comp[1] if comp else "none"
            reason = "verified=%d refuted=%d unresolved=%d; compute=%s match=%.1f; hebb=%.2f; ncd=%.2f; entropy=%.2f" % (v, r, u, kind, cm, h, n, ent)
            out.append((c, float(score), reason, {"v": v, "r": r, "comp": cm, "kind": kind}))
        return out

    # ---------------- public interface ----------------
    def evaluate(self, prompt, candidates):
        cap, hits = self._meta_confidence(prompt)
        res = sorted(self._run(prompt, candidates), key=lambda x: (-x[1], x[0]))
        return [{"candidate": c, "score": s, "reasoning": rs + ("; meta=" + ",".join(hits) if hits else "")} for c, s, rs, _ in res]

    def confidence(self, prompt, answer):
        cap, hits = self._meta_confidence(prompt)
        d = self._run(prompt, [answer])[0][3]
        if d["comp"] == 1.0: base = 0.9 if not d["r"] else 0.3
        elif d["comp"] == 0.0: base = 0.08
        elif d["r"]: base = 0.1
        elif d["v"]: base = 0.72
        else: base = 0.25
        return float(min(base, cap))


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
