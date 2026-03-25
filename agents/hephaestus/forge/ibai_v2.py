"""IBAI v2 — Active Inference with NCD + Structural Analysis.

Active Inference framework with three signal sources:
  1. NCD (compression distance) for structural similarity
  2. Local co-occurrence SVD for distributional semantics
  3. Structural constraint checking (negation, ordering, conditionals)

Score = pragmatic_value + epistemic_value - surprise
  - Pragmatic: how well does the candidate match prompt constraints?
  - Epistemic: does the candidate reduce uncertainty (informative, not generic)?
  - Surprise: NCD-based structural distance

Concepts: Information Theory x Active Inference x Free Energy Principle
"""

import re
import zlib
import numpy as np


class ReasoningTool:
    def __init__(self):
        self._level = 6

    # -- NCD ---------------------------------------------------------------

    def _c(self, text: str) -> int:
        return len(zlib.compress(text.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " \n " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    # -- Structural constraint extraction ----------------------------------

    def _extract_comparatives(self, text: str) -> list:
        """Returns list of (greater, lesser) string pairs."""
        results = []
        for m in re.finditer(
            r"(\S+)\s+(?:is\s+)?(?:larger|greater|bigger|more|higher|taller|"
            r"heavier|faster|better|older)\s+than\s+(\S+)",
            text, re.IGNORECASE
        ):
            results.append((m.group(1).strip(".,;:?").lower(),
                            m.group(2).strip(".,;:?").lower()))
        for m in re.finditer(
            r"(\S+)\s+(?:is\s+)?(?:less|smaller|lower|shorter|lighter|slower|"
            r"worse|younger)\s+than\s+(\S+)",
            text, re.IGNORECASE
        ):
            results.append((m.group(2).strip(".,;:?").lower(),
                            m.group(1).strip(".,;:?").lower()))
        return results

    def _extract_conditionals(self, text: str) -> list:
        results = []
        for m in re.finditer(r"[Ii]f\s+(.+?)[,.]?\s+(?:then\s+)?(.+?)(?:\.|$)", text):
            results.append((m.group(1).strip().lower(), m.group(2).strip().lower()))
        return results

    def _has_negation(self, text: str) -> bool:
        return bool(re.search(
            r"\b(?:not|never|no|neither|nor|cannot|can't|won't|"
            r"doesn't|don't|isn't|aren't|wasn't|weren't)\b",
            text, re.IGNORECASE
        ))

    def _extract_subject_object(self, text: str) -> list:
        results = []
        for m in re.finditer(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)", text):
            results.append((m.group(1).lower(), m.group(2).lower(), m.group(3).lower()))
        return results

    def _build_ordering(self, comparatives: list) -> dict:
        greater_than = {}
        for a, b in comparatives:
            greater_than.setdefault(a, set()).add(b)
        changed = True
        while changed:
            changed = False
            for a in list(greater_than):
                for b in list(greater_than.get(a, [])):
                    for c in list(greater_than.get(b, [])):
                        if c not in greater_than.get(a, set()):
                            greater_than.setdefault(a, set()).add(c)
                            changed = True
        return greater_than

    # -- Constraint consistency score --------------------------------------

    def _try_numeric_eval(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """Try to solve numeric comparison directly. Returns (score, had_signal)."""
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip()

        # "Is X larger/greater than Y?" -> compare floats
        m = re.search(r"(?:is\s+)([\d.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.]+)", p_lower)
        if m:
            try:
                a, b = float(m.group(1)), float(m.group(2))
                correct = "yes" if a > b else "no"
                if c_lower.startswith(correct):
                    return 1.0, True
                return -1.0, True
            except ValueError:
                pass

        # "X is less than Y. Which is larger?" -> compare
        m = re.search(r"([\d.]+)\s+is\s+less\s+than\s+([\d.]+)", p_lower)
        if m and re.search(r"which.*larger", p_lower):
            try:
                lesser, greater = float(m.group(1)), float(m.group(2))
                c_nums = re.findall(r"[\d.]+", candidate)
                if c_nums:
                    c_val = float(c_nums[0])
                    if c_val == greater:
                        return 1.0, True
                    elif c_val == lesser:
                        return -1.0, True
            except ValueError:
                pass

        # "All but N die/left" -> answer is N
        m = re.search(r"all\s+but\s+(\d+)", p_lower)
        if m and re.search(r"how\s+many", p_lower):
            correct_n = m.group(1)
            if correct_n in candidate:
                return 1.0, True
            return -0.5, True

        return 0.0, False

    def _constraint_score(self, prompt: str, candidate: str) -> float:
        """How well does candidate satisfy prompt constraints? Returns [-1, 1]."""
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip()
        score = 0.0
        checks = 0

        # Direct numeric evaluation (highest priority)
        num_score, had_num = self._try_numeric_eval(prompt, candidate)
        if had_num:
            checks += 1
            score += num_score

        # Comparatives + transitivity
        comps = self._extract_comparatives(prompt)
        if comps:
            ordering = self._build_ordering(comps)
            asks_largest = bool(re.search(
                r"(?:who|which|what)\s+(?:is\s+)?(?:largest|tallest|heaviest|"
                r"biggest|greatest|larger|taller|most|best)", p_lower))
            if asks_largest and ordering:
                checks += 1
                top = max(ordering, key=lambda x: len(ordering.get(x, set())))
                if top in c_lower:
                    score += 1.0
                else:
                    score -= 0.5

            # Numeric ordering
            for greater, lesser in comps:
                try:
                    g_val, l_val = float(greater), float(lesser)
                    c_nums = [float(m.group()) for m in re.finditer(r"\b\d+\.?\d*\b", candidate)]
                    if c_nums:
                        checks += 1
                        if re.search(r"which.*larger", p_lower):
                            if c_nums[0] == g_val:
                                score += 1.0
                            elif c_nums[0] == l_val:
                                score -= 1.0
                except ValueError:
                    pass

        # Negation + question
        if self._has_negation(prompt) and "?" in prompt:
            checks += 1
            if c_lower.startswith("yes") or "all " in c_lower:
                score -= 0.5
            elif "cannot be answered" in c_lower or "not enough" in c_lower:
                score += 0.2

        # Modus tollens
        for ante, cons in self._extract_conditionals(prompt):
            cons_words = cons.split()
            if cons_words:
                last_word = cons_words[-1].strip(".,;:?")
                if re.search(r"not\s+" + re.escape(last_word), p_lower):
                    checks += 1
                    if c_lower.startswith("no"):
                        score += 1.0
                    elif c_lower.startswith("yes"):
                        score -= 1.0
                    elif "maybe" in c_lower or "not enough" in c_lower:
                        score -= 0.3

        # Subject-object
        for agent, action, patient in self._extract_subject_object(prompt):
            if re.search(r"(?:who|what)\s+(?:was|were|is)\s+(?:being\s+)?\w+", p_lower):
                checks += 1
                if patient in c_lower and agent not in c_lower:
                    score += 1.0
                elif agent in c_lower and patient not in c_lower:
                    score -= 1.0

        # Universal quantifier
        if re.search(r"all\s+\w+\s+are\s+\w+.*all\s+\w+\s+\w+", p_lower):
            checks += 1
            if c_lower.startswith("no"):
                score += 0.5
            elif c_lower.startswith("yes"):
                score -= 0.5

        if checks == 0:
            return 0.0
        return float(np.clip(score / max(checks, 1), -1.0, 1.0))

    # -- Local co-occurrence SVD -------------------------------------------

    def _tokenize(self, text: str) -> list:
        return re.findall(r"[a-z0-9]+", text.lower())

    def _build_embeddings(self, texts: list, window: int = 3, k: int = 20):
        token_lists = [self._tokenize(t) for t in texts]
        all_tokens = [t for ts in token_lists for t in ts]
        vocab = list(set(all_tokens))
        if len(vocab) < 3:
            return {}, None
        idx = {w: i for i, w in enumerate(vocab)}
        n = len(vocab)
        cooccur = np.zeros((n, n), dtype=np.float64)
        for tokens in token_lists:
            ids = [idx[t] for t in tokens]
            for i, tid in enumerate(ids):
                for j in range(max(0, i - window), min(len(ids), i + window + 1)):
                    if i != j:
                        cooccur[tid, ids[j]] += 1.0
        total = cooccur.sum() + 1e-12
        row_s = cooccur.sum(axis=1, keepdims=True) + 1e-12
        col_s = cooccur.sum(axis=0, keepdims=True) + 1e-12
        pmi = np.log2(cooccur * total / (row_s * col_s) + 1e-12)
        ppmi = np.maximum(pmi, 0.0)
        U, S, _ = np.linalg.svd(ppmi, full_matrices=False)
        dim = min(k, n)
        emb = U[:, :dim] * np.sqrt(S[:dim])
        return {w: emb[i] for w, i in idx.items()}, emb

    def _embed_text(self, text: str, w2v: dict, dim: int) -> np.ndarray:
        vecs = [w2v[t] for t in self._tokenize(text) if t in w2v]
        return np.mean(vecs, axis=0) if vecs else np.zeros(dim)

    # -- Active Inference scoring ------------------------------------------

    def evaluate(self, prompt: str, candidates: list) -> list:
        if not candidates:
            return []

        all_texts = [prompt] + list(candidates)
        w2v, emb = self._build_embeddings(all_texts)
        dim = emb.shape[1] if emb is not None and emb.ndim == 2 else 1

        p_vec = self._embed_text(prompt, w2v, dim) if w2v else np.zeros(1)
        c_vecs = [self._embed_text(c, w2v, dim) if w2v else np.zeros(1)
                  for c in candidates]
        null_vec = np.mean(c_vecs, axis=0) if c_vecs else np.zeros(dim)

        results = []
        for i, cand in enumerate(candidates):
            # 1. Pragmatic: constraint satisfaction (structural)
            constraint = self._constraint_score(prompt, cand)
            pragmatic_struct = (constraint + 1.0) / 2.0  # map to [0, 1]

            # 2. Pragmatic: NCD relevance
            ncd_val = self._ncd(prompt, cand)
            pragmatic_ncd = 1.0 / (1.0 + ncd_val)

            # 3. Epistemic: divergence from null in SVD space
            cv = c_vecs[i]
            pn = np.linalg.norm(cv - p_vec)
            nn = np.linalg.norm(cv - null_vec)
            epistemic = nn / (pn + 1e-8) if pn > 1e-8 else 0.5

            # Active inference: combine with structural as primary signal
            # If structural has signal (constraint != 0), it dominates
            has_structural = abs(constraint) > 0.01
            if has_structural:
                score = 0.7 * pragmatic_struct + 0.15 * pragmatic_ncd + 0.15 * min(epistemic, 2.0)
            else:
                score = 0.4 * pragmatic_ncd + 0.3 * min(epistemic, 2.0) + 0.3 * pragmatic_struct

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": (
                    f"constraint={constraint:.3f}, NCD={ncd_val:.4f}, "
                    f"epistemic={epistemic:.3f}"
                ),
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        struct = self._constraint_score(prompt, answer)
        if struct > 0.3:
            return float(np.clip(0.8 + struct * 0.2, 0.0, 1.0))
        elif struct < -0.3:
            return 0.05
        # No structural signal — fall back to NCD
        ncd_val = self._ncd(prompt, answer)
        return float((1.0 - np.clip(ncd_val, 0.0, 1.0)) ** 2)
