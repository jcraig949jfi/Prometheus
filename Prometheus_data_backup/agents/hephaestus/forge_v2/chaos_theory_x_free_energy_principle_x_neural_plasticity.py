"""Chaotic Free-Energy Plasticity Scorer v2.
Concepts: Chaos Theory x Free Energy Principle x Neural Plasticity
Structural parsing PRIMARY; NCD capped at 15%.
"""

import math
import re
import zlib
import numpy as np


class ReasoningTool:
    def __init__(self):
        self._dim = 32
        rng = np.random.RandomState(42)
        W = rng.randn(self._dim, self._dim)
        eigmax = np.max(np.abs(np.linalg.eigvals(W)))
        self._W = W * (1.15 / eigmax) if eigmax > 0 else W
        self._prior = rng.randn(self._dim) * 0.1

    # -- helpers ----------------------------------------------------------

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), 6))

    def _ncd(self, a: str, b: str) -> float:
        ca, cb = self._c(a), self._c(b)
        cab = self._c(a + " \n " + b)
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _embed(self, text: str) -> np.ndarray:
        v = np.zeros(self._dim)
        if not text:
            return v
        for i, ch in enumerate(text):
            v[ord(ch) % self._dim] += 1.0 / (i + 1)
        n = np.linalg.norm(v) + 1e-9
        return v * (5.0 / n)

    # -- chaotic reservoir ------------------------------------------------

    def _reservoir(self, x: np.ndarray, steps: int = 5) -> np.ndarray:
        s = np.zeros(self._dim)
        for _ in range(steps):
            s = np.tanh(self._W @ s + x * 0.5)
        return s

    # -- free energy computation ------------------------------------------

    def _free_energy(self, state: np.ndarray, target: np.ndarray) -> float:
        accuracy = 0.5 * np.sum((state - target) ** 2)
        complexity = 0.5 * np.sum((state - self._prior) ** 2) * 0.1
        return float(accuracy + complexity)

    # -- neural plasticity (Hebbian readout) ------------------------------

    def _plastic_score(self, state: np.ndarray, target: np.ndarray) -> float:
        dot = float(np.dot(state, target))
        norms = (np.linalg.norm(state) + 1e-9) * (np.linalg.norm(target) + 1e-9)
        return dot / norms  # cosine similarity in [-1,1]

    # -- structural parsing -----------------------------------------------

    def _structural_score(self, prompt: str, cand: str) -> tuple:
        p_lo, c_lo = prompt.lower(), cand.lower().strip()
        score, checks, notes = 0.0, 0, []

        # negation scope
        negs = re.findall(r"\b(?:not|never|no|cannot|can't|won't|doesn't|don't|isn't|aren't)\b", p_lo)
        if negs and "?" in prompt:
            checks += 1
            if c_lo.startswith("yes"):
                score -= 0.5
            notes.append("negation")

        # comparatives
        comps = []
        for m in re.finditer(r"(\S+)\s+(?:is\s+)?(?:larger|greater|more|higher|taller|faster)\s+than\s+(\S+)", p_lo):
            comps.append((m.group(1).strip(".,;:"), m.group(2).strip(".,;:")))
        for m in re.finditer(r"(\S+)\s+(?:is\s+)?(?:less|smaller|lower|shorter|slower)\s+than\s+(\S+)", p_lo):
            comps.append((m.group(2).strip(".,;:"), m.group(1).strip(".,;:")))
        if comps:
            checks += 1
            ordering = {}
            for a, b in comps:
                ordering.setdefault(a, set()).add(b)
            if re.search(r"(?:who|which|what)\s+(?:is\s+)?(?:larg|great|bigg|tall|most|best)", p_lo):
                top = max(ordering, key=lambda x: len(ordering.get(x, set())))
                score += 1.0 if top in c_lo else -0.5
                notes.append(f"comp:top={top}")

        # conditionals
        for m in re.finditer(r"[Ii]f\s+(.+?)[,.]?\s+(?:then\s+)?(.+?)(?:\.|$)", prompt):
            ant, con = m.group(1).lower(), m.group(2).lower()
            checks += 1
            if any(n in con for n in ["not", "never"]):
                score += 1.0 if c_lo.startswith("no") else -0.5
                notes.append("modus_tollens")

        # numerics
        p_nums = [float(x.group()) for x in re.finditer(r"\b\d+\.?\d*\b", p_lo)]
        c_nums = [float(x.group()) for x in re.finditer(r"\b\d+\.?\d*\b", c_lo)]
        if len(p_nums) >= 2 and c_nums:
            checks += 1
            if re.search(r"(?:larger|greater|more|bigger)", p_lo):
                expected = max(p_nums)
                score += 1.0 if c_nums[0] == expected else -0.5
                notes.append("numeric_comp")

        # subject-object
        for m in re.finditer(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)", prompt):
            checks += 1
            agent, patient = m.group(1).lower(), m.group(3).lower()
            if re.search(r"who.+was.+\w+ed", p_lo):
                score += 1.0 if patient in c_lo else -0.5
            elif re.search(r"who.+\w+ed", p_lo):
                score += 1.0 if agent in c_lo else -0.5

        if checks == 0:
            return 0.0, "structural: no constraints"
        normed = max(-1.0, min(1.0, score / max(checks, 1)))
        return normed, "structural: " + "; ".join(notes)

    # -- public interface -------------------------------------------------

    def evaluate(self, prompt: str, candidates: list) -> list:
        if not isinstance(prompt, str) or not isinstance(candidates, list):
            return []
        if not candidates:
            return []

        p_vec = self._embed(prompt)
        p_state = self._reservoir(p_vec)

        results = []
        for cand in candidates:
            if not isinstance(cand, str):
                continue
            c_vec = self._embed(cand)
            c_state = self._reservoir(c_vec)

            # chaos + FEP
            F = self._free_energy(c_state, p_state)
            fep_sc = 1.0 / (1.0 + math.exp(F - 2.0))

            # plasticity (Hebbian cosine)
            plast = (self._plastic_score(c_state, p_state) + 1.0) / 2.0

            # structural
            struct_sc, struct_r = self._structural_score(prompt, cand)
            struct_norm = (struct_sc + 1.0) / 2.0

            # combine: structural 40%, FEP 20%, plasticity 15%, execution 10%
            exec_sc = 0.40 * struct_norm + 0.20 * fep_sc + 0.15 * plast + 0.10 * (fep_sc * plast)

            # NCD fallback (max 15%)
            ncd_val = self._ncd(prompt, cand)
            ncd_sc = (1.0 - ncd_val) * 0.15

            score = max(0.0, min(1.0, exec_sc + ncd_sc))
            reasoning = (
                f"execution: FEP={fep_sc:.3f} plast={plast:.3f} struct={struct_sc:.2f} | "
                f"{struct_r} | fallback:ncd={ncd_val:.3f}"
            )
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})

        results.sort(key=lambda r: r["score"], reverse=True)

        # metacognitive: flag ties
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]:
                r["reasoning"] += " | metacognitive: TIE (<5% gap)"
        # metacognitive: re-examine top for internal consistency
        if results:
            top = results[0]
            if "structural: no constraints" in top["reasoning"]:
                top["reasoning"] += " | metacognitive: structural parse failed, low confidence"

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str):
            return 0.0
        null = "This is a null baseline answer with no relevant content."
        res = self.evaluate(prompt, [answer, null])
        if not res:
            return 0.0
        ans_sc = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_sc = next((r["score"] for r in res if r["candidate"] == null), 0.0)
        delta = ans_sc - null_sc
        return float(max(0.0, min(1.0, 0.5 + delta * 0.5)))
