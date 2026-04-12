import numpy as np
import math

class ReasoningTool:
    """
    Holographic Wavelet Optimal Control (HWOC) Reasoning Engine.
    
    Mechanism:
    1. Holographic Projection: Maps input text to a fixed-dimensional latent space
       using a deterministic hash-based embedding, simulating a low-dimensional boundary.
    2. Wavelet Multi-Resolution: Decomposes the latent vector into coarse (global)
       and fine (local) scales using a Haar-like differencing scheme.
    3. Active Inference Control: 
       - Evaluates candidates by simulating their trajectory in latent space.
       - Computes a 'Control Cost' based on the deviation from a stable fixed point
         (simulating the solution to the HJB equation via LQR approximation).
       - Hypothesis Generation: Candidates that minimize prediction error (cost) 
         while maximizing scale-separation (information gain) receive higher scores.
    """
    
    def __init__(self):
        self.dim = 64  # Holographic boundary dimension
        self.seed = 42
        np.random.seed(self.seed)

    def _hash_text(self, text: str) -> np.ndarray:
        """Deterministic mapping of text to a latent vector (Holographic Screen)."""
        vec = np.zeros(self.dim)
        if not text:
            return vec
        for i, char in enumerate(text):
            idx = (ord(char) * (i + 1)) % self.dim
            val = (ord(char) + i) / 256.0
            vec[idx] += val
        # Normalize to simulate bounded energy
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def _wavelet_decompose(self, x: np.ndarray) -> tuple:
        """
        Simple Haar-like decomposition into Coarse (avg) and Fine (diff) scales.
        Returns (coarse_features, fine_features, energy_ratio).
        """
        if len(x) < 2:
            return x, np.zeros_like(x), 1.0
        
        mid = len(x) // 2
        # Coarse: Low frequency structure
        coarse = (x[:mid] + x[mid:]) / 2.0
        # Fine: High frequency details
        fine = (x[:mid] - x[mid:]) / 2.0
        
        # Energy ratio indicates complexity/uncertainty at fine scales
        e_fine = np.sum(fine**2) + 1e-9
        e_total = np.sum(x**2) + 1e-9
        ratio = e_fine / e_total
        
        return coarse, fine, ratio

    def _solve_riccati_cost(self, state: np.ndarray, target: np.ndarray) -> float:
        """
        Approximates optimal control cost (LQR) to steer state to target.
        Cost = x^T P x where P is identity (simplified Riccati solution).
        """
        diff = state - target
        return float(np.dot(diff, diff))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        # 1. Holographic Encoding of Prompt (The Boundary Condition)
        prompt_vec = self._hash_text(prompt)
        coarse_p, fine_p, _ = self._wavelet_decompose(prompt_vec)
        
        # Define a synthetic 'stable manifold' target based on prompt structure
        # This represents the system dynamics evolving toward equilibrium
        target_vec = np.roll(prompt_vec, 1) - np.roll(prompt_vec, -1)
        
        results = []
        for cand in candidates:
            cand_vec = self._hash_text(cand)
            
            # 2. Multi-resolution Analysis of Candidate
            coarse_c, fine_c, fine_ratio = self._wavelet_decompose(cand_vec)
            
            # 3. Optimal Control Cost (HJB approximation)
            # We want the candidate to 'complete' the prompt dynamics with minimal effort
            # Effort = distance to target manifold
            control_cost = self._solve_riccati_cost(cand_vec, target_vec)
            
            # Information Gain Term: Prefer candidates that resolve fine-scale uncertainty
            # High fine_ratio in candidate implies it adds necessary detail (hypothesis discrimination)
            # But we penalize excessive noise (very high ratio) or total lack of detail (very low)
            # Ideal is a balance where the candidate aligns with prompt coarse structure
            coarse_align = 1.0 / (1.0 + np.sum((coarse_p - coarse_c)**2) + 1e-9)
            
            # Score formulation:
            # Low control cost (good fit) + Good coarse alignment + Moderate fine detail
            score = (1.0 / (1.0 + control_cost)) * 0.6 + \
                    (coarse_align * 0.3) + \
                    (0.1 * math.exp(-abs(fine_ratio - 0.25) * 2)) # Prefer some complexity
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"ControlCost={control_cost:.4f}, CoarseAlign={coarse_align:.4f}, FineScaleRatio={fine_ratio:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the specific answer.
        """
        # Re-run evaluation logic internally to get the score
        # We simulate a candidate list of one to get the raw metrics
        prompt_vec = self._hash_text(prompt)
        cand_vec = self._hash_text(answer)
        target_vec = np.roll(prompt_vec, 1) - np.roll(prompt_vec, -1)
        
        control_cost = self._solve_riccati_cost(cand_vec, target_vec)
        coarse_p, _, _ = self._wavelet_decompose(prompt_vec)
        coarse_c, _, _ = self._wavelet_decompose(cand_vec)
        coarse_align = 1.0 / (1.0 + np.sum((coarse_p - coarse_c)**2) + 1e-9)
        
        raw_score = (1.0 / (1.0 + control_cost)) * 0.6 + (coarse_align * 0.4)
        
        # Normalize to 0-1 range roughly
        # Since max theoretical score is ~1.0, we clamp
        conf = min(1.0, max(0.0, raw_score))
        return float(conf)