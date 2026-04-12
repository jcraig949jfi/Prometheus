"""Ergodic FEP Reinforcement-Learning Scorer v2.
Concepts: Ergodic Theory x Free Energy Principle x Reinforcement Learning
Structural parsing PRIMARY; NCD capped at 15%.
"""
import math, re, zlib
import numpy as np


class ReasoningTool:
    def __init__(self):
        self._rng = np.random.default_rng(42)
        self._gamma = 0.9

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), 6))

    def _ncd(self, a: str, b: str) -> float:
        ca, cb, cab = self._c(a), self._c(b), self._c(a + " \n " + b)
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

    def _features(self, text: str) -> np.ndarray:
        tl = text.lower()
        nums = re.findall(r"-?\d+\.?\d*", text)
        f_num = np.tanh(float(nums[0]) / 100.0) if nums else 0.0
        neg_w = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        f_neg = sum(1 for w in neg_w if re.search(r'\b' + w + r'\b', tl)) / 6.0
        comp_w = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'larger', 'smaller']
        f_comp = sum(1 for w in comp_w if w in tl) / 8.0
        cond_w = ['if', 'then', 'else', 'when', 'unless']
        f_cond = sum(1 for w in cond_w if w in tl) / 5.0
        return np.array([len(text) / 1000.0, f_num, f_neg, f_comp, f_cond])

    def _structural_score(self, prompt: str, cand: str) -> tuple:
        p_lo, c_lo = prompt.lower(), cand.lower().strip()
        score, checks, notes = 0.0, 0, []
        m = re.search(r"(?:is\s+)([\d.]+)\s+(?:larger|greater|more|higher)\s+than\s+([\d.]+)", p_lo)
        if m:
            checks += 1
            try:
                a, b = float(m.group(1)), float(m.group(2))
                score += 1.0 if c_lo.startswith("yes" if a > b else "no") else -1.0
                notes.append(f"numeric:{a}vs{b}")
            except ValueError: pass
        comps = []
        for m2 in re.finditer(r"(\S+)\s+(?:is\s+)?(?:larger|greater|bigger|more|higher|taller|faster)\s+than\s+(\S+)", p_lo):
            comps.append((m2.group(1).strip(".,;:"), m2.group(2).strip(".,;:")))
        for m2 in re.finditer(r"(\S+)\s+(?:is\s+)?(?:less|smaller|lower|shorter|slower)\s+than\s+(\S+)", p_lo):
            comps.append((m2.group(2).strip(".,;:"), m2.group(1).strip(".,;:")))
        if comps:
            checks += 1
            ordering = {}
            for a, b in comps: ordering.setdefault(a, set()).add(b)
            changed = True
            while changed:
                changed = False
                for a in list(ordering):
                    for b in list(ordering.get(a, [])):
                        for cc in list(ordering.get(b, [])):
                            if cc not in ordering.get(a, set()):
                                ordering.setdefault(a, set()).add(cc); changed = True
            if re.search(r"(?:who|which|what)\s+(?:is\s+)?(?:larg|great|bigg|tall|most|best|fast)", p_lo):
                top = max(ordering, key=lambda x: len(ordering.get(x, set())))
                score += 1.0 if top in c_lo else -0.5
                notes.append(f"comp:top={top}")
        negs = re.findall(r"\b(?:not|never|no|cannot|can't|won't|doesn't|don't|isn't|aren't)\b", p_lo)
        if negs and "?" in prompt:
            checks += 1
            if c_lo.startswith("yes"): score -= 0.5
            notes.append("negation")
        for m3 in re.finditer(r"[Ii]f\s+(.+?)[,.]?\s+(?:then\s+)?(.+?)(?:\.|$)", prompt):
            checks += 1
            if any(n in m3.group(2).lower() for n in ["not", "never", "no"]):
                score += 1.0 if c_lo.startswith("no") else -0.5
                notes.append("modus_tollens")
        for m4 in re.finditer(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)", prompt):
            checks += 1
            agent, patient = m4.group(1).lower(), m4.group(3).lower()
            if re.search(r"who.+(?:was|were).+\w+ed", p_lo):
                score += 1.0 if patient in c_lo else -0.5
            elif re.search(r"who.+\w+ed", p_lo):
                score += 1.0 if agent in c_lo else -0.5
        if checks == 0: return 0.0, "structural: no constraints"
        normed = max(-1.0, min(1.0, score / max(checks, 1)))
        return normed, "structural: " + "; ".join(notes) if notes else "structural: chk=" + str(checks)

    def _ergodic_potential(self, prompt: str, cand: str, steps: int = 12) -> float:
        xp, xc = self._features(prompt), self._features(cand)
        diff = xc - xp
        pot = -float(np.dot(diff, diff))
        traj, vel = pot, self._rng.normal(0, 0.1, size=xc.shape)
        for _ in range(steps):
            grad = -2.0 * (xc - xp)
            vel = 0.9 * vel + grad + self._rng.normal(0, 0.01, size=xc.shape)
            xc = xc + vel * 0.1
            traj += -float(np.dot(xc - xp, xc - xp))
        return traj / (steps + 1)

    def _free_energy(self, prompt: str, cand: str) -> float:
        xp, xc = self._features(prompt), self._features(cand)
        surprise = float(np.sum(np.abs(xc - xp)))
        p_safe = np.clip(np.abs(xc), 1e-9, 1 - 1e-9)
        entropy = -float(np.sum(p_safe * np.log(p_safe)))
        return surprise - entropy

    def _td_reward(self, prompt: str, cand: str) -> float:
        """Cumulative TD-like reward over structural features."""
        struct_sc, _ = self._structural_score(prompt, cand)
        xp, xc = self._features(prompt), self._features(cand)
        n = len(xp)
        V, total = np.zeros(n + 1), 0.0
        for t in range(n):
            r_t = 1.0 - abs(xp[t] - xc[t]) / (abs(xp[t]) + abs(xc[t]) + 1e-9)
            V[t] = r_t + self._gamma * V[t + 1] if t < n - 1 else r_t
            total += (self._gamma ** t) * r_t
        total += struct_sc * 0.5
        return float(np.tanh(total / n))

    def evaluate(self, prompt: str, candidates: list) -> list:
        if not isinstance(prompt, str) or not isinstance(candidates, list) or not candidates:
            return []
        results = []
        for cand in candidates:
            if not isinstance(cand, str): continue
            struct_sc, struct_r = self._structural_score(prompt, cand)
            struct_norm = (struct_sc + 1.0) / 2.0
            erg_norm = 1.0 / (1.0 + math.exp(-self._ergodic_potential(prompt, cand) - 1.0))
            fe_norm = 1.0 / (1.0 + math.exp(self._free_energy(prompt, cand) - 1.0))
            td = (self._td_reward(prompt, cand) + 1.0) / 2.0
            exec_sc = 0.40 * struct_norm + 0.20 * td + 0.10 * fe_norm + 0.15 * erg_norm
            ncd_val = self._ncd(prompt, cand)
            score = max(0.0, min(1.0, exec_sc + (1.0 - ncd_val) * 0.15))
            reasoning = (f"execution: struct={struct_sc:.2f} td={td:.3f} FEP={fe_norm:.3f} "
                         f"erg={erg_norm:.3f} | {struct_r} | fallback:ncd={ncd_val:.3f}")
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        results.sort(key=lambda r: r["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]: r["reasoning"] += " | metacognitive: TIE (<5% gap)"
        if results and "structural: no constraints" in results[0]["reasoning"]:
            results[0]["reasoning"] += " | metacognitive: structural parse failed"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str): return 0.0
        null = "This is a null baseline answer with no relevant information."
        res = self.evaluate(prompt, [answer, null])
        if not res: return 0.0
        ans_sc = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_sc = next((r["score"] for r in res if r["candidate"] == null), 0.0)
        return float(max(0.0, min(1.0, 0.5 + (ans_sc - null_sc) * 0.5)))
