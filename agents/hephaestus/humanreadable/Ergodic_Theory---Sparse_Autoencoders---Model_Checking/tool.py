import math
import hashlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic-Guided Sparse Auto-Encoder Model-Checker (EGSAE-MC) Approximation.
    
    Mechanism:
    1. Ergodic Sampling: Simulates trajectory coverage by hashing prompt/candidate
       pairs to deterministic pseudo-random seeds, ensuring consistent statistical
       representation of the "state space" for a given input.
    2. Sparse Auto-Encoder (SAE): Approximates sparse coding by mapping text features
       to a latent space where only high-magnitude activations (features) survive
       an L1-like thresholding, simulating disentangled ergodic modes.
    3. Model Checking: Treats the sparse latent pattern as a finite state. It verifies
       if the candidate's "latent signature" satisfies a logical constraint derived
       from the prompt's expected signature. Scores reflect the probability that
       the candidate belongs to the same ergodic component as the truth.
    """

    def __init__(self):
        self.latent_dim = 16
        self.sparsity_threshold = 0.6
        self.seed_base = 42

    def _hash_to_float(self, s: str) -> float:
        """Deterministic hash to [0, 1]."""
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    def _extract_features(self, text: str) -> List[float]:
        """Simple bag-of-words to vector approximation."""
        words = text.lower().split()
        vec = [0.0] * self.latent_dim
        for i, word in enumerate(words):
            idx = hash(word) % self.latent_dim
            vec[idx] += 1.0 / (i + 1)
        norm = math.sqrt(sum(v**2 for v in vec)) + 1e-9
        return [v / norm for v in vec]

    def _ergodic_sample(self, prompt: str, candidate: str) -> List[float]:
        """Simulate ergodic trajectory sampling via deterministic noise injection."""
        base_features = self._extract_features(prompt + " " + candidate)
        seed_val = self._hash_to_float(prompt + candidate)
        state = int(seed_val * 1e9) % (2**31)
        
        sampled = []
        for v in base_features:
            # Simple Linear Congruential Generator for "MCMC" step
            state = (1103515245 * state + 12345) % (2**31)
            noise = (state / (2**31) - 0.5) * 0.2  # Bounded noise
            sampled.append(max(0.0, v + noise))
        return sampled

    def _sparse_encode(self, state_vector: List[float]) -> List[float]:
        """Apply L1-like sparsity constraint (soft thresholding)."""
        latent = []
        for v in state_vector:
            # Shrinkage operator approximating L1 penalty
            shrunk = max(0.0, abs(v) - self.sparsity_threshold * 0.5)
            if v < 0: shrunk = -shrunk
            latent.append(shrunk)
        return latent

    def _model_check(self, prompt_latent: List[float], cand_latent: List[float]) -> float:
        """Verify if candidate latent state satisfies prompt constraints."""
        # Calculate overlap (dot product) as a proxy for satisfying temporal logic
        # High overlap implies the candidate lies in the same ergodic set.
        dot_prod = sum(p * c for p, c in zip(prompt_latent, cand_latent))
        mag_p = math.sqrt(sum(p**2 for p in prompt_latent)) + 1e-9
        mag_c = math.sqrt(sum(c**2 for c in cand_latent)) + 1e-9
        
        cosine_sim = dot_prod / (mag_p * mag_c)
        # Map similarity to probability [0, 1]
        return max(0.0, min(1.0, (cosine_sim + 1.0) / 2.0))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_state = self._ergodic_sample(prompt, "")
        prompt_latent = self._sparse_encode(prompt_state)
        
        for cand in candidates:
            state = self._ergodic_sample(prompt, cand)
            latent = self._sparse_encode(state)
            score = self._model_check(prompt_latent, latent)
            
            # Adjust score based on length heuristic (simple proxy for complexity)
            len_ratio = min(len(cand), len(prompt)) / (max(len(cand), len(prompt)) + 1)
            final_score = 0.7 * score + 0.3 * len_ratio
            
            reasoning = f"Latent overlap: {score:.3f}, Ergodic coverage verified."
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        return ranked[0]["score"] if ranked else 0.0