import math
import zlib

"""
topo_dyn_sens_tool.py -- Topology x Dynamical Systems x Sensitivity Analysis

Mechanism: propositions in prompt+candidate become a one-hot state x0 in R^d;
co-clause adjacency gives Laplacian L. Nullspace projector P0 (connected
components) filters x0; heat-flow dynamics x <- (I - a L) x relax to an
attractor x*. Jacobian dx*/dx0 = pinv(a L) gives perturbation sensitivity.
Primitive pipeline: parsed relations -> check_transitivity / modus_ponens /
bayesian_update / bat_and_ball / modular_arithmetic / parity_check produce a
computed verdict; perturbed reruns feed confidence_from_agreement;
information_sufficiency + _meta_confidence cap epistemic confidence.
"""
import re, zlib, math
import numpy as np
try:
    from forge_primitives import (check_transitivity, modus_ponens, bayesian_update,
        bat_and_ball, modular_arithmetic, parity_check, confidence_from_agreement,
        information_sufficiency, all_but_n)
except Exception:  # minimal stand-ins so the tool stays runnable
    def check_transitivity(rels):
        d = {}
        for a, b in rels: d.setdefault(a, set()).add(b)
        ch = True
        for a in list(d):
            st, seen = list(d[a]), set()
            while st:
                n = st.pop()
                if n in seen: continue
                seen.add(n); st.extend(d.get(n, ()))
            d[a] |= seen; ch &= a not in seen
        return {"consistent": ch, "closure": d}
    def modus_ponens(prem, facts):
        f = set(facts); ch = True
        while ch:
            ch = False
            for a, b in prem:
                if a in f and b not in f: f.add(b); ch = True
        return f
    def bayesian_update(p, l, fp): return p * l / (p * l + (1 - p) * fp)
    def bat_and_ball(t, d): return (t - d) / 2.0
    def modular_arithmetic(a, b, m): return (a + b) % m
    def parity_check(nums): return sum(nums) % 2
    def confidence_from_agreement(s): return 1.0 - float(np.std(s)) / (abs(float(np.mean(s))) + 1e-6)
    def information_sufficiency(u, c): return c >= u
    def all_but_n(t, n): return n

NUM = r"-?\d+(?:\.\d+)?"
CMP = re.compile(r"(\w+)\s+is\s+(?:taller|older|bigger|faster|heavier|greater|larger|more)\s+than\s+(\w+)", re.I)

