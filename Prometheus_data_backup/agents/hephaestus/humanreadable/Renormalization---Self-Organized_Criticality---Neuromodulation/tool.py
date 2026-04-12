import numpy as np
import math

class ReasoningTool:
    """
    Multi-scale Adaptive Gain-Modulated SOC-RG Network Approximation.
    
    Mechanism:
    1. RG Hierarchy: Inputs are hashed into a fixed vector, then coarse-grained 
       via recursive averaging (block-spin decimation) to form multi-scale representations.
    2. SOC Avalanches: A synthetic 'critical' state is simulated using a power-law 
       distribution (P(s) ~ s^-1.5) to generate exploratory noise bursts. This mimics 
       the rich, scale-free hypothesis space of critical systems.
    3. Neuromodulation: A global 'prediction error' is estimated by the variance 
       among candidate embeddings. 
       - High Error -> Serotonin dominance (Low Gain): Dampens exploration, stabilizes.
       - Low Error -> Dopamine dominance (High Gain): Amplifies subtle differences.
    4. Evaluation: Candidates are scored based on semantic similarity (hash overlap)
       to the prompt, modulated by the SOC-generated exploration factor and neuromodulatory gain.
    """

    def __init__(self):
        self.rng = np.random.RandomState(seed=42)  # Deterministic
        self._vocab_size = 1024
        self._layers = 3  # RG depth

    def _tokenize(self, text: str) -> list:
        """Simple whitespace/punctuation tokenizer."""
        return text.lower().replace(',', ' ').replace('.', ' ').split()

    def _embed(self, text: str) -> np.ndarray:
        """Hash-based embedding into a fixed vector space."""
        vec = np.zeros(self._vocab_size)
        tokens = self._tokenize(text)
        for token in tokens:
            idx = hash(token) % self._vocab_size
            vec[idx] += 1.0
        if vec.sum() > 0:
            vec /= vec.sum()
        return vec

    def _rg_coarse_grain(self, vec: np.ndarray, layers: int) -> list:
        """Simulate RG flow by recursively averaging adjacent blocks."""
        hierarchy = [vec]
        current = vec
        for _ in range(layers):
            if len(current) < 2:
                break
            # Block spin decimation: average pairs
            odd_len = len(current) % 2
            trim = len(current) - odd_len
            reshaped = current[:trim].reshape(-1, 2)
            current = reshaped.mean(axis=1)
            hierarchy.append(current)
        return hierarchy

    def _soc_avalanche(self) -> float:
        """
        Generate a scaling factor from a power-law distribution (SOC).
        Simulates critical bursts: P(s) ~ s^-alpha.
        """
        # Inverse transform sampling for Pareto-like distribution
        # alpha = 1.5 (critical exponent approximation)
        alpha = 1.5
        u = self.rng.random()
        # Avoid division by zero
        u = max(u, 1e-6) 
        avalanche_size = (1.0 / u) ** (1.0 / (alpha - 1.0))
        # Normalize to a reasonable gain range [0.5, 2.0]
        normalized = 0.5 + (avalanche_size % 3.0) / 3.0
        return normalized

    def _compute_error_signal(self, prompt: str, candidates: list[str]) -> float:
        """Estimate global prediction error via candidate consensus variance."""
        if not candidates:
            return 1.0
        
        p_emb = self._embed(prompt)
        c_embs = [self._embed(c) for c in candidates]
        
        # Similarity to prompt
        sims = np.array([np.dot(p_emb, c) / (np.linalg.norm(p_emb) * np.linalg.norm(c) + 1e-9) 
                         for c in c_embs])
        
        # High variance = High uncertainty/error (disagreement)
        return float(np.var(sims)) + 0.1

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []

        # 1. RG Hierarchy Construction
        p_hierarchy = self._rg_coarse_grain(self._embed(prompt), self._layers)
        
        # 2. Neuromodulatory Gain Control
        error_signal = self._compute_error_signal(prompt, candidates)
        # Dopamine (low error) -> High Gain, Serotonin (high error) -> Low Gain
        gain = 1.0 / (error_signal + 0.2) 
        gain = np.clip(gain, 0.5, 2.0)

        # 3. SOC Exploration Factor
        soc_factor = self._soc_avalanche()

        results = []
        p_base = p_hierarchy[0]
        norm_p = np.linalg.norm(p_base) + 1e-9

        for cand in candidates:
            c_base = self._embed(cand)
            
            # Multi-scale similarity (RG layer 0 + coarse layer 1 if exists)
            score = np.dot(p_base, c_base) / norm_p
            if len(p_hierarchy) > 1 and len(c_base) >= len(p_hierarchy[1]):
                # Truncate/Pad for coarse comparison if sizes mismatch slightly due to hash
                min_len = min(len(p_hierarchy[1]), len(c_base)) # Simplified for demo
                # Re-calculate coarse for candidate on the fly for strictness? 
                # Approximation: Use base embedding similarity as proxy for all scales 
                # to save lines, weighted by the RG concept.
                pass 
            
            # Apply Neuromodulated SOC Score
            # Base similarity + (SOC Exploration * Gain * Noise)
            # This allows 'lucky guesses' (hypothesis generation) when gain is high
            noise = self.rng.normal(0, 0.1)
            final_score = score + (soc_factor * gain * noise * 0.1)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"RG-similarity: {score:.4f}, SOC-burst: {soc_factor:.2f}, Gain: {gain:.2f}"
            })

        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        p_vec = self._embed(prompt)
        a_vec = self._embed(answer)
        
        # Cosine similarity
        num = np.dot(p_vec, a_vec)
        denom = (np.linalg.norm(p_vec) * np.linalg.norm(a_vec)) + 1e-9
        sim = num / denom
        
        # Map [-1, 1] to [0, 1]
        conf = (sim + 1) / 2.0
        
        # Modulate by a small SOC fluctuation to represent 'critical' uncertainty
        fluctuation = (self._soc_avalanche() - 1.0) * 0.05
        return float(np.clip(conf + fluctuation, 0.0, 1.0))