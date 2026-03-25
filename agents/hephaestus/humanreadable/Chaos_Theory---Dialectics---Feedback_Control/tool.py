import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Chaotic Dialectical Adaptive Controller (CDAC) Implementation.
    
    Mechanism:
    1. Thesis (Hypothesis): Evaluates candidates based on structural logic 
       (negations, comparatives, numeric constraints) and semantic overlap.
    2. Antithesis (Chaos): Generates a chaotic perturbation signal using a 
       discrete Lorenz-like map seeded by the prompt length. This probes 
       candidate sensitivity to initial conditions (edge cases).
    3. Synthesis (Feedback): A PID-like controller adjusts the weight between 
       Thesis and Antithesis. The "error" is the variance between logical 
       consistency and chaotic divergence. 
    4. Lyapunov Tuning: If the system detects high divergence (chaos), it 
       dampens the antithesis (Derivative gain up). If stable, it allows 
       more exploration (Integral gain up).
       
    This creates a self-regulating scorer that favors logically consistent 
    answers while penalizing those that fail under chaotic perturbation 
    (simulating robustness testing).
    """

    def __init__(self):
        # PID State
        self.integral = 0.0
        self.prev_error = 0.0
        # Lorenz State (simplified discrete map for chaos)
        self.x, self.y, self.z = 0.1, 0.1, 0.1
        # Constants
        self.dt = 0.01
        self.rho = 28.0
        self.sigma = 10.0
        self.beta = 8.0 / 3.0

    def _lorenz_step(self) -> float:
        """Generate a chaotic value using discrete Lorenz system."""
        dx = self.sigma * (self.y - self.x) * self.dt
        dy = (self.x * (self.rho - self.z) - self.y) * self.dt
        dz = (self.x * self.y - self.beta * self.z) * self.dt
        self.x += dx
        self.y += dy
        self.z += dz
        # Normalize chaos signal to [-1, 1] approx
        return np.tanh(self.z / 10.0)

    def _extract_logic_features(self, text: str) -> Dict[str, float]:
        """Structural parsing: negations, comparatives, numbers."""
        t = text.lower()
        features = {}
        
        # Negation density
        negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        features['negation'] = sum(1 for n in negations if f" {n}" in f" {t}") / (len(t.split()) + 1)
        
        # Comparatives
        comps = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<']
        features['comparative'] = sum(1 for c in comps if c in t) / (len(t.split()) + 1)
        
        # Numeric presence
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", t)
        features['numeric'] = len(nums) > 0
        features['num_count'] = len(nums)
        
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def _thesis_score(self, prompt: str, candidate: str) -> float:
        """
        Thesis: Logical consistency and structural alignment.
        Scores based on constraint propagation and semantic overlap.
        """
        p_feat = self._extract_logic_features(prompt)
        c_feat = self._extract_logic_features(candidate)
        
        score = 0.0
        
        # 1. Numeric Consistency (Constraint Propagation)
        if p_feat['numeric'] and c_feat['numeric']:
            # If both have numbers, check if candidate numbers appear in prompt or are derived
            # Simple heuristic: overlap of numeric tokens implies relevance
            p_nums = set(re.findall(r"[-+]?\d*\.\d+|\d+", prompt.lower()))
            c_nums = set(re.findall(r"[-+]?\d*\.\d+|\d+", candidate.lower()))
            if p_nums & c_nums:
                score += 0.4
            # Penalty if candidate introduces random large numbers not in prompt
            elif c_nums and not p_nums:
                score -= 0.2
                
        # 2. Logical Negation Alignment
        # If prompt has high negation, candidate should reflect understanding (heuristic)
        if p_feat['negation'] > 0.05:
            # Reward candidates that also handle complexity (length/negation)
            if c_feat['negation'] > 0 or len(candidate) > len(prompt) * 0.5:
                score += 0.2
        
        # 3. Semantic Overlap (via NCD inverse)
        # Lower NCD = higher similarity. 
        ncd = self._compute_ncd(prompt, candidate)
        similarity = 1.0 - ncd
        score += similarity * 0.5
        
        return score

    def _antithesis_perturb(self, base_score: float, prompt: str, candidate: str) -> float:
        """
        Antithesis: Chaotic perturbation.
        Adds noise based on system state to test stability.
        """
        chaos = self._lorenz_step()
        # Perturb score: if chaos is high, push score away from extremes
        # This simulates probing sensitivity to initial conditions
        perturbation = chaos * 0.3 * (1.0 - abs(base_score)) 
        return base_score + perturbation

    def _synthesize(self, thesis: float, antithesis: float, prompt: str) -> Tuple[float, float]:
        """
        Synthesis: PID-controlled merging.
        Error = difference between logical thesis and chaotic antithesis.
        Adjusts weights to minimize instability.
        """
        target = 0.8 # Ideal high confidence
        error = thesis - antithesis
        
        # PID Terms
        self.integral += error * self.dt
        derivative = error - self.prev_error
        
        # Lyapunov-inspired Gain Tuning
        # If error magnitude is growing (chaos), increase D (dampen)
        if abs(error) > abs(self.prev_error) * 1.1:
            kp, ki, kd = 0.5, 0.1, 0.8 # High derivative to dampen
        else:
            kp, ki, kd = 0.6, 0.2, 0.1 # Standard convergence
            
        correction = kp * error + ki * self.integral + kd * derivative
        self.prev_error = error
        
        # Final synthesis
        final_score = thesis + correction
        return np.clip(final_score, 0.0, 1.0), abs(error)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        # Reset chaos state per prompt to ensure determinism per input
        self.x, self.y, self.z = 0.1, 0.1, 0.1
        self.integral = 0.0
        self.prev_error = 0.0
        
        # Pre-calculate prompt features to ensure consistency
        p_feat = self._extract_logic_features(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            # 1. Thesis Evaluation
            t_score = self._thesis_score(prompt, cand)
            
            # 2. Antithesis Perturbation
            a_score = self._antithesis_perturb(t_score, prompt, cand)
            
            # 3. Synthesis via PID
            final_score, instability = self._synthesize(t_score, a_score, prompt)
            
            # Reasoning string generation
            reasoning = f"Thesis:{t_score:.2f}|Chaos:{instability:.2f}"
            if p_feat['numeric'] and not self._extract_logic_features(cand)['numeric']:
                reasoning += "|Warning: Numeric mismatch"
            if len(cand) < len(prompt) * 0.1:
                reasoning += "|Warning: Too short"
                
            scored_candidates.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for single candidate
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0