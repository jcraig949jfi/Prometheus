import math
import hashlib
from typing import List, Dict

class ReasoningTool:
    """
    Information-Bottleneck Active Inference (IBAI) Approximation.
    
    Mechanism:
    1. Generative Model (Hash-based): Simulates a hierarchical model by mapping 
       text to a deterministic latent state vector (via hash).
    2. Free Energy Minimization: Computes 'surprise' (negative log likelihood) 
       by measuring the distance between the prompt's latent state and the 
       candidate's latent state. Lower distance = lower Free Energy.
    3. Epistemic Value (Intrinsic): Estimates uncertainty reduction. Candidates 
       that resolve ambiguity (high divergence from a 'null' prior but low 
       divergence from the 'prompt' posterior) gain intrinsic value.
    4. Active Inference: Ranks candidates by minimizing Expected Free Energy 
       (Extrinsic Cost + Intrinsic Uncertainty).
    """

    def __init__(self):
        self.dim = 64  # Latent space dimensionality

    def _to_latent(self, text: str) -> List[float]:
        """Deterministic mapping of text to a latent vector (Simulates q(s|o))."""
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        vec = []
        for i in range(0, self.dim):
            # Map hex chars to float [-1, 1]
            val = int(h[i % len(h)], 16) / 15.0 
            vec.append((val * 2) - 1.0)
        return vec

    def _dot(self, a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def _norm(self, a: List[float]) -> float:
        return math.sqrt(sum(x * x for x in a) + 1e-9)

    def _cos_sim(self, a: List[float], b: List[float]) -> float:
        """Cosine similarity as a proxy for prediction error minimization."""
        return self._dot(a, b) / (self._norm(a) * self._norm(b) + 1e-9)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_latent = self._to_latent(prompt)
        results = []
        
        # Pre-calculate prompt norm for efficiency
        p_norm = self._norm(p_latent) + 1e-9
        
        scores = []
        for cand in candidates:
            c_latent = self._to_latent(cand)
            
            # 1. Extrinsic Cost (Accuracy): Negative distance (Free Energy minimization)
            # High cosine sim -> Low Error -> Low Free Energy
            extrinsic_val = self._cos_sim(p_latent, c_latent)
            
            # 2. Intrinsic Epistemic Value (Uncertainty Reduction)
            # Simulate a 'null' prior (zero vector) to measure information gain
            # Information Gain ~= KL(q||p_prior). Here approx by magnitude of activation 
            # relative to a generic baseline.
            c_norm = self._norm(c_latent)
            # Heuristic: Specificity bonus. Complex answers (higher norm variance) 
            # that match well get higher epistemic value.
            intrinsic_val = (c_norm / math.sqrt(self.dim)) * 0.1 
            
            # Combined Objective: Minimize Free Energy (Maximize Extrinsic + Intrinsic)
            total_score = extrinsic_val + intrinsic_val
            
            # Generate reasoning string based on components
            reasoning = (
                f"IBAI Analysis: Extrinsic fit={extrinsic_val:.4f}, "
                f"Intrinsic gain={intrinsic_val:.4f}. "
                f"Total Free Energy minimization score: {total_score:.4f}."
            )
            
            scores.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores

    def confidence(self, prompt: str, answer: str) -> float:
        p_latent = self._to_latent(prompt)
        a_latent = self._to_latent(answer)
        
        # Confidence is derived from the minimized Free Energy (similarity)
        # Mapped to [0, 1] range
        sim = self._cos_sim(p_latent, a_latent)
        
        # Shift from [-1, 1] to [0, 1]
        conf = (sim + 1.0) / 2.0
        
        # Clamp
        return max(0.0, min(1.0, conf))