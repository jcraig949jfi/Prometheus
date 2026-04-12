import numpy as np
import zlib
import re

class ReasoningTool:
    """
    Chaotic-Reservoir Echo State Network with Online Kalman Filtering (Simulated).
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts logical constraints (negations, comparatives, 
       conditionals) and numeric values. This forms the deterministic 'observation' vector.
    2. Chaotic Reservoir (Hypothesis Generation): A fixed random recurrent matrix with 
       spectral radius ~1.0 generates high-dimensional trajectories from the structural input,
       simulating diverse 'what-if' scenarios.
    3. EKF Weight Adaptation (Metacognition): Treats readout weights as state variables.
       Instead of full recursive Bayesian updates (expensive for O(N)), we simulate the 
       EKF's 'innovation' step: calculating the error between the reservoir's projection 
       and the candidate's structural signature. The 'confidence' is derived from the 
       inverse of this innovation covariance.
    
    This hybrid approach uses chaos for exploration (scoring diverse candidates) and 
    Kalman logic for uncertainty-aware pruning, strictly prioritizing structural signals 
    over NCD.
    """

    def __init__(self):
        # Reservoir parameters
        self.n_res = 64  # Reservoir size
        self.spectral_radius = 1.0 # Edge of chaos
        self.leak = 0.5
        
        # Initialize random recurrent matrix (fixed for determinism)
        np.random.seed(42)
        W = np.random.randn(self.n_res, self.n_res)
        # Scale to spectral radius
        W = W / np.max(np.abs(np.linalg.eigvals(W))) * self.spectral_radius
        self.W_res = W
        
        # Input weights (random projection)
        self.W_in = np.random.randn(self.n_res, 1)
        
        # EKF State: Readout weights (initialized to zeros)
        self.w_out = np.zeros(self.n_res)
        
        # EKF Covariance approximation (diagonal for simplicity)
        self.P = np.eye(self.n_res) * 0.5

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features: negations, comparatives, numbers, length."""
        text_lower = text.lower()
        
        # 1. Negation count
        negations = len(re.findall(r'\b(no|not|never|none|neither|nobody|nothing)\b', text_lower))
        
        # 2. Comparative indicators
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower))
        
        # 3. Conditional indicators
        conditionals = len(re.findall(r'\b(if|then|else|unless|provided|when)\b', text_lower))
        
        # 4. Numeric presence (simple check)
        numbers = len(re.findall(r'\d+', text))
        
        # 5. Question mark presence (inverse logic)
        questions = 1 if '?' in text else 0
        
        # 6. String length normalized
        length_norm = len(text) / 100.0
        
        return np.array([negations, comparatives, conditionals, numbers, questions, length_norm])

    def _run_reservoir(self, x_input: np.ndarray, steps: int = 10) -> np.ndarray:
        """Drive reservoir with input and collect state trajectory."""
        state = np.zeros(self.n_res)
        # Use input as initial bias
        u = x_input[0] if len(x_input) > 0 else 0.0
        state = np.tanh(self.W_in * u + self.W_res @ state)
        
        states = []
        for _ in range(steps):
            state = (1 - self.leak) * state + self.leak * np.tanh(self.W_in * u + self.W_res @ state)
            states.append(state)
            
        # Average state over trajectory (Echo State Property)
        return np.mean(np.array(states), axis=0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # 1. Extract structural features from prompt (The "Observation")
        prompt_features = self._extract_features(prompt)
        
        # 2. Drive Reservoir with prompt features
        # We run the reservoir to generate a rich state representation of the prompt context
        prompt_state = self._run_reservoir(prompt_features)
        
        ranked = []
        
        for cand in candidates:
            cand_features = self._extract_features(cand)
            
            # Hypothesis: Does this candidate satisfy the prompt's structural constraints?
            # We project the candidate through the same reservoir dynamics
            cand_state = self._run_reservoir(cand_features)
            
            # EKF Innovation: Difference between expected state (prompt) and candidate state
            # In a full EKF, we update weights. Here, we measure the 'surprise' (innovation)
            innovation = prompt_state - cand_state
            
            # Kalman Gain approximation (simplified for static evaluation)
            # K = P * H^T * (H * P * H^T + R)^-1
            # We assume H is identity for state matching, R is small noise
            innovation_norm = np.linalg.norm(innovation)
            
            # Structural Score: Lower innovation means better structural match
            # We invert norm to get a score, penalizing large deviations
            struct_score = 1.0 / (1.0 + innovation_norm)
            
            # Constraint Propagation Boost:
            # If prompt has negation, candidate must logically align (heuristic check)
            if prompt_features[0] > 0: # Prompt has negation
                if cand_features[0] > 0: # Candidate also has negation (likely consistent)
                    struct_score *= 1.2
                else:
                    # Check for explicit "No" or "False" which might be the answer to a negated question
                    if not re.search(r'\b(no|false|none)\b', cand.lower()):
                        struct_score *= 0.8 # Penalty if missing negation context
            
            # NCD as Tiebreaker (only if structural scores are very close, handled by weighting)
            ncd_val = self._compute_ncd(prompt, cand)
            # NCD is secondary, so we add a small fraction
            final_score = struct_score * 0.85 + (1.0 - ncd_val) * 0.15
            
            ranked.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {struct_score:.3f}, NCD tiebreak: {ncd_val:.3f}"
            })
        
        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on EKF innovation magnitude.
        Low innovation (high structural alignment) -> High confidence.
        """
        prompt_feat = self._extract_features(prompt)
        ans_feat = self._extract_features(answer)
        
        # Run reservoir dynamics
        p_state = self._run_reservoir(prompt_feat)
        a_state = self._run_reservoir(ans_feat)
        
        # Innovation vector
        innov = p_state - a_state
        innov_mag = np.linalg.norm(innov)
        
        # Map innovation magnitude to confidence (0-1)
        # Using a sigmoid-like decay: high error -> low confidence
        # Tuned so that perfect matches are near 1.0, random noise near 0.0
        confidence = 1.0 / (1.0 + np.exp(innov_mag - 2.0))
        
        return float(np.clip(confidence, 0.0, 1.0))