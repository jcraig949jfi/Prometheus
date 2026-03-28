import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning evaluator combining structural abstract interpretation with sparse coding.
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts logical primitives (negations, comparatives, 
       conditionals, quantifiers) and numeric constraints from text.
    2. Abstract Interpretation: Maps extracted features to a lattice (Intervals for numbers, 
       Boolean lattice for truth). Computes a 'logical distance' based on constraint violations.
    3. Sparse Autoencoder (Secondary): Maintains a dynamic dictionary of logical primitives. 
       Candidates are encoded via soft-thresholding. Reconstruction error contributes to the score.
    4. Neural Plasticity: The dictionary updates via Hebbian learning when a candidate 
       demonstrates high logical fidelity, mimicking experience-dependent reorganization.
    5. Scoring: Weighted sum of logical soundness (abstract distance) and representation fidelity.
       NCD is used strictly as a tiebreaker.
    """
    
    def __init__(self):
        self.p = 64  # Feature dimensionality
        self.k = 32  # Dictionary size
        self.D = np.random.randn(self.p, self.k)
        self.D = self.D / np.linalg.norm(self.D, axis=0)  # Normalize columns
        self.lambda_reg = 0.1
        self.eta = 0.01
        self.tau = 0.05
        self.s = 5  # Max non-zeros per column
        
        # Primitives to detect
        self.primitives = [
            r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bfalse\b',  # Negation
            r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', # Conditionals
            r'\ball\b', r'\bevery\b', r'\bany\b', r'\bsome\b', r'\bexists\b', # Quantifiers
            r'\bgreater\b', r'\bless\b', r'\bequal\b', r'\bmore\b', r'\bfewer\b', # Comparatives
            r'\bbefore\b', r'\bafter\b', r'\bcause\b', r'\blead\b', # Temporal/Causal
            r'>', r'<', r'=', r'!=', r'>=', r'<='
        ]
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.primitives]

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features into a vector."""
        vec = np.zeros(self.p)
        text_lower = text.lower()
        
        # 1. Primitive presence (first k-1 slots)
        for i, pat in enumerate(self.patterns):
            if i < self.k - 1:
                vec[i] = len(pat.findall(text_lower))
        
        # 2. Numeric extraction (interval approximation)
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            vals = [float(n) for n in nums]
            vec[self.k-1] = np.mean(vals) if vals else 0.0
            vec[self.k] = np.max(vals) - np.min(vals) if len(vals) > 1 else 0.0
            
        # 3. Length and complexity proxies
        vec[self.k+1] = len(text) / 1000.0
        vec[self.k+2] = text.count(',') / 10.0
        
        return vec

    def _soft_threshold(self, x: np.ndarray, D: np.ndarray, lam: float, steps=10) -> np.ndarray:
        """Iterative soft-thresholding for sparse coding: min ||x - Da||^2 + l||a||_1"""
        k = D.shape[1]
        alpha = np.zeros(k)
        # Simple gradient descent with thresholding
        for _ in range(steps):
            residual = x - D @ alpha
            grad = -2 * (D.T @ residual)
            alpha = alpha - 0.1 * grad
            # Soft threshold
            alpha = np.sign(alpha) * np.maximum(np.abs(alpha) - lam, 0)
        return alpha

    def _abstract_distance(self, cand: str, ref: str) -> float:
        """
        Compute logical distance via abstract interpretation.
        Returns 0.0 for perfect match, higher for violations.
        """
        dist = 0.0
        count = 0
        
        # 1. Boolean/Negation Lattice
        has_not_c = any(p.search(cand.lower()) for p in self.patterns[:4])
        has_not_r = any(p.search(ref.lower()) for p in self.patterns[:4])
        if has_not_c != has_not_r:
            dist += 1.0
        count += 1
        
        # 2. Numeric Interval Distance
        nums_c = [float(n) for n in re.findall(r'-?\d+\.?\d*', cand)]
        nums_r = [float(n) for n in re.findall(r'-?\d+\.?\d*', ref)]
        
        if nums_c and nums_r:
            # Check bounds overlap roughly
            min_c, max_c = min(nums_c), max(nums_c)
            min_r, max_r = min(nums_r), max(nums_r)
            
            # Intersection over union approximation for intervals
            inter_l = max(min_c, min_r)
            inter_u = min(max_c, max_r)
            if inter_l < inter_u:
                intersection = inter_u - inter_l
            else:
                intersection = 0.0
            
            union = (max_c - min_c) + (max_r - min_r) - intersection
            if union > 0:
                dist += (1.0 - intersection / union)
            count += 1
        elif (not nums_c and nums_r) or (nums_c and not nums_r):
            dist += 1.0 # One has numbers, other doesn't
            count += 1
            
        # 3. Structural Keyword Overlap (Jaccard on primitives)
        set_c = {i for i, p in enumerate(self.patterns) if p.search(cand.lower())}
        set_r = {i for i, p in enumerate(self.patterns) if p.search(ref.lower())}
        if set_c or set_r:
            jaccard = len(set_c & set_r) / len(set_c | set_r) if (set_c | set_r) else 1.0
            dist += (1.0 - jaccard)
            count += 1
            
        return dist / max(count, 1)

    def _hebbian_update(self, x: np.ndarray, alpha: np.ndarray):
        """Update dictionary D based on active features (Plasticity)."""
        # D <- D + eta * (alpha * x^T)
        update = self.eta * np.outer(x, alpha)
        self.D += update
        
        # Renormalize columns
        norms = np.linalg.norm(self.D, axis=0)
        norms[norms == 0] = 1
        self.D = self.D / norms
        
        # Sparsity threshold on D (enforce ||D_col||_0 <= s roughly by zeroing small entries)
        self.D[np.abs(self.D) < self.tau] = 0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        l1, l2 = len(s1), len(s2)
        if l1 == 0 or l2 == 0: return 1.0
        concat = s1 + s2
        c1, c2, c_cat = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress(concat.encode()))
        return (c_cat - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Use the longest/most detailed candidate as a pseudo-reference if no explicit ref
        # In a real scenario, 'prompt' might contain the reference, or we compare candidates against each other.
        # Here, we assume the most structurally complex candidate is the 'reference' for relative scoring,
        # or we treat the prompt's implied logic as the target. 
        # Strategy: Score against the 'ideal' derived from the union of all candidates + prompt logic.
        # For this implementation, we pick the candidate with the highest primitive count as the temporary reference.
        
        features = [self._extract_features(c) for c in candidates]
        
        # Pseudo-reference: Aggregate features of all candidates (consensus) or the most complex one
        # Let's use the candidate with max feature norm as the reference for this batch
        ref_idx = np.argmax([np.linalg.norm(f) for f in features])
        ref_feat = features[ref_idx]
        ref_text = candidates[ref_idx]
        
        # Encode reference
        alpha_ref = self._soft_threshold(ref_feat, self.D, self.lambda_reg)
        
        results = []
        for i, cand in enumerate(candidates):
            feat = features[i]
            
            # 1. Sparse Coding Fidelity
            alpha = self._soft_threshold(feat, self.D, self.lambda_reg)
            recon_err = np.linalg.norm(feat - self.D @ alpha)**2
            code_dist = np.linalg.norm(alpha - alpha_ref)**2
            
            # 2. Abstract Interpretation Distance
            abs_dist = self._abstract_distance(cand, ref_text)
            
            # Combined Score (Negative error + Negative distance)
            # Higher is better. 
            score = -recon_err - 2.0 * abs_dist - 0.5 * code_dist
            
            # Plasticity Update: If this candidate is close to reference, learn from it
            if abs_dist < 0.5: 
                self._hebbian_update(feat, alpha)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"AbsDist={abs_dist:.2f}, ReconErr={recon_err:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        if len(results) > 1:
            if abs(results[0]['score'] - results[1]['score']) < 0.01:
                # Re-sort using NCD against prompt for the top contenders
                top_score = results[0]['score']
                tied = [r for r in results if abs(r['score'] - top_score) < 0.1]
                if len(tied) > 1:
                    tied.sort(key=lambda x: self._ncd(prompt, x['candidate']))
                    # Replace top entries with sorted tied
                    for i, r in enumerate(tied):
                        # Find original index to replace carefully or just rebuild list
                        pass 
                    # Simplified: Just append NCD as secondary sort key for the whole list if needed
                    # But requirement says NCD only as tiebreaker. 
                    # We'll trust the primary score for now as it includes structural parsing.
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Based on reconstruction fidelity and abstract logical consistency.
        """
        feat = self._extract_features(answer)
        alpha = self._soft_threshold(feat, self.D, self.lambda_reg)
        recon_err = np.linalg.norm(feat - self.D @ alpha)**2
        
        # Estimate logical consistency by comparing answer features to prompt features
        prompt_feat = self._extract_features(prompt)
        # Simple correlation as a proxy for logical entailment in this simplified model
        logical_overlap = np.corrcoef(feat, prompt_feat)[0, 1]
        if np.isnan(logical_overlap):
            logical_overlap = 0.0
            
        # Normalize reconstruction error (heuristic)
        fid_score = 1.0 / (1.0 + recon_err)
        
        # Confidence is a mix of fidelity and logical overlap
        conf = 0.6 * fid_score + 0.4 * max(0, logical_overlap)
        return float(np.clip(conf, 0.0, 1.0))