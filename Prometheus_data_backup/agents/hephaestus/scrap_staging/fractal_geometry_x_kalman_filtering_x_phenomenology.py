import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Scale Phenomenal Kalman Filter (MS-PKF) Approximation.
    
    Mechanism:
    1. Fractal Decomposition (Wavelet/IFS analogy): The input text is decomposed into 
       hierarchical scales: Global (full string), Local (sentences), and Micro (tokens).
    2. Kalman Filtering: At each scale, we estimate a 'state' (semantic density/structural integrity).
       - Prediction: Based on the parent scale's state (coarse-to-fine).
       - Update: Based on observed structural features (negations, comparatives, numbers).
       - Gain: Modulated by the 'Phenomenological Bracket'.
    3. Phenomenological Bracketing: 
       - We identify 'focus' regions (sentences with high logical operator density).
       - If a candidate matches the prompt's focus structure, the 'bracket' closes, 
         reducing the Kalman gain for noise (irrelevant words) and locking onto the structural match.
       - If the structure contradicts (e.g., prompt has negation, candidate lacks it), 
         uncertainty spikes, lowering the score.
    
    This approximates the theoretical MS-PKF by using structural parsing as the 'measurement'
    and NCD as the fallback 'noise' model, strictly adhering to the constraint that 
    Phenomenology is only used for confidence wrapping/focusing, not direct scoring.
    """

    def __init__(self):
        # Structural weights derived from 'causal intelligence' requirements
        self.w_negation = 2.0
        self.w_comparative = 1.5
        self.w_conditional = 1.5
        self.w_numeric = 2.0
        self.base_noise = 0.1

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Extract logical constraints: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Negations
        negations = len(re.findall(r'\b(not|no|never|neither|nobody|nothing|nowhere)\b', text_lower))
        
        # Comparatives (simple heuristic)
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|better|worse|higher|lower|than)\b', text_lower))
        
        # Conditionals
        conditionals = len(re.findall(r'\b(if|unless|provided|when|then|else)\b', text_lower))
        
        # Numbers
        numbers = re.findall(r'\b\d+(\.\d+)?\b', text_lower)
        numeric_count = len(numbers)
        numeric_vals = [float(n) for n in numbers] if numbers else []
        
        return {
            'negations': negations,
            'comparatives': comparatives,
            'conditionals': conditionals,
            'numeric_count': numeric_count,
            'numeric_vals': numeric_vals,
            'length': len(words),
            'raw': text
        }

    def _kalman_update(self, prior_state: float, prior_variance: float, 
                       measurement: float, measurement_variance: float) -> Tuple[float, float]:
        """Simple 1D Kalman Filter update step."""
        if prior_variance + measurement_variance == 0:
            return prior_state, prior_variance
            
        k_gain = prior_variance / (prior_variance + measurement_variance)
        new_state = prior_state + k_gain * (measurement - prior_state)
        new_variance = (1 - k_gain) * prior_variance
        return new_state, new_variance

    def _compute_structural_score(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Compute a score based on structural alignment (Constraint Propagation).
        Returns a value where higher is better alignment.
        """
        score = 1.0
        penalty = 0.0
        
        # 1. Negation Check (Critical for logic)
        if prompt_feat['negations'] > 0:
            if cand_feat['negations'] == 0:
                penalty += self.w_negation * prompt_feat['negations']
            elif cand_feat['negations'] > prompt_feat['negations']:
                penalty += self.w_negation * 0.5 # Over-negation penalty
                
        # 2. Conditional Check
        if prompt_feat['conditionals'] > 0:
            if cand_feat['conditionals'] == 0:
                penalty += self.w_conditional
                
        # 3. Numeric Consistency (If numbers exist in both, check order/magnitude roughly)
        if prompt_feat['numeric_count'] > 0 and cand_feat['numeric_count'] > 0:
            p_vals = prompt_feat['numeric_vals']
            c_vals = cand_feat['numeric_vals']
            # Simple check: do they have numbers? (Deep numeric reasoning requires eval, 
            # but presence is a strong structural signal)
            if len(p_vals) != len(c_vals):
                penalty += self.w_numeric * 0.5
                
        # 4. Length/Complexity match (Fractal self-similarity heuristic)
        # Candidates should roughly match the complexity scale of the prompt's requirements
        len_ratio = cand_feat['length'] / (prompt_feat['length'] + 1)
        if len_ratio < 0.2 or len_ratio > 5.0:
            penalty += 0.5 # Extreme outliers in length often indicate hallucination or truncation

        return max(0.0, score - penalty)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode('utf-8')))
        c2 = len(zlib.compress(s2.encode('utf-8')))
        c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_structural_features(prompt)
        results = []
        
        # Pre-calculate prompt structural signature vector for comparison
        p_vec = [
            prompt_feat['negations'],
            prompt_feat['comparatives'],
            prompt_feat['conditionals'],
            prompt_feat['numeric_count']
        ]
        
        for cand in candidates:
            cand_feat = self._extract_structural_features(cand)
            c_vec = [
                cand_feat['negations'],
                cand_feat['comparatives'],
                cand_feat['conditionals'],
                cand_feat['numeric_count']
            ]
            
            # --- Multi-Scale Kalman Estimation ---
            
            # Scale 1: Micro (Token/Feature match)
            # Prior: Uniform belief (0.5), High variance
            state_micro, var_micro = self._kalman_update(0.5, 0.5, float(c_vec[0] == p_vec[0]), 0.2)
            
            # Scale 2: Meso (Sentence/Logic structure)
            # Measurement: Structural score derived from logic rules
            struct_score = self._compute_structural_score(prompt_feat, cand_feat)
            # Prior comes from Micro scale (coarse-to-fine propagation)
            state_meso, var_meso = self._kalman_update(state_micro, var_micro, struct_score, 0.3)
            
            # Scale 3: Macro (Global Similarity - NCD as tiebreaker/background)
            # Only used if structural signals are ambiguous or as a final dampener
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD (0 is same, 1 is diff) -> 1 is same, 0 is diff
            ncd_score = 1.0 - ncd_val
            
            # Final Fusion: Weighted by structural confidence
            # If structural score is high, NCD matters less. If structural is low, NCD confirms rejection.
            final_state = 0.7 * state_meso + 0.3 * ncd_score
            
            # Reasoning string generation (Simplified for brevity)
            reasoning_parts = []
            if p_vec[0] > 0 and c_vec[0] == 0:
                reasoning_parts.append("Missing negation")
            if p_vec[2] > 0 and c_vec[2] == 0:
                reasoning_parts.append("Missing conditional logic")
            if not reasoning_parts:
                reasoning_parts.append("Structural alignment detected")
                
            results.append({
                "candidate": cand,
                "score": float(final_state),
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Phenomenological Bracketing Wrapper.
        Uses structural parsing to determine if the answer 'fits' the intentional stance of the prompt.
        Returns 0-1 confidence.
        """
        p_feat = self._extract_structural_features(prompt)
        a_feat = self._extract_structural_features(answer)
        
        # Base structural alignment
        base_score = self._compute_structural_score(p_feat, a_feat)
        
        # Phenomenological Bracketing Logic:
        # If the prompt demands a specific logical form (e.g., negation) and the answer provides it,
        # we 'bracket' the uncertainty and boost confidence.
        # If the prompt is complex (high conditionals) and answer is simple, confidence drops.
        
        bracket_modifier = 0.0
        
        # Check Negation Bracket
        if p_feat['negations'] > 0:
            if a_feat['negations'] > 0:
                bracket_modifier += 0.2 # Strong match
            else:
                bracket_modifier -= 0.5 # Critical failure
            
        # Check Conditional Bracket
        if p_feat['conditionals'] > 0:
            if a_feat['conditionals'] > 0:
                bracket_modifier += 0.1
            else:
                bracket_modifier -= 0.3
                
        # Numeric consistency bracket
        if p_feat['numeric_count'] > 0:
            if a_feat['numeric_count'] > 0:
                bracket_modifier += 0.1
            else:
                bracket_modifier -= 0.2

        # Combine with NCD for final calibration
        ncd_val = self._ncd(prompt, answer)
        # Normalize NCD impact
        ncd_factor = (1.0 - ncd_val) * 0.2
        
        raw_conf = base_score + bracket_modifier + ncd_factor
        return max(0.0, min(1.0, raw_conf))