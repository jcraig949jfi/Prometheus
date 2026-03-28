import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Scale Adaptive Fractal Controller (MAFC) for Reasoning.
    
    Mechanism:
    1. Fractal Reference Generator: Creates a hierarchy of structural constraints 
       (negations, comparatives, conditionals) acting as self-similar reference 
       trajectories at different scales (global logic vs local token consistency).
    2. Chaos Monitor: Estimates instability (Lyapunov exponent analog) by measuring 
       divergence between the candidate's structural signature and the prompt's 
       required logical flow. High divergence indicates a "chaotic" (invalid) hypothesis.
    3. Adaptive Gain Law: Computes a final score by adaptively weighting the 
       semantic similarity (NCD) with a chaos-dependent scaling factor. 
       If logical structure diverges (chaos), the gain on semantic similarity is 
       reduced to prevent false positives from superficially similar but logically 
       flawed answers.
    """
    
    def __init__(self):
        self.scale_factor = 0.5  # Fractal scaling factor s < 1
        self.base_gain = 1.0
        
    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extract logical features as the fractal reference scaffold."""
        text_lower = text.lower()
        features = {
            'negation': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'conditional': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', text_lower)),
            'numeric': len(re.findall(r'\d+', text_lower)),
            'length': len(text)
        }
        return features

    def _compute_fractal_distance(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute distance across scales. 
        Scale 0: Global logical operators.
        Scale 1: Numeric and length consistency.
        """
        # Level 0: Logical Structure (High importance)
        logic_keys = ['negation', 'comparative', 'conditional']
        logic_diff = 0.0
        for k in logic_keys:
            diff = abs(prompt_feats[k] - cand_feats[k])
            # If prompt has logic and candidate misses it, penalty is high (chaos)
            if prompt_feats[k] > 0 and cand_feats[k] == 0:
                logic_diff += 2.0 
            else:
                logic_diff += diff * self.scale_factor
        
        # Level 1: Numeric/Detail consistency
        num_diff = abs(prompt_feats['numeric'] - cand_feats['numeric']) * 0.5
        if prompt_feats['numeric'] > 0 and cand_feats['numeric'] == 0:
            num_diff += 1.0
            
        return logic_diff + num_diff

    def _estimate_lyapunov(self, prompt: str, candidate: str) -> float:
        """
        Estimate largest Lyapunov exponent analog.
        Measures sensitivity to initial conditions by checking if small structural 
        deviations lead to large semantic divergences.
        """
        p_feats = self._extract_structure(prompt)
        c_feats = self._extract_structure(candidate)
        
        # Structural divergence
        struct_dist = self._compute_fractal_distance(p_feats, c_feats)
        
        # If structure is missing where expected, system is chaotic (lambda > 0)
        # Normalize by prompt complexity to get rate
        prompt_complexity = sum(p_feats.values()) + 1e-6
        lambda_max = (struct_dist / prompt_complexity) - 0.1
        
        return max(0.0, lambda_max)

    def _adaptive_gain(self, lambda_max: float) -> float:
        """MRAC gain modulation: reduce trust in similarity if chaos is detected."""
        # alpha = 1 / (1 + |lambda|)
        return 1.0 / (1.0 + abs(lambda_max))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        
        numerator = c12 - min(c1, c2)
        denominator = max(c1, c2)
        
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt features (Reference)
        p_feats = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Chaos Monitor
            lambda_max = self._estimate_lyapunov(prompt, cand)
            
            # 2. Adaptive Gain
            alpha = self._adaptive_gain(lambda_max)
            
            # 3. Base Similarity (NCD)
            ncd_val = self._ncd(prompt, cand)
            
            # 4. Structural Penalty (Direct constraint check)
            c_feats = self._extract_structure(cand)
            struct_penalty = 0.0
            if p_feats['negation'] > 0 and c_feats['negation'] == 0:
                struct_penalty = 0.3
            if p_feats['numeric'] > 0 and c_feats['numeric'] == 0:
                struct_penalty += 0.2
                
            # Final Score: High NCD (bad) reduces score. Chaos (alpha) reduces score.
            # Base score inverted from NCD (1.0 is perfect match)
            base_score = max(0.0, 1.0 - ncd_val)
            
            # Apply adaptive gain and structural penalty
            final_score = (base_score * alpha) - struct_penalty
            final_score = max(0.0, min(1.0, final_score)) # Clamp 0-1
            
            reasoning = f"Chaos(λ={lambda_max:.2f}), Gain={alpha:.2f}, NCD={ncd_val:.2f}, StructPen={struct_penalty:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        ranked = self.evaluate(prompt, [answer])
        return ranked[0]['score'] if ranked else 0.0