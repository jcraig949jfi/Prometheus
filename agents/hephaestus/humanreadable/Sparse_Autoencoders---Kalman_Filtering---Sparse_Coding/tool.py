import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Temporal Sparse Predictive Coding Reasoner.
    
    Mechanism:
    1. Dictionary Learning (SAE analog): Constructs a fixed basis of semantic 
       features (negations, comparatives, numbers, logic keywords) from the prompt.
    2. Sparse Coding (ISTA analog): Projects the prompt and candidates into this 
       basis, enforcing sparsity (L1 penalty) to isolate only relevant logical operators.
    3. Kalman Filtering: Treats the 'truth value' as a hidden state. 
       - Prediction: Based on logical consistency of active sparse features.
       - Update: Corrects the state estimate using the 'innovation' (difference between 
         candidate implication and prompt constraints).
    4. Scoring: Uses the final Kalman state mean and inverse covariance (uncertainty) 
       to rank candidates.
    """

    def __init__(self):
        # Semantic basis vectors (Dictionary D) - simplified to keyword presence
        self.basis_keys = [
            'not', 'no', 'never', 'false', # Negation
            'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', # Comparatives
            'if', 'then', 'else', 'unless', 'only if', # Conditionals
            'all', 'every', 'some', 'none', 'any', # Quantifiers
            'before', 'after', 'first', 'last', # Temporal/Order
            'true', 'yes', 'correct', 'valid' # Affirmation
        ]
        self.basis_size = len(self.basis_keys)
        
        # Kalman Parameters
        self.process_noise = 0.1
        self.measurement_noise = 0.5
        self.sparsity_lambda = 0.3
        
        # Cache for deterministic behavior
        self._state_cache = {}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b|[<>]', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and integers
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _encode_sparse(self, text: str) -> np.ndarray:
        """Map text to sparse latent code z using dictionary matching."""
        tokens = self._tokenize(text)
        z = np.zeros(self.basis_size)
        
        # Hard assignment based on keyword presence (Dictionary Learning analog)
        for i, key in enumerate(self.basis_keys):
            if key in tokens:
                z[i] = 1.0
                
        # ISTA-like soft thresholding to enforce sparsity and reduce noise
        # z = sign(z) * max(|z| - lambda, 0)
        z = np.sign(z) * np.maximum(np.abs(z) - self.sparsity_lambda, 0)
        return z

    def _logical_consistency_check(self, prompt: str, candidate: str) -> float:
        """
        Heuristic evaluator for logical consistency (The 'Measurement' in Kalman).
        Returns a score: 1.0 (consistent), 0.5 (neutral), 0.0 (contradictory).
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # 1. Negation Handling
        negation_words = ['not', 'no', 'never', 'false', 'impossible']
        p_has_neg = any(w in p_low for w in negation_words)
        c_has_neg = any(w in c_low for w in negation_words)
        
        # If prompt implies negation and candidate affirms (or vice versa), penalize
        if p_has_neg != c_has_neg:
            # Check if the candidate is just repeating the prompt structure
            if c_low in p_low or p_low in c_low:
                return 1.0 # Repetition is usually safe
            return 0.2 # Contradiction
        
        # 2. Numeric Consistency
        p_nums = self._extract_numbers(p_low)
        c_nums = self._extract_numbers(c_low)
        
        if p_nums and c_nums:
            # Simple transitivity check: if prompt says A > B, candidate shouldn't say B > A
            # This is a simplified proxy for complex logic
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_diff = p_nums[0] - p_nums[1]
                c_diff = c_nums[0] - c_nums[1]
                if p_diff * c_diff < 0: # Signs opposite
                    return 0.1
        
        # 3. Keyword Overlap (Bag of words with weight)
        # Only effective if structural checks pass
        p_tokens = set(self._tokenize(p_low))
        c_tokens = set(self._tokenize(c_low))
        intersection = p_tokens.intersection(c_tokens)
        
        # Boost if candidate contains specific logical operators found in prompt
        logic_overlap = 0
        for k in self.basis_keys:
            if k in p_tokens and k in c_tokens:
                logic_overlap += 0.1
        
        base_score = len(intersection) / (len(p_tokens) + 0.1) 
        return min(1.0, base_score + logic_overlap + 0.5)

    def _run_kalman_step(self, z_prompt: np.ndarray, z_cand: np.ndarray, measurement: float) -> Tuple[float, float]:
        """
        Single step Kalman Filter update.
        State: Belief in correctness (scalar for simplicity in this context).
        Observation: Logical consistency score.
        """
        # Initialize State
        mu = 0.5  # Prior belief (neutral)
        sigma = 1.0 # High uncertainty
        
        # Prediction Step (Process Model: Identity with noise)
        mu_pred = mu
        sigma_pred = sigma + self.process_noise
        
        # Update Step
        # Measurement Matrix H (mapping state to observation space)
        # Here we assume the latent sparse code similarity influences the measurement reliability
        similarity = np.dot(z_prompt, z_cand) / (np.linalg.norm(z_prompt) * np.linalg.norm(z_cand) + 1e-9)
        H = 0.5 + 0.5 * similarity # Reliability based on semantic overlap
        
        # Innovation
        y = measurement - mu_pred
        
        # Kalman Gain
        S = sigma_pred + self.measurement_noise / (H + 1e-9)
        K = sigma_pred / S
        
        # Update
        mu_new = mu_pred + K * y
        sigma_new = (1 - K) * sigma_pred
        
        return float(mu_new), float(sigma_new)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        z_prompt = self._encode_sparse(prompt)
        
        for cand in candidates:
            # 1. Sparse Coding of candidate
            z_cand = self._encode_sparse(cand)
            
            # 2. Logical Measurement (Observation)
            # Determines how well the candidate fits the logical constraints of the prompt
            measurement = self._logical_consistency_check(prompt, cand)
            
            # 3. Kalman Update (Belief Update)
            # We simulate a sequence: Prior -> Measure -> Posterior
            # To make it robust, we treat the 'measurement' as the observation at time t
            # and the sparse similarity as the context for the Kalman Gain.
            score, uncertainty = self._run_kalman_step(z_prompt, z_cand, measurement)
            
            # Final Score: Weighted by certainty (inverse uncertainty)
            # Higher score = higher mean belief and lower uncertainty
            confidence_factor = 1.0 / (uncertainty + 0.1)
            final_score = score * (0.5 + 0.5 * np.tanh(confidence_factor))
            
            # Reasoning string (Metacognitive signal)
            reasoning = f"Sparse features: {int(np.sum(z_cand > 0))}; Innovation: {abs(measurement - 0.5):.2f}; Uncertainty: {uncertainty:.2f}"
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the score to 0-1 range roughly
        score = res[0]['score']
        return max(0.0, min(1.0, score))