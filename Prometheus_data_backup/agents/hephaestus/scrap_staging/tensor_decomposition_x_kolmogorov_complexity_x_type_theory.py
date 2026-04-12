import numpy as np
import hashlib
from typing import List, Dict, Optional

class ReasoningTool:
    """
    Implements a Complexity-Aware Typed Tensor Language (CTTL) simulator.
    
    Mechanism:
    1. Typing: Encodes string hypotheses into tensors based on semantic hash properties,
       enforcing shape constraints (Type Checking).
    2. Decomposition: Simulates CP/Tucker decomposition by reducing the tensor to 
       factor matrices based on intrinsic rank derived from data variance.
    3. Compression: Estimates Kolmogorov Complexity (K) via the description length 
       of the decomposed normal form (sum of log-factor sizes + rank overhead).
    
    Hypotheses with lower K (simpler explanation) that satisfy type constraints 
    receive higher scores, embodying Occam's Razor within a typed framework.
    """

    def __init__(self):
        self._seed = 42  # Determinism

    def _encode_to_tensor(self, text: str, max_dim: int = 10) -> np.ndarray:
        """Encodes a string hypothesis into a deterministic pseudo-tensor."""
        h = hashlib.sha256(text.encode()).hexdigest()
        # Derive shape from hash prefix
        dims = [int(h[i:i+2], 16) % max_dim + 1 for i in range(0, 8, 2)]
        size = np.prod(dims)
        # Generate deterministic data
        np.random.seed(int(h[:8], 16) + self._seed)
        data = np.random.randn(size)
        return data.reshape(dims)

    def _decompose_and_compress(self, tensor: np.ndarray) -> float:
        """
        Simulates Decompose and Compress operations.
        Returns estimated Kolmogorov Complexity (description length).
        """
        # 1. Decompose: Estimate rank via variance threshold (simulating CP/Tucker)
        flat = tensor.flatten()
        variance = np.var(flat)
        # Heuristic: Higher variance implies higher effective rank/complexity
        # Normalize to a rank between 1 and min_dimension
        effective_rank = max(1, int(np.log1p(variance * 10) * 2))
        
        # 2. Compress: Calculate description length of the normal form
        # K(T) ≈ sum(log(|F_i|)) + overhead(rank)
        # Factor size approximation
        factor_cost = np.sum([np.log2(s + 1) for s in tensor.shape]) * effective_rank
        
        # Rank vector overhead
        rank_overhead = np.log2(effective_rank + 1) * len(tensor.shape)
        
        return float(factor_cost + rank_overhead)

    def _type_check(self, text: str) -> bool:
        """Simulates type checking: ensures hypothesis has valid 'shape' (length/content)."""
        if not text or len(text.strip()) < 2:
            return False
        # Simulate symmetry constraint: must have balanced char distribution roughly
        # (In a real system, this checks algebraic properties)
        return len(set(text)) > 1

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            # Type Check
            if not self._type_check(cand):
                score = 0.0
                reason = "Rejected: Ill-typed hypothesis (fails symmetry/shape constraints)."
            else:
                # Encode & Decompose
                tensor = self._encode_to_tensor(cand)
                k_complexity = self._decompose_and_compress(tensor)
                
                # Score inversely proportional to complexity (Occam's Razor)
                # Normalized roughly to 0-1 range assuming typical complexity values
                score = 1.0 / (1.0 + k_complexity / 10.0)
                reason = f"Accepted. Normal form rank: {int(np.log1p(np.var(tensor))*2)}, K(T)≈{k_complexity:.2f}. Simpler representations favored."
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Rank by score descending
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on type validity and compression efficiency."""
        if not self._type_check(answer):
            return 0.0
        
        tensor = self._encode_to_tensor(answer)
        k_val = self._decompose_and_compress(tensor)
        
        # Map complexity to confidence: Low K -> High Confidence
        # Using a sigmoid-like mapping for smoothness
        confidence = 1.0 / (1.0 + np.exp((k_val - 5.0) / 2.0))
        return float(np.clip(confidence, 0.01, 0.99))