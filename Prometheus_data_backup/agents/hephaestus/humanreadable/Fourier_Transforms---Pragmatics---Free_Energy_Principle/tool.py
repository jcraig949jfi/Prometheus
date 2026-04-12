import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining structural parsing, pragmatic weighting, and 
    Free Energy Principle (FEP) minimization. 
    
    Mechanism:
    1. Structural Extraction: Converts text into a time-series of binary vectors 
       representing logical features (negation, conditionals, numerics, etc.).
    2. Spectral Analysis (Restricted): Uses FFT only within the confidence() wrapper 
       to detect oscillatory patterns (e.g., negation loops) as a stability check, 
       adhering to the 'Fourier as inhibitor' warning for primary scoring.
    3. FEP Scoring: The core evaluate() method computes a 'Free Energy' score based 
       on the KL-divergence between the prompt's structural distribution and the 
       candidate's. Lower divergence (lower F) implies the candidate minimizes 
       prediction error relative to the prompt's logical constraints.
    4. Pragmatics: Weights specific tokens (e.g., 'but', 'if') to adjust the 
       significance of structural matches.
    5. Fallback: Uses Normalized Compression Distance (NCD) only when structural 
       signals are too weak to differentiate.
    """

    def __init__(self):
        # Pragmatic weights for specific cues (higher = more load)
        self.pragmatic_weights = {
            'not': 1.5, 'no': 1.5, 'never': 1.5,
            'if': 1.4, 'then': 1.2, 'unless': 1.4,
            'because': 1.3, 'therefore': 1.3,
            'more': 1.2, 'less': 1.2, 'greater': 1.2, 'smaller': 1.2,
            'first': 1.1, 'after': 1.1, 'before': 1.1,
            'but': 1.6, 'however': 1.6, 'although': 1.5
        }
        
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|second|last|after|before|next)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'contrast': re.compile(r'\b(but|however|although|yet|despite)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Tuple[np.ndarray, List[str]]:
        """Extract binary feature vector and list of weighted tokens."""
        text_lower = text.lower()
        features = []
        tokens_found = []
        
        # Order matters for the vector: [neg, cond, causal, comp, order, num, contrast]
        keys = ['negation', 'conditional', 'causal', 'comparative', 'ordering', 'numeric', 'contrast']
        
        for key in keys:
            matches = self.patterns[key].findall(text_lower)
            count = len(matches)
            features.append(1 if count > 0 else 0)
            if count > 0:
                # Store token for pragmatic weighting
                for m in matches:
                    tokens_found.append(m if isinstance(m, str) else m[0])
        
        return np.array(features, dtype=float), tokens_found

    def _compute_spectrum_instability(self, text: str) -> float:
        """
        Uses FFT to detect high-frequency oscillation of logical cues.
        Used ONLY for confidence adjustment (Fourier as inhibitor warning).
        High instability reduces confidence.
        """
        if len(text) < 10:
            return 0.0
            
        # Create a dense time series based on token positions
        words = re.findall(r'\w+', text.lower())
        if not words:
            return 0.0
            
        signal = []
        for word in words:
            val = 0
            if any(p in word for p in ['not', 'no', 'never']): val = 1
            elif any(p in word for p in ['if', 'then']): val = -1
            signal.append(val)
            
        if len(signal) < 4:
            return 0.0
            
        # Pad to power of 2 for FFT efficiency
        n = len(signal)
        padded_len = 1
        while padded_len < n: padded_len *= 2
        padded_len *= 2 # oversample
        
        fft_signal = np.fft.fft(signal, n=padded_len)
        power = np.abs(fft_signal) ** 2
        
        # High frequency energy ratio (instability)
        mid = len(power) // 2
        high_freq_energy = np.sum(power[mid:])
        total_energy = np.sum(power) + 1e-12
        
        return float(high_freq_energy / total_energy)

    def _free_energy_score(self, prompt: str, candidate: str) -> float:
        """
        Computes Free Energy (F) as KL-divergence between prompt and candidate 
        structural distributions.
        F = sum(P * log(P/Q)) approx.
        Lower F is better. Score = -F.
        """
        p_feats, p_tokens = self._extract_features(prompt)
        c_feats, c_tokens = self._extract_features(candidate)
        
        # 1. Base structural match (Euclidean distance of feature vectors)
        # If prompt has a feature, candidate should ideally have it too.
        struct_diff = np.sum((p_feats - c_feats) ** 2)
        
        # 2. Pragmatic Weighting & Distribution Matching
        # Build a distribution of pragmatic weights present in the text
        def get_weighted_dist(tokens):
            dist = np.zeros(len(self.pragmatic_weights))
            keys = list(self.pragmatic_weights.keys())
            total = 0
            for t in tokens:
                # Simple fuzzy match for the token in our weight dict
                for i, k in enumerate(keys):
                    if k in t or t in k:
                        dist[i] += self.pragmatic_weights[k]
                        total += self.pragmatic_weights[k]
                        break
            if total == 0:
                return dist + 1e-12 # Avoid zero
            return (dist / total) + 1e-12

        p_dist = get_weighted_dist(p_tokens)
        c_dist = get_weighted_dist(c_tokens)
        
        # Normalize to probabilities
        p_dist /= np.sum(p_dist)
        c_dist /= np.sum(c_dist)
        
        # KL Divergence: D_KL(P || C) = sum(P * log(P/C))
        # Add small epsilon to avoid log(0)
        epsilon = 1e-12
        kl_div = np.sum(p_dist * np.log((p_dist + epsilon) / (c_dist + epsilon)))
        
        # Free Energy approximation: Structural Penalty + Pragmatic Divergence
        # If prompt has strong pragmatic signals and candidate misses them, F increases.
        pragmatic_penalty = kl_div * 2.0
        
        F = struct_diff + pragmatic_penalty
        return -F # Higher is better

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1 + s2
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        c1 = len(z(s1.encode()))
        c2 = len(z(s2.encode()))
        c12 = len(z(concat.encode()))
        
        numerator = c12 - min(c1, c2)
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_feats, _ = self._extract_features(prompt)
        prompt_strength = np.sum(prompt_feats) # How structurally rich is the prompt?
        
        scores = []
        
        for cand in candidates:
            # Primary Score: Free Energy Minimization
            fe_score = self._free_energy_score(prompt, cand)
            
            # Secondary Check: Numeric consistency if numbers exist
            prompt_nums = re.findall(r'\d+\.\d+|\d+', prompt)
            cand_nums = re.findall(r'\d+\.\d+|\d+', cand)
            
            numeric_bonus = 0.0
            if prompt_nums and cand_nums:
                try:
                    # Check if order is preserved (simple heuristic)
                    p_vals = [float(x) for x in prompt_nums]
                    c_vals = [float(x) for x in cand_nums]
                    # If prompt implies a comparison, does candidate respect magnitude?
                    # This is a simplified check for demonstration
                    if len(p_vals) >= 2 and len(c_vals) >= 2:
                        p_diff = p_vals[0] - p_vals[1]
                        c_diff = c_vals[0] - c_vals[1]
                        if np.sign(p_diff) == np.sign(c_diff):
                            numeric_bonus = 0.5
                except ValueError:
                    pass
            
            final_score = fe_score + numeric_bonus
            
            # Tiebreaker: If structural signal is weak, use NCD
            if prompt_strength < 1.0:
                ncd = self._ncd_score(prompt, cand)
                # Invert NCD so higher is better, scale to match FE range roughly
                final_score = (1.0 - ncd) * 0.5 
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"FE Score: {fe_score:.4f}, Numeric Bonus: {numeric_bonus}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural match + Fourier-based instability check.
        """
        # 1. Base structural alignment
        score = self._free_energy_score(prompt, answer)
        
        # Normalize score to 0-1 range roughly (heuristic)
        # FE scores are negative, closer to 0 is better. 
        # Let's assume -5.0 is terrible, 0.0 is perfect.
        base_conf = 1.0 / (1.0 + np.exp(score + 2.0)) # Sigmoid shift
        
        # 2. Fourier Instability Penalty (The "Inhibitor" role)
        # If the answer has wild oscillations of logic, reduce confidence
        instability = self._compute_spectrum_instability(answer)
        # Instability is 0.0 to ~1.0. High instability -> low confidence.
        fourier_penalty = instability * 0.4
        
        final_conf = max(0.0, min(1.0, base_conf - fourier_penalty))
        return float(final_conf)