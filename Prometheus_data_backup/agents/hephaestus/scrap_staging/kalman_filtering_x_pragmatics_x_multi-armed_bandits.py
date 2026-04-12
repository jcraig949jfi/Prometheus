import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Kalman Filtering, Pragmatics (Gricean maxims), 
    and Multi-Armed Bandits (UCB) to score candidate answers.
    
    Mechanism:
    1. Structural Parsing: Extracts binary/scalar features (negations, numerics, etc.) 
       from text using regex.
    2. Kalman Filter: Maintains a belief (mean, variance) over the "truth state" of each candidate.
       - Observation model maps features to the truth state.
       - Pragmatics modulates observation noise (R): violations increase noise.
    3. Multi-Armed Bandit (UCB): Dynamically weights feature reliability. Features that 
       consistently reduce uncertainty or align with high-confidence updates get higher weights.
    4. Scoring: Final posterior mean is the score. NCD is used only as a tiebreaker.
    """

    # Feature patterns (ASCII safe)
    PATTERNS = {
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bnone\b'],
        'comparative': [r'\bgreater than\b', r'\bless than\b', r'\bmore.*than\b', r'\bfewer.*than\b'],
        'conditional': [r'\bif\b', r'\bunless\b', r'\bthen\b'],
        'causal': [r'\bbecause\b', r'\bleads to\b', r'\bresults in\b', r'\bcauses\b'],
        'ordering': [r'\bfirst\b', r'\bsecond\b', r'\bbefore\b', r'\bafter\b'],
        'quantifier': [r'\ball\b', r'\bsome\b', r'\bmost\b', r'\bnone\b'],
        'modal': [r'\bmust\b', r'\bmight\b', r'\bshould\b', r'\bcould\b'],
        'speech_act': [r'\bi claim\b', r'\bit is suggested\b', r'\bwe propose\b']
    }
    
    # Numeric pattern
    NUM_PATTERN = re.compile(r'-?\d+(?:\.\d+)?(?:\s*(?:%|percent))?')

    def __init__(self):
        self.feature_names = list(self.PATTERNS.keys()) + ['numeric_count', 'numeric_value']
        self.d = len(self.feature_names)
        # Bandit state: counts and sum of rewards for each feature arm
        self.arm_counts = np.ones(self.d)  # Prior count = 1
        self.arm_rewards = np.zeros(self.d) 
        self.t_total = 1  # Time step counter for UCB

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features into a vector z."""
        text_lower = text.lower()
        features = []
        
        # Regex-based binary features
        for key in self.PATTERNS.keys():
            pattern = '|'.join(self.PATTERNS[key])
            # Simple presence check
            match = 1.0 if re.search(pattern, text_lower) else 0.0
            features.append(match)
            
        # Numeric features
        nums = self.NUM_PATTERN.findall(text_lower)
        features.append(min(1.0, len(nums) / 5.0))  # Normalized count
        
        # Extract single numeric value if present (heuristic for magnitude)
        if nums:
            try:
                val = float(nums[0].replace('%', '').replace('percent', ''))
                # Normalize loosely assuming range 0-100 for typical QA
                features.append(min(1.0, abs(val) / 100.0)) 
            except ValueError:
                features.append(0.0)
        else:
            features.append(0.0)
            
        return np.array(features)

    def _check_pragmatics(self, text: str) -> float:
        """
        Estimate pragmatic quality (0.0 to 1.0). 
        Lower score = higher noise (R).
        Checks for Gricean violations: excessive length (Quantity), repetition (Manner).
        """
        words = text.split()
        length = len(words)
        
        # Penalty for extreme brevity or excessive verbosity
        if length < 3:
            quality = 0.5
        elif length > 200:
            quality = 0.6
        else:
            quality = 1.0
            
        # Penalty for repetition (Manner)
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:
                quality *= 0.7
                
        return quality

    def _compute_ucb_weights(self) -> np.ndarray:
        """Compute UCB weights for features to adjust H matrix."""
        weights = np.zeros(self.d)
        for i in range(self.d):
            if self.arm_counts[i] == 0:
                ucb = float('inf')
            else:
                avg_reward = self.arm_rewards[i] / self.arm_counts[i]
                exploration = math.sqrt(math.log(self.t_total + 1) / self.arm_counts[i])
                ucb = avg_reward + 0.5 * exploration # alpha = 0.5
            weights[i] = ucb
        
        # Normalize weights to [0.5, 1.5] range to scale H
        if np.max(weights) > np.min(weights):
            norm_weights = 0.5 + (weights - np.min(weights)) / (np.max(weights) - np.min(weights))
        else:
            norm_weights = np.ones(self.d)
        return norm_weights

    def _kalman_update(self, mu: float, sigma: float, z: np.ndarray, H_base: np.ndarray, R_base: float, ucb_weights: np.ndarray) -> Tuple[float, float]:
        """Perform single-step Kalman update."""
        # Adjust H by UCB weights (exploit reliable features)
        H_adj = H_base * ucb_weights
        
        # Predict (static state)
        mu_pred = mu
        sigma_pred = sigma
        
        # Observation model: z = H_adj * x + v
        # Innovation: y = z - H_adj * mu
        # We treat z as a scalar observation aggregated from features? 
        # No, the prompt says z is a vector. H is d x 1.
        # So z (d x 1) = H (d x 1) * x (1 x 1).
        
        # Compute Kalman Gain
        # S = H^T * Sigma * H + R (Scalar since state is 1D)
        # But R is a matrix? Prompt says "R_t" and "diagonal entry".
        # Let's assume R is diagonal matrix with base variance scaled by pragmatics.
        R_mat = np.eye(self.d) * R_base / (ucb_weights + 1e-6) # Inverse weight scaling? 
        # Actually, prompt says: violations increase R. UCB boosts weight -> reduces effective noise.
        # Let's make R diagonal where R_ii = base / weight_i
        
        # Simplified 1D State Kalman with Vector Observation
        # K = Sigma * H^T * (H * Sigma * H^T + R)^-1
        # Since Sigma is scalar (variance), let's denote it as P.
        # K is (1 x d)
        
        P = sigma_pred
        H_col = H_adj.reshape(-1, 1) # d x 1
        
        # S = H^T P H + R (d x d matrix)
        S = np.dot(H_col, H_col.T) * P + np.diag(R_base / (ucb_weights + 0.1))
        
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S_inv = np.linalg.pinv(S)
            
        K = P * np.dot(H_col.T, S_inv) # 1 x d
        
        # Innovation y = z - H * mu
        y = z - np.dot(H_col, mu_pred) # d x 1
        
        # Update
        mu_new = mu_pred + np.dot(K, y)[0]
        # P_new = (I - K H) P
        # K (1xd), H (dx1) -> scalar
        KH = np.dot(K, H_col)[0,0]
        sigma_new = (1.0 - KH) * P
        
        return max(0.0, min(1.0, mu_new)), max(1e-6, sigma_new)

    def _score_candidate(self, candidate: str, prompt: str = "") -> Tuple[float, str]:
        """Score a single candidate using the Kalman-Bandit loop."""
        # Initial belief: uniform prior [0, 1] -> mu=0.5, sigma=0.25
        mu = 0.5
        sigma = 0.25
        
        # Base observation noise
        base_R = 1.0
        
        # Extract features from candidate
        z = self._extract_features(candidate)
        
        # Pragmatics factor (affects R)
        prag_quality = self._check_pragmatics(candidate)
        if prag_quality < 1.0:
            base_R *= (2.0 - prag_quality) # Increase noise for poor pragmatics
            
        # H matrix: Mapping scalar truth to features. 
        # Heuristic: Assume presence of feature (1) suggests truth (1) for most logical markers.
        # For negation, it's complex, but we'll treat raw presence as a signal for now.
        H_base = np.ones(self.d) 
        
        # Get UCB weights (Bandit layer)
        ucb_weights = self._compute_ucb_weights()
        
        # Perform Kalman Update
        mu_new, sigma_new = self._kalman_update(mu, sigma, z, H_base, base_R, ucb_weights)
        
        # Update Bandit State (Reward = reduction in uncertainty or alignment)
        # Reward heuristic: If feature was present and contributed to a confident shift, reward it.
        # Simplified: Reward features that are active (z_i > 0) and have high UCB weight
        for i in range(self.d):
            if z[i] > 0:
                self.arm_counts[i] += 1
                # Pseudo-reward: alignment with current mean belief
                reward = mu_new if mu_new > 0.5 else (1-mu_new)
                self.arm_rewards[i] += reward
                
        self.t_total += 1
        
        reason_str = f"Kalman-Bandit update: mu={mu_new:.3f}, sigma={sigma_new:.4f}, prag={prag_quality:.2f}"
        return mu_new, reason_str

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        def compress_len(s):
            return len(zlib.compress(s.encode('utf-8')))
        
        try:
            c1 = compress_len(s1)
            c2 = compress_len(s2)
            c12 = compress_len(s1 + s2)
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        scores = []
        
        # Primary scoring via Kalman-Bandit
        for cand in candidates:
            score, reason = self._score_candidate(cand, prompt)
            scores.append(score)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Tie-breaking with NCD if scores are too close
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                if abs(scores[i] - scores[j]) < 1e-4:
                    # Use NCD against prompt as tiebreaker (lower NCD = more similar/relevant)
                    ncd_i = self._ncd_similarity(prompt, candidates[i])
                    ncd_j = self._ncd_similarity(prompt, candidates[j])
                    # Adjust score slightly based on NCD (lower is better)
                    if ncd_i < ncd_j:
                        scores[i] += 1e-5
                    else:
                        scores[j] += 1e-5

        # Sort descending by score
        sorted_indices = np.argsort([-s for s in scores])
        final_results = [results[i] for i in sorted_indices]
        
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score, _ = self._score_candidate(answer, prompt)
        return float(score)

# Import zlib inside function to keep global scope clean if needed, 
# but here we import at top of block for clarity if allowed, 
# or locally inside the method used above.
import zlib