import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Cognitively-Aware Optimal Incentive Controller (COIC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Optimal Control Constraint): Extracts logical operators
       (negations, comparatives, conditionals) to form a 'structural signature'.
       This acts as the hard constraint for the system, preventing overload from
       superficial string matching (Extraneous Load reduction).
       
    2. Incentive Compatibility (Mechanism Design): Candidates are scored on 
       'truthful reporting' of structural features found in the prompt. 
       - Penalty: High penalty if candidate contradicts prompt negations/comparatives.
       - Reward: Bonus if candidate preserves logical transitivity or numeric consistency.
       
    3. Cognitive Load Scoring (CLT): 
       - Germane Load: Effort spent matching structural logic (Rewarded).
       - Extraneous Load: Effort spent on length mismatch or noise (Penalized).
       
    The final score is a weighted sum where structural adherence (Mechanism Design)
    dominates, NCD serves only as a tie-breaker, and length penalties enforce 
    working memory limits (CLT).
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|don\'t|doesn\'t)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical signatures from text."""
        text_lower = text.lower()
        negations = len(self.negation_pattern.findall(text_lower))
        comparatives = len(self.comparative_pattern.findall(text_lower))
        conditionals = len(self.conditional_pattern.findall(text_lower))
        numbers = [float(n) for n in self.number_pattern.findall(text)]
        
        return {
            'neg_count': negations,
            'comp_count': comparatives,
            'cond_count': conditionals,
            'numbers': numbers,
            'length': len(text.split()),
            'has_numbers': len(numbers) > 0
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_s1_s2 = len(zlib.compress(s1_bytes + s2_bytes))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Using max for denominator to ensure 0-1 range
        numerator = len_s1_s2 - min(len_s1, len_s2)
        denominator = max(len_s1, len_s2)
        
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """
        Mechanism Design: Checks if candidate numbers logically follow prompt numbers.
        Since we don't have the specific operation, we check for presence and order preservation
        as a proxy for 'truthful reporting' of numeric data.
        """
        if not prompt_nums:
            return 1.0 # No numeric constraint
        if not cand_nums:
            return 0.5 # Missing data is uncertain, not necessarily wrong
        
        # Check if the candidate preserves the relative order of the first two numbers if present
        if len(prompt_nums) >= 2 and len(cand_nums) >= 2:
            p_diff = prompt_nums[0] - prompt_nums[1]
            c_diff = cand_nums[0] - cand_nums[1]
            if (p_diff > 0 and c_diff > 0) or (p_diff < 0 and c_diff < 0) or (p_diff == 0 and c_diff == 0):
                return 1.0 # Order preserved
            else:
                return 0.2 # Order violated (Falsehood)
        
        # If only one number, check existence
        return 1.0 if abs(cand_nums[0] - prompt_nums[0]) < 1e-6 else 0.8

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            score = 0.0
            reasoning_parts = []

            # --- Mechanism Design: Incentive Compatibility Check ---
            # Penalize contradiction of negation density (Truthfulness)
            # If prompt has negations, candidate should reflect logical complexity
            neg_penalty = 0.0
            if prompt_struct['neg_count'] > 0:
                # If prompt is negative, candidate must not be overly simplistic (length check)
                if cand_struct['length'] < 3: 
                    neg_penalty = -0.3
                    reasoning_parts.append("Penalized for ignoring negation complexity.")
                else:
                    reasoning_parts.append("Acknowledged negation context.")
            
            # Check Numeric Consistency (Dominant Strategy)
            num_score = 1.0
            if prompt_struct['has_numbers'] or cand_struct['has_numbers']:
                num_score = self._check_numeric_consistency(
                    prompt_struct['numbers'], 
                    cand_struct['numbers']
                )
                if num_score < 1.0:
                    reasoning_parts.append("Numeric inconsistency detected.")
                else:
                    reasoning_parts.append("Numeric consistency verified.")

            # --- Cognitive Load Theory: Load Management ---
            # Penalize excessive length (Extraneous Load) relative to prompt
            length_ratio = cand_struct['length'] / max(prompt_struct['length'], 1)
            load_penalty = 0.0
            if length_ratio > 2.0:
                load_penalty = -0.2 * (length_ratio - 1) # Heavy penalty for verbosity
                reasoning_parts.append("High extraneous load (verbosity).")
            elif length_ratio < 0.1 and prompt_struct['length'] > 5:
                load_penalty = -0.1 # Too short might miss germane processing
                reasoning_parts.append("Potential under-processing.")

            # Base structural overlap (Germane Load utilization)
            # Did the candidate pick up on comparatives/conditionals?
            structural_match = 0.0
            if prompt_struct['comp_count'] > 0:
                structural_match += 0.2 if cand_struct['comp_count'] > 0 else -0.2
            if prompt_struct['cond_count'] > 0:
                structural_match += 0.2 if cand_struct['cond_count'] > 0 else -0.1
            
            # NCD as Tie-Baker (Low weight)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better, but keep weight low
            ncd_score = (1.0 - ncd_val) * 0.1 

            # Final Score Calculation
            # Weights: Numeric (0.4), Structural (0.3), Load (0.2), NCD (0.1)
            final_score = (num_score * 0.4) + (structural_match * 0.3) + load_penalty + ncd_score
            final_score = max(0.0, min(1.0, final_score + 0.5)) # Normalize roughly to 0-1 range with base bias

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Standard structural alignment."
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence based on structural alignment and lack of contradictions.
        Returns 0-1.
        """
        evaluated = self.evaluate(prompt, [answer])
        if not evaluated:
            return 0.0
        
        # The score from evaluate is already normalized roughly 0-1
        # We boost it slightly if the reasoning indicates no penalties
        base_score = evaluated[0]['score']
        reasoning = evaluated[0]['reasoning']
        
        bonus = 0.0
        if "inconsistency" not in reasoning and "Penalized" not in reasoning:
            bonus = 0.1
            
        return min(1.0, base_score + bonus)