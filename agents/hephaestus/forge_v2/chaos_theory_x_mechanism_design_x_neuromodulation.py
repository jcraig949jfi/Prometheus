"""Chaotic Neuromodulated Incentive-Compatible Scorer v2.
Concepts: Chaos Theory x Mechanism Design x Neuromodulation
Structural parsing PRIMARY; NCD capped at 15%.
"""
import math, re, zlib


class ReasoningTool:
    def __init__(self):
        self._r = 3.9

    def _logistic(self, x: float, steps: int = 10) -> float:
        for _ in range(steps): x = self._r * x * (1.0 - x)
        return x

    def _seed_float(self, text: str) -> float:
        h = zlib.crc32(text.encode()) & 0xFFFFFFFF
        return 0.1 + 0.8 * (h / 0xFFFFFFFF)

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

    def _structural_score(self, prompt: str, cand: str) -> tuple:
        p_lo, c_lo = prompt.lower(), cand.lower().strip()
        score, checks, notes = 0.0, 0, []
        negs = self._extract_negations(prompt)
        if negs and "?" in prompt:
            checks += 1
            if c_lo.startswith("yes"): score -= 0.5
            notes.append("negation")
        comps = self._extract_comparatives(prompt)
        if comps:
            checks += 1
            ordering = {}
            for a, b in comps: ordering.setdefault(a, set()).add(b)
            changed = True
            while changed:
                changed = False
                for a in list(ordering):
                    for b in list(ordering.get(a, [])):
                        for c in list(ordering.get(b, [])):
                            if c not in ordering.get(a, set()):
                                ordering.setdefault(a, set()).add(c); changed = True
            if re.search(r"(?:who|which|what)\s+(?:is\s+)?(?:larg|great|bigg|tall|most|best|fast)", p_lo):
                top = max(ordering, key=lambda x: len(ordering.get(x, set())))
                score += 1.0 if top in c_lo else -0.5
                notes.append(f"comp:top={top}")
            elif re.search(r"(?:who|which|what)\s+(?:is\s+)?(?:small|short|least|slow|worst)", p_lo):
                all_lesser = set()
                for v in ordering.values(): all_lesser.update(v)
                bottom_set = all_lesser - set(ordering.keys())
                if bottom_set:
                    bottom = next(iter(bottom_set))
                    score += 1.0 if bottom in c_lo else -0.5
                    notes.append(f"comp:bottom={bottom}")
        for ant, con in self._extract_conditionals(prompt):
            checks += 1
            if any(n in con for n in ["not", "never", "no"]):
                score += 1.0 if c_lo.startswith("no") else -0.5
                notes.append("modus_tollens")
        m = re.search(r"(?:is\s+)([\d.]+)\s+(?:larger|greater|more|higher)\s+than\s+([\d.]+)", p_lo)
        if m:
            checks += 1
            try:
                a, b = float(m.group(1)), float(m.group(2))
                score += 1.0 if c_lo.startswith("yes" if a > b else "no") else -1.0
                notes.append(f"numeric:{a}vs{b}")
            except ValueError: pass
        for m in re.finditer(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)", prompt):
            checks += 1
            agent, patient = m.group(1).lower(), m.group(3).lower()
            if re.search(r"who.+(?:was|were).+\w+ed", p_lo):
                score += 1.0 if patient in c_lo else -0.5
            elif re.search(r"who.+\w+ed", p_lo):
                score += 1.0 if agent in c_lo else -0.5
        if checks == 0: return 0.0, "structural: no constraints"
        normed = max(-1.0, min(1.0, score / max(checks, 1)))
        return normed, "structural: " + "; ".join(notes) if notes else "structural: chk=" + str(checks)

    def _incentive_score(self, prompt: str, cand: str) -> float:
        """Brier-like proper scoring rule: rewards truthful alignment."""
        p_tok = set(re.findall(r"[a-z0-9]+", prompt.lower()))
        c_tok = set(re.findall(r"[a-z0-9]+", cand.lower()))
        if not p_tok: return 0.5
        overlap = len(p_tok & c_tok) / len(p_tok)
        len_ratio = len(c_tok) / max(len(p_tok), 1)
        length_penalty = 1.0 - min(1.0, max(0.0, abs(len_ratio - 1.0) / 2.0))
        return overlap * length_penalty

    def _neuromod_chaos(self, prompt: str, cand: str) -> tuple:
        x = self._logistic(self._seed_float(prompt + cand), steps=5)
        struct_sc, _ = self._structural_score(prompt, cand)
        delta = 1.0 - (struct_sc + 1.0) / 2.0
        return (x - 0.5) * delta * 0.15, delta

    def evaluate(self, prompt: str, candidates: list) -> list:
        if not isinstance(prompt, str) or not isinstance(candidates, list) or not candidates:
            return []
        results = []
        for cand in candidates:
            if not isinstance(cand, str): continue
            struct_sc, struct_r = self._structural_score(prompt, cand)
            struct_norm = (struct_sc + 1.0) / 2.0
            incent = self._incentive_score(prompt, cand)
            chaos_pert, delta = self._neuromod_chaos(prompt, cand)
            exec_sc = 0.45 * struct_norm + 0.25 * incent + 0.05 * (0.5 + chaos_pert) + 0.10 * (1.0 - delta)
            ncd_val = self._ncd(prompt, cand)
            ncd_sc = (1.0 - ncd_val) * 0.15
            score = max(0.0, min(1.0, exec_sc + ncd_sc))
            reasoning = (f"execution: struct={struct_sc:.2f} incentive={incent:.2f} delta={delta:.2f} "
                         f"chaos={chaos_pert:.3f} | {struct_r} | fallback:ncd={ncd_val:.3f}")
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        results.sort(key=lambda r: r["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]: r["reasoning"] += " | metacognitive: TIE (<5% gap)"
        if results and "structural: no constraints" in results[0]["reasoning"]:
            results[0]["reasoning"] += " | metacognitive: structural parse failed"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str): return 0.0
        null = "This is a null baseline answer with no useful content."
        res = self.evaluate(prompt, [answer, null])
        if not res: return 0.0
        ans_sc = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_sc = next((r["score"] for r in res if r["candidate"] == null), 0.0)
        return float(max(0.0, min(1.0, 0.5 + (ans_sc - null_sc) * 0.5)))
