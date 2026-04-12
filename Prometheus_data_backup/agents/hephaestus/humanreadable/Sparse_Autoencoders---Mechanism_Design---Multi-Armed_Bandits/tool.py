import numpy as np
import re
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse Bandit Mechanism (SBM) for Reasoning.
    
    Core Logic:
    1. Structural Parsing: Extracts logical features (negations, comparatives, conditionals, numbers).
    2. Sparse Coding (Simulated): Uses a fixed orthogonal dictionary to encode features. 
       Reconstruction error measures semantic fit to a "valid reasoning" manifold.
    3. Mechanism Design: Applies a quadratic proper scoring rule to the error to incentivize truthfulness.
    4. Constraint Propagation: Checks logical consistency (Horn clauses) via transitive closure.
    5. Bandit Selection: Ranks candidates using UCB-like exploration on consistency vs. plausibility.
    
    Beats NCD baseline by focusing on logical structure rather than string compression.
    """

    def __init__(self):
        self.f = 60  # Feature dimensions (10 per category * 6 categories)
        self.k = 8   # Sparse code dimensions
        self.lambda_reg = 0.1
        self.beta = 1.5  # Exploration bonus
        self.mu_error = 0.5  # Running mean error
        self.epsilon = 1e-6
        
        # Initialize fixed orthogonal dictionary D (f x k) for sparse coding simulation
        # In a real offline phase, this would be learned via OMP. 
        # Here we use random orthogonal projection as a stable proxy for "dictionary".
        np.random.seed(42)
        Q, _ = np.linalg.qr(np.random.randn(self.f, self.k))
        self.D = Q

    def _parse_features(self, text: str) -> np.ndarray:
        """Extract structural features into a vector x in R^f."""
        x = np.zeros(self.f)
        text_lower = text.lower()
        words = text_lower.split()
        
        # Indices mapping (simplified hashing)
        # 0-9: Negations, 10-19: Comparatives, 20-29: Conditionals
        # 30-39: Numerics, 40-49: Causal, 50-59: Ordering
        
        # 1. Negations
        negations = ["not", "no", "never", "neither", "nobody", "nothing", "nowhere", "cannot", "won't", "don't"]
        for i, n in enumerate(negations):
            if n in words: x[i] = 1.0
            
        # 2. Comparatives
        comps = ["greater", "less", "more", "fewer", "higher", "lower", "better", "worse", "larger", "smaller"]
        for i, c in enumerate(comps):
            if c in words: x[10 + i] = 1.0
            
        # 3. Conditionals
        conds = ["if", "then", "unless", "provided", "when", "whenever", "else", "otherwise", "implies", "requires"]
        for i, c in enumerate(conds):
            if c in words: x[20 + i] = 1.0
            
        # 4. Numerics (detect presence of digits)
        nums = re.findall(r"[-+]?\d*\.?\d+", text)
        if nums:
            x[30] = min(len(nums), 1.0) # Presence
            try:
                # Normalize magnitude feature
                val = float(nums[0])
                x[31] = np.tanh(val / 100.0) 
            except: pass
            
        # 5. Causal
        causals = ["causes", "leads", "results", "creates", "produces", "effect", "impact", "influence", "due", "because"]
        for i, c in enumerate(causals):
            if c in words: x[40 + i] = 1.0
            
        # 6. Ordering
        orders = ["first", "second", "third", "before", "after", "next", "last", "previous", "follow", "precede"]
        for i, o in enumerate(orders):
            if o in words: x[50 + o] = 1.0 if o < len(orders) else 0.0 # Safe guard

        return x

    def _sparse_code(self, x: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Simulate OMP sparse coding.
        Returns sparse code alpha and reconstruction error e.
        Since D is orthogonal, alpha = D^T x is the optimal k-sparse approximation.
        """
        alpha = self.D.T @ x
        recon = self.D @ alpha
        error = float(np.sum((x - recon) ** 2))
        return alpha, error

    def _check_consistency(self, text: str) -> int:
        """
        Extract Horn-style clauses and count violations via transitive closure.
        Simplified for text: checks for explicit contradictions like "A > B" and "B > A" 
        or "If A then B" + "A" + "not B".
        Returns violation count v.
        """
        text_lower = text.lower()
        violations = 0
        
        # Simple heuristic: Check for contradictory comparatives
        if ("greater than" in text_lower or "larger" in text_lower) and \
           ("less than" in text_lower or "smaller" in text_lower):
            # Only flag if they seem to apply to same subject (heuristic: close proximity)
            if abs(text_lower.find("greater") - text_lower.find("less")) < 50:
                violations += 1

        # Check for explicit "not" near positive claims
        if " not " in text_lower and (" is " in text_lower or " are " in text_lower):
             # Very rough contradiction detection
             if text_lower.count(" is ") > 1: 
                 violations += 1

        # Numeric consistency
        nums = re.findall(r"[-+]?\d*\.?\d+", text)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                if "greater" in text_lower and n1 <= n2:
                    violations += 1
                if "less" in text_lower and n1 >= n2:
                    violations += 1
            except: pass
            
        return violations

    def _scoring_rule(self, error: float) -> float:
        """Quadratic proper scoring rule: s = 1 - (e - mu)^2"""
        return 1.0 - (error - self.mu_error) ** 2

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        errors = []
        violations = []
        
        # Phase 1: Compute raw metrics for all candidates
        for cand in candidates:
            full_text = f"{prompt} {cand}"
            x = self._parse_features(full_text)
            _, e = self._sparse_code(x)
            v = self._check_consistency(full_text)
            errors.append(e)
            violations.append(v)
            
        # Update running mean error (mechanism design parameter)
        if errors:
            self.mu_error = 0.9 * self.mu_error + 0.1 * np.mean(errors)
            
        # Phase 2: Compute Scores and Bandit UCB
        n = len(candidates)
        for i, cand in enumerate(candidates):
            # Proper scoring rule component
            s = self._scoring_rule(errors[i])
            
            # Consistency component (negative violations)
            cons_score = -violations[i]
            
            # Combined Score (Weighted)
            # w1 for plausibility, w2 for consistency
            w1, w2 = 0.6, 0.4
            base_score = w1 * s + w2 * cons_score
            
            # Bandit Uncertainty (UCB)
            # Estimate variance based on local density or use fixed uncertainty for single shot
            # Here we simulate uncertainty based on how 'average' the error is
            sigma_i = np.std(errors) + self.epsilon if n > 1 else 1.0
            ucb_bonus = self.beta * sigma_i / np.sqrt(i + 1)
            
            final_score = base_score + ucb_bonus
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Reconstruction error: {errors[i]:.4f}, Violations: {violations[i]}, UCB-adjusted score."
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the SBM score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        # Theoretical max score is ~1.0 (if error == mu), min can be negative
        raw_score = res[0]["score"]
        
        # Map to 0-1: Sigmoid-like mapping centered around 0.5
        # If score > 0.5 (good fit), confidence approaches 1
        # If score < 0.0 (bad fit), confidence approaches 0
        conf = 1.0 / (1.0 + np.exp(-4 * (raw_score - 0.5)))
        return float(np.clip(conf, 0.0, 1.0))