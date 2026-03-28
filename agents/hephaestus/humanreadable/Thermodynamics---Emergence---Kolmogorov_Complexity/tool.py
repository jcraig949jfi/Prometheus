import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Algorithmic Free-Energy Minimization via Emergent Compression.
    
    Mechanism:
    Treats reasoning as a thermodynamic process where the 'correct' answer 
    minimizes algorithmic free energy. This energy is a weighted sum of:
    1. Entropy of Prediction Error (Structural Mismatch): High penalty if the 
       candidate contradicts the prompt's logical structure (negations, comparatives).
    2. Model Complexity (Overfitting): Penalty for unnecessary length/redundancy 
       relative to the information gained.
       
    The system parses structural constraints (negations, numbers, conditionals) 
    to establish a 'logical ground state'. Candidates are scored by how well they 
    compress the logical distance between the prompt and a valid conclusion, 
    acting as an emergent phase transition from noise to order.
    """

    def __init__(self):
        self.structural_weight = 0.7
        self.compression_weight = 0.3

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical primitives: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        return {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(text)
        }

    def _structural_similarity(self, s1: Dict, s2: Dict) -> float:
        """Calculate similarity based on logical primitives (Constraint Propagation)."""
        if s1['length'] == 0 and s2['length'] == 0:
            return 1.0
        
        # Normalize features
        norm_neg = 1.0 if (s1['negations'] > 0) == (s2['negations'] > 0) else 0.0
        norm_comp = 1.0 if (s1['comparatives'] > 0) == (s2['comparatives'] > 0) else 0.0
        norm_cond = 1.0 if (s1['conditionals'] > 0) == (s2['conditionals'] > 0) else 0.0
        
        # Numeric consistency check (simplified)
        num_match = 1.0
        if s1['numbers'] and s2['numbers']:
            # Check if order is preserved or logic holds (simplified to presence for now)
            num_match = 1.0 if len(s1['numbers']) == len(s2['numbers']) else 0.5
        elif not s1['numbers'] and not s2['numbers']:
            num_match = 1.0
        elif not s1['numbers'] and s2['numbers']:
            # Candidate adds numbers not in prompt? Potential hallucination unless derived.
            num_match = 0.8 

        return (norm_neg + norm_comp + norm_cond + num_match) / 4.0

    def _kolmogorov_approx(self, s: str) -> int:
        """Approximate Kolmogorov complexity using zlib compression length."""
        return len(zlib.compress(s.encode('utf-8')))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker)."""
        if not s1 and not s2:
            return 0.0
        c1 = self._kolmogorov_approx(s1)
        c2 = self._kolmogorov_approx(s2)
        c12 = self._kolmogorov_approx(s1 + s2)
        min_len = min(c1, c2)
        if min_len == 0:
            return 1.0
        return (c12 - min_len) / max(c1, c2, 1)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Algorithmic Free Energy.
        Lower energy = Better hypothesis.
        F = E_struct - T * S_comp (Simplified to weighted sum for scoring)
        We invert this so Higher Score = Better.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Structural Entropy (Error Cost)
        # How much does the candidate violate the prompt's logical topology?
        struct_sim = self._structural_similarity(p_struct, c_struct)
        error_cost = 1.0 - struct_sim
        
        # 2. Complexity Cost (Occam's Razor)
        # Does the candidate add unnecessary complexity without reducing error?
        # We compare the complexity of the candidate to the prompt.
        # Ideal: Candidate is slightly more complex than prompt (adds info) but not random noise.
        k_prompt = self._kolmogorov_approx(prompt)
        k_cand = self._kolmogorov_approx(candidate)
        
        # Penalty for extreme brevity (underfitting) or extreme length (overfitting)
        # Optimal range is roughly prompt length to 2x prompt length
        length_ratio = k_cand / max(k_prompt, 1)
        complexity_penalty = 0.0
        if length_ratio < 0.2: # Too short, likely missing info
            complexity_penalty = 0.5
        elif length_ratio > 5.0: # Too long, likely noise
            complexity_penalty = 0.5
        else:
            # Smooth penalty for deviation from ideal compression
            complexity_penalty = abs(length_ratio - 1.5) * 0.1

        # 3. Emergent Compression Score (The "Order")
        # If the candidate explains the prompt well, the joint compression should be efficient.
        # We use NCD as a proxy for how well they fit together.
        ncd_val = self._ncd(prompt, candidate)
        
        # Final Score: High Structural Sim + Low Complexity Penalty + Low NCD
        # Score = (Struct_Sim * 0.6) + ((1 - NCD) * 0.3) + ((1 - complexity_penalty) * 0.1)
        score = (struct_sim * self.structural_weight) + \
                ((1.0 - ncd_val) * 0.25) + \
                ((1.0 - complexity_penalty) * 0.15)
                
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            reasoning = (
                f"Structural alignment: {score*0.7:.2f}, "
                f"Compression efficiency: high" if score > 0.5 else "low"
            )
            scored.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on free energy minimization."""
        score = self._compute_free_energy(prompt, answer)
        # Map score to 0-1 range, clamping
        conf = max(0.0, min(1.0, score))
        return round(conf, 4)