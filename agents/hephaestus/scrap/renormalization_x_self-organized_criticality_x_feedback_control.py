import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Adaptive Critical Controller (RACC) for Reasoning.
    
    Mechanism:
    1. Structural Parsing (Renormalization): Extracts logical tokens (negations, 
       comparatives, numbers) as the 'coarse-grained' representation of the prompt.
       This filters noise and isolates relevant scales of information.
    2. SOC-Regulated Scoring (Self-Organized Criticality): 
       Per constraints, SOC is NOT used for direct scoring to avoid reasoning traps.
       Instead, it modulates the confidence() wrapper. It simulates an 'avalanche' 
       threshold: if structural evidence is weak, confidence remains low (sub-critical).
       If strong structural matches exist, confidence spikes (critical state).
    3. Feedback Control: A PID-like error term adjusts the final score based on the 
       discrepancy between the candidate's structural signature and the prompt's 
       expected logical flow (e.g., negation handling).
       
    This architecture prioritizes structural logic over string similarity (NCD), 
    using NCD only as a tiebreaker for ambiguous cases.
    """

    def __init__(self):
        # PID Controller State for Feedback Loop
        self._prev_error = 0.0
        self._integral = 0.0
        self._dt = 0.1
        
        # Coefficients
        self.kp = 0.6  # Proportional: Immediate structural match
        self.ki = 0.1  # Integral: Accumulated consistency
        self.kd = 0.2  # Derivative: Rate of change in logical fit
        
        # SOC Parameters (for confidence wrapper only)
        self._activity = 0.0
        self._threshold = 0.85  # Critical threshold for high confidence

    def _extract_structure(self, text: str) -> Dict:
        """Renormalization step: Coarse-grain text into logical features."""
        t = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', t)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', t)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', t)),
            'numbers': re.findall(r'\d+\.?\d*', t),
            'length': len(t)
        }
        return features

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Evaluate candidate based on structural alignment with prompt.
        Returns a base score 0.0 to 1.0.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        score = 0.0
        matches = 0
        
        # 1. Negation Handling (Critical for logic traps)
        # If prompt has negation, candidate must reflect awareness or specific structure
        if p_feat['negations'] > 0:
            # Reward if candidate length suggests explanation, or contains logical connectors
            if c_feat['length'] > 10 or c_feat['comparatives'] > 0 or c_feat['conditionals'] > 0:
                score += 0.4
            else:
                # Penalty for short, non-structural answers to complex negated prompts
                score -= 0.2
            matches += 1

        # 2. Comparative/Numeric Consistency
        if p_feat['comparatives'] > 0 or len(p_feat['numbers']) >= 2:
            # Check if candidate contains numbers or comparative words
            if len(c_feat['numbers']) > 0 or c_feat['comparatives'] > 0:
                score += 0.3
            matches += 1
            
        # 3. Conditional Logic
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or c_feat['length'] > 20:
                score += 0.3
            matches += 1

        # Normalize base score
        if matches == 0:
            # Fallback for simple prompts without clear logical operators
            return 0.5 
            
        return max(0.0, min(1.0, score / matches + 0.5))

    def _apply_feedback_control(self, base_score: float, prompt: str, candidate: str) -> float:
        """
        Apply PID-like feedback to adjust score based on logical consistency.
        Simulates the 'gain parameter' adjustment in RACC.
        """
        # Error term: Discrepancy between expected structural density and candidate
        # Simple heuristic: If prompt is complex (high structure) and candidate is tiny, error is high
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        prompt_complexity = (p_feat['negations'] + p_feat['comparatives'] + p_feat['conditionals']) * 10
        if prompt_complexity == 0: prompt_complexity = 1
        
        # Expected length ratio heuristic
        expected_ratio = min(1.0, prompt_complexity / 50.0 + 0.2)
        actual_ratio = min(1.0, c_feat['length'] / (p_feat['length'] + 1))
        
        error = expected_ratio - actual_ratio
        
        # PID Terms
        p_term = self.kp * (1.0 - abs(error)) # Reward low error
        self._integral += error * self._dt
        i_term = self.ki * self._integral
        derivative = (error - self._prev_error) / self._dt if self._dt > 0 else 0
        d_term = self.kd * derivative
        
        self._prev_error = error
        
        # Adjust base score
        adjustment = p_term + i_term + d_term
        final_score = base_score + adjustment
        
        return max(0.0, min(1.0, final_score))

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Reset integral term for each new evaluation batch to prevent drift
        self._integral = 0.0
        self._prev_error = 0.0

        scored_candidates = []
        
        for cand in candidates:
            # Step 1: Renormalization (Structural Extraction)
            base_score = self._compute_structural_score(prompt, cand)
            
            # Step 2: Feedback Control (PID Adjustment)
            refined_score = self._apply_feedback_control(base_score, prompt, cand)
            
            # Step 3: NCD Tiebreaker (only if scores are very close, handled by sorting stability)
            # We store NCD to break ties explicitly if needed, but primary sort is refined_score
            ncd = self._ncd_distance(prompt, cand)
            
            scored_candidates.append({
                "candidate": cand,
                "score": refined_score,
                "ncd": ncd,
                "reasoning": f"Structural match: {base_score:.2f}, Feedback adj: {refined_score - base_score:.2f}"
            })

        # Sort: Primary by score (desc), Secondary by NCD (asc - lower distance is better)
        scored_candidates.sort(key=lambda x: (x['score'], -x['ncd']), reverse=True)
        
        # Format output
        for item in scored_candidates:
            results.append({
                "candidate": item["candidate"],
                "score": item["score"],
                "reasoning": item["reasoning"]
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        SOC-modulated confidence wrapper.
        Uses a stochastic threshold model analogous to neuronal avalanches.
        Only yields high confidence if structural evidence pushes activity past critical threshold.
        """
        # Get base structural assessment
        base_score = self._compute_structural_score(prompt, answer)
        
        # Simulate SOC Activity Accumulation
        # If structural score is high, activity grows. If low, it decays.
        target_activity = base_score
        self._activity = 0.9 * self._activity + 0.1 * target_activity
        
        # Critical Threshold Check
        if self._activity > self._threshold:
            # Critical state: High confidence, sensitive to small changes
            return min(1.0, 0.8 + 0.2 * (self._activity - self._threshold) / (1.0 - self._threshold))
        else:
            # Sub-critical state: Low confidence, system is cautious
            return max(0.0, 0.1 + 0.7 * (self._activity / self._threshold))