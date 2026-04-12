import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Stabilizing Hypothesis Sampler via Ergodic-LDPC Analogy.
    
    Mechanism:
    1. Ergodic Exploration: Parses candidates to extract structural features 
       (negations, comparatives, numerics) representing the "hypothesis space".
    2. Emergent Constraints (LDPC Parity Checks): Defines global consistency rules 
       (e.g., numeric transitivity, negation flips). Violations generate a "syndrome".
    3. Error Correction: Uses belief-propagation-inspired scoring to penalize 
       candidates with high syndrome weight (inconsistencies) while rewarding 
       structural alignment with the prompt.
    4. Scoring: Final score = Structural Match - Penalty(Syndrome) + NCD(Tiebreaker).
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'larger', 'smaller'}
        self.bool_map = {'true': 1, 'false': 0, 'yes': 1, 'no': 0}

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for emergent numeric constraints."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _extract_tokens(self, text: str) -> set:
        """Tokenize for structural overlap."""
        return set(re.findall(r'\b\w+\b', text.lower()))

    def _check_emergent_constraints(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        LDPC Parity Check Simulation.
        Returns (syndrome_weight, reason_string).
        Lower syndrome = higher consistency.
        """
        syndrome = 0.0
        reasons = []
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Constraint 1: Numeric Consistency (Transitivity/Magnitude)
        p_nums = self._extract_numbers(p_low)
        c_nums = self._extract_numbers(c_low)
        
        if p_nums and c_nums:
            # If prompt implies an order (e.g. 9.11 vs 9.9), check if candidate respects it
            # Simple heuristic: if prompt has 2 nums, candidate should not invert their order arbitrarily
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_diff = p_nums[0] - p_nums[1]
                c_diff = c_nums[0] - c_nums[1]
                # If signs flip without negation context, penalize
                if (p_diff > 0 and c_diff < 0) or (p_diff < 0 and c_diff > 0):
                    if 'not' not in c_low and 'false' not in c_low:
                        syndrome += 2.0
                        reasons.append("Numeric order violation")

        # Constraint 2: Negation Consistency (Parity of Truth)
        p_has_neg = any(n in p_low.split() for n in self.negation_words)
        c_has_neg = any(n in c_low.split() for n in self.negation_words)
        
        # If prompt asks "Is it NOT X?" and candidate says "Yes", that's a specific logic trap
        # Heuristic: If prompt is purely negative framing, candidate should reflect that or invert answer
        if p_has_neg and not c_has_neg:
            # Potential mismatch in handling negation scope
            syndrome += 0.5
            reasons.append("Negation scope mismatch")

        # Constraint 3: Logical Contradiction (Simple keyword clash)
        # If prompt contains "impossible" and candidate contains "possible" without qualification
        if "impossible" in p_low and "possible" in c_low and "not" not in c_low:
            syndrome += 1.5
            reasons.append("Logical contradiction detected")

        return syndrome, "; ".join(reasons) if reasons else "Consistent"

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Score based on structural parsing (negations, comparatives, numerics)."""
        score = 0.0
        p_low = prompt.lower()
        c_low = candidate.lower()
        p_tokens = self._extract_tokens(p_low)
        c_tokens = self._extract_tokens(c_low)
        
        # 1. Numeric Evaluation
        p_nums = self._extract_numbers(p_low)
        c_nums = self._extract_numbers(c_low)
        
        if p_nums and c_nums:
            # Check for exact number preservation (high priority)
            common_nums = set(p_nums) & set(c_nums)
            score += len(common_nums) * 2.0
            
            # Check relative magnitude if comparatives exist
            if any(c in p_low for c in self.comparatives):
                if p_nums[0] > p_nums[1] and "greater" in c_low:
                    score += 3.0
                elif p_nums[0] < p_nums[1] and "less" in c_low:
                    score += 3.0

        # 2. Negation/Conditional Tracking
        p_neg_count = sum(1 for w in self.negation_words if w in p_tokens)
        c_neg_count = sum(1 for w in self.negation_words if w in c_tokens)
        
        # Reward matching negation parity
        if (p_neg_count % 2) == (c_neg_count % 2):
            score += 1.0
        else:
            score -= 1.0 # Penalty for flipping boolean state unexpectedly

        # 3. Keyword Overlap (Weighted)
        intersection = p_tokens & c_tokens
        # Remove stop words noise
        stop_words = {'the', 'is', 'a', 'an', 'to', 'of', 'in', 'it', 'that', 'this'}
        meaningful_overlap = intersection - stop_words
        score += len(meaningful_overlap) * 0.5

        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Step 1: Structural Parsing (Ergodic Sampler Input)
            struct_score = self._structural_score(prompt, cand)
            
            # Step 2: Emergent Constraints (LDPC Parity Check)
            syndrome, reason_msg = self._check_emergent_constraints(prompt, cand)
            
            # Step 3: Correction (Penalize Syndrome)
            # The decoder attempts to find the nearest valid codeword by down-weighting high-syndrome items
            corrected_score = struct_score - (syndrome * 1.5)
            
            # NCD Tiebreaker (only adds small fraction)
            ncd_val = self._ncd_distance(prompt, cand)
            final_score = corrected_score - (ncd_val * 0.1)
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural:{struct_score:.2f}, Syndrome:{syndrome:.2f} ({reason_msg})"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on syndrome weight and structural alignment.
        """
        struct_score = self._structural_score(prompt, answer)
        syndrome, _ = self._check_emergent_constraints(prompt, answer)
        
        # Base confidence from structural match (normalized roughly)
        # Assume max structural score around 10 for typical short answers
        base_conf = min(1.0, max(0.0, struct_score / 5.0))
        
        # Reduce confidence heavily if syndrome is high
        penalty = min(1.0, syndrome / 3.0)
        
        final_conf = max(0.0, base_conf * (1.0 - penalty))
        return round(final_conf, 4)