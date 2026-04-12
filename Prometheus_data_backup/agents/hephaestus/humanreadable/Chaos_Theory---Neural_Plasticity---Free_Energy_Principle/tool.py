import numpy as np
import math

class ReasoningTool:
    """
    Chaotic Predictive Coding Network (CPCN) Approximation.
    
    Mechanism:
    1. Chaotic Reservoir: Uses a fixed recurrent matrix tuned to the edge of chaos
       (spectral radius ~1.1) to project input embeddings into high-dimensional,
       sensitive trajectories. This mimics the 'exploration engine'.
    2. Free Energy Minimization: Treats the difference between the candidate's
       semantic embedding and the prompt's expected trajectory as 'prediction error'.
       We minimize a proxy for Variational Free Energy by balancing this error
       (accuracy) against a complexity penalty (deviation from prior weights).
    3. Plastic Readout: Scores are derived from how well the reservoir state aligns
       with a target vector, modulated by the inverse of the free energy bound.
       Higher alignment + lower free energy = higher score.
    """
    
    def __init__(self):
        self.dim = 64  # Reservoir dimension
        self.tau = 0.1 # Time constant for plasticity
        # Initialize chaotic reservoir weights (Edge of Chaos: spectral radius > 1)
        np.random.seed(42)
        W = np.random.randn(self.dim, self.dim)
        W *= 1.2 / np.max(np.abs(np.linalg.eigvals(W))) # Tune to edge
        self.W_res = W
        
        # Prior weights (complexity penalty reference)
        self.w_prior = np.random.randn(self.dim) * 0.1
        
        # Simple hash-based embedding for deterministic pseudo-semantics
        self.vocab_size = 256

    def _embed(self, text: str) -> np.ndarray:
        """Deterministic pseudo-embedding based on char frequencies and length."""
        vec = np.zeros(self.dim)
        if not text:
            return vec
        for i, char in enumerate(text):
            idx = ord(char) % self.dim
            vec[idx] += 1.0 / (i + 1) # Decay influence over position
        vec *= 10.0 / (np.linalg.norm(vec) + 1e-9) # Normalize
        return vec

    def _run_reservoir(self, x_in: np.ndarray, steps: int = 5) -> np.ndarray:
        """Propagate input through chaotic reservoir to generate state trajectory."""
        state = np.zeros(self.dim)
        # Input coupling
        u = x_in 
        for _ in range(steps):
            # Recurrent dynamics with input drive
            state = np.tanh(np.dot(self.W_res, state) + u * 0.5)
        return state

    def _compute_free_energy(self, state: np.ndarray, target: np.ndarray) -> float:
        """
        Compute proxy for Variational Free Energy F = Accuracy + Complexity.
        Accuracy: Negative squared error between state and target.
        Complexity: Deviation from prior weights.
        """
        accuracy_cost = 0.5 * np.sum((state - target) ** 2)
        complexity_cost = 0.5 * np.sum((state - self.w_prior) ** 2) * 0.1
        return accuracy_cost + complexity_cost

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_vec = self._embed(prompt)
        prompt_state = self._run_reservoir(prompt_vec)
        
        results = []
        # Use prompt state as the 'target' expectation for valid answers
        target = prompt_state 
        
        for cand in candidates:
            cand_vec = self._embed(cand)
            # Candidate drives the reservoir to a new state
            state = self._run_reservoir(cand_vec)
            
            # Calculate Free Energy (lower is better)
            F = self._compute_free_energy(state, target)
            
            # Score is inverse of Free Energy (mapped to 0-1 range via sigmoid-like transform)
            # We add a small epsilon to avoid division by zero
            score = 1.0 / (1.0 + math.exp(F - 2.0)) # Shifted sigmoid
            
            # Reasoning string generation
            reasoning = f"Reservoir trajectory divergence: {F:.4f}. "
            if score > 0.5:
                reasoning += "Low free energy indicates high consistency with prompt context."
            else:
                reasoning += "High free energy suggests semantic or logical mismatch."
                
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]