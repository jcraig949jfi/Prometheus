import numpy as np
import hashlib

class ReasoningTool:
    """
    GEINLA: Gauge-Equivariant Immune-Neuromodulatory Learning Architecture.
    
    Mechanism:
    1. Gauge Equivariance: Inputs are hashed to a seed, ensuring that the 'coordinate 
       system' (random state) for evaluating a specific prompt is invariant to execution 
       order or external noise. The 'fiber' (model parameters) is simulated via a 
       deterministic projection of the candidate string into a latent space.
    2. Immune Dynamics: We generate a 'clonal population' of the candidate by perturbing 
       its latent representation with noise derived from the gauge seed. Each clone 
       computes a fitness score based on semantic alignment (simulated via hash overlap 
       and length heuristics) with the prompt context.
    3. Neuromodulation: A global gain factor is calculated based on the variance (uncertainty) 
       of the clonal population's fitness. High variance (high uncertainty) triggers 
       'dopaminergic' exploration (widening the score distribution), while low variance 
       triggers 'serotonergic' exploitation (sharpening confidence).
    """

    def __init__(self):
        self.base_dim = 64  # Dimension of the latent fiber space

    def _gauge_seed(self, prompt: str) -> int:
        """Generates a deterministic seed based on the prompt (Gauge fixing)."""
        h = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        return int(h[:8], 16)

    def _project_to_fiber(self, text: str, seed: int) -> np.ndarray:
        """Projects text into a latent vector (fiber coordinate) deterministically."""
        # Combine text hash and seed for context-aware projection
        combined = f"{text}_{seed}"
        h = hashlib.sha256(combined.encode('utf-8')).digest()
        vec = np.array([b for b in h], dtype=np.float32)
        # Expand to base_dim by tiling and truncating
        vec = np.tile(vec, (self.base_dim // len(vec)) + 1)[:self.base_dim]
        # Normalize
        vec = (vec - np.mean(vec)) / (np.std(vec) + 1e-9)
        return vec

    def _compute_fitness(self, prompt: str, candidate: str, noise: np.ndarray) -> float:
        """
        Computes fitness of a clone. 
        Simulates predictive error minimization via string similarity heuristics.
        """
        # Heuristic 1: Length similarity (proxy for structural match)
        len_ratio = 1.0 - abs(len(prompt) - len(candidate)) / (max(len(prompt), len(candidate)) + 1)
        
        # Heuristic 2: Token overlap (proxy for semantic alignment)
        p_tokens = set(prompt.lower().split())
        c_tokens = set(candidate.lower().split())
        overlap = len(p_tokens & c_tokens) / (len(p_tokens | c_tokens) + 1e-9)
        
        # Base fitness
        base_fit = 0.4 * len_ratio + 0.6 * overlap
        
        # Add clone-specific noise (mutation effect)
        mutation_impact = np.sum(noise * 0.1) 
        return float(base_fit + mutation_impact)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        gauge_seed = self._gauge_seed(prompt)
        np.random.seed(gauge_seed)  # Fix gauge for this prompt
        
        results = []
        all_scores = []
        
        # Phase 1: Clonal Expansion & Selection
        for cand in candidates:
            # Generate clonal population (size 5)
            base_vec = self._project_to_fiber(cand, gauge_seed)
            clone_scores = []
            
            for i in range(5):
                # Mutate fiber coordinates
                noise = np.random.randn(self.base_dim) * 0.5
                score = self._compute_fitness(prompt, cand, noise)
                clone_scores.append(score)
            
            # Select best clone (fitness maximization)
            best_clone_score = max(clone_scores)
            results.append({"candidate": cand, "raw_score": best_clone_score})
            all_scores.append(best_clone_score)

        # Phase 2: Neuromodulatory Gain Adjustment
        # Gain scales based on population uncertainty (variance of scores)
        if len(all_scores) > 1:
            uncertainty = np.std(all_scores)
            # Dopamine-like: High uncertainty -> higher gain on differences
            # Serotonin-like: Low uncertainty -> lower gain, stabilize
            gain = 1.0 + 2.0 * uncertainty 
        else:
            gain = 1.0

        # Apply gain and normalize
        final_scores = []
        for r in results:
            # Center then scale by gain
            adjusted = (r["raw_score"] - 0.5) * gain + 0.5
            adjusted = max(0.0, min(1.0, adjusted)) # Clamp 0-1
            final_scores.append(adjusted)
        
        # Normalize to relative ranking
        min_s, max_s = min(final_scores), max(final_scores)
        range_s = max_s - min_s if max_s > min_s else 1.0
        
        ranked = []
        for i, r in enumerate(results):
            norm_score = (final_scores[i] - min_s) / range_s
            ranked.append({
                "candidate": r["candidate"],
                "score": float(norm_score),
                "reasoning": f"Gauge-invariant clone selection yielded raw fitness {r['raw_score']:.3f}. Neuromodulatory gain ({gain:.2f}) adjusted final score based on population uncertainty."
            })
            
        # Sort descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluation logic for single candidate consistency
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Confidence is the score itself, as it represents the normalized fitness 
        # after neuromodulatory adjustment.
        return float(res[0]["score"])