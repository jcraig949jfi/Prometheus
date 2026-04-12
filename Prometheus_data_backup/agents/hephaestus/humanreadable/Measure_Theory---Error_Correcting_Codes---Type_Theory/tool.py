import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Certified Probabilistic-Robustness' inspired reasoning layer.
    
    Mechanism:
    1. Measure-Theoretic Semantic Parsing (Structural): Extracts logical operators 
       (negations, comparatives, conditionals) and numeric constraints to form a 
       'measurable' logical signature. This acts as the high-probability bound.
    2. Error-Correcting Code Simulation (Redundancy): Validates that the candidate 
       answer contains sufficient semantic 'redundancy' (keyword overlap with 
       extracted constraints) to withstand 'noise' (distractors). It checks if 
       the candidate satisfies the logical distance requirements.
    3. Type-Theoretic Certification: Only candidates passing structural checks 
       (Type Safety) and redundancy thresholds (Code Distance) receive high scores.
    4. NCD Tiebreaker: Used only when structural signals are ambiguous.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'false', 'impossible']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers for numeric evaluation."""
        pattern = r"[-+]?\d*\.?\d+"
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                pass
        return nums

    def _structural_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Parses logical structure (Measure Theory layer).
        Returns a score based on constraint satisfaction and a reason string.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.0
        reasons = []

        # 1. Negation Handling (Modus Tollens check)
        has_neg = any(n in p_low for n in self.negations)
        cand_yes = any(y in c_low for y in self.bool_yes)
        cand_no = any(n in c_low for n in self.bool_no)

        if has_neg:
            # If prompt has negation, expect negative answer or specific handling
            if cand_no:
                score += 0.4
                reasons.append("Negation alignment detected.")
            elif cand_yes:
                score -= 0.4
                reasons.append("Potential negation conflict.")
        
        # 2. Comparative Logic
        has_comp = any(c in p_low for c in self.comparatives)
        if has_comp:
            p_nums = self._extract_numbers(p_low)
            c_nums = self._extract_numbers(c_low)
            
            if p_nums and c_nums:
                # Check if candidate preserves or correctly transforms numeric logic
                # Simple heuristic: if prompt compares, candidate should ideally involve numbers or clear direction
                if c_nums:
                    score += 0.3
                    reasons.append("Numeric consistency in comparative context.")
                else:
                    # Check for directional words matching the comparison
                    if any(c in c_low for c in ['greater', 'larger', 'more']) or \
                       any(c in c_low for c in ['less', 'smaller', 'fewer']):
                        score += 0.2
                        reasons.append("Directional consistency detected.")
            else:
                # Fallback to keyword presence
                if any(c in c_low for c in self.comparatives):
                    score += 0.1
                    reasons.append("Comparative keyword match.")

        # 3. Conditional Logic
        has_cond = any(c in p_low for c in self.conditionals)
        if has_cond:
            if any(c in c_low for c in ['yes', 'no', 'true', 'false']) or len(c_low.split()) > 2:
                score += 0.2
                reasons.append("Conditional structure acknowledged.")

        # 4. Basic Constraint Propagation (Subject-Object role check via simple overlap)
        # Remove stopwords to get core tokens
        stopwords = {'the', 'is', 'a', 'an', 'of', 'to', 'in', 'it', 'that', 'this', 'with'}
        p_tokens = set(re.findall(r'\b\w+\b', p_low)) - stopwords
        c_tokens = set(re.findall(r'\b\w+\b', c_low)) - stopwords
        
        overlap = len(p_tokens & c_tokens)
        if overlap > 0:
            score += min(0.3, overlap * 0.05)
            reasons.append(f"Semantic overlap: {overlap} tokens.")

        return score, "; ".join(reasons) if reasons else "No strong structural signal."

    def _ecc_redundancy_check(self, prompt: str, candidate: str) -> float:
        """
        Simulates Error Correcting Code distance check.
        Treats key logical terms as 'parity bits'. If candidate lacks them, 
        it's considered 'corrupted' by noise.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        # Define critical parity bits (logical operators)
        parity_bits = self.negations + self.comparatives + self.conditionals + ['equal', 'difference']
        
        found_bits = 0
        total_bits = 0
        
        for bit in parity_bits:
            if bit in p_low:
                total_bits += 1
                if bit in c_low:
                    found_bits += 1
        
        if total_bits == 0:
            return 1.0 # No parity bits to check, assume safe
        
        # Redundancy ratio
        return found_bits / total_bits

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # Layer 1: Structural/Measure-Theoretic Score
            struct_score, reason = self._structural_score(prompt, cand)
            
            # Layer 2: ECC Redundancy Check
            ecc_factor = self._ecc_redundancy_check(prompt, cand)
            
            # Base score from structure
            final_score = struct_score
            
            # Apply ECC factor as a multiplier for confidence boost/penalty
            # If structural score is neutral, ECC doesn't help much. 
            # If structural score is positive, ECC amplifies it.
            if struct_score > 0:
                final_score *= (0.5 + 0.5 * ecc_factor)
            elif struct_score < 0:
                # Penalties are absolute
                pass 
            else:
                # If no structural signal, rely on NCD tiebreaker logic internally
                ncd = self._ncd_distance(prompt, cand)
                # Lower NCD is better (more similar), invert for score
                final_score = (1.0 - ncd) * 0.5 

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns a confidence score 0-1.
        Uses the evaluate logic but normalizes to [0, 1].
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]["score"]
        
        # Map raw score (approx -1.0 to 1.0) to 0.0 - 1.0
        # Sigmoid-like mapping centered at 0
        import math
        # Clamp for stability
        clamped = max(-2.0, min(2.0, raw_score))
        confidence = 1 / (1 + math.exp(-clamped * 2)) # Steepness factor
        
        return confidence