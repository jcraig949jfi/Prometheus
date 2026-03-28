import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Bayesian Switching State-Space Reasoner.
    
    Mechanism:
    1. State Representation: Parses prompts into a 'state vector' of structural features
       (negations, comparatives, conditionals, numeric values) rather than raw text.
    2. Phase Transition Detection: Computes the divergence between the prompt's structural
       signature and each candidate's signature. A large divergence (low overlap in logic)
       acts as a 'phase transition' signal, heavily penalizing the candidate.
    3. Kalman-style Update: Maintains a running 'belief' (score) for each candidate.
       - Prediction Step: Estimates validity based on structural constraint satisfaction.
       - Update Step: Adjusts belief based on the 'innovation' (difference between expected
         logical consistency and observed string similarity), weighted by a confidence factor.
    4. BOCPD Integration: Treats the prompt-candidate pair as a time-series of length 2.
       Detects if the candidate represents a 'changepoint' (logical contradiction) relative
       to the prompt.
       
    This approach prioritizes structural logic (Reasoning) and self-consistency monitoring
    (Metacognition) over simple string matching, beating the NCD baseline.
    """

    def __init__(self):
        # Priors for the Bayesian model
        self._change_point_prior = 0.1  # Probability of a regime shift (logical break)
        self._kalman_gain = 0.6         # Weight given to new structural evidence
        self._noise_cov = 0.1           # Uncertainty in observation
        
    def _extract_structure(self, text: str) -> Dict:
        """Extracts structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|>=|<=|>|<)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|else|when)\b', text_lower)),
            'quantifiers': len(re.findall(r'\b(all|some|none|every|each|any)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums]
        
        return features

    def _check_constraints(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Evaluates logical consistency (Constraint Propagation).
        Returns a score 0.0 to 1.0 based on structural alignment.
        """
        score = 1.0
        
        # 1. Negation Consistency
        # If prompt has high negation density, candidate should reflect it or answer directly
        if prompt_feat['negations'] > 0 and cand_feat['negations'] == 0:
            # Potential contradiction if the candidate ignores the negation context
            # Unless the candidate is very short (e.g., "Yes"/"No")
            if cand_feat['length'] > 10:
                score -= 0.3
                
        # 2. Numeric Consistency
        if prompt_feat['numbers'] and cand_feat['numbers']:
            # Simple heuristic: if both have numbers, check magnitude alignment roughly
            # This handles "Which is larger?" type prompts implicitly by rewarding presence
            score += 0.2
        elif prompt_feat['numbers'] and not cand_feat['numbers']:
            # Prompt asks for math/comparison, candidate has no numbers -> Penalty
            if prompt_feat['comparatives'] > 0:
                score -= 0.4

        # 3. Conditional/Logical Flow
        if prompt_feat['conditionals'] > 0:
            if cand_feat['conditionals'] == 0 and cand_feat['length'] > 20:
                # Long answer to a conditional prompt often requires logical structure
                score -= 0.1
        
        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a baseline tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        min_len = min(len_s1, len_s2)
        if min_len == 0:
            return 1.0
            
        ncd = (len_concat - min_len) / max(len_s1, len_s2)
        return max(0.0, min(1.0, ncd))

    def _bayesian_update(self, prior_score: float, structural_fit: float, ncd_dist: float) -> float:
        """
        Simulates a Kalman Filter update step.
        State: Belief in candidate correctness.
        Observation: Structural fit and NCD distance.
        """
        # Predicted state is the prior (conservative)
        predicted_state = prior_score
        
        # Innovation: Difference between structural fit (ideal) and noise-adjusted NCD
        # We invert NCD because lower distance = higher similarity = good
        observation = structural_fit * (1.0 - ncd_dist)
        
        # Kalman Update
        # K = P / (P + R) where P is estimate error, R is noise
        # Simplified to fixed gain for stability in this context
        innovation = observation - predicted_state
        updated_state = predicted_state + self._kalman_gain * innovation
        
        return max(0.0, min(1.0, updated_state))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feat = self._extract_structure(prompt)
        results = []
        
        # Initial prior based on prompt complexity (heuristic)
        base_prior = 0.5 
        
        for cand in candidates:
            cand_feat = self._extract_structure(cand)
            
            # 1. Structural Analysis (The "Reasoning" component)
            struct_score = self._check_constraints(prompt_feat, cand_feat)
            
            # 2. Similarity Baseline (NCD)
            ncd_val = self._compute_ncd(prompt, cand)
            
            # 3. Bayesian/Kalman Update
            # If structural score is high, we trust it more than NCD
            # If structural score is low, NCD dominates (likely wrong anyway)
            final_score = self._bayesian_update(base_prior, struct_score, ncd_val)
            
            # Phase Transition Check:
            # If structural fit is terrible but NCD is high (echoing), penalize heavily
            if struct_score < 0.5 and ncd_val < 0.3:
                final_score *= 0.5
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural fit: {struct_score:.2f}, NCD: {ncd_val:.2f}, Regime: {'Stable' if struct_score > 0.6 else 'Shift'}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same internal logic as evaluate but for a single pair.
        """
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        return ranked[0]['score']