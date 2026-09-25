import math
import zlib

"""Innovation-Weighted Abstract Consistency Scorer (Kalman x Adaptive Control x Abstract Interp).
1. Abstract interpretation: regex extractors emit constraints into an AbstractState. Order DAG is
   closed (networkx transitive closure, check_transitivity for conflicts); facts are closed with
   modus_ponens plus a bounded modus-tollens loop (widening); numeric answers are COMPUTED via
   bat_and_ball / all_but_n / modular_arithmetic / fencepost_count / bayesian_update /
   coin_flip_independence.  S+ = closure, S- = zero-ambiguity extractions (numeric/compute).
2. Measurement: each candidate claim -> z=1 (entailed), z=0 (contradicts S+), z=0.5 (abstain).
3. Scalar Kalman filter per candidate, gain K = s2/(s2+R[k]) with per-extractor noise R[k].
4. Adaptive control: innovation variance inflates R[k]; an extractor contradicted on EVERY
   candidate (model-reference check) is treated as mis-parsing and its R is raised; then re-filter.
Score = 0.9*mu + 0.1*(1-NCD).  confidence() is capped by _meta_confidence() (question properties)."""
import re, zlib, math
import numpy as np
import networkx as nx
from forge_primitives import (check_transitivity, modus_ponens, bat_and_ball, all_but_n,
    modular_arithmetic, fencepost_count, coin_flip_independence, bayesian_update,
    confidence_from_agreement, information_sufficiency)

def _safe(fn, *a):
    try: return fn(*a)
    except Exception: return None
def _num(s): return float(s.replace(",", ""))
def _nums(t): return [_num(x) for x in re.findall(r"-?\d+(?:\.\d+)?", t)]
STOP = {"the","a","an","is","are","was","were","do","does","did","it","will","then","get","gets",
        "got","become","becomes","be","that","been"}
def _norm(t):
    ws = [w for w in re.sub(r"[^a-z0-9 ]", " ", t.lower()).split() if w not in STOP]
    return " ".join(re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w for w in ws)
CMP = {"taller":1,"older":1,"faster":1,"bigger":1,"heavier":1,"larger":1,"greater":1,"more":1,
       "stronger":1,"shorter":-1,"younger":-1,"slower":-1,"smaller":-1,"lighter":-1,"less":-1,
       "fewer":-1,"weaker":-1}
HEDGE = (r"ambigu|cannot be determined|can't be determined|not enough|insufficient|depends|unclear|"
         r"presuppos|not necessarily|false dichotomy|neither|both|loaded question|no way to (know|tell)|"
         r"cannot conclude|can't conclude|unanswerable|invalid|does not follow")
META = [(r"\bhave you (stopped|quit|given up|finished)\b|\bwhy (did|does|has|is) .*(fail|stop|quit|bad)", "presupposition"),
        (r"\b(every|each|all) \w+ .*\ban? \w+\b.*\b(same|different)\b", "scope ambiguity"),
        (r"\b\w+ (told|asked|said to) \w+ (that )?(he|she|they) (was|were|is|had)\b", "pronoun ambiguity"),
        (r"\beither\b.*\bor\b(?!.*\bonly (two|2)\b)", "false dichotomy"),
        (r"\b(best|worst|favou?rite|most beautiful|nicest|should i)\b", "subjectivity"),
        (r"\b(surviv|sunk cost|already (spent|invested)|regress|streak|due for|argument (valid|sound|strong)|how strong)", "judgment trap")]

