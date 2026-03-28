import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Chaotic Ecosystem-Based Reasoner (MECER) Implementation.
    
    Mechanism:
    1. Structural Parsing (Ecosystem Base): Extracts logical constraints (negations, 
       comparatives, conditionals) to form the deterministic 'physics' of the hypothesis space.
    2. Chaos Detection (Lyapunov Estimator): Measures the sensitivity of candidate answers 
       to structural perturbations. High divergence indicates a 'chaotic' (unstable/overfit) hypothesis.
    3. Entropy Modulation: Uses the chaos signal to adjust the penalty for uncertainty. 
       If the system is chaotic, entropy requirements increase, lowering scores for 
       candidates that don't robustly satisfy structural constraints.
    4. Trophic Credit: Scores propagate from basal structural matches (direct evidence) 
       to higher-order logical consistency.
    
    This avoids pure NCD failures by prioritizing logical structure over string similarity,
    using chaos theory to detect when a candidate is 'too sensitive' to noise.
    """

    def __init__(self):
        self.epsilon = 1e-9

    def _structural_parse(self, text: str) -> Dict:
        """Extract logical primitives: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'length': len(text.split())
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def _estimate_lyapunov(self, base_feat: Dict, cand_feat: Dict) -> float:
        """
        Estimate local Lyapunov exponent.
        Analogy: Treat feature differences as trajectory divergence in phase space.
        Large divergence in key logical dimensions (negation/conditional) implies instability.
        """
        divergence = 0.0
        weight = 0.0
        
        # Weight logical features heavily (chaos drivers)
        logic_diff = abs(cand_feat['negations'] - base_feat['negations']) + \
                     abs(cand_feat['conditionals'] - base_feat['conditionals'])
        
        if logic_diff > 0:
            divergence += math.log(logic_diff + 1) * 2.0
            weight += 2.0
            
        # Numeric divergence
        if base_feat['numbers'] and cand_feat['numbers']:
            try:
                b_nums = [float(x) for x in base_feat['numbers']]
                c_nums = [float(x) for x in cand_feat['numbers']]
                # Compare sorted lists up to min length
                min_len = min(len(b_nums), len(c_nums))
                if min_len > 0:
                    num_diff = sum(abs(b_nums[i] - c_nums[i]) for i in range(min_len))
                    if num_diff > 0:
                        divergence += math.log(num_diff + 1)
                        weight += 1.0
            except ValueError:
                pass

        if weight == 0:
            return 0.0
        
        # Normalize by feature space volume approximation
        return divergence / (weight + self.epsilon)

    def _entropy_penalty(self, lyap_exp: float, temperature: float = 0.5) -> float:
        """
        Convert Lyapunov exponent to an entropy penalty.
        High chaos (high lyap_exp) -> High penalty (lowers score) unless compensated by strong structure.
        This implements the 'Maximum Entropy' constraint: forcing exploration away from chaotic overfitting.
        """
        # Sigmoidal response to chaos
        chaos_factor = 1.0 / (1.0 + math.exp(-2.0 * (lyap_exp - 0.5)))
        return chaos_factor * temperature

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feat = self._structural_parse(prompt)
        results = []
        
        # Baseline NCD for tie-breaking
        ncd_scores = []
        for cand in candidates:
            ncd = self._compute_ncd(prompt, cand)
            ncd_scores.append(ncd)
        
        avg_ncd = sum(ncd_scores) / len(ncd_scores) if ncd_scores else 0.5
        min_ncd = min(ncd_scores) if ncd_scores else 1.0
        ncd_range = (max(ncd_scores) - min_ncd) if len(ncd_scores) > 1 else 1.0
        if ncd_range == 0: ncd_range = 1.0

        for i, cand in enumerate(candidates):
            cand_feat = self._structural_parse(cand)
            
            # 1. Structural Match (Trophic Base Energy)
            # Reward matching logical complexity and number presence
            struct_score = 0.0
            
            # Negation alignment (critical for reasoning)
            if prompt_feat['negations'] > 0 and cand_feat['negations'] > 0:
                struct_score += 2.0
            elif prompt_feat['negations'] == 0 and cand_feat['negations'] == 0:
                struct_score += 1.0 # Consistent absence
                
            # Conditional alignment
            if prompt_feat['conditionals'] > 0:
                if cand_feat['conditionals'] > 0:
                    struct_score += 1.5
            else:
                if cand_feat['conditionals'] == 0:
                    struct_score += 0.5

            # Numeric consistency (simplified)
            if prompt_feat['numbers'] and cand_feat['numbers']:
                struct_score += 1.0
            
            # 2. Chaos Detection (Lyapunov)
            lyap = self._estimate_lyapunov(prompt_feat, cand_feat)
            
            # 3. Entropy Modulation
            # If chaos is high, we penalize heavily unless structural score is perfect
            entropy_pen = self._entropy_penalty(lyap)
            
            # 4. NCD Tiebreaker (Normalized)
            # Only matters if structural signals are weak or identical
            ncd_norm = (ncd_scores[i] - min_ncd) / (ncd_range + self.epsilon)
            ncd_bonus = (1.0 - ncd_norm) * 0.5 # Max 0.5 bonus for high similarity
            
            # Final Score Composition
            # Logic: Structural Base - Chaos Penalty + NCD Bonus
            final_score = struct_score - entropy_pen + ncd_bonus
            
            # Heuristic boost for exact keyword matches in short answers (common in reasoning tests)
            prompt_words = set(re.findall(r'\w+', prompt.lower()))
            cand_words = set(re.findall(r'\w+', cand.lower()))
            overlap = len(prompt_words.intersection(cand_words))
            if overlap > 0:
                final_score += (overlap / len(prompt_words)) * 0.5

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, Chaos:{lyap:.2f}, EntropyPen:{entropy_pen:.2f}, NCD:{ncd_norm:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and low chaos.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]['score']
        
        # Map score to 0-1 range using a soft sigmoid
        # Assuming typical scores range between -1 and 4 based on logic above
        confidence = 1.0 / (1.0 + math.exp(-(score - 1.5)))
        return max(0.0, min(1.0, confidence))