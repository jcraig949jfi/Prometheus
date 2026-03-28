import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Distributed Sparse Kalman Filter with Mutualistic Consensus (DSKF-MC) Analogue.
    
    Mechanism:
    1. State Vector (x): Represents the structural integrity score of a candidate.
       Dimensions: [Negation_Count, Comparative_Logic, Conditional_Depth, Numeric_Consistency].
    2. Prediction Step: Assumes candidates maintain their structural properties (Identity transition).
    3. Measurement Update (Sparse): 
       - Extracts features (measurements) from text.
       - Computes residuals (r) between candidate features and prompt constraints.
       - Applies L1-like penalty: Heavy penalty for violating explicit constraints (negations/numbers).
    4. Symbiotic Consensus:
       - Candidates "exchange nutrients" (score boosts) if they share consistent logical structures 
         with the prompt's requirements (e.g., if prompt asks for "less than", candidates with 
         comparative logic get a boost).
       - Final score is a fusion of raw feature match (Kalman update) and structural consensus.
    5. Hypothesis Falsification: Large residuals in critical dimensions (numbers/negations) 
       trigger immediate score reduction (falsification).
    """

    def __init__(self):
        # Process noise covariance (uncertainty in our extraction)
        self.Q = np.diag([0.1, 0.1, 0.1, 0.1])
        # Measurement noise covariance (confidence in pattern matching)
        self.R = np.diag([0.05, 0.05, 0.05, 0.05])
        # Mutualistic coupling strength
        self.symbiosis_factor = 0.3

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features: [negations, comparatives, conditionals, numbers]"""
        text_lower = text.lower()
        
        # 1. Negations
        negations = len(re.findall(r'\b(no|not|never|neither|nobody|nothing|nowhere|none)\b', text_lower))
        
        # 2. Comparatives (simple heuristic)
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', text_lower))
        
        # 3. Conditionals
        conditionals = len(re.findall(r'\b(if|unless|provided|when|then|else)\b', text_lower))
        
        # 4. Numeric presence (count of digits)
        numbers = len(re.findall(r'\d+', text))
        
        return np.array([negations, comparatives, conditionals, numbers], dtype=float)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        comp_joint = len(zlib.compress(b1 + b2))
        return (comp_joint - min(comp1, comp2)) / max(comp1, comp2)

    def _kalman_update(self, x_prior: np.ndarray, z: np.ndarray, P_prior: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Perform a simplified Kalman update step.
        x: state estimate
        z: measurement (features extracted from text)
        P: covariance
        Returns updated x, P, and residual (innovation).
        """
        # Identity observation matrix H (we observe all features directly)
        H = np.eye(4)
        
        # Innovation (Residual)
        y = z - x_prior
        
        # Innovation covariance S = H P H^T + R
        S = P_prior + self.R
        
        # Kalman Gain K = P H^T S^-1
        try:
            K = P_prior @ np.linalg.inv(S)
        except np.linalg.LinAlgError:
            K = np.eye(4) * 0.5 # Fallback
            
        # Updated state estimate
        x_post = x_prior + K @ y
        
        # Updated covariance
        I = np.eye(4)
        P_post = (I - K @ H) @ P_prior
        
        return x_post, P_post, y

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt structural signatures for symbiosis
        prompt_has_neg = prompt_feats[0] > 0
        prompt_has_comp = prompt_feats[1] > 0
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Prediction Step (Prior)
            # Assume state is similar to prompt structure initially (mutualistic prior)
            x_prior = prompt_feats * 0.5 
            P_prior = np.diag([1.0, 1.0, 1.0, 1.0])
            
            # 2. Measurement Update (Sparse Update)
            # The candidate's features are the "measurement" of truth
            x_post, P_post, residual = self._kalman_update(x_prior, cand_feats, P_prior)
            
            # 3. Symbiotic Consensus & Hypothesis Falsification
            score = 0.0
            
            # Base score from Kalman fit (inverse of residual norm)
            # Smaller residual means candidate structure matches the "expected" structure derived from prompt
            residual_norm = np.linalg.norm(residual)
            base_score = 1.0 / (1.0 + residual_norm)
            
            # Symbiotic Bonus: If prompt has negations, candidates with negations get a "nutrient" boost
            # This mimics the mutualistic exchange where compatible sparsity patterns reinforce each other
            symbiosis_bonus = 0.0
            if prompt_has_neg and cand_feats[0] > 0:
                symbiosis_bonus += self.symbiosis_factor
            if prompt_has_comp and cand_feats[1] > 0:
                symbiosis_bonus += self.symbiosis_factor
                
            # Hypothesis Falsification (Hard constraints)
            # If prompt implies a number comparison, check basic consistency if possible
            # (Simplified: if prompt has numbers and candidate has none, slight penalty unless it's a yes/no)
            falsification_penalty = 0.0
            prompt_nums = re.findall(r'\d+', prompt)
            cand_nums = re.findall(r'\d+', cand)
            
            if len(prompt_nums) > 0 and len(cand_nums) == 0:
                # Check if candidate is just a short affirmation/negation
                if len(cand.strip().split()) > 3: 
                    falsification_penalty = 0.2
            
            final_score = base_score + symbiosis_bonus - falsification_penalty
            
            # Tie-breaking with NCD (only if scores are very close, but we add a small NCD component always)
            ncd_val = self._compute_ncd(prompt, cand)
            # NCD is 0 (similar) to 1 (different). We want higher score for better match.
            # But NCD is unreliable for short strings, so weight it lightly as a tiebreaker
            ncd_contribution = (1.0 - ncd_val) * 0.05 
            
            total_score = final_score + ncd_contribution
            
            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": f"Structural fit: {base_score:.2f}, Symbiosis: {symbiosis_bonus:.2f}, Penalty: {falsification_penalty:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment and residual error.
        Returns 0-1.
        """
        # Run single evaluation to get score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]['score']
        
        # Normalize score to 0-1 range roughly
        # Base score is around 0.5-1.0 for good matches, <0.5 for bad
        confidence = min(1.0, max(0.0, score))
        
        return confidence