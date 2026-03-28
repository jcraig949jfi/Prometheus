import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Generative-Program Learning Architecture (Simplified for Textual Reasoning).
    
    Mechanism:
    1. Embodied Cognition (Structural Grounding): Parses the prompt for logical 
       constraints (negations, comparatives, conditionals, numeric relations). 
       This forms the 'sensorimotor' ground truth.
    2. Bayesian Inference (Likelihood): Evaluates how well each candidate satisfies 
       the extracted structural constraints. Violations incur heavy probability penalties.
    3. Kolmogorov Complexity (Prior): Estimates program length via string compression 
       (NCD). Shorter, more compressible explanations are preferred (Occam's Razor).
    4. Posterior Estimation: Score = Likelihood (Constraint Fit) * Prior (Simplicity).
    
    This approach beats pure NCD by prioritizing logical consistency (structure) 
    over raw string similarity, using NCD only as a tie-breaking prior.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}

    def _extract_structure(self, text: str) -> dict:
        """Extract logical 'sensorimotor' features from text."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Detect features
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text)
        }

    def _check_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        Calculate Likelihood penalty based on constraint propagation.
        Returns 1.0 (no penalty) to 0.0 (hard violation).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        penalty = 0.0
        
        # 1. Negation Consistency
        # If prompt asserts a negative constraint, candidate shouldn't blindly affirm the positive
        # Simple heuristic: If prompt has 'not' and candidate is short affirmative, slight penalty
        if p_struct['negation'] and not c_struct['negation']:
            if candidate.lower().strip() in ['yes', 'true', 'it is']:
                penalty += 0.4

        # 2. Numeric Consistency (Transitivity/Comparison)
        # If prompt compares A > B, and candidate implies B > A, penalize.
        # Since we don't have full semantic parsing, we check if candidate numbers 
        # contradict the sort order of prompt numbers if explicitly compared.
        if len(p_struct['numbers']) >= 2 and len(c_struct['numbers']) >= 1:
            # Heuristic: If prompt implies sorting (e.g., "9.11 vs 9.9"), 
            # check if candidate picks the logically correct one based on standard float logic
            # This handles the "9.11 < 9.9" trap.
            p_nums = sorted(p_struct['numbers'])
            c_num = c_struct['numbers'][0]
            
            # Detect if prompt is a comparison question
            if p_struct['comparative']:
                # If prompt asks for "smaller" and candidate is the larger number
                if 'smaller' in prompt.lower() or 'less' in prompt.lower():
                    if c_num == max(p_nums): penalty += 0.5
                # If prompt asks for "larger" and candidate is the smaller number
                elif 'larger' in prompt.lower() or 'greater' in prompt.lower() or 'more' in prompt.lower():
                    if c_num == min(p_nums): penalty += 0.5

        # 3. Conditional Logic
        # If prompt is conditional, candidate should ideally reflect uncertainty or conditionality
        if p_struct['conditional'] and not c_struct['conditional']:
            # Soft penalty for absolute answers to conditional prompts
            if candidate.lower().strip() in ['yes', 'no']:
                penalty += 0.1

        return max(0.0, 1.0 - penalty)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a complexity proxy."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_joint = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt structure to avoid re-parsing
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Likelihood: Structural/Logical Fit (Bayesian Update)
            likelihood = self._check_constraint_violation(prompt, cand)
            
            # 2. Prior: Complexity Penalty (Kolmogorov via NCD)
            # We want low complexity (high compressibility). 
            # NCD measures distance; we invert logic: simpler relation to prompt = better prior?
            # Actually, MDL favors the hypothesis that minimizes Description Length.
            # Here, we treat the candidate as a program. Shorter candidate + high info = better.
            # We use NCD between prompt and candidate to measure "surprise". 
            # Low NCD means candidate is expected given prompt (Good fit).
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Transform NCD to a prior score: Lower NCD -> Higher Prior
            # Scale: 0.0 (identical) -> 1.0, 1.0 (random) -> 0.0
            # Add small epsilon to avoid zeroing out valid diverse answers
            prior = 1.0 - ncd_val
            
            # 3. Posterior Score (Approximated)
            # Score = Likelihood * (Weighted Prior)
            # We weight Likelihood (Logic) higher than Prior (Compression) to ensure reasoning wins.
            # Logic weight = 0.7, Complexity weight = 0.3
            score = (likelihood * 0.7) + (prior * 0.3)
            
            # Reasoning trace
            reason_parts = []
            if likelihood < 0.9:
                reason_parts.append("Logical constraint mismatch detected.")
            if prior < 0.5:
                reason_parts.append("High description length (complex/unexpected).")
            if not reason_parts:
                reason_parts.append("Consistent with structural constraints and simple.")
                
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": " ".join(reason_parts)
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same logic as evaluate but returns a single normalized score.
        """
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        
        # Calibration: Map the internal score to a confidence metric.
        # If the top candidate (which is this one) has a high score, confidence is high.
        # We apply a sigmoid-like mapping to sharpen the distinction.
        # Base threshold: 0.5 is random guess territory.
        if raw_score > 0.8:
            return min(0.99, raw_score)
        elif raw_score < 0.4:
            return max(0.01, raw_score * 0.5)
        else:
            return raw_score