import re
import numpy as np
from math import log

class ReasoningTool:
    """
    Implements a reasoning evaluator combining Type Theory parsing, Sparse Autoencoders (ISTA),
    and Mechanism Design scoring.
    
    Mechanism:
    1. Parsing (Type Theory): Converts text to a binary feature vector based on logical atoms
       (negations, comparatives, causals, numerics).
    2. Sparse Coding (SAE): Uses a fixed random dictionary and ISTA to find a sparse representation.
       Reconstruction error (E) measures structural alignment between prompt and answer.
    3. Scoring (Mechanism Design): Combines structural fidelity (-E) with a proper logarithmic
       scoring rule to incentivize truthful confidence reporting.
    """
    
    def __init__(self):
        # Hyperparameters
        self.D = 64  # Dimension of feature space
        self.K = 8   # Sparsity level (dictionary size)
        self.LAMB = 0.1  # L1 regularization strength
        self.ITA_STEPS = 10 # ISTA iterations
        self.TAU = 0.5  # Threshold for "correct" classification
        self.ALPHA = 0.5  # Balance between structure and confidence
        
        # Initialize deterministic random dictionary W (D x K)
        np.random.seed(42)
        self.W = np.random.randn(self.D, self.K)
        # Normalize columns
        self.W = self.W / (np.linalg.norm(self.W, axis=0) + 1e-9)

    def _parse_to_vector(self, text: str) -> np.ndarray:
        """Converts text to a typed binary feature vector."""
        if not text:
            return np.zeros(self.D)
        
        t = text.lower()
        features = []
        
        # Define patterns mapped to indices (modulo D to fit vector)
        patterns = [
            (r'\bnot\b|\bno\b|\bnever\b', 0),          # Negation
            (r'\bif\b|\bthen\b|\bunless\b', 1),        # Conditionals
            (r'\bbecause\b|\bleads to\b|\bresults in\b', 2), # Causal
            (r'\bmore than\b|\bless than\b|>|<|>=|<=', 3), # Comparatives
            (r'\bbefore\b|\bafter\b|\bprecedes\b', 4), # Ordering
            (r'\bis\b|\bequals\b|=', 5),               # Equality
            (r'\d+(\.\d+)?', 6),                       # Numerics
            (r'\btrue\b|\bfalse\b|\byes\b|\bno\b', 7)  # Boolean literals
        ]
        
        vec = np.zeros(self.D)
        for pattern, idx in patterns:
            matches = re.findall(pattern, t)
            if matches:
                # Feature type: count (clamped) + presence
                count = min(len(matches), 5) 
                vec[idx] = 1.0
                # Encode magnitude in next few dimensions if space allows
                for i in range(count):
                    if idx + 1 + i < self.D:
                        vec[idx + 1 + i] = 1.0
        
        # Add simple numeric comparison feature if detected
        nums = re.findall(r'\d+(\.\d+)?', t)
        if len(nums) >= 2:
            try:
                vals = [float(n) for n in nums]
                if vals[0] > vals[1]:
                    vec[10] = 1.0 # Num-Greater
                elif vals[0] < vals[1]:
                    vec[11] = 1.0 # Num-Lesser
            except: pass
            
        return vec

    def _ista_solve(self, f: np.ndarray) -> np.ndarray:
        """Solves sparse coding using Iterative Shrinkage-Thresholding Algorithm."""
        z = np.zeros(self.K)
        # Precompute constants for ISTA: z = soft_threshold(z - step * grad, lambda * step)
        # Gradient of 0.5||f - Wz||^2 is -W^T(f - Wz) = W^T W z - W^T f
        # Simplified update: z_new = soft(z + W^T(f - Wz), lambda)
        # Using fixed step size = 1.0 (assuming W is normalized)
        
        Wt = self.W.T
        for _ in range(self.ITA_STEPS):
            residual = f - self.W @ z
            gradient = Wt @ residual
            z = z + gradient
            # Soft thresholding
            z = np.sign(z) * np.maximum(np.abs(z) - self.LAMB, 0)
        return z

    def _compute_error(self, f: np.ndarray, z: np.ndarray) -> float:
        """Computes L2 reconstruction error."""
        recon = self.W @ z
        return float(np.sum((f - recon) ** 2))

    def confidence(self, prompt: str, answer: str) -> float:
        """Estimates confidence based on structural overlap and logical consistency."""
        f_prompt = self._parse_to_vector(prompt)
        f_ans = self._parse_to_vector(answer)
        
        # Simple heuristic: if answer has no logical tokens but prompt does, low confidence
        prompt_sum = np.sum(f_prompt)
        ans_sum = np.sum(f_ans)
        
        if prompt_sum > 2 and ans_sum == 0:
            return 0.1
            
        # Compute sparse codes
        z_prompt = self._ista_solve(f_prompt)
        z_ans = self._ista_solve(f_ans)
        
        # Similarity of sparse codes (cosine-like)
        norm_p = np.linalg.norm(z_prompt)
        norm_a = np.linalg.norm(z_ans)
        if norm_p == 0 or norm_a == 0:
            sim = 0.0
        else:
            sim = float(np.dot(z_prompt, z_ans) / (norm_p * norm_a + 1e-9))
        
        # Map similarity [-1, 1] to [0, 1]
        conf = (sim + 1) / 2.0
        
        # Boost if numeric logic matches
        if f_prompt[10] == f_ans[10] and f_prompt[10] > 0: # Both agree on greater
            conf = min(conf + 0.2, 0.99)
        if f_prompt[11] == f_ans[11] and f_prompt[11] > 0: # Both agree on lesser
            conf = min(conf + 0.2, 0.99)
            
        return max(0.01, min(0.99, conf))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        f_prompt = self._parse_to_vector(prompt)
        
        # Baseline error from prompt self-reconstruction (ideal case)
        z_prompt = self._ista_solve(f_prompt)
        base_error = self._compute_error(f_prompt, z_prompt)
        
        for cand in candidates:
            f_cand = self._parse_to_vector(cand)
            z_cand = self._ista_solve(f_cand)
            
            # Reconstruction Error (E)
            E = self._compute_error(f_cand, z_cand)
            
            # Normalize error relative to prompt complexity roughly
            # Lower E is better. 
            # We invert E for the score component so higher is better.
            # Using negative E directly as per formula: Score = -E + ...
            
            # Confidence scoring
            c = self.confidence(prompt, cand)
            
            # Determine if "correct" based on threshold tau on error difference
            # If candidate error is close to prompt's self-error, it's structurally similar
            is_correct = (E - base_error) < self.TAU
            
            if is_correct:
                S_conf = log(c) if c > 0 else -100.0
            else:
                S_conf = log(1 - c) if (1-c) > 0 else -100.0
                
            score = -E + self.ALPHA * S_conf
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural Error: {E:.4f}, Confidence Score: {S_conf:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results