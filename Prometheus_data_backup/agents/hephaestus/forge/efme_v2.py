"""EFME v2 — Structure-Aware Falsification Engine.

Structural parsing is the PRIMARY discriminator, NCD is a tiebreaker.
  1. Parse prompt for logical constraints (negations, comparatives,
     conditionals, transitivity, subject-object, quantifiers)
  2. Score each candidate on consistency with extracted constraints
  3. Falsify candidates that contradict prompt structure
  4. NCD used only as secondary relevance signal

Concepts: Ergodic Theory x Falsificationism x Maximum Entropy
"""

import re
import zlib
import numpy as np


class ReasoningTool:
    def __init__(self):
        self._level = 6

    # -- NCD (tiebreaker only) ---------------------------------------------

    def _c(self, text: str) -> int:
        return len(zlib.compress(text.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " \n " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    # -- Structural analysis -----------------------------------------------

    def _extract_numbers(self, text: str) -> list:
        """Extract numeric values from text."""
        return [float(m.group()) for m in re.finditer(r"\b\d+\.?\d*\b", text)]

    def _extract_comparatives(self, text: str) -> list:
        """Find ordering claims -> list of (greater, lesser) pairs."""
        results = []
        # "X is larger/greater/taller/heavier than Y"
        for m in re.finditer(
            r"(\S+)\s+(?:is\s+)?(?:larger|greater|bigger|more|higher|taller|"
            r"heavier|faster|better|older)\s+than\s+(\S+)",
            text, re.IGNORECASE
        ):
            results.append((m.group(1).strip(".,;:?"), m.group(2).strip(".,;:?")))
        # "X is less/smaller/shorter than Y" -> Y > X
        for m in re.finditer(
            r"(\S+)\s+(?:is\s+)?(?:less|smaller|lower|shorter|lighter|slower|"
            r"worse|younger)\s+than\s+(\S+)",
            text, re.IGNORECASE
        ):
            results.append((m.group(2).strip(".,;:?"), m.group(1).strip(".,;:?")))
        return results

    def _extract_negations(self, text: str) -> list:
        pattern = (
            r"(?:not|never|no|neither|nor|cannot|can't|won't|"
            r"doesn't|don't|isn't|aren't|wasn't|weren't)\s+(\w+)"
        )
        return [(m.group(1).lower(), m.group(0).lower())
                for m in re.finditer(pattern, text, re.IGNORECASE)]

    def _extract_conditionals(self, text: str) -> list:
        """Find 'if P then Q' -> (antecedent, consequent)."""
        results = []
        for m in re.finditer(r"[Ii]f\s+(.+?)[,.]?\s+(?:then\s+)?(.+?)(?:\.|$)", text):
            results.append((m.group(1).strip().lower(), m.group(2).strip().lower()))
        return results

    def _extract_subject_object(self, text: str) -> list:
        """Find 'X verbed Y' patterns -> (agent, action, patient)."""
        results = []
        # "The X verbed the Y"
        for m in re.finditer(
            r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)", text
        ):
            results.append((m.group(1).lower(), m.group(2).lower(), m.group(3).lower()))
        return results

    def _has_negation(self, text: str) -> bool:
        return bool(re.search(
            r"\b(?:not|never|no|neither|nor|cannot|can't|won't|"
            r"doesn't|don't|isn't|aren't|wasn't|weren't|not the case)\b",
            text, re.IGNORECASE
        ))

    def _build_ordering(self, comparatives: list) -> dict:
        """Build transitive ordering from comparative pairs.
        Returns dict: entity -> set of entities it's greater than.
        """
        greater_than = {}
        for a, b in comparatives:
            a_low, b_low = a.lower(), b.lower()
            greater_than.setdefault(a_low, set()).add(b_low)
        # Transitive closure
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

    # -- Structural scoring ------------------------------------------------

    def _try_numeric_eval(self, prompt: str, candidate: str) -> tuple[float, bool]:
        """Try to solve numeric comparison directly. Returns (score, had_signal)."""
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip()

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

        m = re.search(r"all\s+but\s+(\d+)", p_lower)
        if m and re.search(r"how\s+many", p_lower):
            correct_n = m.group(1)
            if correct_n in candidate:
                return 1.0, True
            return -0.5, True

        return 0.0, False

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Score candidate based on structural consistency with prompt.
        Returns value in [-1, 1]. Positive = consistent, negative = contradicts.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip()
        score = 0.0
        checks = 0

        # 0. Direct numeric evaluation (highest priority)
        num_score, had_num = self._try_numeric_eval(prompt, candidate)
        if had_num:
            checks += 1
            score += num_score

        # 1. Comparative / ordering analysis
        comparatives = self._extract_comparatives(prompt)
        if comparatives:
            ordering = self._build_ordering(comparatives)
            # Find what the prompt is asking about
            asks_largest = bool(re.search(
                r"(?:who|which|what)\s+(?:is\s+)?(?:largest|tallest|heaviest|"
                r"biggest|greatest|larger|taller|most|best)", p_lower
            ))
            asks_smallest = bool(re.search(
                r"(?:who|which|what)\s+(?:is\s+)?(?:smallest|shortest|lightest|"
                r"least|worst|slower)", p_lower
            ))

            if asks_largest and ordering:
                checks += 1
                # The entity that is greater than the most others
                top = max(ordering, key=lambda x: len(ordering.get(x, set())))
                if top in c_lower:
                    score += 1.0
                else:
                    score -= 0.5
            elif asks_smallest and ordering:
                checks += 1
                # Entity that appears as lesser most often
                all_lesser = set()
                for v in ordering.values():
                    all_lesser.update(v)
                all_entities = set(ordering.keys()) | all_lesser
                # Smallest = in lesser set but not in greater set
                smallest_candidates = all_lesser - set(ordering.keys())
                if smallest_candidates:
                    bottom = next(iter(smallest_candidates))
                    if bottom in c_lower:
                        score += 1.0
                    else:
                        score -= 0.5

            # Check for numeric comparison in prompt
            p_numbers = self._extract_numbers(prompt)
            c_numbers = self._extract_numbers(candidate)
            if len(p_numbers) >= 2 and c_numbers:
                checks += 1
                # If prompt establishes ordering between numbers
                for greater, lesser in comparatives:
                    try:
                        g_val = float(greater)
                        l_val = float(lesser)
                        # Prompt says g_val > l_val
                        if asks_largest or re.search(r"which.*larger", p_lower):
                            if c_numbers[0] == g_val:
                                score += 1.0
                            elif c_numbers[0] == l_val:
                                score -= 1.0
                    except ValueError:
                        pass

        # 2. Negation analysis
        prompt_negated = self._has_negation(prompt)
        cand_affirms = c_lower.startswith("yes") or "all " in c_lower
        cand_denies = c_lower.startswith("no")

        if prompt_negated and "?" in prompt:
            checks += 1
            # Prompt has negation + question — "yes" is suspicious
            if cand_affirms:
                score -= 0.5
            elif "cannot be answered" in c_lower or "not enough" in c_lower:
                # Hedging when prompt has negation — might be appropriate
                score += 0.2

        # 3. Conditional + modus tollens
        conditionals = self._extract_conditionals(prompt)
        for antecedent, consequent in conditionals:
            # Check if prompt also negates the consequent
            neg_consequent = False
            for neg_term, neg_scope in self._extract_negations(prompt):
                if neg_term in consequent or any(
                    w in consequent for w in neg_scope.split()
                ):
                    neg_consequent = True
            # Also check explicit "not wet", "is not wet" etc
            if re.search(r"not\s+" + re.escape(consequent.split()[-1]) if consequent.split() else "",
                         p_lower):
                neg_consequent = True

            if neg_consequent:
                checks += 1
                # Modus tollens: if P->Q and not Q, then not P
                if cand_denies or c_lower.startswith("no"):
                    score += 1.0  # correct: denying the antecedent
                elif cand_affirms:
                    score -= 1.0  # wrong: affirming when consequent is negated
                elif "maybe" in c_lower or "not enough" in c_lower:
                    score -= 0.3  # weaker wrong: hedging

        # 4. Subject-object (who chased whom, etc)
        svo_triples = self._extract_subject_object(prompt)
        if svo_triples:
            asks_patient = bool(re.search(
                r"(?:who|what)\s+(?:was|were|is)\s+(?:being\s+)?(?:\w+ed|chased|bitten|hit|caught)",
                p_lower
            ))
            asks_agent = bool(re.search(
                r"(?:who|what)\s+(?:\w+ed|chased|bit|hit|caught)", p_lower
            ))
            for agent, action, patient in svo_triples:
                if asks_patient:
                    checks += 1
                    if patient in c_lower and agent not in c_lower:
                        score += 1.0
                    elif agent in c_lower and patient not in c_lower:
                        score -= 1.0
                elif asks_agent:
                    checks += 1
                    if agent in c_lower and patient not in c_lower:
                        score += 1.0
                    elif patient in c_lower and agent not in c_lower:
                        score -= 1.0

        # 5. Universal quantifier traps
        # "If all X are Y, are all Y X?" -> No
        if re.search(r"all\s+\w+\s+are\s+\w+.*all\s+\w+\s+\w+", p_lower):
            checks += 1
            if cand_denies:
                score += 0.5
            elif cand_affirms:
                score -= 0.5

        if checks == 0:
            return 0.0
        return np.clip(score / max(checks, 1), -1.0, 1.0)

    # -- Public interface --------------------------------------------------

    def evaluate(self, prompt: str, candidates: list) -> list:
        if not candidates:
            return []

        results = []
        for cand in candidates:
            # Primary: structural analysis
            struct = self._structural_score(prompt, cand)

            # Secondary: NCD relevance (tiebreaker)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 / (1.0 + ncd_val)

            # Combine: structural dominates, NCD breaks ties
            # Map structural from [-1,1] to [0,1]
            struct_norm = (struct + 1.0) / 2.0

            # 80% structural, 20% NCD
            score = 0.8 * struct_norm + 0.2 * ncd_score

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": (
                    f"structural={struct:.3f}, NCD={ncd_val:.4f}"
                ),
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        struct = self._structural_score(prompt, answer)
        if struct > 0.3:
            return float(np.clip(0.8 + struct * 0.2, 0.0, 1.0))
        elif struct < -0.3:
            return 0.05
        # No structural signal — fall back to NCD
        ncd_val = self._ncd(prompt, answer)
        return float((1.0 - np.clip(ncd_val, 0.0, 1.0)) ** 2)
