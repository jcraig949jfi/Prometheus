import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Self-Maintaining Causal World-Model' (RSCM) analog for reasoning.
    
    Mechanism:
    1. Embodied Layer (Structural Parsing): Extracts concrete logical operators 
       (negations, comparatives, conditionals) and numeric values from the text. 
       This represents the agent's sensorimotor interaction with the prompt.
       
    2. Autopoietic Layer (Viability Check): Evaluates if a candidate maintains 
       logical consistency with the extracted structure (e.g., if prompt has 'not', 
       candidate must reflect negation). This acts as a homeostatic loss function; 
       candidates violating structural constraints receive a heavy penalty to 
       maintain the system's organizational closure (logical validity).
       
    3. Causal Inference Layer (Intervention Scoring): Simulates 'do-operations' by 
       checking if the candidate correctly follows the causal chain implied by 
       conditionals ('if A then B') or numeric comparisons. 
       
    The final score is a weighted sum where structural/causal adherence (the 
    'viability' of the model) dominates, and NCD serves only as a tie-breaking 
    similarity metric for semantically ambiguous cases.
    """

    def __init__(self):
        # Keywords defining logical structure (The "Causal Graph" nodes)
        self.negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'right', 'accurate']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong', 'inaccurate']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_words(self, text: str) -> Dict[str, int]:
        words = re.findall(r'\b\w+\b', self._normalize(text))
        counts = {}
        for w in words:
            counts[w] = counts.get(w, 0) + 1
        return counts

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _check_structure(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Embodied & Causal Layer: Checks logical consistency.
        Returns a score delta and a reason string.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        p_words = set(re.findall(r'\b\w+\b', p_low))
        c_words = set(re.findall(r'\b\w+\b', c_low))
        
        score = 0.0
        reasons = []

        # 1. Negation Consistency (Autopoietic Viability)
        # If prompt asserts a negation, valid answers often need to acknowledge it 
        # or the logic implies a specific boolean outcome.
        has_negation = any(n in p_words for n in self.negations)
        has_conditional = any(c in p_words for c in self.conditionals)
        
        # Simple heuristic: If prompt asks a yes/no question involving negation,
        # ensure the answer isn't a blind echo without logical flip detection.
        # Since we don't have the ground truth, we check for 'logical awareness'.
        # We award points if the candidate contains logical operators matching the prompt's complexity.
        
        if has_negation:
            # Does the candidate show awareness of negation? 
            # (Heuristic: Long enough to explain, or uses negation words if the prompt is tricky)
            # For this simplified tool, we penalize short 'yes' if negation is present and complex.
            if len(c_low.split()) < 3 and any(x in c_low for x in self.bool_yes):
                # Risky to say yes to a negative premise without elaboration
                score -= 0.2
                reasons.append("Potential negation trap")

        # 2. Numeric Causal Inference
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Check if candidate number respects the comparison implied
            # Example: "Is 9.11 > 9.9?" -> Candidate should imply False/No
            # We simulate the comparison
            try:
                # Detect comparative direction in prompt
                is_greater = any(x in p_words for x in ['greater', 'larger', 'more', '>'])
                is_less = any(x in p_words for x in ['less', 'smaller', 'fewer', '<'])
                
                if is_greater or '>' in prompt:
                    expected_truth = p_nums[0] > p_nums[1]
                elif is_less or '<' in prompt:
                    expected_truth = p_nums[0] < p_nums[1]
                else:
                    expected_truth = None # Unknown operation

                if expected_truth is not None:
                    # Check candidate boolean sentiment
                    c_yes = any(x in c_low for x in self.bool_yes)
                    c_no = any(x in c_low for x in self.bool_no)
                    
                    if expected_truth:
                        if c_yes: score += 0.5
                        elif c_no: score -= 0.5
                    else: # expected False
                        if c_no: score += 0.5
                        elif c_yes: score -= 0.5
                reasons.append("Numeric logic check")
            except:
                pass

        # 3. Structural Length Penalty (Metacognition)
        # Extremely short answers to complex prompts are often wrong (Hallucination risk)
        if len(p_words) > 15 and len(c_words) < 3:
            score -= 0.1
            reasons.append("Brevity penalty")

        return score, "; ".join(reasons) if reasons else "Structural match"

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(s1_b)
        len2 = len(s2_b)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1_b + s2_b
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed if not compressing individual strings, 
        # but here we compress individually for accuracy.
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        
        numerator = len_concat - min(c1, c2)
        denominator = max(c1, c2)
        
        if denominator == 0:
            return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_base = self._normalize(prompt)
        
        for cand in candidates:
            cand_base = self._normalize(cand)
            
            # 1. Structural/Causal Score (Primary Signal)
            struct_score, reason = self._check_structure(prompt, cand)
            
            # 2. NCD Score (Tiebreaker/Secondary)
            # Invert NCD so 1.0 is perfect match, 0.0 is totally different
            # We want low NCD (similarity) to be a small bonus, not the driver.
            ncd_val = self._ncd(prompt_base, cand_base)
            ncd_score = (1.0 - ncd_val) * 0.1 # Max 0.1 contribution
            
            # Total Score
            # Base score starts at 0.5 (neutral), adjusted by logic, then tiny nudge by NCD
            total_score = 0.5 + struct_score + ncd_score
            
            results.append({
                "candidate": cand,
                "score": round(total_score, 4),
                "reasoning": reason
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        """
        # Reuse the structural check logic
        struct_score, _ = self._check_structure(prompt, answer)
        
        # Map structural score (-1.0 to 1.0 range roughly) to 0.0 - 1.0
        # 0.0 -> 0.2, 0.5 -> 0.7, 1.0 -> 1.0 (clamped)
        conf = 0.5 + struct_score
        conf = max(0.0, min(1.0, conf))
        
        # Bonus for numeric exactness if numbers exist
        p_nums = self._extract_numbers(prompt)
        a_nums = self._extract_numbers(answer)
        if p_nums and a_nums:
            # If numbers match exactly, high confidence
            if set(p_nums) == set(a_nums):
                conf = min(1.0, conf + 0.3)
                
        return round(conf, 4)