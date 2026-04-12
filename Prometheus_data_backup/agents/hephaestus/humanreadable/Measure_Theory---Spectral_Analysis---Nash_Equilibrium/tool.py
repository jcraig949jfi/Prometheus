import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Measure-Theoretic Nash Learning (SMTNL) Operator Implementation.
    
    Mechanism:
    1. Structural Parsing (Measure-Theoretic Support): Extracts logical atoms 
       (negations, comparatives, conditionals, numbers) to form a discrete 
       "belief vector" representing the hypothesis structure.
    2. Spectral Analysis (Stability Check): Computes the Fourier transform of 
       the belief vector. High frequency noise indicates logical inconsistency 
       or lack of structural coherence (divergence). Low frequency dominance 
       suggests a stable "Nash Equilibrium" of thought.
    3. Nash Projection: Scores candidates based on the ratio of low-frequency 
       spectral power (stability) to total power, adjusted by structural 
       constraint satisfaction (e.g., numeric truth).
    4. NCD Tiebreaker: Used only when spectral scores are indistinguishable.
    """

    def __init__(self):
        self._keywords_neg = {'not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self._keywords_comp = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse', 'than'}
        self._keywords_cond = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self._nums = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> np.ndarray:
        """Converts text to a structural feature vector (Measure Space)."""
        t = text.lower()
        words = set(re.findall(r'\b\w+\b', t))
        
        # Feature 0: Negation density
        f_neg = len(words & self._keywords_neg) / (len(words) + 1)
        # Feature 1: Comparative density
        f_comp = len(words & self._keywords_comp) / (len(words) + 1)
        # Feature 2: Conditional density
        f_cond = len(words & self._keywords_cond) / (len(words) + 1)
        # Feature 3: Numeric presence
        nums = self._nums.findall(text)
        f_num = len(nums) / (len(words) + 1)
        # Feature 4: Length normalization (proxy for complexity)
        f_len = min(1.0, len(text) / 500.0)
        
        return np.array([f_neg, f_comp, f_cond, f_num, f_len])

    def _spectral_stability(self, vector: np.ndarray) -> float:
        """
        Computes spectral stability. 
        Uses FFT to detect if the structural vector represents a 'smooth' 
        logical distribution (low freq) or 'noise' (high freq).
        """
        if len(vector) < 2:
            return 0.5
        
        # Center the vector
        v = vector - np.mean(vector)
        fft_res = np.fft.fft(v)
        psd = np.abs(fft_res) ** 2
        
        # Split spectrum: Low freq (stable) vs High freq (noise)
        mid = len(psd) // 2
        if mid == 0: mid = 1
        
        low_energy = np.sum(psd[:mid])
        total_energy = np.sum(psd) + 1e-9
        
        # Ratio of low-frequency energy (Stability Score)
        return float(low_energy / total_energy)

    def _check_numeric_truth(self, prompt: str, candidate: str) -> float:
        """Validates explicit numeric comparisons if present."""
        p_nums = [float(x) for x in self._nums.findall(prompt)]
        c_nums = [float(x) for x in self._nums.findall(candidate)]
        
        # If both have numbers, check simple consistency (heuristic)
        if p_nums and c_nums:
            # If candidate repeats prompt numbers exactly, it's likely echoing (good for fidelity, bad for reasoning)
            # If candidate derives new numbers, check magnitude logic if possible
            if set(p_nums) == set(c_nums):
                return 0.8 # Consistent repetition
            # Simple heuristic: if candidate has fewer numbers than prompt, might be summarizing (ok)
            # If candidate has random large numbers, penalize
            if len(c_nums) > len(p_nums) * 2:
                return 0.2
        return 0.5 # Neutral if no clear numeric conflict

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_vec = self._extract_features(prompt)
        prompt_stability = self._spectral_stability(prompt_vec)
        
        scores = []
        
        for cand in candidates:
            cand_vec = self._extract_features(cand)
            
            # 1. Structural/Spectral Score (Primary)
            cand_stability = self._spectral_stability(cand_vec)
            
            # Measure-theoretic deviation from prompt structure
            structural_dist = np.linalg.norm(prompt_vec - cand_vec)
            
            # Stability alignment: Candidate should have similar or higher stability than prompt
            # Penalize high deviation in structural features
            base_score = cand_stability * (1.0 / (1.0 + structural_dist))
            
            # 2. Numeric Constraint Check
            num_factor = self._check_numeric_truth(prompt, cand)
            
            final_score = base_score * 0.7 + num_factor * 0.3
            
            # 3. NCD Tiebreaker (only if scores are very close, handled by sorting key)
            ncd_val = self._ncd(prompt, cand)
            
            scores.append({
                "candidate": cand,
                "score": final_score,
                "ncd": ncd_val, # Store for tie-breaking
                "reasoning": f"Spectral stability: {cand_stability:.3f}, Structural dist: {structural_dist:.3f}"
            })
        
        # Sort by score desc, then by NCD asc (closer is better if scores equal)
        results = sorted(scores, key=lambda x: (x['score'], -x['ncd']), reverse=True)
        
        # Clean up output format
        return [
            {"candidate": r["candidate"], "score": r["score"], "reasoning": r["reasoning"]}
            for r in results
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on spectral stability and structural alignment.
        """
        p_vec = self._extract_features(prompt)
        a_vec = self._extract_features(answer)
        
        # Spectral match
        p_spec = self._spectral_stability(p_vec)
        a_spec = self._spectral_stability(a_vec)
        
        spec_diff = abs(p_spec - a_spec)
        struct_diff = np.linalg.norm(p_vec - a_vec)
        
        # Numeric truth check
        num_truth = self._check_numeric_truth(prompt, answer)
        
        # Confidence formula: High if spectral diff is low and numeric truth is high
        raw_conf = (1.0 / (1.0 + spec_diff + struct_diff)) * num_truth
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, raw_conf))