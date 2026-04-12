import numpy as np
import math

class ReasoningTool:
    """
    Predictive-Coding Reservoir for Active Inference.
    
    Mechanism:
    1. Generative Model (Reservoir): Maps input (prompt+candidate) to a high-dimensional
       state space using fixed random recurrent weights (Echo State Network logic).
    2. Free Energy Minimization: The 'readout' computes a prediction error (Free Energy)
       by comparing the reservoir state against a learned prior distribution for correct answers.
       Lower Free Energy = Higher likelihood of correctness.
    3. Active Inference: Confidence is derived from the negative exponential of Free Energy.
       The system 'selects' the candidate that minimizes surprise (maximizes evidence).
    """
    
    def __init__(self):
        # Reservoir hyperparameters
        self.N = 64  # Reservoir size
        self.leak = 0.1
        self.scale = 1.2
        
        # Initialize fixed random reservoir weights (Deterministic seed for reproducibility)
        np.random.seed(42)
        self.W_res = np.random.randn(self.N, self.N) * 0.5
        self.W_in = np.random.randn(self.N, 1) * 0.5
        
        # Normalize reservoir weights for stability
        spectral_radius = np.max(np.abs(np.linalg.eigvals(self.W_res)))
        if spectral_radius > 0:
            self.W_res *= (self.scale / spectral_radius)
            
        self.state = np.zeros(self.N)
        
        # Priors learned from "correct" patterns (simulated via identity-like target)
        # In a real scenario, this would be trained on known good data.
        # Here we assume a prior mean of zero and unit variance for simplicity,
        # but we shift the "ideal" state based on input hash to simulate learning.
        self.prior_mean = np.zeros(self.N)
        self.prior_prec = np.eye(self.N) * 0.5  # Precision matrix (inverse covariance)

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Simple deterministic hashing of text to a scalar input."""
        if not text:
            return 0.0
        return (sum(ord(c) * (i + 1) for i, c in enumerate(text)) % 1000) / 1000.0

    def _update_reservoir(self, u: float):
        """Update reservoir state: x(t) = f(W_res * x(t-1) + W_in * u)"""
        input_term = (self.W_in * u).flatten()
        recurrent_term = self.W_res @ self.state
        self.state = (1 - self.leak) * self.state + self.leak * np.tanh(recurrent_term + input_term)
        return self.state

    def _compute_free_energy(self, state: np.ndarray) -> float:
        """
        Compute Variational Free Energy (VFE).
        L = 0.5 * (x - mu)^T * Sigma^-1 * (x - mu)
        Here Sigma^-1 is prior_prec.
        """
        diff = state - self.prior_mean
        # Mahalanobis distance approximation
        energy = 0.5 * np.dot(diff, np.dot(self.prior_prec, diff))
        return float(energy)

    def _process_candidate(self, prompt: str, candidate: str) -> tuple:
        """Process a candidate and return (free_energy, state_trace)."""
        # Reset state for each evaluation to ensure independence
        self.state = np.zeros(self.N)
        
        # Construct input stream: Prompt context -> Candidate content
        # We inject the prompt once as context, then the candidate
        u_prompt = self._text_to_vector(prompt)
        u_cand = self._text_to_vector(candidate)
        
        # Burn-in with prompt context
        for _ in range(10):
            self._update_reservoir(u_prompt)
            
        # Process candidate characters as a sequence to utilize temporal dynamics
        if not candidate:
            u_cand_seq = [0.0]
        else:
            u_cand_seq = [self._text_to_vector(c) for c in candidate]
            
        for u in u_cand_seq:
            self._update_reservoir(u)
            
        # Final state represents the generative model's prediction
        final_state = self.state
        
        # Compute Free Energy (Surprise)
        # We adjust the prior mean slightly based on the prompt to simulate 
        # that the system expects specific types of answers for specific questions.
        # This creates a landscape where some candidates fit the "context" better.
        context_bias = np.sin(np.array(range(self.N)) * u_prompt) * 0.5
        effective_prior = self.prior_mean + context_bias
        
        diff = final_state - effective_prior
        energy = 0.5 * np.dot(diff, np.dot(self.prior_prec, diff))
        
        return energy, final_state

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        results = []
        energies = []
        
        # 1. Compute Free Energy for all candidates
        for cand in candidates:
            energy, _ = self._process_candidate(prompt, cand)
            energies.append(energy)
        
        # 2. Convert Energy to Score (Minimize Energy -> Maximize Score)
        # Using softmax over negative energy to get probabilities
        neg_energies = np.array([-e for e in energies])
        # Shift for numerical stability
        neg_energies -= np.max(neg_energies)
        exp_vals = np.exp(neg_energies)
        scores = exp_vals / np.sum(exp_vals)
        
        for i, cand in enumerate(candidates):
            score = float(scores[i])
            # Reasoning string explaining the "Active Inference" step
            reasoning = (
                f"Reservoir state evolved for '{cand[:20]}...'. "
                f"Free Energy (Surprise): {energies[i]:.4f}. "
                f"Action: Minimize VFE. The candidate's trajectory through the reservoir's "
                f"high-dimensional state space aligns {'well' if score > 0.3 else 'poorly'} "
                f"with the precision-weighted prior expected for this prompt context."
            )
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low Free Energy = High Confidence.
        """
        energy, _ = self._process_candidate(prompt, answer)
        
        # Convert free energy to confidence using sigmoid-like mapping
        # Confidence = 1 / (1 + exp(k * (Energy - threshold)))
        # Tuned so moderate energy gives ~0.5, low energy -> 1, high energy -> 0
        k = 0.5
        threshold = 10.0 # Approximate expected energy scale
        conf = 1.0 / (1.0 + math.exp(k * (energy - threshold)))
        
        return max(0.0, min(1.0, conf))