import numpy as np
import zlib
import re
from typing import List, Dict, Any

class ReasoningTool:
    """
    Spectral Recursive Belief-Reporting Mechanism.
    
    Core Logic (Mechanism Design):
    The 'evaluate' method acts as the peer-predictor. It scores candidates based on 
    structural consistency with the prompt (the 'truth' signal). 
    
    Implementation Details:
    1. Structural Parsing (Primary Signal): Extracts logic operators (negations, 
       comparatives, conditionals) and numeric values. Candidates are scored by 
       how well their structural signature aligns with the prompt's constraints.
    2. Theory of Mind (Validation): Checks if the candidate acknowledges the 
       prompt's context (e.g., presence of specific entities or negation markers).
    3. Fourier Transform (Confidence Wrapper): As per safety constraints, FFT is 
       restricted to the confidence() method. It treats the character-code trajectory 
       of the answer as a time-series signal, computing spectral entropy to measure 
       'belief stability'. High entropy (noise) = low confidence.
    4. NCD: Used strictly as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        self.logic_ops = ['not', 'no', 'never', 'without', 'unless']
        self.comp_ops = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.cond_ops = ['if', 'then', 'else', 'unless', 'provided']

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        features = {
            'has_negation': any(op in t_lower for op in self.logic_ops),
            'has_comparative': any(op in t_lower for op in self.comp_ops),
            'has_conditional': any(op in t_lower for op in self.cond_ops),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(text)
        }
        return features

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design: Peer-prediction scoring based on structural alignment.
        Incentivizes candidates that preserve the logical operators of the prompt.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        
        # Logic Consistency (High weight)
        if p_feat['has_negation']:
            score += 0.4 if c_feat['has_negation'] else -0.4
        else:
            # If prompt has no negation, penalize random negation in short answers
            if c_feat['has_negation'] and len(c_feat['numbers']) == 0:
                score -= 0.2

        if p_feat['has_comparative']:
            score += 0.3 if c_feat['has_comparative'] else -0.3
            
        if p_feat['has_conditional']:
            score += 0.3 if c_feat['has_conditional'] else -0.1

        # Numeric Consistency (Moderate weight)
        if p_feat['numbers'] and c_feat['numbers']:
            # Check if numbers are plausible (simple presence check for now)
            score += 0.3
        elif p_feat['numbers'] and not c_feat['numbers']:
            score -= 0.5 # Critical failure to address numbers

        # Theory of Mind: Context overlap (Jaccard on words > 3 chars)
        p_words = set(w for w in re.findall(r'\w+', prompt.lower()) if len(w) > 3)
        c_words = set(w for w in re.findall(r'\w+', candidate.lower()) if len(w) > 3)
        if p_words:
            overlap = len(p_words & c_words) / len(p_words | c_words)
            score += 0.2 * overlap
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Primary Score: Structural/Mechanism Design
            score = self._structural_score(prompt, cand)
            
            # Tie-breaking with NCD if scores are close (within epsilon)
            # We simulate this by adding a tiny NCD-based perturbation
            ncd_val = self._ncd(prompt, cand)
            final_score = score - (ncd_val * 0.01) 
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment: {score:.2f}, NCD penalty: {ncd_val:.4f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Spectral Analysis of Belief Stability.
        Uses FFT on the character code trajectory to determine signal regularity.
        High frequency noise implies low confidence (hallucination/randomness).
        Low frequency dominance implies structured, confident reasoning.
        """
        if not answer:
            return 0.0
        
        # Convert to signal (ASCII values centered)
        signal = np.array([ord(c) for c in answer], dtype=float)
        signal -= np.mean(signal)
        
        if len(signal) < 2:
            return 0.5
            
        # Discrete Fourier Transform
        spectrum = np.fft.fft(signal)
        magnitude = np.abs(spectrum)
        
        # Spectral Entropy calculation
        total_energy = np.sum(magnitude)
        if total_energy == 0:
            return 0.0
            
        probs = magnitude / total_energy
        # Avoid log(0)
        probs = probs[probs > 0]
        entropy = -np.sum(probs * np.log2(probs))
        
        # Normalize entropy (max entropy is log2(N))
        max_entropy = np.log2(len(probs)) if len(probs) > 0 else 1
        if max_entropy == 0:
            return 1.0
            
        normalized_entropy = entropy / max_entropy
        
        # Confidence is inverse of normalized entropy (structured = low entropy = high confidence)
        # Map [0, 1] entropy to [1, 0] confidence, then scale to reasonable range
        confidence = 1.0 - normalized_entropy
        
        # Apply a non-linear boost for very low entropy (highly structured)
        if confidence > 0.8:
            confidence = 0.9 + (confidence - 0.8) * 0.5
            
        return float(np.clip(confidence, 0.0, 1.0))