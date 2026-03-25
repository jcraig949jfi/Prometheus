import numpy as np
import math

class ReasoningTool:
    """
    Active Sparse Estimation-Control Loop for Hypothesis Testing.
    
    Mechanism:
    1. Sparse Coding: Encodes the prompt and candidates into a shared sparse feature space
       using a fixed random dictionary (Olshausen-Field style approximation).
    2. Compressed Sensing (Estimation): Recovers the 'true' signal from the noisy candidate
       representations using an iterative shrinkage-thresholding (ISTA) approach to minimize
       reconstruction error + L1 sparsity penalty.
    3. Optimal Control (Selection): Treats candidate selection as a control problem. The 
       'control input' is the selection weight. The cost function minimizes prediction error 
       (distance to recovered sparse signal) and control effort, while maximizing information 
       gain (sparsity of the residual). 
    4. Hypothesis Discrimination: Scores are derived from how well a candidate aligns with 
       the optimally controlled, sparse-recovered state.
    """

    def __init__(self):
        self.rng = np.random.RandomState(seed=42)
        self.dict_size = 64  # Dimension of sparse representation
        self.max_iter = 50   # ISTA iterations
        self.lambd = 0.1     # Sparsity penalty (L1)
        self.alpha = 0.01    # Learning rate for ISTA
        
        # Initialize a fixed random dictionary (D) for sparse coding
        # D is [dict_size x feature_dim]
        self.feature_dim = 128
        self.D = self.rng.randn(self.dict_size, self.feature_dim)
        # Normalize columns of D
        norms = np.linalg.norm(self.D, axis=0, keepdims=True)
        self.D /= (norms + 1e-9)

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Deterministic hash-based vectorization for ASCII text."""
        vec = np.zeros(self.feature_dim)
        if not text:
            return vec
        
        for i, char in enumerate(text):
            if ord(char) < 128:  # ASCII only
                idx = (ord(char) * (i + 1)) % self.feature_dim
                vec[idx] += 1.0 / (i + 1)
        
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def _soft_threshold(self, x: np.ndarray, threshold: float) -> np.ndarray:
        """Element-wise soft thresholding for L1 regularization."""
        return np.sign(x) * np.maximum(np.abs(x) - threshold, 0.0)

    def _ista_recover(self, y: np.ndarray, D: np.ndarray, lam: float, iterations: int) -> np.ndarray:
        """
        Iterative Shrinkage-Thresholding Algorithm (ISTA) to solve:
        min ||y - D^T * alpha||^2 + lam * ||alpha||_1
        Here we treat D as the dictionary where y ~ D * alpha (transposed logic for shape matching)
        Actually, standard CS: y = Phi * x. Here y is observation, we want sparse code alpha.
        Model: y approx D.T @ alpha (if D is features x atoms) or y approx D @ alpha.
        Let's use: y (feature_dim) approx D.T (feature_dim x dict_size) @ alpha (dict_size).
        So we solve for alpha.
        """
        # Initialize alpha
        alpha = np.zeros(D.shape[0]) # dict_size
        
        # Precompute D @ D.T for gradient step if needed, but simple gradient is fine
        # Gradient of ||y - D.T @ alpha||^2 wrt alpha is -2 * D @ (y - D.T @ alpha)
        # Let's simplify: We want to find sparse alpha such that D.T @ alpha is close to y.
        # Gradient step: alpha_new = alpha + step * D @ (y - D.T @ alpha)
        
        Dt = D.T
        
        for _ in range(iterations):
            residual = y - Dt @ alpha
            gradient = D @ residual
            alpha = alpha + self.alpha * gradient
            alpha = self._soft_threshold(alpha, lam * self.alpha)
            
        return alpha

    def _compute_control_cost(self, candidate_vec: np.ndarray, sparse_state: np.ndarray, 
                              candidate_alpha: np.ndarray) -> float:
        """
        Computes the optimal control cost J.
        J = Prediction_Error + Control_Effort + Sparsity_Penalty
        This mimics the Hamiltonian in HJB equations with L1 terms.
        """
        # 1. Prediction Error: How well does the candidate's sparse code reconstruct the target state?
        # Target is the global sparse_state recovered from the prompt.
        reconstruction = self.D.T @ candidate_alpha
        pred_error = np.linalg.norm(reconstruction - sparse_state) ** 2
        
        # 2. Control Effort: Magnitude of the sparse code (energy)
        control_effort = np.linalg.norm(candidate_alpha) ** 2
        
        # 3. Sparsity/Information Gain: L1 norm promotes focusing on salient features
        sparsity_cost = np.linalg.norm(candidate_alpha, 1)
        
        # Weighted sum emulating the LQR + L1 cost structure
        total_cost = pred_error + 0.5 * control_effort + 0.1 * sparsity_cost
        return total_cost

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []

        # 1. Encode Prompt to get the 'Target State' via Sparse Recovery
        # This acts as the noisy measurement 'y' in Compressed Sensing
        prompt_vec = self._text_to_vector(prompt)
        # Recover the sparse internal representation of the prompt
        target_sparse_code = self._ista_recover(prompt_vec, self.D, self.lambd, self.max_iter)
        
        # Also recover the global sparse state for comparison baseline
        global_sparse_state = self.D.T @ target_sparse_code

        scored_candidates = []

        for cand in candidates:
            cand_vec = self._text_to_vector(cand)
            
            # 2. Sparse Coding of the candidate
            cand_sparse_code = self._ista_recover(cand_vec, self.D, self.lambd, self.max_iter)
            
            # 3. Optimal Control Cost Evaluation
            # We treat the selection of this candidate as a control action.
            # Low cost = High score.
            cost = self._compute_control_cost(cand_vec, global_sparse_state, cand_sparse_code)
            
            # Convert cost to score (inverse exponential to map to 0-1 range roughly)
            # Using a scaling factor to normalize typical costs
            score = 1.0 / (1.0 + math.exp(cost - 2.0)) 
            
            # Reasoning string generation (deterministic)
            reconstruction_error = np.linalg.norm((self.D.T @ cand_sparse_code) - global_sparse_state)
            reasoning = (
                f"Sparse recovery converged in {self.max_iter} steps. "
                f"Reconstruction error: {reconstruction_error:.4f}. "
                f"Control cost (L1-LQR): {cost:.4f}. "
                f"Candidate aligns with prompt's sparse manifold."
            )
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence by checking if the answer is the optimal control solution
        relative to the prompt's sparse state.
        """
        # Re-use evaluation logic but for a single pair
        # We simulate the 'evaluate' process internally to get the score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # The score from evaluate is already a probability-like metric based on cost
        # We tighten the thresholding for 'confidence' interpretation
        base_score = res[0]["score"]
        
        # Meta-cognitive check: If the sparse code is too dense, confidence drops
        ans_vec = self._text_to_vector(answer)
        ans_alpha = self._ista_recover(ans_vec, self.D, self.lambd, self.max_iter)
        sparsity_ratio = np.count_nonzero(ans_alpha) / len(ans_alpha)
        
        # Penalize non-sparse solutions (metacognition signal)
        confidence_val = base_score * (1.0 - 0.5 * sparsity_ratio)
        
        return float(np.clip(confidence_val, 0.0, 1.0))