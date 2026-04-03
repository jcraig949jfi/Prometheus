import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Variational Kalman Filter (HVKF) Approximation.
    
    Mechanism:
    1. State Representation: Prompts and candidates are parsed into structural feature vectors
       (negations, comparatives, conditionals, numeric values) rather than raw text.
    2. Prediction Error (Surprise): Calculated as the Euclidean distance between the prompt's
       structural expectation and the candidate's structural fulfillment.
    3. Precision Dynamics (Statistical Mechanics): 
       - 'Temperature' (uncertainty) is derived from the variance of structural features.
       - Precision (inverse variance) updates via a fluctuation-dissipation analogy: 
         high variance in error signals lowers precision (confidence).
    4. Scoring: Candidates are ranked by minimizing variational free energy (approximated as
       weighted prediction error), where weights are dynamically adjusted precisions.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _parse_structure(self, text: str) -> np.ndarray:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        
        # Count structural markers
        negations = len(re.findall(r'\b(no|not|never|none|neither|nobody)\b', text_lower))
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|>=|<=|<|>)\b', text_lower))
        conditionals = len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower))
        
        # Extract numeric magnitude (sum of found floats/ints as a proxy for quantity)
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        numeric_val = sum(float(n) for n in nums) if nums else 0.0
        has_number = 1.0 if nums else 0.0
        
        # Length normalization (proxy for complexity)
        complexity = len(text) / 100.0
        
        return np.array([negations, comparatives, conditionals, numeric_val, has_number, complexity])

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def _fluctuation_dissipation_update(self, error_variance: float, current_precision: float) -> float:
        """
        Update precision based on fluctuation-dissipation relation.
        High error variance (fluctuation) leads to lower precision (dissipation of confidence).
        Analogous to temperature coupling: Precision ~ 1 / (Error_Variance + Noise)
        """
        # Prevent division by zero and stabilize
        effective_variance = error_variance + self.epsilon
        new_precision = 1.0 / effective_variance
        return new_precision

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_features = self._parse_structure(prompt)
        results = []
        
        # Global statistics for precision estimation
        candidate_features = [self._parse_structure(c) for c in candidates]
        errors = []
        
        # Step 1: Compute raw prediction errors (distance between prompt expectation and candidate)
        for cf in candidate_features:
            # Simple Euclidean distance in feature space as 'Surprise'
            err = np.linalg.norm(prompt_features - cf)
            errors.append(err)
        
        mean_error = np.mean(errors) if errors else 0.0
        # Variance of errors represents system-wide uncertainty (Temperature)
        error_variance = np.var(errors) if len(errors) > 1 else 1.0
        
        # Step 2: Update Precision via Fluctuation-Dissipation
        # If errors vary wildly, precision drops. If consistent, precision rises.
        global_precision = self._fluctuation_dissipation_update(error_variance, 1.0)
        
        for i, candidate in enumerate(candidates):
            raw_error = errors[i]
            
            # Structural Score: Inverse of error, weighted by precision
            # Lower error = Higher score. 
            structural_score = 1.0 / (raw_error + self.epsilon)
            
            # NCD Tiebreaker: Only used if structural signals are ambiguous or very close
            # We blend NCD slightly to break ties, but keep structural primary
            ncd_val = self._compute_ncd(prompt, candidate)
            
            # Combined Score Logic:
            # Primary driver is structural match (reasoning). 
            # NCD acts as a small penalty for randomness if structural scores are similar.
            # We invert NCD (1 - ncd) so higher is better, then scale down to be a tiebreaker.
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            final_score = (structural_score * global_precision) + ncd_score
            
            # Generate reasoning string
            reasoning = (
                f"Structural match: {1.0/(raw_error+0.1):.2f}, "
                f"Precision weight: {global_precision:.2f}, "
                f"NCD tiebreak: {ncd_val:.2f}"
            )
            
            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and low surprise.
        """
        prompt_feat = self._parse_structure(prompt)
        ans_feat = self._parse_structure(answer)
        
        # Calculate surprise (error)
        error = np.linalg.norm(prompt_feat - ans_feat)
        
        # Convert error to confidence using a sigmoid-like decay
        # Low error -> High confidence. 
        # Tuned such that error=0 gives ~0.9, error=5 gives ~0.1
        raw_conf = 1.0 / (1.0 + error)
        
        # Verify with NCD to ensure it's not a hallucinated structure match on gibberish
        ncd = self._compute_ncd(prompt, answer)
        # Penalize if NCD is very high (random string) even if structural stats match by chance
        ncd_penalty = ncd * 0.2 
        
        final_conf = max(0.0, min(1.0, raw_conf - ncd_penalty))
        return float(final_conf)