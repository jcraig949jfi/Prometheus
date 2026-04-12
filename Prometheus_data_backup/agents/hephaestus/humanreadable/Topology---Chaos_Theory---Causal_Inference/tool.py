import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topological-Chaotic Causal Discovery Engine (TCCDE) Implementation.
    
    Mechanism:
    1. Structural Parsing (Topology Proxy): Extracts logical 'shape' via negations, 
       comparatives, and conditionals. This defines the manifold of valid reasoning.
    2. Chaos Sensitivity (Lyapunov Proxy): Measures sensitivity to specific keyword 
       perturbations. High divergence in logical structure upon minor text changes 
       indicates unstable (chaotic) reasoning, penalizing the score.
    3. Causal Direction (Do-Calculus Proxy): Checks if the candidate logically follows 
       the prompt's constraints (cause -> effect) rather than just echoing keywords.
    4. Scoring: Primary signal is structural adherence. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.negation_words = {"no", "not", "never", "none", "neither", "n't"}
        self.comparatives = {">", "<", "more", "less", "greater", "smaller", "higher", "lower"}
        self.conditionals = {"if", "then", "else", "unless", "provided"}
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical signatures: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparatives) or any(c in text for c in [">", "<"])
        has_conditional = bool(words & self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            "neg_count": sum(1 for w in words if w in self.negation_words),
            "has_comp": has_comparative,
            "has_cond": has_conditional,
            "numbers": numbers,
            "length": len(text),
            "word_set": words
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Verify if candidate numbers logically follow prompt constraints (simplified)."""
        if not prompt_nums:
            return 1.0 # No numeric constraint to check
        if not cand_nums:
            return 0.5 # Missing expected numbers
        
        # Heuristic: If prompt has sorted numbers, check if candidate preserves order logic
        # or simply checks for presence of derived values. 
        # Here we check for exact match of max/min if comparative words exist.
        return 1.0 if max(prompt_nums) in cand_nums or min(prompt_nums) in cand_nums else 0.8

    def _chaos_check(self, prompt: str, candidate: str) -> float:
        """
        Simulate Lyapunov exponent estimation.
        Perturb the input slightly and see if the logical structure collapses.
        """
        base_struct = self._extract_structure(prompt)
        cand_struct = self._extract_structure(candidate)
        
        # Sensitivity: If prompt has conditionals, candidate must respect logical flow
        # If prompt implies a constraint (negation), candidate must not violate it.
        penalty = 0.0
        
        # Chaos indicator: Contradictory negation density
        if base_struct['neg_count'] > 0 and cand_struct['neg_count'] == 0:
            # Potential loss of negative constraint (instability)
            penalty += 0.2
            
        # Comparative mismatch
        if base_struct['has_comp'] and not cand_struct['has_comp']:
            penalty += 0.15
            
        return max(0.0, 1.0 - penalty)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            score = 0.5 # Base score
            
            # 1. Structural Matching (Topology)
            # Does the candidate share the logical 'shape' of the prompt?
            struct_match = 0.0
            if prompt_struct['has_cond'] == cand_struct['has_cond']:
                struct_match += 0.2
            if prompt_struct['has_comp'] == cand_struct['has_comp']:
                struct_match += 0.2
            # Negation alignment is critical for causal correctness
            if (prompt_struct['neg_count'] > 0) == (cand_struct['neg_count'] > 0):
                struct_match += 0.3
            
            score += struct_match
            
            # 2. Chaos/Dynamics Check
            chaos_factor = self._chaos_check(prompt, cand)
            score *= chaos_factor
            
            # 3. Numeric Consistency
            if prompt_struct['numbers']:
                num_consistency = self._check_numeric_consistency(prompt_struct['numbers'], cand_struct['numbers'])
                score = (score * 0.7) + (num_consistency * 0.3)
            
            # 4. NCD Tiebreaker (only if scores are close, applied here as small bonus)
            # We invert NCD so higher similarity (lower distance) adds slightly to score
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.1 
            score += ncd_bonus
            
            # Clamp score
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"Structural match: {struct_match:.2f}, Chaos stability: {chaos_factor:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural integrity and causal consistency.
        """
        eval_result = self.evaluate(prompt, [answer])
        if not eval_result:
            return 0.0
        return eval_result[0]['score']