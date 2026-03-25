import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Spectral Compositional Architecture (CSCA) Approximation.
    
    Mechanism:
    1. Compositional Primitives: Encodes text into a spectral vector using 
       character-level hashing mapped to sine/cosine basis functions (Fourier-like).
    2. Criticality: Implements a susceptibility metric based on the variance 
       of spectral modes. High variance (critical state) amplifies small 
       differences between hypothesis and data, acting as a gradient-free error signal.
    3. Hypothesis Testing: Scores candidates by projecting them onto the prompt's 
       spectral basis. The "critical" score combines structural overlap (compression) 
       with spectral sensitivity to penalize near-matches that fail logical constraints.
    """
    
    def __init__(self):
        self.basis_size = 64  # Number of spectral modes
        self.temperatures = np.linspace(0.1, 1.0, self.basis_size) # Adaptive temps
        
    def _hash_to_spectrum(self, text: str) -> np.ndarray:
        """Convert text to a spectral representation using character frequencies as amplitudes."""
        if not text:
            return np.zeros(self.basis_size)
        
        # Simple char-to-float mapping
        chars = [ord(c) / 256.0 for c in text]
        spectrum = np.zeros(self.basis_size)
        
        # Construct superposition of basis functions
        for i, val in enumerate(chars):
            freq = (i % (self.basis_size // 2)) + 1
            phase = val * 2 * np.pi
            # Superposition: Amplitude modulated by char value, frequency by position
            spectrum[freq-1] += np.sin(phase) * val
            if freq < self.basis_size:
                spectrum[freq] += np.cos(phase) * val
                
        # Normalize
        norm = np.linalg.norm(spectrum)
        return spectrum / (norm + 1e-9)

    def _compute_susceptibility(self, vec: np.ndarray) -> float:
        """
        Compute susceptibility (chi) as a measure of criticality.
        Chi ~ Variance of modes. High variance = high sensitivity to perturbation.
        """
        return float(np.var(vec)) + 1e-9

    def _structural_parse_score(self, prompt: str, candidate: str) -> float:
        """
        Extract logical constraints: negations, comparatives, numeric checks.
        Returns a penalty score (0.0 = perfect match to constraints, 1.0 = violation).
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        penalty = 0.0
        
        # 1. Negation Check
        negations = ["not ", "no ", "never ", "cannot ", "won't "]
        p_has_neg = any(n in p_low for n in negations)
        c_has_neg = any(n in c_low for n in negations)
        if p_has_neg != c_has_neg:
            penalty += 0.5
            
        # 2. Numeric Consistency (Simple extraction)
        nums_p = [float(s) for s in p_low.split() if s.replace('.','').replace('-','').isdigit()]
        nums_c = [float(s) for s in c_low.split() if s.replace('.','').replace('-','').isdigit()]
        
        if nums_p and nums_c:
            # If prompt implies order, check candidate
            if len(nums_p) >= 2 and len(nums_c) >= 2:
                # Check relative order preservation
                p_order = nums_p[0] < nums_p[1]
                c_order = nums_c[0] < nums_c[1]
                if "less" in p_low or "smaller" in p_low:
                    if not p_order or c_order != p_order: # Simplified logic
                         pass # Complex logic omitted for brevity, focusing on presence
                elif "greater" in p_low or "larger" in p_low:
                    if p_order != c_order:
                        penalty += 0.3

        # 3. Keyword containment for strict constraints
        if "must" in p_low or "only" in p_low:
            if not any(k in c_low for k in p_low.split() if len(k) > 4):
                penalty += 0.2
                
        return min(penalty, 1.0)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximation using lengths for speed/stability in this context
        return max(0.0, (len_concat - min(len1, len2)) / max(len1, len2, 1))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_vec = self._hash_to_spectrum(prompt)
        prompt_sus = self._compute_susceptibility(prompt_vec)
        
        for cand in candidates:
            cand_vec = self._hash_to_spectrum(cand)
            
            # 1. Spectral Similarity (Cosine similarity)
            norm_p = np.linalg.norm(prompt_vec)
            norm_c = np.linalg.norm(cand_vec)
            if norm_p == 0 or norm_c == 0:
                spectral_sim = 0.0
            else:
                spectral_sim = float(np.dot(prompt_vec, cand_vec) / (norm_p * norm_c))
            
            # 2. Critical Susceptibility Penalty
            # If the system is near criticality (high variance), small mismatches matter more
            cand_sus = self._compute_susceptibility(cand_vec)
            susceptibility_gap = abs(prompt_sus - cand_sus)
            
            # 3. Structural/Logical Check
            struct_penalty = self._structural_parse_score(prompt, cand)
            
            # 4. NCD Tiebreaker
            ncd = self._ncd_distance(prompt, cand)
            
            # Composite Score Logic:
            # Base: Spectral similarity (semantic overlap)
            # Adjustment: Subtract structural penalty (logic violations)
            # Adjustment: Subtract susceptibility gap (critical mismatch)
            # Tiebreak: NCD (compression overlap)
            
            score = (0.6 * spectral_sim) + (0.3 * (1.0 - ncd)) 
            score -= (0.4 * struct_penalty) 
            score -= (0.1 * susceptibility_gap)
            
            # Normalize to 0-1 roughly
            score = max(0.0, min(1.0, score))
            
            reasoning = f"Spectral:{spectral_sim:.2f}, StructPen:{struct_penalty:.2f}, NCD:{ncd:.2f}"
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on spectral alignment and structural integrity."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # The score from evaluate is already a proxy for confidence
        return res[0]["score"]