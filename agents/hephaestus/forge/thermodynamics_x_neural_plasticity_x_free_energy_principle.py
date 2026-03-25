import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically-Regularized Predictive Coding (TRPC) Implementation.
    
    Mechanism:
    1. Prediction Error (KL Divergence approx): Measures semantic mismatch between 
       prompt and candidate using Normalized Compression Distance (NCD) on structural 
       features (negations, numbers, logic keywords) rather than raw text. This represents 
       the 'accuracy' term in free energy.
       
    2. Thermodynamic Regularizer (Entropy Production): Estimates the 'metabolic cost' 
       of a hypothesis. Complex, verbose, or logically inconsistent answers require 
       more 'ions' (computation/tokens) to sustain. We model this as a function of 
       candidate length and structural complexity (entropy of character distribution).
       
    3. Free Energy Minimization: Score = -(Prediction_Error + lambda * Thermodynamic_Cost).
       This implements Occam's Razor: favoring candidates that fit the data well 
       with minimal energetic expenditure.
    """

    def __init__(self):
        self.lambda_energy = 0.15  # Trade-off weight for thermodynamic cost
        self.struct_keys = ['not', 'no', 'yes', 'true', 'false', 'if', 'then', 'else', 
                            'greater', 'less', 'equal', 'more', 'fewer', 'before', 'after']

    def _extract_structural_features(self, text: str) -> str:
        """Extract logic-critical tokens to reduce noise and focus on reasoning structure."""
        if not text:
            return ""
        t = text.lower()
        # Extract numbers
        nums = re.findall(r'-?\d+\.?\d*', t)
        # Extract logic keywords
        keys = [k for k in self.struct_keys if k in t]
        # Combine signature
        return " ".join(keys + nums)

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a proxy for KL-divergence."""
        if not s1 or not s2:
            return 1.0
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0:
                return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def _estimate_entropy_production(self, text: str) -> float:
        """
        Estimate thermodynamic cost (entropy production) of sustaining this hypothesis.
        Cost ~ Length * Complexity (Character entropy).
        Longer, more chaotic strings require more energy to maintain state.
        """
        if not text:
            return 0.0
        
        L = len(text)
        if L == 0:
            return 0.0
            
        # Character frequency for entropy
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        
        # Shannon entropy approximation
        entropy = 0.0
        for count in freq.values():
            p = count / L
            if p > 0:
                entropy -= p * np.log2(p)
        
        # Normalize entropy by max possible (log2 of unique chars) to get complexity ratio
        max_ent = np.log2(len(freq)) if len(freq) > 1 else 1.0
        complexity_ratio = entropy / max_ent if max_ent > 0 else 0.0
        
        # Thermodynamic cost model: Cost increases with length and disorder
        # Scaling factor to make it comparable to NCD (0-1 range)
        cost = (L / 1000.0) * (1.0 + complexity_ratio)
        return min(cost, 1.0) # Cap at 1.0

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute variational free energy: F = Prediction_Error + lambda * Energy_Cost
        Lower F is better. We return negative F so higher score is better.
        """
        # 1. Prediction Error (Semantic/Structural match)
        # We compare structural features to ignore irrelevant wording differences
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        # If features are empty, fallback to raw NCD
        if not p_feat: p_feat = prompt
        if not c_feat: c_feat = candidate
            
        pred_error = self._ncd(p_feat, c_feat)
        
        # 2. Thermodynamic Regularizer (Energy cost)
        energy_cost = self._estimate_entropy_production(candidate)
        
        # Free Energy
        free_energy = pred_error + (self.lambda_energy * energy_cost)
        
        # Convert to score (higher is better)
        # NCD is 0-1 (0=identical), so 1-NCD is 0-1 (1=identical)
        # We subtract energy cost to penalize high-energy hypotheses
        score = (1.0 - pred_error) - (self.lambda_energy * energy_cost)
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            reasoning = f"PredErr={1.0 - (score + self.lambda_energy * self._estimate_entropy_production(cand)):.2f}, Energy={self._estimate_entropy_production(cand):.2f}"
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on free energy minimization.
        High free energy -> Low confidence.
        """
        score = self._compute_free_energy(prompt, answer)
        # Map score (theoretically -inf to 1) to 0-1
        # A perfect match with 0 energy cost is 1.0
        # A random match might be 0.5 - penalty
        conf = max(0.0, min(1.0, score))
        return float(conf)