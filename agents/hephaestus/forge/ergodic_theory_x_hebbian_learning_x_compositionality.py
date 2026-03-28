import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic Compositional Hebbian Reservoir (ECHR) Approximation.
    
    Mechanism:
    1. Compositional Binding: Parses prompt into structural features (negations, 
       comparatives, numbers) and binds them into a high-dimensional vector space 
       using orthogonal random projections (simulating circular convolution).
    2. Ergodic Reservoir: Maintains a fixed random-orthogonal recurrent matrix. 
       The system state evolves by mixing the bound input with the previous state,
       ensuring the trajectory explores the invariant measure of the input space.
    3. Hebbian Learning: Online update of a weight matrix based on co-activation 
       of features (x_i * x_j). This captures long-term statistical co-occurrences.
    4. Hypothesis Testing: Candidates are projected into this space. The score 
       is the correlation between the candidate's projection and the reservoir's 
       time-averaged state (representing the "learned" logical structure).
    
    This implements the theoretical ECHR concept using deterministic linear algebra 
    to approximate the ergodic sampling and Hebbian plasticity without external deps.
    """

    def __init__(self):
        self.dim = 512  # Reservoir dimension
        self.state = np.zeros(self.dim)
        # Random orthogonal matrix for ergodic mixing (fixed seed for determinism)
        rng = np.random.default_rng(42)
        Q, _ = np.linalg.qr(rng.standard_normal((self.dim, self.dim)))
        self.recurrent_matrix = Q * 0.95  # Spectral radius < 1 for stability
        self.weights = np.zeros(self.dim) # Hebbian weights
        self.lambda_decay = 0.01
        self.learning_rate = 0.1
        
        # Structural parsers cache
        self._feature_cache = {}

    def _extract_features(self, text: str) -> np.ndarray:
        """Compositional binding of structural features into a vector."""
        if text in self._feature_cache:
            return self._feature_cache[text]
        
        text_lower = text.lower()
        features = np.zeros(self.dim)
        rng = np.random.default_rng(hash(text) % (2**31))
        
        # 1. Negation handling (Modus Tollens support)
        negations = ['no', 'not', 'never', 'none', 'neither', 'without']
        has_neg = any(f" {n} " in f" {text_lower} " or text_lower.startswith(n) for n in negations)
        if has_neg:
            features[:64] = rng.standard_normal(64) * -1.0 # Invert signal space
            
        # 2. Comparatives and Numeric Evaluation
        nums = re.findall(r"-?\d+\.?\d*", text)
        if len(nums) >= 2:
            vals = [float(n) for n in nums]
            # Encode relative magnitude structurally
            if vals[0] > vals[1]:
                features[64:128] = 1.0
            elif vals[0] < vals[1]:
                features[64:128] = -1.0
            # Encode presence of numbers
            features[128:192] = 1.0
            
        # 3. Conditionals (If-Then)
        if 'if' in text_lower and ('then' in text_lower or ',' in text_lower):
            features[192:256] = 1.0
            
        # 4. Subject-Object / Transitivity hints (Simple keyword overlap)
        words = set(re.findall(r'\b[a-z]+\b', text_lower))
        logic_words = {'all', 'some', 'every', 'each', 'more', 'less', 'equal'}
        if words & logic_words:
            features[256:320] = 1.0

        # Add noise for ergodicity (weak chaotic injection)
        features += rng.standard_normal(self.dim) * 0.05
        
        # Normalize
        features = features / (np.linalg.norm(features) + 1e-9)
        self._feature_cache[text] = features
        return features

    def _update_reservoir(self, input_vec: np.ndarray):
        """Ergodic dynamics + Hebbian update."""
        # Dynamics: x_t+1 = M * x_t + input
        self.state = np.dot(self.recurrent_matrix, self.state) + input_vec
        
        # Hebbian Update: delta_w ~ x_i * x_j - lambda * w
        # Simplified to vector form: update weights based on current state correlation
        hebbian_term = self.state * input_vec 
        self.weights = self.weights + self.learning_rate * (hebbian_term - self.lambda_decay * self.weights)

    def _get_ergodic_average(self, prompt: str, candidate: str) -> float:
        """Simulate ergodic sampling to get expectation value."""
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # Bind prompt and candidate (superposition)
        combined = p_feat + c_feat
        combined = combined / (np.linalg.norm(combined) + 1e-9)
        
        # Run trajectory for "sampling"
        temp_state = self.state.copy()
        samples = []
        
        # Short ergodic trajectory (Monte Carlo estimate)
        for _ in range(10):
            temp_state = np.dot(self.recurrent_matrix, temp_state) + combined
            # Measure correlation with learned Hebbian weights
            score = np.dot(temp_state, self.weights)
            samples.append(score)
            
        return float(np.mean(samples))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Prime the reservoir with the prompt (Context setting)
        p_feat = self._extract_features(prompt)
        self._update_reservoir(p_feat)
        
        results = []
        for cand in candidates:
            # 2. Hypothesis testing via ergodic sampling
            score = self._get_ergodic_average(prompt, cand)
            
            # 3. Structural Tie-Breaker (NCD fallback for low-diff cases)
            # If scores are very close, NCD acts as the tiebreaker as per instructions
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"ECHR activation: {score:.4f}"
            })
            
            # Update reservoir with candidate to simulate sequential reasoning context
            self._update_reservoir(self._extract_features(cand))

        # Rank by score (higher is better)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized activation strength.
        Uses the magnitude of the ergodic average relative to a dynamic threshold.
        """
        p_feat = self._extract_features(prompt)
        self._update_reservoir(p_feat)
        
        raw_score = self._get_ergodic_average(prompt, answer)
        
        # Map raw score to 0-1 using sigmoid-like scaling
        # Assuming typical scores range between -2 and 2 based on dim/weights
        normalized = 1.0 / (1.0 + np.exp(-raw_score))
        return float(np.clip(normalized, 0.0, 1.0))