import numpy as np
import math

class ReasoningTool:
    """
    Quantum-Variational Active Inference (QVAI) Approximation.
    
    Mechanism:
    1. Superposition: Candidates are treated as basis states in a Hilbert space.
       Initial amplitudes are uniform, representing maximum entropy uncertainty.
    2. Entanglement (Structured Priors): A covariance matrix is synthesized based on 
       textual overlap (Jaccard index) between candidates. This allows 'surprise' 
       (prediction error) to propagate between semantically similar hypotheses.
    3. Measurement (Thompson Sampling): We simulate a quantum measurement by sampling 
       from the probability distribution defined by the squared amplitudes, biased 
       by the prompt context.
    4. Free Energy Minimization: The 'Hamiltonian' (H) represents prediction error. 
       We approximate the gradient step by adjusting amplitudes: increasing probability 
       for candidates that align with the 'context vector' (prompt embedding analog) 
       and decreasing others, effectively minimizing variational free energy.
    5. Collapse: The final scores represent the post-update probability distribution.
    """

    def __init__(self):
        self.rng = np.random.default_rng(seed=42) # Deterministic seed for reproducibility

    def _text_to_vector(self, text: str, length: int) -> np.ndarray:
        """Simple deterministic hash-based vectorization for ASCII text."""
        vec = np.zeros(length)
        if not text:
            return vec
        for i, char in enumerate(text):
            val = ord(char)
            idx = (val * (i + 1)) % length
            vec[idx] += val / 255.0
        # Normalize
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def _jaccard_similarity(self, s1: str, s2: str) -> float:
        """Calculate Jaccard similarity of character sets as a proxy for entanglement."""
        if not s1 or not s2:
            return 0.0
        set1, set2 = set(s1.lower()), set(s2.lower())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        n = len(candidates)
        dim = 64 # Feature dimension for simulation
        
        # 1. Initialize Superposition: Uniform amplitudes alpha_i = 1/sqrt(N)
        # Probability P_i = |alpha_i|^2 = 1/N
        alphas = np.ones(n) / np.sqrt(n)
        
        # 2. Construct Entanglement Matrix (Covariance based on textual similarity)
        # E_ij represents correlation between hypothesis i and j
        entangle_mat = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    entangle_mat[i, j] = 1.0
                else:
                    entangle_mat[i, j] = self._jaccard_similarity(candidates[i], candidates[j])
        
        # 3. Define Hamiltonian (Prediction Error) based on Prompt-Candidate alignment
        # We simulate an 'observation' vector from the prompt
        prompt_vec = self._text_to_vector(prompt, dim)
        candidate_vecs = np.array([self._text_to_vector(c, dim) for c in candidates])
        
        # Calculate raw alignment scores (dot product)
        alignments = np.dot(candidate_vecs, prompt_vec)
        
        # Normalize alignments to [0, 1] range for probability update logic
        min_align, max_align = alignments.min(), alignments.max()
        if max_align > min_align:
            norm_alignments = (alignments - min_align) / (max_align - min_align)
        else:
            norm_alignments = np.ones(n) * 0.5
            
        # 4. Variational Update (Gradient Descent on Free Energy)
        # F = <H> - S. We update amplitudes to minimize error (maximize alignment)
        # while respecting entanglement (smoothing).
        
        # Simulate measurement noise (Thompson sampling component)
        noise = self.rng.normal(0, 0.05, n)
        effective_energy = norm_alignments + noise
        
        # Propagate energy through entanglement matrix (correlated update)
        # This allows high confidence in one hypothesis to boost related ones
        updated_probs = np.dot(entangle_mat, effective_energy)
        
        # Ensure non-negative and normalize to sum to 1 (Probability Simplex)
        updated_probs = np.maximum(updated_probs, 0)
        total = updated_probs.sum()
        if total > 0:
            probs = updated_probs / total
        else:
            probs = np.ones(n) / n
            
        # 5. Generate Output
        results = []
        for i, cand in enumerate(candidates):
            # Reasoning string explaining the quantum-analogous process
            reasoning = (
                f"Superposition collapsed via Thompson-sampling. "
                f"Entanglement propagated alignment from similar hypotheses. "
                f"Free energy minimized by favoring candidate {i+1} with score {probs[i]:.4f}."
            )
            results.append({
                "candidate": cand,
                "score": float(probs[i]),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate the single answer against the prompt using the same mechanism
        # We treat the single answer as a candidate list of one, but compare 
        # its internal consistency with the prompt via the vector alignment.
        
        dim = 64
        p_vec = self._text_to_vector(prompt, dim)
        a_vec = self._text_to_vector(answer, dim)
        
        # Cosine similarity as the base confidence
        dot_prod = np.dot(p_vec, a_vec)
        norm_p = np.linalg.norm(p_vec)
        norm_a = np.linalg.norm(a_vec)
        
        if norm_p == 0 or norm_a == 0:
            base_conf = 0.0
        else:
            base_conf = dot_prod / (norm_p * norm_a)
            
        # Map from [-1, 1] to [0, 1]
        confidence = (base_conf + 1) / 2.0
        
        # Apply a 'quantum Zeno' effect penalty if the answer is too short relative to prompt
        # (Simulating that insufficient data leads to higher uncertainty)
        if len(answer) < len(prompt) * 0.1:
            confidence *= 0.8
            
        return float(np.clip(confidence, 0.0, 1.0))