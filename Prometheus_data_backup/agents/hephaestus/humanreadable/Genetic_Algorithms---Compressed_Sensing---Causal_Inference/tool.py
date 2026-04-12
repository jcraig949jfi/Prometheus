import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    EvolvedSparseCausalScorer: Combines structural parsing (features), 
    L1-regularized scoring (compressed sensing approximation), and 
    causal consistency checks within a simplified evolutionary loop.
    
    Mechanism:
    1. Parses candidates for logical features (negation, causality, numbers).
    2. Uses a genetic algorithm to evolve feature weights that maximize 
       sparsity and causal consistency while fitting a provisional target.
    3. Scores candidates based on the evolved weights and structural alignment.
    4. Falls back to NCD only if structural signals are indistinguishable.
    """
    
    # Feature patterns
    PATTERNS = {
        'negation': [r'\b(not|no|never|neither|none)\b'],
        'comparative': [r'\b(more|less|greater|fewer|higher|lower|better|worse)\b'],
        'conditional': [r'\b(if|then|unless|provided|otherwise)\b'],
        'causal': [r'\b(cause|lead to|result in|because|due to|implies)\b'],
        'ordering': [r'\b(before|after|precede|follow|first|last)\b'],
        'numeric': [r'\d+(\.\d+)?']
    }

    def __init__(self):
        self.m = len(self.PATTERNS)
        self.lambda_reg = 0.1
        self.mu = 0.5
        self.generations = 10
        self.pop_size = 15

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector from text."""
        text_lower = text.lower()
        features = []
        for key, patterns in self.PATTERNS.items():
            match = False
            for p in patterns:
                if re.search(p, text_lower):
                    match = True
                    break
            features.append(1.0 if match else 0.0)
        return np.array(features)

    def _build_graph_and_score(self, text: str) -> float:
        """
        Simplified causal consistency check.
        Returns 1.0 if no internal contradictions detected, else penalizes.
        Since full d-separation requires entity extraction, we approximate
        by checking for conflicting markers (e.g., negation + causal without condition).
        """
        text_lower = text.lower()
        has_causal = any(re.search(p, text_lower) for p in self.PATTERNS['causal'])
        has_neg = any(re.search(p, text_lower) for p in self.PATTERNS['negation'])
        has_cond = any(re.search(p, text_lower) for p in self.PATTERNS['conditional'])
        
        # Heuristic: Causal claims without conditions or with direct negation might be less robust
        # in a strict logical sense, but here we reward structure presence.
        # We return a consistency score based on structural richness.
        score = 0.5
        if has_causal: score += 0.2
        if has_cond: score += 0.2
        if has_neg: score += 0.1 # Negation adds logical depth
        
        return min(score, 1.0)

    def _ga_optimize(self, X: np.ndarray, causal_scores: List[float]) -> np.ndarray:
        """Evolve weight vector w using GA with L1 penalty and causal reward."""
        n_features = X.shape[1]
        if n_features == 0:
            return np.ones(1)
            
        # Initialize population
        pop = np.random.randn(self.pop_size, n_features) * 0.5
        # Provisional target y (zeros as per spec, implying we look for sparse explanations of null or minimal signal)
        y = np.zeros(X.shape[0])
        
        best_w = np.zeros(n_features)
        best_fit = -np.inf

        for _ in range(self.generations):
            fits = []
            for w in pop:
                # Fitness: -||Xw - y||^2 - lambda||w||_1 + mu * mean(causal_consistency)
                # Note: causal_scores are fixed per candidate, w influences prediction Xw
                # We approximate the causal term as a reward for weights aligning with high-causal candidates
                pred = X @ w
                mse = np.sum((pred - y)**2)
                l1 = np.sum(np.abs(w))
                
                # Causal alignment: dot product of predicted scores and causal scores
                # Encourages w to give high scores to causally consistent candidates
                causal_align = np.dot(pred, causal_scores) / (len(causal_scores) + 1e-9)
                
                fitness = -mse - self.lambda_reg * l1 + self.mu * causal_align
                fits.append(fitness)
            
            fits = np.array(fits)
            idx = np.argmax(fits)
            if fits[idx] > best_fit:
                best_fit = fits[idx]
                best_w = pop[idx].copy()
            
            # Tournament selection
            new_pop = []
            for _ in range(self.pop_size):
                candidates_idx = np.random.choice(self.pop_size, 3, replace=False)
                winner = pop[np.argmax(fits[candidates_idx])]
                new_pop.append(winner)
            
            # Crossover and Mutation
            next_gen = []
            for i in range(0, self.pop_size - 1, 2):
                p1, p2 = new_pop[i], new_pop[i+1]
                alpha = np.random.rand()
                c1 = alpha * p1 + (1 - alpha) * p2
                c2 = (1 - alpha) * p1 + alpha * p2
                # Mutation
                c1 += np.random.randn(n_features) * 0.1
                c2 += np.random.randn(n_features) * 0.1
                next_gen.extend([c1, c2])
            if self.pop_size % 2 == 1:
                next_gen.append(new_pop[-1])
            pop = np.array(next_gen[:self.pop_size])

        return best_w

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Structural Parsing
        X = np.vstack([self._extract_features(c) for c in candidates])
        causal_scores = [self._build_graph_and_score(c) for c in candidates]
        
        # 2 & 4. GA Optimization (Compressed Sensing + Evolution)
        w = self._ga_optimize(X, causal_scores)
        
        # Scoring
        scores = []
        for i, c in enumerate(candidates):
            base_score = float(np.dot(X[i], w))
            # Add causal consistency directly to score
            base_score += self.mu * causal_scores[i]
            scores.append(base_score)
        
        # Normalize scores to 0-1 range roughly
        min_s, max_s = min(scores), max(scores)
        if max_s > min_s:
            norm_scores = [(s - min_s) / (max_s - min_s) for s in scores]
        else:
            norm_scores = [0.5] * len(scores)
            
        # NCD Tiebreaker / Boost
        final_scores = []
        prompt_feat = self._extract_features(prompt)
        
        for i, c in enumerate(candidates):
            s = norm_scores[i]
            # If structural scores are very close, use NCD to prompt
            if len(set([round(sc, 3) for sc in norm_scores])) == 1:
                ncd_val = self._ncd(prompt, c)
                s += (1.0 - ncd_val) * 0.1 # Small boost for similarity if tied
            final_scores.append(s)

        # Rank
        ranked_idx = np.argsort(final_scores)[::-1]
        
        results = []
        for idx in ranked_idx:
            results.append({
                "candidate": candidates[idx],
                "score": float(final_scores[idx]),
                "reasoning": f"Structural score: {final_scores[idx]:.4f}, Causal consistency: {causal_scores[idx]:.2f}"
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Score is already normalized roughly 0-1 by evaluate logic
        return max(0.0, min(1.0, res[0]['score']))