import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic-Sparse-Sensitivity Scorer (ESSS)
    
    Mechanism:
    1. Parsing: Extracts atomic logical propositions (numerics, negations, conditionals, causality).
    2. Sparse Rep: Projects proposition vectors onto a fixed orthogonal dictionary (simulating SVD/CS).
    3. Sensitivity: Perturbs the sparse code with Gaussian noise to measure score stability (Variance).
    4. Ergodic Avg: Averages scores over perturbations; penalizes high variance (instability).
    5. Baseline: Uses NCD only as a tiebreaker when structural signals are weak.
    """
    
    def __init__(self):
        # Fixed random seed for determinism
        np.random.seed(42)
        self.m = 6  # Number of proposition types
        # Fixed orthogonal dictionary D (m x k) simulating pre-learned SVD components
        self.D = np.eye(self.m) 
        self.lamb = 0.1
        self.beta = 0.5  # Penalty for sensitivity
        self.N = 20      # Ergodic samples
        self.sigma = 0.05
        
        # Weights w learned via "ridge regression" on hypothetical validation data
        # Priority: Numerics > Conditionals > Causality > Negation > Ordering
        self.w = np.array([1.5, 1.2, 1.0, 0.8, 0.6, 0.4])

    def _extract_features(self, text: str) -> np.ndarray:
        """Extracts binary indicator vector x based on logical patterns."""
        t = text.lower()
        x = np.zeros(self.m)
        
        # 1. Numeric constants/comparisons
        if re.search(r'\d+(\.\d+)?', t) or re.search(r'[<>=]', t):
            x[0] = 1.0
            
        # 2. Negations
        if re.search(r'\b(not|no|never|unless|without)\b', t) or '-' in t:
            x[1] = 1.0
            
        # 3. Conditionals
        if re.search(r'\b(if|then|else|when|provided|unless)\b', t):
            x[2] = 1.0
            
        # 4. Causal verbs
        if re.search(r'\b(causes|leads to|results in|implies|because|therefore)\b', t):
            x[3] = 1.0
            
        # 5. Ordering/Temporal
        if re.search(r'\b(before|after|greater|less|first|last|prior)\b', t):
            x[4] = 1.0
            
        # 6. Conjunctions/Disjunctions (Logical structure)
        if re.search(r'\b(and|or|but|however|moreover)\b', t):
            x[5] = 1.0
            
        return x

    def _sparse_code(self, x: np.ndarray) -> np.ndarray:
        """Computes sparse code alpha = D^T x (simplified Lasso projection)."""
        # Since D is identity in this fixed implementation, alpha ~ x, 
        # but we apply L1 shrinkage manually to simulate sparsity
        alpha = np.dot(self.D.T, x)
        # Soft thresholding for L1 penalty
        return np.sign(alpha) * np.maximum(np.abs(alpha) - self.lamb, 0)

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """Returns (ergodic_mean_score, sensitivity_variance)."""
        # Combine prompt and candidate for context-aware extraction
        full_text = f"{prompt} {candidate}"
        x = self._extract_features(full_text)
        alpha = self._sparse_code(x)
        
        scores = []
        for _ in range(self.N):
            epsilon = np.random.normal(0, self.sigma, size=alpha.shape)
            alpha_pert = alpha + epsilon
            # Linear scorer
            s = np.dot(self.w, alpha_pert)
            scores.append(s)
            
        scores = np.array(scores)
        return np.mean(scores), np.var(scores)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        return (c12 - min(c1, c2)) / denom if denom > 0 else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            mean_score, sens_var = self._score_candidate(prompt, cand)
            # Ergodic Score: Mean - Beta * Variance
            structural_score = mean_score - self.beta * sens_var
            
            # Fallback/Tiebreaker: NCD similarity to prompt (higher similarity often implies relevance)
            # We invert NCD (distance) to similarity and scale it small so it doesn't dominate
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            final_score = structural_score + 0.1 * ncd_sim
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural: {structural_score:.4f}, Sensitivity Penalty: {self.beta*sens_var:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural robustness."""
        mean_score, sens_var = self._score_candidate(prompt, answer)
        structural_score = mean_score - self.beta * sens_var
        
        # Map structural score to 0-1 range using a sigmoid-like mapping
        # Assuming typical scores range between -1 and 3 based on weights
        raw_conf = 1.0 / (1.0 + np.exp(-structural_score))
        return max(0.0, min(1.0, raw_conf))