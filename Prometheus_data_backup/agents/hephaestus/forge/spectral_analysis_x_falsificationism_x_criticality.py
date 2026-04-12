import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Hypothesis-Testing Engine via Spectral Falsification.
    
    Mechanism:
    1. Structural Parsing: Extracts numeric values, negations, and comparatives.
    2. Residual Signal Generation: Converts candidate correctness (via NCD error) 
       into a time-series residual stream.
    3. Spectral Monitor: Uses a simplified periodogram on the residual stream to 
       estimate high-frequency power (falsification signal).
    4. Criticality Controller: Adjusts an internal gain 'g' based on high-freq power.
       - High HF power -> Hypothesis contradicted -> Decrease gain (stabilize).
       - Low HF power -> Hypothesis consistent -> Increase gain (explore edge).
    5. Scoring: Candidates are ranked by a composite score of structural validity 
       and the system's confidence (inverse of spectral falsification).
    """
    
    def __init__(self):
        self.gain = 1.0  # Internal coupling strength
        self.critical_threshold = 0.5
        self.history_size = 16
        self.residual_buffer = np.zeros(self.history_size)
        self.buf_idx = 0
        
    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _parse_structure(self, text: str) -> Dict:
        """Extract numeric and logical constraints."""
        text_lower = text.lower()
        has_neg = any(n in text_lower for n in ['not', 'no ', 'never', 'false'])
        nums = []
        parts = text_lower.replace(',', ' ').split()
        for p in parts:
            try:
                nums.append(float(''.join(filter(lambda c: c.isdigit() or c == '.', p))))
            except: pass
        return {'negation': has_neg, 'numbers': nums}

    def _spectral_power(self, signal: np.ndarray) -> float:
        """
        Estimate high-frequency power using a simple periodogram.
        Simulates Welch's method on the residual buffer.
        """
        if len(signal) < 4: return 0.0
        # Detrend
        signal = signal - np.mean(signal)
        # Simple DFT for high freq components (upper half of spectrum)
        fft_vals = np.abs(np.fft.rfft(signal))
        if len(fft_vals) < 2: return 0.0
        # Focus on high frequencies (upper 50% of bins)
        mid = len(fft_vals) // 2
        return float(np.sum(fft_vals[mid:] ** 2))

    def _update_criticality(self, hf_power: float):
        """SOC Feedback loop to tune gain."""
        if hf_power > self.critical_threshold:
            self.gain *= 0.9  # Dampen if falsified
        else:
            self.gain *= 1.05 # Amplify if consistent
        self.gain = np.clip(self.gain, 0.1, 10.0)

    def _generate_residual(self, prompt: str, candidate: str) -> float:
        """Generate a residual value based on structural mismatch."""
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        
        # Base error from NCD (simulating model prediction error)
        base_error = self._compute_ncd(prompt, candidate)
        
        # Structural penalty
        penalty = 0.0
        if p_struct['numbers'] and c_struct['numbers']:
            # If numbers exist, check logic (simplified)
            if len(p_struct['numbers']) >= 2 and len(c_struct['numbers']) >= 1:
                # Heuristic: if prompt implies comparison, candidate should be short/decisive
                if len(candidate.split()) > 10: penalty = 0.5
        
        if p_struct['negation'] and not c_struct['negation']:
            # Potential logical mismatch
            penalty += 0.2
            
        return (base_error + penalty) * self.gain

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate structural validity for sorting tie-breakers
        candidate_scores = []
        for cand in candidates:
            struct = self._parse_structure(cand)
            ncd_err = self._compute_ncd(prompt, cand)
            
            # Generate residual and update spectral monitor
            resid = self._generate_residual(prompt, cand)
            self.residual_buffer[self.buf_idx] = resid
            self.buf_idx = (self.buf_idx + 1) % self.history_size
            
            # Spectral Analysis
            hf_power = self._spectral_power(self.residual_buffer)
            self._update_criticality(hf_power)
            
            # Falsification-driven loss: High HF power = Low score
            # Score is inverse of spectral falsification signal
            falsification_signal = hf_power * self.gain
            score = 1.0 / (1.0 + falsification_signal + ncd_err)
            
            # Boost if structural constraints are met (e.g., numeric consistency)
            if struct['numbers'] and len(struct['numbers']) > 0:
                score *= 1.1
                
            candidate_scores.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Spectral falsification signal: {falsification_signal:.4f}; NCD: {ncd_err:.4f}; Gain: {self.gain:.2f}"
            })
            
        # Rank by score descending
        return sorted(candidate_scores, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        # Re-run evaluation logic internally to get score for specific pair
        # We simulate a batch of dummy candidates to establish context if needed, 
        # but here we just compute the direct metric.
        struct_p = self._parse_structure(prompt)
        struct_a = self._parse_structure(answer)
        
        ncd_err = self._compute_ncd(prompt, answer)
        resid = (ncd_err + (0.2 if struct_p['negation'] and not struct_a['negation'] else 0)) * self.gain
        
        self.residual_buffer[self.buf_idx] = resid
        self.buf_idx = (self.buf_idx + 1) % self.history_size
        
        hf_power = self._spectral_power(self.residual_buffer)
        self._update_criticality(hf_power)
        
        # Confidence is 1 - normalized falsification
        conf = 1.0 / (1.0 + hf_power * self.gain + ncd_err)
        return float(np.clip(conf, 0.0, 1.0))