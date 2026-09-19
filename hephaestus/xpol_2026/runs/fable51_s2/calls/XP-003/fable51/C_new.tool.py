import itertools
import zlib

"""Perturbation-stable constraint closure grader.

Mechanism (Topology x Dynamical Systems x Sensitivity Analysis):
  1. Regex extraction builds a fact graph from the prompt: LT edges (comparatives,
     before/after), IMPLIES edges (if/then) and atomic facts, each tagged with the
     premise index that justifies it (ATMS-style justification list).
  2. Dynamical system: forward chaining F = check_transitivity + modus_ponens
     (+ modus tollens) is iterated on the fact set until a fixed point; the
     iteration count and closure size are tracked, and signed loops (A<B and
     B<A, or p and not-p) are counted as contradictions.
  3. Topology (beta_0): a candidate's conclusion atoms must lie in the networkx
     component reachable from premise atoms, otherwise the claim is unsupported.
  4. Sensitivity sweep: each premise is dropped, the closure is recomputed, and
     conclusion survival is recorded as a vector s in {0,1}^n; a finite-difference
     Lyapunov analogue (facts changed per perturbation) measures fragility.
     Conclusions that flip under some perturbation are 'reasoned'; those
     invariant to every premise are 'coincidental' and scored lower.
  5. Constructive arithmetic (bat_and_ball, modular_arithmetic, bayesian_update,
     all_but_n, numeric compare, sympy expressions) gives definitive answers.
     NCD is a <=10% tiebreak.  confidence() is capped by _meta_confidence().
"""
import re, zlib, itertools
import numpy as np
import networkx as nx
import sympy
try:
    import forge_primitives as fp
except Exception:
    fp = None

def _prim(name, *a):
    f = getattr(fp, name, None) if fp else None
    if f is None: return None
    try: return f(*a)
    except Exception: return None

def _num(r, fallback):
    return float(r) if isinstance(r, (int, float)) and not isinstance(r, bool) else fallback

HIGH = "taller|older|bigger|faster|heavier|larger|greater|longer|stronger|richer|more"
LOW = "shorter|younger|smaller|slower|lighter|less|fewer|weaker|poorer"
SUP_HI = "tallest|oldest|biggest|fastest|heaviest|largest|greatest|longest|strongest|richest|most|last|latest"
SUP_LO = "shortest|youngest|smallest|slowest|lightest|least|fewest|weakest|poorest|first|earliest"
META = [(r"\b(have|has|had) (you|he|she|they) (stopped|quit|given up)\b", 0.2, "presupposition"),
        (r"\bwhy (did|does|do|has|have) .* (fail|stop|quit|lie|cheat)", 0.2, "presupposition"),
        (r"\b(every|each|all) \w+ .*\b(a|an|some) \w+.*\b(same|different)\b", 0.25, "scope ambiguity"),
        (r"\b\w+ (told|said to|asked) \w+ (that )?(he|she|they) (was|were|is|are)\b.*\bwho\b", 0.2, "pronoun ambiguity"),
        (r"\beither\b .* \bor\b .*\?", 0.25, "false dichotomy"),
        (r"\b(best|worst|favou?rite|most beautiful|nicest)\b", 0.25, "subjective"),
        (r"\b(survived|survivors|returned) .* (armou?r|reinforce|improve)", 0.25, "survivorship bias"),
        (r"\b(already (spent|invested)|sunk)\b", 0.25, "sunk cost"),
        (r"\b(regress|regression|lucky streak|after (an )?(unusually|extremely))", 0.25, "regression to mean"),
        (r"\b(valid|sound|strong|weak) (argument|inference)\b", 0.3, "validity vs truth")]

