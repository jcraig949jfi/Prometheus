import re
import numpy as np
from typing import List, Dict

class ReasoningTool:
    """
    A reasoning tool combining Differentiable Programming, Nash Equilibrium, and Metamorphic Testing.
    
    Mechanism:
    1. Feature Extraction: Parses candidates for logical structures (negations, comparatives, 
       conditionals, numerics, causality, ordering) into binary vectors.
    2. Metamorphic Constraints: Defines linear constraints that valid logical structures should satisfy.
    3. Payoff Construction: Builds a skew-symmetric matrix where candidates are penalized for 
       violating metamorphic relations and rewarded for opponents' violations.
    4. Differentiable Nash Equilibrium: Uses projected gradient ascent on the simplex to find a 
       mixed strategy equilibrium, yielding a robust score for each candidate.
    """
    
    # Fixed regex patterns for feature extraction (k=6 features for brevity/determinism)
    PATTERNS = [
        re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),      # 0: Negation
        re.compile(r'\b(more|less|greater|smaller|better|worse|-er)\b', re.IGNORECASE), # 1: Comparative
        re.compile(r'\b(if|unless|then|else|provided)\b', re.IGNORECASE), # 2: Conditional
        re.compile(r'\d+(\.\d+)?%?', re.IGNORECASE),                   # 3: Numeric
        re.compile(r'\b(because|leads to|results in|causes)\b', re.IGNORECASE), # 4: Causal
        re.compile(r'\b(before|after|first|last|ranked|order)\b', re.IGNORECASE)  # 5: Ordering
    ]

    def __init__(self):
        self.k = len(self.PATTERNS)

    def _extract_features(self, text: str) -> np.ndarray:
        """Returns a binary feature vector for the given text."""
        features = np.zeros(self.k, dtype=float)
        text_lower = text.lower()
        for i, pattern in enumerate(self.PATTERNS):
            if pattern.search(text_lower):
                features[i] = 1.0
        return features

    def _compute_violation(self, f: np.ndarray) -> float:
        """
        Computes a simple metamorphic violation score.
        Logic: High complexity (many features) without numeric grounding or ordering 
        often indicates hallucination in reasoning tasks. 
        Constraint: If (Comparative OR Ordering) is present, Numeric or Causal should ideally be present.
        Violation = max(0, (Comparative + Ordering) - 2*(Numeric + Causal))
        """
        comp_ord = f[1] + f[5]
        ground = f[3] + f[4]
        # Linear constraint: 2*ground - (comp_ord) >= 0. If < 0, violation.
        violation = -(2.0 * ground - comp_ord)
        return max(0.0, violation)

    def _build_payoff_matrix(self, candidates: List[str]) -> np.ndarray:
        """Builds the skew-symmetric payoff matrix Pi."""
        n = len(candidates)
        if n == 0:
            return np.array([])
        if n == 1:
            return np.array([[0.0]])
        
        features = [self._extract_features(c) for c in candidates]
        violations = np.array([self._compute_violation(f) for f in features])
        
        # Payoff Pi_ij = 1 - lambda*violation_i + mu*violation_j
        # We use lambda=1.0, mu=0.5 to prioritize self-consistency while penalizing bad opponents
        lam, mu = 1.0, 0.5
        
        Pi = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    Pi[i, j] = 0.0
                else:
                    val = 1.0 - lam * violations[i] + mu * violations[j]
                    # Skew-symmetric adjustment for Nash stability in zero-sum context
                    # Actually, the prompt asks for skew-symmetric Pi where Pi = -Pi.T usually, 
                    # but the formula given is specific. We follow the formula strictly.
                    Pi[i, j] = val
        
        # To ensure strict skew-symmetry for standard Nash solvers (optional but robust):
        # Pi = 0.5 * (Pi - Pi.T) 
        # However, the prompt defines Pi explicitly. We stick to the prompt's definition 
        # but note that gradient ascent on p^T Pi p works for general matrices too.
        return Pi

    def _nash_equilibrium(self, Pi: np.ndarray, steps: int = 100, lr: float = 0.1) -> np.ndarray:
        """Projected Gradient Ascent to find approximate Nash Equilibrium mixed strategy."""
        n = Pi.shape[0]
        if n == 0:
            return np.array([])
        if n == 1:
            return np.array([1.0])
        
        # Initialize uniform strategy
        p = np.ones(n) / n
        
        for _ in range(steps):
            # Gradient of p^T Pi p w.r.t p is (Pi + Pi.T) @ p
            # Since we want to maximize payoff, we ascend.
            gradient = (Pi + Pi.T) @ p
            
            p = p + lr * gradient
            
            # Project onto simplex (simple clipping and normalization for approximation)
            p = np.clip(p, 0.0, None)
            if np.sum(p) == 0:
                p = np.ones(n) / n
            else:
                p = p / np.sum(p)
                
        return p

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Feature Extraction & 2. Payoff Construction
        Pi = self._build_payoff_matrix(candidates)
        
        # 3. Differentiable Nash Equilibrium
        if Pi.size == 0:
            return []
            
        scores = self._nash_equilibrium(Pi)
        
        # Fallback for single candidate or if NE fails
        if len(scores) == 1:
            scores = np.array([1.0])
            
        # Normalize scores to 0-1 range based on rank
        # Add small NCD tie-breaking if scores are too close
        final_results = []
        score_list = scores.tolist()
        
        # Simple normalization to ensure 0-1 range relative to the group
        min_s, max_s = min(score_list), max(score_list)
        if max_s - min_s > 1e-6:
            normalized_scores = [(s - min_s) / (max_s - min_s + 1e-9) for s in score_list]
        else:
            # If all equal, use NCD against prompt as tie breaker
            normalized_scores = []
            for c in candidates:
                ncd = self._ncd_score(prompt, c)
                # Lower NCD (more similar) is often better for simple QA, but we invert for score
                normalized_scores.append(1.0 - ncd) 

        for i, c in enumerate(candidates):
            final_results.append({
                "candidate": c,
                "score": float(normalized_scores[i]),
                "reasoning": f"NE Score derived from metamorphic constraint violations and equilibrium stability."
            })
            
        # Sort by score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural consistency and NCD tie-breaking."""
        # Use the same logic as evaluate but for a single candidate vs itself implicitly
        # We simulate a 2-candidate scenario: [answer, "False"] to gauge relative strength
        # Or simpler: Check violation directly.
        
        f = self._extract_features(answer)
        violation = self._compute_violation(f)
        
        # Base confidence inversely proportional to violation
        base_conf = 1.0 / (1.0 + violation)
        
        # Adjust with NCD to prompt (similarity often correlates with relevance in simple tasks)
        ncd = self._ncd_score(prompt, answer)
        
        # Weighted combination
        conf = 0.7 * base_conf + 0.3 * (1.0 - ncd)
        return float(np.clip(conf, 0.0, 1.0))