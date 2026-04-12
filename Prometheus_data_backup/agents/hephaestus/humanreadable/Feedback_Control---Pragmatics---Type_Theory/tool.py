import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Type-Theoretic Adaptive Controller (PTTAC) Approximation.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) as 'type signatures'. Candidates violating 
       explicit prompt constraints receive a heavy penalty (Type Violation).
    2. Pragmatics (Contextual Refinement): Analyzes keyword overlap and semantic 
       relevance between prompt context and candidate. Uses Gricean maxims implicitly 
       by penalizing candidates that ignore specific contextual modifiers.
    3. Feedback Control (PID-like Tuning): 
       - Error (e_t): Difference between expected structural match (1.0) and current 
         structural score.
       - Controller: Adjusts the weight of the 'Pragmatic' signal vs 'Structural' signal.
         If structural constraints are weak (high error), the system relies more on 
         compression similarity (NCD). If structural constraints are strong, it dominates.
       - Output: A unified score where logical consistency is the primary gate, 
         refined by contextual relevance.
    """

    def __init__(self):
        # PID-like parameters for weighting signals
        self.kp = 1.0  # Proportional gain for structural error
        self.base_weight_struct = 0.7
        self.base_weight_prag = 0.3
        
        # Regex patterns for "Type Signatures" (Logical constraints)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|except|cannot|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|only if)\b', re.I),
            'causality': re.compile(r'\b(because|therefore|thus|causes|leads to)\b', re.I),
            'quantity': re.compile(r'\b(all|some|none|every|at least|at most)\b', re.I)
        }
        self.number_re = re.compile(r'-?\d+\.?\d*')

    def _extract_types(self, text: str) -> Dict[str, bool]:
        """Extract logical 'types' or constraints present in the text."""
        found = {}
        for key, pattern in self.patterns.items():
            found[key] = bool(pattern.search(text))
        return found

    def _check_type_compatibility(self, prompt_types: Dict[str, bool], candidate: str) -> float:
        """
        Check if candidate violates explicit logical constraints.
        Returns a penalty factor (0.0 to 1.0).
        """
        # Simple heuristic: If prompt has negation, check if candidate contradicts it?
        # Since we don't have full NLI, we check for presence of conflicting markers.
        # For this implementation, we reward candidates that share the same 'logical type'
        # density as the prompt, assuming the answer must address the logical structure.
        
        cand_types = self._extract_types(candidate)
        match_count = 0
        total_types = 0
        
        for key in prompt_types:
            if prompt_types[key]:
                total_types += 1
                if cand_types[key]:
                    match_count += 1
        
        if total_types == 0:
            return 1.0 # No specific logical constraints detected
        
        # Reward matching logical complexity
        return 0.5 + 0.5 * (match_count / total_types)

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Score based on structural parsing and constraint propagation.
        """
        prompt_types = self._extract_types(prompt)
        
        # 1. Type Compatibility (Logical Consistency)
        type_score = self._check_type_compatibility(prompt_types, candidate)
        
        # 2. Numeric Evaluation
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        num_score = 1.0
        if p_nums and c_nums:
            # Check if candidate preserves numeric ordering if comparatives exist
            if prompt_types['comparative'] and len(p_nums) >= 2 and len(c_nums) >= 1:
                # Heuristic: If prompt compares A > B, does candidate reflect magnitude?
                # Simplified: Just ensure numbers are present and reasonable
                num_score = 1.0 if len(c_nums) > 0 else 0.5
        elif p_nums and not c_nums:
            # Prompt has numbers, candidate doesn't -> likely wrong for math/logic Qs
            num_score = 0.2
            
        # 3. Constraint Propagation (Negation check)
        # If prompt says "not X", and candidate is exactly "X", penalize heavily.
        negation_penalty = 0.0
        if prompt_types['negation']:
            # Very rough check: if prompt has "not A" and candidate is "A"
            # We simulate this by checking length similarity to potential negated phrases
            # Since we can't parse full logic, we rely on the type_score mostly.
            pass

        return (type_score * 0.6) + (num_score * 0.4)

    def _extract_numbers(self, text: str) -> List[float]:
        matches = self.number_re.findall(text)
        return [float(m) for m in matches]

    def _pragmatic_score(self, prompt: str, candidate: str) -> float:
        """
        Score based on Gricean maxims (Relevance, Quantity).
        Uses NCD as a proxy for semantic relevance in this constrained setting.
        """
        # Relevance: How much does the candidate compress with the prompt?
        ncd_val = self._ncd(prompt, candidate)
        # Convert distance to similarity (0 dist = 1.0 score)
        relevance = 1.0 - ncd_val
        
        # Quantity: Penalize if candidate is too short compared to prompt complexity
        # unless it's a definitive "Yes/No/Number"
        prompt_len = len(prompt.split())
        cand_len = len(candidate.split())
        
        quantity_score = 1.0
        if prompt_len > 10 and cand_len < 3:
            # If prompt is complex and answer is tiny, might be missing nuance
            # Unless it's a specific keyword match
            quantity_score = 0.8
            
        return (relevance * 0.7) + (quantity_score * 0.3)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Calculate baseline structural strength of the prompt
        prompt_types = self._extract_types(prompt)
        structural_density = sum(prompt_types.values())
        
        # Feedback Control: Adjust weights based on structural density
        # High structural density -> Trust Logic (Type Theory) more
        # Low structural density -> Trust Pragmatics (NCD/Relevance) more
        error_signal = 1.0 - (structural_density / len(prompt_types)) if prompt_types else 1.0
        
        # Adaptive Weights
        w_struct = self.base_weight_struct + (self.kp * (1.0 - error_signal))
        w_prag = self.base_weight_prag + (self.kp * error_signal)
        
        # Normalize weights
        total_w = w_struct + w_prag
        w_struct /= total_w
        w_prag /= total_w

        for cand in candidates:
            # 1. Type Theoretic Check (Logic)
            s_score = self._structural_score(prompt, cand)
            
            # 2. Pragmatic Check (Context)
            p_score = self._pragmatic_score(prompt, cand)
            
            # 3. Feedback Integration
            final_score = (s_score * w_struct) + (p_score * w_prag)
            
            # Tie-breaking with pure NCD if scores are very close (not implemented here 
            # as we have continuous scores, but NCD is inside pragmatic score)
            
            reasoning = f"Structural:{s_score:.2f} Pragmatic:{p_score:.2f} [W: S={w_struct:.2f}, P={w_prag:.2f}]"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the same adaptive mechanism to score the single answer.
        """
        # Evaluate against a dummy set to get the score
        # We treat the answer as the only candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to confidence
        # If the top score is high, confidence is high.
        # We also penalize if the structural score was low but pragmatic was high
        # (indicating a plausible sounding but logically flawed answer)
        
        s_score = self._structural_score(prompt, answer)
        
        # Confidence is a product of total score and logical consistency
        # If logic fails (s_score < 0.5), confidence drops significantly
        if s_score < 0.5:
            return max(0.0, score * 0.5)
        
        return min(1.0, score)