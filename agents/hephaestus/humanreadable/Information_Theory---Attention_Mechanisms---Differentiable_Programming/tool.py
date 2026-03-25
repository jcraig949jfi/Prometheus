import math
import hashlib

class ReasoningTool:
    """
    Implements a simplified Differentiable Information-Bottleneck Attention (DIB-Attention)
    mechanism using only numpy-free standard library operations for deterministic execution.
    
    Mechanism Analogy:
    1. Encoding: Maps tokens to fixed integer vectors based on character hashes.
    2. Attention (Query-Key): Computes similarity between prompt (Query) and candidate (Key).
    3. Information Bottleneck (IB): 
       - Compression: Penalizes candidates with high entropy (randomness/noise).
       - Preservation: Rewards candidates that maximize mutual information proxy 
         (alignment with prompt features).
    4. Scoring: Combines task loss (semantic match) with IB regularization to rank candidates.
    """

    def __init__(self):
        self.vocab_size = 256
        self.embed_dim = 16
        # Deterministic pseudo-projection weights (fixed seeds)
        self.weights = [(i * 7 + 3) % 17 - 8 for i in range(self.embed_dim)]

    def _hash_vec(self, text: str) -> list[float]:
        """Deterministic sparse embedding based on character hashes."""
        vec = [0.0] * self.embed_dim
        if not text:
            return vec
        for char in text:
            h = ord(char)
            for i in range(self.embed_dim):
                # Simple deterministic mixing
                val = ((h * (i + 1) + self.weights[i]) % 101) - 50
                vec[i] += val / (len(text) * 50.0)
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _dot_product(self, v1: list[float], v2: list[float]) -> float:
        return sum(a * b for a, b in zip(v1, v2))

    def _entropy_proxy(self, text: str) -> float:
        """Estimates entropy (complexity/noise) of the text."""
        if not text:
            return 0.0
        freq = {}
        for c in text:
            freq[c] = freq.get(c, 0) + 1
        ent = 0.0
        length = len(text)
        for count in freq.values():
            p = count / length
            if p > 0:
                ent -= p * math.log2(p)
        return ent

    def _mutual_info_proxy(self, prompt_vec: list[float], cand_vec: list[float]) -> float:
        """
        Estimates mutual information proxy via alignment strength.
        High alignment = high preserved predictive information.
        """
        return self._dot_product(prompt_vec, cand_vec)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        prompt_vec = self._hash_vec(prompt)
        results = []
        
        # Calculate max possible score for normalization
        scores = []
        for cand in candidates:
            cand_vec = self._hash_vec(cand)
            
            # 1. Preservation Term (Alignment with prompt)
            preservation = self._mutual_info_proxy(prompt_vec, cand_vec)
            
            # 2. Compression Term (Penalize unnecessary complexity/entropy)
            # Normalizing entropy by length to avoid bias towards long text
            complexity = self._entropy_proxy(cand) / (math.log2(len(cand) + 2) + 1e-9)
            
            # 3. Task Loss Proxy (Simple string overlap heuristic for 'correctness')
            # In a real neural net, this is the gradient from the label. 
            # Here we approximate semantic match via shared token density.
            common_tokens = set(prompt.lower().split()) & set(cand.lower().split())
            task_match = len(common_tokens) * 0.5 + (1.0 if prompt.lower().strip() in cand.lower() else 0.0)
            
            # DIB Objective: Maximize (Preservation - lambda * Complexity) + Task Match
            # lambda_H set to 0.3 to balance compression
            score = (preservation * 1.5) - (complexity * 0.3) + task_match
            
            scores.append((cand, score))
        
        # Normalize scores to 0-1 range roughly
        if scores:
            min_s = min(s[1] for s in scores)
            max_s = max(s[1] for s in scores)
            range_s = max_s - min_s if max_s != min_s else 1.0
            
            ranked = []
            for cand, raw_score in sorted(scores, key=lambda x: x[1], reverse=True):
                normalized_score = (raw_score - min_s) / range_s
                ranked.append({
                    "candidate": cand,
                    "score": float(normalized_score),
                    "reasoning": f"IB-Score: Alignment={self._mutual_info_proxy(prompt_vec, self._hash_vec(cand)):.2f}, Complexity Penalty={self._entropy_proxy(cand)*0.3:.2f}"
                })
            return ranked
        return []

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the DIB score of the single answer.
        """
        # Reuse evaluation logic for consistency
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]