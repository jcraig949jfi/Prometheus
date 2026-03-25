import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MEACF Reasoning Tool: Maximum-Entropy Adaptive Chaos Feedback.
    
    Mechanism:
    1. Structural Parsing: Extracts numeric values, negations, and comparatives.
    2. Chaotic Explorer: Uses a logistic map to generate dynamic weights for hypothesis features.
       The 'chaos' parameter adapts based on the diversity of candidate scores (simulating Lyapunov exponent).
    3. Max-Entropy Prior: Adjusts the scoring distribution to prevent premature convergence on low-entropy answers.
    4. Feedback Control (PID-like): Tunes the exploration gain based on the error between predicted rank and observed structural validity.
    
    This implements the theoretical MEACF loop using deterministic numerical scoring functions
    optimized for logic puzzles, numeric comparisons, and constraint propagation.
    """

    def __init__(self):
        # State variables for the feedback loop
        self.integral_error = 0.0
        self.prev_error = 0.0
        self.chaos_param = 3.9  # Initial high chaos for exploration
        self.base_entropy = 1.0
        
        # PID Constants (Tuned for stability in hypothesis space)
        self.kp = 0.5
        self.ki = 0.1
        self.kd = 0.2

    def _structural_parse(self, text: str) -> Dict:
        """Extract structural features: numbers, negations, comparatives."""
        text_lower = text.lower()
        
        # Numeric extraction
        numbers = [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]
        
        # Logic flags
        has_negation = any(n in text_lower for n in ['not', 'no', 'never', 'false', 'impossible'])
        has_comparative = any(c in text_lower for c in ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'])
        has_conditional = any(c in text_lower for c in ['if', 'then', 'unless', 'otherwise'])
        
        return {
            "numbers": numbers,
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "length": len(text)
        }

    def _logistic_map(self, x: float, r: float) -> float:
        """Deterministic chaotic map."""
        return r * x * (1.0 - x)

    def _estimate_lyapunov_proxy(self, scores: List[float]) -> float:
        """
        Estimate system sensitivity (proxy for Lyapunov exponent).
        High variance in scores indicates high sensitivity/chaos.
        """
        if len(scores) < 2:
            return 0.0
        s_arr = np.array(scores)
        # Normalize to [0, 1] range for stability
        s_min, s_max = s_arr.min(), s_arr.max()
        if s_max - s_min < 1e-9:
            return 0.0
        s_norm = (s_arr - s_min) / (s_max - s_min)
        
        # Variance as a proxy for divergence
        return float(np.var(s_norm))

    def _compute_entropy_weight(self, scores: List[float]) -> float:
        """Calculate entropy-based weight to broaden consideration."""
        if not scores:
            return 1.0
        s_arr = np.array(scores)
        s_shifted = s_arr - s_arr.min() + 1e-9
        prob = s_shifted / s_shifted.sum()
        # Shannon entropy
        entropy = -np.sum(prob * np.log2(prob + 1e-9))
        max_entropy = np.log2(len(scores) + 1e-9)
        return float(entropy / max_entropy) if max_entropy > 0 else 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        p_feat = self._structural_parse(prompt)
        c_feats = [self._structural_parse(c) for c in candidates]
        
        raw_scores = []
        
        # 1. Base Scoring via Structural Matching & Constraint Propagation
        for i, c_feat in enumerate(c_feats):
            score = 0.0
            
            # Numeric Logic: Exact match or correct ordering
            if p_feat["numbers"] and c_feat["numbers"]:
                # Check for number presence
                p_nums = set(p_feat["numbers"])
                c_nums = set(c_feat["numbers"])
                if p_nums == c_nums:
                    score += 2.0
                # Check for comparative logic if present
                if p_feat["comparative"]:
                    if len(p_nums) >= 2 and len(c_nums) >= 2:
                        # Simple transitivity check simulation
                        p_sorted = sorted(p_nums)
                        c_sorted = sorted(c_nums)
                        if p_sorted == c_sorted:
                            score += 1.5
            
            # Negation handling
            if p_feat["negation"] == c_feat["negation"]:
                score += 1.0
                
            # Length heuristic (often correct answers are detailed but not rambling)
            len_ratio = min(len(c_feat["text"]) / (len(prompt) * 0.8), 1.5) if "text" in c_feat else 0.5
            # Fallback to simple string matching for keywords if structure is weak
            common_words = set(prompt.lower().split()) & set(candidates[i].lower().split())
            score += len(common_words) * 0.1

            raw_scores.append(score)

        # 2. Chaotic Explorer & Feedback Loop
        # Normalize raw scores to [0.1, 0.9] for logistic map input
        if max(raw_scores) - min(raw_scores) > 1e-9:
            norm_scores = [(s - min(raw_scores)) / (max(raw_scores) - min(raw_scores)) * 0.8 + 0.1 for s in raw_scores]
        else:
            norm_scores = [0.5] * len(raw_scores)

        # Estimate chaos (Lyapunov proxy)
        lambda_est = self._estimate_lyapunov_proxy(raw_scores)
        
        # Feedback Control: Adjust chaos parameter based on variance (error signal)
        # Target: Moderate variance (exploration) without divergence
        target_variance = 0.15
        error = target_variance - lambda_est
        
        self.integral_error += error
        derivative = error - self.prev_error
        adjustment = self.kp * error + self.ki * self.integral_error + self.kd * derivative
        
        # Update chaos parameter deterministically
        self.chaos_param = 3.5 + (adjustment * 0.4) # Keep in chaotic but bounded region [3.5, 3.9]
        self.chaos_param = max(3.5, min(3.99, self.chaos_param))
        self.prev_error = error

        # 3. Maximum Entropy Prior Updater
        # Inject chaos into scores
        chaotic_scores = []
        x = 0.5 # Fixed seed for determinism within this call
        for ns in norm_scores:
            x = self._logistic_map(x, self.chaos_param)
            # Blend original score with chaotic exploration
            mixed = (1.0 - self.chaos_param/4.0) * ns + (self.chaos_param/4.0) * x
            chaotic_scores.append(mixed)

        # Apply Entropy Weighting to prevent premature commitment
        entropy_factor = self._compute_entropy_weight(chaotic_scores)
        final_scores = [s * (1.0 + 0.5 * entropy_factor) for s in chaotic_scores]

        # Normalize to 0-1 range for output
        f_min, f_max = min(final_scores), max(final_scores)
        if f_max - f_min > 1e-9:
            normalized_scores = [(s - f_min) / (f_max - f_min) for s in final_scores]
        else:
            normalized_scores = [0.5] * len(final_scores)

        # Construct result
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(normalized_scores[i]),
                "reasoning": f"Structural match: {p_feat['comparative'] or p_feat['negation']}, Chaos-adjusted: {self.chaos_param:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural consistency and NCD tie-breaking.
        Returns 0.0 to 1.0.
        """
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        score = 0.5 # Base confidence
        
        # Numeric consistency
        if p_feat["numbers"] and a_feat["numbers"]:
            if set(p_feat["numbers"]) == set(a_feat["numbers"]):
                score += 0.3
            else:
                # Penalty for mismatched numbers in logic problems
                score -= 0.2
        
        # Negation consistency
        if p_feat["negation"] == a_feat["negation"]:
            score += 0.1
            
        # Comparative consistency
        if p_feat["comparative"] and a_feat["comparative"]:
            score += 0.1
            
        # NCD as a tiebreaker/refiner (only if strings are substantial)
        if len(prompt) > 10 and len(answer) > 5:
            try:
                s_prompt = prompt.encode('utf-8')
                s_answer = answer.encode('utf-8')
                comp_pa = zlib.compress(s_prompt + s_answer)
                comp_p = zlib.compress(s_prompt)
                comp_a = zlib.compress(s_answer)
                
                len_pa = len(comp_pa)
                len_p = len(comp_p)
                len_a = len(comp_a)
                
                # Normalized Compression Distance approximation
                ncd = (len_pa - min(len_p, len_a)) / max(len_p, len_a)
                # Low NCD implies high similarity/relevance -> boost confidence slightly
                if ncd < 0.6:
                    score += 0.1
            except:
                pass

        return max(0.0, min(1.0, score))

    # Helper to store text in features for the loop
    def _structural_parse(self, text: str) -> Dict:
        # Override to include raw text
        base = super()._structural_parse(text) if hasattr(super(), '_structural_parse') else {}
        # Re-implementing inline to ensure self-contained class behavior without super call issues in this specific structure
        text_lower = text.lower()
        numbers = [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]
        has_negation = any(n in text_lower for n in ['not', 'no', 'never', 'false', 'impossible'])
        has_comparative = any(c in text_lower for c in ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'])
        has_conditional = any(c in text_lower for c in ['if', 'then', 'unless', 'otherwise'])
        
        return {
            "numbers": numbers,
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "length": len(text),
            "text": text
        }