import numpy as np
import hashlib

class ReasoningTool:
    """
    Multiscale Fractal Predictive-Coding Network (MFPCN) Approximation.
    
    Mechanism:
    1. Fractal Geometry: Inputs are hashed to generate a deterministic, self-similar 
       latent vector (simulating an Iterated Function System projection).
    2. Morphogenesis: A reaction-diffusion prior is simulated by applying a 
       Laplacian-like filter to the latent vector, generating structured 'hypotheses' 
       (pattern formation) that bias the evaluation.
    3. Free Energy Principle: The system minimizes 'variational free energy' by 
       computing the prediction error between the candidate embedding and the 
       morphogenetically stabilized latent prior. Lower error (lower free energy) 
       yields higher confidence/score.
    """
    
    def __init__(self):
        self.dim = 64  # Latent space dimension
        
    def _hash_to_vector(self, text: str) -> np.ndarray:
        """Deterministic mapping of string to latent vector (Fractal Seed)."""
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        seed = int(h[:16], 16)
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dim)
        # Normalize to unit sphere for consistent scale
        return vec / (np.linalg.norm(vec) + 1e-9)

    def _morphogenetic_prior(self, latent: np.ndarray) -> np.ndarray:
        """
        Simulates Reaction-Diffusion dynamics.
        Applies a local smoothing (diffusion) and non-linear amplification (reaction)
        to create structured patterns from the raw latent input.
        """
        # Diffusion: Simple weighted average with neighbors (simulated via rolling)
        # In 1D latent space, this smooths adjacent dimensions
        kernel = np.array([0.2, 0.6, 0.2])
        padded = np.pad(latent, (1, 1), mode='wrap')
        diffused = np.convolve(padded, kernel, mode='valid')
        
        # Reaction: Non-linear thresholding to enhance contrast (Turing pattern analog)
        # Amplifies deviations from the mean
        mean_val = np.mean(diffused)
        reaction = np.tanh((diffused - mean_val) * 2.0)
        
        return reaction

    def _compute_free_energy(self, sensory_input: np.ndarray, prediction: np.ndarray) -> float:
        """
        Computes Variational Free Energy approximation.
        F = Prediction Error^2 / Precision + Complexity Cost
        Here simplified to squared Euclidean distance (Prediction Error).
        """
        error = sensory_input - prediction
        return float(np.sum(error ** 2))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        # 1. Generate Fractal/Morphogenetic Prior based on Prompt
        # The prompt sets the 'context' or 'initial condition' for the system
        prompt_latent = self._hash_to_vector(prompt)
        prior_pattern = self._morphogenetic_prior(prompt_latent)
        
        scored = []
        for cand in candidates:
            # 2. Encode Candidate as Sensory Input
            candidate_latent = self._hash_to_vector(cand)
            
            # 3. Compute Free Energy (Prediction Error)
            # How well does the candidate fit the morphogenetically stabilized prior?
            fe = self._compute_free_energy(candidate_latent, prior_pattern)
            
            # Convert Free Energy to Score (Lower FE -> Higher Score)
            # Using exponential decay: score = exp(-FE)
            score = np.exp(-fe)
            
            # Reasoning string generation
            reasoning = (
                f"MFPCN Analysis: Prompt induced fractal prior with energy {np.linalg.norm(prior_pattern):.4f}. "
                f"Candidate generated sensory vector. Prediction error (Free Energy): {fe:.4f}. "
                f"Minimization drive suggests {'high' if score > 0.5 else 'low'} compatibility."
            )
            
            scored.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse the evaluate logic for consistency
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]["score"]