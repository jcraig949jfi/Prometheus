import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Hierarchical Predictive-Coding Tool.
    
    Mechanism:
    1. Theta-Gamma Sampling (Hypothesis Generation): Parses prompts for structural
       constraints (negations, comparatives, conditionals, numerics). These form
       the 'global hypothesis' window.
    2. Hierarchical Kalman Update (Belief Revision): Computes a base score based
       on constraint satisfaction (structural parsing) and numeric validity.
    3. PID-Regulated Precision (Feedback Control):
       - Error (e): Deviation from perfect constraint satisfaction.
       - Precision (P): Dynamically adjusted gain. If error is high, precision
         drops (broadening uncertainty), preventing over-confidence in bad matches.
       - The final score is a precision-weighted combination of structural match
         and NCD similarity.
    
    This implements the requested Bayesian/Oscillatory/Control synthesis by using
    structural parsing as the 'gamma' evidence accumulation and PID logic as the
    'neuromodulatory' gain control over the final confidence score.
    """

    def __init__(self):
        # PID Controller State for Precision Regulation
        self.k_p = 0.6  # Proportional gain (response to current error)
        self.k_i = 0.1  # Integral gain (response to accumulated error)
        self.k_d = 0.05 # Derivative gain (response to rate of change)
        self._prev_error = 0.0
        self._integral_error = 0.0
        
        # Baseline threshold for NCD tie-breaking
        self.ncd_threshold = 0.85

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance (0-1)."""
        if not s1 or not s2:
            return 1.0
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            ncd = (c12 - min(c1, c2)) / denom
            return min(1.0, max(0.0, ncd))
        except:
            return 1.0

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Theta-window: Extracts logical constraints and numeric values."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(no|not|never|neither|none|without)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise|else)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text_lower)],
            'length': len(text.split())
        }
        return features

    def _evaluate_numeric_logic(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Gamma-burst: Fast local belief revision based on numeric consistency."""
        if not prompt_nums:
            return 1.0 # No numeric constraints to violate
        
        if not cand_nums:
            return 0.2 # Penalty for missing numbers when prompt has them
        
        # Simple transitivity/comparison check
        # If prompt implies ordering, does candidate respect it?
        # Heuristic: Check if relative magnitudes are preserved
        if len(prompt_nums) >= 2 and len(cand_nums) >= 2:
            p_diff = prompt_nums[0] - prompt_nums[1]
            c_diff = cand_nums[0] - cand_nums[1]
            if (p_diff > 0 and c_diff < 0) or (p_diff < 0 and c_diff > 0):
                return 0.1 # Contradiction in ordering
        return 1.0

    def _pid_adjust_precision(self, error: float) -> float:
        """
        Feedback Control: Adjusts precision (gain) based on prediction error.
        High error -> Lower precision (uncertainty broadening).
        Low error -> Higher precision (confidence sharpening).
        """
        self._integral_error += error
        derivative = error - self._prev_error
        self._prev_error = error
        
        # PID Output represents the 'correction' to the baseline uncertainty
        # We map this to a precision gain factor (0.2 to 1.0)
        correction = (self.k_p * error) + (self.k_i * self._integral_error) + (self.k_d * derivative)
        
        # Invert logic: High error should reduce precision (gain)
        # Base precision 1.0, subtract weighted error impact
        precision = 1.0 - min(0.8, max(0.0, correction))
        return max(0.1, precision)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_structural_features(prompt)
        prompt_nums = prompt_feat['numbers']
        prompt_len = prompt_feat['length']
        
        results = []
        
        for cand in candidates:
            cand_feat = self._extract_structural_features(cand)
            cand_nums = cand_feat['numbers']
            
            # 1. Structural Constraint Satisfaction (The "Reasoning" Score)
            structural_score = 1.0
            
            # Negation consistency (simplified: if prompt negates, candidate shouldn't affirm blindly)
            # This is a proxy for logical consistency
            if prompt_feat['has_negation'] and not cand_feat['has_negation']:
                # Soft penalty unless candidate is clearly a direct answer
                if len(cand.split()) > 1: 
                    structural_score -= 0.2
            
            # Numeric Logic
            numeric_score = self._evaluate_numeric_logic(prompt_nums, cand_nums)
            structural_score *= numeric_score
            
            # 2. NCD Similarity (The "Similarity" Score)
            ncd_val = self._compute_ncd(prompt, cand)
            # Convert distance to similarity (1 - ncd)
            similarity_score = 1.0 - ncd_val
            
            # 3. PID-Regulated Fusion
            # Error is defined as (1 - structural_score). 
            # If structural logic is perfect, error is 0.
            error = 1.0 - structural_score
            
            # Get dynamic precision gain
            precision_gain = self._pid_adjust_precision(error)
            
            # Final Score: Weighted sum where weights are modulated by precision
            # If precision is low (high error), we rely less on the structural claim 
            # and more on the raw similarity (or rather, the whole score is dampened).
            # Here we interpret 'precision' as the confidence in the structural evaluation.
            final_score = (structural_score * precision_gain) + (similarity_score * (1.0 - precision_gain) * 0.5)
            
            # Normalize to 0-1 range roughly
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{structural_score:.2f}, NCD:{similarity_score:.2f}, Precision:{precision_gain:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the internal evaluation logic."""
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']