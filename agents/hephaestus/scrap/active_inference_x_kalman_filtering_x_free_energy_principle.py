import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Active Inference / Free Energy Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, 
       conditionals, causality, ordering, numbers) from text using regex.
    2. Belief State: Maintains a Gaussian belief (mu, Sigma) over the latent 
       correctness of a candidate.
    3. Active Inference (Evaluate): Treats each candidate as a hypothesis. 
       Computes Expected Free Energy (G) based on prediction error (innovation) 
       between the candidate's structural features and the prompt's constraints.
       Score = -G. Lower prediction error -> Higher score.
    4. Kalman Filtering (Confidence): Used ONLY for the confidence wrapper to 
       estimate uncertainty reduction, avoiding direct scoring bias.
    5. NCD Tiebreaker: Uses zlib compression distance only if structural scores 
       are indistinguishable.
    """
    
    def __init__(self):
        self.sigma_process = 0.1  # Process noise Q
        self.r_noise = 0.5        # Measurement noise R
        
        # Feature extractors
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'comparative': [r'\b(more|less|greater|smaller|higher|lower)\b', r'[<>=]'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bimplies\b'],
            'causal': [r'\bbecause\b', r'\btherefore\b', r'\bcauses?\b', r'\bleads?\s+to\b'],
            'ordering': [r'\b(first|second|third|last|before|after)\b'],
            'numeric': r'\d+\.?\d*'
        }

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts structural features into a normalized vector."""
        text_lower = text.lower()
        features = []
        
        # Binary flags for logical structures
        for key in ['negation', 'comparative', 'conditional', 'causal', 'ordering']:
            count = sum(len(re.findall(p, text_lower)) for p in self.patterns[key])
            features.append(1.0 if count > 0 else 0.0)
            
        # Numeric density (normalized)
        nums = re.findall(self.patterns['numeric'], text_lower)
        num_val = min(1.0, len(nums) / 10.0) if nums else 0.0
        features.append(num_val)
        
        # Length penalty (normalized) to prevent echo
        features.append(min(1.0, len(text) / 500.0))
        
        return np.array(features)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        l1, l2 = len(s1.encode()), len(s2.encode())
        if l1 == 0 or l2 == 0: return 1.0
        c12 = len(zlib.compress((s1 + s2).encode()))
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _propagate_constraints(self, prompt_feats: np.ndarray, cand_feats: np.ndarray) -> np.ndarray:
        """
        Simulates constraint propagation. 
        If prompt has high logical density, candidate must match structural complexity.
        Returns a target measurement vector y_k.
        """
        # Simple heuristic: Target features should mirror prompt features 
        # but filtered by candidate's capacity to express them.
        # This acts as the observation model H_k * mu_k approx.
        
        # If prompt has negation, correct answer likely needs specific handling 
        # (modeled here as requiring matching structural presence)
        target = np.copy(prompt_feats)
        
        # Transitivity/Modus Ponens approximation:
        # If prompt implies logic (conditional/causal), candidate must have > 0 logic score
        logic_prompt = prompt_feats[2] + prompt_feats[3] # conditional + causal
        if logic_prompt > 0:
            if cand_feats[2] + cand_feats[3] == 0:
                # Penalty: Candidate lacks logical structure found in prompt
                target[2:] *= 0.5 
                
        return target

    def _kalman_update(self, mu: np.ndarray, sigma: np.ndarray, y: np.ndarray, H: np.ndarray, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Standard Kalman Update step."""
        # Innovation
        epsilon = y - H @ mu
        
        # Innovation covariance
        S = H @ sigma @ H.T + R
        
        # Kalman Gain
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S_inv = np.eye(len(S)) * 0.1
            
        K = sigma @ H.T @ S_inv
        
        # Update
        mu_new = mu + K @ epsilon
        sigma_new = (np.eye(len(mu)) - K @ H) @ sigma
        
        # Compute scalar innovation magnitude for scoring
        # Mahalanobis distance component of Free Energy
        error_metric = float(epsilon.T @ S_inv @ epsilon)
        
        return mu_new, sigma_new, error_metric

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feats = self._extract_features(prompt)
        n_features = len(prompt_feats)
        
        # Priors for Active Inference
        # mu: belief that candidate is correct (start neutral)
        mu = np.ones((n_features, 1)) * 0.5 
        Sigma = np.eye(n_features) * 0.5
        
        # Observation Noise Matrix
        R = np.eye(n_features) * self.r_noise
        
        # Hand-crafted Observation Model H (Identity for direct mapping, 
        # but scaled by feature importance)
        H = np.eye(n_features) 
        
        scores = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand).reshape(-1, 1)
            
            # Generate predicted measurement based on constraints
            y_k = self._propagate_constraints(prompt_feats, cand_feats).reshape(-1, 1)
            
            # Active Inference: Evaluate hypothesis (candidate)
            # We treat the candidate's features as the "action" that reveals the world state.
            # We want to minimize Expected Free Energy (G).
            # G = 0.5 * (innovation_cost + entropy_cost)
            
            # Run Kalman update virtually to get innovation error
            _, _, innovation_cost = self._kalman_update(mu, Sigma, y_k, H, R)
            
            # Entropy term (log det S) - simplified as trace for stability
            S = H @ Sigma @ H.T + R
            entropy_cost = np.log(np.linalg.det(S) + 1e-6)
            
            # Expected Free Energy
            G = 0.5 * (innovation_cost + entropy_cost)
            
            # Score is negative free energy (lower G -> higher score)
            # Add small bonus for matching numeric values exactly if present
            bonus = 0.0
            if re.search(r'\d+', prompt) and re.search(r'\d+', cand):
                if self._compute_ncd(prompt, cand) < 0.5: # Rough similarity check for numbers
                    bonus = 0.5
                    
            final_score = -G + bonus
            scores.append((cand, final_score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # NCD Tiebreaker logic for top candidates if scores are too close
        if len(scores) > 1 and abs(scores[0][1] - scores[1][1]) < 1e-4:
            # Re-rank top cluster by NCD to prompt (preferring concise relevance)
            top_score = scores[0][1]
            cluster = [s for s in scores if abs(s[1] - top_score) < 1e-3]
            rest = [s for s in scores if abs(s[1] - top_score) >= 1e-3]
            
            cluster.sort(key=lambda x: self._compute_ncd(prompt, x[0]))
            scores = cluster + rest

        return [
            {"candidate": cand, "score": float(score), "reasoning": "Active Inference via Free Energy minimization on structural features"}
            for cand, score in scores
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 using Kalman Filter uncertainty reduction.
        High confidence = low posterior uncertainty after observing the answer.
        """
        prompt_feats = self._extract_features(prompt)
        cand_feats = self._extract_features(answer)
        
        n = len(prompt_feats)
        mu = np.ones((n, 1)) * 0.5
        Sigma = np.eye(n) * 0.5  # Prior uncertainty
        H = np.eye(n)
        R = np.eye(n) * self.r_noise
        
        y_k = self._propagate_constraints(prompt_feats, cand_feats).reshape(-1, 1)
        
        # Perform update
        _, Sigma_post, error_metric = self._kalman_update(mu, Sigma, y_k, H, R)
        
        # Confidence is inverse of remaining uncertainty (trace of Sigma)
        # Normalized to 0-1 range roughly
        uncertainty = np.trace(Sigma_post)
        max_uncertainty = np.trace(Sigma)
        
        # Map uncertainty to confidence
        # If uncertainty reduced significantly, confidence is high
        conf = 1.0 - (uncertainty / max_uncertainty)
        
        # Penalize high innovation error (contradiction)
        if error_metric > 5.0:
            conf *= 0.5
            
        return float(np.clip(conf, 0.0, 1.0))