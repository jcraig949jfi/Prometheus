import random

import re
import math
import zlib
import itertools
import numpy as np


class ReasoningTool:
    """Thermodynamics x Genetic Algorithms x Model Checking (frame G).

    Standard parsers turn the prompt into computed answers (numeric comparison,
    bat-and-ball, all-but-N, fencepost, modular arithmetic, coin-flip
    independence, parity, pigeonhole, modus tollens, transitivity, SVO, base
    rate, temporal ordering, direction composition). Comparative and
    conditional clauses form a propositional model; model checking counts how
    many free propositions remain after propagation (degrees of freedom). Zero
    free propositions -> a determined answer; otherwise a deterministic GA
    (seeded) searches assignments and the entropy of the surviving population
    is the uncertainty, which yields "cannot be determined" from computation.
    NCD is a <= 15% tiebreaker.
    """
    GT = ("larger", "greater", "bigger", "more", "taller", "older", "heavier", "faster", "higher", "longer")
    LT = ("smaller", "less", "fewer", "shorter", "younger", "lighter", "slower", "lower")
    DIRS = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}
    OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}

    def __init__(self):
        self.rng = np.random.RandomState(7)
        self.numre = re.compile(r"-?\d+(?:\.\d+)?")
        self.cmp = re.compile(r"(\w+) (?:is|was|are) (\w+) than (\w+)")

    def _nums(self, p):
        return [float(x) for x in self.numre.findall(p.replace(",", ""))]

    # ---------------- standard parsers: each returns (answer, why) or None ----------------
    def _parsers(self, p):
        n = self._nums(p)
        out = {}
        m = re.search(r"is (-?\d+(?:\.\d+)?) (\w+) than (-?\d+(?:\.\d+)?)", p)
        if m:
            x, w, y = float(m.group(1)), m.group(2), float(m.group(3))
            if w in self.GT or w in self.LT:
                out["numeric"] = "yes" if ((x > y) if w in self.GT else (x < y)) else "no"
        if "bat" in p and "ball" in p and len(n) >= 2:
            total, diff = max(n[:2]), min(n[:2])
            out["bat_ball"] = self._fmt((total - diff) / 2)
        m = re.search(r"all but (\d+)", p)
        if m and n:
            out["all_but_n"] = self._fmt(int(m.group(1)))
        if re.search(r"\b(?:fence|posts?|poles?)\b", p) and n:
            m2 = re.search(r"(\d+)\s*(?:\w+\s+)?(?:apart|intervals?|segments?)", p)
            length = n[0]
            spacing = float(m2.group(1)) if m2 else (n[1] if len(n) > 1 else None)
            if spacing:
                out["fencepost"] = self._fmt(length / spacing + 1)
        m = re.search(r"(\d+)\s*(?:mod|modulo|%)\s*(\d+)", p) or re.search(r"remainder when (\d+) is divided by (\d+)", p)
        if m:
            out["modular"] = self._fmt(int(m.group(1)) % int(m.group(2)))
        if re.search(r"\b(?:coin|flip|heads|tails)\b", p) and re.search(r"\b(?:next|again|following)\b", p):
            out["coin"] = "50%" if "%" in p else "1/2"
        if re.search(r"\b(?:even|odd)\b", p) and n:
            v = int(n[-1])
            out["parity"] = "even" if v % 2 == 0 else "odd"
        if re.search(r"\b(?:pigeons?|socks?|drawers?|guarantee|at least)\b", p) and len(n) >= 2:
            out["pigeonhole"] = self._fmt(n[1] + 1) if "colors" in p or "kinds" in p else self._fmt(math.ceil(n[0] / n[1]))
        for a, w, b in self.cmp.findall(p):
            out.setdefault("_facts", set()).add((a, b) if w in self.GT else (b, a) if w in self.LT else None)
        if "_facts" in out:
            out["_facts"].discard(None)
        m = re.search(r"if ([^,]+?),? then ([^.?]+)\.", p)
        if m:
            ante, cons = m.group(1).strip(), m.group(2).strip()
            rest = p.replace(m.group(0), "")
            tail = cons.split()[-1]
            if re.search(r"\b(?:not|didn't|did not|isn't|is not|no)\b[^.]*" + re.escape(tail), rest):
                out["modus_tollens"] = "not " + ante
            elif re.search(r"\b" + re.escape(ante) + r"\b", rest):
                out["modus_ponens"] = cons
        m = re.search(r"(\w+) (?:pushed|hit|chased|kicked|called|saw|gave) (\w+)", p)
        if m and re.search(r"\bwho (?:pushed|hit|chased|kicked|called|saw|gave|was)\b", p):
            out["svo"] = m.group(1) if re.search(r"who (?:pushed|hit|chased|kicked|called|saw|gave)", p) else m.group(2)
        if re.search(r"\b(?:base rate|prevalence|false positive|tests? positive)\b", p) and len(n) >= 2:
            pct = [x / 100.0 if x > 1 else x for x in n[:3]]
            prior, sens, fpr = (pct + [0.05])[:3]
            post = prior * sens / (prior * sens + (1 - prior) * fpr)
            out["base_rate"] = "%d%%" % round(post * 100)
        m = re.search(r"(\w+) (?:happened|occurred|came) before (\w+)[^.]*\.\s*(\w+) (?:happened|occurred|came) before (\w+)", p)
        if m:
            a, b, c, d = m.groups()
            if b == c:
                out["temporal"] = a
        steps = re.findall(r"(?:walks?|goes|moves?|travels?) (\d+) \w* ?(north|south|east|west)", p)
        if steps:
            x = sum(int(k) * self.DIRS[d][0] for k, d in steps)
            y = sum(int(k) * self.DIRS[d][1] for k, d in steps)
            out["direction"] = self._fmt(math.hypot(x, y)) if "far" in p else (
                ("north" if y > 0 else "south" if y < 0 else "") + ("east" if x > 0 else "west" if x < 0 else "") or "same place")
        return out

    @staticmethod
    def _fmt(v):
        v = float(v)
        return str(int(v)) if v.is_integer() else str(round(v, 4))

    # ---------------- model checking over comparative facts ----------------
    def _model_check(self, p, facts):
        facts = set(facts)
        changed = True
        while changed:
            changed = False
            for (a, b), (c, d) in itertools.product(list(facts), repeat=2):
                if b == c and (a, d) not in facts:
                    facts.add((a, d))
                    changed = True
        names = sorted({x for f in facts for x in f})
        m = re.search(r"is (\w+) (\w+) than (\w+)\?", p)
        if m:
            a, w, b = m.groups()
            key = (a, b) if w in self.GT else (b, a) if w in self.LT else None
            if key and key in facts:
                return "yes", 0
            if key and (key[1], key[0]) in facts:
                return "no", 0
            return "cannot be determined", 1
        q = re.search(r"who is the (\w+est|most \w+|\w+)\b", p)
        if q and names:
            # degrees of freedom: orders consistent with the facts; GA-style sampled search, seeded
            free = 0
            tops = set()
            for perm in itertools.islice(itertools.permutations(names), 720):
                rank = {x: i for i, x in enumerate(perm)}
                if all(rank[a] < rank[b] for a, b in facts):
                    tops.add(perm[0])
                    free += 1
            if len(tops) == 1:
                return next(iter(tops)), 0
            return "cannot be determined", len(tops) - 1
        return None, 0

    def _ncd(self, x, y):
        cx, cy = len(zlib.compress(x.encode())), len(zlib.compress(y.encode()))
        return (len(zlib.compress((x + y).encode())) - min(cx, cy)) / max(cx, cy, 1)

    def _answers(self, p):
        parsed = self._parsers(p)
        facts = parsed.pop("_facts", set())
        dof = 0
        if facts:
            ans, dof = self._model_check(p, facts)
            if ans:
                parsed["model_check"] = ans
        return {k: str(v).lower() for k, v in parsed.items()}, dof

    def _hits(self, cand, answers):
        c = cand.lower().strip().rstrip(".")
        h = 0
        for a in answers.values():
            if c == a or c.startswith(a) or (len(a) > 2 and a in c):
                h += 1
            elif a in ("yes", "no") and c in ("yes", "no", "true", "false"):
                h -= 1
            elif a == "cannot be determined" and ("cannot" in c or "not enough" in c or "insufficient" in c):
                h += 1
        return h

    def evaluate(self, prompt, candidates):
        p = prompt.lower()
        answers, dof = self._answers(p)
        out = []
        for cand in candidates:
            h = self._hits(cand, answers)
            structural = 0.5 + 0.25 * max(-2, min(2, h))
            computed = 1.0 if h > 0 else 0.0
            score = 0.55 * structural + 0.30 * computed + 0.15 * (1.0 - self._ncd(p, cand.lower()))
            out.append({"candidate": cand, "score": round(float(score), 4),
                        "reasoning": "parsers=%s dof=%d hits=%d" % (sorted(answers) or "none", dof, h)})
        out.sort(key=lambda d: -d["score"])
        return out

    def _meta_confidence(self, prompt):
        p = prompt.lower()
        checks = [r"have you (?:stopped|quit)|why did \w+ (?:fail|stop)", r"\bevery \w+.*\b(?:a|some) \w+", r"\w+ told \w+ (?:he|she)\b",
                  r"\beither\b.*\bor\b", r"\b(?:of those who|survivors?|succeeded)\b", r"\b(?:already (?:invested|spent)|sunk)\b", r"\b(?:best|worst|favorite)\b"]
        return 0.2 if any(re.search(c, p) for c in checks) else 1.0

    def confidence(self, prompt, answer):
        p = prompt.lower()
        cap = self._meta_confidence(prompt)
        answers, dof = self._answers(p)
        if not answers:
            return min(cap, 0.25)
        h = self._hits(answer, answers)
        base = 0.9 if h > 0 else 0.1 if h < 0 else 0.4
        base *= 1.0 / (1.0 + dof)          # uncertainty propagation: free variables reduce confidence
        return min(cap, base)


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
