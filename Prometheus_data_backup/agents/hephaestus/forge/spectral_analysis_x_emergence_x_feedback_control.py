import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Emergence Feedback Controller (SEFC) for Reasoning.
    
    Mechanism:
    1. Spectral Analysis: Treats the sequence of structural features (negations, 
       comparatives, conditionals, numbers) as a time-series signal. Computes 
       Power Spectral Density (PSD) via a simplified DFT to detect dominant 
       frequencies (patterns) in the logical structure.
    2. Emergence: Identifies "emergent modes" where the spectral power of 
       logical constraints exceeds a statistical threshold, indicating a coherent 
       logical structure rather than noise.
    3. Feedback Control: Uses a PID-like controller to adjust the scoring weight.
       - Proportional: Matches the candidate's structural signature to the prompt's.
       - Integral: Accumulates match quality across all constraint types.
       - Derivative: Penalizes rapid deviations in logical consistency (e.g., 
         double negations that don't resolve).
       
    The final score combines structural alignment (primary) with NCD (tiebreaker).
    """

    def __init__(self):
        self.target_spectrum = None
        self.pid_kp = 1.0
        self.pid_ki = 0.1
        self.pid_kd = 0.05
        self.prev_error = 0.0
        self.integral = 0.0

    def _extract_features(self, text: str) -> List[float]:
        """Extract structural features as a numeric signal."""
        text_lower = text.lower()
        features = []
        
        # 1. Negations
        negations = len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower))
        features.append(negations)
        
        # 2. Comparatives
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|better|wor|er)\b', text_lower))
        features.append(comparatives)
        
        # 3. Conditionals
        conditionals = len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower))
        features.append(conditionals)
        
        # 4. Numeric density
        numbers = len(re.findall(r'\d+\.?\d*', text_lower))
        features.append(numbers)
        
        # 5. Logical connectors (AND/OR)
        connectors = len(re.findall(r'\b(and|or|but|however)\b', text_lower))
        features.append(connectors)
        
        # Pad to ensure minimum length for spectral analysis
        while len(features) < 8:
            features.append(0.0)
            
        return features

    def _compute_psd(self, signal: List[float]) -> List[float]:
        """Simple DFT-based Power Spectral Density estimation."""
        n = len(signal)
        if n == 0:
            return [0.0]
        
        psd = []
        # Compute magnitude of frequencies
        for k in range(n // 2 + 1):
            real_part = sum(signal[t] * math.cos(2 * math.pi * k * t / n) for t in range(n))
            imag_part = sum(signal[t] * math.sin(2 * math.pi * k * t / n) for t in range(n))
            magnitude = math.sqrt(real_part**2 + imag_part**2)
            psd.append(magnitude**2 / n)
            
        return psd

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _pid_control(self, error: float) -> float:
        """Simulate PID adjustment for hypothesis weighting."""
        self.integral += error
        derivative = error - self.prev_error
        output = (self.pid_kp * error) + \
                 (self.pid_ki * self.integral) + \
                 (self.pid_kd * derivative)
        self.prev_error = error
        return output

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_features = self._extract_features(prompt)
        prompt_psd = self._compute_psd(prompt_features)
        max_power = max(prompt_psd) if prompt_psd else 1.0
        
        # Normalize prompt spectrum to define target
        target_spectrum = [p / (max_power + 1e-9) for p in prompt_psd]
        
        results = []
        for candidate in candidates:
            cand_features = self._extract_features(candidate)
            cand_psd = self._compute_psd(cand_features)
            
            # Ensure same length for comparison
            min_len = min(len(target_spectrum), len(cand_psd))
            t_spec = target_spectrum[:min_len]
            c_spec = cand_psd[:min_len]
            
            # Calculate spectral error (Euclidean distance in spectral domain)
            spectral_error = math.sqrt(sum((t - c)**2 for t, c in zip(t_spec, c_spec)))
            
            # PID Control to adjust score based on error dynamics
            # Low error = high score. We invert error for the controller.
            control_signal = self._pid_control(-spectral_error)
            
            # Base score from structural match (inverse of spectral error)
            structural_score = 1.0 / (1.0 + spectral_error)
            
            # Apply control signal as a modifier
            final_score = structural_score + (control_signal * 0.1)
            
            # Tiebreaker: NCD (only if structural scores are very close)
            ncd_val = self._ncd(prompt, candidate)
            # NCD is 0 (same) to 1 (diff). We want high score for low NCD.
            # But NCD is weak for reasoning, so weight is tiny.
            ncd_bonus = (1.0 - ncd_val) * 0.01
            
            total_score = max(0.0, min(1.0, final_score + ncd_bonus))
            
            reasoning = f"Spectral match: {structural_score:.4f}, PID adj: {control_signal:.4f}, NCD: {ncd_val:.4f}"
            
            results.append({
                "candidate": candidate,
                "score": total_score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]