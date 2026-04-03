"""
Neuromodulation x Pragmatics x Compositional Semantics Reasoning Tool

Combines:
1. Compositional semantic parsing into atomic propositions + logic trees
2. Neuromodulatory gain control (dopamine/serotonin/acetylcholine signals)
3. Pragmatic scoring (relevance, quantity, manner)
4. Constraint propagation and computational evaluation
5. Epistemic honesty via meta-confidence checks
"""

import re
import zlib
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple, Optional


class ReasoningTool:
    """
    Neuromodulation x Pragmatics x Compositional Semantics tool.
    Parses compositional logic, applies neuromodulatory gain control,
    computes via constraint propagation, scores with pragmatic weights.
    """

    def __init__(self):
        self.W_d = 0.3  # Dopamine weight (causal reasoning)
        self.W_s = 0.3  # Serotonin weight (uncertainty)
        self.W_a = 0.3  # Acetylcholine weight (comparison)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by neuro-pragmatic-compositional score."""
        results = []
        for candidate in candidates:
            score = self._full_score(prompt, candidate)
            reasoning = f"Score: {score:.3f}"
            results.append({"candidate": candidate, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence checks."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf

        comp_result = self._computational_solve(prompt, answer)
        if comp_result is not None and comp_result > 0.9:
            return min(0.92, meta_conf)

        score = self._full_score(prompt, answer)
        base_conf = min(0.85, max(0.1, score))
        return min(base_conf, meta_conf)

    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()

        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p_lower):
            return 0.22

        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and 'who' in p_lower:
            return 0.23

        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower) and '?' in prompt:
            return 0.25

        # False dichotomy
        if re.search(r'\b(either .* or .*)\b', p_lower):
            return 0.27

        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower) and '?' in prompt:
            return 0.28

        # Insufficient info
        if re.search(r'\b(not enough|insufficient|cannot determine)\b', p_lower):
            return 0.18

        return 0.95

    def _full_score(self, prompt: str, candidate: str) -> float:
        """Main scoring combining computational + neuro-pragmatic + NCD."""
        comp_score = self._computational_solve(prompt, candidate)
        if comp_score is not None:
            return 0.65 * comp_score + 0.20 * self._neuro_pragmatic_score(prompt, candidate) + 0.15 * self._ncd_score(prompt, candidate)

        struct_score = self._structural_score(prompt, candidate)
        neuro_score = self._neuro_pragmatic_score(prompt, candidate)
        ncd_score = self._ncd_score(prompt, candidate)
        return 0.50 * struct_score + 0.35 * neuro_score + 0.15 * ncd_score

    def _computational_solve(self, prompt: str, candidate: str) -> Optional[float]:
        """Execute computational solvers for known problem types."""
        # Numeric comparison
        if re.search(r'\d+\.?\d*', prompt) and any(w in prompt.lower() for w in ['greater', 'less', 'larger', 'smaller', 'which']):
            result = self._solve_numeric(prompt, candidate)
            if result is not None:
                return result

        # Bat-and-ball algebra
        if 'cost' in prompt.lower() and 'more than' in prompt.lower() and ('total' in prompt.lower() or 'together' in prompt.lower()):
            result = self._solve_algebra(prompt, candidate)
            if result is not None:
                return result

        # All-but-N
        if re.search(r'all but \d+', prompt.lower()):
            result = self._solve_all_but_n(prompt, candidate)
            if result is not None:
                return result

        # Modular arithmetic
        if 'remainder' in prompt.lower() or 'mod' in prompt.lower():
            result = self._solve_modular(prompt, candidate)
            if result is not None:
                return result

        # Temporal ordering
        if any(w in prompt.lower() for w in ['before', 'after', 'then', 'first', 'last']):
            result = self._solve_temporal(prompt, candidate)
            if result is not None:
                return result

        # Modus tollens
        if 'if' in prompt.lower() and 'not' in prompt.lower():
            result = self._solve_modus_tollens(prompt, candidate)
            if result is not None:
                return result

        return None

    def _solve_numeric(self, prompt: str, candidate: str) -> Optional[float]:
        """Compare numeric values."""
        try:
            nums = [float(n) for n in re.findall(r'\d+\.?\d*', prompt)]
            if len(nums) < 2:
                return None

            cand_nums = [float(n) for n in re.findall(r'\d+\.?\d*', candidate)]

            if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                expected = max(nums[:2])
                if cand_nums and abs(cand_nums[0] - expected) < 0.01:
                    return 1.0
                elif str(expected) in candidate or (expected == nums[0] and str(int(nums[0])) in candidate):
                    return 0.95
            elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                expected = min(nums[:2])
                if cand_nums and abs(cand_nums[0] - expected) < 0.01:
                    return 1.0
                elif str(expected) in candidate:
                    return 0.95
        except:
            pass
        return None

    def _solve_algebra(self, prompt: str, candidate: str) -> Optional[float]:
        """Solve bat-and-ball type problems."""
        try:
            nums = [float(n) for n in re.findall(r'\d+\.?\d*', prompt)]
            if len(nums) >= 2:
                total, diff = nums[0], nums[1]
                # x + (x + diff) = total => 2x + diff = total => x = (total - diff) / 2
                x = (total - diff) / 2
                cand_nums = [float(n) for n in re.findall(r'\d+\.?\d*', candidate)]
                if cand_nums and abs(cand_nums[0] - x) < 0.01:
                    return 1.0
        except:
            pass
        return None

    def _solve_all_but_n(self, prompt: str, candidate: str) -> Optional[float]:
        """Solve all-but-N problems."""
        try:
            match = re.search(r'(\d+).*all but (\d+)', prompt.lower())
            if match:
                total, but_n = int(match.group(1)), int(match.group(2))
                result = total - but_n
                cand_nums = [int(n) for n in re.findall(r'\d+', candidate)]
                if cand_nums and cand_nums[0] == result:
                    return 1.0
        except:
            pass
        return None

    def _solve_modular(self, prompt: str, candidate: str) -> Optional[float]:
        """Solve modular arithmetic."""
        try:
            match = re.search(r'(\d+).*(?:mod|remainder).*(\d+)', prompt.lower())
            if match:
                dividend, divisor = int(match.group(1)), int(match.group(2))
                result = dividend % divisor
                cand_nums = [int(n) for n in re.findall(r'\d+', candidate)]
                if cand_nums and cand_nums[0] == result:
                    return 1.0
        except:
            pass
        return None

    def _solve_temporal(self, prompt: str, candidate: str) -> Optional[float]:
        """Solve temporal ordering."""
        befores = re.findall(r'(\w+)\s+before\s+(\w+)', prompt, re.I)
        afters = re.findall(r'(\w+)\s+after\s+(\w+)', prompt, re.I)

        order = {}
        for a, b in befores:
            order[a] = order.get(a, 0)
            order[b] = order.get(b, 0) + 1
        for a, b in afters:
            order[b] = order.get(b, 0)
            order[a] = order.get(a, 0) + 1

        if order:
            sorted_items = sorted(order.items(), key=lambda x: x[1])
            first = sorted_items[0][0] if sorted_items else None
            if first and first.lower() in candidate.lower():
                return 0.85
        return None

    def _solve_modus_tollens(self, prompt: str, candidate: str) -> Optional[float]:
        """Solve modus tollens (if A then B, not B, therefore not A)."""
        if_match = re.search(r'if\s+(.+?)\s+then\s+(.+?)[\.,]', prompt, re.I)
        if if_match:
            antecedent = if_match.group(1).strip()
            consequent = if_match.group(2).strip()
            if 'not' in prompt.lower() and consequent.lower() in prompt.lower():
                if 'not' in candidate.lower() and antecedent.lower() in candidate.lower():
                    return 0.9
        return None

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Structural consistency via proposition matching."""
        p_props = self._extract_atoms(prompt)
        c_props = self._extract_atoms(candidate)

        if not p_props:
            return 0.5

        overlap = len(set(p_props) & set(c_props))
        return min(1.0, overlap / len(p_props) + 0.3)

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract atomic propositions."""
        atoms = []
        patterns = [
            r'\b(\w+)\s+(?:is|are|was|were)\s+(\w+)',
            r'\b(not|no)\s+(\w+)',
            r'\b(\w+)\s+(?:greater|less|more|fewer)\s+than\s+(\w+)',
        ]
        for pat in patterns:
            for m in re.finditer(pat, text, re.I):
                atoms.append(m.group(0).lower())
        return atoms

    def _neuro_pragmatic_score(self, prompt: str, candidate: str) -> float:
        """Neuromodulatory gain + pragmatic weights."""
        # Extract neuromodulatory signals
        dopamine = len(re.findall(r'\b(because|leads to|therefore|causes|results in)\b', prompt, re.I))
        serotonin = len(re.findall(r'\b(maybe|might|could|possibly|perhaps)\b', prompt, re.I))
        acetylcholine = len(re.findall(r'\b(more|less|greater|smaller|\w+er than|\w+est)\b', prompt, re.I))

        # Compute gain
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))

        gain = sigmoid(self.W_d * dopamine + self.W_s * serotonin + self.W_a * acetylcholine)

        # Pragmatic weights
        relevance = self._tfidf_similarity(prompt, candidate)
        p_atoms = self._extract_atoms(prompt)
        c_atoms = self._extract_atoms(candidate)
        extra = len(set(c_atoms) - set(p_atoms))
        quantity = 1 / (1 + extra)

        # Manner (simplicity)
        depth = candidate.count(',') + candidate.count(';') + 1
        manner = 1 / (1 + depth * 0.1)

        return gain * relevance * quantity * manner

    def _tfidf_similarity(self, prompt: str, candidate: str) -> float:
        """TF-IDF cosine similarity."""
        p_words = re.findall(r'\w+', prompt.lower())
        c_words = re.findall(r'\w+', candidate.lower())

        p_counts = Counter(p_words)
        c_counts = Counter(c_words)

        all_words = set(p_words) | set(c_words)
        if not all_words:
            return 0.5

        p_vec = np.array([p_counts.get(w, 0) for w in all_words])
        c_vec = np.array([c_counts.get(w, 0) for w in all_words])

        p_norm = np.linalg.norm(p_vec)
        c_norm = np.linalg.norm(c_vec)

        if p_norm == 0 or c_norm == 0:
            return 0.5

        return np.dot(p_vec, c_vec) / (p_norm * c_norm)

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        c_p = len(zlib.compress(prompt.encode()))
        c_c = len(zlib.compress(candidate.encode()))
        c_both = len(zlib.compress((prompt + candidate).encode()))
        ncd = (c_both - min(c_p, c_c)) / max(c_p, c_c, 1)
        return max(0, 1 - ncd)
