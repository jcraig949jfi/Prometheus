import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Wavelet-Based Multiscale Information-Lyapunov Monitor (WB-MILM) Analogue.
    
    Mechanism:
    Since true wavelet decomposition and Lyapunov exponent estimation require 
    continuous time-series data, this implementation creates a computational 
    analogy for text-based reasoning tasks:
    
    1. Signal Decomposition (Wavelet Analogue): The text is converted to a 
       numeric signal (ASCII/Length features). A simple Haar-like differencing 
       simulates multi-scale decomposition to detect local structural volatility 
       (chaos) vs smooth semantic flow.
       
    2. Entropy & Mutual Information: 
       - H_s (Entropy): Calculated via character/n-gram frequency distribution 
         of the candidate relative to the prompt's expected complexity.
       - I_s (Mutual Information): Approximated by Normalized Compression Distance (NCD) 
         between prompt and candidate, acting as a proxy for shared information.
         
    3. Lyapunov Exponent Analogue: 
       - Measures the rate of divergence between the candidate's structural 
         pattern and the prompt's constraints. High divergence in constrained 
         logic tasks indicates instability (incorrectness).
         
    4. Scoring Logic:
       - Primary: Structural parsing (negations, comparatives, numeric logic).
       - Secondary: The WB-MILM analogue metrics (Entropy consistency, NCD-based MI).
       - Tiebreaker: Raw NCD.
    """

    def __init__(self):
        self.eps = 1e-9

    def _to_signal(self, text: str) -> np.ndarray:
        """Convert text to a numeric signal for analysis."""
        if not text:
            return np.array([0.0])
        # Use ASCII values normalized to [0, 1]
        vals = [float(ord(c)) / 255.0 for c in text]
        return np.array(vals)

    def _haar_decompose(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Simple 1-level Haar wavelet decomposition analogue."""
        if len(signal) < 2:
            return signal, np.array([0.0])
        # Approximation (average) and Detail (difference)
        even = signal[0::2]
        odd = signal[1::2]
        if len(odd) < len(even):
            odd = np.append(odd, 0) # Pad for simplicity
        approx = (even + odd[:len(even)]) / 2.0
        detail = (even - odd[:len(even)]) / 2.0
        return approx, detail

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of character distribution."""
        if not text:
            return 0.0
        freq = {}
        for c in text:
            freq[c] = freq.get(c, 0) + 1
        length = len(text)
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * np.log2(p)
        return entropy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0:
            return 0.0
        return (z12 - min(z1, z2)) / denom

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extract logical structural features."""
        text_lower = text.lower()
        features = {
            'has_negation': float(any(w in text_lower for w in ['not', 'no ', 'never', 'false', 'impossible'])),
            'has_comparative': float(any(w in text_lower for w in ['greater', 'less', 'more', 'fewer', '>', '<', 'larger', 'smaller'])),
            'has_conditional': float(any(w in text_lower for w in ['if', 'then', 'unless', 'otherwise'])),
            'numeric_density': len(re.findall(r'\d+', text)) / (len(text.split()) + 1),
            'length_ratio': len(text) / (len(text.split()) + 1) # Avg word length proxy
        }
        return features

    def _evaluate_lyapunov_analogue(self, prompt: str, candidate: str) -> float:
        """
        Estimate stability. If the prompt implies strict logic (high structure),
        the candidate must match that structure. Divergence = instability.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        # Calculate divergence in structural space
        divergence = 0.0
        count = 0
        for k in p_feat:
            diff = abs(p_feat[k] - c_feat[k])
            # Weight negation and conditional mismatches heavily as they imply logic flips
            weight = 2.0 if k in ['has_negation', 'has_conditional'] else 1.0
            divergence += diff * weight
            count += 1
            
        avg_divergence = divergence / (count + self.eps)
        # Lyapunov exponent analogue: positive means diverging (bad), negative means converging
        # We invert this so higher score = more stable (correct)
        return -avg_divergence

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_signal = self._to_signal(prompt)
        prompt_approx, prompt_detail = self._haar_decompose(prompt_signal)
        prompt_entropy = self._calculate_entropy(prompt)
        prompt_struct = self._extract_structural_features(prompt)

        for cand in candidates:
            cand_signal = self._to_signal(cand)
            cand_approx, cand_detail = self._haar_decompose(cand_signal)
            
            # 1. Mutual Information Proxy (NCD based)
            # High MI = Low NCD between prompt and candidate (contextual relevance)
            mi_score = 1.0 - self._ncd(prompt, cand)
            
            # 2. Entropy Consistency (Wavelet Scale H_s)
            # Reasonable answers often have entropy density similar to the prompt's complexity
            cand_entropy = self._calculate_entropy(cand)
            entropy_diff = abs(prompt_entropy - cand_entropy)
            entropy_score = 1.0 / (1.0 + entropy_diff) # Normalize to 0-1
            
            # 3. Lyapunov Stability (Structural Divergence)
            lyap_score = self._evaluate_lyapunov_analogue(prompt, cand)
            
            # 4. Structural Parsing (Primary Signal per instructions)
            # Check for direct logical contradictions in features
            struct_penalty = 0.0
            if prompt_struct['has_negation'] and not self._extract_structural_features(cand)['has_negation']:
                 # If prompt has negation logic, candidate ignoring it might be wrong (heuristic)
                 # This is a weak heuristic, so small penalty
                struct_penalty = 0.1
            
            # Combined Score
            # Weighted sum: Structural integrity > MI > Entropy consistency
            score = (0.5 * lyap_score) + (0.3 * mi_score) + (0.2 * entropy_score) - struct_penalty
            
            # Ensure non-negative
            score = max(0.0, score)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"MI:{mi_score:.2f}, EntropySim:{entropy_score:.2f}, LyapStab:{lyap_score:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Use the same logic as evaluate but for a single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        base_score = res[0]['score']
        
        # Calibration step:
        # If the answer is extremely short compared to prompt without being a simple yes/no, lower confidence
        if len(answer) < 3 and len(prompt) > 20 and answer.lower() not in ['yes', 'no', 'true', 'false']:
            return 0.2
            
        # Map score to 0-1 range more aggressively for calibration
        # Assuming base_score is roughly 0.4 to 0.9 for good matches
        conf = min(1.0, max(0.0, (base_score - 0.3) * 1.5))
        return conf