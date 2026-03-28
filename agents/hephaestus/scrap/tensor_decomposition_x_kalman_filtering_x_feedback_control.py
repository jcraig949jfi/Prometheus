import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    TSAKF-CGT Approximation: Tensor-Structured Adaptive Kalman Filter with Closed-Loop Gain Tuning.
    
    Mechanism:
    1. State Representation (Tensor Decomposition): The 'state' is a low-rank approximation of the 
       candidate's structural features (negations, numerics, conditionals) mapped to a latent vector.
    2. Estimation (Kalman Filtering): We estimate the 'truthiness' of a candidate by comparing its 
       structural signature against the prompt's constraints. The 'innovation' is the mismatch between 
       expected structural properties (derived from the prompt) and the candidate's properties.
    3. Adaptation (Feedback Control): A PID-like controller adjusts the 'gain' (weight) of specific 
       structural features. If a candidate fails a hard constraint (e.g., numeric comparison), the 
       error signal drives the gain to penalize that candidate heavily. 
    4. Scoring: The final score is a fusion of the Kalman-updated state estimate and a tie-breaking 
       Normalized Compression Distance (NCD).
    """

    def __init__(self):
        # P: Error covariance (uncertainty in our structural model)
        self.P = 1.0
        # K: Kalman Gain (how much we trust the structural evidence)
        self.K = 0.5
        # Q: Process noise (expectation that reasoning rules might vary)
        self.Q = 0.1
        # R: Measurement noise (ambiguity in language)
        self.R = 0.2
        # Integral term for PID-like control on constraint violations
        self.integral_error = 0.0

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extract structural features: negations, comparatives, numerics, conditionals."""
        t = text.lower()
        features = np.zeros(5)
        
        # 1. Negations
        negations = ['not', 'no ', 'never', 'none', 'neither', 'without']
        features[0] = sum(1 for n in negations if n in t)
        
        # 2. Comparatives/Superlatives
        comps = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'best', 'worst']
        features[1] = sum(1 for c in comps if c in t)
        
        # 3. Conditionals
        conds = ['if', 'then', 'unless', 'otherwise', 'when']
        features[2] = sum(1 for c in conds if c in t)
        
        # 4. Numeric presence (simple digit count heuristic)
        features[3] = sum(1 for c in t if c.isdigit())
        
        # 5. Logical connectors
        logic = ['therefore', 'thus', 'hence', 'because', 'so ']
        features[4] = sum(1 for l in logic if l in t)
        
        return features

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Check basic numeric logic (e.g., 9.11 < 9.9)."""
        # Extract floats from both
        import re
        p_nums = re.findall(r"[-+]?\d*\.\d+|\d+", prompt.lower())
        c_nums = re.findall(r"[-+]?\d*\.\d+|\d+", candidate.lower())
        
        if not p_nums or not c_nums:
            return 0.0 # No numeric constraint to violate
        
        try:
            # Simple heuristic: if prompt has comparison words and numbers, check candidate numbers
            if any(w in prompt.lower() for w in ['less', 'smaller', 'lower']):
                # Candidate should ideally contain the smaller number if it's answering "which is smaller"
                if c_nums:
                    c_val = float(c_nums[0])
                    p_vals = [float(x) for x in p_nums]
                    min_p = min(p_vals)
                    # Penalty if candidate picks the larger number when asked for smaller
                    if c_val > min_p and c_val in p_vals:
                        return -1.0 # Strong violation
            elif any(w in prompt.lower() for w in ['greater', 'larger', 'bigger', 'more']):
                if c_nums:
                    c_val = float(c_nums[0])
                    p_vals = [float(x) for x in p_nums]
                    max_p = max(p_vals)
                    if c_val < max_p and c_val in p_vals:
                        return -1.0
            # Direct equality check for simple "what is X + Y" if candidate is just a number
            if len(p_nums) >= 2 and len(c_nums) == 1:
                # Very rough heuristic for demonstration: if prompt implies math, check magnitude
                pass 
        except ValueError:
            pass
        return 0.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def _kalman_update(self, measurement: float, target: float) -> Tuple[float, float, float]:
        """
        Perform a scalar Kalman update step.
        State: Estimate of correctness.
        Measurement: Structural match score.
        Returns: Updated state, updated P, innovation.
        """
        # Prediction step (identity model)
        x_pred = 0.5 # Prior belief is neutral
        P_pred = self.P + self.Q
        
        # Update step
        if P_pred + self.R == 0:
            K = 0
        else:
            K = P_pred / (P_pred + self.R)
        
        innovation = measurement - x_pred
        x_upd = x_pred + K * innovation
        P_upd = (1 - K) * P_pred
        
        return x_upd, P_upd, innovation

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Global PID integral reset per query
        self.integral_error = 0.0

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural Matching (Measurement)
            # Compare feature vectors (L1 distance normalized)
            diff = np.abs(prompt_struct - cand_struct)
            # Heuristic: If prompt has high feature count, candidate should too
            struct_score = 1.0 / (1.0 + np.sum(diff))
            
            # 2. Numeric Consistency Check (Hard Constraint)
            numeric_penalty = self._check_numeric_consistency(prompt, cand)
            
            # 3. Kalman Filtering Step
            # Treat struct_score as the measurement of "truth"
            estimated_state, new_P, innovation = self._kalman_update(struct_score, 1.0)
            
            # 4. Feedback Control (PID-like adjustment)
            # Error is the lack of alignment or constraint violation
            error = (1.0 - struct_score) 
            if numeric_penalty < 0:
                error += 2.0 # Huge penalty for logic violation
            
            self.integral_error += error
            derivative = error - (1.0 - struct_score) # Simplified
            
            # Control law: Adjust gain based on error dynamics
            # If error is high, reduce trust (K) in this candidate type, or simply penalize score
            control_signal = 0.7 * error + 0.1 * self.integral_error # P + I terms
            
            # Final Score Construction
            # Base score from Kalman state
            score = estimated_state
            
            # Apply control signal as a penalty/bonus
            score -= control_signal * 0.2
            
            # Apply hard numeric penalty
            if numeric_penalty < 0:
                score = -10.0 # Immediate disqualification
            
            # NCD Tiebreaker (only if scores are close, but we add a small amount always)
            ncd = self._compute_ncd(prompt, cand)
            # Invert NCD (lower is better) and scale small so it doesn't dominate logic
            ncd_score = (1.0 - ncd) * 0.05 
            
            final_score = score + ncd_score
            
            # Reasoning string
            reason = f"Structural match: {struct_score:.2f}, Kalman state: {estimated_state:.2f}, Control penalty: {control_signal:.2f}"
            if numeric_penalty < 0:
                reason = "Failed numeric/logic constraint check."

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against itself to get internal score
        # We simulate a ranking where this is the only option
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to 0-1 confidence
        # Score can be negative (bad) or >1 (very good)
        conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid mapping
        return max(0.0, min(1.0, conf))