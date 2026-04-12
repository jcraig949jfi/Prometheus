import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Abductive Immune-Sparse Reasoner.
    
    Mechanism:
    1. Structural Parsing: Extracts 6 binary logical features (neg, comp, cond, num, caus, ord).
    2. Sparse Coding: Projects features onto a fixed dictionary of 'explanatory prototypes' 
       using Iterative Shrinkage-Thresholding (ISTA). Reconstruction error measures fit.
    3. Immune Clonal Selection: Simulates hypothesis refinement. High-affinity (low error) 
       candidates are cloned and mutated to explore local structural variations.
    4. Scoring: Final score combines best immune-generation affinity with NCD tie-breaking.
    """
    
    # Fixed Dictionary D (6x12): Prototypical explanatory patterns (columns)
    # Rows: neg, comp, cond, num, caus, ord
    D = np.array([
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0], # neg
        [0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0], # comp
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1], # cond
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0], # num
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1], # caus
        [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]  # ord
    ], dtype=float)

    def __init__(self):
        self.D = self.D.T  # Transpose to shape (12, 6) for D @ a operation if a is (12,)
        # Actually, standard sparse coding: x ≈ D @ a. 
        # If D is (6x12) and a is (12,), result is (6,). Correct.
        # We store D as (6, 12) in the class var, but need to be careful with dot products.
        # Let's keep D as (6, 12). x is (6,). a is (12,).
        # Reconstruction: D @ a -> (6, 12) @ (12,) = (6,). Matches x.

    def _parse_features(self, text: str) -> np.ndarray:
        """Extract 6 binary structural features."""
        t = text.lower()
        # neg: not, no, never
        neg = 1 if re.search(r'\b(not|no|never)\b', t) else 0
        # comp: more, less, -er, as ... as
        comp = 1 if re.search(r'\b(more|less|better|worse|greater|smaller)|\b\w+er\b|\bas\s+\w+\s+as', t) else 0
        # cond: if, unless, provided
        cond = 1 if re.search(r'\b(if|unless|provided|assuming)\b', t) else 0
        # num: integers or decimals
        num = 1 if re.search(r'\d+(\.\d+)?', t) else 0
        # caus: because, therefore, leads to
        caus = 1 if re.search(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', t) else 0
        # ord: before, after, first, last
        ord_ = 1 if re.search(r'\b(before|after|first|last|prior|subsequent)\b', t) else 0
        return np.array([neg, comp, cond, num, caus, ord_], dtype=float)

    def _soft_threshold(self, x: np.ndarray, lam: float) -> np.ndarray:
        return np.sign(x) * np.maximum(np.abs(x) - lam, 0)

    def _compute_affinity(self, x: np.ndarray) -> float:
        """Compute affinity via sparse coding reconstruction error."""
        # ISTA parameters
        T_steps = 10
        lr = 0.1
        lam = 0.15
        
        a = np.zeros(12) # Sparse code
        D = self.D # 6x12
        
        # Gradient descent step
        for _ in range(T_steps):
            # gradient = D.T @ (D @ a - x)
            recon = D @ a
            error_vec = recon - x
            gradient = D.T @ error_vec
            a = self._soft_threshold(a - lr * gradient, lam)
        
        # Reconstruction error
        final_recon = D @ a
        err = np.linalg.norm(x - final_recon)
        return 1.0 / (1.0 + err)

    def _immune_clonal_selection(self, x: np.ndarray, generations: int = 3) -> float:
        """Simulate immune clonal selection to refine affinity."""
        # Initial population: just the candidate itself (represented by its feature vector x)
        # In this abstract space, we clone the 'idea' of the answer.
        # Since we can't generate new text, we simulate mutation by perturbing the feature vector
        # slightly to see if a 'nearby' logical structure fits the prototype better.
        
        best_affinity = self._compute_affinity(x)
        current_x = x.copy()
        
        for _ in range(generations):
            # Clone count based on affinity (simulated)
            # Higher affinity -> more clones (simulated by sampling more mutations)
            clone_count = max(1, int(5 * best_affinity))
            
            mutants = []
            for _ in range(clone_count):
                # Mutate: flip 1-2 bits randomly
                mutant_x = current_x.copy()
                flips = np.random.randint(1, 3)
                indices = np.random.choice(6, flips, replace=False)
                for idx in indices:
                    mutant_x[idx] = 1.0 - mutant_x[idx] # Flip 0->1, 1->0
                
                aff = self._compute_affinity(mutant_x)
                mutants.append((aff, mutant_x))
            
            # Select best mutant if better than current
            if mutants:
                mutants.sort(key=lambda m: m[0], reverse=True)
                top_aff, top_x = mutants[0]
                if top_aff > best_affinity:
                    best_affinity = top_aff
                    current_x = top_x
                    
        return best_affinity

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(z(s1_b))
        len_s2 = len(z(s2_b))
        len_comb = len(z(s1_b + s2_b))
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
        return (len_comb - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feat = self._parse_features(prompt)
        results = []
        
        # Calculate base scores
        scores = []
        for cand in candidates:
            cand_feat = self._parse_features(cand)
            # Primary score: Immune-refined affinity
            affinity = self._immune_clonal_selection(cand_feat)
            
            # Secondary score: NCD similarity to prompt (as a tiebreaker/modifier)
            # We want answers that are structurally similar but not identical copying
            ncd_val = self._ncd(prompt, cand)
            
            # Heuristic: High affinity is good. Low NCD (high similarity) is good but secondary.
            # Combine: Score = 0.7 * Affinity + 0.3 * (1 - NCD)
            # Note: NCD is 0..1 where 0 is identical. So (1-NCD) is similarity.
            combined_score = 0.7 * affinity + 0.3 * (1.0 - ncd_val)
            
            scores.append(combined_score)
        
        # Normalize scores to 0-1 range roughly
        min_s = min(scores)
        max_s = max(scores)
        range_s = max_s - min_s if max_s > min_s else 1.0
        
        for i, cand in enumerate(candidates):
            norm_score = (scores[i] - min_s) / range_s
            results.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": f"Structural affinity: {scores[i]:.4f}, NCD modifier applied."
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        cand_list = [answer]
        # Evaluate against itself to get a baseline, but we need context.
        # Since we only have one candidate here, we rely purely on the internal affinity 
        # of the answer's structure against the universal dictionary, 
        # and its NCD fit to the prompt.
        
        x = self._parse_features(answer)
        affinity = self._immune_clonal_selection(x)
        ncd_val = self._ncd(prompt, answer)
        
        # Same weighting as evaluate
        raw_score = 0.7 * affinity + 0.3 * (1.0 - ncd_val)
        
        # Clamp to 0-1
        return max(0.0, min(1.0, raw_score))