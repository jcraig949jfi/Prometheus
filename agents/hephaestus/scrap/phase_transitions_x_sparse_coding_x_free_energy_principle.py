import numpy as np
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    A reasoning evaluator combining Sparse Coding, Free Energy Principle, and Phase Transitions.
    
    Mechanism:
    1. Structural Parsing: Extracts binary linguistic features (negations, comparatives, conditionals,
       causality, quantifiers, temporality) from prompts and candidates into feature vectors.
    2. Sparse Coding: Approximates a dictionary learning step where the 'ideal' answer matches the 
       prompt's structural signature. We enforce sparsity (L1) on the difference between candidate 
       and prompt features.
    3. Free Energy: Computes F = 0.5 * error^T * Precision * error + Lambda * sparsity.
       This balances fidelity to the prompt (prediction error) with model complexity (sparsity).
    4. Phase Transition: Uses a critical precision threshold (alpha_c) to switch between high-entropy
       (lenient) and low-entropy (strict) scoring regimes, filtering out noisy candidates.
    5. Scoring: Returns negative Free Energy as the score. NCD is used only as a tiebreaker.
    """
    
    def __init__(self):
        self.lambda_sparsity = 0.5
        self.alpha_base = 1.0
        self.delta_threshold = 0.1
        
        # Feature patterns for structural parsing
        self.patterns = [
            (r'\b(not|no|never|neither)\b', 'negation'),
            (r'\b(greater|less|more|fewer|higher|lower|before|after)\b', 'comparative'),
            (r'\b(if|then|unless|provided|when)\b', 'conditional'),
            (r'\b(cause|lead|result|effect|because|therefore)\b', 'causal'),
            (r'\b(all|some|every|none|any|most)\b', 'quantifier'),
            (r'\d+(\.\d+)?', 'numeric'), # Detects presence of numbers
            (r'\b(must|should|could|may)\b', 'modality')
        ]
        self.feature_names = [p[1] for p in self.patterns]
        self.K = len(self.feature_names)

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary structural features from text."""
        if not text:
            return np.zeros(self.K)
        
        text_lower = text.lower()
        features = []
        for pattern, _ in self.patterns:
            if re.search(pattern, text_lower):
                features.append(1.0)
            else:
                features.append(0.0)
        return np.array(features)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            import zlib
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 0.5

    def _compute_free_energy(self, f_candidate: np.ndarray, f_prompt: np.ndarray, alpha: float) -> float:
        """
        Compute Variational Free Energy.
        F = 0.5 * (f_c - f_p)^T * Pi * (f_c - f_p) + lambda * ||z||_1
        Where z is the sparse code approximating the difference.
        """
        epsilon = f_candidate - f_prompt
        
        # Precision weighted error (Pi = alpha * I)
        # Since Pi is diagonal, epsilon^T Pi epsilon = alpha * sum(epsilon^2)
        prediction_error_term = 0.5 * alpha * np.dot(epsilon, epsilon)
        
        # Sparsity penalty (L1 norm of the error vector as a proxy for sparse code z)
        # In this simplified model, the 'code' required to explain the deviation is the deviation itself
        sparsity_term = self.lambda_sparsity * np.sum(np.abs(epsilon))
        
        return prediction_error_term + sparsity_term

    def _get_critical_alpha(self, candidates_features: List[np.ndarray], prompt_features: np.ndarray) -> float:
        """
        Estimate critical precision alpha_c for phase transition.
        alpha_c = 2 * lambda / E[|epsilon|]
        """
        errors = []
        for f_c in candidates_features:
            eps = f_c - prompt_features
            errors.extend(np.abs(eps))
        
        if not errors:
            return self.alpha_base
            
        avg_error = np.mean(errors)
        if avg_error < 1e-9:
            return self.alpha_base * 10 # High precision if errors are negligible
            
        return (2.0 * self.lambda_sparsity) / avg_error

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        prompt_features = self._extract_features(prompt)
        cand_features = [self._extract_features(c) for c in candidates]
        
        # Phase Transition: Determine regime via critical alpha
        alpha_c = self._get_critical_alpha(cand_features, prompt_features)
        # Use a precision slightly above critical to ensure we are in the low-entropy (selective) regime
        alpha = alpha_c * 1.2 
        
        results = []
        min_energy = float('inf')
        
        # Calculate Free Energy for each candidate
        energies = []
        for i, f_c in enumerate(cand_features):
            energy = self._compute_free_energy(f_c, prompt_features, alpha)
            energies.append(energy)
            if energy < min_energy:
                min_energy = energy
        
        # Thresholding based on phase transition logic
        threshold = min_energy + self.delta_threshold
        
        scored_candidates = []
        for i, candidate in enumerate(candidates):
            energy = energies[i]
            
            # Base score is negative free energy
            score = -energy
            
            # Phase transition filter: if energy is too high (above threshold), penalize heavily
            # unless it's the best we have (to avoid empty results)
            if energy > threshold:
                # Apply a steep penalty but keep relative ordering for tie-breaking
                score -= 10.0 
            
            # Tie-breaking with NCD if scores are very close
            # We add a tiny fraction of NCD distance to break ties deterministically
            ncd_val = self._compute_ncd(prompt, candidate)
            final_score = score - (ncd_val * 1e-6)
            
            reasoning = f"Structural match (energy={energy:.4f}, alpha={alpha:.2f}). "
            if energy > threshold:
                reasoning += "High entropy regime (low confidence)."
            else:
                reasoning += "Low entropy regime (high confidence)."
                
            scored_candidates.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1 based on free energy relative to a baseline.
        0 = high energy (wrong), 1 = low energy (correct).
        """
        prompt_features = self._extract_features(prompt)
        answer_features = self._extract_features(answer)
        
        # Use a standard high precision for confidence check
        alpha = self.alpha_base * 2.0
        energy = self._compute_free_energy(answer_features, prompt_features, alpha)
        
        # Map energy to [0, 1]. 
        # Max theoretical energy for binary features of size K is approx 0.5*alpha*K + lambda*K
        max_energy = 0.5 * alpha * self.K + self.lambda_sparsity * self.K
        if max_energy == 0:
            return 1.0
            
        # Normalize: 0 energy -> 1.0, max energy -> 0.0
        conf = 1.0 - (energy / max_energy)
        return max(0.0, min(1.0, conf))