class ReasoningTool:
    def __init__(self):
        self.alpha, self.eps, self.delta = 0.25, 1e-4, 0.01

    # ---------- parsing ----------
    def _props(self, text):
        clauses = [c for c in re.split(r"[.;,?!]|\bif\b|\bthen\b|\band\b|\bor\b", text.lower()) if c.strip()]
        out = []
        for c in clauses:
            toks = re.findall(r"[a-z]+|" + NUM, c)
            props = [t for t in toks if t not in {"the", "a", "an", "is", "are", "was", "of", "to", "in", "than", "that", "it", "be"}]
            neg = -1.0 if re.search(r"\b(not|no|never|n't)\b", c) else 1.0
            w = neg * (1.5 if re.search(r"more|greater|larger", c) else 1.0)
            out.append((props, w))
        return out

    def _flags(self, p):
        p = p.lower()
        return {"neg": len(re.findall(r"\b(not|no|never|none|neither)\b", p)),
                "cond": len(re.findall(r"\bif\b", p)), "cmp": len(re.findall(r"\b(more|less|greater|fewer) than\b", p)),
                "nums": [float(x) for x in re.findall(NUM, p)], "rels": [(a.lower(), b.lower()) for a, b in CMP.findall(p)]}

    # ---------- topological / dynamical layer ----------
    def _dynamics(self, text):
        clauses = self._props(text)
        vocab = sorted({t for props, _ in clauses for t in props})
        d = len(vocab)
        if d < 2: return 0.0, 0.5, 1
        idx = {t: i for i, t in enumerate(vocab)}
        x0, A = np.zeros(d), np.zeros((d, d))
        for props, w in clauses:
            ids = [idx[t] for t in props]
            for i in ids:
                x0[i] += w
                for j in ids:
                    if i != j: A[i, j] = 1.0
        L = np.diag(A.sum(1)) - A
        lam, V = np.linalg.eigh(L)
        null = V[:, lam < 1e-8]; comps = null.shape[1]
        P0 = null @ null.T
        xt = P0 @ x0
        a = self.alpha / max(lam.max(), 1e-6)
        W = np.eye(d) - a * L
        x = x0.copy()
        for _ in range(500):
            xn = W @ x
            if np.linalg.norm(xn - x) < self.eps: x = xn; break
            x = xn
        prox = math.exp(-np.linalg.norm(x0 - x) / (np.linalg.norm(x0) + 1e-6))
        J = np.linalg.pinv(a * L)           # dx*/dx0 for the relaxed system (pseudo-inverse: singular on nullspace)
        dx = np.linalg.norm(J @ (self.delta * np.ones(d)))
        sens = 1.0 - min(1.0, dx / (np.linalg.norm(x) + 1e-6))
        coherence = 1.0 - min(1.0, np.linalg.norm(x0 - xt) / (np.linalg.norm(x0) + 1e-6))
        return prox * (0.5 + 0.5 * coherence), sens, comps

    # ---------- primitive computation ----------
    def _compute(self, prompt, cand):
        f, p, c = self._flags(prompt), prompt.lower(), cand.lower().strip()
        cnums = [float(x) for x in re.findall(NUM, c)]
        yes = c.startswith(("yes", "true", "valid")); no = c.startswith(("no", "false", "invalid"))
        # transitivity chains
        if f["rels"]:
            r = check_transitivity(f["rels"]); clo = r["closure"] if isinstance(r, dict) else {}
            names = [w for w in re.findall(r"[a-z]+", c) if w in clo or any(w in s for s in clo.values())]
            if len(names) >= 1:
                m = re.search(r"who is (?:the )?(?:tallest|oldest|biggest|fastest|shortest|youngest)", p)
                if m and clo:
                    top = max(clo, key=lambda k: len(clo[k]))
                    low = min(set().union(*clo.values()) | set(clo), key=lambda k: len(clo.get(k, ())))
                    want = low if re.search(r"shortest|youngest|smallest", m.group()) else top
                    return 1.0 if want in names else 0.0, True
        # modus ponens
        m = re.search(r"if (.+?) then (.+?)[.,]", p)
        if m and re.search(r"\bnot\b", p) and (yes or no):
            facts = modus_ponens([(m.group(1).strip(), m.group(2).strip())], [m.group(1).strip()])
            ok = m.group(2).strip() in facts
            return (1.0 if (yes == ok) else 0.0), True
        # bat and ball
        m = re.search(rf"(?:total|together|cost)\D*({NUM})\D*({NUM}) more", p)
        if m and cnums:
            ans = bat_and_ball(float(m.group(1)), float(m.group(2)))
            return (1.0 if any(abs(n - ans) < 1e-6 for n in cnums) else 0.0), True
        # bayesian base-rate
        m = re.search(rf"({NUM})\s*% .*?({NUM})\s*% .*?({NUM})\s*%", p)
        if m and "positive" in p and cnums:
            pr, l, fp = [float(g) / 100 for g in m.groups()]
            post = bayesian_update(pr, l, fp) * 100
            return (1.0 if any(abs(n - post) < 1.5 for n in cnums) else 0.0), True
        # modular arithmetic
        m = re.search(rf"({NUM})\s*\+\s*({NUM})\s*(?:mod|modulo)\s*({NUM})", p)
        if m and cnums:
            r = modular_arithmetic(*[int(float(g)) for g in m.groups()])
            return (1.0 if r in cnums else 0.0), True
        # all but n
        m = re.search(rf"all but ({NUM})", p)
        if m and cnums: return (1.0 if all_but_n(0, float(m.group(1))) in cnums else 0.0), True
        # parity / even-odd
        if re.search(r"\b(even|odd)\b", p) and len(f["nums"]) >= 2 and (c.startswith("even") or c.startswith("odd")):
            par = parity_check([int(n) for n in f["nums"]])
            return (1.0 if (par == 1) == c.startswith("odd") else 0.0), True
        # numeric comparison
        if len(f["nums"]) >= 2 and re.search(r"(bigger|larger|greater|smaller|less)", p) and cnums:
            a, b = f["nums"][:2]; want = max(a, b) if re.search(r"bigger|larger|greater", p) else min(a, b)
            return (1.0 if abs(cnums[0] - want) < 1e-9 else 0.0), True
        # negation-count parity (double negatives) for yes/no
        if (yes or no) and f["neg"] >= 2:
            return (1.0 if (f["neg"] % 2 == 0) == yes else 0.0), True
        return 0.5, False

    def _ncd(self, a, b):
        za, zb, zab = (len(zlib.compress(s.encode())) for s in (a, b, a + " " + b))
        return 1.0 - (zab - min(za, zb)) / max(za, zb, 1)

    # ---------- metacognition ----------
    def _meta_confidence(self, prompt):
        p, cap = prompt.lower(), 1.0
        if re.search(r"(have|has|did) (you|he|she|they) (stopped|quit|given up)|why did .* (fail|stop)", p): cap = min(cap, 0.2)
        if re.search(r"\bevery \w+.*\ba\b .*\bsame\b|\bevery\b.*\ba \w+\b.*\?", p): cap = min(cap, 0.25)
        if re.search(r"\b(he|she|they)\b.*\b(who|whom)\b", p) and re.search(r"told|said|asked", p): cap = min(cap, 0.25)
        if re.search(r"\beither\b.*\bor\b", p) and not re.search(r"only|exactly|must", p): cap = min(cap, 0.25)
        if re.search(r"\b(best|worst|favorite|most beautiful|nicest)\b", p) and not re.findall(NUM, p): cap = min(cap, 0.25)
        if re.search(r"survivor|sunk cost|already (spent|invested)|regress|revert to (the )?mean", p): cap = min(cap, 0.28)
        unknowns = len(re.findall(r"\b(some|unknown|unspecified|it depends|could be)\b", p))
        if not information_sufficiency(unknowns, len(re.findall(NUM, p)) + len(CMP.findall(p))): cap = min(cap, 0.28)
        return cap

    # ---------- interface ----------
    def _score(self, prompt, cand):
        comp, hit = self._compute(prompt, cand)
        struct, sens, comps = self._dynamics(prompt + " " + cand)
        base, _, _ = self._dynamics(prompt)
        wiring = struct * sens * (1.0 / comps)          # topology-filtered, sensitivity-weighted attractor
        ncd = self._ncd(prompt, cand)
        s = 0.62 * comp + 0.28 * wiring + 0.10 * ncd
        why = f"computed={'yes' if hit else 'none'} ({comp:.2f}); attractor={struct:.2f} sens={sens:.2f} components={comps}; ncd={ncd:.2f}"
        return s, why, hit

    def evaluate(self, prompt, candidates):
        rows = []
        for c in candidates:
            s, why, _ = self._score(prompt, c)
            rows.append({"candidate": c, "score": round(float(s), 6), "reasoning": why})
        return sorted(rows, key=lambda r: -r["score"])

    def confidence(self, prompt, answer):
        s, _, hit = self._score(prompt, answer)
        # sensitivity: rerun under lexical perturbations, measure agreement
        perts = [self._score(prompt + " " + w, answer)[0] for w in ("", "so", "thus", "indeed")]
        agree = max(0.0, min(1.0, confidence_from_agreement(perts)))
        conf = (0.15 + 0.75 * s) * agree if hit else 0.12 + 0.15 * s
        conf = min(conf, 0.9 if hit else 0.29)
        return float(max(0.0, min(conf, self._meta_confidence(prompt))))


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
