import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    AVIMDC-Inspired Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (The 'Organizational Constraint'): Extracts logical operators
       (negations, comparatives, conditionals) and numeric values. This satisfies the 
       'autopoietic' requirement by defining the system's internal structural integrity 
       without relying on external training data.
       
    2. Mechanism Design (The 'Incentive Compatibility'): Implements a proper scoring rule.
       Candidates are scored based on logical consistency with the parsed structure.
       Truthful alignment with structural constraints yields high 'payoff' (score).
       Contradictions (e.g., answering 'Yes' to a negative constraint) are heavily penalized.
       
    3. Thermodynamic Sampling (The 'Metabolic Cost'): Uses NCD as an entropy-based 
       tiebreaker only when structural signals are ambiguous, preventing runaway 
       exploration of semantically distant but structurally similar noise.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'only if']
        self.bool_yes = ['yes', 'true', 'correct', 'right', 'affirmative']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong', 'negative']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point numbers for numeric evaluation
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _check_structure(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Parses prompt for logical constraints and evaluates candidate against them.
        Returns (score, reasoning_string).
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.0
        reasons = []

        # 1. Negation Logic (Modus Tollens check)
        has_negation = any(n in p_low.split() for n in self.negations)
        is_yes = any(y in c_low.split() for y in self.bool_yes)
        is_no = any(n in c_low.split() for n in self.bool_no)

        if has_negation:
            # If prompt has negation, a 'No' answer often implies understanding the negation
            # depending on the question structure. Here we use a heuristic:
            # If prompt asks "Is it NOT X?" and candidate says "Yes", it's ambiguous.
            # Simplified: If prompt contains "not", and candidate contradicts the negation logic.
            # Heuristic: Strong penalty if candidate ignores explicit negation markers in specific contexts.
            if "is not" in p_low or "are not" in p_low:
                if is_yes:
                    score -= 0.5
                    reasons.append("Potential negation mismatch")
                elif is_no:
                    score += 0.5
                    reasons.append("Negation handled")

        # 2. Comparative Logic
        has_comparative = any(c in p_low for c in self.comparatives)
        nums = self._extract_numbers(prompt)
        cand_nums = self._extract_numbers(candidate)

        if has_comparative and len(nums) >= 2:
            # Determine direction
            direction = 1 # 1 for greater/more, -1 for less/fewer
            if any(x in p_low for x in ['less', 'fewer', 'smaller', 'lower']):
                direction = -1
            
            # Check if candidate number aligns with comparative logic
            if cand_nums:
                c_val = cand_nums[0]
                # Simple transitivity check: If A > B, and prompt asks for larger, expect A.
                # This is a simplified proxy for complex reasoning.
                if direction == 1 and c_val == max(nums):
                    score += 1.0
                    reasons.append("Comparative max selected")
                elif direction == -1 and c_val == min(nums):
                    score += 1.0
                    reasons.append("Comparative min selected")
                else:
                    score -= 1.0
                    reasons.append("Comparative mismatch")

        # 3. Boolean Consistency
        if is_yes and not is_no:
            score += 0.1 # Small base reward for decisive answer
        elif is_no and not is_yes:
            score += 0.1

        reason_str = "; ".join(reasons) if reasons else "Structural neutral"
        return score, reason_str

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate structural signals
        struct_scores = []
        max_struct_score = -float('inf')
        
        for cand in candidates:
            sc, reason = self._check_structure(prompt, cand)
            struct_scores.append((sc, reason, cand))
            if sc > max_struct_score:
                max_struct_score = sc

        # If structural parsing found distinct signals, prioritize them.
        # Otherwise, fall back to NCD (Thermodynamic tiebreaker).
        use_structure = max_struct_score > -float('inf') and any(s[0] != 0 for s in struct_scores)

        for i, cand in enumerate(candidates):
            sc, reason, _ = struct_scores[i]
            
            if use_structure:
                # Mechanism Design: Payoff based on structural truthfulness
                final_score = sc
                # Add small noise based on NCD to break ties deterministically but subtly
                ncd_val = self._ncd(prompt, cand)
                final_score -= (ncd_val * 0.01) 
            else:
                # Fallback: NCD as primary if no structure detected (rare in this design)
                # Lower NCD is better, so invert
                final_score = -self._ncd(prompt, cand)

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment strength.
        """
        sc, reason = self._check_structure(prompt, answer)
        
        # Map structural score to 0-1 confidence
        # Base confidence 0.5 (uncertain)
        conf = 0.5
        
        if "mismatch" in reason:
            conf = 0.1
        elif "handled" in reason or "selected" in reason:
            conf = 0.9
        elif sc > 0:
            conf = 0.6 + (sc * 0.2)
        elif sc < 0:
            conf = 0.4 - (abs(sc) * 0.2)
            
        return max(0.0, min(1.0, conf))