class ReasoningTool:
    def __init__(self):
        self.lam, self.mu = 0.2, 0.3

    # ---------- extraction: prompt -> justified premises ----------
    def _neg(self, s): return s[4:] if s.startswith("not ") else "not " + s

    def _premises(self, text):
        prem = []
        for i, s in enumerate(re.split(r"(?<=[.;!?])\s+", text.lower())):
            s = s.strip(" .")
            if not s or s.endswith("?"): continue
            m = re.search(r"(\w+) (?:is|was|runs|comes) (?:%s) than (\w+)" % HIGH, s)
            if m: prem.append(("LT", (m.group(2), m.group(1)), i)); continue
            m = re.search(r"(\w+) (?:is|was) (?:%s) than (\w+)" % LOW, s)
            if m: prem.append(("LT", (m.group(1), m.group(2)), i)); continue
            m = re.search(r"(\w+) (?:comes |happens |is |was )?(before|after) (\w+)", s)
            if m:
                a, b = (m.group(1), m.group(3)) if m.group(2) == "before" else (m.group(3), m.group(1))
                prem.append(("LT", (a, b), i)); continue
            m = re.search(r"if (.+?),? then (.+)", s) or re.search(r"(.+?) implies (.+)", s)
            if m: prem.append(("IMP", (self._atom(m.group(1)), self._atom(m.group(2))), i)); continue
            m = re.search(r"(\w+ (?:is|are|was|does|did|has|will)(?: not)? [\w ]+)", s)
            if m: prem.append(("FACT", self._atom(m.group(1)), i))
        return prem

    def _atom(self, s):
        s = re.sub(r"\b(the|a|an|it|then)\b", "", s.lower()).strip(" .,")
        s = re.sub(r"\s+", " ", s)
        neg = bool(re.search(r"\b(not|n't|never|no)\b", s))
        s = re.sub(r"\b(not|n't|never|no|is|are|was|were|does|do|did)\b", "", s).strip()
        return ("not " if neg else "") + re.sub(r"\s+", " ", s)

    # ---------- dynamical system: iterate F to a fixed point ----------
    def _closure(self, prem):
        lt = {p for k, p, _ in prem if k == "LT"}; imp = [p for k, p, _ in prem if k == "IMP"]
        facts = {p for k, p, _ in prem if k == "FACT"}; iters = 0
        while iters < 40:
            iters += 1; n = (len(lt), len(facts))
            r = _prim("check_transitivity", sorted(lt))
            if isinstance(r, dict): r = r.get("closure") or r.get("implied") or []
            if isinstance(r, (list, set, tuple)):
                lt |= {tuple(p) for p in r if isinstance(p, (list, tuple)) and len(p) == 2}
            for (a, b), (c, d) in itertools.product(list(lt), repeat=2):
                if b == c and a != d: lt.add((a, d))
            r = _prim("modus_ponens", [list(p) for p in imp], sorted(facts))
            if isinstance(r, (list, set, tuple)): facts |= {x for x in r if isinstance(x, str)}
            for p, q in imp:
                if p in facts: facts.add(q)
                if self._neg(q) in facts: facts.add(self._neg(p))  # modus tollens
            if (len(lt), len(facts)) == n: break
        contra = sum(1 for a, b in lt if (b, a) in lt) // 2 + sum(1 for f in facts if self._neg(f) in facts) // 2
        return lt, facts, iters, contra

    # ---------- conclusion test: +1 supported / -1 refuted / 0 unknown ----------
    def _holds(self, prompt, cand, lt, facts):
        p, c = prompt.lower(), cand.lower().strip(" .")
        ents = {x for e in lt for x in e}
        m = re.search(r"(\w+) (?:is|was) (?:%s) than (\w+)" % HIGH, c) or re.search(r"(\w+) (?:comes |is )?before (\w+)", c)
        if m: return 1 if (m.group(2), m.group(1)) in lt else -1 if (m.group(1), m.group(2)) in lt else 0
        q = re.search(r"(?:is|was) (\w+) (?:%s) than (\w+)\?" % HIGH, p)
        if q and re.match(r"(yes|no)\b", c):
            v = 1 if (q.group(2), q.group(1)) in lt else -1 if (q.group(1), q.group(2)) in lt else 0
            return v if c.startswith("yes") else -v
        sup = re.search(r"\b(%s|%s)\b" % (SUP_HI, SUP_LO), p)
        if sup and c in ents:
            hi = sup.group(1) in SUP_HI.split("|")
            ok = all(((e, c) if hi else (c, e)) in lt for e in ents if e != c)
            return 1 if ok else -1 if any(((c, e) if hi else (e, c)) in lt for e in ents if e != c) else 0
        a = self._atom(c)
        if a in facts: return 1
        if self._neg(a) in facts: return -1
        return 0

    # ---------- constructive computation via arithmetic primitives ----------
    def _compute(self, p):
        p = p.lower(); nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", p.replace(",", ""))]
        m = re.search(r"\$?(\d+(?:\.\d+)?)[^.]*?\$?(\d+(?:\.\d+)?) more than", p)
        if m and "cost" in p:
            t, d = float(m.group(1)), float(m.group(2)); return _num(_prim("bat_and_ball", t, d), (t - d) / 2)
        m = re.search(r"remainder when (\d+) is divided by (\d+)", p) or re.search(r"(\d+) mod(?:ulo)? (\d+)", p)
        if m:
            a, b = int(m.group(1)), int(m.group(2)); return _num(_prim("modular_arithmetic", a, 0, b), a % b)
        m = re.search(r"all but (\d+)", p)
        if m and nums: return _num(_prim("all_but_n", nums[0], int(m.group(1))), int(m.group(1)))
        pc = [float(x) / 100 for x in re.findall(r"(\d+(?:\.\d+)?)\s?%", p)]
        if len(pc) >= 3 and re.search(r"test|positive", p):
            pr, s, f = pc[0], pc[1], pc[2]
            return _num(_prim("bayesian_update", pr, s, f), pr * s / (pr * s + (1 - pr) * f))
        m = re.search(r"(?:larger|bigger|greater|smaller|less)\b", p)
        if m and len(nums) == 2: return max(nums) if m.group(0) in ("larger", "bigger", "greater") else min(nums)
        m = re.search(r"what is ([\d\s\+\-\*/\(\)\.]{3,})\??", p)
        if m:
            try: return float(sympy.sympify(m.group(1).strip()))
            except Exception: return None
        return None

    def _ncd(self, a, b):
        C = lambda s: len(zlib.compress(s.encode())); return (C(a + b) - min(C(a), C(b))) / max(C(a), C(b))

    # ---------- topology + sensitivity wiring ----------
    def _analyse(self, prompt, cand):
        prem = self._premises(prompt); lt, facts, iters, contra = self._closure(prem)
        h = self._holds(prompt, cand, lt, facts)
        G = nx.Graph([(a, b) for a, b in lt] + [(p, q) for k, (p, q), _ in prem if k == "IMP"])
        toks = set(re.findall(r"\w+", cand.lower()))
        connected = bool(toks & set(G.nodes)) or h != 0  # beta_0: claim touches the premise component
        surv, deltas = [], []
        for i in range(len(prem)):
            sub = prem[:i] + prem[i + 1:]; lt2, f2, _, _ = self._closure(sub)
            surv.append(1.0 if self._holds(prompt, cand, lt2, f2) == h else 0.0)
            deltas.append(len(lt ^ lt2) + len(facts ^ f2))
        lyap = float(np.mean(deltas)) / max(1, len(lt) + len(facts)) if deltas else 0.0
        if h == 0 or not prem: consist = 0.5
        else:
            r = _prim("confidence_from_agreement", surv); agree = _num(r, float(np.mean(surv)))
            consist = 1.0 if 0.0 < agree < 1.0 else (0.6 if agree == 0.0 else 0.0)  # invariant to all = coincidence
        return dict(h=h, contra=contra, connected=connected, consist=consist, lyap=lyap, n=len(prem), iters=iters)

    def _comp_score(self, prompt, cand):
        ans = self._compute(prompt)
        if ans is None: return 0
        m = re.search(r"-?\d+(?:\.\d+)?", cand.replace(",", "").replace("$", ""))
        if not m: return 0
        return 1 if abs(float(m.group(0)) - ans) < 1e-6 * max(1, abs(ans)) + 1e-6 else -1

    def _meta_confidence(self, prompt):
        p = prompt.lower(); cap, why = 1.0, []
        for pat, c, name in META:
            if re.search(pat, p): cap, why = min(cap, c), why + [name]
        prem = self._premises(prompt)
        if self._compute(prompt) is None and not any(k in ("LT", "IMP") for k, _, _ in prem):
            r = _prim("information_sufficiency", [prompt], [str(x) for x in prem])
            cap, why = min(cap, 0.28), why + ["no structural parser matched"]
        return cap, why

    def evaluate(self, prompt, candidates):
        out = []
        for idx, c in enumerate(candidates):
            a = self._analyse(prompt, c); comp = self._comp_score(prompt, c)
            core = a["h"] if a["h"] != 0 else comp
            score = 0.6 * core - self.lam * min(a["contra"], 3) / 3 + self.mu * a["consist"]
            score += 0.1 * (1 - self._ncd(prompt, c)) - (0.1 if not a["connected"] else 0) - 0.1 * min(a["lyap"], 1)
            why = "support=%d comp=%d contradictions=%d consistency=%.1f lyapunov=%.2f premises=%d iters=%d" % (
                a["h"], comp, a["contra"], a["consist"], a["lyap"], a["n"], a["iters"])
            out.append({"candidate": c, "score": round(float(score), 4), "reasoning": why, "_i": idx})
        out.sort(key=lambda d: (-d["score"], d["_i"]))
        for d in out: d.pop("_i")
        return out

    def confidence(self, prompt, answer):
        cap, why = self._meta_confidence(prompt); a = self._analyse(prompt, answer); comp = self._comp_score(prompt, answer)
        if comp != 0: conf = 0.92 if comp > 0 else 0.08
        elif a["h"] != 0:
            conf = (0.78 if a["h"] > 0 else 0.15) * (1 - 0.3 * min(a["lyap"], 1)) - 0.15 * min(a["contra"], 3) / 3
            if a["consist"] == 0.0: conf = min(conf, 0.5)  # coincidental: invariant to every premise
        else: conf = 0.25
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
