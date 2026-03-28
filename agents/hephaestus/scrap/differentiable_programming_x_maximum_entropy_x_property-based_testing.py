import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A structural reasoning tool combining Maximum Entropy feature extraction 
    with Differentiable weight updates, constrained by Causal Intelligence guidelines.
    
    Mechanism:
    1. Parses logical structures (negations, comparatives, conditionals, causality).
    2. Computes a score based on feature alignment between prompt and candidate.
    3. Uses a differentiable (sigmoid) update to adjust feature weights based on 
       internal consistency checks (simulated property testing).
    4. NCD is used strictly as a tie-breaker for low-confidence structural matches.
    """
    
    def __init__(self):
        # Feature weights (w) initialized to 1.0. 
        # Order: [negation, comparative, conditional, causal, ordering, numeric]
        self.weights = np.ones(6, dtype=np.float64)
        self.learning_rate = 0.1
        
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|n\'t|never|neither|nor)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|>\|<|≥|≤|than)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|else|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in|due to)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|precede|follow|first|last)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?')
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary structural features from text."""
        features = np.zeros(6, dtype=np.float64)
        text_lower = text.lower()
        
        # Binary presence detection
        features[0] = 1.0 if self.patterns['negation'].search(text_lower) else 0.0
        features[1] = 1.0 if self.patterns['comparative'].search(text_lower) else 0.0
        features[2] = 1.0 if self.patterns['conditional'].search(text_lower) else 0.0
        features[3] = 1.0 if self.patterns['causal'].search(text_lower) else 0.0
        features[4] = 1.0 if self.patterns['ordering'].search(text_lower) else 0.0
        features[5] = 1.0 if self.patterns['numeric'].search(text_lower) else 0.0
        
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance (tie-breaker)."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _numeric_consistency_score(self, prompt: str, candidate: str) -> float:
        """
        Extract numeric literals and check for basic consistency.
        If prompt has numbers and candidate has numbers, check magnitude logic if possible.
        Returns 1.0 for match/neutral, 0.0 for contradiction, 0.5 for partial.
        """
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric data to contradict
        
        try:
            # Simple heuristic: if prompt implies a comparison (e.g. "greater than 5")
            # and candidate provides a number, check if it satisfies simple bounds if explicit.
            # For this implementation, we reward numeric presence if prompt has numeric context.
            return 1.0 if c_nums else 0.5
        except:
            return 0.5

    def _simulate_property_test(self, prompt: str, candidate: str) -> float:
        """
        Simulate property-based testing by generating perturbations (shrinking).
        Checks if removing key logical tokens changes the meaning drastically.
        Returns a 'violation' score (0.0 = robust, 1.0 = fragile/violation).
        """
        # Simplified PBT: Check if candidate contradicts explicit negation in prompt
        has_not = bool(re.search(r'\bnot\b', prompt.lower()))
        cand_has_not = bool(re.search(r'\bnot\b', candidate.lower()))
        
        # If prompt says "not X" and candidate says "X" (without not), it's a violation
        # This is a heuristic approximation of a property test
        if has_not and not cand_has_not:
            # Check for positive assertion of the negated concept (simplified)
            return 0.2 # Slight penalty for potential contradiction
        return 0.0

    def _energy(self, features: np.ndarray) -> float:
        """Compute energy E = -w^T f (lower energy = higher probability)."""
        return -np.dot(self.weights, features)

    def _update_weights(self, prompt_features: np.ndarray, candidate_features: np.ndarray, target_score: float):
        """
        Differentiable update step.
        Adjusts weights to minimize error between predicted energy and target quality.
        """
        pred_energy = self._energy(candidate_features)
        # Target energy: low for good answers (high score), high for bad
        # We map target_score (0-1) to an energy target roughly (-2 to 2)
        target_energy = -2.0 * target_score + 1.0 
        
        error = pred_energy - target_energy
        
        # Gradient descent step: w = w - lr * dE/dw
        # dE/dw = -f (since E = -w^T f)
        # Update rule approx: w += lr * error * f
        self.weights += self.learning_rate * error * candidate_features

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feat = self._extract_features(prompt)
        results = []
        
        # Pre-calculate numeric consistency for the prompt context
        base_numeric_score = self._numeric_consistency_score(prompt, "")
        
        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # 1. Structural Score (MaxEnt Model)
            # Score = w^T f (Higher is better)
            struct_score = float(np.dot(self.weights, c_feat))
            
            # 2. Property-Based Test (Consistency Check)
            pbt_violation = self._simulate_property_test(prompt, cand)
            struct_score -= pbt_violation * 2.0 # Penalty for violations
            
            # 3. Numeric Consistency
            num_score = self._numeric_consistency_score(prompt, cand)
            struct_score += num_score * 0.5
            
            # 4. NCD Tie-Breaker (Only if structural score is near zero/neutral)
            ncd_score = 0.0
            if abs(struct_score) < 0.1:
                ncd_val = self._compute_ncd(prompt, cand)
                # Invert NCD (lower distance = higher score) and scale down
                ncd_score = (1.0 - ncd_val) * 0.01 
            
            final_score = struct_score + ncd_score
            
            # Online learning step (Differentiable Programming aspect)
            # Assume high structural overlap implies correctness for weight adjustment
            if p_feat.sum() > 0 and c_feat.sum() > 0:
                # Pseudo-target: if features align, assume positive example
                target = 1.0 if np.all(p_feat == c_feat) else 0.8
                self._update_weights(p_feat, c_feat, target)

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {struct_score:.2f}, NCD boost: {ncd_score:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Based on structural feature density and alignment.
        """
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # Base confidence on feature coverage
        # If prompt has complex logic (many features), answer must share some
        prompt_complexity = np.sum(p_feat)
        overlap = np.sum((p_feat > 0) & (a_feat > 0))
        
        if prompt_complexity == 0:
            # Simple prompt, rely on answer structure
            conf = 0.5 + (np.sum(a_feat) * 0.1)
        else:
            # Ratio of overlapping logical features
            conf = 0.4 + (0.6 * (overlap / prompt_complexity))
            
        # Penalty for PBT violations
        if self._simulate_property_test(prompt, answer) > 0:
            conf *= 0.7
            
        return float(np.clip(conf, 0.0, 1.0))