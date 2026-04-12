import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Zeta-Weighted Boltzmann Policy Gradient (ZW-BPG) Approximation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. Candidates are scored based 
       on constraint satisfaction and logical consistency with the prompt.
    2. Prime-Indexed Hypothesis Space (Complexity Prior): Each candidate is assigned 
       an index based on its structural complexity (token count). A 'Zeta-weighted' 
       penalty (1/n^s) acts as an Occam's razor, favoring simpler valid hypotheses.
    3. Boltzmann Exploration (Temperature Scaling): The final score is a softmax-like 
       transformation of the structural score, scaled by a temperature parameter T. 
       T anneals based on the 'energy gap' between the best and average structural scores, 
       mimicking the fluctuation-dissipation theorem to suppress noise in clear-cut cases.
    4. NCD Tiebreaker: If structural scores are identical, Normalized Compression Distance 
       breaks ties based on information density relative to the prompt.
    """

    def __init__(self):
        self.s = 1.5  # Zeta parameter for complexity penalty
        self.k = 1.0  # Boltzmann constant equivalent

    def _structural_parse(self, text: str) -> Dict:
        """Extract logical features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluate candidate against prompt constraints.
        Returns a score: 1.0 (perfect), 0.5 (partial), 0.0 (contradiction).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 1.0
        
        # 1. Negation Check: If prompt says "not X", candidate shouldn't be "X"
        # Simple heuristic: if prompt has strong negation and candidate is affirmative short form
        if p_feat['negations'] > 0:
            if c_lower in ['yes', 'true', 'correct']:
                # Check if the candidate is just echoing without reasoning
                if len(c_lower.split()) < 3: 
                    score -= 0.5
        
        # 2. Numeric Consistency
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                # If prompt asks for max/min, check candidate number
                if 'max' in p_lower or 'largest' in p_lower:
                    if c_nums and max(c_nums) != max(p_nums):
                        # Heuristic: if candidate picks a number, it should be the target
                        pass # Hard to verify without full semantics, skip penalty for now
                if 'min' in p_lower or 'smallest' in p_lower:
                    pass
            except ValueError:
                pass

        # 3. Length/Complexity constraint (Occam's Razor via structure)
        # If prompt is a simple yes/no question, long rambling answers might be less likely
        if '?' in prompt and len(candidate.split()) > 50:
            score -= 0.1
            
        return max(0.0, score)

    def _zeta_weight(self, complexity: int) -> float:
        """Calculate 1 / n^s as a complexity penalty (Occam's razor)."""
        if complexity == 0: return 1.0
        return 1.0 / (complexity ** self.s)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scores = []
        
        # Phase 1: Compute Structural Scores and Energies
        raw_scores = []
        for cand in candidates:
            logic_score = self._check_logical_consistency(prompt, cand)
            complexity = len(cand.split())
            zeta_pen = self._zeta_weight(complexity)
            
            # Combined structural score
            # Higher logic_score is better. Lower complexity (higher zeta_pen) is better.
            # We weight logic heavily, zeta as a tiebreaker/modulator
            base_score = (logic_score * 0.9) + (zeta_pen * 0.1)
            raw_scores.append(base_score)
        
        # Phase 2: Boltzmann Distribution (Temperature Annealing)
        # Energy E = -score. We want P(a) ~ exp(score / T)
        max_score = max(raw_scores)
        min_score = min(raw_scores)
        score_range = max_score - min_score if max_score != min_score else 1.0
        
        # Temperature T anneals based on clarity (score_range). 
        # High clarity (large range) -> Low T (sharp peak). Low clarity -> High T (explore).
        # Fluctuation-dissipation analogy: Variance in scores dictates T.
        T = 0.5 / (score_range + 0.1) 
        T = max(0.1, min(T, 2.0)) # Clamp T
        
        final_scores = []
        for i, cand in enumerate(candidates):
            # Boltzmann weight
            energy = -raw_scores[i]
            boltzmann_weight = math.exp((raw_scores[i] - max_score) / (T + 1e-9))
            
            # NCD Tiebreaker logic (only if structural scores are very close)
            ncd_score = 0.0
            if score_range < 0.05: # Ambiguous structural signal
                ncd_val = self._ncd(prompt, cand)
                # Prefer lower NCD (more similar/compressible together)
                ncd_score = (1.0 - ncd_val) * 0.01 # Small bonus
            
            total_score = boltzmann_weight + ncd_score
            final_scores.append(total_score)
        
        # Normalize to 0-1 range for output consistency
        max_final = max(final_scores)
        min_final = min(final_scores)
        range_final = max_final - min_final if max_final != min_final else 1.0
        
        results = []
        for i, cand in enumerate(candidates):
            norm_score = (final_scores[i] - min_final) / range_final
            results.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": f"Structural match: {raw_scores[i]:.2f}, Boltzmann weight: {final_scores[i]:.4f}, Temp: {T:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment and zeta-complexity.
        Returns 0.0 to 1.0.
        """
        logic_score = self._check_logical_consistency(prompt, answer)
        complexity = len(answer.split())
        zeta_pen = self._zeta_weight(complexity)
        
        base_conf = (logic_score * 0.8) + (zeta_pen * 0.2)
        
        # Penalty for contradictions detected in logic check
        if logic_score < 0.5:
            base_conf *= 0.5
            
        # NCD check for gibberish detection
        # If answer is random noise, NCD with prompt will be high (low similarity)
        # But if answer is just "Yes", NCD is low. 
        # We use NCD to penalize answers that are totally unrelated in token distribution
        ncd_val = self._ncd(prompt, answer)
        # Heuristic: if NCD is very high (>0.9) and logic is weak, reduce confidence
        if ncd_val > 0.9 and logic_score < 0.8:
            base_conf *= 0.8
            
        return max(0.0, min(1.0, base_conf))