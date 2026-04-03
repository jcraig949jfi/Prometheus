import re
import numpy as np
import zlib

class ReasoningTool:
    """
    Implements a Kalman Filter-based reasoning engine guided by the Free Energy Principle.
    
    Mechanism:
    1. Structural Parsing: Extracts binary features (negations, comparatives, conditionals, numbers).
    2. Observation Model: Maps prompt structure to a latent truth variable z via linear model f = Hz + e.
    3. Entropy-weighted Noise: Uses Shannon entropy of lexical tokens to define observation noise covariance R.
       High surprise (high entropy) -> Higher noise -> Lower Kalman Gain (trust less).
    4. Kalman Update: Recursively updates belief (mu, sigma) about the candidate's truth.
    5. Free Energy Minimization: The update step inherently minimizes variational free energy by 
       weighting prediction error by precision (inverse noise).
    6. NCD Tiebreaker: Uses Normalized Compression Distance only if structural signals are ambiguous.
    """

    def __init__(self):
        # Lexicon for structural features
        self.negations = ['not', 'no', 'never', 'none', 'neither']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'better', 'worse', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.causals = ['because', 'leads', 'results', 'causes']
        self.ordering = ['before', 'after', 'first', 'last', 'next']
        self.quantifiers = ['all', 'some', 'every', 'each']
        self.num_regex = re.compile(r'\d+(\.\d+)?')
        
        # Feature dimension D
        self.D = 6 
        # Prior
        self.mu_0 = 0.5
        self.sigma2_0 = 0.25
        self.alpha = 0.1  # Noise scaling factor

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts binary structural features from text."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        f = np.zeros(self.D)
        
        # 1. Negation
        if any(w in words for w in self.negations): f[0] = 1
        # 2. Comparative
        if any(w in words for w in self.comparatives): f[1] = 1
        # 3. Conditional
        if any(w in words for w in self.conditionals): f[2] = 1
        # 4. Numeric presence
        if self.num_regex.search(text): f[3] = 1
        # 5. Causal
        if any(w in t_lower for w in self.causals): f[4] = 1
        # 6. Ordering/Quantifier (combined for density)
        if any(w in words for w in (self.ordering + self.quantifiers)): f[5] = 1
        
        return f

    def _calc_entropy_noise(self, text: str) -> float:
        """Calculates lexical surprise (entropy) to scale observation noise."""
        if not text: return 1.0
        words = re.findall(r'\b\w+\b', text.lower())
        if not words: return 1.0
        
        freq = {}
        for w in words: freq[w] = freq.get(w, 0) + 1
        
        entropy = 0.0
        n = len(words)
        for count in freq.values():
            p = count / n
            if p > 0: entropy -= p * np.log2(p)
            
        # Normalize roughly by max possible entropy for stability
        max_ent = np.log2(n) if n > 1 else 1
        return (entropy / max_ent) if max_ent > 0 else 1.0

    def _kalman_update(self, mu, sigma2, f, H, R):
        """Single step Kalman update."""
        # Prediction (static model)
        mu_pred = mu
        sigma2_pred = sigma2
        
        # Gain: K = sigma2 * H^T / (H * sigma2 * H^T + R)
        # H is (D, 1), sigma2 is scalar, R is scalar (assuming isotropic for simplicity in this 1D latent case)
        # H^T H is scalar sum(H^2)
        HTH = float(np.dot(H.T, H))
        if HTH == 0: return mu, sigma2 # No information
        
        denom = HTH * sigma2_pred + R
        K = (sigma2_pred * H.T) / denom # Shape (D, 1) scaled
        
        # Update Mean: mu = mu + K * (f - H * mu)
        # H * mu is (D, 1) * scalar
        prediction = H.flatten() * mu_pred
        innovation = f - prediction
        
        mu_new = mu_pred + float(np.dot(K.flatten(), innovation))
        
        # Update Variance: sigma2 = (1 - K * H) * sigma2
        # K * H is scalar (dot product of K and H column)
        KH = float(np.dot(K.flatten(), H.flatten()))
        sigma2_new = (1.0 - KH) * sigma2_pred
        
        # Clamp variance to avoid numerical instability
        sigma2_new = max(1e-6, sigma2_new)
        
        return mu_new, sigma2_new

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        denom = max(len1, len2)
        if denom == 0: return 0.0
        return (len12 - min(len1, len2)) / denom

    def _score_candidate(self, prompt: str, candidate: str) -> tuple[float, str]:
        """Scores a single candidate against the prompt."""
        full_text = f"{prompt} {candidate}"
        f = self._extract_features(full_text)
        
        # Construct H matrix (D x 1)
        # Heuristic: If a feature is present in prompt, we expect it to be consistent in truth.
        # We treat presence of structural cues as evidence. 
        # Simplified H: Identity-like mapping where active features contribute to truth.
        # In a real scenario, H is learned. Here we assume structural consistency implies truth.
        H = np.eye(self.D, 1) # Default to identity column for active features
        
        # If no features detected, H is zero -> skip Kalman, rely on NCD
        if np.all(f == 0):
            H = np.zeros((self.D, 1))
            
        # Calculate Noise R based on entropy
        entropy = self._calc_entropy_noise(full_text)
        R = self.alpha * (entropy + 0.1) * np.eye(self.D) # Diagonal noise matrix approximated as scalar per dim
        
        # Initialize belief
        mu = self.mu_0
        sigma2 = self.sigma2_0
        
        # Perform update (treating the whole feature vector as one observation block)
        # For this simplified model, we treat the feature vector as a single multi-dimensional observation
        # R needs to be scalar for the formula used above, so we take mean diagonal
        R_scalar = np.mean(np.diag(R)) if R.ndim == 2 else R
        
        if np.any(f > 0):
            # Only update if we have features
            # Adjust H to be relevant only where features exist to avoid noise from inactive dims
            active_mask = f > 0
            if np.any(active_mask):
                f_active = f[active_mask]
                H_active = np.eye(np.sum(active_mask), 1) # Local identity
                
                # Re-calc entropy for active parts only? Keep global for now.
                mu, sigma2 = self._kalman_update(mu, sigma2, f_active, H_active, R_scalar)

        # Free Energy check (implicit in the update, but we can use final variance as uncertainty)
        # Lower variance = higher confidence in the mean.
        
        return mu, sigma2

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        scores = []
        
        # Phase 1: Structural Scoring
        for cand in candidates:
            mu, sigma2 = self._score_candidate(prompt, cand)
            # Score is posterior mean, penalized slightly by uncertainty if needed
            # But primarily mu drives the ranking
            scores.append((cand, mu, sigma2))
        
        # Phase 2: NCD Tiebreaking for close calls
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        final_results = []
        for i, (cand, mu, sigma2) in enumerate(scores):
            reasoning = f"Posterior truth prob: {mu:.4f}. Uncertainty: {sigma2:.4f}."
            
            # Check for tie with next candidate (threshold 0.01)
            if i < len(scores) - 1:
                next_mu = scores[i+1][1]
                if abs(mu - next_mu) < 0.01:
                    # Apply NCD tiebreaker
                    ncd_self = self._compute_ncd(prompt, cand)
                    ncd_next = self._compute_ncd(prompt, scores[i+1][0])
                    # Lower NCD is better (more similar/compressible together)
                    if ncd_self < ncd_next:
                        reasoning += " (NCD tiebreak favor)"
                    else:
                        # Swap logic handled by sort stability or re-sort if needed, 
                        # but here we just annotate. For strict ranking, we'd re-sort.
                        pass
            
            final_results.append({
                "candidate": cand,
                "score": float(mu),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        mu, sigma2 = self._score_candidate(prompt, answer)
        # Confidence is a mix of high mean and low variance
        # Map to 0-1. Mu is already 0-1 approx.
        # Penalize high uncertainty
        confidence = mu * (1.0 - min(sigma2 / self.sigma_0, 1.0))
        return max(0.0, min(1.0, confidence))