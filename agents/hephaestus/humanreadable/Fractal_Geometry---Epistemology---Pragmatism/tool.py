import numpy as np
from typing import List, Dict

class ReasoningTool:
    """
    Fractal Pragmatic Epistemic Network (FPEN) Simulator.
    
    Mechanism:
    1. Fractal Layer: Maps candidates to a latent space via hash-derived seeds.
       Uses a deterministic Iterated Function System (IFS) logic to estimate 
       'hypothesis density' (simulating Hausdorff dimension coverage).
    2. Epistemic Layer: Computes a Bayesian-like posterior where likelihood 
       is inversely proportional to the semantic distance from the prompt 
       (simulating prediction error/reliability).
    3. Pragmatic Layer: Applies a utility weight based on candidate specificity 
       (length/complexity proxy) to re-rank scores via softmax, balancing 
       correctness probability with informational utility.
    """
    
    def __init__(self):
        self._seed = 42  # Deterministic state

    def _hash_to_vec(self, text: str, dim: int = 2) -> np.ndarray:
        """Deterministic mapping of string to latent vector."""
        h = np.array([hash(text + str(i)) for i in range(dim)], dtype=np.float64)
        return (h - h.mean()) / (h.std() + 1e-9)

    def _ifs_density(self, seed_vec: np.ndarray, iterations: int = 4) -> float:
        """Simulates fractal hypothesis generation density."""
        points = [seed_vec]
        # Simple contractive maps: scale by 0.5, shift by seed components
        for _ in range(iterations):
            new_pts = []
            for p in points:
                for i in range(len(p)):
                    shift = np.zeros_like(p)
                    shift[i] = 1.0 / (len(p) + 1)
                    new_pts.append(0.5 * p + shift)
            points = new_pts
        # Density proxy: inverse of average distance to origin
        dists = [np.linalg.norm(p) for p in points]
        return 1.0 / (np.mean(dists) + 0.1)

    def _compute_score(self, prompt: str, candidate: str) -> float:
        # 1. Fractal Layer: Generate latent representation and density
        p_vec = self._hash_to_vec(prompt)
        c_vec = self._hash_to_vec(candidate)
        fractal_density = self._ifs_density(c_vec)
        
        # 2. Epistemic Layer: Reliability based on latent similarity (inverse error)
        # Normalized similarity as likelihood
        dist = np.linalg.norm(p_vec - c_vec)
        likelihood = np.exp(-dist) 
        
        # Prior from fractal structure (normalized loosely)
        prior = min(1.0, fractal_density / 10.0) 
        posterior = likelihood * (0.5 + 0.5 * prior) # Bayesian update proxy
        
        # 3. Pragmatic Layer: Utility = Reward (posterior) - Cost (complexity)
        # Cost proxy: length deviation from prompt (assumes relevant answers match prompt scale)
        cost = abs(len(candidate) - len(prompt)) / (len(prompt) + 1)
        utility = posterior - 0.1 * cost
        
        return utility

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scores = []
        for cand in candidates:
            raw_score = self._compute_score(prompt, cand)
            scores.append((cand, raw_score))
        
        # Normalize via Softmax (Pragmatic re-weighting)
        raw_vals = np.array([s[1] for s in scores])
        exp_vals = np.exp(raw_vals - np.max(raw_vals)) # Stability
        norm_scores = exp_vals / np.sum(exp_vals)
        
        results = []
        for i, (cand, _) in enumerate(scores):
            results.append({
                "candidate": cand,
                "score": float(norm_scores[i]),
                "reasoning": f"Fractal density & epistemic match yielded utility score {norm_scores[i]:.4f}"
            })
            
        # Rank by score descending
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against itself in a list to get relative score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # The softmax score in a single-item list is 1.0, so we use the raw utility logic
        # mapped to 0-1 via sigmoid for absolute confidence
        raw_util = self._compute_score(prompt, answer)
        return float(1.0 / (1.0 + np.exp(-raw_util * 5))) # Sigmoid scaling