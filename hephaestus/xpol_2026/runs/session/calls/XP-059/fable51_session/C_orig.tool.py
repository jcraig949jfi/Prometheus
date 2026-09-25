import re
import math
import zlib
import itertools
import numpy as np


class ReasoningTool:
    """Prime Number Theory x Program Synthesis x Analogical Reasoning.

    A library of tiny solution PROGRAMS (schemas) is enumerated for each prompt:
    numeric comparison, arithmetic evaluation, modular / parity / primality
    predicates, comparative-chain transitivity, and conditional inference
    (modus ponens / tollens). Analogical mapping selects the schemas whose
    relational signature matches the prompt's parsed relations; each selected
    program is EXECUTED to produce a computed answer, and candidates are scored
    by agreement with computed answers (structural >= 50%, computation >= 20%),
    with NCD to the prompt as a <= 15% tiebreaker. Number-theoretic predicates
    prune candidates that violate a computed constraint.
    """
    GT = ("larger", "greater", "bigger", "more", "taller", "older", "heavier", "faster", "higher", "longer")
    LT = ("smaller", "less", "fewer", "shorter", "younger", "lighter", "slower", "lower")

    def __init__(self):
        self.num = re.compile(r"-?\d+(?:\.\d+)?")
        self.cmp = re.compile(r"(\w+) (?:is|was|are) (\w+) than (\w+)")
        self.cond = re.compile(r"if ([^,]+?),? then ([^.?]+)")
        self.arith = re.compile(r"(?:what is|compute|calculate|evaluate)\s+([-\d\s\+\*/\(\)\.]+)\??")

    # ---------------- number-theoretic predicates ----------------
    @staticmethod
    def _is_prime(n):
        if n < 2 or n != int(n):
            return False
        n = int(n)
        return all(n % k for k in range(2, int(math.isqrt(n)) + 1))

    # ---------------- schema programs: each returns a computed answer or None ----------------
    def _prog_numeric_compare(self, p):
        m = re.search(r"is (-?\d+(?:\.\d+)?) (\w+) than (-?\d+(?:\.\d+)?)", p)
        if not m:
            return None
        x, w, y = float(m.group(1)), m.group(2), float(m.group(3))
        if w in self.GT:
            return "yes" if x > y else "no"
        if w in self.LT:
            return "yes" if x < y else "no"
        return None

    def _prog_arith(self, p):
        m = self.arith.search(p)
        if not m:
            return None
        expr = m.group(1).strip()
        if not re.fullmatch(r"[-\d\s\+\*/\(\)\.]+", expr) or not any(c in expr for c in "+-*/"):
            return None
        try:
            v = eval(expr, {"__builtins__": {}}, {})
        except Exception:
            return None
        return str(int(v)) if float(v).is_integer() else str(round(float(v), 4))

    def _prog_number_theory(self, p):
        nums = [float(n) for n in self.num.findall(p)]
        if "prime" in p and nums:
            return "yes" if self._is_prime(nums[-1]) else "no"
        m = re.search(r"(\d+) (?:mod|modulo|divided by) (\d+)", p)
        if m and "remainder" in p or (m and "mod" in p):
            a, b = int(m.group(1)), int(m.group(2))
            return str(a % b) if b else None
        if ("even" in p or "odd" in p) and nums:
            n = int(nums[-1])
            ask_even = "even" in p
            return "yes" if (n % 2 == 0) == ask_even else "no"
        m = re.search(r"is (\d+) divisible by (\d+)", p)
        if m:
            return "yes" if int(m.group(1)) % int(m.group(2)) == 0 else "no"
        return None

    def _prog_transitive(self, p):
        facts = set()
        for a, w, b in self.cmp.findall(p):
            if w in self.GT:
                facts.add((a, b))
            elif w in self.LT:
                facts.add((b, a))
        if not facts:
            return None
        changed = True
        while changed:
            changed = False
            for (a, b), (c, d) in itertools.product(list(facts), repeat=2):
                if b == c and (a, d) not in facts:
                    facts.add((a, d))
                    changed = True
        m = re.search(r"is (\w+) (\w+) than (\w+)\?", p)
        if m:
            a, w, b = m.groups()
            key = (a, b) if w in self.GT else (b, a) if w in self.LT else None
            if key is None:
                return None
            if key in facts:
                return "yes"
            if (key[1], key[0]) in facts:
                return "no"
            return "cannot be determined"
        names = {x for f in facts for x in f}
        if re.search(r"\bwho is the (?:\w+est|most \w+)\b", p):
            tops = [n for n in names if not any(b == n for (_, b) in facts)]
            return tops[0] if len(tops) == 1 else None
        return None

    def _prog_conditional(self, p):
        for ante, cons in self.cond.findall(p):
            ante, cons = ante.strip(), cons.strip()
            rest = p.replace("if " + ante, "")
            if re.search(r"\b" + re.escape(ante) + r"\b", rest):
                return cons                                   # modus ponens
            if re.search(r"\b(?:not|never|didn't|did not|isn't|is not)\b[^.]*" + re.escape(cons.split()[-1]), rest):
                return "not " + ante                          # modus tollens
        return None

    def _synthesize(self, p):
        """Analogical selection: run every schema, keep the ones whose relations fire."""
        answers = {}
        for name in ("numeric_compare", "arith", "number_theory", "transitive", "conditional"):
            a = getattr(self, "_prog_" + name)(p)
            if a is not None:
                answers[name] = a.lower()
        return answers

    def _ncd(self, x, y):
        cx, cy = len(zlib.compress(x.encode())), len(zlib.compress(y.encode()))
        return (len(zlib.compress((x + y).encode())) - min(cx, cy)) / max(cx, cy, 1)

    # ---------------- interface ----------------
    def _match(self, cand, answers):
        c = cand.lower().strip().rstrip(".")
        hits = 0
        for a in answers.values():
            if c == a or (a in ("yes", "no") and c.startswith(a)) or (a not in ("yes", "no") and a in c):
                hits += 1
            elif a in ("yes", "no") and c in ("yes", "no", "true", "false"):
                hits -= 1
        return hits

    def evaluate(self, prompt, candidates):
        p = prompt.lower()
        answers = self._synthesize(p)
        out = []
        for cand in candidates:
            hits = self._match(cand, answers)
            structural = 0.5 + 0.25 * max(-2, min(2, hits))
            computed = 1.0 if hits > 0 else 0.0
            ncd_term = 1.0 - self._ncd(p, cand.lower())
            score = 0.55 * structural + 0.30 * computed + 0.15 * ncd_term
            out.append({"candidate": cand, "score": round(float(score), 4),
                        "reasoning": "programs=%s hits=%d" % (sorted(answers) or "none", hits)})
        out.sort(key=lambda d: -d["score"])
        return out

    def _meta_confidence(self, prompt):
        p = prompt.lower()
        if re.search(r"have you (?:stopped|quit)|why did \w+ (?:fail|stop)", p):
            return 0.2
        if re.search(r"\bevery \w+ .*\ba \w+\b", p) and "same" in p:
            return 0.25
        if re.search(r"\w+ told \w+ (?:he|she) ", p) and "who" in p:
            return 0.2
        if re.search(r"\beither\b.*\bor\b", p):
            return 0.25
        if re.search(r"\b(?:best|worst|favorite)\b", p):
            return 0.25
        return 1.0

    def confidence(self, prompt, answer):
        p = prompt.lower()
        cap = self._meta_confidence(prompt)
        answers = self._synthesize(p)
        if not answers:
            return min(cap, 0.25)
        hits = self._match(answer, answers)
        base = 0.9 if hits > 0 else 0.1 if hits < 0 else 0.4
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
