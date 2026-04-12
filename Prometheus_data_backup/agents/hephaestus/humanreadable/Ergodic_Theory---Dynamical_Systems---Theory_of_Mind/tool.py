import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Recursive Belief-State Dynamical Estimator (Approximated).
    
    Mechanism:
    1. Structural Parsing (Dynamical Systems): Extracts logical operators (negations, 
       comparatives) and numeric values to define the initial state vector.
    2. Ergodic Regularizer (Hypothesis Validation): Uses NCD to estimate the "distance" 
       between the prompt's logical structure and the candidate's structure. It treats 
       the candidate as a trajectory; if the candidate violates the prompt's constraints 
       (e.g., wrong number comparison, ignored negation), the "Lyapunov exponent" 
       (instability metric) increases, lowering the score.
    3. Belief Update: Combines structural compliance (logic/numbers) with semantic 
       proximity (NCD) to produce a deterministic score.
    """

    def __init__(self):
        self.numeric_ops = ['<', '>', '==', '!=', '>=', '<=']
        self.negations = ['not', 'no', 'never', 'false', 'impossible']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower']
        
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        pattern = r"[-+]?\d*\.?\d+"
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _check_logic_compliance(self, prompt: str, candidate: str) -> float:
        """
        Checks structural constraints: Negations and Numeric Comparisons.
        Returns a compliance score (0.0 to 1.0).
        """
        score = 1.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Consistency
        p_nums = self._extract_numbers(p_lower)
        c_nums = self._extract_numbers(c_lower)
        
        if len(p_nums) >= 2 and len(c_nums) >= 2:
            # If prompt has a comparison logic (implied by having numbers), 
            # check if candidate preserves the order if it claims to answer.
            # Simple heuristic: If prompt has A and B, and candidate has A and B,
            # do they maintain the same relative order if the prompt implies sorting?
            # Since we don't know the exact question type, we check for contradiction.
            # If prompt says "9.11 < 9.9" (false) vs "9.9 > 9.11" (true).
            # We penalize if the candidate explicitly contradicts the sorted order of unique numbers
            # when the prompt asks for sorting (detected by keywords).
            if any(k in p_lower for k in ['sort', 'order', 'larger', 'smaller', 'compare']):
                p_sorted = sorted(p_nums)
                # Check if candidate numbers are a permutation of prompt numbers
                if len(c_nums) == len(p_nums):
                    # Simple check: if candidate lists numbers, are they in the requested order?
                    # This is a heuristic approximation of the dynamical rule.
                    if 'ascend' in p_lower or 'increasing' in p_lower:
                        if c_nums != sorted(c_nums):
                            score -= 0.5
                    elif 'descend' in p_lower or 'decreasing' in p_lower:
                        if c_nums != sorted(c_nums, reverse=True):
                            score -= 0.5

        # 2. Negation Consistency
        # If prompt has strong negation and candidate lacks it (or vice versa), penalize.
        p_has_neg = any(n in p_lower for n in self.negations)
        c_has_neg = any(n in c_lower for n in self.negations)
        
        # Heuristic: If prompt asks "Is it not X?" and candidate says "Yes", 
        # it's ambiguous. But if prompt says "X is impossible" and candidate says "X is true",
        # that's a conflict. 
        # Simplified: If prompt has negation and candidate does not (and isn't short), penalize slightly.
        if p_has_neg and not c_has_neg and len(c_lower.split()) > 3:
            # Check if the candidate is just repeating the prompt without the negation logic
            # This is a weak signal, so small penalty.
            score -= 0.1
            
        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        try:
            comp12 = len(zlib.compress(b1 + b2))
            comp1 = len(zlib.compress(b1))
            comp2 = len(zlib.compress(b2))
            numerator = comp12 - min(comp1, comp2)
            denominator = max(comp1, comp2)
            if denominator == 0:
                return 1.0
            return numerator / denominator
        except Exception:
            return 1.0

    def _ergodic_score(self, prompt: str, candidate: str) -> float:
        """
        Estimates the 'ergodicity' of the candidate relative to the prompt.
        Interprets the prompt as the 'space average' and the candidate as the 'time average'.
        Low NCD between structured versions implies the candidate trajectory covers the 
        necessary logical space of the prompt.
        """
        # Normalize whitespace and case for structural comparison
        p_norm = " ".join(prompt.lower().split())
        c_norm = " ".join(candidate.lower().split())
        
        # Base similarity
        ncd_val = self._ncd(p_norm, c_norm)
        
        # Transform NCD to similarity (0 to 1, where 1 is identical)
        # NCD is 0 for identical, 1 for totally different.
        similarity = 1.0 - ncd_val
        
        return similarity

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features (Dynamical System Initial State)
        p_nums = self._extract_numbers(prompt)
        p_has_logic = any(x in prompt.lower() for x in self.negations + self.comparatives)
        
        for cand in candidates:
            # 1. Structural/Logic Score (The "Dynamical Rule")
            logic_score = self._check_logic_compliance(prompt, cand)
            
            # 2. Ergodic/Similarity Score (The "Invariant Measure")
            # We weight this less if logic score is low (constraint propagation)
            ergo_score = self._ergodic_score(prompt, cand)
            
            # 3. Fusion: Recursive Belief Update
            # If logic fails, ergodicity doesn't matter much (model misspecification)
            if logic_score < 0.5:
                final_score = logic_score * 0.5
            else:
                # Combine: Logic is primary, Ergodicity breaks ties and ensures relevance
                # Weighted sum favoring logic for reasoning tasks
                final_score = (logic_score * 0.6) + (ergo_score * 0.4)
            
            # Add a small deterministic bias based on length matching (heuristic for completeness)
            len_ratio = min(len(cand), len(prompt)) / max(len(cand), len(prompt), 1)
            final_score += len_ratio * 0.05
            
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Logic:{logic_score:.2f}, Ergodic:{ergo_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']