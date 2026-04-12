import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-MDL Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Optimal Control Proxy): Extracts logical constraints 
       (negations, comparatives, conditionals) to define the 'feasible region' 
       of answers. This avoids the 'Optimal Control' trap of direct scoring by 
       using logic as a filter/gate.
    2. Thermodynamic Entropy (Exploration): Uses Shannon entropy of candidate 
       token distributions to penalize low-information (degenerate) answers 
       and reward diverse but valid options, simulating detailed balance.
    3. Kolmogorov Complexity (MDL): Uses NCD (zlib) to penalize overly complex 
       candidates that don't proportionally increase structural match, enforcing 
       Occam's razor.
       
    The final score is a weighted sum: 
    Score = (Structural_Fit * Control_Weight) - (Complexity_Penalty * MDL_Weight) + (Entropy_Bonus * Temp)
    """

    def __init__(self):
        # Weights derived from the "strong positive synergy" note
        self.w_struct = 0.60  # Primary driver (Structural/Logic)
        self.w_mdl = 0.30     # Complexity penalty
        self.w_thermo = 0.10  # Entropy bonus
        self.temp = 1.0       # Temperature for entropy scaling

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worser|than|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|implies)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluates if the candidate satisfies structural constraints of the prompt.
        Returns a score 0.0 to 1.0.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        score = 1.0
        
        # Constraint 1: Negation matching (Modus Tollens proxy)
        # If prompt has negation, valid answers often acknowledge it or flip logic
        if p_feat['negations'] > 0:
            # Heuristic: If prompt is negative, simple positive echoes are suspicious
            if c_feat['negations'] == 0 and len(candidate.split()) < 10:
                score -= 0.3
        
        # Constraint 2: Numeric consistency
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                # Check if candidate numbers are within reasonable bounds of prompt numbers
                # (Simple transitivity check)
                if p_nums and c_nums:
                    ratio = sum(c_nums) / (sum(p_nums) + 1e-9)
                    if ratio > 10.0 or ratio < 0.1: # Wild deviation penalty
                        score -= 0.4
            except ValueError:
                pass

        # Constraint 3: Conditional presence
        if p_feat['conditionals'] > 0 and c_feat['conditionals'] == 0:
            # If prompt is conditional, answer lacking conditionality might be incomplete
            score -= 0.1
            
        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def _compute_entropy(self, text: str) -> float:
        """Shannon entropy of character distribution (Thermodynamic proxy)."""
        if not text:
            return 0.0
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        length = len(text)
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._extract_structure(prompt)
        
        # Pre-calculate prompt complexity for NCD baseline
        prompt_comp = len(zlib.compress(prompt.encode('utf-8')))

        for cand in candidates:
            # 1. Structural Score (Optimal Control Logic)
            struct_score = self._check_logical_consistency(prompt, cand)
            
            # 2. MDL Score (Kolmogorov Complexity via NCD)
            # Penalize if candidate adds significant description length without value
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD: Lower is better (similar), but we want to penalize high complexity
            # If NCD is high, it means they are very different/complex together.
            # We interpret high NCD as high "description length" of the joint state.
            mdl_penalty = ncd_val 

            # 3. Thermodynamic Score (Entropy)
            # Reward moderate entropy (exploration), penalize zero entropy (degenerate)
            entropy = self._compute_entropy(cand)
            # Normalize entropy by max possible (log2(charset)), approximated by log2(len)
            max_ent = math.log2(len(cand) + 1) if cand else 1
            norm_entropy = entropy / (max_ent + 1e-9)
            
            # Combined Score Formula
            # High structural fit is mandatory.
            # MDL penalizes unnecessary complexity (high NCD relative to prompt)
            # Entropy provides a small bonus for non-degenerate answers
            raw_score = (self.w_struct * struct_score) - (self.w_mdl * mdl_penalty) + (self.w_thermo * norm_entropy)
            
            # Deterministic tie-breaking using NCD if scores are close
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Structural:{struct_score:.2f}, MDL:{mdl_penalty:.2f}, Entropy:{norm_entropy:.2f}",
                "_ncd": ncd_val # Store for tie-breaking
            })

        # Sort by score descending, then by NCD (lower NCD is better for ties)
        results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up internal keys
        for r in results:
            del r['_ncd']
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and complexity.
        """
        struct_score = self._check_logical_consistency(prompt, answer)
        ncd_val = self._compute_ncd(prompt, answer)
        
        # Confidence is high if structural fit is high AND complexity is low (low NCD)
        # Map NCD (0-1ish) to a penalty
        complexity_penalty = max(0, ncd_val - 0.5) * 2 # Penalize if NCD > 0.5
        
        conf = struct_score * (1.0 - complexity_penalty)
        return max(0.0, min(1.0, conf))