class ReasoningTool:
    def __init__(self):
        self.Q = 0.01
        self.R0 = {"numeric": 0.05, "compute": 0.03, "prob": 0.08, "order": 0.08, "fact": 0.15,
                   "cond": 0.10, "meta": 0.10}

    # ---------- 1. abstract interpretation of the prompt ----------
    def _abstract(self, p):
        S = {"ans": [], "G": nx.DiGraph(), "facts": {}, "conds": [], "ents": set(), "q": None}
        low, A = p.lower(), []
        m = re.search(r"(?:larger|bigger|greater|smaller|less|more|higher|lower)[^?]*?(-?\d+\.?\d*)\s*(?:or|vs\.?|,|and)\s*(-?\d+\.?\d*)", low)
        if m:
            a, b = _num(m.group(1)), _num(m.group(2))
            A.append(("numeric", min(a, b) if re.search(r"smaller|less|lower", m.group(0)) else max(a, b), 1e-9))
        m = re.search(r"\$?(\d+\.?\d*)\s*(?:in total|total|together|altogether).*?\$?(\d+\.?\d*)\s*more than", low, re.S)
        if m:
            r = _safe(bat_and_ball, _num(m.group(1)), _num(m.group(2)))
            r = min(r) if isinstance(r, (tuple, list)) else r
            A.append(("compute", float(r if r is not None else (_num(m.group(1)) - _num(m.group(2))) / 2), 1e-6))
        m = re.search(r"(\d+)\s+\w+.*?all but (\d+)", low, re.S)
        if m: A.append(("compute", float(_safe(all_but_n, int(m.group(1)), int(m.group(2))) or int(m.group(2))), 1e-6))
        m = re.search(r"(\d+)\s*(?:o'?clock|:00|am|pm).*?(\d+)\s*hours", low, re.S)
        if m:
            r = _safe(modular_arithmetic, int(m.group(1)), int(m.group(2)), 12)
            if not isinstance(r, (int, float)): r = (int(m.group(1)) + int(m.group(2))) % 12
            A.append(("compute", float(r or 12), 1e-6))
        m = re.search(r"remainder when (\d+) is divided by (\d+)|(\d+)\s*(?:mod|modulo)\s*(\d+)", low)
        if m:
            a, mod = [int(x) for x in m.groups() if x]
            A.append(("compute", float(a % mod), 1e-6))
        m = re.search(r"(\d+)\s*(?:m|meters|metres|feet|ft|km)\b.*?every\s*(\d+)", low, re.S)
        if m and re.search(r"post|pole|tree|lamp", low):
            segs = int(m.group(1)) // max(1, int(m.group(2))); r = _safe(fencepost_count, segs)
            A.append(("compute", float(r if isinstance(r, (int, float)) else segs + 1), 1e-6))
        if re.search(r"flip|toss", low) and re.search(r"next (flip|toss)|probability", low):
            n = [int(x) for x in re.findall(r"(\d+)\s*(?:times|heads|tails)", low)] or [5]
            r = _safe(coin_flip_independence, n[0], n[-1])
            A.append(("prob", float(r) if isinstance(r, float) and 0 < r < 1 else 0.5, 0.01))
        pr = re.search(r"(\d+\.?\d*)\s*%\s*(?:of|prevalence|have|has)", low)
        fp = re.search(r"(\d+\.?\d*)\s*%\s*false positive", low)
        lk = re.search(r"(\d+\.?\d*)\s*%\s*(?:sensitiv|accura|true positive)|(?:detect|identif|catch)\w*\s*(\d+\.?\d*)\s*%", low)
        if pr and fp:
            pv, f = _num(pr.group(1)) / 100, _num(fp.group(1)) / 100
            l = _num([g for g in lk.groups() if g][0]) / 100 if lk else 1.0
            r = _safe(bayesian_update, pv, l, f)
            A.append(("prob", float(r) if isinstance(r, float) else pv * l / (pv * l + (1 - pv) * f), 0.02))
        m = re.search(r"(?:what is|what's|calculate|evaluate|compute)\s*:?\s*([\d\.\s\+\-\*/\(\)x]+?)\s*[?=]", low)
        if m and re.search(r"[\+\-\*/x]", m.group(1)) and re.search(r"\d", m.group(1)):
            try: A.append(("compute", float(eval(m.group(1).replace("x", "*"), {"__builtins__": {}})), 1e-6))
            except Exception: pass
        m = re.search(r"(\d+\.?\d*)\s*%\s*of\s*(\d+\.?\d*)", low)
        if m and "false" not in low: A.append(("compute", _num(m.group(1)) / 100 * _num(m.group(2)), 1e-6))
        edges = []
        for a, rel, b in re.findall(r"(\w+) (?:is|are|was|runs|weighs) (\w+) than (\w+)", low):
            if rel in CMP: edges.append((a, b) if CMP[rel] > 0 else (b, a)); S["ents"] |= {a, b}
        if edges:
            S["G"] = nx.transitive_closure(nx.DiGraph(edges))
            S["conflict"] = _safe(check_transitivity, edges) is False or not nx.is_directed_acyclic_graph(S["G"])
            m = re.search(r"(?:who|which)\s+(?:\w+\s+)?(?:is|one is)\s+(?:the\s+)?(\w+est)\b", low)
            if m and not S["conflict"]:
                up = CMP.get(re.sub(r"est$", "er", m.group(1)), 1) > 0
                top = [n for n in S["G"] if (S["G"].in_degree(n) if up else S["G"].out_degree(n)) == 0]
                if len(top) == 1: A.append(("order", top[0], 0))
        for s in re.split(r"(?<=[.;!?])\s+", p):
            sl = s.lower().strip()
            m = re.match(r"if (.+?),? then (.+?)[.;!]?$", sl) or re.match(r"if (.+?), (.+?)[.;!]?$", sl)
            if m: S["conds"].append((_norm(m.group(1)), _norm(m.group(2)))); continue
            m = re.match(r"(is|are|does|do|did|can|will|was|has|were)\s+(.+?)\??$", sl)
            if m: S["q"] = _norm(m.group(2)); continue
            if sl.endswith("?") or " than " in sl or not sl: continue
            key = _norm(re.sub(r"\b(not|never|n't)\b", "", sl))
            if key and len(key.split()) <= 8: S["facts"][key] = -1 if re.search(r"\b(not|never|n't)\b", sl) else 1
        derived = _safe(modus_ponens, S["conds"], [k for k, v in S["facts"].items() if v > 0])
        for d in (derived if isinstance(derived, (list, set, tuple)) else []):
            if isinstance(d, str): S["facts"].setdefault(_norm(d), 1)
        for _ in range(20):  # widened closure: modus ponens + modus tollens (S+)
            ch = False
            for a, c in S["conds"]:
                if S["facts"].get(a) == 1 and S["facts"].get(c) != 1: S["facts"][c] = 1; ch = True
                if S["facts"].get(c) == -1 and S["facts"].get(a) != -1: S["facts"][a] = -1; ch = True
            if not ch: break
        S["ans"] = A; S["n"] = len(A) + len(edges) + len(S["facts"]) + len(S["conds"])
        return S

    # ---------- 2. measurement of candidate claims against S-/S+ ----------
    def _measure(self, S, cand, meta):
        c, ms = cand.lower(), []
        cn = _nums(c) + [_num(x) / 100 for x in re.findall(r"(\d+\.?\d*)\s*%", c)] + \
             [int(a) / int(b) for a, b in re.findall(r"(\d+)\s*/\s*(\d+)", c) if int(b)]
        if "cent" in c: cn += [x / 100 for x in _nums(c)]
        for k, val, tol in S["ans"]:
            if isinstance(val, str):
                hit = [e for e in S["ents"] if re.search(r"\b%s\b" % re.escape(e), c)]
                if hit: ms.append((k, 1.0 if hit == [val] else 0.0))
            elif k == "prob" and re.search(r"less|more|greater|lower|higher|unlikely|likely than", c): ms.append((k, 0.0))
            elif cn: ms.append((k, 1.0 if any(abs(x - val) <= tol * max(1.0, abs(val)) for x in cn) else 0.0))
        for a, rel, b in re.findall(r"(\w+) (?:is|are|was) (\w+) than (\w+)", c):
            if rel in CMP and S["G"].number_of_nodes():
                x, y = (a, b) if CMP[rel] > 0 else (b, a)
                ms.append(("order", 1.0 if S["G"].has_edge(x, y) else 0.0 if S["G"].has_edge(y, x) else 0.5))
        yn = re.match(r"\s*(yes|no)\b", c)
        if S["q"] is not None:
            pol = S["facts"].get(S["q"])
            if yn and pol is not None: ms.append(("fact", 1.0 if (yn.group(1) == "yes") == (pol > 0) else 0.0))
            elif yn and S["conds"]: ms.append(("cond", 0.0))       # affirming the consequent trap
            elif pol is None and S["conds"] and re.search(HEDGE, c): ms.append(("cond", 1.0))
        nc = _norm(re.sub(r"\b(not|never|n't)\b", "", c)); cneg = bool(re.search(r"\b(not|never|n't)\b", c))
        for f, pol in S["facts"].items():
            if 2 <= len(f.split()) <= 6 and f in nc: ms.append(("fact", 1.0 if (pol > 0) != cneg else 0.0))
        if meta < 0.3: ms.append(("meta", 1.0 if re.search(HEDGE, c) else 0.0))
        return ms

    # ---------- 3./4. scalar Kalman filter + adaptive noise ----------
    def _kalman(self, ms, R):
        mu, s2, inn = 0.5, 0.25, {}
        for k, z in ms:
            s2 += self.Q; pred = s2 + R[k]; K = s2 / pred; nu = z - mu
            mu += K * nu; s2 *= (1 - K); inn.setdefault(k, []).append((nu, pred))
        return mu, s2, inn

    def _adapt(self, R, allms, inns):
        for k in R:
            zs = [z for ms in allms for kk, z in ms if kk == k]
            if len(zs) >= 2 and all(z == 0.0 for z in zs): R[k] *= 5.0   # model-reference: mis-parse
            nus = [(nu, p) for inn in inns for nu, p in inn.get(k, [])]
            if len(nus) >= 2:
                v, p = float(np.var([n for n, _ in nus])), float(np.mean([p for _, p in nus]))
                if v > p: R[k] *= min(4.0, v / p)                        # self-tuning regulator
        return R

    def _ncd(self, a, b):
        za, zb, zab = (len(zlib.compress(x.encode())) for x in (a, b, a + " " + b))
        return (zab - min(za, zb)) / max(za, zb, 1)

    def _meta_confidence(self, prompt):
        low, cap, why = prompt.lower(), 0.85, []
        for pat, name in META:
            if re.search(pat, low, re.S): cap, why = min(cap, 0.2), why + [name]
        S = self._abstract(prompt)
        if S["n"] == 0: cap, why = min(cap, 0.25), why + ["no structural parser matched"]
        if S.get("conflict"): cap, why = min(cap, 0.3), why + ["inconsistent ordering"]
        unk = sorted(set(re.findall(r"\b([a-z])\b(?=\s*[=+\-*/])|(?<=[=+\-*/])\s*\b([a-z])\b", low)))
        unk = sorted({u for pair in unk for u in pair if u}); eqs = re.findall(r"[^=]+=[^=]+", low)
        if unk:
            suff = _safe(information_sufficiency, unk, eqs)
            if suff is False or (suff is None and len(unk) > len(eqs)) or (isinstance(suff, (int, float)) and not isinstance(suff, bool) and suff < 0.5):
                cap, why = min(cap, 0.3), why + ["information insufficient"]
        return cap, why

    def evaluate(self, prompt, candidates):
        S, R = self._abstract(prompt), dict(self.R0)
        cap, why = self._meta_confidence(prompt)
        allms = [self._measure(S, c, cap) for c in candidates]
        R = self._adapt(R, allms, [self._kalman(ms, R)[2] for ms in allms])
        out = []
        for c, ms in zip(candidates, allms):
            mu, s2, _ = self._kalman(ms, R)
            abst = sum(1 for _, z in ms if z == 0.5)
            out.append({"candidate": c, "score": round(0.9 * mu + 0.1 * (1 - self._ncd(prompt, c)), 4),
                        "reasoning": "mu=%.2f var=%.3f claims=%d abstained=%d R=%s meta=%s" % (
                            mu, s2, len(ms), abst, {k: round(v, 3) for k, v in R.items()}, why or "none")})
        agree = _safe(confidence_from_agreement, [o["score"] for o in out])
        out.sort(key=lambda d: -d["score"])
        if out and agree is not None: out[0]["reasoning"] += " agreement=%s" % agree
        return out

    def confidence(self, prompt, answer):
        cap, why = self._meta_confidence(prompt)
        S = self._abstract(prompt); ms = self._measure(S, answer, cap)
        if not ms or all(z == 0.5 for _, z in ms): return float(min(cap, 0.25))
        mu, s2, _ = self._kalman(ms, dict(self.R0))
        definitive = any(k in ("compute", "numeric", "prob", "order") and z == 1.0 for k, z in ms)
        ceiling = cap if cap < 0.3 else min(cap, 0.95 if definitive else 0.8)
        return float(min(ceiling, max(0.0, mu - math.sqrt(s2))))


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
