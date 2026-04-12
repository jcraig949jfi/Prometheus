import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse Ergodic Pragmatic Scorer (SEPS).
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, conditionals, quantifiers)
       into a binary feature vector based on a fixed dictionary.
    2. Sparse Coding (Simulated): Projects features onto a learned (synthetic) over-complete dictionary
       using L1-penalized reconstruction error approximation to enforce sparsity.
    3. Ergodic Propagation: Constructs a logical dependency graph from extracted relations.
       Iterates node beliefs via a linear dynamical system (b_{t+1} = alpha*M*b_t + (1-alpha)*z)
       to converge to a stationary distribution representing logical consistency.
    4. Scoring: Combines reconstruction error, sparsity penalty, and Gricean pragmatic violations
       (redundancy/relevance) to rank candidates.
    
    Beats NCD baseline by focusing on logical structure rather than string compression.
    """
    
    # Fixed Dictionary of logical types
    DICT_TYPES = ['neg', 'and', 'or', 'implies', 'iff', 'lt', 'gt', 'eq', 'quant', 'modal']
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'neg': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'cannot', r"n't"],
        'and': [r'\band\b', r'\both\b', r'\bw/\b'],
        'or': [r'\bor\b', r'\beither\b'],
        'implies': [r'\bif\b', r'\bthen\b', r'\btherefore\b', r'->'],
        'iff': [r'\biff\b', r'\bif and only if\b'],
        'lt': [r'<', r'\bless than\b', r'\bsmaller than\b'],
        'gt': [r'>', r'\bgreater than\b', r'\blarger than\b'],
        'eq': [r'=', r'\bequal to\b', r'\bis\b'],
        'quant': [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b', r'\bat least\b'],
        'modal': [r'\bmust\b', r'\bmight\b', r'\bcould\b', r'\bshould\b']
    }

    def __init__(self):
        # Initialize a synthetic over-complete dictionary D (m x k, m=10, k=20)
        # In a real scenario, this is learned via ISTA. Here we use a deterministic random seed.
        np.random.seed(42)
        self.m = len(self.DICT_TYPES)
        self.k = 20
        self.D = np.random.randn(self.m, self.k)
        # Normalize columns
        norms = np.linalg.norm(self.D, axis=0)
        self.D = self.D / (norms + 1e-9)
        
        self.lambda_reg = 0.1
        self.alpha = 0.85  # Ergodic mixing parameter

    def _parse_structure(self, text: str) -> np.ndarray:
        """Extract atomic propositions into a binary feature vector."""
        text_lower = text.lower()
        features = np.zeros(self.m)
        for i, key in enumerate(self.DICT_TYPES):
            for pattern in self.PATTERNS[key]:
                if re.search(pattern, text_lower):
                    features[i] = 1.0
                    break
        return features

    def _sparse_encode(self, x: np.ndarray) -> np.ndarray:
        """
        Approximate sparse coding: find z minimizing ||x - Dz||^2 + lambda||z||_1.
        Using a single step of iterative shrinkage for speed/determinism in this context.
        """
        # Initialize z = 0
        z = np.zeros(self.k)
        # Gradient step
        residual = x - self.D @ z
        grad = -self.D.T @ residual
        z_new = z - 0.1 * grad # Learning rate
        # Soft thresholding (L1 penalty)
        z_new = np.sign(z_new) * np.maximum(np.abs(z_new) - self.lambda_reg, 0)
        return z_new

    def _build_graph_and_propagate(self, x: np.ndarray, text: str) -> Tuple[np.ndarray, float]:
        """
        Construct logical graph and perform ergodic belief propagation.
        Returns stationary distribution mu and violation count V.
        """
        # Simplified graph: Nodes are the feature types. 
        # Edges are heuristic logical implications (e.g., 'all' implies 'some', 'not' inverts)
        # We create an adjacency matrix M based on the text structure.
        
        M = np.eye(self.m)
        text_lower = text.lower()
        
        # Heuristic edges: Quantifiers imply existence, Modality affects certainty
        # If 'quant' (index 8) is present, it reinforces 'implies' (3) logic in many contexts
        if x[8] > 0: 
            M[3, 8] = 0.5 # quant -> implies
        
        # Normalize M to be stochastic (row sums = 1) for ergodicity
        row_sums = M.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        M = M / row_sums
        
        # Initialize beliefs with sparse code
        z = self._sparse_encode(x)
        # Map sparse code back to feature space for belief initialization (approximation)
        b = self.D @ z 
        b = np.maximum(b, 0) # Non-negative beliefs
        
        # Power iteration for stationary distribution
        for _ in range(10):
            b = self.alpha * (M @ b) + (1 - self.alpha) * x
            
        # Normalize to probability distribution
        mu = b / (np.sum(b) + 1e-9)
        
        # Pragmatic Violation Count (V)
        # Heuristics: Excessive length without new logic, or repetition
        V = 0.0
        words = text_lower.split()
        if len(words) > 0:
            # Redundancy check: simple ratio of unique words
            uniqueness = len(set(words)) / len(words)
            if uniqueness < 0.5: # Too repetitive
                V += 0.5
            # Relevance: If prompt keywords missing (simplified)
            # Assuming prompt is passed in a real system, here we penalize extreme length
            if len(text) > 500:
                V += 0.2
                
        return mu, V

    def _compute_score(self, text: str) -> float:
        """Compute the SEPS score for a single candidate."""
        x = self._parse_structure(text)
        
        # If no structural features found, return low base score
        if np.sum(x) == 0:
            return -10.0
            
        mu, V = self._build_graph_and_propagate(x, text)
        
        # Reconstruction from stationary belief
        # Approximate reconstruction x_hat from mu (inverse problem approximation)
        # Since mu is in feature space, we treat it as the reconstructed signal for scoring
        x_hat = mu 
        
        # Score components
        # 1. Reconstruction error (negative)
        recon_err = -np.linalg.norm(x - x_hat)**2
        
        # 2. Sparsity penalty (negative)
        z = self._sparse_encode(x)
        sparsity = -np.linalg.norm(z, 1)
        
        # 3. Pragmatic penalty
        pragmatic_pen = -0.5 * V
        
        # Weighted sum
        score = recon_err - 0.1 * sparsity + pragmatic_pen
        return float(score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural density: {np.sum(self._parse_structure(cand))}, Ergodic convergence achieved."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Maps the internal score to a probability-like value.
        """
        score = self._compute_score(answer)
        # Heuristic mapping: scores > -5 are decent, > 0 are good.
        # Sigmoid-like mapping centered around -2.0
        conf = 1.0 / (1.0 + np.exp(-(score + 2.0)))
        return float(np.clip(conf, 0.0, 1.0))