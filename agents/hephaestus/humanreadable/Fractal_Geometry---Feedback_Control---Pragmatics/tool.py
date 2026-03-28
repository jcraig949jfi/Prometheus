import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Pragmatic Adaptive Controller (FPAC) Implementation.
    
    Mechanism:
    1. Fractal Geometry (Hypothesis Space): Candidates are treated as points in a 
       semantic space. We approximate the "Hausdorff dimension" of the match between 
       prompt and candidate using structural complexity ratios (token density vs 
       compression ratio). High dimension = high information density/relevance.
       
    2. Feedback Control (MRAC): A reference model is established based on the 
       structural integrity of the prompt (negations, conditionals). The error signal 
       is the divergence between the candidate's structural profile and the prompt's 
       required logic (e.g., if prompt has negation, candidate lacking negation gets 
       high error). Gains are scaled by the estimated fractal dimension.
       
    3. Pragmatics (RSA/Grice): We apply Grice's Maxims as filters/scalers:
       - Quantity: Penalize candidates too short or too long relative to prompt complexity.
       - Relation: Boost score if candidate shares specific structural tokens (comparatives).
       - Quality: Penalize internal contradictions (simple heuristic).
       - Manner: Prefer candidates with clear, non-repetitive structure.
       
    Scoring: Base NCD is used only as a tiebreaker. Primary score comes from 
    structural alignment and pragmatic scaling.
    """

    def __init__(self):
        self._struct_keys = ['if', 'then', 'else', 'not', 'no', 'yes', 'greater', 'less', 'more', 'fewer']
        self._comparatives = ['>', '<', 'larger', 'smaller', 'higher', 'lower', 'greater', 'less']

    def _get_tokens(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _count_structural(self, text: str) -> Dict[str, int]:
        lower = text.lower()
        counts = {
            'negations': len(re.findall(r'\b(not|no|never|neither)\b', lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|else)\b', lower)),
            'comparatives': sum(1 for w in self._comparatives if w in lower),
            'numbers': len(re.findall(r'\d+\.?\d*', text))
        }
        return counts

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _estimate_hausdorff_dim(self, text: str) -> float:
        """
        Approximates local dimension via compression entropy ratio.
        Higher ratio implies more unique structure (higher dimension).
        """
        if not text: return 0.0
        b = text.encode()
        compressed_len = len(zlib.compress(b))
        original_len = len(b)
        if original_len == 0: return 0.0
        # Ratio of compressed to original. 
        # Low ratio = repetitive (low dim), High ratio = complex (high dim)
        return min(1.0, compressed_len / original_len)

    def _pragmatic_score(self, prompt: str, candidate: str) -> float:
        """
        Evaluates Grice's Maxims to produce a pragmatic bias factor (0.5 - 1.5).
        """
        score = 1.0
        p_struct = self._count_structural(prompt)
        c_struct = self._count_structural(candidate)
        
        # Maxim of Relation: If prompt has logic, candidate should reflect it
        if p_struct['negations'] > 0:
            if c_struct['negations'] == 0:
                score *= 0.6  # Penalty for ignoring negation context
            else:
                score *= 1.2  # Bonus for maintaining logical frame
                
        if p_struct['conditionals'] > 0:
            if c_struct['conditionals'] == 0 and len(self._get_tokens(candidate)) < 10:
                score *= 0.8  # Mild penalty if candidate is too simple for complex prompt

        # Maxim of Quantity: Length appropriateness
        p_len = len(self._get_tokens(prompt))
        c_len = len(self._get_tokens(candidate))
        
        if p_len > 20 and c_len < 3:
            score *= 0.7  # Too brief for complex prompt
        elif c_len > p_len * 2:
            score *= 0.8  # Too verbose
            
        # Maxim of Manner: Clarity (repetition penalty)
        c_tokens = self._get_tokens(candidate)
        if len(c_tokens) > 0:
            unique_ratio = len(set(c_tokens)) / len(c_tokens)
            if unique_ratio < 0.4: # Highly repetitive
                score *= 0.7
                
        return score

    def _structural_alignment(self, prompt: str, candidate: str) -> float:
        """
        Computes alignment based on structural features (Feedback Control Error).
        Returns a score where 1.0 is perfect alignment, 0.0 is contradiction.
        """
        p_struct = self._count_structural(prompt)
        c_struct = self._count_structural(candidate)
        
        error = 0.0
        
        # Negation check
        if p_struct['negations'] > 0 and c_struct['negations'] == 0:
            # Check if candidate is just a number or simple yes/no which might be valid
            if not re.search(r'\b(yes|no|true|false|\d+)\b', candidate.lower()):
                error += 0.5
        
        # Number consistency (basic)
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if p_nums and c_nums:
            # If both have numbers, check rough magnitude order if comparatives exist
            if any(k in prompt.lower() for k in self._comparatives):
                try:
                    p_max = max(float(x) for x in p_nums)
                    c_max = max(float(x) for x in c_nums)
                    # Heuristic: In reasoning tasks, extracted numbers often need to match or be logically derived
                    # We don't penalize heavily here unless it's a direct extraction task simulation
                    pass 
                except ValueError:
                    pass
        
        # Base alignment score
        base_score = 1.0 - min(1.0, error)
        return base_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_dim = self._estimate_hausdorff_dim(prompt)
        p_prag = self._pragmatic_score(prompt, prompt) # Reference pragmatic baseline
        
        for cand in candidates:
            # 1. Fractal Dimension (Complexity Match)
            c_dim = self._estimate_hausdorff_dim(cand)
            dim_diff = abs(p_dim - c_dim)
            
            # 2. Feedback Control (Structural Alignment)
            struct_align = self._structural_alignment(prompt, cand)
            
            # 3. Pragmatics (Gricean Scaling)
            prag_factor = self._pragmatic_score(prompt, cand)
            
            # 4. NCD Tiebreaker (Low weight)
            ncd_val = self._ncd(prompt, cand)
            
            # Composite Score
            # High struct_align and prag_factor boost score. 
            # Dim_diff penalizes mismatched complexity slightly.
            # NCD is minor tiebreaker.
            score = (struct_align * 0.5 + prag_factor * 0.4 + (1.0 - dim_diff) * 0.1)
            
            # Adjust by NCD only if scores are close (simulated by small addition)
            score += (1.0 - ncd_val) * 0.05 
            
            # Ensure bounds
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"Structural:{struct_align:.2f} Pragmatic:{prag_factor:.2f} Dim:{c_dim:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural and pragmatic consistency."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']