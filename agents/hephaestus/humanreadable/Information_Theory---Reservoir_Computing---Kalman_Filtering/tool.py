import numpy as np
import math

class ReasoningTool:
    """
    Information-Theoretic Reservoir Kalman Filter (IT-RKF) Approximation.
    
    Mechanism:
    1. Reservoir Computing: Inputs (prompt + candidate) are hashed into a fixed,
       high-dimensional nonlinear state vector using deterministic trigonometric mappings.
       This mimics the Echo State Network's rich temporal features without training.
    2. Kalman Filtering: We treat the 'correctness' of a candidate as a latent state.
       The filter updates this state based on 'observations' derived from semantic 
       overlap (Jaccard similarity) between the prompt and candidate.
    3. Information Theory: The readout weight is updated to maximize Mutual Information.
       In this static approximation, this equates to weighting the candidate score 
       by the inverse of the estimated uncertainty (Kalman gain), effectively selecting
       the hypothesis that reduces entropy the most relative to the prompt context.
    """

    def __init__(self):
        self.dim = 64  # Reservoir dimension
        self.process_noise = 1e-4
        self.measurement_noise = 0.1
        # Deterministic seed for reproducibility
        self.rng = np.random.RandomState(42)
        
        # Initialize fixed reservoir weights (Echo State Property approximation)
        # Fixed random projection matrix
        self.W_in = self.rng.randn(self.dim, 1) 
        self.W_in = self.W_in / (np.linalg.norm(self.W_in) + 1e-8)

    def _hash_text(self, text: str) -> float:
        """Deterministic hash of text to a float in [0, 1]."""
        if not text: return 0.0
        h = 0
        for c in text:
            h = (h * 31 + ord(c)) % (2**32)
        return h / (2**32)

    def _generate_reservoir_state(self, prompt: str, candidate: str) -> np.ndarray:
        """
        Generates a high-dimensional state vector r_t.
        Combines prompt and candidate hashes into a nonlinear trajectory.
        """
        combined = f"{prompt}::{candidate}"
        base_hash = self._hash_text(combined)
        prompt_hash = self._hash_text(prompt)
        
        # Nonlinear transformation (sinusoidal embedding)
        t = np.linspace(0, 2 * math.pi, self.dim)
        phase = base_hash * 100
        state = np.sin(t + phase) * np.cos(prompt_hash * 50)
        
        # Add input projection
        state += (self.W_in.flatten() * base_hash)
        return state

    def _jaccard_similarity(self, s1: str, s2: str) -> float:
        """Simple token-based similarity as the observation model."""
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())
        if not set1 and not set2: return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _run_kalman_step(self, z_obs: float, r_state: np.ndarray, 
                         x_prev: float, P_prev: float) -> tuple:
        """
        Performs one step of Kalman filtering.
        State: Scalar correctness probability.
        Observation: Similarity-derived heuristic.
        """
        # Prediction step (Identity model for static candidate evaluation)
        x_pred = x_prev
        P_pred = P_prev + self.process_noise
        
        # Update step
        # Observation model C: Map reservoir state to observation space via simple projection
        # Approximating C * r_t as a scalar relevance score
        C_val = np.mean(r_state) 
        H = C_val if abs(C_val) > 1e-6 else 1.0
        
        # Innovation
        y = z_obs - (H * x_pred)
        S = H * H * P_pred + self.measurement_noise
        K = (P_pred * H) / (S + 1e-8) # Kalman Gain
        
        x_upd = x_pred + K * y
        P_upd = (1 - K * H) * P_pred
        
        return max(0.0, min(1.0, x_upd)), max(1e-6, P_upd)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        # Global prior for the session
        x_prior = 0.5 
        P_prior = 0.25 
        
        for cand in candidates:
            # 1. Reservoir State Generation
            r_t = self._generate_reservoir_state(prompt, cand)
            
            # 2. Observation Model (Heuristic similarity as 'y_t')
            # We assume higher similarity to prompt implies higher likelihood of being 
            # the intended answer in a reasoning context, serving as the measurement.
            z_t = 0.5 + 0.5 * self._jaccard_similarity(prompt, cand)
            
            # 3. Kalman Update (Information-Theoretic Readout)
            # The 'Infomax' aspect is approximated by the Kalman Gain minimizing 
            # the posterior uncertainty (variance), thus maximizing information gain.
            x_post, P_post = self._run_kalman_step(z_t, r_t, x_prior, P_prior)
            
            # Score is the estimated state (mean of the posterior)
            score = float(x_post)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"IT-RKF estimate: prior={x_prior:.3f}, obs={z_t:.3f}, gain={P_prior/(P_prior+self.measurement_noise):.3f}"
            })
            
            # Reset prior for next independent candidate evaluation 
            # (or could carry over if evaluating a sequence)
            x_prior = 0.5 
            P_prior = 0.25

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence score 0-1."""
        # Reuse evaluation logic for consistency
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]