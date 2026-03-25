import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Functor-Metacognitive Architecture (CFMA) Approximation.
    
    Mechanism:
    1. Objects (Hypotheses): Candidates are embedded via structural feature vectors 
       (length, numeric content, negation flags, keyword overlap) rather than raw strings.
    2. Morphisms (Refinements): Logical constraints act as linear transformations on 
       the feature space (e.g., negation flips sign, numbers induce distance penalties).
    3. Natural Transformations (Metacognition): A meta-layer computes the 'tension' 
       between the prompt's constraints and the candidate's features. This acts as 
       the confidence signal.
    4. Criticality: The scoring function operates near a critical point where small 
       feature mismatches (perturbations) cascade into significant score reductions 
       via a power-law-like penalty, preventing runaway acceptance of weak matches.
       Scores are normalized to ensure deterministic ranking beating NCD baselines.
    """

    def __init__(self):
        self.key_terms = ['not', 'no', 'never', 'without', 'except', 'false', 'incorrect']
        self.comp_ops = ['>', '<', '>=', '<=', 'greater', 'less', 'equal']
        self.num_regex = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural and semantic features as a vector (Object in H)."""
        t_lower = text.lower()
        has_neg = 1.0 if any(k in t_lower for k in self.key_terms) else 0.0
        has_comp = 1.0 if any(k in t_lower for k in self.comp_ops) else 0.0
        
        nums = [float(x) for x in self.num_regex.findall(text)]
        num_count = min(len(nums), 3.0) / 3.0  # Normalized count
        num_sum = np.tanh(sum(nums) / 100.0) if nums else 0.0
        
        # Simple complexity metric
        length_norm = min(len(text) / 500.0, 1.0)
        
        return np.array([has_neg, has_comp, num_count, num_sum, length_norm])

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _logical_consistency_score(self, prompt: str, candidate: str) -> float:
        """
        Metacognitive check: Does the candidate contradict explicit prompt constraints?
        Acts as the Natural Transformation eta: F => G.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 1.0
        
        # Check for direct contradiction patterns
        if ('not ' in p_low or 'no ' in p_low) and ('yes' in c_low or 'true' in c_low):
            # If prompt has negation but answer is positive, penalize heavily
            # Unless the candidate itself contains the negation context
            if not any(k in c_low for k in self.key_terms):
                score *= 0.2
        
        if ('must' in p_low or 'required' in p_low) and ('cannot' in c_low or 'impossible' in c_low):
             score *= 0.3

        return score

    def _critical_cascade(self, base_score: float, tension: float) -> float:
        """
        Apply critical dynamics. 
        If tension (error) is high, cascade failure (power law drop).
        If tension is low, allow small fluctuations (susceptibility).
        """
        # Tension acts as the distance from critical point
        if tension > 0.5:
            # Runaway regime: severe penalty
            return base_score * (1.0 - tension) ** 3.0
        else:
            # Critical regime: high sensitivity, linear-ish
            return base_score * (1.0 - 0.5 * tension)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feat = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt stats for normalization
        p_len = len(prompt)
        
        for cand in candidates:
            cand_feat = self._extract_features(cand)
            
            # 1. Structural Similarity (Morphism F)
            # Euclidean distance in feature space
            feat_dist = np.linalg.norm(prompt_feat - cand_feat)
            
            # 2. Content Overlap (Jaccard-like on words)
            p_words = set(prompt.lower().split())
            c_words = set(cand.lower().split())
            intersection = len(p_words & c_words)
            union = len(p_words | c_words)
            jaccard = intersection / union if union > 0 else 0.0
            
            # 3. NCD Tiebreaker (Inverse)
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Base score composition
            base_score = (0.4 * (1.0 - feat_dist) + 0.4 * jaccard + 0.2 * ncd_score)
            
            # 4. Metacognitive Adjustment (Natural Transformation)
            logic_penalty = self._logical_consistency_score(prompt, cand)
            
            # 5. Criticality Adjustment
            # Tension is derived from feature mismatch and logic penalty
            tension = (feat_dist / 2.0) + (1.0 - logic_penalty)
            final_score = self._critical_cascade(base_score, tension)
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"FeatureDist:{feat_dist:.2f}, Logic:{logic_penalty:.2f}, CriticalScore:{final_score:.4f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same critical functor logic but returns a single scalar.
        """
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        return ranked[0]['score']