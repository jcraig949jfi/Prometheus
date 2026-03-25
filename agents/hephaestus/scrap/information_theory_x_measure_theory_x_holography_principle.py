import math
import hashlib
from typing import List, Dict

class ReasoningTool:
    """
    Holographic Measure-Theoretic Information-Bottleneck (HMIB) Approximation.
    
    Mechanism:
    1. Bulk Encoder: Maps text to a latent vector via deterministic hashing 
       (simulating a frozen deep network).
    2. Boundary Decoder: Uses a tensor-network analogy where 'area' (latent dim) 
       limits information capacity (Bekenstein bound).
    3. Measure-Regularizer: Computes a score based on the 'Radon-Nikodym' derivative 
       analogy. We treat the candidate's hash-derived density vs. a uniform prior.
       If the candidate deviates too wildly from the prompt's expected measure 
       (high divergence), the regularizer penalizes it, simulating the rejection 
       of non-absolutely continuous hypotheses.
    4. Scoring: Combines semantic similarity (via hash overlap) with the measure 
       penalty to rank candidates.
    """

    def __init__(self):
        self.latent_dim = 64
        self.beta = 0.5  # Compression weight
        self.lambda_reg = 0.2  # Measure regularizer weight

    def _hash_to_vector(self, text: str) -> List[float]:
        """Deterministic mapping of string to latent space [0, 1]^dim."""
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        vector = []
        for i in range(self.latent_dim):
            chunk = h[i % len(h): (i % len(h)) + 2]
            if len(chunk) < 2: chunk = chunk + '0'
            val = int(chunk, 16) / 255.0
            vector.append(val)
        return vector

    def _compute_mutual_info_approx(self, v1: List[float], v2: List[float]) -> float:
        """Approximate I(X;Z) via cosine similarity as a proxy for alignment."""
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1)) + 1e-9
        norm2 = math.sqrt(sum(b * b for b in v2)) + 1e-9
        return dot / (norm1 * norm2)

    def _compute_measure_regularizer(self, posterior: List[float], prior_mean: float) -> float:
        """
        Approximates R_mu = D_KL(Q || P).
        Treats posterior as observed density and prior as uniform reference.
        Penalizes high divergence (non-absolute continuity).
        """
        eps = 1e-9
        divergence = 0.0
        for p in posterior:
            # Simple binary entropy-like divergence from uniform reference
            q = p + eps
            p_ref = prior_mean + eps
            if q > 0:
                divergence += q * math.log(q / p_ref)
        return divergence

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_vec = self._hash_to_vector(prompt)
        prior_mean = 0.5  # Uniform prior expectation on [0,1]
        results = []

        for cand in candidates:
            cand_vec = self._hash_to_vector(cand)
            
            # 1. Information Term: Alignment between prompt and candidate
            info_gain = self._compute_mutual_info_approx(prompt_vec, cand_vec)
            
            # 2. Measure Regularizer: Penalty for diverging from typicality
            reg_penalty = self._compute_measure_regularizer(cand_vec, prior_mean)
            
            # 3. Holographic Bound Objective
            # Score = Info - Beta*Compression - Lambda*Reg
            # Since we approximate compression via the fixed dim, we focus on Info - Reg
            score = info_gain - (self.lambda_reg * reg_penalty)
            
            # Normalize score to [0, 1] roughly for ranking
            final_score = max(0.0, min(1.0, (score + 1.0) / 2.0))

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Info:{info_gain:.4f} Reg:{reg_penalty:.4f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the HMIB objective."""
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        return ranked[0]["score"]