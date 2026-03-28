"""Abductive-Ergodic Theory-of-Mind Scorer v2.
Concepts: Abductive Reasoning x Ergodic Theory x Theory of Mind
Structural parsing PRIMARY; NCD capped at 15%.
"""
import hashlib, math, re, zlib


class ReasoningTool:
    def __init__(self):
        self._seed = 42

    def _hash01(self, s: str) -> float:
        return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

    def _tokens(self, s: str) -> set:
        return set(re.findall(r"[a-z0-9]+", s.lower()))

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), 6))

    def _ncd(self, a: str, b: str) -> float:
        ca, cb, cab = self._c(a), self._c(b), self._c(a + " \n " + b)
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _extract_negations(self, t: str) -> list:
        return re.findall(r"\b(?:not|never|no|neither|cannot|can't|won't|doesn't|don't|isn't|aren't|wasn't|weren't)\b", t, re.I)

    def _extract_comparatives(self, t: str) -> list:
        pairs = []
        for m in re.finditer(r"(\S+)\s+(?:is\s+)?(?:larger|greater|bigger|more|higher|taller|faster|better|older)\s+than\s+(\S+)", t, re.I):
            pairs.append((m.group(1).lower().strip(".,;:"), m.group(2).lower().strip(".,;:")))
        for m in re.finditer(r"(\S+)\s+(?:is\s+)?(?:less|smaller|lower|shorter|slower|worse|younger)\s+than\s+(\S+)", t, re.I):
            pairs.append((m.group(2).lower().strip(".,;:"), m.group(1).lower().strip(".,;:")))
        return pairs

    def _extract_conditionals(self, t: str) -> list:
        return [(m.group(1).strip().lower(), m.group(2).strip().lower())
                for m in re.finditer(r"[Ii]f\s+(.+?)[,.]?\s+(?:then\s+)?(.+?)(?:\.|$)", t)]

    def _extract_numbers(self, t: str) -> list:
        return [float(m.group()) for m in re.finditer(r"\b\d+\.?\d*\b", t)]

    def _abductive_score(self, prompt: str, cand: str) -> tuple:
        pt, ct = self._tokens(prompt), self._tokens(cand)
        if not pt or not ct:
            return 0.0, "structural: no tokens"
        coverage = len(pt & ct) / len(pt | ct)
        parsimony = math.exp(-0.5 * abs(1.0 - len(ct) / len(pt)))
        return coverage * parsimony, f"structural: cov={coverage:.2f} pars={parsimony:.2f}"

    def _structural_score(self, prompt: str, cand: str) -> tuple:
        p_lo, c_lo = prompt.lower(), cand.lower().strip()
        score, checks, notes = 0.0, 0, []
        comps = self._extract_comparatives(prompt)
        if comps:
            checks += 1
            ordering = {}
            for a, b in comps:
                ordering.setdefault(a, set()).add(b)
            if re.search(r"(?:who|which|what)\s+(?:is\s+)?(?:larg|tall|great|bigg|most|best)", p_lo):
                top = max(ordering, key=lambda x: len(ordering.get(x, set())))
                score += 1.0 if top in c_lo else -0.5
                notes.append(f"comp:top={top}")
        negs = self._extract_negations(prompt)
        if negs and "?" in prompt:
            checks += 1
            if c_lo.startswith("yes"): score -= 0.5
            notes.append("negation")
        for ant, con in self._extract_conditionals(prompt):
            checks += 1
            if any(n in con for n in ["not", "never", "no"]):
                score += 1.0 if c_lo.startswith("no") else -0.5
                notes.append("modus_tollens")
        for m in re.finditer(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)", prompt):
            checks += 1
            agent, patient = m.group(1).lower(), m.group(3).lower()
            if re.search(r"who.+(?:was|were).+\w+ed", p_lo):
                score += 1.0 if patient in c_lo else -0.5
            elif re.search(r"who.+\w+ed", p_lo):
                score += 1.0 if agent in c_lo else -0.5
        if checks == 0:
            return 0.0, "structural: no constraints"
        normed = max(-1.0, min(1.0, score / max(checks, 1)))
        return normed, "structural: " + "; ".join(notes) if notes else "structural: chk=" + str(checks)

    def _tom_reweight(self, prompt: str, cand: str) -> float:
        w = [1.0 if self._extract_negations(prompt) and self._extract_negations(cand) else 0.5,
             1.0 if self._extract_numbers(prompt) and self._extract_numbers(cand) else 0.5,
             1.0 if self._extract_conditionals(prompt) else 0.5]
        return sum(w) / len(w)

    def _ergodic_mean(self, prompt: str, cand: str, steps: int = 15) -> float:
        abd, _ = self._abductive_score(prompt, cand)
        cur, vals = abd, []
        for t in range(steps):
            noise = self._hash01(f"{prompt}::{cand}::{t}") * 0.2 - 0.1
            cur = max(0.0, min(1.0, cur * (0.9 + 0.2 * self._hash01(str(t))) + noise))
            vals.append(cur)
        return sum(vals) / len(vals) if vals else 0.0

    def evaluate(self, prompt: str, candidates: list) -> list:
        if not isinstance(prompt, str) or not isinstance(candidates, list) or not candidates:
            return []
        results = []
        for cand in candidates:
            if not isinstance(cand, str): continue
            struct_sc, struct_r = self._structural_score(prompt, cand)
            abd_sc, abd_r = self._abductive_score(prompt, cand)
            tom_w = self._tom_reweight(prompt, cand)
            erg_sc = self._ergodic_mean(prompt, cand)
            struct_norm = (struct_sc + 1.0) / 2.0
            exec_sc = 0.35 * struct_norm + 0.30 * abd_sc + 0.10 * tom_w + 0.10 * erg_sc
            ncd_val = self._ncd(prompt, cand)
            ncd_sc = (1.0 - ncd_val) * 0.15
            score = max(0.0, min(1.0, exec_sc + ncd_sc))
            reasoning = f"execution: struct={struct_sc:.2f} abd={abd_sc:.2f} tom={tom_w:.2f} erg={erg_sc:.2f} | {struct_r} | fallback:ncd={ncd_val:.3f}"
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        results.sort(key=lambda r: r["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]: r["reasoning"] += " | metacognitive: TIE (<5% gap)"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str): return 0.0
        null = "This is a null baseline answer with no information."
        res = self.evaluate(prompt, [answer, null])
        if not res: return 0.0
        ans_sc = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_sc = next((r["score"] for r in res if r["candidate"] == null), 0.0)
        return float(max(0.0, min(1.0, 0.5 + (ans_sc - null_sc) * 0.5)))
