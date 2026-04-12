"""Thermodynamic Gene-Regulatory Active-Inference Scorer v2.
Concepts: Active Inference x Gene Regulatory Networks x Thermodynamics
Structural parsing PRIMARY; NCD capped at 15%.
"""
import math, re, zlib
import numpy as np


class ReasoningTool:
    def __init__(self):
        self._prior = 0.6
        self._temp = 0.5
        self._beta = 2.0  # Boltzmann inverse temperature

    def _c(self, t: str) -> int:
        return len(zlib.compress(t.encode("utf-8"), 6))

    def _ncd(self, a: str, b: str) -> float:
        ca, cb, cab = self._c(a), self._c(b), self._c(a + " \n " + b)
        d = max(ca, cb)
        return (cab - min(ca, cb)) / d if d else 1.0

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
            elif re.search(r"(?:who|which|what)\s+(?:is\s+)?(?:small|short|least|slow|worst)", p_lo):
                all_lesser = set()
                for v in ordering.values(): all_lesser.update(v)
                bottom_set = all_lesser - set(ordering.keys())
                if bottom_set:
                    bottom = next(iter(bottom_set))
                    score += 1.0 if bottom in c_lo else -0.5
                    notes.append(f"comp:bottom={bottom}")
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

    # -- gene regulatory network ------------------------------------------

    def _build_grn(self, text: str) -> tuple:
        raw = re.split(r'[.,;]', text.lower())
        nodes = [n.strip() for n in raw if len(n.strip()) > 3]
        if not nodes: nodes = [text.lower()[:200]]
        n = len(nodes)
        A, biases = np.zeros((n, n)), np.full(n, self._prior)
        neg_pat = re.compile(r'\b(not|no|never|without|false)\b')
        cond_pat = re.compile(r'\b(if|then|implies|causes|leads to)\b')
        num_pat = re.compile(r'(\d+\.?\d*)')
        for i, node in enumerate(nodes):
            if neg_pat.search(node): biases[i] -= 0.4
            if re.search(r'\b(greater|less|more|fewer|before|after)\b', node): biases[i] += 0.1
            nums = num_pat.findall(node)
            if len(nums) >= 2:
                try:
                    v1, v2 = float(nums[0]), float(nums[1])
                    if ("less" in node or "before" in node) and v1 >= v2: biases[i] -= 0.5
                    elif ("greater" in node or "after" in node) and v1 <= v2: biases[i] -= 0.5
                except (ValueError, IndexError): pass
            for j, other in enumerate(nodes):
                if i == j: continue
                if cond_pat.search(node) and (other in node or node in other): A[j, i] = 0.5
                if neg_pat.search(node) and (other in node or node in other): A[j, i] = -0.8
        return nodes, A, biases

    def _propagate_grn(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        p = np.full(A.shape[0], self._prior)
        for _ in range(10):
            p_new = 1.0 / (1.0 + np.exp(-(A.T @ p + b) / self._temp))
            if np.max(np.abs(p_new - p)) < 1e-3: break
            p = p_new
        return p

    def _thermo_energy(self, p: np.ndarray, A: np.ndarray) -> float:
        p_safe = np.clip(p, 1e-9, 1 - 1e-9)
        surprise = float(np.sum(self._prior * np.abs(p_safe - self._prior)))
        entropy = -float(np.sum(p_safe * np.log(p_safe)))
        epistemic = 0.1 * float(np.mean(np.var(A, axis=0)))
        return surprise - entropy + epistemic

    def _active_inference_score(self, prompt: str, cand: str) -> tuple:
        nodes, A, b = self._build_grn(f"{prompt} {cand}")
        if not nodes: return 0.0, "execution: empty GRN"
        p_state = self._propagate_grn(A, b)
        F = self._thermo_energy(p_state, A)
        return -F, f"execution: F={F:.4f} nodes={len(nodes)}"

    def evaluate(self, prompt: str, candidates: list) -> list:
        if not isinstance(prompt, str) or not isinstance(candidates, list) or not candidates:
            return []
        raw = []
        for cand in candidates:
            if not isinstance(cand, str): continue
            struct_sc, struct_r = self._structural_score(prompt, cand)
            ai_sc, ai_r = self._active_inference_score(prompt, cand)
            raw.append((cand, struct_sc, ai_sc, struct_r, ai_r))
        if not raw: return []
        energies = np.array([r[2] for r in raw])
        e_shifted = energies - np.max(energies)
        boltz = np.exp(self._beta * e_shifted)
        boltz /= (np.sum(boltz) + 1e-12)
        results = []
        for idx, (cand, struct_sc, ai_sc, struct_r, ai_r) in enumerate(raw):
            struct_norm = (struct_sc + 1.0) / 2.0
            bp = float(boltz[idx])
            exec_sc = 0.40 * struct_norm + 0.25 * bp + 0.10 * (1.0 / (1.0 + math.exp(-ai_sc))) + 0.10 * bp
            ncd_val = self._ncd(prompt, cand)
            score = max(0.0, min(1.0, exec_sc + (1.0 - ncd_val) * 0.15))
            reasoning = (f"{ai_r} | {struct_r} | execution: boltz={bp:.3f} struct={struct_sc:.2f} "
                         f"| fallback:ncd={ncd_val:.3f}")
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        results.sort(key=lambda r: r["score"], reverse=True)
        if len(results) >= 2 and results[0]["score"] - results[1]["score"] < 0.05:
            for r in results[:2]: r["reasoning"] += " | metacognitive: TIE (<5% gap)"
        if results and "structural: no constraints" in results[0]["reasoning"]:
            results[0]["reasoning"] += " | metacognitive: structural parse failed"
        if results and results[0]["score"] < 0.4:
            results[0]["reasoning"] += " | metacognitive: top score <0.4, low confidence"
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        if not isinstance(prompt, str) or not isinstance(answer, str): return 0.0
        null = "This is a null baseline answer with no relevant information."
        res = self.evaluate(prompt, [answer, null])
        if not res: return 0.0
        ans_sc = next((r["score"] for r in res if r["candidate"] == answer), 0.0)
        null_sc = next((r["score"] for r in res if r["candidate"] == null), 0.0)
        return float(max(0.0, min(1.0, 0.5 + (ans_sc - null_sc) * 0.5)))
