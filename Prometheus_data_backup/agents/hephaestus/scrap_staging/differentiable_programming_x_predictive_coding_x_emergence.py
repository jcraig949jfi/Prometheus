import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable Constraint-Propagation Network (DCPN) for logical reasoning.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (comparisons, negations, conditionals)
       from the prompt and candidates into a unified constraint graph.
    2. Differentiable Propagation: Encodes atoms as vectors and uses a soft-logic 
       weight matrix updated via gradient descent to minimize "surprise" (prediction error).
       This simulates predictive coding where the network settles into a consistent state.
    3. Emergent Scoring: The final score is derived from the residual error after convergence.
       Low error (high consistency with extracted rules) yields a high score.
    4. Fallback: Uses NCD only if structural features are absent.
    """
    
    def __init__(self):
        self.lr = 0.1
        self.steps = 20
        self.epsilon = 1e-6

    def _parse_text(self, text: str) -> Tuple[List[str], List[float], bool, List[Tuple[str, str]]]:
        """Extract comparatives, numbers, negations, and conditionals."""
        text_lower = text.lower()
        comps = []
        nums = []
        negated = False
        conds = []
        
        # Detect negation
        if re.search(r'\b(not|no|never|impossible|false)\b', text_lower):
            negated = True
            
        # Extract numbers
        nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        # Extract comparatives
        if any(w in text_lower for w in ['greater', 'larger', 'more', '>', 'exceeds']):
            comps.append('gt')
        if any(w in text_lower for w in ['less', 'smaller', 'fewer', '<', 'under']):
            comps.append('lt')
        if any(w in text_lower for w in ['equal', 'same', '==']):
            comps.append('eq')
            
        # Extract conditionals (simplified)
        if 'if' in text_lower and ('then' in text_lower or ',' in text):
            conds.append(('if', 'then'))
            
        return comps, nums, negated, conds

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2, 1)
        except:
            return 1.0

    def _run_dcpn(self, prompt: str, candidate: str) -> float:
        """Core differentiable constraint propagation logic."""
        full_text = f"{prompt} {candidate}"
        comps, nums, negated, conds = self._parse_text(full_text)
        p_comps, p_nums, p_neg, p_conds = self._parse_text(prompt)
        c_comps, c_nums, c_neg, c_conds = self._parse_text(candidate)
        
        # Feature vector construction (K=6: gt, lt, eq, num_present, neg, cond)
        def to_vec(comps, nums, neg, conds):
            v = np.zeros(6)
            if 'gt' in comps: v[0] = 1.0
            if 'lt' in comps: v[1] = 1.0
            if 'eq' in comps: v[2] = 1.0
            if nums: v[3] = 1.0
            if neg: v[4] = 1.0
            if conds: v[5] = 1.0
            return v

        S_prompt = to_vec(p_comps, p_nums, p_neg, p_conds)
        S_cand = to_vec(c_comps, c_nums, c_neg, c_conds)
        
        # If no structural features detected, rely on NCD
        if np.sum(S_prompt) == 0 and np.sum(S_cand) == 0:
            return 1.0 - self._compute_ncd(prompt, candidate)

        # Initialize State S (stacked) and Weight Matrix W
        S = np.stack([S_prompt, S_cand]).T # Shape: (6, 2)
        # Flatten for optimization: S_flat shape (12,)
        S_flat = S.flatten().astype(np.float64)
        
        # Initialize Weights (Identity + small noise for symmetry breaking)
        K = 6
        W = np.eye(K) * 0.5 + np.random.randn(K, K) * 0.01
        
        # Gradient Descent to minimize prediction error (Predictive Coding)
        # Target: Consistency between prompt constraints and candidate implications
        for _ in range(self.steps):
            S_mat = S_flat.reshape(K, 2)
            # Predict next state: S' = sigmoid(S @ W)
            pred = 1.0 / (1.0 + np.exp(-np.dot(S_mat, W)))
            
            # Error: Difference between actual and predicted (Surprise)
            # We want the candidate to be a logical continuation of the prompt
            error = S_mat - pred
            loss = np.sum(error ** 2)
            
            # Gradients
            # dL/dW approximated via chain rule through sigmoid derivative
            sigmoid_deriv = pred * (1 - pred)
            dW = np.dot(S_mat.T, error * sigmoid_deriv) 
            
            # Update Weights
            W -= self.lr * dW
            
            # Update State towards prediction (Relaxation)
            S_flat = (S_flat + pred.flatten()) / 2.0

        # Final Score: Inverse of residual error
        final_S = S_flat.reshape(K, 2)
        final_pred = 1.0 / (1.0 + np.exp(-np.dot(final_S, W)))
        residual = np.mean((final_S - final_pred) ** 2)
        
        # Normalize score: 1.0 is perfect consistency, 0.0 is chaos
        # Add small penalty for contradiction (e.g. prompt says GT, candidate says LT)
        contradiction = 0.0
        if p_comps and c_comps:
            if ('gt' in p_comps and 'lt' in c_comps) or ('lt' in p_comps and 'gt' in c_comps):
                contradiction = 0.5
        
        score = max(0.0, 1.0 - residual - contradiction)
        return float(score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        scores = []
        
        # Calculate scores
        for cand in candidates:
            struct_score = self._run_dcpn(prompt, cand)
            
            # Heuristic boost for numeric consistency if numbers exist
            p_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', prompt)]
            c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', cand)]
            
            bonus = 0.0
            if p_nums and c_nums:
                # Simple check: if prompt implies ordering, does candidate respect magnitude?
                # This is a rough proxy for logical consistency in numeric domains
                if 'less' in prompt.lower() and c_nums[0] < max(p_nums + [float('inf')]):
                    bonus = 0.1
                elif 'greater' in prompt.lower() and c_nums[0] > min(p_nums + [float('-inf')]):
                    bonus = 0.1
            
            final_score = min(1.0, struct_score + bonus)
            scores.append((cand, final_score))
        
        # Handle tie-breaking with NCD if scores are too close
        processed = []
        for i, (cand, score) in enumerate(scores):
            # Check for ties within epsilon
            is_tie = any(abs(score - s) < self.epsilon for j, s in enumerate(scores) if j != i)
            
            if is_tie and score > 0.5:
                # Use NCD as tiebreaker for high-scoring candidates
                ncd_val = self._compute_ncd(prompt, cand)
                # Adjust score slightly by NCD (lower NCD = higher similarity = better)
                score += (1.0 - ncd_val) * 0.01
            
            processed.append({"candidate": cand, "score": score, "reasoning": "DCPN convergence"})
        
        # Sort descending by score
        processed.sort(key=lambda x: x["score"], reverse=True)
        return processed

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence score for a single candidate."""
        res = self.evaluate(prompt, [answer])
        return res[0]["score"] if res else 0.0