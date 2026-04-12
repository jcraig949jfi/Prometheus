import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Predictive Coding x Active Inference x Free Energy Principle reasoning engine.
    
    Mechanism:
    1. Propositional Extraction: Parses text into atomic propositions with feature vectors 
       (negation, numeric value, causal/conditional flags).
    2. Graph Construction: Builds an incidence matrix A representing logical constraints 
       (implications, causality, ordering) derived from the prompt.
    3. Free Energy Minimization: For each candidate, constructs a belief vector x.
       - Prediction Error (epsilon): ||Ax - b||^2 (Constraint violation).
       - Complexity (C): ||x - prior||^2 (Deviation from ignorance).
       - Epistemic Gain (G): Information gain approximated by covariance reduction.
       - Score F = epsilon + lambda*C - eta*G.
    4. Ranking: Candidates are ranked by negative Free Energy (lower F is better).
    """

    def __init__(self):
        self.lambda_c = 0.1  # Complexity weight
        self.eta_g = 0.1     # Epistemic gain weight
        self.prior_mu = 0.5  # Ignorance prior
        self.sigma_sq = 1.0  # Prior variance

    def _extract_propositions(self, text: str) -> Tuple[List[str], List[dict], List[float]]:
        """Extracts atomic propositions, their features, and numeric values."""
        props = []
        features = []
        values = []
        
        # Split by common delimiters but keep structure
        segments = re.split(r'[,.;]', text)
        
        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue
            
            # Detect numeric value
            nums = re.findall(r"-?\d+\.?\d*", seg)
            val = float(nums[-1]) if nums else 0.0
            
            # Feature vector: [is_negated, is_comparative, is_conditional, is_causal, has_number]
            is_neg = 1 if re.search(r'\b(not|no|never|none)\b', seg.lower()) else 0
            is_comp = 1 if re.search(r'(>|<|greater|less|more|before|after)', seg.lower()) else 0
            is_cond = 1 if re.search(r'\b(if|then|unless)\b', seg.lower()) else 0
            is_caus = 1 if re.search(r'\b(because|causes|leads to|therefore)\b', seg.lower()) else 0
            has_num = 1 if nums else 0
            
            props.append(seg)
            features.append([is_neg, is_comp, is_cond, is_caus, has_num])
            values.append(val)
            
        return props, features, values

    def _build_constraints(self, prompt: str, props: List[str], features: List[list]) -> Tuple[np.ndarray, np.ndarray]:
        """Builds incidence matrix A and constraint vector b based on logical patterns."""
        n = len(props)
        if n == 0:
            return np.array([]), np.array([])
            
        constraints = []
        targets = []
        
        # Rule 1: Negation consistency (If "not A" exists, A should be false)
        # Simplified: If a proposition has negation flag, target is 0, else 1 (heuristic)
        for i, f in enumerate(features):
            # Self-consistency constraint: x_i should match implied truth from negation flag
            # If negated, we expect x_i ~ 0. If not, x_i ~ 1 (unless context says otherwise)
            # We encode this as: 1 * x_i = (1 - is_neg)
            constraints.append([0]*i + [1.0] + [0]*(n-i-1))
            targets.append(1.0 - f[0]) 
            
        # Rule 2: Conditional/Causal linking (If A then B -> x_A <= x_B approx)
        # Encode as: x_B - x_A >= 0  =>  -x_A + x_B >= 0
        for i in range(len(props) - 1):
            f_curr = features[i]
            f_next = features[i+1] if i+1 < len(features) else [0]*5
            
            if f_curr[2] == 1 or f_curr[3] == 1: # If current is conditional/causal
                # Link to next proposition
                row = [0.0] * n
                row[i] = -1.0
                if i+1 < n:
                    row[i+1] = 1.0
                constraints.append(row)
                targets.append(0.0) # Expect x_next - x_curr >= 0 (relaxed to =0 for squared error min)

        # Rule 3: Numeric ordering
        for i in range(len(props) - 1):
            v1, v2 = values[i], values[i+1]
            f_curr = features[i]
            if f_curr[4] == 1 and features[i+1][4] == 1: # Both have numbers
                if "greater" in props[i].lower() or ">" in props[i]:
                    if v1 > v2: # Consistent
                        row = [0.0]*n; row[i]=1; row[i+1]=-1
                        constraints.append(row); targets.append(1) 
        
        if not constraints:
            return np.eye(n), np.ones(n) * 0.5
            
        return np.array(constraints), np.array(targets)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Computes the Free Energy score for a candidate given the prompt."""
        full_text = f"{prompt} {candidate}"
        props, features, values = self._extract_propositions(full_text)
        n = len(props)
        
        if n == 0:
            return 100.0 # High energy for empty
            
        A, b = self._build_constraints(prompt, props, features)
        if A.size == 0:
            return 100.0

        m, n_cols = A.shape
        
        # Belief vector x: Initialize based on candidate alignment with prompt assertions
        # Heuristic: If candidate repeats prompt props, x -> 1, else 0.5
        x = np.full(n_cols, self.prior_mu)
        
        # Simple constraint satisfaction step (Gradient descent approximation for x)
        # Minimize ||Ax - b||^2
        try:
            # Pseudo-inverse solution for least squares as the "optimal" belief state
            x_opt, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
            # Clip to [0, 1]
            x_opt = np.clip(x_opt, 0, 1)
        except:
            x_opt = x

        # 1. Prediction Error (epsilon) = ||Ax - b||^2
        epsilon = np.linalg.norm(A @ x_opt - b) ** 2
        
        # 2. Complexity (C) = ||x - mu||^2
        complexity = np.linalg.norm(x_opt - self.prior_mu) ** 2
        
        # 3. Epistemic Gain (G) approx: Reduction in entropy
        # Prior cov Sigma0 = sigma^2 * I
        # Posterior cov Sigma1 = (sigma^-2 I + A^T A)^-1
        # Gain = 0.5 * (log|Sigma0| - log|Sigma1|) = 0.5 * log(|Sigma0|/|Sigma1|)
        # For diagonal approximation or small n:
        try:
            identity = np.eye(n_cols)
            sigma_inv = (1/self.sigma_sq) * identity
            post_prec = sigma_inv + A.T @ A
            # Use determinant for entropy change (volume of uncertainty)
            det_prior = self.sigma_sq ** n_cols
            det_post = np.linalg.det(np.linalg.inv(post_prec))
            # Avoid log(0) or negative det issues
            if det_post <= 0: det_post = 1e-6
            gain = 0.5 * (np.log(det_prior) - np.log(det_post))
        except:
            gain = 0.0

        # Free Energy F = epsilon + lambda*C - eta*G
        F = epsilon + self.lambda_c * complexity - self.eta_g * gain
        return F

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = -self._compute_free_energy(prompt, cand) # Lower F is better, so negate for ranking
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Free Energy minimized: {score:.4f}"
            })
        
        # Sort by score descending (higher score = lower free energy)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on normalized inverse free energy."""
        fe = self._compute_free_energy(prompt, answer)
        # Map free energy to [0, 1]. 
        # Assuming FE >= 0. Lower FE -> Higher Confidence.
        # Use sigmoid-like mapping: 1 / (1 + FE)
        conf = 1.0 / (1.0 + fe)
        return min(1.0, max(0.0, conf))