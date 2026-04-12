import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning scorer based on Ergodic Theory, Chaos Theory, and Sparse Autoencoders.
    
    Mechanism:
    1. Structural Parsing: Extracts binary feature vectors (negations, comparatives, etc.) from text.
    2. Sparse Coding (SAE): Uses a fixed orthogonal dictionary and Iterative Shrinkage-Thresholding 
       (ISTA) to find sparse representations of these features.
    3. Ergodic Scoring: Compares the time-average of the sparse code against a pre-computed 
       space-average (corpus norm) to measure statistical consistency.
    4. Chaos Scoring: Perturbs the input features and measures the amplification (Lyapunov exponent) 
       after one ISTA step to penalize unstable reasoning.
    5. Final Score: Weighted combination of Ergodic alignment, Chaos stability, and Sparsity.
    """

    def __init__(self):
        # Primitives for structural parsing
        self.patterns = [
            r'\bnot\b|\bno\b',          # Negation
            r'\bmore\b|\bless\b|[<>]',  # Comparative
            r'\bif\b|\bthen\b|\bunless\b', # Conditional
            r'\bbecause\b|\bleads to\b|\bresults in\b', # Causal
            r'\bbefore\b|\bafter\b|\bfirst\b|\blast\b', # Ordering
            r'\d+(\.\d+)?%?',           # Numeric
            r'\ball\b|\bsome\b|\bnone\b' # Quantifiers
        ]
        self.M = len(self.patterns)
        self.K = self.M * 2  # Over-complete dictionary
        
        # Initialize fixed dictionary D (Orthogonal-like for stability)
        # D shape: (M, K)
        rng = np.random.default_rng(seed=42)
        D_raw = rng.standard_normal((self.M, self.K))
        # Normalize columns
        norms = np.linalg.norm(D_raw, axis=0, keepdims=True)
        norms[norms == 0] = 1
        self.D = D_raw / norms
        
        # Pre-computed space average (mu_star) - simulated from a "corpus" of logical text
        # Assumption: Logical text has moderate activation of conditionals and quantifiers
        self.mu_star = np.zeros(self.K)
        self.mu_star[2:4] = 0.5  # Conditionals
        self.mu_star[6:8] = 0.3  # Quantifiers
        
        # Hyperparameters
        self.eta = 0.1  # Step size (simplified 1/||D||^2 approx)
        self.lambda_sparsity = 0.1
        self.ista_steps = 5
        self.w1 = 1.0 # Ergodic
        self.w2 = 0.5 # Chaos
        self.w3 = 0.1 # Sparsity penalty

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature matrix F (T=1 treated as single aggregate vector for this scope)."""
        text_lower = text.lower()
        features = np.zeros(self.M)
        for i, pattern in enumerate(self.patterns):
            if re.search(pattern, text_lower):
                features[i] = 1.0
        return features

    def _ista_step(self, Z: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Single step of Iterative Shrinkage-Thresholding Algorithm."""
        # Reconstruction error
        recon = Z @ self.D.T
        error = recon - F
        # Gradient descent
        Z_new = Z - self.eta * (error @ self.D)
        # Soft thresholding
        threshold = self.lambda_sparsity
        Z_new = np.sign(Z_new) * np.maximum(np.abs(Z_new) - threshold, 0)
        return Z_new

    def _run_ista(self, F: np.ndarray, steps: int) -> np.ndarray:
        """Run ISTA for fixed steps."""
        Z = np.zeros(self.K)
        for _ in range(steps):
            Z = self._ista_step(Z, F)
        return Z

    def _compute_ergodic_score(self, Z: np.ndarray) -> float:
        """Compute negative distance between time average (Z) and space average (mu_star)."""
        # Since T=1 per candidate in this simplified view, time average is just Z
        return -np.linalg.norm(Z - self.mu_star)

    def _compute_chaos_score(self, F: np.ndarray, Z: np.ndarray) -> float:
        """Approximate Lyapunov exponent via perturbation."""
        epsilon = 1e-4
        delta_F = epsilon * np.random.randn(self.M)
        # Perturb F
        F_pert = F + delta_F
        # Run one step of ISTA on perturbed input starting from same Z=0 for fair comparison of sensitivity
        # Or strictly following prompt: measure amplification after one iteration
        Z_pert = np.zeros(self.K)
        Z_pert = self._ista_step(Z_pert, F_pert)
        
        # Measure divergence
        diff_Z = np.linalg.norm(Z_pert - Z)
        diff_F = np.linalg.norm(delta_F)
        
        if diff_F == 0:
            return 0.0
            
        # Lyapunov estimate: log(||delta_Z|| / ||delta_F||) / steps (tau=1 here)
        # If diff_Z is very small, log is large negative -> stable -> good score (less penalty)
        # We want S_cha = -lambda_hat. 
        # Large lambda_hat (positive) = chaotic = bad score.
        ratio = diff_Z / diff_F
        if ratio == 0:
            lyap = -10.0 # Extremely stable
        else:
            lyap = np.log(ratio + 1e-10) # + small epsilon to avoid log(0) if ratio is 0
            
        return -lyap

    def _get_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        if max(c1, c2) == 0: return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feat = self._extract_features(prompt)
        
        # Baseline NCD for tie-breaking
        prompt_comp = len(zlib.compress(prompt.encode()))
        
        for cand in candidates:
            # 1. Feature Extraction
            F = self._extract_features(cand)
            
            # 2. Sparse Coding (ISTA)
            Z = self._run_ista(F, self.ista_steps)
            
            # 3. Ergodic Score
            s_erg = self._compute_ergodic_score(Z)
            
            # 4. Chaos Score
            s_cha = self._compute_chaos_score(F, Z)
            
            # 5. Sparsity Penalty
            sparsity_penalty = np.sum(np.abs(Z))
            
            # Final Score
            score = self.w1 * s_erg + self.w2 * s_cha - self.w3 * sparsity_penalty
            
            # NCD Tie-breaker logic (incorporated as small bonus if structurally similar to prompt)
            # This helps when structural signals are weak
            ncd_val = self._get_ncd(prompt, cand)
            if ncd_val < 0.5: # If somewhat similar
                score += 0.01 * (1 - ncd_val)
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Ergodic:{s_erg:.2f}, Chaos:{s_cha:.2f}, Sparse:{-sparsity_penalty:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on relative scoring."""
        # Generate a dummy wrong answer to compare against? 
        # Instead, use the absolute score mapped to 0-1 via sigmoid-like function
        # Since scores can be negative, we normalize based on typical ranges observed in testing
        
        F = self._extract_features(answer)
        Z = self._run_ista(F, self.ista_steps)
        s_erg = self._compute_ergodic_score(Z)
        s_cha = self._compute_chaos_score(F, Z)
        sparsity_penalty = np.sum(np.abs(Z))
        
        raw_score = self.w1 * s_erg + self.w2 * s_cha - self.w3 * sparsity_penalty
        
        # Heuristic mapping: 
        # Typical good scores > -2.0, bad scores < -5.0 (depends on params)
        # Map [-10, 0] roughly to [0, 1]
        conf = 1.0 / (1.0 + np.exp(raw_score + 3.0)) # Shifted sigmoid
        return float(np.clip(conf, 0.0, 1.0))