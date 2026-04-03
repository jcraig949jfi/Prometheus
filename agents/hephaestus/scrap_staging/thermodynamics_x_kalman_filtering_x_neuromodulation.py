import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Thermodynamics, and Neuromodulation.
    
    Mechanism:
    1. Structural Parsing: Extracts linguistic features (negations, causals, numbers) from candidates.
    2. Neuromodulatory Gain Control: Adjusts observation noise (R) based on linguistic certainty cues.
       - High certainty (causal claims) -> Low noise -> High Kalman Gain.
       - High uncertainty (negations, conditionals) -> High noise -> Low Kalman Gain.
    3. Thermodynamic Scoring: Treats 'score' as free energy minimization. 
       Score = Posterior Mean - (Temperature * Entropy/Variance).
       This penalizes high-uncertainty answers even if their mean estimate is high.
    4. Kalman Update: Iteratively refines the latent 'quality' state using parsed features as observations.
    5. NCD Tiebreaker: Uses compression distance only when structural scores are indistinguishable.
    """

    def __init__(self):
        # Base variance for observation noise
        self.r0 = 1.0
        # Process noise (tiny, for random walk)
        self.Q = 1e-4
        # Temperature parameter for thermodynamic scoring
        self.temperature = 0.5
        # Linguistic patterns
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r"n't", r'\bneither\b', r'\bnor\b'],
            'causal': [r'\bbecause\b', r'\btherefore\b', r'\bthus\b', r'\bhence\b', r'\bleads to\b', r'\bdue to\b'],
            'conditional': [r'\bif\b', r'\bunless\b', r'\bprovided\b', r'\bthen\b', r'\botherwise\b'],
            'comparative': [r'\bmore\b', r'\bless\b', r'\bthan\b', r'\bas\s+\w+\s+as\b', r'-er\b'],
            'numeric': [r'\d+[\.]?\d*', r'\bhalf\b', r'\bdouble\b'],
            'ordering': [r'\bfirst\b', r'\bsecond\b', r'\bbefore\b', r'\bafter\b', r'\bprevious\b', r'\bsubsequent\b']
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract normalized structural features [0, 1]."""
        text_lower = text.lower()
        features = []
        
        # Counts for each category
        counts = []
        for key, regex_list in self.patterns.items():
            count = 0
            for pattern in regex_list:
                count += len(re.findall(pattern, text_lower))
            counts.append(count)
        
        # Normalize counts to [0, 1] range roughly (assuming max count ~5 for short texts)
        total_counts = sum(counts) + 1e-6
        for c in counts:
            features.append(min(1.0, c / 5.0))
            
        return np.array(features)

    def _get_neuromodulatory_R(self, features: np.ndarray) -> np.diag:
        """
        Compute observation noise covariance R based on linguistic cues.
        Weights:
        - Negation (idx 0), Conditional (idx 2): Increase uncertainty (w > 0)
        - Causal (idx 1), Numeric (idx 4): Decrease uncertainty (w < 0)
        """
        # Weights aligned with feature order: neg, causal, cond, comp, num, ord
        weights = np.array([0.8, -0.6, 0.7, 0.2, -0.5, 0.1])
        
        # R = diag(r0 * (1 + w * f))
        # Ensure R stays positive
        r_diag = self.r0 * (1.0 + weights * features)
        r_diag = np.maximum(r_diag, 0.1) # Floor to avoid singularity
        return np.diag(r_diag)

    def _kalman_update(self, x_prev: float, P_prev: float, z: np.ndarray, R: np.ndarray) -> Tuple[float, float]:
        """Perform single-step Kalman update."""
        # State transition (identity)
        x_pred = x_prev
        P_pred = P_prev + self.Q
        
        # Observation model H (mapping scalar state to feature dimensions)
        H = np.ones((len(z), 1))
        
        # Kalman Gain
        # K = P * H^T * (H * P * H^T + R)^-1
        S = H @ (P_pred * H.T) + R  # Innovation covariance
        K = (P_pred * H.T) @ np.linalg.inv(S)
        
        # Update
        innovation = z - (H @ x_pred)
        x_post = x_pred + (K @ innovation)[0, 0]
        P_post = (1 - (K @ H)[0, 0]) * P_pred
        
        return x_post, max(P_post, 1e-6)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if c12 == 0: return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, float, str]:
        """Calculate thermodynamic score and confidence."""
        # Initial state (prior)
        x = 0.5  # Neutral prior
        P = 1.0  # High initial uncertainty
        
        # Extract features from candidate
        z = self._extract_features(candidate)
        
        # Neuromodulatory noise modulation
        R = self._get_neuromodulatory_R(z)
        
        # Kalman Update
        x_post, P_post = self._kalman_update(x, P, z, R)
        
        # Thermodynamic Scoring: Free Energy = Mean - T * Variance
        # We want high mean (quality) and low variance (certainty)
        # Score represents "useful work" extractable from the answer
        score = x_post - (self.temperature * P_post)
        
        # Reasoning string generation
        reasoning = f"Posterior Quality: {x_post:.3f}, Uncertainty: {P_post:.3f}. "
        if P_post < 0.2:
            reasoning += "High confidence due to strong causal/numeric signals."
        elif P_post > 0.8:
            reasoning += "Low confidence due to negations/conditionals increasing entropy."
        else:
            reasoning += "Moderate confidence."
            
        return score, 1.0 - min(P_post, 1.0), reasoning

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        scores = []
        
        # Primary scoring via Kalman-Thermo engine
        for cand in candidates:
            score, conf, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason,
                "_conf": conf # Internal use
            })
            scores.append(score)
        
        # Handle ties using NCD (Thermodynamic synergy: NCD as entropy check)
        # Only apply NCD if scores are very close (within 1% of max score)
        max_score = max(scores)
        threshold = max_score * 0.99
        
        tied_indices = [i for i, s in enumerate(scores) if s >= threshold]
        
        if len(tied_indices) > 1:
            # Break ties using NCD relative to prompt
            # Heuristic: Answers that compress well with prompt (high similarity) 
            # but aren't identical (trivial) might be better, 
            # BUT requirement says NCD is tiebreaker for "no structural signal".
            # Here we use NCD to penalize candidates that are just noise vs prompt structure.
            # Actually, standard NCD logic: Lower NCD = More Similar.
            # If the prompt asks a question, a good answer should be semantically linked.
            # We will slightly boost scores of candidates with optimal NCD (not too high, not too low)
            # Or simpler: Use NCD to break exact ties in score.
            
            current_best_score = -float('inf')
            best_candidates = []
            
            # Re-sort primarily by score, then by NCD logic
            # Since we need a list of dicts, let's just adjust the score slightly for tie-breaking
            epsilon = 1e-6
            for i in tied_indices:
                ncd_val = self._compute_ncd(prompt, candidates[i])
                # Prefer lower NCD (more related) but penalize exact duplicates if any
                # Add tiny perturbation based on NCD
                results[i]["score"] += (1.0 - ncd_val) * epsilon

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Clean up internal keys
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r["candidate"],
                "score": r["score"],
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        _, conf, _ = self._score_candidate(prompt, answer)
        return float(np.clip(conf, 0.0, 1.0))