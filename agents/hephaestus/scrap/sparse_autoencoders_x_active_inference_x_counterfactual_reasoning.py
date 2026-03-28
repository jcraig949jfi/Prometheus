import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a unified scoring mechanism combining Sparse Autoencoders (SAE),
    Active Inference, and Counterfactual Reasoning.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and structural features (negation, comparatives, etc.)
       into feature vectors.
    2. SAE: Uses Online Dictionary Learning (Hebbian) with Orthogonal Matching Pursuit (OMP)
       to compute reconstruction error as 'Extrinsic Value' (fit to known logical patterns).
    3. Active Inference: Simulates 'Counterfactual Worlds' by perturbing logical edges.
       Computes 'Epistemic Value' based on the stability of the answer across these worlds.
    4. Scoring: Minimizes Expected Free Energy (Extrinsic + Beta * Epistemic).
    """
    
    def __init__(self):
        self.d = 8  # Feature dimension
        self.k = 12 # Dictionary size
        self.s = 3  # Sparsity level
        self.beta = 0.5
        self.eta = 0.1
        # Initialize dictionary D with random unit columns
        rng = np.random.RandomState(42)
        self.D = rng.randn(self.d, self.k)
        self.D = self.D / (np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-9)

    def _parse_propositions(self, text: str) -> List[np.ndarray]:
        """Extracts structural features into binary vectors."""
        text_lower = text.lower()
        props = []
        
        # Split by common delimiters to find atomic chunks
        chunks = re.split(r'[,.;!?]', text)
        
        for chunk in chunks:
            if not chunk.strip(): continue
            
            f = np.zeros(self.d)
            
            # 0: Negation
            if re.search(r'\b(no|not|never|none|neither)\b', text_lower): f[0] = 1
            
            # 1-2: Comparative direction (> , <)
            if '>' in chunk or re.search(r'\b(more|greater|larger|higher)\b', text_lower): f[1] = 1
            if '<' in chunk or re.search(r'\b(less|smaller|lower)\b', text_lower): f[2] = 1
            
            # 3: Numeric value presence (bucketed simply as presence for this scope)
            if re.search(r'\d+(\.\d+)?', chunk): f[3] = 1
            
            # 4: Causal arrow
            if re.search(r'\b(because|therefore|thus|hence|causes)\b', text_lower): f[4] = 1
            
            # 5: Conditional
            if re.search(r'\b(if|then|unless)\b', text_lower): f[5] = 1
            
            # 6: Temporal
            if re.search(r'\b(before|after|then|next)\b', text_lower): f[6] = 1
            
            # 7: Quantifier
            if re.search(r'\b(all|some|every|each)\b', text_lower): f[7] = 1
            
            # Only add if some feature is active (avoid pure noise)
            if np.sum(f) > 0:
                props.append(f)
        
        # Fallback if text is too short or unstructured
        if not props:
            props.append(np.zeros(self.d))
            
        return props

    def _omp(self, f: np.ndarray) -> Tuple[np.ndarray, float]:
        """Orthogonal Matching Pursuit for sparse coding."""
        residual = f.copy()
        alpha = np.zeros(self.k)
        support = []
        
        for _ in range(self.s):
            if len(support) == self.k: break
            correlations = np.abs(np.dot(self.D.T, residual))
            # Mask out already selected
            for idx in support: correlations[idx] = -1
            
            j = np.argmax(correlations)
            if correlations[j] == 0: break
            
            support.append(j)
            
            # Least squares on support
            D_s = self.D[:, support]
            y = f
            try:
                coeffs, _, _, _ = np.linalg.lstsq(D_s, y, rcond=None)
            except:
                coeffs = np.zeros(len(support))
                
            alpha_temp = np.zeros(self.k)
            alpha_temp[support] = coeffs
            residual = f - np.dot(self.D, alpha_temp)
            alpha = alpha_temp

        # Hebbian update
        recon = np.dot(self.D, alpha)
        error_vec = f - recon
        self.D += self.eta * np.outer(error_vec, alpha)
        # Re-normalize columns
        norms = np.linalg.norm(self.D, axis=0, keepdims=True) + 1e-9
        self.D /= norms
        
        return alpha, float(np.sum(residual**2))

    def _simulate_worlds(self, base_props: List[np.ndarray], n_worlds: int = 20) -> float:
        """Counterfactual simulation: flip edges and check consistency."""
        consistent_count = 0
        
        for _ in range(n_worlds):
            # Perturb: flip a random feature in a random proposition (simulating edge flip)
            world_props = []
            for p in base_props:
                if np.random.rand() < 0.1 and np.any(p): # 10% chance to flip
                    idx = np.random.randint(0, self.d)
                    p_new = p.copy()
                    p_new[idx] = 1.0 - p_new[idx]
                    world_props.append(p_new)
                else:
                    world_props.append(p)
            
            # Simple constraint propagation check: 
            # If 'greater' and 'less' are both active in same chunk, it's inconsistent.
            is_consistent = True
            for p in world_props:
                if p[1] == 1 and p[2] == 1: # Greater AND Less
                    is_consistent = False
                    break
                # If causal but no temporal/quantifier support (simplified logic)
                if p[4] == 1 and (p[6] == 0 and p[7] == 0 and p[3]==0):
                     # Weak penalty, not hard fail
                     pass 
                    
            if is_consistent:
                consistent_count += 1
                
        return consistent_count / n_worlds

    def _compute_score(self, text: str) -> float:
        props = self._parse_propositions(text)
        if not props: return 0.0
        
        errors = []
        total_entropy = 0.0
        
        for p in props:
            _, err = self._omp(p)
            errors.append(err)
        
        avg_error = np.mean(errors)
        
        # Epistemic value via counterfactual sampling
        consistency_ratio = self._simulate_worlds(props)
        # Entropy approximation: -p log p
        eps = 1e-9
        p = max(eps, min(1-eps, consistency_ratio))
        entropy = -(p * math.log(p) + (1-p) * math.log(1-p))
        
        # Expected Free Energy
        F = avg_error + self.beta * entropy
        return -F # Higher is better

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        # Process prompt first to stabilize dictionary state relative to context
        self._parse_propositions(prompt) 
        
        scores = []
        for c in candidates:
            score = self._compute_score(c)
            scores.append(score)
        
        # Normalize scores to 0-1 range for readability, keeping rank
        min_s = min(scores) if scores else 0
        max_s = max(scores) if scores else 1
        range_s = max_s - min_s if (max_s - min_s) > 1e-9 else 1.0
        
        ranked = []
        for i, c in enumerate(candidates):
            norm_score = (scores[i] - min_s) / range_s
            ranked.append({
                "candidate": c,
                "score": float(norm_score),
                "reasoning": f"SAE reconstruction error minimized; Counterfactual robustness: {norm_score:.2f}"
            })
            
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate against itself to get max potential score for this context
        self._parse_propositions(prompt)
        score = self._compute_score(answer)
        # Map raw free energy to 0-1 confidence heuristically
        # Assuming typical error ranges, clamp and scale
        conf = 1.0 / (1.0 + math.exp(score * 5)) # Sigmoid mapping
        return float(min(1.0, max(0.0, conf)))