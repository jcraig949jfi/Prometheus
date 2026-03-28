import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dual-Timescale Bayesian Policy Learner for Reasoning Evaluation.
    
    Mechanism:
    1. Structural Parsing (Fast Timescale): Extracts logical features (negations, 
       comparatives, conditionals) and numeric values from prompts/candidates.
       These act as noisy observations of truth.
    2. Kalman Filtering (Belief Update): Maintains a Gaussian belief over the 
       correctness of each candidate. The 'observation' is the structural match 
       between prompt constraints and candidate content. The Kalman Gain adjusts 
       belief based on uncertainty.
    3. Epigenetic Consolidation (Slow Timescale): Tracks the accumulation of 
       squared updates (surprise). If a logical feature consistently supports 
       a hypothesis, its variance is reduced (methylation), making the belief 
       robust to future noise. If contradiction persists, variance remains high.
    
    This implements the RL x Epigenetics x Kalman triple by treating the 
    evaluation of text as a sequential decision process where logical consistency 
    drives belief convergence.
    """

    def __init__(self):
        # State: Belief parameters (mu, sigma) and Epigenetic traces
        self._reset_state()

    def _reset_state(self):
        """Reset internal Bayesian state for a new evaluation context."""
        self.mu = 0.5       # Prior belief in correctness (uniform)
        self.sigma = 0.25   # Prior uncertainty (variance)
        self.epigenetic_trace = 0.0 # Accumulated surprise/stability
        self.consolidated = False   # Has the hypothesis stabilized?
        
        # Dynamics model noise (process noise)
        self.Q = 0.01 
        # Observation noise (measurement noise)
        self.R = 0.1 

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural and numeric features from text."""
        text_lower = text.lower()
        features = {
            'negation': 0.0,
            'comparative': 0.0,
            'conditional': 0.0,
            'numeric_val': 0.0,
            'length_norm': min(len(text) / 100.0, 1.0)
        }
        
        # Structural Parsing
        negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        if any(n in text_lower for n in negations):
            features['negation'] = 1.0
            
        comparatives = ['>', '<', 'greater', 'less', 'more', 'fewer', 'better', 'worse']
        if any(c in text_lower for c in comparatives):
            features['comparative'] = 1.0
            
        conditionals = ['if', 'then', 'unless', 'provided', 'condition']
        if any(c in text_lower for c in conditionals):
            features['conditional'] = 1.0
            
        # Numeric Evaluation
        numbers = re.findall(r"-?\d+\.?\d*", text)
        if numbers:
            try:
                # Take the first valid number found as the primary signal
                features['numeric_val'] = float(numbers[0])
            except ValueError:
                pass
                
        return features

    def _compute_observation(self, prompt: str, candidate: str) -> float:
        """
        Compute a pseudo-observation (y_k) based on structural alignment.
        Returns a value between 0 and 1 representing 'likelihood of correctness'.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.5 # Base prior
        
        # Logic Rule 1: Negation Consistency
        # If prompt has negation, candidate should ideally reflect it or answer appropriately
        if p_feat['negation'] > 0:
            if c_feat['negation'] > 0 or 'no' in candidate.lower() or 'false' in candidate.lower():
                score += 0.3
            elif 'yes' in candidate.lower() or 'true' in candidate.lower():
                score -= 0.3 # Potential contradiction
                
        # Logic Rule 2: Numeric Consistency
        if p_feat['numeric_val'] > 0 and c_feat['numeric_val'] > 0:
            # Simple heuristic: if numbers are close, higher score
            diff = abs(p_feat['numeric_val'] - c_feat['numeric_val'])
            if diff == 0:
                score += 0.4
            elif diff < 1.0:
                score += 0.2
                
        # Logic Rule 3: Structural Complexity Match
        # If prompt is conditional, simple yes/no might be insufficient (penalize slightly)
        if p_feat['conditional'] > 0 and c_feat['conditional'] == 0:
            if len(candidate.split()) < 5:
                score -= 0.1
                
        # Logic Rule 4: Direct keyword matching for basic validation
        cand_lower = candidate.lower()
        if any(k in cand_lower for k in ['correct', 'true', 'yes', 'accurate']):
            score += 0.1
        if any(k in cand_lower for k in ['wrong', 'false', 'incorrect', 'impossible']):
            score -= 0.1
            
        return max(0.0, min(1.0, score))

    def _kalman_update(self, y_obs: float):
        """Perform Kalman Filter update step on the belief state."""
        # Prediction Step
        mu_pred = self.mu
        sigma_pred = self.sigma + self.Q
        
        # Update Step
        # Kalman Gain: K = sigma_pred / (sigma_pred + R)
        K = sigma_pred / (sigma_pred + self.R)
        
        # Innovation (Surprise)
        innovation = y_obs - mu_pred
        
        # Update Belief
        self.mu = mu_pred + K * innovation
        self.sigma = (1 - K) * sigma_pred
        
        # Ensure bounds
        self.mu = max(0.0, min(1.0, self.mu))
        self.sigma = max(1e-6, self.sigma)
        
        return innovation, K

    def _epigenetic_consolidation(self, innovation: float, K: float):
        """
        Apply epigenetic-like consolidation.
        Accumulate squared updates. If stable, reduce variance permanently.
        """
        # Accumulate surprise (squared innovation weighted by gain)
        delta_e = (innovation * K) ** 2
        self.epigenetic_trace += delta_e
        
        # Threshold for methylation (consolidation)
        threshold = 0.05
        
        if not self.consolidated and self.epigenetic_trace > threshold:
            # Methylation: Reduce variance significantly, locking the belief
            self.sigma *= 0.1 
            self.consolidated = True
        elif self.consolidated:
            # If already consolidated, slow decay of trace to allow eventual unlearning if needed
            self.epigenetic_trace *= 0.99

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for candidate in candidates:
            # Reset state for each candidate evaluation to treat them independently
            # In a real agent, this might be sequential, but for ranking, we reset.
            self._reset_state()
            
            # Compute observation based on structural parsing
            y_obs = self._compute_observation(prompt, candidate)
            
            # Kalman Update
            innovation, K = self._kalman_update(y_obs)
            
            # Epigenetic Consolidation
            self._epigenetic_consolidation(innovation, K)
            
            # Final score is the posterior mean (mu)
            # Add small noise based on remaining uncertainty to break ties deterministically
            score = self.mu + (self.sigma * 0.01) 
            
            results.append({
                "candidate": candidate,
                "score": float(score),
                "reasoning": f"Structural match: {y_obs:.2f}, Uncertainty: {self.sigma:.4f}, Consolidated: {self.consolidated}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the posterior belief."""
        self._reset_state()
        y_obs = self._compute_observation(prompt, answer)
        innovation, K = self._kalman_update(y_obs)
        self._epigenetic_consolidation(innovation, K)
        
        # Confidence is inversely related to uncertainty (sigma) and directly to belief (mu)
        # High mu and low sigma = high confidence
        confidence = self.mu * (1.0 - self.sigma)
        return float(max(0.0, min(1.0, confidence)))

# Example usage logic (not executed here but demonstrates interface compliance):
# tool = ReasoningTool()
# res = tool.evaluate("Is 5 greater than 3?", ["Yes", "No"])
# conf = tool.confidence("Is 5 greater than 3?", "Yes")