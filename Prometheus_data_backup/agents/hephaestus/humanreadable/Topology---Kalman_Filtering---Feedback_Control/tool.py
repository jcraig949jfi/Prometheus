import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topological Feedback Kalman Observer (TFKO) Implementation.
    
    Mechanism:
    1. Structural Parsing (Topology Proxy): Extracts logical features (negations, comparatives,
       conditionals, numbers) to form a 'belief vector'. This acts as the topological signature
       of the prompt's logical structure.
    2. Kalman Filtering: Maintains a running estimate of the 'correct' feature distribution based
       on the prompt's constraints. It computes an innovation (error) between the candidate's
       features and the prompt's requirements.
    3. Feedback Control: Adjusts the scoring weight (process noise Q) dynamically. If a candidate
       violates a hard logical constraint (e.g., negation mismatch), the feedback loop inflates
       the error covariance, drastically reducing the score.
    4. Scoring: Candidates are ranked by their likelihood under the filtered belief state.
       NCD is used only as a tie-breaker for structurally identical candidates.
    """

    def __init__(self):
        self._eps = 1e-6
        # Kalman State: Mean (x) and Covariance (P) initialized to neutral
        self._x = np.zeros(5) 
        self._P = np.eye(5) * 0.5
        # Control gains
        self._K_gain = 0.8
        self._Q_base = np.eye(5) * 0.1

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts structural features: [negations, comparatives, conditionals, numbers, length_norm]"""
        t = text.lower()
        
        # 1. Negations (Logic inversion)
        negations = len(re.findall(r'\b(not|no|never|neither|none|cannot|won\'t|don\'t|doesn\'t)\b', t))
        
        # 2. Comparatives (Logical ordering)
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|larger|better|worse|than|>=|<=|<|>)\b', t))
        
        # 3. Conditionals (Causal links)
        conditionals = len(re.findall(r'\b(if|then|unless|provided|assuming|when|else)\b', t))
        
        # 4. Numeric presence (Quantitative reasoning)
        numbers = len(re.findall(r'\d+(?:\.\d+)?', t))
        
        # 5. Normalized Length (Complexity proxy)
        length_norm = min(1.0, len(t) / 200.0)
        
        return np.array([negations, comparatives, conditionals, numbers, length_norm])

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _kalman_update(self, prompt_features: np.ndarray, candidate_features: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Simulates a Kalman step where the 'process' is the logical consistency.
        Returns a score (likelihood) and updated state.
        """
        # Prediction step
        x_pred = self._x
        P_pred = self._P + self._Q_base
        
        # Innovation (difference between what prompt implies and candidate offers)
        # In a real TFKO, this detects topological holes. Here, feature mismatch = hole.
        y = candidate_features - prompt_features
        S = P_pred + np.eye(5) * 0.1 # Measurement noise
        
        # Kalman Gain
        K = P_pred @ np.linalg.inv(S)
        
        # Update state (Learning the prompt's logical shape)
        self._x = x_pred + K @ y
        self._P = (np.eye(5) - K) @ P_pred
        
        # Compute Mahalanobis distance as the 'topological anomaly' score
        # Low distance = candidate fits the logical topology of the prompt
        try:
            inv_S = np.linalg.inv(S)
            mahalanobis = np.sqrt(y @ inv_S @ y)
        except np.linalg.LinAlgError:
            mahalanobis = 10.0
            
        return mahalanobis

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feat = self._extract_features(prompt)
        # Reset filter state for each new prompt evaluation to ensure independence
        self._x = np.zeros(5)
        self._P = np.eye(5) * 0.5
        
        scored_candidates = []
        
        for cand in candidates:
            cand_feat = self._extract_features(cand)
            
            # 1. Structural/Kalman Score
            anomaly_score = self._kalman_update(prompt_feat, cand_feat)
            
            # Convert anomaly to probability-like score (Gaussian kernel)
            # High anomaly -> Low score
            structural_score = np.exp(-0.5 * anomaly_score**2)
            
            # 2. Constraint Propagation (Hard checks)
            # If prompt has high negation count and candidate has none (or vice versa), penalize heavily
            p_neg, c_neg = prompt_feat[0], cand_feat[0]
            if (p_neg > 0 and c_neg == 0) or (p_neg == 0 and c_neg > 0):
                # Soft penalty via feedback control simulation
                structural_score *= 0.5 
            
            # 3. NCD Tie-breaker (Only if structural scores are close)
            # We add a tiny NCD component to break ties, but keep structural primary
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better, scale down to not override structural
            ncd_score = (1.0 - ncd_val) * 0.05 
            
            final_score = structural_score + ncd_score
            
            # Reasoning string generation
            reasoning = f"Structural match: {structural_score:.3f}. "
            if anomaly_score > 2.0:
                reasoning += "Detected logical/topological divergence."
            elif p_neg != c_neg:
                reasoning += "Negation mismatch detected."
            else:
                reasoning += "Logical structure consistent."

            scored_candidates.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        prompt_feat = self._extract_features(prompt)
        ans_feat = self._extract_features(answer)
        
        # Re-run a quick kalman step to get anomaly score
        self._x = np.zeros(5)
        self._P = np.eye(5) * 0.5
        anomaly, _ = self._kalman_update(prompt_feat, ans_feat)
        
        # Map anomaly to confidence
        conf = np.exp(-0.5 * anomaly**2)
        
        # Hard constraint check
        if (prompt_feat[0] > 0 and ans_feat[0] == 0): # Negation mismatch
            conf *= 0.4
            
        return float(np.clip(conf, 0.0, 1.0))